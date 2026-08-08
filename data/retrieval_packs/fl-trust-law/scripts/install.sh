#!/usr/bin/env bash
#
# Install / reinstall the fl-trust-law retrieval pack.
#
# Source order (lab root = parent of data/retrieval_packs):
#   1) If Legal_AI_FL/ exists and contains law_data_clean/, rsync it into documents/.
#   2) Else if Legal_AI_FL.rar exists, wipe documents/ and unrar there (legacy).
#
# Idempotent for RAR path (wipes documents/). Folder path does a merge-style
# rsync (same as a fresh copy into empty dir if you rm -rf documents first).
# Prints aggregate sha256; compare to manifest.json -> aggregate_sha256.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACK_ROOT="$(dirname "$HERE")"
LAB_ROOT="$(cd "$PACK_ROOT/../../.." && pwd)"
FOLDER="$LAB_ROOT/Legal_AI_FL"
ARCHIVE="$LAB_ROOT/Legal_AI_FL.rar"
DOCS="$PACK_ROOT/documents"

echo "install: pack=fl-trust-law"
echo "install: lab_root=$LAB_ROOT"
echo "install: docs=$DOCS"

if [[ -d "$FOLDER/law_data_clean" ]]; then
  echo "install: source=folder $FOLDER"
  mkdir -p "$DOCS"
  rsync -a "$FOLDER/" "$DOCS/"
elif [[ -f "$ARCHIVE" ]]; then
  echo "install: source=archive $ARCHIVE"
  if ! command -v unrar >/dev/null 2>&1; then
    echo "error: unrar not installed (sudo apt install unrar)" >&2
    exit 1
  fi
  rm -rf "$DOCS"
  mkdir -p "$DOCS"
  unrar x -inul "$ARCHIVE" "$DOCS/"
  if [[ -d "$DOCS/Legal_AI_FL" ]]; then
    shopt -s dotglob
    mv "$DOCS/Legal_AI_FL/"* "$DOCS/" 2>/dev/null || true
    shopt -u dotglob
    rmdir "$DOCS/Legal_AI_FL" 2>/dev/null || true
  fi
else
  echo "error: neither $FOLDER/law_data_clean nor $ARCHIVE found" >&2
  exit 1
fi

COUNT=$(find "$DOCS" -type f | wc -l)
CHECKSUM=$(cd "$DOCS" && find . -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | awk '{print $1}')

echo "install: files=$COUNT"
echo "install: aggregate_sha256=$CHECKSUM"
echo "install: done"
