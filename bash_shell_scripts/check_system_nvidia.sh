#!/bin/bash

echo "=== NVIDIA / GPU Health Check ==="
echo

# 1. Check kernel modules
echo "1. Loaded NVIDIA kernel modules:"
lsmod | grep -i nvidia || echo "NVIDIA modules not loaded!"

echo
# 2. Check GPU via nvidia-smi
echo "2. NVIDIA GPU status:"
if command -v nvidia-smi &>/dev/null; then
    nvidia-smi
else
    echo "nvidia-smi not found. NVIDIA driver might not be installed."
fi

echo
# 3. Check for Nouveau conflicts
echo "3. Nouveau driver status:"
lsmod | grep -i nouveau || echo "Nouveau is not loaded (good)."

echo
# 4. Check Xorg is using NVIDIA
echo "4. Xorg GPU check:"
if [ -f /var/log/Xorg.0.log ]; then
    grep -i "nvidia" /var/log/Xorg.0.log | tail -n 20
    grep -i "EE" /var/log/Xorg.0.log | tail -n 20
else
    echo "Xorg log not found."
fi

echo
# 5. Check /dev nodes
echo "5. NVIDIA device nodes:"
ls -l /dev/nvidia* 2>/dev/null || echo "No NVIDIA device nodes found!"

echo
# 6. Check DRM devices
echo "6. /dev/dri devices:"
ls -l /dev/dri 2>/dev/null || echo "No /dev/dri devices found!"

echo
# 7. Check PCI device
echo "7. PCI GPU devices:"
lspci | grep -i nvidia || echo "No NVIDIA PCI devices found!"

echo
# 8. Check recent kernel logs for NVIDIA errors
echo "8. Recent NVIDIA kernel errors (last 100 lines):"
dmesg | tail -n 100 | grep -iE "nvrm|nvidia|drm|gpu|xid"

echo
# 9. Check current XDG session type
echo "9. Current session type:"
echo $XDG_SESSION_TYPE

echo
# 10. Optional GPU stress test message
echo "10. Optional: You can run 'glmark2' for a stress test of GPU."

echo
echo "=== End of Check ==="
