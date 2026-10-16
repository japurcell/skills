"""Thin native provider adapters for the maintained normal scanner engine."""
from __future__ import annotations
from hooks.families.diagnostics import collector_source
from hooks.families.reporting import build_identity
from hooks.manifest import GeneratedTarget
from hooks.providers import Provider

SHEBANG = '#!/usr/bin/env python3\n'
HEADER = '# Generated from hooks/families/scan_secrets.py by scripts/generate-hooks.py. Do not edit.\n'
ADAPTER_START = '# BEGIN PROVIDER ADAPTER\n'
ADAPTER_END = '# END PROVIDER ADAPTER\n'


_PRELUDE_SOURCE = r'''
from __future__ import annotations

import codecs
import contextlib
import json
import os
import re
import shutil
import signal
import stat
import sys
import tempfile
import time
import unicodedata
from collections.abc import Iterator
from datetime import datetime, timezone
from typing import BinaryIO
from pathlib import Path, PurePosixPath

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.common import emit_json, read_json_input  # noqa: E402

# __DIAGNOSTIC_BOOTSTRAP__


SCRIPT_NAME = Path(__file__).name
MAX_FILES = 256
MAX_TOTAL_BYTES = 8388608
MAX_GIT_OUTPUT_BYTES = 8388608
MAX_SCAN_SECONDS = 8.0
INCOMPLETE_LOG = None
SCAN_ACTION = "scan"
SCAN_RESULT = None
SCAN_SECURITY_OUTCOME = "incomplete"
REPORT_BUILD = "__REPORT_BUILD__"
REPORT_PROVIDER = DIAG_PROVIDER

# Optional detector assets load only after exact diagnostics recovery routing.
_SCAN_RUNTIME_ERROR = None
try:
    from helpers.scan_native_file import WindowsDirectoryHandles
    from helpers.scan_types import ScanLimits, ScanFailure, ScanSecurityError, GitCommandError
    from helpers.scan_engine import ScanPolicy, scan
    from helpers.scan_allowlist import parse_allowlist
    from helpers.scan_audit import AuditPolicy, append_scan_log as _write_scan_log
except Exception:
    _SCAN_RUNTIME_ERROR = True


def noop():
    emit_json({})
    raise SystemExit(0)
'''


_COPILOT_RESPONSE_ADAPTER = r'''
def block_denial_payload(reason: str, hook_event: str) -> dict:
    return {
        "continue": True,
        "permissionDecision": "deny",
        "hookSpecificOutput": {
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        },
        "permissionDecisionReason": reason,
    }


def emit_block_denial(reason: str) -> None:
    emit_json(block_denial_payload(reason, HOOK_EVENT))
'''


_GEMINI_RESPONSE_ADAPTER = r'''
def block_denial_payload(reason: str, hook_event: str) -> dict:
    return {"decision": "deny", "reason": reason}


def emit_block_denial(reason: str) -> None:
    emit_json(block_denial_payload(reason, HOOK_EVENT))
'''


_CODEX_RESPONSE_ADAPTER = r'''
def block_denial_payload(reason: str, hook_event: str) -> dict:
    if hook_event != "PreToolUse":
        return {"decision": "block", "reason": reason}
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        },
    }


def emit_block_denial(reason: str) -> None:
    emit_json(block_denial_payload(reason, HOOK_EVENT))
'''


_POLICY_SOURCE = r'''def scanner_attribution(security: str, audit: str, enforcement: str, route: str, cause: str) -> str:
    return (f"security_outcome={security}; audit_outcome={audit}; enforcement={enforcement}; build={REPORT_BUILD}; "
            f"profile=pending_snapshots_v1; route={route}; cause={cause}.")


def emit_output(findings_count: int, log_path: Path, checked_files: int = 0, skipped: bool = False) -> None:
    if findings_count > 0:
        emit_json({"systemMessage": f"scan-secrets warning: {SCAN_ACTION}; potential secrets detected. "
                   + scanner_attribution("findings", "written", "allow", "pending_scan", "findings")})
        return
    if HOOK_EVENT == "Stop":
        if skipped:
            emit_json({"systemMessage": "scan-secrets: skipped"})
        else:
            emit_json({"systemMessage": f"scan-secrets: pass; {checked_files} modified {'file' if checked_files == 1 else 'files'}"})
        return
    emit_json({})


def normalized_mode_from_env() -> str:
    mode = os.environ.get("SCAN_MODE", "block")
    if mode not in {"warn", "block"}:
        return "block"
    return mode


def append_scan_log(**kwargs):
    global SCAN_SECURITY_OUTCOME
    if kwargs.get("status") != "incomplete":
        SCAN_SECURITY_OUTCOME = kwargs.get("status", "incomplete")
    result = SCAN_RESULT
    if result is not None:
        result.audit_outcome = "written"
        kwargs["scan_result"] = result.summary()
    try:
        _write_scan_log(AuditPolicy(REPORT_BUILD, REPORT_PROVIDER, SCAN_ACTION, MAX_FILES,
                        os.environ.get("AUDIT_LOG_MAX_BYTES", "1048576"),
                        os.environ.get("AUDIT_LOG_MAX_BACKUPS", "3")), **kwargs)
    except BaseException:
        if result is not None:
            result.audit_outcome = "failed"
            result.outcome = "incomplete"
            if result.failure is None:
                result.reason = "audit_unavailable"
        raise


def handle_unexpected_exception(exc):
    mode = normalized_mode_from_env()
    failure = exc if isinstance(exc, ScanFailure) else ScanFailure("internal_error")
    detail = failure.detail()
    outcome = "blocked" if mode == "block" else "warning"
    result = SCAN_RESULT
    processed = result.counts["processed_findings"] if result else 0
    security = "findings" if processed else SCAN_SECURITY_OUTCOME
    audit = "failed"
    if INCOMPLETE_LOG is not None:
        try:
            append_scan_log(**INCOMPLETE_LOG, status="incomplete", env_files=result.env_files if result else [],
                            findings=result.findings if result else [],
                            omitted_findings=max(0, processed - len(result.findings)) if result else 0,
                            findings_truncated=bool(result and (processed > len(result.findings))),
                            note=detail, diagnostic=failure.diagnostic(), security_outcome=security)
            audit = "written"
        except Exception:
            pass
    finding_message = "potential secrets detected; scan incomplete." if processed else "scan incomplete; potential secrets could not be checked."
    reason = (f"scan-secrets {outcome}: {SCAN_ACTION}; {finding_message} {detail} "
              + scanner_attribution(security, audit, "deny" if mode == "block" else "allow", "pending_scan", failure.cause))
    print(reason, file=sys.stderr)
    if mode == "block":
        emit_block_denial(reason)
    else:
        emit_json({"systemMessage": reason})
    return 0
'''


_COPILOT_RUNTIME_ADAPTER = r'''
SESSION_ID_KEYS = ("sessionId", "session_id")
DEFAULT_SECRETS_LOG_PATH = Path.home() / ".copilot" / "hooks" / "secrets"
HOOK_EVENT = ""


def resolve_work_dir(payload: dict) -> Path:
    del payload
    return Path.cwd()
'''


_GEMINI_RUNTIME_ADAPTER = r'''
SESSION_ID_KEYS = ("session_id",)
DEFAULT_SECRETS_LOG_PATH = Path.home() / ".gemini" / "hooks" / "secrets"
HOOK_EVENT = ""


def resolve_work_dir(payload: dict) -> Path:
    hook_cwd = str(payload.get("cwd") or "")
    return Path(hook_cwd or os.environ.get("GEMINI_PROJECT_DIR") or Path.cwd())
'''


_CODEX_RUNTIME_ADAPTER = r'''
SESSION_ID_KEYS = ("session_id",)
DEFAULT_SECRETS_LOG_PATH = Path.home() / ".codex" / "hooks" / "secrets"
HOOK_EVENT = ""


def resolve_work_dir(payload: dict) -> Path:
    global HOOK_EVENT
    HOOK_EVENT = payload.get("hook_event_name", "")
    return Path(str(payload.get("cwd") or Path.cwd()))
'''


_RECOVERY_SOURCE = r'''

def _diagnostic_request(payload):
    if not isinstance(payload, dict):
        return False
    if DIAG_PROVIDER == "copilot":
        event, tool_key, args_key = "preToolUse", "toolName", "toolArgs"
        # Native Copilot CLI envelopes omit the event name.
        if payload.get("hook_event_name", event) != event or payload.get(tool_key) != "bash":
            return False
        metadata = {"sessionId": 256, "cwd": 8192}
    else:
        event = "PreToolUse" if DIAG_PROVIDER == "codex" else "BeforeTool"
        tool_key, args_key = "tool_name", "tool_input"
        tools = {"exec_command", "functions.exec_command"} if DIAG_PROVIDER == "codex" else {"run_shell_command"}
        if payload.get("hook_event_name") != event or type(payload.get(tool_key)) is not str or payload[tool_key] not in tools:
            return False
        metadata = {"session_id": 256, "cwd": 8192, "transcript_path": 8192, "tool_use_id": 256}
    if not set(payload) <= {"hook_event_name", tool_key, args_key, "timestamp", *metadata}:
        return False
    if any(type(payload[key]) is not str or len(payload[key]) > limit for key, limit in metadata.items() if key in payload):
        return False
    if "timestamp" in payload:
        stamp = payload["timestamp"]
        if DIAG_PROVIDER == "copilot":
            if type(stamp) is not int or not 0 <= stamp <= 9223372036854775807:
                return False
        elif type(stamp) is not str or len(stamp) > 128:
            return False
    args = payload.get(args_key)
    if not isinstance(args, dict):
        return False
    if DIAG_PROVIDER == "codex":
        if not {"cmd", "login"} <= set(args) or not set(args) <= {"cmd", "login", "max_output_tokens", "yield_time_ms"}:
            return False
        if args["cmd"] != "hooks-diagnostics-v1" or args["login"] is not False:
            return False
        return all(type(args[key]) is int and 0 <= args[key] <= 2147483647 for key in ("max_output_tokens", "yield_time_ms") if key in args)
    return args == {"command": "hooks-diagnostics-v1"}


# BEGIN PROVIDER ADAPTER
def _diagnostic_denial(text):
    reason = "scan-secrets diagnostics (request not executed):" + text
    return block_denial_payload(reason, "PreToolUse")
# END PROVIDER ADAPTER


_SCAN_PAYLOAD = None
_SCAN_INPUT_ERROR = ""
_SCAN_INPUT_LOADED = False
_SCAN_STARTED = None


def _load_scan_payload():
    global _SCAN_PAYLOAD, _SCAN_INPUT_ERROR, _SCAN_INPUT_LOADED
    if _SCAN_INPUT_LOADED:
        return
    _SCAN_INPUT_LOADED = True
    try:
        _SCAN_PAYLOAD = read_json_input()
    except ValueError:
        _SCAN_INPUT_ERROR = "input_invalid"
    except Exception:
        _SCAN_INPUT_ERROR = "internal_error"


if __name__ == "__main__":
    # Recovery routing reads stdin before main. Ordinary scans inherit this
    # same start so transport cannot extend the overall security work budget.
    _SCAN_STARTED = time.monotonic()
    _load_scan_payload()
    if _diagnostic_request(_SCAN_PAYLOAD):
        _report = diagnostics_collect(__file__)
        _report.update(action="diagnostics", security_outcome="not_scanned", enforcement="deny", audit_outcome="not_attempted")
        _payload_cwd = _SCAN_PAYLOAD.get("cwd")
        # Inventory is process cwd only. Never resolve/stat/open the payload path.
        try:
            _location_verified = _payload_cwd is None or _payload_cwd == os.getcwd()
        except OSError:
            _location_verified = False
        _report["repository"]["repository_location"] = "process_cwd" if _location_verified else "unverified"
        sys.stdout.buffer.write(diagnostics_encode(_report, wrap=_diagnostic_denial))
        raise SystemExit(0)
'''


_MAIN_SOURCE = r'''


def findings_denial_reason(scan_log: Path) -> str:
    return (f"scan-secrets blocked: {SCAN_ACTION}; potential secrets detected. "
            + scanner_attribution("findings", "written", "deny", "pending_scan", "findings"))

def resolve_scan_log() -> Path:
    log_dir_str = os.environ.get("SECRETS_LOG_DIR", str(DEFAULT_SECRETS_LOG_PATH))
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
    return scan_log


def main() -> int:
    global INCOMPLETE_LOG, SCAN_ACTION, SCAN_RESULT, HOOK_EVENT
    if isinstance(_SCAN_PAYLOAD, dict):
        HOOK_EVENT = _SCAN_PAYLOAD.get("hook_event_name", "")
    if _SCAN_RUNTIME_ERROR:
        emit_block_denial("scan-secrets blocked: tool scan; scan incomplete; scanner helper unavailable. Use the standalone diagnostics CLI. "
                          + scanner_attribution("incomplete", "not_attempted", "deny", "initialization", "internal_error"))
        return 0
    mode = normalized_mode_from_env()
    scan_started = _SCAN_STARTED if _SCAN_STARTED is not None else time.monotonic()
    scan_log = resolve_scan_log()
    INCOMPLETE_LOG = {"log_path": scan_log, "session_id": "", "timestamp": "", "mode": mode,
                      "scope": "diff", "repo_root_path": Path.cwd()}
    _load_scan_payload()
    if _SCAN_INPUT_ERROR:
        raise ScanSecurityError(_SCAN_INPUT_ERROR, "input")
    payload = _SCAN_PAYLOAD
    if not isinstance(payload, dict):
        raise ScanSecurityError("input_invalid", "input")
    HOOK_EVENT = payload.get("hook_event_name", "")
    if shutil.which("git") is None:
        raise GitCommandError("git_unavailable", "initialization")
    try:
        from helpers.audit import audit_init
    except Exception:
        emit_block_denial("scan-secrets blocked: tool scan; scan incomplete; audit helper unavailable. Use the standalone diagnostics CLI. "
                          + scanner_attribution("incomplete", "not_attempted", "deny", "initialization", "audit_unavailable"))
        return 0
    if not audit_init():
        raise ScanSecurityError("audit_unavailable", "initialization")
    event = payload.get("hook_event_name")
    SCAN_ACTION = ("session-end scan" if event in {"Stop", "SessionEnd", "agentStop", "subagentStop"}
                   or payload.get("reason") == "complete" else "tool scan")
    session_id = next((str(payload[key]) for key in SESSION_ID_KEYS if payload.get(key)), "")
    timestamp = str(payload.get("timestamp") or "")
    scope = os.environ.get("SCAN_SCOPE", "diff")
    if scope not in {"diff", "staged"}:
        scope = "diff"
    work_dir = resolve_work_dir(payload)
    INCOMPLETE_LOG = {"log_path": scan_log, "session_id": session_id, "timestamp": timestamp,
                      "mode": mode, "scope": scope, "repo_root_path": work_dir}
    log_context = {**INCOMPLETE_LOG, "deadline": scan_started + MAX_SCAN_SECONDS}
    if os.environ.get("SKIP_SECRETS_SCAN") == "true":
        append_scan_log(**log_context, status="skipped", env_files=[], findings=[],
                        note="scan disabled by SKIP_SECRETS_SCAN")
        emit_output(0, scan_log, skipped=True)
        return 0
    policy = ScanPolicy(REPORT_BUILD, scope, allowlist=tuple(parse_allowlist(os.environ.get("SECRETS_ALLOWLIST"))))
    result = scan(work_dir, policy,
                  ScanLimits(MAX_FILES, MAX_TOTAL_BYTES, MAX_SCAN_SECONDS, MAX_GIT_OUTPUT_BYTES),
                  started=scan_started)
    SCAN_RESULT = result
    if result.failure is not None:
        raise result.failure
    if result.skipped:
        append_scan_log(**log_context, status="skipped", env_files=[], findings=[], note="not inside git repository")
        emit_output(0, scan_log, skipped=True)
        return 0
    log_context["repo_root_path"] = result.root
    processed = result.counts["processed_findings"]
    append_scan_log(**log_context, status="findings" if processed else "clean", env_files=result.env_files,
                    findings=result.findings, omitted_findings=result.counts["omitted_findings"],
                    findings_truncated=result.counts["omitted_findings"] > 0,
                    note="no modified files to scan" if not result.counts["candidates"] else "")
    if processed and mode == "block":
        emit_block_denial(findings_denial_reason(scan_log))
    else:
        emit_output(processed, scan_log, checked_files=result.counts["candidates"])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        if _SCAN_RUNTIME_ERROR:
            emit_block_denial("scan-secrets blocked: tool scan; scan incomplete; scanner helper unavailable.")
            raise SystemExit(0)
        raise SystemExit(handle_unexpected_exception(exc))
'''


def _adapters(provider: Provider) -> tuple[str, str]:
    if provider.name == "copilot":
        return _COPILOT_RESPONSE_ADAPTER, _COPILOT_RUNTIME_ADAPTER
    if provider.name == "gemini":
        return _GEMINI_RESPONSE_ADAPTER, _GEMINI_RUNTIME_ADAPTER
    if provider.name == "codex":
        return _CODEX_RESPONSE_ADAPTER, _CODEX_RUNTIME_ADAPTER
    raise ValueError(f"Unsupported secret scanner provider: {provider.name}")


def render(provider: Provider, target: GeneratedTarget) -> str:
    """Render one self-contained provider-local secret scanner."""
    if (
        target.family != "scan_secrets"
        or target.provider != provider.name
        or provider.name not in {"copilot", "gemini", "codex"}
    ):
        raise ValueError(f"Unsupported secret scanner target/provider: {target.output_path}")
    response_adapter, runtime_adapter = _adapters(provider)
    return (
        SHEBANG
        + HEADER
        + _PRELUDE_SOURCE.lstrip("\n").replace("__REPORT_BUILD__", build_identity("scan_secrets")).replace(
            "# __DIAGNOSTIC_BOOTSTRAP__",
            ADAPTER_START + response_adapter.lstrip("\n") + ADAPTER_END + collector_source(provider) + _RECOVERY_SOURCE)
        + _POLICY_SOURCE
        + ADAPTER_START
        + runtime_adapter.lstrip("\n")
        + ADAPTER_END
        + _MAIN_SOURCE
    )
