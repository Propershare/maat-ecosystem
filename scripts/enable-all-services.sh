#!/bin/bash
# Verify and enable all Tehuti Lab services on boot
# Maat-Aligned Service Management

set -e

echo "🔍 Checking Tehuti Lab services auto-start status..."
echo ""

# All MCP servers
MCP_SERVICES=(
    "mcpo-tehuti-core"
    "mcpo-tehuti-curriculum"
    "mcpo-tehuti-research"
    "mcpo-tehuti-integration"
    "mcpo-n8n-mcp"
    "mcpo-filesystem"
    "mcpo-postgres"
    "mcpo-memory"
    "mcpo-comfyui-intelligent"
    "mcpo-maatlangchain-pipeline"
    "mcpo-tehuti-audio"
)

# Core services
CORE_SERVICES=(
    "n8n"
    "comfyui"
    "open-webui"
    "postgresql"
)

# LDAP service (needs installation)
LDAP_SERVICE="tehuti-ldap"
LDAP_SOURCE="/home/suspect/.n8n/tehuti-ldap/systemd/tehuti-ldap.service"

# Check MCP services
echo "📋 MCP Servers:"
for service in "${MCP_SERVICES[@]}"; do
    if systemctl list-unit-files | grep -q "^${service}.service"; then
        status=$(systemctl is-enabled ${service}.service 2>/dev/null || echo "disabled")
        if [ "$status" = "enabled" ]; then
            echo "  ✅ $service: enabled"
        else
            echo "  ❌ $service: disabled"
            echo "     Enabling..."
            sudo systemctl enable ${service}.service 2>/dev/null && echo "     ✅ Enabled" || echo "     ⚠️  Failed"
        fi
    else
        echo "  ⚠️  $service: service file not found"
    fi
done

echo ""
echo "📋 Core Services:"
for service in "${CORE_SERVICES[@]}"; do
    if systemctl list-unit-files | grep -q "^${service}.service"; then
        status=$(systemctl is-enabled ${service}.service 2>/dev/null || echo "disabled")
        if [ "$status" = "enabled" ]; then
            echo "  ✅ $service: enabled"
        else
            echo "  ❌ $service: disabled"
            echo "     Enabling..."
            sudo systemctl enable ${service}.service 2>/dev/null && echo "     ✅ Enabled" || echo "     ⚠️  Failed"
        fi
    else
        echo "  ⚠️  $service: service file not found"
    fi
done

echo ""
echo "📋 LDAP Service:"
if [ -f "/etc/systemd/system/${LDAP_SERVICE}.service" ]; then
    status=$(systemctl is-enabled ${LDAP_SERVICE}.service 2>/dev/null || echo "disabled")
    if [ "$status" = "enabled" ]; then
        echo "  ✅ $LDAP_SERVICE: enabled"
    else
        echo "  ❌ $LDAP_SERVICE: installed but not enabled"
        echo "     Enabling..."
        sudo systemctl enable ${LDAP_SERVICE}.service 2>/dev/null && echo "     ✅ Enabled" || echo "     ⚠️  Failed"
    fi
elif [ -f "$LDAP_SOURCE" ]; then
    echo "  ⚠️  $LDAP_SERVICE: service file exists but not installed"
    echo "     Installing..."
    sudo cp "$LDAP_SOURCE" "/etc/systemd/system/${LDAP_SERVICE}.service"
    sudo systemctl daemon-reload
    sudo systemctl enable ${LDAP_SERVICE}.service 2>/dev/null && echo "     ✅ Installed and enabled" || echo "     ⚠️  Failed"
else
    echo "  ⚠️  $LDAP_SERVICE: service file not found at $LDAP_SOURCE"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Count enabled services
ENABLED_COUNT=0
TOTAL_COUNT=0

for service in "${MCP_SERVICES[@]}" "${CORE_SERVICES[@]}"; do
    if systemctl list-unit-files | grep -q "^${service}.service"; then
        TOTAL_COUNT=$((TOTAL_COUNT + 1))
        if systemctl is-enabled ${service}.service >/dev/null 2>&1; then
            ENABLED_COUNT=$((ENABLED_COUNT + 1))
        fi
    fi
done

# Check LDAP
if [ -f "/etc/systemd/system/${LDAP_SERVICE}.service" ]; then
    TOTAL_COUNT=$((TOTAL_COUNT + 1))
    if systemctl is-enabled ${LDAP_SERVICE}.service >/dev/null 2>&1; then
        ENABLED_COUNT=$((ENABLED_COUNT + 1))
    fi
fi

echo "Enabled: $ENABLED_COUNT / $TOTAL_COUNT services"
echo ""

if [ $ENABLED_COUNT -eq $TOTAL_COUNT ]; then
    echo "✅ All services are enabled for auto-start on boot!"
else
    echo "⚠️  Some services are not enabled. They will NOT start automatically on reboot."
    echo ""
    echo "To manually enable remaining services:"
    echo "  sudo systemctl enable <service-name>.service"
fi

echo ""
echo "📋 To verify all services will start on boot:"
echo "  systemctl list-unit-files | grep -E '(mcp|n8n|comfyui|open-webui|ldap)' | grep enabled"

