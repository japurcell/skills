import logging
import re

logger = logging.getLogger(__name__)


def record_download(name: str) -> None:
    logger.info("download requested for %s", name)


def compile_filter(pattern: str):
    return re.compile(pattern)