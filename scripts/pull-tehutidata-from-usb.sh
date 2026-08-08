#!/usr/bin/env bash
# Copy UKMT Tehuti dataset from a mounted volume into ~/.n8n/
#
# 1) Mount the external disk (example for NTFS on /dev/sda1):
#    sudo mkdir -p /mnt/usb_sda1
#    sudo mount -t ntfs3 -o uid="$(id -u)",gid="$(id -g)",umask=022 /dev/sda1 /mnt/usb_sda1
#    # or: sudo mount -t ntfs-3g ...
#
# 2) Run this script (pass mount point, or let it search):
#    ./scripts/pull-tehutidata-from-usb.sh /mnt/usb_sda1
#    ./scripts/pull-tehutidata-from-usb.sh /mnt/usb_sda1 --force   # replace ukmt-rbg-dataset
#
# Windows path D:\Tehuti-Dataset → after mounting the drive, that folder appears as
#   <mountpoint>/Tehuti-Dataset
# (same data; Linux has no D:).
#
# Produces:  ~/.n8n/data/tehuti/ukmt-rbg-dataset  (Tehuti-Dataset or Tehutidata.db from USB)

set -euo pipefail

ROOT="${HOME}/.n8n"
DEST="${ROOT}/data/tehuti/ukmt-rbg-dataset"

FORCE=false
ARGS=()
for a in "$@"; do
  if [[ "$a" == "--force" ]]; then
    FORCE=true
  else
    ARGS+=("$a")
  fi
done
set -- "${ARGS[@]}"

search_roots=()
if [[ "${1:-}" ]]; then
  if [[ ! -d "$1" ]]; then
    echo "error: not a directory (or it does not exist yet): $1" >&2
    echo >&2
    echo "If this was meant to be the USB disk: it must be mounted first." >&2
    echo "Example (NTFS on /dev/sda1, label WINSERVER2019):" >&2
    echo "  sudo mkdir -p /mnt/usb_sda1" >&2
    echo "  sudo mount -t ntfs3 -o uid=\$(id -u),gid=\$(id -g),umask=022 /dev/sda1 /mnt/usb_sda1" >&2
    echo "  ls /mnt/usb_sda1" >&2
    echo "Then run: $0 /mnt/usb_sda1" >&2
    echo "Or try: ~/.n8n/scripts/show-tehuti-mount-hints.sh" >&2
    exit 1
  fi
  search_roots+=("$1")
else
  for p in /mnt/usb_sda1 /media/"${USER}"/WINSERVER2019; do
    [[ -e "$p" ]] && search_roots+=("$p")
  done
  if [[ -d /media/${USER} ]]; then
    for p in /media/"${USER}"/*; do
      [[ -e "$p" ]] && search_roots+=("$p")
    done
  fi
  if [[ -d /run/media/${USER} ]]; then
    for p in /run/media/"${USER}"/*; do
      [[ -e "$p" ]] && search_roots+=("$p")
    done
  fi
fi

find_tehuti() {
  local root="$1"
  # Prefer Tehuti-Dataset (UKMT) when both it and Tehutidata.db exist on the volume.
  local hit
  hit=$(find "$root" -maxdepth 8 \( -name 'Tehuti-Dataset' -o -name 'tehuti-dataset' \) 2>/dev/null | head -1)
  if [[ -n "$hit" ]]; then
    echo "$hit"
    return
  fi
  find "$root" -maxdepth 8 \( \
    -name 'Tehutidata.db' -o -name 'TehutiData.db' -o -name 'tehutidata.db' \
    \) 2>/dev/null | head -1
}

SRC=""
for r in "${search_roots[@]}"; do
  [[ -d "$r" ]] || continue
  SRC=$(find_tehuti "$r")
  [[ -n "$SRC" ]] && break
done

if [[ -z "${SRC:-}" ]]; then
  echo "Could not find Tehutidata.db or Tehuti-Dataset under:" >&2
  printf '  %s\n' "${search_roots[@]}" >&2
  echo >&2
  echo "Mount the external drive, then run:" >&2
  echo "  $0 /path/to/mount" >&2
  exit 1
fi

if [[ -e "$DEST" ]]; then
  if [[ "$FORCE" == true ]]; then
    echo "Removing existing $DEST (--force)"
    rm -rf -- "$DEST"
  else
    echo "Destination already exists: $DEST" >&2
    echo "Remove or rename it first, or re-run with:  $0 ${1:-/mnt/usb_sda1} --force" >&2
    exit 1
  fi
fi

echo "Source: $SRC"
echo "Dest:   $DEST"
mkdir -p "${ROOT}/data/tehuti"
cp -a -- "$SRC" "$DEST"
echo "Done."
