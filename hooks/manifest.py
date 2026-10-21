"""Explicit generated-hook ownership manifest."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath


@dataclass(frozen=True)
class GeneratedTarget:
    """A checked-in provider-local file rendered from one canonical family."""

    family: str
    provider: str
    output_path: PurePosixPath
    mode: int = 0o755


def targets() -> tuple[GeneratedTarget, ...]:
    """Return the explicit provider-local generated ownership inventory."""
    return (
        GeneratedTarget("send_event", "copilot", PurePosixPath(".copilot/hooks/scripts/send-event.py")),
        GeneratedTarget("send_event", "gemini", PurePosixPath(".gemini/hooks/scripts/send-event.py")),
        GeneratedTarget("common", "copilot", PurePosixPath(".copilot/hooks/scripts/helpers/common.py")),
        GeneratedTarget("common", "codex", PurePosixPath(".codex/hooks/helpers/common.py")),
        GeneratedTarget("common", "gemini", PurePosixPath(".gemini/hooks/scripts/helpers/common.py")),
        GeneratedTarget("audit", "copilot", PurePosixPath(".copilot/hooks/scripts/helpers/audit.py")),
        GeneratedTarget("audit", "codex", PurePosixPath(".codex/hooks/helpers/audit.py")),
        GeneratedTarget("audit", "gemini", PurePosixPath(".gemini/hooks/scripts/helpers/audit.py")),
        GeneratedTarget("observability", "copilot", PurePosixPath(".copilot/hooks/scripts/helpers/observability.py")),
        GeneratedTarget("observability", "gemini", PurePosixPath(".gemini/hooks/scripts/helpers/observability.py")),
        GeneratedTarget("tool_guard", "copilot", PurePosixPath(".copilot/hooks/scripts/tool-guard.py")),
        GeneratedTarget("tool_guard", "gemini", PurePosixPath(".gemini/hooks/scripts/tool-guard.py")),
        GeneratedTarget("tool_guard", "codex", PurePosixPath(".codex/hooks/tool-guard.py")),
        GeneratedTarget("tool_guard", "copilot", PurePosixPath(".copilot/hooks/scripts/helpers/tool_guard_policy.py")),
        GeneratedTarget("tool_guard", "gemini", PurePosixPath(".gemini/hooks/scripts/helpers/tool_guard_policy.py")),
        GeneratedTarget("tool_guard", "codex", PurePosixPath(".codex/hooks/helpers/tool_guard_policy.py")),
        GeneratedTarget("diagnostics", "copilot", PurePosixPath(".copilot/hooks/scripts/hooks-diagnostics.py")),
        GeneratedTarget("diagnostics", "codex", PurePosixPath(".codex/hooks/hooks-diagnostics.py")),
        GeneratedTarget("diagnostics", "gemini", PurePosixPath(".gemini/hooks/scripts/hooks-diagnostics.py")),
        GeneratedTarget("scan_runtime", "copilot", PurePosixPath(".copilot/hooks/scripts/helpers/scan_types.py")),
        GeneratedTarget("scan_runtime", "copilot", PurePosixPath(".copilot/hooks/scripts/helpers/scan_reporting.py")),
        GeneratedTarget("scan_runtime", "copilot", PurePosixPath(".copilot/hooks/scripts/helpers/scan_allowlist.py")),
        GeneratedTarget("scan_runtime", "copilot", PurePosixPath(".copilot/hooks/scripts/helpers/scan_stream.py")),
        GeneratedTarget("scan_runtime", "copilot", PurePosixPath(".copilot/hooks/scripts/helpers/scan_git.py")),
        GeneratedTarget("scan_runtime", "copilot", PurePosixPath(".copilot/hooks/scripts/helpers/scan_audit.py")),
        GeneratedTarget("scan_runtime", "copilot", PurePosixPath(".copilot/hooks/scripts/helpers/scan_native_file.py")),
        GeneratedTarget("scan_runtime", "copilot", PurePosixPath(".copilot/hooks/scripts/helpers/scan_native_process.py")),
        GeneratedTarget("scan_runtime", "copilot", PurePosixPath(".copilot/hooks/scripts/helpers/scan_engine.py")),
        GeneratedTarget("scan_runtime", "codex", PurePosixPath(".codex/hooks/helpers/scan_types.py")),
        GeneratedTarget("scan_runtime", "codex", PurePosixPath(".codex/hooks/helpers/scan_reporting.py")),
        GeneratedTarget("scan_runtime", "codex", PurePosixPath(".codex/hooks/helpers/scan_allowlist.py")),
        GeneratedTarget("scan_runtime", "codex", PurePosixPath(".codex/hooks/helpers/scan_stream.py")),
        GeneratedTarget("scan_runtime", "codex", PurePosixPath(".codex/hooks/helpers/scan_git.py")),
        GeneratedTarget("scan_runtime", "codex", PurePosixPath(".codex/hooks/helpers/scan_audit.py")),
        GeneratedTarget("scan_runtime", "codex", PurePosixPath(".codex/hooks/helpers/scan_native_file.py")),
        GeneratedTarget("scan_runtime", "codex", PurePosixPath(".codex/hooks/helpers/scan_native_process.py")),
        GeneratedTarget("scan_runtime", "codex", PurePosixPath(".codex/hooks/helpers/scan_engine.py")),
        GeneratedTarget("scan_runtime", "gemini", PurePosixPath(".gemini/hooks/scripts/helpers/scan_types.py")),
        GeneratedTarget("scan_runtime", "gemini", PurePosixPath(".gemini/hooks/scripts/helpers/scan_reporting.py")),
        GeneratedTarget("scan_runtime", "gemini", PurePosixPath(".gemini/hooks/scripts/helpers/scan_allowlist.py")),
        GeneratedTarget("scan_runtime", "gemini", PurePosixPath(".gemini/hooks/scripts/helpers/scan_stream.py")),
        GeneratedTarget("scan_runtime", "gemini", PurePosixPath(".gemini/hooks/scripts/helpers/scan_git.py")),
        GeneratedTarget("scan_runtime", "gemini", PurePosixPath(".gemini/hooks/scripts/helpers/scan_audit.py")),
        GeneratedTarget("scan_runtime", "gemini", PurePosixPath(".gemini/hooks/scripts/helpers/scan_native_file.py")),
        GeneratedTarget("scan_runtime", "gemini", PurePosixPath(".gemini/hooks/scripts/helpers/scan_native_process.py")),
        GeneratedTarget("scan_runtime", "gemini", PurePosixPath(".gemini/hooks/scripts/helpers/scan_engine.py")),
        GeneratedTarget("scan_status", "copilot", PurePosixPath(".copilot/hooks/scripts/scan-status.py")),
        GeneratedTarget("scan_status", "codex", PurePosixPath(".codex/hooks/scan-status.py")),
        GeneratedTarget("scan_status", "gemini", PurePosixPath(".gemini/hooks/scripts/scan-status.py")),
        GeneratedTarget("scan_secrets", "copilot", PurePosixPath(".copilot/hooks/scripts/scan-secrets.py")),
        GeneratedTarget("scan_secrets", "codex", PurePosixPath(".codex/hooks/scan-secrets.py")),
        GeneratedTarget("scan_secrets", "gemini", PurePosixPath(".gemini/hooks/scripts/scan-secrets.py")),
        GeneratedTarget("rtk", "copilot", PurePosixPath(".copilot/hooks/scripts/rtk-hook-copilot.py")),
        GeneratedTarget("rtk", "gemini", PurePosixPath(".gemini/hooks/scripts/rtk-hook-gemini.py")),
        GeneratedTarget("brain", "github", PurePosixPath(".github/hooks/scripts/auto-index-brain.py")),
        GeneratedTarget("brain", "github", PurePosixPath(".github/hooks/scripts/inject-brain.py")),
        GeneratedTarget("brain", "gemini", PurePosixPath(".gemini/hooks/scripts/auto-index-brain.py")),
        GeneratedTarget("brain", "gemini", PurePosixPath(".gemini/hooks/scripts/inject-brain.py")),
        GeneratedTarget("brain", "codex", PurePosixPath(".codex/hooks/auto-index-brain.py")),
        GeneratedTarget("brain", "codex", PurePosixPath(".codex/hooks/inject-brain.py")),
    )
