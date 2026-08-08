#!/bin/bash
# Tool Health Monitor
# Maat-Aligned Tool Monitoring System
# Checks all MCP tools and core services every 60 seconds

set -e

MONITOR_DIR="/home/suspect/.n8n/scripts"
STATE_FILE="/tmp/tool-monitor-state.json"
LOG_FILE="/var/log/tehuti-tool-monitor.log"
ALERT_SCRIPT="$MONITOR_DIR/send-discord-alert.sh"
RECOVERY_SCRIPT="$MONITOR_DIR/auto-recover-tool.sh"
GITMAAT_SCRIPT="$MONITOR_DIR/log-to-gitmaat.py"

# Ensure log directory exists
sudo mkdir -p /var/log
sudo touch "$LOG_FILE"
sudo chown suspect:suspect "$LOG_FILE" 2>/dev/null || true

# Initialize state file if it doesn't exist
if [ ! -f "$STATE_FILE" ]; then
    echo '{}' > "$STATE_FILE"
fi

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# MCP Tools to monitor (port, service_name, tool_name)
declare -a TOOLS=(
    "8011:mcpo-tehuti-curriculum:Tehuti Curriculum"
    "8012:mcpo-tehuti-research:Tehuti Research"
    "8013:mcpo-tehuti-integration:Tehuti Integration"
    "8014:mcpo-tehuti-core:Tehuti Core"
    "8015:mcpo-n8n-mcp:n8n MCP"
    "8016:mcpo-filesystem:Filesystem MCP"
    "8017:mcpo-postgres:Postgres MCP"
    "8018:mcpo-memory:Memory MCP"
    "8019:mcpo-comfyui-intelligent:ComfyUI Intelligent"
    "8020:mcpo-maatlangchain-pipeline:MaatLangChain Pipeline"
    "8021:mcpo-tehuti-audio:Tehuti Audio"
)

# Core services to monitor
declare -a CORE_SERVICES=(
    "n8n:n8n"
    "comfyui:ComfyUI"
    "open-webui:Open WebUI"
    "postgresql:PostgreSQL"
)

check_tool() {
    local port=$1
    local service_name=$2
    local tool_name=$3
    
    # Check HTTP endpoint
    local http_status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://127.0.0.1:$port/openapi.json 2>/dev/null || echo "000")
    
    # Check service status
    local service_status="unknown"
    if systemctl is-active --quiet "$service_name.service" 2>/dev/null; then
        service_status="active"
    elif systemctl is-failed --quiet "$service_name.service" 2>/dev/null; then
        service_status="failed"
    else
        service_status="inactive"
    fi
    
    # Determine overall status
    local status="healthy"
    if [ "$http_status" != "200" ] || [ "$service_status" != "active" ]; then
        status="unhealthy"
    fi
    
    echo "$status|$http_status|$service_status"
}

check_core_service() {
    local service_name=$1
    local service_display=$2
    
    if systemctl is-active --quiet "$service_name.service" 2>/dev/null; then
        echo "healthy|active"
    elif systemctl is-failed --quiet "$service_name.service" 2>/dev/null; then
        echo "unhealthy|failed"
    else
        echo "unhealthy|inactive"
    fi
}

update_state() {
    local tool_id=$1
    local status=$2
    local timestamp=$(date +%s)
    
    # Read current state
    local state=$(cat "$STATE_FILE" 2>/dev/null || echo '{}')
    
    # Update state using Python for JSON manipulation
    python3 <<EOF
import json
import sys
from datetime import datetime

state_file = "$STATE_FILE"
tool_id = "$tool_id"
status = "$status"
timestamp = $timestamp

try:
    with open(state_file, 'r') as f:
        state = json.load(f)
except:
    state = {}

if tool_id not in state:
    state[tool_id] = {
        "consecutive_failures": 0,
        "last_status": "unknown",
        "last_check": 0,
        "last_alert": 0,
        "restart_attempts": []
    }

old_status = state[tool_id]["last_status"]
state[tool_id]["last_check"] = timestamp
state[tool_id]["last_status"] = status

if status == "unhealthy":
    state[tool_id]["consecutive_failures"] += 1
else:
    if old_status == "unhealthy":
        # Tool recovered
        state[tool_id]["consecutive_failures"] = 0
        state[tool_id]["recovered_at"] = timestamp
    else:
        state[tool_id]["consecutive_failures"] = 0

with open(state_file, 'w') as f:
    json.dump(state, f, indent=2)
EOF
}

get_state() {
    local tool_id=$1
    local key=$2
    
    python3 <<EOF
import json
import sys

state_file = "$STATE_FILE"
tool_id = "$tool_id"
key = "$key"

try:
    with open(state_file, 'r') as f:
        state = json.load(f)
    if tool_id in state and key in state[tool_id]:
        print(state[tool_id][key])
    else:
        print("0")
except:
    print("0")
EOF
}

# Main monitoring loop
log "Starting tool monitor..."

while true; do
    # Check MCP tools
    for tool_info in "${TOOLS[@]}"; do
        IFS=':' read -r port service_name tool_name <<< "$tool_info"
        tool_id="${service_name}"
        
        result=$(check_tool "$port" "$service_name" "$tool_name")
        IFS='|' read -r status http_status service_status <<< "$result"
        
        update_state "$tool_id" "$status"
        consecutive_failures=$(get_state "$tool_id" "consecutive_failures")
        
        if [ "$status" = "unhealthy" ]; then
            log "❌ $tool_name (port $port): HTTP=$http_status, Service=$service_status, Failures=$consecutive_failures"
            
            # Send alert if needed (rate limited)
            last_alert=$(get_state "$tool_id" "last_alert")
            current_time=$(date +%s)
            if [ $((current_time - last_alert)) -gt 300 ]; then  # 5 minutes
                if [ -f "$ALERT_SCRIPT" ]; then
                    "$ALERT_SCRIPT" "$tool_name" "$port" "$http_status" "$service_status" "$consecutive_failures"
                fi
                python3 <<EOF
import json
state_file = "$STATE_FILE"
tool_id = "$tool_id"
with open(state_file, 'r') as f:
    state = json.load(f)
state[tool_id]["last_alert"] = $current_time
with open(state_file, 'w') as f:
    json.dump(state, f, indent=2)
EOF
            fi
            
            # Log to gitMaat
            if [ -f "$GITMAAT_SCRIPT" ]; then
                python3 "$GITMAAT_SCRIPT" "tool_down" "$tool_id" "$tool_name" "$port" "$http_status" "$service_status" "$consecutive_failures" 2>/dev/null || true
            fi
            
            # Attempt recovery for transient failures
            if [ "$consecutive_failures" -le 2 ] && [ -f "$RECOVERY_SCRIPT" ]; then
                log "🔄 Attempting auto-recovery for $tool_name..."
                "$RECOVERY_SCRIPT" "$service_name" "$tool_name" "$consecutive_failures" 2>&1 | tee -a "$LOG_FILE"
            fi
        else
            # Check if tool just recovered
            last_status=$(get_state "$tool_id" "last_status")
            if [ "$last_status" = "unhealthy" ]; then
                log "✅ $tool_name (port $port): Recovered!"
                
                # Log recovery to gitMaat
                if [ -f "$GITMAAT_SCRIPT" ]; then
                    python3 "$GITMAAT_SCRIPT" "tool_recovered" "$tool_id" "$tool_name" "$port" 2>/dev/null || true
                fi
            fi
        fi
    done
    
    # Check core services
    for service_info in "${CORE_SERVICES[@]}"; do
        IFS=':' read -r service_name service_display <<< "$service_info"
        service_id="core_${service_name}"
        
        result=$(check_core_service "$service_name" "$service_display")
        IFS='|' read -r status service_status <<< "$result"
        
        update_state "$service_id" "$status"
        consecutive_failures=$(get_state "$service_id" "consecutive_failures")
        
        if [ "$status" = "unhealthy" ]; then
            log "❌ $service_display: Service=$service_status, Failures=$consecutive_failures"
            
            # Send alert
            last_alert=$(get_state "$service_id" "last_alert")
            current_time=$(date +%s)
            if [ $((current_time - last_alert)) -gt 300 ]; then
                if [ -f "$ALERT_SCRIPT" ]; then
                    "$ALERT_SCRIPT" "$service_display" "N/A" "N/A" "$service_status" "$consecutive_failures"
                fi
            fi
        fi
    done
    
    # Wait 60 seconds before next check
    sleep 60
done

