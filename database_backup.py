from storage import WorkDrive
from dotenv import load_dotenv
from app import scheduler
import requests
import os

def backup_database():
    with scheduler.app.app_context():
        load_dotenv()
        zwd = WorkDrive()
        scheduler.app.logger.info("Backing up jobs DB to WorkDrive.")
        zwd.upload_file(os.getenv("Z_DATABASE_BACKUP_LOCATION_ID"), "jobs.sqlite")
        scheduler.app.logger.info("Backing up main DB to WorkDrive.")
        zwd.upload_file(os.getenv("Z_DATABASE_BACKUP_LOCATION_ID"), "suppliers.sqlite")
        scheduler.app.logger.info("Sending heartbeat request to Betterstack.")
        requests.get(os.getenv("BACKUP_HEARTBEAT_URL"))
