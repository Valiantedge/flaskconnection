import requests
import time

# Replace with the actual customer agent IP or hostname
AGENT_URL = "http://localhost:5000/api/wgconfig"
CUSTOMER_NAME = "customer1"

# Load WireGuard config from file
with open("client_wg.conf", "r") as f:
    wg_config = f.read()

payload = {
    "config": wg_config,
    "customer": CUSTOMER_NAME
}

while True:
    try:
        r = requests.post(AGENT_URL, json=payload, timeout=10)
        print("POST result:", r.text)
        break
    except Exception as e:
        print("Agent not reachable, retrying in 10s...")
        time.sleep(10)
