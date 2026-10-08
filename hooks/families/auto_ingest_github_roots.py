SKILLS_ENVIRONMENT = "COPILOT_SKILLS_DIR"


def scan_sources(sources_dir: Path, summary_dir: Path) -> list[SourceRecord]:
    return _scan_sources(sources_dir, summary_dir)


def source_root(repo_root: Path) -> Path:
    override = os.environ.get("COPILOT_AUTO_INGEST_SOURCE_DIR")
    if override:
        return Path(override)
    return repo_root / ".agents" / "sources"


def summary_root(repo_root: Path) -> Path:
    override = os.environ.get("COPILOT_AUTO_INGEST_SUMMARY_DIR")
    if override:
        return Path(override)
    return repo_root / ".agents" / "memory" / "sources"


def manifest_path(summary_dir: Path) -> Path:
    override = os.environ.get("COPILOT_AUTO_INGEST_MANIFEST_PATH")
    if override:
        return Path(override)
    return summary_dir / MANIFEST_FILE_NAME

