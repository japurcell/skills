#!/usr/bin/env python3
"""Behavioral parity tests for the inactive, embeddable stream component."""
import importlib.util
import json
import os
from pathlib import Path
import random
import re
import tracemalloc
import unittest


def redact(value):
    return value[:4] + "..." + value[-4:]

ROOT = Path(__file__).resolve().parents[1]

# Independent legacy oracle: deliberately operates on whole test-only strings.
ORACLE_PATTERNS = [
    ("github_classic_pat", "high", re.compile(r"gh[pousr]_[A-Za-z0-9]{36}")),
    ("github_fine_grained_pat", "high", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("aws_access_key", "high", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("stripe_live_key", "high", re.compile(r"sk_live_[0-9A-Za-z]{16,}")),
    ("slack_token", "medium", re.compile(r"xox[baprs]-[0-9A-Za-z-]{10,}")),
]
TOKENS = ["ghp_" + "A" * 36, "github_pat_" + "B" * 20,
          "AKIA" + "C" * 16, "sk_live_" + "D" * 16, "xoxb-" + "E" * 10]

def component():
    spec = importlib.util.spec_from_file_location("scanner_stream", ROOT / "hooks/families/scanner_stream.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    namespace = {}
    exec(module.SOURCE, namespace)
    return namespace


def oracle(lines, path="p", is_allowlisted=lambda key: False, initial=None, processed=0):
    findings = list(initial or [])
    for number, line in lines:
        for name, severity, regex in ORACLE_PATTERNS:
            for match in regex.finditer(line):
                if is_allowlisted(f"{path}:{number}:{name}:{match.group()}"):
                    continue
                if len(findings) < 100:
                    findings.append((name, severity, path, number, redact(match.group())))
                processed += 1
                if processed == 1000:
                    return findings, processed, True
    return findings, processed, False


def full_scan(api, raw, sizes, classification="text", path="p", allow=lambda key: False,
              initial=None, processed=0):
    def chunks():
        offset = 0
        for size in sizes:
            yield raw[offset:offset + size]
            offset += size
        while offset < len(raw):
            yield raw[offset:offset + 65536]
            offset += 65536
    report = api["StreamReport"](list(initial or []), processed)
    api["scan_line_events"](path, api["full_line_events"](chunks(), classification),
                            report, allow, redact)
    return report.findings, report.processed, report.stopped


def diff_oracle(raw):
    lines = []
    current = None
    for line in raw.splitlines():
        if line.startswith(b"diff --git "):
            current = None
        elif line.startswith(b"@@"):
            match = re.search(rb"\+(\d+)", line)
            current = int(match.group(1)) if match else None
        elif current is not None:
            if line.startswith(b"+"):
                lines.append((current, os.fsdecode(line[1:])))
                current += 1
            elif line.startswith(b" "):
                current += 1
    return oracle(lines)

class StreamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = component()

    def assert_full_parity(self, raw, sizes, classification="text", **kwargs):
        if classification == "binary":
            text = "".join(chr(byte) if byte in (9, 10, 13) or 32 <= byte <= 126 else " "
                           for byte in raw)
        else:
            text = raw.decode("utf-8", "replace")
        expected = oracle(enumerate(text.splitlines(), 1), **{
            "is_allowlisted" if key == "allow" else key: value
            for key, value in kwargs.items()})
        self.assertEqual(full_scan(self.api, raw, sizes, classification, **kwargs), expected)

    def test_every_token_and_delimiter_split(self):
        for token in TOKENS:
            raw = ("before " + token + "/" + token + " after").encode()
            for boundary in range(len(raw) + 1):
                with self.subTest(token=token[:4], boundary=boundary):
                    self.assert_full_parity(raw, [boundary])
        for separator in ("\n", "\r", "\r\n", "\v", "\f", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029"):
            raw = (separator + TOKENS[0] + separator * 2 + TOKENS[2] + separator).encode()
            for boundary in range(len(raw) + 1):
                self.assert_full_parity(raw, [boundary])

    def test_bounded_random_parity_and_invalid_utf8(self):
        rng = random.Random(144)
        vocabulary = TOKENS + ["github_pat_bad", "AKIAAKIA", "xoxb-xoxb-", "ghp_ghp_",
                               " ", "/", "\r\n", "\u2028", "\t", "safe", "_", "\x00"]
        for _ in range(300):
            raw = "".join(rng.choices(vocabulary, k=rng.randrange(1, 30))).encode()
            sizes = [rng.randrange(1, 40) for _ in range(len(raw) // 10)]
            self.assert_full_parity(raw, sizes, rng.choice(["text", "binary"]))
        for raw in (b"\xf0\x9f\x92" + TOKENS[0].encode(), TOKENS[1].encode() + b"\xe2\x80",
                    b"\xe2\x80" + b"a" * 65536 + TOKENS[2].encode()):
            self.assert_full_parity(raw, [2, 65536])

    def test_fixed_nonoverlap_and_failed_candidate_restart(self):
        raw = ("AKIA" * 30 + " ghp_ghp_" + "A" * 36 + " github_pat_bad/" + TOKENS[1]
               + " xoxb-xoxb-" + "E" * 10).encode()
        for size in range(1, 43):
            self.assert_full_parity(raw, [size] * (len(raw) // size))

    def test_order_caps_and_credential_path_consumption(self):
        raw = ((TOKENS[2] + " " + TOKENS[0] + " ") * 700 + "\n" + TOKENS[1]).encode()
        for initial_count in (0, 99, 999):
            initial = [("credential_path", "critical", "p", 1, "[SENSITIVE PATH]")] if initial_count else []
            self.assert_full_parity(raw, [127] * (len(raw) // 127), initial=initial,
                                    processed=initial_count)

    def test_exact_normalized_allowlist_cap_and_forbidden_prefix(self):
        spec = importlib.util.spec_from_file_location("allowlist", ROOT / "hooks/runtime/scan_allowlist.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for path in ("p", "   p", "p\\n", "p\t", "p" * 8200):
            prefix = f"{path}:1:github_fine_grained_pat:"
            available = 8192 - len(prefix.lstrip(" "))
            for length in (31, max(31, available), max(32, available + 1)):
                token = "github_pat_" + "B" * (length - 11)
                entries = module.parse_allowlist(json.dumps([{"tool": "scan_secrets", "input": prefix + token}]))
                allow = lambda key: module.allowlist_contains("scan_secrets", key, entries)
                self.assert_full_parity((token + "/" + token + "Z").encode(), [19] * (length // 9),
                                        path=path, allow=allow)

    def test_retained_state_is_bounded_on_long_line_and_empty_lines(self):
        api = self.api
        report = api["StreamReport"]()
        chunk = b"A" * 65536
        def chunks():
            yield b"github_pat_"
            for _ in range(64):
                yield chunk
        tracemalloc.start()
        try:
            api["scan_line_events"]("p", api["full_line_events"](chunks(), "text"), report,
                                    lambda key: False, redact)
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        self.assertLess(peak, 1024 * 1024)
        self.assertEqual(report.findings[0][-1], "gith...AAAA")
        self.assertEqual(list(api["full_line_events"]((b"\n" * 65536 for _ in range(128)), "text")), [])

    def test_diff_exhaustive_boundaries_and_surrogateescape(self):
        raw = (b"diff --git a/p b/p\r\nignored header\n@@ -3,2 +19,2 @@ section\r\n-removed\n+"
               + TOKENS[0].encode() + b"\xe2\x80\xa8" + TOKENS[1].encode()
               + b"\r\n context\n\\ No newline at end of file\n+\xf0\x9f\x92"
               + TOKENS[2].encode() + b"\n+\n")
        for boundary in range(len(raw) + 1):
            report = self.api["StreamReport"]()
            self.api["scan_line_events"]("p", self.api["diff_added_line_events"](
                [raw[:boundary], raw[boundary:]]), report, lambda key: False, redact)
            self.assertEqual((report.findings, report.processed, report.stopped), diff_oracle(raw))
        raw = b"diff --git a/p b/p\n@@ +1 @@\n+\xe2\x80" + b"a" * 65536 + TOKENS[3].encode() + b"\n"
        report = self.api["StreamReport"]()
        self.api["scan_line_events"]("p", self.api["diff_added_line_events"](
            [raw[:37], raw[37:65573], raw[65573:]]), report, lambda key: False, redact)
        self.assertEqual((report.findings, report.processed, report.stopped), diff_oracle(raw))

    def test_budget_and_invalid_chunks_fail_without_hiding_errors(self):
        class BudgetExpired(Exception):
            pass
        def expired():
            raise BudgetExpired()
        for events in (self.api["full_line_events"]([b"safe"], "text", expired),
                       self.api["diff_added_line_events"]([b""], expired)):
            with self.assertRaises(BudgetExpired):
                list(events)
        with self.assertRaises(ValueError):
            list(self.api["full_line_events"]([b"x" * 65537], "text"))
        with self.assertRaises(ValueError):
            list(self.api["diff_added_line_events"]([b"x" * 65537]))
        report = self.api["StreamReport"]()
        with self.assertRaises(BudgetExpired):
            self.api["scan_line_events"]("p", [("start", 1)], report, lambda key: False, redact, expired)

    def test_diff_bytes_split_before_unicode_decoding(self):
        api = component()
        token = "github_pat_" + "D" * 20
        raw = ("diff --git a/p b/p\n@@ -1 +7,2 @@\n+left\u2028" + token
               + "\r\n+" + token + "\n").encode()
        report = api["StreamReport"]()
        api["scan_line_events"]("p", api["diff_added_line_events"](
            [raw[index:index + 1] for index in range(len(raw))]), report,
            lambda key: False, redact)
        self.assertEqual([finding[3] for finding in report.findings], [7, 8])
        for malformed in (raw[:-1], b"not a diff\n", b"diff --git a/p b/p\n@@ +" + b"9" * 21 + b" @@\n"):
            with self.assertRaises(ValueError):
                list(api["diff_added_line_events"]([malformed]))

    def test_diff_late_invalid_content_is_not_hidden_by_finding_cap(self):
        raw = (b"diff --git a/p b/p\n@@ +1 @@\n+" + (TOKENS[0] + " ").encode() * 1001
               + b"\n+safe\nunexpected hunk content\n")
        with self.assertRaises(self.api["StreamDiffError"]):
            report = self.api["StreamReport"]()
            self.api["scan_line_events"]("p", self.api["diff_added_line_events"](
                (raw[offset:offset + 65536] for offset in range(0, len(raw), 65536))),
                report, lambda key: False, redact)

    def test_matching_preserves_line_pattern_order_and_greedy_extension(self):
        api = component()
        short = "github_pat_" + "A" * 20
        raw = ("AKIA" + "B" * 16 + " " + short + "C" * 9000 + "\n").encode()
        report = api["StreamReport"]()
        api["scan_line_events"]("p", api["full_line_events"](
            [raw[index:index + 7] for index in range(0, len(raw), 7)], "text"),
            report, lambda key: key == "p:1:github_fine_grained_pat:" + short, redact)
        self.assertEqual(report.findings, [
            ("github_fine_grained_pat", "high", "p", 1, "gith...CCCC"),
            ("aws_access_key", "high", "p", 1, "AKIA...BBBB")])
        self.assertEqual(report.processed, 2)

    def test_full_lines_preserve_splitlines_numbers(self):
        api = component()
        raw = "one\r\n\nthree\u2028four".encode()
        events = []
        for kind, value in api["full_line_events"]([raw[:4], raw[4:8], raw[8:]], "text"):
            if kind == "data" and events and events[-1][0] == "data":
                events[-1] = ("data", events[-1][1] + value)
            else:
                events.append((kind, value))
        self.assertEqual(events, [("start", 1), ("data", "one"), ("end", None),
                                  ("start", 3), ("data", "three"), ("end", None),
                                  ("start", 4), ("data", "four"), ("end", None)])

if __name__ == "__main__":
    unittest.main()
