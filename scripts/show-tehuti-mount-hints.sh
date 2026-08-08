#!/usr/bin/env bash
# Read-only hints: where is the external disk, and what folders exist?
# Run after plugging in the USB drive (mount may be automatic under /media).

set -euo pipefail

echo "=== /dev/sda (typical external USB) ==="
lsblk -o NAME,SIZE,MOUNTPOINT,LABEL,FSTYPE /dev/sda 2>/dev/null || echo "(no /dev/sda)"

echo ""
echo "=== Likely mount points to inspect ==="
for p in /mnt/usb_sda1 "/media/${USER}/WINSERVER2019" "/media/${USER}" "/run/media/${USER}"; do
  [[ -e "$p" ]] || continue
  if [[ -d "$p" ]]; then
    echo "--- $p ---"
    ls -la "$p" 2>/dev/null | head -25
    echo ""
  fi
done

echo "=== Names matching Tehuti / Tehutidata (max depth 4) ==="
for root in /mnt/usb_sda1 "/media/${USER}" "/run/media/${USER}"; do
  [[ -d "$root" ]] || continue
  find "$root" -maxdepth 4 \( -iname '*tehuti*' -o -iname '*tehutidata*' \) 2>/dev/null | head -20
done

echo ""
echo "If MOUNTPOINT is empty for sda1, the disk is not mounted yet — use:" 
echo "  sudo mkdir -p /mnt/usb_sda1 && sudo mount -t ntfs3 /dev/sda1 /mnt/usb_sda1"
