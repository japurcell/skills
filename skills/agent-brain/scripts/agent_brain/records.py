"""Typed records used by the first public agent-brain CLI commands."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


OperationStatus = Literal["ok", "error"]
SetupStatus = Literal["uninitialized", "configured", "invalid"]
CheckStatus = Literal["present", "missing", "invalid", "unavailable", "disabled"]
InspectionCommand = Literal["doctor", "status"]
RetryEligibility = Literal[True, False]
KnowledgeOwnership = Literal["read_only", "agent_brain"]
LoadingMode = Literal["whole"]


@dataclass(frozen=True, slots=True)
class KnowledgeRoot:
    path: str
    ownership: KnowledgeOwnership


@dataclass(frozen=True, slots=True)
class MappedUnit:
    id: str
    path: str
    unit: Literal["whole"]


@dataclass(frozen=True, slots=True)
class StartupRead:
    id: str
    loading_mode: LoadingMode


@dataclass(frozen=True, slots=True)
class AgentBrainConfig:
    schema_version: Literal[1]
    repository_id: str
    knowledge_roots: tuple[KnowledgeRoot, ...]
    mapped_units: tuple[MappedUnit, ...]
    startup: tuple[StartupRead, ...]


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
    artifacts: tuple[RecalledArtifact, ...]

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
