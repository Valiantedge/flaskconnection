#!/bin/bash
# Auto-install and run agent as a systemd service

set -e

AGENT_PATH="/opt/client_agent.py"
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

#!/bin/bash
# Universal installer for Python agent client
set -e

AGENT_URL="https://socket.valiantedgetech.com/client_agent.py"
AGENT_PATH="/opt/client_agent.py"
VENV_PATH="/opt/agent-venv"
SERVICE_PATH="/etc/systemd/system/agent-client.service"
USER="$(whoami)"

# Detect OS and install Python3 & venv if missing
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    OS=$(uname -s)
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "[INFO] Python3 not found. Installing..."
    if [[ "$OS" == "ubuntu" || "$OS" == "debian" ]]; then
        sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip curl
    elif [[ "$OS" == "centos" || "$OS" == "rhel" || "$OS" == "fedora" ]]; then
        sudo yum install -y python3 python3-venv python3-pip curl
    else
        echo "[ERROR] Unsupported OS. Please install Python3 manually."
        exit 1
    fi
fi

# Download agent script
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
