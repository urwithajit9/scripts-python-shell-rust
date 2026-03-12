#!/usr/bin/env python3
import subprocess
import sys
import re
from datetime import datetime


def get_last_reboot_data():
    """Runs 'last -x -F reboot' to get raw boot/shutdown data."""
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


def calculate_span(target_date_str):
    try:
        target_date_obj = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    except ValueError:
        print("Error: Invalid date format. Use YYYY-MM-DD")
        sys.exit(1)

    log_lines = get_last_reboot_data()

    # Regex to capture: Start Time AND (End Time OR "still running")
    pattern = re.compile(
        r"reboot\s+system boot\s+.*?\s+([A-Z][a-z]{2}\s+[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2}\s+\d{4})\s+(?:-\s+([A-Z][a-z]{2}\s+[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2}\s+\d{4})|still running)"
    )

    # We will collect all start times and end times that happen ON the target day
    starts_on_day = []
    ends_on_day = []

    print(f"=== Workday Span for {target_date_str} ===")

    for line in log_lines:
        match = pattern.search(line)
        if not match:
            continue

        start_str = match.group(1)
        end_str = match.group(2)

        try:
            session_start = parse_date(start_str)

            # Determine Session End
            if end_str:
                session_end = parse_date(end_str)
            else:
                # "still running" means NOW
                session_end = datetime.now()

            # --- SPAN LOGIC ---

            # 1. Capture Boot Time if it matches Target Date
            if session_start.date() == target_date_obj:
                starts_on_day.append(session_start)

            # 2. Capture Shutdown Time if it matches Target Date
            # Note: We also check session_start to assume the shutdown belongs to a session relevant to this timeframe
            if session_end.date() == target_date_obj:
                ends_on_day.append(session_end)

            # Handle the case where "still running" goes into the future/current moment
            # If we are checking Today, and it's still running, the end time is NOW.
            if end_str is None and session_start.date() == target_date_obj:
                ends_on_day.append(session_end)

        except ValueError:
            continue

    # --- CALCULATE RESULTS ---

    if not starts_on_day:
        print(f"No boot events found starting on {target_date_str}.")
        # Edge Case: Maybe computer was left on overnight?
        return

    # Find the Earliest Boot and Latest Shutdown
    earliest_boot = min(starts_on_day)

    if ends_on_day:
        latest_shutdown = max(ends_on_day)
    else:
        # If logs show boots but no shutdowns on this day (rare, implies crash or running into next day)
        # We cap it at the last known activity or end of day?
        # For safety, let's assume it ran until the latest boot time found (min viable) or warn user.
        print(
            "Warning: Boots found but no shutdowns recorded for this date (running overnight?)."
        )
        latest_shutdown = max(starts_on_day)  # Fallback

    # Calculate Span
    span = latest_shutdown - earliest_boot
    total_seconds = span.total_seconds()

    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)

    print(f"First Boot:    {earliest_boot}")
    print(f"Last Shutdown: {latest_shutdown}")
    print(f"----------------------------------")
    print(f"Total Span:    {hours} hours {minutes} minutes")

    # CSV Export
    csv_filename = f"workspan_{target_date_str}.csv"
    with open(csv_filename, "w") as f:
        f.write("date,first_boot,last_shutdown,span_hours,span_minutes\n")
        f.write(
            f"{target_date_str},{earliest_boot},{latest_shutdown},{hours},{minutes}\n"
        )
    print(f"CSV exported to {csv_filename}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 daily_span.py YYYY-MM-DD")
        sys.exit(1)

    calculate_span(sys.argv[1])
