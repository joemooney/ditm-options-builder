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
    get_schwab_client, build_ditm_portfolio, find_ditm_calls,
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


@app.route('/api/performance', methods=['GET'])
def api_performance():
    """Get performance data."""
    try:
        update = request.args.get('update', 'false').lower() == 'true'

        client = None
        if update:
            client = get_schwab_client()

        # Get performance summary
        df = tracker.get_performance_summary()

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

        # Portfolio summary - handle None values
        total_invested = float(df["Total_Cost"].fillna(0).sum())
        current_value = float(df["Current_Value"].fillna(0).sum())
        total_pnl = float(df["P&L"].fillna(0).sum())

        # Safe mean calculations
        avg_return = df["P&L_%"].mean()
        avg_days = df["Days_Held"].mean()

        summary = {
            "total_recommendations": len(df),
            "open_positions": len(df[df["Status"] == "open"]),
            "expired_positions": len(df[df["Status"] == "expired"]),
            "total_invested": total_invested,
            "current_value": current_value,
            "total_pnl": total_pnl,
            "total_pnl_pct": (total_pnl / total_invested * 100) if total_invested > 0 else 0,
            "win_rate": (len(df[df["P&L"] > 0]) / len(df) * 100) if len(df) > 0 else 0,
            "avg_return": float(avg_return) if not pd.isna(avg_return) else 0.0,
            "avg_days_held": float(avg_days) if not pd.isna(avg_days) else 0.0
        }

        # Convert DataFrame to dict with proper type conversion
        positions = df.to_dict('records')

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

        # Calculate additional metrics with null safety
        current_price = pos.get('Current_Stock_Price') or 0
        current_value = pos.get('Current_Value') or 0
        option_price = current_value / 100 if current_value else 0  # Per share
        total_cost = pos.get('Total_Cost') or 0
        contracts = pos.get('Contracts') or 1

        # Breakeven calculation
        if total_cost > 0 and contracts > 0:
            cost_per_share = total_cost / (contracts * 100)
        else:
            cost_per_share = 0
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
        distance_to_breakeven = current_price - breakeven
        distance_to_breakeven_pct = (distance_to_breakeven / breakeven * 100) if breakeven > 0 else 0

        # Safe conversions for response
        days_held = pos.get('Days_Held')
        days_to_expiration = pos.get('DTE')

        return jsonify({
            "success": True,
            "position": pos,
            "analysis": {
                "breakeven": breakeven,
                "cost_per_share": cost_per_share,
                "current_stock_price": current_price,
                "distance_to_breakeven": distance_to_breakeven,
                "distance_to_breakeven_pct": distance_to_breakeven_pct,
                "exit_targets": exit_targets,
                "contracts": int(contracts),
                "intrinsic_value": max(0, current_price - float(strike)),
                "days_held": int(days_held) if days_held is not None else 0,
                "days_to_expiration": int(days_to_expiration) if days_to_expiration is not None else 0
            }
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
