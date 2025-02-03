from database import query_db, insert_to_db, delete_from_db
import sqlite3


def get_processing_options(automation_id: int) -> sqlite3.Row | str | None:
    return query_db(
        "SELECT options FROM processing_options WHERE automation_id = ?",
        (automation_id,),
    )


def add_processing_options(automation_id: int, options: str) -> None:
    return insert_to_db(
        "INSERT INTO processing_options (automation_id, options) VALUES (:id, :options)",
        {"id": automation_id, "options": options},
    )


def delete_processing_options(id: int) -> None:
    delete_from_db("DELETE FROM processing_options WHERE id = ?", (id,))


def save_options_to_zoho(automation_id: int, options: str) -> None:
    pass
