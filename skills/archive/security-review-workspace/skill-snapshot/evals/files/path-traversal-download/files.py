from pathlib import Path

from flask import Flask, abort, request, send_file

app = Flask(__name__)
DATA_DIR = Path("/srv/reports")


@app.get("/download")
def download_report():
    requested_name = request.args["name"]
    return send_file(DATA_DIR / requested_name)