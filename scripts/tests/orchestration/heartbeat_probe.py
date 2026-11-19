"""Write bounded, timestamped heartbeats inside the current disposable project."""

import argparse
import json
import math
import os
from pathlib import Path
import sys
import time


MAX_DURATION_SECONDS = 240.0


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--output", required=True, type=Path)
    result.add_argument("--interval", required=True, type=float)
    result.add_argument("--duration", required=True, type=float)
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    if not math.isfinite(args.interval) or args.interval <= 0:
        parser().error("interval must be a finite positive number")
    if not math.isfinite(args.duration) or args.duration <= 0:
        parser().error("duration must be a finite positive number")
    if args.duration > MAX_DURATION_SECONDS:
        parser().error(f"maximum duration is {MAX_DURATION_SECONDS:g} seconds")

    project = Path.cwd().resolve()
    output = args.output.resolve()
    try:
        output.relative_to(project)
    except ValueError:
        parser().error("output must be inside the current project")
    output.parent.mkdir(parents=True, exist_ok=True)

    stop_at = time.monotonic() + args.duration
    sequence = 0
    try:
        with output.open("x", encoding="utf-8") as stream:
            while True:
                now = time.monotonic()
                if now >= stop_at:
                    break
                sequence += 1
                record = {
                    "sequence": sequence,
                    "wall_time_ns": time.time_ns(),
                    "monotonic_ns": time.monotonic_ns(),
                    "pid": os.getpid(),
                }
                stream.write(json.dumps(record, separators=(",", ":")) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
                remaining = stop_at - time.monotonic()
                if remaining > 0:
                    time.sleep(min(args.interval, remaining))
    except FileExistsError:
        parser().error("output already exists; use a fresh project path")
    return 0


if __name__ == "__main__":
    sys.exit(main())
