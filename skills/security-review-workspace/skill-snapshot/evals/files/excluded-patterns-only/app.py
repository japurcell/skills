import logging
import re

from flask import Flask, request

app = Flask(__name__)
logger = logging.getLogger(__name__)


@app.get("/search")
def search() -> dict[str, str]:
    logger.info("search query=%s", request.args.get("q", ""))
    matcher = re.compile(request.args.get("q", ".*"))
    matcher.search("")
    return {"query": request.args.get("q", "")}