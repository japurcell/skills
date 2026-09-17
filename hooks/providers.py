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


PROVIDERS = {
    "copilot": Provider("copilot", PurePosixPath(".copilot/hooks"), ".copilot"),
    "gemini": Provider("gemini", PurePosixPath(".gemini/hooks"), ".gemini"),
    "github": Provider("github", PurePosixPath(".github/hooks"), ".copilot"),
}
