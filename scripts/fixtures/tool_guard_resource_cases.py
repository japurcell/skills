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

FIXTURE_SETS = ("historical-v1", "file-operations-v1", "file-operations-v2")
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
    if fixture_set in {"file-operations-v1", "file-operations-v2"}:
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
    if fixture_set == "file-operations-v2":
        result = [(name, data, mode, "raw-envelope" if name in {"structure-wide-overflow", "native-wide-paths-overflow"} else injection)
                  for name, data, mode, injection in result]
        result.extend(capacity_inputs(provider))
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
        suite = document["fixture_sets"][fixture_set]
        contracts = suite[section]
        if fixture_set == "file-operations-v2":
            validate_partition(suite)
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("missing or invalid reviewed expectations: " + str(exc)) from exc
    if not isinstance(contracts, dict):
        raise ValueError("invalid expectations case mapping")
    names = [name for name, *_rest in inputs]
    if len(names) != len(set(names)) or set(names) != set(contracts):
        raise ValueError("expectations require complete unique case IDs; missing or unknown cases")
    for name, data, mode, injection in inputs:
        entry = contracts[name]
        if (not isinstance(entry, dict) or not {"input_sha256", "injection", "baseline", "candidate"} <= set(entry)
                or set(entry) - {"input_sha256", "injection", "baseline", "candidate", "reader_limits", "structural_markers"}):
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
            if injection == "raw-envelope" or "reader_limits" in entry or "structural_markers" in entry:
                limits = entry.get("reader_limits")
                if (not isinstance(limits, dict) or set(limits) != {"baseline", "candidate"}
                        or any(not isinstance(value, dict) or set(value) != {"max_bytes", "max_markers"}
                               or type(value["max_bytes"]) is not int or value["max_bytes"] <= 0
                               or value["max_markers"] is not None and (type(value["max_markers"]) is not int or value["max_markers"] <= 0)
                               for value in limits.values())):
                    raise ValueError(name + ": missing reviewed reader limits")
                count = raw_structural_size(data)
                if type(entry.get("structural_markers")) is not int or entry["structural_markers"] != count:
                    raise ValueError(name + ": stale structural marker count")
                current = limits[condition]
                exceeded = (len(data) > current["max_bytes"] or current["max_markers"] is not None and count > current["max_markers"])
                if injection == "raw-envelope" and exceeded != (outcome == "not_attempted"):
                    raise ValueError(name + ": reader boundary contract mismatch")
            if outcome == "written":
                if type(audit["records_per_call"]) is not int or audit["records_per_call"] != 1 or audit["event"] not in ("guard_passed", "threats_detected") or injection not in {"none", "raw-envelope"}:
                    raise ValueError(name + ": contradictory written audit contract")
                if contract["decision"] == "deny" and audit["event"] != "threats_detected":
                    raise ValueError(name + ": denied call cannot have clean audit")
            elif outcome in ("failed", "not_attempted"):
                if type(audit["records_per_call"]) is not int or audit["records_per_call"] != 0 or audit["event"] is not None:
                    raise ValueError(name + ": contradictory absent audit contract")
                if outcome == "failed" and injection != "audit-unavailable":
                    raise ValueError(name + ": failed audit requires failure injection")
                if outcome == "not_attempted" and injection not in {"malformed-json", "missing-policy", "raw-envelope"}:
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
            if fixture_set != "historical-v1":
                nonsilent = contract["decision"] == "deny" or outcome != "written" or record_attrs.get("security_outcome") == "findings"
                if nonsilent and set(attrs) != {"audit_outcome", "enforcement", "security_outcome", "cause"}:
                    raise ValueError(name + ": missing complete response attribution")
                if not nonsilent and attrs:
                    raise ValueError(name + ": ordinary clean passes must be silent")
                if attrs and any(attrs.get(key) != value for key, value in record_attrs.items()):
                    raise ValueError(name + ": response and completed-record attribution conflict")
                if outcome == "written":
                    security = record_attrs["security_outcome"]
                    if ((audit["event"] == "guard_passed") != (security == "clean")
                            or security == "clean" and contract["decision"] != "allow"
                            or security == "incomplete" and contract["decision"] != "deny"
                            or security == "findings" and contract["decision"] != ("allow" if mode == "warn" else "deny")):
                        raise ValueError(name + ": audit event, security outcome, and enforcement conflict")
            if outcome == "failed" and (attrs.get("audit_outcome") != "failed" or attrs.get("cause") != "audit_unavailable"):
                raise ValueError(name + ": failed audit requires response attribution")
            if outcome == "not_attempted" and fixture_set != "historical-v1":
                cause = "policy_unavailable" if injection == "missing-policy" else "input_invalid"
                allowed = {cause}
                if "reader_limits" in entry:
                    allowed = {"input_invalid"} if condition == "baseline" else set()
                    limits = entry["reader_limits"][condition]
                    if len(data) > limits["max_bytes"]:
                        allowed.add("raw_input_bytes")
                    if limits["max_markers"] is not None and entry["structural_markers"] > limits["max_markers"]:
                        allowed.add("raw_structural_markers")
                if (set(attrs) != {"audit_outcome", "security_outcome", "enforcement", "cause"}
                        or attrs["audit_outcome"] != "not_attempted" or attrs["security_outcome"] != "incomplete"
                        or attrs["enforcement"] != "deny" or attrs["cause"] not in allowed):
                    raise ValueError(name + ": missing transport/bootstrap attribution")
    return contracts


def validate_response(contract: dict, output: dict, *, provider: str) -> None:
    expected = contract["attribution"]
    if not expected:
        return
    if contract["decision"] == "allow":
        reason = output.get("systemMessage")
    elif provider == "codex":
        reason = output.get("hookSpecificOutput", {}).get("permissionDecisionReason")
    elif provider == "copilot":
        reason = output.get("permissionDecisionReason")
        if reason != output.get("hookSpecificOutput", {}).get("permissionDecisionReason"):
            raise ValueError("contradictory Copilot denial reasons")
    elif provider == "gemini":
        reason = output.get("reason")
    else:
        raise ValueError("unknown attribution provider")
    marker = " security_outcome="
    if not isinstance(reason, str) or reason.count(marker) != 1 or not reason.endswith("."):
        raise ValueError("missing or ambiguous authoritative attribution suffix")
    suffix = "security_outcome=" + reason.partition(marker)[2][:-1]
    fields = [field.partition("=") for field in suffix.split("; ")]
    keys = ("security_outcome", "audit_outcome", "enforcement", "build", "profile", "route", "cause")
    if tuple(field[0] for field in fields) != keys or any(
        not separator or not value or not value.isascii()
        or any(not (char.isalnum() or char in "_.-") for char in value)
        for _key, separator, value in fields
    ):
        raise ValueError("invalid or duplicate authoritative attribution fields")
    actual = {key: value for key, _separator, value in fields}
    for key, value in expected.items():
        if actual.get(key) != value:
            raise ValueError(f"missing required response attribution {key}={value}")


@dataclass(frozen=True)
class ResourceCase:
    name: str
    script: Path
    payload: bytes
    environment: dict[str, str]
    expected_decision: str
    fixture_metadata: dict


# Reviewed 1 MiB capacity universe. Every size remains part of its frozen ID.
def capacity_inputs(provider):
    from tool_guard_corpus import Fixture, encode, envelope, patch
    result = []
    for capacity in (1048576,):
        def native(body):
            if provider == "codex":
                return payload(provider, "apply_patch", {"command": body})
            return payload(provider, "create" if provider == "copilot" else "write_file",
                           {"path": "example.txt", "file_text": body} if provider == "copilot"
                           else {"file_path": "example.txt", "content": body})
        def shell(command):
            fixture = Fixture("probe", "provider_shell", {"command": command}, "deny", "allow", "capacity", "probe")
            return encode(envelope(provider, fixture))
        for extra in (0, 1):
            text = patch(4, size=capacity + extra) if provider == "codex" else "x" * (capacity + extra)
            result.append((f"capacity-{capacity}.native-{'overflow' if extra else 'max'}", native(text), "block", "none"))
        text = patch(4, size=capacity) if provider == "codex" else "x" * capacity
        encoded = native(text).decode()
        encoded = encoded.replace("x", "\\u0078").encode()
        result.append((f"capacity-{capacity}.native-escaped-max", encoded, "block", "none"))
        # High-line patch bodies exercise list/storage cost independently of bytes.
        prefix, suffix = "*** Begin Patch\n*** Add File: example.txt\n", "*** End Patch"
        high = prefix + "+\n" * ((capacity - len(prefix + suffix)) // 2) + suffix
        high = high.replace("+\n", "+" + "x" * (capacity - len(high)) + "\n", 1)
        assert len(high.encode("utf-8")) == capacity
        if provider in {"codex", "copilot"}:
            value = {"command": high} if provider == "codex" else high
            data = payload(provider, "apply_patch", value)
            result.append((f"capacity-{capacity}.patch-high-lines-exact", data, "block", "none"))
        else:
            data = payload(provider, "replace", {"file_path": "example.txt", "old_string": "x" * (capacity // 2),
                                                  "new_string": "y" * (capacity - capacity // 2), "instruction": "Replace exact text"})
            result.append((f"capacity-{capacity}.edit-aggregate", data, "block", "none"))
        unicode_body = "界" * (capacity // 3) + "x" * (capacity % 3)
        if provider == "codex":
            unicode_body = patch(4, size=capacity - 3 * (capacity // 6))
            unicode_body = unicode_body.replace("+safe", "+" + "界" * (capacity // 6) + "safe", 1)
        result.append((f"capacity-{capacity}.native-unicode", native(unicode_body), "block", "none"))
        body = "x" * (capacity - 1) + "\n"
        writer = "cat > example.txt <<'EOF'\n" + body + "EOF"
        result.append((f"capacity-{capacity}.shell-max", shell(writer), "block", "none"))
        result.append((f"capacity-{capacity}.shell-unproved", shell("echo '" + body + "'"), "block", "none"))
        literal = "x" * (capacity - len("example.txtSaved"))
        source = "from pathlib import Path\np=Path('example.txt')\np.write_text(" + repr(literal) + ")\nprint('Saved')\n"
        result.append((f"capacity-{capacity}.python-wrapped", shell("rtk proxy python3 - <<'PY'\n" + source + "PY"), "block", "none"))
        result.append((f"capacity-{capacity}.python-inline", shell("python3 -c " + shlex.quote(source)), "block", "none"))
        raw_limit = 6 * (capacity + 3 * 32768) + 8192
        clean = shell("echo safe").rstrip()
        for extra in (0, 1):
            result.append((f"capacity-{capacity}.raw-interior-{'overflow' if extra else 'max'}",
                           clean[:-1] + b" " * (raw_limit + extra - len(clean)) + b"}", "block", "raw-envelope"))
        text = patch(4, size=capacity).replace("x", '"') if provider == "codex" else '"' * capacity
        result.append((f"capacity-{capacity}.native-quoted-max", native(text), "block", "none"))
        event = json.loads(shell("echo safe"))
        event["unused_metadata"] = ["x"] * capacity
        result.append((f"capacity-{capacity}.envelope-wide", json.dumps(event, separators=(",", ":")).encode(), "block", "none"))
        result.append((f"capacity-{capacity}.shell-source-overflow", shell("x" * (capacity + 32769)), "block", "none"))
        result.append((f"capacity-{capacity}.shell-literal-overflow", shell("cat > example.txt <<'EOF'\n" + "x" * capacity + "\nEOF"), "block", "none"))
        large_source = "from pathlib import Path\np=Path('example.txt')\np.write_text(" + repr(literal + "x") + ")\nprint('Saved')\n"
        result.append((f"capacity-{capacity}.python-constant-overflow", shell("rtk proxy python3 - <<'PY'\n" + large_source + "PY"), "block", "none"))
        unproved = "value=" + repr("x" * (capacity - 32))
        result.append((f"capacity-{capacity}.python-unproved", shell("python3 -c " + shlex.quote(unproved)), "block", "none"))
        for label, command in (("shell-escaped-max", writer), ("python-escaped-max", "rtk proxy python3 - <<'PY'\n" + source + "PY")):
            result.append((f"capacity-{capacity}.{label}", shell(command).decode().replace("x", "\\u0078").encode(), "block", "none"))
        # Dense invalid markers stress bounded collection before json.loads rejects.
        bomb = b'{"x":' + b'"' * (raw_limit - 6) + b'}'
        assert len(bomb) == raw_limit
        result.append((f"capacity-{capacity}.raw-marker-exhaustion", bomb, "block", "malformed-json"))
    return [(name, data, mode, "raw-envelope" if injection != "malformed-json" and (injection == "raw-envelope" or len(data) > 2097152 or name.endswith(".envelope-wide")) else injection)
            for name, data, mode, injection in result]


def raw_structural_size(data):
    """Independent fixture proof from decoded JSON, plus one declared invalid bomb."""
    try:
        value = json.loads(data)
    except ValueError:
        if data.startswith(b'{"x":') and data.endswith(b'}') and data[5:-1].count(b'"') == len(data) - 6 and (len(data) - 6) % 2 == 0:
            return 4 + (len(data) - 6) // 2
        raise ValueError("unsupported invalid structural fixture") from None
    stack, total = [value], 0
    while stack:
        current = stack.pop()
        if isinstance(current, str):
            total += 1
        elif isinstance(current, dict):
            total += 2 + 2 * len(current) + max(0, len(current) - 1)
            stack.extend(current.values())
        elif isinstance(current, list):
            total += 2 + max(0, len(current) - 1)
            stack.extend(current)
    return total


def validate_partition(suite: dict) -> dict:
    """Require the reviewed D14 split, independent of run results and filters."""
    partition = suite.get("throughput_partition")
    if not isinstance(partition, dict) or set(partition) != {"established", "observations"}:
        raise ValueError("missing reviewed throughput partition")
    from tool_guard_corpus import file_operation_fixtures
    established = set(HISTORICAL_TIMING_CASES)
    established.update("guard." + fixture.name for fixture in file_operation_fixtures())
    for mode in ("block", "warn"):
        for label in ("clean", "finding", "incomplete"):
            established.update((f"guard.mode.{mode}.{label}", f"guard.audit-unavailable.{mode}.{label}"))
        established.add(f"guard.bootstrap.{mode}")
    established.add("guard.transport.malformed")
    capacity_labels = ("native-max", "native-overflow", "native-escaped-max", "native-unicode",
                       "shell-max", "shell-unproved", "python-wrapped", "python-inline",
                       "raw-interior-max", "raw-interior-overflow", "native-quoted-max",
                       "envelope-wide", "shell-source-overflow", "shell-literal-overflow",
                       "python-constant-overflow", "python-unproved", "shell-escaped-max",
                       "python-escaped-max", "raw-marker-exhaustion")
    observations = {f"{provider}.guard.capacity-1048576.{label}" for provider in SHELL_TOOLS
                    for label in (*capacity_labels, "edit-aggregate" if provider == "gemini" else "patch-high-lines-exact")}
    expected = {"established": {f"{provider}.{name}" for provider in SHELL_TOOLS for name in established},
                "observations": observations}
    for label, count in (("established", 219), ("observations", 60)):
        names = partition[label]
        if (not isinstance(names, list) or any(not isinstance(name, str) for name in names)
                or len(names) != count or len(set(names)) != count or set(names) != expected[label]):
            raise ValueError("invalid reviewed throughput partition: " + label)
    if set(partition["established"]) & set(partition["observations"]):
        raise ValueError("overlapping throughput partition")
    return partition


def fixture_metadata(entry: dict, condition: str) -> dict:
    result = {"contract": entry[condition], "injection": entry["injection"]}
    if "reader_limits" in entry:
        result.update(reader_limits=entry["reader_limits"][condition],
                      structural_markers=entry["structural_markers"])
    return result
