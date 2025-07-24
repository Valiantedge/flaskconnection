import requests

# Set your ZeroTier API token and network ID here
API_TOKEN = "YOUR_ZEROTIER_API_TOKEN"
NETWORK_ID = "YOUR_ZEROTIER_NETWORK_ID"
API_URL = f"https://my.zerotier.com/api/network/{NETWORK_ID}/member"
HEADERS = {"Authorization": f"bearer {API_TOKEN}"}

def get_all_members():
    """Fetch all members in the ZeroTier network."""
    response = requests.get(API_URL, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def authorize_member(member_id):
    """Authorize a member (device) in the ZeroTier network."""
    url = f"{API_URL}/{member_id}"
    data = {"authorized": True}
    response = requests.post(url, headers=HEADERS, json=data)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    # Example usage
    members = get_all_members()
    print("All members:", members)
    # Authorize the first unauthorized member (if any)
    for member in members:
        if not member.get("authorized", False):
            print(f"Authorizing member: {member['nodeId']}")
            result = authorize_member(member["nodeId"])
            print("Result:", result)
            break
