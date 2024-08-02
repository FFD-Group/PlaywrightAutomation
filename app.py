from flask import Flask, g, json, render_template, request, redirect, url_for
from automation_builder import AutomationBuilder
from database import get_db, query_db, insert_to_db, delete_from_db
from suppliers import get_suppliers

app = Flask(__name__, static_folder="static/")

@app.route("/")
def index():
    suppliers = get_suppliers()
    return render_template("index.html", suppliers=suppliers)

@app.route("/automations/download/save", methods=['POST'])
def save_download():
    data = request.get_json()
    print(data)
    try:
        ## INSERT SUPPLIER ROW
        insert_to_db(
            "INSERT OR IGNORE INTO suppliers (id, name) VALUES (:id,:name)",
            {"id":int(data["supplier_id"]), "name":data["supplier_name"]}
        )
        inserted = insert_to_db(
            "INSERT INTO automations (type, url, location, name, supplier_id) VALUES (:type,:url,:location,:name,:supplier_id)", #(type, url, location, name, supplier_id) 
            {"type":1, "url":data["download_url"], "location":data["save_location"], "name":data["automation_name"], "supplier_id":int(data["supplier_id"])}
        )
        return json.dumps(inserted)
    except Exception as e:
        print(e)

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

@app.route("/automation/<int:supplier_id>/<int:automation_id>/delete", methods=['DELETE'])
def delete_automation(supplier_id: int, automation_id: int):
    deleted_automations = delete_from_db("DELETE FROM automations WHERE id = ? AND supplier_id = ?", (automation_id, supplier_id))
    result = {}
    if deleted_automations:
        result = [dict(row) for row in deleted_automations]
        print(result)
    return result

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