"""Render the provider-local observability event no-op entrypoint."""

from __future__ import annotations

from hooks.manifest import GeneratedTarget
from hooks.providers import Provider


SOURCE_PATH = "hooks/families/send_event.py"
HEADER = f"# Generated from {SOURCE_PATH} by scripts/generate-hooks.py. Do not edit.\n"

_RUNTIME_BODY = '''
from __future__ import annotations

import os
import sys

from helpers.common import emit_json, read_json_input


def main() -> int:
    if "--include-transcript" in sys.argv[1:]:
        os.environ["OBSERVABILITY_INCLUDE_TRANSCRIPT"] = "true"

    read_json_input()
    emit_json({})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def render(provider: Provider, target: GeneratedTarget) -> str:
    """Return the complete local script without reading runtime state."""
    if target.family != "send_event" or target.provider != provider.name:
        raise ValueError(f"send_event cannot render target {target.output_path}")
    return "#!/usr/bin/env python3\n" + HEADER + _RUNTIME_BODY
