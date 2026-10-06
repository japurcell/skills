"""Command-line interface for the agent-brain bundle."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .config import ConfigurationError, load_config
from .knowledge import load_knowledge
from .retrieval import retrieve
from .records import CommandError, Diagnostic, ErrorDetail, InspectionResult, RecallResult
from .records import RetrievalScope


COMMANDS = {
    "recall": "Read complete mapped guidance for informational use.",
    "learn": "A registered integration is required for an evidenced lesson update.",
    "dream": "A registered integration is required for a knowledge review.",
    "setup": "Plan repository setup or apply a reviewed exact plan.",
    "doctor": "Check the repository configuration without changing it.",
    "status": "Show repository configuration and state without changing them.",
}

COMMAND_DETAILS = {
    "recall": (
        "Inputs: --config PATH selects a repository configuration; otherwise the default is used.\n"
        "Effects: reads configured startup guidance and relevant indexed units; --path, --concept, "
        "--action, --dependency, --provider, and --runtime add known scope, while --query searches text. "
        "Without task scope, recall shows startup plus universal policy. --all-guidance browses the full library. "
        "--investigate includes candidate guidance; --show-evidence discloses evidence details. "
        "The result does not confirm agent delivery.\n"
        "Active agent: the foreground agent applies relevant context; receipt is not confirmed.\n"
        "Example: agent-brain recall --path src/app.py --concept python"
    ),
    "learn": (
        "Inputs: UTF-8 JSON from --input PATH (or - for stdin) and an integration-issued --invocation-file.\n"
        "Effects: start delivers a foreground work package; prepare validates an evidenced proposal or scoped no-change review; "
        "publish writes the exact prepared set with inverse history; complete checks resulting files and settles current obligations. "
        "Invalid authority fails before semantic input.\n"
        "Active agent: a registered integration is required; the CLI never launches a model.\n"
        "Example: agent-brain learn prepare --input proposal.json --invocation-file /path/to/invocation.json; "
        "agent-brain learn publish --invocation-file /path/to/invocation.json; "
        "agent-brain learn complete --invocation-file /path/to/invocation.json"
    ),
    "dream": (
        "Inputs: UTF-8 JSON from --input PATH (or - for stdin) and an integration-issued --invocation-file.\n"
        "Effects: checks an assigned finite review batch, publishes evidenced changes, and records exact coverage. "
        "Routine coverage stays due until every current target is reviewed; unfinished assigned work blocks session completion.\n"
        "Active agent: a registered integration is required; the CLI never launches a model.\n"
        "Example: agent-brain dream start --invocation-file /path/to/invocation.json; "
        "agent-brain dream prepare --input review.json --invocation-file /path/to/invocation.json; "
        "agent-brain dream complete --input review.json --invocation-file /path/to/invocation.json"
    ),
    "setup": (
        "Inputs: --config selects mappings; --apply --plan requires a still-valid reviewed plan.\n"
        "Effects: plain setup is read-only. Apply/rollback journal exact managed effects; retained private operational ignore guards survive rollback.\n"
        "Active agent: no model is launched; matching certification is required for activation.\n"
        "Privacy: raw plans contain provider setting snapshots. Save to an owner-only private file outside the worktree.\n"
        "Example: agent-brain setup --json; save privately and review, then agent-brain setup --apply --plan /private/outside-worktree/plan.json --json"
    ),
    "doctor": (
        "Inputs: --config PATH selects a repository configuration; otherwise the default is used.\n"
        "Effects: validates configuration and reports runtime-state presence without changing files.\n"
        "Active agent: none; this report does not establish integration context.\n"
        "Example: agent-brain doctor --config .agents/context/config.json"
    ),
    "status": (
        "Inputs: --config PATH selects a repository configuration; otherwise the default is used.\n"
        "Effects: reports configuration and runtime-state presence without changing files. Active "
        "integration context is unavailable to this standalone CLI.\n"
        "Active agent: none; this report does not establish integration context.\n"
        "Example: agent-brain status"
    ),
}

HELP_DETAILS = (
    "Inputs: an optional command name.\n"
    "Effects: prints command help without reading repository state or changing files.\n"
    "Active agent: none.\n"
    "Example: agent-brain help recall"
)

DEFAULT_CONFIG = Path(".agents/context/config.json")
DEFAULT_RUNTIME_STATE = Path(".agents/context/state/brain.sqlite3")


class _JsonUsageError(Exception):
    """Raised after a JSON-mode parser has emitted its public usage result."""


class _ArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args: object, json_errors: bool = False, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.json_errors = json_errors

    def error(self, message: str) -> None:
        if self.json_errors:
            _print_error(
                "USAGE_INVALID",
                message,
                "command-line arguments",
                "Correct the command-line arguments and consult agent-brain --help.",
                json_output=True,
            )
            raise _JsonUsageError from None
        super().error(message)


def _parser(*, json_errors: bool) -> tuple[argparse.ArgumentParser, dict[str, argparse.ArgumentParser]]:
    parser = _ArgumentParser(
        prog="agent-brain",
        allow_abbrev=False,
        json_errors=json_errors,
        description=(
            "A cooperative context CLI with read-only status, doctor, and whole-artifact recall. "
            "The standalone CLI never starts a model."
        ),
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"agent-brain {__version__}",
    )
    _add_shared_options(parser)
    subparsers = parser.add_subparsers(
        dest="command",
        metavar="COMMAND",
        title="Commands",
        parser_class=_ArgumentParser,
    )
    command_parsers: dict[str, argparse.ArgumentParser] = {}
    for name, description in COMMANDS.items():
        command_parser = subparsers.add_parser(
            name,
            description=description,
            help=description,
            epilog=COMMAND_DETAILS[name],
            allow_abbrev=False,
            json_errors=json_errors,
        )
        _add_shared_options(command_parser, inherited=True)
        command_parsers[name] = command_parser
    for name in ("learn", "dream"):
        command_parsers[name].add_argument("operation", nargs="?", default="start",
            choices=("start", "prepare", "publish", "complete"), help="Start foreground work, prepare evidence, publish exact changes, or verify completion.")
        command_parsers[name].add_argument(
            "--input",
            metavar="PATH",
            help="Read UTF-8 JSON from a file, or - for stdin.",
        )
    for name in ("learn", "dream"):
        command_parsers[name].add_argument(
            "--invocation-file",
            metavar="PATH",
            help="Integration-issued context; a path alone cannot grant authority.",
        )
    setup_parser = command_parsers["setup"]
    setup_parser.add_argument("--apply", action="store_true", help="Apply a still-valid reviewed plan.")
    setup_parser.add_argument("--plan", metavar="PATH", help="Private reviewed plan file, preferably outside the worktree.")
    setup_parser.add_argument("--rollback", metavar="PATH", help="Reverse only exact owned effects from a setup journal.")
    setup_parser.add_argument("--deactivate", action="store_true", help="Plan removal of owned registrations and authority.")
    setup_parser.add_argument("--shell", choices=("posix", "powershell"), help="Explicit configured shell command representation.")
    recall_parser = command_parsers["recall"]
    recall_parser.add_argument("--query", metavar="TEXT", help="Search guidance text and routed concepts.")
    recall_parser.add_argument(
        "--all-guidance", action="store_true",
        help="Browse all established guidance when no task scope is supplied.",
    )
    for field in ("path", "concept", "action", "dependency", "provider", "runtime"):
        plural = field[:-1] + "ies" if field.endswith("y") else field + "s"
        recall_parser.add_argument(
            f"--{field}", dest=plural, action="append", default=[], metavar="VALUE",
            help=f"Add a known {field} to retrieval scope; may be repeated.",
        )
    recall_parser.add_argument(
        "--investigate", action="store_true",
        help="Include applicable candidate units for investigation; they never satisfy policy references.",
    )
    recall_parser.add_argument(
        "--show-evidence", action="store_true",
        help="Include detailed evidence notes for a relevant investigation or precision request.",
    )
    help_parser = subparsers.add_parser(
        "help",
        description="Show help for a command.",
        help="Show help for a command.",
        epilog=HELP_DETAILS,
        allow_abbrev=False,
        json_errors=json_errors,
    )
    help_parser.add_argument("command_name", nargs="?", choices=tuple(COMMANDS))
    return parser, command_parsers


def _add_shared_options(parser: argparse.ArgumentParser, *, inherited: bool = False) -> None:
    default = argparse.SUPPRESS if inherited else None
    parser.add_argument(
        "--config",
        metavar="PATH",
        default=default,
        help="Select a repository configuration.",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        default=default,
        help="Write a JSON result.",
    )
    parser.add_argument(
        "--no-color",
        dest="no_color",
        action="store_true",
        default=default,
        help="Disable terminal color.",
    )


def _inspection_result(command: str, config_argument: str | None) -> InspectionResult:
    config_path = Path(config_argument) if config_argument is not None else DEFAULT_CONFIG
    config_present = config_path.is_file()
    runtime_state_path = DEFAULT_RUNTIME_STATE
    if config_present:
        try:
            config = load_config(config_path)
        except ConfigurationError as exc:
            setup_status = "invalid"
            config_check = Diagnostic("portable configuration", "invalid", str(exc))
        else:
            setup_status = "configured"
            runtime_state_path = Path(config.state_dir) / "brain.sqlite3"
            config_check = Diagnostic(
                "portable configuration",
                "present",
                f"Validated: {config_path.as_posix()}.",
            )
    else:
        setup_status = "uninitialized"
        config_check = Diagnostic(
            "portable configuration",
            "missing",
            f"Not found: {config_path.as_posix()}.",
        )
    runtime_present = runtime_state_path.is_file()
    checks = (
        config_check,
        Diagnostic(
            "runtime state",
            "present" if runtime_present else "missing",
            f"{'Found' if runtime_present else 'Not found'}: {runtime_state_path.as_posix()}.",
        ),
        Diagnostic(
            "active integration context",
            "unavailable",
            "This standalone CLI cannot establish registered active context.",
        ),
        Diagnostic(
            "model execution",
            "disabled",
            "The CLI never launches a model.",
        ),
    )
    return InspectionResult(
        schema_version=1,
        operation_status="ok",
        command=command,  # type: ignore[arg-type]
        setup_status=setup_status,  # type: ignore[arg-type]
        config_path=config_path.as_posix(),
        config_present=config_present,
        runtime_state_path=runtime_state_path.as_posix(),
        runtime_state_present=runtime_present,
        active_context="unavailable",
        model_execution="disabled",
        checks=checks if command == "doctor" else (),
    )


def _print_inspection(result: InspectionResult, *, json_output: bool) -> None:
    if json_output:
        print(json.dumps(result.as_json_object(), ensure_ascii=False, indent=2, sort_keys=True))
        return

    print(f"agent-brain {result.command}")
    print(f"Setup: {result.setup_status}")
    config_state = "present" if result.config_present else "missing"
    print(f"Configuration: {config_state} ({result.config_path})")
    print(
        "Runtime state: "
        f"{'present' if result.runtime_state_present else 'missing'} ({result.runtime_state_path})"
    )
    print("Active integration context: unavailable in this CLI")
    print("Model execution: disabled; the CLI never launches a model")
    if result.command == "doctor":
        print("Checks:")
        for check in result.checks:
            print(f"- {check.name}: {check.status} - {check.detail}")


def _print_error(
    code: str,
    cause: str,
    affected_scope: str,
    next_action: str,
    *,
    json_output: bool,
) -> None:
    if json_output:
        result = CommandError(
            1,
            "error",
            ErrorDetail(code, cause, affected_scope, False, next_action),
        )
        print(
            json.dumps(
                result.as_json_object(),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ),
        )
    print(f"agent-brain: {code}: {cause}", file=sys.stderr)
    print(f"Next action: {next_action}", file=sys.stderr)


def _print_recall(result: RecallResult, *, json_output: bool) -> None:
    if json_output:
        print(json.dumps(result.as_json_object(), ensure_ascii=False, indent=2, sort_keys=True))
        _print_recall_gaps(result)
        return

    print(result.notice)
    if result.scope_status == "task_unknown":
        print("Task scope: unknown; showing required startup guidance and universal policy only.")
    elif result.scope_status == "library":
        print("Scope: complete indexed guidance library.")
    elif result.scope_status == "broadened":
        print("Scope: broadened because one or more selectors were uncertain.")
    for artifact in result.artifacts:
        label = "whole artifact" if artifact.loading_mode == "whole" else "guidance unit"
        print(f"\n## {artifact.path} [{label}]")
        scope_parts = [
            f"{field}={', '.join(values)}"
            for field, values in artifact.applies.items()
            if values
        ]
        print(f"Applies: {'; '.join(scope_parts) if scope_parts else 'unspecified'}")
        if artifact.evidence_details_included:
            print("Whole-artifact read preserves source metadata comments and any detailed evidence they contain.")
        sys.stdout.write(artifact.content)
        if not artifact.content.endswith(("\n", "\r")):
            sys.stdout.write("\n")
        contained_ids = set(artifact.contained_unit_ids)
        for unit in result.units:
            if unit.id in contained_ids and unit.evidence:
                print(f"Evidence for {unit.id}: {json.dumps(unit.evidence, ensure_ascii=False, sort_keys=True)}")
    _print_recall_gaps(result)


def _print_recall_gaps(result: RecallResult) -> None:
    for gap in result.gaps:
        print(f"agent-brain: CONTEXT_GAP: {gap['path']}: {gap['message']}", file=sys.stderr)


def _configure_output_encoding() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="strict")


def main(argv: Sequence[str] | None = None) -> int:
    _configure_output_encoding()
    selected_argv = list(argv) if argv is not None else sys.argv[1:]
    parser, command_parsers = _parser(json_errors="--json" in selected_argv)
    try:
        arguments = parser.parse_args(selected_argv)
    except _JsonUsageError:
        return 2
    except SystemExit as exc:
        return int(exc.code)

    if arguments.command is None:
        parser.print_help()
        return 0

    if arguments.command == "help":
        if arguments.command_name is None:
            parser.print_help()
        else:
            command_parsers[arguments.command_name].print_help()
        return 0

    if arguments.command == "setup":
        from .setup import run
        from .state import LifecycleError
        try:
            result = run(arguments, Path.cwd().resolve())
        except (LifecycleError, ConfigurationError, OSError, ValueError, KeyError, TypeError) as exc:
            _print_error(getattr(exc, "code", "SETUP_INVALID"), str(exc), "repository setup",
                getattr(exc, "next_action", "Correct the configuration, exact reviewed plan or certified software inputs and retry."),
                json_output=arguments.json_output)
            return getattr(exc, "exit_code", 2)
        except KeyboardInterrupt:
            _print_error("SETUP_INTERRUPTED", "apply or inverse is incomplete; the durable journal retains recoverable effects", "repository setup",
                "Inspect status and use setup --rollback PATH with the retained setup journal.", json_output=arguments.json_output)
            return 130
        if arguments.json_output:
            print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        else:
            print("agent-brain setup\nActivation: " + result["activation"])
            for item in result.get("changes", []):
                print(f"Change: {item['path']} ({item['before_revision']} -> {item['after_revision']})")
            for prerequisite in result.get("prerequisites", []):
                print(f"Prerequisite: {prerequisite['name']}: {prerequisite['status']}")
            if "journal_path" in result:
                print("Managed inverse journal: " + result["journal_path"])
            else:
                print("Save raw setup --json output to an owner-only private file outside the worktree; it contains provider setting snapshots. Review it, then run setup --apply --plan PATH.")
        return 0

    if arguments.command in ("status", "doctor"):
        result = _inspection_result(arguments.command, arguments.config)
        if result.setup_status == "configured":
            from .lifecycle import inspection
            config_path = Path(arguments.config) if arguments.config is not None else DEFAULT_CONFIG
            details = inspection(load_config(config_path), Path.cwd().resolve(), config_path)
            from .diagnostics import diagnose
            details.update(diagnose(load_config(config_path), Path.cwd().resolve()))
            if arguments.json_output:
                print(json.dumps(result.as_json_object() | details, ensure_ascii=False, sort_keys=True))
            else:
                _print_inspection(result, json_output=False)
                print(f"Lifecycle state: {details['state_status']}")
                print(f"Activation: {details['activation_status']}; software: {details['software_status']}")
                for session in details["work_sessions"]:
                    print(f"Work session {session['work_session_id']}: {session['work_session_status']}")
        else:
            from .diagnostics import diagnose
            details = diagnose(None, Path.cwd().resolve())
            if arguments.json_output:
                print(json.dumps(result.as_json_object() | details, ensure_ascii=False, sort_keys=True))
            else:
                _print_inspection(result, json_output=False)
                print(f"Activation: {details['activation_status']}; software: {details['software_status']}")
        return 0

    if arguments.command == "recall":
        config_path = Path(arguments.config) if arguments.config is not None else DEFAULT_CONFIG
        try:
            config = load_config(config_path)
            knowledge = load_knowledge(config, repository_root=Path.cwd())
            scope = RetrievalScope(
                query=arguments.query,
                selectors={
                    "paths": tuple(arguments.paths),
                    "concepts": tuple(arguments.concepts),
                    "actions": tuple(arguments.actions),
                    "dependencies": tuple(arguments.dependencies),
                    "providers": tuple(arguments.providers),
                    "runtimes": tuple(arguments.runtimes),
                },
                investigate=arguments.investigate,
                show_evidence=arguments.show_evidence,
                all_guidance=arguments.all_guidance,
            )
            result = retrieve(config, knowledge, scope)
            from .source_ingestion import snapshot, pending
            from .state import LifecycleError
            from dataclasses import replace
            gaps = []
            try:
                source_state = snapshot(config, Path.cwd().resolve())
                if source_state is not None and (source_state["blocking"] or source_state["changes"]):
                    gaps.append({"code": "SOURCE_INGESTION_PENDING", "path": ".agents/sources", "message": "Focused source ingestion and current redelivery are required before a dependent action or conclusion."})
                if source_state is not None:
                    from .lifecycle import inspection
                    inspected = inspection(config, Path.cwd().resolve(), config_path)
                    if inspected["state_status"] == "unavailable" or any(session.get("source_work") and not session.get("action_ready") for session in inspected["work_sessions"]):
                        gaps.append({"code": "SOURCE_REDELIVERY_REQUIRED", "path": ".agents/context", "message": "Current foreground source evidence and redelivery are incomplete."})
            except LifecycleError as exc:
                gaps.append({"code": exc.code, "path": ".agents/sources", "message": str(exc)})
            if gaps:
                result = replace(result, recall=replace(result.recall, complete=False, gaps=result.recall.gaps + tuple(gaps)), exit_code=1)
        except ConfigurationError as exc:
            _print_error(
                "CONFIGURATION_INVALID",
                str(exc),
                "repository configuration and mapped guidance",
                "Correct the supported configuration using "
                "skills/agent-brain/schemas/config-v1.schema.json, then retry recall.",
                json_output=arguments.json_output,
            )
            return 2
        try:
            _print_recall(result.recall, json_output=arguments.json_output)
            sys.stdout.flush()
        except BrokenPipeError:
            with open(os.devnull, "w", encoding="utf-8") as sink:
                os.dup2(sink.fileno(), sys.stdout.fileno())
            print("agent-brain: DELIVERY_INCOMPLETE: output closed before recall completed.", file=sys.stderr)
            return 1
        return result.exit_code

    if arguments.command in ("learn", "dream"):
        if arguments.invocation_file:
            from .lifecycle import stage_operation, error_result
            from .state import LifecycleError
            try:
                result, code, store = stage_operation(arguments.command, arguments.operation,
                    arguments.invocation_file, arguments.config, arguments.input)
            except (LifecycleError, ConfigurationError, OSError, ValueError, TypeError, KeyError) as exc:
                if isinstance(exc, LifecycleError) and exc.code == "ACTIVE_CONTEXT_REQUIRED":
                    pass
                else:
                    error = exc if isinstance(exc, LifecycleError) else LifecycleError("INPUT_INVALID", str(exc))
                    if arguments.json_output:
                        print(json.dumps(error_result(error), ensure_ascii=False, sort_keys=True))
                    print(f"agent-brain: {error.code}: {error}", file=sys.stderr)
                    print(f"Next action: {error.next_action}", file=sys.stderr)
                    return error.exit_code
            except KeyboardInterrupt:
                import signal
                signal.signal(signal.SIGINT, signal.SIG_IGN)
                error = LifecycleError("INTERRUPTED", "interrupted attempt preserves pending work", exit_code=130)
                if arguments.json_output:
                    print(json.dumps(error_result(error), sort_keys=True))
                print("agent-brain: INTERRUPTED: pending work is retained.", file=sys.stderr)
                return 130
            else:
                if code != 0 and "error" in result:
                    print(f"agent-brain: {result['error']['code']}: {result['error']['cause']}", file=sys.stderr)
                    print(f"Next action: {result['error']['next_action']}", file=sys.stderr)
                try:
                    if arguments.operation == "complete" and code == 0:
                        from .publication import barrier
                        barrier(load_config(Path(arguments.config or ".agents/context/config.json")), Path.cwd().resolve(), "after_completion")
                    if arguments.json_output:
                        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
                    else:
                        print(f"Stage: {result['stage_outcome']}; work session: {result['work_session_status']}")
                        if "work_package" in result:
                            print(json.dumps(result["work_package"], ensure_ascii=False, indent=2, sort_keys=True))
                            print(f"Current input revision: {result['input_revision']}")
                        if "check_receipts" in result:
                            print(json.dumps(result["check_receipts"], indent=2, sort_keys=True))
                    sys.stdout.flush()
                    if arguments.operation == "complete" and code == 0:
                        from .lifecycle import settle_output
                        settle_output(result, arguments.config, delivered=True, store=store)
                except BrokenPipeError:
                    from .lifecycle import failed_output
                    failed_output(result, arguments.config, store=store)
                    return 1
                except (LifecycleError, ConfigurationError, OSError) as exc:
                    print(f"agent-brain: DELIVERY_RECONCILIATION_REQUIRED: {exc}", file=sys.stderr)
                    return 1
                except KeyboardInterrupt:
                    import signal
                    signal.signal(signal.SIGINT, signal.SIG_IGN)
                    error = LifecycleError("INTERRUPTED", "unfinished completion output remains pending", exit_code=130)
                    if arguments.json_output:
                        print(json.dumps(error_result(error), sort_keys=True))
                    print("agent-brain: INTERRUPTED: pending output reconciliation is retained.", file=sys.stderr)
                    return 130
                return code
        _print_error(
            "ACTIVE_CONTEXT_REQUIRED",
            f"{arguments.command} requires registered active agent context; "
            "this standalone CLI cannot establish it.",
            arguments.command,
            "Use recall for informational reads. Run learn or dream only through a "
            "registered integration; this CLI never launches a model.",
            json_output=arguments.json_output,
        )
        return 2

    _print_error(
        "COMMAND_NOT_AVAILABLE",
        f"{arguments.command} is not available in this CLI; no repository changes were made.",
        arguments.command,
        "Use a read-only command such as status, doctor, or recall.",
        json_output=arguments.json_output,
    )
    return 2
