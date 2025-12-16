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
    "Content-Type": "application/json",
}


def get_suppliers() -> list:
    r = requests.get(SUPPLIERS_API, headers=API_HEADERS)
    print(r.content)
    print(r.status_code)
    if r.status_code == 200:
        return r.json()
    else:
        print("Response from getting manufacturers off website: " + str(r))
        pass
    return []


def get_supplier_id(supplier_name: str) -> int:
    suppliers = get_suppliers()
    for supplier in suppliers:
        if supplier["label"] == supplier_name:
            return supplier["value"]
    return None


def create_supplier(name: str, id: int) -> int | None:
    """Create a new supplier in the database with the given name and ID.
    Returns the ID of the inserted row or None."""
    return insert_to_db(
        "INSERT OR IGNORE INTO suppliers (id, name) VALUES (:id,:name)",
        {"id": int(id), "name": name},
    )


def get_supplier_automations(supplier_id: str) -> Row | str | None:
    return query_db(
        "SELECT * FROM automations WHERE supplier_id = ?", (int(supplier_id),)
    )


def get_supplier_uploads(supplier_id: str) -> Row | str | None:
    return query_db(
        "SELECT * FROM uploads WHERE supplier_id = ?", (int(supplier_id),)
    )


def add_uploaded_file(
    supplier_id: str, filename: str, uploaded_at: int, processed: int
) -> int | None:
    """Create an entry for an uploaded file."""
    return insert_to_db(
        "INSERT OR IGNORE INTO uploads (supplier_id, filename, uploaded_at, processed) VALUES (:id, :file, :datetime, :processed)",
        {
            "id": supplier_id,
            "file": filename,
            "datetime": uploaded_at,
            "processed": processed,
        },
    )
