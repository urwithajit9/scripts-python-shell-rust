#!/usr/bin/env python3
"""
daily_worktime_final.py

Usage:
  python3 daily_worktime_final.py YYYY-MM-DD

Behavior:
 - Finds earliest boot timestamp on target date (or boot that started before day but overlaps day start).
 - Finds latest shutdown *start* timestamp on target date (or uses shutdown that starts before but overlaps).
 - Computes working_time = last_shutdown - first_boot and writes an output CSV (uptime_<date>.csv).
"""

import subprocess, sys, csv
from datetime import datetime, timedelta
import re

TS_RE = re.compile(
    r"[A-Z][a-z]{2}\s+[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+\d{4}"
)


def run_last(cmd_args):
    out = subprocess.check_output(cmd_args, text=True, stderr=subprocess.DEVNULL)
    return [l for l in out.splitlines() if l.strip()]


def parse_timestamps_from_line(line):
    """Return list of datetime objects found in the line (0,1 or 2)."""
    matches = TS_RE.findall(line)
    dt_list = []
    for m in matches:
        # try with weekday included
        try:
            dt = datetime.strptime(m, "%a %b %d %H:%M:%S %Y")
        except ValueError:
            # fallback: no weekday
            dt = datetime.strptime(" ".join(m.split()[1:]), "%b %d %H:%M:%S %Y")
        dt_list.append(dt)
    return dt_list


def collect_boots_and_shutdowns():
    boot_lines = run_last(["last", "-x", "-F", "reboot"])
    shutdown_lines = run_last(["last", "-x", "-F", "shutdown"])

    boots = []
    for line in boot_lines:
        if not line.startswith("reboot"):
            continue
        ts = parse_timestamps_from_line(line)
        if not ts:
            continue
        start = ts[0]
        # Optional end hint may be in ts[1]
        end_hint = ts[1] if len(ts) > 1 else None
        boots.append({"start": start, "end_hint": end_hint, "raw": line})

    shutdowns = []
    for line in shutdown_lines:
        if not line.startswith("shutdown"):
            continue
        ts = parse_timestamps_from_line(line)
        if not ts:
            continue
        # use shutdown start timestamp (when system went down)
        shutdowns.append({"start": ts[0], "raw": line})

    # sort ascending
    boots.sort(key=lambda b: b["start"])
    shutdowns.sort(key=lambda s: s["start"])
    return boots, shutdowns


def find_first_boot_for_date(boots, target_date):
    day_start = datetime(target_date.year, target_date.month, target_date.day)
    day_end = day_start + timedelta(days=1)

    # boots on that day
    boots_on_day = [b for b in boots if b["start"].date() == target_date]
    if boots_on_day:
        # earliest boot on that day
        return min(b["start"] for b in boots_on_day)

    # fallback: find a boot that started before day_start but lasted into the day
    for b in reversed(boots):  # reverse so we find the latest boot before the day
        if b["start"] < day_start:
            # if end_hint exists and is after day_start, accept it
            if b["end_hint"] and b["end_hint"] > day_start:
                return b["start"]
            # otherwise we can't be sure - but if there's no end_hint, we can assume it continued -> accept
            if not b["end_hint"]:
                return b["start"]
            # otherwise it ended before the day, skip
    return None


def find_last_shutdown_for_date(shutdowns, target_date):
    # last shutdown start on that date
    shutting_on_day = [s for s in shutdowns if s["start"].date() == target_date]
    if shutting_on_day:
        return max(s["start"] for s in shutting_on_day)
    # fallback: maybe there is a shutdown whose end occurs on the day but start was earlier.
    # But shutdown lines use the start-of-shutdown timestamp; so if none start that day, we return None.
    return None


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 daily_worktime_final.py YYYY-MM-DD")
        sys.exit(1)

    try:
        target_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date. Use YYYY-MM-DD")
        sys.exit(1)

    boots, shutdowns = collect_boots_and_shutdowns()

    first_boot = find_first_boot_for_date(boots, target_date)
    last_shutdown = find_last_shutdown_for_date(shutdowns, target_date)

    print(f"=== System Running Time Summary for {target_date.isoformat()} ===")
    if not first_boot:
        print("No boot found for that date (and no spanning boot).")
        sys.exit(0)
    else:
        print("First Boot:", first_boot)

    if not last_shutdown:
        # If no shutdown recorded on that date, try to find a shutdown that happened after the day (rare)
        # or if the system is still running for that day's last boot, treat as "still running"
        print("No shutdown record starting on that date.")
        # as fallback, try to use last shutdown after the day_start (if any)
        later_shutdowns = [
            s["start"] for s in shutdowns if s["start"].date() > target_date
        ]
        if later_shutdowns:
            last_shutdown = min(later_shutdowns)  # first shutdown after day
            print("Using next shutdown after day as last_shutdown:", last_shutdown)
        else:
            # else use end of day
            last_shutdown = datetime(
                target_date.year, target_date.month, target_date.day, 23, 59, 59
            )
            print("Using end-of-day as last_shutdown:", last_shutdown)

    # Compute working interval
    interval = last_shutdown - first_boot
    total_seconds = int(interval.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    print("Last Shutdown:", last_shutdown)
    print(f"Working time = {hours} hours {minutes} minutes")

    # Export CSV
    csvname = f"uptime_{target_date.isoformat()}.csv"
    with open(csvname, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "first_boot", "last_shutdown", "hours", "minutes"])
        writer.writerow(
            [
                target_date.isoformat(),
                first_boot.isoformat(sep=" "),
                last_shutdown.isoformat(sep=" "),
                hours,
                minutes,
            ]
        )

    print("CSV exported:", csvname)


if __name__ == "__main__":
    main()
