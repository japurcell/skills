"""Shape of the actor-written coordination document."""


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
