from flask import Flask, render_template

from download_lincat_file import *

app = Flask(__name__, static_folder="static/")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/automation-builder")
def automation_builder():
    return render_template("automation.html")

@app.route("/test-automation/<string:supplier>")
def test_automation(supplier: str):
    ## test the automation for the supplier passed
    download_file()
    return "Tested!"