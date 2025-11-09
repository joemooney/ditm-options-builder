// DITM Options Portfolio Builder - Frontend Application

// State
let currentPage = 'dashboard';
let config = null;
let tickers = [];

// Theme Management
function initializeTheme() {
    // Get saved theme or default to dark
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const icon = document.querySelector('#theme-toggle i');
    if (icon) {
        // Show sun icon in dark mode (click to go light)
        // Show moon icon in light mode (click to go dark)
        icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeTheme();
    loadConfig();
    setupEventListeners();
    loadDashboard();
});

// Setup event listeners
function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;
            showPage(page);
        });
    });

    // Scan form
    document.getElementById('scan-form').addEventListener('submit', handleScanSubmit);

    // Ticker input
    document.getElementById('tickers-input').addEventListener('keydown', handleTickerInput);

    // Settings form
    document.getElementById('settings-form').addEventListener('submit', handleSettingsSubmit);
}

// Page navigation
function showPage(pageName) {
    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.page === pageName) {
            link.classList.add('active');
        }
    });

    // Update active page
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });

    const targetPage = document.getElementById(`page-${pageName}`);
    if (targetPage) {
        targetPage.classList.add('active');
        currentPage = pageName;

        // Load page-specific data
        if (pageName === 'performance') {
            loadPerformance(false);
        } else if (pageName === 'settings') {
            loadSettings();
        } else if (pageName === 'scan') {
            loadScanPage();
        }
    }
}

// Load configuration
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        config = await response.json();
        tickers = config.tickers || [];
        updateTickerChips();
    } catch (error) {
        showToast('Error loading configuration', 'error');
        console.error(error);
    }
}

// Load scan page
async function loadScanPage() {
    try {
        // Reload tickers from configuration
        const response = await fetch('/api/tickers');
        const data = await response.json();

        if (data.success) {
            tickers = data.tickers || [];
            updateTickerChips();
        }
    } catch (error) {
        console.error('Error loading scan page:', error);
    }
}

// Load dashboard
async function loadDashboard() {
    try {
        const response = await fetch('/api/performance?update=false');
        const data = await response.json();

        if (data.success && data.summary) {
            updateDashboardStats(data.summary);
            updateActiveAndRecommendedPositions(data.positions);
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Update dashboard stats
function updateDashboardStats(summary) {
    document.getElementById('stat-invested').textContent = formatCurrency(summary.total_invested);
    document.getElementById('stat-value').textContent = formatCurrency(summary.current_value);

    const pnlElement = document.getElementById('stat-pnl');
    pnlElement.textContent = formatCurrency(summary.total_pnl) +
                            ` (${formatPercent(summary.total_pnl_pct)})`;
    pnlElement.className = 'stat-value ' + (summary.total_pnl >= 0 ? 'positive' : 'negative');

    document.getElementById('stat-winrate').textContent = formatPercent(summary.win_rate);
}

// Update active and recommended positions tables
function updateActiveAndRecommendedPositions(positions) {
    if (!positions || positions.length === 0) {
        document.getElementById('active-positions-table').innerHTML = '<p class="text-muted">No active positions</p>';
        document.getElementById('recommended-positions-table').innerHTML = '<p class="text-muted">No recommendations</p>';
        return;
    }

    // Filter positions
    const activePositions = positions.filter(p => p.Status === 'open' && p.Is_Active);
    const recommendedPositions = positions.filter(p => p.Status === 'open' && !p.Is_Active);

    // Update active positions
    const activeContainer = document.getElementById('active-positions-table');
    if (activePositions.length === 0) {
        activeContainer.innerHTML = '<p class="text-muted">No active positions in your account</p>';
    } else {
        let html = '<table class="table"><thead><tr>';
        html += '<th>Ticker</th><th>Strike</th><th>Expiration</th><th>DTE</th>';
        html += '<th>Cost</th><th>Value</th><th>P&L</th>';
        html += '</tr></thead><tbody>';

        activePositions.forEach(pos => {
            const pnlClass = pos['P&L'] >= 0 ? 'positive' : 'negative';
            html += `<tr class="clickable-row" onclick="showPositionDetail('${pos.Ticker}', '${pos.Strike}', '${pos.Expiration}')" style="cursor: pointer;">`;
            html += `<td><strong>${pos.Ticker}</strong></td>`;
            html += `<td>${pos.Strike}</td>`;
            html += `<td>${pos.Expiration}</td>`;
            html += `<td>${pos.DTE || 0}</td>`;
            html += `<td>${formatCurrency(pos.Total_Cost)}</td>`;
            html += `<td>${formatCurrency(pos.Current_Value)}</td>`;
            html += `<td class="${pnlClass}">${formatCurrency(pos['P&L'])} (${formatPercent(pos['P&L_%'])})</td>`;
            html += '</tr>';
        });

        html += '</tbody></table>';
        activeContainer.innerHTML = html;
    }

    // Update recommended positions
    const recommendedContainer = document.getElementById('recommended-positions-table');
    if (recommendedPositions.length === 0) {
        recommendedContainer.innerHTML = '<p class="text-muted">No new recommendations. Run a scan to find opportunities!</p>';
    } else {
        let html = '<table class="table"><thead><tr>';
        html += '<th>Ticker</th><th>Strike</th><th>Expiration</th><th>DTE</th>';
        html += '<th>Cost/Share</th><th>Delta</th><th>IV</th><th>Score</th>';
        html += '</tr></thead><tbody>';

        recommendedPositions.slice(0, 10).forEach(pos => {
            html += `<tr class="clickable-row" onclick="showPositionDetail('${pos.Ticker}', '${pos.Strike}', '${pos.Expiration}')" style="cursor: pointer;">`;
            html += `<td><strong>${pos.Ticker}</strong></td>`;
            html += `<td>${pos.Strike}</td>`;
            html += `<td>${pos.Expiration}</td>`;
            html += `<td>${pos.DTE || 0}</td>`;
            html += `<td>${formatCurrency(pos.Cost_Share || pos['Cost/Share'] || 0)}</td>`;
            html += `<td>${formatPercent(pos.Delta_Entry * 100)}</td>`;
            html += `<td>${formatPercent((pos.IV_Entry || 0) * 100)}</td>`;
            html += `<td>${(pos.Score || 0).toFixed(3)}</td>`;
            html += '</tr>';
        });

        html += '</tbody></table>';
        recommendedContainer.innerHTML = html;
    }
}

// Handle ticker input
function handleTickerInput(e) {
    if (e.key === 'Enter' || e.key === ',' || e.key === ' ') {
        e.preventDefault();
        const input = e.target;
        const ticker = input.value.trim().toUpperCase().replace(/[^A-Z]/g, '');

        if (ticker && !tickers.includes(ticker)) {
            tickers.push(ticker);
            input.value = '';
            updateTickerChips();
        }
    } else if (e.key === 'Backspace' && e.target.value === '' && tickers.length > 0) {
        tickers.pop();
        updateTickerChips();
    }
}

// Update ticker chips display
function updateTickerChips() {
    const container = document.getElementById('ticker-chips');
    container.innerHTML = tickers.map(ticker => `
        <div class="ticker-chip">
            ${ticker}
            <span class="ticker-chip-remove" onclick="removeTicker('${ticker}')">
                <i class="fas fa-times"></i>
            </span>
        </div>
    `).join('');

    // Update ticker count in scan page
    const countElement = document.getElementById('ticker-count-scan');
    if (countElement) {
        if (tickers.length > 0) {
            countElement.textContent = `${tickers.length} ticker${tickers.length !== 1 ? 's' : ''} selected. Add more using Enter, comma, or space.`;
        } else {
            countElement.textContent = 'Add tickers using Enter, comma, or space. Manage your watchlist in Settings.';
        }
    }
}

// Remove ticker
function removeTicker(ticker) {
    tickers = tickers.filter(t => t !== ticker);
    updateTickerChips();
}

// Handle scan submission
async function handleScanSubmit(e) {
    e.preventDefault();

    const capital = parseInt(document.getElementById('capital-input').value);

    if (tickers.length === 0) {
        showToast('Please add at least one ticker symbol', 'error');
        return;
    }

    showLoading('Running options scan...');

    try {
        const response = await fetch('/api/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tickers: tickers,
                target_capital: capital
            })
        });

        const data = await response.json();
        hideLoading();

        if (data.success) {
            displayScanResults(data);
            showToast('Scan completed successfully!', 'success');
            loadDashboard(); // Refresh dashboard
        } else {
            showToast(data.error || data.message || 'Scan failed', 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('Error running scan: ' + error.message, 'error');
        console.error(error);
    }
}

// Display scan results
function displayScanResults(data) {
    const resultsDiv = document.getElementById('scan-results');
    const contentDiv = document.getElementById('scan-results-content');

    let html = '<div class="stats-grid mb-4">';
    html += `<div class="stat-card"><div class="stat-icon blue"><i class="fas fa-list"></i></div>
             <div class="stat-content"><div class="stat-label">Positions</div>
             <div class="stat-value">${data.summary.num_positions}</div></div></div>`;
    html += `<div class="stat-card"><div class="stat-icon green"><i class="fas fa-dollar-sign"></i></div>
             <div class="stat-content"><div class="stat-label">Total Cost</div>
             <div class="stat-value">${formatCurrency(data.summary.total_invested)}</div></div></div>`;
    html += `<div class="stat-card"><div class="stat-icon purple"><i class="fas fa-chart-line"></i></div>
             <div class="stat-content"><div class="stat-label">Equiv Shares</div>
             <div class="stat-value">${data.summary.total_equiv_shares.toFixed(0)}</div></div></div>`;
    html += '</div>';

    if (data.portfolio && data.portfolio.length > 0) {
        html += '<table class="table"><thead><tr>';
        html += '<th>Ticker</th><th>Strike</th><th>Expiration</th><th>DTE</th>';
        html += '<th>Delta</th><th>Contracts</th><th>Cost</th><th>Score</th>';
        html += '</tr></thead><tbody>';

        data.portfolio.forEach(pos => {
            html += '<tr>';
            html += `<td><strong>${pos.Ticker}</strong></td>`;
            html += `<td>${pos.Strike}</td>`;
            html += `<td>${pos.Expiration}</td>`;
            html += `<td>${pos.DTE}</td>`;
            html += `<td>${pos.Delta.toFixed(3)}</td>`;
            html += `<td>${pos.Contracts}</td>`;
            html += `<td>${formatCurrency(pos['Total Cost'])}</td>`;
            html += `<td>${pos.Score.toFixed(3)}</td>`;
            html += '</tr>';
        });

        html += '</tbody></table>';
    }

    contentDiv.innerHTML = html;
    resultsDiv.style.display = 'block';
}

// Load performance data
async function loadPerformance(update = false) {
    showLoading('Loading performance data...');

    try {
        const response = await fetch(`/api/performance?update=${update}`);
        const data = await response.json();
        hideLoading();

        if (data.success) {
            displayPerformance(data);
        } else {
            showToast(data.error || 'Error loading performance', 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('Error loading performance: ' + error.message, 'error');
        console.error(error);
    }
}

// Display performance data
function displayPerformance(data) {
    // Risk metrics
    if (data.risk_metrics) {
        const metricsDiv = document.getElementById('risk-metrics-grid');
        const metrics = data.risk_metrics;

        let html = '';
        html += createMetricCard('Sharpe Ratio', metrics.sharpe_ratio.toFixed(2));
        html += createMetricCard('Sortino Ratio', metrics.sortino_ratio.toFixed(2));
        html += createMetricCard('Max Drawdown', formatPercent(metrics.max_drawdown));
        html += createMetricCard('Calmar Ratio', metrics.calmar_ratio.toFixed(2));
        html += createMetricCard('Profit Factor', metrics.profit_factor.toFixed(2));
        html += createMetricCard('Win/Loss Ratio',
            (metrics.avg_win / metrics.avg_loss).toFixed(2));
        html += createMetricCard('Expectancy', formatCurrency(metrics.expectancy));
        html += createMetricCard('Std Dev', formatPercent(metrics.std_return));

        metricsDiv.innerHTML = html;
    }

    // Positions table
    if (data.positions && data.positions.length > 0) {
        const tableDiv = document.getElementById('performance-table');
        let html = '<table class="table"><thead><tr>';
        html += '<th>Date</th><th>Ticker</th><th>Strike</th><th>Exp</th>';
        html += '<th>Status</th><th>Days</th><th>Cost</th><th>Value</th><th>P&L</th>';
        html += '</tr></thead><tbody>';

        data.positions.forEach(pos => {
            const pnlClass = pos['P&L'] >= 0 ? 'positive' : 'negative';
            html += `<tr class="clickable-row" onclick="showPositionDetail('${pos.Ticker}', '${pos.Strike}', '${pos.Expiration}')" style="cursor: pointer;">`;
            html += `<td>${pos.Rec_Date}</td>`;
            html += `<td><strong>${pos.Ticker}</strong></td>`;
            html += `<td>${pos.Strike}</td>`;
            html += `<td>${pos.Expiration}</td>`;
            html += `<td>${pos.Status}</td>`;
            html += `<td>${pos.Days_Held}</td>`;
            html += `<td>${formatCurrency(pos.Total_Cost)}</td>`;
            html += `<td>${formatCurrency(pos.Current_Value)}</td>`;
            html += `<td class="${pnlClass}">${formatCurrency(pos['P&L'])} (${formatPercent(pos['P&L_%'])})</td>`;
            html += '</tr>';
        });

        html += '</tbody></table>';
        tableDiv.innerHTML = html;
    }
}

// Create metric card HTML
function createMetricCard(label, value) {
    return `
        <div class="metric-item">
            <div class="metric-label">${label}</div>
            <div class="metric-value">${value}</div>
        </div>
    `;
}

// Update performance (with live data)
function updatePerformance() {
    loadPerformance(true);
}

// Load documentation
async function loadDoc(docName) {
    showLoading('Loading documentation...');

    try {
        const response = await fetch(`/api/docs/${docName}`);
        const data = await response.json();
        hideLoading();

        if (data.success) {
            document.getElementById('doc-content').innerHTML = data.content;
        } else {
            showToast('Error loading document', 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('Error loading document: ' + error.message, 'error');
        console.error(error);
    }
}

// Load settings
async function loadSettings() {
    if (!config || !config.filters) return;

    document.getElementById('setting-min-delta').value = config.filters.MIN_DELTA;
    document.getElementById('setting-max-delta').value = config.filters.MAX_DELTA;
    document.getElementById('setting-min-intrinsic').value = config.filters.MIN_INTRINSIC_PCT;
    document.getElementById('setting-min-dte').value = config.filters.MIN_DTE;
    document.getElementById('setting-max-iv').value = config.filters.MAX_IV;
    document.getElementById('setting-max-spread').value = config.filters.MAX_SPREAD_PCT;
    document.getElementById('setting-min-oi').value = config.filters.MIN_OI;

    // Load ticker list
    await loadTickerList();

    // Allow Enter key on new ticker input
    document.getElementById('new-ticker-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            addTicker();
        }
    });
}

// Load ticker list
async function loadTickerList() {
    try {
        const response = await fetch('/api/tickers');
        const data = await response.json();

        if (data.success) {
            displayTickerList(data.tickers);
        }
    } catch (error) {
        console.error('Error loading tickers:', error);
        showToast('Error loading ticker list', 'error');
    }
}

// Display ticker list
function displayTickerList(tickerList) {
    const container = document.getElementById('ticker-list');
    const countBadge = document.getElementById('ticker-count');

    countBadge.textContent = `${tickerList.length} ticker${tickerList.length !== 1 ? 's' : ''}`;

    if (tickerList.length === 0) {
        container.innerHTML = '<p class="text-muted">No tickers in watchlist. Add some above!</p>';
        return;
    }

    let html = '<div class="ticker-grid">';
    tickerList.forEach(ticker => {
        html += `
            <div class="ticker-item">
                <span class="ticker-symbol">${ticker}</span>
                <button class="btn-icon-danger" onclick="removeTickerFromList('${ticker}')"
                        title="Remove ${ticker}">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
    });
    html += '</div>';

    container.innerHTML = html;
}

// Add ticker to watchlist
async function addTicker() {
    const input = document.getElementById('new-ticker-input');
    const ticker = input.value.trim().toUpperCase();

    if (!ticker) {
        showToast('Please enter a ticker symbol', 'error');
        return;
    }

    // Basic validation
    if (!/^[A-Z]{1,5}$/.test(ticker)) {
        showToast('Invalid ticker symbol. Use 1-5 letters only.', 'error');
        return;
    }

    try {
        const response = await fetch('/api/tickers/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticker: ticker })
        });

        const data = await response.json();

        if (data.success) {
            input.value = '';
            displayTickerList(data.tickers);
            // Update global tickers array so scan page will have latest
            tickers = data.tickers;
            showToast(`Added ${ticker} to watchlist`, 'success');
        } else {
            showToast(data.error || 'Failed to add ticker', 'error');
        }
    } catch (error) {
        console.error('Error adding ticker:', error);
        showToast('Error adding ticker: ' + error.message, 'error');
    }
}

// Remove ticker from watchlist
async function removeTickerFromList(ticker) {
    if (!confirm(`Remove ${ticker} from watchlist?`)) {
        return;
    }

    try {
        const response = await fetch('/api/tickers/remove', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticker: ticker })
        });

        const data = await response.json();

        if (data.success) {
            displayTickerList(data.tickers);
            // Update global tickers array so scan page will have latest
            tickers = data.tickers;
            showToast(`Removed ${ticker} from watchlist`, 'success');
        } else {
            showToast(data.error || 'Failed to remove ticker', 'error');
        }
    } catch (error) {
        console.error('Error removing ticker:', error);
        showToast('Error removing ticker: ' + error.message, 'error');
    }
}

// Handle settings submission
async function handleSettingsSubmit(e) {
    e.preventDefault();

    const newConfig = {
        tickers: tickers,
        target_capital: config.target_capital,
        filters: {
            MIN_DELTA: parseFloat(document.getElementById('setting-min-delta').value),
            MAX_DELTA: parseFloat(document.getElementById('setting-max-delta').value),
            MIN_INTRINSIC_PCT: parseFloat(document.getElementById('setting-min-intrinsic').value),
            MIN_DTE: parseInt(document.getElementById('setting-min-dte').value),
            MAX_IV: parseFloat(document.getElementById('setting-max-iv').value),
            MAX_SPREAD_PCT: parseFloat(document.getElementById('setting-max-spread').value),
            MIN_OI: parseInt(document.getElementById('setting-min-oi').value)
        }
    };

    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newConfig)
        });

        const data = await response.json();

        if (data.success) {
            config = newConfig;
            showToast('Settings saved successfully!', 'success');
        } else {
            showToast('Error saving settings', 'error');
        }
    } catch (error) {
        showToast('Error saving settings: ' + error.message, 'error');
        console.error(error);
    }
}

// Reset settings to defaults
function resetSettings() {
    if (confirm('Reset all settings to defaults?')) {
        document.getElementById('setting-min-delta').value = 0.80;
        document.getElementById('setting-max-delta').value = 0.95;
        document.getElementById('setting-min-intrinsic').value = 0.85;
        document.getElementById('setting-min-dte').value = 90;
        document.getElementById('setting-max-iv').value = 0.30;
        document.getElementById('setting-max-spread').value = 0.02;
        document.getElementById('setting-min-oi').value = 500;
        showToast('Settings reset to defaults', 'info');
    }
}

// Utility functions
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
    }).format(value || 0);
}

function formatPercent(value) {
    return (value || 0).toFixed(2) + '%';
}

function showLoading(message = 'Loading...') {
    const overlay = document.getElementById('loading-overlay');
    const messageEl = document.getElementById('loading-message');
    messageEl.textContent = message;
    overlay.style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');

    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        info: 'fa-info-circle'
    };

    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-icon">
            <i class="fas ${icons[type]}"></i>
        </div>
        <div class="toast-message">${message}</div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Show position detail modal
async function showPositionDetail(ticker, strike, expiration) {
    const modal = document.getElementById('position-detail-modal');
    const content = document.getElementById('position-detail-content');

    modal.style.display = 'flex';
    content.innerHTML = '<p class="text-muted">Loading position analysis...</p>';

    try {
        const response = await fetch(`/api/position/${ticker}/${strike}/${expiration}`);
        const data = await response.json();

        if (data.success) {
            displayPositionDetail(data.position, data.analysis);
        } else {
            content.innerHTML = `<p class="text-danger">Error: ${data.error}</p>`;
        }
    } catch (error) {
        content.innerHTML = `<p class="text-danger">Error loading position: ${error.message}</p>`;
        console.error(error);
    }
}

// Display position detail
function displayPositionDetail(position, analysis) {
    const content = document.getElementById('position-detail-content');

    const pnl = position['P&L'] || 0;
    const pnlPct = position['P&L_%'] || 0;
    const status = position.Status || 'unknown';
    const isProfitable = pnl >= 0;

    let html = `
        <!-- Position Header -->
        <div class="position-header">
            <div class="position-title">
                <h3>${position.Ticker} $${position.Strike} Call - ${position.Expiration}</h3>
                <p class="text-muted">Recommended on ${position.Rec_Date}</p>
            </div>
            <div class="position-status ${status}">${status.toUpperCase()}</div>
        </div>

        <!-- Current Performance -->
        <div class="detail-section">
            <h4><i class="fas fa-chart-line"></i> Current Performance</h4>
            <div class="detail-grid">
                <div class="detail-item ${isProfitable ? 'positive' : 'negative'}">
                    <div class="detail-label">Profit/Loss</div>
                    <div class="detail-value large">${formatCurrency(pnl)}</div>
                    <small>${formatPercent(pnlPct)}</small>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Total Invested</div>
                    <div class="detail-value">${formatCurrency(position.Total_Cost)}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Current Value</div>
                    <div class="detail-value">${formatCurrency(position.Current_Value)}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Days Held</div>
                    <div class="detail-value">${analysis.days_held}</div>
                    <small>${analysis.days_to_expiration} DTE remaining</small>
                </div>
            </div>
        </div>

        <!-- Option Details -->
        <div class="detail-section">
            <h4><i class="fas fa-info-circle"></i> Option Details</h4>
            <div class="detail-grid">
                <div class="detail-item">
                    <div class="detail-label">Current Stock Price</div>
                    <div class="detail-value">${formatCurrency(analysis.current_stock_price)}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Strike Price</div>
                    <div class="detail-value">${formatCurrency(position.Strike)}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Contracts</div>
                    <div class="detail-value">${analysis.contracts}</div>
                    <small>${analysis.contracts * 100} shares equivalent</small>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Intrinsic Value</div>
                    <div class="detail-value">${formatCurrency(analysis.intrinsic_value)}</div>
                </div>
            </div>
        </div>

        <!-- Breakeven Analysis -->
        <div class="detail-section">
            <h4><i class="fas fa-balance-scale"></i> Breakeven Analysis</h4>
            <div class="breakeven-indicator">
                <i class="fas ${analysis.distance_to_breakeven >= 0 ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
                <div>
                    <strong>Breakeven Price: ${formatCurrency(analysis.breakeven)}</strong><br>
                    <span>Stock is currently ${formatCurrency(Math.abs(analysis.distance_to_breakeven))}
                    ${analysis.distance_to_breakeven >= 0 ? 'above' : 'below'} breakeven
                    (${formatPercent(Math.abs(analysis.distance_to_breakeven_pct))})</span>
                </div>
            </div>
            <div class="detail-grid">
                <div class="detail-item">
                    <div class="detail-label">Cost Per Share</div>
                    <div class="detail-value">${formatCurrency(analysis.cost_per_share)}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Breakeven Stock Price</div>
                    <div class="detail-value">${formatCurrency(analysis.breakeven)}</div>
                    <small>Strike + Cost/Share</small>
                </div>
            </div>
        </div>

        <!-- Exit Strategy -->
        <div class="detail-section">
            <h4><i class="fas fa-flag-checkered"></i> Exit Strategy Recommendations</h4>

            <div class="exit-strategy-box">
                <h5><i class="fas fa-trophy"></i> Profit Targets</h5>
                <p>Consider taking profits at these levels:</p>
                <div class="exit-targets">
                    <div class="exit-target">
                        <div class="exit-target-label">50% Profit Target</div>
                        <div class="exit-target-value">${formatCurrency(analysis.exit_targets.take_profit_50.price)}</div>
                        <small>Gain: ${formatCurrency(analysis.exit_targets.take_profit_50.gain)}</small>
                    </div>
                    <div class="exit-target">
                        <div class="exit-target-label">100% Profit Target</div>
                        <div class="exit-target-value">${formatCurrency(analysis.exit_targets.take_profit_100.price)}</div>
                        <small>Gain: ${formatCurrency(analysis.exit_targets.take_profit_100.gain)}</small>
                    </div>
                </div>
                <p style="margin-top: 1rem;"><strong>Strategy:</strong> Sell 50% of position at first target, let remainder run to second target or exit before expiration.</p>
            </div>

            <div class="warning-box">
                <p><strong><i class="fas fa-exclamation-triangle"></i> Stop Loss:</strong>
                Consider exiting if option price falls to ${formatCurrency(analysis.exit_targets.stop_loss.price)}
                (20% loss = ${formatCurrency(analysis.exit_targets.stop_loss.loss)})</p>
            </div>
        </div>

        <!-- Execution Instructions -->
        <div class="detail-section">
            <h4><i class="fas fa-tasks"></i> How to Execute This Trade</h4>
            <ul class="instruction-list">
                <li data-step="1">
                    <div>
                        <strong>Log into Schwab</strong><br>
                        Navigate to Trade → Options
                    </div>
                </li>
                <li data-step="2">
                    <div>
                        <strong>Enter Position Details</strong><br>
                        Symbol: ${position.Ticker}, Strike: $${position.Strike},
                        Expiration: ${position.Expiration}, Type: CALL
                    </div>
                </li>
                <li data-step="3">
                    <div>
                        <strong>Select Action</strong><br>
                        Action: BUY TO OPEN, Quantity: ${analysis.contracts} contract(s)
                    </div>
                </li>
                <li data-step="4">
                    <div>
                        <strong>Set Order Type</strong><br>
                        Use LIMIT order at or below current ask price to control cost
                    </div>
                </li>
                <li data-step="5">
                    <div>
                        <strong>Review and Submit</strong><br>
                        Verify total cost ≈ ${formatCurrency(position.Total_Cost)}, then submit
                    </div>
                </li>
            </ul>
        </div>

        <!-- Exit Instructions -->
        <div class="detail-section">
            <h4><i class="fas fa-sign-out-alt"></i> How to Exit This Position</h4>
            <ul class="instruction-list">
                <li data-step="1">
                    <div>
                        <strong>Monitor Price Targets</strong><br>
                        Set price alerts at ${formatCurrency(analysis.exit_targets.take_profit_50.price)} (50% profit)
                        and ${formatCurrency(analysis.exit_targets.take_profit_100.price)} (100% profit)
                    </div>
                </li>
                <li data-step="2">
                    <div>
                        <strong>Scale Out Strategy</strong><br>
                        At 50% profit: Sell ${Math.floor(analysis.contracts / 2)} contract(s) to lock in gains<br>
                        At 100% profit: Sell remaining ${Math.ceil(analysis.contracts / 2)} contract(s)
                    </div>
                </li>
                <li data-step="3">
                    <div>
                        <strong>To Exit</strong><br>
                        Action: SELL TO CLOSE, use LIMIT order to maximize proceeds
                    </div>
                </li>
                <li data-step="4">
                    <div>
                        <strong>Before Expiration</strong><br>
                        Close position at least 1-2 weeks before expiration to avoid time decay acceleration
                    </div>
                </li>
            </ul>
        </div>

        <!-- Risk Disclaimer -->
        <div class="warning-box">
            <p><strong><i class="fas fa-info-circle"></i> Important:</strong>
            This is educational analysis only. Options trading involves substantial risk.
            Past performance does not guarantee future results. Consult with a financial advisor
            before making investment decisions.</p>
        </div>
    `;

    content.innerHTML = html;
}

// Close position detail modal
function closePositionDetail() {
    document.getElementById('position-detail-modal').style.display = 'none';
}

// Export functions for inline use
window.showPage = showPage;
window.removeTicker = removeTicker;
window.updatePerformance = updatePerformance;
window.loadDoc = loadDoc;
window.resetSettings = resetSettings;
window.addTicker = addTicker;
window.removeTickerFromList = removeTickerFromList;
window.showPositionDetail = showPositionDetail;
window.closePositionDetail = closePositionDetail;
window.toggleTheme = toggleTheme;
