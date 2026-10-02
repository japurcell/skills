# Final documentation pass

This is the single formal `update-agent-docs` pass for the completed Tool Guardian code session. It reconciles durable guidance with runtime source at `1a4610ad`; root owns the retained ExecPlan, handoff, dispatch audit, and acceptance evidence. Installed hooks and user-global configuration were not changed. The user owns the installer refresh and subsequent trust/live validation.

## Source reconciliation

Reviewed the canonical classifier, policy renderer, shell/Python inspection and redaction paths, generated-target manifest, both installer copy lists, public benchmark parsers/dispatch, aggregate suite registry, and repaired helper/root fixtures. The knowledge base now routes exact observed native schemas and current limits through `API_MAP.md`, required changes through hook/script instructions, installation and decoding caveats through hook known issues, and correctness/performance procedures through testing guidance. The benchmark contract distinguishes guard-only RTK handling, externally supplied fingerprints, and replay preparation against the original inline source at `84eae394`.

The durable contract separates native data from executable or unsupported input, preserves bounded sink inspection and strict fallback, and limits patch protections to deletion and move sources. It makes no general destination-protection, saved-script-inspection, raw-JSON memory, installed-behavior, or blanket optimization-benefit claim. Historical failed latency/optimization observations and partial timed-out reviews remain historical evidence rather than acceptance or security approval.

The accepted source evidence remains in [cold-profile-final-comparison.json](evidence/cold-profile-final-comparison.json) and its raw reports. Both 147-case warm pairs pass, with maximum median deltas of -1.841/-0.727 ms and p95 deltas of +1.618/+2.445 ms. The original 7,350-launch cold report retains three failures; the exact 150-launch repeat covers all three and passes. All 90 resource cases pass at 25 samples/three warmups, with maximum runtime 49.085958 ms and peak macOS RSS 22,413,312 bytes. The focused 12 writer medians improve by 0.318-0.570 ms against the extracted checkpoint. Root separately retained the initial noisy four-observation concurrency result and the successful 25-batch-per-condition repeated comparison; source stayed frozen.

Native macOS correctness was established with Python 3.13.14 and 3.14.6. Native Windows remains unverified. The earlier aggregate result remains 39/41 in its historical report; the two repaired suites now pass independently, including the helper suite under the actual root sandbox with warnings as errors. The documentation pass does not replace those reports with a fabricated new aggregate result.

## Routing result

- Added: This formal pass record only; no new canonical concept.
- Changed: Hook/script instructions; architecture, API, file and index maps; hook known issues; hook/script testing guidance.
- Split or moved: Moved the current schema/limit contract into the existing API map while keeping installed-copy and raw-decoding caveats in hook known issues.
- Deduplicated: Replaced stale source false-positive and 32,768-byte native-body descriptions with the current contract and focused links. Corrected the generated-target count from 26 to 29.
- Index updates: API-map routing in `INDEX.md` and maintained guardian files plus retained effort status in `FILE_MAP.md`.
- Remaining doc quality TODOs: None for this scoped pass.

## Representation and checks

Applied `okf-authoring` after semantic changes using `references/profile.md`; the source-summary branch is not applicable. Existing canonical paths and their frontmatter types remain stable: `Agent Instruction`, `Agent Memory`, `Knowledge Index`, `Known Issue`, and `Testing Guidance`. Local links and referenced headings were inspected, including the retained latency-contract anchor.

From the isolated documentation worktree, with `RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db`:

- `rtk proxy python3 scripts/lint-okf.py`: exit 0, no diagnostics, both canonical bundles checked.
- `rtk proxy python3 scripts/generate-hooks.py --check`: exit 0, `Generated hooks are current (29 files).`
- `rtk git diff --check`: exit 0, no whitespace findings.

The scoped diff contains only the nine authorized canonical documents and this record. No source, generated hooks, tests, skills, immutable sources, protected AGENTS sections, or installed files changed. No full suites or heavy benchmarks were rerun for documentation alone. The retained feature folder is preserved because historical retention was explicitly requested.
