#!/bin/bash
# Auto-install and run agent as a systemd service

set -e

AGENT_PATH="/opt/agent_client_dynamic.py"
SERVICE_PATH="/etc/systemd/system/agent-client.service"
PYTHON_BIN="$(which python3)"
USER="$(whoami)"

# Copy agent script to /opt
sudo cp agent_client_dynamic.py "$AGENT_PATH"
sudo chown $USER:$USER "$AGENT_PATH"
sudo chmod 755 "$AGENT_PATH"

# Create systemd service file
sudo tee "$SERVICE_PATH" > /dev/null <<EOF
[Unit]
Description=Python Agent Client
After=network.target

[Service]
Type=simple
ExecStart=$PYTHON_BIN $AGENT_PATH
WorkingDirectory=/opt/
Restart=always
User=$USER

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd, enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable agent-client
sudo systemctl start agent-client

echo "Agent installed and running as a systemd service."
