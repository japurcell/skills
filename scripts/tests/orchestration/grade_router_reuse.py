"""Grade the router-reuse fixture against one native Codex parent rollout."""
import argparse
import json
from pathlib import Path
import re
import shlex


def command_event(item, caller):
    # Match executed commands, not mentions in prompts or coordination records.
    command = item["command"][-1]
    if "SKILL.md" not in command and "route.py" not in command:
        return None
    output = item["aggregated_output"]
    ambiguous = ("subagent-model-router/SKILL.md" in command
                 or "name: subagent-model-router" in output or "usage: route.py" in output)
    direct = re.match(r"^(?:rtk )?(?:proxy )?(?:cat|read|python3?) +", command)
    if not direct:
        return "unclassified router access" if ambiguous else None
    argv = shlex.split(command)
    if argv[:1] == ["rtk"]:
        argv = argv[1:]
    if argv[:1] == ["proxy"]:
        argv = argv[1:]
    if argv[:1] in (["cat"], ["read"]) and len(argv) == 2:
        for skill, label in [(caller, "caller"), ("subagent-model-router", "read")]:
            if argv[1].endswith(f"/{skill}/SKILL.md"):
                return label if item["exit_code"] == 0 else "failed read"
    if (len(argv) >= 2 and Path(argv[0]).name in {"python", "python3"}
            and argv[1].endswith("/subagent-model-router/scripts/route.py")):
        if any(token in argv for token in ("&&", ";", "||", "|")):
            return "compound invocation"
        if item["exit_code"] != 0:
            return "failed invocation"
        if "--help" in argv or "-h" in argv:
            return "help"
        route = json.loads(item["aggregated_output"])
        return "route" if route.get("reason") else "missing route"
    return "unclassified router access" if ambiguous else None


def grade(rows, caller):
    events = []
    workers = set()
    for line, row in enumerate(rows, 1):
        payload = row["payload"]
        label = None
        if row["type"] == "response_item" and payload.get("type") == "function_call":
            label = {"spawn_agent": "spawn", "followup_task": "followup"}.get(payload["name"])
        elif row["type"] == "event_msg" and payload.get("type") == "item_completed":
            item = payload["item"]
            if item["type"] == "CommandExecution":
                label = command_event(item, caller)
            elif item["type"] == "SubAgentActivity":
                label = item["kind"]
                workers.add(item["agent_thread_id"])
        if label:
            events.append((line, label))
    labels = [label for _, label in events]
    # Caller and router instructions can be read in the same preparation phase.
    expected = ["read", "help", "route", "spawn", "started", "completed",
                "route", "followup", "interacted", "completed"]
    passed = ("caller" in labels and [x for x in labels if x != "caller"] == expected
              and len(workers) == 1 and all(workers))
    return {"passed": passed, "events": events, "workers": sorted(workers)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("caller", choices=["delegate-to-subagents", "execplan-implement"])
    parser.add_argument("rollout", type=Path)
    args = parser.parse_args()
    try:
        with args.rollout.open(encoding="utf-8") as stream:
            result = grade(map(json.loads, stream), args.caller)
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError) as error:
        parser.exit(2, f"Invalid or unsupported rollout: {error}\n")
    print(json.dumps(result))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
