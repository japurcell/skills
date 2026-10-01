#!/usr/bin/env python3
"""Prepare, verify, and time clean full-process optional guard ablations.

Only trusted repository revisions supply variant code. Fixture operations are
inert JSON strings; they are never passed to a shell or execution tool.
"""
from __future__ import annotations

import argparse
import ast
import concurrent.futures
import hashlib
import importlib.util
import json
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from tool_guard_corpus import OPERATIONS, PROVIDERS, Fixture, decision, encode, envelope, fixtures, numeric, script_path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("high_rate_benchmark", ROOT / "scripts/benchmark-high-rate-hooks.py")
bench = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = bench
spec.loader.exec_module(bench)


def git_text(root: Path, revision: str, path: str) -> str:
    return subprocess.run(["git", "-C", str(root), "show", f"{revision}:{path}"],
                          check=True, capture_output=True, text=True).stdout


def policy_literal(source: str) -> str:
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "_POLICY_SOURCE" for target in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError("trusted canonical source lacks _POLICY_SOURCE")


def replace_functions(source: str, reference: str, names: set[str] | None = None) -> str:
    names = names or {"_match_recursive_rm_target", "_match_git_push"}
    old_lines = reference.splitlines(keepends=True)
    bodies = {node.name: "".join(old_lines[node.lineno - 1:node.end_lineno])
              for node in ast.parse(reference).body if isinstance(node, ast.FunctionDef) and node.name in names}
    lines = source.splitlines(keepends=True)
    nodes = [node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name in names]
    if set(bodies) != names or {node.name for node in nodes} != names:
        raise ValueError("trusted matcher extraction is incomplete")
    for node in sorted(nodes, key=lambda item: item.lineno, reverse=True):
        lines[node.lineno - 1:node.end_lineno] = [bodies[node.name]]
    rendered = "".join(lines)
    ast.parse(rendered)
    return rendered


def hashes(root: Path) -> dict[str, str]:
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for provider in PROVIDERS for path in sorted(script_path(root, provider).parent.rglob("*.py"))}


def prepare(root: Path, parent: Path, output: Path) -> dict:
    parent.mkdir(parents=True, exist_ok=True)
    variants = {name: parent / name for name in ("final", "common-before", "suffix-before")}
    for destination in variants.values():
        if destination.exists():
            raise ValueError(f"refusing to replace existing variant {destination}")
        for provider in PROVIDERS:
            relative = script_path(root, provider).parent.relative_to(root)
            shutil.copytree(root / relative, destination / relative,
                            ignore=shutil.ignore_patterns("__pycache__", "logs", "*.log", "*.ndjson"))
    for provider in PROVIDERS:
        common = script_path(root, provider).parent.relative_to(root) / "helpers/common.py"
        (variants["common-before"] / common).write_text(git_text(root, "5f1aa7e", str(common)), encoding="utf-8")
    reference = policy_literal(git_text(root, "9bcc6ff5", "hooks/families/tool_guard.py"))
    for provider in PROVIDERS:
        path = script_path(variants["suffix-before"], provider)
        path.write_text(replace_functions(path.read_text(encoding="utf-8"), reference), encoding="utf-8")
    fingerprints = {name: hashes(path) for name, path in variants.items()}
    changed = {name: [path for path, digest in entries.items() if digest != fingerprints["final"][path]]
               for name, entries in fingerprints.items() if name != "final"}
    for name, expected_suffix in (("common-before", "helpers/common.py"), ("suffix-before", "tool-guard.py")):
        expected = {str(script_path(root, provider).parent.relative_to(root) / expected_suffix) for provider in PROVIDERS}
        if set(changed[name]) != expected:
            raise ValueError(f"unexpected ablation source differences: {name}: {changed[name]}")
    manifest = {"source_revision": subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip(),
                "reference_revisions": {"common-before": "5f1aa7e", "suffix-before": "9bcc6ff5"},
                "variants": {name: str(path) for name, path in variants.items()}, "sha256": fingerprints,
                "changed_paths": changed, "construction": "copy final provider trees excluding runtime caches/logs; replace common helpers or two AST-bounded matcher functions from trusted git source"}
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def prepare_git(parent: Path, evidence: Path) -> dict:
    original = json.loads((evidence / "optimization-manifest.json").read_text(encoding="utf-8"))
    final = Path(original["variants"]["final"])
    before = parent / "git-before"
    if before.exists():
        raise ValueError("refusing to replace existing git variant")
    reference = policy_literal(git_text(ROOT, "9bcc6ff5", "hooks/families/tool_guard.py"))
    for provider in PROVIDERS:
        relative = script_path(final, provider).parent.relative_to(final)
        shutil.copytree(final / relative, before / relative, ignore=shutil.ignore_patterns("__pycache__", "logs", "*.log", "*.ndjson"))
        path = script_path(before, provider)
        path.write_text(replace_functions(path.read_text(encoding="utf-8"), reference, {"_match_git_push"}), encoding="utf-8")
    manifest = {**original, "variants": {"final": str(final), "git-before": str(before)},
                "sha256": {"final": hashes(final), "git-before": hashes(before)},
                "construction": "final rm suffix and cached quote-aware shell representation retained; only _match_git_push replaced from trusted9bcc6ff5 source"}
    manifest["changed_paths"] = {"git-before": [path for path, digest in manifest["sha256"]["git-before"].items() if digest != manifest["sha256"]["final"][path]]}
    expected = {str(script_path(final, provider).relative_to(final)) for provider in PROVIDERS}
    if set(manifest["changed_paths"]["git-before"]) != expected:
        raise ValueError("unexpected git-only source differences")
    (evidence / "optimization-git-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def controls() -> list[Fixture]:
    force = OPERATIONS["force_push_protected_branch"]
    remove = numeric(114, 109)
    commands = [
        ("rm-options-before-terminator", remove + " -rf -- /", "deny"),
        ("rm-options-after-terminator", remove + " -- -rf /", "allow"),
        ("rm-option-looking-operand", remove + " -rf -- safe", "allow"),
        ("rm-windows-home", remove + " -rf '%USERPROFILE%'", "deny"),
        ("git-options-with-values", "git -C demo " + force[4:], "deny"),
        ("git-quoted-option-value", "git -c 'alias.example=" + force + "' status", "deny"),
        ("git-readonly-literal", "rg -n '" + force + "' docs", "allow"),
        ("windows-launcher-strict", "rg.exe -n '" + force + "' docs", "deny"),
        ("quoted-substitution-data", "rg -n '$(" + force + ")' docs", "allow"),
        ("unquoted-substitution-execution", "echo $(" + force + ")", "deny"),
        ("force-refspec", numeric(103,105,116,32,112,117,115,104,32,111,114,105,103,105,110,32,43,72,69,65,68,58,114,101,102,115,47,104,101,97,100,115,47,109,97,105,110), "deny"),
        ("role-native-content", None, "allow"),
    ]
    result = [Fixture("control." + name, "Bash" if command is not None else "write_file",
                      {"command": command} if command is not None else {"file_path": "guardian-example.md", "content": force},
                      expected, expected, "optimization-control", "synthetic public semantic control")
              for name, command, expected in commands]
    for size in (64, 128, 250):
        for name, command in (("rm", " ".join([remove] * (size - 1) + ["safe"])),
                              ("git", "git" + " -c git" * ((size - 3) // 2) + " push safe" + (" safe" if size % 2 == 0 else ""))):
            pair = "danger.recursive_remove_root" if name == "rm" else "danger.force_push_protected_branch"
            result.append(Fixture(f"growth.{name}-{size}", "Bash", {"command": command}, "allow", "allow", "adverse-growth", f"synthetic repeated {name} token workload at {size} tokens", pair))
        head = [numeric(103,105,116), numeric(112,117,115,104)]
        safe = (head * (size // 2 - 1)) + ["safe", "safe"]
        dangerous = (head * ((size - 3) // 2)) + [numeric(45,45,102,111,114,99,101), "origin", numeric(109,97,105,110)]
        if len(dangerous) < size:
            dangerous.insert(-3, "safe")
        for name, tokens, expected in (("git-push", safe, "allow"), ("git-push-danger", dangerous, "deny")):
            result.append(Fixture(f"growth.{name}-{size}", "Bash", {"command": " ".join(tokens)}, expected, expected, "adverse-suffix-growth", "synthetic adjacent git/push arguments force old repeated tail traversal; no represented operation executed", "danger.force_push_protected_branch"))
    return result


def make_case(root: Path, provider: str, fixture: Fixture):
    return bench.Case(f"{provider}.guard.{fixture.name}", script_path(root, provider), encode(envelope(provider, fixture)),
                      "clean", {"GUARD_MODE": "block"}, fixture.candidate,
                      {"category": fixture.category, "source": fixture.source, "pair": fixture.pair})


def validate(manifest: dict, output: Path) -> dict:
    results = []
    included_controls = controls() if "git-before" in manifest["variants"] else [fixture for fixture in controls() if fixture.category != "adverse-suffix-growth"]
    with tempfile.TemporaryDirectory(prefix="guard-optimization-correctness-") as temporary:
        base = Path(temporary)
        repo = base / "repo"
        repo.mkdir()
        for variant, root in manifest["variants"].items():
            for provider in PROVIDERS:
                selected = [make_case(Path(root), provider, fixture) for fixture in fixtures() + included_controls]
                selected.extend(case for case in bench.guard_cases(Path(root), "candidate") if case.name == f"{provider}.guard.failure")
                for case in selected:
                    home = base / variant / case.name
                    home.mkdir(parents=True)
                    elapsed, code, response = bench.invoke(case, repo, home)
                    actual = decision(provider, response)
                    results.append({"variant": variant, "case": case.name, "input_bytes": len(case.payload),
                                    "payload_sha256": hashlib.sha256(case.payload).hexdigest(), "response": response,
                                    "expected": case.expected_decision, "actual": actual, "exit_code": code,
                                    "matches": code == 0 and actual == case.expected_decision})
    result = {"results": results, "passed": sum(row["matches"] for row in results),
              "failed": [row for row in results if not row["matches"]], "fixture_count_per_provider": len(fixtures()),
              "controls_per_provider": len(included_controls), "corpus_checks_per_variant": (len(fixtures()) + 1) * len(PROVIDERS)}
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def measure(manifest: dict, correctness: Path, group: str, output: Path) -> dict:
    verified = json.loads(correctness.read_text(encoding="utf-8"))
    if verified["failed"]:
        raise ValueError("correctness failed; timing prohibited")
    names = {"clean", "search.shell-literal", "writer.chars-8787-segments-183", "writer.lines-120-segments-139",
             "survey.json-stdin", "survey.python-subprocess", "patch.bytes-46899", "patch.lines-330",
             "write.examples.md", "danger.recursive_remove_root", "danger.force_push_protected_branch"}
    selected = [fixture for fixture in fixtures() if fixture.name in names] + [fixture for fixture in controls() if fixture.category == "adverse-growth"]
    if group == "git":
        selected = [fixture for fixture in controls() if fixture.name.startswith("growth.git-push-")]
    before = group + "-before"
    results, concurrency = [], []
    with tempfile.TemporaryDirectory(prefix="guard-optimization-timing-") as temporary:
        base = Path(temporary)
        repo = base / "repo"
        repo.mkdir()
        for run, variant in enumerate((before, "final", "final", before), 1):
            for provider in PROVIDERS:
                for fixture in selected:
                    case = make_case(Path(manifest["variants"][variant]), provider, fixture)
                    home = base / str(run) / case.name
                    home.mkdir(parents=True)
                    samples = []
                    for index in range(29):
                        elapsed, code, response = bench.invoke(case, repo, home)
                        bench.verify_outcome(case, code, response)
                        if index == 0:
                            first = elapsed
                        elif index > 3:
                            samples.append(elapsed)
                    results.append({"run": run, "variant": variant, "case": case.name, "input_bytes": len(case.payload),
                                    "payload_sha256": hashlib.sha256(case.payload).hexdigest(), "first_run_ms": first,
                                    "samples_ms": samples, "warm": bench.summary(samples), "expected_decision": case.expected_decision})
                    if fixture.name == "clean":
                        start = time.perf_counter_ns()
                        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
                            calls = list(pool.map(lambda _: bench.invoke(case, repo, home), range(4)))
                        batch_ms = (time.perf_counter_ns() - start) / 1_000_000
                        for _, code, response in calls:
                            bench.verify_outcome(case, code, response)
                        concurrency.append({"run": run, "variant": variant, "case": case.name, "workers": 4,
                                            "batch_ms": batch_ms, "samples_ms": [row[0] for row in calls],
                                            "individual": bench.summary([row[0] for row in calls])})
    result = {"environment": {"platform": platform.platform(), "python": platform.python_version(),
                               "python_executable": sys.executable, "logging": "fresh disposable provider-specific homes per run/case; reused for warm samples"},
              "method": {"group": group, "order": [before, "final", "final", before], "samples": 25, "warmups": 3,
                         "first_definition": "first process with fresh log home; OS file cache not cleared", "boundary": "complete hook subprocess through existing benchmark invoke API"},
              "manifest": manifest, "results": results, "concurrency": concurrency}
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def compare(evidence: Path) -> dict:
    result = {"method": "Before-minus-after deltas pair runs1/2 and4/3. Observed noise is the maximum per-run MAD or same-variant repeated-median span. Clear benefit/regression requires both median deltas to exceed that noise in the same direction. P95 and first observations remain separate.", "groups": {}}
    for group in ("common", "suffix", "git"):
        if not (evidence / f"optimization-{group}-timing.json").exists():
            continue
        report = json.loads((evidence / f"optimization-{group}-timing.json").read_text(encoding="utf-8"))
        comparisons = []
        for case in sorted({row["case"] for row in report["results"]}):
            rows = {row["run"]: row for row in report["results"] if row["case"] == case}
            before = [rows[index] for index in (1, 4)]
            after = [rows[index] for index in (2, 3)]
            medians = [[row["warm"]["median_ms"] for row in selected] for selected in (before, after)]
            deltas = [round(medians[0][index] - medians[1][index], 3) for index in (0, 1)]
            noise = max([row["warm"]["mad_ms"] for row in rows.values()] + [abs(values[0] - values[1]) for values in medians])
            verdict = "clear-benefit" if min(deltas) > noise else "clear-regression" if max(deltas) < -noise else "within-noise-or-inconclusive"
            if len({row["payload_sha256"] for row in rows.values()}) != 1:
                raise ValueError(f"unmatched input payload for {case}")
            comparisons.append({"case": case, "before_median_ms": medians[0], "after_median_ms": medians[1],
                                "paired_median_delta_ms": deltas, "observed_noise_ms": round(noise, 3), "verdict": verdict,
                                "before_p95_ms": [row["warm"]["p95_ms"] for row in before],
                                "after_p95_ms": [row["warm"]["p95_ms"] for row in after],
                                "before_mad_ms": [row["warm"]["mad_ms"] for row in before],
                                "after_mad_ms": [row["warm"]["mad_ms"] for row in after],
                                "before_first_ms": [row["first_run_ms"] for row in before],
                                "after_first_ms": [row["first_run_ms"] for row in after],
                                "input_bytes": rows[1]["input_bytes"], "payload_sha256": rows[1]["payload_sha256"]})
        result["groups"][group] = {"comparisons": comparisons, "verdict_counts": {name: sum(row["verdict"] == name for row in comparisons) for name in ("clear-benefit", "clear-regression", "within-noise-or-inconclusive")}, "concurrency": report["concurrency"]}
    (evidence / "optimization-comparison.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("prepare", "validate", "measure", "compare", "prepare-git", "validate-git", "measure-git"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--variant-parent", type=Path, default=Path("/private/tmp/tool-guardian-ablation-final-m4"))
    parser.add_argument("--evidence", type=Path, default=ROOT / "docs/tool-guardian-tuning/evidence")
    parser.add_argument("--group", choices=("common", "suffix"), default="common")
    args = parser.parse_args()
    args.evidence.mkdir(parents=True, exist_ok=True)
    manifest_path = args.evidence / "optimization-manifest.json"
    if args.phase == "prepare-git":
        prepare_git(args.variant_parent, args.evidence)
        return 0
    if args.phase.endswith("-git"):
        manifest_path = args.evidence / "optimization-git-manifest.json"
        args.phase = args.phase.removesuffix("-git")
        args.group = "git"
    if args.phase == "compare":
        result = compare(args.evidence)
        print(json.dumps({group: value["verdict_counts"] for group, value in result["groups"].items()}))
        return 0
    if args.phase == "prepare":
        prepare(args.root, args.variant_parent, manifest_path)
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if any(hashes(Path(root)) != manifest["sha256"][name] for name, root in manifest["variants"].items()):
            raise ValueError("frozen variant fingerprints changed")
        correctness = args.evidence / ("optimization-git-correctness.json" if args.group == "git" else "optimization-correctness.json")
        if args.phase == "validate":
            result = validate(manifest, correctness)
            print(json.dumps({"passed": result["passed"], "failed": result["failed"]}))
            return int(bool(result["failed"]))
        measure(manifest, correctness, args.group, args.evidence / f"optimization-{args.group}-timing.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
