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
        return "route"
    return "unclassified router access" if ambiguous else None


def route_matches(candidate, args):
    if not isinstance(candidate, dict) or candidate.get("model") != args["model"]:
        return False
    effort = candidate["reasoning_effort"]
    if candidate["effort_policy"] == "host_default":
        return effort is None and "reasoning_effort" not in args
    return (candidate["effort_policy"] == "explicit" and isinstance(effort, str)
            and bool(effort) and args.get("reasoning_effort") == effort)


def authorized(route, args, blocked_models):
    if not route or route.get("route_available") is not True or not route.get("reason"):
        return False
    if args["model"] in blocked_models:
        return False
    candidate = route.get("fallback") if route["model"] in blocked_models else route
    return route_matches(candidate, args)


def model_rejected(output, model):
    # Only a host error for this spawn can establish a model-wide blocker.
    try:
        receipt = json.loads(output)
    except (ValueError, TypeError):
        return False
    error = receipt.get("error") if isinstance(receipt, dict) else None
    if not isinstance(error, str):
        return False
    return bool(re.fullmatch(
        rf"model(?: ['\"]?{re.escape(model)}['\"]?)? (?:is )?(?:unavailable|not supported)\.?",
        error.strip(), re.IGNORECASE))


def read_spawn_args(payload):
    args = json.loads(payload.get("arguments") or "{}")
    if not isinstance(args.get("model"), str) or not args["model"]:
        raise ValueError("insufficient evidence: missing spawn model or arguments")
    return args


def grade(rows, caller):
    events = []
    workers = set()
    route = None
    spawn_args = None
    worker_args = None
    pending_spawns = {}
    blocked_models = set()
    for line, row in enumerate(rows, 1):
        payload = row["payload"]
        label = None
        if row["type"] == "response_item" and payload.get("type") == "function_call":
            if payload["name"] == "spawn_agent":
                spawn_args = read_spawn_args(payload)
                if authorized(route, spawn_args, blocked_models):
                    label = "spawn"
                    pending_spawns[payload["call_id"]] = (len(events), spawn_args["model"])
                else:
                    label = "unauthorized spawn"
            elif payload["name"] == "followup_task":
                can_reuse = worker_args and authorized(route, worker_args, blocked_models)
                label = "followup" if can_reuse else "unauthorized followup"
        elif row["type"] == "response_item" and payload.get("type") == "function_call_output":
            pending = pending_spawns.pop(payload.get("call_id"), None)
            if pending:
                index, model = pending
                if model_rejected(payload["output"], model) and index == len(events) - 1:
                    events[index] = (events[index][0], "rejected spawn")
                    blocked_models.add(model)
                    spawn_args = None
        elif row["type"] == "event_msg" and payload.get("type") == "item_completed":
            item = payload["item"]
            if item["type"] == "CommandExecution":
                label = command_event(item, caller)
                if label == "route":
                    route = json.loads(item["aggregated_output"])
            elif item["type"] == "SubAgentActivity":
                label = item["kind"]
                workers.add(item["agent_thread_id"])
                if label == "started":
                    worker_args = spawn_args
        if label:
            events.append((line, label))
    labels = [label for _, label in events]
    # Caller and router instructions can be read in the same preparation phase.
    expected = ["read", "help", "route", "spawn", "started", "completed",
                "route", "followup", "interacted", "completed"]
    sequence = [label for label in labels if label not in {"caller", "rejected spawn"}]
    passed = ("caller" in labels and sequence == expected
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
