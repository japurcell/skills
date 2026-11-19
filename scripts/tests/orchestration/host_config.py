#!/usr/bin/env python3
"""Capture only the configured Codex model and effort used by a trial."""
from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path


def capture(config: Path, command_record: Path) -> dict:
    parsed = tomllib.loads(config.read_text())
    command = json.loads(command_record.read_text())
    argv = command.get("argv", [])
    return {
        "configured_default_model": parsed.get("model"),
        "configured_default_effort": parsed.get("model_reasoning_effort"),
        "config_path": str(config),
        "model_flag_in_actor_command": "--model" in argv or "-m" in argv,
        "effort_flag_in_actor_command": "--effort" in argv,
        "resolved_model_emitted_in_codex_jsonl": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command_record", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--config", type=Path, default=Path.home() / ".codex" / "config.toml")
    args = parser.parse_args()
    result = capture(args.config, args.command_record)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "model_flag_in_actor_command": result["model_flag_in_actor_command"]}))


if __name__ == "__main__":
    main()
