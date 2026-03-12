import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, time
import numpy as np

# --- 1. Configuration ---
CSV_FILE = "system_work_history.csv"
TARGET_SPAN_HOURS = 9.0  # 8 hours work + 1 hour lunch
DUMMY_DATE = datetime(1900, 1, 1)

# --- 2. Data Preparation Functions ---


def h_mm_to_decimal(h_mm_str):
    """Converts the 'H.MM' format string (e.g., '9.06') to decimal hours (e.g., 9.1)."""
    try:
        h_mm = float(h_mm_str)
        # Separate hours and minutes (9.06 -> hours=9, minutes=6)
        hours = np.floor(h_mm)
        minutes = (h_mm * 100) % 100
        # Convert to decimal hours: 9 + (minutes / 60)
        return hours + (minutes / 60)
    except (ValueError, TypeError):
        return np.nan


def time_to_offset_seconds(time_str):
    """Converts a time string ('HH:MM:SS') into total seconds from midnight."""
    if pd.isna(time_str) or not time_str:
        return np.nan
    try:
        # We parse the time and convert it to a datetime.time object
        t = datetime.strptime(time_str, "%H:%M:%S").time()
        # Convert time to total seconds from midnight
        return t.hour * 3600 + t.minute * 60 + t.second
    except ValueError:
        return np.nan


# --- 3. Main Plotting Function ---


def generate_monthly_charts():
    print(f"Reading data from {CSV_FILE}...")
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        print(f"Error: CSV file '{CSV_FILE}' not found. Ensure the file exists.")
        return

    # Filter out rows where the total span calculation failed
    df = df[df["total_span"].notna() & (df["total_span"] != "")].copy()

    if df.empty:
        print("No complete work spans found in the CSV to plot.")
        return

    # --- Data Cleaning and Conversion ---

    # 1. Convert span to decimal hours
    df["decimal_hours"] = df["total_span"].apply(h_mm_to_decimal)

    # 2. Convert date string to datetime object
    df["date_dt"] = pd.to_datetime(df["date"])

    # 3. Extract Month for grouping
    df["month"] = df["date_dt"].dt.to_period("M")

    # 4. Convert time strings to seconds from midnight for averaging
    df["first_boot_sec"] = df["first_boot"].apply(time_to_offset_seconds)
    df["last_shutdown_sec"] = df["last_shutdown"].apply(time_to_offset_seconds)

    # --- Aggregation by Month ---

    monthly_summary = (
        df.groupby("month")
        .agg(
            avg_span=("decimal_hours", "mean"),
            avg_boot_sec=("first_boot_sec", "mean"),
            avg_shutdown_sec=("last_shutdown_sec", "mean"),
            day_count=("date", "count"),
        )
        .reset_index()
    )

    # Convert month back to string for plotting labels
    monthly_summary["month_label"] = monthly_summary["month"].astype(str)

    # =========================================================================
    ## 1. Monthly Duration Summary (Bar Chart)
    # =========================================================================

    plt.figure(figsize=(10, 6))

    # Color bars based on whether the monthly average met the target
    colors = np.where(
        monthly_summary["avg_span"] >= TARGET_SPAN_HOURS, "#28a745", "#dc3545"
    )  # Green/Red

    plt.bar(monthly_summary["month_label"], monthly_summary["avg_span"], color=colors)

    # Draw the 9-hour target line
    plt.axhline(
        TARGET_SPAN_HOURS,
        color="#007bff",
        linestyle="--",
        linewidth=2,
        label=f"{TARGET_SPAN_HOURS} Hour Target Span",
    )

    plt.ylabel("Average Daily Work Span (Hours)")
    plt.xlabel("Month")
    plt.title("Monthly Average Daily Work Span vs. Target")
    plt.legend()
    plt.grid(axis="y", alpha=0.5)
    plt.tight_layout()
    plt.savefig("monthly_avg_duration_summary.png")
    plt.close()
    print("Chart 1: 'monthly_avg_duration_summary.png' saved.")

    # =========================================================================
    ## 2. Monthly Start/End Trend (Line Plot)
    # =========================================================================

    # Function to convert average seconds back to a readable time object for plotting
    def seconds_to_time_offset(seconds):
        if pd.isna(seconds):
            return np.nan
        # Add seconds to the dummy date
        return DUMMY_DATE.replace(hour=0, minute=0, second=0) + pd.Timedelta(
            seconds=seconds
        )

    monthly_summary["avg_boot_time"] = monthly_summary["avg_boot_sec"].apply(
        seconds_to_time_offset
    )
    monthly_summary["avg_shutdown_time"] = monthly_summary["avg_shutdown_sec"].apply(
        seconds_to_time_offset
    )

    plt.figure(figsize=(10, 6))

    plt.plot(
        monthly_summary["month_label"],
        monthly_summary["avg_boot_time"],
        marker="o",
        linestyle="-",
        color="red",
        label="Average First Boot Time",
    )

    plt.plot(
        monthly_summary["month_label"],
        monthly_summary["avg_shutdown_time"],
        marker="o",
        linestyle="-",
        color="blue",
        label="Average Last Shutdown Time",
    )

    # Set Y-axis to display time
    ax = plt.gca()
    formatter = mdates.DateFormatter("%H:%M")
    ax.yaxis.set_major_formatter(formatter)

    # Set Y-axis limits to focus on work hours (e.g., 8 AM to 8 PM)
    start_time_limit = DUMMY_DATE.replace(hour=8, minute=0, second=0)
    end_time_limit = DUMMY_DATE.replace(hour=20, minute=0, second=0)
    ax.set_ylim(start_time_limit, end_time_limit)

    plt.ylabel("Time of Day")
    plt.xlabel("Month")
    plt.title("Monthly Trend in Average Work Start and End Times")
    plt.legend()
    plt.grid(axis="y", alpha=0.5)
    plt.tight_layout()
    plt.savefig("monthly_start_end_trend.png")
    plt.close()
    print("Chart 2: 'monthly_start_end_trend.png' saved.")


if __name__ == "__main__":
    generate_monthly_charts()
