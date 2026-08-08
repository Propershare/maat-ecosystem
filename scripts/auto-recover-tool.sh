#!/bin/bash
# Auto-Recovery Script for Failed Tools
# Maat-Aligned Smart Recovery System

set -e

SERVICE_NAME="${1}"
TOOL_NAME="${2}"
CONSECUTIVE_FAILURES="${3:-0}"
STATE_FILE="/tmp/tool-monitor-state.json"
GITMAAT_SCRIPT="/home/suspect/.n8n/scripts/log-to-gitmaat.py"

# Rate limiting: Max 3 restart attempts per hour per tool
MAX_RESTARTS_PER_HOUR=3
RESTART_WINDOW=3600  # 1 hour in seconds

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

check_restart_rate_limit() {
    local service_name=$1
    
    python3 <<EOF
import json
import time
import sys

state_file = "$STATE_FILE"
service_name = "$service_name"
max_restarts = $MAX_RESTARTS_PER_HOUR
window = $RESTART_WINDOW
current_time = int(time.time())

try:
    with open(state_file, 'r') as f:
        state = json.load(f)
except:
    state = {}

if service_name not in state:
    state[service_name] = {"restart_attempts": []}

restart_attempts = state[service_name].get("restart_attempts", [])
# Remove attempts outside the window
restart_attempts = [t for t in restart_attempts if current_time - t < window]

if len(restart_attempts) >= max_restarts:
    print("RATE_LIMITED")
    sys.exit(1)
else:
    # Add current attempt
    restart_attempts.append(current_time)
    state[service_name]["restart_attempts"] = restart_attempts
    
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
    
    print("ALLOWED")
EOF
}

# Only attempt recovery for transient failures (1-2 consecutive)
if [ "$CONSECUTIVE_FAILURES" -gt 2 ]; then
    log "⚠️  $TOOL_NAME: Persistent failure ($CONSECUTIVE_FAILURES consecutive). Manual intervention required."
    exit 0
fi

# Check rate limit
if ! check_restart_rate_limit "$SERVICE_NAME" 2>/dev/null; then
    log "⚠️  $TOOL_NAME: Rate limit exceeded. Max $MAX_RESTARTS_PER_HOUR restarts per hour."
    exit 0
fi

log "🔄 Attempting to restart $TOOL_NAME (service: $SERVICE_NAME)..."

# Log restart attempt to gitMaat
if [ -f "$GITMAAT_SCRIPT" ]; then
    python3 "$GITMAAT_SCRIPT" "tool_restart_attempted" "$SERVICE_NAME" "$TOOL_NAME" "N/A" "N/A" "restarting" "$CONSECUTIVE_FAILURES" 2>/dev/null || true
fi

# Attempt to restart service
if sudo systemctl restart "${SERVICE_NAME}.service" 2>/dev/null; then
    log "✅ Restart command sent for $TOOL_NAME"
    
    # Wait a bit for service to start
    sleep 5
    
    # Check if service is now active
    if systemctl is-active --quiet "${SERVICE_NAME}.service" 2>/dev/null; then
        log "✅ $TOOL_NAME restarted successfully"
        
        # Wait a bit more and check if tool responds
        sleep 3
        
        # Try to get port from service name (basic mapping)
        PORT=""
        case "$SERVICE_NAME" in
            mcpo-tehuti-core) PORT="8014" ;;
            mcpo-tehuti-curriculum) PORT="8011" ;;
            mcpo-tehuti-research) PORT="8012" ;;
            mcpo-tehuti-integration) PORT="8013" ;;
            mcpo-n8n-mcp) PORT="8015" ;;
            mcpo-filesystem) PORT="8016" ;;
            mcpo-postgres) PORT="8017" ;;
            mcpo-memory) PORT="8018" ;;
            mcpo-comfyui-intelligent) PORT="8019" ;;
            mcpo-maatlangchain-pipeline) PORT="8020" ;;
            mcpo-tehuti-audio) PORT="8021" ;;
        esac
        
        if [ -n "$PORT" ]; then
            HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://127.0.0.1:$PORT/openapi.json 2>/dev/null || echo "000")
            if [ "$HTTP_STATUS" = "200" ]; then
                log "✅ $TOOL_NAME (port $PORT) is responding after restart"
            else
                log "⚠️  $TOOL_NAME (port $PORT) restarted but not responding yet (HTTP: $HTTP_STATUS)"
            fi
        fi
        
        exit 0
    else
        log "❌ $TOOL_NAME restart failed - service not active"
        exit 1
    fi
else
    log "❌ Failed to restart $TOOL_NAME - check service status manually"
    exit 1
fi

