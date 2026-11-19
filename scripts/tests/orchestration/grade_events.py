#!/usr/bin/env python3
"""Grade controlled W1 choices only from router/host boundary events."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from case_trace import CASE_IDS, read_cases


def completed(row: dict) -> bool:
    return row.get("result") == "worker_completed" and bool(row.get("worker_id"))


def fallback_failure(case, route):
    actions = case.actions
    if len(actions) != 2 or any(row["kind"] != "dispatch" for row in actions):
        return "expected exactly two dispatch attempts"
    primary, fallback = actions
    primary_model = route.get("model")
    routed_fallback = route.get("fallback")
    fallback_model = routed_fallback.get("model") if isinstance(routed_fallback, dict) else None
    if primary.get("model") == fallback_model and fallback.get("model") == primary_model:
        return "primary and fallback receipts are reversed"
    if (not primary_model or not fallback_model or primary_model == fallback_model
            or primary.get("model") != primary_model or primary.get("result") != "model_wide_rejection"
            or fallback.get("model") != fallback_model or not completed(fallback)
            or fallback.get("fallback_tier") is None or fallback.get("effort") is not None):
        return "expected primary rejection and successful routed fallback"
    if len(case.of_kind("dispatch_start")) > 2:
        return "extra dispatch start"
    follows_rejection = case.order_after_receipt(primary, fallback)
    if follows_rejection is None:
        return "insufficient ordering evidence"
    if not follows_rejection:
        return "fallback start overlaps the primary attempt"
    return None


def grade(path: Path) -> dict:
    checks = []

    def case_check(case_id: str, name: str, condition: bool, evidence: object) -> None:
        checks.append({"case_id": case_id, "check": name, "pass": bool(condition), "evidence": evidence})

    def verdict() -> dict:
        passed = sum(item["pass"] for item in checks)
        return {"source": str(path), "passed": passed, "total": len(checks),
                "verdict": "pass" if passed == len(checks) else "fail", "checks": checks}

    expected_ids = set(CASE_IDS)
    if not path.is_file():
        case_check("all", "trace file exists", False, str(path))
        return verdict()
    try:
        cases = read_cases(path)
    except (OSError, ValueError) as error:
        case_check("all", "trace parses", False, str(error))
        return verdict()

    route_rows = [row for case in cases.values() for row in case.of_kind("route")]
    control_rows = [row for case in cases.values() for row in case.of_kind("host_controls")]
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
    unexpected = sorted(set(cases) - expected_ids)
    case_check("all", "no arbitrary dispatch or reuse IDs", not unexpected, unexpected)

    case_check("all", "one router call per case", len(route_rows) == 16 and len(routes) == 16,
               {"route_count": len(route_rows), "unique_case_ids": len(routes)})
    case_check("all", "host facts captured for every case", len(control_rows) == 16,
               {"host_control_count": len(control_rows)})

    def expect(case_id: str, condition: bool, evidence: object) -> None:
        case_check(case_id, "observed action matches controlled requirement", condition, evidence)

    def dispatches_for(case_id):
        return cases[case_id].of_kind("dispatch")

    def reuses_for(case_id):
        return cases[case_id].of_kind("reuse")

    def dispatched_model(attempts, model):
        return len(attempts) == 1 and attempts[0].get("model") == model and completed(attempts[0])

    attempts = dispatches_for("case01")
    disallowed = routes["case01"].get("model")
    expect("case01", all(row.get("model") != disallowed for row in attempts), attempts)

    attempts = dispatches_for("case02")
    expect("case02", dispatched_model(attempts, routes["case02"].get("model")), attempts)

    case = cases["case03"]
    reason = fallback_failure(case, routes["case03"])
    expect("case03", reason is None, {"actions": case.actions, "reason": reason,
                                      "ordering_issues": case.ordering_issues})

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
