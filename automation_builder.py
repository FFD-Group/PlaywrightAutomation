from typing import Protocol

from playwright_automation import PlayWrightMethods as pw_methods

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

    def build_automation(self) -> list[str]:
        automation_list = []
        self._read_start_url()
        automation_list.append({
            "pw_action": "gotopage",
            "url": self.start_url,
            "pw_arg": "",
            "pw_arg_2": ""
        })
        for action in self.action_list:
            method = CONSTANT_METHOD_MAP[action['pw_action']]
            print(method)

    def test_automation(self, automation: list[str]) -> list[str, str]:
        # run the automation steps and return trace and downloads
        pass

    def _read_start_url(self) -> None:
        self.start_url = self.action_list[0]['pw_url']
        self.action_list = self.action_list[1:]