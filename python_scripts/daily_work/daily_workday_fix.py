#!/usr/bin/env python3
import subprocess
import re
from datetime import datetime, timedelta
import csv

BOOT_LINE_REGEX = re.compile(r"^\s*-?\d+\s+[0-9a-f]+\s+(.+?)\s+(.+?)\s*—\s*(.+?)\s*$")


def parse_datetime(dtstr):
    """
    Convert journalctl datetime text into Python datetime
    Example: "Mon 2025-04-14 09:20:01 KST"
    """
    try:
        return datetime.strptime(dtstr, "%a %Y-%m-%d %H:%M:%S %Z")
    except ValueError:
        # Some distros omit timezone, fallback
        try:
            return datetime.strptime(dtstr, "%a %Y-%m-%d %H:%M:%S")
        except ValueError:
            return None


def get_boot_ranges():
    """Return list of (boot_time, shutdown_time_or_none)."""
    out = subprocess.check_output(
        ["journalctl", "--list-boots", "--no-pager"], text=True
    )

    boot_ranges = []

    for line in out.splitlines():
        m = BOOT_LINE_REGEX.match(line)
        if not m:
            continue

        start_str = m.group(1).strip()
        end_str = m.group(3).strip()

        start_dt = parse_datetime(start_str)
        end_dt = parse_datetime(end_str) if end_str != "n/a" else None

        if start_dt:
            boot_ranges.append((start_dt, end_dt))

    return boot_ranges


def compute_daily_minutes(boot_dt, shutdown_dt):
    """
    Converts uptime to minutes.
    Also corrects if the range spans multiple days and results exceed ~600 minutes.
    """
    if shutdown_dt is None:
        shutdown_dt = datetime.now()

    total_minutes = int((shutdown_dt - boot_dt).total_seconds() // 60)

    # If more than 600 minutes AND not same day → cap per-day but still track realism
    if total_minutes > 600:
        same_day = boot_dt.date() == shutdown_dt.date()

        if not same_day:
            # Normal workday: limit to 540–600 range
            return min(total_minutes, 600)

    return total_minutes


def main():
    ranges = get_boot_ranges()

    rows = []

    for boot_dt, shutdown_dt in ranges:
        minutes = compute_daily_minutes(boot_dt, shutdown_dt)
        date_str = boot_dt.date().isoformat()

        rows.append((date_str, minutes))

    # Write CSV
    with open("daily_runtime.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "minutes"])
        writer.writerows(rows)

    print("✓ CSV generated: daily_runtime.csv")


if __name__ == "__main__":
    main()
