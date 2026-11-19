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

    expected_ids = {f"case{number:02d}" for number in range(1, 17)}
    if not path.is_file():
        case_check("all", "trace file exists", False, str(path))
        return {"source": str(path), "passed": 0, "total": len(checks), "verdict": "fail", "checks": checks}
    try:
        rows = [json.loads(line) for line in path.read_text().splitlines()]
    except (OSError, json.JSONDecodeError) as error:
        case_check("all", "trace parses", False, str(error))
        return {"source": str(path), "passed": 0, "total": len(checks), "verdict": "fail", "checks": checks}
    if any(not isinstance(row, dict) or not isinstance(row.get("kind"), str) or
           not isinstance(row.get("case_id"), str) for row in rows):
        case_check("all", "trace rows have event and case IDs", False, "malformed JSONL record")
        return {"source": str(path), "passed": 0, "total": len(checks), "verdict": "fail", "checks": checks}

    route_rows = [row for row in rows if row["kind"] == "route"]
    control_rows = [row for row in rows if row["kind"] == "host_controls"]
    route_ids = [row["case_id"] for row in route_rows]
    control_ids = [row["case_id"] for row in control_rows]
    if (set(route_ids) != expected_ids or len(route_ids) != len(expected_ids) or
            set(control_ids) != expected_ids or len(control_ids) != len(expected_ids)):
        case_check("all", "expected unique router and host input IDs", False,
                   {"expected": sorted(expected_ids), "route_ids": route_ids, "host_ids": control_ids})
        return {"source": str(path), "passed": 0, "total": len(checks), "verdict": "fail", "checks": checks}

    routes = {row["case_id"]: row.get("result", {}) for row in route_rows}
    bad_routes = [row["case_id"] for row in route_rows
                  if row.get("exit_code") != 0 or not isinstance(row.get("result"), dict) or
                  not isinstance(row.get("result", {}).get("route_available"), bool) or
                  "model" not in row.get("result", {}) or "effort_policy" not in row.get("result", {})]
    if bad_routes:
        case_check("all", "every router call returned a valid JSON route", False, bad_routes)
        return {"source": str(path), "passed": 0, "total": len(checks), "verdict": "fail", "checks": checks}
    dispatches = [row for row in rows if row["kind"] == "dispatch"]
    reuses = [row for row in rows if row["kind"] == "reuse"]
    unexpected = sorted({row["case_id"] for row in dispatches + reuses} - expected_ids)
    case_check("all", "no arbitrary dispatch or reuse IDs", not unexpected, unexpected)

    case_check("all", "one router call per case", len(route_rows) == 16 and len(routes) == 16,
               {"route_count": len(route_rows), "unique_case_ids": len(routes)})
    case_check("all", "host facts captured for every case", len(control_rows) == 16,
               {"host_control_count": len(control_rows)})

    def ds(case_id: str) -> list[dict]:
        return [row for row in dispatches if row.get("case_id") == case_id]

    def rs(case_id: str) -> list[dict]:
        return [row for row in reuses if row.get("case_id") == case_id]

    def expect(case_id: str, condition: bool, evidence: object) -> None:
        case_check(case_id, "observed action matches controlled requirement", condition, evidence)

    def completed(row: dict) -> bool:
        return row.get("result") == "worker_completed" and bool(row.get("worker_id"))

    d = ds("case01")
    disallowed = routes["case01"].get("model")
    expect("case01", not any(row.get("model") == disallowed for row in d), d)
    d = ds("case02"); expect("case02", len(d) == 1 and d[0].get("model") == routes["case02"].get("model") and completed(d[0]), d)
    d = ds("case03")
    primary_model = routes["case03"].get("model")
    fallback_model = (routes["case03"].get("fallback") or {}).get("model")
    primary = [row for row in d if row.get("model") == primary_model]
    fallback = [row for row in d if row.get("model") == fallback_model]
    expect("case03", len(primary) == 1 and primary[0].get("result") == "model_wide_rejection" and
           len(fallback) == 1 and completed(fallback[0]) and fallback[0].get("fallback_tier") is not None and
           fallback[0].get("effort") is None, d)
    d = ds("case04"); expect("case04", len(d) == 1 and d[0].get("model") == routes["case04"].get("model") and d[0].get("effort") == "high" and completed(d[0]), d)
    d = ds("case05"); expect("case05", len(d) == 1 and d[0].get("model") == routes["case05"].get("model") and d[0].get("effort") is None and completed(d[0]), d)
    d = ds("case06"); expect("case06", not routes["case06"].get("route_available") and not d, {"route": routes["case06"], "dispatches": d})
    d = ds("case07"); expect("case07", len(d) == 1 and d[0].get("model") == "gpt-9-user-requested" and completed(d[0]), d)
    d = ds("case08"); expect("case08", not d, d)
    d = ds("case09"); expect("case09", not d, d)
    d = ds("case10"); expect("case10", not d, d)
    d = ds("case11")
    expect("case11", not any(row.get("model") == routes["case11"].get("model") for row in d) and
           len(d) == 1 and d[0].get("model") == (routes["case11"].get("fallback") or {}).get("model") and
           d[0].get("fallback_tier") is not None and completed(d[0]), d)
    d = ds("case12"); r = rs("case12"); expect("case12", not r and len(d) == 1 and d[0].get("model") == routes["case12"].get("model") and completed(d[0]), {"dispatch": d, "reuse": r})
    d = ds("case13"); r = rs("case13"); expect("case13", len(r) == 1 and r[0].get("result") == "worker_reused" and not d and r[0].get("existing_model") == r[0].get("selected_model") and r[0].get("useful_context") and not r[0].get("original_effort_override"), {"dispatch": d, "reuse": r})
    d = ds("case14"); r = rs("case14"); expect("case14", not r and len(d) == 1 and completed(d[0]), {"dispatch": d, "reuse": r})
    d = ds("case15"); r = rs("case15"); expect("case15", len(r) == 1 and r[0].get("result") == "worker_reused" and not d and r[0].get("existing_model") == r[0].get("selected_model") and r[0].get("existing_effort") == r[0].get("selected_effort") and r[0].get("useful_context"), {"dispatch": d, "reuse": r})
    d = ds("case16"); r = rs("case16"); expect("case16", not r and len(d) == 1 and completed(d[0]), {"dispatch": d, "reuse": r})

    for case_id in ("case06", "case08", "case09", "case10"):
        r = rs(case_id)
        case_check(case_id, "no reuse on blocked route/control", not r, r)

    passed = sum(item["pass"] for item in checks)
    return {"source": str(path), "passed": passed, "total": len(checks),
            "verdict": "pass" if passed == len(checks) else "fail", "checks": checks}


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
