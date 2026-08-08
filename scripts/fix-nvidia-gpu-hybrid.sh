#!/usr/bin/env bash
# Fix hung nvidia-drm modprobe on hybrid Intel + NVIDIA (PRIME on-demand).
# Run: bash scripts/fix-nvidia-gpu-hybrid.sh
# Then reboot once (required to clear stuck udev "D" state).

set -euo pipefail

if [[ $(id -u) -ne 0 ]]; then
  echo "Run with sudo:  sudo bash $0"
  exit 1
fi

CONF=/etc/modprobe.d/zz-nvidia-drm-modeset-off.conf
echo "Writing ${CONF} (modeset=0 avoids common i915+nvidia DRM deadlocks)"
printf '%s\n' 'options nvidia-drm modeset=0' > "${CONF}"
chmod 644 "${CONF}"

echo "Updating initramfs for all installed kernels (may take a minute)..."
update-initramfs -u -k all

echo ""
echo "Done. You must reboot once:"
echo "  sudo reboot"
echo "After boot:  nvidia-smi  &&  ls -la /dev/nvidia*"
echo ""
echo "To undo:  sudo rm ${CONF} && sudo update-initramfs -u -k all && reboot"
