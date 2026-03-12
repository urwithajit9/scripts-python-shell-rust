#!/bin/bash

# Script to calculate the total system running time (uptime) for a given date.
# Relies on the 'last' command's history.

DATE="$1"

# === 1. Input Validation ===
if [ -z "$DATE" ]; then
    echo "Usage: $0 YYYY-MM-DD"
    exit 1
fi

if ! date -d "$DATE" >/dev/null 2>&1; then
    echo "Invalid date format: $DATE"
    exit 1
fi

echo "=== System Running Time Summary for $DATE ==="

# --- 2. Date Formatting ---
# Convert input date to the 'last -F' output format: "Mon Dec 2 2025"
# %b: Abbreviated month name (e.g., Dec)
# %e: Day of month, space-padded (e.g., " 2")
# %Y: Year (e.g., 2025)
MONTH_DAY_YEAR=$(date -d "$DATE" "+%b %e %Y")

# Use sed to remove any double-spaces if %e produced a single digit day with a leading space.
MONTH_DAY_YEAR=$(echo "$MONTH_DAY_YEAR" | sed 's/  / /g')
YEAR_ONLY=$(date -d "$DATE" "+%Y")


# --- 3. Data Extraction ---

# Regex to extract the full timestamp (e.g., Fri Dec 20 09:32:52 2024)
# This handles the day name, month name, day number, time, and year.
TIMESTAMP_REGEX="[A-Z][a-z]{2} +[A-Z][a-z]{2} +[0-9]{1,2} [0-9]{2}:[0-9]{2}:[0-9]{2} [0-9]{4}"

# 1️⃣ Find ALL reboot events matching the specific date and year.
# Grepping the full date string prevents matching events from other years.
REBOOTS_MATCHES=$(last -x -F reboot | grep "$MONTH_DAY_YEAR")

if [ -z "$REBOOTS_MATCHES" ]; then
    echo "No boots found on $DATE"
    exit 0
fi

# The first boot of the day is the LAST line in the `last` output (since it lists newest first).
# We pipe through tail -1 to get the single line, then grep -oE to extract only the timestamp.
FIRST_BOOT_TIME=$(echo "$REBOOTS_MATCHES" | tail -1 | grep -oE "$TIMESTAMP_REGEX")

if [ -z "$FIRST_BOOT_TIME" ]; then
    echo "Error: Could not extract first boot time for $DATE."
    exit 1
fi

echo "First Boot:      $FIRST_BOOT_TIME"

# 2️⃣ Find ALL shutdown events matching the specific date and year.
SHUTDOWNS_MATCHES=$(last -x -F shutdown | grep "$MONTH_DAY_YEAR")

if [ -z "$SHUTDOWNS_MATCHES" ]; then
    # No shutdown found on this date, assume the system is currently running.
    LAST_SHUTDOWN_TIME=$(date "+%a %b %e %H:%M:%S $YEAR_ONLY")
else
    # The latest shutdown of the day is the FIRST line in the `last` output.
    LAST_SHUTDOWN_TIME=$(echo "$SHUTDOWNS_MATCHES" | head -1 | grep -oE "$TIMESTAMP_REGEX")
fi

if [ -z "$LAST_SHUTDOWN_TIME" ]; then
    echo "Error: Could not extract last shutdown time for $DATE."
    exit 1
fi

echo "Last Shutdown:   $LAST_SHUTDOWN_TIME"

# --- 4. Time Calculation ---

# Convert both timestamps to seconds since epoch
BOOT_TS=$(date -d "$FIRST_BOOT_TIME" +%s)
SHUT_TS=$(date -d "$LAST_SHUTDOWN_TIME" +%s)

# Compute difference
DIFF=$((SHUT_TS - BOOT_TS))

# Handle negative difference (e.g., if shutdown is in the next day's log, although the logic tries to prevent this)
if [ "$DIFF" -lt 0 ]; then
    echo "Warning: Running time calculated as 0 (boot time appears after shutdown time)."
    HOURS=0
    MINUTES=0
else
    HOURS=$((DIFF / 3600))
    MINUTES=$(((DIFF % 3600) / 60))
fi

echo "Total Running Time: ${HOURS} hours ${MINUTES} minutes"

# --- 5. Export CSV ---
CSV="runtime_${DATE}.csv"
echo "date,first_boot,last_shutdown,total_hours,total_minutes" > "$CSV"
echo "$DATE,$FIRST_BOOT_TIME,$LAST_SHUTDOWN_TIME,$HOURS,$MINUTES" >> "$CSV"

echo "CSV exported to $CSV"