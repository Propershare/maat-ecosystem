#!/bin/bash
# Setup systemd service for Tehuti Lab WebUI

SERVICE_FILE="/etc/systemd/system/tehuti-lab-webui.service"
VENV_PATH="/home/suspect/.n8n/tehuti-lab-webui-venv"
WORK_DIR="/home/suspect/.n8n/tehuti-lab-webui"

# Create service file
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Tehuti Lab WebUI
After=network.target ollama.service

[Service]
Type=simple
User=suspect
WorkingDirectory=$WORK_DIR
Environment="PATH=$VENV_PATH/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=$WORK_DIR/backend"
Environment="OLLAMA_BASE_URL=http://127.0.0.1:11434"
Environment="WEBUI_URL=https://ai.suspecttv.com"
Environment="ENABLE_SIGNUP=true"
Environment="DEFAULT_USER_ROLE=user"
ExecStart=$VENV_PATH/bin/open-webui serve --host 0.0.0.0 --port 3000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

echo "✅ Service configured: $SERVICE_FILE"
echo "To start: sudo systemctl start tehuti-lab-webui"
echo "To enable: sudo systemctl enable tehuti-lab-webui"

