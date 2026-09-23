#!/usr/bin/env python3
"""Public CLI checks for maintained Codex hook merging."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INSTALLER = ROOT / "scripts/install-codex-hooks.py"
SOURCE_TEMPLATE = ROOT / ".codex/global-hooks.json"


def run(template: Path, destination: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(INSTALLER), "--template", str(template), "--destination", str(destination)],
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        template = Path(temporary) / "template.json"
        maintained = json.loads(SOURCE_TEMPLATE.read_text(encoding="utf-8"))
        for event in ("PreToolUse", "Stop"):
            maintained["hooks"][event] = [{"hooks": [{
                "type": "command",
                "command": "python3 ~/.codex/hooks/scan-secrets.py",
                "commandWindows": 'py -3 "%USERPROFILE%\\.codex\\hooks\\scan-secrets.py"',
            }]}]
        template.write_text(json.dumps(maintained), encoding="utf-8")
        destination = Path(temporary) / "hooks.json"
        original = {
            "custom": {"keep": True},
            "hooks": {
                "PreToolUse": [{"matcher": "Bash", "custom": "keep", "hooks": [
                    {"type": "command", "command": "echo user"},
                    {"type": "command", "command": "python3 ~/.codex/hooks/scan-secrets.py"},
                ]}],
                "Stop": [{"hooks": [{"type": "command", "commandWindows": "py -3 \"%USERPROFILE%\\.codex\\hooks\\scan-secrets.py\""}]}],
                "SessionStart": [{"hooks": [{"type": "command", "command": "echo unrelated"}]}],
            },
        }
        destination.write_text(json.dumps(original), encoding="utf-8")
        first = run(template, destination)
        assert first.returncode == 0, first.stderr
        merged = json.loads(destination.read_text(encoding="utf-8"))
        assert merged["custom"] == original["custom"]
        assert merged["hooks"]["PreToolUse"][0]["custom"] == "keep"
        assert merged["hooks"]["PreToolUse"][0]["hooks"][0]["command"] == "echo user"
        for event in ("SessionStart", "PreToolUse", "Stop"):
            for group in maintained["hooks"][event]:
                for handler in group["hooks"]:
                    command = handler["command"]
                    matches = [candidate for existing_group in merged["hooks"][event]
                               for candidate in existing_group["hooks"] if candidate.get("command") == command]
                    assert matches == [handler], (event, command, matches)
        first_bytes = destination.read_bytes()
        second = run(template, destination)
        assert second.returncode == 0, second.stderr
        assert destination.read_bytes() == first_bytes

        malformed = json.loads(template.read_text(encoding="utf-8"))
        malformed["hooks"]["PreToolUse"][0]["hooks"][0]["commandWindows"] = (
            'py -3 "%USERPROFILE%\\.codex\\hooks\\load-required-skills.py"'
        )
        template.write_text(json.dumps(malformed), encoding="utf-8")
        failed = run(template, destination)
        assert failed.returncode == 1
        assert destination.read_bytes() == first_bytes

    print("PASS: Codex maintained hook merge")


if __name__ == "__main__":
    main()
