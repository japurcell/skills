"""Immutable provider metadata used by hook renderers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath


@dataclass(frozen=True)
class Provider:
    """One runtime surface that receives a self-contained generated hook."""

    name: str
    hook_root: PurePosixPath
    runtime_home_name: str
    observability_environment_prefix: str
    auto_ingest_helper_name: str


PROVIDERS = {
    "copilot": Provider("copilot", PurePosixPath(".copilot/hooks"), ".copilot", "COPILOT", "auto_ingest"),
    "gemini": Provider("gemini", PurePosixPath(".gemini/hooks"), ".gemini", "GEMINI", "source_ingest"),
    "github": Provider("github", PurePosixPath(".github/hooks"), ".copilot", "COPILOT", "auto_ingest"),
}
