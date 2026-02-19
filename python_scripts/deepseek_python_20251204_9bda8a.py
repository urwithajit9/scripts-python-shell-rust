#!/usr/bin/env python3

import subprocess
from datetime import datetime, timedelta
import re
from collections import defaultdict

def run_command(cmd):
    """Run a shell command and return its output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{cmd}': {e}")
        return ""

def parse_last_output(output):
    """Parse last command output to extract events"""
    events = []
    lines = output.strip().split('\n')
    
    for line in lines:
        if not line.strip():
            continue
            
        # Skip header lines and wtmp begins lines
        if line.startswith('reboot') or line.startswith('shutdown'):
            # Parse reboot or shutdown line
            parts = line.split()
            
            if line.startswith('reboot'):
                event_type = 'boot'
            else:
                event_type = 'down'
            
            # Extract date strings using regex
            # Pattern matches: "Thu Dec  4 11:10:21 2025" or "Thu Dec 04 11:10:21 2025"
            date_pattern = r'(\w{3} \w{3} \s?\d{1,2} \d{2}:\d{2}:\d{2} \d{4})'
            dates = re.findall(date_pattern, line)
            
            if dates:
                try:
                    # Normalize single digit days to have two spaces
                    date_str = dates[0]
                    # Fix spacing for single-digit days
                    if date_str[7] == ' ' and date_str[8] != ' ':
                        date_str = date_str[:7] + ' ' + date_str[7:]
                    
                    start_time = datetime.strptime(date_str, '%a %b %d %H:%M:%S %Y')
                    
                    if 'still running' in line:
                        end_time = None
                    elif len(dates) > 1:
                        # Second date exists
                        date_str2 = dates[1]
                        if date_str2[7] == ' ' and date_str2[8] != ' ':
                            date_str2 = date_str2[:7] + ' ' + date_str2[7:]
                        end_time = datetime.strptime(date_str2, '%a %b %d %H:%M:%S %Y')
                    else:
                        # Parse duration in parentheses
                        duration_match = re.search(r'\((\d+):(\d+)\)', line)
                        if duration_match:
                            hours = int(duration_match.group(1))
                            minutes = int(duration_match.group(2))
                            end_time = start_time + timedelta(hours=hours, minutes=minutes)
                        else:
                            # Handle multi-day format like "(2+20:14)"
                            multi_day_match = re.search(r'\((\d+)\+(\d+):(\d+)\)', line)
                            if multi_day_match:
                                days = int(multi_day_match.group(1))
                                hours = int(multi_day_match.group(2))
                                minutes = int(multi_day_match.group(3))
                                end_time = start_time + timedelta(days=days, hours=hours, minutes=minutes)
                            else:
                                # No end time found, use start time
                                end_time = start_time
                    
                    events.append({
                        'type': event_type,
                        'start': start_time,
                        'end': end_time
                    })
                except ValueError as e:
                    print(f"Warning: Could not parse date from line: {line}")
                    print(f"Error: {e}")
                    continue
    
    return events

def get_current_boot_time():
    """Get the current boot time using uptime command"""
    try:
        # Try to get boot time from /proc/uptime and calculate
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.read().split()[0])
        
        boot_time = datetime.now() - timedelta(seconds=uptime_seconds)
        return boot_time
    except:
        # Fallback: use who -b
        output = run_command("who -b")
        if output:
            lines = output.strip().split('\n')
            for line in lines:
                if 'system boot' in line:
                    date_str = line.split('system boot')[1].strip()
                    try:
                        return datetime.strptime(date_str, '%Y-%m-%d %H:%M')
                    except:
                        pass
        return datetime.now()

def calculate_daily_uptime(boot_events, shutdown_events):
    """Calculate uptime for each day"""
    # Get current time
    current_time = datetime.now()
    
    # Combine all events into a single timeline
    all_events = []
    
    # Add boot events
    for event in boot_events:
        all_events.append({
            'timestamp': event['start'],
            'action': 'start',
            'type': 'up'
        })
        if event['end']:
            all_events.append({
                'timestamp': event['end'],
                'action': 'end',
                'type': 'up'
            })
        elif event['type'] == 'boot':  # Still running
            all_events.append({
                'timestamp': current_time,
                'action': 'end',
                'type': 'up'
            })
    
    # Add shutdown events
    for event in shutdown_events:
        all_events.append({
            'timestamp': event['start'],
            'action': 'start',
            'type': 'down'
        })
        if event['end']:
            all_events.append({
                'timestamp': event['end'],
                'action': 'end',
                'type': 'down'
            })
    
    # Sort events by timestamp
    all_events.sort(key=lambda x: x['timestamp'])
    
    # Initialize daily uptime tracking
    daily_uptime = defaultdict(timedelta)
    
    # Process events to calculate uptime per day
    current_state = 'down'  # Assume system started down
    last_timestamp = None
    
    # Find the earliest timestamp from events or use current boot time
    earliest_time = current_time
    if all_events:
        earliest_time = min(all_events[0]['timestamp'], earliest_time)
    
    last_timestamp = earliest_time
    
    for event in all_events:
        if current_state == 'up' and last_timestamp:
            # System was up, add this period to daily uptime
            add_uptime_period(last_timestamp, event['timestamp'], daily_uptime)
        
        # Update state
        if event['action'] == 'start':
            if event['type'] == 'up':
                current_state = 'up'
            else:  # down
                current_state = 'down'
        else:  # end
            if event['type'] == 'up':
                current_state = 'down'
            else:  # down ended (system came up)
                current_state = 'up'
        
        last_timestamp = event['timestamp']
    
    # Handle current state if still up
    if current_state == 'up' and last_timestamp:
        add_uptime_period(last_timestamp, current_time, daily_uptime)
    
    return daily_uptime

def add_uptime_period(start_time, end_time, daily_uptime):
    """Add an uptime period to the daily totals"""
    current_day = start_time.date()
    end_day = end_time.date()
    
    # If period spans multiple days, split it
    while current_day <= end_day:
        day_start = datetime.combine(current_day, datetime.min.time())
        day_end = datetime.combine(current_day, datetime.max.time()) + timedelta(seconds=1)
        
        # Calculate overlap with current day
        period_start = max(start_time, day_start)
        period_end = min(end_time, day_end)
        
        if period_start < period_end:
            duration = period_end - period_start
            daily_uptime[current_day] += duration
        
        # Move to next day
        current_day += timedelta(days=1)

def format_duration(td):
    """Format timedelta to HH:MM:SS"""
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def main():
    print("Fetching system boot and shutdown history...")
    print("-" * 60)
    
    # Get current boot time
    current_boot = get_current_boot_time()
    print(f"Current system boot time: {current_boot.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get reboot history
    print("\nFetching reboot history...")
    reboot_output = run_command("last -x -F reboot")
    boot_events = parse_last_output(reboot_output)
    print(f"Found {len(boot_events)} boot events")
    
    # Get shutdown history
    print("\nFetching shutdown history...")
    shutdown_output = run_command("last -x -F shutdown")
    shutdown_events = parse_last_output(shutdown_output)
    print(f"Found {len(shutdown_events)} shutdown events")
    
    if not boot_events and not shutdown_events:
        print("\nNo boot/shutdown events found. Checking uptime...")
        uptime_output = run_command("uptime -p")
        print(f"Current uptime: {uptime_output.strip()}")
        return
    
    # Calculate daily uptime
    print("\nCalculating daily uptime...")
    daily_uptime = calculate_daily_uptime(boot_events, shutdown_events)
    
    # Print results
    print("\n" + "=" * 60)
    print("DAILY UPTIME REPORT")
    print("=" * 60)
    
    if not daily_uptime:
        print("No uptime data available.")
        return
    
    # Get today and yesterday for comparison
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    # Print most recent days first
    sorted_days = sorted(daily_uptime.keys(), reverse=True)
    
    total_uptime = timedelta()
    days_with_data = 0
    
    for day in sorted_days:
        uptime = daily_uptime[day]
        total_uptime += uptime
        days_with_data += 1
        
        # Calculate percentage (handle partial days for today)
        if day == today:
            day_seconds = (datetime.now() - datetime.combine(day, datetime.min.time())).total_seconds()
        else:
            day_seconds = 24 * 3600
        
        percentage = (uptime.total_seconds() / day_seconds) * 100
        
        day_str = day.strftime('%Y-%m-%d (%a)')
        duration_str = format_duration(uptime)
        
        # Highlight today and yesterday
        if day == today:
            day_str = f"▶ {day_str} (TODAY)"
        elif day == yesterday:
            day_str = f"  {day_str} (YESTERDAY)"
        else:
            day_str = f"  {day_str}"
        
        print(f"{day_str}: {duration_str} ({percentage:.1f}%)")
    
    # Calculate and print averages
    if days_with_data > 0:
        avg_uptime = total_uptime / days_with_data
        avg_percentage = (avg_uptime.total_seconds() / (24 * 3600)) * 100
        
        print("\n" + "-" * 60)
        print(f"Average daily uptime ({days_with_data} days): {format_duration(avg_uptime)} ({avg_percentage:.1f}%)")
    
    # Print current session info
    print("\n" + "=" * 60)
    print("CURRENT SESSION")
    print("=" * 60)
    
    # Get current uptime
    uptime_output = run_command("uptime -p")
    if uptime_output:
        print(f"Current uptime: {uptime_output.strip()}")
    
    # Count today's reboots
    today_reboots = sum(1 for event in boot_events 
                       if event['start'].date() == today and event['type'] == 'boot')
    if today_reboots > 0:
        print(f"Reboots today: {today_reboots}")
    
    # Get load average
    load_output = run_command("cat /proc/loadavg")
    if load_output:
        load_parts = load_output.strip().split()
        if len(load_parts) >= 3:
            print(f"Load average: {load_parts[0]} (1min), {load_parts[1]} (5min), {load_parts[2]} (15min)")

if __name__ == "__main__":
    main()