# DITM Options Portfolio Builder - Overview

## Vision

The DITM Options Portfolio Builder transforms complex options analysis into an accessible, data-driven investment tool. It empowers individual investors to leverage institutional-grade strategies for building conservative, capital-efficient portfolios using deep-in-the-money call options.

**Goal:** Democratize sophisticated options trading by automating the research, filtering, and tracking processes that would otherwise require hours of manual analysis.

## What Problem Does It Solve?

### The Challenge
Traditional stock investing requires significant capital. For example:
- 100 shares of a $70 stock = $7,000 investment
- Limited diversification with small portfolios
- Full exposure to downside risk

Options provide leverage, but most options strategies are:
- Risky (OTM options with high time decay)
- Complex (multi-leg strategies)
- Time-intensive (manual chain analysis)

### The Solution
DITM call options offer **stock-like exposure with 7-13x leverage** while minimizing time decay:
- Same delta-adjusted movement as stock (70-90%)
- 92% less capital required
- Asymmetric upside potential

**This tool automates the entire selection process:**
1. Scans options chains via Schwab API
2. Filters by 10+ criteria (liquidity, delta, IV, spreads)
3. Ranks by conservative scoring algorithm
4. Tracks performance over time
5. Provides actionable recommendations

## How It Works

### For End Users
1. **Add Tickers:** Build a watchlist of stocks you want to analyze
2. **Run Scan:** Click one button to analyze all options chains
3. **Review Results:** See ranked DITM call recommendations with detailed metrics
4. **Track Performance:** Monitor open positions with live market data
5. **Analyze Risk:** View comprehensive risk metrics (Sharpe, Sortino, drawdown)

### For Developers
1. **Schwab API Integration:** OAuth 2.0 authentication with automatic token refresh
2. **Options Analysis Engine:** Black-Scholes delta calculation, multi-criteria filtering
3. **SQLite Database:** Persistent tracking of recommendations and performance
4. **Flask Web Server:** REST API endpoints for scan, positions, performance
5. **Port Manager Integration:** Global port registry and dashboard launcher

## Key Features

### Options Analysis
- **Multi-Ticker Scanning:** Analyze entire watchlist in one scan
- **Conservative Filtering:** 10+ criteria ensure quality recommendations
- **Intelligent Ranking:** Composite score balances leverage, liquidity, and risk
- **Dividend Awareness:** Warns about dividend-paying stocks (options don't receive dividends)

### Performance Tracking
- **Automatic Recording:** Every recommendation saved with full market data
- **Live Updates:** Refresh current prices on demand
- **Win Rate Analysis:** Track success rate and average returns
- **Risk Metrics:** Sharpe ratio, Sortino ratio, max drawdown, Calmar ratio, profit factor
- **Position Comparison:** Active vs. recommended vs. closed positions

### Web Dashboard
- **Professional Interface:** Clean, intuitive design
- **Real-Time Data:** Live position tracking from Schwab account
- **Position Details:** Breakeven, profit targets, leverage analysis
- **Documentation:** Built-in guides (setup, tracking, user guide)
- **Mobile Responsive:** Works on desktop, tablet, phone

### Developer Features
- **Port Manager Integration:** Global port registry (5010)
- **RESTful API:** JSON endpoints for all functionality
- **Modular Architecture:** Separate concerns (API, logic, tracking, web)
- **Type Safety:** Clean data conversion (numpy/pandas → JSON)

## Target Audience

### Primary Users
- **Conservative Options Traders:** Looking for stock-replacement strategies
- **Capital-Efficient Investors:** Want leverage without excessive risk
- **Data-Driven Traders:** Prefer systematic selection over gut feelings
- **Portfolio Diversifiers:** Need to spread limited capital across multiple positions

### Developer Use Cases
- **Algorithmic Trading:** API can be integrated into automated systems
- **Research Platform:** Use as foundation for custom options strategies
- **Educational Tool:** Learn options analysis through working code
- **Portfolio Management:** Integrate with broader investment platforms

## Technology Choices

### Why Flask?
- Lightweight, easy to deploy
- Python-native (matches analysis libraries)
- RESTful API design
- Rapid prototyping and iteration

### Why Schwab API?
- Official broker integration
- Real-time market data access
- Account position tracking
- OAuth 2.0 security

### Why SQLite?
- Zero configuration
- File-based (easy backups)
- Sufficient for < 10K records
- ACID compliance

### Why Port Manager Integration?
- Centralized port management across all projects
- Web-based launcher (no manual startups)
- Prevents port conflicts
- Professional development workflow

## Real-World Example

**Scenario:** You have $10,000 to invest in AAPL (trading at $187)

**Traditional Approach:**
- Buy 53 shares = $9,911
- Exposure: 53 shares
- Capital efficiency: 100%

**DITM Options Approach:**
- Buy 2 contracts @ $18.50 (strike $170, delta 0.85) = $3,700
- Exposure: 170 delta-adjusted shares (2 × 100 × 0.85)
- Capital efficiency: 37% (saved $6,300 for other positions)
- Leverage: 10x

**If AAPL rises 10% to $205.70:**
- Stock gain: 53 × $18.70 = $991 (10% return)
- Option gain (simplified): 170 × $18.70 × 0.85 = $2,700 (73% return)

**The Difference:**
- 7.3x better returns with options
- Freed up $6,300 for 3-4 more positions
- Diversification without diluting returns

## Getting Started (New User)

### Prerequisites
1. Python 3.7+ installed
2. Charles Schwab brokerage account
3. Approved Schwab Developer Application ([apply here](https://developer.schwab.com/))

### 5-Minute Setup
```bash
# 1. Navigate to project
cd /home/joe/ai/ditm

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure Schwab API credentials
# Create .env file with:
# SCHWAB_APP_KEY=your_key
# SCHWAB_APP_SECRET=your_secret
# SCHWAB_ACCOUNT_HASH=your_account

# 5. Start web application
python web_app.py

# 6. Open browser to http://localhost:5010
```

**Or use Port Manager dashboard:**
```bash
# Open http://localhost:5050
# Click "Start" button for DITM app
```

## Project Structure

```
ditm/
├── Core Application
│   ├── web_app.py              # Flask web server (main entry)
│   ├── ditm.py                 # Options analysis engine
│   ├── recommendation_tracker.py # Performance tracking
│   └── main.py                 # Legacy CLI interface
│
├── Web Interface
│   ├── templates/              # HTML templates
│   │   └── index.html          # Single-page dashboard
│   └── static/                 # CSS, JavaScript
│       ├── css/
│       └── js/
│
├── Configuration
│   ├── .env                    # API credentials (not in git)
│   ├── web_config.json         # User preferences
│   └── requirements.txt        # Python dependencies
│
├── Data
│   ├── recommendations.db      # SQLite tracking database
│   ├── recommendations_history.json  # JSON export
│   └── tokens.json             # OAuth tokens (auto-managed)
│
└── Documentation
    ├── README.md               # Project overview
    ├── CLAUDE.md               # Developer context (this file)
    ├── OVERVIEW.md             # Vision and architecture
    ├── REQUIREMENTS.md         # System requirements
    ├── USER_GUIDE.md           # End-user instructions
    ├── SCHWAB_SETUP.md         # API setup guide
    ├── TRACKING_GUIDE.md       # Performance tracking guide
    └── WEB_INTERFACE_GUIDE.md  # Dashboard usage
```

## Development Philosophy

### Principles
1. **Conservative by Design:** Prioritize capital preservation over aggressive returns
2. **Data-Driven Decisions:** Every recommendation backed by quantitative metrics
3. **Transparency:** Show all criteria, calculations, and reasoning
4. **Simplicity:** Complex analysis, simple interface
5. **Automation:** Eliminate manual, error-prone tasks

### Quality Standards
- **No Hardcoded Values:** All thresholds configurable
- **Type Safety:** Proper numpy/pandas → Python type conversion
- **Error Handling:** Graceful degradation on API failures
- **Documentation:** Every function, endpoint, and feature documented
- **Testing:** Manual validation against real market data

## Maintenance and Evolution

### Current Maintenance
- **Active Development:** Performance tracking enhancements
- **Regular Updates:** As Schwab API evolves
- **Community Feedback:** User-requested features

### Future Roadmap
- **Charting:** Visual performance graphs
- **Alerts:** Email/SMS notifications for positions
- **Multi-Account:** Support multiple Schwab accounts
- **Strategy Expansion:** DITM puts, spreads, calendars
- **Backtesting:** Historical performance analysis
- **Mobile App:** Native iOS/Android interface

## Contributing

This is a personal project, but the architecture supports extension:
- **Modular Design:** Add new analysis criteria in `ditm.py`
- **RESTful API:** Build custom frontends
- **Database Schema:** Extend tracking with new fields
- **Plugin Architecture:** Add new risk metrics in `recommendation_tracker.py`

## License and Usage

Personal project for educational and investment purposes. Schwab API usage subject to their terms of service.

**Disclaimer:** Options trading involves risk. This tool provides analysis, not investment advice. Past performance doesn't guarantee future results.

## Support and Resources

### Documentation
- **User Guide:** Complete walkthrough for end users
- **Schwab Setup:** Step-by-step API configuration
- **Tracking Guide:** Understanding performance metrics
- **Web Interface Guide:** Dashboard feature reference

### External Resources
- [Schwab Developer Portal](https://developer.schwab.com/)
- [schwab-py Library](https://github.com/itsjafer/schwab-py)
- [Options Education](https://www.cboe.com/education/)
- [DITM Strategy Guide](https://www.optionseducation.org/)

## Contact and Feedback

For bugs, feature requests, or questions:
- Check documentation in `/docs`
- Review code comments for technical details
- Test in paper trading account first
