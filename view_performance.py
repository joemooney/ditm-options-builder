#!/usr/bin/env python3
"""
Performance Viewer for DITM Options Recommendations
View historical performance and track open positions.
"""
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from recommendation_tracker import RecommendationTracker
from ditm import get_schwab_client

load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="View DITM options recommendation performance"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update open positions with current market data"
    )
    parser.add_argument(
        "--export",
        type=str,
        metavar="FILENAME",
        help="Export performance data to CSV file"
    )
    parser.add_argument(
        "--db",
        type=str,
        default="./recommendations_history.json",
        help="Path to recommendations database (default: ./recommendations_history.json)"
    )

    args = parser.parse_args()

    # Check if database exists
    db_path = Path(args.db)
    if not db_path.exists():
        print(f"✗ Database not found: {db_path}")
        print("\nNo recommendations tracked yet. Run ditm.py first to generate recommendations.")
        return 1

    # Initialize tracker
    tracker = RecommendationTracker(db_path=args.db)

    # Get Schwab client if updating
    client = None
    if args.update:
        print("Initializing Schwab client for live data...")
        try:
            client = get_schwab_client()
        except Exception as e:
            print(f"✗ Failed to initialize Schwab client: {e}")
            print("Continuing with cached data...")

    # Generate report
    print("\nGenerating performance report...\n")
    report = tracker.generate_report(client=client, update_values=args.update)
    print(report)

    # Export if requested
    if args.export:
        tracker.export_to_csv(args.export)

    return 0


if __name__ == "__main__":
    sys.exit(main())
