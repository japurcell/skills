"""Render provider-local audit helpers from explicit provider adapters."""

from __future__ import annotations

from hooks.manifest import GeneratedTarget
from hooks.providers import Provider


SHEBANG = "#!/usr/bin/env python3\n"


PREAMBLE = """from __future__ import annotations

try:
    import fcntl
except ImportError:
    fcntl = None
import os
import time
from datetime import datetime
from pathlib import Path

from .common import sanitize_log_field


def _lock_timeout_seconds(value: str | None) -> float:
    try:
        return max(0.1, float(value or "1000") / 1000.0)
    except ValueError:
        return 1.0


def _int_env(value: str | None, default: int) -> int:
    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default


def _ensure_parent(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def _acquire_lock(lock_path: str, timeout_seconds: float) -> int | None:
    _ensure_parent(lock_path)
    lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    if fcntl is None:
        return lock_fd
    deadline = time.monotonic() + timeout_seconds

    while True:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return lock_fd
        except BlockingIOError:
            if time.monotonic() >= deadline:
                os.close(lock_fd)
                return None
            time.sleep(0.05)
        except OSError:
            os.close(lock_fd)
            return None


def _append_line(path: str, sender: str, message: str) -> None:
    _ensure_parent(path)
    flags = os.O_APPEND | os.O_CREAT | os.O_WRONLY
    fd = os.open(path, flags, 0o600)
    try:
        os.fchmod(fd, 0o600)
    except (AttributeError, OSError):
        pass

    try:
        handle = os.fdopen(fd, "a", encoding="utf-8")
    except Exception:
        os.close(fd)
        raise

    with handle:
        handle.write(f"[{sender}] {message}\\n")
        handle.flush()
        os.fsync(handle.fileno())
"""

ROTATE = """def _rotate_audit_log(log_path: str, max_bytes: int, backups: int) -> None:
    try:
        if not Path(log_path).exists() or Path(log_path).stat().st_size < max_bytes:
            return
    except OSError:
        return

    if backups <= 0:
        try:
            Path(log_path).unlink()
        except OSError:
            pass
        return

    for index in range(backups, 0, -1):
        current = Path(f"{log_path}.{index}")
        next_path = Path(f"{log_path}.{index + 1}")
        if current.exists():
            try:
                if index == backups:
                    current.unlink()
                else:
                    current.replace(next_path)
            except OSError:
                pass

    try:
        Path(log_path).replace(Path(f"{log_path}.1"))
    except OSError:
        return
"""

COPILOT_ADAPTER = """def audit_init() -> bool:
    log_path = os.environ.get("AUDIT_LOG", str(Path.home() / ".copilot" / "hooks" / "audit.log"))
    mode = os.environ.get("AUDIT_PASSIVE_LOG_MODE", "default")
    try:
        _ensure_parent(log_path)
        if mode != "default":
            shadow_path = os.environ.get("AUDIT_PASSIVE_LOG_SHADOW_LOG", f"{log_path}.shadow")
            _ensure_parent(shadow_path)
        return True
    except OSError:
        return False


def _write_log(sender: str, message: str, passive_shadow_path: str | None = None) -> bool:
    log_path = os.environ.get("AUDIT_LOG", str(Path.home() / ".copilot" / "hooks" / "audit.log"))
    lock_path = os.environ.get("AUDIT_LOCK", f"{log_path}.lock")
    timeout_seconds = _lock_timeout_seconds(os.environ.get("AUDIT_LOCK_WAIT_MS"))
    max_bytes = _int_env(os.environ.get("AUDIT_LOG_MAX_BYTES"), 1048576)
    backups = _int_env(os.environ.get("AUDIT_LOG_MAX_BACKUPS"), 3)

    try:
        lock_fd = _acquire_lock(lock_path, timeout_seconds)
    except OSError:
        return False
    if lock_fd is None:
        return False

    safe_sender = sanitize_log_field(sender)
    safe_message = sanitize_log_field(message)

    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        _rotate_audit_log(log_path, max_bytes, backups)
        _append_line(log_path, safe_sender, f"[{timestamp}] {safe_message}")
        if passive_shadow_path:
            _rotate_audit_log(passive_shadow_path, max_bytes, backups)
            _append_line(passive_shadow_path, safe_sender, f"[{timestamp}] {safe_message}")
    except OSError:
        return False
    finally:
        try:
            if fcntl is not None:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
        finally:
            os.close(lock_fd)

    return True


def audit_log_event(sender: str, message: str) -> bool:
    return _write_log(sender, message)


def audit_log_passive_event(sender: str, message: str) -> bool:
    log_path = os.environ.get("AUDIT_LOG", str(Path.home() / ".copilot" / "hooks" / "audit.log"))
    mode = os.environ.get("AUDIT_PASSIVE_LOG_MODE", "default")
    shadow_path = None
    if mode != "default":
        shadow_path = os.environ.get("AUDIT_PASSIVE_LOG_SHADOW_LOG", f"{log_path}.shadow")
    return _write_log(sender, message, shadow_path)
"""

GEMINI_ADAPTER = """def audit_init() -> bool:
    log_path = os.environ.get("AUDIT_LOG", str(Path.home() / ".gemini" / "hooks" / "audit.log"))
    mode = os.environ.get("GEMINI_PASSIVE_LOG_MODE", "default")
    try:
        _ensure_parent(log_path)
        if mode == "shadow":
            shadow_path = os.environ.get("GEMINI_PASSIVE_SHADOW_LOG", f"{log_path}.shadow")
            _ensure_parent(shadow_path)
        return True
    except OSError:
        return False


def _write_log(sender: str, message: str, passive_shadow_path: str | None = None) -> bool:
    log_path = os.environ.get("AUDIT_LOG", str(Path.home() / ".gemini" / "hooks" / "audit.log"))
    lock_path = os.environ.get("AUDIT_LOCK", f"{log_path}.lock")
    timeout_seconds = _lock_timeout_seconds(os.environ.get("AUDIT_LOCK_WAIT_MS"))
    max_bytes = _int_env(os.environ.get("AUDIT_LOG_MAX_BYTES"), 1048576)
    backups = _int_env(os.environ.get("AUDIT_LOG_MAX_BACKUPS"), 3)

    try:
        lock_fd = _acquire_lock(lock_path, timeout_seconds)
    except OSError:
        return False
    if lock_fd is None:
        return False

    safe_sender = sanitize_log_field(sender)
    safe_message = sanitize_log_field(message)

    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        _rotate_audit_log(log_path, max_bytes, backups)
        _append_line(log_path, safe_sender, f"[{timestamp}] {safe_message}")
        if passive_shadow_path:
            _rotate_audit_log(passive_shadow_path, max_bytes, backups)
            _append_line(passive_shadow_path, safe_sender, f"[{timestamp}] {safe_message}")
    except OSError:
        return False
    finally:
        try:
            if fcntl is not None:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
        finally:
            os.close(lock_fd)

    return True


def audit_log_event(sender: str, message: str) -> bool:
    return _write_log(sender, message)


def audit_log_passive_event(sender: str, message: str) -> bool:
    log_path = os.environ.get("AUDIT_LOG", str(Path.home() / ".gemini" / "hooks" / "audit.log"))
    mode = os.environ.get("GEMINI_PASSIVE_LOG_MODE", "default")
    shadow_path = None
    if mode == "shadow":
        shadow_path = os.environ.get("GEMINI_PASSIVE_SHADOW_LOG", f"{log_path}.shadow")
    return _write_log(sender, message, shadow_path)
"""

GITHUB_ADAPTER = """def _write_log(
    sender: str,
    message: str,
    passive_shadow_path: str | None = None,
    passive_shadow_mode: str | None = None,
) -> bool:
    log_path = os.environ.get("AUDIT_LOG", str(Path.home() / ".copilot" / "hooks" / "audit.log"))
    lock_path = os.environ.get("AUDIT_LOCK", f"{log_path}.lock")
    timeout_seconds = _lock_timeout_seconds(os.environ.get("AUDIT_LOCK_WAIT_MS"))
    max_bytes = _int_env(os.environ.get("AUDIT_LOG_MAX_BYTES"), 1048576)
    backups = _int_env(os.environ.get("AUDIT_LOG_MAX_BACKUPS"), 3)

    try:
        lock_fd = _acquire_lock(lock_path, timeout_seconds)
    except OSError:
        return False
    if lock_fd is None:
        return False

    safe_sender = sanitize_log_field(sender)
    safe_message = sanitize_log_field(message)

    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        _rotate_audit_log(log_path, max_bytes, backups)
        _append_line(log_path, safe_sender, f"[{timestamp}] {safe_message}")
        if passive_shadow_path:
            shadow_mode = passive_shadow_mode or os.environ.get("AUDIT_PASSIVE_LOG_MODE", "default")
            _rotate_audit_log(passive_shadow_path, max_bytes, backups)
            _append_line(passive_shadow_path, safe_sender, f"[mode={shadow_mode}] [{timestamp}] {safe_message}")
    except OSError:
        return False
    finally:
        try:
            if fcntl is not None:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
        finally:
            os.close(lock_fd)

    return True


def audit_log_event(sender: str, message: str) -> bool:
    log_path = os.environ.get("AUDIT_LOG", str(Path.home() / ".copilot" / "hooks" / "audit.log"))
    mode = os.environ.get("AUDIT_PASSIVE_LOG_MODE", "default")
    shadow_path = None
    if mode != "default":
        shadow_path = os.environ.get("AUDIT_PASSIVE_LOG_SHADOW_LOG", f"{log_path}.shadow")
    return _write_log(sender, message, shadow_path, mode)
"""


def render(provider: Provider, target: GeneratedTarget) -> str:
    """Render the complete audit helper for one supported runtime."""
    if target.provider != provider.name:
        raise ValueError(f"Audit target/provider mismatch: {target.output_path}")
    if provider.name in {"copilot", "codex"}:
        adapter = COPILOT_ADAPTER
        if provider.name == "codex":
            adapter = adapter.replace(' / ".copilot" / ', ' / ".codex" / ')
        body = "\n\n".join((PREAMBLE, adapter, ROTATE))
    elif provider.name == "gemini":
        body = "\n\n".join((PREAMBLE, GEMINI_ADAPTER, ROTATE))
    elif provider.name == "github":
        body = "\n\n".join((PREAMBLE, ROTATE, GITHUB_ADAPTER))
    else:
        raise ValueError(f"Unsupported audit provider: {provider.name}")
    return SHEBANG + "# Generated from hooks/families/audit.py by scripts/generate-hooks.py. Do not edit.\n" + body
