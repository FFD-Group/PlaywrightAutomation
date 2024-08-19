from database import query_db, insert_to_db, delete_from_db
from typing import List

def create_automation(type: int, url: str, location: str, name: str, supplier_id: str) -> int|None:
    return insert_to_db(
        "INSERT INTO automations (type, url, location, name, supplier_id) VALUES (:type,:url,:location,:name,:supplier_id)",
        {"type":type, "url":url, "location":location, "name":name, "supplier_id":int(supplier_id)}
    )

def delete_automation(automation_id: str, supplier_id: str) -> List[str]|str|None:
    delete_from_db("DELETE FROM steps WHERE automation_id = ?", (automation_id,))
    return delete_from_db("DELETE FROM automations WHERE id = ? AND supplier_id = ?", (automation_id, supplier_id))

def save_automation_steps(automation_id: str, steps: str) -> int|None:
    return insert_to_db(
        "INSERT INTO steps (automation_id, automation_steps) VALUES (:id, :steps)",
        {"id": int(automation_id), "steps": steps}
    )

def get_automation_steps(automation_id: str) -> str|None:
    return query_db(
        "SELECT automation_steps FROM steps WHERE automation_id = ?", (automation_id,)
    )

def set_automation_schedule(automation_id: str, schedule: str) -> None:
    return insert_to_db("UPDATE automations SET schedule = (:schedule) WHERE id = (:id)", {"schedule":schedule, "id":automation_id})

def set_automation_last_run_result(automation_id: str, result: str) -> None:
    insert_to_db("UPDATE automations SET (last_run_result) = (:last_run_result) WHERE id = (:id)", {"last_run_result":result, "id":automation_id})

def get_job_location(automation_id: str) -> str|None:
    return query_db(
        "SELECT location FROM automations WHERE id = ?", (automation_id,)
    )