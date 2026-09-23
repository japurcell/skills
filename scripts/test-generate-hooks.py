#!/usr/bin/env python3
"""Public CLI and transaction tests for the checked-in hook generator."""

from __future__ import annotations

import importlib.util
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
from hashlib import sha256
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "generate-hooks.py"
OWNERSHIP = "# Generated from hooks/families/send_event.py by scripts/generate-hooks.py. Do not edit.\n"
PILOT_RUNTIME_BODY = '''
from __future__ import annotations

import os
import sys

from helpers.common import emit_json, read_json_input


def main() -> int:
    if "--include-transcript" in sys.argv[1:]:
        os.environ["OBSERVABILITY_INCLUDE_TRANSCRIPT"] = "true"

    read_json_input()
    emit_json({})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
TARGETS = (
    ".copilot/hooks/scripts/send-event.py",
    ".gemini/hooks/scripts/send-event.py",
)
OBSERVABILITY_TARGETS = (
    ".copilot/hooks/scripts/helpers/observability.py",
    ".gemini/hooks/scripts/helpers/observability.py",
)
TOOL_GUARD_TARGETS = (
    ".copilot/hooks/scripts/tool-guard.py",
    ".gemini/hooks/scripts/tool-guard.py",
)
SECRET_SCANNER_TARGETS = (
    ".copilot/hooks/scripts/scan-secrets.py",
    ".gemini/hooks/scripts/scan-secrets.py",
    ".codex/hooks/scan-secrets.py",
)
CODEX_HELPER_TARGETS = (
    ".codex/hooks/helpers/common.py",
    ".codex/hooks/helpers/audit.py",
)
AUTO_INGEST_TARGETS = (
    ".github/hooks/scripts/helpers/auto_ingest.py",
    ".gemini/hooks/scripts/helpers/source_ingest.py",
    ".github/hooks/scripts/auto-ingest-source.py",
    ".gemini/hooks/scripts/auto-ingest.py",
    ".github/hooks/scripts/inject-auto-ingest-context.py",
    ".gemini/hooks/scripts/inject-auto-ingest-context.py",
)
RTK_TARGETS = (
    ".copilot/hooks/scripts/rtk-hook-copilot.py",
    ".gemini/hooks/scripts/rtk-hook-gemini.py",
)
OBSERVABILITY_ALLOWED_DIFFERENCES = (
    ('OBSERVABILITY_RUNTIME = "copilot"', 'OBSERVABILITY_RUNTIME = "gemini"'),
    ('_truthy_env("COPILOT_OBSERVABILITY_DISABLE", "OBSERVABILITY_DISABLE")',
     '_truthy_env("GEMINI_OBSERVABILITY_DISABLE", "OBSERVABILITY_DISABLE")'),
    ('_truthy_env("OBSERVABILITY_CAPTURE_EVENT", "COPILOT_OBSERVABILITY_CAPTURE_EVENT")',
     '_truthy_env("OBSERVABILITY_CAPTURE_EVENT", "GEMINI_OBSERVABILITY_CAPTURE_EVENT")'),
    ('_truthy_env("OBSERVABILITY_INCLUDE_TRANSCRIPT", "COPILOT_OBSERVABILITY_INCLUDE_TRANSCRIPT")',
     '_truthy_env("OBSERVABILITY_INCLUDE_TRANSCRIPT", "GEMINI_OBSERVABILITY_INCLUDE_TRANSCRIPT")'),
    ('os.environ.get("COPILOT_OBSERVABILITY_LOG_PATH")',
     'os.environ.get("GEMINI_OBSERVABILITY_LOG_PATH")'),
    ('Path.home() / ".copilot" / "hooks" / "logs"',
     'Path.home() / ".gemini" / "hooks" / "logs"'),
    ('os.environ.get("COPILOT_OBSERVABILITY_LOCK_WAIT_MS")',
     'os.environ.get("GEMINI_OBSERVABILITY_LOCK_WAIT_MS")'),
    ('os.environ.get("COPILOT_OBSERVABILITY_SOURCE_EVENT_NAME")',
     'os.environ.get("GEMINI_OBSERVABILITY_SOURCE_EVENT_NAME")'),
)
COMMON_AUDIT_TARGETS = {
    ".copilot/hooks/scripts/helpers/common.py": "ce024e0062ba449229b2ca2f79b44f5409f0df5e40764fafa81ad98efc27ac3f",
    ".gemini/hooks/scripts/helpers/common.py": "9e67b30751c3fbae8716a2fbb7bd544dfb213b7fcd285999c6f4651b17662e44",
    ".github/hooks/scripts/helpers/common.py": "6efd2a563b2e8012fe0e8c813630c94a50d3ed5f8cc6cb7c6507c8771dc357be",
    ".copilot/hooks/scripts/helpers/audit.py": "ffe27670de493f4d07285093927ea1a9bc06b2096941c3f6d52277447407edeb",
    ".gemini/hooks/scripts/helpers/audit.py": "6a5f20c4af7c4e9eeb7d187c0e24d1e340f15d82634f3de96ddbb2d79e1fcaa5",
    ".github/hooks/scripts/helpers/audit.py": "4b8fa5f1cfce5b948c3ef54230fa1ead4a5c7ebb6ea125dd45222b9968f403a9",
}


def load_generator():
    specification = importlib.util.spec_from_file_location("generate_hooks", SCRIPT)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def load_module(name: str, path: Path):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def snapshot(root: Path) -> dict[str, tuple[bytes, int]]:
    return {
        path.relative_to(root).as_posix(): (path.read_bytes(), stat.S_IMODE(path.stat().st_mode))
        for path in root.rglob("*")
        if path.is_file()
    }


class GenerateHooksTests(unittest.TestCase):
    def run_cli(self, *arguments: str, cwd: Path | None = None, environment: dict[str, str] | None = None):
        variables = os.environ.copy()
        if environment:
            variables.update(environment)
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            cwd=cwd or ROOT,
            text=True,
            capture_output=True,
            check=False,
            env=variables,
        )

    def restore_checked_in_outputs(self) -> None:
        subprocess.run(
            [sys.executable, str(SCRIPT), "--write"], cwd=ROOT,
            text=True, capture_output=True, check=True,
        )

    def tearDown(self) -> None:
        self.restore_checked_in_outputs()

    def test_auto_ingest_targets_are_generated_and_keep_runtime_boundaries(self) -> None:
        generator = load_generator()
        rendered = {
            output.target.output_path.as_posix(): output.content.decode("utf-8")
            for output in generator.render_all(ROOT)
        }
        self.assertTrue(set(AUTO_INGEST_TARGETS).issubset(rendered))
        for target in AUTO_INGEST_TARGETS:
            with self.subTest(target=target):
                self.assertIn("# Generated from hooks/families/auto_ingest.py", rendered[target])
                self.assertNotIn(".github.hooks", rendered[target])
                self.assertNotIn(".gemini.hooks", rendered[target])

    def test_rtk_targets_share_runtime_body_outside_explicit_provider_adapters(self) -> None:
        generator = load_generator()
        rendered = {
            output.target.output_path.as_posix(): output.content.decode("utf-8")
            for output in generator.render_all(ROOT)
        }
        self.assertTrue(set(RTK_TARGETS).issubset(rendered))

        shared_sections = []
        for target, provider in zip(RTK_TARGETS, ("copilot", "gemini"), strict=True):
            with self.subTest(target=target):
                source = rendered[target]
                self.assertTrue(source.startswith(
                    "#!/usr/bin/env python3\n"
                    "# Generated from hooks/families/rtk.py by scripts/generate-hooks.py. Do not edit.\n"
                ))
                self.assertEqual(stat.S_IMODE((ROOT / target).stat().st_mode), 0o755)
                self.assertIn(f'RTK_PROVIDER = "{provider}"', source)
                self.assertIn('[rtk_bin, "hook", RTK_PROVIDER]', source)
                self.assertIn("from helpers.audit import audit_log_event", source)
                self.assertIn("from helpers.common import emit_json, sanitize_log_field", source)
                self.assertIn("from helpers.observability import begin_hook_capture", source)
                self.assertNotIn(".copilot.hooks", source)
                self.assertNotIn(".gemini.hooks", source)
                sections = re.split(
                    r"# BEGIN PROVIDER ADAPTER\n.*?# END PROVIDER ADAPTER\n",
                    source,
                    flags=re.DOTALL,
                )
                self.assertEqual(len(sections), 2, f"Expected one provider adapter in {target}.")
                shared_sections.append(sections)

        self.assertEqual(
            shared_sections[0],
            shared_sections[1],
            "RTK outputs diverged outside their explicit provider adapters.",
        )
        self.assertIn('rewritten["permissionDecision"] = "allow"', rendered[RTK_TARGETS[0]])
        self.assertIn('hook_out["permissionDecision"] = "allow"', rendered[RTK_TARGETS[0]])
        self.assertNotIn('permissionDecision"] = "allow"', rendered[RTK_TARGETS[1]])

    def test_rtk_renderer_rejects_swapped_and_undeclared_target_paths(self) -> None:
        load_generator()
        from hooks.families import rtk
        from hooks.manifest import GeneratedTarget
        from hooks.providers import PROVIDERS

        invalid_targets = (
            (
                "swapped",
                GeneratedTarget("rtk", "copilot", Path(RTK_TARGETS[1])),
            ),
            (
                "undeclared",
                GeneratedTarget(
                    "rtk",
                    "copilot",
                    Path(".copilot/hooks/scripts/rtk-hook-undeclared.py"),
                ),
            ),
        )
        for case, target in invalid_targets:
            with self.subTest(case=case):
                with self.assertRaisesRegex(ValueError, "Unsupported RTK target/provider"):
                    rtk.render(PROVIDERS["copilot"], target)

    def test_help_and_usage_are_explicit_and_non_mutating(self) -> None:
        before = snapshot(ROOT)
        for flag in ("-h", "--help"):
            with self.subTest(flag=flag):
                result = self.run_cli(flag)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("Examples:", result.stdout)
                self.assertEqual(result.stderr, "")
                self.assertNotRegex(result.stdout + result.stderr, re.compile("\\x1b"))
        bare = self.run_cli()
        self.assertEqual(bare.returncode, 2)
        self.assertIn("Examples:", bare.stdout)
        self.assertIn("choose exactly one", bare.stderr)
        conflicting = self.run_cli("--check", "--write")
        self.assertEqual(conflicting.returncode, 2)
        self.assertEqual(before, snapshot(ROOT))

    def test_check_is_read_only_and_reports_missing_stale_and_undeclared_outputs(self) -> None:
        self.restore_checked_in_outputs()
        before = snapshot(ROOT)
        fresh = self.run_cli("--check")
        self.assertEqual(fresh.returncode, 0, fresh.stderr)
        self.assertEqual(fresh.stdout, "Generated hooks are current (25 files).\n")
        self.assertEqual(fresh.stderr, "")
        self.assertEqual(before, snapshot(ROOT))

        stale = ROOT / TARGETS[0]
        stale.write_text("stale\n", encoding="utf-8")
        expected_after_manual_edit = snapshot(ROOT)
        result = self.run_cli("--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn(TARGETS[0], result.stdout)
        self.assertEqual(result.stderr, "")
        self.assertEqual(expected_after_manual_edit, snapshot(ROOT))

        undeclared = ROOT / ".copilot/hooks/scripts/obsolete-generated.py"
        undeclared.write_text("#!/usr/bin/env python3\n" + OWNERSHIP, encoding="utf-8")
        result = self.run_cli("--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn(undeclared.relative_to(ROOT).as_posix(), result.stdout)
        undeclared.unlink()

    def test_windows_check_ignores_posix_executable_mode(self) -> None:
        generator = load_generator()
        outputs = generator.render_all(ROOT)
        target = ROOT / TARGETS[0]
        target.chmod(0o644)

        self.assertIn(PurePosixPath(TARGETS[0]), generator.check_outputs(ROOT, outputs).stale_paths)
        with mock.patch.object(generator.os, "name", "nt"):
            self.assertTrue(generator.check_outputs(ROOT, outputs).is_current)

    def test_write_repairs_outputs_and_is_idempotent_from_any_directory(self) -> None:
        target = ROOT / TARGETS[0]
        target.write_text("stale\n", encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli("--write", cwd=Path(directory))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(TARGETS[0], result.stdout)
        self.assertEqual(result.stderr, "")
        after_first_write = snapshot(ROOT)
        second = self.run_cli("--write")
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(second.stdout, "Generated hooks already current (25 files).\n")
        self.assertEqual(after_first_write, snapshot(ROOT))
        for target_path in TARGETS:
            content = (ROOT / target_path).read_text(encoding="utf-8")
            self.assertTrue(content.startswith("#!/usr/bin/env python3\n" + OWNERSHIP))
            self.assertEqual(stat.S_IMODE((ROOT / target_path).stat().st_mode), 0o755)

    def test_rendered_pilot_preserves_the_pre_generation_runtime_body(self) -> None:
        generator = load_generator()
        outputs = generator.render_all(ROOT)
        self.assertEqual(
            tuple(output.target.output_path.as_posix() for output in outputs[:len(TARGETS)]),
            TARGETS,
        )
        for target in TARGETS:
            expected = "#!/usr/bin/env python3\n" + OWNERSHIP + PILOT_RUNTIME_BODY
            rendered = next(output.content.decode("utf-8") for output in outputs if output.target.output_path.as_posix() == target)
            self.assertEqual(rendered, expected)

    def test_common_and_audit_renderings_preserve_pre_generation_runtime_bodies(self) -> None:
        generator = load_generator()
        rendered = {
            output.target.output_path.as_posix(): output.content
            for output in generator.render_all(ROOT)
        }
        self.assertEqual(
            set(rendered) - set(TARGETS) - set(OBSERVABILITY_TARGETS) - set(TOOL_GUARD_TARGETS) - set(SECRET_SCANNER_TARGETS) - set(CODEX_HELPER_TARGETS) - set(AUTO_INGEST_TARGETS) - set(RTK_TARGETS),
            set(COMMON_AUDIT_TARGETS),
        )
        for target, expected_digest in COMMON_AUDIT_TARGETS.items():
            with self.subTest(target=target):
                content = rendered[target].decode("utf-8")
                lines = content.splitlines(keepends=True)
                self.assertEqual(lines[0], "#!/usr/bin/env python3\n")
                self.assertEqual(
                    lines[1],
                    f"# Generated from hooks/families/{'common' if target.endswith('common.py') else 'audit'}.py by scripts/generate-hooks.py. Do not edit.\n",
                )
                self.assertEqual(sha256("".join(lines[2:]).encode("utf-8")).hexdigest(), expected_digest)

    def test_observability_renderings_have_only_named_provider_differences(self) -> None:
        generator = load_generator()
        rendered = {
            output.target.output_path.as_posix(): output.content.decode("utf-8")
            for output in generator.render_all(ROOT)
        }
        copilot = rendered[OBSERVABILITY_TARGETS[0]]
        gemini = rendered[OBSERVABILITY_TARGETS[1]]
        self.assertTrue(copilot.startswith("#!/usr/bin/env python3\n"))
        self.assertTrue(gemini.startswith("#!/usr/bin/env python3\n"))
        normalized = copilot
        for copilot_value, gemini_value in OBSERVABILITY_ALLOWED_DIFFERENCES:
            self.assertEqual(copilot.count(copilot_value), 1)
            self.assertEqual(gemini.count(gemini_value), 1)
            normalized = normalized.replace(copilot_value, gemini_value)
        self.assertEqual(normalized, gemini, "Observability outputs diverged outside their named provider differences.")

    def test_tool_guard_renderings_share_one_policy_outside_provider_adapters(self) -> None:
        generator = load_generator()
        rendered = {
            output.target.output_path.as_posix(): output.content.decode("utf-8")
            for output in generator.render_all(ROOT)
        }
        self.assertTrue(set(TOOL_GUARD_TARGETS).issubset(rendered))

        shared_sections = []
        for target in TOOL_GUARD_TARGETS:
            source = rendered[target]
            self.assertTrue(source.startswith(
                "#!/usr/bin/env python3\n"
                "# Generated from hooks/families/tool_guard.py by scripts/generate-hooks.py. Do not edit.\n"
            ))
            sections = re.split(
                r"# BEGIN PROVIDER ADAPTER\n.*?# END PROVIDER ADAPTER\n",
                source,
                flags=re.DOTALL,
            )
            self.assertEqual(len(sections), 3, f"Expected two explicit provider adapters in {target}.")
            shared_sections.append(sections)

        self.assertEqual(
            shared_sections[0],
            shared_sections[1],
            "Tool Guardian policy diverged outside explicit provider adapters.",
        )

    def test_tool_guard_provider_neutral_matcher_and_allowlist_vectors(self) -> None:
        vectors = load_module(
            "tool_guard_vectors",
            ROOT / "scripts" / "fixtures" / "tool_guard_vectors.py",
        )
        modules = (
            load_module("copilot_tool_guard_vectors", ROOT / TOOL_GUARD_TARGETS[0]),
            load_module("gemini_tool_guard_vectors", ROOT / TOOL_GUARD_TARGETS[1]),
        )

        provider_outcomes = []
        for module in modules:
            self.assertEqual(len(module.PATTERNS), len(vectors.POSITIVE_MATCHER_VECTORS))
            for pattern, vector in zip(module.PATTERNS, vectors.POSITIVE_MATCHER_VECTORS, strict=True):
                with self.subTest(provider=module.__name__, vector=vector.name):
                    category, severity, matcher, suggestion = pattern
                    self.assertTrue(category)
                    self.assertTrue(severity)
                    self.assertTrue(suggestion)
                    self.assertEqual(matcher(vector.text, vector.text.lower()), vector.expected_match)
                    aggregated_threats = module.build_threats(vector.text)
                    self.assertIn(category, {threat["category"] for threat in aggregated_threats})
                    self.assertTrue(
                        all(set(threat) == {"category", "severity"} for threat in aggregated_threats)
                    )

            outcomes = []
            for name, text in vectors.NEGATIVE_AGGREGATION_VECTORS:
                with self.subTest(provider=module.__name__, vector=name):
                    threats = module.build_threats(text)
                    self.assertEqual(threats, [])
                    outcomes.append(threats)

            for name, text, expected_category in vectors.ADVERSARIAL_AGGREGATION_VECTORS:
                with self.subTest(provider=module.__name__, vector=name):
                    threats = module.build_threats(text)
                    self.assertIn(expected_category, {threat["category"] for threat in threats})

            for name, text in vectors.LIMIT_EXCEEDING_VECTORS:
                with self.subTest(provider=module.__name__, vector=name):
                    self.assertEqual(
                        module.build_threats(text),
                        [{"category": "input_limits", "severity": "critical"}],
                    )

            multi_threats = module.build_threats(vectors.MULTI_THREAT_TEXT)
            self.assertEqual(
                [(threat["category"], threat["severity"]) for threat in multi_threats],
                [("system_danger", "high"), ("system_danger", "high")],
            )
            sensitive_threats = module.build_threats(vectors.SENSITIVE_THREAT_TEXT)
            self.assertTrue(sensitive_threats)
            for threat in sensitive_threats:
                self.assertEqual(set(threat), {"category", "severity"})
            serialized_sensitive_output = json.dumps(
                {
                    "threats": sensitive_threats,
                    "reason": module.build_block_reason("bash", sensitive_threats),
                }
            )
            for sensitive_value in vectors.FAKE_SENSITIVE_VALUES:
                self.assertNotIn(sensitive_value, serialized_sensitive_output)
            allowlist = module.parse_allowlist(vectors.ALLOWLIST_RAW)
            self.assertEqual(
                tuple((entry["tool"], entry["input"]) for entry in allowlist),
                vectors.ALLOWLIST_ENTRIES,
            )
            self.assertTrue(module.allowlist_contains("Bash", f"  {vectors.ALLOWLIST_INPUT}  ", allowlist))
            self.assertFalse(module.allowlist_contains("write_file", vectors.ALLOWLIST_INPUT, allowlist))
            self.assertFalse(module.allowlist_contains("bash", f"echo safe && {vectors.ALLOWLIST_INPUT}", allowlist))
            self.assertFalse(module.allowlist_contains("bash", f"{vectors.ALLOWLIST_INPUT} && echo unsafe", allowlist))
            self.assertFalse(module.allowlist_contains("bash", vectors.ALLOWLIST_INPUT.upper(), allowlist))
            self.assertEqual(module.parse_allowlist(None), [])
            self.assertEqual(module.parse_allowlist(""), [])
            self.assertEqual(module.parse_allowlist(vectors.ALLOWLIST_INPUT), [])
            self.assertEqual(module.parse_allowlist('[{"tool":"bash"}]'), [])
            for separator in ("\n", "\r", "\t", r"\n"):
                separated_input = f"{vectors.ALLOWLIST_INPUT}{separator}echo safe"
                encoded_allowlist = json.dumps([{"tool": "bash", "input": separated_input}])
                self.assertEqual(module.parse_allowlist(encoded_allowlist), [])
                self.assertFalse(module.allowlist_contains("bash", separated_input, allowlist))
            for allowlisted_input, compatibility_input in vectors.ALLOWLIST_COMPATIBILITY_PAIRS:
                compatibility_allowlist = module.parse_allowlist(
                    json.dumps([{"tool": "bash", "input": allowlisted_input}])
                )
                self.assertFalse(
                    module.allowlist_contains("bash", compatibility_input, compatibility_allowlist)
                )
            internal_spacing = vectors.ALLOWLIST_INPUT.replace(" ", "  ", 1)
            self.assertFalse(module.allowlist_contains("bash", internal_spacing, allowlist))

            input_key = module.TOOL_INPUT_KEYS[0]
            structured_inputs = module.read_tool_scan_inputs(
                {
                    input_key: {
                        "request": {"query": vectors.STRUCTURED_DESTRUCTIVE_QUERY},
                        "options": {"timeout": 5},
                    }
                }
            )
            self.assertIn(vectors.STRUCTURED_DESTRUCTIVE_QUERY, structured_inputs)
            self.assertEqual(
                module.build_input_threats("database_query", structured_inputs),
                [{"category": "database_destruction", "severity": "high"}],
            )
            safe_structured_inputs = module.read_tool_scan_inputs(
                {
                    input_key: {
                        "request": {"query": vectors.STRUCTURED_SAFE_QUERY},
                        "options": {"timeout": 5},
                    }
                }
            )
            self.assertEqual(module.build_input_threats("database_query", safe_structured_inputs), [])
            overdeep: object = "safe"
            for _ in range(module.MAX_STRUCTURED_DEPTH + 1):
                overdeep = {"nested": overdeep}
            with self.assertRaises(module.ScanLimitExceeded):
                module.read_tool_scan_inputs({input_key: overdeep})
            provider_outcomes.append((outcomes, multi_threats, allowlist))

        self.assertEqual(provider_outcomes[0], provider_outcomes[1])

    def test_secret_scanner_renderings_share_policy_outside_provider_adapters(self) -> None:
        from hooks.families.allowlist import ALLOWLIST_SOURCE

        generator = load_generator()
        rendered = {
            output.target.output_path.as_posix(): output.content.decode("utf-8")
            for output in generator.render_all(ROOT)
        }
        self.assertTrue(set(SECRET_SCANNER_TARGETS).issubset(rendered))

        shared_sections = []
        for target in SECRET_SCANNER_TARGETS:
            source = rendered[target]
            self.assertTrue(source.startswith(
                "#!/usr/bin/env python3\n"
                "# Generated from hooks/families/scan_secrets.py by scripts/generate-hooks.py. Do not edit.\n"
            ))
            sections = re.split(
                r"# BEGIN PROVIDER ADAPTER\n.*?# END PROVIDER ADAPTER\n",
                source,
                flags=re.DOTALL,
            )
            self.assertEqual(len(sections), 3, f"Expected two explicit provider adapters in {target}.")
            self.assertNotIn('"permissionDecision": "deny"', "".join(sections))
            self.assertNotIn('"decision": "deny"', "".join(sections))
            self.assertEqual(source.count(ALLOWLIST_SOURCE), 1)
            shared_sections.append(sections)

        for target in TOOL_GUARD_TARGETS:
            self.assertEqual(rendered[target].count(ALLOWLIST_SOURCE), 1)

        self.assertEqual(
            shared_sections[0],
            shared_sections[1],
            "Secret scanner policy diverged outside explicit provider adapters.",
        )

    def test_secret_scanner_provider_neutral_detection_and_allowlist_vectors(self) -> None:
        vectors = load_module(
            "secret_scanner_vectors",
            ROOT / "scripts" / "fixtures" / "secret_scanner_vectors.py",
        )
        modules = (
            load_module("copilot_secret_scanner_vectors", ROOT / SECRET_SCANNER_TARGETS[0]),
            load_module("gemini_secret_scanner_vectors", ROOT / SECRET_SCANNER_TARGETS[1]),
        )

        provider_outcomes = []
        for module in modules:
            patterns = {name: (severity, regex) for name, severity, regex in module.PATTERNS}
            outcomes = []
            for name, text, expected_severity, expected_redaction in vectors.PATTERN_VECTORS:
                with self.subTest(provider=module.__name__, vector=name):
                    severity, regex = patterns[name]
                    match = regex.search(text)
                    self.assertIsNotNone(match)
                    assert match is not None
                    self.assertEqual(severity, expected_severity)
                    self.assertEqual(module.redact_match(match.group(0)), expected_redaction)
                    outcomes.append((name, severity, expected_redaction))
            for text in vectors.NEGATIVE_PATTERN_VECTORS:
                with self.subTest(provider=module.__name__, negative=text):
                    self.assertFalse(any(regex.search(text) for _severity, regex in patterns.values()))
            for path, expected in vectors.CREDENTIAL_PATH_VECTORS:
                self.assertEqual(module.is_credential_path(path), expected)
            for path, expected in vectors.ENV_PATH_VECTORS:
                self.assertEqual(module.is_env_path(path), expected)
            self.assertTrue(module.is_text_candidate("notes.txt", b"safe text\n"))
            self.assertFalse(module.is_text_candidate("image.bin", b"safe\x00binary"))
            self.assertEqual(module.enumerate_file_lines("one\ntwo\n"), [(1, "one"), (2, "two")])
            process = mock.Mock()
            process.stdout = io.BytesIO(b"")
            process.wait.return_value = 0
            with mock.patch("subprocess.Popen", return_value=process) as run:
                self.assertEqual(module.run_git(["status"], cwd=ROOT), "")
            invocation = run.call_args
            self.assertEqual(invocation.args[0], ["git", "status"])
            self.assertEqual(invocation.kwargs["env"]["GIT_TERMINAL_PROMPT"], "0")
            self.assertEqual(invocation.kwargs["env"]["GIT_ASKPASS"], "")
            self.assertEqual(invocation.kwargs["env"]["GIT_LITERAL_PATHSPECS"], "1")

            allowlist = module.parse_allowlist(vectors.ALLOWLIST_RAW)
            self.assertEqual(
                tuple((entry["tool"], entry["input"]) for entry in allowlist),
                vectors.ALLOWLIST_ENTRIES,
            )
            self.assertTrue(
                module.allowlist_contains("SCAN_SECRETS", f"  {vectors.ALLOWLIST_INPUT}  ", allowlist)
            )
            self.assertFalse(module.allowlist_contains("tool_guard", vectors.ALLOWLIST_INPUT, allowlist))
            self.assertFalse(
                module.allowlist_contains(
                    "scan_secrets", f"prefix:{vectors.ALLOWLIST_INPUT}", allowlist
                )
            )
            self.assertEqual(module.parse_allowlist(vectors.ALLOWLIST_INPUT), [])
            self.assertEqual(module.parse_allowlist('[{"tool":"scan_secrets"}]'), [])
            separated = f"{vectors.ALLOWLIST_INPUT}\\nextra"
            self.assertEqual(
                module.parse_allowlist(json.dumps([{"tool": "scan_secrets", "input": separated}])),
                [],
            )
            provider_outcomes.append((outcomes, allowlist))

        self.assertEqual(provider_outcomes[0], provider_outcomes[1])

    def test_secret_scanner_git_failures_are_not_clean_results(self) -> None:
        modules = (
            load_module("copilot_secret_scanner_git_errors", ROOT / SECRET_SCANNER_TARGETS[0]),
            load_module("gemini_secret_scanner_git_errors", ROOT / SECRET_SCANNER_TARGETS[1]),
        )
        commands = (
            ["diff", "--name-only", "--"],
            ["ls-files", "--others"],
            ["show", ":notes.txt"],
        )

        for module in modules:
            for command in commands:
                with self.subTest(provider=module.__name__, command=command[0], failure="exit"):
                    process = mock.Mock()
                    process.stdout = io.BytesIO(b"")
                    process.wait.return_value = 9
                    with mock.patch("subprocess.Popen", return_value=process):
                        with self.assertRaises(module.GitCommandError):
                            module.run_git(command, cwd=ROOT)
                with self.subTest(provider=module.__name__, command=command[0], failure="launch"):
                    with mock.patch("subprocess.Popen", side_effect=OSError("unavailable")):
                        with self.assertRaises(module.GitCommandError):
                            module.run_git(command, cwd=ROOT)

    def test_secret_scanner_git_output_and_cumulative_deadline_are_bounded(self) -> None:
        modules = (
            load_module("copilot_secret_scanner_git_bounds", ROOT / SECRET_SCANNER_TARGETS[0]),
            load_module("gemini_secret_scanner_git_bounds", ROOT / SECRET_SCANNER_TARGETS[1]),
        )

        with tempfile.TemporaryDirectory() as directory:
            fake_bin = Path(directory)
            git_path = fake_bin / "git"
            original_path = os.environ.get("PATH", "")
            bounded_path = f"{fake_bin}{os.pathsep}{original_path}"

            for module in modules:
                pid_path = fake_bin / f"{module.__name__}.pid"
                git_path.write_text(
                    "#!/usr/bin/env python3\n"
                    "import os\n"
                    "import time\n"
                    "from pathlib import Path\n"
                    "Path(os.environ['GIT_TEST_PID_PATH']).write_text(str(os.getpid()))\n"
                    "os.write(1, b'x' * 2048)\n"
                    "time.sleep(10)\n",
                    encoding="utf-8",
                )
                git_path.chmod(0o755)
                with self.subTest(provider=module.__name__, case="output-cap"):
                    with mock.patch.dict(
                        os.environ,
                        {"PATH": bounded_path, "GIT_TEST_PID_PATH": str(pid_path)},
                    ):
                        with mock.patch.object(module, "MAX_GIT_OUTPUT_BYTES", 1024):
                            started = time.monotonic()
                            with self.assertRaises(module.ScanLimitExceeded):
                                module.run_git(
                                    ["status"],
                                    cwd=ROOT,
                                    deadline=time.monotonic() + 2.0,
                                )
                            self.assertLess(time.monotonic() - started, 1.0)
                    stopped_pid = int(pid_path.read_text(encoding="utf-8"))
                    with self.assertRaises(ProcessLookupError):
                        os.kill(stopped_pid, 0)

                git_path.write_text(
                    "#!/usr/bin/env bash\n"
                    "sleep 0.15\n"
                    "printf 'ok\\n'\n",
                    encoding="utf-8",
                )
                git_path.chmod(0o755)
                with self.subTest(provider=module.__name__, case="cumulative-deadline"):
                    deadline = time.monotonic() + 0.25
                    with mock.patch.dict(os.environ, {"PATH": bounded_path}):
                        self.assertEqual(
                            module.run_git(["status"], cwd=ROOT, deadline=deadline),
                            "ok\n",
                        )
                        with self.assertRaises(module.ScanLimitExceeded):
                            module.run_git(["status"], cwd=ROOT, deadline=deadline)

    def test_secret_scanner_parses_git_paths_and_diff_lines_without_ambiguity(self) -> None:
        modules = (
            load_module("copilot_secret_scanner_git_parsing", ROOT / SECRET_SCANNER_TARGETS[0]),
            load_module("gemini_secret_scanner_git_parsing", ROOT / SECRET_SCANNER_TARGETS[1]),
        )
        cached_output = b"shared.txt\0"
        worktree_output = b"shared.txt\0"
        untracked_output = b"line\nbreak.txt\0tab\tname.txt\0nonutf-\xff.txt\0"
        diff_output = (
            b"diff --git a/notes.txt b/notes.txt\n"
            b"--- a/notes.txt\n"
            b"+++ b/notes.txt\n"
            b"@@ -0,0 +1,2 @@\n"
            b"+first\n"
            b"+++starts-with-two-plus\n"
        )

        for module in modules:
            with self.subTest(provider=module.__name__, behavior="paths"):
                expected_candidates = sorted(
                    (
                        (module.CANDIDATE_STAGED, "shared.txt"),
                        (module.CANDIDATE_WORKTREE, "shared.txt"),
                        (module.CANDIDATE_UNTRACKED, "line\nbreak.txt"),
                        (module.CANDIDATE_UNTRACKED, "tab\tname.txt"),
                        (module.CANDIDATE_UNTRACKED, os.fsdecode(b"nonutf-\xff.txt")),
                    ),
                    key=lambda candidate: (candidate[1], candidate[0]),
                )
                with mock.patch.object(
                    module,
                    "run_git",
                    side_effect=(cached_output, worktree_output, untracked_output),
                ) as run:
                    self.assertEqual(
                        module.collect_files(ROOT, "diff", True),
                        expected_candidates,
                    )
                cached_args = run.call_args_list[0].args[0]
                worktree_args = run.call_args_list[1].args[0]
                ls_args = run.call_args_list[2].args[0]
                self.assertIn("-z", cached_args)
                self.assertIn("--cached", cached_args)
                self.assertIn("HEAD", cached_args)
                self.assertIn("-z", worktree_args)
                self.assertNotIn("--cached", worktree_args)
                self.assertNotIn("HEAD", worktree_args)
                self.assertIn("-z", ls_args)
                self.assertIn("--no-color", cached_args)
                self.assertIn("--no-textconv", worktree_args)

            with self.subTest(provider=module.__name__, behavior="diff"):
                with mock.patch.object(module, "run_git", return_value=diff_output) as run:
                    self.assertEqual(
                        module.emit_diff_added_lines(
                            ROOT,
                            "notes.txt",
                            module.CANDIDATE_WORKTREE,
                            root_has_head=True,
                        ),
                        [(1, "first"), (2, "++starts-with-two-plus")],
                    )
                args = run.call_args.args[0]
                self.assertIn("--no-color", args)
                self.assertIn("--no-textconv", args)
                self.assertIn("--output-indicator-new=+", args)
                self.assertNotIn("--cached", args)
                self.assertNotIn("HEAD", args)

            with self.subTest(provider=module.__name__, behavior="staged-index"):
                with mock.patch.object(module, "run_git", side_effect=(b"5\n", b"token")) as run:
                    self.assertEqual(
                        module.read_candidate_bytes(
                            ROOT,
                            "0:notes.env",
                            module.CANDIDATE_STAGED,
                        ),
                        b"token",
                    )
                self.assertEqual(run.call_args_list[0].args[0][-1], ":./0:notes.env")
                self.assertEqual(run.call_args_list[1].args[0][-1], ":./0:notes.env")

    def test_secret_scanner_rejects_unsafe_or_oversized_candidate_files(self) -> None:
        modules = (
            load_module("copilot_secret_scanner_file_safety", ROOT / SECRET_SCANNER_TARGETS[0]),
            load_module("gemini_secret_scanner_file_safety", ROOT / SECRET_SCANNER_TARGETS[1]),
        )

        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            repo = parent / "repo"
            repo.mkdir()
            (parent / "outside.txt").write_text("outside", encoding="utf-8")
            (repo / "regular.txt").write_text("inside", encoding="utf-8")

            for module in modules:
                with self.subTest(provider=module.__name__, case="regular"):
                    self.assertEqual(
                        module.read_candidate_bytes(repo, "regular.txt", "diff"),
                        b"inside",
                    )
                with self.subTest(provider=module.__name__, case="escape"):
                    with self.assertRaises(module.ScanSecurityError):
                        module.read_candidate_bytes(repo, "../outside.txt", "diff")
                oversized = repo / "oversized.bin"
                oversized.write_bytes(b"x" * (module.MAX_FILE_BYTES + 1))
                with self.subTest(provider=module.__name__, case="oversized"):
                    with self.assertRaises(module.ScanLimitExceeded):
                        module.read_candidate_bytes(repo, "oversized.bin", "diff")
                oversized.unlink()
                if hasattr(os, "symlink"):
                    linked = repo / "linked.txt"
                    linked.symlink_to(parent / "outside.txt")
                    with self.subTest(provider=module.__name__, case="symlink"):
                        with self.assertRaises(module.ScanSecurityError):
                            module.read_candidate_bytes(repo, "linked.txt", "diff")
                    linked.unlink()

    def test_secret_scanner_enforces_file_count_total_bytes_and_time_limits(self) -> None:
        modules = (
            load_module("copilot_secret_scanner_limits", ROOT / SECRET_SCANNER_TARGETS[0]),
            load_module("gemini_secret_scanner_limits", ROOT / SECRET_SCANNER_TARGETS[1]),
        )
        for module in modules:
            too_many_paths = b"".join(
                f"file-{index}.txt".encode("ascii") + b"\0"
                for index in range(module.MAX_FILES + 1)
            )
            with self.subTest(provider=module.__name__, case="file-count"):
                with mock.patch.object(
                    module,
                    "run_git",
                    side_effect=(too_many_paths, b"", b""),
                ):
                    with self.assertRaises(module.ScanLimitExceeded):
                        module.collect_files(ROOT, "diff", True)
            with self.subTest(provider=module.__name__, case="total-bytes"):
                with self.assertRaises(module.ScanLimitExceeded):
                    module.enforce_scan_budget(10.0, module.MAX_TOTAL_BYTES + 1, now=10.0)
            with self.subTest(provider=module.__name__, case="elapsed-time"):
                with self.assertRaises(module.ScanLimitExceeded):
                    module.enforce_scan_budget(
                        10.0,
                        0,
                        now=10.0 + module.MAX_SCAN_SECONDS + 0.01,
                    )

    def test_secret_scanner_logs_are_owner_only_and_reject_links(self) -> None:
        modules = (
            load_module("copilot_secret_scanner_log_safety", ROOT / SECRET_SCANNER_TARGETS[0]),
            load_module("gemini_secret_scanner_log_safety", ROOT / SECRET_SCANNER_TARGETS[1]),
        )

        for module in modules:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                log_dir = root / "logs"
                log_dir.mkdir(mode=0o755)
                log_path = log_dir / "scan.log"
                arguments = {
                    "log_path": log_path,
                    "status": "clean",
                    "session_id": "safe-session",
                    "timestamp": "2026-09-17T07:30:00Z",
                    "mode": "warn",
                    "scope": "diff",
                    "repo_root_path": root,
                    "env_files": [],
                    "findings": [],
                }
                module.append_scan_log(**arguments)
                existing_size = log_path.stat().st_size
                with mock.patch.dict(
                    os.environ,
                    {
                        "AUDIT_LOG_MAX_BYTES": str(existing_size + 1),
                        "AUDIT_LOG_MAX_BACKUPS": "2",
                    },
                ):
                    module.append_scan_log(**arguments)

                self.assertEqual(stat.S_IMODE(log_dir.stat().st_mode), 0o700)
                self.assertEqual(stat.S_IMODE(log_path.stat().st_mode), 0o600)
                self.assertEqual(stat.S_IMODE((log_dir / "scan.log.lock").stat().st_mode), 0o600)
                self.assertEqual(stat.S_IMODE((log_dir / "scan.log.1").stat().st_mode), 0o600)

                oversized_arguments = {
                    **arguments,
                    "session_id": "x" * module.MAX_LOG_RECORD_BYTES,
                }
                with self.subTest(provider=module.__name__, case="oversized-record"):
                    with self.assertRaises(module.ScanLimitExceeded):
                        module.append_scan_log(**oversized_arguments)

                if hasattr(os, "symlink"):
                    log_path.unlink()
                    target = root / "outside.log"
                    target.write_text("unchanged\n", encoding="utf-8")
                    log_path.symlink_to(target)
                    with self.subTest(provider=module.__name__, case="linked-log"):
                        with self.assertRaises(module.ScanSecurityError):
                            module.append_scan_log(**arguments)
                    self.assertEqual(target.read_text(encoding="utf-8"), "unchanged\n")
                    log_path.unlink()
                    lock_path = log_dir / "scan.log.lock"
                    lock_path.unlink()
                    lock_path.symlink_to(target)
                    with self.subTest(provider=module.__name__, case="linked-lock"):
                        with self.assertRaises(module.ScanSecurityError):
                            module.append_scan_log(**arguments)
                    self.assertEqual(target.read_text(encoding="utf-8"), "unchanged\n")
                    lock_path.unlink()
                    linked_log_dir = root / "linked-logs"
                    linked_log_dir.symlink_to(log_dir, target_is_directory=True)
                    linked_dir_arguments = {
                        **arguments,
                        "log_path": linked_log_dir / "scan.log",
                    }
                    with self.subTest(provider=module.__name__, case="linked-directory"):
                        with self.assertRaises(module.ScanSecurityError):
                            module.append_scan_log(**linked_dir_arguments)

    def test_secret_scanner_log_lock_wait_is_bounded(self) -> None:
        try:
            import fcntl
        except ImportError:
            self.skipTest("POSIX flock is unavailable")

        modules = (
            load_module("copilot_secret_scanner_log_lock", ROOT / SECRET_SCANNER_TARGETS[0]),
            load_module("gemini_secret_scanner_log_lock", ROOT / SECRET_SCANNER_TARGETS[1]),
        )
        for module in modules:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                log_path = root / "logs" / "scan.log"
                log_path.parent.mkdir()
                lock_path = log_path.with_name("scan.log.lock")
                lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
                fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                try:
                    with mock.patch.object(module, "LOG_LOCK_TIMEOUT_SECONDS", 0.1):
                        started = time.monotonic()
                        with self.assertRaises(module.ScanLimitExceeded):
                            module.append_scan_log(
                                log_path=log_path,
                                status="clean",
                                session_id="locked",
                                timestamp="2026-09-17T07:31:00Z",
                                mode="block",
                                scope="diff",
                                repo_root_path=root,
                                env_files=[],
                                findings=[],
                            )
                        self.assertLess(time.monotonic() - started, 1.0)
                finally:
                    fcntl.flock(lock_fd, fcntl.LOCK_UN)
                    os.close(lock_fd)

    def test_rendering_rejects_unsafe_paths_and_invalid_python_before_writing(self) -> None:
        generator = load_generator()
        original = snapshot(ROOT)
        bad_path = generator.GeneratedTarget("send_event", "copilot", Path("outside.py"))
        with self.assertRaises(generator.GenerateError):
            generator.validate_target(ROOT, bad_path)
        bad_render = generator.RenderedOutput(
            generator.targets()[0], b"#!/usr/bin/env python3\nnot python !\n"
        )
        with self.assertRaises(generator.GenerateError):
            generator.validate_rendered_output(ROOT, bad_render)
        self.assertEqual(original, snapshot(ROOT))

    def test_rejects_symbolic_links_without_following_them(self) -> None:
        if not hasattr(os, "symlink"):
            self.skipTest("symbolic links are unavailable")
        target = ROOT / TARGETS[0]
        original = target.read_bytes()
        mode = stat.S_IMODE(target.stat().st_mode)
        outside = Path(tempfile.mkdtemp()) / "outside.py"
        outside.write_bytes(original)
        target.unlink()
        target.symlink_to(outside)
        try:
            result = self.run_cli("--check")
            self.assertEqual(result.returncode, 2)
            self.assertIn(TARGETS[0], result.stderr)
            self.assertEqual(outside.read_bytes(), original)
        finally:
            target.unlink()
            target.write_bytes(original)
            target.chmod(mode)
            shutil.rmtree(outside.parent)

    def test_lock_and_injected_write_failure_leave_outputs_unchanged(self) -> None:
        generator = load_generator()
        target = ROOT / TARGETS[0]
        target.write_text("stale\n", encoding="utf-8")
        before = snapshot(ROOT)
        lock = ROOT / generator.LOCK_NAME
        lock.write_text("held\n", encoding="utf-8")
        try:
            result = self.run_cli("--write")
            self.assertEqual(result.returncode, 2)
            self.assertIn("lock", result.stderr.lower())
            self.assertEqual(before | {lock.relative_to(ROOT).as_posix(): (b"held\n", stat.S_IMODE(lock.stat().st_mode))}, snapshot(ROOT))
        finally:
            lock.unlink()
        result = self.run_cli("--write", environment={"GENERATE_HOOKS_TEST_FAIL_AFTER_REPLACEMENTS": "1"})
        self.assertEqual(result.returncode, 2)
        self.assertIn("rollback", result.stderr.lower())
        self.assertEqual(before, snapshot(ROOT))
        self.assertFalse(lock.exists())
        result = self.run_cli("--write", environment={"GENERATE_HOOKS_TEST_INTERRUPT_AFTER_REPLACEMENTS": "1"})
        self.assertEqual(result.returncode, 130)
        self.assertEqual(before, snapshot(ROOT))
        self.assertFalse(lock.exists())


if __name__ == "__main__":
    unittest.main()
