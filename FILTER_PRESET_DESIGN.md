# Filter Preset System - Design Document

## Overview
Allow users to create, save, and compare different filter parameter sets to optimize DITM option selection criteria based on historical performance.

## Goals
1. Save multiple named filter presets (e.g., "Conservative", "Aggressive", "High Leverage")
2. Store ALL qualifying options from scans (not just the top pick)
3. Retroactively match past options against different filter presets
4. Compare performance across filter presets
5. Identify which filter parameters lead to best outcomes

## Current Data Flow

### Scan Process
```
1. User runs scan for tickers: [AAPL, MSFT, GOOGL]
2. For each ticker:
   - Fetch options chain from Schwab
   - Apply filters (delta, IV, DTE, spread, etc.)
   - ALL qualifying options stored in rows[]
   - Sort by Score (conservatism)
   - SELECT TOP 1 → save as recommendation
3. Result: 3 recommendations saved (1 per ticker)
```

### Problem
- **Lost Data**: 10-50 qualifying options per ticker are discarded
- **No Comparison**: Can't test if different filters would have been better
- **No Optimization**: Can't refine parameters based on results

## Proposed Solution

### 1. Data Model Changes

#### Add `all_candidates` Table
Store ALL qualifying options from each scan:

```python
{
    "scan_id": "scan_20251115_140530",
    "ticker": "AAPL",
    "strike": 175.0,
    "expiration": "2025-12-19",
    "dte": 34,
    "bid": 17.50,
    "ask": 17.65,
    "mid": 17.575,
    "delta": 0.85,
    "iv": 0.25,
    "intrinsic_pct": 0.92,
    "extrinsic_pct": 0.08,
    "spread_pct": 0.008,
    "oi": 500,
    "score": 0.234,
    "stock_price": 192.50,
    "matched_presets": ["conservative", "moderate"],  # Which presets matched
    "recommended": false  # Was this the top pick?
}
```

#### Add `filter_presets` Configuration
```python
{
    "filter_presets": {
        "conservative": {
            "name": "Conservative (Low Risk)",
            "description": "Minimize time decay and maximize intrinsic value",
            "filters": {
                "MIN_DELTA": 0.80,
                "MAX_DELTA": 0.90,
                "MIN_INTRINSIC_PCT": 0.80,
                "MIN_DTE": 20,
                "MAX_DTE": 45,
                "MAX_IV": 0.25,
                "MAX_SPREAD_PCT": 0.015,
                "MIN_OI": 500,
                "MAX_EXTRINSIC_PCT": 0.20
            }
        },
        "moderate": {
            "name": "Moderate (Balanced)",
            "description": "Balance between leverage and time decay",
            "filters": {
                "MIN_DELTA": 0.75,
                "MAX_DELTA": 0.90,
                "MIN_INTRINSIC_PCT": 0.75,
                "MIN_DTE": 15,
                "MAX_DTE": 60,
                "MAX_IV": 0.30,
                "MAX_SPREAD_PCT": 0.020,
                "MIN_OI": 250,
                "MAX_EXTRINSIC_PCT": 0.25
            }
        },
        "aggressive": {
            "name": "Aggressive (High Leverage)",
            "description": "Maximize leverage, accept more time decay",
            "filters": {
                "MIN_DELTA": 0.70,
                "MAX_DELTA": 0.85,
                "MIN_INTRINSIC_PCT": 0.70,
                "MIN_DTE": 10,
                "MAX_DTE": 90,
                "MAX_IV": 0.35,
                "MAX_SPREAD_PCT": 0.025,
                "MIN_OI": 200,
                "MAX_EXTRINSIC_PCT": 0.30
            }
        },
        "high_liquidity": {
            "name": "High Liquidity",
            "description": "Focus on tight spreads and high volume",
            "filters": {
                "MIN_DELTA": 0.75,
                "MAX_DELTA": 0.90,
                "MIN_INTRINSIC_PCT": 0.75,
                "MIN_DTE": 15,
                "MAX_DTE": 60,
                "MAX_IV": 0.30,
                "MAX_SPREAD_PCT": 0.010,  # Very tight
                "MIN_OI": 1000,  # High volume
                "MAX_EXTRINSIC_PCT": 0.25
            }
        },
        "low_volatility": {
            "name": "Low Volatility",
            "description": "Prefer stable, low-IV stocks",
            "filters": {
                "MIN_DELTA": 0.80,
                "MAX_DELTA": 0.90,
                "MIN_INTRINSIC_PCT": 0.80,
                "MIN_DTE": 20,
                "MAX_DTE": 45,
                "MAX_IV": 0.20,  # Low IV only
                "MAX_SPREAD_PCT": 0.015,
                "MIN_OI": 500,
                "MAX_EXTRINSIC_PCT": 0.20
            }
        }
    }
}
```

### 2. Scan Flow Changes

```python
def build_ditm_portfolio_with_presets(client, tickers, tracker, preset_name="moderate"):
    # 1. Get current preset filters
    preset = get_filter_preset(preset_name)

    # 2. Record scan with preset info
    scan_id = tracker.record_scan(
        scan_date=now(),
        tickers=tickers,
        filter_params=preset["filters"],
        preset_name=preset_name
    )

    # 3. For each ticker, find ALL qualifying options
    for ticker in tickers:
        candidates_df = find_ditm_calls(client, ticker)  # Returns ALL matches

        # 4. Store ALL candidates
        for _, candidate in candidates_df.iterrows():
            # Check which presets this candidate matches
            matched_presets = check_preset_matches(candidate)

            # Save candidate to all_candidates table
            tracker.add_candidate(
                scan_id=scan_id,
                ticker=ticker,
                option_data=candidate,
                matched_presets=matched_presets,
                recommended=(idx == 0)  # Top pick?
            )

        # 5. Save TOP candidate as recommendation (existing behavior)
        if not candidates_df.empty:
            top_candidate = candidates_df.iloc[0]
            tracker.add_recommendation(...)  # Existing code

    return summary
```

### 3. Performance Comparison

#### API Endpoint: `/api/preset/performance`
```json
{
    "success": true,
    "presets": [
        {
            "name": "conservative",
            "total_recommendations": 45,
            "avg_return": 12.5,
            "win_rate": 78.0,
            "sharpe_ratio": 1.85,
            "max_drawdown": -8.5,
            "avg_days_held": 18,
            "total_profit": 5420.00
        },
        {
            "name": "moderate",
            "total_recommendations": 62,
            "avg_return": 15.2,
            "win_rate": 72.0,
            "sharpe_ratio": 1.65,
            "max_drawdown": -12.3,
            "avg_days_held": 21,
            "total_profit": 7150.00
        }
    ]
}
```

#### UI: Preset Comparison Page
```
┌─────────────────────────────────────────────────────┐
│ Filter Preset Performance Comparison                │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Preset          Recs   Win%   Avg Return  Sharpe   │
│  ────────────────────────────────────────────────   │
│  Conservative     45    78%     +12.5%      1.85    │
│  Moderate         62    72%     +15.2%      1.65    │
│  Aggressive       38    65%     +18.7%      1.42    │
│  High Liquidity   51    75%     +13.8%      1.72    │
│  Low Volatility   29    82%     +11.2%      1.95    │
│                                                      │
│  [View Details] [Edit Presets] [Create New]         │
└─────────────────────────────────────────────────────┘
```

### 4. Scan Page UI Changes

```
┌─────────────────────────────────────────────────────┐
│ Run Options Scan                                    │
├─────────────────────────────────────────────────────┤
│  Tickers: [AAPL] [MSFT] [GOOGL] [+ Add]            │
│                                                      │
│  Filter Preset: [Moderate ▼]                        │
│                 • Conservative (Low Risk)            │
│                 • Moderate (Balanced) ✓             │
│                 • Aggressive (High Leverage)         │
│                 • High Liquidity                     │
│                 • Low Volatility                     │
│                 • Custom...                          │
│                                                      │
│  [Run Scan]  [Compare All Presets]                  │
└─────────────────────────────────────────────────────┘
```

### 5. Scan Results Enhancements

Show which presets each option matches:

```
Scan Results - Moderate Preset
═══════════════════════════════════════════════════════

AAPL  $175 Strike  Exp: 2025-12-19  DTE: 34
────────────────────────────────────────────────────
  Delta: 0.85  |  IV: 25%  |  Extrinsic: 8%
  Cost: $1,758  |  Score: 0.234

  Matches: [Conservative] [Moderate] [High Liquidity]
  ────────────────────────────────────────────────────

MSFT  $380 Strike  Exp: 2025-12-19  DTE: 34
────────────────────────────────────────────────────
  Delta: 0.82  |  IV: 28%  |  Extrinsic: 12%
  Cost: $3,820  |  Score: 0.267

  Matches: [Moderate] [High Liquidity]
  ────────────────────────────────────────────────────
```

### 6. Retroactive Analysis

#### Feature: "What If" Analysis
```
┌─────────────────────────────────────────────────────┐
│ Retroactive Preset Analysis                         │
├─────────────────────────────────────────────────────┤
│  Date Range: [Last 30 Days ▼]                       │
│                                                      │
│  If you had used "Aggressive" preset instead:       │
│                                                      │
│  Current (Moderate):  62 positions, +$7,150 (+15%)  │
│  Alternative (Aggr):  38 positions, +$6,890 (+19%)  │
│                                                      │
│  Difference: -24 positions, -$260, +4% avg return   │
│                                                      │
│  Analysis: Aggressive would have made fewer         │
│  recommendations but higher average returns.        │
│  Consider if you prefer quality over quantity.      │
│                                                      │
│  [View Detailed Comparison]                         │
└─────────────────────────────────────────────────────┘
```

## Implementation Phases

### Phase 1: Storage Foundation
- [ ] Add `all_candidates` array to recommendations_history.json
- [ ] Add `filter_presets` to web_config.json
- [ ] Create 5 default presets (conservative → aggressive)
- [ ] Update `add_candidate()` method in RecommendationTracker

### Phase 2: Scan Enhancement
- [ ] Modify `build_ditm_portfolio()` to save ALL candidates
- [ ] Add `check_preset_matches()` function
- [ ] Tag each candidate with matching presets
- [ ] Preserve existing recommendation behavior (top pick)

### Phase 3: API Endpoints
- [ ] `/api/presets` - GET all presets
- [ ] `/api/presets` - POST create/update preset
- [ ] `/api/preset/performance` - GET performance by preset
- [ ] `/api/scan` - Accept preset_name parameter

### Phase 4: UI Updates
- [ ] Preset selector on scan page
- [ ] Preset performance comparison page
- [ ] Preset editor (create/edit/delete)
- [ ] Show matched presets on scan results
- [ ] "What If" retroactive analysis tool

### Phase 5: Analytics
- [ ] Calculate performance metrics per preset
- [ ] Chart preset performance over time
- [ ] Recommend best preset based on historical data
- [ ] Export preset comparison to CSV

## Benefits

1. **Data Preservation**: Keep ALL qualifying options, not just top picks
2. **Optimization**: Identify which filter parameters work best
3. **Experimentation**: Try different strategies without losing data
4. **Learning**: Understand why some parameters outperform others
5. **Confidence**: Make data-driven decisions on filter tuning

## Example Use Cases

### Use Case 1: Compare Conservative vs Aggressive
- User runs scans for 30 days with "Moderate" preset
- Goes to Preset Performance page
- Sees "Conservative" had 82% win rate but only 11% avg return
- Sees "Aggressive" had 65% win rate but 19% avg return
- Decides their risk tolerance favors "Moderate" (75% win, 15% return)

### Use Case 2: Optimize for Liquidity
- User notices some positions have wide spreads
- Creates new preset "Ultra Liquid" with MAX_SPREAD_PCT = 0.005
- Runs retroactive analysis
- Sees this would have eliminated 30% of positions
- But remaining positions had 20% higher returns
- Adopts new preset going forward

### Use Case 3: Market Conditions
- During high volatility, user switches to "Low Volatility" preset
- Filters out high-IV stocks that might have excessive time decay
- During low volatility, switches to "Aggressive" for more leverage
- Tracks which strategy works better in each market regime

## Technical Considerations

### Storage Impact
- Current: ~1KB per recommendation
- With all candidates: ~10-50KB per scan (10-50 options × 1KB each)
- 100 scans = ~1-5MB additional data
- **Acceptable** for JSON storage, may need SQLite migration later

### Performance Impact
- Minimal: All filtering already happens in memory
- Just need to SAVE more data (no extra API calls)
- Retroactive matching is fast (simple conditionals)

### Backward Compatibility
- Existing scans don't have all_candidates → show "N/A"
- Old recommendations still work normally
- Graceful degradation for historical data

## Open Questions

1. **Should we auto-track all presets on every scan?**
   - Pro: Complete data for retroactive analysis
   - Con: More storage, processing time
   - **Recommendation**: Yes, but make it toggleable

2. **Should presets be user-editable?**
   - Pro: Customization, experimentation
   - Con: Can break retroactive comparisons if filters change
   - **Recommendation**: Allow editing but keep version history

3. **Should we show all matched presets or just top N?**
   - Pro (all): Complete transparency
   - Con (all): UI clutter
   - **Recommendation**: Show all, use tags/chips for compact display

## Next Steps

1. Review this design document
2. Decide on implementation scope (all phases or subset)
3. Create database schema updates
4. Implement Phase 1 (storage foundation)
5. Test with sample data before UI work
