#!/usr/bin/env python3
import subprocess
import re
from datetime import datetime, timedelta
import sys
import csv

MONTHS = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}


def parse_last_output():
    """Parse last -x -F output reliably using token positions."""
    raw = subprocess.check_output(["last", "-x", "-F"], text=True)

    events = []

    for line in raw.splitlines():
        parts = line.split()

        if len(parts) < 9:
            continue

        etype = parts[0]  # reboot / shutdown
        if etype not in ("reboot", "shutdown"):
            continue

        # ---- Parse start timestamp ----
        smonth = parts[5]
        sday = int(parts[6])
        stime = parts[7]
        syear = int(parts[8])

        start_dt = datetime(
            year=syear,
            month=MONTHS[smonth],
            day=sday,
            hour=int(stime[0:2]),
            minute=int(stime[3:5]),
            second=int(stime[6:8]),
        )

        # ---- Parse optional end timestamp ----
        end_dt = None
        if "-" in parts:
            dash_index = parts.index("-")

            # example: shutdown ... Wed Dec 3 18:28:09 2025 - Thu Dec 4 09:23:10 2025
            if len(parts) >= dash_index + 6:
                emonth = parts[dash_index + 2]
                eday = int(parts[dash_index + 3])
                etime = parts[dash_index + 4]
                eyear = int(parts[dash_index + 5])

                end_dt = datetime(
                    year=eyear,
                    month=MONTHS[emonth],
                    day=eday,
                    hour=int(etime[0:2]),
                    minute=int(etime[3:5]),
                    second=int(etime[6:8]),
                )

        events.append((etype, start_dt, end_dt))

    return events


def calculate_daily_uptime(events, target_date):
    sessions = []
    total = timedelta()

    boots = [(t, bstart, bend) for (t, bstart, bend) in events if t == "boot"]

    for _, boot, boot_end in boots:
        # Find next shutdown *after* boot
        matching_shutdown = next(
            (
                send
                for (t, sstart, send) in events
                if t == "shutdown" and sstart >= boot
            ),
            None,
        )

        if matching_shutdown:
            end_time = matching_shutdown
        else:
            end_time = boot_end if boot_end else datetime.now()

        sessions.append((boot, end_time))
        total += end_time - boot

    return total, sessions


def export_csv(sessions, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Boot Time", "Shutdown Time", "Duration (minutes)"])
        for boot, shutdown, duration in sessions:
            writer.writerow([
                boot.strftime("%Y-%m-%d %H:%M:%S"),
                shutdown.strftime("%Y-%m-%d %H:%M:%S"),
                int(duration.total_seconds() / 60)
            ])


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 daily_worktime.py YYYY-MM-DD")
        sys.exit(1)

    target_str = sys.argv[1]
    target_date = datetime.strptime(target_str, "%Y-%m-%d").date()

    events = parse_last_output()
    total, sessions = calculate_daily_uptime(events, target_date)

    print(f"=== System Running Time Summary for {target_str} ===")

    if not sessions:
        print("No boots on this date.")
        sys.exit(0)

    for boot, shutdown, duration in sessions:
        print(f"Boot: {boot}  →  Shutdown: {shutdown}  =  {duration}")

    print(f"\nTotal uptime: {total}")

    csv_name = f"uptime_{target_str}.csv"
    export_csv(sessions, csv_name)
    print(f"\nCSV exported: {csv_name}")


if __name__ == "__main__":
    main()
