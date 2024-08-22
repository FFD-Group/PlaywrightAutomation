from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask import Flask, g, json, render_template, request, has_request_context
from flask_apscheduler import APScheduler
from apscheduler import events
from datetime import datetime
from logging.config import dictConfig
import requests
import os

class Config:
    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url="sqlite:///jobs.sqlite")
    }
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = "Europe/London"

dictConfig({
    'version': 1,
    'root': {
        'level': os.getenv("LOGGING_LEVEL")
    }
})

app = Flask(__name__, static_folder="static/")
app.config.from_object(Config())

app.logger.info("Creating Advanced Python Scheduler object and initialising.")

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

from automations import create_automation, delete_automation, save_automation_steps, set_automation_schedule
from automation_builder import AutomationBuilder
from database import get_db
from suppliers import get_suppliers, create_supplier, get_supplier_automations
from job_schedule import add_automation_schedule, get_automation_next_run_time, remove_automation_schedule, CRON_SCHEDULES
from storage import WorkDrive
from job_callback import job_callback
from database_backup import backup_database


app.logger.info("Scheduling heartbeat, backups and adding scheduler event callback.")
def betterstack_heartbeat():
    requests.get(os.getenv("HEARTBEAT_URL"))

scheduler.add_job(id='heartbeat', func=betterstack_heartbeat, trigger='cron', hour='*/1', replace_existing=True)
scheduler.add_job(id="database-backup", func=backup_database, trigger='cron', day='*/1', hour='3', replace_existing=True)
scheduler.add_listener(job_callback, events.EVENT_JOB_ERROR | events.EVENT_JOB_EXECUTED)

## INDEX

@app.route("/")
def index():
    suppliers = get_suppliers()
    wd = WorkDrive()
    folders = wd.get_locations()
    return render_template("index.html", suppliers=suppliers, save_locations=folders)

## DOWNLOADS

@app.route("/automations/download/save", methods=['POST'])
def save_download():
    data = request.get_json()
    app.logger.debug("New download saving with data:" + str(data))
    try:
        create_supplier(data["supplier_name"], data["supplier_id"])
        inserted_id = create_automation(1, data["download_url"], data["save_location"], data["automation_name"], data["supplier_id"])
        return json.dumps(inserted_id)
    except Exception as e:
        print(e)
        app.logger.error("Something went wrong saving the download.", exc_info=True)

## AUTOMATIONS

@app.route("/automation-builder/<int:supplier_id>/new")
def automation_builder(supplier_id: int):
    supplier_name = request.args.get('supplier_name')
    create_supplier(supplier_name, supplier_id)
    return render_template("automation.html", supplier_id=supplier_id, supplier_name=supplier_name)

@app.route("/automations/<int:supplier_id>/save", methods=['POST'])
def save_automation(supplier_id: int):
    data = request.get_json()
    app.logger.debug("Saving new automation with passed data:" + str(data))
    supplier_name = request.args.get('supplier_name')
    try:
        create_supplier(supplier_name, supplier_id)
        automation_id = create_automation(0, data["url"], data["location"], data["name"], supplier_id)
        save_automation_steps(automation_id, json.dumps(data["steps"]))
        return json.dumps(f"/?automation_id={automation_id}&supplier_id={supplier_id}&supplier_name={supplier_name}")
    except Exception as e:
        print(e)
        app.logger.error("Something went wrong saving the automation.", exc_info=True)

@app.route("/test-automation/<int:supplier_id>", methods=['POST'])
def test_automation(supplier_id: int):
    data = request.get_json()
    app.logger.debug("Testing automation with passed data:" + str(data))
    builder = AutomationBuilder(supplier_id, data)
    automation = builder.build_automation()
    test_results = builder.test_automation(automation)
    return test_results

@app.route("/automations/<int:supplier_id>")
def get_automations(supplier_id: int):
    existing_automations = get_supplier_automations(supplier_id)
    result = [dict(row) for row in existing_automations]
    for automation in result:
        next_run: datetime = get_automation_next_run_time(scheduler, automation["id"])
        automation["next_run_time"] = next_run if next_run else None
        
    return result

@app.route("/automation/<int:supplier_id>/<int:automation_id>/delete", methods=['DELETE'])
def delete_supplier_automation(supplier_id: int, automation_id: int):
    logdata = (supplier_id, automation_id, (request.remote_addr if has_request_context() else None))
    app.logger.info("Deleting automation: " + str(logdata))
    deleted_schedules = delete_supplier_automation(supplier_id, automation_id)
    deleted_automations = delete_automation(automation_id, supplier_id)
    result = {}
    if deleted_automations:
        result["automations"] = [dict(row) for row in deleted_automations]
    if deleted_schedules:
        result["schedules"] = [dict(row) for row in deleted_schedules]
    return result

## SCHEDULES

@app.route("/schedule/<string:automation_id>", methods=['POST'])
def schedule_automation(automation_id: str):
    data = request.get_json()
    app.logger.info(f"Scheduling automation with ID: {automation_id} for: " + str(data))
    schedule = data["schedule"]
    cron = CRON_SCHEDULES[schedule]
    if schedule == "custom":
        cron["hour"],cron["minute"] = data["time"].split(":")
    set_automation_schedule(automation_id, schedule)
    add_automation_schedule(scheduler, automation_id, cron, data["type"])
    next_run = get_automation_next_run_time(scheduler, automation_id)
    return json.dumps(next_run)

## DATABASE

@app.teardown_appcontext
def close_connection(exception) -> None:
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        app.logger.debug("Initialising database.")
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def add_sample_data():
    with app.app_context():
        app.logger.debug("Installing sample data.")
        db = get_db()
        with app.open_resource('sample_data.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
