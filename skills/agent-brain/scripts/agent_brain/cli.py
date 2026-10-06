"""Command-line interface for the agent-brain bundle."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .config import ConfigurationError, load_config
from .knowledge import recall_whole_artifacts
from .records import CommandError, Diagnostic, ErrorDetail, InspectionResult, RecallResult


COMMANDS = {
    "recall": "Read complete mapped guidance for informational use.",
    "learn": "Request an evidenced lesson update through a registered integration.",
    "dream": "Request a knowledge review through a registered integration.",
    "setup": "Repository setup is not available from this CLI.",
    "doctor": "Check the repository configuration without changing it.",
    "status": "Show repository configuration and state without changing them.",
}

COMMAND_DETAILS = {
    "recall": (
        "Inputs: --config PATH selects a repository configuration; otherwise the default is used.\n"
        "Effects: reads each configured startup artifact in full and prints it as informational context. "
        "It does not confirm agent delivery.\n"
        "Active agent: the foreground agent applies relevant context; receipt is not confirmed.\n"
        "Example: agent-brain recall --config .agents/context/config.json"
    ),
    "learn": (
        "Inputs: UTF-8 JSON from --input PATH (or - for stdin) and an integration-issued --invocation-file.\n"
        "Effects: this standalone CLI reports that registered active context is unavailable before it "
        "reads input or changes files.\n"
        "Active agent: a registered integration is required; the CLI never launches a model.\n"
        "Example: agent-brain learn --input notes.json --invocation-file /path/to/invocation.json"
    ),
    "dream": (
        "Inputs: UTF-8 JSON from --input PATH (or - for stdin) and an integration-issued --invocation-file.\n"
        "Effects: this standalone CLI reports that registered active context is unavailable before it "
        "reads input or changes files.\n"
        "Active agent: a registered integration is required; the CLI never launches a model.\n"
        "Example: agent-brain dream --input review.json --invocation-file /path/to/invocation.json"
    ),
    "setup": (
        "Inputs: none.\n"
        "Effects: setup is not available from this CLI, and no repository files are changed.\n"
        "Active agent: none.\n"
        "Example: agent-brain setup"
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
    runtime_present = DEFAULT_RUNTIME_STATE.is_file()
    if config_present:
        try:
            load_config(config_path)
        except ConfigurationError as exc:
            setup_status = "invalid"
            config_check = Diagnostic("portable configuration", "invalid", str(exc))
        else:
            setup_status = "configured"
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
    checks = (
        config_check,
        Diagnostic(
            "runtime state",
            "present" if runtime_present else "missing",
            f"{'Found' if runtime_present else 'Not found'}: {DEFAULT_RUNTIME_STATE.as_posix()}.",
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
        runtime_state_path=DEFAULT_RUNTIME_STATE.as_posix(),
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
        return

    print(result.notice)
    for artifact in result.artifacts:
        print(f"\n## {artifact.path} [whole artifact]")
        sys.stdout.write(artifact.content)
        if not artifact.content.endswith(("\n", "\r")):
            sys.stdout.write("\n")


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

    if arguments.command in ("status", "doctor"):
        result = _inspection_result(arguments.command, arguments.config)
        _print_inspection(result, json_output=arguments.json_output)
        return 0

    if arguments.command == "recall":
        config_path = Path(arguments.config) if arguments.config is not None else DEFAULT_CONFIG
        try:
            config = load_config(config_path)
            result = recall_whole_artifacts(config, repository_root=Path.cwd())
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
        _print_recall(result, json_output=arguments.json_output)
        return 0

    if arguments.command in ("learn", "dream"):
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
