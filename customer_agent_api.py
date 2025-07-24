from fastapi import FastAPI, Request
import os
import socket
import requests

app = FastAPI()

WG_CONFIG_PATH = "C:/WireGuard/wg0.conf"  # Change path as needed for Windows

@app.post("/api/wgconfig")
async def receive_wg_config(request: Request):
    data = await request.json()
    config = data.get("config")
    customer = data.get("customer")
    if not config:
        return {"status": "error", "message": "No config provided"}
    # Save config file
    with open(WG_CONFIG_PATH, "w") as f:
        f.write(config)
    # Optionally, start WireGuard tunnel (Windows CLI)
    os.system(f'"C:\\Program Files\\WireGuard\\wireguard.exe" /installtunnelservice "{WG_CONFIG_PATH}"')
    # After starting tunnel, report LAN IPs to cloud
    local_ips = get_local_ips()
    cloud_api_url = os.environ.get("CLOUD_API_URL")  # Set this env var to your cloud API endpoint
    if cloud_api_url:
        try:
            report_ips_to_cloud(cloud_api_url, customer, local_ips)
        except Exception as e:
            return {"status": "partial", "message": f"Config applied, but failed to report IPs: {e}"}
    return {"status": "success", "message": f"Config applied for {customer}", "ips": local_ips}

if __name__ == "__main__":
    # Automated IP reporting on startup
    customer = os.environ.get("CUSTOMER", "customer1")
    cloud_api_url = os.environ.get("CLOUD_API_URL", "http://13.58.212.239:8000/report")
    local_ips = get_local_ips()
    print(f"[Agent Startup] Reporting IPs: {local_ips} for customer: {customer}")
    report_ips_to_cloud(cloud_api_url, customer, local_ips)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)

def get_local_ips():
    ips = []
    hostname = socket.gethostname()
    try:
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if not ip.startswith("127."):
                ips.append(ip)
    except Exception:
        pass
    # Also try to get all interfaces (Windows)
    try:
        import psutil
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                    if addr.address not in ips:
                        ips.append(addr.address)
    except ImportError:
        pass
    return ips

def report_ips_to_cloud(cloud_api_url, customer, ips):
    try:
        resp = requests.post(cloud_api_url, json={"customer": customer, "ips": ips}, timeout=10)
        print(f"Reporting IPs to cloud: {ips} for customer: {customer}")
        print(f"Cloud API response: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Failed to report IPs to cloud: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
