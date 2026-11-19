#!/usr/bin/env python3
"""Controlled, observable host boundary for W1 wording trials."""
from __future__ import annotations

import json
import fcntl
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PROJECT = Path(os.environ.get("W1_PROJECT", ".")).resolve()
DATA = PROJECT / ".w1" / "cases.json"
EVENTS = PROJECT / ".w1" / "events.jsonl"
ROUTES = PROJECT / ".w1" / "routes"
OUTCOMES = Path(os.environ.get("W1_OUTCOMES", ""))
TIER_RANK = {"Fast": 0, "Standard": 1, "Premium": 2}


def cases() -> dict[str, dict]:
    rows = {item["id"]: item for item in json.loads(DATA.read_text())["cases"]}
    outcomes = json.loads(OUTCOMES.read_text()) if OUTCOMES.is_file() else {}
    for case_id, row in rows.items():
        row["simulator"] = {"dispatch_outcomes": outcomes.get(case_id, {})}
    return rows


def record(event: dict) -> None:
    with EVENTS.open("a+") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        stream.seek(0)
        event["sequence"] = sum(1 for _ in stream)
        stream.seek(0, os.SEEK_END)
        stream.write(json.dumps(event, sort_keys=True) + "\n")
        stream.flush()
        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def latest_route(case_id: str) -> dict:
    for event in reversed([json.loads(line) for line in EVENTS.read_text().splitlines()]):
        if event["case_id"] == case_id and event["kind"] == "route":
            return event["result"]
    raise RuntimeError(f"route38 must run before a dispatch decision for {case_id}")


def catalog_tier(model: str, floor: str | None = None) -> str | None:
    catalog_path = PROJECT / ".agents" / "skills" / "subagent-model-router" / "reference" / "catalog.json"
    catalog = json.loads(catalog_path.read_text())
    matching = []
    for tier, rows in catalog["tiers"].items():
        if any(row["model"] == model for row in rows):
            if floor is None or TIER_RANK.get(tier, -1) >= TIER_RANK.get(floor, 99):
                matching.append(tier)
    return min(matching, key=TIER_RANK.get) if matching else None


def main() -> int:
    started_ns = time.time_ns()
    command = Path(sys.argv[0]).name
    args = sys.argv[1:]
    available = cases()
    if command == "case38":
        if args and args[0] == "list":
            print(json.dumps([{"id": row["id"], "task": row["route"].get("task", {})}
                              for row in available.values()], indent=2))
            return 0
        print("usage: case38 list", file=sys.stderr)
        return 2
    if not args or args[0] not in available:
        print("unknown case id", file=sys.stderr)
        return 2
    case_id = args[0]
    case = available[case_id]
    if command == "route38":
        request = case["route"]
        ROUTES.mkdir(parents=True, exist_ok=True)
        route_input = ROUTES / f"{case_id}.json"
        route_input.write_text(json.dumps(request, indent=2) + "\n")
        proc = subprocess.run([sys.executable, str(PROJECT / ".w1" / "router" / "scripts" / "route.py"),
                              "--input", str(route_input)], text=True, capture_output=True)
        event = {"kind": "route", "case_id": case_id, "argv": ["route38", *args],
                 "call_started_ns": started_ns, "input": request,
                 "exit_code": proc.returncode, "stderr": proc.stderr}
        if proc.returncode == 0:
            event["result"] = json.loads(proc.stdout)
            record(event)
            print(json.dumps(event["result"], sort_keys=True))
            return 0
        record(event)
        print(proc.stderr, file=sys.stderr)
        return proc.returncode
    if command == "host38":
        policy = case["host"]
        record({"kind": "host_controls", "case_id": case_id, "argv": ["host38", *args],
                "call_started_ns": started_ns,
                "controls": policy})
        print(json.dumps(policy, sort_keys=True))
        return 0
    if command == "dispatch38":
        route = latest_route(case_id)
        if len(args) < 3 or args[1] != "--model":
            print("usage: dispatch38 CASE --model MODEL [--effort LEVEL]", file=sys.stderr)
            return 2
        model = args[2]
        effort = None
        if "--effort" in args:
            effort = args[args.index("--effort") + 1]
        policy = case["host"]
        simulator = case["simulator"]
        if route.get("route_available"):
            expected = {route.get("model")}
            fallback = route.get("fallback")
            if isinstance(fallback, dict):
                expected.add(fallback.get("model"))
            if model not in expected:
                result = "wrong_model"
            else:
                result = None
        elif policy.get("exact_user_model") == model:
            result = None
        else:
            result = "route_unavailable_without_exact_override"
        if result is None and model in policy.get("known_disallowed_models", []):
            result = "host_restriction"
        if result is None and not policy.get("model_control", False):
            result = "missing_model_control"
        selected_route = route
        fallback_tier = None
        if isinstance(route.get("fallback"), dict) and model == route["fallback"].get("model"):
            selected_route = {**route, **route["fallback"]}
            fallback_tier = catalog_tier(model, route.get("floor"))
            if fallback_tier is None:
                result = "fallback_below_capability_floor"
        if result is None and route.get("effort_policy") == "explicit":
            expected_effort = policy.get("user_effort") or selected_route.get("reasoning_effort")
            if not policy.get("effort_control", False):
                result = "missing_effort_control"
            elif effort != expected_effort:
                result = "wrong_effort"
        elif result is None and effort is not None:
            result = "unexpected_effort_under_host_default"
        if result is None and policy.get("availability") == "unknown":
            previous = [row for row in (json.loads(line) for line in EVENTS.read_text().splitlines())
                        if row["case_id"] == case_id and row["kind"] == "dispatch" and row["model"] == model]
            result = "retry_forbidden" if previous and any(row["result"] == "model_wide_rejection" for row in previous) else result
        if result is None:
            result = simulator.get("dispatch_outcomes", {}).get(model, "host_rejection")
        worker_id = f"w1-{uuid.uuid5(uuid.NAMESPACE_DNS, case_id).hex[:12]}" if result == "worker_completed" else None
        event = {"kind": "dispatch", "case_id": case_id, "argv": ["dispatch38", *args],
                 "call_started_ns": started_ns,
                 "route": route, "model": model, "effort": effort,
                 "fallback_tier": fallback_tier, "result": result, "worker_id": worker_id}
        record(event)
        print(json.dumps(event, sort_keys=True))
        return 0
    if command == "reuse38":
        route = latest_route(case_id)
        policy = case["host"]
        reuse = policy.get("reuse")
        if not reuse:
            print("case has no existing worker", file=sys.stderr)
            return 2
        selected_model = route.get("model") or policy.get("exact_user_model")
        selected_effort = (policy.get("user_effort") or route.get("reasoning_effort")) \
            if route.get("effort_policy") == "explicit" else None
        if "--worker" not in args:
            print("usage: reuse38 CASE --worker WORKER_ID", file=sys.stderr)
            return 2
        worker_id = args[args.index("--worker") + 1]
        event = {"kind": "reuse", "case_id": case_id, "argv": ["reuse38", *args],
                 "call_started_ns": started_ns,
                 "route": route, "selected_model": selected_model, "selected_effort": selected_effort,
                 "existing_worker_id": reuse["existing_worker_id"],
                 "existing_model": reuse["existing_model"], "existing_effort": reuse.get("existing_effort"),
                 "useful_context": reuse["useful_context"],
                 "original_effort_override": reuse.get("original_effort_override", False),
                 "requested_worker_id": worker_id, "result": "worker_reused",
                 "host_enforces_reuse_eligibility": False}
        record(event)
        print(json.dumps(event, sort_keys=True))
        return 0
    print(f"unknown boundary command: {command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
