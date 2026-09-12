import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SENTINEL_CLIENT_ID")
CLIENT_SECRET = os.getenv("SENTINEL_CLIENT_SECRET")

TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

response = requests.post(
    TOKEN_URL,
    data={
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    },
)

print("Status code:", response.status_code)
token_data = response.json()
if "access_token" in token_data:
    print("Got access token! (first 20 chars):", token_data["access_token"][:20], "...")
else:
    print("No token. Response:", token_data)
