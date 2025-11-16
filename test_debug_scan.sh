#!/bin/bash
# Test script to run a scan with DEBUG_SCAN enabled

export DEBUG_SCAN=true

# Use the existing web_app to trigger a scan, or run ditm.py directly
echo "Running scan with DEBUG_SCAN=true..."
echo "This will show detailed filter statistics for each ticker"
echo ""

# Run a quick test with the ditm.py directly (if possible)
# or use the web app API
.venv/bin/python -c "
import os
os.environ['DEBUG_SCAN'] = 'true'
from ditm import get_schwab_client, build_ditm_portfolio

# Use a small ticker list for testing
tickers = ['AAPL']

client = get_schwab_client()
portfolio = build_ditm_portfolio(client, tickers)
"
