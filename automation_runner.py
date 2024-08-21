from typing import List
import playwright_automation
import time
from app import scheduler
from datetime import datetime
from playwright.sync_api import sync_playwright
from automations import set_automation_last_run_result
from flask import json
import os

def run_automation_steps(automation_id: str, steps: List) -> List[str]:
    downloads = []
    with scheduler.app.app_context():
        scheduler.app.logger.info("Running automation with ID:" + automation_id)
        scheduler.app.logger.debug("Automation steps:" + str(steps))
        result = "Success, the automations steps ran successfully"
        if not steps:
            result = "Failure, could not load automation steps"
            scheduler.app.logger.warn("Automation steps not found.")
        else:
            actions = json.loads(steps[0]['automation_steps'])
            try:
                downloads = perform_actions(actions, automation_id)
                if downloads:
                    scheduler.app.logger.info(f"Downloaded {len(downloads)} files: " + str(downloads))
            except Exception as e:
                print(e)
                result = "Failure, an error occurred during the automation steps"
                scheduler.app.logger.error("Error running the automation steps.", exc_info=True)
                raise e
        set_automation_last_run_result(automation_id, result)
    return downloads

def perform_actions(actions: List, automation_id: str) -> List|None:
    run_time = datetime.now()
    downloads = []
    headless = False if os.getenv("DEBUG") == 1 else True
    with sync_playwright() as pw:
        chromium = pw.chromium
        browser = chromium.launch(headless=headless)
        context = browser.new_context(record_video_dir="static/recordings/videos/")
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()
        time.sleep(0.5)
        start_url = actions[0]['url']
        page.goto(start_url)

        for action in actions[1:]:
            scheduler.app.logger.debug("Performing action:" + str(action))
            # call the action => func_name, page => page, **args
            func = action['action'] # func name
            args = { # construct args
                "type": action['method'],
                "text": action['pw_arg'],
                "input": action['pw_arg_2']
            }
            result = getattr(playwright_automation, func)(page, **args) # run function
            if func == "playwright_click_download" and result:
                downloads.append(f"{result}")
            time.sleep(0.5)

        time.sleep(2)
        trace_filename = f"{automation_id}_trace_" + run_time.strftime("%Y-%m-%d-%H-%M") + ".zip"
        context.tracing.stop(path="static/recordings/traces/" + trace_filename)
        context.close()
        browser.close()

        if downloads:
            return downloads