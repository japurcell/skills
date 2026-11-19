#!/usr/bin/env python3
"""Grade controlled W1 choices only from router/host boundary events."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def grade(path: Path) -> dict:
    checks = []

    def case_check(case_id: str, name: str, condition: bool, evidence: object) -> None:
        checks.append({"case_id": case_id, "check": name, "pass": bool(condition), "evidence": evidence})

    def verdict() -> dict:
        passed = sum(item["pass"] for item in checks)
        return {"source": str(path), "passed": passed, "total": len(checks),
                "verdict": "pass" if passed == len(checks) else "fail", "checks": checks}

    expected_ids = {f"case{number:02d}" for number in range(1, 17)}
    if not path.is_file():
        case_check("all", "trace file exists", False, str(path))
        return verdict()
    try:
        rows = [json.loads(line) for line in path.read_text().splitlines()]
    except (OSError, json.JSONDecodeError) as error:
        case_check("all", "trace parses", False, str(error))
        return verdict()
    if any(not isinstance(row, dict) or not isinstance(row.get("kind"), str) or
           not isinstance(row.get("case_id"), str) for row in rows):
        case_check("all", "trace rows have event and case IDs", False, "malformed JSONL record")
        return verdict()

    route_rows = [row for row in rows if row["kind"] == "route"]
    control_rows = [row for row in rows if row["kind"] == "host_controls"]
    route_ids = [row["case_id"] for row in route_rows]
    control_ids = [row["case_id"] for row in control_rows]
    if (set(route_ids) != expected_ids or len(route_ids) != len(expected_ids) or
            set(control_ids) != expected_ids or len(control_ids) != len(expected_ids)):
        case_check("all", "expected unique router and host input IDs", False,
                   {"expected": sorted(expected_ids), "route_ids": route_ids, "host_ids": control_ids})
        return verdict()

    routes = {row["case_id"]: row.get("result", {}) for row in route_rows}
    bad_routes = [row["case_id"] for row in route_rows
                  if row.get("exit_code") != 0 or not isinstance(row.get("result"), dict) or
                  not isinstance(row.get("result", {}).get("route_available"), bool) or
                  "model" not in row.get("result", {}) or "effort_policy" not in row.get("result", {})]
    if bad_routes:
        case_check("all", "every router call returned a valid JSON route", False, bad_routes)
        return verdict()
    dispatches = [row for row in rows if row["kind"] == "dispatch"]
    reuses = [row for row in rows if row["kind"] == "reuse"]
    unexpected = sorted({row["case_id"] for row in dispatches + reuses} - expected_ids)
    case_check("all", "no arbitrary dispatch or reuse IDs", not unexpected, unexpected)

    case_check("all", "one router call per case", len(route_rows) == 16 and len(routes) == 16,
               {"route_count": len(route_rows), "unique_case_ids": len(routes)})
    case_check("all", "host facts captured for every case", len(control_rows) == 16,
               {"host_control_count": len(control_rows)})

    def expect(case_id: str, condition: bool, evidence: object) -> None:
        case_check(case_id, "observed action matches controlled requirement", condition, evidence)

    def completed(row: dict) -> bool:
        return row.get("result") == "worker_completed" and bool(row.get("worker_id"))

    def dispatches_for(case_id):
        return [row for row in dispatches if row["case_id"] == case_id]

    def reuses_for(case_id):
        return [row for row in reuses if row["case_id"] == case_id]

    def dispatched_model(attempts, model):
        return len(attempts) == 1 and attempts[0].get("model") == model and completed(attempts[0])

    attempts = dispatches_for("case01")
    disallowed = routes["case01"].get("model")
    expect("case01", all(row.get("model") != disallowed for row in attempts), attempts)

    attempts = dispatches_for("case02")
    expect("case02", dispatched_model(attempts, routes["case02"].get("model")), attempts)

    attempts = dispatches_for("case03")
    primary_model = routes["case03"].get("model")
    fallback_model = (routes["case03"].get("fallback") or {}).get("model")
    primary = [row for row in attempts if row.get("model") == primary_model]
    fallback = [row for row in attempts if row.get("model") == fallback_model]
    expect("case03", len(primary) == 1 and primary[0].get("result") == "model_wide_rejection" and
           len(fallback) == 1 and completed(fallback[0]) and fallback[0].get("fallback_tier") is not None and
           fallback[0].get("effort") is None, attempts)

    for case_id, effort in (("case04", "high"), ("case05", None)):
        attempts = dispatches_for(case_id)
        expect(case_id, dispatched_model(attempts, routes[case_id].get("model")) and
               attempts[0].get("effort") == effort, attempts)

    attempts = dispatches_for("case06")
    expect("case06", not routes["case06"].get("route_available") and not attempts,
           {"route": routes["case06"], "dispatches": attempts})
    attempts = dispatches_for("case07")
    expect("case07", dispatched_model(attempts, "gpt-9-user-requested"), attempts)

    for case_id in ("case08", "case09", "case10"):
        attempts = dispatches_for(case_id)
        expect(case_id, not attempts, attempts)

    attempts = dispatches_for("case11")
    route = routes["case11"]
    expect("case11", len(attempts) == 1 and attempts[0].get("model") != route.get("model") and
           dispatched_model(attempts, (route.get("fallback") or {}).get("model")) and
           attempts[0].get("fallback_tier") is not None, attempts)

    def expect_new_worker(case_id, *, match_route=False):
        attempts = dispatches_for(case_id)
        reused = reuses_for(case_id)
        valid = not reused and len(attempts) == 1 and completed(attempts[0])
        if valid and match_route:
            valid = attempts[0].get("model") == routes[case_id].get("model")
        expect(case_id, valid, {"dispatch": attempts, "reuse": reused})

    def expect_reuse(case_id, *, host_default):
        attempts = dispatches_for(case_id)
        reused = reuses_for(case_id)
        valid = not attempts and len(reused) == 1
        if valid:
            worker = reused[0]
            if host_default:
                effort_matches = not worker.get("original_effort_override")
            else:
                effort_matches = worker.get("existing_effort") == worker.get("selected_effort")
            valid = (worker.get("result") == "worker_reused" and worker.get("useful_context") and
                     worker.get("existing_model") == worker.get("selected_model") and effort_matches)
        expect(case_id, valid, {"dispatch": attempts, "reuse": reused})

    expect_new_worker("case12", match_route=True)
    expect_reuse("case13", host_default=True)
    expect_new_worker("case14")
    expect_reuse("case15", host_default=False)
    expect_new_worker("case16")

    for case_id in ("case06", "case08", "case09", "case10"):
        reused = reuses_for(case_id)
        case_check(case_id, "no reuse on blocked route/control", not reused, reused)

    return verdict()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("events", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = grade(args.events)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.out:
        args.out.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
