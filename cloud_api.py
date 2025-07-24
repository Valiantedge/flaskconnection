
from fastapi import FastAPI, Request
import os
import subprocess

app = FastAPI()

# Store reported IPs in memory (for demo; use DB in production)
reported_ips = {}
registered_agents = {}

# Utility: Generate WireGuard config (demo keys/IPs)
def generate_wg_config(customer):
    private_key = subprocess.getoutput('wg genkey')
    public_key = subprocess.getoutput(f'echo {private_key} | wg pubkey')
    config = f"""[Interface]
PrivateKey = {private_key}
Address = 10.0.0.2/32
DNS = 8.8.8.8

[Peer]
PublicKey = <server-public-key>
Endpoint = <server-endpoint>:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
"""
    config_dir = os.path.join(os.getcwd(), "configs")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, f"{customer}.conf")
    with open(config_path, "w") as f:
        f.write(config)
    return config_path

# API endpoint: Generate WireGuard config for customer
@app.post("/generate_config")
async def api_generate_config(request: Request):
    data = await request.json()
    customer = data.get("customer")
    if not customer:
        return {"status": "error", "message": "Missing customer name"}
    config_path = generate_wg_config(customer)
    return {"status": "success", "message": f"Config generated for {customer}", "config_path": config_path}

# API endpoint: Add customer as WireGuard peer to server config
@app.post("/add_peer")
async def add_peer(request: Request):
    data = await request.json()
    customer = data.get("customer")
    config_dir = os.path.join(os.getcwd(), "configs")
    config_path = os.path.join(config_dir, f"{customer}.conf")
    if not os.path.exists(config_path):
        return {"status": "error", "message": "Customer config not found"}
    # Extract public key from customer config
    pubkey = None
    with open(config_path, "r") as f:
        for line in f:
            if line.strip().startswith("PrivateKey ="):
                privkey = line.strip().split("=",1)[1].strip()
                pubkey = subprocess.getoutput(f'echo {privkey} | wg pubkey')
                break
    if not pubkey:
        return {"status": "error", "message": "Could not extract public key"}
    # Append peer to server config
    server_conf = "/etc/wireguard/wg0.conf"
    peer_conf = f"\n[Peer]\nPublicKey = {pubkey}\nAllowedIPs = 10.0.0.2/32\n"
    try:
        with open(server_conf, "a") as f:
            f.write(peer_conf)
    except Exception as e:
        return {"status": "error", "message": f"Failed to update server config: {e}"}
    # Optionally restart WireGuard (uncomment if desired)
    # subprocess.run(["sudo", "wg-quick", "down", "wg0"])
    # subprocess.run(["sudo", "wg-quick", "up", "wg0"])
    return {"status": "success", "message": f"Peer added for {customer}", "public_key": pubkey}
    customer = data.get("customer")
    ips = data.get("ips")
    if not customer or not ips:
        return {"status": "error", "message": "Missing customer or IPs"}
    reported_ips[customer] = ips
    return {"status": "success", "message": f"IPs received for {customer}", "ips": ips}

@app.get("/ips/{customer}")
@app.get("/agent/{customer}")
async def get_agent_ip(customer: str):
    ip = registered_agents.get(customer)
    if not ip:
        return {"status": "error", "message": "No agent IP found for customer"}
    return {"status": "success", "customer": customer, "ip": ip}
async def get_ips(customer: str):
    ips = reported_ips.get(customer)
    if not ips:
        return {"status": "error", "message": "No IPs found for customer"}
    return {"status": "success", "customer": customer, "ips": ips}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
