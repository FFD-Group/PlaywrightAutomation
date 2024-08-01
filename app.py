from flask import Flask, g, render_template, request, redirect, url_for
from automation_builder import AutomationBuilder
from database import get_db, query_db
from suppliers import get_suppliers

app = Flask(__name__, static_folder="static/")

@app.route("/")
def index():
    suppliers = get_suppliers()
    return render_template("index.html", suppliers=suppliers)

@app.route("/automation-builder/<int:supplier_id>/new")
def automation_builder(supplier_id: int):
    return render_template("automation.html", supplier_id=supplier_id)

@app.route("/test-automation/<int:supplier_id>", methods=['POST'])
def test_automation(supplier_id: int):
    data = request.get_json()
    builder = AutomationBuilder(supplier_id, data)
    automation = builder.build_automation()
    test_results = builder.test_automation(automation)
    return test_results

@app.route("/automations/<int:supplier_id>")
def get_automations(supplier_id: int):
    existing_automations = query_db("SELECT * FROM automations WHERE supplier_id = ?", (supplier_id,))
    result = [dict(row) for row in existing_automations]
    print(result)
    return result

@app.route("/automation/<int:supplier_id>/<int:automation_id>/edit")
def edit_automation(supplier_id: int, automation_id: int):
    return f"Edit {supplier_id} automation with ID: {automation_id}."

@app.route("/automation/<int:supplier_id>/<int:automation_id>/delete", methods=['DELETE'])
def delete_automation(supplier_id: int, automation_id: int):
    return f"Delete {supplier_id} automation with ID: {automation_id}."

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