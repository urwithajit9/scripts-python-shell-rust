import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
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
        # Convert to decimal hours: 9 + (6 / 60)
        return hours + (minutes / 60)
    except (ValueError, TypeError):
        return np.nan


def time_to_offset(time_str):
    """Converts a time string ('HH:MM:SS') into a datetime object tied to a dummy date (Jan 1, 1900)
    for plotting on a time-based axis."""
    if pd.isna(time_str) or not time_str:
        return np.nan
    try:
        dt = datetime.strptime(time_str, "%H:%M:%S")
        # Combine with the dummy date
        return DUMMY_DATE.replace(hour=dt.hour, minute=dt.minute, second=dt.second)
    except ValueError:
        return np.nan


# --- 3. Main Plotting Function ---


def generate_work_span_charts():
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        print(
            f"Error: CSV file '{CSV_FILE}' not found. Please run the script that generates it first."
        )
        return

    # Filter out rows where the total span calculation failed (i.e., missing data)
    df = df[df["total_span"].notna() & (df["total_span"] != "")].copy()

    if df.empty:
        print("No complete work spans found in the CSV to plot.")
        return

    # --- Data Cleaning and Conversion ---

    # Convert H.MM format to decimal hours for accurate comparison
    df["decimal_hours"] = df["total_span"].apply(h_mm_to_decimal)

    # Convert date and time strings to usable datetime formats
    df["date_dt"] = pd.to_datetime(df["date"])
    df["first_boot_dt"] = df["first_boot"].apply(time_to_offset)
    df["last_shutdown_dt"] = df["last_shutdown"].apply(time_to_offset)

    # Calculate duration (for the width of the bars in the Range Plot)
    df["duration_td"] = df["last_shutdown_dt"] - df["first_boot_dt"]

    # Sort the DataFrame by date for chronological plotting
    df = df.sort_values(by="date_dt").reset_index(drop=True)

    # Determine colors based on the target
    colors = np.where(
        df["decimal_hours"] >= TARGET_SPAN_HOURS, "#28a745", "#dc3545"
    )  # Green/Red

    # =========================================================================
    ## 1. Bar Chart: Daily Duration Comparison
    # =========================================================================

    plt.figure(figsize=(12, 6))

    plt.bar(df["date"], df["decimal_hours"], color=colors)

    # Draw the 9-hour target line
    plt.axhline(
        TARGET_SPAN_HOURS,
        color="#007bff",
        linestyle="--",
        linewidth=2,
        label=f"{TARGET_SPAN_HOURS} Hour Target Span",
    )

    plt.ylabel("Total Span (Decimal Hours)")
    plt.title("Daily Work Span vs. Target Duration")
    plt.xticks(rotation=45, ha="right")
    plt.ylim(0, df["decimal_hours"].max() * 1.1)
    plt.legend()
    plt.grid(axis="y", alpha=0.5)
    plt.tight_layout()
    plt.savefig("daily_duration_comparison.png")
    plt.close()
    print("Chart 1: 'daily_duration_comparison.png' saved.")

    # =========================================================================
    ## 2. Range Plot (Gantt-style): Login/Logout Times
    # =========================================================================

    plt.figure(figsize=(12, 8))

    # Plot the range from first_boot to last_shutdown
    plt.barh(
        y=df["date"],
        left=df["first_boot_dt"],
        width=df["duration_td"],
        color=colors,
        edgecolor="black",
        alpha=0.7,
    )

    # Set X-axis to display time
    ax = plt.gca()
    formatter = mdates.DateFormatter("%H:%M")
    ax.xaxis.set_major_formatter(formatter)

    # Set X-axis limits based on typical work hours (e.g., 8 AM to 8 PM)
    start_time = DUMMY_DATE.replace(hour=8, minute=0, second=0)
    end_time = DUMMY_DATE.replace(hour=20, minute=0, second=0)
    ax.set_xlim(start_time, end_time)

    plt.xlabel("Time of Day")
    plt.ylabel("Date")
    plt.title("Daily Work Span (Login to Logout Times)")
    plt.grid(axis="x", alpha=0.5)
    plt.tight_layout()
    plt.savefig("daily_time_span_gantt.png")
    plt.close()
    print("Chart 2: 'daily_time_span_gantt.png' saved.")


if __name__ == "__main__":
    generate_work_span_charts()
