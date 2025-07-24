import os

# Example customer data (replace with your actual data source)
customers = [
    {
        "name": "customer1",
        "lan_subnet": "192.168.10.0/24",
        "gateway_publickey": "<customer1_gateway_publickey>",
        "gateway_vpn_ip": "10.10.10.2",
        "api_url": "http://customer1.example.com/api/wgconfig"  # Example API endpoint
    },
    {
        "name": "customer2",
        "lan_subnet": "192.168.20.0/24",
        "gateway_publickey": "<customer2_gateway_publickey>",
        "gateway_vpn_ip": "10.10.20.2",
        "api_url": "http://customer2.example.com/api/wgconfig"
    }
]

cloud_privatekey = "<cloud_privatekey>"
cloud_publickey = "<cloud_publickey>"
cloud_vpn_ip = "10.10.0.1"
listen_port = 51820

# Generate cloud WireGuard config with all customers as peers
def generate_cloud_config():
    config = f"""
[Interface]
PrivateKey = {cloud_privatekey}
Address = {cloud_vpn_ip}/24
ListenPort = {listen_port}
"""
    for c in customers:
        config += f"\n[Peer]\nPublicKey = {c['gateway_publickey']}\nAllowedIPs = {c['gateway_vpn_ip']}/32, {c['lan_subnet']}\n"
    with open("cloud_wg0.conf", "w") as f:
        f.write(config)
    print("Cloud WireGuard config generated: cloud_wg0.conf")

# Generate customer gateway config
def generate_customer_configs():
    for c in customers:
        config = f"""
[Interface]
PrivateKey = <customer_gateway_privatekey>
Address = {c['gateway_vpn_ip']}/24

[Peer]
PublicKey = {cloud_publickey}
Endpoint = <cloud_public_ip>:{listen_port}
AllowedIPs = {cloud_vpn_ip}/32
PersistentKeepalive = 25
"""
        fname = f"{c['name']}_wg0.conf"
        with open(fname, "w") as f:
            f.write(config)
        print(f"Customer config generated: {fname}")

import requests

def deploy_config_via_api(customer_name, config_path, api_url):
    with open(config_path, "r") as f:
        config_data = f.read()
    try:
        response = requests.post(
            api_url,
            json={"customer": customer_name, "config": config_data}
        )
        print(f"Deployed {config_path} to {api_url}: {response.status_code}")
    except Exception as e:
        print(f"Failed to deploy {config_path} to {api_url}: {e}")

if __name__ == "__main__":
    generate_cloud_config()
    generate_customer_configs()
    # Deploy each customer config via API if api_url is provided
    for c in customers:
        fname = f"{c['name']}_wg0.conf"
        api_url = c.get("api_url")
        if api_url:
            deploy_config_via_api(c["name"], fname, api_url)
