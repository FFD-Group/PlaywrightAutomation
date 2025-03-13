import requests
import json
import os
from dotenv import load_dotenv
from pprint import pprint

TRIGGER_PROCESS_URL = os.getenv("TRIGGER_PROCESS_URL")


def ready_for_processing(
    file_id: str,
    source: str,
    gathered_at: str,
    supplier_id: int,
    automation_id: int,
) -> None:
    """Prepares metadata ready for processing.
    file_id - the WorkDrive File ID of the data file
    source - where the data was gathered from
    gathered_at - the date/time the data was gathered at
    supplier_id - the ID of the supplier
    """
    meta_data = {
        "fileID": file_id,
        "source": source,
        "gathered_at": gathered_at,
        "supplierID": supplier_id,
        "automationID": automation_id,
    }
    trigger_processing(meta_data)


def trigger_processing(data) -> None:
    """Send the signal to process the gathered data."""

    json_data = json.dumps(data)
    r = requests.post(TRIGGER_PROCESS_URL, data=json_data)
    pprint(r)


if __name__ == "__main__":
    TRIGGER_PROCESS_URL = "https://httpbin.org/post"
    data = {"test": "data", "with": "multiple", "parameters": [1, 2, 3, 4, 5]}
    trigger_processing(data)
