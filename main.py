#!/bin/env python3
import yfinance as yf
import pandas as pd
from datetime import datetime
import numpy as np
from scipy.stats import norm

# -------------------------------------------------
# CONFIGURATION
# -------------------------------------------------
MIN_DELTA         = 0.70          # Allow 70-90 delta range
MAX_DELTA         = 0.90          # Transcript prefers ≤90
MIN_INTRINSIC_PCT = 0.70          # At least 70% intrinsic value
MAX_EXTRINSIC_PCT = 0.30          # CRITICAL: Max 30% extrinsic (prefer 20%)
MIN_DTE           = 15            # Match average holding period
PREFERRED_DTE     = 21            # Target expiration window
MAX_DTE           = 45            # Don't overpay for time
MAX_IV            = 0.30
MAX_SPREAD_PCT    = 0.02          # 2% max spread
MAX_BID_ASK_ABS   = 1.00          # $1.00 max absolute spread (prefer $0.50)
MIN_OI            = 250           # Minimum open interest
MIN_LEVERAGE      = 7.0           # Minimum leverage factor
RISK_FREE_RATE    = 0.04          # approximate Treasury yield

# -------------------------------------------------
# HELPER: Black-Scholes delta for a call
# -------------------------------------------------
def bs_call_delta(S, K, T, r, sigma):
    if T <= 0: return 1.0 if S > K else 0.0
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    return norm.cdf(d1)

# -------------------------------------------------
# SINGLE STOCK FUNCTION (unchanged)
# -------------------------------------------------
def find_ditm_calls(ticker: str, as_of: str = None) -> pd.DataFrame:
    """
    Returns a DataFrame of deep-in-the-money call candidates.
    """
    stock = yf.Ticker(ticker)
    S = stock.history(period="1d")["Close"].iloc[-1]      # current price

    # Get all option chains
    expirations = stock.options
    rows = []

    for exp in expirations:
        opt = stock.option_chain(exp)
        calls = opt.calls

        # Parse expiration date
        exp_date = datetime.strptime(exp, "%Y-%m-%d")
        T = (exp_date - datetime.now()).days / 365.0
        dte = int(T * 365)

        # Filter by DTE range
        if dte < MIN_DTE or dte > MAX_DTE:
            continue

        for _, row in calls.iterrows():
            K   = row.strike
            bid = row.bid
            ask = row.ask
            mid = (bid + ask) / 2.0
            iv  = row.impliedVolatility
            oi  = row.openInterest

            # ---- liquidity filters ----
            if oi < MIN_OI: continue
            if bid <= 0 or ask <= 0: continue

            # Spread filters (both percentage and absolute)
            spread_abs = ask - bid
            spread_pct = spread_abs / mid if mid > 0 else 999
            if spread_pct > MAX_SPREAD_PCT: continue
            if spread_abs > MAX_BID_ASK_ABS: continue

            # ---- intrinsic and extrinsic value ----
            intrinsic = max(S - K, 0)
            if intrinsic == 0: continue

            extrinsic = ask - intrinsic  # Use ASK price for extrinsic
            extrinsic_pct = extrinsic / ask if ask > 0 else 999
            intrinsic_pct = intrinsic / ask if ask > 0 else 0

            # CRITICAL FILTER: Extrinsic value percentage
            if extrinsic_pct > MAX_EXTRINSIC_PCT: continue
            if intrinsic_pct < MIN_INTRINSIC_PCT: continue

            # ---- delta (use BS if IV missing) ----
            sigma = iv if not np.isnan(iv) else 0.30
            delta = bs_call_delta(S, K, T, RISK_FREE_RATE, sigma)

            if not (MIN_DELTA <= delta <= MAX_DELTA):
                continue

            # ---- IV filter ----
            if sigma > MAX_IV:
                continue

            # ---- Leverage factor ----
            leverage = S / ask if ask > 0 else 0
            if leverage < MIN_LEVERAGE:
                continue

            # ---- cost vs. stock ----
            shares_equiv = delta * 100
            cost_per_share = ask / shares_equiv if shares_equiv > 0 else 999

            # Calculate key metrics
            breakeven = K + ask
            risk_dollars = ask * 100
            stock_cost = S * 100
            savings = stock_cost - risk_dollars

            rows.append({
                "Expiration": exp,
                "Strike": K,
                "DTE": dte,
                "Bid": bid,
                "Ask": ask,
                "Spread$": spread_abs,
                "Spread%": spread_pct,
                "IV": sigma,
                "Delta": delta,
                "Intrinsic%": intrinsic_pct,
                "Extrinsic%": extrinsic_pct,
                "Leverage": leverage,
                "Breakeven": breakeven,
                "Risk$": risk_dollars,
                "Stock$": stock_cost,
                "Savings$": savings,
                "Cost/Share": cost_per_share,
                "OI": oi,
            })

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    # ---- ranking score (lower = better) ----
    # Prioritize: low extrinsic%, high leverage, high delta, low spread
    df["Score"] = (
        0.35 * df["Extrinsic%"] / MAX_EXTRINSIC_PCT +  # MOST IMPORTANT
        0.25 * (1 - df["Delta"]) +                      # prefer higher delta
        0.20 * (1 / df["Leverage"]) * 10 +              # prefer higher leverage
        0.10 * df["IV"] / MAX_IV +                      # penalize high IV
        0.10 * df["Spread%"] / MAX_SPREAD_PCT           # penalize wide spreads
    )
    df = df.sort_values("Score").reset_index(drop=True)
    return df

# -------------------------------------------------
# NEW: PORTFOLIO BUILDER
# -------------------------------------------------
def build_ditm_portfolio(tickers: list, target_capital: float = 50000) -> pd.DataFrame:
    """
    Builds a conservative DITM call portfolio across multiple stocks.
    Allocates equally (e.g., $10k per stock for $50k total).
    Returns summary DataFrame.
    """
    portfolio = []
    num_stocks = len(tickers)
    per_stock_capital = target_capital / num_stocks
    
    for ticker in tickers:
        candidates = find_ditm_calls(ticker)
        if candidates.empty:
            print(f"No qualifying DITM calls for {ticker}.")
            continue
            
        top = candidates.iloc[0]  # Lowest score = most conservative
        stock = yf.Ticker(ticker)
        S = stock.history(period="1d")["Close"].iloc[-1]
        
        # Position sizing: Max whole contracts affordable per stock
        contract_cost = top["Ask"] * 100  # Use ASK price for realistic cost
        contracts = int(per_stock_capital / contract_cost)  # Whole contracts only

        if contracts == 0:
            print(f"Skipping {ticker}: Insufficient capital for even 1 contract.")
            continue

        total_cost = contracts * contract_cost
        equiv_shares = contracts * top["Delta"] * 100  # Delta-adjusted exposure
        total_leverage = (equiv_shares * S) / total_cost if total_cost > 0 else 0

        portfolio.append({
            "Ticker": ticker,
            "Strike": top["Strike"],
            "Expiration": top["Expiration"],
            "DTE": top["DTE"],
            "Delta": round(top["Delta"], 3),
            "Extrinsic%": round(top["Extrinsic%"] * 100, 1),
            "Leverage": round(top["Leverage"], 1),
            "Breakeven": round(top["Breakeven"], 2),
            "Contracts": contracts,
            "Cost": round(total_cost, 2),
            "Stock Cost": round(equiv_shares * S, 2),
            "Savings": round((equiv_shares * S) - total_cost, 2),
            "Total Lev": round(total_leverage, 1),
            "Score": round(top["Score"], 3)
        })
    
    df = pd.DataFrame(portfolio)
    if not df.empty:
        df["Allocation %"] = (df["Cost"] / df["Cost"].sum() * 100).round(2)
        total_cost = df["Cost"].sum()
        total_stock_cost = df["Stock Cost"].sum()
        total_savings = df["Savings"].sum()
        avg_leverage = total_stock_cost / total_cost if total_cost > 0 else 0

        print(f"\n{'='*70}")
        print(f"DITM PORTFOLIO SUMMARY")
        print(f"{'='*70}")
        print(f"Total Capital Deployed:    ${total_cost:>12,.2f} (of ${target_capital:,.2f} target)")
        print(f"Equivalent Stock Cost:     ${total_stock_cost:>12,.2f}")
        print(f"Total Savings:             ${total_savings:>12,.2f}")
        print(f"Average Leverage Factor:   {avg_leverage:>12.1f}x")
        print(f"Capital Efficiency:        {(total_cost/total_stock_cost*100):>11.1f}%")
        print(f"{'='*70}\n")

    return df.sort_values("Score")  # Sort by conservatism

# -------------------------------------------------
# COMPARISON TOOL: Option vs Stock Returns
# -------------------------------------------------
def compare_returns(ticker: str, stock_price_targets: list = None) -> pd.DataFrame:
    """
    Compare returns between buying DITM options vs buying stock
    at various price targets.

    Args:
        ticker: Stock symbol
        stock_price_targets: List of price increase percentages (e.g., [5, 10, 20, 37])
                            If None, defaults to [5, 10, 20, 30, 40, 50]

    Returns:
        DataFrame comparing option vs stock returns
    """
    if stock_price_targets is None:
        stock_price_targets = [5, 10, 20, 30, 40, 50]

    # Get current stock price
    stock = yf.Ticker(ticker)
    S = stock.history(period="1d")["Close"].iloc[-1]

    # Get best DITM option
    candidates = find_ditm_calls(ticker)
    if candidates.empty:
        print(f"No qualifying DITM options found for {ticker}")
        return pd.DataFrame()

    best = candidates.iloc[0]

    # Calculate comparison data
    results = []
    option_ask = best["Ask"]
    delta = best["Delta"]
    leverage = best["Leverage"]

    print(f"\n{'='*70}")
    print(f"OPTION vs STOCK RETURN COMPARISON: {ticker}")
    print(f"{'='*70}")
    print(f"Current Stock Price:     ${S:.2f}")
    print(f"Option Strike:           ${best['Strike']:.2f}")
    print(f"Option Ask:              ${option_ask:.2f}")
    print(f"Delta:                   {delta:.3f}")
    print(f"Leverage Factor:         {leverage:.1f}x")
    print(f"Extrinsic Value:         {best['Extrinsic%']*100:.1f}%")
    print(f"Break-Even:              ${best['Breakeven']:.2f}")
    print(f"DTE:                     {best['DTE']} days")
    print(f"{'='*70}\n")

    for pct_increase in stock_price_targets:
        new_price = S * (1 + pct_increase / 100)
        stock_gain = new_price - S
        stock_gain_pct = pct_increase

        # Option gain (simplified: delta * stock move)
        option_gain = stock_gain * delta
        option_gain_pct = (option_gain / option_ask) * 100

        # Investment amounts (per 100 shares)
        stock_investment = S * 100
        option_investment = option_ask * 100

        # Dollar gains
        stock_dollar_gain = stock_gain * 100
        option_dollar_gain = option_gain * 100

        results.append({
            "Stock +%": f"{pct_increase}%",
            "New Price": f"${new_price:.2f}",
            "Stock Gain%": f"{stock_gain_pct:.1f}%",
            "Option Gain%": f"{option_gain_pct:.1f}%",
            "Stock $ Gain": f"${stock_dollar_gain:,.0f}",
            "Option $ Gain": f"${option_dollar_gain:,.0f}",
            "Stock Investment": f"${stock_investment:,.0f}",
            "Option Investment": f"${option_investment:,.0f}",
            "Multiplier": f"{option_gain_pct/stock_gain_pct:.2f}x"
        })

    return pd.DataFrame(results)

# -------------------------------------------------
# EXAMPLE USAGE
# -------------------------------------------------
if __name__ == "__main__":
    stocks = ["AAPL", "MSFT", "GOOGL", "JNJ", "JPM"]  # Conservative blue-chips
    portfolio = build_ditm_portfolio(stocks, target_capital=50000)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 150)
    print(portfolio)

    # Show comparison for first stock
    if not portfolio.empty:
        print("\n" + "="*70)
        print("EXAMPLE: Option vs Stock Returns Comparison")
        print("="*70)
        comparison = compare_returns(portfolio.iloc[0]["Ticker"])
        print(comparison.to_string(index=False))
