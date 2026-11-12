"""Explicit generated-hook ownership manifest."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath


@dataclass(frozen=True)
class GeneratedTarget:
    """A checked-in hook file rendered from one canonical family."""

    family: str
    provider: str
    output_path: PurePosixPath
    mode: int = 0o755


def targets() -> tuple[GeneratedTarget, ...]:
    """Return the explicit provider and bundled-hook ownership inventory."""
    return (
        GeneratedTarget("common", "copilot", PurePosixPath(".copilot/hooks/scripts/helpers/common.py")),
        GeneratedTarget("common", "gemini", PurePosixPath(".gemini/hooks/scripts/helpers/common.py")),
        GeneratedTarget("audit", "copilot", PurePosixPath(".copilot/hooks/scripts/helpers/audit.py")),
        GeneratedTarget("audit", "gemini", PurePosixPath(".gemini/hooks/scripts/helpers/audit.py")),
        GeneratedTarget("observability", "copilot", PurePosixPath(".copilot/hooks/scripts/helpers/observability.py")),
        GeneratedTarget("observability", "gemini", PurePosixPath(".gemini/hooks/scripts/helpers/observability.py")),
        GeneratedTarget("rtk", "copilot", PurePosixPath(".copilot/hooks/scripts/rtk-hook-copilot.py")),
        GeneratedTarget("rtk", "gemini", PurePosixPath(".gemini/hooks/scripts/rtk-hook-gemini.py")),
        GeneratedTarget("brain", "github", PurePosixPath(".github/hooks/scripts/auto-index-brain.py")),
        GeneratedTarget("brain", "github", PurePosixPath(".github/hooks/scripts/inject-brain.py")),
        GeneratedTarget("brain", "gemini", PurePosixPath(".gemini/hooks/scripts/auto-index-brain.py")),
        GeneratedTarget("brain", "gemini", PurePosixPath(".gemini/hooks/scripts/inject-brain.py")),
        GeneratedTarget("brain", "codex", PurePosixPath(".codex/hooks/auto-index-brain.py")),
        GeneratedTarget("brain", "codex", PurePosixPath(".codex/hooks/inject-brain.py")),
        GeneratedTarget("brain", "github", PurePosixPath("skills/default/brain-install/assets/skills/brain/scripts/auto-index-brain.py")),
        GeneratedTarget("brain", "github", PurePosixPath("skills/default/brain-install/assets/hooks/inject-brain.py")),
    )
