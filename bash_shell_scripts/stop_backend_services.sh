#!/bin/bash

# --- Configuration ---
# Services that are often heavy or non-essential for daily desktop development use.
# NOTE: postgresql.service is included, but only disable it if you don't need it running 24/7.
SERVICES_TO_DISABLE=(
    # Web & Database Servers
    "apache2.service"
    "nginx.service"
    "redis-server.service"
    "gunicorn.socket"

    # AI/ML/Developer Tools
    "ollama.service"

    # Docker & Container Related (High Priority)
    "snap.docker.dockerd.service"
    "snap.docker.nvidia-container-toolkit.service"
    "docker.socket"

    # Printing & General System Services
    "cups.service"
    "cups-browsed.service"
    "cups.path"
    "cups.socket"
    "bluetooth.service"
    "ModemManager.service"
    "postfix.service"
    "gnome-remote-desktop.service"
    "openvpn.service"
    "whoopsie.path"
    "sssd.service" # Includes all sssd-*.socket files implicitly
   
)

echo "--- Stopping and Disabling Non-Essential Services ---"
echo " "

# Loop through the list of services
for SERVICE in "${SERVICES_TO_DISABLE[@]}"; do
    echo "Processing: $SERVICE"

    # 1. Stop the service immediately
    if sudo systemctl is-active "$SERVICE" &> /dev/null; then
        echo "  - Stopping $SERVICE..."
        sudo systemctl stop "$SERVICE"
        if [ $? -eq 0 ]; then
            echo "    -> STOPPED successfully."
        else
            echo "    -> STOP failed or service was already stopped."
        fi
    else
        echo "  - Service $SERVICE is not active. Skipping stop."
    fi

    # 2. Disable the service from starting on boot
    if sudo systemctl is-enabled "$SERVICE" &> /dev/null; then
        echo "  - Disabling $SERVICE from boot..."
        sudo systemctl disable "$SERVICE"
        if [ $? -eq 0 ]; then
            echo "    -> DISABLED successfully."
        else
            echo "    -> DISABLE failed."
        fi
    else
        echo "  - Service $SERVICE is already disabled from boot."
    fi
    echo "---"
done

echo "Cleanup complete. Please reboot your system for all changes to take full effect."
echo "You can check your current running processes with 'htop'."
