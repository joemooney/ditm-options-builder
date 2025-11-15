#!/usr/bin/env python3
"""
Schwab API Re-Authentication Script
Deletes expired tokens and initiates OAuth flow.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import schwab

# Load environment variables
load_dotenv()

APP_KEY = os.getenv("SCHWAB_APP_KEY")
APP_SECRET = os.getenv("SCHWAB_APP_SECRET")
CALLBACK_URL = os.getenv("SCHWAB_CALLBACK_URL", "https://127.0.0.1:8182")
TOKEN_PATH = Path(os.getenv("SCHWAB_TOKEN_PATH", "./schwab_tokens.json"))

def main():
    """Re-authenticate with Schwab API."""
    print("=" * 70)
    print("SCHWAB API RE-AUTHENTICATION")
    print("=" * 70)

    # Check credentials
    if not APP_KEY or not APP_SECRET:
        print("\n✗ Error: Missing Schwab API credentials!")
        print("Please set SCHWAB_APP_KEY and SCHWAB_APP_SECRET in .env file.")
        print("See SCHWAB_SETUP.md for setup instructions.")
        return 1

    # Remove old token file
    if TOKEN_PATH.exists():
        print(f"\n✓ Removing expired tokens from {TOKEN_PATH}...")
        TOKEN_PATH.unlink()
    else:
        print(f"\n• No existing token file found at {TOKEN_PATH}")

    # Start OAuth flow
    print("\n" + "=" * 70)
    print("AUTHENTICATION REQUIRED")
    print("=" * 70)
    print("A browser window will open. Please:")
    print("1. Log in to your Schwab account")
    print("2. Authorize the application")
    print("3. Copy the ENTIRE redirect URL from your browser")
    print("   Example: https://127.0.0.1:8182/?code=XXXXXXXXX&session=...")
    print("4. Paste it here when prompted")
    print("=" * 70 + "\n")

    try:
        from schwab import auth

        client = auth.client_from_manual_flow(
            APP_KEY,
            APP_SECRET,
            CALLBACK_URL,
            str(TOKEN_PATH)
        )

        print("\n" + "=" * 70)
        print("✓ AUTHENTICATION SUCCESSFUL!")
        print("=" * 70)
        print(f"✓ Tokens saved to {TOKEN_PATH}")
        print("✓ You can now run scans from the web interface")
        print("=" * 70 + "\n")

        # Test the connection
        print("Testing connection with a quick quote fetch...")
        try:
            test_resp = client.get_quote("AAPL")
            if test_resp.status_code == 200:
                print("✓ Connection test successful!")
                print("  Your Schwab API integration is working correctly.\n")
            else:
                print(f"⚠ Warning: Quote fetch returned status {test_resp.status_code}")
        except Exception as e:
            print(f"⚠ Warning: Connection test failed: {e}")
            print("  But tokens were saved. Try running a scan from the web interface.")

        return 0

    except KeyboardInterrupt:
        print("\n\n✗ Authentication cancelled by user.")
        return 1
    except Exception as e:
        print(f"\n✗ Authentication failed: {e}")
        print("\nTroubleshooting:")
        print("- Ensure your app status is 'Ready For Use' in Schwab Developer Portal")
        print("- Verify APP_KEY and APP_SECRET in .env file")
        print(f"- Check callback URL is: {CALLBACK_URL}")
        print("- Make sure you copied the ENTIRE redirect URL including ?code=...")
        print("- See SCHWAB_SETUP.md for detailed setup instructions")
        return 1

if __name__ == "__main__":
    exit(main())
