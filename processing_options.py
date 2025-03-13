import json
import os
from pprint import pprint
import requests
from database import query_db, insert_to_db, delete_from_db
import sqlite3

SAVE_OPTIONS_URL = os.getenv("SAVE_OPTIONS_URL")


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


def delete_automation_processing_options(automation_id: int) -> None:
    delete_from_db(
        "DELETE FROM processing_options WHERE automation_id = ?",
        (automation_id,),
    )


def delete_processing_options(id: int) -> None:
    delete_from_db("DELETE FROM processing_options WHERE id = ?", (id,))


def save_options_to_zoho(automation_id: int, options: str) -> None:
    """Stores processing options in Zoho Creator App.
    automation_id - The automation ID linked to the options
    options - the JSON object representation of the options to be saved
    """
    data = {
        "Automation_ID": automation_id,
        "Processing_Options_Object": options,
    }
    r = requests.post(SAVE_OPTIONS_URL, data=json.dumps(data))
    pprint(r)


if __name__ == "__main__":
    test_options_object = {
        "Sku_column_example": "Model Number",
        "skip_rows": 3,
        "Some_object": {"an_object_property": "grass"},
    }
    save_options_to_zoho(1, json.dumps(test_options_object))
