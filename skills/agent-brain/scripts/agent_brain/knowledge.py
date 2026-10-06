"""Read complete, explicitly mapped artifacts for informational recall."""

from __future__ import annotations

from pathlib import Path

from .config import ConfigurationError
from .records import AgentBrainConfig, RecalledArtifact, RecallResult


NOTICE = "Informational output only; this does not confirm agent delivery or application."


def recall_whole_artifacts(config: AgentBrainConfig, *, repository_root: Path) -> RecallResult:
    repository = repository_root.resolve(strict=True)
    units_by_id = {unit.id: unit for unit in config.mapped_units}
    artifacts: list[RecalledArtifact] = []
    for startup_read in config.startup:
        unit = units_by_id[startup_read.id]
        artifact_path = repository / Path(*unit.path.split("/"))
        try:
            resolved = artifact_path.resolve(strict=True)
        except FileNotFoundError as exc:
            raise ConfigurationError(f"mapped artifact not found: {unit.path}") from exc
        except OSError as exc:
            raise ConfigurationError(f"cannot read mapped artifact {unit.path}: {exc}") from exc
        if not resolved.is_relative_to(repository):
            raise ConfigurationError(f"mapped artifact escapes repository: {unit.path}")
        matching_roots: list[Path] = []
        for root in config.knowledge_roots:
            if root.path != "." and not unit.path.startswith(f"{root.path}/"):
                continue
            try:
                resolved_root = (repository / Path(*root.path.split("/"))).resolve(strict=True)
            except OSError as exc:
                raise ConfigurationError(f"declared knowledge root unavailable: {root.path}") from exc
            if not resolved_root.is_relative_to(repository):
                raise ConfigurationError(f"declared knowledge root escapes repository: {root.path}")
            matching_roots.append(resolved_root)
        if not matching_roots:
            raise ConfigurationError(f"mapped artifact is outside declared knowledge roots: {unit.path}")
        if not any(resolved.is_relative_to(root) for root in matching_roots):
            raise ConfigurationError(
                f"mapped artifact resolves outside declared knowledge roots: {unit.path}"
            )
        try:
            content = resolved.read_bytes().decode("utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise ConfigurationError(f"cannot read mapped artifact {unit.path}: {exc}") from exc
        artifacts.append(RecalledArtifact(unit.id, unit.path, startup_read.loading_mode, content))
    return RecallResult(1, "ok", "recall", True, NOTICE, tuple(artifacts))
