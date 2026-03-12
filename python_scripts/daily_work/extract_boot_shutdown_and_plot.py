import subprocess
import re
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

BOOT_RE = re.compile(
    r"reboot\s+system boot.*?(\w{3}\s+\w{3}\s+\d+\s+\d+:\d+:\d+\s+\d{4})"
    r"(?:\s+-\s+(\w{3}\s+\w{3}\s+\d+\s+\d+:\d+:\d+\s+\d{4})|.*still running)"
)


def parse_last():
    out = subprocess.check_output(["last", "-F"]).decode()

    sessions = []
    for boot_time, shutdown_time in BOOT_RE.findall(out):
        bt = datetime.strptime(boot_time, "%a %b %d %H:%M:%S %Y")
        if "still running" in out:
            st = None
        else:
            st = (
                datetime.strptime(shutdown_time, "%a %b %d %H:%M:%S %Y")
                if shutdown_time
                else None
            )
        sessions.append((bt, st))

    return sessions


def compress_by_day(sessions):
    days = {}

    for boot, shutdown in sessions:
        day = boot.date()

        if day not in days:
            days[day] = {"boot": boot, "shutdown": shutdown}
        else:
            # earliest boot
            if boot < days[day]["boot"]:
                days[day]["boot"] = boot
            # latest shutdown
            if shutdown and (
                days[day]["shutdown"] is None or shutdown > days[day]["shutdown"]
            ):
                days[day]["shutdown"] = shutdown

    # remove incomplete days
    cleaned = {
        d: v
        for d, v in days.items()
        if v["boot"] is not None and v["shutdown"] is not None
    }
    return cleaned


def to_csv(days, csv_path="boot_shutdown.csv"):
    rows = []
    for d, v in days.items():
        rows.append(
            [
                d.isoformat(),
                v["boot"].time().isoformat(),
                v["shutdown"].time().isoformat(),
            ]
        )
    df = pd.DataFrame(rows, columns=["date", "boot_time", "shutdown_time"])
    df.to_csv(csv_path, index=False)
    return df


def plot(df):
    # Convert times to datetime "today + time" for plotting
    df["boot_dt"] = pd.to_datetime(df["boot_time"])
    df["shutdown_dt"] = pd.to_datetime(df["shutdown_time"])

    plt.figure(figsize=(12, 6))
    plt.plot(
        df["date"], df["boot_dt"].dt.hour + df["boot_dt"].dt.minute / 60, marker="o"
    )
    plt.plot(
        df["date"],
        df["shutdown_dt"].dt.hour + df["shutdown_dt"].dt.minute / 60,
        marker="o",
    )
    plt.xlabel("Date")
    plt.ylabel("Clock time (hours)")
    plt.title("Boot and Shutdown Times")
    plt.xticks(rotation=45)
    plt.grid()
    plt.legend(["Boot Time", "Shutdown Time"])
    plt.show()


if __name__ == "__main__":
    sessions = parse_last()
    days = compress_by_day(sessions)
    df = to_csv(days)
    print(df)
    plot(df)
