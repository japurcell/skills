"""Read-only prerequisite checks for explicitly selected runtimes."""

import re
import shutil
import subprocess

from .sources import AssetError


def check(catalog, assets, clients):
    runtime = sorted({requirement for asset in assets for requirement in catalog["assets"][asset]["runtime"]})
    if "rtk" in runtime or any(requirement.startswith("rtk>=") for requirement in runtime):
        guidance = "Install stable RTK 0.50.0 or newer with the selected hook processors; configure personal settings separately using python3 scripts/configure-rtk.py --home PATH. Repository installs never change account-wide settings."
        def refuse():
            raise AssetError("ASSET_PREREQUISITE_MISSING", guidance, 1)
        executable = shutil.which("rtk")
        if executable is None:
            refuse()
        try:
            result = subprocess.run([executable, "--version"], capture_output=True, text=True, timeout=5)
            match = re.fullmatch(r"rtk (\d+)\.(\d+)\.(\d+)(?:\+[\w.-]+)?\s*", result.stdout)
            if result.returncode or not match or tuple(map(int, match.groups())) < (0, 50, 0):
                refuse()
            for client in clients:
                if client not in ("copilot", "gemini"):
                    continue
                result = subprocess.run([executable, "hook", client, "--help"], capture_output=True, text=True, timeout=5)
                if result.returncode:
                    refuse()
        except (OSError, subprocess.TimeoutExpired):
            refuse()
    return runtime
