#!/usr/bin/env python3
"""Resource boundaries through each generated hook's public JSON interface."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
PROVIDERS = ('copilot', 'gemini', 'codex')
SHELL_TOOLS = {'copilot': 'bash', 'gemini': 'run_shell_command', 'codex': 'Bash'}


class ResourceLimitTests(unittest.TestCase):
    def invoke(self, provider: str, tool: str, value: object, *, mode: str = 'block', allowlist: bool = False) -> dict:
        script = ROOT / ('.codex/hooks/tool-guard.py' if provider == 'codex' else f'.{provider}/hooks/scripts/tool-guard.py')
        payload = {'toolName': tool, 'toolArgs': value} if provider == 'copilot' else {'tool_name': tool, 'tool_input': value}
        payload['hook_event_name'] = 'BeforeTool' if provider == 'gemini' else 'PreToolUse'
        with tempfile.TemporaryDirectory() as temporary:
            env = {**os.environ, 'GUARD_MODE': mode, 'TOOL_GUARD_LOG_DIR': str(Path(temporary) / 'log')}
            env.pop('SKIP_TOOL_GUARD', None)
            env.pop('TOOL_GUARD_ALLOWLIST', None)
            if allowlist:
                exact = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, separators=(',', ':'))
                # A rejected >8192 entry would not prove allowlist precedence.
                self.assertLessEqual(len(exact), 8192)
                self.assertFalse(any(ord(char) < 32 for char in exact))
                env['TOOL_GUARD_ALLOWLIST'] = json.dumps([{'tool': tool, 'input': exact}])
            result = subprocess.run([sys.executable, '-I', '-S', '-B', str(script)], input=json.dumps(payload),
                                    text=True, capture_output=True, env=env, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def assert_decision(self, response: dict, expected: str) -> None:
        decision = (response.get('permissionDecision') or response.get('decision')
                    or response.get('hookSpecificOutput', {}).get('permissionDecision')
                    or ('allow' if response == {} else None))
        self.assertEqual(decision, expected, response)
        if expected == 'allow':
            self.assertNotIn('systemMessage', response)

    def assert_boundary(self, provider: str, tool: str, maximum: object, overflow: object,
                        rule: str, count: str, *, valid_allowlist: bool = False) -> None:
        self.assert_decision(self.invoke(provider, tool, maximum), 'allow')
        for mode in ('block', 'warn'):
            with self.subTest(provider=provider, rule=rule, mode=mode):
                response = self.invoke(provider, tool, overflow, mode=mode, allowlist=valid_allowlist)
                self.assert_decision(response, 'deny')
                reason = json.dumps(response)
                self.assertIn(rule, reason)
                self.assertIn(count, reason)
                self.assertNotIn('TOOL_GUARD_ALLOWLIST', reason)
                self.assertIn('command omitted', reason)

    def test_structure_maximum_and_first_rejected_node_string_and_depth(self) -> None:
        deep: object = 0
        for _ in range(32):
            deep = [deep]
        cases = (([0] * 255, [0] * 256, 'structured_nodes', '257 nodes'),
                 (['x'] * 128, ['x'] * 129, 'structured_strings', '129 strings'),
                 (deep, [deep], 'structured_depth', '33 levels'))
        for provider in PROVIDERS:
            for maximum, overflow, rule, count in cases:
                self.assert_boundary(provider, 'unknown_tool', maximum, overflow, rule, count, valid_allowlist=True)

    def test_strict_ascii_and_utf8_byte_maxima(self) -> None:
        # Strict scalar inspection includes one space and the tool name.
        for provider in PROVIDERS:
            self.assert_boundary(provider, 'X', 'x' * 32766, 'x' * 32767,
                                 'scan_text_characters', '32769 characters')
            maximum = '界' * 10922
            self.assert_boundary(provider, 'X', maximum, maximum + 'x', 'scan_text_bytes', '32769 bytes')

    def test_native_utf8_body_maximum_and_first_rejected_aggregate(self) -> None:
        for provider, tool, path_key, body_key in (('copilot', 'create', 'path', 'file_text'),
                                                  ('gemini', 'write_file', 'file_path', 'content')):
            overhead = len(path_key + body_key + 'example.txt')
            available = 65536 - overhead
            body = '界' * (available // 3) + 'x' * (available % 3)
            maximum = {path_key: 'example.txt', body_key: body}
            overflow = {path_key: 'example.txt', body_key: body + 'x'}
            self.assert_boundary(provider, tool, maximum, overflow, 'structured_bytes', '65537 bytes')


    def test_native_patch_operation_normalization_ascii_maximum(self) -> None:
        prefix, suffix = '*** Begin Patch\n*** Delete File: ', '\n*** End Patch'
        self.assert_boundary('codex', 'apply_patch', {'command': prefix + 'x' * 32768 + suffix},
                             {'command': prefix + 'x' * 32769 + suffix},
                             'normalized_operation_bytes', '32769 bytes')

    def test_native_patch_operation_nfkc_expansion_and_casefold_maxima(self) -> None:
        prefix, suffix = '*** Begin Patch\n*** Delete File: ', '\n*** End Patch'
        # U+FDFA expands 3 UTF-8 bytes to 33; U+0390 casefold expands 2 to 6.
        for path in ('\ufdfa' * 992 + 'x' * 32, '\u0390' * 5461 + 'xx'):
            self.assert_boundary('codex', 'apply_patch', {'command': prefix + path + suffix},
                                 {'command': prefix + path + 'x' + suffix},
                                 'normalized_operation_bytes', '32769 bytes')

    def test_native_patch_normalized_work_is_aggregate_across_operations(self) -> None:
        prefix, suffix = '*** Begin Patch\n', '\n*** End Patch'
        path = '\ufdfa' * 496 + 'x' * 16
        maximum = prefix + '*** Delete File: ' + path + '\n*** Delete File: ' + path + suffix
        overflow = maximum.replace(path + suffix, path + 'x' + suffix)
        self.assert_boundary('codex', 'apply_patch', {'command': maximum}, {'command': overflow},
                             'normalized_operation_bytes', '32769 bytes')

    def test_recognized_search_paths_first_rejected_string(self) -> None:
        self.assert_boundary('copilot', 'grep', {'pattern': 'safe', 'paths': ['docs'] * 127},
                             {'pattern': 'safe', 'paths': ['docs'] * 128},
                             'structured_strings', '129 strings', valid_allowlist=True)

    def test_strict_normalized_text_expansion_maximum(self) -> None:
        # The tool prefix and quotes account for four ASCII bytes.
        # U+0958 becomes two three-byte combining characters without spaces.
        maximum = "'" + '\u0958' * 5460 + 'x' * 4 + "'"
        overflow = maximum[:-1] + 'x' + maximum[-1]
        for provider in PROVIDERS:
            self.assert_boundary(provider, 'X', maximum, overflow,
                                 'normalized_scan_text_bytes', '32769 bytes', valid_allowlist=True)

    def test_shell_command_and_total_token_maxima(self) -> None:
        for provider in PROVIDERS:
            tool = SHELL_TOOLS[provider]
            for maximum, overflow, rule, count in (
                (';'.join(['x'] * 128), ';'.join(['x'] * 129), 'command_segments', '129 segments'),
                (' '.join(['x'] * 256), ' '.join(['x'] * 257), 'command_tokens', '257 tokens'),
                (';'.join(['x x'] * 128), ';'.join(['x x'] * 127 + ['x x x']), 'command_tokens', '257 tokens')):
                self.assert_boundary(provider, tool, {'command': maximum}, {'command': overflow}, rule, count, valid_allowlist=True)

    def test_unproved_quoted_argument_first_rejected_matcher_token(self) -> None:
        for provider in PROVIDERS:
            maximum = {'command': "echo '" + 'x ' * 255 + "'"}
            overflow = {'command': "echo '" + 'x ' * 256 + "'"}
            self.assert_boundary(provider, SHELL_TOOLS[provider], maximum, overflow,
                                 'command_tokens', '257 tokens', valid_allowlist=True)

    def test_redirection_and_unproved_heredoc_spend_aggregate_matcher_tokens(self) -> None:
        for provider in PROVIDERS:
            tool = SHELL_TOOLS[provider]
            # The redirection's one lexical slot already accounts for its operand.
            self.assert_boundary(provider, tool, {'command': "echo > '" + 'x ' * 255 + "'"},
                                 {'command': "echo > '" + 'x ' * 256 + "'"},
                                 'command_tokens', '257 tokens', valid_allowlist=True)
            self.assert_boundary(provider, tool, {'command': "cat <<'EOF'\n" + 'x ' * 254 + '\nEOF'},
                                 {'command': "cat <<'EOF'\n" + 'x ' * 255 + '\nEOF'},
                                 'command_tokens', '257 tokens')

    def test_executable_byte_budget_and_substitution_depth(self) -> None:
        for provider in PROVIDERS:
            tool = SHELL_TOOLS[provider]
            source = "bash -c '" + 'x' * 16378 + "'  "
            self.assert_boundary(provider, tool, {'command': source}, {'command': source + ' '},
                                 'executable_bytes', '32769 bytes')
            self.assert_boundary(provider, tool, {'command': 'echo $(' * 16 + 'x' + ')' * 16},
                                 {'command': 'echo $(' * 17 + 'x' + ')' * 17},
                                 'executable_depth', '17 levels', valid_allowlist=True)

    def test_python_parser_depth_token_and_ast_depth_maxima(self) -> None:
        def command(source: str) -> dict:
            return {'command': 'python3 -c ' + shlex.quote(source)}
        writer = 'from pathlib import Path;Path("x").write_text('
        assignment = 'from pathlib import Path;Path("x").write_text("safe");a='
        cases = (('(' * 32 + '0' + ')' * 32, '(' * 33 + '0' + ')' * 33, 'python_syntax_depth', '33 levels'),
                 (writer + '"x"' * 1011 + ')', writer + '"x"' * 1012 + ')', 'python_syntax_tokens', '1025 tokens'),
                 (assignment + '"x"' * 1007, assignment + '"x"' * 1008, 'python_syntax_tokens', '1025 tokens'),
                 ('x+' * 29 + 'x', 'x+' * 30 + 'x', 'python_ast_depth', '33 levels'))
        for provider in PROVIDERS:
            for maximum, overflow, rule, count in cases:
                self.assert_boundary(provider, SHELL_TOOLS[provider], command(maximum), command(overflow), rule, count, valid_allowlist=True)

    def test_allowlist_control_proves_valid_matching_entry(self) -> None:
        operation = 'git push' + ' --force origin main'
        for provider in PROVIDERS:
            tool = SHELL_TOOLS[provider]
            value = {'command': operation}
            self.assert_decision(self.invoke(provider, tool, value), 'deny')
            self.assert_decision(self.invoke(provider, tool, value, allowlist=True), 'allow')

    def test_python_resolved_string_maximum_and_first_rejected_byte(self) -> None:
        maximum = "a='" + 'x' * 1024 + "';b=a+a;c=b+b;d=c+c;e=d+d;f=e+e"
        overflow = maximum + ';g=f+"x"'
        for provider in PROVIDERS:
            self.assert_boundary(provider, SHELL_TOOLS[provider],
                                 {'command': 'python3 -c ' + shlex.quote(maximum)},
                                 {'command': 'python3 -c ' + shlex.quote(overflow)},
                                 'python_resolved_bytes', '32769 bytes', valid_allowlist=True)

    def test_encoding_failure_precedes_valid_allowlist_in_warn_mode(self) -> None:
        for provider in PROVIDERS:
            value = {'body': '\ud800'}
            response = self.invoke(provider, 'unknown_tool', value, mode='warn', allowlist=True)
            self.assert_decision(response, 'deny')
            self.assertIn('inspection_failure', json.dumps(response))


if __name__ == '__main__':
    unittest.main()
