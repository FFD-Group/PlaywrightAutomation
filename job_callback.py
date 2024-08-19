from comms import Cliq
from storage import WorkDrive
from automations import get_job_location
import os
from dotenv import load_dotenv
from app import scheduler

def job_callback(event) -> None:
    with scheduler.app.app_context():
        load_dotenv()
        cliq = Cliq()
        message = None
        if event.retval:
            zwd = WorkDrive()
            job_location = get_job_location(event.job_id)[0][0]
            message = {
                "text": "I have gathered this file as asked, it is ready to view.",
                "card": {
                    "theme": "modern-inline"
                },
                "buttons": []
            }
            if event.retval and len(event.retval) > 1:
                for download in event.retval:
                    permalink = zwd.upload_file(job_location, download)
                    message["buttons"].append({
                        "label": "View file",
                        "type": "+",
                        "action": {
                            "type": "open.url",
                            "data": {
                                "web": permalink
                            }
                        }
                    })
            elif event.retval and len(event.retval) == 1:
                permalink = zwd.upload_file(job_location, event.retval[0])
                message["buttons"].append({
                        "label": "View file",
                        "type": "+",
                        "action": {
                            "type": "open.url",
                            "data": {
                                "web": permalink
                            }
                        }
                    })
                
            ### Find a way to add identifying info to card too.

        if event.exception:
            message = {
                "text": f"""Oh no! Something went wrong gathering this file at {event.scheduled_run_time}.\n
                        Here is the error\n\n
                        {event.exception}
                        """,
                "card": {
                    "theme": "modern-inline"
                },
            }
        
        if message:
            # cliq.post_message(os.getenv("Z_CLIQ_CHANNEL_NAME"), message=message)
            print(message)