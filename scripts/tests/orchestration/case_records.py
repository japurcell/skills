#!/usr/bin/env python3
"""Build per-assignment before/after evidence from controlled host events."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from case_trace import CASE_IDS, read_cases


def build_records(source: Path) -> list[dict]:
    cases = read_cases(source)
    output = []
    for case_id in dict.fromkeys((*CASE_IDS, *cases)):
        case = cases[case_id]
        route = next(iter(case.of_kind("route")), {})
        controls = next(iter(case.of_kind("host_controls")), {})
        output.append({
            "case_id": case_id,
            "events": case.rows,
            "ordering_issues": case.ordering_issues,
            "before": {
                "router_invocation": route.get("argv"),
                "router_input": route.get("input"),
                "router_output_unchanged": route.get("result"),
                "host_controls": controls.get("controls"),
            },
            "after": {
                "actual_dispatch_or_reuse_events": case.actions,
            },
        })
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("events", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    records = build_records(args.events)
    args.out.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in records))
    print(json.dumps({"source": str(args.events), "records": len(records), "output": str(args.out)}))


if __name__ == "__main__":
    main()
