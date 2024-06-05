from flask import Flask, g, render_template, request, redirect, url_for
from download_lincat_file import *
from database import get_db, query_db
from suppliers import get_suppliers

app = Flask(__name__, static_folder="static/")

@app.route("/")
def index():
    suppliers = get_suppliers()
    return render_template("index.html", suppliers=suppliers)

@app.route("/automation-builder")
def automation_builder():
    return render_template("automation.html")

@app.route("/test-automation/<string:supplier>")
def test_automation(supplier: str):
    ## test the automation for the supplier passed
    download_file()
    return "Tested!"

@app.teardown_appcontext
def close_connection(exception) -> None:
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()