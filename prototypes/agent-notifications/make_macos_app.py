"""Create a local launcher bundle. No install, registration, or login item is added."""
import plistlib
from pathlib import Path

root = Path(__file__).resolve().parent
bundle = root / "Agent Alert Prototype.app" / "Contents"
executable = bundle / "MacOS" / "AgentAlerts"
executable.parent.mkdir(parents=True, exist_ok=True)
executable.write_text('#!/bin/sh\ncd "$(dirname "$0")/../../.." || exit 1\nexec "$PWD/.venv/bin/python" "$PWD/native_alerts.py" serve --show\n')
executable.chmod(0o755)
with (bundle / "Info.plist").open("wb") as handle:
    plistlib.dump({"CFBundleName": "Agent Alert Prototype", "CFBundleDisplayName": "Agent Alert Prototype",
                  "CFBundleIdentifier": "local.prototype.agent-alerts", "CFBundleExecutable": "AgentAlerts",
                  "CFBundlePackageType": "APPL", "CFBundleVersion": "0.1", "LSUIElement": True}, handle)
print(root / "Agent Alert Prototype.app")
