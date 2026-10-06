"""Read indexed guidance from declared repository roots without modifying it."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections import Counter
from pathlib import Path

from .config import ConfigurationError
from .metadata import MetadataIssue, extract_section_content, parse_document_metadata
from .records import AgentBrainConfig, GuidanceUnit, RequiredReference


@dataclass(frozen=True, slots=True)
class KnowledgeBase:
    units: tuple[GuidanceUnit, ...]
    issues: tuple[MetadataIssue, ...]
    documents: dict[str, str]
    contained_ids: dict[str, tuple[str, ...]]
    unavailable: dict[str, tuple[GuidanceUnit, ...]] = field(default_factory=dict)


def validate_guidance_references(knowledge: KnowledgeBase) -> tuple[MetadataIssue, ...]:
    """Validate identity and reference closure across configured guidance roots."""
    issues: list[MetadataIssue] = []
    counts = Counter(unit.id for unit in knowledge.units)
    for unit_id, count in counts.items():
        if count > 1:
            duplicate = next(unit for unit in knowledge.units if unit.id == unit_id)
            issues.append(MetadataIssue("ABM002", duplicate.path, 1, 1,
                                        f"duplicate guidance unit id {unit_id}"))
    by_id = {unit.id: unit for unit in knowledge.units if counts[unit.id] == 1}
    for unit in knowledge.units:
        for reference in unit.requires:
            target = by_id.get(reference.id)
            if target is None:
                issues.append(MetadataIssue("ABM003", unit.path, 1, 1,
                                            f"required reference {reference.id} is unresolved"))
            elif unit.status == "established" and target.status == "candidate":
                issues.append(MetadataIssue("ABM003", unit.path, 1, 1,
                                            f"candidate {reference.id} cannot satisfy established guidance"))
    return tuple(issues)


def load_knowledge(config: AgentBrainConfig, *, repository_root: Path, ignore_publication: bool = False, state_store=None) -> KnowledgeBase:
    repository = repository_root.resolve(strict=True)
    root_paths: list[tuple[str, Path]] = []
    issues: list[MetadataIssue] = []
    for root in config.knowledge_roots:
        declared = repository if root.path == "." else repository / Path(*root.path.split("/"))
        try:
            resolved = declared.resolve(strict=True)
        except OSError as exc:
            issues.append(MetadataIssue("ABM004", root.path, 1, 1, f"knowledge root unavailable: {exc}"))
            continue
        if not resolved.is_relative_to(repository) or not resolved.is_dir():
            issues.append(MetadataIssue("ABM004", root.path, 1, 1, "knowledge root is not a repository directory"))
            continue
        root_paths.append((root.path, resolved))

    documents: dict[str, str] = {}
    blocked: set[str] = set()
    unavailable: dict[str, tuple[GuidanceUnit, ...]] = {}
    if not ignore_publication:
        from .history import pending
        from .state import LifecycleError
        try:
            publication = pending(repository, config, state_store)
            blocked = set(publication["paths"]) if publication else set()
            if publication:
                from .history import read
                journal = read(repository, publication["history_path"])
                current = load_knowledge(config, repository_root=repository, ignore_publication=True)
                for item in journal["changes"]:
                    units = [unit for unit in current.units if unit.path == item["path"]]
                    for content in (item["before"], item["after"]):
                        if content is not None:
                            parsed, _ = parse_document_metadata(item["path"], content)
                            units.extend(parsed)
                    unavailable[item["path"]] = tuple(units)
        except LifecycleError:
            blocked = {path.relative_to(repository).as_posix() for _, owner in root_paths for path in owner.rglob("*.md")}
        for path in sorted(blocked):
            issues.append(MetadataIssue("ABM007", path, 1, 1, "publication/recovery pending; affected guidance is unavailable"))
    for root_name, resolved_root in root_paths:
        candidates = sorted(resolved_root.rglob("*.md")) if resolved_root.is_dir() else []
        for candidate in candidates:
            try:
                resolved = candidate.resolve(strict=True)
            except OSError as exc:
                issues.append(MetadataIssue("ABM004", _repo_relative(repository, candidate), 1, 1,
                                            f"guidance file unavailable: {exc}"))
                continue
            if not resolved.is_relative_to(resolved_root):
                issues.append(MetadataIssue("ABM004", _repo_relative(repository, candidate), 1, 1,
                                            "guidance file resolves outside its declared knowledge root"))
                continue
            relative = _repo_relative(repository, candidate)
            if relative in blocked:
                continue
            if relative in documents:
                continue
            content, issue = _read_utf8(relative, resolved)
            if issue is not None:
                issues.append(issue)
            elif content is not None:
                documents[relative] = content

    units: list[GuidanceUnit] = []
    for relative, content in sorted(documents.items()):
        parsed, parse_issues = parse_document_metadata(relative, content)
        units.extend(parsed)
        issues.extend(parse_issues)

    for mapped in config.mapped_units:
        if mapped.path in blocked:
            continue
        content = documents.get(mapped.path)
        if content is None:
            artifact = repository / Path(*mapped.path.split("/"))
            try:
                resolved = artifact.resolve(strict=True)
            except OSError as exc:
                issues.append(MetadataIssue("ABM004", mapped.path, 1, 1,
                                            f"mapped guidance is unavailable: {exc}"))
                continue
            allowed_roots = [root for _, root in root_paths if resolved.is_relative_to(root)]
            if not resolved.is_relative_to(repository) or not allowed_roots:
                raise ConfigurationError(
                    f"mapped artifact resolves outside declared knowledge roots: {mapped.path}"
                )
            content, issue = _read_utf8(mapped.path, resolved)
            if issue is not None:
                issues.append(issue)
                continue
            assert content is not None
            documents[mapped.path] = content
        if mapped.selector == "section":
            assert mapped.heading is not None
            selected_content, issue = extract_section_content(mapped.path, content, mapped.heading)
            if issue is not None:
                issues.append(issue)
                continue
            assert selected_content is not None
            content = selected_content
        units.append(
            GuidanceUnit(
                id=mapped.id,
                path=mapped.path,
                selector=mapped.selector,
                heading=mapped.heading,
                kind=mapped.kind,
                status=mapped.status,
                applies=mapped.applies,
                requires=mapped.requires,
                evidence=mapped.evidence,
                content=content,
                source="mapping",
            )
        )

    ids_by_path: dict[str, list[str]] = {}
    for unit in units:
        ids_by_path.setdefault(unit.path, []).append(unit.id)
    contained_ids = {path: tuple(dict.fromkeys(ids)) for path, ids in ids_by_path.items()}
    return KnowledgeBase(tuple(units), tuple(issues), documents, contained_ids, unavailable)


def _repo_relative(repository: Path, path: Path) -> str:
    try:
        return path.absolute().relative_to(repository).as_posix()
    except ValueError:
        return path.as_posix()


def _read_utf8(relative: str, resolved: Path) -> tuple[str | None, MetadataIssue | None]:
    try:
        before = resolved.stat()
        raw = resolved.read_bytes()
        after = resolved.stat()
    except OSError as exc:
        return None, MetadataIssue("ABM004", relative, 1, 1, f"guidance file unavailable: {exc}")
    if len(raw) != before.st_size or before.st_size != after.st_size or before.st_mtime_ns != after.st_mtime_ns:
        return None, MetadataIssue("ABM006", relative, 1, 1, "guidance changed while it was being read; delivery is incomplete")
    try:
        return raw.decode("utf-8"), None
    except UnicodeDecodeError as exc:
        return None, MetadataIssue("ABM006", relative, 1, 1,
                                   f"guidance is not complete UTF-8 text at byte {exc.start}")
