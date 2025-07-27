#!/bin/bash
# Auto-install and run agent as a systemd service

set -e

AGENT_PATH="/opt/client_agent.py"
SERVICE_PATH="/etc/systemd/system/agent-client.service"
PYTHON_BIN="$(which python3)"
USER="$(whoami)"





# Ensure Python 3 is installed, then install python3-venv module depending on OS
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 not found. Installing..."
    if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update
        sudo apt-get install -y python3
    elif command -v dnf >/dev/null 2>&1; then
        sudo dnf install -y python3
    elif command -v yum >/dev/null 2>&1; then
        sudo yum install -y python3
    else
        echo "Error: Could not detect supported package manager (apt, dnf, yum). Please install python3 manually."
        exit 1
    fi
fi

# Install venv module for Python 3
if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y python3-venv
elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y python3-venv python3-virtualenv || sudo dnf install -y python3.10-venv
elif command -v yum >/dev/null 2>&1; then
    sudo yum install -y python3-venv python3-virtualenv || sudo yum install -y python3.10-venv
else
    echo "Error: Could not detect supported package manager (apt, dnf, yum). Please install python3-venv manually."
    exit 1
fi

# Download agent script from public URL
AGENT_URL="https://socket.valiantedgetech.com/client_agent.py"
sudo curl -fsSL "$AGENT_URL" -o "$AGENT_PATH"
sudo chown $USER:$USER "$AGENT_PATH"
sudo chmod 755 "$AGENT_PATH"

# Create virtual environment
VENV_PATH="/opt/agent-venv"
python3 -m venv "$VENV_PATH"
source "$VENV_PATH/bin/activate"
pip install --upgrade pip
pip install websockets requests

# Create systemd service file (correct block only)
sudo tee "$SERVICE_PATH" > /dev/null <<EOF
[Unit]
Description=Python Agent Client
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/
ExecStart=$VENV_PATH/bin/python $AGENT_PATH
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd, enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable agent-client
sudo systemctl start agent-client
