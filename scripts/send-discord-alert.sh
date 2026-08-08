#!/bin/bash
# Send Discord Webhook Alert
# Maat-Aligned Alerting System

set -e

WEBHOOK_URL="https://discord.com/api/webhooks/1450617709917372441/kRJGaERLtm_cwzYwFTh0Vk3Wch798ykZV_QHnpJ7IkpLmvbsGd4PKbODEJ3tnlDE10Ao"

TOOL_NAME="${1:-Unknown Tool}"
PORT="${2:-N/A}"
HTTP_STATUS="${3:-N/A}"
SERVICE_STATUS="${4:-unknown}"
CONSECUTIVE_FAILURES="${5:-0}"

# Determine color based on severity
if [ "$CONSECUTIVE_FAILURES" -ge 3 ]; then
    COLOR=15158332  # Red - Critical
    SEVERITY="🔴 CRITICAL"
elif [ "$CONSECUTIVE_FAILURES" -ge 2 ]; then
    COLOR=15105570  # Orange - Warning
    SEVERITY="🟠 WARNING"
else
    COLOR=3447003   # Blue - Info
    SEVERITY="🔵 INFO"
fi

# Create embed message
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
HOSTNAME=$(hostname)

# Build description
DESCRIPTION="**Tool Status Alert**\n\n"
DESCRIPTION+="**Tool:** $TOOL_NAME\n"
if [ "$PORT" != "N/A" ]; then
    DESCRIPTION+="**Port:** $PORT\n"
fi
DESCRIPTION+="**HTTP Status:** $HTTP_STATUS\n"
DESCRIPTION+="**Service Status:** $SERVICE_STATUS\n"
DESCRIPTION+="**Consecutive Failures:** $CONSECUTIVE_FAILURES\n"
DESCRIPTION+="**Host:** $HOSTNAME\n"
DESCRIPTION+="**Time:** $(date '+%Y-%m-%d %H:%M:%S UTC')"

# Create JSON payload
JSON_PAYLOAD=$(cat <<EOF
{
  "embeds": [{
    "title": "$SEVERITY - Tool Failure Detected",
    "description": "$DESCRIPTION",
    "color": $COLOR,
    "timestamp": "$TIMESTAMP",
    "footer": {
      "text": "Tehuti Lab Tool Monitor - Maat-Aligned"
    },
    "fields": [
      {
        "name": "Status",
        "value": "Unhealthy",
        "inline": true
      },
      {
        "name": "Failures",
        "value": "$CONSECUTIVE_FAILURES consecutive",
        "inline": true
      }
    ]
  }]
}
EOF
)

# Send to Discord
curl -s -H "Content-Type: application/json" \
    -d "$JSON_PAYLOAD" \
    "$WEBHOOK_URL" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Discord alert sent for $TOOL_NAME"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Failed to send Discord alert for $TOOL_NAME" >&2
fi

