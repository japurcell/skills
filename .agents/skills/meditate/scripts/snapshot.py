#!/usr/bin/env python3
"""Write a delimited snapshot of regular Markdown files under one directory."""

import argparse
import os
import stat
import sys
from pathlib import Path


def is_link(path):
    info = path.lstat()
    return (stat.S_ISLNK(info.st_mode)
            or bool(getattr(info, "st_file_attributes", 0)
                    & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)))


def markdown_files(directory):
    root = directory.resolve(strict=True)
    for current, directories, files in os.walk(directory, followlinks=False):
        parent = Path(current)
        directories[:] = [name for name in directories
                          if name not in {"node_modules", "slides"}
                          and not is_link(parent / name)
                          and (parent / name).resolve().is_relative_to(root)]
        for name in files:
            path = parent / name
            if (path.match("*.md") and not is_link(path)
                    and path.resolve().is_relative_to(root) and path.is_file()):
                yield path


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Skips symlinks, reparse points, node_modules, and slides. "
               "Reads no stdin; prints the output path to stdout. "
               "Diagnostics go to stderr. Exit: 0 success, 1 I/O failure, 2 invalid arguments.",
    )
    parser.add_argument("directory", type=Path, help="Source directory")
    parser.add_argument("output", type=Path, help="Snapshot file to write")
    arguments = parser.parse_args()
    if not arguments.directory.is_dir():
        parser.error(f"not a directory: {arguments.directory}")
    if is_link(arguments.directory):
        parser.error("source directory must not be a symlink or reparse point")
    paths = sorted(
        path for path in markdown_files(arguments.directory)
        if path.resolve() != arguments.output.resolve()
    )
    with arguments.output.open("wb") as output:
        for path in paths:
            output.write(f"=== {path} ===\n".encode())
            output.write(path.read_bytes())
            output.write(b"\n\n")
    print(arguments.output)


if __name__ == "__main__":
    main()
