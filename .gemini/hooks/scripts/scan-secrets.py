#!/usr/bin/env python3

from __future__ import annotations

import fcntl
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.audit import audit_init  # noqa: E402
from helpers.common import emit_json, read_json_input  # noqa: E402


SCRIPT_NAME = Path(__file__).name
TEXT_EXTENSIONS = {
    ".c",
    ".cc",
    ".cfg",
    ".conf",
    ".cpp",
    ".cs",
    ".css",
    ".csv",
    ".env",
    ".go",
    ".h",
    ".html",
    ".ini",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".kt",
    ".md",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".sh",
    ".sql",
    ".svg",
    ".tf",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
PATTERNS = [
    ("github_classic_pat", "high", re.compile(r"gh[pousr]_[A-Za-z0-9]{36}")),
    ("github_fine_grained_pat", "high", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("aws_access_key", "high", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("stripe_live_key", "high", re.compile(r"sk_live_[0-9A-Za-z]{16,}")),
    ("slack_token", "medium", re.compile(r"xox[baprs]-[0-9A-Za-z-]{10,}")),
]


def noop() -> None:
    emit_json({})
    raise SystemExit(0)


def warn_and_noop(message: str) -> None:
    print(message, file=sys.stderr)
    noop()


def read_payload(mode: str) -> dict:
    payload: dict | None = None
    try:
        payload = read_json_input()
    except Exception as exc:
        if mode == "block":
            print(f"{SCRIPT_NAME}: {exc}", file=sys.stderr)
            raise SystemExit(1)
        warn_and_noop(f"{SCRIPT_NAME}: {exc}")

    if not isinstance(payload, dict):
        if mode == "block":
            print(f"{SCRIPT_NAME}: invalid JSON input.", file=sys.stderr)
            raise SystemExit(1)
        warn_and_noop(f"{SCRIPT_NAME}: invalid JSON input; skipping hook.")

    return payload


def git_available() -> bool:
    return shutil.which("git") is not None


def run_git(args: list[str], *, cwd: Path, text: bool = True) -> str | bytes | None:
    import subprocess

    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=text,
            check=False,
        )
    except OSError:
        return None

    if result.returncode != 0:
        return None

    return result.stdout


def repo_root(work_dir: Path) -> Path:
    output = run_git(["rev-parse", "--show-toplevel"], cwd=work_dir)
    if isinstance(output, str):
        root = output.strip()
        if root:
            return Path(root)
    return work_dir


def is_inside_git_repo(work_dir: Path) -> bool:
    output = run_git(["rev-parse", "--is-inside-work-tree"], cwd=work_dir)
    return isinstance(output, str)


def has_head(root: Path) -> bool:
    return run_git(["rev-parse", "--verify", "HEAD"], cwd=root) is not None


def collect_files(root: Path, scope: str, root_has_head: bool) -> list[str]:
    files: list[str] = []

    if scope == "staged":
        output = run_git(["diff", "--cached", "--name-only", "--diff-filter=ACMRTUXB", "--"], cwd=root)
        if isinstance(output, str):
            files.extend(line for line in output.splitlines() if line)
    elif root_has_head:
        output = run_git(["diff", "--name-only", "--diff-filter=ACMRTUXB", "HEAD", "--"], cwd=root)
        if isinstance(output, str):
            files.extend(line for line in output.splitlines() if line)
    else:
        output = run_git(["diff", "--name-only", "--diff-filter=ACMRTUXB", "--"], cwd=root)
        if isinstance(output, str):
            files.extend(line for line in output.splitlines() if line)
        output = run_git(["diff", "--cached", "--name-only", "--diff-filter=ACMRTUXB", "--"], cwd=root)
        if isinstance(output, str):
            files.extend(line for line in output.splitlines() if line)

    output = run_git(["ls-files", "--others", "--exclude-standard"], cwd=root)
    if isinstance(output, str):
        files.extend(line for line in output.splitlines() if line)

    return sorted({path for path in files if path})


def untracked_files(root: Path) -> set[str]:
    output = run_git(["ls-files", "--others", "--exclude-standard"], cwd=root)
    if not isinstance(output, str):
        return set()
    return {line for line in output.splitlines() if line}


def read_candidate_bytes(root: Path, path: str, scope: str) -> bytes | None:
    if scope == "staged":
        output = run_git(["show", f":{path}"], cwd=root, text=False)
        return output if isinstance(output, bytes) else None

    candidate = root / path
    try:
        return candidate.read_bytes()
    except OSError:
        return None


def is_env_path(path: str) -> bool:
    return bool(re.search(r"(^|/)\.env($|[.])", path.lower()))


def is_credential_path(path: str) -> bool:
    lowered = path.lower()
    base_name = lowered.rsplit("/", 1)[-1]
    if base_name in {"credentials", ".git-credentials"}:
        return True
    if base_name.startswith("credentials."):
        return True

    return any(
        re.search(pattern, lowered)
        for pattern in (
            r"(^|/)\.ssh(/|$)",
            r"(^|/)\.aws(/|$)",
            r"(^|/)\.gnupg(/|$)",
            r"(^|/)\.?credentials(/|$)",
            r"(^|/)\.?secrets(/|$)",
        )
    )


def is_text_candidate(path: str, raw_bytes: bytes) -> bool:
    if b"\0" in raw_bytes:
        return False
    try:
        raw_bytes.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return Path(path).suffix.lower() in TEXT_EXTENSIONS


def enumerate_file_lines(text: str) -> list[tuple[int, str]]:
    return [(index + 1, line) for index, line in enumerate(text.splitlines())]


def emit_diff_added_lines(root: Path, path: str) -> list[tuple[int, str]]:
    output = run_git(["diff", "--no-ext-diff", "--unified=0", "HEAD", "--", path], cwd=root)
    if not isinstance(output, str):
        return []

    lines: list[tuple[int, str]] = []
    current_line: int | None = None
    for raw_line in output.splitlines():
        if raw_line.startswith("+++"):
            continue
        if raw_line.startswith("@@"):
            match = re.search(r"\+(\d+)", raw_line)
            current_line = int(match.group(1)) if match else None
            continue
        if raw_line.startswith("+") and current_line is not None:
            lines.append((current_line, raw_line[1:]))
            current_line += 1
    return lines


def redact_match(match: str) -> str:
    if len(match) <= 8:
        return "[REDACTED]"
    return f"{match[:4]}...{match[-4:]}"


def parse_allowlist_csv(raw_allowlist: str | None) -> list[str]:
    if not raw_allowlist:
        return []
    return [entry.strip() for entry in raw_allowlist.split(",") if entry.strip()]


def allowlist_contains(text: str, entries: list[str]) -> bool:
    return any(entry in text for entry in entries)


def rotate_scan_log(log_path: Path, max_bytes: int = 1048576, backups: int = 3) -> None:
    try:
        if not log_path.exists() or log_path.stat().st_size < max_bytes:
            return
    except OSError:
        return

    for index in range(backups, 0, -1):
        current = log_path.with_name(f"{log_path.name}.{index}")
        next_path = log_path.with_name(f"{log_path.name}.{index + 1}")
        if not current.exists():
            continue
        try:
            if index == backups:
                os.remove(current)
            else:
                current.replace(next_path)
        except OSError:
            return

    try:
        log_path.replace(log_path.with_name(f"{log_path.name}.1"))
    except OSError:
        return


def append_scan_log(
    *,
    log_path: Path,
    status: str,
    session_id: str,
    timestamp: str,
    mode: str,
    scope: str,
    repo_root_path: Path,
    env_files: list[str],
    findings: list[dict[str, object]],
    note: str = "",
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, object] = {
        "timestamp": timestamp,
        "sessionId": session_id,
        "repoRoot": str(repo_root_path),
        "mode": mode,
        "scope": scope,
        "status": status,
    }
    if note:
        payload["note"] = note
    if env_files:
        payload["envFiles"] = env_files
    if findings:
        payload["findings"] = findings

    lock_path = log_path.with_name(f"{log_path.name}.lock")
    lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        rotate_scan_log(
            log_path,
            int(os.environ.get("AUDIT_LOG_MAX_BYTES", "1048576")),
            int(os.environ.get("AUDIT_LOG_MAX_BACKUPS", "3")),
        )
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)


def build_findings_json(findings: list[tuple[str, str, str, int, str]]) -> list[dict[str, object]]:
    return [
        {
            "pattern": pattern_name,
            "severity": severity,
            "path": path,
            "line": line_number,
            "redactedMatch": redacted,
        }
        for pattern_name, severity, path, line_number, redacted in findings
    ]


def emit_output(findings_count: int, log_path: Path) -> None:
    if findings_count > 0:
        emit_json({"systemMessage": f"Potential secrets detected in modified files. See {log_path}."})
        return
    emit_json({})


def main() -> int:
    mode = os.environ.get("SCAN_MODE", "block")
    if mode not in {"warn", "block"}:
        mode = "block"

    if not git_available():
        if mode == "block":
            emit_json({"decision": "deny", "reason": f"{SCRIPT_NAME}: required command not found: git"})
            return 0
        warn_and_noop(f"{SCRIPT_NAME}: required command not found: git")

    if not audit_init():
        if mode == "block":
            emit_json({"decision": "deny", "reason": f"{SCRIPT_NAME}: failed to initialize audit logging."})
            return 0
        warn_and_noop(f"{SCRIPT_NAME}: failed to initialize audit logging; skipping hook.")

    payload = read_payload(mode)
    session_id = str(payload.get("session_id") or "")
    timestamp = str(payload.get("timestamp") or "")
    hook_cwd = str(payload.get("cwd") or "")

    scope = os.environ.get("SCAN_SCOPE", "diff")
    if scope not in {"diff", "staged"}:
        scope = "diff"

    log_dir_str = os.environ.get("SECRETS_LOG_DIR", str(Path.home() / ".gemini" / "hooks" / "secrets"))
    log_path = Path(log_dir_str)
    if log_path.is_dir() or not log_path.suffix:
        scan_log = log_path / "scan.log"
    elif log_path.suffix.lower() == ".log":
        if log_path.parent.exists() and log_path.parent.is_file():
            scan_log = log_path.parent.parent / "secrets" / log_path.name
        else:
            scan_log = log_path
    else:
        scan_log = log_path / "scan.log"
    work_dir = Path(hook_cwd or os.environ.get("GEMINI_PROJECT_DIR") or Path.cwd())

    if not timestamp:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if os.environ.get("SKIP_SECRETS_SCAN") == "true":
        append_scan_log(
            log_path=scan_log,
            status="skipped",
            session_id=session_id,
            timestamp=timestamp,
            mode=mode,
            scope=scope,
            repo_root_path=work_dir,
            env_files=[],
            findings=[],
            note="scan disabled by SKIP_SECRETS_SCAN",
        )
        emit_output(0, scan_log)
        return 0

    if not is_inside_git_repo(work_dir):
        append_scan_log(
            log_path=scan_log,
            status="skipped",
            session_id=session_id,
            timestamp=timestamp,
            mode=mode,
            scope=scope,
            repo_root_path=work_dir,
            env_files=[],
            findings=[],
            note="not inside git repository",
        )
        emit_output(0, scan_log)
        return 0

    root = repo_root(work_dir)
    root_has_head = has_head(root)
    files = collect_files(root, scope, root_has_head)

    if not files:
        append_scan_log(
            log_path=scan_log,
            status="clean",
            session_id=session_id,
            timestamp=timestamp,
            mode=mode,
            scope=scope,
            repo_root_path=root,
            env_files=[],
            findings=[],
            note="no modified files to scan",
        )
        emit_output(0, scan_log)
        return 0

    allowlist = parse_allowlist_csv(os.environ.get("SECRETS_ALLOWLIST"))
    env_files: list[str] = []
    findings: list[tuple[str, str, str, int, str]] = []

    untracked = untracked_files(root) if scope == "diff" and root_has_head else set()

    for path in files:
        raw_bytes = read_candidate_bytes(root, path, scope)
        if raw_bytes is None:
            continue

        if is_env_path(path) and path not in env_files:
            env_files.append(path)

        if not is_text_candidate(path, raw_bytes):
            continue

        if scope == "staged" or not root_has_head or path in untracked:
            candidate_lines = enumerate_file_lines(raw_bytes.decode("utf-8", errors="replace"))
        else:
            candidate_lines = emit_diff_added_lines(root, path)

        if is_credential_path(path):
            allowlist_text = f"{path}:1:credential_path:[SENSITIVE PATH]"
            if not allowlist_contains(allowlist_text, allowlist):
                findings.append(("credential_path", "critical", path, 1, "[SENSITIVE PATH]"))

        for line_number, line_text in candidate_lines:
            for pattern_name, severity, regex in PATTERNS:
                for match in regex.finditer(line_text):
                    match_value = match.group(0)
                    allowlist_text = f"{path}:{line_number}:{pattern_name}:{match_value}"
                    if allowlist_contains(allowlist_text, allowlist):
                        continue
                    findings.append(
                        (pattern_name, severity, path, line_number, redact_match(match_value))
                    )

    if not findings:
        append_scan_log(
            log_path=scan_log,
            status="clean",
            session_id=session_id,
            timestamp=timestamp,
            mode=mode,
            scope=scope,
            repo_root_path=root,
            env_files=env_files,
            findings=[],
        )
        emit_output(0, scan_log)
        return 0

    findings_json = build_findings_json(findings)
    append_scan_log(
        log_path=scan_log,
        status="findings",
        session_id=session_id,
        timestamp=timestamp,
        mode=mode,
        scope=scope,
        repo_root_path=root,
        env_files=env_files,
        findings=findings_json,
    )
    if mode == "block":
        emit_json({"decision": "deny", "reason": f"Potential secrets detected in modified files. See {scan_log}."})
    else:
        emit_output(len(findings), scan_log)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
