# Brain Install Maintenance

Runtime instructions are in SKILL.md and references/migration.md. This README is for maintainers, not an installation dependency.

## Snapshot sources

The payload snapshots the six `.agents/skills/{brain,meditate,reflect,ruminate,todo,todo-refine}` trees, `brain/principles.md` and its 14 linked notes, and the Brain/End of Work Session Defined sections of root AGENTS.md. Principles and AGENTS sections remain byte-identical for fresh installs. Starter todos and four directory indexes are minimal; do not copy this repository's backlog or project notes.

Hook implementations come from `hooks/families/brain.py`; the indexer has one bundled output under `assets/skills/brain/scripts/`. Registration assets contain only brain handlers from `.github/hooks/hooks.json`, `.codex/hooks.json`, and `.gemini/settings.json`. Canonical registrations use the PATH alias `python` on every provider/platform, never the installer's absolute interpreter. Selected hooks require this alias to run Python 3.12+; inspection and apply validate it before writes. The same alias must be available in the provider's environment. Python-only Windows installations work without `python3`; python3-only or py-only hosts must explicitly provide a `python` alias before installing hooks. No automatic shell-specific fallback is claimed: Gemini exposes one host-shell command, while Copilot and Codex have platform-specific fields. Helpers also diagnose an old runtime interpreter without emitting non-JSON stdout.

Reinstallation upgrades only exact known brain registrations differing in their Python executable prefix (`python`, `python3`, `py -3`, or an absolute Python executable). All handler code, events, matchers, timeouts, and other fields must still match; changed or ambiguous registrations remain conflicts. Unrelated settings/handlers and configuration bytes on stable reruns are preserved. Helper-file conflicts still require reviewed, backed-up replacement, not a broad overwrite option. The installer rejects linked target ancestors; use canonical directory paths.

Both bundled hook helpers are declared in `hooks/manifest.py` and generated alongside the provider scripts. Edit the canonical family, then run `python3 scripts/generate-hooks.py --write` from the repository root; `--check` detects drift in the bundle as well as provider outputs. Do not hand-edit or maintain bundle-local forks of generated helpers. The portable bundle remains self-contained at runtime and does not require the repository generator.

Intentional skill adaptations: portable `snapshot.py` replaces `snapshot.sh`; callers use Python and invocation-owned temporary directories; ruminate documents only supported Claude/Codex extraction and its extractor emits UTF-8 diagnostics and output paths; brain carries its own manual index command; reflect uses installed principle paths and optional authoring fallbacks. Explicit-only meditate/ruminate flags remain. Ordinary activation references use skill names. Minor punctuation normalization follows repository conventions. Source skills are not modified.

Project-scoped extraction requires matching working-directory metadata; missing or empty attribution is excluded only when `--cwd` is supplied. Brain writes maintain curated navigation before root-index reconciliation, because generated inventory does not repair links below curated boundaries. Preserve these bundled workflow adaptations when refreshing their source snapshots.

When refreshing, map obligations before editing. Recheck resource closure, source parity with these explicit exceptions, and provider schemas. Do not copy historical live-provider claims into target instructions.

## Verification

From the repository root:

```text
python3 -m unittest discover -s skills/default/brain-install/tests -p 'test_*.py'
python3 skills/default/skill-creator/scripts/quick_validate.py skills/default/brain-install
python3 scripts/generate-hooks.py --check
python3 scripts/test-brain-hooks.py
```

The focused brain-hooks workflow runs Windows/Linux/macOS on Python 3.12/3.14. Process/config tests do not prove live-provider delivery. Installer subprocesses use relocated bundles; all test targets, histories, and homes live in disposable temporary directories outside the bundle. Retain actual native results before claiming cross-platform verification.

## Skill evaluations

Use `evals/evals.json` for three realistic scenarios: fresh/no hooks, legacy/scoped migration, and conflicting/repeated installation. Run each scenario in an isolated fixture twice, once with this SKILL.md and once without this skill or its migration reference. Both arms may access the same mechanical assets and installer. Keep the prompts, fixtures, and requested outputs identical between arms. The comparison measures the runtime procedure's added value, not exclusive access to payload files.

Use a disposable external workspace or sibling `brain-install-workspace/iteration-N/`. Each scenario has `eval_metadata.json`, `with_skill/run-1/outputs/`, and `without_skill/run-1/outputs/`. Put each run's `grading.json` and available `timing.json` beside its outputs directory: the aggregate tool discovers `run-*` directories. Retain targets and response/transcript evidence. Use deterministic assertions for files/configurations and direct semantic review for obligation coverage, scope, conditions, approvals, and source retirement. Missing outputs fail their applicable assertions. Validate any new grader against positive, negative, missing, and malformed artifacts before trusting its results.

Capture measured token/duration fields only when the runtime exposes them. Missing metrics remain explicitly unavailable; output character counts and zero defaults are not measured tokens or time. Use `skill-creator`'s `scripts.aggregate_benchmark` and `eval-viewer/generate_review.py` from the available skill installation, resolving that location rather than depending on this checkout. For example:

```text
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name brain-install
python <skill-creator-path>/eval-viewer/generate_review.py <workspace>/iteration-N --skill-name brain-install --benchmark <workspace>/iteration-N/benchmark.json --static <workspace>/iteration-N/review.html
```

Run the aggregate module from the resolved skill-creator directory. Inspect all assertion failures even if the grader exits zero. Review raw artifacts and distinguish sampled success from repeated-run variance; do not invent performance deltas. Preserve earlier valid failures and identify the selected run for each scenario.

The current aggregator cannot sum null timing values and substitutes zero or character-count proxies when metrics are absent. Preserve original evidence. For aggregation only, omit unavailable timing fields in presentation copies; then remove unmeasured metric rows from the presented benchmark/viewer. Keep raw aggregate output labeled raw. Do not turn those fallback values into performance claims.

## Provider references

Rechecked 2026-10-21: [Copilot hook reference](https://docs.github.com/en/copilot/reference/hooks-reference), [Codex hooks](https://learn.chatgpt.com/docs/hooks), and [Gemini hook reference](https://geminicli.com/docs/hooks/reference/). Preserve repo-level paths, independent selection, trust boundaries, and provider-specific event semantics when updating assets.
