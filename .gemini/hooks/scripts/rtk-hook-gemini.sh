#!/usr/bin/env bash

set -euo pipefail

exec python3 -I -S -B - <<'PY'
import subprocess
import sys

payload = sys.stdin.buffer.read()
if not payload.startswith(b'{') or not payload.rstrip().endswith(b'}'):
    sys.stdout.buffer.write(b'{}\n')
    raise SystemExit(0)

try:
    result = subprocess.run(['rtk', 'hook', 'gemini'], input=payload, capture_output=True, check=False)
except Exception:
    sys.stdout.buffer.write(b'{}\n')
    raise SystemExit(0)

if result.returncode != 0 or not result.stdout.startswith(b'{'):
    sys.stdout.buffer.write(b'{}\n')
    raise SystemExit(0)

sys.stdout.buffer.write(result.stdout if result.stdout.endswith(b'\n') else result.stdout + b'\n')
PY
