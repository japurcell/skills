SKILLS_ENVIRONMENT = "GEMINI_SKILLS_DIR"

def scan_sources(source_root: Path, summary_root: Path) -> list[SourceRecord]:
    return _scan_sources(source_root, summary_root)


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

