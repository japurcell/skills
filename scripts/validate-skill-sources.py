#!/usr/bin/env python3
"""Validate both skill categories before either installer writes destinations."""

import argparse
import sys
import unicodedata
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="repository skills directory")
    source = parser.parse_args().source
    names: dict[str, Path] = {}
    try:
        for category in ("default", "forest-service"):
            directory = source / category
            if not directory.is_dir():
                raise ValueError(f"Missing source directory: {directory}. Restore this category before installing.")
            for entry in sorted(directory.iterdir()):
                if not entry.is_dir() or entry.name == "archive" or entry.name.endswith("-workspace"):
                    continue
                if not (entry / "SKILL.md").is_file():
                    raise ValueError(f"Missing skill source file: {entry / 'SKILL.md'}. Add SKILL.md or remove the unexpected directory.")
                key = unicodedata.normalize("NFC", entry.name).casefold()
                if key in names:
                    raise ValueError(f"Conflicting skill destination names: {names[key]} and {entry}. Rename one skill directory before installing.")
                names[key] = entry
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
