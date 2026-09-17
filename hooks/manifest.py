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
    )
