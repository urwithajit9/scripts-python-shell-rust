import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, time
import numpy as np
import os

# --- 1. Configuration ---
CSV_FILE = "system_work_history.csv"
TARGET_SPAN_HOURS = 9.0  # 8 hours work + 1 hour lunch
DUMMY_DATE = datetime(1900, 1, 1)

# Crucial lines for Start/End time visualization
TARGET_START_TIME = DUMMY_DATE.replace(hour=9, minute=0, second=0)
TARGET_END_TIME = DUMMY_DATE.replace(hour=18, minute=0, second=0)
OUTPUT_DIR = "monthly_charts"

# --- 2. Data Preparation Functions ---


def h_mm_to_decimal(h_mm_str):
    """Converts the 'H.MM' format string (e.g., '9.06') to decimal hours (e.g., 9.1)."""
    try:
        h_mm = float(h_mm_str)
        # Separate hours and minutes (9.06 -> hours=9, minutes=6)
        hours = np.floor(h_mm)
        minutes = (h_mm * 100) % 100
        return hours + (minutes / 60)
    except (ValueError, TypeError):
        return np.nan


def time_to_offset_seconds(time_str):
    """Converts a time string ('HH:MM:SS') into total seconds from midnight."""
    if pd.isna(time_str) or not time_str:
        return np.nan
    try:
        t = datetime.strptime(time_str, "%H:%M:%S").time()
        # Convert time to total seconds from midnight
        return t.hour * 3600 + t.minute * 60 + t.second
    except ValueError:
        return np.nan


def seconds_to_time_offset(seconds):
    """Converts average seconds back to a readable time object for plotting."""
    if pd.isna(seconds):
        return np.nan
    # Add seconds to the dummy date
    return DUMMY_DATE.replace(hour=0, minute=0, second=0) + pd.Timedelta(
        seconds=seconds
    )


# --- 3. Main Plotting Function ---


def generate_detailed_monthly_charts():
    print(f"Reading data from {CSV_FILE}...")
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        print(f"Error: CSV file '{CSV_FILE}' not found. Ensure the file exists.")
        return

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Filter out rows where the total span calculation failed
    df = df[df["total_span"].notna() & (df["total_span"] != "")].copy()

    if df.empty:
        print("No complete work spans found in the CSV to plot.")
        return

    # --- Data Cleaning and Conversion (Daily) ---

    df["decimal_hours"] = df["total_span"].apply(h_mm_to_decimal)
    df["date_dt"] = pd.to_datetime(df["date"])
    df["first_boot_sec"] = df["first_boot"].apply(time_to_offset_seconds)
    df["last_shutdown_sec"] = df["last_shutdown"].apply(time_to_offset_seconds)
    df["month"] = df["date_dt"].dt.to_period("M")

    # --- Generate Charts for Each Month ---

    unique_months = df["month"].unique()

    for month in unique_months:
        month_str = str(month)
        month_df = df[df["month"] == month].sort_values(by="date_dt").copy()

        # Convert daily data to time offsets for plotting
        month_df["first_boot_time"] = month_df["first_boot_sec"].apply(
            seconds_to_time_offset
        )
        month_df["last_shutdown_time"] = month_df["last_shutdown_sec"].apply(
            seconds_to_time_offset
        )

        # Determine colors based on the target
        colors = np.where(
            month_df["decimal_hours"] >= TARGET_SPAN_HOURS, "#28a745", "#dc3545"
        )  # Green/Red

        # =========================================================================
        ## 1. Monthly Duration Chart (Daily Bars vs. Target)
        # =========================================================================

        plt.figure(figsize=(12, 6))

        plt.bar(month_df["date_dt"].dt.day, month_df["decimal_hours"], color=colors)

        plt.axhline(
            TARGET_SPAN_HOURS,
            color="#007bff",
            linestyle="--",
            linewidth=2,
            label=f"{TARGET_SPAN_HOURS} Hour Target Span",
        )

        plt.ylabel("Total Span (Decimal Hours)")
        plt.xlabel(f"Day of Month ({month_str})")
        plt.title(f"Daily Work Span vs. Target: {month_str}")
        plt.ylim(0, month_df["decimal_hours"].max() * 1.1)
        plt.legend()
        plt.grid(axis="y", alpha=0.5)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f"{month_str}_duration_chart.png"))
        plt.close()

        # =========================================================================
        ## 2. Monthly Start/End Time Chart (Daily Trend vs. 9:00/18:00)
        # =========================================================================

        plt.figure(figsize=(12, 6))

        # Plot Start Time
        plt.plot(
            month_df["date_dt"].dt.day,
            month_df["first_boot_time"],
            marker="o",
            linestyle="-",
            color="red",
            label="First Boot Time",
        )

        # Plot End Time
        plt.plot(
            month_df["date_dt"].dt.day,
            month_df["last_shutdown_time"],
            marker="o",
            linestyle="-",
            color="blue",
            label="Last Shutdown Time",
        )

        # --- Crucial Target Lines ---
        plt.axhline(
            TARGET_START_TIME,
            color="red",
            linestyle=":",
            alpha=0.6,
            label="Target Start (9:00 AM)",
        )
        plt.axhline(
            TARGET_END_TIME,
            color="blue",
            linestyle=":",
            alpha=0.6,
            label="Target End (6:00 PM)",
        )

        # Set Y-axis to display time
        ax = plt.gca()
        formatter = mdates.DateFormatter("%H:%M")
        ax.yaxis.set_major_formatter(formatter)

        # Adjust Y-axis limits for clarity (e.g., 8 AM to 8 PM)
        start_limit = DUMMY_DATE.replace(hour=8, minute=0, second=0)
        end_limit = DUMMY_DATE.replace(hour=20, minute=0, second=0)
        ax.set_ylim(start_limit, end_limit)

        plt.ylabel("Time of Day")
        plt.xlabel(f"Day of Month ({month_str})")
        plt.title(f"Daily Start/End Time Trend: {month_str}")
        plt.legend()
        plt.grid(axis="y", alpha=0.5)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f"{month_str}_time_trend_chart.png"))
        plt.close()

        print(f"Successfully generated 2 charts for {month_str}.")

    print(f"\nAll charts saved in the '{OUTPUT_DIR}' directory.")


if __name__ == "__main__":
    generate_detailed_monthly_charts()
