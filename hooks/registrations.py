"""Exact provider registration identities, including explicitly retired events.

This installer-only registry never runs inside provider hooks. Unknown commands
are retained; an owned path combined with an unrecognized launch is ambiguous.
"""
from __future__ import annotations

import copy
import hashlib
import sys
from contextlib import contextmanager
import os
from pathlib import Path
import stat
import shlex

from scripts.trusted_hook_launch import serialize_trusted_launch, trusted_posix_arguments, hook_arguments, template_commands

DESIRED = {
    "codex": {"SessionStart": ("load-required-skills.py",)},
    "copilot": {
        "sessionEnd": ("bell.py",),
        "sessionStart": ("load-required-skills.py",),
    },
    "gemini": {
        "SessionStart": ("skill-context-injector.py",),
        "BeforeTool": ("rtk-hook-gemini.py",),
    },
}
# These identities do not depend on events present in the replacement template.
RETIRED = {
    'codex': {
        'PreToolUse': ('scan-secrets.py', 'rtk-explicit-codex.py', 'tool-guard.py'),
        'PostToolUse': ('rtk-explicit-codex.py', 'rtk-agent-launcher.py', 'auto-index-brain.py'),
        'SessionStart': ('inject-brain.py',),
        'Stop': ('scan-secrets.py', 'scan-status.py'),
    },
    'copilot': {
        'preToolUse': ('scan-secrets.py', 'tool-guard.py', 'send-event.py'),
        'sessionEnd': ('scan-secrets.py', 'send-event.py'),
        'sessionStart': ('inject-brain.py', 'send-event.py'),
        'postToolUse': ('auto-index-brain.py', 'send-event.py'),
        'agentStop': ('scan-status.py', 'send-event.py'),
        'errorOccurred': ('send-event.py',),
        'notification': ('send-event.py',),
        'permissionRequest': ('send-event.py',),
        'preCompact': ('send-event.py',),
        'postToolUseFailure': ('send-event.py',),
        'subagentStart': ('send-event.py',),
        'subagentStop': ('send-event.py',),
        'userPromptSubmitted': ('send-event.py',),
        'userPromptTransformed': ('send-event.py',),
    },
    'gemini': {
        'BeforeTool': ('scan-secrets.py', 'tool-guard.py', 'send-event.py'),
        'SessionEnd': ('scan-secrets.py', 'send-event.py'),
        'SessionStart': ('inject-brain.py', 'send-event.py'),
        'AfterTool': ('auto-index-brain.py', 'send-event.py'),
        'AfterAgent': ('scan-status.py', 'send-event.py'),
        'BeforeAgent': ('send-event.py',),
        'BeforeModel': ('send-event.py',),
        'AfterModel': ('send-event.py',),
        'BeforeToolSelection': ('send-event.py',),
        'PreCompress': ('send-event.py',),
        'Notification': ('send-event.py',),
    },
}

# Historical ingestion/OKF registrations are retired only at exact known launches.
for _provider, _events in {
    "codex": {"Stop": ("repository-okf.py",)},
    "copilot": {"sessionStart": ("auto-ingest-source.py",),
                "userPromptTransformed": ("inject-auto-ingest-context.py",),
                "agentStop": ("validate-stop.py", "lint-okf.py", "inject-auto-ingest-context.py"),
                "subagentStop": ("validate-stop.py", "lint-okf.py")},
    "gemini": {"SessionStart": ("auto-ingest.py",),
               "BeforeAgent": ("inject-auto-ingest-context.py",),
               "AfterAgent": ("inject-auto-ingest-context.py", "lint-okf.py")},
}.items():
    for _event, _names in _events.items():
        RETIRED[_provider][_event] = (*RETIRED[_provider].get(_event, ()), *_names)


def legacy_commands(provider, filename):
    return template_commands(provider, filename)


def literal_output_command(command, provider, field):
    """Recognize only known POSIX output fields without evaluation/sinks."""
    posix_field = field == "bash" or (field == "command" and (provider == "codex" or os.name == "posix"))
    if not posix_field:
        return False
    if any(character in command for character in "$`;&|<>(){}\r\n"):
        return False
    try:
        arguments = shlex.split(command)
    except ValueError:
        return False
    return bool(arguments) and arguments[0] in {"echo", "printf"}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def classify(handler, provider, event, directory):
    """Return an exact owned filename, None for unowned, or refuse ambiguity."""
    names = set(DESIRED[provider].get(event, ())) | set(RETIRED[provider].get(event, ()))
    keys = ("command", "commandWindows") if provider == "codex" else ("bash", "powershell") if provider == "copilot" else ("command",)
    for key in keys:
        if key in handler and not isinstance(handler[key], str):
            raise ValueError("Hook command must be a string")
    def admit(filename):
        executable_fields = {"command", "commandWindows", "bash", "powershell"}
        if set(handler) & (executable_fields - set(keys)) or handler.get("type", "command") != "command":
            raise ValueError(f"Ambiguous {provider} hook ownership at {event}; unsupported executable override")
        return filename

    for filename in names:
        legacy = legacy_commands(provider, filename)
        if all(handler.get(key) == value for key, value in legacy.items()):
            return admit(filename)
        # A bash-only old provider config is an explicitly maintained fixture
        # shape, provided it has no alternate executable override.
        if provider == "copilot" and handler.get("bash") == legacy["bash"] and "powershell" not in handler and "command" not in handler:
            return admit(filename)
        script = str(directory / filename)
        command = handler.get(keys[0], "")
        arguments = trusted_posix_arguments(command)
        python = arguments[0] if arguments and arguments[4] == script else None
        if provider == "gemini" and os.name == "nt":
            prefix, separator, _ = command.partition(" -I -S -B ")
            if (separator and prefix.startswith('"') and prefix.endswith('"')
                    and command == serialize_trusted_launch(prefix[1:-1], script, "native", windows=True,
                                                            extra=hook_arguments(filename, provider))):
                python = prefix[1:-1]
        if python:
            shells = ("posix", "windows") if provider == "codex" else ("posix", "powershell") if provider == "copilot" else ("native",)
            if all(handler.get(key) == serialize_trusted_launch(python, script, shell, windows=os.name == "nt", extra=hook_arguments(filename, provider)) for key, shell in zip(keys, shells)):
                return admit(filename)
        # Mentioning our exact home path with unknown executable behavior is
        # neither ownership proof nor permission to delete that behavior.
        markers = (script, f"~/.{provider}/hooks/{filename}", f"$HOME/.{provider}/hooks/scripts/{filename}", f"%USERPROFILE%\\.{provider}\\hooks\\{filename}")
        if any(marker in handler.get(key, "") and not literal_output_command(handler.get(key, ""), provider, key) for key in keys for marker in markers):
            raise ValueError(f"Ambiguous {provider} hook ownership at {event}; review commands before retrying")
    return None


def reconcile(current, maintained, provider, directory):
    result = copy.deepcopy(current)
    disabled = {}
    # Preserve explicit disable intent for retained handlers.
    for event in set(DESIRED[provider]) | set(RETIRED[provider]):
        entries = current.get(event, [])
        for entry in entries:
            for handler in ([entry] if provider == "copilot" else entry["hooks"]):
                name = classify(handler, provider, event, directory)
                if name:
                    intent = {key: value for obj in (entry, handler) for key, value in obj.items() if (key == "enabled" and value is False) or (key == "disabled" and value is True)}
                    disabled.setdefault(name, {}).update(intent)
    for event in dict.fromkeys((*maintained, *RETIRED[provider])):
        if provider == "gemini" and event == "disabled":
            result.setdefault(event, copy.deepcopy(maintained[event]))
            continue
        entries = current.get(event, [])
        preserved = []
        for entry in entries:
            if provider == "copilot":
                if classify(entry, provider, event, directory) is None:
                    preserved.append(copy.deepcopy(entry))
            else:
                remaining = [copy.deepcopy(handler) for handler in entry["hooks"] if classify(handler, provider, event, directory) is None]
                if remaining or not entry["hooks"]:
                    preserved.append({**copy.deepcopy(entry), "hooks": remaining})
        replacements = copy.deepcopy(maintained.get(event, []))
        for entry in replacements:
            for handler in ([entry] if provider == "copilot" else entry["hooks"]):
                name = classify(handler, provider, event, directory)
                if name:
                    handler.update(disabled.get(name, {}))
        if event in current or replacements:
            result[event] = [*preserved, *replacements]
    return result


def _check_ancestor_links(ancestor: Path, message: str) -> None:
    while ancestor != ancestor.parent:
        system_alias = os.name == "posix" and str(ancestor) in {"/var", "/tmp"} and str(ancestor.resolve()) == "/private" + str(ancestor)
        try:
            info = ancestor.lstat()
        except FileNotFoundError:
            ancestor = ancestor.parent
            continue
        reparse = getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        if (stat.S_ISLNK(info.st_mode) and not system_alias) or reparse:
            raise ValueError(message)
        ancestor = ancestor.parent


def check_parent_directories(home: Path, destination: Path) -> None:
    home = Path(os.path.abspath(home))
    destination = Path(os.path.abspath(destination))
    try:
        relative = destination.relative_to(home)
    except ValueError as exc:
        raise ValueError(f"Destination is outside the install home: {destination}") from exc
    if not relative.parts:
        raise ValueError(f"Destination must be a file below the install home: {destination}")

    _check_ancestor_links(home, "Refusing linked configuration ancestor")

    current = home
    for part in ("", *relative.parts[:-1]):
        if part:
            current /= part
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or (
            getattr(info, "st_file_attributes", 0)
            & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        ):
            raise ValueError(f"Refusing linked configuration directory: {current}")
        if not stat.S_ISDIR(info.st_mode):
            raise ValueError(f"Configuration parent must be a directory: {current}")


@contextmanager
def configuration_lock(destination, check=False):
    """A stable kernel-released lock for cooperating writers, never a CAS."""
    if check:
        yield
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    path = destination.with_name(destination.name + ".install-lock")
    descriptor = os.open(path, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
    locked = False
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or (hasattr(os, "getuid") and (info.st_uid != os.getuid() or info.st_mode & 0o077)):
            raise ValueError("Unsafe provider migration lock")
        try:
            if os.name == "nt":
                import msvcrt
                if info.st_size == 0:
                    os.write(descriptor, b"0")
                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise ValueError("Provider migration is busy; retry after the cooperating writer finishes") from None
        locked = True
        yield
    finally:
        if locked:
            if os.name == "nt":
                import msvcrt
                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def verify_unchanged(destination, existed, content):
    if destination.is_symlink() or destination.exists() != existed:
        raise ValueError("Provider configuration changed during migration; review and retry")
    if existed and destination.read_bytes() != content:
        raise ValueError("Provider configuration changed during migration; review and retry")


# Receipts for repository-owned retired assets at the migration boundary.
# Modified files and runtime logs belong to the user and are preserved.
RETIRED_ASSETS = {
    'codex': {
        'repository-okf.py': '56d21dd4c59676d91c12c748e4ba16f61a79d0f28c3c9991bc137f4bb8924fda',
        'helpers/okf.py': 'e47f1e645bcf9c6882106991dac7137c3ea430feff666579f24edfbb61c83f3b',
        'helpers/okf_audit.py': '66c43ec59482b363358155b4d1fe27ce7720b231632e8064b1dee5c1c880fc43',
        'helpers/common.py': '5c4a4b1131feb3723624da7049e2fee8137ccd093f78c16dff677578a2adc40e',
        'helpers/audit.py': 'ccc58956b61edb5e6bb4914ed90326c0fedc565fd3732d4c6edccac6136f9f87',
        'tool-guard.py': 'd0d302d31d64979a09feb07055a4a4e25fe01b5a899c394d63c67541724c907a',
        'helpers/tool_guard_policy.py': '3070fc058325b661fb4fd0c60bbc0b4ea9317910a90f4917c01059cd542c2b66',
        'hooks-diagnostics.py': '411f144f7bc4d4e21619c1b37e158eba3b753bd6d623962bedcdfe947e65ec44',
        'helpers/scan_types.py': '19f69ccb6d3268d9c43c353b86c0898d75994c1bf1279a544eed52dbac2bfe59',
        'helpers/scan_reporting.py': '0b3d355f49f49d22ac8340e644635c7ad7306af59c22215ace7e42c5b94e1c28',
        'helpers/scan_allowlist.py': '370485db39a1ceccee1bfdf078ef21b490f778b5e5e8644dab644c2984fcbe43',
        'helpers/scan_stream.py': '631b9d0b3f3b9389be6de37843f941c35950256f0c7b9c55fd5a874fbd4abf31',
        'helpers/scan_git.py': '5512a1a5c39ac8e3d221f203514f35c27f6c466b9e76beb71ab8aaf8419d7dcb',
        'helpers/scan_audit.py': '501f7dc6d5705538672642061835f9d1b95a35b2c69f1b73ba29d9934bc15450',
        'helpers/scan_native_file.py': '1c07697a5020bed461b41f3c0015c7dc798fc8f5c62941af60947c003ea4adf8',
        'helpers/scan_native_process.py': 'ed68b76b0021e2514ffd0822eba2a463e1bfb459ab707d47a4161c42e909bbc1',
        'helpers/scan_engine.py': '2f75e639211905e25650af46959512e49ac2abb338aa248ffeb74b81d43570d1',
        'scan-status.py': '126de1936d82b294e15306d99ab1a35e312d9d55e239c5941d6266ef96cf84f3',
        'scan-secrets.py': 'ffb680d735f18607b41540bd1a8c0a1bfcf2027d5af7f51eeb04573b69ab865e',
    },
    'gemini': {
        'auto-ingest.py': 'd46ec00c738e03bc55417a66b97b85658d429737a484462a940af0b1cb374f9b',
        'inject-auto-ingest-context.py': '8ea94475dc185ad5b95380faf81d4573928e6c3e0f0905ffb764dbc4e709aeed',
        'lint-okf.py': '2bb08460c8a33d832cbdab5574616e2ceb8060aa592dc11b7528fdb9d980faa6',
        'helpers/source_ingest.py': 'ada92fbadfa7b5500eca61ecad63e9bf3d5d4c5f5afe7b5c7eaee101884e1a82',
        'helpers/okf.py': 'e47f1e645bcf9c6882106991dac7137c3ea430feff666579f24edfbb61c83f3b',
        'helpers/okf_audit.py': '66c43ec59482b363358155b4d1fe27ce7720b231632e8064b1dee5c1c880fc43',
        'send-event.py': '22837f6bec97d3f3aad055213de292b5386a4473ccab17653d84643bfab40351',
        'tool-guard.py': '522f1158c90b74876725162695b98b08f95530e0600dd27ab2f6daf768313efc',
        'helpers/tool_guard_policy.py': '3070fc058325b661fb4fd0c60bbc0b4ea9317910a90f4917c01059cd542c2b66',
        'hooks-diagnostics.py': 'ae494bfdbc44f894ea4a482e80e5a7a6707e2986da5818039530dbb25c99d086',
        'helpers/scan_types.py': '19f69ccb6d3268d9c43c353b86c0898d75994c1bf1279a544eed52dbac2bfe59',
        'helpers/scan_reporting.py': '0b3d355f49f49d22ac8340e644635c7ad7306af59c22215ace7e42c5b94e1c28',
        'helpers/scan_allowlist.py': '370485db39a1ceccee1bfdf078ef21b490f778b5e5e8644dab644c2984fcbe43',
        'helpers/scan_stream.py': '631b9d0b3f3b9389be6de37843f941c35950256f0c7b9c55fd5a874fbd4abf31',
        'helpers/scan_git.py': '5512a1a5c39ac8e3d221f203514f35c27f6c466b9e76beb71ab8aaf8419d7dcb',
        'helpers/scan_audit.py': '501f7dc6d5705538672642061835f9d1b95a35b2c69f1b73ba29d9934bc15450',
        'helpers/scan_native_file.py': '1c07697a5020bed461b41f3c0015c7dc798fc8f5c62941af60947c003ea4adf8',
        'helpers/scan_native_process.py': 'ed68b76b0021e2514ffd0822eba2a463e1bfb459ab707d47a4161c42e909bbc1',
        'helpers/scan_engine.py': '2f75e639211905e25650af46959512e49ac2abb338aa248ffeb74b81d43570d1',
        'scan-status.py': '0fc85f1e234497eca04264bbaa0a7bf2008fe6c3c6cf26ad910558324fb16251',
        'scan-secrets.py': '4e485f459f86d172771522e99172053222aef987e1fcc0546d7aeca53133a606',
    },
    'copilot': {
        'send-event.py': '22837f6bec97d3f3aad055213de292b5386a4473ccab17653d84643bfab40351',
        'tool-guard.py': 'b7b4b415e986bf43b8725508f6d748e7063b7601eef4a1cd51fba4634e3b249a',
        'helpers/tool_guard_policy.py': '3070fc058325b661fb4fd0c60bbc0b4ea9317910a90f4917c01059cd542c2b66',
        'hooks-diagnostics.py': 'cf8a38f73e5286e07fe84c04a9430b9df6b988ee1c9197012d618bf052ca9c3a',
        'helpers/scan_types.py': '19f69ccb6d3268d9c43c353b86c0898d75994c1bf1279a544eed52dbac2bfe59',
        'helpers/scan_reporting.py': '0b3d355f49f49d22ac8340e644635c7ad7306af59c22215ace7e42c5b94e1c28',
        'helpers/scan_allowlist.py': '370485db39a1ceccee1bfdf078ef21b490f778b5e5e8644dab644c2984fcbe43',
        'helpers/scan_stream.py': '631b9d0b3f3b9389be6de37843f941c35950256f0c7b9c55fd5a874fbd4abf31',
        'helpers/scan_git.py': '5512a1a5c39ac8e3d221f203514f35c27f6c466b9e76beb71ab8aaf8419d7dcb',
        'helpers/scan_audit.py': '501f7dc6d5705538672642061835f9d1b95a35b2c69f1b73ba29d9934bc15450',
        'helpers/scan_native_file.py': '1c07697a5020bed461b41f3c0015c7dc798fc8f5c62941af60947c003ea4adf8',
        'helpers/scan_native_process.py': 'ed68b76b0021e2514ffd0822eba2a463e1bfb459ab707d47a4161c42e909bbc1',
        'helpers/scan_engine.py': '2f75e639211905e25650af46959512e49ac2abb338aa248ffeb74b81d43570d1',
        'scan-status.py': 'b85e4efd4d159746f0ff37b3c2800638a5d39173fa3031aa104e87f0677635da',
        'scan-secrets.py': '8547fbf3855c9f47ed98d52fe365c230edaacb53752d5f2a98cdce8d0ef89849',
    },
}


def retire_assets(provider, directory):
    for name, expected in RETIRED_ASSETS.get(provider, {}).items():
        path = directory / name
        try:
            check_parent_directories(directory, path)
        except ValueError:
            print("Preserved retired hook asset below a linked directory for manual review", file=sys.stderr)
            continue
        try:
            info = path.lstat()
        except FileNotFoundError:
            continue
        if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
                or getattr(info, "st_file_attributes", 0) & 0x400):
            print("Preserved linked or non-file retired hook asset for manual review", file=sys.stderr)
            continue
        if info.st_size > 2 * 1024 * 1024:
            print("Preserved oversized retired hook asset for manual review", file=sys.stderr)
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() == expected:
            path.unlink()
        else:
            print("Preserved modified retired hook asset for manual review", file=sys.stderr)
