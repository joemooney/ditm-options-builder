# DITM Options Portfolio Builder - Project Context

## High-Level Feature Summary

The DITM (Deep-In-The-Money) Options Portfolio Builder is a sophisticated Python-based web application for analyzing and building conservative options portfolios using the Charles Schwab Trader API.

**Core Features:**
- Automated DITM call options scanning with multi-criteria filtering
- Real-time options chain analysis via Schwab API
- Web-based dashboard for portfolio management
- Recommendation tracking with performance analytics
- Risk metrics (Sharpe ratio, Sortino ratio, max drawdown, Calmar ratio)
- Ticker management with dividend awareness
- Live position tracking and comparison

## Architecture Overview

### Framework: Flask Web Application
- **Main Entry Point:** `web_app.py` (Flask application)
- **Core Logic:** `ditm.py` (Schwab API integration, options analysis)
- **Tracking:** `recommendation_tracker.py` (SQLite database for performance tracking)
- **Port Management:** Integrated with global Port Manager at `/home/joe/ai/port_manager`

### Technology Stack
- **Backend:** Python 3.7+, Flask
- **API:** Schwab Trader API (`schwab-py` library)
- **Database:** SQLite (for recommendation tracking)
- **Frontend:** HTML/CSS/JavaScript (templates in `/templates`, static in `/static`)
- **Dependencies:** pandas, numpy, scipy, markdown, python-dotenv

### File Structure
```
ditm/
├── web_app.py              # Flask web server (main entry point)
├── ditm.py                 # Core options analysis logic
├── recommendation_tracker.py # Performance tracking database
├── main.py                 # Legacy CLI interface
├── templates/              # HTML templates
├── static/                 # CSS, JavaScript
├── .env                    # API credentials (not in git)
├── web_config.json         # User preferences
└── recommendations_history.json  # Tracking data
```

## Recent Major Updates

### Port Manager Integration (Latest)
- Fully integrated with global Port Manager
- Registered on port 5010
- Dashboard launcher enabled with start command: `python web_app.py`
- Working directory: `/home/joe/ai/ditm`
- Access via Port Manager dashboard at http://localhost:5050

### Web Interface Enhancement
- Professional dashboard for options analysis
- Real-time position tracking
- Performance metrics visualization
- Ticker management with dividend warnings
- Mobile-responsive design

### Recommendation Tracking System
- Automatic storage of all recommendations
- Performance tracking over time
- Win rate and average return calculations
- Risk-adjusted metrics (Sharpe, Sortino, etc.)
- Active vs. closed position separation

## Technical Limitations

### API Constraints
- Schwab API requires OAuth 2.0 authentication
- Tokens expire and need refresh (handled automatically)
- Rate limiting may apply (not currently implemented)
- Market data delayed unless real-time subscription active

### Options Data Limitations
- Only analyzes call options (not puts)
- Delta range: 0.70-0.90 (DITM focus)
- DTE range: 15-45 days (configurable)
- Requires minimum open interest: 250 contracts
- Max bid-ask spread: 2% or $1.00 absolute

### Performance Considerations
- Scanning multiple tickers can take 5-10 seconds
- Database grows with recommendations (SQLite sufficient for < 10K records)
- No caching of market data (always fetches fresh)

## Key Design Principles

1. **Conservative Selection:** Prioritize low extrinsic value (≤30%) and high delta (≥0.70)
2. **Liquidity Focus:** Require tight spreads and sufficient open interest
3. **Realistic Pricing:** Use ask price for entry, bid price for exits
4. **Position Sizing:** Equal allocation across tickers
5. **Dividend Awareness:** Warn users about dividend-paying stocks
6. **Risk Management:** Calculate multiple risk-adjusted metrics

## Environment Variables

Required in `.env`:
```
SCHWAB_APP_KEY=your_app_key
SCHWAB_APP_SECRET=your_app_secret
SCHWAB_ACCOUNT_HASH=your_account_hash
```

Optional:
```
TOKEN_FILE=tokens.json  # OAuth token storage (default)
```

## Common Commands

### Start Web Application
```bash
# Via Port Manager (recommended)
# Dashboard auto-starts via launcher button at http://localhost:5050

# Or direct start
python web_app.py
# Opens on http://localhost:5010
```

### CLI Analysis (Legacy)
```bash
# Activate virtual environment
source .venv/bin/activate

# Run portfolio builder
python ditm.py

# View performance
python view_performance.py
```

### Port Management
```bash
# Check registration
port-manager list

# Get port
port-manager get ditm
```

## Development Environment

- **Python Version:** 3.7+
- **Virtual Environment:** `.venv/` (local to project)
- **Working Directory:** `/home/joe/ai/ditm`
- **Port:** 5010 (managed via Port Manager)
- **Platform:** Linux (Ubuntu/Debian)

## Critical Implementation Details

### Options Filtering Criteria (in `ditm.py`)
```python
MIN_DELTA = 0.70          # Allow 70-90 delta range
MAX_DELTA = 0.90
MIN_INTRINSIC_PCT = 0.70  # At least 70% intrinsic value
MIN_DTE = 15              # Minimum 15 days to expiration
MAX_IV = 0.30             # Max implied volatility 30%
MAX_SPREAD_PCT = 0.02     # 2% max bid-ask spread
MIN_OI = 250              # Minimum open interest
```

### Scoring Algorithm
Options are ranked by a composite score (lower is better):
```python
Score = 0.35 * (Extrinsic% / MAX_EXTRINSIC_PCT)  # Most important
      + 0.25 * (1 - Delta)                        # Prefer high delta
      + 0.20 * (1 / Leverage) * 10                # Prefer high leverage
      + 0.10 * (IV / MAX_IV)                      # Penalize high IV
      + 0.10 * (Spread% / MAX_SPREAD_PCT)         # Penalize wide spreads
```

### Database Schema (SQLite)
Table: `recommendations`
- id, ticker, strike, expiration, status (open/closed)
- entry_date, entry_price, entry_bid, entry_ask, entry_mid
- contracts, stock_entry, delta_entry, extrinsic_value
- current_bid, current_ask, current_mid, stock_current
- last_updated, closed_date, close_reason

## Project Status

**Current State:** Production-ready web application
**Active Development:** Performance tracking enhancements
**Known Issues:** None critical
**Next Steps:**
- Enhanced charting/visualization
- Email alerts for positions
- Multi-account support
