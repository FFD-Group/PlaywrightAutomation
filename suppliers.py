from dotenv import load_dotenv
import requests
import os

load_dotenv()

SUPPLIERS_API = "https://www.247cateringsupplies.co.uk/rest/default/V1/products/attributes/manufacturer/options"
INTEGRATION_ACCESS_TOKEN = os.getenv("INTEGRATION_ACCESS_TOKEN")
CLOUDFLARE_PASSCODE = os.getenv("CLOUDFLARE_PASSCODE")
API_HEADERS = {
    "Authorization": f"Bearer {INTEGRATION_ACCESS_TOKEN}",
    "cf-ffd-pass": CLOUDFLARE_PASSCODE,
    "Content-Type": "application/json"
}

def get_suppliers() -> list:
    r = requests.get(SUPPLIERS_API, headers=API_HEADERS)
    if (r.status_code == 200):
        return r.json()
    return []