from pathlib import Path
from typing import List

from flask import json
from database import query_db, insert_to_db, delete_from_db
from playwright.sync_api import sync_playwright
import playwright_automation
import time

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

def run_automation_steps(steps: List) -> None:

    actions = json.loads(steps[0]['automation_steps'])

    with sync_playwright() as pw:
        chromium = pw.chromium
        browser = chromium.launch(headless=False)
        context = browser.new_context(record_video_dir="static/recordings/videos/")
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()
        time.sleep(0.5)
        start_url = actions[0]['url']
        page.goto(start_url)

        downloads = []

        for action in actions[1:]:
            # call the action => func_name, page => page, **args
            func = action['action'] # func name
            args = { # construct args
                "type": action['method'],
                "text": action['pw_arg'],
                "input": action['pw_arg_2']
            }
            result = getattr(playwright_automation, func)(page, **args) # run function
            if func == "playwright_click_download" and result:
                downloads.append(f"/{result}")
            time.sleep(0.5)

        time.sleep(2)
        video_path = "/static/recordings/videos/" + Path(page.video.path()).name
        context.tracing.stop(path="static/recordings/traces/trace.zip")
        context.close()
        browser.close()