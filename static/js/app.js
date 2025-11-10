// DITM Options Portfolio Builder - Frontend Application

// State
let currentPage = 'dashboard';
let config = null;
let tickers = [];

// Helper function to create tooltip icon HTML
function tooltip(text) {
    return `<span data-tooltip="${text}"><i class="fas fa-info-circle tooltip-icon"></i></span>`;
}

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
    // Active positions stats
    document.getElementById('stat-active-invested').textContent = formatCurrency(summary.active_invested);
    document.getElementById('stat-active-value').textContent = formatCurrency(summary.active_value);

    const activePnlElement = document.getElementById('stat-active-pnl');
    activePnlElement.textContent = formatCurrency(summary.active_pnl) +
        ` (${formatPercent(summary.active_pnl_pct)})`;
    activePnlElement.className = 'stat-value ' + (summary.active_pnl >= 0 ? 'positive' : 'negative');

    // Recommended positions stats
    document.getElementById('stat-recommended-invested').textContent = formatCurrency(summary.recommended_invested);
    document.getElementById('stat-recommended-value').textContent = formatCurrency(summary.recommended_value);

    const recommendedPnlElement = document.getElementById('stat-recommended-pnl');
    recommendedPnlElement.textContent = formatCurrency(summary.recommended_pnl) +
        ` (${formatPercent(summary.recommended_pnl_pct)})`;
    recommendedPnlElement.className = 'stat-value ' + (summary.recommended_pnl >= 0 ? 'positive' : 'negative');
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
        html += '<th>Ticker</th>';
        html += `<th>Strike ${tooltip("Strike price of the call option. You have the right to buy stock at this price.")}</th>`;
        html += `<th>Expiration ${tooltip("Option expiration date. After this date, the option becomes worthless.")}</th>`;
        html += `<th>DTE ${tooltip("Days to Expiration. More days = less time decay risk. See User Guide for details.")}</th>`;
        html += `<th>Qty ${tooltip("Number of contracts held. Each contract represents 100 shares.")}</th>`;
        html += `<th>Contract Cost ${tooltip("Cost per contract (100 shares) at entry. Your average purchase price.")}</th>`;
        html += `<th>Extrinsic $ ${tooltip("Premium above intrinsic value per contract. This is the 'time value' that must be recouped to break-even. Lower is better. See User Guide for details.")}</th>`;
        html += `<th>Extrinsic % ${tooltip("Extrinsic value as % of contract cost. This is the percentage that was 'lost' immediately at purchase. Lower % = more conservative. See User Guide for details.")}</th>`;
        html += `<th>Total Cost ${tooltip("Total amount invested in this position (contract cost × quantity × 100).")}</th>`;
        html += `<th>Value ${tooltip("Current market value of the position. Updated from Schwab account.")}</th>`;
        html += `<th>P&L ${tooltip("Profit/Loss: Current Value - Total Cost. Shows both dollar amount and percentage. See User Guide for details.")}</th>`;
        html += '</tr></thead><tbody>';

        activePositions.forEach(pos => {
            const pnlClass = pos['P&L'] >= 0 ? 'positive' : 'negative';
            const extrinsicClass = 'negative'; // Extrinsic is always a "cost"
            html += `<tr class="clickable-row" onclick="showPositionDetail('${pos.Ticker}', '${pos.Strike}', '${pos.Expiration}')" style="cursor: pointer;">`;
            html += `<td><strong>${pos.Ticker}</strong></td>`;
            html += `<td>${pos.Strike}</td>`;
            html += `<td>${pos.Expiration}</td>`;
            html += `<td>${pos.DTE || 0}</td>`;
            html += `<td>${pos.Quantity || 0}</td>`;
            html += `<td>${formatCurrency(pos.Contract_Cost || 0)}</td>`;
            html += `<td class="${extrinsicClass}">${formatCurrency((pos.Extrinsic_Value || 0) * 100)}</td>`;
            html += `<td class="${extrinsicClass}">${formatPercent(pos.Extrinsic_Pct || 0)}</td>`;
            html += `<td>${formatCurrency(pos.Total_Cost || 0)}</td>`;
            html += `<td>${formatCurrency(pos.Current_Value || 0)}</td>`;
            html += `<td class="${pnlClass}">${formatCurrency(pos['P&L'] || 0)} (${formatPercent(pos['P&L_%'] || 0)})</td>`;
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
        // Check if data is stale (>24 hours old during market hours)
        const shouldShowRefresh = checkIfDataStale(recommendedPositions);

        let html = '';

        // Add refresh button if data is stale
        if (shouldShowRefresh) {
            html += '<div class="warning-box" style="margin-bottom: 1rem;">';
            html += '<p><strong><i class="fas fa-exclamation-triangle"></i> Stale Price Data</strong></p>';
            html += '<p>Stock prices have not been updated since the last market close. ';
            html += '<button class="btn btn-primary" onclick="refreshRecommendedPrices()" style="margin-left: 0.5rem;">';
            html += '<i class="fas fa-sync"></i> Refresh Prices</button></p>';
            html += '</div>';
        }

        html += '<table class="table"><thead><tr>';
        html += '<th>Ticker</th>';
        html += `<th>Stock Price ${tooltip("Current stock price. Stale data shows warning icon.")}</th>`;
        html += `<th>Strike ${tooltip("Strike price of the call option. You have the right to buy stock at this price.")}</th>`;
        html += `<th>Expiration ${tooltip("Option expiration date. After this date, the option becomes worthless.")}</th>`;
        html += `<th>DTE ${tooltip("Days to Expiration. More days = less time decay risk. See User Guide for details.")}</th>`;
        html += `<th>Cost/Share ${tooltip("Effective cost per share of stock exposure. Lower than stock price = leverage advantage. See User Guide for details.")}</th>`;
        html += `<th>Delta ${tooltip("How much the option price moves per $1 stock move. 85% means option gains ~85¢ when stock gains $1. See User Guide for details.")}</th>`;
        html += `<th>IV ${tooltip("Implied Volatility at entry. Higher IV = more expensive options, more risk. DITM strategy prefers <30%. See User Guide for details.")}</th>`;
        html += `<th>Score ${tooltip("Composite score ranking options. Lower score = more conservative. See User Guide for details.")}</th>`;
        html += '<th></th>';
        html += '</tr></thead><tbody>';

        recommendedPositions.slice(0, 10).forEach(pos => {
            // Determine which stock price to show (current if available, otherwise entry)
            const stockPrice = pos.Stock_Current || pos.Stock_Entry || 0;
            const isStale = !pos.Stock_Current || pos.Stock_Current === 0;

            html += `<tr class="clickable-row">`;
            html += `<td onclick="showPositionDetail('${pos.Ticker}', '${pos.Strike}', '${pos.Expiration}')" style="cursor: pointer;"><strong>${pos.Ticker}</strong></td>`;
            html += `<td onclick="showPositionDetail('${pos.Ticker}', '${pos.Strike}', '${pos.Expiration}')" style="cursor: pointer;">`;
            html += `${formatCurrency(stockPrice)}`;
            if (isStale) {
                html += ` <i class="fas fa-exclamation-circle" style="color: var(--warning-color); font-size: 0.8rem;" title="Stale price data"></i>`;
            }
            html += `</td>`;
            html += `<td onclick="showPositionDetail('${pos.Ticker}', '${pos.Strike}', '${pos.Expiration}')" style="cursor: pointer;">${pos.Strike}</td>`;
            html += `<td onclick="showPositionDetail('${pos.Ticker}', '${pos.Strike}', '${pos.Expiration}')" style="cursor: pointer;">${pos.Expiration}</td>`;
            html += `<td onclick="showPositionDetail('${pos.Ticker}', '${pos.Strike}', '${pos.Expiration}')" style="cursor: pointer;">${pos.DTE || 0}</td>`;
            html += `<td onclick="showPositionDetail('${pos.Ticker}', '${pos.Strike}', '${pos.Expiration}')" style="cursor: pointer;">${formatCurrency(pos.Cost_Share || pos['Cost/Share'] || 0)}</td>`;
            html += `<td onclick="showPositionDetail('${pos.Ticker}', '${pos.Strike}', '${pos.Expiration}')" style="cursor: pointer;">${formatPercent(pos.Delta_Entry * 100)}</td>`;
            html += `<td onclick="showPositionDetail('${pos.Ticker}', '${pos.Strike}', '${pos.Expiration}')" style="cursor: pointer;">${formatPercent((pos.IV_Entry || 0) * 100)}</td>`;
            html += `<td onclick="showPositionDetail('${pos.Ticker}', '${pos.Strike}', '${pos.Expiration}')" style="cursor: pointer;">${(pos.Score || 0).toFixed(3)}</td>`;
            html += `<td style="text-align: center;">`;
            html += `<button class="btn-icon" onclick="event.stopPropagation(); removeRecommendation('${pos.Ticker}', '${pos.Strike}', '${pos.Expiration}')" title="Remove recommendation">`;
            html += `<i class="fas fa-trash" style="color: var(--danger-color);"></i>`;
            html += `</button>`;
            html += `</td>`;
            html += '</tr>';
        });

        html += '</tbody></table>';
        recommendedContainer.innerHTML = html;
    }
}

// Get the last market close time
function getLastMarketClose() {
    const now = new Date();
    const nowET = new Date(now.toLocaleString('en-US', { timeZone: 'America/New_York' }));

    let lastClose = new Date(nowET);
    const dayOfWeek = nowET.getDay();
    const hour = nowET.getHours();
    const minute = nowET.getMinutes();

    // Market closes at 4:00 PM ET
    lastClose.setHours(16, 0, 0, 0);

    // If it's before 4 PM today, use yesterday's close
    if (hour < 16 || (hour === 16 && minute === 0)) {
        lastClose.setDate(lastClose.getDate() - 1);
    }

    // If last close was on weekend, roll back to Friday
    while (lastClose.getDay() === 0 || lastClose.getDay() === 6) {
        lastClose.setDate(lastClose.getDate() - 1);
    }

    return lastClose;
}

// Check if recommendation data is stale (not updated since last market close)
function checkIfDataStale(positions) {
    if (!positions || positions.length === 0) return false;

    // Check if any position has stale data
    // A position is stale if Stock_Current is 0/null (means it hasn't been updated)
    const hasStaleData = positions.some(pos => !pos.Stock_Current || pos.Stock_Current === 0);

    return hasStaleData;
}

// Refresh prices for recommended positions
async function refreshRecommendedPrices() {
    // Disable button and show loading state
    const button = event.target.closest('button');
    if (button) {
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
    }

    showToast('Fetching latest prices from Schwab...', 'info');

    try {
        const response = await fetch('/api/performance?update=true');
        const data = await response.json();

        if (data.success) {
            showToast('Prices refreshed successfully', 'success');
            // Reload dashboard to show updated prices
            await loadDashboard();
        } else {
            showToast('Failed to refresh prices: ' + (data.error || 'Unknown error'), 'error');
            // Re-enable button on error
            if (button) {
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-sync"></i> Refresh Prices';
            }
        }
    } catch (error) {
        console.error('Error refreshing prices:', error);
        showToast('Error refreshing prices: ' + error.message, 'error');
        // Re-enable button on error
        if (button) {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-sync"></i> Refresh Prices';
        }
    }
}

// Remove recommendation
async function removeRecommendation(ticker, strike, expiration) {
    if (!confirm(`Remove ${ticker} $${strike} ${expiration} recommendation?`)) {
        return;
    }

    try {
        const response = await fetch('/api/recommendation/remove', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ticker: ticker,
                strike: parseFloat(strike),
                expiration: expiration
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`Removed ${ticker} $${strike} recommendation`, 'success');
            // Reload dashboard to refresh the list
            loadDashboard();
        } else {
            showToast(data.error || 'Failed to remove recommendation', 'error');
        }
    } catch (error) {
        console.error('Error removing recommendation:', error);
        showToast('Error removing recommendation: ' + error.message, 'error');
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
    html += `<div class="stat-card"><div class="stat-icon orange"><i class="fas fa-exclamation-triangle"></i></div>
             <div class="stat-content"><div class="stat-label">Total Extrinsic</div>
             <div class="stat-value">${formatCurrency(data.summary.total_extrinsic)}</div></div></div>`;
    html += `<div class="stat-card"><div class="stat-icon purple"><i class="fas fa-chart-line"></i></div>
             <div class="stat-content"><div class="stat-label">Equiv Shares</div>
             <div class="stat-value">${data.summary.total_equiv_shares.toFixed(0)}</div></div></div>`;
    html += '</div>';

    if (data.info) {
        html += `<div class="info-box mb-3"><i class="fas fa-info-circle"></i> ${data.info}</div>`;
    }

    if (data.portfolio && data.portfolio.length > 0) {
        html += '<table class="table"><thead><tr>';
        html += '<th>Ticker</th>';
        html += `<th>Strike ${tooltip("Strike price of the call option. You have the right to buy stock at this price.")}</th>`;
        html += `<th>Expiration ${tooltip("Option expiration date. After this date, the option becomes worthless.")}</th>`;
        html += `<th>DTE ${tooltip("Days to Expiration. More days = less time decay risk. See User Guide for details.")}</th>`;
        html += `<th>Delta ${tooltip("How much the option price moves per $1 stock move. 0.85 delta means option gains ~85¢ when stock gains $1. Higher = more stock-like. See User Guide for details.")}</th>`;
        html += `<th>Contract Cost ${tooltip("Cost to purchase one contract (100 shares). Uses Ask price (realistic buy price).")}</th>`;
        html += `<th>Extrinsic $ ${tooltip("Premium above intrinsic value (time value). This amount would be 'lost' if bought and sold immediately. Lower is better. See User Guide for details.")}</th>`;
        html += `<th>Extrinsic % ${tooltip("Extrinsic value as % of option price. Lower % = more conservative, less exposed to time decay. DITM typically <15%. See User Guide for details.")}</th>`;
        html += `<th>Score ${tooltip("Composite score ranking options. Lower score = more conservative. Considers delta, intrinsic %, IV, and spread. See User Guide for details.")}</th>`;
        html += '</tr></thead><tbody>';

        data.portfolio.forEach(pos => {
            html += '<tr>';
            html += `<td><strong>${pos.Ticker}</strong></td>`;
            html += `<td>$${pos.Strike}</td>`;
            html += `<td>${pos.Expiration}</td>`;
            html += `<td>${pos.DTE}</td>`;
            html += `<td>${pos.Delta.toFixed(3)}</td>`;
            html += `<td>${formatCurrency(pos['Contract Cost'])}</td>`;
            html += `<td class="negative">${formatCurrency(pos['Extrinsic Value'])}</td>`;
            html += `<td class="negative">${pos['Extrinsic %'].toFixed(2)}%</td>`;
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
    if (!config) return;

    // Default filter values (from ditm.py)
    const defaults = {
        MIN_DELTA: 0.80,
        MAX_DELTA: 0.95,
        MIN_INTRINSIC_PCT: 0.85,
        MIN_DTE: 90,
        MAX_IV: 0.30,
        MAX_SPREAD_PCT: 0.02,
        MIN_OI: 500
    };

    // Use config values if present, otherwise use defaults
    const filters = config.filters || {};
    document.getElementById('setting-min-delta').value = filters.MIN_DELTA ?? defaults.MIN_DELTA;
    document.getElementById('setting-max-delta').value = filters.MAX_DELTA ?? defaults.MAX_DELTA;
    document.getElementById('setting-min-intrinsic').value = filters.MIN_INTRINSIC_PCT ?? defaults.MIN_INTRINSIC_PCT;
    document.getElementById('setting-min-dte').value = filters.MIN_DTE ?? defaults.MIN_DTE;
    document.getElementById('setting-max-iv').value = filters.MAX_IV ?? defaults.MAX_IV;
    document.getElementById('setting-max-spread').value = filters.MAX_SPREAD_PCT ?? defaults.MAX_SPREAD_PCT;
    document.getElementById('setting-min-oi').value = filters.MIN_OI ?? defaults.MIN_OI;

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
            displayTickerList(data.ticker_info || data.tickers);
        }
    } catch (error) {
        console.error('Error loading tickers:', error);
        showToast('Error loading ticker list', 'error');
    }
}

// Display ticker list
function displayTickerList(tickerData) {
    const container = document.getElementById('ticker-list');
    const countBadge = document.getElementById('ticker-count');

    // Handle both formats: array of strings or array of objects with ticker info
    const tickerList = Array.isArray(tickerData) && tickerData.length > 0 && typeof tickerData[0] === 'object'
        ? tickerData
        : tickerData.map(t => ({ symbol: t, has_dividend: false, div_yield: 0, div_amount: 0 }));

    countBadge.textContent = `${tickerList.length} ticker${tickerList.length !== 1 ? 's' : ''}`;

    if (tickerList.length === 0) {
        container.innerHTML = '<p class="text-muted">No tickers in watchlist. Add some above!</p>';
        return;
    }

    let html = '<div class="ticker-grid">';
    tickerList.forEach(info => {
        const ticker = info.symbol;
        const hasDividend = info.has_dividend;
        const divYield = info.div_yield || 0;
        const divAmount = info.div_amount || 0;

        html += `
            <div class="ticker-item">
                <span class="ticker-symbol">
                    ${ticker}
                    ${hasDividend ? `<i class="fas fa-exclamation-triangle"
                        style="color: var(--warning-color); font-size: 0.8rem; margin-left: 0.25rem;"
                        title="Pays dividends: ${divYield.toFixed(2)}% yield, $${divAmount.toFixed(2)}/share"></i>` : ''}
                </span>
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
async function addTicker(force = false) {
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
            body: JSON.stringify({ ticker: ticker, force: force })
        });

        const data = await response.json();

        if (data.success) {
            input.value = '';
            await loadTickerList();  // Reload to get dividend info
            showToast(`Added ${ticker} to watchlist`, 'success');
        } else if (data.warning === 'dividend_stock') {
            // Show dividend warning and ask for confirmation
            const confirmed = confirm(
                `⚠️ DIVIDEND WARNING\n\n` +
                `${ticker} pays dividends:\n` +
                `• Yield: ${data.div_yield.toFixed(2)}%\n` +
                `• Amount: $${data.div_amount.toFixed(2)}/share annually\n\n` +
                `DITM call options do NOT receive dividends, which will reduce your returns.\n\n` +
                `Add ${ticker} to watchlist anyway?`
            );

            if (confirmed) {
                // User confirmed, add with force=true
                await addTicker(true);
            }
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

    // Calculate current value from analysis if position shows 0
    let currentValue = position.Current_Value || 0;
    if (currentValue === 0 && analysis.current_option_price > 0) {
        currentValue = analysis.current_option_price * analysis.contracts * 100;
    }

    // Calculate P&L based on current value
    const totalCost = position.Total_Cost || 0;
    let pnl = position['P&L'] || 0;
    let pnlPct = position['P&L_%'] || 0;

    if (currentValue > 0 && pnl === 0) {
        pnl = currentValue - totalCost;
        pnlPct = totalCost > 0 ? (pnl / totalCost) * 100 : 0;
    }

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
                <div class="detail-item ${isProfitable ? 'positive' : 'negative'}">
                    <div class="detail-label">CAGR</div>
                    <div class="detail-value">${formatPercent(analysis.cagr)}</div>
                    <small>Annualized: ${formatPercent(analysis.annualized_return)}</small>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Total Invested</div>
                    <div class="detail-value">${formatCurrency(position.Total_Cost)}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Current Value</div>
                    <div class="detail-value">${formatCurrency(currentValue)}</div>
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
                    <div class="detail-value">${formatCurrency(analysis.strike_price)}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Entry Bid/Ask/Mid</div>
                    <div class="detail-value">
                        ${formatCurrency(analysis.entry_bid)} /
                        ${formatCurrency(analysis.entry_ask)} /
                        ${formatCurrency(analysis.entry_mid)}
                    </div>
                    <small>Spread: ${formatCurrency(analysis.entry_spread)} (${analysis.entry_spread_pct.toFixed(2)}%)</small>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Entry Price Used</div>
                    <div class="detail-value">${formatCurrency(analysis.entry_price_used)}</div>
                    <small>${analysis.use_ask_for_entry ? 'Ask (realistic)' : 'Mid (optimistic)'} - for breakeven calc</small>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Current Option Price</div>
                    <div class="detail-value">${formatCurrency(analysis.current_option_price)}</div>
                    <small>Current value per contract</small>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Contracts</div>
                    <div class="detail-value">${analysis.contracts}</div>
                    <small>${analysis.contracts * 100} shares equivalent</small>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Intrinsic Value</div>
                    <div class="detail-value">${formatCurrency(analysis.intrinsic_value)}</div>
                    <small>Stock - Strike</small>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Time Value</div>
                    <div class="detail-value">${formatCurrency(analysis.time_value)}</div>
                    <small>Option - Intrinsic</small>
                </div>
            </div>
        </div>

        <!-- Leverage Analysis -->
        <div class="detail-section">
            <h4><i class="fas fa-chart-line"></i> Leverage & Capital Efficiency</h4>

            <div class="info-box" style="margin-bottom: 1rem;">
                <p><strong><i class="fas fa-lightbulb"></i> Leverage Advantage:</strong>
                You're controlling ${formatCurrency(analysis.cost_to_buy_shares)} worth of stock exposure
                for only ${formatCurrency(position.Total_Cost)} invested
                (${analysis.leverage_ratio.toFixed(2)}x leverage)</p>
            </div>

            <div class="detail-grid">
                <div class="detail-item">
                    <div class="detail-label">Delta</div>
                    <div class="detail-value">${analysis.delta.toFixed(3)}</div>
                    <small>Stock-like exposure per contract</small>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Delta-Adjusted Shares</div>
                    <div class="detail-value">${Math.round(analysis.delta_adjusted_shares)} shares</div>
                    <small>${analysis.contracts} contracts × 100 × ${analysis.delta.toFixed(2)} delta</small>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Cost to Buy Shares</div>
                    <div class="detail-value">${formatCurrency(analysis.cost_to_buy_shares)}</div>
                    <small>${Math.round(analysis.delta_adjusted_shares)} shares × ${formatCurrency(analysis.current_stock_price)}</small>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Leverage Ratio</div>
                    <div class="detail-value">${analysis.leverage_ratio.toFixed(2)}x</div>
                    <small>Stock value / Capital invested</small>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Capital Saved</div>
                    <div class="detail-value" style="color: var(--success-color);">
                        ${formatCurrency(analysis.capital_saved)}
                    </div>
                    <small>vs. buying ${Math.round(analysis.delta_adjusted_shares)} shares</small>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Capital Efficiency</div>
                    <div class="detail-value" style="color: var(--success-color);">
                        ${analysis.capital_efficiency_pct.toFixed(1)}%
                    </div>
                    <small>Savings as % of stock cost</small>
                </div>
            </div>

            <div style="margin-top: 1rem; padding: 1rem; background: var(--bg-secondary); border-radius: 8px;">
                <h5 style="margin: 0 0 0.5rem 0;">What This Means:</h5>
                <ul style="margin: 0.5rem 0 0 1.5rem; line-height: 1.6;">
                    <li>You invested <strong>${formatCurrency(position.Total_Cost)}</strong> in options</li>
                    <li>This controls <strong>${Math.round(analysis.delta_adjusted_shares)} shares</strong> worth of price movement</li>
                    <li>Buying those shares outright would cost <strong>${formatCurrency(analysis.cost_to_buy_shares)}</strong></li>
                    <li>You saved <strong>${formatCurrency(analysis.capital_saved)}</strong> (${analysis.capital_efficiency_pct.toFixed(1)}%) by using options</li>
                    <li>Your leverage is <strong>${analysis.leverage_ratio.toFixed(2)}x</strong> - for every $1 invested, you control $${analysis.leverage_ratio.toFixed(2)} of stock</li>
                </ul>
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

        <!-- Exercise Information -->
        <div class="detail-section">
            <h4><i class="fas fa-hand-holding-usd"></i> Exercise vs. Sell Analysis</h4>

            <div class="${analysis.better_to_sell_option ? 'info-box' : 'warning-box'}">
                <p><strong><i class="fas ${analysis.better_to_sell_option ? 'fa-lightbulb' : 'fa-exclamation-triangle'}"></i>
                Recommendation:</strong> ${analysis.better_to_sell_option ? 'Sell the option (better profit)' : 'Exercise may be preferable (consult advisor)'}</p>
            </div>

            <div class="detail-grid">
                <div class="detail-item">
                    <div class="detail-label">Exercise Cost</div>
                    <div class="detail-value">${formatCurrency(analysis.exercise_cost)}</div>
                    <small>${analysis.total_shares_if_exercised} shares × ${formatCurrency(analysis.strike_price)}</small>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Total If Exercised</div>
                    <div class="detail-value">${formatCurrency(analysis.total_investment_if_exercised)}</div>
                    <small>Premium paid + Exercise cost</small>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Stock Value If Exercised</div>
                    <div class="detail-value">${formatCurrency(analysis.current_stock_value_if_exercised)}</div>
                    <small>${analysis.total_shares_if_exercised} shares × ${formatCurrency(analysis.current_stock_price)}</small>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Shares Received</div>
                    <div class="detail-value">${analysis.total_shares_if_exercised} shares</div>
                    <small>${analysis.contracts} contracts × 100</small>
                </div>
            </div>

            <div style="margin-top: 1rem; padding: 1rem; background: var(--bg-secondary); border-radius: 8px;">
                <h5 style="margin: 0 0 0.5rem 0;">Comparison:</h5>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div>
                        <strong>Option 1: Sell the Option</strong><br>
                        <span style="color: ${analysis.sell_option_profit >= 0 ? 'var(--success-color)' : 'var(--danger-color)'};">
                            Profit: ${formatCurrency(analysis.sell_option_profit)}
                        </span><br>
                        <small>No additional capital needed</small>
                    </div>
                    <div>
                        <strong>Option 2: Exercise & Sell Shares</strong><br>
                        <span style="color: ${analysis.exercise_and_sell_profit >= 0 ? 'var(--success-color)' : 'var(--danger-color)'};">
                            Profit: ${formatCurrency(analysis.exercise_and_sell_profit)}
                        </span><br>
                        <small>Requires ${formatCurrency(analysis.exercise_cost)} cash</small>
                    </div>
                </div>
            </div>

            ${(() => {
                const dte = analysis.days_to_expiration;
                let boxClass = 'info-box';
                let iconClass = 'fa-info-circle';
                let titleText = 'Auto-Exercise Information';
                let urgencyText = '';

                if (dte <= 7) {
                    boxClass = 'danger-box';
                    iconClass = 'fa-exclamation-triangle';
                    titleText = 'Auto-Exercise Warning';
                    urgencyText = '<strong style="color: #dc3545;">⚠️ URGENT - EXPIRING IN ' + dte + ' DAYS!</strong><br>';
                } else if (dte <= 14) {
                    boxClass = 'danger-box';
                    iconClass = 'fa-exclamation-triangle';
                    titleText = 'Auto-Exercise Warning';
                    urgencyText = '<strong style="color: #dc3545;">⚠️ WARNING - EXPIRING IN ' + dte + ' DAYS!</strong><br>';
                } else if (dte <= 30) {
                    boxClass = 'warning-box';
                    iconClass = 'fa-exclamation-triangle';
                    titleText = 'Auto-Exercise Notice';
                    urgencyText = '<strong style="color: #ff9800;">⏰ NOTICE - EXPIRING IN ' + dte + ' DAYS</strong><br>';
                }

                return `
            <div class="${boxClass}" style="margin-top: 1rem;">
                <p><strong><i class="fas ${iconClass}"></i> ${titleText} (${dte} DTE):</strong></p>
                ${urgencyText ? '<p style="margin: 0.5rem 0;">' + urgencyText + '</p>' : ''}
                <ul style="margin: 0.5rem 0 0 1.5rem;">
                    <li>If you don't sell or exercise before expiration, and the option is in-the-money, it will be <strong>automatically exercised</strong></li>
                    <li>You will need <strong>${formatCurrency(analysis.exercise_cost)}</strong> in your account to cover the exercise</li>
                    <li>If you lack funds, your broker may sell the option or reject the exercise</li>
                    <li><strong>Recommendation:</strong> Always sell DITM options before expiration rather than exercising</li>
                    ${dte <= 30 ? '<li style="color: ' + (dte <= 14 ? '#dc3545' : '#ff9800') + '; font-weight: bold;">⚠️ Consider closing this position soon to avoid expiration complications!</li>' : ''}
                </ul>
            </div>
                `;
            })()}
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
