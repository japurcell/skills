#!/bin/sh
# User-local prototype launcher. No sudo, system package install, or login registration.
set -eu
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
    python3 -m venv .venv
fi
if ! .venv/bin/python -c 'import PySide6; from PySide6.QtMultimedia import QSoundEffect; assert PySide6.__version__ == "6.12.0"' >/dev/null 2>&1; then
    .venv/bin/python -m pip install --only-binary=:all: --no-cache-dir -r requirements.txt
fi
if [ "$#" -eq 0 ]; then
    set -- open
fi
exec .venv/bin/python native_alerts.py "$@"
