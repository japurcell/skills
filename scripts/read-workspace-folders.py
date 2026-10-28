#!/usr/bin/env python3
"""Print local folder paths from a VS Code JSON-with-comments workspace file."""

import argparse
import json
from pathlib import Path
import re
import sys


# Match strings first so comment markers inside paths/settings remain untouched.
STRING = r'"(?:[^"\\\r\n]|\\[^\r\n])*"'
COMMENTS = re.compile(STRING + r'|//[^\r\n]*|/\*[\s\S]*?\*/')
TRAILING_COMMAS = re.compile(STRING + r'|,(?=\s*[}\]])')


def read_folders(path):
    text = path.read_text(encoding="utf-8-sig")
    # Preserve positions so JSON errors still refer to the original file.
    def blank_comment(match):
        token = match[0]
        if token.startswith('"'):
            return token
        return re.sub(r"[^\r\n]", " ", token)

    text = COMMENTS.sub(blank_comment, text)

    def blank_trailing_comma(match):
        token = match[0]
        if token != ",":
            return token
        previous_character = text[:match.start()].rstrip()[-1:]
        if previous_character in ("", "[", "{", ",", ":"):
            return token
        return " "

    text = TRAILING_COMMAS.sub(blank_trailing_comma, text)
    data = json.loads(text)
    if not isinstance(data, dict) or not isinstance(data.get("folders"), list):
        raise ValueError("Expected a workspace object with a 'folders' array.")
    paths = []
    for index, folder in enumerate(data["folders"]):
        value = folder.get("path") if isinstance(folder, dict) else None
        if not isinstance(value, str) or not value.strip() or any(
            char in value for char in "\r\n\0"
        ):
            raise ValueError(f"folders[{index}].path must be a nonempty local path without line breaks or NUL.")
        paths.append(value)
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()
    try:
        paths = read_folders(args.workspace)
    except (OSError, ValueError) as error:
        print(f"Error: could not read workspace {args.workspace}: {error}", file=sys.stderr)
        return 1
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
