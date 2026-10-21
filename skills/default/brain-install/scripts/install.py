#!/usr/bin/env python3
"""Inspect or install the bundled brain system in an explicit target directory."""

import argparse
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile


ASSETS = Path(__file__).resolve().parents[1] / "assets"
PROVIDERS = {
    "copilot": (".github/hooks/hooks.json", ".github/hooks/scripts"),
    "codex": (".codex/hooks.json", ".codex/hooks"),
    "gemini": (".gemini/settings.json", ".gemini/hooks/scripts"),
}


class Conflict(ValueError):
    """An invalid target or unresolved user choice; no application may begin."""


def safe_path(target, relative):
    path = target / relative
    if target.is_symlink() or target.is_junction():
        raise Conflict(f"unsafe linked target: {target}")
    current = target
    for component in Path(relative).parts:
        current /= component
        if current.is_symlink() or current.is_junction():
            raise Conflict(f"unsafe linked destination: {relative}")
        if current.exists() and current != path and not current.is_dir():
            raise Conflict(f"destination ancestor is not a directory: {relative}")
    if path.exists() and not path.is_file():
        raise Conflict(f"destination is not a regular file: {relative}")
    return path


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".brain-install-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def payload():
    files = {}
    for source_root, destination in ((ASSETS / "brain", "brain"),
                                     (ASSETS / "skills", ".agents/skills")):
        for source in sorted(source_root.rglob("*")):
            if source.is_file() and "__pycache__" not in source.parts:
                files[f"{destination}/{source.relative_to(source_root).as_posix()}"] = source.read_bytes()
    return files


def sections(text):
    """Locate real ATX headings outside fenced code, retaining original bytes."""
    headings = []
    fence = None
    offset = 0
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\r\n"))
        if marker:
            run, suffix = marker.groups()
            if fence is None:
                fence = run
            elif run[0] == fence[0] and len(run) >= len(fence) and not suffix.strip():
                fence = None
        elif fence is None:
            heading = re.match(r"^ {0,3}(#{1,2})[ \t]+(.+?)[ \t]*#*[ \t]*(?:\r?\n)?$", line)
            if heading:
                headings.append((offset, len(heading[1]), heading[2]))
        offset += len(line)
    result = {}
    for index, (start, level, title) in enumerate(headings):
        end = next((position for position, following, _ in headings[index + 1:]
                    if following <= level), len(text))
        if level == 2 and title in ("Brain", "End of Work Session Defined"):
            if title in result:
                raise Conflict(f"duplicate AGENTS.md section: {title}")
            result[title] = text[start:end]
    return result


def agents_content(existing, template):
    actual = sections(existing)
    expected = sections(template)
    output = existing
    for title, content in expected.items():
        if title in actual:
            if actual[title].replace("\r\n", "\n").rstrip() != content.rstrip():
                raise Conflict(f"AGENTS.md section conflict: {title}; proposed section:\n{content}")
        else:
            output += ("\n\n" if output and not output.endswith("\n\n") else "") + content
    return output.encode("utf-8")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Conflict(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_config(path):
    def reject_constant(value):
        raise Conflict(f"invalid JSON constant: {value}")

    value = json.loads(path.read_bytes().decode("utf-8"), object_pairs_hook=unique_object,
                       parse_constant=reject_constant)
    if not isinstance(value, dict):
        raise Conflict(f"configuration must be an object: {path}")
    return value


def pin_interpreter(template, provider):
    """Keep root discovery and provider fields, pinning the active host interpreter."""
    python = str(Path(sys.executable).resolve())
    if os.name == "nt" and any(character in python for character in ('"', '%', '!', '\r', '\n')):
        raise Conflict("Python path contains unsupported Windows shell characters")
    for groups in template["hooks"].values():
        for entry in groups:
            for handler in ([entry] if provider == "copilot" else entry["hooks"]):
                field = ("powershell" if provider == "copilot" else
                         "commandWindows" if provider == "codex" else "command") if os.name == "nt" else (
                             "bash" if provider == "copilot" else "command")
                command = handler[field]
                suffix = command[command.index(" -I "):]
                if os.name == "nt":
                    prefix = ("& '" + python.replace("'", "''") + "'" if provider == "copilot"
                              else '"' + python + '"')
                else:
                    prefix = shlex.quote(python)
                handler[field] = prefix + suffix


def merge_provider(existing, template, provider):
    hooks = existing.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise Conflict(f"{provider}: hooks must be an object")
    if existing.get("disableAllHooks") is True:
        raise Conflict(f"{provider}: disableAllHooks is enabled; resolve before installing hooks")
    if provider == "copilot":
        if existing.get("version", 1) != 1:
            raise Conflict("copilot: unsupported hooks version")
        existing["version"] = 1
    for event, entries in hooks.items():
        if provider == "gemini" and event == "disabled":
            if not isinstance(entries, list) or not all(isinstance(name, str) for name in entries):
                raise Conflict("gemini: hooks.disabled must be a list of names")
            if set(entries) & {"inject-brain", "auto-index-brain"}:
                raise Conflict("gemini: brain hooks are disabled; resolve before installing")
            continue
        if not isinstance(entries, list):
            raise Conflict(f"{provider}: hooks.{event} must be an array")
        for entry in entries:
            if not isinstance(entry, dict):
                raise Conflict(f"{provider}: hooks.{event} contains a non-object")
            handlers = [entry] if provider == "copilot" else entry.get("hooks")
            if not isinstance(handlers, list) or not all(isinstance(item, dict) for item in handlers):
                raise Conflict(f"{provider}: hooks.{event} contains invalid handlers")
            for handler in handlers:
                for field in ("command", "commandWindows", "bash", "powershell", "exec"):
                    if field in handler and not isinstance(handler[field], str):
                        raise Conflict(f"{provider}: hook {field} must be a string")
    original = load_config(ASSETS / "hooks" / f"{provider}.json")
    expected_entries = [(event, entry, original["hooks"][event][index])
                        for event, entries in template["hooks"].items()
                        for index, entry in enumerate(entries)]
    for event, wanted, portable in expected_entries:
        # Recognize only the two brain registrations. Ambiguous mixed handlers
        # require review rather than broad ownership inference or replacement.
        name = "inject-brain" if "inject-brain" in json.dumps(wanted) else "auto-index-brain"
        matches = [(old_event, entry) for old_event, entries in hooks.items()
                   if not (provider == "gemini" and old_event == "disabled")
                   for entry in entries if name in json.dumps(entry)]
        if matches:
            if len(matches) != 1 or matches[0][0] != event or matches[0][1] not in (wanted, portable):
                raise Conflict(f"{provider}: conflicting or ambiguous {name} registration; reconcile before retrying")
        else:
            hooks.setdefault(event, []).append(wanted)
    return existing


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--index-reviewed", action="store_true")
    parser.add_argument("--keep-existing", action="append", default=[], metavar="RELATIVE_PATH")
    parser.add_argument("--provider", choices=tuple(PROVIDERS), action="append", default=[])
    arguments = parser.parse_args()
    if sys.version_info < (3, 12):
        parser.error("Python 3.12 or newer is required")
    completed = []
    try:
        target = arguments.target.absolute()
        for ancestor in (target, *target.parents):
            if ancestor.is_symlink() or ancestor.is_junction():
                raise Conflict(f"unsafe linked target or ancestor: {ancestor}; use its real directory path")
        target = target.resolve()
        if not target.is_dir():
            raise Conflict("target must be an existing directory")
        files = payload()
        kept = set()
        for relative in arguments.keep_existing:
            path = Path(relative)
            if (path.is_absolute() or ".." in path.parts or "\\" in relative
                    or path.as_posix() != relative or relative not in files):
                raise Conflict(f"unknown or unsafe --keep-existing path: {relative}")
            if not safe_path(target, relative).is_file():
                raise Conflict(f"--keep-existing requires an existing regular file: {relative}")
            kept.add(relative)
        agents = safe_path(target, "AGENTS.md")
        files["AGENTS.md"] = agents_content(
            agents.read_bytes().decode("utf-8") if agents.exists() else "",
            (ASSETS / "AGENTS-brain.md").read_text(encoding="utf-8"),
        )
        merged_paths = {"AGENTS.md", ".gitignore"}
        for provider in sorted(set(arguments.provider)):
            config_name, directory = PROVIDERS[provider]
            config = safe_path(target, config_name)
            before = config.read_bytes() if config.exists() else None
            existing = load_config(config) if before is not None else {}
            template = load_config(ASSETS / "hooks" / f"{provider}.json")
            pin_interpreter(template, provider)
            merged = merge_provider(existing, template, provider)
            if before is not None and merged == load_config(config):
                files[config_name] = before
            else:
                files[config_name] = (json.dumps(merged, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
            merged_paths.add(config_name)
            files[f"{directory}/auto-index-brain.py"] = (ASSETS / "skills/brain/scripts/auto-index-brain.py").read_bytes()
            files[f"{directory}/inject-brain.py"] = (ASSETS / "hooks/inject-brain.py").read_bytes()
        ignore = safe_path(target, ".gitignore")
        ignore_bytes = ignore.read_bytes() if ignore.exists() else b""
        if b"/brain/.brain-index.lock" not in ignore_bytes.splitlines():
            files[".gitignore"] = ignore_bytes + (b"\n" if ignore_bytes and not ignore_bytes.endswith(b"\n") else b"") + b"/brain/.brain-index.lock\n"
        index = safe_path(target, "brain/index.md")
        safe_path(target, "brain/.brain-index.lock")
        if index.exists():
            print("REVIEW brain/index.md: preserve and migrate unique content before --index-reviewed")
            if arguments.apply and not arguments.index_reviewed:
                raise Conflict("existing brain/index.md requires --index-reviewed before any writes")
        changes = []
        for relative, content in files.items():
            path = safe_path(target, relative)
            if relative in kept:
                print(f"KEEP {relative}: verify retained content compatibility")
                continue
            if path.exists() and path.read_bytes() == content:
                continue
            if path.exists() and relative not in merged_paths:
                raise Conflict(f"content conflict: {relative}; review and reconcile before retrying")
            changes.append((relative, content))
        for relative, _ in changes:
            print(f"{'WRITE' if arguments.apply else 'PROPOSE'} {relative}")
        if not arguments.apply:
            print("Inspection complete; no files changed")
            return 0
        for relative, content in changes:
            atomic_write(safe_path(target, relative), content)
            completed.append(relative)
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-B",
             str(target / ".agents/skills/brain/scripts/auto-index-brain.py"), "--provider", "codex"],
            input=json.dumps({"cwd": str(target), "hook_event_name": "PostToolUse"}),
            text=True, capture_output=True, timeout=15,
        )
        if result.returncode or result.stderr or not index.is_file():
            raise OSError(f"indexing failed: {result.stderr.strip() or 'no index generated'}")
        inventory = index.read_text(encoding="utf-8")
        for expected in ("principles.md", "todos.md", "codebase/index.md", "plans/index.md", "audits/index.md", "archive/index.md"):
            if expected not in inventory:
                raise OSError(f"indexing failed: missing {expected}")
        print("Installation complete; brain/index.md verified")
        return 0
    except (ValueError, UnicodeError) as error:
        print(f"brain-install: {error}", file=sys.stderr)
        return 2
    except (OSError, subprocess.SubprocessError) as error:
        print(f"brain-install: {error}; completed paths: {', '.join(completed) or 'none'}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
