#!/usr/bin/env python3

import argparse
import pathlib
import sqlite3
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Show play activity entries spanning more than N days"
    )
    parser.add_argument(
        "sdcard_dir", type=pathlib.Path, help="Path to SD card root"
    )
    parser.add_argument(
        "-d",
        "--days",
        type=int,
        default=2,
        help="Minimum span in days (default: 2)",
    )
    parser.add_argument(
        "--delete", action="store_true", help="Delete matching entries"
    )
    args = parser.parse_args()

    db = (
        args.sdcard_dir
        / "Saves/CurrentProfile/play_activity/play_activity_db.sqlite"
    )
    if not db.exists():
        print(f"Database not found: {db}", file=sys.stderr)
        sys.exit(2)

    conn = sqlite3.connect(db)
    cursor = conn.execute(
        """
        SELECT r.name, pa.rowid, pa.play_time,
               datetime(pa.created_at, 'unixepoch', 'localtime') as created,
               datetime(pa.updated_at, 'unixepoch', 'localtime') as updated,
               pa.updated_at - pa.created_at as span
        FROM play_activity pa
        JOIN rom r ON r.id = pa.rom_id
        WHERE pa.updated_at - pa.created_at > ? * 86400
        ORDER BY span DESC
    """,
        (args.days,),
    )

    rows = cursor.fetchall()
    if not rows:
        print(f"No entries spanning more than {args.days} days.")
        return

    print(
        f"{'Name':<50} {'Play Time':>10} {'Span (days)':>12} {'Created':<20} {'Updated':<20}"
    )
    print("-" * 114)
    for name, rowid, play_time, created, updated, span in rows:
        days = span / 86400
        print(
            f"{name:<50} {play_time:>9}s {days:>11.1f} {created:<20} {updated:<20}"
        )

    total = sum(r[2] for r in rows)
    print("-" * 114)
    print(f"{'Total: ' + str(len(rows)) + ' entries':<50} {total:>9}s")

    if args.delete:
        rowids = [r[1] for r in rows]
        conn.executemany(
            "DELETE FROM play_activity WHERE rowid = ?", [(r,) for r in rowids]
        )
        conn.commit()
        print(f"Deleted {len(rowids)} entries.")

    conn.close()
    if not args.delete:
        sys.exit(1)


if __name__ == "__main__":
    main()
