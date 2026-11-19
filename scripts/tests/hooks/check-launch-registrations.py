#!/usr/bin/env python3
"""Compare checked-in brain launch registrations with the frozen rollout oracle."""

import argparse
import json
from pathlib import Path
import sys

FIXTURE = Path(__file__).with_name("launch-registrations-069b3f22.json")
ROOT = Path(__file__).resolve().parents[3]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    errors = []
    command_count = 0
    for name, expected in fixture.items():
        try:
            actual = json.loads((args.root / name).read_text(encoding="utf-8"))
            for event, registrations in expected["hooks"].items():
                actual_registrations = actual["hooks"][event]
                for registration in registrations:
                    # Allow unrelated handlers in a wrapper while comparing every owned field.
                    inner = registration.get("hooks", [registration])
                    def matches(candidate):
                        if "hooks" not in registration:
                            return candidate == registration
                        return (isinstance(candidate, dict)
                                and {k: v for k, v in candidate.items() if k != "hooks"}
                                == {k: v for k, v in registration.items() if k != "hooks"}
                                and all(candidate.get("hooks", []).count(item) == 1 for item in inner))
                    if sum(matches(candidate) for candidate in actual_registrations) != 1:
                        errors.append(f"{name}: {event} registration differs or is ambiguous")
                    command_count += sum(key in handler for handler in inner
                                         for key in ("bash", "powershell", "command", "commandWindows"))
        except (OSError, ValueError, KeyError, TypeError) as error:
            errors.append(f"{name}: {error}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Launch registrations match: {len(fixture)} documents, {command_count} commands")
    return 0


if __name__ == "__main__":
    sys.exit(main())
