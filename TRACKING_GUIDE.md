# DITM Recommendation Tracking System

## Overview

The DITM Options Portfolio Builder now includes a comprehensive tracking system that:

1. **Stores every recommendation** with full details in a JSON database
2. **Tracks performance over time** with historical snapshots
3. **Updates current values** using live market data from Schwab API
4. **Generates performance reports** showing wins, losses, and leverage
5. **Exports to CSV** for external analysis

This allows you to backtest the strategy and evaluate real-world performance.

---

## Quick Start

### 1. Run a Scan (Automatically Tracked)

```bash
.venv/bin/python3 ditm.py
```

Every time you run `ditm.py`, recommendations are automatically saved to `recommendations_history.json`.

### 2. View Performance Report

```bash
# View cached performance (no API calls)
.venv/bin/python3 view_performance.py

# Update with live market data
.venv/bin/python3 view_performance.py --update

# Export to CSV
.venv/bin/python3 view_performance.py --update --export my_performance.csv
```

---

## How It Works

### Database Structure

The tracking system uses a JSON file (`recommendations_history.json`) with three main sections:

#### 1. Metadata
```json
{
  "metadata": {
    "created": "2025-11-08T10:30:00",
    "last_updated": "2025-11-08T14:25:00",
    "version": "1.0"
  }
}
```

#### 2. Scans
Each scan session is recorded:

```json
{
  "scans": {
    "scan_20251108_103000": {
      "scan_date": "2025-11-08T10:30:00",
      "tickers": ["AAPL", "MSFT", "GOOGL", "JNJ", "JPM"],
      "target_capital": 50000,
      "filter_params": {
        "MIN_DELTA": 0.80,
        "MAX_DELTA": 0.95,
        ...
      },
      "recommendations_count": 5
    }
  }
}
```

#### 3. Recommendations
Full details for each recommended option:

```json
{
  "recommendations": [
    {
      "id": "scan_20251108_103000_AAPL_200.0_2025-06-20",
      "scan_id": "scan_20251108_103000",
      "recommendation_date": "2025-11-08T10:30:00",

      "ticker": "AAPL",
      "stock_price_at_rec": 225.50,

      "option_type": "CALL",
      "strike": 200.0,
      "expiration": "2025-06-20",
      "dte_at_rec": 180,

      "premium_bid": 27.80,
      "premium_ask": 28.20,
      "premium_mid": 28.00,

      "delta_at_rec": 0.892,
      "iv_at_rec": 0.24,
      "intrinsic_pct_at_rec": 0.893,
      "oi_at_rec": 5243,
      "spread_pct_at_rec": 0.014,

      "contracts_recommended": 4,
      "total_cost": 11200.00,
      "equiv_shares": 357,
      "score": 0.121,

      "status": "open",
      "current_value": 13600.00,
      "current_stock_price": 232.00,
      "current_delta": 0.905,
      "unrealized_pnl": 2400.00,
      "unrealized_pnl_pct": 21.43,
      "last_updated": "2025-11-15T14:25:00",

      "snapshots": [
        {
          "timestamp": "2025-11-15T14:25:00",
          "stock_price": 232.00,
          "option_premium": 34.00,
          "delta": 0.905,
          "value": 13600.00,
          "pnl": 2400.00,
          "pnl_pct": 21.43
        }
      ]
    }
  ]
}
```

### Data Flow

```
┌─────────────┐
│  ditm.py    │  Runs scan, finds options
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│ RecommendationTracker   │  Saves to database
│ - record_scan()         │
│ - add_recommendation()  │
└──────┬──────────────────┘
       │
       ▼
┌──────────────────────────┐
│ recommendations_history  │  JSON file on disk
│         .json            │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│  view_performance.py     │  Reads & updates
│  - generate_report()     │
│  - update_values()       │
│  - export_to_csv()       │
└──────────────────────────┘
```

---

## Performance Tracking

### What Gets Tracked

For each recommendation, the system tracks:

**At Recommendation Time:**
- Stock price
- Option strike, expiration, premium (bid/ask/mid)
- Greeks (delta, IV)
- Quality metrics (intrinsic %, OI, spread)
- Position sizing (contracts, cost, equiv shares)
- Conservatism score

**Over Time:**
- Current stock price
- Current option value
- Current delta
- Unrealized P&L ($ and %)
- Status (open/expired/closed)
- Historical snapshots with timestamps

### Performance Metrics

The performance report calculates:

1. **Individual Position Metrics**
   - P&L per position ($ and %)
   - Days held
   - Current vs. entry values
   - Stock return for comparison

2. **Portfolio Metrics**
   - Total capital invested
   - Current portfolio value
   - Total P&L ($ and %)
   - Win rate (% of profitable positions)
   - Average return
   - Average holding period

3. **Leverage Analysis**
   - Average stock return
   - Average option return
   - Effective leverage multiplier

4. **Rankings**
   - Top 5 performers
   - Worst 5 performers
   - Current open positions

---

## Usage Examples

### Example 1: Basic Workflow

```bash
# Day 1: Run initial scan
.venv/bin/python3 ditm.py
# Output: 5 recommendations saved to recommendations_history.json

# Day 7: Check performance (1 week later)
.venv/bin/python3 view_performance.py --update

# Output:
# PORTFOLIO OVERVIEW
# Total Recommendations:     5
# Total Capital Invested:    $47,850.00
# Current Portfolio Value:   $51,200.00
# Total P&L:                 $3,350.00 (+7.0%)
```

### Example 2: Multiple Scans Over Time

```bash
# Week 1
.venv/bin/python3 ditm.py  # Scan 1: 5 recommendations

# Week 2 (different market conditions)
.venv/bin/python3 ditm.py  # Scan 2: 5 more recommendations

# Week 3
.venv/bin/python3 ditm.py  # Scan 3: 5 more recommendations

# View all 15 recommendations together
.venv/bin/python3 view_performance.py --update

# Output:
# Total Recommendations:     15
# Open Positions:            15
# Total Invested:            $145,000
# Current Value:             $158,750
# Total P&L:                 $13,750 (+9.5%)
```

### Example 3: Export for Analysis

```bash
# Generate CSV for Excel/analysis
.venv/bin/python3 view_performance.py --update --export analysis.csv

# Open in Excel, Google Sheets, or pandas
# Columns: Rec_Date, Ticker, Strike, Expiration, Status, Days_Held,
#          Entry_Price, Current_Price, P&L, P&L_%, Stock_Return_%, etc.
```

### Example 4: Track Specific Scan

```python
# In Python script or notebook
from recommendation_tracker import RecommendationTracker

tracker = RecommendationTracker()

# Get all scans
scans = tracker.recommendations["scans"]
for scan_id, scan_data in scans.items():
    print(f"{scan_id}: {scan_data['scan_date']} - {scan_data['recommendations_count']} recs")

# Get recommendations from specific scan
scan_recs = [r for r in tracker.recommendations["recommendations"]
             if r["scan_id"] == "scan_20251108_103000"]

print(f"Found {len(scan_recs)} recommendations from that scan")
```

---

## Sample Performance Report

```
================================================================================
DITM OPTIONS RECOMMENDATION PERFORMANCE REPORT
================================================================================
Generated: 2025-11-15 14:25:30
Database: ./recommendations_history.json

PORTFOLIO OVERVIEW
--------------------------------------------------------------------------------
Total Recommendations:     10
  Open Positions:          8
  Expired Positions:       2

Total Capital Invested:    $95,700.00
Current Portfolio Value:   $104,850.00
Total P&L:                 $9,150.00 (+9.6%)

PERFORMANCE METRICS
--------------------------------------------------------------------------------
Win Rate:                  70.0% (7W / 3L)
Average Return:            +12.3%
Average Holding Period:    45 days

LEVERAGE ANALYSIS
--------------------------------------------------------------------------------
Average Stock Return:      +3.2%
Average Option Return:     +12.3%
Effective Leverage:        3.8x

RISK METRICS
--------------------------------------------------------------------------------
Sharpe Ratio:              1.45
Sortino Ratio:             1.82
Max Drawdown:              12.50%
Max Single Loss:           8.30%
Calmar Ratio:              1.92
Profit Factor:             2.15

Average Win:               +15.20% ($1,520)
Average Loss:              -6.80% ($680)
Win/Loss Ratio:            2.24
Expectancy (avg $ per trade): $485

Return Std Dev:            9.50%
Best Trade:                +32.50%
Worst Trade:               -8.30%
Max Consecutive Wins:      4
Max Consecutive Losses:    3

TOP PERFORMERS
--------------------------------------------------------------------------------
  Ticker  Strike  Expiration    P&L_%      P&L
   GOOGL   125.0  2025-06-20  +32.50  3250.00
    AAPL   200.0  2025-06-20  +21.43  2400.00
    MSFT   380.0  2025-06-20  +18.75  1875.00
     JPM   175.0  2025-06-20  +15.20  1140.00
     JNJ   145.0  2025-06-20  +12.30   980.00

WORST PERFORMERS
--------------------------------------------------------------------------------
  Ticker  Strike  Expiration    P&L_%       P&L
     BAC   35.0   2025-03-21  -45.00  -1800.00
      GE   120.0  2025-04-18  -22.50   -900.00
      XOM  105.0  2025-05-16  -8.30    -415.00

CURRENT OPEN POSITIONS
--------------------------------------------------------------------------------
  Ticker  Strike  Expiration  Days_Held  Total_Cost  Current_Value     P&L   P&L_%
    AAPL   200.0  2025-06-20         38    11200.00       13600.00  2400.00  +21.43
    MSFT   380.0  2025-06-20         38    10000.00       11875.00  1875.00  +18.75
   GOOGL   125.0  2025-06-20         38    10000.00       13250.00  3250.00  +32.50
     JNJ   145.0  2025-06-20         38     7950.00        8930.00   980.00  +12.30
     JPM   175.0  2025-06-20         38     7500.00        8640.00  1140.00  +15.20

================================================================================
```

---

## Advanced Usage

### Programmatic Access

You can use the `RecommendationTracker` class directly in your own scripts:

```python
from recommendation_tracker import RecommendationTracker
from ditm import get_schwab_client
import pandas as pd

# Initialize
tracker = RecommendationTracker()
client = get_schwab_client()

# Update all open positions
tracker.update_all_open_recommendations(client)

# Get performance DataFrame
df = tracker.get_performance_summary()

# Custom analysis
winning_trades = df[df["P&L"] > 0]
print(f"Winning trades: {len(winning_trades)}")
print(f"Average win: ${winning_trades['P&L'].mean():.2f}")

losing_trades = df[df["P&L"] < 0]
print(f"Losing trades: {len(losing_trades)}")
print(f"Average loss: ${losing_trades['P&L'].mean():.2f}")

# Analyze by ticker
ticker_performance = df.groupby("Ticker")["P&L_%"].mean().sort_values(ascending=False)
print("\nPerformance by ticker:")
print(ticker_performance)

# Analyze by holding period
df["Hold_Weeks"] = df["Days_Held"] / 7
weekly_return = df["P&L_%"] / df["Hold_Weeks"]
print(f"\nAverage weekly return: {weekly_return.mean():.2f}%")
```

### Filter Optimization

Analyze which filter settings work best:

```python
from recommendation_tracker import RecommendationTracker
import json

tracker = RecommendationTracker()

# Group by scan (each scan has different filters)
for scan_id, scan_data in tracker.recommendations["scans"].items():
    scan_recs = [r for r in tracker.recommendations["recommendations"]
                 if r["scan_id"] == scan_id]

    if scan_recs:
        avg_return = sum(r.get("unrealized_pnl_pct", 0) for r in scan_recs) / len(scan_recs)

        print(f"\n{scan_id}")
        print(f"Filters: MIN_DELTA={scan_data['filter_params']['MIN_DELTA']}, "
              f"MAX_IV={scan_data['filter_params']['MAX_IV']}")
        print(f"Recommendations: {len(scan_recs)}")
        print(f"Average return: {avg_return:+.2f}%")
```

### Historical Snapshots

Access the full history of each position:

```python
from recommendation_tracker import RecommendationTracker
import pandas as pd
import matplotlib.pyplot as plt

tracker = RecommendationTracker()

# Get a specific recommendation
rec = tracker.recommendations["recommendations"][0]

# Extract snapshots
if rec["snapshots"]:
    df = pd.DataFrame(rec["snapshots"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Plot P&L over time
    plt.figure(figsize=(10, 6))
    plt.plot(df["timestamp"], df["pnl_pct"])
    plt.title(f"{rec['ticker']} {rec['strike']} {rec['expiration']} - P&L Over Time")
    plt.xlabel("Date")
    plt.ylabel("P&L %")
    plt.grid(True)
    plt.show()
```

---

## Data Management

### Backup

The database is a single JSON file, easy to backup:

```bash
# Backup
cp recommendations_history.json recommendations_history_backup_$(date +%Y%m%d).json

# Restore
cp recommendations_history_backup_20251108.json recommendations_history.json
```

### Merge Multiple Databases

If running on multiple machines:

```python
import json

# Load databases
with open("machine1_history.json") as f:
    db1 = json.load(f)

with open("machine2_history.json") as f:
    db2 = json.load(f)

# Merge
db1["scans"].update(db2["scans"])
db1["recommendations"].extend(db2["recommendations"])

# Save merged
with open("merged_history.json", "w") as f:
    json.dump(db1, f, indent=2)
```

### Clean Old Data

Remove expired recommendations older than 1 year:

```python
from recommendation_tracker import RecommendationTracker
from datetime import datetime, timedelta

tracker = RecommendationTracker()

cutoff = datetime.now() - timedelta(days=365)

# Filter recommendations
tracker.recommendations["recommendations"] = [
    r for r in tracker.recommendations["recommendations"]
    if datetime.fromisoformat(r["recommendation_date"]) > cutoff
]

tracker._save_database()
print(f"Cleaned old recommendations. Now tracking {len(tracker.recommendations['recommendations'])} total.")
```

---

## Interpreting Results

### Good Performance Indicators

✓ **Win rate > 60%**: More winners than losers
✓ **Average return > 10%**: Beating stock market average
✓ **Leverage 2-4x**: Good risk/reward for DITM
✓ **Low max drawdown**: Losses contained

### Warning Signs

✗ **Win rate < 50%**: More losers than winners
✗ **Large single losses**: Risk management issue
✗ **Delta drift**: Positions becoming ATM/OTM
✗ **Expired positions**: Missing exit opportunities

### Leverage Analysis

**Effective Leverage** = (Avg Option Return) / (Avg Stock Return)

**Interpretation:**
- **1.0x**: No benefit (just buy stock)
- **2-3x**: Good leverage for DITM
- **4-6x**: Excellent leverage
- **>10x**: Suspicious (check data quality)
- **Negative**: Options underperforming stock (avoid strategy)

---

## Best Practices

### 1. Update Regularly

```bash
# Weekly update
0 9 * * MON .venv/bin/python3 view_performance.py --update
```

Set up a cron job or reminder to update weekly.

### 2. Review Before New Scans

```bash
# Before running new scan, check current positions
.venv/bin/python3 view_performance.py --update

# Then decide if you want to add more
.venv/bin/python3 ditm.py
```

### 3. Export Monthly

```bash
# Monthly export for records
.venv/bin/python3 view_performance.py --update \
  --export monthly_$(date +%Y%m).csv
```

### 4. Track Filter Experiments

If you change filter parameters, note it in your scans to compare.

### 5. Monitor Delta Drift

Check the "Delta_Current" column. If positions drift below 0.75, consider closing.

---

## Troubleshooting

### "No recommendations tracked yet"

**Cause**: Database doesn't exist yet.

**Solution**: Run `ditm.py` first to generate recommendations.

### "Failed to update recommendation"

**Cause**: API error or option no longer trading.

**Solution**: Check Schwab API status, try again during market hours.

### "Could not find current price"

**Cause**: Option delisted or not returned by API.

**Solution**: Option may have been delisted or restructured. Mark as closed.

### Large discrepancies in P&L

**Cause**: Stock split, dividend, or data error.

**Solution**: Check for corporate actions. Manually adjust if needed.

---

## Appendix: Database Schema

### Recommendation Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier |
| `scan_id` | string | Parent scan ID |
| `recommendation_date` | ISO datetime | When recommended |
| `ticker` | string | Stock symbol |
| `stock_price_at_rec` | float | Stock price at recommendation |
| `option_type` | string | "CALL" or "PUT" |
| `strike` | float | Strike price |
| `expiration` | string | YYYY-MM-DD |
| `dte_at_rec` | int | Days to expiration at rec |
| `premium_bid` | float | Bid at rec |
| `premium_ask` | float | Ask at rec |
| `premium_mid` | float | Mid at rec |
| `delta_at_rec` | float | Delta at rec |
| `iv_at_rec` | float | IV at rec |
| `intrinsic_pct_at_rec` | float | Intrinsic % at rec |
| `oi_at_rec` | int | Open interest at rec |
| `spread_pct_at_rec` | float | Spread % at rec |
| `cost_per_share` | float | Cost per delta-adj share |
| `contracts_recommended` | int | Number of contracts |
| `total_cost` | float | Total position cost |
| `equiv_shares` | float | Delta-adjusted shares |
| `score` | float | Conservatism score |
| `status` | string | "open", "expired", "closed" |
| `current_value` | float | Current position value |
| `current_stock_price` | float | Current stock price |
| `current_delta` | float | Current delta |
| `unrealized_pnl` | float | P&L in dollars |
| `unrealized_pnl_pct` | float | P&L in percent |
| `last_updated` | ISO datetime | Last update time |
| `snapshots` | array | Historical snapshots |

### Snapshot Object

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | ISO datetime | Snapshot time |
| `stock_price` | float | Stock price |
| `option_premium` | float | Option price |
| `delta` | float | Delta |
| `value` | float | Position value |
| `pnl` | float | P&L dollars |
| `pnl_pct` | float | P&L percent |

---

## Conclusion

The DITM Recommendation Tracking System provides comprehensive performance analysis, allowing you to:

- **Validate the strategy** with real data
- **Optimize filters** based on results
- **Track positions** over time
- **Learn from** winners and losers
- **Export data** for further analysis

Use this data to continuously improve your DITM options trading approach!
