#!/usr/bin/env python3
"""File-operation capacity through generated hooks; fixture commands never execute."""
from __future__ import annotations

import json
from pathlib import Path
import shlex
import unittest

from tool_guard_corpus import Fixture, OPERATIONS, PROVIDERS, decision, encode, envelope, patch
from tool_guard_test_support import invoke_guard

ROOT = Path(__file__).resolve().parents[1]
CAPACITY = 1048576


class FileOperationTests(unittest.TestCase):
    def test_quoted_shell_writer_keeps_the_body_out_of_execution_budgets(self):
        body = ("literal text " * (CAPACITY // 13 + 1))[:CAPACITY - 1] + "\n"
        writer = "cat > example.txt <<'EOF'\n" + body + "EOF"
        for command, expected, cause in (
            (writer, "allow", None),
            (writer + "\n" + OPERATIONS["force_push_protected_branch"], "deny", "force_push_protected_branch"),
            ("echo '" + body + "'", "deny", "security_outcome=incomplete"),
        ):
            fixture = Fixture("capacity-shell", "provider_shell", {"command": command},
                              "deny", expected, "capacity", "bounded prototype")
            for provider in PROVIDERS:
                with self.subTest(provider=provider, expected=expected, cause=cause):
                    result = invoke_guard(ROOT, provider, encode(envelope(provider, fixture)))
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(decision(provider, json.loads(result.stdout)), expected, result.stdout)
                    if cause:
                        self.assertIn(cause, result.stdout.decode())

    def test_shell_literal_content_budget_counts_raw_utf8_and_tab_bytes(self):
        for extra in (0, 1):
            # 349525 three-byte characters plus newline exactly fill 1 MiB.
            body = "界" * 349525 + "x" * extra + "\n"
            for delimiter, contents in (("<<'EOF'", body), ("<<-'EOF'", "\t" + body[1:-1] + "xx\n")):
                # The tab-stripping form still charges every original body byte.
                self.assertEqual(len(contents.encode("utf-8")), 1048576 + extra)
                fixture = Fixture("literal-bytes", "provider_shell",
                                  {"command": "cat > example.txt " + delimiter + "\n" + contents + "EOF"},
                                  "deny", "deny" if extra else "allow", "bounds", "raw literal byte accounting")
                for provider in PROVIDERS:
                    for mode in ("block", "warn"):
                        result = invoke_guard(ROOT, provider, encode(envelope(provider, fixture)), mode=mode)
                        with self.subTest(provider=provider, extra=extra, delimiter=delimiter, mode=mode):
                            self.assertEqual(decision(provider, json.loads(result.stdout)), fixture.candidate, result.stdout)
                            if extra:
                                self.assertIn("literal_content_bytes", result.stdout.decode())
                                self.assertIn("1048577 bytes exceeds limit 1048576 bytes", result.stdout.decode())

    def test_unused_envelope_metadata_is_bounded_independently(self):
        fixture = Fixture("envelope-metadata", "provider_shell", {"command": "echo safe"}, "deny", "deny", "bounds", "probe")
        for provider in PROVIDERS:
            data = envelope(provider, fixture)
            data["unused_metadata"] = "x" * 32769
            result = invoke_guard(ROOT, provider, encode(data))
            self.assertEqual(decision(provider, json.loads(result.stdout)), "deny", result.stdout)
            self.assertIn("envelope_metadata_bytes", result.stdout.decode())

    def test_raw_structure_limit_reports_the_first_rejected_marker(self):
        for provider in PROVIDERS:
            for extra in (0, 1):
                if provider == "copilot":
                    event = {"toolName": "bash", "toolArgs": {"command": "echo safe"}}
                else:
                    event = {"tool_name": "Bash" if provider == "codex" else "run_shell_command", "tool_input": {"command": "echo safe"}}
                event["unused"] = [0] * (4079 + extra)
                result = invoke_guard(ROOT, provider, encode(event))
                with self.subTest(provider=provider, extra=extra):
                    self.assertEqual(decision(provider, json.loads(result.stdout)), "deny", result.stdout)
                    self.assertIn("raw_structural_markers" if extra else "envelope_metadata_nodes", result.stdout.decode())
                    if extra:
                        self.assertIn("4097 markers exceeds limit 4096 markers", result.stdout.decode())

    def test_raw_byte_limit_reports_the_first_rejected_byte(self):
        raw_limit = 6 * (CAPACITY + 3 * 32768) + 8192
        fixture = Fixture("raw-boundary", "provider_shell", {"command": "echo safe"}, "deny", "allow", "capacity", "probe")
        for provider in PROVIDERS:
            event = encode(envelope(provider, fixture)).rstrip()
            for extra in (0, 1):
                data = event[:-1] + b" " * (raw_limit + extra - len(event)) + b"}"
                result = invoke_guard(ROOT, provider, data)
                with self.subTest(provider=provider, extra=extra):
                    self.assertEqual(decision(provider, json.loads(result.stdout)), "deny" if extra else "allow", result.stdout)
                    if extra:
                        self.assertIn("raw_input_bytes", result.stdout.decode())
                        self.assertIn(f"{raw_limit + 1} bytes exceeds limit {raw_limit} bytes", result.stdout.decode())

    def test_json_escape_runs_across_reader_chunks_keep_exact_provenance(self):
        for provider in PROVIDERS:
            for suffix in ("\\", "\\\"", "\\\\", "\\\\\""):
                pattern = json.dumps(suffix)[1:-1].encode()
                def encoded_body(length):
                    body = "x" * length + suffix
                    value = ({"command": "*** Begin Patch\n*** Add File: example.txt\n+" + body + "\n*** End Patch"}
                             if provider == "codex" else {"file_path": "example.txt", "content": body})
                    fixture = Fixture("chunk-escape", "apply_patch" if provider == "codex" else "write_file", value, "deny", "allow", "capacity", "probe")
                    return encode(envelope(provider, fixture))
                prefix = encoded_body(32).index(pattern) - 32
                for boundary in (65534, 65535, 65536):
                    data = encoded_body(boundary - prefix)
                    with self.subTest(provider=provider, suffix=suffix, boundary=boundary):
                        self.assertEqual(data.index(pattern), boundary)
                        result = invoke_guard(ROOT, provider, data)
                        self.assertEqual(decision(provider, json.loads(result.stdout)), "allow", result.stdout)

    def test_fully_escaped_native_maximum(self):
        for provider in PROVIDERS:
            fixture = (Fixture("capacity", "apply_patch", {"command": patch(4, size=CAPACITY)}, "deny", "allow", "capacity", "probe")
                       if provider == "codex" else
                       Fixture("capacity", "write_file", {"file_path": "example.txt", "content": "x" * CAPACITY}, "deny", "allow", "capacity", "probe"))
            serialized = json.dumps(envelope(provider, fixture), separators=(",", ":"))
            payload = "".join("\\u%04x" % ord(char) if char == "x" else char for char in serialized).encode()
            result = invoke_guard(ROOT, provider, payload)
            self.assertEqual(decision(provider, json.loads(result.stdout)), "allow", result.stdout)

    def test_admitted_unproved_shell_source_keeps_executable_limits(self):
        for extra, cause in ((0, "scan_text_characters"), (1, "inspection_source_bytes")):
            source = "echo " + "x" * (CAPACITY + 32768 - 5 + extra)
            fixture = Fixture("source-admission", "provider_shell", {"command": source},
                              "deny", "deny", "bounds", "finite admission is not a proof")
            for provider in PROVIDERS:
                for mode in ("block", "warn"):
                    with self.subTest(provider=provider, extra=extra, mode=mode):
                        result = invoke_guard(ROOT, provider, encode(envelope(provider, fixture)), mode=mode)
                        self.assertEqual(decision(provider, json.loads(result.stdout)), "deny", result.stdout)
                        self.assertIn(cause, result.stdout.decode())
                        self.assertIn("security_outcome=incomplete", result.stdout.decode())

    def test_edit_content_limit_is_aggregate_across_both_fields(self):
        for provider, tool, old_key, new_key in (("copilot", "edit", "old_str", "new_str"),
                                                 ("gemini", "replace", "old_string", "new_string")):
            for extra in (0, 1):
                value = {"path" if provider == "copilot" else "file_path": "example.txt",
                         old_key: "x" * 524288, new_key: "y" * (524288 + extra)}
                if provider == "gemini":
                    value["instruction"] = "Replace literal document"
                fixture = Fixture("aggregate-edit", tool, value, "deny", "deny" if extra else "allow",
                                  "bounds", "two fields share one content budget")
                result = invoke_guard(ROOT, provider, encode(envelope(provider, fixture)))
                with self.subTest(provider=provider, extra=extra):
                    self.assertEqual(decision(provider, json.loads(result.stdout)), fixture.candidate, result.stdout)
                    if extra:
                        self.assertIn("1048577 bytes exceeds limit 1048576 bytes", result.stdout.decode())

    def test_native_aggregate_maximum_and_first_rejection(self):
        for provider in PROVIDERS:
            for extra in (0, 1):
                if provider == "codex":
                    fixture = Fixture("capacity", "apply_patch", {"command": patch(4, size=CAPACITY + extra)},
                                      "deny", "allow", "capacity", "finite content contract")
                else:
                    fixture = Fixture("capacity", "write_file", {"file_path": "example.txt", "content": "x" * (CAPACITY + extra)},
                                      "deny", "allow", "capacity", "finite content contract")
                with self.subTest(provider=provider, extra=extra):
                    result = invoke_guard(ROOT, provider, encode(envelope(provider, fixture)))
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(decision(provider, json.loads(result.stdout)), "deny" if extra else "allow", result.stdout)
                    if extra:
                        self.assertIn("native_content_bytes", result.stdout.decode())


if __name__ == "__main__":
    unittest.main()
