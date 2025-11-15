#!/usr/bin/env python3
"""
SQLite-based Recommendation Tracker for DITM Options Portfolio Builder
Stores scans, recommendations, and ALL qualifying candidates for analysis.
"""
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


class RecommendationTrackerDB:
    """Tracks DITM option recommendations using SQLite database."""

    def __init__(self, db_path: str = "./recommendations.db"):
        self.db_path = Path(db_path)
        self.conn = None
        self._initialize_database()

    def _initialize_database(self):
        """Initialize database and create tables if needed."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Enable column access by name

        # Read and execute schema
        schema_path = Path(__file__).parent / "db_schema.sql"
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
            self.conn.executescript(schema_sql)
        self.conn.commit()

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # ========================================================================
    # SCAN MANAGEMENT
    # ========================================================================

    def record_scan(self, scan_date: str, tickers: List[str],
                    filter_params: Dict, preset_name: str = None) -> str:
        """
        Record a new scan session.

        Args:
            scan_date: ISO format datetime string
            tickers: List of ticker symbols scanned
            filter_params: Dictionary of filter parameters used
            preset_name: Name of the preset used (if any)

        Returns:
            scan_id: Unique identifier for this scan
        """
        scan_id = f"scan_{scan_date.replace('-', '').replace(':', '').replace(' ', '').replace('T', '')}"

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO scans (scan_id, scan_date, preset_name, tickers, filter_params)
            VALUES (?, ?, ?, ?, ?)
        """, (
            scan_id,
            scan_date,
            preset_name,
            json.dumps(tickers),
            json.dumps(filter_params)
        ))
        self.conn.commit()

        return scan_id

    def get_scan_info(self, scan_id: str) -> Optional[Dict]:
        """Get scan information by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM scans WHERE scan_id = ?", (scan_id,))
        row = cursor.fetchone()

        if row:
            return {
                'scan_id': row['scan_id'],
                'scan_date': row['scan_date'],
                'preset_name': row['preset_name'],
                'tickers': json.loads(row['tickers']),
                'filter_params': json.loads(row['filter_params']),
                'recommendations_count': row['recommendations_count'],
                'candidates_count': row['candidates_count']
            }
        return None

    # ========================================================================
    # RECOMMENDATION MANAGEMENT
    # ========================================================================

    def add_recommendation(self, scan_id: str, ticker: str,
                          stock_price: float, strike: float,
                          expiration: str, dte: int,
                          premium_bid: float, premium_ask: float,
                          premium_mid: float,
                          delta: float, iv: float, intrinsic_pct: float,
                          oi: int, spread_pct: float,
                          cost_per_share: float, contracts: int,
                          total_cost: float, equiv_shares: float,
                          score: float,
                          extrinsic_value: float = 0,
                          extrinsic_pct: float = 0) -> str:
        """Record a single option recommendation (top pick from scan)."""

        scan_info = self.get_scan_info(scan_id)
        if not scan_info:
            raise ValueError(f"Scan {scan_id} not found")

        rec_id = f"{scan_id}_{ticker}_{strike}_{expiration}"
        recommendation_date = scan_info['scan_date']

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO recommendations (
                id, scan_id, recommendation_date,
                ticker, stock_price_at_rec,
                option_type, strike, expiration, dte_at_rec,
                premium_bid, premium_ask, premium_mid,
                delta_at_rec, iv_at_rec, intrinsic_pct,
                extrinsic_value, extrinsic_pct,
                contracts_recommended, total_cost, equiv_shares, cost_per_share,
                score, spread_pct, open_interest,
                status, last_updated
            ) VALUES (
                ?, ?, ?,
                ?, ?,
                'CALL', ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?,
                'open', ?
            )
        """, (
            rec_id, scan_id, recommendation_date,
            ticker, stock_price,
            strike, expiration, dte,
            premium_bid, premium_ask, premium_mid,
            delta, iv, intrinsic_pct,
            extrinsic_value, extrinsic_pct,
            contracts, total_cost, equiv_shares, cost_per_share,
            score, spread_pct, oi,
            datetime.now().isoformat()
        ))

        # Update scan recommendations count
        cursor.execute("""
            UPDATE scans
            SET recommendations_count = recommendations_count + 1
            WHERE scan_id = ?
        """, (scan_id,))

        self.conn.commit()
        return rec_id

    def update_recommendation_value(self, rec_id: str, client,
                                    current_bid: float = None,
                                    current_ask: float = None,
                                    current_mid: float = None,
                                    stock_current: float = None,
                                    delta_current: float = None):
        """Update current values for a recommendation."""

        cursor = self.conn.cursor()

        # Get recommendation details
        cursor.execute("SELECT * FROM recommendations WHERE id = ?", (rec_id,))
        rec = cursor.fetchone()
        if not rec:
            return

        contracts = rec['contracts_recommended']
        total_cost = rec['total_cost']

        # Calculate current value and P&L
        if current_mid:
            current_value = current_mid * contracts * 100
            unrealized_pnl = current_value - total_cost
            unrealized_pnl_pct = (unrealized_pnl / total_cost * 100) if total_cost > 0 else 0

            # Update recommendation
            cursor.execute("""
                UPDATE recommendations
                SET current_bid = ?, current_ask = ?, current_mid = ?,
                    stock_current = ?, delta_current = ?,
                    current_value = ?, unrealized_pnl = ?, unrealized_pnl_pct = ?,
                    last_updated = ?
                WHERE id = ?
            """, (
                current_bid, current_ask, current_mid,
                stock_current, delta_current,
                current_value, unrealized_pnl, unrealized_pnl_pct,
                datetime.now().isoformat(),
                rec_id
            ))

            # Add price snapshot
            cursor.execute("""
                INSERT INTO price_snapshots (
                    recommendation_id, timestamp,
                    stock_price, option_bid, option_ask, option_mid,
                    delta, value, pnl, pnl_pct
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rec_id, datetime.now().isoformat(),
                stock_current, current_bid, current_ask, current_mid,
                delta_current, current_value, unrealized_pnl, unrealized_pnl_pct
            ))

            self.conn.commit()

    def get_open_recommendations(self) -> pd.DataFrame:
        """Get all open recommendations."""
        query = "SELECT * FROM v_open_recommendations"
        return pd.read_sql_query(query, self.conn)

    def close_recommendation(self, ticker: str, strike: float,
                            expiration: str, reason: str = "User closed"):
        """Mark a recommendation as closed."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE recommendations
            SET status = 'closed',
                closed_date = ?,
                close_reason = ?
            WHERE ticker = ? AND strike = ? AND expiration = ? AND status = 'open'
        """, (datetime.now().isoformat(), reason, ticker, strike, expiration))
        self.conn.commit()

    # ========================================================================
    # CANDIDATE MANAGEMENT (ALL QUALIFYING OPTIONS)
    # ========================================================================

    def add_candidate(self, scan_id: str, ticker: str, stock_price: float,
                     strike: float, expiration: str, dte: int,
                     bid: float, ask: float, mid: float,
                     delta: float, iv: float,
                     intrinsic: float, intrinsic_pct: float,
                     extrinsic: float, extrinsic_pct: float,
                     score: float, spread_pct: float, oi: int,
                     cost_per_share: float,
                     matched_presets: List[str] = None,
                     recommended: bool = False):
        """
        Record a qualifying option candidate (may or may not be top pick).

        Args:
            All option metrics from scan
            matched_presets: List of preset names this candidate matches
            recommended: True if this was selected as the top recommendation
        """
        scan_info = self.get_scan_info(scan_id)
        if not scan_info:
            raise ValueError(f"Scan {scan_id} not found")

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO candidates (
                scan_id, scan_date, ticker, stock_price,
                strike, expiration, dte,
                bid, ask, mid,
                delta, iv,
                intrinsic, intrinsic_pct,
                extrinsic, extrinsic_pct,
                score, spread_pct, open_interest, cost_per_share,
                matched_presets, recommended
            ) VALUES (
                ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?,
                ?, ?,
                ?, ?,
                ?, ?, ?, ?,
                ?, ?
            )
        """, (
            scan_id, scan_info['scan_date'], ticker, stock_price,
            strike, expiration, dte,
            bid, ask, mid,
            delta, iv,
            intrinsic, intrinsic_pct,
            extrinsic, extrinsic_pct,
            score, spread_pct, oi, cost_per_share,
            json.dumps(matched_presets or []), 1 if recommended else 0
        ))

        # Update scan candidates count
        cursor.execute("""
            UPDATE scans
            SET candidates_count = candidates_count + 1
            WHERE scan_id = ?
        """, (scan_id,))

        self.conn.commit()

    def get_candidates_by_scan(self, scan_id: str) -> pd.DataFrame:
        """Get all candidates from a specific scan."""
        query = """
            SELECT * FROM candidates
            WHERE scan_id = ?
            ORDER BY ticker, score
        """
        return pd.read_sql_query(query, self.conn, params=(scan_id,))

    def get_candidates_by_ticker(self, ticker: str, days: int = 30) -> pd.DataFrame:
        """Get all candidates for a ticker from recent scans."""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        query = """
            SELECT * FROM candidates
            WHERE ticker = ? AND scan_date >= ?
            ORDER BY scan_date DESC, score
        """
        return pd.read_sql_query(query, self.conn, params=(ticker, cutoff))

    # ========================================================================
    # PERFORMANCE ANALYSIS
    # ========================================================================

    def get_preset_performance(self) -> pd.DataFrame:
        """Get performance metrics grouped by preset."""
        query = "SELECT * FROM v_preset_performance"
        return pd.read_sql_query(query, self.conn)

    def get_performance_summary(self) -> pd.DataFrame:
        """Generate performance summary of all recommendations."""
        query = """
            SELECT
                r.recommendation_date,
                r.ticker,
                r.strike,
                r.expiration,
                r.status,
                julianday('now') - julianday(r.recommendation_date) as days_held,
                julianday(r.expiration) - julianday('now') as dte_current,
                r.premium_mid as entry_price,
                r.premium_bid as entry_bid,
                r.premium_ask as entry_ask,
                r.contracts_recommended as contracts,
                r.total_cost,
                r.stock_price_at_rec as stock_entry,
                r.delta_at_rec as delta_entry,
                r.extrinsic_value,
                r.extrinsic_pct,
                r.current_mid as current_price,
                r.current_value,
                r.stock_current,
                r.delta_current,
                r.unrealized_pnl as pnl,
                r.unrealized_pnl_pct as pnl_pct,
                s.preset_name
            FROM recommendations r
            LEFT JOIN scans s ON r.scan_id = s.scan_id
            ORDER BY r.recommendation_date DESC
        """
        df = pd.read_sql_query(query, self.conn)

        # Rename columns to match existing format
        df = df.rename(columns={
            'recommendation_date': 'Rec_Date',
            'ticker': 'Ticker',
            'strike': 'Strike',
            'expiration': 'Expiration',
            'status': 'Status',
            'days_held': 'Days_Held',
            'dte_current': 'DTE',
            'entry_price': 'Entry_Price',
            'entry_bid': 'Entry_Bid',
            'entry_ask': 'Entry_Ask',
            'contracts': 'Contracts',
            'total_cost': 'Total_Cost',
            'stock_entry': 'Stock_Entry',
            'delta_entry': 'Delta_Entry',
            'extrinsic_value': 'Extrinsic_Value',
            'extrinsic_pct': 'Extrinsic_Pct',
            'current_price': 'Current_Price',
            'current_value': 'Current_Value',
            'stock_current': 'Stock_Current',
            'delta_current': 'Delta_Current',
            'pnl': 'P&L',
            'pnl_pct': 'P&L_%',
            'preset_name': 'Preset'
        })

        # Format Rec_Date to just date
        if not df.empty and 'Rec_Date' in df.columns:
            df['Rec_Date'] = pd.to_datetime(df['Rec_Date']).dt.strftime('%Y-%m-%d')

        return df

    # ========================================================================
    # METADATA MANAGEMENT
    # ========================================================================

    def record_successful_schwab_fetch(self):
        """Record timestamp of successful Schwab API data fetch."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO metadata (key, value, updated_at)
            VALUES ('last_schwab_fetch', ?, ?)
        """, (datetime.now().isoformat(), datetime.now().isoformat()))
        self.conn.commit()

    def get_last_schwab_fetch(self) -> Optional[str]:
        """Get timestamp of last successful Schwab API fetch."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM metadata WHERE key = 'last_schwab_fetch'")
        row = cursor.fetchone()
        return row['value'] if row and row['value'] else None

    def get_tickers_with_recent_recommendations(self, hours: int = 24) -> Dict[str, Dict]:
        """Get tickers that have open recommendations created within the time window."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        cutoff_str = cutoff_time.isoformat()

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                ticker,
                id as rec_id,
                recommendation_date,
                scan_id,
                strike,
                expiration
            FROM recommendations
            WHERE status = 'open'
              AND recommendation_date >= ?
            ORDER BY recommendation_date DESC
        """, (cutoff_str,))

        recent_tickers = {}
        for row in cursor.fetchall():
            ticker = row['ticker']
            rec_date = row['recommendation_date']

            # Keep most recent for each ticker
            if ticker not in recent_tickers or rec_date > recent_tickers[ticker]['recommendation_date']:
                recent_tickers[ticker] = {
                    'rec_id': row['rec_id'],
                    'recommendation_date': rec_date,
                    'scan_id': row['scan_id'],
                    'strike': row['strike'],
                    'expiration': row['expiration']
                }

        return recent_tickers

    def calculate_risk_metrics(self) -> Dict:
        """Calculate comprehensive risk metrics for the portfolio."""
        df = self.get_performance_summary()

        if df.empty or 'P&L_%' not in df.columns:
            return {
                'sharpe_ratio': 0,
                'sortino_ratio': 0,
                'max_drawdown': 0,
                'calmar_ratio': 0,
                'profit_factor': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'std_return': 0,
                'expectancy': 0
            }

        returns = df['P&L_%'].replace([np.inf, -np.inf], np.nan).dropna()

        if len(returns) == 0:
            return {
                'sharpe_ratio': 0,
                'sortino_ratio': 0,
                'max_drawdown': 0,
                'calmar_ratio': 0,
                'profit_factor': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'std_return': 0,
                'expectancy': 0
            }

        wins = returns[returns > 0]
        losses = returns[returns < 0]

        avg_return = returns.mean()
        std_return = returns.std()
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() if len(downside_returns) > 0 else 0.0001

        # Sharpe Ratio (annualized)
        sharpe_ratio = (avg_return / std_return) * np.sqrt(252/21) if std_return > 0 else 0

        # Sortino Ratio
        sortino_ratio = (avg_return / downside_std) * np.sqrt(252/21) if downside_std > 0 else 0

        # Max Drawdown
        cumulative = (1 + returns/100).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100

        # Calmar Ratio
        calmar_ratio = avg_return / abs(max_drawdown) if max_drawdown != 0 else 0

        # Profit Factor
        total_wins = wins.sum() if len(wins) > 0 else 0
        total_losses = abs(losses.sum()) if len(losses) > 0 else 0.0001
        profit_factor = total_wins / total_losses if total_losses > 0 else 0

        # Expectancy
        win_rate = len(wins) / len(returns) if len(returns) > 0 else 0
        avg_win = wins.mean() if len(wins) > 0 else 0
        avg_loss = abs(losses.mean()) if len(losses) > 0 else 0
        expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)

        return {
            'sharpe_ratio': float(sharpe_ratio),
            'sortino_ratio': float(sortino_ratio),
            'max_drawdown': float(max_drawdown),
            'calmar_ratio': float(calmar_ratio),
            'profit_factor': float(profit_factor),
            'avg_win': float(avg_win),
            'avg_loss': float(avg_loss),
            'std_return': float(std_return),
            'expectancy': float(expectancy)
        }
