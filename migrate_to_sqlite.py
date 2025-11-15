#!/usr/bin/env python3
"""
Migration script: JSON to SQLite
Migrates existing recommendations_history.json data to new SQLite database.
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from recommendation_tracker_db import RecommendationTrackerDB


def migrate_json_to_sqlite(json_path: str = "./recommendations_history.json",
                           db_path: str = "./recommendations.db"):
    """
    Migrate data from JSON file to SQLite database.

    Args:
        json_path: Path to existing JSON file
        db_path: Path to new SQLite database
    """
    json_file = Path(json_path)

    if not json_file.exists():
        print(f"✓ No existing JSON file found at {json_path}")
        print("  Starting fresh with SQLite database")
        return

    print(f"Migrating data from {json_path} to {db_path}...")
    print("=" * 70)

    # Load JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Initialize SQLite database
    tracker = RecommendationTrackerDB(db_path)

    # Migrate metadata
    print("\n1. Migrating metadata...")
    if 'metadata' in data:
        cursor = tracker.conn.cursor()
        cursor.execute("""
            UPDATE metadata
            SET value = ?, updated_at = ?
            WHERE key = 'last_schwab_fetch'
        """, (
            data['metadata'].get('last_schwab_fetch'),
            datetime.now().isoformat()
        ))
        tracker.conn.commit()
        print(f"   ✓ Migrated metadata")

    # Migrate scans
    print("\n2. Migrating scans...")
    scans_migrated = 0
    if 'scans' in data:
        for scan_id, scan_data in data['scans'].items():
            try:
                # Insert scan directly with original scan_id (don't regenerate it)
                cursor = tracker.conn.cursor()
                cursor.execute("""
                    INSERT INTO scans (scan_id, scan_date, preset_name, tickers, filter_params)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    scan_id,  # Use original scan_id
                    scan_data['scan_date'],
                    scan_data.get('preset_name'),
                    json.dumps(scan_data['tickers']),
                    json.dumps(scan_data['filter_params'])
                ))
                tracker.conn.commit()
                scans_migrated += 1
            except Exception as e:
                print(f"   ⚠ Warning: Failed to migrate scan {scan_id}: {e}")

    print(f"   ✓ Migrated {scans_migrated} scans")

    # Migrate recommendations
    print("\n3. Migrating recommendations...")
    recs_migrated = 0
    if 'recommendations' in data:
        for rec in data['recommendations']:
            try:
                # Add recommendation (handle missing fields from old data)
                rec_id = tracker.add_recommendation(
                    scan_id=rec['scan_id'],
                    ticker=rec['ticker'],
                    stock_price=rec.get('stock_price_at_rec', 0),
                    strike=rec['strike'],
                    expiration=rec['expiration'],
                    dte=rec.get('dte_at_rec', 0),
                    premium_bid=rec.get('premium_bid', 0),
                    premium_ask=rec.get('premium_ask', 0),
                    premium_mid=rec.get('premium_mid', 0),
                    delta=rec.get('delta_at_rec', 0.8),
                    iv=rec.get('iv_at_rec', 0),
                    intrinsic_pct=rec.get('intrinsic_pct', 0.8),  # Default for old data
                    oi=rec.get('open_interest', 0),
                    spread_pct=rec.get('spread_pct', 0),
                    cost_per_share=rec.get('cost_per_share', 0),
                    contracts=rec.get('contracts_recommended', 1),
                    total_cost=rec.get('total_cost', 0),
                    equiv_shares=rec.get('equiv_shares', 0),
                    score=rec.get('score', 0),
                    extrinsic_value=rec.get('extrinsic_value', 0),
                    extrinsic_pct=rec.get('extrinsic_pct', 0)
                )

                # Update with current values if available
                if rec.get('current_mid'):
                    tracker.update_recommendation_value(
                        rec_id=rec_id,
                        client=None,
                        current_bid=rec.get('current_bid'),
                        current_ask=rec.get('current_ask'),
                        current_mid=rec.get('current_mid'),
                        stock_current=rec.get('stock_current'),
                        delta_current=rec.get('delta_current')
                    )

                # Update status if not open
                if rec.get('status') != 'open':
                    cursor = tracker.conn.cursor()
                    cursor.execute("""
                        UPDATE recommendations
                        SET status = ?, closed_date = ?, close_reason = ?
                        WHERE id = ?
                    """, (
                        rec['status'],
                        rec.get('closed_date'),
                        rec.get('close_reason'),
                        rec_id
                    ))
                    tracker.conn.commit()

                recs_migrated += 1

            except Exception as e:
                print(f"   ⚠ Warning: Failed to migrate recommendation {rec.get('id', 'unknown')}: {e}")

    print(f"   ✓ Migrated {recs_migrated} recommendations")

    # Summary
    print("\n" + "=" * 70)
    print("MIGRATION SUMMARY")
    print("=" * 70)
    print(f"Scans migrated:            {scans_migrated}")
    print(f"Recommendations migrated:  {recs_migrated}")
    print(f"\nNew database:              {db_path}")
    print(f"Original JSON backed up:   {json_path}.backup")
    print("=" * 70)

    # Backup original JSON
    backup_path = f"{json_path}.backup"
    import shutil
    shutil.copy(json_path, backup_path)
    print(f"\n✓ Original JSON backed up to {backup_path}")

    tracker.close()
    print("✓ Migration complete!")


if __name__ == "__main__":
    json_path = sys.argv[1] if len(sys.argv) > 1 else "./recommendations_history.json"
    db_path = sys.argv[2] if len(sys.argv) > 2 else "./recommendations.db"

    migrate_json_to_sqlite(json_path, db_path)
