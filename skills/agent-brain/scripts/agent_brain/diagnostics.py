"""Read-only installed software and managed activation diagnoses."""
from __future__ import annotations
from pathlib import Path

from .setup import checked_local, checked_journal, text, EXPECTED
from .software import validate_software


def diagnose(config, root: Path) -> dict:
    result = {"activation_status": "uninitialized", "software_status": "unconfigured", "integrations": []}
    try:
        activation = checked_local(root)
        if activation:
            status = activation["status"]
            journal = checked_journal(root, activation["journal_path"])
            result["activation_status"] = status if journal["status"] == "applied" else "incomplete"
        if config and config.software:
            validate_software(config.software)
            result["software_status"] = "available"
        if config:
            from .native import support_record
            for name, provider in config.providers.items():
                status = "disabled"
                if provider["enabled"]:
                    try:
                        if provider["kind"] == "native":
                            support_record(config, root, provider)
                        status = "available"
                    except (OSError, ValueError, KeyError, TypeError):
                        status = "unsupported"
                result["integrations"].append({"id": name, "status": status})
        if text(root, EXPECTED) is not None and not config:
            result["activation_status"] = "incomplete"
            result["state_status"] = "unavailable"
        if text(root, EXPECTED) is not None and config:
            from .state import StateStore
            try:
                StateStore(root, config.state_dir).read()
            except (OSError, ValueError):
                result["activation_status"] = "incomplete"
    except (OSError, ValueError, KeyError, TypeError):
        result["activation_status"] = "unavailable"
        if config and config.software:
            result["software_status"] = "unavailable"
    return result
