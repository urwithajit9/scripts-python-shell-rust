#!/usr/bin/env python3
import subprocess
import sys
import re
import csv
from collections import defaultdict
from datetime import datetime

OUTPUT_CSV = "system_work_history.csv"


def get_last_reboot_data():
    """Runs 'last -x -F reboot' to get raw boot/shutdown data."""
    try:
        # -x shows shutdown entries, -F shows full dates
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


def process_history():
    print("Reading system logs...")
    log_lines = get_last_reboot_data()

    # Dictionary to hold data for each date
    # Key: "YYYY-MM-DD", Value: {'starts': [], 'ends': []}
    daily_data = defaultdict(lambda: {"starts": [], "ends": []})

    # Regex: Captures Start Time AND (End Time OR "still running")
    pattern = re.compile(
        r"reboot\s+system boot\s+.*?\s+([A-Z][a-z]{2}\s+[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2}\s+\d{4})\s+(?:-\s+([A-Z][a-z]{2}\s+[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2}\s+\d{4})|still running)"
    )

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

            # --- GROUPING LOGIC ---
            # 1. Bucket the Boot Time to its specific date
            start_date_key = session_start.strftime("%Y-%m-%d")
            daily_data[start_date_key]["starts"].append(session_start)

            # 2. Bucket the Shutdown Time to its specific date
            end_date_key = session_end.strftime("%Y-%m-%d")
            daily_data[end_date_key]["ends"].append(session_end)

        except ValueError:
            continue

    # Prepare data for CSV
    csv_rows = []

    # Sort dates chronologically
    sorted_dates = sorted(daily_data.keys())

    print(f"Found activity on {len(sorted_dates)} unique dates.")

    for date_key in sorted_dates:
        day_events = daily_data[date_key]

        starts = day_events["starts"]
        ends = day_events["ends"]

        # Determine Earliest Boot
        first_boot = min(starts) if starts else None

        # Determine Latest Shutdown
        last_shutdown = max(ends) if ends else None

        # Calculate Span
        span_str = ""
        total_minutes_str = ""

        if first_boot and last_shutdown:
            # Only calculate if we have both points
            if last_shutdown >= first_boot:
                diff = last_shutdown - first_boot
                total_seconds = diff.total_seconds()

                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                total_mins_calc = int(total_seconds // 60)

                # Format as H.MM (e.g. 9.05 for 9 hours 5 minutes)
                span_str = f"{hours}.{minutes:02d}"
                total_minutes_str = str(total_mins_calc)
            else:
                # This handles edge cases where shutdown might be logged before boot (clock skew/errors)
                span_str = "Error"
                total_minutes_str = "Error"

        # Format timestamps for CSV (or leave blank if None)
        fb_str = first_boot.strftime("%H:%M:%S") if first_boot else ""
        ls_str = last_shutdown.strftime("%H:%M:%S") if last_shutdown else ""

        csv_rows.append(
            {
                "date": date_key,
                "first_boot": fb_str,
                "last_shutdown": ls_str,
                "total_span": span_str,
                "total_span_minutes": total_minutes_str,
            }
        )

    # Write to CSV
    with open(OUTPUT_CSV, "w", newline="") as f:
        fieldnames = [
            "date",
            "first_boot",
            "last_shutdown",
            "total_span",
            "total_span_minutes",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"Successfully exported full history to {OUTPUT_CSV}")


if __name__ == "__main__":
    process_history()
