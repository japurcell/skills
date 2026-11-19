#!/usr/bin/env python3
"""Build per-assignment before/after evidence from controlled host events."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_records(source: Path) -> list[dict]:
    events = [json.loads(line) for line in source.read_text().splitlines()]
    output = []
    for number in range(1, 17):
        case_id = f"case{number:02d}"
        own = [event for event in events if event.get("case_id") == case_id]
        route = next((event for event in own if event.get("kind") == "route"), None)
        controls = next((event for event in own if event.get("kind") == "host_controls"), None)
        after = [event for event in own if event.get("kind") in ("dispatch", "reuse")]
        output.append({
            "case_id": case_id,
            "before": {
                "router_invocation": route.get("argv") if route else None,
                "router_input": route.get("input") if route else None,
                "router_output_unchanged": route.get("result") if route else None,
                "host_controls": controls.get("controls") if controls else None,
            },
            "after": {
                "actual_dispatch_or_reuse_events": after,
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
