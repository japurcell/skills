#!/usr/bin/env python3
"""Extract the ordered host-tool calls from a local Codex JSONL trace."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def extract(source: Path) -> list[dict]:
    output = []
    for index, line in enumerate(source.read_text().splitlines()):
        event = json.loads(line)
        item = event.get("item")
        if not isinstance(item, dict) or item.get("type") != "command_execution":
            continue
        output.append({
            "event_index": index,
            "phase": event.get("type"),
            "call_id": item.get("id"),
            "command": item.get("command"),
            "status": item.get("status"),
            "exit_code": item.get("exit_code"),
        })
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    rows = extract(args.source)
    args.out.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))
    print(json.dumps({"source": str(args.source), "events": len(rows), "output": str(args.out)}))


if __name__ == "__main__":
    main()
