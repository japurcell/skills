#!/usr/bin/env python3
"""Check native provider permission decisions for sanitized incident fixtures."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from tool_guard_corpus import PROVIDERS, decision, encode, envelope, fixtures, script_path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--script-root", type=Path, default=ROOT)
    parser.add_argument("--expected-behavior", choices=("baseline", "candidate"), default="candidate")
    args = parser.parse_args()
    failures = []
    count = 0
    with tempfile.TemporaryDirectory(prefix="guardian-public-fixtures-") as temporary:
        for provider in PROVIDERS:
            for fixture in fixtures():
                count += 1
                env = os.environ.copy()
                for key in ("SKIP_TOOL_GUARD", "TOOL_GUARD_ALLOWLIST"):
                    env.pop(key, None)
                env.update(GUARD_MODE="block", TOOL_GUARD_LOG_DIR=str(Path(temporary)/provider))
                result = subprocess.run([sys.executable, str(script_path(args.script_root, provider))], input=encode(envelope(provider, fixture)), capture_output=True, env=env, cwd=temporary, timeout=15)
                try:
                    actual = decision(provider, json.loads(result.stdout))
                    if result.returncode or actual != fixture.expected(args.expected_behavior,provider):
                        failures.append(f"{provider}.{fixture.name}: expected {fixture.expected(args.expected_behavior,provider)}, got {actual}, exit {result.returncode}")
                except (ValueError, TypeError) as error:
                    failures.append(f"{provider}.{fixture.name}: {error}")
        # The input event itself can be malformed, independently of its tool schema.
        for provider in PROVIDERS:
            result = subprocess.run([sys.executable, str(script_path(args.script_root, provider))], input=b'{"incomplete":\n', capture_output=True, env=env, cwd=temporary, timeout=15)
            count += 1
            if result.returncode or decision(provider, json.loads(result.stdout)) != "deny":
                failures.append(f"{provider}.malformed-envelope: expected deny")
    for failure in failures:
        print(failure, file=sys.stderr)
    print(f"Guardian public fixtures: {count-len(failures)} passed, {len(failures)} failed ({args.expected_behavior}).")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
