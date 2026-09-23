#!/usr/bin/env python3
"""Public envelope checks for security hook messages."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


class SecurityBannerTests(unittest.TestCase):
    def invoke(self, provider: str, mode: str, tool: str, value: object) -> tuple[dict, list[dict]]:
        path = ROOT / ('.codex/hooks/tool-guard.py' if provider == 'codex' else f'.{provider}/hooks/scripts/tool-guard.py')
        with tempfile.TemporaryDirectory() as temporary:
            log = Path(temporary) / ('gemini-log' if provider == 'gemini' else 'guard.log')
            log_file = log / 'guard.log' if provider == 'gemini' else log
            payload = {'tool_name': tool, 'tool_input': value} if provider != 'copilot' else {'toolName': tool, 'toolArgs': value}
            if provider == 'codex':
                payload['hook_event_name'] = 'PreToolUse'
            result = subprocess.run([sys.executable, '-I', '-S', '-B', str(path)], input=json.dumps(payload), text=True, capture_output=True,
                                    env={**os.environ, 'GUARD_MODE': mode, 'TOOL_GUARD_LOG_DIR': str(log)}, timeout=5)
            self.assertEqual(result.returncode, 0, result.stderr)
            rows = [json.loads(line[line.find('{'):]) for line in log_file.read_text().splitlines()] if log_file.exists() else []
            return json.loads(result.stdout), rows

    def test_block_and_warning_excerpt(self) -> None:
        operation = 'git push' + ' --force origin main'
        secret = 'sk-' + 'a' * 30
        command = f'echo prefix --token={secret}; {operation}'
        for provider in ('copilot', 'gemini', 'codex'):
            with self.subTest(provider=provider):
                blocked, rows = self.invoke(provider, 'block', 'Bash', command)
                output = json.dumps(blocked)
                self.assertIn('Tool Guardian blocked', output)
                self.assertIn('Action:', output)
                self.assertNotIn(secret, output)
                self.assertNotIn(secret, json.dumps(rows))
                self.assertLessEqual(len(rows[-1]['excerpt']), 160)
                self.assertTrue(rows[-1]['excerpt'].startswith(operation))
                self.assertIn(rows[-1]['excerpt'], output)
                warned, _ = self.invoke(provider, 'warn', 'Bash', command)
                self.assertIn('Tool Guardian warning', json.dumps(warned))

    def test_excerpt_is_bounded_and_fallback_is_safe(self) -> None:
        operation = 'git push' + ' --force origin main'
        secret = 'ghp_' + 'A' * 40
        command = f'{"x" * 200} {operation} --api-key={secret}'
        for provider in ('copilot', 'gemini', 'codex'):
            with self.subTest(provider=provider):
                blocked, rows = self.invoke(provider, 'block', 'Bash', command)
                excerpt = rows[-1]['excerpt']
                self.assertEqual(len(excerpt), 160)
                self.assertTrue(excerpt.startswith(operation))
                self.assertNotIn(secret, json.dumps(blocked))
                self.assertNotIn(secret, json.dumps(rows))
                too_long, limit_rows = self.invoke(provider, 'block', 'Bash', 'x' * 33000)
                self.assertIn('command omitted', json.dumps(too_long))
                self.assertEqual(limit_rows[-1]['excerpt'], 'command omitted')

    def test_quoted_credential_redacts_complete_value(self) -> None:
        operation = 'git push' + ' --force origin main'
        secret = 'alpha' + ' bravo'
        for prefix in ('--password=', 'API_KEY='):
            for quote in ("'", '"'):
                command = f'{operation} {prefix}{quote}{secret}{quote}'
                for provider in ('copilot', 'gemini', 'codex'):
                    with self.subTest(provider=provider, quote=quote, prefix=prefix):
                        blocked, rows = self.invoke(provider, 'block', 'Bash', command)
                        output = json.dumps(blocked)
                        logged = json.dumps(rows)
                        self.assertTrue(rows[-1]['excerpt'].startswith(operation))
                        self.assertIn(f'{prefix}[REDACTED]', rows[-1]['excerpt'])
                        self.assertNotIn('alpha', output + logged)
                        self.assertNotIn('bravo', output + logged)
                        self.assertIn(rows[-1]['excerpt'], output)
                        self.assertLessEqual(len(rows[-1]['excerpt']), 160)

    def test_json_credential_field_is_redacted_from_banner_and_log(self) -> None:
        operation = 'git push' + ' --force origin main'
        placeholder = 'fake' + '-credential-value'
        tool_input = {'command': operation, 'password': placeholder}
        for provider in ('copilot', 'gemini', 'codex'):
            with self.subTest(provider=provider):
                blocked, rows = self.invoke(provider, 'block', 'Bash', tool_input)
                excerpt = rows[-1]['excerpt']
                self.assertTrue(excerpt.startswith(operation))
                self.assertIn('"password":"[REDACTED]"', excerpt)
                self.assertNotIn(placeholder, json.dumps(blocked))
                self.assertNotIn(placeholder, json.dumps(rows))
                reason = (blocked.get('permissionDecisionReason') or blocked.get('reason')
                          or blocked.get('hookSpecificOutput', {}).get('permissionDecisionReason'))
                self.assertIn(f'Action: {excerpt}.', reason)
                self.assertLessEqual(len(excerpt), 160)

    def test_structured_action(self) -> None:
        operation = 'git push' + ' --force origin main'
        for provider in ('copilot', 'gemini', 'codex'):
            with self.subTest(provider=provider):
                blocked, rows = self.invoke(provider, 'block', 'complete_task', {'result': f'check: {operation}'})
                self.assertIn('Action:', json.dumps(blocked))
                self.assertTrue(rows[-1]['excerpt'].startswith(operation))


if __name__ == '__main__':
    unittest.main()
