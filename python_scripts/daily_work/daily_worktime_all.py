#!/usr/bin/env python3
"""
daily_worktime_all.py

Processes ALL available boot/shutdown logs and outputs a CSV:

    uptime_all.csv

Columns:
    date, minutes

Uses the logic:
    - Earliest boot of the day (or spanning boot)
    - Last shutdown of the day (or next shutdown fallback)
"""

import subprocess
import re
import csv
from datetime import datetime, timedelta

TS_RE = re.compile(
    r"[A-Z][a-z]{2}\s+[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+\d{4}"
)


def run_last(args):
    out = subprocess.check_output(args, text=True)
    return [l for l in out.splitlines() if l.strip()]


def parse_timestamps_from_line(line):
    matches = TS_RE.findall(line)
    dt_list = []
    for m in matches:
        try:
            dt = datetime.strptime(m, "%a %b %d %H:%M:%S %Y")
        except ValueError:
            dt = datetime.strptime(" ".join(m.split()[1:]), "%b %d %H:%M:%S %Y")
        dt_list.append(dt)
    return dt_list


def collect_boots_and_shutdowns():
    boot_lines = run_last(["last", "-x", "-F", "reboot"])
    shutdown_lines = run_last(["last", "-x", "-F", "shutdown"])

    boots, shutdowns = [], []

    for line in boot_lines:
        if not line.startswith("reboot"):
            continue
        ts = parse_timestamps_from_line(line)
        if not ts:
            continue
        start = ts[0]
        end_hint = ts[1] if len(ts) > 1 else None
        boots.append({"start": start, "end_hint": end_hint})

    for line in shutdown_lines:
        if not line.startswith("shutdown"):
            continue
        ts = parse_timestamps_from_line(line)
        if not ts:
            continue
        shutdowns.append({"start": ts[0]})

    boots.sort(key=lambda x: x["start"])
    shutdowns.sort(key=lambda x: x["start"])
    return boots, shutdowns


def find_first_boot_for_date(boots, date):
    day_start = datetime(date.year, date.month, date.day)
    day_end = day_start + timedelta(days=1)

    boots_today = [b for b in boots if b["start"].date() == date]
    if boots_today:
        return min(b["start"] for b in boots_today)

    # spanning boots
    for b in reversed(boots):
        if b["start"] < day_start:
            if b["end_hint"] and b["end_hint"] > day_start:
                return b["start"]
            if not b["end_hint"]:
                return b["start"]
    return None


def find_last_shutdown_for_date(shutdowns, date):
    sd_today = [s for s in shutdowns if s["start"].date() == date]
    if sd_today:
        return max(s["start"] for s in sd_today)

    # fallback: shutdown after date
    after = [s["start"] for s in shutdowns if s["start"].date() > date]
    if after:
        return min(after)

    # fallback: end of day
    return datetime(date.year, date.month, date.day, 23, 59, 59)


def main():
    boots, shutdowns = collect_boots_and_shutdowns()

    # Collect all dates found in logs
    all_dates = set()

    for b in boots:
        all_dates.add(b["start"].date())
        if b["end_hint"]:
            all_dates.add(b["end_hint"].date())

    for s in shutdowns:
        all_dates.add(s["start"].date())

    all_dates = sorted(all_dates)

    results = []
    for date in all_dates:
        first_boot = find_first_boot_for_date(boots, date)
        last_shutdown = find_last_shutdown_for_date(shutdowns, date)

        if not first_boot or not last_shutdown:
            continue

        if last_shutdown < first_boot:
            continue  # corrupt entry

        delta = last_shutdown - first_boot
        minutes = int(delta.total_seconds() // 60)

        results.append((date.isoformat(), minutes))

    # Write CSV
    with open("uptime_all.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "minutes"])
        for row in results:
            writer.writerow(row)

    print("DONE: uptime_all.csv created with", len(results), "records")


if __name__ == "__main__":
    main()
