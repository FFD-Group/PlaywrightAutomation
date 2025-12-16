from storage import WorkDrive
from dotenv import load_dotenv
from extensions import scheduler
import requests
import os

def backup_database():
    app = scheduler.app
    
    with app.app_context():
        load_dotenv()
        zwd = WorkDrive()
        app.logger.info("Backing up jobs DB to WorkDrive.")
        zwd.upload_file(os.getenv("Z_DATABASE_BACKUP_LOCATION_ID"), "jobs.sqlite", False)
        app.logger.info("Backing up main DB to WorkDrive.")
        zwd.upload_file(os.getenv("Z_DATABASE_BACKUP_LOCATION_ID"), "suppliers.sqlite", False)
        app.logger.info("Sending heartbeat request to Betterstack.")
        requests.get(os.getenv("BACKUP_HEARTBEAT_URL"))
