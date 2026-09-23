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
    """Return the Phase 1 targets implemented by the current milestone."""
    return (
        GeneratedTarget("send_event", "copilot", PurePosixPath(".copilot/hooks/scripts/send-event.py")),
        GeneratedTarget("send_event", "gemini", PurePosixPath(".gemini/hooks/scripts/send-event.py")),
        GeneratedTarget("common", "copilot", PurePosixPath(".copilot/hooks/scripts/helpers/common.py")),
        GeneratedTarget("common", "codex", PurePosixPath(".codex/hooks/helpers/common.py")),
        GeneratedTarget("common", "gemini", PurePosixPath(".gemini/hooks/scripts/helpers/common.py")),
        GeneratedTarget("common", "github", PurePosixPath(".github/hooks/scripts/helpers/common.py")),
        GeneratedTarget("audit", "copilot", PurePosixPath(".copilot/hooks/scripts/helpers/audit.py")),
        GeneratedTarget("audit", "codex", PurePosixPath(".codex/hooks/helpers/audit.py")),
        GeneratedTarget("audit", "gemini", PurePosixPath(".gemini/hooks/scripts/helpers/audit.py")),
        GeneratedTarget("audit", "github", PurePosixPath(".github/hooks/scripts/helpers/audit.py")),
        GeneratedTarget("observability", "copilot", PurePosixPath(".copilot/hooks/scripts/helpers/observability.py")),
        GeneratedTarget("observability", "gemini", PurePosixPath(".gemini/hooks/scripts/helpers/observability.py")),
        GeneratedTarget("tool_guard", "copilot", PurePosixPath(".copilot/hooks/scripts/tool-guard.py")),
        GeneratedTarget("tool_guard", "gemini", PurePosixPath(".gemini/hooks/scripts/tool-guard.py")),
        GeneratedTarget("tool_guard", "codex", PurePosixPath(".codex/hooks/tool-guard.py")),
        GeneratedTarget("scan_secrets", "copilot", PurePosixPath(".copilot/hooks/scripts/scan-secrets.py")),
        GeneratedTarget("scan_secrets", "codex", PurePosixPath(".codex/hooks/scan-secrets.py")),
        GeneratedTarget("scan_secrets", "gemini", PurePosixPath(".gemini/hooks/scripts/scan-secrets.py")),
        GeneratedTarget("markdown_health", "copilot", PurePosixPath(".copilot/hooks/scripts/markdown-health.py")),
        GeneratedTarget("markdown_health", "gemini", PurePosixPath(".gemini/hooks/scripts/markdown-health.py")),
        GeneratedTarget("markdown_health", "codex", PurePosixPath(".codex/hooks/markdown-health.py")),
        GeneratedTarget("auto_ingest", "github", PurePosixPath(".github/hooks/scripts/helpers/auto_ingest.py")),
        GeneratedTarget("auto_ingest", "gemini", PurePosixPath(".gemini/hooks/scripts/helpers/source_ingest.py")),
        GeneratedTarget("auto_ingest", "github", PurePosixPath(".github/hooks/scripts/auto-ingest-source.py")),
        GeneratedTarget("auto_ingest", "gemini", PurePosixPath(".gemini/hooks/scripts/auto-ingest.py")),
        GeneratedTarget("auto_ingest", "github", PurePosixPath(".github/hooks/scripts/inject-auto-ingest-context.py")),
        GeneratedTarget("auto_ingest", "gemini", PurePosixPath(".gemini/hooks/scripts/inject-auto-ingest-context.py")),
        GeneratedTarget("rtk", "copilot", PurePosixPath(".copilot/hooks/scripts/rtk-hook-copilot.py")),
        GeneratedTarget("rtk", "gemini", PurePosixPath(".gemini/hooks/scripts/rtk-hook-gemini.py")),
        GeneratedTarget("rtk", "copilot", PurePosixPath(".copilot/hooks/scripts/rtk-explicit-copilot.py")),
        GeneratedTarget("rtk", "gemini", PurePosixPath(".gemini/hooks/scripts/rtk-explicit-gemini.py")),
        GeneratedTarget("rtk", "codex", PurePosixPath(".codex/hooks/rtk-explicit-codex.py")),
        GeneratedTarget("rtk", "copilot", PurePosixPath(".copilot/hooks/scripts/rtk-agent-launcher.py")),
        GeneratedTarget("rtk", "gemini", PurePosixPath(".gemini/hooks/scripts/rtk-agent-launcher.py")),
        GeneratedTarget("rtk", "codex", PurePosixPath(".codex/hooks/rtk-agent-launcher.py")),
    )
