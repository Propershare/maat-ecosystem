#!/usr/bin/env bash
# Read-only disk snapshot for Tehuti Lab: major paths + df + optional DB/Ollama hints.
# Ends with a === SUMMARY === block suitable for pasting into gitMaat / memory.
# Usage: ./scripts/lab-storage-audit.sh
#        LAB_ROOT=/path/to/lab ./scripts/lab-storage-audit.sh
#        FULL=1 ./scripts/lab-storage-audit.sh   # include huge dirs (pdf-library, openclaw/node_modules); slow
set -euo pipefail

ROOT="${LAB_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
FULL="${FULL:-0}"
DISK_WARN_PCT="${DISK_WARN_PCT:-85}"

SUMMARY_TMP=$(mktemp)
trap 'rm -f "$SUMMARY_TMP"' EXIT

PG_SIZE_PRETTY=""
PG_SIZE_BYTES=""
KB_PGDATA=""

append_kb() {
  local kb="$1"
  local label="$2"
  local path="$3"
  [[ -n "$kb" ]] && [[ "$kb" =~ ^[0-9]+$ ]] && echo -e "${kb}\t${label}\t${path}" >>"$SUMMARY_TMP"
}

# du -sk with timeout; returns kb on stdout or empty
du_sk_kb() {
  local p="$1"
  [[ -e "$p" ]] || return 1
  if command -v timeout >/dev/null 2>&1; then
    timeout 45 du -sk "$p" 2>/dev/null | awk '{print $1}'
  else
    du -sk "$p" 2>/dev/null | awk '{print $1}'
  fi
}

human_kb() {
  local k="$1"
  awk -v k="$k" 'BEGIN {
    # k is size in KB (du -sk units)
    if (k >= 1073741824) { printf "%.2fT", k/1073741824; exit }
    if (k >= 1048576) { printf "%.2fG", k/1048576; exit }
    if (k >= 1024) { printf "%.1fM", k/1024; exit }
    printf "%dK", k
  }'
}

echo "=== Lab storage audit ==="
echo "LAB_ROOT=${ROOT}"
echo "FULL=${FULL} (set FULL=1 to measure pdf-library + openclaw/node_modules)"
echo "Date: $(date -Iseconds 2>/dev/null || date)"
echo "Host: $(hostname 2>/dev/null || echo unknown)"
echo ""

du_line() {
  local p="$1"
  local label="$2"
  if [[ ! -e "$p" ]]; then
    echo -e "(missing)\t${label}"
    return
  fi
  local kb
  kb=$(du_sk_kb "$p") || kb=""
  if [[ -z "$kb" ]]; then
    echo -e "(slow or timeout)\t${label} — run: du -sh \"$p\""
    return
  fi
  append_kb "$kb" "$label" "$p"
  local hum
  hum=$(human_kb "$kb")
  echo -e "${hum}\t${label} (${p})"
}

echo "--- Key paths under LAB_ROOT ---"
du_line "$ROOT/data/tehuti/ukmt-rbg-dataset" "Tehuti UKMT/RBG text"
if [[ "$FULL" == "1" ]]; then
  du_line "$ROOT/data/tehuti/pdf-library" "Tehuti PDF library"
else
  if [[ -d "$ROOT/data/tehuti/pdf-library" ]]; then
    echo -e "(skipped)\tTehuti PDF library — set FULL=1 (large tree)"
  else
    echo -e "(missing)\tTehuti PDF library"
  fi
fi
du_line "$ROOT/data/tehuti/archives" "Tehuti archives"
du_line "$ROOT/chroma_db_maat" "Chroma (if present)"
du_line "$ROOT/models" "models/ (if present)"
du_line "$ROOT/fine-tuned-models" "fine-tuned-models/"
if [[ "$FULL" == "1" ]]; then
  du_line "$ROOT/openclaw/node_modules" "openclaw node_modules"
else
  if [[ -d "$ROOT/openclaw/node_modules" ]]; then
    echo -e "(skipped)\topenclaw/node_modules — set FULL=1"
  else
    echo -e "(missing)\topenclaw/node_modules"
  fi
fi
du_line "$ROOT/.venv" "repo .venv"
du_line "$ROOT/tehuti-lab-webui-venv" "tehuti-lab-webui-venv"
du_line "$ROOT/maatlangchain/.venv" "maatlangchain .venv"

echo ""
echo "--- Filesystem (df -h) ---"
DF_LINE=$(df -P -h "$ROOT" 2>/dev/null | tail -1 || df -P -h / | tail -1)
echo "$DF_LINE"
USE_PCT=""
USE_PCT=$(echo "$DF_LINE" | awk '{gsub(/%/,"",$5); print $5}')
# Fallback: parse df without -P
if [[ -z "$USE_PCT" ]] || ! [[ "$USE_PCT" =~ ^[0-9]+$ ]]; then
  USE_PCT=$(df "$ROOT" 2>/dev/null | tail -1 | awk '{print $5}' | tr -d '%' || echo "")
fi

# Optional: system Postgres data dir can be huge and slow to du — SHOW_PG_DATA=1
if [[ "${SHOW_PG_DATA:-0}" == "1" ]] && [[ -d /var/lib/postgresql ]]; then
  echo ""
  echo "--- Postgres data dir (SHOW_PG_DATA=1) ---"
  kb_pgdata=$(du_sk_kb /var/lib/postgresql || true)
  KB_PGDATA="${kb_pgdata:-}"
  if [[ -n "${kb_pgdata:-}" ]]; then
    append_kb "$kb_pgdata" "Postgres PGDATA on-disk (du, not logical DB size)" "/var/lib/postgresql"
    echo "$(human_kb "$kb_pgdata")	(/var/lib/postgresql)  [PGDATA disk — not pg_database_size]"
  else
    du -sh /var/lib/postgresql 2>/dev/null || true
  fi
fi

echo ""
echo "--- Ollama models (~/.ollama) ---"
if [[ -d "${HOME}/.ollama" ]]; then
  kb_ollama=$(du_sk_kb "${HOME}/.ollama" || true)
  if [[ -n "${kb_ollama:-}" ]]; then
    append_kb "$kb_ollama" "Ollama ~/.ollama" "${HOME}/.ollama"
    echo "$(human_kb "$kb_ollama")	${HOME}/.ollama"
  else
    du -sh "${HOME}/.ollama" 2>/dev/null || true
  fi
else
  echo "(no ~/.ollama on this host)"
fi

echo ""
echo "--- Postgres DB size (if psql + PGVECTOR_DB_URL) ---"
if command -v psql >/dev/null 2>&1; then
  _psql_size() {
    local url="$1"
    if command -v timeout >/dev/null 2>&1; then
      timeout 20 psql "$url" -At -c "SELECT pg_size_pretty(pg_database_size(current_database()));" 2>/dev/null
    else
      psql "$url" -At -c "SELECT pg_size_pretty(pg_database_size(current_database()));" 2>/dev/null
    fi
  }
  _psql_bytes() {
    local url="$1"
    if command -v timeout >/dev/null 2>&1; then
      timeout 20 psql "$url" -At -c "SELECT pg_database_size(current_database());" 2>/dev/null
    else
      psql "$url" -At -c "SELECT pg_database_size(current_database());" 2>/dev/null
    fi
  }
  if [[ -n "${PGVECTOR_DB_URL:-}" ]]; then
    PG_SIZE_PRETTY=$(_psql_size "$PGVECTOR_DB_URL" || true)
    PG_SIZE_BYTES=$(_psql_bytes "$PGVECTOR_DB_URL" || true)
    if [[ -n "$PG_SIZE_PRETTY" ]]; then
      echo "  maat_memory DB: $PG_SIZE_PRETTY"
      if [[ -n "$PG_SIZE_BYTES" ]] && [[ "$PG_SIZE_BYTES" =~ ^[0-9]+$ ]]; then
        # bytes -> KB for consistent top-N (1K blocks)
        kb_pg=$((PG_SIZE_BYTES / 1024))
        append_kb "$kb_pg" "Postgres logical DB (pg_database_size, not PGDATA disk)" "pg:maat_memory"
      fi
    else
      echo "  (psql failed or timeout — check PGVECTOR_DB_URL)"
    fi
  elif [[ -f "$ROOT/.env" ]]; then
    # shellcheck disable=SC1090
    set -a && source "$ROOT/.env" && set +a
    if [[ -n "${PGVECTOR_DB_URL:-}" ]]; then
      PG_SIZE_PRETTY=$(_psql_size "$PGVECTOR_DB_URL" || true)
      PG_SIZE_BYTES=$(_psql_bytes "$PGVECTOR_DB_URL" || true)
      if [[ -n "$PG_SIZE_PRETTY" ]]; then
        echo "  maat_memory DB: $PG_SIZE_PRETTY"
        if [[ -n "$PG_SIZE_BYTES" ]] && [[ "$PG_SIZE_BYTES" =~ ^[0-9]+$ ]]; then
          kb_pg=$((PG_SIZE_BYTES / 1024))
          append_kb "$kb_pg" "Postgres logical DB (pg_database_size, not PGDATA disk)" "pg:maat_memory"
        fi
      else
        echo "  (psql failed or timeout after sourcing .env)"
      fi
    else
      echo "  (PGVECTOR_DB_URL not set; source .env manually)"
    fi
  else
    echo "  (no .env at LAB_ROOT; export PGVECTOR_DB_URL to measure DB)"
  fi
else
  echo "  (psql not installed)"
fi

# --- SUMMARY (durable / paste / gitMaat) ---
echo ""
echo "=== SUMMARY (paste / gitMaat / memory) ==="
echo "machine: $(hostname 2>/dev/null || echo unknown)"
echo "date: $(date -Iseconds 2>/dev/null || date)"
echo "lab_root: ${ROOT}"

TOTAL_KB=0
while IFS=$'\t' read -r kb _label _path; do
  [[ "$kb" =~ ^[0-9]+$ ]] || continue
  TOTAL_KB=$((TOTAL_KB + kb))
done <"$SUMMARY_TMP"
echo "paths_in_summary: $(wc -l <"$SUMMARY_TMP" | tr -d ' ')"
echo "total_hot_storage (sum of measured paths, KB): ${TOTAL_KB}"
echo "total_hot_storage (approx): $(human_kb "$TOTAL_KB")"

echo "metric_note: Postgres logical size (pg_database_size) measures the current database bytes inside the cluster; PGDATA on-disk (du /var/lib/postgresql) is the whole data directory — different quantities; do not compare them as equal."
echo "values_note: skipped = not requested (that check was omitted by default or flags); unavailable = requested or applicable but value not obtained (missing tool, URL, path, timeout, or failure)."
echo "top_5_paths_by_size:"
if [[ ! -s "$SUMMARY_TMP" ]]; then
  echo "  (none)"
else
  sort -t $'\t' -k1 -nr "$SUMMARY_TMP" | head -5 | while IFS=$'\t' read -r kb label path; do
    echo "  $(human_kb "$kb")	${label}	${path}"
  done
fi

# Structural lines for paste/gitMaat — always print both keys
if [[ -n "$PG_SIZE_PRETTY" ]]; then
  echo "postgres_db_logical: ${PG_SIZE_PRETTY}"
else
  echo "postgres_db_logical: unavailable"
fi

if [[ "${SHOW_PG_DATA:-0}" == "1" ]]; then
  if [[ -n "${KB_PGDATA:-}" ]] && [[ "$KB_PGDATA" =~ ^[0-9]+$ ]]; then
    echo "postgres_pgdata_disk: $(human_kb "$KB_PGDATA") (du /var/lib/postgresql — cluster dir on disk, not only current DB logical size)"
  else
    echo "postgres_pgdata_disk: unavailable"
  fi
else
  echo "postgres_pgdata_disk: skipped (set SHOW_PG_DATA=1 to measure on-disk PGDATA; still not the same as postgres_db_logical)"
fi

if [[ -n "${USE_PCT:-}" ]] && [[ "$USE_PCT" =~ ^[0-9]+$ ]]; then
  echo "filesystem_use_pct (${ROOT}): ${USE_PCT}%"
  if [[ "$USE_PCT" -ge "$DISK_WARN_PCT" ]]; then
    echo "action: WARN — disk use ${USE_PCT}% >= ${DISK_WARN_PCT}% (DISK_WARN_PCT). Plan prune (models/venvs/old logs), expand disk, or run restore drill to verify backups before crisis."
  else
    echo "action: OK — below warn threshold (${DISK_WARN_PCT}%). Still schedule restore drills; measuring != restoring."
  fi
else
  echo "filesystem_use_pct: (unparsed)"
  echo "action: confirm df manually; treat restore drills as real work, not ceremonial."
fi

echo ""
echo "Done. Append this SUMMARY to memory/ or gitMaat when tracking fleet storage."
exit 0
