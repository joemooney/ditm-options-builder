// DITM Options Portfolio Builder - Frontend Application

// State
let currentPage = 'dashboard';
let config = null;
let tickers = [];

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
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
            updateOpenPositions(data.positions);
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

// Update open positions table
function updateOpenPositions(positions) {
    const container = document.getElementById('open-positions-table');

    if (!positions || positions.length === 0) {
        container.innerHTML = '<p class="text-muted">No open positions</p>';
        return;
    }

    const openPositions = positions.filter(p => p.Status === 'open');

    if (openPositions.length === 0) {
        container.innerHTML = '<p class="text-muted">No open positions</p>';
        return;
    }

    let html = '<table class="table"><thead><tr>';
    html += '<th>Ticker</th><th>Strike</th><th>Expiration</th>';
    html += '<th>Days Held</th><th>Cost</th><th>Value</th><th>P&L</th>';
    html += '</tr></thead><tbody>';

    openPositions.slice(0, 10).forEach(pos => {
        const pnlClass = pos['P&L'] >= 0 ? 'positive' : 'negative';
        html += '<tr>';
        html += `<td><strong>${pos.Ticker}</strong></td>`;
        html += `<td>${pos.Strike}</td>`;
        html += `<td>${pos.Expiration}</td>`;
        html += `<td>${pos.Days_Held}</td>`;
        html += `<td>${formatCurrency(pos.Total_Cost)}</td>`;
        html += `<td>${formatCurrency(pos.Current_Value)}</td>`;
        html += `<td class="${pnlClass}">${formatCurrency(pos['P&L'])} (${formatPercent(pos['P&L_%'])})</td>`;
        html += '</tr>';
    });

    html += '</tbody></table>';
    container.innerHTML = html;
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
            html += '<tr>';
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

// Export functions for inline use
window.showPage = showPage;
window.removeTicker = removeTicker;
window.updatePerformance = updatePerformance;
window.loadDoc = loadDoc;
window.resetSettings = resetSettings;
window.addTicker = addTicker;
window.removeTickerFromList = removeTickerFromList;
