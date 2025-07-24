import requests
import os

CLOUD_API_URL = os.environ.get("CLOUD_API_URL", "http://13.58.212.239:8000/register")
CUSTOMER = os.environ.get("CUSTOMER", "customer1")

payload = {"customer": CUSTOMER}

try:
    r = requests.post(CLOUD_API_URL, json=payload, timeout=10)
    print("Registration result:", r.text)
except Exception as e:
    print("Failed to register agent:", e)
