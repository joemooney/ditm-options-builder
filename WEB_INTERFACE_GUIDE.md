

# DITM Options Portfolio Builder - Web Interface Guide

## Overview

The DITM Options Portfolio Builder now includes a **professional web interface** that provides an intuitive, visual way to:

- Run options scans with customizable tickers
- View real-time performance analytics
- Track portfolio metrics and risk analytics
- Access comprehensive documentation
- Manage filter settings

Built with Flask (backend) and modern HTML/CSS/JavaScript (frontend), the web interface offers a polished, responsive experience accessible from any web browser.

---

## Quick Start

### 1. Start the Web Server

```bash
cd /home/joe/ai/ditm
source .venv/bin/activate  # Or: .venv/bin/python3
python web_app.py
```

You'll see:
```
======================================================================
DITM Options Portfolio Builder - Web Interface
======================================================================
Starting server at http://localhost:5000
Press Ctrl+C to stop
======================================================================
```

### 2. Open in Browser

Navigate to: **http://localhost:5000**

The dashboard will load automatically.

### 3. First-Time Setup

If you haven't set up Schwab API credentials yet:
1. Click **Documentation** → **Schwab Setup**
2. Follow the instructions to obtain API credentials
3. Configure your `.env` file with credentials
4. Restart the web server

---

## Interface Overview

### Navigation Bar

The top navigation provides quick access to all features:

- **Dashboard** 🏠 - Overview and quick actions
- **New Scan** 🔍 - Run options scans
- **Performance** 📊 - Analytics and metrics
- **Documentation** 📚 - Guides and references
- **Settings** ⚙️ - Configure filters

---

## Features

### 📊 Dashboard

**What it shows:**
- Key portfolio stats (invested, current value, P&L, win rate)
- Open positions table
- Quick action buttons

**Stats Cards:**
- **Total Invested** - Capital deployed in options
- **Current Value** - Real-time portfolio value
- **Total P&L** - Profit/loss ($ and %)
- **Win Rate** - Percentage of profitable trades

**Quick Actions:**
- **Run New Scan** - Jump to scan page
- **Update Performance** - Refresh with live data
- **View Documentation** - Access guides

**Open Positions Table:**
- Recent open positions (up to 10)
- Ticker, strike, expiration, days held
- Cost, current value, P&L

### 🔍 New Scan

**Run options scans** to find DITM call opportunities.

#### How to Use:

1. **Add Ticker Symbols**
   - Type ticker (e.g., "AAPL")
   - Press Enter, comma, or space to add
   - Chip appears for each ticker
   - Click ✕ to remove

2. **Set Target Capital**
   - Default: $50,000
   - Adjust as needed for your portfolio size

3. **Click "Run Scan"**
   - Server queries Schwab API for options chains
   - Applies filters to find DITM candidates
   - Returns recommendations automatically

#### Scan Results:

Displays:
- Summary stats (positions, total cost, equiv shares)
- Detailed table of recommended options
- Ticker, strike, expiration, DTE, delta, contracts, cost, score

All scans are **automatically saved** to the tracking database for performance analysis.

### 📈 Performance Analytics

**Comprehensive performance tracking** with institutional-grade metrics.

#### Summary Metrics:
- Total recommendations tracked
- Open vs. expired positions
- Total invested vs. current value
- Overall P&L ($ and %)
- Win rate and average return
- Average holding period

#### Risk Metrics Grid:

**8 key risk metrics** displayed in cards:
- **Sharpe Ratio** - Risk-adjusted returns
- **Sortino Ratio** - Downside-only risk
- **Max Drawdown** - Largest peak-to-trough decline
- **Calmar Ratio** - Return / max drawdown
- **Profit Factor** - Gross profit / gross loss
- **Win/Loss Ratio** - Avg win / avg loss
- **Expectancy** - Average $ per trade
- **Std Dev** - Return variability

See **USER_GUIDE.md** section "Understanding Risk Metrics" for detailed explanations of each metric.

#### All Positions Table:

Complete history of all recommendations:
- Date, ticker, strike, expiration
- Status (open/expired)
- Days held
- Cost, current value, P&L

**Refresh Button:**
- Click "Refresh Data" to update with live market data from Schwab API
- Recalculates all metrics in real-time

### 📚 Documentation

**Built-in documentation viewer** with all guides.

#### Available Documents:

1. **User Guide** 📖
   - Complete options trading education
   - 40+ pages covering all concepts
   - Risk metrics deep dive
   - Step-by-step trading guide

2. **Schwab Setup** 🔑
   - How to get API credentials
   - Authentication walkthrough
   - Troubleshooting guide

3. **Tracking Guide** 📊
   - Performance tracking system
   - Database schema
   - Advanced analysis techniques

4. **README** ℹ️
   - Project overview
   - Quick start guide
   - Features summary

Documents are **converted from Markdown to HTML** for easy reading in the browser.

### ⚙️ Settings

**Configure filter parameters** for option screening.

#### Customizable Filters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| **MIN_DELTA** | 0.80 | Minimum option delta |
| **MAX_DELTA** | 0.95 | Maximum option delta |
| **MIN_INTRINSIC_PCT** | 0.85 | Minimum intrinsic value % |
| **MIN_DTE** | 90 | Minimum days to expiration |
| **MAX_IV** | 0.30 | Maximum implied volatility |
| **MAX_SPREAD_PCT** | 0.02 | Maximum bid-ask spread % |
| **MIN_OI** | 500 | Minimum open interest |

**How to Use:**
1. Adjust values as desired
2. Click "Save Settings"
3. Settings persist across sessions
4. Click "Reset to Defaults" to restore original values

**Tip:** Conservative traders should increase MIN_DELTA to 0.85+ and decrease MAX_IV to 0.25.

---

## Architecture

### Backend (Flask)

**File:** `web_app.py`

**API Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Serve main HTML page |
| `/api/config` | GET/POST | Load/save configuration |
| `/api/scan` | POST | Run options scan |
| `/api/performance` | GET | Get performance data |
| `/api/ticker/analyze/<ticker>` | GET | Analyze single ticker |
| `/api/docs/<doc_name>` | GET | Serve documentation |
| `/api/health` | GET | Health check |

**Key Features:**
- Integrates with existing `ditm.py` and `recommendation_tracker.py`
- Automatic Schwab client initialization
- JSON responses for all data
- Error handling and validation
- Configuration persistence

### Frontend

**Files:**
- `templates/index.html` - Main HTML structure
- `static/css/style.css` - Professional styling (800+ lines)
- `static/js/app.js` - Application logic (600+ lines)

**Technologies:**
- Vanilla JavaScript (no frameworks required)
- CSS Grid & Flexbox for responsive layouts
- Font Awesome icons
- Modern ES6+ features

**Design Principles:**
- Clean, professional aesthetic
- Responsive (works on mobile/tablet/desktop)
- Intuitive navigation
- Loading states and feedback
- Toast notifications for user actions

---

## Usage Workflows

### Workflow 1: First-Time User

1. **Setup Schwab API**
   - Click "Documentation" → "Schwab Setup"
   - Follow instructions
   - Configure `.env` file
   - Restart web server

2. **Run First Scan**
   - Click "New Scan"
   - Add tickers (AAPL, MSFT, GOOGL, etc.)
   - Click "Run Scan"
   - View recommendations

3. **Check Performance**
   - Click "Performance"
   - View metrics (will show initial scan)
   - Bookmark for future reference

### Workflow 2: Regular Monitoring

1. **Update Performance**
   - Open dashboard
   - Click "Update Performance" (updates with live data)
   - Review P&L changes

2. **Run New Scan**
   - Add new tickers or adjust existing
   - Run scan
   - Compare to previous scans

3. **Adjust Filters**
   - Click "Settings"
   - Tweak parameters based on performance
   - Save settings
   - Run new scan to test

### Workflow 3: Research Mode

1. **Analyze Single Ticker**
   - Use API endpoint: `/api/ticker/analyze/AAPL`
   - View top 10 DITM candidates
   - Compare across multiple tickers

2. **Review Documentation**
   - Click "Documentation"
   - Study User Guide sections
   - Understand risk metrics
   - Learn strategy optimization

3. **Backtest Filters**
   - Change settings (e.g., MIN_DELTA 0.85)
   - Run scan
   - Track performance over time
   - Compare Sharpe/Sortino ratios

---

## Configuration Files

### web_config.json

**Auto-generated** after first scan. Stores user preferences:

```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL", "JNJ", "JPM"],
  "target_capital": 50000,
  "filters": {
    "MIN_DELTA": 0.80,
    "MAX_DELTA": 0.95,
    "MIN_INTRINSIC_PCT": 0.85,
    "MIN_DTE": 90,
    "MAX_IV": 0.30,
    "MAX_SPREAD_PCT": 0.02,
    "MIN_OI": 500
  }
}
```

**Location:** `./web_config.json`

**Persistence:** Settings saved on every update, loaded on startup.

### recommendations_history.json

**Tracking database** created by `recommendation_tracker.py`.

Stores:
- All scans
- All recommendations
- Performance snapshots
- Risk metrics

**Location:** `./recommendations_history.json`

---

## Customization

### Change Port

Edit `web_app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Change from 5000
```

### Add Custom Metrics

1. Update `recommendation_tracker.py` → `calculate_risk_metrics()`
2. Add calculation for new metric
3. Update `web_app.py` → `/api/performance` to return metric
4. Update `static/js/app.js` → `displayPerformance()` to display

### Customize Styling

Edit `static/css/style.css`:

**Change Primary Color:**
```css
:root {
    --primary-color: #10b981;  /* Change from blue to green */
}
```

**Change Layout:**
- Adjust `.stats-grid` grid columns
- Modify `.card` padding/margins
- Change font sizes

### Add New Pages

1. **HTML:** Add `<div id="page-mypage" class="page">` in `index.html`
2. **Nav:** Add link with `data-page="mypage"`
3. **API:** Add endpoint in `web_app.py`
4. **JavaScript:** Add handler in `app.js`

---

## Troubleshooting

### "Cannot connect to server"

**Problem:** Web server not running or crashed.

**Solution:**
```bash
# Check if running
ps aux | grep web_app.py

# Restart
python web_app.py
```

### "Schwab authentication failed"

**Problem:** API credentials not configured or token expired.

**Solution:**
1. Check `.env` file has valid `SCHWAB_APP_KEY` and `SCHWAB_APP_SECRET`
2. Delete `schwab_tokens.json` and re-authenticate
3. Verify app status is "Ready For Use" in Schwab portal

### "No data available"

**Problem:** No scans run yet or database missing.

**Solution:**
1. Run at least one scan from "New Scan" page
2. Check `recommendations_history.json` exists
3. Verify Schwab API is accessible

### "Error running scan"

**Problem:** Schwab API error or invalid ticker.

**Solutions:**
- Check network connection
- Verify tickers are valid symbols
- Run during market hours for best data
- Check browser console (F12) for detailed errors

### "Documentation not loading"

**Problem:** Markdown files missing or path incorrect.

**Solution:**
```bash
# Verify files exist
ls -lh *.md

# Should see:
# README.md
# USER_GUIDE.md
# SCHWAB_SETUP.md
# TRACKING_GUIDE.md
```

### Port Already in Use

**Problem:** Another service using port 5000.

**Solution:**
```bash
# Find process
lsof -i :5000

# Kill it
kill -9 <PID>

# Or change port in web_app.py
```

---

## Security Considerations

### Local Development

**Current setup** runs on `localhost:5000` - only accessible from your machine. This is **safe for personal use**.

### Production Deployment

**DO NOT** deploy to public internet without:

1. **Authentication** - Add login system (Flask-Login)
2. **HTTPS** - Use SSL certificates
3. **Firewall** - Restrict access
4. **Secret Key** - Use strong, random secret key
5. **CORS** - Configure cross-origin policies
6. **Rate Limiting** - Prevent abuse

**For personal use, keep it local!**

### Sensitive Data

**Never commit:**
- `.env` (API credentials)
- `schwab_tokens.json` (OAuth tokens)
- `web_config.json` (personal preferences)
- `recommendations_history.json` (trading data)

All are in `.gitignore` by default.

---

## Performance Optimization

### Large Databases

If `recommendations_history.json` grows large (100+ scans):

**Option 1:** Archive old data
```bash
# Backup
cp recommendations_history.json archive_2025.json

# Clean old (via Python script or manually)
```

**Option 2:** Use pagination
- Modify `get_performance_summary()` to limit rows
- Add pagination controls to UI

### Slow Scans

**Problem:** Scanning many tickers takes time.

**Solutions:**
- Reduce number of tickers per scan
- Increase `delay_between_stocks` in `ditm.py`
- Run during off-peak hours
- Use progress indicators (already included)

### Browser Performance

For best experience:
- Use modern browser (Chrome, Firefox, Safari, Edge)
- Close other tabs
- Clear browser cache if UI seems slow

---

## API Reference

### POST /api/scan

**Request:**
```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL"],
  "target_capital": 50000
}
```

**Response:**
```json
{
  "success": true,
  "portfolio": [
    {
      "Ticker": "AAPL",
      "Stock Price": 225.50,
      "Strike": 200.0,
      "Expiration": "2025-06-20",
      "DTE": 180,
      "Delta": 0.892,
      "Cost/Share": 198.45,
      "Contracts": 4,
      "Total Cost": 11200.00,
      "Equiv Shares": 357,
      "Score": 0.121
    }
  ],
  "summary": {
    "total_invested": 47850.00,
    "total_equiv_shares": 547,
    "num_positions": 5,
    "scan_date": "2025-11-08T15:30:00"
  }
}
```

### GET /api/performance?update=true

**Response:**
```json
{
  "success": true,
  "summary": {
    "total_recommendations": 10,
    "open_positions": 8,
    "expired_positions": 2,
    "total_invested": 95700.00,
    "current_value": 104850.00,
    "total_pnl": 9150.00,
    "total_pnl_pct": 9.56,
    "win_rate": 70.0,
    "avg_return": 12.3,
    "avg_days_held": 45
  },
  "risk_metrics": {
    "sharpe_ratio": 1.45,
    "sortino_ratio": 1.82,
    "max_drawdown": 12.50,
    "profit_factor": 2.15,
    ...
  },
  "positions": [...]
}
```

---

## Advanced Features

### Programmatic Access

Use the API from other applications:

**Python Example:**
```python
import requests

# Run scan
response = requests.post('http://localhost:5000/api/scan', json={
    'tickers': ['AAPL', 'MSFT'],
    'target_capital': 25000
})
data = response.json()
print(data['portfolio'])
```

**JavaScript Example:**
```javascript
// Get performance
fetch('http://localhost:5000/api/performance?update=true')
    .then(response => response.json())
    .then(data => console.log(data.risk_metrics));
```

### Automation

**Schedule Regular Scans:**
```bash
# Cron job (runs daily at 9:30 AM)
30 9 * * * curl -X POST http://localhost:5000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"tickers": ["AAPL", "MSFT"], "target_capital": 50000}'
```

### Export Data

**Via API:**
```bash
# Get performance as JSON
curl http://localhost:5000/api/performance > performance.json
```

**Via Python:**
```python
from recommendation_tracker import RecommendationTracker
tracker = RecommendationTracker()
tracker.export_to_csv('export.csv')
```

---

## Future Enhancements

Potential additions:

- **Charts** - Historical performance graphs (Chart.js)
- **Alerts** - Email/SMS notifications for position updates
- **Comparison** - Side-by-side scan comparisons
- **Backtesting** - Historical strategy simulation
- **Export** - PDF report generation
- **Mobile App** - React Native or Flutter app
- **Multi-user** - Authentication and user accounts
- **Real-time** - WebSocket for live updates

---

## Conclusion

The **DITM Options Portfolio Builder Web Interface** provides a professional, user-friendly way to:

✅ Run options scans with ease
✅ Track performance with institutional metrics
✅ Access comprehensive documentation
✅ Customize filter settings
✅ Monitor portfolio in real-time

**All while maintaining the power and flexibility of the command-line tools!**

For questions or issues, refer to:
- **USER_GUIDE.md** - Complete trading guide
- **TRACKING_GUIDE.md** - Performance tracking
- **SCHWAB_SETUP.md** - API setup

Happy trading! 📈
