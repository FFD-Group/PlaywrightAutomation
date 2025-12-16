from __future__ import annotations

from typing import Any, List
from database import query_db, insert_to_db, delete_from_db, get_db


def create_automation(type: int, url: str, location: str, name: str, supplier_id: str) -> int | None:
    return insert_to_db(
        "INSERT INTO automations (type, url, location, name, supplier_id) VALUES (:type,:url,:location,:name,:supplier_id)",
        {
            "type": type,
            "url": url,
            "location": location,
            "name": name,
            "supplier_id": int(supplier_id),
        },
    )


def delete_automation(automation_id: str, supplier_id: str) -> List[str] | str | None:
    delete_from_db("DELETE FROM steps WHERE automation_id = ?", (automation_id,))
    return delete_from_db(
        "DELETE FROM automations WHERE id = ? AND supplier_id = ?",
        (automation_id, supplier_id),
    )


def save_automation_steps(automation_id: str, steps: str) -> int | None:
    return insert_to_db(
        "INSERT INTO steps (automation_id, automation_steps) VALUES (:id, :steps)",
        {"id": int(automation_id), "steps": steps},
    )


def get_automation_steps(automation_id: str) -> str | None:
    return query_db(
        "SELECT automation_steps FROM steps WHERE automation_id = ?",
        (automation_id,),
    )


def set_automation_last_run_result(automation_id: str, result: str) -> None:
    insert_to_db(
        "UPDATE automations SET last_run_result = (:last_run_result) WHERE id = (:id)",
        {"last_run_result": result, "id": automation_id},
    )


def get_job_location(automation_id: str) -> str | None:
    return query_db("SELECT location FROM automations WHERE id = ?", (automation_id,))


def get_automation_card_data(automation_id: str) -> str | None:
    return query_db(
        "SELECT a.id as automation_id, s.name as supplier_name, a.type, a.name as automation_name "
        "FROM automations a JOIN suppliers s ON a.supplier_id = s.id WHERE a.id = ?",
        (automation_id,),
    )


def set_automation_schedule(automation_id: int | str, schedule: str, time_str: str | None = None) -> None:
    db = get_db()
    cur = db.cursor()

    automation_id = int(automation_id)
    schedule = (schedule or "").strip()

    if schedule == "custom":
        if not time_str or ":" not in time_str:
            raise ValueError("Custom schedule requires time_str in format 'HH:MM'")
        time_str = time_str.strip()
    else:
        time_str = None

    cur.execute(
        """
        UPDATE automations
        SET schedule = ?,
            schedule_time = ?,
            schedule_enabled = 1
        WHERE id = ?
        """,
        (schedule, time_str, automation_id),
    )
    db.commit()


def clear_automation_schedule(automation_id: int | str) -> None:
    db = get_db()
    cur = db.cursor()
    automation_id = int(automation_id)

    cur.execute(
        """
        UPDATE automations
        SET schedule = NULL,
            schedule_time = NULL,
            schedule_enabled = 0
        WHERE id = ?
        """,
        (automation_id,),
    )
    db.commit()


def get_scheduled_automations() -> list[dict[str, Any]]:
    db = get_db()
    cur = db.cursor()
    rows = cur.execute(
        """
        SELECT id, type, schedule, schedule_time
        FROM automations
        WHERE schedule_enabled = 1
          AND schedule IS NOT NULL
          AND schedule <> ''
        """
    ).fetchall()
    return [dict(r) for r in rows]
