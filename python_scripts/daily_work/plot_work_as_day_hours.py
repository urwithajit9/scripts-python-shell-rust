#!/usr/bin/env python3
import csv
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

INPUT_FILE = "uptime_all.csv"
OUTPUT_FILE = "work_hours_plot.png"

# Base start of work-day for visualization (example: 8 AM)
BASE_START_HOUR = 9  # chart bottom will be 08:00


def read_csv(file_path):
    dates = []
    minutes = []

    with open(file_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                date = datetime.strptime(row["date"], "%Y-%m-%d")
                mins = int(row["minutes"])

                # Skip abnormal
                if mins > 700:
                    continue

                dates.append(date)
                minutes.append(mins)

            except Exception:
                continue

    return dates, minutes


def minutes_to_daytime(mins):
    """Convert minutes to a clock-time for plotting (e.g., 480 → 16:00)."""
    return BASE_START_HOUR + mins / 60.0


def main():
    dates, minutes = read_csv(INPUT_FILE)
    if not dates:
        print("No valid data.")
        return

    # Convert minutes to clock times (hour-of-day floats)
    day_hours = [minutes_to_daytime(m) for m in minutes]
    adjusted_hours = [minutes_to_daytime(max(m - 60, 0)) for m in minutes]

    # Plot
    plt.figure(figsize=(12, 6))

    plt.plot(dates, day_hours, marker="o", label="Work Duration (clock time)")
    plt.plot(
        dates,
        adjusted_hours,
        marker="o",
        linestyle="--",
        label="Work Duration - 60 min (clock time)",
    )

    plt.title("Daily Work Duration (Shown as Time of Day)")
    plt.xlabel("Date")
    plt.ylabel("Workday Time (Hour of Day)")

    # Show Y-axis as real clock labels (08:00 → 20:00)
    yticks = list(range(BASE_START_HOUR, BASE_START_HOUR + 13))  # 08 → 20
    plt.yticks(yticks, [f"{h:02d}:00" for h in yticks])

    plt.grid(True)
    plt.tight_layout()
    plt.legend()

    plt.savefig(OUTPUT_FILE)
    print(f"✓ Chart saved as {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
