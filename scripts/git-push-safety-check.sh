#!/usr/bin/env bash
# Fail if staged files match known high-risk patterns (run before commit/push).
# Usage: ./scripts/git-push-safety-check.sh
set -euo pipefail

cd "$(dirname "$0")/.."

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "git-push-safety-check: not a git repository; skip."
  exit 0
fi

mapfile -t STAGED < <(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || true)

if [[ ${#STAGED[@]} -eq 0 ]]; then
  echo "git-push-safety-check: no staged files — OK."
  exit 0
fi

BAD=()
for f in "${STAGED[@]}"; do
  base=$(basename "$f")

  # Env files: allow only .env.example (template)
  if [[ "$base" == .env.example ]]; then
    :
  elif [[ "$base" == .env ]] || [[ "$base" == .env.* ]]; then
    BAD+=("$f")
  fi

  case "$base" in
    .webui_secret_key|.ka-auth)
      BAD+=("$f")
      ;;
  esac

  case "$f" in
    *.pem|*.p12)
      BAD+=("$f")
      ;;
  esac

  case "$f" in
    MEMORY.md|USER.md|SOUL.md|SSH-CREDENTIALS.md)
      BAD+=("$f")
      ;;
    memory|memory/*)
      BAD+=("$f")
      ;;
  esac
done

if [[ ${#BAD[@]} -gt 0 ]]; then
  echo "git-push-safety-check: BLOCKED — staged files match push-risk list:"
  printf '  %s\n' "${BAD[@]}" | sort -u
  echo "Remove from index: git reset HEAD -- <path>  (or unstage all) and use .gitignore + .example templates."
  echo "See docs/PUSH-SAFETY.md"
  exit 1
fi

echo "git-push-safety-check: staged paths OK (${#STAGED[@]} file(s))."
exit 0
