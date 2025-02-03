from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask import (
    Flask,
    g,
    json,
    jsonify,
    render_template,
    request,
    has_request_context,
    flash,
    redirect,
    url_for,
)
from flask_apscheduler import APScheduler
from apscheduler import events
from datetime import datetime
from logging.config import dictConfig
import requests
import os
import time
from werkzeug.utils import secure_filename
from trigger_process import ready_for_processing
from sample_uploads import get_file_column_names, get_column_values
from processing_options import add_processing_options

UPLOAD_FOLDER = "static/uploads"
TEMP_FOLDER = "temp"
ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}


class Config:
    SCHEDULER_JOBSTORES = {
        "default": SQLAlchemyJobStore(url="sqlite:///jobs.sqlite")
    }
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = "Europe/London"


dictConfig({"version": 1, "root": {"level": os.getenv("LOGGING_LEVEL")}})

app = Flask(__name__, static_folder="static/")
app.config.from_object(Config())
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["TEMP_FOLDER"] = TEMP_FOLDER

app.secret_key = b"tghJUV813_d/emp1"

app.logger.info("Creating Advanced Python Scheduler object and initialising.")

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

from automations import (
    create_automation,
    delete_automation,
    save_automation_steps,
    set_automation_schedule,
)
from automation_builder import AutomationBuilder
from database import get_db
from suppliers import (
    get_suppliers,
    create_supplier,
    get_supplier_automations,
    get_supplier_uploads,
    add_uploaded_file,
)
from job_schedule import (
    add_automation_schedule,
    get_automation_next_run_time,
    remove_automation_schedule,
    CRON_SCHEDULES,
)
from storage import WorkDrive
from job_callback import job_callback
from database_backup import backup_database


app.logger.info(
    "Scheduling heartbeat, backups and adding scheduler event callback."
)


def betterstack_heartbeat():
    requests.get(os.getenv("HEARTBEAT_URL"))


# scheduler.add_job(
#     id="heartbeat",
#     func=betterstack_heartbeat,
#     trigger="cron",
#     hour="*/1",
#     replace_existing=True,
# )
# scheduler.add_job(
#     id="database-backup",
#     func=backup_database,
#     trigger="cron",
#     day="*/1",
#     hour="3",
#     replace_existing=True,
# )
scheduler.add_listener(
    job_callback, events.EVENT_JOB_ERROR | events.EVENT_JOB_EXECUTED
)


## INDEX
def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part", "error")
            return redirect(request.url)
        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash("No selected file", "error")
            return redirect(request.url)
        if "supplier_id" not in request.form:
            flash("No supplier ID", "error")
            return redirect(request.url)
        if "supplier_name" not in request.form:
            return redirect(request.url)
        if not request.form["supplier_id"]:
            flash("No supplier selected", "error")
            return redirect(request.url)
        supplier_id = request.form["supplier_id"]
        if not request.form["supplier_name"]:
            flash("No supplier name", "error")
            return redirect(request.url)
        supplier_name = request.form["supplier_name"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            create_supplier(supplier_name, supplier_id)
            uploaded_at = time.time()
            add_uploaded_file(supplier_id, filename, uploaded_at, 0)
            flash("File uploaded for processing", "success")
            zwd = WorkDrive()
            zwd.upload_file(
                os.getenv("Z_WD_UPLOAD_FOLDER_ID"),
                os.path.join(app.config["UPLOAD_FOLDER"], filename),
            )
            file_id = zwd.get_last_file_id()
            ready_for_processing(file_id, "manual", uploaded_at, supplier_id)
            return redirect(url_for("index", supplier_id=supplier_id))
        else:
            flash("Invalid file format", "error")
            redirect(request.url)
    suppliers = get_suppliers()
    wd = WorkDrive()
    folders = wd.get_locations()
    return render_template(
        "index.html", suppliers=suppliers, save_locations=folders
    )


## DOWNLOADS


@app.route("/automations/download/save", methods=["POST"])
def save_download():
    data = request.get_json()
    app.logger.debug("New download saving with data:" + str(data))
    try:
        create_supplier(data["supplier_name"], data["supplier_id"])
        inserted_id = create_automation(
            1,
            data["download_url"],
            data["save_location"],
            data["automation_name"],
            data["supplier_id"],
        )
        return json.dumps(inserted_id)
    except Exception as e:
        print(e)
        app.logger.error(
            "Something went wrong saving the download.", exc_info=True
        )


## UPLOADS


@app.route("/uploads/<int:supplier_id>")
def get_uploads(supplier_id: int):
    uploads = get_supplier_uploads(supplier_id)
    result = [dict(row) for row in uploads]
    return result


@app.route("/upload-sample-file", methods=["POST"])
def get_uploaded_file_columns() -> list[str]:
    # check if the post request has the file part
    if "file" not in request.files:
        return jsonify({"result": "error", "detail": "No file part"})
    file = request.files["file"]
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == "":
        return jsonify({"result": "error", "detail": "No selected file"})
    if file and allowed_file(file.filename):
        skiprows = (
            request.form["skip_rows"] if "skip_rows" in request.form else 0
        )
        filename = secure_filename(file.filename)
        temp_file_path = os.path.join(app.config["TEMP_FOLDER"], filename)
        try:
            file.save(temp_file_path)
            # read file into pandas then return column names
            column_names = get_file_column_names(temp_file_path, int(skiprows))
        except Exception as e:
            return jsonify({"result": "error", "detail": str(e)})
        return jsonify({"result": "success", "detail": column_names})
    return jsonify({"result": "error", "detail": "File type not supported!"})


@app.route("/distinct-column-values", methods=["POST"])
def get_column_distinct_values():
    if "file" not in request.files:
        return jsonify({"result": "error", "detail": "No file part"})
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"result": "error", "detail": "No selected file"})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        skip_rows = request.form["skip_rows"]
        group_by_column = request.form["group_by_column"]
        temp_file_path = os.path.join(app.config["TEMP_FOLDER"], filename)
        column_values = get_column_values(
            temp_file_path, int(skip_rows), group_by_column
        )
        return jsonify({"result": "success", "detail": column_values})
    else:
        return jsonify(
            {"result": "error", "detail": "File type not supported!"}
        )


## AUTOMATIONS


@app.route("/automation-builder/<int:supplier_id>/new")
def automation_builder(supplier_id: int):
    supplier_name = request.args.get("supplier_name")
    create_supplier(supplier_name, supplier_id)
    return render_template(
        "automation.html", supplier_id=supplier_id, supplier_name=supplier_name
    )


@app.route("/automations/<int:supplier_id>/save", methods=["POST"])
def save_automation(supplier_id: int):
    data = request.get_json()
    app.logger.debug("Saving new automation with passed data:" + str(data))
    supplier_name = request.args.get("supplier_name")
    try:
        create_supplier(supplier_name, supplier_id)
        automation_id = create_automation(
            0, data["url"], data["location"], data["name"], supplier_id
        )
        save_automation_steps(automation_id, json.dumps(data["steps"]))
        return json.dumps(
            f"/?automation_id={automation_id}&supplier_id={supplier_id}&supplier_name={supplier_name}"
        )
    except Exception as e:
        print(e)
        app.logger.error(
            "Something went wrong saving the automation.", exc_info=True
        )


@app.route("/automations/validate_processing_options", methods=["POST"])
def validate_processing_options():
    data = request.get_json()
    # skip_rows: int - default 0
    if not data["skip_rows"] or int(data["skip_rows"]) < 0:
        return jsonify(
            {"result": "error", "detail": "'skip_rows' is required."}
        )
    # sku_column: str - required
    if not data["sku_column"]:
        return jsonify(
            {"result": "error", "detail": "'SKU' column must be mapped."}
        )
    #     price_column: this.cm_price,                                  str - could be ""
    #     cost_column: this.cm_cost,                                    str - could be ""
    #     data_type: this.processing_file_type,                         str - determines extra validation:
    #                       "stock file": ONE OF stock_availability_column, stock_quantity_column REQUIRED
    #                       "price file": ONE OF price_column, cost_column REQUIRED
    if data["data_type"] == "Stock file":
        #   stock_availability_column: str - could be ""
        #   stock_quantity_column: str - could be ""
        if (
            data["stock_availability_column"] == ""
            and data["stock_quantity_column"] == ""
        ):
            return jsonify(
                {
                    "result": "error",
                    "detail": "At least one of 'Stock Availability', 'Stock Quantity' columns must be mapped.",
                }
            )
        #   stock_strategy: str|None - optional depending on data_type
        if not data["stock_strategy"] or data["stock_strategy"] == "":
            return jsonify(
                {"result": "error", "detail": "Stock strategy is required."}
            )
    elif data["data_type"] == "Price file":
        if data["price_column"] == "" and data["cost_column"] == "":
            return jsonify(
                {
                    "result": "error",
                    "detail": "At least one of 'Price', 'Cost' columns must be mapped.",
                }
            )
        #   price_strategy: str|None - optional depending on data_type
        if not data["price_strategy"] or data["price_strategy"] == "":
            return jsonify(
                {"result": "error", "detail": "Price strategy is required."}
            )
        #   pricing_markup: float - optional depending on data type
        if not data["pricing_markup"]:
            return jsonify({"result": "error", "detail": "Markup is required."})
        #   pricing_discount: float - optional depending on data type
        if not data["pricing_discount"]:
            return jsonify(
                {"result": "error", "detail": "Discount is required."}
            )
    # specials_type: str - required
    if not data["specials_type"]:
        return jsonify(
            {"result": "error", "detail": "Specials Type is required."}
        )
    # adv_pricing_group_column: str|None - optional
    # adv_pricing_groups: list[Object] - optional, each Object represents a value in grouping column

    return jsonify(
        {"result": "sucess", "detail": "Processing options validated."}
    )


@app.route(
    "/automations/<int:automation_id>/save_processing_options", methods=["POST"]
)
def save_processing_options(automation_id: int):
    data = request.get_json()
    ## @TODO: save to database with relation to automation
    add_processing_options(automation_id, str(data))
    ## @TODO: save to Zoho Creator app
    return "saved"


@app.route("/test-automation/<int:supplier_id>", methods=["POST"])
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
        next_run: datetime = get_automation_next_run_time(
            scheduler, automation["id"]
        )
        automation["next_run_time"] = next_run if next_run else None

    return result


@app.route(
    "/automation/<int:supplier_id>/<int:automation_id>/delete",
    methods=["DELETE"],
)
def delete_supplier_automation(supplier_id: int, automation_id: int):
    logdata = (
        supplier_id,
        automation_id,
        (request.remote_addr if has_request_context() else None),
    )
    app.logger.info("Deleting automation: " + str(logdata))
    deleted_schedules = None
    try:
        deleted_schedules = remove_automation_schedule(scheduler, automation_id)
    except Exception as e:
        print(e)
    deleted_automations = delete_automation(automation_id, supplier_id)
    result = {}
    if deleted_automations:
        result["automations"] = [dict(row) for row in deleted_automations]
    if deleted_schedules:
        result["schedules"] = [dict(row) for row in deleted_schedules]
    return result


## SCHEDULES


@app.route("/schedule/<string:automation_id>", methods=["POST"])
def schedule_automation(automation_id: str):
    data = request.get_json()
    app.logger.info(
        f"Scheduling automation with ID: {automation_id} for: " + str(data)
    )
    schedule = data["schedule"]
    cron = CRON_SCHEDULES[schedule]
    if schedule == "custom":
        cron["hour"], cron["minute"] = data["time"].split(":")
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
        with app.open_resource("schema.sql", mode="r") as f:
            db.cursor().executescript(f.read())
        db.commit()


def add_sample_data():
    with app.app_context():
        app.logger.debug("Installing sample data.")
        db = get_db()
        with app.open_resource("sample_data.sql", mode="r") as f:
            db.cursor().executescript(f.read())
        db.commit()
