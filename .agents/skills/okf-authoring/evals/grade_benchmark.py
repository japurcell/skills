#!/usr/bin/env python3

import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


def repository_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "scripts/lint-okf.py").is_file() and (candidate / "scripts/fixtures/okf-valid-repo").is_dir():
            return candidate
    raise RuntimeError("cannot locate repository root from hidden .agents skill path")


REPO_ROOT = repository_root()
FIXTURE_ROOT = REPO_ROOT / "scripts/fixtures/okf-valid-repo"
LINTER = REPO_ROOT / "scripts/lint-okf.py"
sys.path.insert(0, str(REPO_ROOT / "scripts/vendor"))
import yaml


TARGET_LISTS = {
    0: [
        (".agents/memory/telemetry.md", "Agent Memory"),
        (".agents/memory/INDEX.md", "Knowledge Index"),
        (".agents/memory/LOG.md", "Source Ingestion Log"),
        (".agents/memory/adrs/retention.md", "Architecture Decision"),
    ],
    1: [(".agents/instructions/hooks.md", "Agent Instruction")],
    2: [(".agents/memory/sources/pending-md.summary.md", "Source Summary")],
    3: [(".agents/memory/sources/example-md.summary.md", "Source Summary")],
    4: [(".agents/memory/testing/skills.md", "Testing Guidance")],
    5: [(".agents/memory/KNOWN_ISSUES.md", "Known Issue")],
    6: [("docs/outside.md", "out_of_scope")],
    7: [(".agents/memory/ARCHITECTURE.md", "Agent Memory")],
}
EXPECTED_BODIES = {
    ".agents/memory/telemetry.md": "# Telemetry\n\nRecord durable telemetry guidance.\n",
    ".agents/memory/INDEX.md": "# Index\n\nRoute canonical knowledge.\n",
    ".agents/memory/LOG.md": "# Log\n\nRecord source ingestion.\n",
    ".agents/memory/adrs/retention.md": "# Retention\n\nKeep stable paths.\n",
    ".agents/instructions/hooks.md": "# Hook Guidance\n\nRetain this sentence exactly.\n",
    ".agents/memory/sources/pending-md.summary.md": "# Pending example summary\n\nThis source summary is intentionally unresolved but structurally conforming.\n",
    ".agents/memory/sources/example-md.summary.md": "# Example source summary\n\nThe source demonstrates a completed manifest-backed summary.\n",
    ".agents/memory/testing/skills.md": "# Skills Testing\n\nRun targeted skill validation.\n",
    ".agents/memory/ARCHITECTURE.md": "# Architecture\n\nPreserve this canonical body.\n",
}
EXPECTED_EVAL_IDS = set(TARGET_LISTS)
EXPECTED_CONFIGS = {"with_skill", "without_skill"}
CHANGING_EVALS = {0, 1, 2, 3, 4, 7}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def read_json(path: Path) -> dict:
    try:
        value = json.loads(read_text(path))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def expectation(text: str, passed: bool, evidence: str) -> dict:
    return {"text": text, "passed": passed, "evidence": evidence}


def expected_type(path: str) -> str:
    if path.startswith(".agents/instructions/"):
        return "Agent Instruction"
    memory_path = path.removeprefix(".agents/memory/")
    if memory_path == "INDEX.md":
        return "Knowledge Index"
    if memory_path == "LOG.md":
        return "Source Ingestion Log"
    if memory_path == "KNOWN_ISSUES.md" or memory_path.startswith("known-issues/"):
        return "Known Issue"
    if memory_path == "TESTING_STRATEGY.md" or memory_path.startswith("testing/"):
        return "Testing Guidance"
    if memory_path.startswith("adrs/"):
        return "Architecture Decision"
    if memory_path.startswith("sources/") and memory_path.endswith(".summary.md"):
        return "Source Summary"
    return "Agent Memory"


def frontmatter(text: str) -> tuple[dict, str, str]:
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return {}, text, "missing frontmatter"
    try:
        metadata = yaml.safe_load(match.group(1))
    except yaml.YAMLError as error:
        return {}, text, f"invalid YAML: {error}"
    return (metadata if isinstance(metadata, dict) else {}), text[match.end():], ""


def files_under(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()} if root.is_dir() else set()


def snapshot(root: Path) -> dict[str, str]:
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in root.rglob("*") if path.is_file()}


def changed_paths(before: dict[str, str], after: dict[str, str]) -> list[str]:
    return sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))


def output_files(run_dir: Path) -> set[str]:
    return files_under(run_dir / "outputs/repo")


def expected_output_files(eval_id: int) -> set[str]:
    return {path for path, _ in TARGET_LISTS[eval_id]} if eval_id in CHANGING_EVALS else set()


def expected_changed_paths(eval_id: int) -> list[str]:
    return sorted(expected_output_files(eval_id))


def prepare_baseline(eval_id: int, sandbox: Path) -> None:
    if eval_id == 0:
        for path, _ in TARGET_LISTS[eval_id]:
            target = sandbox / path
            if target.exists():
                target.unlink()
        return
    if eval_id in {1, 2, 3, 4, 5, 7}:
        path = TARGET_LISTS[eval_id][0][0]
        target = sandbox / path
        target.parent.mkdir(parents=True, exist_ok=True)
        body = EXPECTED_BODIES.get(path, "# Known issues\n")
        target.write_text(body, encoding="utf-8")


def apply_model_output(run_dir: Path, sandbox: Path) -> None:
    output_root = run_dir / "outputs/repo"
    for source in output_root.rglob("*"):
        if source.is_symlink():
            raise ValueError(f"model output contains a symlink: {source.relative_to(output_root)}")
        if not source.is_file():
            continue
        relative = source.relative_to(output_root)
        destination = (sandbox / relative).resolve()
        try:
            destination.relative_to(sandbox.resolve())
        except ValueError as error:
            raise ValueError(f"model output escapes validation sandbox: {relative}") from error
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)


def run_linter(eval_id: int, sandbox: Path) -> dict:
    command = [str(LINTER), "--format", "json"] if eval_id != 7 else [str(sandbox / "scripts/lint-okf.py"), "--format", "json"]
    evidence = {
        "owner": "grade_benchmark.py",
        "eval_id": eval_id,
        "sandbox_cwd": str(sandbox),
        "command": command,
        "attempted": eval_id != 6,
        "exit_code": None,
        "stdout": "",
        "stderr": "",
        "execution_error": "",
    }
    if eval_id == 6:
        return evidence
    try:
        result = subprocess.run(command, cwd=sandbox, check=False, capture_output=True, text=True)
    except OSError as error:
        evidence["execution_error"] = f"{type(error).__name__}: {error}"
    else:
        evidence["exit_code"] = result.returncode
        evidence["stdout"] = result.stdout
        evidence["stderr"] = result.stderr
    return evidence


def harness_evidence(eval_id: int, run_dir: Path) -> dict:
    sandbox = run_dir / "validation-sandbox"
    if sandbox.is_symlink():
        raise ValueError("validation sandbox must not be a symlink")
    if sandbox.exists():
        shutil.rmtree(sandbox)
    shutil.copytree(FIXTURE_ROOT, sandbox)
    prepare_baseline(eval_id, sandbox)
    before = snapshot(sandbox)
    apply_model_output(run_dir, sandbox)
    evidence = run_linter(eval_id, sandbox)
    evidence["changed_paths"] = changed_paths(before, snapshot(sandbox))
    evidence_path = run_dir / "harness/lint-evidence.json"
    write_json(evidence_path, evidence)
    return evidence


def outcome_ok(outcome: dict, mode: str, completion: str, targets: list[tuple[str, str]], lint: tuple[object, str] | None) -> tuple[bool, str]:
    affected = [{"path": path, "type": type_name} for path, type_name in targets]
    base = outcome.get("mode") == mode and outcome.get("completion") == completion and outcome.get("affected") == affected
    if lint is None:
        lint_report = outcome.get("lint")
        no_lint = lint_report is None or lint_report == {"command": None, "exit_code": None, "outcome": "not_run"}
        return base and no_lint, json.dumps(outcome, sort_keys=True)
    value = outcome.get("lint")
    return base and value == {"command": "./scripts/lint-okf.py", "exit_code": lint[0], "outcome": lint[1]}, json.dumps(outcome, sort_keys=True)


def report_evidence_ok(outcome: dict, eval_id: int) -> tuple[bool, bool, str]:
    references = [] if eval_id == 6 else ["profile", "source-summaries"] if eval_id in {2, 3} else ["profile"]
    scoped_diff = outcome.get("scoped_diff")
    expected_outcome = "clean" if eval_id in CHANGING_EVALS else "no_changes"
    scoped_ok = (
        isinstance(scoped_diff, dict)
        and scoped_diff.get("outcome") == expected_outcome
        and sorted(scoped_diff.get("paths", [])) == expected_changed_paths(eval_id)
    )
    evidence = json.dumps({"references_loaded": outcome.get("references_loaded"), "scoped_diff": outcome.get("scoped_diff")}, sort_keys=True)
    return outcome.get("references_loaded") == references, scoped_ok, evidence


def actual_evidence_ok(eval_id: int, evidence: dict) -> tuple[bool, bool, str]:
    base = evidence.get("owner") == "grade_benchmark.py" and evidence.get("eval_id") == eval_id and evidence.get("sandbox_cwd", "").endswith("validation-sandbox")
    diff_ok = evidence.get("changed_paths") == expected_changed_paths(eval_id)
    if eval_id in {0, 1, 2, 3, 4}:
        lint_ok = evidence.get("attempted") is True and evidence.get("exit_code") == 0 and not evidence.get("stderr") and json.loads(evidence.get("stdout", "{}")) == {"schema_version": 1, "diagnostics": []}
    elif eval_id == 5:
        lint_ok = evidence.get("attempted") is True and evidence.get("exit_code") == 1 and not evidence.get("stderr")
    elif eval_id == 6:
        lint_ok = evidence.get("attempted") is False and evidence.get("exit_code") is None
    else:
        lint_ok = evidence.get("attempted") is True and evidence.get("exit_code") is None and "FileNotFoundError" in evidence.get("execution_error", "")
    return base and lint_ok, base and diff_ok, json.dumps(evidence, sort_keys=True)


def provenance_ok(repo: Path, summary_path: str, raw_path: str, draft: bool) -> tuple[bool, str]:
    metadata, _, error = frontmatter(read_text(repo / summary_path))
    sources = metadata.get("sources")
    if error or not isinstance(sources, list) or len(sources) != 1 or not isinstance(sources[0], dict):
        return False, error or json.dumps(metadata, sort_keys=True)
    resource = sources[0].get("resource")
    parsed = urlsplit(resource) if isinstance(resource, str) else None
    if not isinstance(resource, str) or not resource or parsed.scheme or resource.startswith("/"):
        return False, json.dumps(sources, sort_keys=True)
    resolved = ((repo / summary_path).parent / unquote(parsed.path)).resolve()
    expected = (repo / raw_path).resolve()
    status_ok = metadata.get("status") == "draft" if draft else "status" not in metadata
    return metadata.get("type") == "Source Summary" and bool(str(metadata.get("description", "")).strip()) and status_ok and resolved == expected and expected.is_file(), json.dumps(metadata, sort_keys=True)


def has_prohibited_claim(run_dir: Path) -> bool:
    paths = [run_dir / "response.md"]
    paths.extend(path for path in (run_dir / "outputs").rglob("*") if path.is_file() and path.name != "outcome.json")
    text = "\n".join(read_text(path).lower() for path in paths)
    return re.search(r"\b(?:completion|change|work|lint|conformance)\b.{0,24}\b(?:complete|completed|success|successful|verified|passed)\b", text) is not None


def composition_ok(outcome: dict) -> tuple[bool, str]:
    skill = read_text(REPO_ROOT / ".agents/skills/okf-authoring/SKILL.md")
    updater = read_text(REPO_ROOT / ".agents/skills/update-agent-docs/SKILL.md")
    expected = {"semantic_owner": "update-agent-docs", "representation_owner": "okf-authoring", "reverse_invocation": False}
    return outcome.get("orchestration") == expected and "invoke `okf-authoring`" in updater and "does not invoke `update-agent-docs`" in skill, json.dumps(outcome.get("orchestration"), sort_keys=True)


def grade_case(eval_id: int, run_dir: Path) -> list[dict]:
    outcome = read_json(run_dir / "outputs/outcome.json")
    evidence = harness_evidence(eval_id, run_dir)
    sandbox = run_dir / "validation-sandbox"
    targets = TARGET_LISTS[eval_id]
    results = [expectation("Produces exactly the allowed model output files.", output_files(run_dir) == expected_output_files(eval_id), ", ".join(sorted(output_files(run_dir))) or "no model output")]
    for path in sorted(expected_output_files(eval_id)):
        metadata, body, error = frontmatter(read_text(sandbox / path))
        results.extend([
            expectation(f"Uses the exact path-derived type and non-empty description for {path}.", metadata.get("type") == expected_type(path) and bool(str(metadata.get("description", "")).strip()), error or json.dumps(metadata, sort_keys=True)),
            expectation(f"Preserves the exact required Markdown body for {path}.", body == EXPECTED_BODIES[path], body or error or "missing document"),
        ])
    if eval_id == 2:
        ok, detail = provenance_ok(sandbox, targets[0][0], ".agents/sources/pending.md", draft=True)
        results.append(expectation("Preserves the fixture draft source-summary/raw pair.", ok, detail))
    if eval_id == 3:
        ok, detail = provenance_ok(sandbox, targets[0][0], ".agents/sources/example.md", draft=False)
        results.append(expectation("Preserves the fixture stable source-summary/raw pair.", ok, detail))
    lint_ok, diff_ok, actual = actual_evidence_ok(eval_id, evidence)
    results.extend([
        expectation("Actual linter result matches this scenario.", lint_ok, actual),
        expectation("Actual validation-sandbox diff has exactly the authorized paths.", diff_ok, actual),
    ])
    if eval_id in {0, 1, 2, 3, 4}:
        ok, detail = outcome_ok(outcome, "change", "complete", targets, (0, "clean"))
        results.append(expectation("Reports the expected complete outcome.", ok, detail))
    elif eval_id == 5:
        ok, detail = outcome_ok(outcome, "review", "incomplete", targets, (1, "nonconforming"))
        results.extend([expectation("Reports the expected incomplete review outcome.", ok, detail), expectation("Makes no completion or success claim.", not has_prohibited_claim(run_dir), "prohibited claim found" if has_prohibited_claim(run_dir) else "none")])
    elif eval_id == 6:
        ok, detail = outcome_ok(outcome, "out_of_scope", "not_applicable", targets, None)
        results.extend([expectation("Reports the expected outside-root outcome.", ok, detail), expectation("Makes no completion or success claim.", not has_prohibited_claim(run_dir), "prohibited claim found" if has_prohibited_claim(run_dir) else "none")])
    else:
        ok, detail = outcome_ok(outcome, "change", "unverified", targets, (None, "unavailable"))
        results.extend([expectation("Reports the expected unavailable-linter outcome.", ok, detail), expectation("Makes no completion or success claim.", not has_prohibited_claim(run_dir), "prohibited claim found" if has_prohibited_claim(run_dir) else "none")])
    references_ok, scoped_ok, detail = report_evidence_ok(outcome, eval_id)
    results.extend([expectation("Records the expected references loaded.", references_ok, detail), expectation("Reports the expected scoped diff.", scoped_ok, detail)])
    if eval_id == 4:
        ok, detail = composition_ok(outcome)
        results.append(expectation("Records one-way update-agent-docs composition.", ok, detail))
    return results


def eval_id(eval_dir: Path) -> int | None:
    value = read_json(eval_dir / "eval_metadata.json").get("eval_id")
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def validate_run_artifacts(eval_identifier: int, run_dir: Path) -> list[str]:
    errors = []
    for relative in ("response.md", "transcript.md", "timing.json", "outputs/outcome.json"):
        path = run_dir / relative
        if not path.is_file() or not read_text(path).strip():
            errors.append(f"missing or empty {relative}")
    timing = read_json(run_dir / "timing.json")
    duration_keys = ("duration_ms", "total_duration_seconds", "duration_seconds")
    durations = [timing[key] for key in duration_keys if key in timing]
    compatible_duration = bool(durations) and all(
        value is None
        or (isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0)
        for value in durations
    )
    if not compatible_duration:
        errors.append("invalid timing.json benchmark schema")
    repo = run_dir / "outputs/repo"
    if repo.is_symlink() or any(path.is_symlink() for path in repo.rglob("*")):
        errors.append("model output must not contain symlinks")
    files = output_files(run_dir)
    for relative in sorted(expected_output_files(eval_identifier) - files):
        errors.append(f"missing expected output outputs/repo/{relative}")
    for relative in sorted(files - expected_output_files(eval_identifier)):
        errors.append(f"unexpected output outputs/repo/{relative}")
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 .agents/skills/okf-authoring/evals/grade_benchmark.py <iteration-dir>")
        return 1
    iteration = Path(sys.argv[1])
    if not iteration.is_dir():
        print(f"Iteration directory not found: {iteration}")
        return 1
    eval_dirs = sorted(path for path in iteration.iterdir() if path.is_dir() and path.name.startswith("eval-"))
    identifiers = {identifier for path in eval_dirs if (identifier := eval_id(path)) is not None}
    if identifiers != EXPECTED_EVAL_IDS:
        missing, unexpected = sorted(EXPECTED_EVAL_IDS - identifiers), sorted(identifiers - EXPECTED_EVAL_IDS)
        if missing:
            print(f"Invalid benchmark: missing eval ids {missing}")
        if unexpected:
            print(f"Invalid benchmark: unexpected eval ids {unexpected}")
        return 1
    for eval_dir in eval_dirs:
        identifier = eval_id(eval_dir)
        configs = {path.name for path in eval_dir.iterdir() if path.is_dir()}
        if configs != EXPECTED_CONFIGS:
            print(f"Invalid benchmark: eval {identifier} configurations missing={sorted(EXPECTED_CONFIGS - configs)} unexpected={sorted(configs - EXPECTED_CONFIGS)}")
            return 1
        for config in sorted(EXPECTED_CONFIGS):
            run_dirs = sorted((eval_dir / config).glob("run-*"))
            if not run_dirs:
                print(f"Invalid benchmark: eval {identifier} {config} has no run-* directory")
                return 1
            for run_dir in run_dirs:
                errors = validate_run_artifacts(identifier, run_dir)
                if errors:
                    print(f"Invalid benchmark: eval {identifier} {config}/{run_dir.name}: {'; '.join(errors)}")
                    return 1
    runs = 0
    for eval_dir in eval_dirs:
        identifier = eval_id(eval_dir)
        for config in sorted(EXPECTED_CONFIGS):
            for run_dir in sorted((eval_dir / config).glob("run-*")):
                expectations = grade_case(identifier, run_dir)
                passed = sum(item["passed"] for item in expectations)
                write_json(run_dir / "grading.json", {"expectations": expectations, "summary": {"passed": passed, "failed": len(expectations) - passed, "total": len(expectations), "pass_rate": round(passed / len(expectations), 2)}})
                runs += 1
    print(f"Wrote grading.json for {runs} run(s) in {iteration}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
