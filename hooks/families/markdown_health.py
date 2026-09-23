"""Render self-contained, provider-specific touched Markdown hooks."""

from __future__ import annotations

from hooks.manifest import GeneratedTarget
from hooks.providers import Provider


RUNTIME = r'''from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import re
import shlex
import sys
import tempfile
import time
from urllib.parse import unquote, urlsplit

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from helpers.common import emit_json, read_json_input
from helpers.audit import audit_log_event

PROVIDER = __PROVIDER__
LIMIT_SECONDS = 8
MAX_PATHS = 10000
MAX_STATE_BYTES = 1024 * 1024
MAX_FILE_BYTES = 4 * 1024 * 1024
MAX_RESPONSE = 8192
MAX_AUDIT = 4096
FENCE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})(?:[^`\n]*)?$")
HEADING = re.compile(r"^[ \t]{0,3}#{1,6}[ \t]+(.+?)[ \t]*#*[ \t]*$")
REFERENCE = re.compile(r"^[ \t]{0,3}\[([^\]]+)\]:[ \t]*(?:<([^>]+)>|(\S+))")


class Incomplete(Exception):
    pass


def budget(deadline):
    if time.monotonic() >= deadline:
        raise Incomplete("Markdown check timed out")


def digest(path, deadline):
    budget(deadline)
    if path.stat().st_size > MAX_FILE_BYTES:
        raise Incomplete("Markdown file exceeds size limit")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root, deadline):
    result = {}
    for directory, dirs, files in os.walk(root):
        budget(deadline)
        dirs[:] = [item for item in dirs if item not in {".git", "node_modules", ".agents/scratchpad"}]
        for name in files:
            if Path(name).suffix.lower() not in {".md", ".markdown"}:
                continue
            path = Path(directory) / name
            relative = path.relative_to(root).as_posix()
            if len(result) >= MAX_PATHS:
                raise Incomplete("Markdown baseline exceeds file limit")
            if path.is_symlink():
                continue
            details = path.stat()
            result[relative] = [details.st_size, details.st_mtime_ns]
    return result


def slug(text):
    text = re.sub(r"<[^>]*>", "", text)
    text = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s]+", "-", text.strip())


def visible_lines(text):
    lines = text.splitlines()
    visible = []
    opening = None
    for number, line in enumerate(lines, 1):
        match = FENCE.match(line)
        if opening:
            if re.match(r"^[ \t]{0,3}" + re.escape(opening[0]) + "{" + str(opening[1]) + r",}[ \t]*$", line):
                opening = None
            visible.append("")
            continue
        if match:
            marker = match.group(1)
            opening = (marker[0], len(marker), number)
            visible.append("")
            continue
        visible.append(re.sub(r"(`+)(.*?)\1", "", line))
    return visible, opening


def local_target(root, document, raw, headings, deadline):
    raw = re.sub(r"\\([\\()<>])", r"\1", raw)
    parsed = urlsplit(raw)
    if parsed.scheme or raw.startswith("//"):
        return None
    if PureWindowsPath(raw).is_absolute():
        return "outside workspace, not checked"
    candidate = (document.parent / unquote(parsed.path)).resolve() if parsed.path else document
    try:
        candidate.relative_to(root)
    except ValueError:
        return "outside workspace, not checked"
    budget(deadline)
    if not candidate.exists():
        return "missing local target"
    if parsed.fragment:
        if candidate.suffix.lower() not in {".md", ".markdown"}:
            return None
        if candidate not in headings:
            headings[candidate] = heading_slugs(candidate, deadline)
        if unquote(parsed.fragment).lower() not in headings[candidate]:
            return "missing heading fragment"
    return None


def heading_slugs(path, deadline):
    budget(deadline)
    if path.stat().st_size > MAX_FILE_BYTES:
        raise Incomplete("Linked Markdown file exceeds size limit")
    text = path.read_text(encoding="utf-8")
    lines, _ = visible_lines(text)
    counts = {}
    found = set()
    for line in lines:
        budget(deadline)
        match = HEADING.match(line)
        if match:
            base = slug(match.group(1))
            count = counts.get(base, 0)
            found.add(base if count == 0 else f"{base}-{count}")
            counts[base] = count + 1
    return found


def balanced_close(text, start, opening, closing):
    depth = 0
    index = start
    while index < len(text):
        if text[index] == "\\":
            index += 2
            continue
        if text[index] == opening:
            depth += 1
        elif text[index] == closing:
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return None


def links_in(line):
    index = 0
    while index < len(line):
        if line[index] != "[" or (index and line[index - 1] == "\\"):
            index += 1
            continue
        label_end = balanced_close(line, index, "[", "]")
        if label_end is None or label_end + 1 >= len(line):
            index += 1
            continue
        label = line[index + 1:label_end]
        next_character = line[label_end + 1]
        if next_character == "[":
            reference_end = balanced_close(line, label_end + 1, "[", "]")
            if reference_end is not None:
                yield label, None, line[label_end + 2:reference_end] or label
                index = reference_end + 1
                continue
        if next_character != "(":
            index = label_end + 1
            continue
        start = label_end + 2
        while start < len(line) and line[start] in " \t":
            start += 1
        if start < len(line) and line[start] == "<":
            end = line.find(">", start + 1)
            if end != -1 and ")" in line[end + 1:]:
                yield label, line[start + 1:end], None
                index = line.find(")", end + 1) + 1
                continue
        end = balanced_close(line, label_end + 1, "(", ")")
        if end is not None:
            target = line[start:end]
            target = re.split(r"(?<!\\)[ \t]+", target, maxsplit=1)[0]
            yield label, target, None
            index = end + 1
            continue
        index = label_end + 1


def findings_for(root, relative, deadline):
    document = (root / relative).resolve()
    if not document.is_relative_to(root):
        raise Incomplete("Touched Markdown path leaves workspace")
    text = document.read_text(encoding="utf-8")
    lines, opening = visible_lines(text)
    findings = []
    if opening:
        findings.append((relative, opening[2], "unclosed fence", ""))
    references = {}
    for line in lines:
        match = REFERENCE.match(line)
        if match:
            references[" ".join(match.group(1).lower().split())] = match.group(2) or match.group(3)
    headings = {}
    for number, line in enumerate(lines, 1):
        budget(deadline)
        if REFERENCE.match(line):
            continue
        for label, inline, reference in links_in(line):
            if reference is not None:
                key = " ".join(reference.lower().split())
                if key not in references:
                    findings.append((relative, number, "undefined reference", key))
                    continue
                target = references[key]
            else:
                target = inline or ""
            problem = local_target(root, document, target, headings, deadline)
            if problem:
                findings.append((relative, number, problem, target if problem != "outside workspace, not checked" else ""))
    for key, target in references.items():
        problem = local_target(root, document, target, headings, deadline)
        if problem:
            findings.append((relative, 1, problem, target if problem != "outside workspace, not checked" else ""))
    return findings


def safe_path(value):
    if not isinstance(value, str):
        return None
    path = value.replace("\\", "/")
    if Path(path).suffix.lower() not in {".md", ".markdown"}:
        return None
    return path


def direct_paths(value):
    result = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"path", "file_path", "filename", "fileName"}:
                candidate = safe_path(child)
                if candidate:
                    result.add(candidate)
            elif isinstance(child, (dict, list)):
                result.update(direct_paths(child))
    elif isinstance(value, list):
        for child in value:
            result.update(direct_paths(child))
    return result


def state_path(root, session):
    directory = Path(os.environ.get("MARKDOWN_HEALTH_STATE_DIR", str(Path.home() / f".{PROVIDER}" / "hooks" / "markdown-health-state")))
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    if directory.is_symlink():
        raise Incomplete("Markdown state directory is linked")
    key = hashlib.sha256((session + "\0" + str(root)).encode()).hexdigest()
    return directory / (key + ".json")


def load_state(path):
    if not path.exists():
        return None
    if path.is_symlink() or time.time() - path.stat().st_mtime > 86400:
        raise Incomplete("Markdown session state is stale or linked")
    if path.stat().st_size > MAX_STATE_BYTES:
        raise Incomplete("Markdown session state exceeds size limit")
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path, state):
    serialized = json.dumps(state, separators=(",", ":")).encode("utf-8")
    if len(serialized) > MAX_STATE_BYTES:
        raise Incomplete("Markdown session state exceeds size limit")
    fd, name = tempfile.mkstemp(prefix=".markdown-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def audit(status, paths, count, context):
    def sanitize(value):
        return re.sub(r"[^A-Za-z0-9._/-]", "_", value)[:256]
    prefix = f"timestamp={int(time.time())} sender=markdown-health session={sanitize(context[0])} event={sanitize(context[1])} status={status} checked={len(paths)} findings={count} "
    listed = []
    for item in sorted(paths):
        candidate = ",".join([*listed, sanitize(item)])
        if len((prefix + f"omitted={len(paths)-len(listed)-1} files={candidate}").encode()) > MAX_AUDIT - 128:
            break
        listed.append(sanitize(item))
    line = prefix + f"omitted={len(paths)-len(listed)} files={','.join(listed)}"
    if PROVIDER != "codex":
        if not audit_log_event("markdown-health", line):
            raise OSError("audit write failed")
        return
    path = Path(os.environ.get("AUDIT_LOG", str(Path.home() / ".codex" / "hooks" / "logs" / "audit.log")))
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.is_symlink() or path.parent.is_symlink():
        raise OSError("linked audit path")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        if hasattr(os, "fchmod"):
            os.fchmod(fd, 0o600)
        with os.fdopen(fd, "ab", closefd=False) as handle:
            handle.write((line + "\n").encode())
            handle.flush()
            os.fsync(fd)
    finally:
        os.close(fd)


def response(event, status, findings, warning, retry):
    if status == "pass" and not findings and not warning:
        return {"decision": "allow"} if event == "final" and PROVIDER != "gemini" else {}
    shown = [f"{path}:{line}: {rule}" + (f" ({target})" if target else "")
             for path, line, rule, target in findings[:20]]
    rerun_path = shlex.quote(findings[0][0]) if findings else "<path>"

    def build(rows):
        lines = [*rows]
        if len(findings) > len(rows):
            lines.append(f"{len(findings)-len(rows)} more findings omitted")
        if warning:
            lines.append(warning)
        rerun = "python3 ~/." + PROVIDER + "/hooks/" + ("scripts/" if PROVIDER != "codex" else "") + "markdown-health.py --check"
        rerun += " " + rerun_path
        lines.append("Rerun: " + rerun)
        message = "Markdown health " + status + ": " + "\n".join(lines)
        if PROVIDER == "gemini":
            if event == "final" and status == "fail" and retry < 2:
                return {"decision": "deny", "reason": message}
            if event == "post":
                return {"systemMessage": message, "hookSpecificOutput": {"additionalContext": message}}
            return {"systemMessage": message}
        if PROVIDER == "codex":
            if event == "final":
                return {"decision": "block" if status == "fail" and retry < 2 else "allow", "reason": message}
            return {"systemMessage": message, "hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": message}}
        if event == "final":
            return {"decision": "block" if status == "fail" and retry < 2 else "allow", "reason": message}
        return {"additionalContext": message}

    result = build(shown)
    while len(json.dumps(result, ensure_ascii=False, separators=(",", ":")).encode()) > MAX_RESPONSE and shown:
        shown.pop()
        result = build(shown)
    if len(json.dumps(result, ensure_ascii=False, separators=(",", ":")).encode()) > MAX_RESPONSE:
        rerun_path = "<path>"
        result = build(shown)
    return result


def main():
    event = os.environ.get("MARKDOWN_HEALTH_EVENT", "post")
    paths = []
    checked = []
    content_fingerprints = []
    findings = []
    warning = ""
    state = None
    session = ""
    try:
        payload = read_json_input()
        if not isinstance(payload, dict):
            raise Incomplete("Invalid Markdown hook input")
        session = payload.get("sessionId") or payload.get("session_id") or ""
        root_value = payload.get("cwd")
        if not isinstance(root_value, str) or not Path(root_value).is_dir() or not isinstance(session, str) or not session:
            raise Incomplete("Missing workspace or session key")
        root = Path(root_value).resolve()
        deadline = time.monotonic() + LIMIT_SECONDS
        state_file = state_path(root, session)
        state = load_state(state_file)
        if event == "pre":
            if state is None:
                state = {"baseline": snapshot(root, deadline), "touched": [], "last": None, "retries": 0}
            save_state(state_file, state)
            emit_json({})
            return
        if state is None:
            raise Incomplete("No complete Markdown session baseline")
        current = snapshot(root, deadline)
        touched = set(state["touched"])
        touched.update(path for path in set(current) | set(state["baseline"]) if current.get(path) != state["baseline"].get(path))
        tool_input = payload.get("toolArgs", payload.get("tool_input", {}))
        for raw in direct_paths(tool_input):
            candidate = Path(raw)
            if not candidate.is_absolute():
                candidate = root / candidate
            resolved = candidate.resolve()
            if resolved.is_relative_to(root):
                touched.add(resolved.relative_to(root).as_posix())
        paths = sorted(path for path in touched if path in current)
        if not paths:
            emit_json({"decision": "allow"} if event == "final" and PROVIDER != "gemini" else {})
            return
        state["touched"] = sorted(touched)
        for path in paths:
            findings.extend(findings_for(root, path, deadline))
            content_fingerprints.append((path, digest(root / path, deadline)))
            checked.append(path)
        status = "fail" if any(item[2] != "outside workspace, not checked" for item in findings) else "pass"
        fingerprint = hashlib.sha256(json.dumps(content_fingerprints).encode()).hexdigest()
        if event == "final" and status == "fail":
            state["retries"] += 1
        duplicate = event == "final" and state.get("last") == [fingerprint, status]
        if not duplicate:
            try:
                audit(status, paths, len(findings), (session, event))
            except OSError:
                warning = "audit unavailable"
        state["last"] = [fingerprint, status]
        save_state(state_file, state)
    except Exception as exc:
        status = "incomplete"
        warning = str(exc) if isinstance(exc, Incomplete) else "Markdown checker failed"
        if paths:
            try:
                audit(status, checked, len(findings), (session, event))
            except OSError:
                warning += "; audit unavailable"
    result = response(event, status, findings, warning, state.get("retries", 0) - 1 if state else 0)
    emit_json(result)


def explicit_check():
    if len(sys.argv) < 3:
        print("usage: markdown-health.py --check PATH [PATH ...]", file=sys.stderr)
        return 2
    root = Path.cwd().resolve()
    deadline = time.monotonic() + LIMIT_SECONDS
    try:
        all_findings = []
        for name in sys.argv[2:]:
            document = Path(name).resolve()
            if not document.is_relative_to(root) or document.suffix.lower() not in {".md", ".markdown"}:
                raise Incomplete("Only workspace Markdown paths may be checked")
            all_findings.extend(findings_for(root, document.relative_to(root).as_posix(), deadline))
    except Exception:
        print("Markdown check incomplete", file=sys.stderr)
        return 2
    for path, line, rule, target in all_findings:
        print(f"{path}:{line}: {rule}" + (f" ({target})" if target else ""))
    return 1 if any(item[2] != "outside workspace, not checked" for item in all_findings) else 0


if __name__ == "__main__":
    if sys.argv[1:2] == ["--check"]:
        raise SystemExit(explicit_check())
    main()
'''


def render(provider: Provider, target: GeneratedTarget) -> str:
    if target.provider != provider.name or provider.name not in {"copilot", "gemini", "codex"}:
        raise ValueError(f"Unsupported Markdown hook target: {target.output_path}")
    return (
        "#!/usr/bin/env python3\n"
        "# Generated from hooks/families/markdown_health.py by scripts/generate-hooks.py. Do not edit.\n"
        + RUNTIME.replace("__PROVIDER__", repr(provider.name))
    )
