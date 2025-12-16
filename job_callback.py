from comms import Cliq
from storage import WorkDrive
from automations import get_job_location, get_automation_card_data
from suppliers import get_supplier_id
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from app import scheduler
from trigger_process import ready_for_processing


def job_callback(event) -> None:
    job_id = str(event.job_id)

    # Only handle automation jobs (numeric IDs); ignore service tasks like backups/heartbeats.
    if not job_id.isdigit():
        scheduler.app.logger.debug(
            f"Skipping job callback for non-automation job_id={job_id}"
        )
        return

    with scheduler.app.app_context():
        load_dotenv()
        cliq = Cliq()
        supplier_details_rows = get_automation_card_data(event.job_id)
        supplier_details = (
            dict(supplier_details_rows[0]) if supplier_details_rows else None
        )
        if not supplier_details:
            supplier_details = {
                "supplier_name": "Unknown",
                "type": 1,
                "automation_name": "Unknown",
                "automation_id": int(job_id),
            }
        type_value = (
            "Automation" if supplier_details["type"] == 0 else "Download"
        )
        details_table = (
            {
                "type": "table",
                "title": "Details",
                "data": {
                    "headers": ["Type", type_value],
                    "rows": [
                        {
                            "Type": "Supplier",
                            type_value: supplier_details["supplier_name"],
                        },
                        {
                            "Type": "Name",
                            type_value: supplier_details["automation_name"],
                        },
                    ],
                },
            },
        )
        message = None
        if event.retval and not event.exception:
            zwd = WorkDrive()
            job_location = get_job_location(event.job_id)[0][0]
            message = {
                "text": f"I have gathered this  file as asked, it is ready to view.",
                "card": {"theme": "modern-inline"},
                "slides": details_table,
                "buttons": [],
            }
            if event.retval and len(event.retval) > 1:
                for download in event.retval:
                    scheduler.app.logger.info(
                        "Uploading file to WorkDrive.", args=download
                    )
                    permalink = zwd.upload_file(job_location, download)
                    scheduler.app.logger.debug(
                        "Permalink for file:" + permalink
                    )
                    message["buttons"].append(
                        {
                            "label": "View file",
                            "type": "+",
                            "action": {
                                "type": "open.url",
                                "data": {"web": permalink},
                            },
                        }
                    )
            elif event.retval and len(event.retval) == 1:
                scheduler.app.logger.info(
                    "Uploading file to WorkDrive: " + str(event.retval[0])
                )
                permalink = zwd.upload_file(job_location, event.retval[0])
                scheduler.app.logger.debug("Permalink for file:" + permalink)
                message["buttons"].append(
                    {
                        "label": "View file",
                        "type": "+",
                        "action": {
                            "type": "open.url",
                            "data": {"web": permalink},
                        },
                    }
                )

            scheduler.app.logger.info("Posting successful result to cliq.")

            ready_for_processing(
                zwd.get_last_file_id(),
                "Automation",
                time.time(),
                get_supplier_id(supplier_details["supplier_name"]),
                supplier_details["automation_id"],
            )

        if event.exception:
            message = {
                "text": f"""Oh no! Something went wrong gathering this file at {event.scheduled_run_time}.\nHere is the error\n\n```\n{event.exception}\n```""",
                "slides": details_table,
                "card": {"theme": "modern-inline"},
            }
            scheduler.app.logger.info("Posting failed result to cliq.")

        if message:
            cliq.post_message(os.getenv("Z_CLIQ_CHANNEL_NAME"), message=message)
            # print(message)
