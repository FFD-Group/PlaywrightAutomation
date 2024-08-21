import re
import mimetypes
from typing import List
from flask import json
from app import scheduler
from automations import set_automation_last_run_result
from database import query_db
import requests

def download_file(automation_id: str) -> List[str]:
    with scheduler.app.app_context():
        scheduler.app.logger.info("Running the download with ID:" + automation_id)
        result = "Success, the download ran successfully"
        automation = query_db("SELECT * FROM automations WHERE id = ?", (automation_id,))
        automation = [dict(row) for row in automation][0]
        download_url = automation["url"]
        name = automation["name"]
        download_file = None
        filename = str(name).strip().replace(" ", "_")
        filename = re.sub(r"(?u)[^-\w.]", "", filename)
        try:
            response = requests.get(download_url)
            extension = mimetypes.guess_extension(response.headers.get('content-type', '').split(';')[0])
            response.raise_for_status()

            download_file = f"static/downloads/{automation_id}_{filename}{extension}"

            with open(download_file, 'wb') as file:
                file.write(response.content)

        except Exception as e:
            print(e)
            result = "Failure, an error occurred during the download"
            scheduler.app.logger.error("Error occurred while running the download.", exc_info=True)
            raise e
        set_automation_last_run_result(automation_id, result)
        if download_file:
            scheduler.app.logger.info("Downloaded file:" + download_file)
            return [download_file]


