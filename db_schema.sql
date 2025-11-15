-- DITM Options Portfolio Builder - Database Schema
-- SQLite database for storing scans, recommendations, and candidates

-- ============================================================================
-- SCANS TABLE
-- Records each scan session with metadata and filter parameters
-- ============================================================================
CREATE TABLE IF NOT EXISTS scans (
    scan_id TEXT PRIMARY KEY,
    scan_date TEXT NOT NULL,
    preset_name TEXT,
    tickers TEXT NOT NULL,  -- JSON array of ticker symbols
    filter_params TEXT NOT NULL,  -- JSON object of filter parameters
    recommendations_count INTEGER DEFAULT 0,
    candidates_count INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_scans_date ON scans(scan_date);
CREATE INDEX idx_scans_preset ON scans(preset_name);

-- ============================================================================
-- RECOMMENDATIONS TABLE
-- Stores the TOP option selected from each scan (one per ticker)
-- This is what the user sees as actionable recommendations
-- ============================================================================
CREATE TABLE IF NOT EXISTS recommendations (
    id TEXT PRIMARY KEY,
    scan_id TEXT NOT NULL,
    recommendation_date TEXT NOT NULL,

    -- Stock info
    ticker TEXT NOT NULL,
    stock_price_at_rec REAL NOT NULL,

    -- Option details
    option_type TEXT DEFAULT 'CALL',
    strike REAL NOT NULL,
    expiration TEXT NOT NULL,
    dte_at_rec INTEGER NOT NULL,

    -- Pricing at recommendation
    premium_bid REAL NOT NULL,
    premium_ask REAL NOT NULL,
    premium_mid REAL NOT NULL,

    -- Greeks and metrics
    delta_at_rec REAL NOT NULL,
    iv_at_rec REAL,
    intrinsic_pct REAL NOT NULL,
    extrinsic_value REAL,
    extrinsic_pct REAL,

    -- Position sizing
    contracts_recommended INTEGER NOT NULL,
    total_cost REAL NOT NULL,
    equiv_shares REAL NOT NULL,
    cost_per_share REAL NOT NULL,

    -- Quality metrics
    score REAL NOT NULL,
    spread_pct REAL NOT NULL,
    open_interest INTEGER NOT NULL,

    -- Status tracking
    status TEXT DEFAULT 'open',  -- open, closed, expired

    -- Current values (updated over time)
    current_bid REAL,
    current_ask REAL,
    current_mid REAL,
    stock_current REAL,
    delta_current REAL,
    current_value REAL,
    unrealized_pnl REAL,
    unrealized_pnl_pct REAL,

    -- Closure info
    last_updated TEXT,
    closed_date TEXT,
    close_reason TEXT,

    FOREIGN KEY (scan_id) REFERENCES scans(scan_id)
);

CREATE INDEX idx_rec_ticker ON recommendations(ticker);
CREATE INDEX idx_rec_status ON recommendations(status);
CREATE INDEX idx_rec_scan ON recommendations(scan_id);
CREATE INDEX idx_rec_expiration ON recommendations(expiration);
CREATE UNIQUE INDEX idx_rec_unique ON recommendations(ticker, strike, expiration);

-- ============================================================================
-- CANDIDATES TABLE
-- Stores ALL qualifying options from each scan (10-50 per ticker)
-- Used for retroactive analysis and preset comparison
-- ============================================================================
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id TEXT NOT NULL,
    scan_date TEXT NOT NULL,

    -- Stock info
    ticker TEXT NOT NULL,
    stock_price REAL NOT NULL,

    -- Option details
    strike REAL NOT NULL,
    expiration TEXT NOT NULL,
    dte INTEGER NOT NULL,

    -- Pricing
    bid REAL NOT NULL,
    ask REAL NOT NULL,
    mid REAL NOT NULL,

    -- Greeks and metrics
    delta REAL NOT NULL,
    iv REAL,
    intrinsic REAL NOT NULL,
    intrinsic_pct REAL NOT NULL,
    extrinsic REAL NOT NULL,
    extrinsic_pct REAL NOT NULL,

    -- Quality metrics
    score REAL NOT NULL,
    spread_pct REAL NOT NULL,
    open_interest INTEGER NOT NULL,
    cost_per_share REAL NOT NULL,

    -- Matching info
    matched_presets TEXT,  -- JSON array of preset names that matched
    recommended BOOLEAN DEFAULT 0,  -- Was this the top pick?

    -- Performance tracking (updated over time if recommended)
    current_mid REAL,
    current_stock_price REAL,
    pnl REAL,
    pnl_pct REAL,

    FOREIGN KEY (scan_id) REFERENCES scans(scan_id)
);

CREATE INDEX idx_cand_scan ON candidates(scan_id);
CREATE INDEX idx_cand_ticker ON candidates(ticker);
CREATE INDEX idx_cand_recommended ON candidates(recommended);
CREATE INDEX idx_cand_date ON candidates(scan_date);

-- ============================================================================
-- PRICE_SNAPSHOTS TABLE
-- Historical price tracking for each recommendation
-- Allows us to chart performance over time
-- ============================================================================
CREATE TABLE IF NOT EXISTS price_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recommendation_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    stock_price REAL NOT NULL,
    option_bid REAL NOT NULL,
    option_ask REAL NOT NULL,
    option_mid REAL NOT NULL,
    delta REAL,
    value REAL NOT NULL,
    pnl REAL NOT NULL,
    pnl_pct REAL NOT NULL,

    FOREIGN KEY (recommendation_id) REFERENCES recommendations(id)
);

CREATE INDEX idx_snap_rec ON price_snapshots(recommendation_id);
CREATE INDEX idx_snap_timestamp ON price_snapshots(timestamp);

-- ============================================================================
-- METADATA TABLE
-- Store application metadata and settings
-- ============================================================================
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Initialize metadata
INSERT OR IGNORE INTO metadata (key, value) VALUES
    ('db_version', '1.0'),
    ('created_at', datetime('now')),
    ('last_schwab_fetch', NULL),
    ('total_scans', '0'),
    ('total_recommendations', '0');

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Open recommendations with current performance
CREATE VIEW IF NOT EXISTS v_open_recommendations AS
SELECT
    r.*,
    s.preset_name,
    s.scan_date as scan_timestamp,
    julianday('now') - julianday(r.recommendation_date) as days_held,
    julianday(r.expiration) - julianday('now') as dte_current
FROM recommendations r
JOIN scans s ON r.scan_id = s.scan_id
WHERE r.status = 'open'
ORDER BY r.recommendation_date DESC;

-- View: Performance summary by preset
CREATE VIEW IF NOT EXISTS v_preset_performance AS
SELECT
    s.preset_name,
    COUNT(DISTINCT r.id) as total_recommendations,
    AVG(r.unrealized_pnl_pct) as avg_return_pct,
    SUM(CASE WHEN r.unrealized_pnl > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate,
    SUM(r.total_cost) as total_invested,
    SUM(r.current_value) as total_current_value,
    SUM(r.unrealized_pnl) as total_pnl,
    AVG(julianday('now') - julianday(r.recommendation_date)) as avg_days_held
FROM recommendations r
JOIN scans s ON r.scan_id = s.scan_id
WHERE s.preset_name IS NOT NULL
GROUP BY s.preset_name;

-- View: Recent scan summary
CREATE VIEW IF NOT EXISTS v_recent_scans AS
SELECT
    s.scan_id,
    s.scan_date,
    s.preset_name,
    s.tickers,
    s.recommendations_count,
    s.candidates_count,
    COUNT(r.id) as actual_recommendations,
    SUM(r.total_cost) as total_invested
FROM scans s
LEFT JOIN recommendations r ON s.scan_id = r.scan_id
GROUP BY s.scan_id
ORDER BY s.scan_date DESC
LIMIT 20;
