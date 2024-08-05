from typing import List
from database import query_db, insert_to_db, delete_from_db

def create_automation(type: int, url: str, location: str, name: str, supplier_id: str) -> int|None:
    return insert_to_db(
        "INSERT INTO automations (type, url, location, name, supplier_id) VALUES (:type,:url,:location,:name,:supplier_id)",
        {"type":1, "url":url, "location":location, "name":name, "supplier_id":int(supplier_id)}
    )

def delete_automation(automation_id: str, supplier_id: str) -> List[str]|str|None:
    return delete_from_db("DELETE FROM automations WHERE id = ? AND supplier_id = ?", (automation_id, supplier_id))