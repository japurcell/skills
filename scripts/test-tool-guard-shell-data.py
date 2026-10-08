#!/usr/bin/env python3
"""Shell/Python data and execution through the generated public provider seam."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import shlex
import subprocess
import sys
import tempfile
import unittest

from tool_guard_corpus import OPERATIONS, PROVIDERS, Fixture, decision, encode, envelope, fixtures, script_path

ROOT = Path(__file__).resolve().parent.parent


class ShellDataTests(unittest.TestCase):
    def test_literal_delimiters_preserve_data_and_following_execution(self) -> None:
        operation = OPERATIONS['force_push_protected_branch']
        literals = [repr(operation + '\\'), repr('\\' * 257 + operation),
                    json.dumps(operation + '\\' * 2),
                    '"""' + operation + '\\' + '"""' + 'tail"""',
                    "'''" + operation + '\\' + "'''" + "tail'''",
                    repr("quote'" + operation + '"quote')]
        for literal in literals:
            source = 'from pathlib import Path;Path("example.txt").write_text(' + literal + ')'
            self.check('python3 -c ' + shlex.quote(source), 'allow')
            self.check('python3 -c ' + shlex.quote(source + ';import os;os.system(' + repr(operation) + ')'), 'deny')
        self.check("rg '" + operation + "\\$(ignored)' docs", 'allow')
        self.check("rg '" + operation + "' docs; " + operation, 'deny')
        for literal in ("'unfinished\\", '"""unfinished\\"""', "'''unfinished\\'''"):
            self.check('python3 -c ' + shlex.quote('value=' + literal), 'deny', mode='warn')

    def test_missing_or_invalid_local_policy_denies_in_block_and_warn_modes(self) -> None:
        fixture = Fixture('delivery', 'Bash', {'command': 'echo safe'}, 'allow', 'allow', 'delivery', 'local helper boundary')
        for provider in PROVIDERS:
            for invalid in (None, 'raise RuntimeError("invalid local policy")\n'):
                for mode in ('block', 'warn'):
                    with self.subTest(provider=provider, invalid=invalid, mode=mode), tempfile.TemporaryDirectory() as temporary:
                        directory = Path(temporary)
                        script = directory / 'tool-guard.py'
                        shutil.copy2(script_path(ROOT, provider), script)
                        helpers = directory / 'helpers'
                        helpers.mkdir()
                        for filename in ('common.py', 'audit.py'):
                            source = script_path(ROOT, provider).parent / 'helpers' / filename
                            if source.exists():
                                shutil.copy2(source, helpers / filename)
                        if invalid is not None:
                            (helpers / 'tool_guard_policy.py').write_text(invalid)
                        env = {**os.environ, 'GUARD_MODE': mode, 'TOOL_GUARD_LOG_DIR': str(directory / 'logs'),
                               'AUDIT_LOG': str(directory / 'audit.log')}
                        env.pop('SKIP_TOOL_GUARD', None)
                        env.pop('TOOL_GUARD_ALLOWLIST', None)
                        result = subprocess.run([sys.executable, '-I', '-S', '-B', str(script)],
                                                input=encode(envelope(provider, fixture)), capture_output=True, env=env, timeout=5)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertEqual(decision(provider, json.loads(result.stdout)), 'deny', result.stdout)

    def check(self, command: str, expected: str, *, mode: str = 'block') -> None:
        fixture = Fixture('shell-control', 'Bash', {'command': command}, expected, expected, 'shell', 'public control')
        for provider in PROVIDERS:
            with self.subTest(provider=provider, command=command[:80]), tempfile.TemporaryDirectory() as directory:
                env = {**os.environ, 'GUARD_MODE': mode, 'TOOL_GUARD_LOG_DIR': directory}
                env.pop('SKIP_TOOL_GUARD', None)
                env.pop('TOOL_GUARD_ALLOWLIST', None)
                result = subprocess.run([sys.executable, '-I', '-S', '-B', str(script_path(ROOT, provider))],
                                        input=encode(envelope(provider, fixture)), capture_output=True, env=env, timeout=5)
                self.assertEqual(result.returncode, 0, result.stderr)
                response = json.loads(result.stdout)
                if expected == 'warn':
                    native = response.get('permissionDecision') or response.get('decision') or response.get('hookSpecificOutput', {}).get('permissionDecision')
                    if provider == 'codex' and set(response) == {'systemMessage'}:
                        native = 'allow'
                    self.assertEqual(native, 'allow', result.stdout)
                    self.assertIn('Tool Guardian warning', json.dumps(response))
                else:
                    self.assertEqual(decision(provider, response), expected, result.stdout)

    def test_recorded_writers_and_execution_gaps(self) -> None:
        names = {'writer.chars-8787-segments-183', 'writer.lines-120-segments-139', 'danger.substitution',
                 'danger.interpreter-sink', 'survey.json-stdin', 'survey.python-subprocess'}
        for fixture in fixtures():
            if fixture.name in names:
                with self.subTest(fixture=fixture.name):
                    self.check(fixture.value['command'], fixture.candidate)

    def test_search_literals_and_nested_execution(self) -> None:
        operation = OPERATIONS['force_push_protected_branch']
        self.check("rg -n '" + operation + "' docs", 'allow')
        self.check("rg -e '" + operation + "' -- docs", 'allow')
        self.check("rg --regexp='" + operation + "' docs", 'allow')
        self.check("rg -n '$(" + operation + ")' docs", 'allow')
        self.check('rg -n "$(' + operation + ')" docs', 'deny')
        self.check("rg -n '" + operation + "' --pre 'sh -c true' docs", 'deny')
        self.check("rg -n safe docs; " + operation, 'deny')
        self.check("rg -n '" + operation + "' docs " + chr(124) + ' bash', 'deny')
        self.check("rg -n '" + operation + "' docs " + chr(124) + ' cat ' + chr(124) + ' sh', 'deny')

    def test_interpreter_heredoc_is_code_and_survey_target_is_exact(self) -> None:
        operation = OPERATIONS['force_push_protected_branch']
        self.check("sh <<'END'\n" + operation + "\nEND", 'deny')
        self.check("sh -c '" + operation + "'", 'deny')
        self.check("bash -lc '" + operation + "'", 'deny')
        self.check("eval '" + operation + "'", 'deny')
        self.check('eval "$BODY"', 'deny', mode='warn')
        body = json.dumps({'tool_name': 'Bash', 'tool_input': {'command': operation}})
        self.check("python3 .codex/hooks/tool-guard.py <<'J'SON\n" + body + "\nJSON", 'allow')
        self.check("python3 other/tool-guard.py <<'JSON'\n" + body + "\nJSON", 'deny')
        self.check("python3 .codex/hooks/tool-guard.py <<JSON\n$(" + operation + ")\nJSON", 'deny')

    def test_sink_aliases_concatenations_and_unresolved_arguments(self) -> None:
        operation = OPERATIONS['force_push_protected_branch']
        self.check('python3 -c ' + repr('import os as process; process.system(' + repr(operation[:9]) + '+' + repr(operation[9:]) + ')'), 'deny')
        self.check('python3 -c ' + repr('import os; os.system(dynamic)'), 'deny', mode='warn')
        self.check('python3 -c ' + repr('import os; value = f"{os.system(' + repr(operation) + ')}"'), 'deny')
        self.check('python3 -c ' + repr('from os import system as execute; execute(' + repr(operation[:9]) + '+' + repr(operation[9:]) + ')'), 'deny')
        self.check('python3 -c ' + repr('if flag:\n import os as runner\n runner.system(' + repr(operation[:9]) + '+' + repr(operation[9:]) + ')'), 'deny')
        self.check('python3 -c ' + repr('import os as runner; runner = unknown; runner.system(dynamic)'), 'deny', mode='warn')
        self.check('python3 -c "$BODY"', 'deny', mode='warn')
        self.check('{ python3 -c ' + repr('import os; os.system(' + repr(operation[:9]) + '+' + repr(operation[9:]) + ')') + '; }', 'deny')
        self.check('python3 -c ' + repr('__import__("os").system(' + repr(operation[:9]) + '+' + repr(operation[9:]) + ')'), 'deny')
        self.check('python3 -c ' + repr('__import__("os").system(dynamic)'), 'deny', mode='warn')
        self.check('env python3 -c ' + repr('import os; os.system(' + repr(operation[:9]) + '+' + repr(operation[9:]) + ')'), 'deny')
        self.check('env python3 -I -c ' + repr('import os; os.system(' + repr(operation[:9]) + '+' + repr(operation[9:]) + ')'), 'deny')
        for flags in ('-Wignore', '-X dev', '-W ignore'):
            self.check('python3 ' + flags + ' -c ' + repr('import os; os.system(' + repr(operation[:9]) + '+' + repr(operation[9:]) + ')'), 'deny')
        self.check("bash --noprofile -c '" + operation + "'", 'deny')
        self.check("sh -e -c '" + operation + "'", 'deny')
        glued = operation.replace('git', 'g"it"').replace('push', 'p"ush"')
        self.check('bash -e -c ' + repr(glued), 'deny')
        self.check('python3.11 -c ' + repr('import os; os.system(' + repr(operation[:9]) + '+' + repr(operation[9:]) + ')'), 'deny')

    def test_multiple_and_overridden_heredocs_remain_strict(self) -> None:
        operation = OPERATIONS['force_push_protected_branch']
        self.check("sh <<'FIRST' <<'SECOND'\nsafe\nFIRST\n" + operation + "\nSECOND", 'deny')
        self.check("python3 .codex/hooks/tool-guard.py <<'JSON' </dev/null\n" + json.dumps({'command': operation}) + "\nJSON", 'deny')
        self.check("python3 -c " + repr('import os; os.system(' + repr(operation[:9]) + '+' + repr(operation[9:]) + ')') + " <<'IGNORED'\nsafe\nIGNORED", 'deny')

    def test_unsupported_writer_constructs_never_mask_part_of_source(self) -> None:
        operation = OPERATIONS['force_push_protected_branch']
        writers = [fixture.value['command'] for fixture in fixtures() if fixture.name.startswith('writer.')]
        for writer in writers:
            self.check(writer + '\n' + operation, 'deny')
        small = "from pathlib import Path\np = Path('example.txt')\np.write_text(" + repr(operation) + ")\n"
        self.check("python3 - <<'PY'\n" + small + 'unsupported()\nPY', 'deny')
        self.check("python3 - <<'PY'\n" + small.replace('p.write_text(', 'p.write_text(unsupported(), ') + '\nPY', 'deny')
        self.check("python3 - <<'PY'\n" + small + 'Path = unknown\nPY', 'deny')

    def test_malformed_input_and_parser_limits_deny_in_warn_mode(self) -> None:
        for command in ("python3 - <<'PY'\nsafe", "echo 'unterminated", 'echo $(unfinished',
                        'python3 -c ' + repr('value = ' + '(' * 33 + '0' + ')' * 33)):
            self.check(command, 'deny', mode='warn')

    def test_pipeline_operators_follow_shell_quote_boundaries(self) -> None:
        operation = OPERATIONS['download_execute_bash']
        self.check("echo '" + operation + "'", 'allow')
        self.check('echo ' + operation.replace(chr(124), chr(92) + chr(124)), 'allow')
        self.check(operation.replace(chr(124) + ' bash', chr(124) + ' rg -n bash'), 'allow')
        self.check(operation, 'deny')
        self.check(OPERATIONS['download_execute_sh'], 'deny')

    def test_wrapped_pipeline_operations_keep_existing_protection(self) -> None:
        operation = OPERATIONS['download_execute_bash']
        self.check('env ' + operation, 'deny')
        self.check('command ' + operation, 'deny')
        self.check(operation.replace(chr(124) + ' bash', chr(124) + ' env bash'), 'deny')
        self.check(operation.replace(chr(124) + ' bash', chr(124) + ' command bash'), 'deny')
        force = OPERATIONS['force_push_protected_branch']
        self.check("rg -n '" + force + "' docs " + chr(124) + ' env bash', 'deny')
        self.check("rg -n '" + force + "' docs " + chr(124) + ' env cat ' + chr(124) + ' command sh', 'deny')

    def test_installer_pipeline_intermediates_keep_existing_protection(self) -> None:
        for operation in (OPERATIONS['download_execute_bash'], OPERATIONS['download_execute_sh']):
            for intermediary in ('cat', 'tee /tmp/guardian-demo', 'head -c 100000', 'cat ' + chr(124) + ' tee'):
                command = operation.replace(chr(124), chr(124) + ' ' + intermediary + ' ' + chr(124), 1)
                self.check(command, 'deny')
                self.check(command, 'warn', mode='warn')
        self.check("echo '" + OPERATIONS['download_execute_bash'] + "'", 'allow')
        self.check('printf safe ' + chr(124) + ' cat ' + chr(124) + ' bash', 'allow')

    def test_inline_shell_arguments_and_input_remain_inspected(self) -> None:
        operation = OPERATIONS['force_push_protected_branch']
        for launcher in ('sh -c', 'bash -lc'):
            for body, argument in (("exec \"$@\"", operation), ('eval "$1"', shlex.quote(operation)),
                                   ('printf "%s" "$1"', shlex.quote(operation))):
                command = launcher + ' ' + shlex.quote(body) + ' _ ' + argument
                self.check(command, 'deny')
                self.check(command, 'deny' if body.startswith('eval') else 'warn', mode='warn')
            self.check(launcher + ' ' + shlex.quote('exec "$@"') + ' _ printf safe', 'allow')
            self.check(launcher + ' ' + shlex.quote("rg -n '" + operation + "' docs"), 'allow')
        self.check("rg -n '" + operation + "' docs " + chr(124) + " sh -c 'sh'", 'deny')
        self.check(OPERATIONS['download_execute_bash'] + " -c 'true'", 'deny')

    def test_attached_unresolved_python_code_fails_closed(self) -> None:
        for launcher in ('python3', 'python3 -I', 'env python3', 'command python3', 'python3 "$FLAGS"'):
            for operand in ('-c "$BODY"', '-c"$BODY"', '"-c$BODY"'):
                for mode in ('block', 'warn'):
                    self.check(launcher + ' ' + operand, 'deny', mode=mode)
        self.check('python3 -c"print(1)"', 'allow')
        self.check('python3 "-cprint(1)"', 'allow')
        self.check('python3 demo.py "-c$BODY"', 'allow')

    def test_pipeline_nested_consumers_keep_inherited_input_context(self) -> None:
        operation = OPERATIONS['download_execute_bash']
        prefix = operation.rsplit(chr(124), 1)[0] + chr(124) + ' '
        consumers = ["sh -c 'bash'", "sh -c 'exec bash'", "cat " + chr(124) + " sh -c 'bash'",
                     "sh -c 'env bash'", 'sh -c ' + shlex.quote("sh -c 'bash'"),
                     "sh -c 'eval bash'", 'sh -c ' + shlex.quote('python3 -c ' + shlex.quote('import os;os.system("bash")'))]
        commands = [prefix + consumer for consumer in consumers]
        other = OPERATIONS['download_execute_sh'].rsplit(chr(124), 1)[0] + chr(124) + ' '
        commands.append(other + 'python3 -c ' + shlex.quote('import os;os.system("sh")'))
        commands.append(other + "bash -c 'exec sh'")
        producer = operation.rsplit(chr(124), 1)[0].strip()
        commands.append('sh -c ' + shlex.quote(producer) + ' ' + chr(124) + ' bash')
        commands.append('sh -c ' + shlex.quote('eval ' + shlex.quote(producer)) + ' ' + chr(124) + ' bash')
        commands.append('sh -c ' + shlex.quote('rg -n ' + shlex.quote(operation) + ' docs') + ' ' + chr(124) + ' bash')
        sequential_search = 'rg -n ' + shlex.quote(operation) + ' docs; printf safe'
        commands.append('sh -c ' + shlex.quote(sequential_search) + ' ' + chr(124) + ' bash')
        for command in commands:
            self.check(command, 'deny')
            self.check(command, 'warn', mode='warn')
        controls = [prefix + "sh -c 'printf safe'", other + 'python3 -c ' + shlex.quote('print("safe")'),
                    prefix + 'sh -c ' + shlex.quote("eval 'printf safe'")]
        search = 'rg -n ' + shlex.quote(operation) + ' docs'
        controls.append(prefix + 'sh -c ' + shlex.quote(search))
        controls.append(prefix + 'sh -c ' + shlex.quote(sequential_search))
        controls.append(prefix + 'sh -c ' + shlex.quote('eval ' + shlex.quote(search)))
        writer = 'from pathlib import Path;Path("example.txt").write_text(' + repr(operation) + ')'
        controls.append(prefix + 'sh -c ' + shlex.quote('python3 -c ' + shlex.quote(writer)))
        controls.append('sh -c ' + shlex.quote('python3 -c ' + shlex.quote(writer) + '; printf safe') + ' ' + chr(124) + ' bash')
        for fixture in fixtures():
            if fixture.name in {'survey.json-stdin', 'survey.python-subprocess'}:
                controls.append(prefix + 'sh -c ' + shlex.quote(fixture.value['command']))
        for command in controls:
            for mode in ('block', 'warn'):
                self.check(command, 'allow', mode=mode)

    def test_sql_interpreter_arguments_keep_policy(self) -> None:
        self.check("sqlite3 demo.db '" + OPERATIONS['delete_without_where'] + "'", 'deny')
        self.check("psql -c '" + OPERATIONS['drop_table'] + "'", 'deny')
        self.check('psql -c "$QUERY"', 'deny', mode='warn')
        self.check("sqlite3 demo.db 'select 1'", 'allow')

    def test_windows_launchers_receive_no_posix_data_exemption(self) -> None:
        operation = OPERATIONS['force_push_protected_branch']
        self.check("rg.exe -n '" + operation + "' docs", 'deny')
        self.check('powershell -Command "' + operation + '"', 'deny')
        fullwidth = ''.join(chr(ord(char) + 65248) for char in 'rg')
        self.check(fullwidth + " -n '" + operation + "' docs", 'deny')
        self.check("arbitrary/rg -n '" + operation + "' docs", 'deny')
        writer = "from pathlib import Path\np=Path('example.txt')\np.write_text(" + repr(operation) + ")"
        self.check('arbitrary/python3 -c ' + repr(writer), 'deny')
        self.check('env python3 -c ' + repr(writer), 'deny')


if __name__ == '__main__':
    unittest.main()
