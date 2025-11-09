#!/usr/bin/env python3
"""
Command-line tool for managing ticker watchlist
"""
import json
import sys
from pathlib import Path
import argparse


CONFIG_FILE = Path("./web_config.json")


def load_config():
    """Load configuration from file."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "tickers": [],
        "target_capital": 50000,
        "filters": {}
    }


def save_config(config):
    """Save configuration to file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def list_tickers():
    """List all tickers in the watchlist."""
    config = load_config()
    tickers = config.get("tickers", [])

    if not tickers:
        print("Watchlist is empty.")
        return

    print(f"\nCurrent Watchlist ({len(tickers)} ticker{'s' if len(tickers) != 1 else ''}):")
    print("-" * 40)
    for i, ticker in enumerate(tickers, 1):
        print(f"  {i}. {ticker}")
    print()


def add_ticker(ticker):
    """Add a ticker to the watchlist."""
    ticker = ticker.upper().strip()

    # Validate ticker
    if not ticker.isalpha() or len(ticker) > 5:
        print(f"Error: '{ticker}' is not a valid ticker symbol.")
        print("Ticker must be 1-5 letters only.")
        return False

    config = load_config()
    tickers = config.get("tickers", [])

    if ticker in tickers:
        print(f"'{ticker}' is already in the watchlist.")
        return False

    tickers.append(ticker)
    config["tickers"] = tickers
    save_config(config)

    print(f"✓ Added '{ticker}' to watchlist")
    print(f"  Total tickers: {len(tickers)}")
    return True


def remove_ticker(ticker):
    """Remove a ticker from the watchlist."""
    ticker = ticker.upper().strip()

    config = load_config()
    tickers = config.get("tickers", [])

    if ticker not in tickers:
        print(f"'{ticker}' is not in the watchlist.")
        return False

    tickers.remove(ticker)
    config["tickers"] = tickers
    save_config(config)

    print(f"✓ Removed '{ticker}' from watchlist")
    print(f"  Total tickers: {len(tickers)}")
    return True


def clear_all():
    """Clear all tickers from the watchlist."""
    config = load_config()
    count = len(config.get("tickers", []))

    if count == 0:
        print("Watchlist is already empty.")
        return

    # Ask for confirmation
    response = input(f"Are you sure you want to remove all {count} ticker(s)? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Cancelled.")
        return

    config["tickers"] = []
    save_config(config)

    print(f"✓ Cleared all {count} ticker(s) from watchlist")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Manage DITM options ticker watchlist",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                 # List all tickers
  %(prog)s add AAPL             # Add AAPL to watchlist
  %(prog)s add AAPL MSFT GOOGL  # Add multiple tickers
  %(prog)s remove AAPL          # Remove AAPL from watchlist
  %(prog)s clear                # Clear all tickers (with confirmation)
        """
    )

    parser.add_argument(
        'action',
        choices=['list', 'add', 'remove', 'clear'],
        help='Action to perform'
    )

    parser.add_argument(
        'tickers',
        nargs='*',
        help='Ticker symbol(s) to add or remove'
    )

    args = parser.parse_args()

    # Handle actions
    if args.action == 'list':
        list_tickers()

    elif args.action == 'add':
        if not args.tickers:
            print("Error: Please specify at least one ticker to add.")
            print("Usage: manage_tickers.py add TICKER [TICKER ...]")
            sys.exit(1)

        added = 0
        for ticker in args.tickers:
            if add_ticker(ticker):
                added += 1

        if added > 0:
            print()
            list_tickers()

    elif args.action == 'remove':
        if not args.tickers:
            print("Error: Please specify at least one ticker to remove.")
            print("Usage: manage_tickers.py remove TICKER [TICKER ...]")
            sys.exit(1)

        removed = 0
        for ticker in args.tickers:
            if remove_ticker(ticker):
                removed += 1

        if removed > 0:
            print()
            list_tickers()

    elif args.action == 'clear':
        clear_all()


if __name__ == '__main__':
    main()
