#!/usr/bin/env python3
"""Native data boundaries through the generated provider stdin/stdout seam."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


def text(*codes: int) -> str:
    return ''.join(map(chr, codes))


FORCE_PUSH = text(103, 105, 116, 32, 112, 117, 115, 104, 32, 45, 45, 102, 111, 114, 99, 101, 32, 111, 114, 105, 103, 105, 110, 32, 109, 97, 105, 110)


class NativeDataTests(unittest.TestCase):
    def invoke(self, provider: str, tool: str, value: object, *, mode: str = 'block', extra: dict | None = None, allowlist: bool = False) -> dict:
        path = ROOT / ('.codex/hooks/tool-guard.py' if provider == 'codex' else f'.{provider}/hooks/scripts/tool-guard.py')
        payload = {'toolName': tool, 'toolArgs': value} if provider == 'copilot' else {'tool_name': tool, 'tool_input': value}
        payload['hook_event_name'] = 'BeforeTool' if provider == 'gemini' else 'PreToolUse'
        payload.update(extra or {})
        with tempfile.TemporaryDirectory() as temporary:
            env = {**os.environ, 'GUARD_MODE': mode, 'TOOL_GUARD_LOG_DIR': str(Path(temporary) / 'guard-log')}
            env.pop('SKIP_TOOL_GUARD', None)
            env.pop('TOOL_GUARD_ALLOWLIST', None)
            if allowlist:
                env['TOOL_GUARD_ALLOWLIST'] = json.dumps([{'tool': tool, 'input': json.dumps(value, ensure_ascii=False, separators=(',', ':'))}])
            result = subprocess.run([sys.executable, '-I', '-S', '-B', str(path)], input=json.dumps(payload),
                                    text=True, capture_output=True, env=env, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def assert_decision(self, response: dict, expected: str) -> None:
        decision = response.get('permissionDecision') or response.get('decision') or response.get('hookSpecificOutput', {}).get('permissionDecision') or ('allow' if response == {} else None)
        self.assertEqual(decision, expected, response)
        if expected == 'allow':
            self.assertNotIn('systemMessage', response)

    def test_codex_patch_body_is_data_and_shell_counterpart_is_denied(self) -> None:
        patch = '*** Begin Patch\n*** Add File: example.sh\n+Example: ' + FORCE_PUSH + '\n*** End Patch'
        self.assert_decision(self.invoke('codex', 'apply_patch', {'command': patch}), 'allow')
        self.assert_decision(self.invoke('codex', 'Bash', {'command': FORCE_PUSH}), 'deny')

    def test_native_write_edit_search_schemas_accept_examples(self) -> None:
        cases = (
            ('copilot', 'create', {'path': 'example.py', 'file_text': FORCE_PUSH}),
            ('copilot', 'edit', {'path': 'example.sh', 'old_str': FORCE_PUSH, 'new_str': FORCE_PUSH}),
            ('copilot', 'grep', {'query': FORCE_PUSH, 'paths': ['docs', 'tests'], 'n': True, 'C': 2}),
            ('copilot', 'rg', {'pattern': FORCE_PUSH, 'paths': 'docs', '-n': True, '-C': 2}),
            ('gemini', 'write_file', {'file_path': 'example.test.py', 'content': FORCE_PUSH}),
            ('gemini', 'replace', {'file_path': 'example.txt', 'instruction': 'Replace example', 'old_string': FORCE_PUSH, 'new_string': FORCE_PUSH, 'allow_multiple': False}),
            ('gemini', 'grep_search', {'pattern': FORCE_PUSH, 'path': '.', 'include': '*.sh'}),
        )
        for provider, tool, value in cases:
            with self.subTest(provider=provider, tool=tool):
                self.assert_decision(self.invoke(provider, tool, value), 'allow')
                shell = 'bash' if provider == 'copilot' else 'run_shell_command'
                self.assert_decision(self.invoke(provider, shell, {'command': FORCE_PUSH}), 'deny')

    def test_unknown_fields_keys_nested_strings_and_aliases_keep_strict_inspection(self) -> None:
        cases = (
            ('copilot', 'create', {'path': 'example.txt', 'file_text': 'safe', 'command': FORCE_PUSH}),
            ('copilot', 'edit', {'path': 'example.txt', 'old_str': 'safe', 'new_str': {'unknown': FORCE_PUSH}}),
            ('copilot', 'grep', {'query': FORCE_PUSH, 'paths': {'unknown': 'docs'}}),
            ('copilot', 'CREATE', {'path': 'example.txt', 'file_text': FORCE_PUSH}),
            ('gemini', 'write_file', {'file_path': 'example.txt', 'content': 'safe', FORCE_PUSH: 'safe'}),
            ('gemini', 'replace', {'file_path': 'example.txt', 'old_string': 'safe', 'new_string': FORCE_PUSH}),
            ('gemini', 'grep_search', {'pattern': FORCE_PUSH, 'head_limit': True}),
            ('codex', 'Write', {'file_path': 'example.txt', 'content': FORCE_PUSH}),
            ('codex', 'write_file', {'file_path': 'example.txt', 'content': FORCE_PUSH}),
            ('copilot', 'create', FORCE_PUSH),
            ('gemini', 'apply_patch', {'command': FORCE_PUSH}),
            ('copilot', 'apply_patch', {'command': '*** Begin Patch\n*** Add File: x\n+Example: ' + FORCE_PUSH + '\n*** End Patch'}),
            ('codex', 'apply_patch', {'command': FORCE_PUSH}),
            ('codex', 'apply_patch', {'command': '*** Begin Patch\n*** Add File: x\n+safe\n*** End Patch', 'nested': {'command': FORCE_PUSH}}),
        )
        for provider, tool, value in cases:
            with self.subTest(provider=provider, tool=tool):
                self.assert_decision(self.invoke(provider, tool, value), 'deny')

    def test_patch_delete_move_sources_keep_operation_protection(self) -> None:
        for provider in ('codex',):
            for source in ('.env', '.git/config', 'config.env', '.env-test', 'backup.git', '.git-old/config'):
                patches = (
                    '*** Begin Patch\n*** Delete File: ' + source + '\n*** End Patch',
                    '*** Begin Patch\n*** Update File: ' + source + '\n*** Move to: example.txt\n@@\n-old\n+new\n*** End Patch',
                )
                for patch in patches:
                    with self.subTest(provider=provider, source=source, patch=patch):
                        self.assert_decision(self.invoke(provider, 'apply_patch', {'command': patch}), 'deny')
            patch = '*** Begin Patch\n*** Delete File: example.txt\n*** Update File: example.py\n*** Move to: moved.py\n@@\n-old\n+Example: ' + FORCE_PUSH + '\n*** End Patch'
            self.assert_decision(self.invoke(provider, 'apply_patch', {'command': patch}), 'allow')
            for source in ('.envrc', '.github', 'ordinary.txt'):
                patch = '*** Begin Patch\n*** Delete File: ' + source + '\n*** End Patch'
                self.assert_decision(self.invoke(provider, 'apply_patch', {'command': patch}), 'allow')

    def test_patch_literal_headers_and_destinations_do_not_execute(self) -> None:
        patch = '*** Begin Patch\n*** Add File: ' + FORCE_PUSH + '\n+*** Delete File: .env\n*** End Patch'
        for provider in ('codex',):
            self.assert_decision(self.invoke(provider, 'apply_patch', {'command': patch}), 'allow')
            self.assert_decision(self.invoke(provider, 'apply_patch', {'command': patch + '\n' + FORCE_PUSH}), 'deny')

    def test_patch_repeated_operation_causes_remain_distinct(self) -> None:
        patch = '*** Begin Patch\n' + '\n'.join('*** Delete File: config' + str(index) + '.env' for index in range(4)) + '\n*** End Patch'
        response = self.invoke('codex', 'apply_patch', {'command': patch})
        self.assert_decision(response, 'deny')
        reason = response['hookSpecificOutput']['permissionDecisionReason']
        self.assertEqual(reason.count('[remove_env_file]'), 1)
        self.assertNotIn('omitted', reason)

    def test_unrecognized_patch_hunk_header_falls_back_to_strict_inspection(self) -> None:
        patch = '*** Begin Patch\n*** Update File: example.txt\n@@invalid\n+Example: ' + FORCE_PUSH + '\n*** End Patch'
        self.assert_decision(self.invoke('codex', 'apply_patch', {'command': patch}), 'deny')

    def test_patch_native_aggregate_maximum_and_first_overflow(self) -> None:
        prefix = '*** Begin Patch\n*** Add File: example.txt\n+'
        suffix = '\n*** End Patch'
        patch = prefix + 'x' * (65536 - len('command') - len(prefix + suffix)) + suffix
        for provider in ('codex',):
            self.assert_decision(self.invoke(provider, 'apply_patch', {'command': patch}), 'allow')
            response = self.invoke(provider, 'apply_patch', {'command': patch.replace('+x', '+xx', 1)}, mode='warn', allowlist=True)
            self.assert_decision(response, 'deny')
            self.assertIn('65537 bytes', json.dumps(response))

    def test_unknown_shape_keeps_original_executable_byte_limit(self) -> None:
        for provider in ('codex', 'copilot', 'gemini'):
            response = self.invoke(provider, 'unknown_tool', {'body': 'x' * 32769}, mode='warn', allowlist=True)
            self.assert_decision(response, 'deny')
            self.assertIn('32768 bytes', json.dumps(response))

    def test_large_native_patch_does_not_spend_shell_segment_budget(self) -> None:
        prefix = '*** Begin Patch\n*** Add File: example.txt\n+'
        suffix = '\n' + '+literal; value\n' * 330 + '*** End Patch'
        patch = prefix + 'x' * (46899 - len(prefix + suffix)) + suffix
        for provider in ('codex',):
            with self.subTest(provider=provider):
                self.assert_decision(self.invoke(provider, 'apply_patch', {'command': patch}), 'allow')

    def test_native_aggregate_byte_maximum_and_first_overflow(self) -> None:
        for provider, tool, path_key, content_key in (('gemini', 'write_file', 'file_path', 'content'),
                                                    ('copilot', 'create', 'path', 'file_text')):
            # The public aggregate includes UTF-8 data, the destination and keys.
            overhead = len((path_key + content_key + 'example.txt').encode('utf-8'))
            length = 65536 - overhead
            for utf8 in (False, True):
                body = 'x' * length if not utf8 else '界' * (length // 3) + 'x' * (length % 3)
                valid = {path_key: 'example.txt', content_key: body}
                self.assert_decision(self.invoke(provider, tool, valid), 'allow')
                overflow = {path_key: 'example.txt', content_key: body + 'x'}
                for mode in ('warn', 'block'):
                    with self.subTest(provider=provider, utf8=utf8, mode=mode):
                        response = self.invoke(provider, tool, overflow, mode=mode, allowlist=True)
                        self.assert_decision(response, 'deny')
                        output = json.dumps(response)
                        self.assertIn('65537 bytes', output)
                        self.assertIn('65536 bytes', output)
                        self.assertNotIn('TOOL_GUARD_ALLOWLIST', output)

    def test_native_structural_overflow_and_encoding_failure_stay_closed(self) -> None:
        for paths, rule in (([0] * 256, 'structured_nodes'), (['docs'] * 128, 'structured_strings')):
            response = self.invoke('copilot', 'grep', {'pattern': 'safe', 'paths': paths}, mode='warn', allowlist=True)
            self.assert_decision(response, 'deny')
            self.assertIn(rule, json.dumps(response))
        response = self.invoke('gemini', 'write_file', {'file_path': 'example.txt', 'content': '\ud800'}, mode='warn', allowlist=True)
        self.assert_decision(response, 'deny')
        self.assertIn('inspection_failure', json.dumps(response))

    def test_provider_input_name_and_argument_precedence_stays_unchanged(self) -> None:
        safe = {'path': 'example.txt', 'file_text': FORCE_PUSH}
        response = self.invoke('copilot', 'create', safe, extra={'tool_name': 'bash', 'tool_input': {'command': FORCE_PUSH}})
        self.assert_decision(response, 'allow')
        response = self.invoke('codex', 'Bash', {'command': FORCE_PUSH}, extra={'toolName': 'apply_patch', 'toolArgs': {'command': 'safe'}})
        self.assert_decision(response, 'deny')
        response = self.invoke('gemini', 'run_shell_command', {'command': FORCE_PUSH}, extra={'toolName': 'write_file', 'toolArgs': {'file_path': 'example.txt', 'content': 'safe'}})
        self.assert_decision(response, 'deny')


if __name__ == '__main__':
    unittest.main()
