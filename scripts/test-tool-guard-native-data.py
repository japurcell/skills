#!/usr/bin/env python3
"""Native data boundaries through the generated provider stdin/stdout seam."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from fixtures.tool_guard_vectors import sized_native_patch
from tool_guard_test_support import invoke_guard, native_decision

ROOT = Path(__file__).resolve().parent.parent


def text(*codes: int) -> str:
    return ''.join(map(chr, codes))


FORCE_PUSH = text(103, 105, 116, 32, 112, 117, 115, 104, 32, 45, 45, 102, 111, 114, 99, 101, 32, 111, 114, 105, 103, 105, 110, 32, 109, 97, 105, 110)


class NativeDataTests(unittest.TestCase):
    def invoke(self, provider: str, tool: str, value: object, *, mode: str = 'block', extra: dict | None = None, allowlist: bool = False) -> dict:
        payload = {'toolName': tool, 'toolArgs': value} if provider == 'copilot' else {'tool_name': tool, 'tool_input': value}
        payload['hook_event_name'] = 'BeforeTool' if provider == 'gemini' else 'PreToolUse'
        payload.update(extra or {})
        encoded_allowlist = (
            json.dumps([{'tool': tool, 'input': json.dumps(value, ensure_ascii=False, separators=(',', ':'))}])
            if allowlist else None
        )
        result = invoke_guard(ROOT, provider, json.dumps(payload), mode=mode, allowlist=encoded_allowlist)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def assert_decision(self, response: dict, expected: str) -> None:
        self.assertEqual(native_decision(response), expected, response)
        if expected == 'allow':
            self.assertNotIn('systemMessage', response)

    def test_codex_patch_body_is_data_and_shell_counterpart_is_denied(self) -> None:
        patch = '*** Begin Patch\n*** Add File: example.sh\n+Example: ' + FORCE_PUSH + '\n*** End Patch'
        self.assert_decision(self.invoke('codex', 'apply_patch', {'command': patch}), 'allow')
        self.assert_decision(self.invoke('codex', 'Bash', {'command': FORCE_PUSH}), 'deny')

    def test_copilot_raw_patch_body_is_native_data(self) -> None:
        patch = sized_native_patch(6194, line_count=134)
        self.assert_decision(self.invoke('copilot', 'apply_patch', patch), 'allow')

    def test_copilot_raw_patch_aggregate_maximum_and_first_overflow(self) -> None:
        prefix = '*** Begin Patch\n*** Add File: example.txt\n+'
        suffix = '\n*** End Patch'
        available = 262144 - len((prefix + suffix).encode('utf-8'))
        for utf8 in (False, True):
            body = 'x' * available if not utf8 else '界' * (available // 3) + 'x' * (available % 3)
            patch = prefix + body + suffix
            self.assertEqual(len(patch.encode('utf-8')), 262144)
            self.assert_decision(self.invoke('copilot', 'apply_patch', patch), 'allow')
            for mode in ('block', 'warn'):
                response = self.invoke('copilot', 'apply_patch', prefix + body + 'x' + suffix, mode=mode)
                self.assert_decision(response, 'deny')
                self.assertIn('tool input: 262145 bytes exceeds limit 262144 bytes', json.dumps(response))
                self.assertNotIn('TOOL_GUARD_ALLOWLIST', json.dumps(response))

    def test_copilot_raw_patch_envelope_aliases_and_object_shapes_remain_strict(self) -> None:
        patch = sized_native_patch(6194, line_count=134)
        for value in ({'command': patch}, {'input': patch}, {'patch': patch}, json.dumps({'command': patch})):
            self.assert_decision(self.invoke('copilot', 'apply_patch', value), 'deny')
        for provider in ('codex', 'gemini'):
            self.assert_decision(self.invoke(provider, 'apply_patch', patch), 'deny')
        for tool in ('APPLY_PATCH', 'functions.apply_patch', 'apply-patch'):
            self.assert_decision(self.invoke('copilot', tool, patch), 'deny')
        for payload in ({'tool_name': 'apply_patch', 'toolArgs': patch},
                        {'toolName': 'apply_patch', 'toolInput': patch},
                        {'toolName': 'apply_patch', 'tool_input': patch}):
            result = invoke_guard(ROOT, 'copilot', json.dumps(payload))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assert_decision(json.loads(result.stdout), 'deny')

    def test_copilot_raw_patch_protected_sources_are_inspected(self) -> None:
        for source, rule in (('.env', 'remove_env_file'), ('.git/config', 'remove_git_metadata')):
            patches = ('*** Begin Patch\n*** Delete File: ' + source + '\n*** End Patch',
                       '*** Begin Patch\n*** Update File: ' + source + '\n*** Move to: ordinary.txt\n@@\n-old\n+new\n*** End Patch')
            for patch in patches:
                with self.subTest(source=source, operation=patch.splitlines()[1]):
                    response = self.invoke('copilot', 'apply_patch', patch)
                    self.assert_decision(response, 'deny')
                    self.assertIn(rule, json.dumps(response))

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
        available = 262144 - len(('command' + prefix + suffix).encode('utf-8'))
        for utf8 in (False, True):
            body = 'x' * available if not utf8 else '界' * (available // 3) + 'x' * (available % 3)
            patch = prefix + body + suffix
            self.assertEqual(len(patch.encode('utf-8')) + 7, 262144)
            self.assert_decision(self.invoke('codex', 'apply_patch', {'command': patch}), 'allow')
            for mode in ('block', 'warn'):
                with self.subTest(utf8=utf8, mode=mode):
                    response = self.invoke('codex', 'apply_patch', {'command': prefix + body + 'x' + suffix}, mode=mode)
                    self.assert_decision(response, 'deny')
                    self.assertIn('tool input: 262145 bytes exceeds limit 262144 bytes', json.dumps(response))
                    self.assertNotIn('TOOL_GUARD_ALLOWLIST', json.dumps(response))

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

    def test_historical_segment_dimensions_and_recent_byte_sizes_are_native_data(self) -> None:
        historical = ((22025, 161, 1), (22259, 330, 15), (10903, 228, 5), (11288, 189, 2),
                      (7271, 124, 1), (11022, 209, 1), (20937, 237, 10), (9436, 177, 1),
                      (24727, 523, 1), (9198, 153, 1), (14199, 234, 1), (6194, 134, 1))
        for size, lines, files in historical:
            with self.subTest(size=size, lines=lines, files=files):
                patch = sized_native_patch(size, line_count=lines, files=files)
                self.assertEqual(len(patch.encode('utf-8')), size)
                self.assertEqual(len(patch.splitlines()), lines)
                for provider in ('codex', 'copilot'):
                    value = patch if provider == 'copilot' else {'command': patch}
                    self.assert_decision(self.invoke(provider, 'apply_patch', value), 'allow')
        for size in (77089, 80666, 90127, 99186):
            for files in (1, 3):
                with self.subTest(size=size, files=files):
                    patch = sized_native_patch(size, files=files)
                    self.assertEqual(len(patch.encode('utf-8')), size)
                    for provider in ('codex', 'copilot'):
                        value = patch if provider == 'copilot' else {'command': patch}
                        self.assert_decision(self.invoke(provider, 'apply_patch', value), 'allow')

    def test_patch_capacity_only_applies_to_exact_codex_schema(self) -> None:
        patch = sized_native_patch(6194, line_count=134)
        unsupported = (patch, {'input': patch}, {'patch': patch}, {'command': patch, 'extra': True},
                       {'command': [patch]}, {'command': {'body': patch}}, {'command': 7, 'body': FORCE_PUSH})
        for value in unsupported:
            with self.subTest(shape=type(value).__name__, keys=tuple(value) if isinstance(value, dict) else ()):
                self.assert_decision(self.invoke('codex', 'apply_patch', value), 'deny')
        for provider in ('copilot', 'gemini'):
            self.assert_decision(self.invoke(provider, 'apply_patch', {'command': patch}), 'deny')
        large = sized_native_patch(77089)
        for provider in ('codex', 'copilot', 'gemini'):
            for value in ({'patch': large}, {'command': large, 'extra': True}):
                response = self.invoke(provider, 'apply_patch', value, mode='warn')
                self.assert_decision(response, 'deny')
                self.assertIn('32768 bytes', json.dumps(response))

    def test_malformed_full_size_patch_and_trailing_input_remain_strict(self) -> None:
        patch = sized_native_patch(262137)
        malformed = (patch.replace('*** Begin Patch', '*** Badly Patch', 1),
                     patch.replace('+Documentation', ' Documentation', 1),
                     patch.replace('*** End Patch', '*** Bad Patch'),
                     patch[:-1] + '!', patch + '\n' + FORCE_PUSH)
        for value in malformed:
            for mode in ('block', 'warn'):
                with self.subTest(mode=mode, size=len(value)):
                    for provider in ('codex', 'copilot'):
                        arguments = value if provider == 'copilot' else {'command': value}
                        response = self.invoke(provider, 'apply_patch', arguments, mode=mode)
                        self.assert_decision(response, 'deny')
                        self.assertIn('input_limits', json.dumps(response))
        small = '*** Begin Patch\n*** Add File: x\n+safe\n*** End Patch\n' + FORCE_PUSH
        for provider in ('codex', 'copilot'):
            arguments = small if provider == 'copilot' else {'command': small}
            response = self.invoke(provider, 'apply_patch', arguments)
            self.assert_decision(response, 'deny')
            self.assertIn('force_push_protected_branch', json.dumps(response))
        result = invoke_guard(ROOT, 'codex', json.dumps({'tool_name': 'apply_patch', 'tool_input': {'command': 'safe'}}) + ' trailing')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_decision(json.loads(result.stdout), 'deny')

    def test_large_multifile_patch_checks_late_protected_operations_without_touching_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            env_file = directory / '.env'
            git_config = directory / '.git' / 'config'
            git_config.parent.mkdir()
            safe = directory / 'safe.txt'
            for path in (env_file, git_config, safe):
                path.write_text('sentinel fixture\n')
            original = {path: path.read_bytes() for path in (env_file, git_config, safe)}
            base = sized_native_patch(99186, files=3).removesuffix('*** End Patch')
            for source, rule in ((env_file, 'remove_env_file'), (git_config, 'remove_git_metadata')):
                operations = ('*** Delete File: ' + str(source),
                              '*** Update File: ' + str(source) + '\n*** Move to: ' + str(safe) + '\n@@\n-old\n+new')
                for operation in operations:
                    for provider in ('codex', 'copilot'):
                        for mode in ('block', 'warn'):
                            with self.subTest(provider=provider, source=source.name, operation=operation.splitlines()[0], mode=mode):
                                patch = base + operation + '\n*** End Patch'
                                response = self.invoke(provider, 'apply_patch', patch if provider == 'copilot' else {'command': patch}, mode=mode)
                                if mode == 'block':
                                    self.assert_decision(response, 'deny')
                                else:
                                    self.assertIn('Tool Guardian warning apply_patch', response['systemMessage'])
                                    self.assertNotEqual(native_decision(response), 'deny')
                                self.assertIn(rule, json.dumps(response))
                                self.assertNotIn('input_limits', json.dumps(response))
                                # Prehook rejection leaves fixtures untouched; this is not executor atomicity.
                                self.assertEqual({path: path.read_bytes() for path in original}, original)

    def test_full_capacity_high_line_count_patch_requires_complete_grammar(self) -> None:
        prefix = '*** Begin Patch\n*** Add File: example.txt\n+'
        suffix = '\n' + '+\n' * 130000 + '*** End Patch'
        for provider, key_bytes in (('codex', 7), ('copilot', 0)):
            patch = prefix + 'x' * (262144 - key_bytes - len(prefix + suffix)) + suffix
            self.assertEqual(len(patch.encode('utf-8')) + key_bytes, 262144)
            value = patch if provider == 'copilot' else {'command': patch}
            self.assert_decision(self.invoke(provider, 'apply_patch', value), 'allow')
            for mode in ('block', 'warn'):
                malformed = patch[:-1] + '!'
                value = malformed if provider == 'copilot' else {'command': malformed}
                response = self.invoke(provider, 'apply_patch', value, mode=mode)
                self.assert_decision(response, 'deny')
                self.assertIn('32768', json.dumps(response))
                self.assertIn('scan_text_characters' if provider == 'copilot' else 'structured_bytes', json.dumps(response))

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
