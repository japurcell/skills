#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from contextlib import contextmanager
from pathlib import Path

from helpers.audit import audit_log_event
from helpers.common import emit_json, read_json_input, run_command


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
    ("github_classic_pat", "high", r"gh[pousr]_[A-Za-z0-9]{36}"),
    ("github_fine_grained_pat", "high", r"github_pat_[A-Za-z0-9_]{20,}"),
    ("aws_access_key", "high", r"AKIA[0-9A-Z]{16}"),
    ("stripe_live_key", "high", r"sk_live_[0-9A-Za-z]{16,}"),
    ("slack_token", "medium", r"xox[baprs]-[0-9A-Za-z-]{10,}"),
]


@contextmanager
def temporary_env(key: str, value: str):
    previous = os.environ.get(key)
    os.environ[key] = value
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = previous


def repo_root() -> Path:
    result = run_command(["git", "rev-parse", "--show-toplevel"], cwd=str(Path.cwd()), capture_output=True)
    if result.returncode == 0:
        top_level = str(result.stdout or "").strip()
        if top_level:
            return Path(top_level)
    return Path.cwd()


def is_inside_git_repo(cwd: Path) -> bool:
    result = run_command(["git", "rev-parse", "--is-inside-work-tree"], cwd=str(cwd), capture_output=True)
    return result.returncode == 0


def git_lines(root: Path, args: list[str]) -> list[str]:
    result = run_command(["git", *args], cwd=str(root), capture_output=True)
    if result.returncode != 0:
        return []
    return [line for line in str(result.stdout or "").splitlines() if line]


def git_bytes(root: Path, args: list[str]) -> bytes | None:
    result = run_command(["git", *args], cwd=str(root), capture_output=True, text=False)
    if result.returncode != 0:
        return None
    return bytes(result.stdout or b"")


def git_has_head(root: Path) -> bool:
    return run_command(["git", "rev-parse", "--verify", "HEAD"], cwd=str(root), capture_output=True).returncode == 0


def collect_files(root: Path, scope: str, has_head: bool) -> list[str]:
    files: list[str] = []

    if scope == "staged":
        files.extend(git_lines(root, ["diff", "--cached", "--name-only", "--diff-filter=ACMRTUXB", "--"]))
    elif has_head:
        files.extend(git_lines(root, ["diff", "--name-only", "--diff-filter=ACMRTUXB", "HEAD", "--"]))
    else:
        files.extend(git_lines(root, ["diff", "--name-only", "--diff-filter=ACMRTUXB", "--"]))
        files.extend(git_lines(root, ["diff", "--cached", "--name-only", "--diff-filter=ACMRTUXB", "--"]))

    files.extend(git_lines(root, ["ls-files", "--others", "--exclude-standard"]))
    return sorted({path for path in files if path})


def untracked_files(root: Path) -> set[str]:
    return set(git_lines(root, ["ls-files", "--others", "--exclude-standard"]))


def read_candidate_bytes(root: Path, path: str, scope: str) -> bytes | None:
    if scope == "staged":
        return git_bytes(root, ["show", f":{path}"])

    file_path = root / path
    try:
        return file_path.read_bytes()
    except OSError:
        return None


def is_env_path(path: str) -> bool:
    lowered = path.lower()
    return bool(re.search(r"(^|/)\.env($|[.])", lowered))


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
    result = run_command(
        ["git", "diff", "--no-ext-diff", "--unified=0", "HEAD", "--", path],
        cwd=str(root),
        capture_output=True,
    )
    lines: list[tuple[int, str]] = []
    current_line = None
    for raw_line in str(result.stdout or "").splitlines():
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


def audit_append(
    *,
    log_path: str,
    status: str,
    session_id: str,
    timestamp: str,
    mode: str,
    scope: str,
    repo_root: Path,
    env_files: list[str],
    findings: list[dict[str, object]],
    note: str = "",
) -> None:
    payload: dict[str, object] = {
        "timestamp": timestamp,
        "sessionId": session_id,
        "repoRoot": str(repo_root),
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

    with temporary_env("AUDIT_LOG", log_path):
        audit_log_event(SCRIPT_NAME, json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


def print_findings(findings: list[dict[str, object]]) -> None:
    print("Potential secrets detected in modified files:")
    for finding in findings:
        print(
            f" - {finding['path']}:{finding['line']} "
            f"[{finding['severity']}] {finding['pattern']} {finding['redactedMatch']}"
        )
    print("Set SECRETS_ALLOWLIST to suppress intentional matches.")


def main() -> int:
    payload = read_json_input()
    if not isinstance(payload, dict):
        raise ValueError("Invalid hook input: expected a JSON object")

    session_id = str(payload.get("sessionId") or payload.get("session_id") or "")
    timestamp = str(payload.get("timestamp") or "")
    if not timestamp:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    mode = os.environ.get("SCAN_MODE", "warn")
    if mode not in {"warn", "block"}:
        mode = "warn"

    scope = os.environ.get("SCAN_SCOPE", "diff")
    if scope not in {"diff", "staged"}:
        scope = "diff"

    log_path = os.environ.get("SECRETS_LOG_DIR", str(Path.home() / ".copilot" / "hooks" / "secrets" / "scan.log"))
    root = repo_root()

    if os.environ.get("SKIP_SECRETS_SCAN") == "true":
        audit_append(
            log_path=log_path,
            status="skipped",
            session_id=session_id,
            timestamp=timestamp,
            mode=mode,
            scope=scope,
            repo_root=root,
            env_files=[],
            findings=[],
            note="scan disabled by SKIP_SECRETS_SCAN",
        )
        print("Secrets scan skipped.")
        return 0

    if not is_inside_git_repo(Path.cwd()):
        audit_append(
            log_path=log_path,
            status="skipped",
            session_id=session_id,
            timestamp=timestamp,
            mode=mode,
            scope=scope,
            repo_root=root,
            env_files=[],
            findings=[],
            note="not inside git repository",
        )
        print("Not in git repository. Skipping secrets scan.")
        return 0

    has_head = git_has_head(root)
    files = collect_files(root, scope, has_head)
    if not files:
        audit_append(
            log_path=log_path,
            status="clean",
            session_id=session_id,
            timestamp=timestamp,
            mode=mode,
            scope=scope,
            repo_root=root,
            env_files=[],
            findings=[],
            note="no modified files to scan",
        )
        print("No modified files to scan.")
        return 0

    untracked = untracked_files(root) if scope == "diff" and has_head else set()
    allowlist = parse_allowlist_csv(os.environ.get("SECRETS_ALLOWLIST"))
    env_files: list[str] = []
    findings: list[dict[str, object]] = []

    for path in files:
        candidate_bytes = read_candidate_bytes(root, path, scope)
        if candidate_bytes is None:
            continue

        if is_env_path(path) and path not in env_files:
            env_files.append(path)

        if not is_text_candidate(path, candidate_bytes):
            continue

        candidate_text = candidate_bytes.decode("utf-8", errors="replace")

        if is_credential_path(path):
            allowlist_text = f"{path}:1:credential_path:[SENSITIVE PATH]"
            if not allowlist_contains(allowlist_text, allowlist):
                findings.append(
                    {
                        "pattern": "credential_path",
                        "severity": "critical",
                        "path": path,
                        "line": 1,
                        "redactedMatch": "[SENSITIVE PATH]",
                    }
                )

        if scope == "staged" or not has_head or path in untracked:
            candidate_lines = enumerate_file_lines(candidate_text)
        else:
            candidate_lines = emit_diff_added_lines(root, path)

        for line_number, line_text in candidate_lines:
            for pattern_name, severity, regex in PATTERNS:
                for match in re.finditer(regex, line_text):
                    match_value = match.group(0)
                    allowlist_text = f"{path}:{line_number}:{pattern_name}:{match_value}"
                    if allowlist_contains(allowlist_text, allowlist):
                        continue
                    findings.append(
                        {
                            "pattern": pattern_name,
                            "severity": severity,
                            "path": path,
                            "line": line_number,
                            "redactedMatch": redact_match(match_value),
                        }
                    )

    if not findings:
        audit_append(
            log_path=log_path,
            status="clean",
            session_id=session_id,
            timestamp=timestamp,
            mode=mode,
            scope=scope,
            repo_root=root,
            env_files=env_files,
            findings=[],
        )
        print("Secrets scan clean.")
        return 0

    audit_append(
        log_path=log_path,
        status="findings",
        session_id=session_id,
        timestamp=timestamp,
        mode=mode,
        scope=scope,
        repo_root=root,
        env_files=env_files,
        findings=findings,
    )
    print_findings(findings)
    return 1 if mode == "block" else 0


if __name__ == "__main__":
    raise SystemExit(main())
