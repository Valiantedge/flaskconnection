import os
import requests

CLOUD_API_URL = os.environ.get("CLOUD_API_URL", "http://13.58.212.239:8000/generate_config")
CUSTOMER = os.environ.get("CUSTOMER", "customer1")
WG_CONFIG_PATH = "C:/WireGuard/wg0.conf"

# Fetch WireGuard config from cloud
resp = requests.post(CLOUD_API_URL, json={"customer": CUSTOMER})
if resp.status_code == 200:
    data = resp.json()
    config_path = data.get("config_path")
    # Download config file from server
    # For demo, assume config is local to server, so we need to fetch its content
    # You may want to expose an endpoint to download the config file directly
    # Here, we just fetch the config content via another endpoint (not implemented yet)
    # For now, simulate by reading from the path if accessible
    # If you expose /get_config, you can use:
    # config_resp = requests.get(f"http://13.58.212.239:8000/get_config?customer={CUSTOMER}")
    # with open(WG_CONFIG_PATH, "w") as f:
    #     f.write(config_resp.text)
    print(f"Config generated at server: {config_path}")
    print("Please implement config download endpoint for full automation.")
else:
    print("Failed to fetch config from cloud API.")
