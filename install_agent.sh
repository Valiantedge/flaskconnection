#!/bin/bash
# Auto-install and run agent as a systemd service

set -e

AGENT_PATH="/opt/client_agent.py"
SERVICE_PATH="/etc/systemd/system/agent-client.service"
PYTHON_BIN="$(which python3)"
USER="$(whoami)"


# Download agent script from your Apache server
AGENT_URL="https://socket.valiantedgetech.com/client_agent.py"
sudo curl -fsSL "$AGENT_URL" -o "$AGENT_PATH"
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

#!/bin/bash
# Universal installer for Python agent client
set -e


AGENT_PATH="/opt/client_agent.py"
VENV_PATH="/opt/agent-venv"
SERVICE_PATH="/etc/systemd/system/agent-client.service"
USER="$(whoami)"
# Download agent script from public URL
AGENT_URL="https://socket.valiantedgetech.com/client_agent.py"
sudo curl -fsSL "$AGENT_URL" -o "$AGENT_PATH"
sudo chown $USER:$USER "$AGENT_PATH"
sudo chmod 755 "$AGENT_PATH"

# Create virtual environment
python3 -m venv "$VENV_PATH"
source "$VENV_PATH/bin/activate"
pip install --upgrade pip
pip install websockets requests

# Create systemd service file
sudo tee "$SERVICE_PATH" > /dev/null <<EOF
[Unit]
Description=Python Agent Client
After=network.target

[Service]
Type=simple
ExecStart=$VENV_PATH/bin/python $AGENT_PATH
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
