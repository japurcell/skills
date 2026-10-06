"""Bundled agent-brain command-line implementation."""

from __future__ import annotations

import json
from pathlib import Path


_VERSION_PATH = Path(__file__).resolve().parents[2] / "schemas" / "version.json"
try:
    _version_record = json.loads(_VERSION_PATH.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    raise RuntimeError(f"cannot read agent-brain version metadata at {_VERSION_PATH}: {exc}") from exc

if (
    not isinstance(_version_record, dict)
    or set(_version_record) != {"schema_version", "name", "bundle_version", "minimum_python"}
    or type(_version_record.get("schema_version")) is not int
    or _version_record["schema_version"] != 1
    or _version_record["name"] != "agent-brain"
    or not isinstance(_version_record["bundle_version"], str)
    or not _version_record["bundle_version"].strip()
    or not isinstance(_version_record["minimum_python"], str)
    or not _version_record["minimum_python"].strip()
):
    raise RuntimeError(f"invalid agent-brain version metadata at {_VERSION_PATH}")

__version__ = _version_record["bundle_version"]
