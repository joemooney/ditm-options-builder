#!/usr/bin/env python3
"""
Recommendation Tracker for DITM Options Portfolio Builder
Stores historical recommendations and tracks their performance over time.
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import numpy as np


class RecommendationTracker:
    """Tracks DITM option recommendations and their performance over time."""

    def __init__(self, db_path: str = "./recommendations_history.json"):
        self.db_path = Path(db_path)
        self.recommendations = self._load_database()

    def _load_database(self) -> Dict:
        """Load existing recommendation database or create new one."""
        if self.db_path.exists():
            with open(self.db_path, 'r') as f:
                return json.load(f)
        return {
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            },
            "scans": {},
            "recommendations": []
        }

    def _save_database(self):
        """Save recommendation database to disk."""
        self.recommendations["metadata"]["last_updated"] = datetime.now().isoformat()
        with open(self.db_path, 'w') as f:
            json.dump(self.recommendations, f, indent=2, default=str)

    def record_scan(self, scan_date: str, tickers: List[str],
                    target_capital: float, filter_params: Dict):
        """
        Record a new scan session.

        Args:
            scan_date: ISO format date string
            tickers: List of ticker symbols scanned
            target_capital: Target portfolio capital
            filter_params: Dictionary of filter parameters used
        """
        scan_id = f"scan_{scan_date.replace('-', '').replace(':', '').replace(' ', '_')}"

        self.recommendations["scans"][scan_id] = {
            "scan_date": scan_date,
            "tickers": tickers,
            "target_capital": target_capital,
            "filter_params": filter_params,
            "recommendations_count": 0
        }

        return scan_id

    def add_recommendation(self, scan_id: str, ticker: str,
                          stock_price: float, strike: float,
                          expiration: str, dte: int,
                          premium_bid: float, premium_ask: float,
                          premium_mid: float,
                          delta: float, iv: float, intrinsic_pct: float,
                          oi: int, spread_pct: float,
                          cost_per_share: float, contracts: int,
                          total_cost: float, equiv_shares: float,
                          score: float):
        """
        Record a single option recommendation.

        Args:
            scan_id: ID of the scan session
            ticker: Stock symbol
            stock_price: Current stock price at recommendation time
            strike: Option strike price
            expiration: Expiration date (YYYY-MM-DD)
            dte: Days to expiration
            premium_bid: Bid price
            premium_ask: Ask price
            premium_mid: Mid price (used for calculations)
            delta: Option delta
            iv: Implied volatility
            intrinsic_pct: Intrinsic value percentage
            oi: Open interest
            spread_pct: Bid-ask spread percentage
            cost_per_share: Cost per delta-adjusted share
            contracts: Recommended number of contracts
            total_cost: Total position cost
            equiv_shares: Delta-adjusted share equivalents
            score: Conservatism score
        """
        recommendation = {
            "id": f"{scan_id}_{ticker}_{strike}_{expiration}",
            "scan_id": scan_id,
            "recommendation_date": self.recommendations["scans"][scan_id]["scan_date"],

            # Stock info
            "ticker": ticker,
            "stock_price_at_rec": stock_price,

            # Option details
            "option_type": "CALL",
            "strike": strike,
            "expiration": expiration,
            "dte_at_rec": dte,

            # Pricing at recommendation
            "premium_bid": premium_bid,
            "premium_ask": premium_ask,
            "premium_mid": premium_mid,

            # Greeks and metrics
            "delta_at_rec": delta,
            "iv_at_rec": iv,
            "intrinsic_pct_at_rec": intrinsic_pct,
            "oi_at_rec": oi,
            "spread_pct_at_rec": spread_pct,

            # Position sizing
            "cost_per_share": cost_per_share,
            "contracts_recommended": contracts,
            "total_cost": total_cost,
            "equiv_shares": equiv_shares,
            "score": score,

            # Performance tracking (to be updated)
            "status": "open",  # open, expired, closed
            "current_value": None,
            "current_stock_price": None,
            "current_delta": None,
            "unrealized_pnl": None,
            "unrealized_pnl_pct": None,
            "last_updated": None,

            # Historical snapshots
            "snapshots": []
        }

        self.recommendations["recommendations"].append(recommendation)
        self.recommendations["scans"][scan_id]["recommendations_count"] += 1
        self._save_database()

        return recommendation["id"]

    def update_recommendation_value(self, client, rec_id: str) -> Dict:
        """
        Update current value of a recommendation using live market data.

        Args:
            client: Schwab API client
            rec_id: Recommendation ID

        Returns:
            Dictionary with updated values
        """
        # Find the recommendation
        rec = None
        for r in self.recommendations["recommendations"]:
            if r["id"] == rec_id:
                rec = r
                break

        if not rec:
            raise ValueError(f"Recommendation {rec_id} not found")

        # Check if expired
        exp_date = datetime.strptime(rec["expiration"], "%Y-%m-%d")
        if datetime.now() > exp_date:
            rec["status"] = "expired"
            rec["current_value"] = 0.0
            rec["unrealized_pnl"] = -rec["total_cost"]
            rec["unrealized_pnl_pct"] = -100.0
            self._save_database()
            return rec

        try:
            # Get current stock price
            quote_resp = client.get_quote(rec["ticker"])
            if quote_resp.status_code != 200:
                print(f"Failed to get quote for {rec['ticker']}")
                return rec

            quote_data = quote_resp.json()
            current_stock_price = quote_data[rec["ticker"]]["quote"]["lastPrice"]

            # Get current option price
            import schwab
            options_resp = client.get_option_chain(
                rec["ticker"],
                contract_type=schwab.client.Client.Options.ContractType.CALL,
                strike=rec["strike"],
                from_date=datetime.strptime(rec["expiration"], "%Y-%m-%d"),
                to_date=datetime.strptime(rec["expiration"], "%Y-%m-%d")
            )

            if options_resp.status_code != 200:
                print(f"Failed to get options for {rec['ticker']}")
                return rec

            options_data = options_resp.json()

            # Find the specific contract
            call_exp_map = options_data.get("callExpDateMap", {})

            current_premium = None
            current_delta = None

            for exp_date_str, strikes in call_exp_map.items():
                if rec["expiration"] in exp_date_str:
                    strike_str = str(float(rec["strike"]))
                    if strike_str in strikes:
                        contracts = strikes[strike_str]
                        if contracts:
                            contract = contracts[0]
                            bid = contract.get("bid", 0)
                            ask = contract.get("ask", 0)
                            if bid > 0 and ask > 0:
                                current_premium = (bid + ask) / 2.0
                                current_delta = contract.get("delta", rec["delta_at_rec"])
                            break

            if current_premium is None:
                print(f"Could not find current price for {rec['ticker']} {rec['strike']} {rec['expiration']}")
                return rec

            # Calculate current values
            current_value = current_premium * rec["contracts_recommended"] * 100
            unrealized_pnl = current_value - rec["total_cost"]
            unrealized_pnl_pct = (unrealized_pnl / rec["total_cost"]) * 100 if rec["total_cost"] > 0 else 0

            # Update recommendation
            rec["current_value"] = round(current_value, 2)
            rec["current_stock_price"] = round(current_stock_price, 2)
            rec["current_delta"] = round(current_delta, 4) if current_delta else None
            rec["unrealized_pnl"] = round(unrealized_pnl, 2)
            rec["unrealized_pnl_pct"] = round(unrealized_pnl_pct, 2)
            rec["last_updated"] = datetime.now().isoformat()

            # Add snapshot
            snapshot = {
                "timestamp": datetime.now().isoformat(),
                "stock_price": current_stock_price,
                "option_premium": current_premium,
                "delta": current_delta,
                "value": current_value,
                "pnl": unrealized_pnl,
                "pnl_pct": unrealized_pnl_pct
            }
            rec["snapshots"].append(snapshot)

            self._save_database()

        except Exception as e:
            print(f"Error updating {rec_id}: {e}")

        return rec

    def update_all_open_recommendations(self, client):
        """Update all open recommendations with current market data."""
        open_recs = [r for r in self.recommendations["recommendations"]
                     if r["status"] == "open"]

        print(f"\nUpdating {len(open_recs)} open recommendations...")

        for i, rec in enumerate(open_recs, 1):
            print(f"  [{i}/{len(open_recs)}] {rec['ticker']} {rec['strike']} {rec['expiration']}")
            self.update_recommendation_value(client, rec["id"])

        print(f"✓ Updated {len(open_recs)} recommendations\n")

    def get_performance_summary(self) -> pd.DataFrame:
        """
        Generate performance summary of all recommendations.

        Returns:
            DataFrame with performance metrics
        """
        if not self.recommendations["recommendations"]:
            return pd.DataFrame()

        rows = []
        for rec in self.recommendations["recommendations"]:
            # Calculate days held
            rec_date = datetime.fromisoformat(rec["recommendation_date"])

            if rec["status"] == "expired":
                days_held = (datetime.strptime(rec["expiration"], "%Y-%m-%d") - rec_date).days
            else:
                days_held = (datetime.now() - rec_date).days

            # Stock performance for comparison
            stock_return_pct = None
            if rec.get("current_stock_price"):
                stock_return_pct = ((rec["current_stock_price"] - rec["stock_price_at_rec"])
                                   / rec["stock_price_at_rec"] * 100)

            # Calculate DTE safely
            exp_date = datetime.strptime(rec["expiration"], "%Y-%m-%d")
            dte = max(0, (exp_date - datetime.now()).days)

            # Handle None values properly
            current_value = rec.get("current_value") or 0
            unrealized_pnl = rec.get("unrealized_pnl") or 0
            unrealized_pnl_pct = rec.get("unrealized_pnl_pct") or 0
            current_stock_price = rec.get("current_stock_price") or 0

            current_price = current_value / (rec["contracts_recommended"] * 100) if rec["contracts_recommended"] > 0 else 0

            rows.append({
                "Rec_Date": rec["recommendation_date"][:10],
                "Ticker": rec["ticker"],
                "Strike": rec["strike"],
                "Expiration": rec["expiration"],
                "Status": rec["status"],
                "Days_Held": days_held,
                "DTE": dte,
                "Entry_Price": rec["premium_mid"],  # Still use mid for display consistency
                "Entry_Bid": rec["premium_bid"],     # Store bid for spread analysis
                "Entry_Ask": rec["premium_ask"],     # Store ask for realistic breakeven
                "Entry_Mid": rec["premium_mid"],     # Store mid for reference
                "Current_Price": current_price,
                "Contracts": rec["contracts_recommended"],
                "Total_Cost": rec["total_cost"],
                "Current_Value": current_value,
                "P&L": unrealized_pnl,
                "P&L_%": unrealized_pnl_pct,
                "Stock_Entry": rec["stock_price_at_rec"],
                "Stock_Current": current_stock_price,
                "Stock_Return_%": stock_return_pct,
                "Delta_Entry": rec["delta_at_rec"],
                "Delta_Current": rec.get("current_delta"),
                "Score": rec["score"]
            })

        return pd.DataFrame(rows)

    def calculate_risk_metrics(self) -> Dict:
        """
        Calculate comprehensive risk metrics for the portfolio.

        Returns:
            Dictionary with risk metrics
        """
        df = self.get_performance_summary()

        if df.empty:
            return {}

        metrics = {}

        # Basic return statistics
        returns = df["P&L_%"].values
        metrics["total_positions"] = len(returns)
        metrics["mean_return"] = np.mean(returns)
        metrics["median_return"] = np.median(returns)
        metrics["std_return"] = np.std(returns, ddof=1) if len(returns) > 1 else 0
        metrics["min_return"] = np.min(returns)
        metrics["max_return"] = np.max(returns)

        # Maximum Drawdown
        # For each position, track cumulative returns and find max peak-to-trough
        df_sorted = df.sort_values("Rec_Date")
        cumulative_returns = (1 + df_sorted["P&L_%"] / 100).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max * 100
        metrics["max_drawdown"] = abs(drawdown.min()) if len(drawdown) > 0 else 0

        # Alternative: Simple max loss
        metrics["max_single_loss"] = abs(df[df["P&L_%"] < 0]["P&L_%"].min()) if len(df[df["P&L_%"] < 0]) > 0 else 0

        # Sharpe Ratio (annualized)
        # Assuming risk-free rate of 4% annually
        risk_free_rate = 4.0
        avg_days_held = df["Days_Held"].mean()

        # Handle None/NaN values
        if pd.isna(avg_days_held):
            avg_days_held = 0

        if avg_days_held > 0 and metrics["std_return"] > 0:
            # Annualize the return
            annualization_factor = 365 / avg_days_held
            annualized_return = metrics["mean_return"] * annualization_factor
            annualized_std = metrics["std_return"] * np.sqrt(annualization_factor)

            metrics["sharpe_ratio"] = (annualized_return - risk_free_rate) / annualized_std
        else:
            metrics["sharpe_ratio"] = 0

        # Sortino Ratio (uses downside deviation instead of total std)
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 1:
            downside_std = np.std(downside_returns, ddof=1)
            annualized_downside_std = downside_std * np.sqrt(365 / avg_days_held) if avg_days_held > 0 else 0

            if annualized_downside_std > 0:
                annualized_return = metrics["mean_return"] * (365 / avg_days_held) if avg_days_held > 0 else 0
                metrics["sortino_ratio"] = (annualized_return - risk_free_rate) / annualized_downside_std
            else:
                metrics["sortino_ratio"] = 0
        else:
            metrics["sortino_ratio"] = 0

        # Win Rate
        winners = len(df[df["P&L_%"] > 0])
        losers = len(df[df["P&L_%"] < 0])
        metrics["win_rate"] = (winners / len(df) * 100) if len(df) > 0 else 0
        metrics["winners"] = winners
        metrics["losers"] = losers

        # Profit Factor (gross profits / gross losses)
        gross_profit = df[df["P&L"] > 0]["P&L"].sum()
        gross_loss = abs(df[df["P&L"] < 0]["P&L"].sum())
        metrics["profit_factor"] = gross_profit / gross_loss if gross_loss > 0 else float('inf')

        # Average Win vs Average Loss
        if winners > 0:
            metrics["avg_win"] = df[df["P&L_%"] > 0]["P&L_%"].mean()
            metrics["avg_win_dollars"] = df[df["P&L"] > 0]["P&L"].mean()
        else:
            metrics["avg_win"] = 0
            metrics["avg_win_dollars"] = 0

        if losers > 0:
            metrics["avg_loss"] = abs(df[df["P&L_%"] < 0]["P&L_%"].mean())
            metrics["avg_loss_dollars"] = abs(df[df["P&L"] < 0]["P&L"].mean())
        else:
            metrics["avg_loss"] = 0
            metrics["avg_loss_dollars"] = 0

        # Expectancy (average $ per trade)
        expectancy = df["P&L"].mean()
        metrics["expectancy"] = float(expectancy) if not pd.isna(expectancy) else 0.0

        # Recovery Factor (net profit / max drawdown)
        total_pnl = df["P&L"].sum()
        total_cost_mean = df["Total_Cost"].mean()
        if pd.isna(total_cost_mean):
            total_cost_mean = 0
        metrics["recovery_factor"] = total_pnl / (metrics["max_single_loss"] * total_cost_mean / 100) if metrics["max_single_loss"] > 0 and total_cost_mean > 0 else float('inf')

        # Calmar Ratio (annualized return / max drawdown)
        if avg_days_held > 0 and metrics["max_drawdown"] > 0:
            annualized_return = metrics["mean_return"] * (365 / avg_days_held)
            metrics["calmar_ratio"] = annualized_return / metrics["max_drawdown"]
        else:
            metrics["calmar_ratio"] = 0

        # Consecutive wins/losses
        results = (df.sort_values("Rec_Date")["P&L_%"] > 0).astype(int)
        if len(results) > 0:
            max_consecutive_wins = 0
            max_consecutive_losses = 0
            current_streak = 0
            current_type = None

            for is_win in results:
                if is_win == current_type:
                    current_streak += 1
                else:
                    if current_type == 1:
                        max_consecutive_wins = max(max_consecutive_wins, current_streak)
                    elif current_type == 0:
                        max_consecutive_losses = max(max_consecutive_losses, current_streak)
                    current_type = is_win
                    current_streak = 1

            # Check final streak
            if current_type == 1:
                max_consecutive_wins = max(max_consecutive_wins, current_streak)
            elif current_type == 0:
                max_consecutive_losses = max(max_consecutive_losses, current_streak)

            metrics["max_consecutive_wins"] = max_consecutive_wins
            metrics["max_consecutive_losses"] = max_consecutive_losses
        else:
            metrics["max_consecutive_wins"] = 0
            metrics["max_consecutive_losses"] = 0

        return metrics

    def generate_report(self, client=None, update_values: bool = True) -> str:
        """
        Generate a comprehensive performance report.

        Args:
            client: Schwab API client (required if update_values=True)
            update_values: Whether to update with current market data

        Returns:
            Formatted report string
        """
        if update_values and client:
            self.update_all_open_recommendations(client)

        df = self.get_performance_summary()

        if df.empty:
            return "No recommendations tracked yet."

        # Overall statistics
        total_recs = len(df)
        open_recs = len(df[df["Status"] == "open"])
        expired_recs = len(df[df["Status"] == "expired"])

        total_invested = df["Total_Cost"].sum()
        current_value = df["Current_Value"].sum()
        total_pnl = df["P&L"].sum()
        total_pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0

        # Winners vs losers
        winners = len(df[df["P&L"] > 0])
        losers = len(df[df["P&L"] < 0])
        win_rate = (winners / total_recs * 100) if total_recs > 0 else 0

        # Average metrics
        avg_return = df["P&L_%"].mean()
        avg_days_held = df["Days_Held"].mean()

        # Build report
        report = []
        report.append("=" * 80)
        report.append("DITM OPTIONS RECOMMENDATION PERFORMANCE REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Database: {self.db_path}")
        report.append("")

        report.append("PORTFOLIO OVERVIEW")
        report.append("-" * 80)
        report.append(f"Total Recommendations:     {total_recs}")
        report.append(f"  Open Positions:          {open_recs}")
        report.append(f"  Expired Positions:       {expired_recs}")
        report.append("")
        report.append(f"Total Capital Invested:    ${total_invested:,.2f}")
        report.append(f"Current Portfolio Value:   ${current_value:,.2f}")
        report.append(f"Total P&L:                 ${total_pnl:,.2f} ({total_pnl_pct:+.2f}%)")
        report.append("")

        report.append("PERFORMANCE METRICS")
        report.append("-" * 80)
        report.append(f"Win Rate:                  {win_rate:.1f}% ({winners}W / {losers}L)")
        report.append(f"Average Return:            {avg_return:+.2f}%")
        report.append(f"Average Holding Period:    {avg_days_held:.0f} days")
        report.append("")

        if not df[df["Stock_Return_%"].notna()].empty:
            report.append("LEVERAGE ANALYSIS")
            report.append("-" * 80)
            avg_stock_return = df[df["Stock_Return_%"].notna()]["Stock_Return_%"].mean()
            avg_option_return = df[df["Stock_Return_%"].notna()]["P&L_%"].mean()
            leverage_factor = avg_option_return / avg_stock_return if avg_stock_return != 0 else 0
            report.append(f"Average Stock Return:      {avg_stock_return:+.2f}%")
            report.append(f"Average Option Return:     {avg_option_return:+.2f}%")
            report.append(f"Effective Leverage:        {leverage_factor:.2f}x")
            report.append("")

        # Calculate and display risk metrics
        risk_metrics = self.calculate_risk_metrics()
        if risk_metrics:
            report.append("RISK METRICS")
            report.append("-" * 80)
            report.append(f"Sharpe Ratio:              {risk_metrics['sharpe_ratio']:.2f}")
            report.append(f"Sortino Ratio:             {risk_metrics['sortino_ratio']:.2f}")
            report.append(f"Max Drawdown:              {risk_metrics['max_drawdown']:.2f}%")
            report.append(f"Max Single Loss:           {risk_metrics['max_single_loss']:.2f}%")
            report.append(f"Calmar Ratio:              {risk_metrics['calmar_ratio']:.2f}")
            report.append(f"Profit Factor:             {risk_metrics['profit_factor']:.2f}")
            report.append("")
            report.append(f"Average Win:               {risk_metrics['avg_win']:+.2f}% (${risk_metrics['avg_win_dollars']:,.2f})")
            report.append(f"Average Loss:              -{risk_metrics['avg_loss']:.2f}% (${risk_metrics['avg_loss_dollars']:,.2f})")
            report.append(f"Win/Loss Ratio:            {risk_metrics['avg_win']/risk_metrics['avg_loss'] if risk_metrics['avg_loss'] > 0 else float('inf'):.2f}")
            report.append(f"Expectancy (avg $ per trade): ${risk_metrics['expectancy']:,.2f}")
            report.append("")
            report.append(f"Return Std Dev:            {risk_metrics['std_return']:.2f}%")
            report.append(f"Best Trade:                {risk_metrics['max_return']:+.2f}%")
            report.append(f"Worst Trade:               {risk_metrics['min_return']:+.2f}%")
            report.append(f"Max Consecutive Wins:      {risk_metrics['max_consecutive_wins']}")
            report.append(f"Max Consecutive Losses:    {risk_metrics['max_consecutive_losses']}")
            report.append("")

        report.append("TOP PERFORMERS")
        report.append("-" * 80)
        top_performers = df.nlargest(5, "P&L_%")[["Ticker", "Strike", "Expiration", "P&L_%", "P&L"]]
        report.append(top_performers.to_string(index=False))
        report.append("")

        report.append("WORST PERFORMERS")
        report.append("-" * 80)
        worst_performers = df.nsmallest(5, "P&L_%")[["Ticker", "Strike", "Expiration", "P&L_%", "P&L"]]
        report.append(worst_performers.to_string(index=False))
        report.append("")

        report.append("CURRENT OPEN POSITIONS")
        report.append("-" * 80)
        open_positions = df[df["Status"] == "open"][["Ticker", "Strike", "Expiration", "Days_Held",
                                                       "Total_Cost", "Current_Value", "P&L", "P&L_%"]]
        if not open_positions.empty:
            report.append(open_positions.to_string(index=False))
        else:
            report.append("No open positions")
        report.append("")

        report.append("=" * 80)

        return "\n".join(report)

    def export_to_csv(self, filename: str = None):
        """Export performance data to CSV."""
        if filename is None:
            filename = f"ditm_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        df = self.get_performance_summary()
        df.to_csv(filename, index=False)
        print(f"✓ Performance data exported to: {filename}")

        return filename
