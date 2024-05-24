from playwright.sync_api import Page, sync_playwright
import time


def download_file():
    with sync_playwright() as pw:
        chromium = pw.chromium
        browser = chromium.launch(headless=False)
        context = browser.new_context(record_video_dir="static/recordings/videos/")
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()
        time.sleep(0.5)
        page.goto("https://www.dropbox.com/sh/jys76901q44nxpr/AACYu9RfSCE4-BDbGIkBKaJUa?e=1&dl=0")

        ccpa = page.frame_locator("#ccpa-iframe")
        accept = ccpa.locator("#accept_all_cookies_button")
        accept.click()

        time.sleep(2)
        page.get_by_role("button", name="Download").click()
        time.sleep(2)

        with page.expect_download() as download_info:
            # Perform the action that initiates download
            page.get_by_text("Or continue with download only", exact=True).click()
        download = download_info.value

        download.save_as("downloads/" + download.suggested_filename)
        
        print(page.video.path)
        time.sleep(2)
        context.tracing.stop(path="static/recordings/traces/trace.zip")
        context.close()
        browser.close()

if __name__ == "__main__":
    download_file()