# DITM Options Portfolio Builder - System Requirements

## Functional Requirements

### 1. Options Analysis Engine

#### 1.1 Market Data Integration
- **FR-1.1.1:** Must connect to Charles Schwab Trader API for real-time options data
- **FR-1.1.2:** Must support OAuth 2.0 authentication with automatic token refresh
- **FR-1.1.3:** Must retrieve complete options chains for specified tickers
- **FR-1.1.4:** Must fetch current stock quotes for position tracking
- **FR-1.1.5:** Must handle API rate limiting and errors gracefully

#### 1.2 Options Filtering
- **FR-1.2.1:** Must filter options by delta range (0.70 - 0.90)
- **FR-1.2.2:** Must filter by intrinsic value percentage (≥70%)
- **FR-1.2.3:** Must filter by extrinsic value percentage (≤30%)
- **FR-1.2.4:** Must filter by days to expiration (15-45 days)
- **FR-1.2.5:** Must filter by implied volatility (≤30%)
- **FR-1.2.6:** Must filter by bid-ask spread (≤2% or $1.00 absolute)
- **FR-1.2.7:** Must filter by open interest (≥250 contracts)
- **FR-1.2.8:** Must filter by leverage factor (≥7x)

#### 1.3 Options Ranking
- **FR-1.3.1:** Must calculate composite score based on multiple criteria
- **FR-1.3.2:** Must prioritize low extrinsic value (35% weight)
- **FR-1.3.3:** Must favor high delta (25% weight)
- **FR-1.3.4:** Must favor high leverage (20% weight)
- **FR-1.3.5:** Must penalize high IV (10% weight)
- **FR-1.3.6:** Must penalize wide spreads (10% weight)
- **FR-1.3.7:** Must rank results from most to least conservative

#### 1.4 Portfolio Construction
- **FR-1.4.1:** Must support multi-ticker portfolio analysis
- **FR-1.4.2:** Must calculate position sizing (whole contracts only)
- **FR-1.4.3:** Must compute delta-adjusted exposure
- **FR-1.4.4:** Must calculate total portfolio leverage
- **FR-1.4.5:** Must show capital efficiency vs. buying stock

### 2. Performance Tracking

#### 2.1 Recommendation Storage
- **FR-2.1.1:** Must automatically save all scan recommendations to database
- **FR-2.1.2:** Must record entry date, prices (bid/ask/mid), and market conditions
- **FR-2.1.3:** Must track stock price, delta, and extrinsic value at entry
- **FR-2.1.4:** Must assign unique identifier (ticker + strike + expiration)
- **FR-2.1.5:** Must record number of contracts recommended

#### 2.2 Position Updates
- **FR-2.2.1:** Must update current prices for open positions on demand
- **FR-2.2.2:** Must calculate current P&L (dollar and percentage)
- **FR-2.2.3:** Must track days held for each position
- **FR-2.2.4:** Must calculate days to expiration dynamically
- **FR-2.2.5:** Must match recommendations with active account positions

#### 2.3 Performance Metrics
- **FR-2.3.1:** Must calculate win rate (% of profitable positions)
- **FR-2.3.2:** Must calculate average return (mean P&L%)
- **FR-2.3.3:** Must calculate total invested capital
- **FR-2.3.4:** Must calculate current portfolio value
- **FR-2.3.5:** Must calculate total P&L (dollar and percentage)

#### 2.4 Risk Metrics
- **FR-2.4.1:** Must calculate Sharpe ratio (risk-adjusted return)
- **FR-2.4.2:** Must calculate Sortino ratio (downside risk-adjusted return)
- **FR-2.4.3:** Must calculate maximum drawdown
- **FR-2.4.4:** Must calculate Calmar ratio (return / max drawdown)
- **FR-2.4.5:** Must calculate profit factor (wins / losses)
- **FR-2.4.6:** Must calculate win/loss ratio
- **FR-2.4.7:** Must calculate average win vs. average loss

#### 2.5 Position Analysis
- **FR-2.5.1:** Must calculate breakeven price (strike + premium paid)
- **FR-2.5.2:** Must show distance to breakeven (dollars and percentage)
- **FR-2.5.3:** Must calculate profit targets (25%, 50%, 100% gains)
- **FR-2.5.4:** Must calculate stop-loss level (20% loss)
- **FR-2.5.5:** Must show leverage ratio and capital efficiency
- **FR-2.5.6:** Must calculate CAGR (compound annual growth rate)
- **FR-2.5.7:** Must compare option returns vs. buying stock
- **FR-2.5.8:** Must calculate option outperformance percentage

### 3. Web Interface

#### 3.1 Dashboard
- **FR-3.1.1:** Must display portfolio summary (total invested, P&L, win rate)
- **FR-3.1.2:** Must show active positions with current prices
- **FR-3.1.3:** Must display recommended positions (not yet purchased)
- **FR-3.1.4:** Must show closed/expired positions
- **FR-3.1.5:** Must provide quick scan button
- **FR-3.1.6:** Must show health status (API connection, database)

#### 3.2 Ticker Management
- **FR-3.2.1:** Must allow adding tickers to watchlist
- **FR-3.2.2:** Must validate ticker symbols (alphabetic, ≤5 chars)
- **FR-3.2.3:** Must check for dividends and warn user
- **FR-3.2.4:** Must allow removing tickers from watchlist
- **FR-3.2.5:** Must display dividend info (yield, annual amount) per ticker
- **FR-3.2.6:** Must persist watchlist between sessions

#### 3.3 Scanning
- **FR-3.3.1:** Must scan all watchlist tickers in one operation
- **FR-3.3.2:** Must show scan progress and results
- **FR-3.3.3:** Must skip tickers with recent recommendations (< 24 hours)
- **FR-3.3.4:** Must display scan summary (positions found, total cost)
- **FR-3.3.5:** Must automatically update prices after scan completion

#### 3.4 Position Details
- **FR-3.4.1:** Must show detailed analysis for each position
- **FR-3.4.2:** Must display entry pricing (bid/ask/mid/spread)
- **FR-3.4.3:** Must show current pricing and intrinsic/time value
- **FR-3.4.4:** Must calculate and display breakeven analysis
- **FR-3.4.5:** Must show leverage metrics (delta, exposure, capital saved)
- **FR-3.4.6:** Must display performance metrics (CAGR, annualized return)
- **FR-3.4.7:** Must show stock comparison (what if bought stock instead)
- **FR-3.4.8:** Must provide exercise analysis (cost, profit if exercised)
- **FR-3.4.9:** Must show exit strategy targets

#### 3.5 Configuration
- **FR-3.5.1:** Must allow viewing current filter settings
- **FR-3.5.2:** Must allow updating filter parameters
- **FR-3.5.3:** Must persist configuration between sessions
- **FR-3.5.4:** Must support realistic vs. optimistic pricing mode

#### 3.6 Documentation
- **FR-3.6.1:** Must provide in-app user guide
- **FR-3.6.2:** Must provide Schwab setup instructions
- **FR-3.6.3:** Must provide tracking guide
- **FR-3.6.4:** Must render Markdown documentation as HTML

### 4. API Endpoints

#### 4.1 Configuration API
- **FR-4.1.1:** GET /api/config - Retrieve current configuration
- **FR-4.1.2:** POST /api/config - Update configuration

#### 4.2 Scanning API
- **FR-4.2.1:** POST /api/scan - Run options scan for specified tickers
- **FR-4.2.2:** GET /api/ticker/analyze/<ticker> - Analyze single ticker

#### 4.3 Position API
- **FR-4.3.1:** GET /api/positions/active - Get active positions from account
- **FR-4.3.2:** GET /api/performance - Get performance summary with metrics
- **FR-4.3.3:** GET /api/performance?update=true - Update prices and get performance
- **FR-4.3.4:** GET /api/position/<ticker>/<strike>/<expiration> - Get position details

#### 4.4 Ticker API
- **FR-4.4.1:** GET /api/tickers - Get ticker watchlist with dividend info
- **FR-4.4.2:** POST /api/tickers/add - Add ticker to watchlist
- **FR-4.4.3:** POST /api/tickers/remove - Remove ticker from watchlist

#### 4.5 Recommendation API
- **FR-4.5.1:** POST /api/recommendation/remove - Remove recommendation from tracking

#### 4.6 Health API
- **FR-4.6.1:** GET /api/health - Check system health (API, database)

#### 4.7 Documentation API
- **FR-4.7.1:** GET /api/docs/<doc_name> - Get documentation as HTML

### 5. Port Management Integration

#### 5.1 Registration
- **FR-5.1.1:** Must register with Port Manager on startup
- **FR-5.1.2:** Must use port 5010 (or find available if conflict)
- **FR-5.1.3:** Must provide application name "ditm"
- **FR-5.1.4:** Must provide description "DITM Options Portfolio Builder - Web Interface"
- **FR-5.1.5:** Must provide start command "python web_app.py"
- **FR-5.1.6:** Must provide working directory "/home/joe/ai/ditm"

#### 5.2 Port Assignment
- **FR-5.2.1:** Must retrieve assigned port from Port Manager
- **FR-5.2.2:** Must use dynamic port (not hardcoded)
- **FR-5.2.3:** Must handle port conflicts gracefully
- **FR-5.2.4:** Must display port assignment on startup

#### 5.3 Launcher Integration
- **FR-5.3.1:** Must be startable from Port Manager dashboard
- **FR-5.3.2:** Must show as running when active
- **FR-5.3.3:** Must provide "Open" link to application
- **FR-5.3.4:** Must support clean shutdown

## Non-Functional Requirements

### 6. Performance

#### 6.1 Response Time
- **NFR-6.1.1:** Web pages must load in < 2 seconds
- **NFR-6.1.2:** API endpoints must respond in < 5 seconds
- **NFR-6.1.3:** Single ticker scan must complete in < 3 seconds
- **NFR-6.1.4:** Multi-ticker scan (5 tickers) must complete in < 15 seconds
- **NFR-6.1.5:** Database queries must execute in < 500ms

#### 6.2 Scalability
- **NFR-6.2.1:** Must support ≥20 tickers in watchlist
- **NFR-6.2.2:** Must track ≥1000 recommendations in database
- **NFR-6.2.3:** Must handle ≥50 concurrent position updates

### 7. Reliability

#### 7.1 Error Handling
- **NFR-7.1.1:** Must handle Schwab API failures gracefully
- **NFR-7.1.2:** Must retry failed API calls (3 attempts)
- **NFR-7.1.3:** Must validate all user inputs
- **NFR-7.1.4:** Must provide meaningful error messages
- **NFR-7.1.5:** Must log errors for debugging

#### 7.2 Data Integrity
- **NFR-7.2.1:** Must persist all recommendations (no data loss)
- **NFR-7.2.2:** Must handle concurrent database access safely
- **NFR-7.2.3:** Must validate JSON serialization (numpy/pandas → Python)
- **NFR-7.2.4:** Must handle NaN and Infinity values properly

#### 7.3 Availability
- **NFR-7.3.1:** Must auto-refresh OAuth tokens before expiration
- **NFR-7.3.2:** Must reconnect to API after temporary failures
- **NFR-7.3.3:** Must function with stale data if API unavailable

### 8. Security

#### 8.1 Authentication
- **NFR-8.1.1:** Must use OAuth 2.0 for Schwab API access
- **NFR-8.1.2:** Must store tokens securely (file permissions 600)
- **NFR-8.1.3:** Must store credentials in .env file (not in code)
- **NFR-8.1.4:** Must exclude .env from version control

#### 8.2 Data Privacy
- **NFR-8.2.1:** Must not log sensitive data (tokens, account numbers)
- **NFR-8.2.2:** Must use account hash (not raw account number)
- **NFR-8.2.3:** Must run on localhost only (no external exposure)

### 9. Usability

#### 9.1 User Interface
- **NFR-9.1.1:** Must provide clean, professional design
- **NFR-9.1.2:** Must be responsive (desktop, tablet, mobile)
- **NFR-9.1.3:** Must use intuitive navigation
- **NFR-9.1.4:** Must provide helpful tooltips and explanations
- **NFR-9.1.5:** Must use consistent color scheme and typography

#### 9.2 Documentation
- **NFR-9.2.1:** Must provide comprehensive user guide
- **NFR-9.2.2:** Must document all API setup steps
- **NFR-9.2.3:** Must explain all metrics and calculations
- **NFR-9.2.4:** Must include examples and screenshots

### 10. Maintainability

#### 10.1 Code Quality
- **NFR-10.1.1:** Must use modular architecture (separation of concerns)
- **NFR-10.1.2:** Must include docstrings for all functions
- **NFR-10.1.3:** Must use type hints where applicable
- **NFR-10.1.4:** Must follow PEP 8 style guidelines
- **NFR-10.1.5:** Must avoid hardcoded values (use configuration)

#### 10.2 Configuration
- **NFR-10.2.1:** Must externalize all filter thresholds
- **NFR-10.2.2:** Must use environment variables for secrets
- **NFR-10.2.3:** Must persist user preferences in JSON
- **NFR-10.2.4:** Must provide default configuration

#### 10.3 Testing
- **NFR-10.3.1:** Must validate against real market data
- **NFR-10.3.2:** Must test error handling paths
- **NFR-10.3.3:** Must verify all API endpoints
- **NFR-10.3.4:** Must test edge cases (empty results, API failures)

### 11. Deployment

#### 11.1 Environment
- **NFR-11.1.1:** Must run on Linux (Ubuntu/Debian)
- **NFR-11.1.2:** Must require Python 3.7+
- **NFR-11.1.3:** Must use virtual environment (.venv)
- **NFR-11.1.4:** Must install via pip (requirements.txt)

#### 11.2 Dependencies
- **NFR-11.2.1:** Must use schwab-py for API access
- **NFR-11.2.2:** Must use Flask for web server
- **NFR-11.2.3:** Must use pandas/numpy for data analysis
- **NFR-11.2.4:** Must use SQLite for database (no external DB server)
- **NFR-11.2.5:** Must use python-dotenv for environment variables

#### 11.3 Port Management
- **NFR-11.3.1:** Must integrate with global Port Manager
- **NFR-11.3.2:** Must use port-manager CLI for registration
- **NFR-11.3.3:** Must support launcher functionality
- **NFR-11.3.4:** Must avoid port conflicts

## Data Requirements

### 12. Data Storage

#### 12.1 Database Schema
- **DR-12.1.1:** Table: recommendations (main tracking table)
- **DR-12.1.2:** Fields: id, ticker, strike, expiration, status
- **DR-12.1.3:** Fields: entry_date, entry_price, entry_bid, entry_ask, entry_mid
- **DR-12.1.4:** Fields: contracts, stock_entry, delta_entry, extrinsic_value
- **DR-12.1.5:** Fields: current_bid, current_ask, current_mid, stock_current
- **DR-12.1.6:** Fields: last_updated, closed_date, close_reason
- **DR-12.1.7:** Index: (ticker, strike, expiration) for fast lookups

#### 12.2 Configuration Files
- **DR-12.2.1:** .env - API credentials (excluded from git)
- **DR-12.2.2:** web_config.json - User preferences and watchlist
- **DR-12.2.3:** tokens.json - OAuth tokens (auto-managed)
- **DR-12.2.4:** recommendations_history.json - JSON export of database

#### 12.3 Data Retention
- **DR-12.3.1:** Must retain all recommendations indefinitely
- **DR-12.3.2:** Must mark expired positions (not delete)
- **DR-12.3.3:** Must preserve closed position history

## Integration Requirements

### 13. External APIs

#### 13.1 Schwab Trader API
- **IR-13.1.1:** Must use schwab-py library
- **IR-13.1.2:** Must support API version 1.0+
- **IR-13.1.3:** Must handle market hours vs. after-hours data
- **IR-13.1.4:** Must support both sandbox and production environments

#### 13.2 Port Manager
- **IR-13.2.1:** Must import from /home/joe/ai/port_manager
- **IR-13.2.2:** Must use PortManager class for registration
- **IR-13.2.3:** Must call register_port() on startup
- **IR-13.2.4:** Must call get_port() to retrieve assigned port

## Compliance Requirements

### 14. Financial Regulations

#### 14.1 Disclaimers
- **CR-14.1.1:** Must display "not investment advice" disclaimer
- **CR-14.1.2:** Must warn about options trading risks
- **CR-14.1.3:** Must clarify past performance ≠ future results

#### 14.2 Data Usage
- **CR-14.2.1:** Must comply with Schwab API terms of service
- **CR-14.2.2:** Must not redistribute market data
- **CR-14.2.3:** Must use data for personal trading only

## Future Requirements (Roadmap)

### 15. Planned Enhancements

#### 15.1 Visualization
- **FR-15.1.1:** Performance charts (line graphs)
- **FR-15.1.2:** Position heat maps
- **FR-15.1.3:** Risk distribution charts

#### 15.2 Alerts
- **FR-15.2.1:** Email notifications for profit targets
- **FR-15.2.2:** SMS alerts for stop-loss triggers
- **FR-15.2.3:** Position expiration reminders

#### 15.3 Multi-Account
- **FR-15.3.1:** Support multiple Schwab accounts
- **FR-15.3.2:** Aggregate performance across accounts
- **FR-15.3.3:** Account switching in UI

#### 15.4 Strategy Expansion
- **FR-15.4.1:** DITM put options
- **FR-15.4.2:** Vertical spreads
- **FR-15.4.3:** Calendar spreads
- **FR-15.4.4:** Custom strategy builder

#### 15.5 Backtesting
- **FR-15.5.1:** Historical data import
- **FR-15.5.2:** Strategy backtesting engine
- **FR-15.5.3:** Performance comparison (actual vs. backtest)

#### 15.6 Mobile App
- **FR-15.6.1:** Native iOS application
- **FR-15.6.2:** Native Android application
- **FR-15.6.3:** Push notifications
- **FR-15.6.4:** Touch-optimized UI
