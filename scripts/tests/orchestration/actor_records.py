#!/usr/bin/env python3
"""Check the saved coordination.json in the project directory for a dispatch phase."""

import argparse
import json
from pathlib import Path


BEFORE = {
    "recorded_at": ("string",), "assignment_id": ("string",),
    "router_argv": ("array", "string"), "router_request": ("object",),
    "router_output": ("object",), "intended_child_controls": ("object",),
    "parent_controls": ("object",),
}
AFTER = {**BEFORE, "actual_args": ("object",), "worker_id": ("string", "null"),
         "observed_worker_model": ("string", "null"), "blocker": ("string", "null"),
         "override_fallback": ("string", "object", "null")}
RECORDS = {"before": BEFORE, "after": AFTER}
_JSON_TYPES = {dict: "object", list: "array", str: "string", type(None): "null"}


def coordination_schema():
    def object_schema(properties):
        return {"type": "object", "required": list(properties),
                "additionalProperties": False, "properties": properties}

    return object_schema({name: object_schema({key: {"type": list(types)}
                                               for key, types in fields.items()})
                          for name, fields in RECORDS.items()})


def field_failures(name, record):
    if not isinstance(record, dict):
        yield (), f"{name} gate record is missing or malformed"
        return
    fields = RECORDS[name]
    for key, types in fields.items():
        if key not in record:
            yield (), f"{name} gate record lacks {key}"
        elif _JSON_TYPES.get(type(record[key])) not in types:
            yield (key,), f"{name} gate record has malformed {key}"


def check_saved_record(phase):
    document = json.loads(Path("coordination.json").read_text(encoding="utf-8"))
    if not isinstance(document, dict) or document.keys() != RECORDS.keys():
        raise ValueError("expected before and after at the document root")
    if phase == "before" and document["after"] is not None:
        raise ValueError("after must be null before dispatch")
    for name in (("before",) if phase == "before" else ("before", "after")):
        record = document[name]
        for _, message in field_failures(name, record):
            raise ValueError(message)
        extra = record.keys() - RECORDS[name].keys()
        if extra:
            raise ValueError(f"unexpected fields in {name}: {', '.join(sorted(extra))}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=RECORDS)
    phase = parser.parse_args().phase
    try:
        check_saved_record(phase)
    except (OSError, ValueError) as error:
        parser.exit(1, f"coordination.json: {error}\n")
    print(f"coordination.json valid for {phase}")
