#!/usr/bin/env python3
"""
DITM (Deep-In-The-Money) Options Portfolio Builder
Uses Charles Schwab Trader API for market data
"""
import os
import json
from pathlib import Path
from datetime import datetime, timedelta, time as dt_time
import time
from typing import Optional
import pytz

import pandas as pd
import numpy as np
from scipy.stats import norm
from dotenv import load_dotenv
import schwab
from schwab import auth
from recommendation_tracker import RecommendationTracker
from filter_matcher import FilterMatcher

# Load environment variables
load_dotenv()

# -------------------------------------------------
# CONFIGURATION
# -------------------------------------------------
MIN_DELTA         = 0.80
MAX_DELTA         = 0.95
MIN_INTRINSIC_PCT = 0.85          # intrinsic / premium
MIN_DTE           = 90
MAX_IV            = 0.30
MAX_SPREAD_PCT    = 0.02
MIN_OI            = 500
MAX_IMMEDIATE_LOSS_PCT = 0.15     # Maximum acceptable immediate loss % (formula: 5% + DTE/365 * 5%)
RISK_FREE_RATE    = 0.04          # approximate Treasury yield

# Schwab API Configuration
APP_KEY = os.getenv("SCHWAB_APP_KEY")
APP_SECRET = os.getenv("SCHWAB_APP_SECRET")
CALLBACK_URL = os.getenv("SCHWAB_CALLBACK_URL", "https://127.0.0.1:8182")
TOKEN_PATH = Path(os.getenv("SCHWAB_TOKEN_PATH", "./schwab_tokens.json"))

# Market data cache
CACHE_DIR = Path("./market_data_cache")
CACHE_DIR.mkdir(exist_ok=True)

# -------------------------------------------------
# MARKET HOURS AND CACHING
# -------------------------------------------------
def is_market_open() -> bool:
    """
    Check if US stock market is currently open.
    Market hours: 9:30 AM - 4:00 PM ET, Monday-Friday (excluding holidays)
    """
    et_tz = pytz.timezone('America/New_York')
    now_et = datetime.now(et_tz)

    # Check if weekend
    if now_et.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False

    # Check if within market hours (9:30 AM - 4:00 PM ET)
    market_open = dt_time(9, 30)
    market_close = dt_time(16, 0)
    current_time = now_et.time()

    if market_open <= current_time <= market_close:
        return True

    return False

def get_cache_path(ticker: str) -> Path:
    """Get cache file path for a ticker"""
    return CACHE_DIR / f"{ticker}_cache.json"

def get_cached_data(ticker: str) -> Optional[dict]:
    """
    Retrieve cached market data for a ticker if available and fresh.
    Returns None if cache is invalid or market is open.
    """
    if is_market_open():
        return None

    cache_path = get_cache_path(ticker)
    if not cache_path.exists():
        return None

    try:
        with open(cache_path, 'r') as f:
            cache_data = json.load(f)

        # Check cache timestamp - valid for same trading day only
        cache_time = datetime.fromisoformat(cache_data['timestamp'])
        now = datetime.now()

        # Cache is valid if it's from the same day
        if cache_time.date() == now.date():
            print(f"  ✓ Using cached data for {ticker} (market closed)")
            return cache_data['data']

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"  ⚠ Cache read error for {ticker}: {e}")

    return None

def save_to_cache(ticker: str, quote_data: dict, options_data: dict):
    """Save market data to cache"""
    cache_path = get_cache_path(ticker)
    cache_data = {
        'timestamp': datetime.now().isoformat(),
        'data': {
            'quote': quote_data,
            'options': options_data
        }
    }

    try:
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f, indent=2)
    except Exception as e:
        print(f"  ⚠ Cache write error for {ticker}: {e}")

# -------------------------------------------------
# HELPER: Black-Scholes delta for a call
# -------------------------------------------------
def bs_call_delta(S, K, T, r, sigma):
    """Calculate Black-Scholes delta for a call option"""
    if T <= 0: return 1.0 if S > K else 0.0
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    return norm.cdf(d1)

# -------------------------------------------------
# ACCOUNT POSITIONS
# -------------------------------------------------
def get_account_positions(client) -> pd.DataFrame:
    """
    Fetch actual option positions from Schwab account.
    Returns DataFrame with ticker, strike, expiration, quantity, and extrinsic value.
    """
    try:
        # Get all accounts with positions
        response = client.get_accounts(fields=schwab.client.Client.Account.Fields.POSITIONS)

        if response.status_code != 200:
            print(f"Failed to fetch account positions: HTTP {response.status_code}")
            return pd.DataFrame()

        accounts_data = response.json()

        positions = []
        tickers_to_fetch = set()

        for account in accounts_data:
            if 'positions' not in account['securitiesAccount']:
                continue

            for position in account['securitiesAccount']['positions']:
                instrument = position.get('instrument', {})

                # Only process option positions
                if instrument.get('assetType') != 'OPTION':
                    continue

                # Only process call options
                option_type = instrument.get('putCall')
                if option_type != 'CALL':
                    continue

                # Parse option symbol (format: AAPL  250117C00225000)
                symbol = instrument.get('symbol', '')
                underlying = instrument.get('underlyingSymbol', '')

                # Extract details
                quantity = position.get('longQuantity', 0) - position.get('shortQuantity', 0)

                if quantity <= 0:
                    continue

                strike = instrument.get('strikePrice', 0)
                avg_price = position.get('averagePrice', 0)

                positions.append({
                    'Ticker': underlying,
                    'Symbol': symbol,
                    'Strike': strike,
                    'Expiration': instrument.get('expirationDate', ''),
                    'Quantity': int(quantity),
                    'Description': instrument.get('description', ''),
                    'Average_Price': avg_price,
                    'Current_Value': position.get('marketValue', 0),
                    'Unrealized_PL': position.get('currentDayProfitLoss', 0)
                })

                tickers_to_fetch.add(underlying)

        df = pd.DataFrame(positions)

        # Convert expiration date format from milliseconds to YYYY-MM-DD
        if not df.empty and 'Expiration' in df.columns:
            # Schwab returns dates as milliseconds since epoch
            df['Expiration'] = pd.to_datetime(df['Expiration'], unit='ms').dt.strftime('%Y-%m-%d')

            # Get current stock prices to calculate intrinsic/extrinsic values
            stock_prices = {}
            for ticker in tickers_to_fetch:
                try:
                    quote_resp = client.get_quote(ticker)
                    if quote_resp.status_code == 200:
                        quote_data = quote_resp.json()
                        stock_prices[ticker] = quote_data.get(ticker, {}).get('quote', {}).get('lastPrice', 0)
                except Exception as e:
                    print(f"Warning: Could not get quote for {ticker}: {e}")
                    stock_prices[ticker] = 0

            # Calculate extrinsic values
            df['Stock_Price'] = df['Ticker'].map(stock_prices)
            df['Intrinsic_Value'] = df.apply(
                lambda row: max(row['Stock_Price'] - row['Strike'], 0) if row['Stock_Price'] > 0 else 0,
                axis=1
            )
            df['Extrinsic_Value'] = df['Average_Price'] - df['Intrinsic_Value']
            df['Extrinsic_Pct'] = df.apply(
                lambda row: (row['Extrinsic_Value'] / row['Average_Price'] * 100) if row['Average_Price'] > 0 else 0,
                axis=1
            )
            df['Contract_Cost'] = df['Average_Price'] * 100  # Per contract in dollars

            # Calculate additional display fields
            df['Total_Cost'] = df['Average_Price'] * df['Quantity'] * 100
            df['P&L'] = df['Current_Value'] - df['Total_Cost']
            df['P&L_%'] = (df['P&L'] / df['Total_Cost'] * 100).fillna(0)

            # Calculate DTE
            df['DTE'] = (pd.to_datetime(df['Expiration']) - pd.Timestamp.now()).dt.days

        return df

    except Exception as e:
        print(f"Error fetching account positions: {e}")
        return pd.DataFrame()

# -------------------------------------------------
# SCHWAB CLIENT INITIALIZATION
# -------------------------------------------------
def get_schwab_client():
    """
    Initialize and return Schwab API client with authentication.
    First run will open browser for OAuth login.
    """
    if not APP_KEY or not APP_SECRET:
        raise ValueError(
            "Missing Schwab API credentials! Please set SCHWAB_APP_KEY and "
            "SCHWAB_APP_SECRET in .env file. See SCHWAB_SETUP.md for details."
        )

    try:
        if TOKEN_PATH.exists():
            # Use existing tokens
            print(f"Loading existing tokens from {TOKEN_PATH}...")
            client = auth.client_from_token_file(str(TOKEN_PATH), APP_KEY, APP_SECRET)
        else:
            # First-time authentication
            print("\n" + "=" * 60)
            print("FIRST-TIME AUTHENTICATION REQUIRED")
            print("=" * 60)
            print("A browser window will open. Please:")
            print("1. Log in to your Schwab account")
            print("2. Authorize the application")
            print("3. Copy the ENTIRE redirect URL from your browser")
            print("4. Paste it here when prompted")
            print("=" * 60 + "\n")

            client = auth.client_from_manual_flow(
                APP_KEY,
                APP_SECRET,
                CALLBACK_URL,
                str(TOKEN_PATH)
            )
            print(f"\n✓ Tokens saved to {TOKEN_PATH}")
            print("Future runs will use saved tokens automatically.\n")

        return client

    except Exception as e:
        print(f"\n✗ Authentication failed: {e}")
        print("\nTroubleshooting:")
        print("- Ensure your app status is 'Ready For Use' in Schwab Developer Portal")
        print("- Verify APP_KEY and APP_SECRET in .env file")
        print(f"- Check callback URL is: {CALLBACK_URL}")
        print("- See SCHWAB_SETUP.md for detailed setup instructions")
        raise


def get_option_quote(client, ticker: str, strike: float, expiration: str, option_type: str = 'CALL'):
    """
    Get current quote data for a specific option contract.

    Args:
        client: Schwab API client
        ticker: Stock ticker symbol
        strike: Strike price
        expiration: Expiration date (YYYY-MM-DD format)
        option_type: 'CALL' or 'PUT' (default: 'CALL')

    Returns:
        Dictionary with option data or None if not found
    """
    try:
        import schwab
        from datetime import datetime

        # Get option chain for this ticker
        contract_type = schwab.client.Client.Options.ContractType.CALL if option_type == 'CALL' else schwab.client.Client.Options.ContractType.PUT

        options_resp = client.get_option_chain(
            ticker,
            contract_type=contract_type,
            include_underlying_quote=True
        )

        if options_resp.status_code != 200:
            print(f"    Failed to get options chain: HTTP {options_resp.status_code}")
            return None

        options_data = options_resp.json()

        if options_data.get("status") != "SUCCESS":
            print(f"    Options query failed: {options_data.get('status')}")
            return None

        # Get stock price from underlying quote
        stock_price = options_data.get("underlyingPrice", 0)
        if not stock_price and "underlying" in options_data:
            stock_price = options_data["underlying"].get("last", 0)

        # Parse expiration date to match format in option chain
        exp_date = datetime.strptime(expiration, "%Y-%m-%d")

        # Search through option chain for matching strike and expiration
        exp_map = options_data.get("callExpDateMap" if option_type == 'CALL' else "putExpDateMap", {})

        for exp_date_str, strikes in exp_map.items():
            # Parse expiration date (format: "2025-01-17:45" where 45 is DTE)
            chain_exp_date = datetime.strptime(exp_date_str.split(":")[0], "%Y-%m-%d")

            # Check if expiration matches
            if chain_exp_date.date() != exp_date.date():
                continue

            # Look for matching strike
            strike_str = str(float(strike))
            if strike_str in strikes:
                contracts = strikes[strike_str]
                if contracts:
                    contract = contracts[0]  # Take first contract

                    bid = contract.get("bid", 0)
                    ask = contract.get("ask", 0)
                    mid = (bid + ask) / 2.0 if bid > 0 and ask > 0 else 0
                    delta = contract.get("delta", 0)

                    return {
                        'ticker': ticker,
                        'strike': strike,
                        'expiration': expiration,
                        'bid': bid,
                        'ask': ask,
                        'mid': mid,
                        'delta': delta,
                        'stock_price': stock_price,
                        'iv': contract.get("volatility", 0),
                        'oi': contract.get("openInterest", 0)
                    }

        print(f"    Option not found: {ticker} ${strike} {expiration}")
        return None

    except Exception as e:
        print(f"    Error fetching option quote: {e}")
        return None


# -------------------------------------------------
# SINGLE STOCK FUNCTION (Schwab API version)
# -------------------------------------------------
def find_ditm_calls(client, ticker: str, max_retries: int = 3) -> pd.DataFrame:
    """
    Returns a DataFrame of deep-in-the-money call candidates using Schwab API.
    Uses cached data when market is closed.
    """
    # Try to get cached data first
    cached = get_cached_data(ticker)
    if cached:
        quote_data = cached['quote']
        options_data = cached['options']
        S = quote_data[ticker]["quote"]["lastPrice"]
    else:
        # Fetch fresh data from API
        for attempt in range(max_retries):
            try:
                # Add delay between retries to avoid rate limiting
                if attempt > 0:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"  Retry {attempt}/{max_retries} for {ticker} after {wait_time}s...")
                    time.sleep(wait_time)

                # Get current stock price
                quote_resp = client.get_quote(ticker)
                if quote_resp.status_code != 200:
                    raise Exception(f"Failed to get quote: HTTP {quote_resp.status_code}")

                quote_data = quote_resp.json()
                if ticker not in quote_data:
                    raise Exception(f"No quote data for {ticker}")

                S = quote_data[ticker]["quote"]["lastPrice"]

                # Get option chain (all expirations, CALL options only)
                options_resp = client.get_option_chain(
                    ticker,
                    contract_type=schwab.client.Client.Options.ContractType.CALL,
                    include_underlying_quote=True
                )

                if options_resp.status_code != 200:
                    raise Exception(f"Failed to get options: HTTP {options_resp.status_code}")

                options_data = options_resp.json()

                if options_data["status"] != "SUCCESS":
                    raise Exception(f"Options query failed: {options_data.get('status')}")

                # Cache the fresh data
                save_to_cache(ticker, quote_data, options_data)
                break

            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"ERROR: Failed to fetch data for {ticker} after {max_retries} attempts: {e}")
                    return pd.DataFrame()  # Return empty DataFrame on failure
                continue

    # Process the data (either from cache or fresh API call)
    try:
        # Parse options data
        rows = []
        call_exp_map = options_data.get("callExpDateMap", {})

        for exp_date_str, strikes in call_exp_map.items():
            # Parse expiration date (format: "2025-01-17:45" where 45 is DTE)
            exp_date = datetime.strptime(exp_date_str.split(":")[0], "%Y-%m-%d")
            T = (exp_date - datetime.now()).days / 365.0
            dte = int(T * 365)

            if dte < MIN_DTE:
                continue

            for strike_str, contracts in strikes.items():
                K = float(strike_str)

                # Each strike can have multiple contracts (different expiries)
                for contract in contracts:
                    bid = contract.get("bid", 0)
                    ask = contract.get("ask", 0)

                    if bid <= 0 or ask <= 0:
                        continue

                    mid = (bid + ask) / 2.0
                    iv = contract.get("volatility", 0.30)  # Implied volatility
                    oi = contract.get("openInterest", 0)

                    # ---- liquidity filters ----
                    if oi < MIN_OI:
                        continue

                    spread_pct = (ask - bid) / mid
                    if spread_pct > MAX_SPREAD_PCT:
                        continue

                    # ---- intrinsic value ----
                    intrinsic = max(S - K, 0)
                    if intrinsic == 0:
                        continue

                    intrinsic_pct = intrinsic / mid
                    if intrinsic_pct < MIN_INTRINSIC_PCT:
                        continue

                    # ---- delta (use BS if IV missing) ----
                    sigma = iv / 100.0 if iv > 1 else iv  # Normalize IV
                    if np.isnan(sigma) or sigma == 0:
                        sigma = 0.30

                    delta = contract.get("delta")
                    if delta is None or np.isnan(delta):
                        delta = bs_call_delta(S, K, T, RISK_FREE_RATE, sigma)

                    if not (MIN_DELTA <= delta <= MAX_DELTA):
                        continue

                    # ---- IV filter ----
                    if sigma > MAX_IV:
                        continue

                    # ---- cost vs. stock ----
                    shares_equiv = delta * 100
                    cost_per_share = mid / shares_equiv if shares_equiv > 0 else 0

                    # ---- extrinsic value (premium above intrinsic) ----
                    extrinsic = mid - intrinsic  # Time value + volatility premium
                    extrinsic_pct = extrinsic / mid if mid > 0 else 0

                    # ---- immediate loss filter (extrinsic + spread based on DTE) ----
                    # Calculate DTE-adjusted max immediate loss: 5% base + (DTE/365)*5%
                    # This allows higher immediate loss for longer-dated options
                    max_loss_for_dte = 0.05 + (dte / 365.0) * 0.05  # Formula from User Guide
                    max_loss_cap = min(max_loss_for_dte, MAX_IMMEDIATE_LOSS_PCT)  # Cap at MAX setting

                    # Total immediate loss = extrinsic + spread
                    immediate_loss_pct = extrinsic_pct + spread_pct
                    if immediate_loss_pct > max_loss_cap:
                        continue  # Skip this option, too expensive for its DTE

                    rows.append({
                        "Expiration": exp_date_str.split(":")[0],
                        "Strike": K,
                        "DTE": dte,
                        "Bid": bid,
                        "Ask": ask,
                        "Mid": mid,
                        "IV": sigma,
                        "Delta": delta,
                        "Intrinsic": intrinsic,
                        "Intrinsic%": intrinsic_pct,
                        "Extrinsic": extrinsic,
                        "Extrinsic%": extrinsic_pct,
                        "Cost/Share": cost_per_share,
                        "OI": oi,
                        "Spread%": spread_pct,
                    })

        df = pd.DataFrame(rows)
        if df.empty:
            return df

        # ---- ranking score (lower = more conservative) ----
        df["Score"] = (
            0.4 * (1 - df["Delta"]) +               # prefer slightly lower delta
            0.3 * (1 - df["Intrinsic%"]) +          # higher intrinsic %
            0.2 * df["IV"] / MAX_IV +              # penalize high IV
            0.1 * df["Spread%"] / MAX_SPREAD_PCT
        )
        df = df.sort_values("Score").reset_index(drop=True)
        return df

    except Exception as e:
        print(f"ERROR: Failed to process data for {ticker}: {e}")
        return pd.DataFrame()

# -------------------------------------------------
# PORTFOLIO BUILDER
# -------------------------------------------------
def build_ditm_portfolio(client, tickers: list,
                         delay_between_stocks: float = 0.5,
                         tracker: RecommendationTracker = None,
                         save_recommendations: bool = True) -> pd.DataFrame:
    """
    Builds a conservative DITM call portfolio across multiple stocks using Schwab API.
    Scans for 1 contract per ticker to find the best DITM opportunities.
    Returns summary DataFrame.

    Args:
        client: Schwab API client
        tickers: List of stock symbols to scan
        delay_between_stocks: Delay in seconds between API calls
        tracker: RecommendationTracker instance (created if None)
        save_recommendations: Whether to save to tracking database
    """
    portfolio = []
    num_stocks = len(tickers)

    # Initialize tracker and create scan record
    scan_id = None
    recent_tickers = {}
    matcher = None
    current_preset = None

    if save_recommendations:
        if tracker is None:
            tracker = RecommendationTracker()

        # Initialize filter matcher and load presets
        try:
            matcher = FilterMatcher()
            # Try to load current preset from config, default to 'moderate'
            config_path = Path("./web_config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                current_preset = config.get('current_preset', matcher.get_default_preset())
            else:
                current_preset = matcher.get_default_preset()
            print(f"\nUsing filter preset: {current_preset}")
        except Exception as e:
            print(f"\nWarning: Could not load filter presets: {e}")
            print("Continuing without preset matching...")

        # Check for tickers with recent open recommendations (within 24 hours)
        recent_tickers = tracker.get_tickers_with_recent_recommendations(hours=24)

        # Filter out tickers that already have recent recommendations
        tickers_to_scan = []
        skipped_tickers = []
        for ticker in tickers:
            if ticker in recent_tickers:
                rec_info = recent_tickers[ticker]
                skipped_tickers.append(ticker)
                print(f"\nSkipping {ticker}: Already has open recommendation from {rec_info['recommendation_date'][:19]}")
                print(f"  Strike: ${rec_info['strike']}, Exp: {rec_info['expiration']}")
            else:
                tickers_to_scan.append(ticker)

        if not tickers_to_scan:
            print("\nAll tickers already have recent open recommendations. No new scan needed.")
            return pd.DataFrame()

        print(f"\nScanning {len(tickers_to_scan)} ticker(s), skipping {len(skipped_tickers)} with recent recommendations.")
        tickers = tickers_to_scan
        num_stocks = len(tickers)

        scan_date = datetime.now().isoformat()
        filter_params = {
            "MIN_DELTA": MIN_DELTA,
            "MAX_DELTA": MAX_DELTA,
            "MIN_INTRINSIC_PCT": MIN_INTRINSIC_PCT,
            "MIN_DTE": MIN_DTE,
            "MAX_IV": MAX_IV,
            "MAX_SPREAD_PCT": MAX_SPREAD_PCT,
            "MIN_OI": MIN_OI,
            "RISK_FREE_RATE": RISK_FREE_RATE
        }
        # Pass preset_name to scan record if available
        scan_id = tracker.record_scan(
            scan_date,
            tickers,
            filter_params,
            preset_name=current_preset if current_preset else None
        )

    for i, ticker in enumerate(tickers):
        print(f"\nProcessing {ticker} ({i+1}/{num_stocks})...")

        # Add delay between stocks to avoid rate limiting
        if i > 0:
            time.sleep(delay_between_stocks)

        candidates = find_ditm_calls(client, ticker)
        if candidates.empty:
            print(f"  No qualifying DITM calls for {ticker}.")
            continue

        # Get current stock price for comparison
        quote_resp = client.get_quote(ticker)
        S = quote_resp.json()[ticker]["quote"]["lastPrice"]

        # Save ALL candidates if using DB tracker with add_candidate method
        if save_recommendations and scan_id and matcher and hasattr(tracker, 'add_candidate'):
            print(f"  Found {len(candidates)} qualifying options for {ticker}")
            for idx, candidate in candidates.iterrows():
                # Calculate values for this candidate
                intrinsic = max(S - candidate["Strike"], 0)
                extrinsic = candidate["Ask"] - intrinsic
                spread_loss = candidate["Ask"] - candidate["Bid"]
                total_immediate_loss = extrinsic + spread_loss
                total_immediate_loss_pct = (total_immediate_loss / candidate["Ask"]) * 100 if candidate["Ask"] > 0 else 0

                # Check which presets match this candidate
                matched_presets = matcher.check_all_preset_matches({
                    'delta': candidate['Delta'],
                    'iv': candidate['IV'],
                    'intrinsic_pct': candidate['Intrinsic%'],
                    'extrinsic_pct': candidate.get('Extrinsic%', total_immediate_loss_pct / 100),
                    'dte': candidate['DTE'],
                    'spread_pct': candidate['Spread%'],
                    'oi': candidate['OI']
                })

                # Save candidate to database
                tracker.add_candidate(
                    scan_id=scan_id,
                    ticker=ticker,
                    stock_price=S,
                    strike=candidate["Strike"],
                    expiration=candidate["Expiration"],
                    dte=candidate["DTE"],
                    bid=candidate["Bid"],
                    ask=candidate["Ask"],
                    mid=candidate["Mid"],
                    delta=candidate["Delta"],
                    iv=candidate["IV"],
                    intrinsic=intrinsic,
                    intrinsic_pct=candidate["Intrinsic%"],
                    extrinsic=total_immediate_loss,
                    extrinsic_pct=total_immediate_loss_pct / 100,
                    score=candidate["Score"],
                    spread_pct=candidate["Spread%"],
                    oi=candidate["OI"],
                    cost_per_share=candidate["Cost/Share"],
                    matched_presets=matched_presets,
                    recommended=(idx == 0)  # First one is top pick
                )

            print(f"  Saved {len(candidates)} candidates, matching presets: {set([p for cand in [matcher.check_all_preset_matches({'delta': c['Delta'], 'iv': c['IV'], 'intrinsic_pct': c['Intrinsic%'], 'extrinsic_pct': 0.15, 'dte': c['DTE'], 'spread_pct': c['Spread%'], 'oi': c['OI']}) for _, c in candidates.iterrows()] for p in cand])}")

        top = candidates.iloc[0]  # Lowest score = most conservative

        # Position sizing: Single contract per ticker
        contracts = 1
        contract_cost = top["Ask"] * 100  # Use Ask price (realistic buy price)
        equiv_shares = contracts * top["Delta"] * 100  # Delta-adjusted exposure

        # Calculate total immediate loss (extrinsic + spread)
        # This is what you'd lose if you bought at Ask and sold at Bid immediately
        intrinsic = max(S - top["Strike"], 0)
        extrinsic = top["Ask"] - intrinsic  # Time value portion
        spread_loss = top["Ask"] - top["Bid"]  # Immediate spread loss
        total_immediate_loss = extrinsic + spread_loss  # Total amount to recoup
        total_immediate_loss_pct = (total_immediate_loss / top["Ask"]) * 100 if top["Ask"] > 0 else 0

        # Conservative check: Ensure cost/share < stock price * 0.98
        if top["Cost/Share"] > S * 0.98:
            print(f"  Skipping {ticker}: Not cheaper than stock.")
            continue

        portfolio.append({
            "Ticker": ticker,
            "Stock Price": round(S, 2),
            "Strike": top["Strike"],
            "Expiration": top["Expiration"],
            "DTE": top["DTE"],
            "Delta": round(top["Delta"], 3),
            "Cost/Share": round(top["Cost/Share"], 2),
            "Contracts": contracts,
            "Contract Cost": round(contract_cost, 2),
            "Extrinsic Value": round(total_immediate_loss * 100, 2),  # Per contract in dollars (extrinsic + spread)
            "Extrinsic %": round(total_immediate_loss_pct, 2),
            "Equiv Shares": round(equiv_shares),
            "Score": round(top["Score"], 3)
        })

        # Save recommendation to tracker (top pick)
        if save_recommendations and scan_id:
            tracker.add_recommendation(
                scan_id=scan_id,
                ticker=ticker,
                stock_price=S,
                strike=top["Strike"],
                expiration=top["Expiration"],
                dte=top["DTE"],
                premium_bid=top["Bid"],
                premium_ask=top["Ask"],
                premium_mid=top["Mid"],
                delta=top["Delta"],
                iv=top["IV"],
                intrinsic_pct=top["Intrinsic%"],
                oi=top["OI"],
                spread_pct=top["Spread%"],
                cost_per_share=top["Cost/Share"],
                contracts=contracts,
                total_cost=contract_cost,  # Using contract_cost (Ask * 100)
                equiv_shares=equiv_shares,
                score=top["Score"],
                extrinsic_value=total_immediate_loss * 100,  # Per contract in dollars (extrinsic + spread)
                extrinsic_pct=total_immediate_loss_pct
            )

    df = pd.DataFrame(portfolio)
    if not df.empty:
        df["Allocation %"] = (df["Contract Cost"] / df["Contract Cost"].sum() * 100).round(2)
        total_cost_port = df["Contract Cost"].sum()
        total_equiv = df["Equiv Shares"].sum()

        print(f"\n{'=' * 70}")
        print(f"PORTFOLIO SUMMARY")
        print(f"{'=' * 70}")
        print(f"Total Invested: ${total_cost_port:,.2f}")
        print(f"Total Equivalent Shares Controlled: {total_equiv:,}")
        print(f"Capital Efficiency: {(total_cost_port / total_equiv) * 100:.1f}% of stock cost")
        print(f"{'=' * 70}\n")

    return df.sort_values("Score")  # Sort by conservatism

# -------------------------------------------------
# EXAMPLE USAGE
# -------------------------------------------------
if __name__ == "__main__":
    print("DITM Options Portfolio Builder - Schwab API Edition")
    print("=" * 70)

    # Initialize Schwab client
    try:
        client = get_schwab_client()
    except Exception as e:
        print(f"\n✗ Failed to initialize Schwab client: {e}")
        print("\nPlease complete setup steps in SCHWAB_SETUP.md")
        exit(1)

    # Conservative blue-chip stocks
    stocks = ["AAPL", "MSFT", "GOOGL", "JNJ", "JPM"]

    print(f"\nScanning {len(stocks)} stocks for DITM call opportunities...")
    print(f"Scanning for 1 contract per ticker")
    print(f"Filters: Delta {MIN_DELTA}-{MAX_DELTA}, DTE >{MIN_DTE}, IV <{MAX_IV}")
    print("=" * 70)

    portfolio = build_ditm_portfolio(client, stocks)

    if not portfolio.empty:
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        print(portfolio)

        # Save to CSV
        output_file = f"ditm_portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        portfolio.to_csv(output_file, index=False)
        print(f"\n✓ Portfolio saved to: {output_file}")
    else:
        print("\n✗ No qualifying options found. Try:")
        print("  - Adjusting filter parameters (MIN_DELTA, MAX_IV, etc.)")
        print("  - Different stock tickers")
        print("  - Running during market hours for better data")
