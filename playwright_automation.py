from typing import Callable
from playwright.sync_api import Page, sync_playwright

CONSTANT_LOCATOR_TYPES = {
    "text": "get_by_text",
    "label": "get_by_label",
    "placeholder": "get_by_placeholder",
    "alt text": "get_by_alt_text",
    "title": "get_by_title"
}

class PlayWrightMethods:

    def playwright_goto(self, page: Page, url: str) -> None:
        page.goto(url)

    def playwright_click(self, page: Page, text: str, type: str) -> None:
        if type:
            locator_type = self._get_locator_type(type)
            element = getattr(page, locator_type)(text)
        else:
            element = page.locator(text)
        element.click()

    def playwright_iframe_click(self, page: Page, iframe_selector: str, type: str, text: str) -> None:
        iframe = page.frame_locator(iframe_selector)
        if type:
            locator_type = self._get_locator_type(type)
            element = getattr(iframe, locator_type)(text)
        else:
            element = iframe.locator(text)
        element.click()

    def playwright_click_download(self, page: Page, type: str, text: str) -> str:
        with page.expect_download() as download_info:
            # Perform the action that initiates download
            if type:
                locator_type = self._get_locator_type(type)
                element = getattr(page, locator_type)(text)
            else:
                element = page.locator(text)
            element.click()
        # Save the downloaded file
        download = download_info.value
        download.save_as("downloads/" + download.suggested_filename)
        return f"downloads/{download.suggested_filename}"
    
    def playwright_fill_input(self, page: Page, type: str, text: str, input: str) -> None:
        pass

    def playwright_tick_checkbox(self, page: Page, type: str, text: str) -> None:
        pass

    def playwright_select_dropdown(self, page: Page, type: str, text: str, option: str) -> None:
        pass

    def _get_locator_type(type) -> str:
        return CONSTANT_LOCATOR_TYPES[type]