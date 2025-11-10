#!/usr/bin/env python3
"""
DITM Options Portfolio Builder - Web Interface
Professional web application for options analysis and portfolio management.
"""
import os
import json
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv
import markdown
import pandas as pd
import numpy as np

from ditm import (
    get_schwab_client, build_ditm_portfolio, find_ditm_calls, get_account_positions,
    MIN_DELTA, MAX_DELTA, MIN_INTRINSIC_PCT, MIN_DTE, MAX_IV, MAX_SPREAD_PCT, MIN_OI
)
from recommendation_tracker import RecommendationTracker

# Import PortManager from global installation
import sys
sys.path.insert(0, '/home/joe/ai/port_manager')
from port_manager import PortManager

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Global tracker instance
tracker = RecommendationTracker()

# Configuration file for user preferences
CONFIG_FILE = Path("./web_config.json")


def load_config():
    """Load user configuration."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "tickers": ["AAPL", "MSFT", "GOOGL", "JNJ", "JPM"],
        "target_capital": 50000,
        "use_ask_for_entry": True,  # Use ask price for breakeven (realistic), False for mid price (optimistic)
        "filters": {
            "MIN_DELTA": MIN_DELTA,
            "MAX_DELTA": MAX_DELTA,
            "MIN_INTRINSIC_PCT": MIN_INTRINSIC_PCT,
            "MIN_DTE": MIN_DTE,
            "MAX_IV": MAX_IV,
            "MAX_SPREAD_PCT": MAX_SPREAD_PCT,
            "MIN_OI": MIN_OI
        }
    }


def save_config(config):
    """Save user configuration."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


@app.route('/')
def index():
    """Main dashboard."""
    return render_template('index.html')


@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """Get or update configuration."""
    if request.method == 'POST':
        config = request.json
        save_config(config)
        return jsonify({"success": True, "message": "Configuration saved"})

    return jsonify(load_config())


@app.route('/api/scan', methods=['POST'])
def api_scan():
    """Run options scan."""
    try:
        data = request.json
        tickers = data.get('tickers', [])
        target_capital = data.get('target_capital', 50000)

        if not tickers:
            return jsonify({"success": False, "error": "No tickers provided"}), 400

        # Initialize Schwab client
        client = get_schwab_client()

        # Run scan with tracking
        portfolio_df = build_ditm_portfolio(
            client,
            tickers,
            target_capital=target_capital,
            tracker=tracker,
            save_recommendations=True
        )

        if portfolio_df.empty:
            return jsonify({
                "success": False,
                "message": "No qualifying options found"
            })

        # Convert to JSON-serializable format
        portfolio_dict = portfolio_df.to_dict('records')

        # Calculate summary stats
        summary = {
            "total_invested": float(portfolio_df["Total Cost"].sum()),
            "total_equiv_shares": float(portfolio_df["Equiv Shares"].sum()),
            "num_positions": len(portfolio_df),
            "scan_date": datetime.now().isoformat()
        }

        return jsonify({
            "success": True,
            "portfolio": portfolio_dict,
            "summary": summary
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/positions/active', methods=['GET'])
def api_active_positions():
    """Get actual positions from Schwab account."""
    try:
        client = get_schwab_client()
        positions_df = get_account_positions(client)

        if positions_df.empty:
            return jsonify({
                "success": True,
                "message": "No active option positions found",
                "positions": []
            })

        # Convert to JSON-serializable format
        positions = positions_df.to_dict('records')

        # Convert numpy/pandas types to Python native types
        for pos in positions:
            for key, value in pos.items():
                if pd.isna(value):
                    pos[key] = None
                elif isinstance(value, (np.integer, np.int64)):
                    pos[key] = int(value)
                elif isinstance(value, (np.floating, np.float64)):
                    pos[key] = float(value)

        return jsonify({
            "success": True,
            "positions": positions
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/performance', methods=['GET'])
def api_performance():
    """Get performance data with active position matching."""
    try:
        update = request.args.get('update', 'false').lower() == 'true'

        client = None
        if update:
            client = get_schwab_client()
            # Update all open recommendation prices from Schwab
            tracker.update_all_open_recommendations(client)

        # Get performance summary (all recommendations)
        df = tracker.get_performance_summary()

        # Get active positions from account
        active_df = get_account_positions(client if client else get_schwab_client())

        # Add is_active flag by matching with account positions
        if not df.empty and not active_df.empty:
            df['Is_Active'] = df.apply(
                lambda row: any(
                    (active_df['Ticker'] == row['Ticker']) &
                    (abs(active_df['Strike'] - row['Strike']) < 0.01) &
                    (active_df['Expiration'] == row['Expiration'])
                ),
                axis=1
            )
        else:
            df['Is_Active'] = False

        if df.empty:
            return jsonify({
                "success": True,
                "message": "No performance data available",
                "data": []
            })

        # Calculate risk metrics
        risk_metrics = tracker.calculate_risk_metrics()

        # Convert numpy/pandas types to Python native types in risk_metrics
        for key, value in risk_metrics.items():
            if pd.isna(value):
                risk_metrics[key] = None
            elif isinstance(value, (np.integer, np.int64)):
                risk_metrics[key] = int(value)
            elif isinstance(value, (np.floating, np.float64)):
                # Handle infinity values - convert to None for JSON
                float_val = float(value)
                if np.isinf(float_val):
                    risk_metrics[key] = None
                else:
                    risk_metrics[key] = float_val
            elif isinstance(value, float):
                # Handle Python float infinity
                if np.isinf(value):
                    risk_metrics[key] = None
                else:
                    risk_metrics[key] = value

        # Convert DataFrame to dict with proper type conversion
        positions = df.to_dict('records')

        # Convert numpy/pandas types to Python native types and fix zero current values
        for pos in positions:
            for key, value in pos.items():
                if pd.isna(value):
                    pos[key] = None
                elif isinstance(value, (np.integer, np.int64)):
                    pos[key] = int(value)
                elif isinstance(value, (np.floating, np.float64)):
                    pos[key] = float(value)

            # Fix Total_Cost if it's 0 for new positions
            total_cost = pos.get('Total_Cost') or 0
            if total_cost == 0 and pos.get('Status') == 'open':
                entry_ask = pos.get('Entry_Ask') or 0
                entry_mid = pos.get('Entry_Mid') or pos.get('Entry_Price') or 0
                contracts = pos.get('Contracts') or 1

                # Calculate total cost (what you paid to buy)
                if entry_ask > 0:
                    total_cost = entry_ask * contracts * 100
                    pos['Total_Cost'] = total_cost
                elif entry_mid > 0:
                    total_cost = entry_mid * contracts * 100
                    pos['Total_Cost'] = total_cost

            # Fix Current_Value if it's 0 for new positions
            current_value = pos.get('Current_Value') or 0
            if current_value == 0 and pos.get('Status') == 'open':
                # Use entry bid price as realistic current value (what you'd get if selling immediately)
                entry_bid = pos.get('Entry_Bid') or 0
                entry_mid = pos.get('Entry_Mid') or pos.get('Entry_Price') or 0
                contracts = pos.get('Contracts') or 1

                if entry_bid > 0:
                    # Use bid price (realistic sell price)
                    pos['Current_Value'] = entry_bid * contracts * 100
                elif entry_mid > 0:
                    # Fallback to mid price
                    pos['Current_Value'] = entry_mid * contracts * 100

                # Recalculate P&L based on new current value
                if pos['Current_Value'] > 0 and total_cost > 0:
                    pos['P&L'] = pos['Current_Value'] - total_cost
                    pos['P&L_%'] = (pos['P&L'] / total_cost) * 100

        # Calculate summaries AFTER fixing values
        # Separate active vs recommended positions
        active_positions = [p for p in positions if p.get('Is_Active') == True]
        recommended_only = [p for p in positions if p.get('Status') == 'open' and p.get('Is_Active') == False]

        # Overall summary (all positions)
        total_invested = sum(p.get('Total_Cost') or 0 for p in positions)
        current_value = sum(p.get('Current_Value') or 0 for p in positions)
        total_pnl = sum(p.get('P&L') or 0 for p in positions)

        # Active positions summary
        active_invested = sum(p.get('Total_Cost') or 0 for p in active_positions)
        active_value = sum(p.get('Current_Value') or 0 for p in active_positions)
        active_pnl = sum(p.get('P&L') or 0 for p in active_positions)

        # Recommended only summary (hypothetical)
        recommended_invested = sum(p.get('Total_Cost') or 0 for p in recommended_only)
        recommended_value = sum(p.get('Current_Value') or 0 for p in recommended_only)
        recommended_pnl = sum(p.get('P&L') or 0 for p in recommended_only)

        summary = {
            "total_recommendations": len(positions),
            "active_positions": len(active_positions),
            "recommended_only": len(recommended_only),
            "expired_positions": len([p for p in positions if p.get('Status') == 'expired']),

            # Overall totals
            "total_invested": total_invested,
            "current_value": current_value,
            "total_pnl": total_pnl,
            "total_pnl_pct": (total_pnl / total_invested * 100) if total_invested > 0 else 0,

            # Active positions
            "active_invested": active_invested,
            "active_value": active_value,
            "active_pnl": active_pnl,
            "active_pnl_pct": (active_pnl / active_invested * 100) if active_invested > 0 else 0,

            # Recommended only (hypothetical)
            "recommended_invested": recommended_invested,
            "recommended_value": recommended_value,
            "recommended_pnl": recommended_pnl,
            "recommended_pnl_pct": (recommended_pnl / recommended_invested * 100) if recommended_invested > 0 else 0,

            # Other metrics
            "win_rate": (len([p for p in positions if (p.get('P&L') or 0) > 0]) / len(positions) * 100) if len(positions) > 0 else 0,
            "avg_return": sum(p.get('P&L_%') or 0 for p in positions) / len(positions) if len(positions) > 0 else 0,
            "avg_days_held": sum(p.get('Days_Held') or 0 for p in positions) / len(positions) if len(positions) > 0 else 0
        }

        return jsonify({
            "success": True,
            "summary": summary,
            "risk_metrics": risk_metrics,
            "positions": positions
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/ticker/analyze/<ticker>', methods=['GET'])
def api_analyze_ticker(ticker):
    """Analyze a single ticker for DITM opportunities."""
    try:
        client = get_schwab_client()

        candidates = find_ditm_calls(client, ticker.upper())

        if candidates.empty:
            return jsonify({
                "success": True,
                "ticker": ticker.upper(),
                "message": "No qualifying DITM calls found",
                "candidates": []
            })

        return jsonify({
            "success": True,
            "ticker": ticker.upper(),
            "candidates": candidates.head(10).to_dict('records')
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/docs/<doc_name>')
def api_docs(doc_name):
    """Serve documentation as HTML."""
    try:
        # Map doc names to files
        doc_files = {
            "user_guide": "USER_GUIDE.md",
            "schwab_setup": "SCHWAB_SETUP.md",
            "tracking_guide": "TRACKING_GUIDE.md",
            "readme": "README.md"
        }

        if doc_name not in doc_files:
            return jsonify({"success": False, "error": "Document not found"}), 404

        doc_path = Path(doc_files[doc_name])
        if not doc_path.exists():
            return jsonify({"success": False, "error": "Document file not found"}), 404

        # Read and convert markdown to HTML
        with open(doc_path, 'r') as f:
            md_content = f.read()

        html_content = markdown.markdown(
            md_content,
            extensions=['tables', 'fenced_code', 'toc']
        )

        return jsonify({
            "success": True,
            "title": doc_name.replace('_', ' ').title(),
            "content": html_content
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/tickers', methods=['GET'])
def api_get_tickers():
    """Get current ticker list."""
    config = load_config()
    return jsonify({
        "success": True,
        "tickers": config.get("tickers", [])
    })


@app.route('/api/tickers/add', methods=['POST'])
def api_add_ticker():
    """Add a ticker to the watchlist."""
    try:
        data = request.json
        ticker = data.get('ticker', '').upper().strip()

        if not ticker:
            return jsonify({"success": False, "error": "Ticker symbol required"}), 400

        # Basic validation
        if not ticker.isalpha() or len(ticker) > 5:
            return jsonify({"success": False, "error": "Invalid ticker symbol"}), 400

        config = load_config()
        tickers = config.get("tickers", [])

        if ticker in tickers:
            return jsonify({"success": False, "error": f"{ticker} already in watchlist"}), 400

        tickers.append(ticker)
        config["tickers"] = tickers
        save_config(config)

        return jsonify({
            "success": True,
            "message": f"Added {ticker} to watchlist",
            "tickers": tickers
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/tickers/remove', methods=['POST'])
def api_remove_ticker():
    """Remove a ticker from the watchlist."""
    try:
        data = request.json
        ticker = data.get('ticker', '').upper().strip()

        if not ticker:
            return jsonify({"success": False, "error": "Ticker symbol required"}), 400

        config = load_config()
        tickers = config.get("tickers", [])

        if ticker not in tickers:
            return jsonify({"success": False, "error": f"{ticker} not in watchlist"}), 404

        tickers.remove(ticker)
        config["tickers"] = tickers
        save_config(config)

        return jsonify({
            "success": True,
            "message": f"Removed {ticker} from watchlist",
            "tickers": tickers
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/position/<ticker>/<strike>/<expiration>', methods=['GET'])
def api_position_detail(ticker, strike, expiration):
    """Get detailed analysis for a specific position."""
    try:
        # Get current price
        client = get_schwab_client()

        # Find the position in recommendations
        df = tracker.get_performance_summary()
        position = df[
            (df['Ticker'] == ticker.upper()) &
            (df['Strike'] == float(strike)) &
            (df['Expiration'] == expiration)
        ]

        if position.empty:
            return jsonify({"success": False, "error": "Position not found"}), 404

        pos = position.iloc[0].to_dict()

        # Get stock price - fetch fresh if not available
        current_stock_price = pos.get('Stock_Current') or pos.get('Current_Stock_Price')
        if not current_stock_price or current_stock_price == 0:
            # Fetch current stock price
            quote_resp = client.get_quote(ticker.upper())
            if quote_resp.status_code == 200:
                quote_data = quote_resp.json()
                current_stock_price = quote_data[ticker.upper()]["quote"]["lastPrice"]
            else:
                current_stock_price = pos.get('Stock_Entry') or 0

        # Option pricing
        entry_bid = pos.get('Entry_Bid') or 0
        entry_ask = pos.get('Entry_Ask') or 0
        entry_mid = pos.get('Entry_Mid') or pos.get('Entry_Price') or 0

        # Determine which price to use for breakeven calculation based on config
        config = load_config()
        use_ask_for_entry = config.get('use_ask_for_entry', True)

        # Use ask price for realistic breakeven (you buy at ask), or mid for optimistic
        entry_price_for_breakeven = entry_ask if use_ask_for_entry and entry_ask > 0 else entry_mid

        current_value = pos.get('Current_Value') or 0
        contracts = pos.get('Contracts') or 1

        # Current option price per contract
        current_option_price = current_value / contracts if contracts > 0 and current_value > 0 else 0

        # If current option price is 0 (new position or not updated), estimate from intrinsic value
        if current_option_price == 0:
            intrinsic_now = max(0, current_stock_price - float(strike))
            # For brand new position, assume you'd get bid price if selling immediately
            # Use entry bid as proxy for immediate sell (realistic loss from spread)
            if entry_bid > 0:
                current_option_price = entry_bid
                current_value = current_option_price * contracts
            else:
                # Fallback: use intrinsic value (assumes zero time value for immediate calculation)
                current_option_price = intrinsic_now
                current_value = current_option_price * contracts * 100

        # Cost per share (premium paid divided by 100 shares per contract)
        total_cost = pos.get('Total_Cost') or 0
        if total_cost > 0 and contracts > 0:
            cost_per_share = total_cost / (contracts * 100)
        else:
            # Use ask price for realistic cost, or mid if ask not available
            cost_per_share = entry_price_for_breakeven / 100 if entry_price_for_breakeven > 0 else 0

        # Breakeven = Strike + Premium Paid Per Share (using ask price if configured)
        breakeven = float(strike) + cost_per_share

        # Profit targets
        profit_25 = cost_per_share * 1.25
        profit_50 = cost_per_share * 1.50
        profit_100 = cost_per_share * 2.00

        # Exit strategy calculations
        exit_targets = {
            "take_profit_50": {
                "price": profit_50,
                "gain": (profit_50 - cost_per_share) * contracts * 100,
                "gain_pct": 50
            },
            "take_profit_100": {
                "price": profit_100,
                "gain": (profit_100 - cost_per_share) * contracts * 100,
                "gain_pct": 100
            },
            "stop_loss": {
                "price": cost_per_share * 0.80,
                "loss": (cost_per_share * 0.80 - cost_per_share) * contracts * 100,
                "loss_pct": -20
            }
        }

        # Current position vs breakeven
        distance_to_breakeven = current_stock_price - breakeven
        distance_to_breakeven_pct = (distance_to_breakeven / breakeven * 100) if breakeven > 0 else 0

        # Safe conversions for response
        days_held = pos.get('Days_Held')
        days_to_expiration = pos.get('DTE')

        # Calculate bid/ask spread
        entry_spread = entry_ask - entry_bid if entry_ask > 0 and entry_bid > 0 else 0
        entry_spread_pct = (entry_spread / entry_mid * 100) if entry_mid > 0 else 0

        # Exercise calculations
        shares_per_contract = 100
        total_shares_if_exercised = contracts * shares_per_contract
        exercise_cost = total_shares_if_exercised * float(strike)
        current_stock_value_if_exercised = total_shares_if_exercised * current_stock_price

        # Total investment if exercised (original premium + exercise cost)
        total_investment_if_exercised = total_cost + exercise_cost

        # What you'd get if you exercised and immediately sold shares
        exercise_and_sell_profit = current_stock_value_if_exercised - exercise_cost - total_cost

        # Compare to just selling the option
        sell_option_profit = current_value - total_cost if current_value > 0 else -total_cost

        # Leverage calculations
        # Delta-adjusted exposure (how many shares worth of movement you control)
        delta = pos.get('Delta_Current') or pos.get('Delta_Entry') or 0.85  # Fallback to typical DITM delta
        delta_adjusted_shares = total_shares_if_exercised * delta

        # Cost to buy equivalent shares outright
        cost_to_buy_shares = delta_adjusted_shares * current_stock_price

        # Leverage ratio = (Stock value controlled) / (Capital invested)
        leverage_ratio = cost_to_buy_shares / total_cost if total_cost > 0 else 0

        # Capital efficiency = How much you saved vs buying stock
        capital_saved = cost_to_buy_shares - total_cost
        capital_efficiency_pct = (capital_saved / cost_to_buy_shares * 100) if cost_to_buy_shares > 0 else 0

        # CAGR (Compound Annual Growth Rate) calculation
        # CAGR = (Ending Value / Beginning Value) ^ (1 / Years) - 1
        pnl_pct = pos.get('P&L_%') or 0

        # Calculate years held (use days_held if available, otherwise 0)
        if days_held and days_held > 0:
            years_held = days_held / 365.25

            # Calculate CAGR
            # Return = (1 + P&L%)
            total_return = 1 + (pnl_pct / 100)

            if total_return > 0 and years_held > 0:
                cagr = (total_return ** (1 / years_held) - 1) * 100
            else:
                cagr = 0
        else:
            cagr = 0
            years_held = 0

        # Annualized return (simple, for comparison)
        if days_held and days_held > 0:
            annualized_return = (pnl_pct / days_held) * 365.25
        else:
            annualized_return = 0

        return jsonify({
            "success": True,
            "position": pos,
            "analysis": {
                # Entry Pricing (Bid/Ask/Mid)
                "entry_bid": entry_bid,
                "entry_ask": entry_ask,
                "entry_mid": entry_mid,
                "entry_spread": entry_spread,
                "entry_spread_pct": entry_spread_pct,
                "entry_price_used": entry_price_for_breakeven,  # Which price was used for breakeven
                "use_ask_for_entry": use_ask_for_entry,  # Config setting

                # Current Pricing
                "current_option_price": current_option_price,
                "current_stock_price": current_stock_price,
                "strike_price": float(strike),

                # Breakeven
                "breakeven": breakeven,
                "cost_per_share": cost_per_share,
                "distance_to_breakeven": distance_to_breakeven,
                "distance_to_breakeven_pct": distance_to_breakeven_pct,

                # Position details
                "contracts": int(contracts),
                "intrinsic_value": max(0, current_stock_price - float(strike)),
                "time_value": max(0, current_option_price - max(0, current_stock_price - float(strike))),

                # Leverage metrics
                "delta": delta,
                "delta_adjusted_shares": delta_adjusted_shares,
                "cost_to_buy_shares": cost_to_buy_shares,
                "leverage_ratio": leverage_ratio,
                "capital_saved": capital_saved,
                "capital_efficiency_pct": capital_efficiency_pct,

                # Performance metrics
                "cagr": cagr,
                "annualized_return": annualized_return,
                "years_held": years_held,

                # Exercise information
                "exercise_cost": exercise_cost,
                "total_shares_if_exercised": total_shares_if_exercised,
                "total_investment_if_exercised": total_investment_if_exercised,
                "current_stock_value_if_exercised": current_stock_value_if_exercised,
                "exercise_and_sell_profit": exercise_and_sell_profit,
                "sell_option_profit": sell_option_profit,
                "better_to_sell_option": sell_option_profit > exercise_and_sell_profit,

                # Exit strategy
                "exit_targets": exit_targets,

                # Time
                "days_held": int(days_held) if days_held is not None else 0,
                "days_to_expiration": int(days_to_expiration) if days_to_expiration is not None else 0
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/recommendation/remove', methods=['POST'])
def api_remove_recommendation():
    """Remove a recommendation from tracking."""
    try:
        data = request.json
        ticker = data.get('ticker')
        strike = data.get('strike')
        expiration = data.get('expiration')

        if not all([ticker, strike, expiration]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        # Close the recommendation in the tracker
        tracker.close_recommendation(ticker, strike, expiration, reason="User removed")

        return jsonify({
            "success": True,
            "message": f"Removed {ticker} ${strike} {expiration}"
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/health')
def api_health():
    """Health check endpoint."""
    try:
        # Check if Schwab client can be initialized
        client = get_schwab_client()
        schwab_status = "connected"
    except Exception as e:
        schwab_status = f"error: {str(e)}"

    return jsonify({
        "status": "healthy",
        "schwab": schwab_status,
        "database": "connected" if tracker.db_path.exists() else "not_found",
        "timestamp": datetime.now().isoformat()
    })


# Serve static files
@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files."""
    return send_from_directory('static', filename)


if __name__ == '__main__':
    # Create necessary directories
    Path("templates").mkdir(exist_ok=True)
    Path("static/css").mkdir(parents=True, exist_ok=True)
    Path("static/js").mkdir(parents=True, exist_ok=True)

    # Get port from port manager
    port_manager = PortManager()

    # Register this application if not already registered
    app_name = "ditm"
    port = port_manager.get_port(app_name)

    if port is None:
        # Register with default port
        port = 5010
        try:
            port_manager.register_port(
                app_name,
                port,
                "DITM Options Portfolio Builder - Web Interface"
            )
            print(f"✓ Registered '{app_name}' on port {port} in global registry")
        except ValueError as e:
            # Port conflict - find available port
            print(f"⚠ Port {port} conflict: {e}")
            port = port_manager.find_available_port(5000, 6000)
            port_manager.register_port(
                app_name,
                port,
                "DITM Options Portfolio Builder - Web Interface"
            )
            print(f"✓ Registered '{app_name}' on port {port} (auto-assigned)")

    print("=" * 70)
    print("DITM Options Portfolio Builder - Web Interface")
    print("=" * 70)
    print(f"Starting server at http://localhost:{port}")
    print(f"Port assignment managed via: {port_manager.registry_path}")
    print("Press Ctrl+C to stop")
    print("=" * 70)

    app.run(debug=True, host='0.0.0.0', port=port)
