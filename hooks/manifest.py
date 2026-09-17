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
        GeneratedTarget("common", "gemini", PurePosixPath(".gemini/hooks/scripts/helpers/common.py")),
        GeneratedTarget("common", "github", PurePosixPath(".github/hooks/scripts/helpers/common.py")),
        GeneratedTarget("audit", "copilot", PurePosixPath(".copilot/hooks/scripts/helpers/audit.py")),
        GeneratedTarget("audit", "gemini", PurePosixPath(".gemini/hooks/scripts/helpers/audit.py")),
        GeneratedTarget("audit", "github", PurePosixPath(".github/hooks/scripts/helpers/audit.py")),
        GeneratedTarget("observability", "copilot", PurePosixPath(".copilot/hooks/scripts/helpers/observability.py")),
        GeneratedTarget("observability", "gemini", PurePosixPath(".gemini/hooks/scripts/helpers/observability.py")),
        GeneratedTarget("tool_guard", "copilot", PurePosixPath(".copilot/hooks/scripts/tool-guard.py")),
        GeneratedTarget("tool_guard", "gemini", PurePosixPath(".gemini/hooks/scripts/tool-guard.py")),
    )
