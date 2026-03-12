#!/usr/bin/env python3
import subprocess
import sys
import re
from datetime import datetime, timedelta


def get_last_reboot_data():
    """Runs 'last -x -F reboot' and returns the output lines."""
    try:
        # We use -x -F to get full timestamps
        result = subprocess.run(
            ["last", "-x", "-F", "reboot"], stdout=subprocess.PIPE, text=True
        )
        return result.stdout.splitlines()
    except FileNotFoundError:
        print("Error: 'last' command not found.")
        sys.exit(1)


def parse_date(date_str):
    """Parses date string like 'Wed Dec  3 16:10:31 2025'"""
    # Collapse multiple spaces into one for cleaner parsing
    clean_str = " ".join(date_str.split())
    return datetime.strptime(clean_str, "%a %b %d %H:%M:%S %Y")


def calculate_uptime(target_date_str):
    try:
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    except ValueError:
        print("Error: Invalid date format. Use YYYY-MM-DD")
        sys.exit(1)

    # Define the 24-hour window for the target date
    day_start = datetime.combine(target_date, datetime.min.time())
    day_end = datetime.combine(target_date, datetime.max.time())

    log_lines = get_last_reboot_data()

    # Regex to capture: Start Time AND (End Time OR "still running")
    # Matches: "reboot system boot ... Wed Dec 3 16:10:31 2025 - Wed Dec 3 18:28:09 2025"
    # Or:      "reboot system boot ... Thu Dec 4 11:10:21 2025   still running"
    pattern = re.compile(
        r"reboot\s+system boot\s+.*?\s+([A-Z][a-z]{2}\s+[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2}\s+\d{4})\s+(?:-\s+([A-Z][a-z]{2}\s+[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2}\s+\d{4})|still running)"
    )

    total_seconds = 0
    sessions_found = 0

    print(f"=== Analyzing Sessions for {target_date} ===")

    for line in log_lines:
        match = pattern.search(line)
        if not match:
            continue

        start_str = match.group(1)
        end_str = match.group(2)

        try:
            session_start = parse_date(start_str)

            if end_str:
                session_end = parse_date(end_str)
            else:
                # "still running" means the session goes until NOW (or end of log scope)
                session_end = datetime.now()

            # --- INTERVAL INTERSECTION LOGIC ---
            # 1. Clip the session start to the target day
            # If session started yesterday, we count from 00:00:00 today.
            effective_start = max(session_start, day_start)

            # 2. Clip the session end to the target day
            # If session ends tomorrow, we count until 23:59:59 today.
            effective_end = min(session_end, day_end)

            # 3. Check if there is a valid overlap
            if effective_start < effective_end:
                duration = effective_end - effective_start
                total_seconds += duration.total_seconds()
                sessions_found += 1
                # Optional: Print detail for debugging
                # print(f"  + Added {duration} from session starting {session_start}")

        except ValueError as e:
            continue

    if sessions_found == 0:
        print(f"No active sessions found for {target_date_str}")

    # Format output
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)

    print(f"Total Active Worktime: {hours} hours {minutes} minutes")
    print(f"Sessions counted: {sessions_found}")

    # CSV Export
    csv_filename = f"runtime_{target_date_str}.csv"
    with open(csv_filename, "w") as f:
        f.write("date,total_hours,total_minutes,sessions_count\n")
        f.write(f"{target_date_str},{hours},{minutes},{sessions_found}\n")
    print(f"CSV exported to {csv_filename}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 daily_uptime.py YYYY-MM-DD")
        sys.exit(1)

    calculate_uptime(sys.argv[1])

"""
# For the day with many reboots (Dec 3)
python daily_uptime_gemini.py 2025-12-03

# For today
python daily_uptime.py 2025-12-04
"""
