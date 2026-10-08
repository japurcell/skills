"""Render provider-local auto-ingest engines and hook entrypoints.

The canonical family owns the complete source fragments.  It selects the
provider adapter at generation time; generated programs never import another
provider's runtime tree.
"""

from __future__ import annotations

from pathlib import Path

from hooks.manifest import GeneratedTarget
from hooks.providers import Provider


SHEBANG = "#!/usr/bin/env python3\n"
HEADER = "# Generated from hooks/families/auto_ingest.py by scripts/generate-hooks.py. Do not edit.\n"
_FAMILY_ROOT = Path(__file__).resolve().parent


def _source(name: str) -> str:
    return (_FAMILY_ROOT / name).read_text(encoding="utf-8")


def _render_engine(provider: Provider) -> str:
    """Compose the neutral engine with its explicit root/environment adapter."""
    engine = _source("auto_ingest_engine.py")
    marker = "# __ROOT_ADAPTER__\n"
    if engine.count(marker) != 1:
        raise ValueError("Auto-ingest engine must declare exactly one root adapter slot")
    adapter = _source(f"auto_ingest_{provider.name}_roots.py")
    return engine.replace(marker, adapter)


def render(provider: Provider, target: GeneratedTarget) -> str:
    """Return a complete provider-local auto-ingest executable."""
    path = target.output_path.as_posix()
    sources = {
        ".github/hooks/scripts/helpers/auto_ingest.py": "auto_ingest_engine.py",
        ".gemini/hooks/scripts/helpers/source_ingest.py": "auto_ingest_engine.py",
        ".github/hooks/scripts/auto-ingest-source.py": "auto_ingest_github_startup.py",
        ".gemini/hooks/scripts/auto-ingest.py": "auto_ingest_gemini_startup.py",
        ".github/hooks/scripts/inject-auto-ingest-context.py": "auto_ingest_github_inject.py",
        ".gemini/hooks/scripts/inject-auto-ingest-context.py": "auto_ingest_gemini_inject.py",
    }
    try:
        body = _render_engine(provider) if sources[path] == "auto_ingest_engine.py" else _source(sources[path])
    except KeyError as error:
        raise ValueError(f"Unsupported auto-ingest target: {path}") from error
    return SHEBANG + HEADER + body.removeprefix(SHEBANG)
