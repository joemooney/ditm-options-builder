#!/usr/bin/env python3
"""
DITM (Deep-In-The-Money) Options Portfolio Builder
Uses Charles Schwab Trader API for market data
"""
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
import time
from typing import Optional

import pandas as pd
import numpy as np
from scipy.stats import norm
from dotenv import load_dotenv
import schwab
from schwab import auth
from recommendation_tracker import RecommendationTracker

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
RISK_FREE_RATE    = 0.04          # approximate Treasury yield

# Schwab API Configuration
APP_KEY = os.getenv("SCHWAB_APP_KEY")
APP_SECRET = os.getenv("SCHWAB_APP_SECRET")
CALLBACK_URL = os.getenv("SCHWAB_CALLBACK_URL", "https://127.0.0.1:8182")
TOKEN_PATH = Path(os.getenv("SCHWAB_TOKEN_PATH", "./schwab_tokens.json"))

# -------------------------------------------------
# HELPER: Black-Scholes delta for a call
# -------------------------------------------------
def bs_call_delta(S, K, T, r, sigma):
    """Calculate Black-Scholes delta for a call option"""
    if T <= 0: return 1.0 if S > K else 0.0
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    return norm.cdf(d1)

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

# -------------------------------------------------
# SINGLE STOCK FUNCTION (Schwab API version)
# -------------------------------------------------
def find_ditm_calls(client, ticker: str, max_retries: int = 3) -> pd.DataFrame:
    """
    Returns a DataFrame of deep-in-the-money call candidates using Schwab API.
    """
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

                        rows.append({
                            "Expiration": exp_date_str.split(":")[0],
                            "Strike": K,
                            "DTE": dte,
                            "Bid": bid,
                            "Ask": ask,
                            "Mid": mid,
                            "IV": sigma,
                            "Delta": delta,
                            "Intrinsic%": intrinsic_pct,
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
            if attempt == max_retries - 1:
                print(f"ERROR: Failed to fetch data for {ticker} after {max_retries} attempts: {e}")
                return pd.DataFrame()  # Return empty DataFrame on failure
            continue

    return pd.DataFrame()

# -------------------------------------------------
# PORTFOLIO BUILDER
# -------------------------------------------------
def build_ditm_portfolio(client, tickers: list, target_capital: float = 50000,
                         delay_between_stocks: float = 0.5,
                         tracker: RecommendationTracker = None,
                         save_recommendations: bool = True) -> pd.DataFrame:
    """
    Builds a conservative DITM call portfolio across multiple stocks using Schwab API.
    Allocates equally (e.g., $10k per stock for $50k total).
    Returns summary DataFrame.

    Args:
        client: Schwab API client
        tickers: List of stock symbols to scan
        target_capital: Total capital to allocate
        delay_between_stocks: Delay in seconds between API calls
        tracker: RecommendationTracker instance (created if None)
        save_recommendations: Whether to save to tracking database
    """
    portfolio = []
    num_stocks = len(tickers)
    per_stock_capital = target_capital / num_stocks

    # Initialize tracker and create scan record
    scan_id = None
    if save_recommendations:
        if tracker is None:
            tracker = RecommendationTracker()

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
        scan_id = tracker.record_scan(scan_date, tickers, target_capital, filter_params)

    for i, ticker in enumerate(tickers):
        print(f"\nProcessing {ticker} ({i+1}/{num_stocks})...")

        # Add delay between stocks to avoid rate limiting
        if i > 0:
            time.sleep(delay_between_stocks)

        candidates = find_ditm_calls(client, ticker)
        if candidates.empty:
            print(f"  No qualifying DITM calls for {ticker}.")
            continue

        top = candidates.iloc[0]  # Lowest score = most conservative

        # Get current stock price for comparison
        quote_resp = client.get_quote(ticker)
        S = quote_resp.json()[ticker]["quote"]["lastPrice"]

        # Position sizing: Max whole contracts affordable per stock
        contract_cost = top["Mid"] * 100
        contracts = int(per_stock_capital / contract_cost)  # Whole contracts only
        total_cost = contracts * contract_cost
        equiv_shares = contracts * top["Delta"] * 100  # Delta-adjusted exposure

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
            "Total Cost": round(total_cost, 2),
            "Equiv Shares": round(equiv_shares),
            "Score": round(top["Score"], 3)
        })

        # Save recommendation to tracker
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
                total_cost=total_cost,
                equiv_shares=equiv_shares,
                score=top["Score"]
            )

    df = pd.DataFrame(portfolio)
    if not df.empty:
        df["Allocation %"] = (df["Total Cost"] / df["Total Cost"].sum() * 100).round(2)
        total_cost_port = df["Total Cost"].sum()
        total_equiv = df["Equiv Shares"].sum()

        print(f"\n{'=' * 70}")
        print(f"PORTFOLIO SUMMARY")
        print(f"{'=' * 70}")
        print(f"Total Invested: ${total_cost_port:,.2f} (of ${target_capital:,.2f} target)")
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
    print(f"Target capital: $50,000")
    print(f"Filters: Delta {MIN_DELTA}-{MAX_DELTA}, DTE >{MIN_DTE}, IV <{MAX_IV}")
    print("=" * 70)

    portfolio = build_ditm_portfolio(client, stocks, target_capital=50000)

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
