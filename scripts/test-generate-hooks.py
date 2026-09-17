#!/usr/bin/env python3
"""Public CLI and transaction tests for the checked-in hook generator."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import re
from hashlib import sha256
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest


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
        self.assertEqual(fresh.stdout, "Generated hooks are current (12 files).\n")
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
        self.assertEqual(second.stdout, "Generated hooks already current (12 files).\n")
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
            set(rendered) - set(TARGETS) - set(OBSERVABILITY_TARGETS) - set(TOOL_GUARD_TARGETS),
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
                        all(set(threat) == {"category", "severity", "excerpt"} for threat in aggregated_threats)
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

            multi_threats = module.build_threats(vectors.MULTI_THREAT_TEXT)
            self.assertEqual(
                [(threat["category"], threat["severity"]) for threat in multi_threats],
                [("system_danger", "high"), ("system_danger", "high")],
            )
            sensitive_threats = module.build_threats(vectors.SENSITIVE_THREAT_TEXT)
            self.assertTrue(sensitive_threats)
            redacted_excerpt = module.redact_excerpt(vectors.SENSITIVE_THREAT_TEXT)
            self.assertLessEqual(len(redacted_excerpt), 160)
            for threat in sensitive_threats:
                self.assertEqual(set(threat), {"category", "severity", "excerpt"})
                self.assertLessEqual(len(threat["excerpt"]), 160)
            serialized_sensitive_output = json.dumps(
                {
                    "threats": sensitive_threats,
                    "reason": module.build_block_reason("bash", sensitive_threats),
                }
            )
            for sensitive_value in vectors.FAKE_SENSITIVE_VALUES:
                self.assertNotIn(sensitive_value, redacted_excerpt)
                self.assertNotIn(sensitive_value, serialized_sensitive_output)
            self.assertIn("[REDACTED]", serialized_sensitive_output)
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
            provider_outcomes.append((outcomes, multi_threats, allowlist))

        self.assertEqual(provider_outcomes[0], provider_outcomes[1])

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
