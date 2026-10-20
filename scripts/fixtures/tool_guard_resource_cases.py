"""Versioned inert benchmark inputs and reviewed condition contracts.

Historical builders are frozen. Add new case IDs or a new fixture-set version
when payload bytes change; expected outcomes come only from reviewed JSON.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import shlex

from fixtures.tool_guard_vectors import RECENT_NATIVE_PATCH_SIZES, full_capacity_native_patch, sized_native_patch

FIXTURE_SETS = ("historical-v1", "file-operations-v1")
HISTORICAL_TIMING_CASES = (
    'guard.clean',
    'guard.finding',
    'guard.large',
    'guard.failure',
    'guard.patch.bytes-46899',
    'guard.patch.lines-330',
    'guard.patch.lines-124-segments-142',
    'guard.write.actual-newlines',
    'guard.write.escaped-newlines',
    'guard.write.utf8-growth',
    'guard.write.examples.md',
    'guard.write.examples.py',
    'guard.write.examples.test.py',
    'guard.edit.replacement',
    'guard.search.literal',
    'guard.search.shell-literal',
    'guard.writer.chars-8787-segments-183',
    'guard.writer.lines-120-segments-139',
    'guard.survey.json-stdin',
    'guard.survey.python-subprocess',
    'guard.survey.analysis-source',
    'guard.write.english-inflection',
    'guard.search.full-provider-envelope',
    'guard.danger.full-envelope',
    'guard.danger.full-envelope-unknown',
    'guard.danger.recursive_remove_root',
    'guard.danger.recursive_remove_home',
    'guard.danger.recursive_remove_current',
    'guard.danger.recursive_remove_parent',
    'guard.danger.remove_env_file',
    'guard.danger.remove_git_metadata',
    'guard.danger.force_push_protected_branch',
    'guard.danger.hard_reset',
    'guard.danger.forced_git_clean',
    'guard.danger.drop_table',
    'guard.danger.drop_database',
    'guard.danger.truncate_table',
    'guard.danger.delete_without_where',
    'guard.danger.recursive_world_writable',
    'guard.danger.world_writable',
    'guard.danger.download_execute_bash',
    'guard.danger.download_execute_sh',
    'guard.danger.upload_local_data',
    'guard.danger.privileged_command',
    'guard.danger.publish_package',
    'guard.danger.writer-before',
    'guard.danger.writer-after',
    'guard.danger.substitution',
    'guard.danger.interpreter-sink',
    'guard.danger.unicode-normalization',
    'guard.danger.extra-field',
    'guard.danger.malformed-schema',
)
DEFAULT_EXPECTATIONS = Path(__file__).with_name("tool_guard_file_operations_expectations.json")

SHELL_TOOLS = {'copilot': 'bash', 'gemini': 'run_shell_command', 'codex': 'Bash'}


def historical_fixtures(provider: str) -> list[tuple[str, str, object, str]]:
    shell = SHELL_TOOLS[provider]
    cases = [
        ('strict-max', 'X', 'x' * 32766, 'allow'),
        ('strict-overflow', 'X', 'x' * 32767, 'deny'),
        ('strict-utf8-max', 'X', '界' * 10922, 'allow'),
        ('normalized-max', 'X', "'" + '\u0958' * 5460 + 'xxxx' + "'", 'allow'),
        ('normalized-overflow', 'X', "'" + '\u0958' * 5460 + 'xxxxx' + "'", 'deny'),
        ('quoted-max', shell, {'command': "echo '" + 'x' * 32754 + "'"}, 'allow'),
        ('tokens-max', shell, {'command': ' '.join(['x'] * 256)}, 'allow'),
        ('tokens-overflow', shell, {'command': ' '.join(['x'] * 257)}, 'deny'),
        ('commands-max', shell, {'command': ';'.join(['x'] * 128)}, 'allow'),
        ('commands-overflow', shell, {'command': ';'.join(['x'] * 129)}, 'deny'),
        ('quoted-tokens-max', shell, {'command': "echo '" + 'x ' * 255 + "'"}, 'allow'),
        ('quoted-tokens-overflow', shell, {'command': "echo '" + 'x ' * 256 + "'"}, 'deny'),
        ('heredoc-tokens-max', shell, {'command': "cat <<'EOF'\n" + 'x ' * 254 + '\nEOF'}, 'allow'),
        ('heredoc-tokens-overflow', shell, {'command': "cat <<'EOF'\n" + 'x ' * 255 + '\nEOF'}, 'deny'),
        ('structure-nodes-max', 'unknown_tool', [0] * 255, 'allow'),
        ('structure-wide-overflow', 'unknown_tool', [0] * 30000, 'deny'),
        ('substitution-depth-max', shell, {'command': 'echo $(' * 16 + 'x' + ')' * 16}, 'allow'),
        ('substitution-depth-overflow', shell, {'command': 'echo $(' * 17 + 'x' + ')' * 17}, 'deny'),
    ]
    writer = 'from pathlib import Path;Path("x").write_text('
    assignment = 'from pathlib import Path;Path("x").write_text("safe");a='
    for name, source, expected in (
        ('python-syntax-max', writer + '"x"' * 1011 + ')', 'allow'),
        ('python-syntax-overflow', writer + '"x"' * 1012 + ')', 'deny'),
        ('python-literal-token-max', assignment + '"x"' * 1007, 'allow'),
        ('python-literal-token-overflow', assignment + '"x"' * 1008, 'deny'),
        ('python-ast-depth-max', 'x+' * 29 + 'x', 'allow'),
        ('python-ast-depth-overflow', 'x+' * 30 + 'x', 'deny'),
        ('python-decoded-literal', "x='" + '\\u754c' * 2000 + "'", 'allow')):
        cases.append((name, shell, {'command': 'python3 -c ' + shlex.quote(source)}, expected))
    resolved = "a='" + 'x' * 1024 + "';b=a+a;c=b+b;d=c+c;e=d+d;f=e+e"
    cases.extend((('python-resolved-max', shell, {'command': 'python3 -c ' + shlex.quote(resolved)}, 'allow'),
                  ('python-resolved-overflow', shell, {'command': 'python3 -c ' + shlex.quote(resolved + ';g=f+"x"')}, 'deny')))
    if provider in {'copilot', 'gemini'}:
        tool, path_key, body_key = ('create', 'path', 'file_text') if provider == 'copilot' else ('write_file', 'file_path', 'content')
        available = 65536 - len(path_key + body_key + 'example.txt')
        body = '界' * (available // 3) + 'x' * (available % 3)
        cases.extend((('native-max', tool, {path_key: 'example.txt', body_key: body}, 'allow'),
                      ('native-overflow', tool, {path_key: 'example.txt', body_key: body + 'x'}, 'deny')))
    if provider in {'codex', 'copilot'}:
        def patch_value(source: str) -> object:
            return source if provider == 'copilot' else {'command': source}
        key_bytes = 7 if provider == 'codex' else 0
        case_prefix = 'native' if provider == 'codex' else 'patch'
        patch = full_capacity_native_patch(key_bytes=key_bytes)
        high_line_patch = full_capacity_native_patch(key_bytes=key_bytes, high_lines=130000)
        path = '\ufdfa' * 496 + 'x' * 16
        operations = '*** Begin Patch\n*** Delete File: ' + path + '\n*** Delete File: ' + path + '\n*** End Patch'
        cases.extend(((case_prefix + '-max', 'apply_patch', patch_value(patch), 'allow'),
                      (case_prefix + '-overflow', 'apply_patch', patch_value(patch.replace('+x', '+xx', 1)), 'deny'),
                      (case_prefix + '-high-line-max', 'apply_patch', patch_value(high_line_patch), 'allow'),
                      (case_prefix + '-malformed-full-size', 'apply_patch', patch_value(patch[:-1] + '!'), 'deny'),
                      (case_prefix + '-malformed-high-line-full-size', 'apply_patch', patch_value(high_line_patch[:-1] + '!'), 'deny'),
                      ('operation-normalized-max', 'apply_patch', patch_value(operations), 'allow'),
                      ('operation-normalized-overflow', 'apply_patch', patch_value(operations.replace(path + '\n*** End', path + 'x\n*** End')), 'deny')))
        for size in RECENT_NATIVE_PATCH_SIZES:
            cases.append((case_prefix + '-recent-' + str(size), 'apply_patch', patch_value(sized_native_patch(size, files=3)), 'allow'))
    if provider == 'copilot':
        cases.append(('native-wide-paths-overflow', 'grep', {'pattern': 'safe', 'paths': ['docs'] * 30000}, 'deny'))
    return cases


def payload(provider: str, tool: str, value: object) -> bytes:
    event = {'toolName': tool, 'toolArgs': value} if provider == 'copilot' else {'tool_name': tool, 'tool_input': value}
    event['hook_event_name'] = 'BeforeTool' if provider == 'gemini' else 'PreToolUse'
    return json.dumps(event, ensure_ascii=False, separators=(',', ':')).encode('utf-8')



def resource_inputs(provider: str, fixture_set: str):
    if fixture_set not in FIXTURE_SETS:
        raise ValueError("unknown fixture set: " + fixture_set)
    result = [(name, payload(provider, tool, value), "block", "none")
              for name, tool, value, _expected in historical_fixtures(provider)]
    if fixture_set == "file-operations-v1":
        from tool_guard_corpus import file_operation_fixtures, encode, envelope
        result.extend((fixture.name, encode(envelope(provider, fixture)), "block", "none")
                      for fixture in file_operation_fixtures())
        shell = SHELL_TOOLS[provider]
        for mode in ("block", "warn"):
            for label, command in (("clean", "echo safe"), ("finding", "git push --force origin main"),
                                   ("incomplete", " ".join(["x"] * 257))):
                result.append((f"mode.{mode}.{label}", payload(provider, shell, {"command": command}), mode, "none"))
                result.append((f"audit-unavailable.{mode}.{label}", payload(provider, shell, {"command": command}), mode, "audit-unavailable"))
            result.append((f"bootstrap.{mode}", payload(provider, shell, {"command": "echo safe"}), mode, "missing-policy"))
        result.append(("transport.malformed", b"{invalid json\n", "block", "malformed-json"))
    return result


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate expectation key: " + key)
        result[key] = value
    return result


def load_contracts(path: Path, fixture_set: str, section: str, inputs: list[tuple]) -> dict:
    """Validate the complete selected universe before exact-case filtering."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
        if not isinstance(document, dict) or type(document.get("schema_version")) is not int or document["schema_version"] != 1:
            raise ValueError("unsupported expectation schema version")
        contracts = document["fixture_sets"][fixture_set][section]
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("missing or invalid reviewed expectations: " + str(exc)) from exc
    if not isinstance(contracts, dict):
        raise ValueError("invalid expectations case mapping")
    names = [name for name, *_rest in inputs]
    if len(names) != len(set(names)) or set(names) != set(contracts):
        raise ValueError("expectations require complete unique case IDs; missing or unknown cases")
    for name, data, mode, injection in inputs:
        entry = contracts[name]
        if not isinstance(entry, dict) or set(entry) != {"input_sha256", "injection", "baseline", "candidate"}:
            raise ValueError(name + ": invalid expectation entry")
        if entry["input_sha256"] != hashlib.sha256(data).hexdigest():
            raise ValueError(name + ": stale fixture hash")
        if entry["injection"] != injection:
            raise ValueError(name + ": injection mismatch")
        for condition in ("baseline", "candidate"):
            contract = entry[condition]
            if not isinstance(contract, dict) or set(contract) != {"mode", "decision", "audit", "attribution", "record_attribution"}:
                raise ValueError(name + ": invalid condition contract")
            if contract["mode"] != mode or contract["decision"] not in ("allow", "deny"):
                raise ValueError(name + ": mode or decision mismatch")
            audit = contract["audit"]
            if not isinstance(audit, dict) or set(audit) != {"outcome", "event", "records_per_call"}:
                raise ValueError(name + ": invalid audit contract")
            outcome = audit["outcome"]
            if outcome == "written":
                if type(audit["records_per_call"]) is not int or audit["records_per_call"] != 1 or audit["event"] not in ("guard_passed", "threats_detected") or injection not in {"none"}:
                    raise ValueError(name + ": contradictory written audit contract")
                if contract["decision"] == "deny" and audit["event"] != "threats_detected":
                    raise ValueError(name + ": denied call cannot have clean audit")
            elif outcome in ("failed", "not_attempted"):
                if type(audit["records_per_call"]) is not int or audit["records_per_call"] != 0 or audit["event"] is not None:
                    raise ValueError(name + ": contradictory absent audit contract")
                if outcome == "failed" and injection != "audit-unavailable":
                    raise ValueError(name + ": failed audit requires failure injection")
                if outcome == "not_attempted" and injection not in {"malformed-json", "missing-policy"}:
                    raise ValueError(name + ": not_attempted requires transport/bootstrap injection")
            else:
                raise ValueError(name + ": invalid audit outcome")
            record_attrs = contract["record_attribution"]
            if not isinstance(record_attrs, dict):
                raise ValueError(name + ": invalid completed-record attribution")
            if fixture_set != "historical-v1" and outcome == "written":
                if (set(record_attrs) != {"audit_outcome", "enforcement", "security_outcome"}
                        or record_attrs["audit_outcome"] != "written"
                        or record_attrs["enforcement"] != contract["decision"]
                        or record_attrs["security_outcome"] not in ("clean", "findings", "incomplete")):
                    raise ValueError(name + ": contradictory completed-record attribution")
            elif record_attrs:
                raise ValueError(name + ": unexpected completed-record attribution")
            attrs = contract["attribution"]
            if not isinstance(attrs, dict) or any(not isinstance(k, str) or not isinstance(v, str) or not v for k, v in attrs.items()):
                raise ValueError(name + ": invalid attribution")
            if attrs and (attrs.get("enforcement") != contract["decision"] or attrs.get("audit_outcome") != outcome
                          or attrs.get("security_outcome") not in {"clean", "findings", "incomplete"} or not attrs.get("cause")):
                raise ValueError(name + ": contradictory response attribution")
            if outcome == "failed" and (attrs.get("audit_outcome") != "failed" or attrs.get("cause") != "audit_unavailable"):
                raise ValueError(name + ": failed audit requires response attribution")
            if outcome == "not_attempted" and fixture_set != "historical-v1":
                cause = "policy_unavailable" if injection == "missing-policy" else "input_invalid"
                if attrs != {"audit_outcome": "not_attempted", "security_outcome": "incomplete", "enforcement": "deny", "cause": cause}:
                    raise ValueError(name + ": missing transport/bootstrap attribution")
    return contracts


def validate_response(contract: dict, output: dict) -> None:
    rendered = json.dumps(output, ensure_ascii=False)
    for key, value in contract["attribution"].items():
        # Attribution is a bounded semicolon-delimited public response suffix.
        if f"{key}={value};" not in rendered and f"{key}={value}." not in rendered:
            raise ValueError(f"missing required response attribution {key}={value}")


@dataclass(frozen=True)
class ResourceCase:
    name: str
    script: Path
    payload: bytes
    environment: dict[str, str]
    expected_decision: str
    fixture_metadata: dict
