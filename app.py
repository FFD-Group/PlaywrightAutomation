from flask import Flask, g, render_template, request, redirect, url_for
from automation_builder import AutomationBuilder
from database import get_db, query_db
from suppliers import get_suppliers

app = Flask(__name__, static_folder="static/")

@app.route("/")
def index():
    suppliers = get_suppliers()
    return render_template("index.html", suppliers=suppliers)

@app.route("/automation-builder/<string:supplier>")
def automation_builder(supplier: str):
    return render_template("automation.html", supplier=supplier)

@app.route("/test-automation/<string:supplier>", methods=['POST'])
def test_automation(supplier: str):
    data = request.get_json()
    print("Data received from POST!")
    print(data)
    builder = AutomationBuilder(supplier, data)
    automation = builder.build_automation()
    test_results = builder.test_automation(automation)
    print(test_results)
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