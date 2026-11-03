#!/usr/bin/env python3
"""Extract user and assistant messages from Claude and Codex conversation JSONL files.

Usage:
  extract-conversations.py <output-dir> --claude-dir DIR [--codex-dir DIR] [options]
  extract-conversations.py <output-dir> --codex-dir DIR [--claude-dir DIR] [options]

Options:
  --claude-dir DIR   Claude project conversation directory (repeatable)
  --codex-dir DIR    Codex sessions root directory (repeatable, recursive)
  --cwd PATH         Include only conversations from this working directory
  --batches N        Number of batch manifests to create (default: 5)
  --from YYYY-MM-DD  Include conversations modified on or after this date
  --to YYYY-MM-DD    Include conversations modified on or before this date
  --min-size BYTES   Minimum file size in bytes (default: 500)

Date filters are composable:
  --from 2026-02-13 --to 2026-02-13   Exactly Feb 13
  --from 2026-02-13                    Feb 13 onwards
  --to 2026-02-13                      Up to and including Feb 13

Output:
  <output-dir>/000_<provider>_<name>.txt  - extracted messages per conversation
  <output-dir>/batches/batch_0.txt ... batch_N.txt - file lists for each batch

Inputs are confined to ~/.claude/projects and ~/.codex/sessions. Output must
be below an existing private ruminate-* workspace in the platform temporary
directory. HOME, temporary configuration, and the trees must remain trusted
and stable; path checks do not prevent hostile concurrent ancestor swaps.
"""

import argparse
import json
import os
import stat
import sys
import tempfile
import unicodedata
from datetime import date, datetime
from pathlib import Path
from typing import Any, Callable


class PathPolicyError(ValueError):
    pass


def literal_path(value: str) -> Path:
    if any(unicodedata.category(char) in {"Cc", "Zl", "Zp"} for char in value):
        raise PathPolicyError("paths must not contain control characters or line separators")
    path = Path(value)
    if ".." in path.parts:
        raise PathPolicyError("paths must not contain '..' components")
    return path.absolute()


def source_root(value: str, anchor: Path) -> str:
    path = literal_path(value)
    try:
        resolved = path.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise PathPolicyError(f"input directory is unavailable: {path}") from exc
    if not resolved.is_relative_to(anchor):
        raise PathPolicyError(f"input directory must be within {anchor}")
    if not resolved.is_dir():
        raise PathPolicyError(f"input root must be a directory: {path}")
    return str(resolved)


def private_directory(path: Path) -> None:
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode):
        raise PathPolicyError(f"output directory must be a real directory, not a symlink: {path}")
    if info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise PathPolicyError(f"output directory must be owned by this user and private (mode 700): {path}")


def output_parts(path: Path, workspace: Path) -> tuple[str, ...]:
    if not path.resolve().is_relative_to(workspace):
        raise PathPolicyError(f"output path escapes workspace: {path}")
    parts = path.relative_to(workspace).parts
    name_max = os.pathconf(workspace, "PC_NAME_MAX")
    if name_max > 0 and any(len(os.fsencode(part)) > name_max for part in parts):
        raise PathPolicyError("output component exceeds the filesystem name limit")
    return parts


def output_directory(path: Path, workspace: Path) -> None:
    current = workspace
    for part in output_parts(path, workspace):
        current /= part
        try:
            private_directory(current)
        except FileNotFoundError:
            continue


def output_root(value: str) -> tuple[Path, Path]:
    path = literal_path(value)
    temp = Path(tempfile.gettempdir())
    anchor = temp.resolve(strict=True)
    if not path.resolve().is_relative_to(anchor):
        raise PathPolicyError("output must be below a private ruminate-* workspace in the platform temporary directory")
    if path.is_relative_to(temp):
        relative = path.relative_to(temp)
    elif path.is_relative_to(anchor):
        relative = path.relative_to(anchor)
    else:
        raise PathPolicyError("output must not use a symlink to the temporary directory")
    if len(relative.parts) < 2 or not relative.parts[0].startswith("ruminate-"):
        raise PathPolicyError("output must be a strict descendant of a ruminate-* workspace")
    workspace = anchor / relative.parts[0]
    try:
        private_directory(workspace)
    except FileNotFoundError as exc:
        raise PathPolicyError("the private ruminate-* workspace must already exist") from exc
    output = anchor / relative
    output_directory(output, workspace)
    return output, workspace


def make_output_directory(path: Path, workspace: Path) -> None:
    output_directory(path, workspace)
    current = workspace
    for part in path.relative_to(workspace).parts:
        current /= part
        current.mkdir(mode=0o700, exist_ok=True)


def output_file(path: Path, workspace: Path) -> None:
    output_directory(path.parent, workspace)
    output_parts(path, workspace)
    try:
        info = path.lstat()
    except FileNotFoundError:
        return
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise PathPolicyError(f"output must be a regular, non-symlink file with one link: {path}")


def write_output(path: Path, content: str, workspace: Path) -> None:
    output_file(path, workspace)
    flags = os.O_WRONLY | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    descriptor = os.open(path, flags, 0o600)
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise PathPolicyError(f"output must be a regular file with one link: {path}")
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            descriptor = -1
            handle.truncate(0)
            handle.write(content)
    finally:
        if descriptor != -1:
            os.close(descriptor)


def file_mod_date(fpath: str) -> date:
    """Return the modification date of a file."""
    return datetime.fromtimestamp(os.path.getmtime(fpath)).date()


def _extract_texts(content: Any, accepts_type: Callable[[Any], bool]) -> list[str]:
    texts: list[str] = []
    if isinstance(content, str):
        texts.append(content)
        return texts
    if not isinstance(content, list):
        return texts

    for item in content:
        if not isinstance(item, dict):
            continue
        if accepts_type(item.get("type")) and isinstance(item.get("text"), str):
            texts.append(item["text"])
    return texts


def extract_claude_texts(content: Any) -> list[str]:
    return _extract_texts(content, lambda item_type: item_type == "text")


def extract_codex_texts(content: Any) -> list[str]:
    return _extract_texts(content, lambda item_type: item_type in {"input_text", "output_text", "text"})


def append_message(messages: list[str], role: str, text: str, max_len: int) -> None:
    clean = text.strip()
    if not clean or len(clean) <= 10:
        return
    if clean.startswith("<system-reminder>") and clean.endswith("</system-reminder>"):
        return
    if role == "user":
        messages.append(f"[USER]: {text[:max_len]}")
        return
    if role == "assistant":
        messages.append(f"[ASSISTANT]: {text[:max_len]}")


def extract_messages(fpath: str, root: Path) -> tuple[str, str, list[str]]:
    """Extract messages from one conversation JSONL file.

    Returns (provider, cwd, messages), where provider is one of:
    claude, codex, unknown.
    """
    provider = "unknown"
    cwd = ""
    messages: list[str] = []

    checked = contained_source(Path(fpath), root)
    with open(checked, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            try:
                entry = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                continue
            if not isinstance(entry, dict):
                continue

            entry_type = entry.get("type", "")

            if isinstance(entry.get("cwd"), str) and not cwd:
                cwd = entry["cwd"]
                provider = "claude"

            if entry_type == "session_meta":
                payload = entry.get("payload")
                if isinstance(payload, dict):
                    provider = "codex"
                    if isinstance(payload.get("cwd"), str) and not cwd:
                        cwd = payload["cwd"]
                continue

            if entry_type in {"user", "assistant"}:
                provider = "claude"
                if entry_type == "user" and entry.get("isMeta"):
                    continue
                msg = entry.get("message")
                if not isinstance(msg, dict):
                    continue
                for text in extract_claude_texts(msg.get("content", "")):
                    append_message(messages, entry_type, text, 3000 if entry_type == "user" else 800)
                continue

            if entry_type != "response_item":
                continue

            payload = entry.get("payload")
            if not isinstance(payload, dict):
                continue
            if payload.get("type") != "message":
                continue

            role = payload.get("role", "")
            if role not in {"user", "assistant"}:
                continue
            provider = "codex"
            for text in extract_codex_texts(payload.get("content", "")):
                append_message(messages, role, text, 3000 if role == "user" else 800)

    return provider, cwd, messages


def contained_source(path: Path, root: Path) -> Path:
    literal_path(str(path))
    try:
        resolved = path.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise PathPolicyError(f"source is unavailable: {path}") from exc
    if not resolved.is_relative_to(root):
        raise PathPolicyError(f"source escapes input directory: {path}")
    literal_path(str(resolved))
    return resolved


def discover_files(claude_dirs: list[str], codex_dirs: list[str]) -> dict[str, Path]:
    files: dict[str, Path] = {}

    def visit(directory: Path, root: Path, recursive: bool) -> None:
        directories: list[Path] = []
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.name.startswith("."):
                    continue
                path = Path(entry.path)
                resolved = contained_source(path, root)
                if resolved.is_dir():
                    if recursive and not entry.is_symlink():
                        directories.append(resolved)
                elif entry.name.endswith(".jsonl"):
                    if not resolved.is_file():
                        raise PathPolicyError(f"source must be a regular file: {path}")
                    files.setdefault(str(resolved), root)
        # Match glob's immediate-files-first order when modification times tie.
        for child in directories:
            visit(child, root, recursive)

    for roots, recursive in ((claude_dirs, False), (codex_dirs, True)):
        for root in roots:
            visit(Path(root), Path(root), recursive)
    return files


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Extract messages from Claude and Codex conversation JSONL files."
    )
    parser.add_argument(
        "output_dir", help="Output below a private ruminate-* workspace in the platform temporary directory",
    )
    parser.add_argument(
        "--claude-dir", action="append", default=[],
        help="Literal directory beneath ~/.claude/projects (nonrecursive)",
    )
    parser.add_argument(
        "--codex-dir", action="append", default=[],
        help="Literal directory beneath ~/.codex/sessions (recursive)",
    )
    parser.add_argument("--cwd", help="Only include conversations where detected cwd matches this path")
    parser.add_argument("--batches", type=int, default=5, help="Number of batch manifests (default: 5)")
    parser.add_argument(
        "--from",
        dest="from_date",
        type=date.fromisoformat,
        help="Include conversations modified on or after this date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--to",
        dest="to_date",
        type=date.fromisoformat,
        help="Include conversations modified on or before this date (YYYY-MM-DD)",
    )
    parser.add_argument("--min-size", type=int, default=500, help="Minimum file size in bytes (default: 500)")
    args = parser.parse_args()

    if not args.claude_dir and not args.codex_dir:
        parser.error("at least one input source is required (--claude-dir or --codex-dir)")
    if args.batches <= 0:
        parser.error("--batches must be positive")
    if args.min_size < 0:
        parser.error("--min-size must be nonnegative")
    if args.from_date and args.to_date and args.from_date > args.to_date:
        parser.error("--from must be on or before --to")

    try:
        run(args)
    except PathPolicyError as exc:
        parser.error(str(exc))
    except OSError as exc:
        parser.exit(1, f"{parser.prog}: error: I/O failure: {exc}\n")


def run(args: argparse.Namespace) -> None:
    home = Path.home().resolve()
    claude_dirs = [source_root(root, home / ".claude/projects") for root in args.claude_dir]
    codex_dirs = [source_root(root, home / ".codex/sessions") for root in args.codex_dir]
    output, workspace = output_root(args.output_dir)
    sources = discover_files(claude_dirs, codex_dirs)

    files = []
    for fpath in sources:
        if os.path.getsize(fpath) < args.min_size:
            continue
        if args.from_date or args.to_date:
            mod = file_mod_date(fpath)
            if args.from_date and mod < args.from_date:
                continue
            if args.to_date and mod > args.to_date:
                continue
        files.append(fpath)

    files.sort(key=os.path.getmtime, reverse=True)

    date_desc = ""
    if args.from_date and args.to_date:
        date_desc = f" (from {args.from_date} to {args.to_date})"
    elif args.from_date:
        date_desc = f" (from {args.from_date})"
    elif args.to_date:
        date_desc = f" (to {args.to_date})"
    print(f"Found {len(files)} candidate conversations{date_desc}", file=sys.stderr)

    extracted: list[str] = []
    outputs: list[tuple[Path, str]] = []
    provider_counts: dict[str, int] = {"claude": 0, "codex": 0, "unknown": 0}

    for idx, fpath in enumerate(files):
        provider, cwd, messages = extract_messages(fpath, sources[fpath])
        if args.cwd and (not cwd or os.path.realpath(cwd) != os.path.realpath(args.cwd)):
            continue
        if not messages:
            continue

        provider_counts[provider] = provider_counts.get(provider, 0) + 1
        fname = os.path.basename(fpath).replace(".jsonl", "")
        out_path = f"{args.output_dir}/{idx:03d}_{provider}_{fname}.txt"
        destination = output / f"{idx:03d}_{provider}_{fname}.txt"
        output_file(destination, workspace)
        content = f"[PROVIDER]: {provider}\n"
        if cwd:
            content += f"[CWD]: {cwd}\n"
        content += f"[SOURCE_FILE]: {fpath}\n\n" + "\n\n".join(messages) + "\n"
        outputs.append((destination, content))
        extracted.append(out_path)

    batch_dir = output / "batches"
    output_directory(batch_dir, workspace)
    batch_size = max(1, (len(extracted) + args.batches - 1) // args.batches)
    manifests: list[tuple[Path, list[str]]] = []
    for b in range(args.batches):
        batch_files = extracted[b * batch_size : (b + 1) * batch_size]
        if batch_files:
            manifest = batch_dir / f"batch_{b}.txt"
            output_file(manifest, workspace)
            manifests.append((manifest, batch_files))

    make_output_directory(output, workspace)
    make_output_directory(batch_dir, workspace)
    for destination, content in outputs:
        write_output(destination, content, workspace)

    print(
        "Extracted "
        f"{len(extracted)} conversations with content "
        f"(claude={provider_counts.get('claude', 0)}, "
        f"codex={provider_counts.get('codex', 0)}, "
        f"unknown={provider_counts.get('unknown', 0)})",
        file=sys.stderr,
    )

    for b, (manifest, batch_files) in enumerate(manifests):
        write_output(manifest, "\n".join(batch_files) + "\n", workspace)
        print(f"Batch {b}: {len(batch_files)} conversations", file=sys.stderr)

    print(args.output_dir)


if __name__ == "__main__":
    main()
