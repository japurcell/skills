"""Typed records used by the first public agent-brain CLI commands."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal


OperationStatus = Literal["ok", "error"]
SetupStatus = Literal["uninitialized", "configured", "invalid"]
CheckStatus = Literal["present", "missing", "invalid", "unavailable", "disabled"]
InspectionCommand = Literal["doctor", "status"]
RetryEligibility = Literal[True, False]
KnowledgeOwnership = Literal["read_only", "agent_brain"]
LoadingMode = Literal["unit", "whole"]
GuidanceLoadingMode = Literal["unit", "whole"]
GuidanceKind = Literal["policy", "fact"]
GuidanceStatus = Literal["established", "candidate"]


@dataclass(frozen=True, slots=True)
class KnowledgeRoot:
    path: str
    ownership: KnowledgeOwnership


@dataclass(frozen=True, slots=True)
class MappedUnit:
    id: str
    path: str
    selector: Literal["document", "section"]
    heading: str | None
    kind: GuidanceKind
    status: GuidanceStatus
    applies: dict[str, tuple[str, ...]]
    requires: tuple["RequiredReference", ...]
    evidence: dict[str, object]


@dataclass(frozen=True, slots=True)
class StartupRead:
    id: str
    loading_mode: GuidanceLoadingMode


@dataclass(frozen=True, slots=True)
class AgentBrainConfig:
    schema_version: Literal[1]
    repository_id: str
    knowledge_roots: tuple[KnowledgeRoot, ...]
    mapped_units: tuple[MappedUnit, ...]
    startup: tuple[StartupRead, ...]
    providers: dict[str, dict[str, object]] = field(default_factory=dict)
    checks: dict[str, object] = field(default_factory=lambda: {
        "required": ["guidance", "review_sources"], "trusted": [],
    })
    limits: dict[str, float | int] = field(default_factory=lambda: {
        "lease_seconds": 1800, "contention_seconds": 2, "max_attempts": 3,
        "check_timeout_seconds": 60,
    })
    state_dir: str = ".agents/context/state"


@dataclass(frozen=True, slots=True)
class GuidanceUnit:
    id: str
    path: str
    selector: Literal["document", "section"]
    heading: str | None
    kind: GuidanceKind
    status: GuidanceStatus
    applies: dict[str, tuple[str, ...]]
    requires: tuple["RequiredReference", ...]
    evidence: dict[str, object]
    content: str
    source: Literal["annotation", "mapping"]


@dataclass(frozen=True, slots=True)
class RequiredReference:
    id: str
    loading_mode: GuidanceLoadingMode


@dataclass(frozen=True, slots=True)
class RetrievalScope:
    query: str | None
    selectors: dict[str, tuple[str, ...]]
    investigate: bool = False
    show_evidence: bool = False
    all_guidance: bool = False


@dataclass(frozen=True, slots=True)
class RecalledUnit:
    id: str
    path: str
    kind: GuidanceKind
    status: GuidanceStatus
    loading_mode: GuidanceLoadingMode
    source: Literal["annotation", "mapping"]
    applies: dict[str, tuple[str, ...]]
    content_revision: str
    input_revision: str
    requires: tuple[RequiredReference, ...]
    evidence: dict[str, object]


@dataclass(frozen=True, slots=True)
class DeliveryArtifact:
    id: str
    path: str
    loading_mode: GuidanceLoadingMode
    applies: dict[str, tuple[str, ...]]
    evidence_details_included: bool
    content: str
    content_bytes: int
    content_revision: str
    input_revision: str
    contained_unit_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Diagnostic:
    name: str
    status: CheckStatus
    detail: str


@dataclass(frozen=True, slots=True)
class InspectionResult:
    schema_version: Literal[1]
    operation_status: OperationStatus
    command: InspectionCommand
    setup_status: SetupStatus
    config_path: str
    config_present: bool
    runtime_state_path: str
    runtime_state_present: bool
    active_context: Literal["unavailable"]
    model_execution: Literal["disabled"]
    checks: tuple[Diagnostic, ...] = ()

    def as_json_object(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RecalledArtifact:
    id: str
    path: str
    loading_mode: LoadingMode
    content: str


@dataclass(frozen=True, slots=True)
class RecallResult:
    schema_version: Literal[1]
    operation_status: OperationStatus
    command: Literal["recall"]
    informational_only: Literal[True]
    notice: str
    scope_status: Literal["task_unknown", "scoped", "broadened", "library"]
    complete: bool
    gaps: tuple[dict[str, str], ...]
    units: tuple[RecalledUnit, ...]
    artifacts: tuple[DeliveryArtifact, ...]

    def as_json_object(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ErrorDetail:
    code: str
    cause: str
    affected_scope: str
    retry_eligible: RetryEligibility
    next_action: str


@dataclass(frozen=True, slots=True)
class CommandError:
    schema_version: Literal[1]
    operation_status: Literal["error"]
    error: ErrorDetail

    def as_json_object(self) -> dict[str, object]:
        return asdict(self)
