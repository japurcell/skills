#!/usr/bin/env python3
# Generated from hooks/families/send_event.py by scripts/generate-hooks.py. Do not edit.

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
