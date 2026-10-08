#!/usr/bin/env python3
"""Public CLI checks for maintained Codex hook merging."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INSTALLER = ROOT / "scripts/install-codex-hooks.py"
SOURCE_TEMPLATE = ROOT / ".codex/global-hooks.json"


def run(
    template: Path,
    destination: Path,
    *,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(INSTALLER), "--template", str(template), "--destination", str(destination)],
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, **(environment or {})},
    )


def check_write_failure_cleanup() -> None:
    for operation in ("fsync", "replace"):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            template = root / "template.json"
            template.write_bytes(SOURCE_TEMPLATE.read_bytes())
            destination = root / "hooks.json"
            original = b'{"custom": "keep"}\n'
            destination.write_bytes(original)
            injection = root / "injection"
            injection.mkdir()
            injection.joinpath("sitecustomize.py").write_text(
                "import os\n"
                "def fail(*args, **kwargs):\n"
                "    raise OSError('injected write failure')\n"
                f"os.{operation} = fail\n",
                encoding="utf-8",
            )
            result = run(template, destination, environment={
                "PYTHONPATH": str(injection),
                "PYTHONDONTWRITEBYTECODE": "1",
            })
            assert result.returncode == 1, (operation, result)
            assert "injected write failure" in result.stderr, (operation, result.stderr)
            assert destination.read_bytes() == original, operation
            assert not destination.with_name("hooks.json.bak").exists(), operation
            assert not list(root.glob(".*.tmp")), operation


def main() -> None:
    check_write_failure_cleanup()
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
                    {"type": "command", "command": "python3 ~/.codex/hooks/scan-secrets.py",
                     "commandWindows": "echo windows user"},
                    {"type": "command", "command": "echo unix user",
                     "commandWindows": 'py -3 "%USERPROFILE%\\.codex\\hooks\\scan-secrets.py"'},
                    {"type": "command", "command": "python3 ~/.codex/hooks/scan-secrets.py",
                     "commandWindows": 'py -3 "%USERPROFILE%\\.codex\\hooks\\scan-secrets.py"'},
                    {"type": "command", "command": "python3 ~/.codex/hooks/rtk-explicit-codex.py",
                     "commandWindows": 'py -3 "%USERPROFILE%\\.codex\\hooks\\rtk-explicit-codex.py"'},
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
        assert merged["hooks"]["PreToolUse"][0]["hooks"] == original["hooks"]["PreToolUse"][0]["hooks"][:3]
        assert "rtk-explicit-codex.py" not in destination.read_text(encoding="utf-8")
        for event in ("SessionStart", "PreToolUse", "Stop"):
            for group in maintained["hooks"][event]:
                for handler in group["hooks"]:
                    command = handler["command"]
                    matches = [candidate for existing_group in merged["hooks"][event]
                               for candidate in existing_group["hooks"]
                               if candidate.get("command") == command
                               and candidate.get("commandWindows") == handler["commandWindows"]]
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
