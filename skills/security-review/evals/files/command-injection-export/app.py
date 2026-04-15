from flask import Flask, abort, request
import subprocess

app = Flask(__name__)
AUTHORIZED_TOKENS = {"ops-token"}


@app.post("/archive")
def archive() -> dict[str, str]:
    if request.headers.get("X-Ops-Token") not in AUTHORIZED_TOKENS:
        abort(403)

    target = request.json["target"]
    result = subprocess.run(
        f"/usr/local/bin/archive-job --target {target}",
        shell=True,
        check=True,
        capture_output=True,
        text=True,
    )
    return {"status": "queued", "job": result.stdout.strip()}