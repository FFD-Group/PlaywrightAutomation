from database import insert_to_db, query_db
from dotenv import load_dotenv
from sqlite3 import Row
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
    else:
        pass
    return []

def create_supplier(name: str, id: int) -> int|None:
    """Create a new supplier in the database with the given name and ID.
    Returns the ID of the inserted row or None."""
    return insert_to_db(
        "INSERT OR IGNORE INTO suppliers (id, name) VALUES (:id,:name)",
        {"id":int(id), "name":name}
    )

def get_supplier_automations(supplier_id: str) -> Row|str|None:
    return query_db("SELECT * FROM automations WHERE supplier_id = ?", (int(supplier_id),))