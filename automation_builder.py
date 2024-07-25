from typing import Any
from playwright.sync_api import sync_playwright
import playwright_automation

import time
## Receives a supplier ID and a list of actions from the HTML UI
## Needs to compile the automation, run it and return;
## a) downloaded file links
## b) trace report

CONSTANT_METHOD_MAP = {
    "gotopage": "playwright_goto",
    "pwclick": "playwright_click",
    "pwframeclick": "playwright_iframe_click",
    "pwdownload": "playwright_click_download",
    "pwinput": "playwright_fill_input",
    "pwcheck": "playwright_tick_checkbox",
    "pwselect": "playwright_select_dropdown"
}

class AutomationBuilder:
    supplier_id: str
    action_list: list
    start_url: str

    def __init__(self, supplier_id: str, actions: list):
        self.supplier_id = supplier_id
        self.action_list = actions

    def build_automation(self) -> list[Any]:
        automation_list = []
        self._read_start_url()
        automation_list.append({
            "action": "playwright_goto",
            "url": self.start_url,
            "pw_arg": "",
            "pw_arg_2": ""
        })
        for action in self.action_list:
            automation_list.append({
                "action": CONSTANT_METHOD_MAP[action['pw_action']],
                "method": action['pw_method'],
                "pw_arg": action['pw_method_arg'],
                "pw_arg_2": action['pw_method_arg_2']
            })
        return automation_list

    def test_automation(self, automation: list[Any]) -> list[str, str]:
        try:
            # run the automation steps and return trace and downloads
            with sync_playwright() as pw:
                chromium = pw.chromium
                browser = chromium.launch(headless=False)
                context = browser.new_context(record_video_dir="static/recordings/videos/")
                context.tracing.start(screenshots=True, snapshots=True, sources=True)
                page = context.new_page()
                time.sleep(0.5)
                start_url = automation[0]['url']
                page.goto(start_url)

                for action in automation[1:]:
                    # call the action => func_name, page => page, **args
                    func = action['action'] # func name
                    args = { # construct args
                        "type": action['method'],
                        "text": action['pw_arg'],
                        "input": action['pw_arg_2']
                    }
                    result = getattr(playwright_automation, func)(page, **args) # run function
                    if result:
                        print(result)
                    time.sleep(0.5)

                print(page.video.path)
                time.sleep(2)
                context.tracing.stop(path="static/recordings/traces/trace.zip")
                context.close()
                browser.close()
        except Exception as e:
            print(e)
            return ["Failure", "error"]
        return [
            page.video.path,
            "static/recordings/traces/trace.zip"
        ]

    def _read_start_url(self) -> None:
        self.start_url = self.action_list[0]['pw_url']
        self.action_list = self.action_list[1:]