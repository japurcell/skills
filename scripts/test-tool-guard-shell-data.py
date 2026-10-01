#!/usr/bin/env python3
"""Shell/Python data and execution through the generated public provider seam."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tool_guard_corpus import OPERATIONS, PROVIDERS, Fixture, decision, encode, envelope, fixtures, script_path

ROOT = Path(__file__).resolve().parent.parent


class ShellDataTests(unittest.TestCase):
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
                self.assertEqual(decision(provider, json.loads(result.stdout)), expected, result.stdout)

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
