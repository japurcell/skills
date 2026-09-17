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

_GEMINI_ROOT_ADAPTER = '''
def source_root_for_payload(payload: dict[str, object]) -> Path:
    override = os.environ.get("AGENTS_SOURCE_SCAN_DIR")
    if override:
        return Path(override)
    cwd = str(payload.get("cwd") or "")
    if cwd:
        from helpers.common import convert_windows_path_to_posix
        cwd = convert_windows_path_to_posix(cwd)
    return Path(cwd) / ".agents/sources" if cwd else Path.cwd() / ".agents/sources"


def summary_root_for_payload(payload: dict[str, object]) -> Path:
    override = os.environ.get("AGENTS_SOURCE_SUMMARY_DIR")
    if override:
        return Path(override)
    cwd = str(payload.get("cwd") or "")
    if cwd:
        from helpers.common import convert_windows_path_to_posix
        cwd = convert_windows_path_to_posix(cwd)
    return Path(cwd) / ".agents/memory/sources" if cwd else Path.cwd() / ".agents/memory/sources"


def manifest_path_for_summary_root(summary_dir: Path) -> Path:
    return summary_dir / MANIFEST_FILE_NAME


def manifest_path_for_payload(payload: dict[str, object], summary_root: Path) -> Path:
    override = os.environ.get("AGENTS_SOURCE_MANIFEST_PATH")
    if override:
        return Path(override)
    return manifest_path_for_summary_root(summary_root)


def repo_root_for_payload(payload: dict[str, object]) -> Path:
    cwd = str(payload.get("cwd") or "")
    if cwd:
        from helpers.common import convert_windows_path_to_posix
        cwd = convert_windows_path_to_posix(cwd)
    return Path(cwd) if cwd else Path.cwd()


'''


def _source(name: str) -> str:
    return (_FAMILY_ROOT / name).read_text(encoding="utf-8")


def _render_gemini_engine() -> str:
    """Adapt repository-root resolution to Gemini's payload-derived roots."""
    engine = _source("auto_ingest_engine.py")
    start = engine.index("def source_root(")
    end = engine.index("def ingest_skill_path(")
    engine = engine[:start] + _GEMINI_ROOT_ADAPTER + engine[end:]
    engine = engine.replace(
        'os.environ.get("AGENTS_SKILLS_DIR") or os.environ.get("COPILOT_SKILLS_DIR")',
        'os.environ.get("AGENTS_SKILLS_DIR") or os.environ.get("GEMINI_SKILLS_DIR")',
    )
    engine = engine.replace("sources_dir: Path, summary_dir: Path", "source_root: Path, summary_root: Path")
    engine = engine.replace("sources_dir.exists()", "source_root.exists()")
    engine = engine.replace("sources_dir.rglob", "source_root.rglob")
    engine = engine.replace("relative_to(sources_dir)", "relative_to(source_root)")
    engine = engine.replace(
        "summary_path_for_source(summary_dir, source_relpath)",
        "summary_path_for_source(summary_root, source_relpath)",
        1,
    )
    return engine


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
        body = _render_gemini_engine() if provider.name == "gemini" and path.endswith("helpers/source_ingest.py") else _source(sources[path])
    except KeyError as error:
        raise ValueError(f"Unsupported auto-ingest target: {path}") from error
    return SHEBANG + HEADER + body.removeprefix(SHEBANG)
