#!/usr/bin/env python3
import csv
from datetime import datetime
import matplotlib.pyplot as plt

INPUT_FILE = "uptime_all.csv"
OUTPUT_FILE = "worktime_plot.png"


def read_csv(file_path):
    dates = []
    minutes = []

    with open(file_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                date = datetime.strptime(row["date"], "%Y-%m-%d")
                mins = int(row["minutes"])

                # Skip abnormal long uptime (>700 min)
                if mins > 700:
                    continue

                dates.append(date)
                minutes.append(mins)

            except Exception:
                continue

    return dates, minutes


def main():
    dates, minutes = read_csv(INPUT_FILE)

    if not dates:
        print("No valid data to plot.")
        return

    # Create the adjusted line
    adjusted = [max(m - 60, 0) for m in minutes]  # avoid negative values

    plt.figure(figsize=(12, 6))

    plt.plot(dates, minutes, marker="o", label="Daily Minutes")
    plt.plot(dates, adjusted, marker="o", linestyle="--", label="Minutes - 60")

    plt.title("Daily Working Time")
    plt.xlabel("Date")
    plt.ylabel("Minutes Worked")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig(OUTPUT_FILE)
    print(f"✓ Chart saved as {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
