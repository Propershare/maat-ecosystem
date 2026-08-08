#!/usr/bin/env bash
# opencode-rules pull — sync ~/.opencode-rules/ from the source of truth.
#
# Default source: a sparse checkout of the maat-ecosystem repo at branch
# `opencode-rules`, using only the opencode-rules/ subtree. This means
# `opencode-rules/` lives inside the maat-ecosystem repo (no separate
# repository to maintain) and is automatically fetched whenever you
# clone/pull the parent.
#
# Override with OPENCODE_RULES_SYNC env var to point at a different source:
#   OPENCODE_RULES_SYNC="git::https://github.com/Propershare/maat-ecosystem.git?ref=opencode-rules&path=opencode-rules"
#   OPENCODE_RULES_SYNC="https://example.com/opencode-rules.tar.gz"
#   OPENCODE_RULES_SYNC="rsync::peer-host:/srv/opencode-rules/"
#
# Usage: opencode-rules pull   — fetch and overwrite ~/.opencode-rules/
#        opencode-rules status — show the current sync source + last-pull time
#        opencode-rules edit   — open the source script for editing
#        opencode-rules push   — push local changes back to source (if git)
#        opencode-rules doctor — verify config + connectivity

set -euo pipefail

DEST="${HOME}/.opencode-rules"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# --- Default sync spec (override via OPENCODE_RULES_SYNC env) ---
DEFAULT_SYNC="git::https://github.com/Propershare/maat-ecosystem.git?ref=opencode-rules&path=opencode-rules"
SYNC_SPEC="${OPENCODE_RULES_SYNC:-$DEFAULT_SYNC}"

cmd="${1:-pull}"

case "$cmd" in
  status)
    echo "DEST:        $DEST"
    echo "SYNC_SPEC:   $SYNC_SPEC"
    echo "DEFAULT:     $DEFAULT_SYNC"
    if [ -d "$DEST/.git" ]; then
      echo "DEST is a git repo (last commit: $(git -C "$DEST" log -1 --format='%h %s %ai' 2>/dev/null || echo 'unknown'))"
    elif [ -d "$DEST" ]; then
      echo "DEST exists (not a git repo)"
    else
      echo "DEST does not exist"
    fi
    ;;
  edit)
    exec "${EDITOR:-nano}" "$0"
    ;;
  doctor)
    echo "[doctor] checking $DEST"
    mkdir -p "$DEST"
    case "$SYNC_SPEC" in
      git::*) url="${SYNC_SPEC#git::}"
             repo="${url%%\?*}"
             qs="${url#*\?}"
             ref=$(echo "$qs" | sed -nE 's/.*ref=([^&]+).*/\1/p')
             path=$(echo "$qs" | sed -nE 's/.*path=([^&]+).*/\1/p')
             echo "  repo:    $repo"
             echo "  ref:     ${ref:-HEAD}"
             echo "  path:    $path"
             if command -v git >/dev/null 2>&1; then
               echo "  git:     $(git --version)"
             else
               echo "  git:     NOT INSTALLED"
             fi
             if command -v curl >/dev/null 2>&1; then
               echo "  curl:    $(curl --version | head -1)"
             fi
             if command -v rsync >/dev/null 2>&1; then
               echo "  rsync:   $(rsync --version | head -1)"
             fi
             ;;
      https*) echo "  HTTPS tarball source"
             ;;
      rsync*) echo "  rsync peer source"
             ;;
      *) echo "  unknown source type"; exit 2 ;;
    esac
    ;;
  push)
    if [ ! -d "$DEST/.git" ]; then
      echo "opencode-rules push: $DEST is not a git checkout (need git source)" >&2
      exit 3
    fi
    cd "$DEST"
    git add -A
    if git diff --cached --quiet; then
      echo "[push] no changes"
      exit 0
    fi
    git commit -m "opencode-rules: $(date -Iseconds) sync from $(hostname)"
    # Parse the git:: spec to get the repo URL
    if [[ "$SYNC_SPEC" == git::* ]]; then
      url="${SYNC_SPEC#git::}"
      repo="${url%%\?*}"
      qs="${url#*\?}"
      ref=$(echo "$qs" | sed -nE 's/.*ref=([^&]+).*/\1/p')
      path=$(echo "$qs" | sed -nE 's/.*path=([^&]+).*/\1/p')
      echo "[push] pushing to $repo ref=$ref path=$path"
      git push "$repo" "HEAD:${ref:-main}"
    fi
    ;;
  pull)
    # --- Resolve the source ---
    case "$SYNC_SPEC" in
      git::*)
        url="${SYNC_CMD_git:="${SYNC_SPEC#git::}"}"
        url="${SYNC_SPEC#git::}"
        repo="${url%%\?*}"
        qs="${url#*\?}"
        ref=$(echo "$qs" | sed -nE 's/.*ref=([^&]+).*/\1/p')
        path=$(echo "$qs" | sed -nE 's/.*path=([^&]+).*/\1/p')
        ref="${ref:-main}"
        echo "[pull] git clone (sparse) repo=$repo ref=$ref path=$path"
        git clone --depth 1 --filter=blob:none --sparse --branch "$ref" "$repo" "$TMP/repo"
        git -C "$TMP/repo" sparse-checkout set "$path"
        if [ ! -d "$TMP/repo/$path" ]; then
          echo "[pull] ERROR: sparse checkout path '$path' not found in $repo @ $ref" >&2
          echo "  Has the opencode-rules branch been created and pushed?" >&2
          echo "  Try: opencode-rules doctor" >&2
          exit 4
        fi
        cp -a "$TMP/repo/$path/." "$TMP/rules/"
        ;;
      https*)
        echo "[pull] HTTPS tarball"
        curl -fsSL "$SYNC_SPEC" | tar -xz -C "$TMP"
        ;;
      rsync*)
        src="${SYNC_SPEC#rsync::}"
        echo "[pull] rsync from $src"
        rsync -a --delete "$src" "$TMP/rules/"
        ;;
      *)
        echo "opencode-rules pull: unknown sync spec: $SYNC_SPEC" >&2
        echo "  Supported: git::URL?ref=X&path=Y | https://... | rsync::user@host:path" >&2
        exit 2
        ;;
    esac

    if [ ! -d "$TMP/rules" ]; then
      echo "opencode-rules pull: fetch did not produce a rules/ dir." >&2
      exit 3
    fi

    # Atomic-ish swap into $DEST
    mkdir -p "$DEST"
    rm -rf "$DEST.new"
    cp -a "$TMP/rules/." "$DEST.new/"
    mv "$DEST.new" "$DEST"

    echo "[pull] installed to $DEST:"
    ls -la "$DEST" | head -15
    echo
    echo "Restart opencode to pick up changes."
    ;;
  *)
    echo "Usage: opencode-rules {pull|status|push|doctor|edit}" >&2
    exit 1
    ;;
esac
