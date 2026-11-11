#!/usr/bin/env python3
"""Check a UTF-8 commit-message file before git commit --file (Python 3 only)."""

import argparse
import re
import sys
from pathlib import Path


def issue_id(value):
    if not re.fullmatch(r"#?[1-9][0-9]*", value):
        raise argparse.ArgumentTypeError("use a positive issue number, with an optional # prefix")
    return value.removeprefix("#")


def validate(message):
    lines = message.replace("\r\n", "\n").split("\n")
    if not lines or not re.fullmatch(
        r"(?:docs|test|fix|feat|refactor|perf|chore)(?:\([^()\s]+\))?: \S.*", lines[0]
    ) or len(lines[0]) > 72 or lines[0].endswith("."):
        raise ValueError("use a typed subject of at most 72 characters, without a trailing period")
    if len(lines) < 2 or lines[1] != "":
        raise ValueError("separate the subject and body with a real blank line")
    position = 2
    for section in ("Summary:", "Rationale:", "Tests:"):
        if position >= len(lines) or lines[position] != section:
            raise ValueError(f"expected {section} on its own line")
        position += 1
        count = 0
        while position < len(lines) and lines[position].strip():
            line = lines[position]
            if line.startswith("- ") and line[2:].strip():
                count += 1
            elif not (count and line.startswith("  ") and line.strip()):
                raise ValueError(f"use nonempty bullets in {section}")
            position += 1
        if not count:
            raise ValueError(f"add at least one bullet to {section}")
        while position < len(lines) and not lines[position].strip():
            position += 1
    return lines[position:]


def validate_trailers(lines, args):
    while lines and not lines[-1].strip():
        lines.pop()
    authors = []
    expected_authors = list(dict.fromkeys(args.co_author))
    issues = list(dict.fromkeys(args.issue))
    last_issue = -1
    issue_or_author = False
    session_seen = False
    for line in lines:
        if not line.strip():
            if issue_or_author:
                raise ValueError("keep issue and co-author trailers contiguous")
            continue
        if re.fullmatch(r"Session: \S.*", line):
            if session_seen or issue_or_author:
                raise ValueError("put one optional Session trailer before issue and co-author trailers")
            session_seen = True
        elif match := re.fullmatch(r"(Refs|Fixes) #([1-9][0-9]*)", line):
            issue_or_author = True
            if match[2] not in args.issue:
                raise ValueError(f"verify issue #{match[2]} and pass --issue {match[2]}, or remove its trailer")
            position = issues.index(match[2])
            if position <= last_issue:
                raise ValueError("deduplicate issue trailers and keep their input order")
            last_issue = position
            if match[1] == "Fixes" and match[2] not in args.fixes:
                raise ValueError(f"use Refs unless the user intends to close issue #{match[2]}; then pass --fixes {match[2]}")
        elif re.fullmatch(r"Co-authored-by: [^<>]+ <[^<>\s]+@[^<>\s]+>", line):
            issue_or_author = True
            if line.removeprefix("Co-authored-by: ") not in args.co_author:
                raise ValueError("verify the contributor and pass --co-author 'Name <email>', or remove its trailer")
            if line in authors:
                raise ValueError("remove duplicate co-author trailers")
            authors.append(line)
        else:
            raise ValueError(f"malformed or unsupported trailer: {line}")
    for author in expected_authors:
        if authors.count(f"Co-authored-by: {author}") != 1:
            raise ValueError(f"missing required co-author trailer: {author}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("message_file", type=Path)
    parser.add_argument("--issue", action="append", default=[], type=issue_id, metavar="ID", help="verified actual issue ID, with optional # prefix; repeatable in input order")
    parser.add_argument("--fixes", action="append", default=[], type=issue_id, metavar="ID", help="specific issue the user explicitly intends this commit to close; repeatable")
    parser.add_argument("--co-author", action="append", default=[], metavar="NAME <EMAIL>", help="contributor identified by the user or reliably established by session context; repeatable")
    args = parser.parse_args()
    try:
        with args.message_file.open(encoding="utf-8", newline="") as message_file:
            message = message_file.read()
    except (OSError, UnicodeError) as error:
        print(f"Cannot read message: {error}", file=sys.stderr)
        return 2
    try:
        validate_trailers(validate(message), args)
    except ValueError as error:
        print(f"Invalid commit message: {error}", file=sys.stderr)
        return 1
    print("Commit message valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
