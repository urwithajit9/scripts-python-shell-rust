#!/usr/bin/env python3
import subprocess
import argparse
import csv
from datetime import datetime, timedelta

MONTHS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


def parse_datetime(tokens):
    # Example tokens: ["Tue","Dec","2","09:12:54","2025"]
    _, month, day, time_, year = tokens
    return datetime(
        int(year),
        MONTHS[month],
        int(day),
        int(time_.split(":")[0]),
        int(time_.split(":")[1]),
        int(time_.split(":")[2]),
    )


def load_boot_sessions():
    """Parse last -x -F reboot output into (boot, shutdown) pairs."""
    raw = subprocess.check_output(["last", "-x", "-F", "reboot"], text=True)
    sessions = []

    for line in raw.splitlines():
        if not line.startswith("reboot"):
            continue

        parts = line.split()

        # Boot timestamp always starts at index 4
        # Example: reboot system boot VERSION Tue Dec 2 09:12:54 2025 ...
        boot = parse_datetime(parts[4:9])

        # Detect shutdown or "still running"
        if "still" in line:
            shutdown = None
        else:
            # Shutdown starts at token containing "-"
            idx = parts.index("-")
            shutdown = parse_datetime(parts[idx + 1 : idx + 6])

        sessions.append((boot, shutdown))

    return sessions


def overlap_with_day(boot, shutdown, day):
    """Calculate overlapping time for one boot interval with the target day."""
    day_start = datetime(day.year, day.month, day.day, 0, 0, 0)
    day_end = day_start + timedelta(days=1)

    start = max(boot, day_start)
    end = min(shutdown, day_end)

    if end <= start:
        return timedelta(0)

    return end - start


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    args = parser.parse_args()

    target_day = datetime.strptime(args.date, "%Y-%m-%d")

    sessions = load_boot_sessions()

    total = timedelta(0)
    rows = []

    for boot, shutdown in sessions:
        if shutdown is None:
            # running session → assume running until now
            shutdown = datetime.now()

        delta = overlap_with_day(boot, shutdown, target_day)

        if delta > timedelta(0):
            total += delta
            rows.append((boot, shutdown, delta))

    print(f"=== System Running Time Summary for {args.date} ===")
    for b, s, d in rows:
        print(f"Boot: {b} → Shutdown: {s}   overlap: {d}")

    hours = int(total.total_seconds() // 3600)
    minutes = int((total.total_seconds() % 3600) // 60)

    print(f"\nTotal running time on {args.date}: {hours} hours {minutes} minutes")

    # Export CSV
    outname = f"uptime_{args.date}.csv"
    with open(outname, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["boot", "shutdown", "overlap_hours"])
        for b, s, d in rows:
            w.writerow([b, s, str(d)])

    print(f"CSV exported: {outname}")


if __name__ == "__main__":
    main()


# # Summary for a single date (YYYY-MM-DD)
# python daily_worktime2.py --date 2025-12-03

# # Full CSV for all dates found in logs
# python daily_worktime2.py --all --out history_uptime.csv
