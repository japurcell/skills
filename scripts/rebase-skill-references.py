#!/usr/bin/env python3
"""Rebase source-root reference links after a skill is installed flat."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import stat


MARKDOWN_SUFFIXES = {".md", ".markdown"}
REFERENCE_PREFIX_BOUNDARY = r"(?<![A-Za-z0-9._/-])"


def portable_relative_path(target: Path, start: Path) -> str:
    return os.path.relpath(target, start=start).replace(os.sep, "/")


def is_link_or_junction(path: Path) -> bool:
    try:
        details = path.lstat()
    except OSError:
        return False

    if stat.S_ISLNK(details.st_mode):
        return True

    is_junction = getattr(os.path, "isjunction", None)
    if is_junction is not None and is_junction(path):
        return True

    reparse_point = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(getattr(details, "st_file_attributes", 0) & reparse_point)


def has_link_component(root: Path, relative_path: Path) -> bool:
    current = root
    for component in relative_path.parts:
        current /= component
        if is_link_or_junction(current):
            return True
    return False


def regular_markdown_files(root: Path):
    for current_dir, child_dirs, filenames in os.walk(root, followlinks=False):
        directory = Path(current_dir)
        child_dirs[:] = [
            name for name in child_dirs if not is_link_or_junction(directory / name)
        ]
        for filename in filenames:
            path = directory / filename
            if is_link_or_junction(path) or path.suffix.lower() not in MARKDOWN_SUFFIXES:
                continue
            try:
                if stat.S_ISREG(path.lstat().st_mode):
                    yield path
            except OSError:
                continue


def rebase_skill_references(
    source_dir: Path,
    destination_dir: Path,
    references_source: Path,
    references_destination: Path,
) -> None:
    # A category entry may itself be a symlink or Windows junction. Check it
    # before normalizing paths so we never rewrite through its external target.
    if is_link_or_junction(source_dir) or is_link_or_junction(destination_dir):
        return

    source_dir = Path(os.path.abspath(source_dir))
    destination_dir = Path(os.path.abspath(destination_dir))
    references_source = Path(os.path.abspath(references_source))
    references_destination = Path(os.path.abspath(references_destination))

    for destination_file in sorted(regular_markdown_files(destination_dir)):
        relative_path = destination_file.relative_to(destination_dir)
        source_file = source_dir / relative_path
        if has_link_component(source_dir, relative_path):
            continue
        try:
            if not stat.S_ISREG(source_file.lstat().st_mode):
                continue
        except OSError:
            continue

        source_prefix = portable_relative_path(references_source, source_file.parent)
        destination_prefix = portable_relative_path(
            references_destination, destination_file.parent
        )
        if source_prefix == destination_prefix:
            continue

        content = destination_file.read_bytes()
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            continue

        prefix_pattern = re.compile(
            REFERENCE_PREFIX_BOUNDARY + re.escape(source_prefix) + r"/"
        )
        rebased = prefix_pattern.sub(lambda match: f"{destination_prefix}/", text)
        if rebased != text:
            destination_file.write_bytes(rebased.encode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", required=True, type=Path)
    parser.add_argument("--destination-dir", required=True, type=Path)
    parser.add_argument("--references-source", required=True, type=Path)
    parser.add_argument("--references-destination", required=True, type=Path)
    args = parser.parse_args()

    rebase_skill_references(
        args.source_dir,
        args.destination_dir,
        args.references_source,
        args.references_destination,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
