#!/usr/bin/env python3
"""Concatenate Markdown files with the snapshot.sh delimiter format."""

import argparse
import sys
from pathlib import Path


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("output", type=Path)
    arguments = parser.parse_args()
    if not arguments.directory.is_dir():
        parser.error(f"not a directory: {arguments.directory}")
    paths = sorted(
        path for path in arguments.directory.rglob("*.md")
        if path.is_file()
        and not {"node_modules", "slides"}.intersection(
            path.relative_to(arguments.directory).parts[:-1])
        and path.resolve() != arguments.output.resolve()
    )
    with arguments.output.open("wb") as output:
        for path in paths:
            output.write(f"=== {path} ===\n".encode())
            output.write(path.read_bytes())
            output.write(b"\n\n")
    print(arguments.output)


if __name__ == "__main__":
    main()
