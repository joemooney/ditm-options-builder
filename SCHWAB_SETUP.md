# Schwab API Setup Guide

This guide walks you through setting up Charles Schwab's Trader API for the DITM Options Portfolio Builder.

## Prerequisites

- Active Charles Schwab brokerage account
- Python 3.7 or higher
- Internet connection

## Step 1: Register for Developer Access

1. Visit [Charles Schwab Developer Portal](https://developer.schwab.com/)
2. Log in with your Schwab credentials
3. Navigate to "My Apps" or "Developer Dashboard"
4. Click "Create New App" or "Register Application"

## Step 2: Configure Your Application

When creating your app, use these settings:

- **App Name**: `DITM Options Scanner` (or your preferred name)
- **Description**: `Personal options analysis tool for deep-in-the-money calls`
- **API Product**: **Accounts and Trading Production** (grants access to all APIs)
- **Order Limit**: `120` orders per minute
- **Callback URL**: `https://127.0.0.1:8182` (EXACT - no trailing slash!)

**CRITICAL**: The callback URL must be exactly `https://127.0.0.1:8182` for OAuth to work.

## Step 3: Wait for Approval

- Initial status will be "Approved - Pending"
- Approval typically takes **3-7 business days**
- You'll receive an email when status changes to "Ready For Use"
- **You cannot proceed until status is "Ready For Use"**

## Step 4: Get Your Credentials

Once approved:

1. Go to your app in the developer portal
2. Copy your **App Key** (also called API Key or Client ID)
3. Copy your **App Secret** (keep this secure!)

## Step 5: Install Dependencies

```bash
cd /home/joe/ai/ditm
source .venv/bin/activate  # Or use: .venv/bin/pip
pip install schwab-py
```

## Step 6: Create Configuration File

Create a file named `.env` in the project root:

```bash
# DO NOT COMMIT THIS FILE TO GIT!
SCHWAB_APP_KEY=your_app_key_here
SCHWAB_APP_SECRET=your_app_secret_here
SCHWAB_CALLBACK_URL=https://127.0.0.1:8182
SCHWAB_TOKEN_PATH=./schwab_tokens.json
```

Replace `your_app_key_here` and `your_app_secret_here` with your actual credentials.

## Step 7: First-Time Authentication

The first time you run the script:

1. It will open a browser window to Schwab's login page
2. Log in with your Schwab credentials
3. Authorize the application
4. You'll be redirected to `https://127.0.0.1:8182/?code=...`
5. Copy the **entire URL** from the browser address bar
6. Paste it into the terminal when prompted
7. Tokens will be saved to `schwab_tokens.json`

**After first authentication**, tokens are automatically refreshed.

## Security Best Practices

1. **Never commit credentials to git**:
   ```bash
   echo ".env" >> .gitignore
   echo "schwab_tokens.json" >> .gitignore
   ```

2. **Protect your token file**: It contains access tokens for your brokerage account

3. **Use environment variables** for production deployments

4. **Rotate secrets periodically** through the developer portal

## Troubleshooting

### "Approved - Pending" Status
- Wait for Schwab approval email (3-7 days)
- Cannot proceed until status is "Ready For Use"

### Invalid Callback URL Error
- Verify callback URL is exactly: `https://127.0.0.1:8182`
- No trailing slash
- Port must be 8182
- Must use HTTPS

### Token Expired Errors
- Schwab tokens expire quickly compared to other APIs
- The library auto-refreshes tokens
- If refresh fails, delete `schwab_tokens.json` and re-authenticate

### Browser Opens But Doesn't Redirect
- Check firewall isn't blocking localhost:8182
- Try different browser
- Ensure you're using the exact callback URL

## API Limits

- Market data requests: Respect rate limits
- Order submission: 120 orders/minute (as configured)
- Token lifetime: Shorter than typical OAuth tokens

## Documentation

- [schwab-py Documentation](https://schwab-py.readthedocs.io/)
- [Schwab Developer Portal](https://developer.schwab.com/)
- [Schwab API Reference](https://developer.schwab.com/products/trader-api--individual)

## Next Steps

Once setup is complete, run:
```bash
.venv/bin/python3 ditm.py
```

The script will authenticate and begin scanning for DITM call options!
