import re
import mimetypes
from flask import json
from app import scheduler
from database import query_db
import requests

def download_file(automation_id: str) -> None:
    with scheduler.app.app_context():
        automation = query_db("SELECT * FROM automations WHERE id = ?", (automation_id,))
        automation = [dict(row) for row in automation][0]
        download_url = automation["url"]
        name = automation["name"]
        filename = str(name).strip().replace(" ", "_")
        filename = re.sub(r"(?u)[^-\w.]", "", filename)
        try:
            response = requests.get(download_url)
            extension = mimetypes.guess_extension(response.headers.get('content-type', '').split(';')[0])
            response.raise_for_status()

            with open(f"static/downloads/{automation_id}_{filename}{extension}", 'wb') as file:
                file.write(response.content)

        except Exception as e:
            print(e)


