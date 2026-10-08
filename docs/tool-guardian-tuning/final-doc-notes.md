# Tool Guardian documentation checks

This record preserves the formal `update-agent-docs` checks for Tool Guardian runtime source at `1a4610ad`; root owns the retained ExecPlan, handoff, dispatch audit, and acceptance evidence. Installed hooks and user-global configuration were not changed. The user owns the installer refresh and subsequent trust/live validation.

## Source reconciliation

Reviewed the canonical classifier, policy renderer, shell/Python inspection and redaction paths, generated-target manifest, both installer copy lists, public benchmark parsers/dispatch, aggregate suite registry, and repaired helper/root fixtures. Current rules and validation procedures are linked below. Read the canonical runtime source for exact native schemas and limits. The benchmark contract distinguishes guard-only RTK handling, externally supplied fingerprints, and replay preparation against the original inline source at `84eae394`.

The durable contract separates native data from executable or unsupported input, preserves bounded sink inspection and strict fallback, and limits patch protections to deletion and move sources. It makes no general destination-protection, saved-script-inspection, raw-JSON memory, installed-behavior, or blanket optimization-benefit claim. Historical failed latency/optimization observations and partial timed-out reviews remain historical evidence rather than acceptance or security approval.

The accepted source evidence remains in [cold-profile-final-comparison.json](evidence/cold-profile-final-comparison.json) and its raw reports. Both 147-case warm pairs pass, with maximum median deltas of -1.841/-0.727 ms and p95 deltas of +1.618/+2.445 ms. The original 7,350-launch cold report retains three failures; the exact 150-launch repeat covers all three and passes. All 90 resource cases pass at 25 samples/three warmups, with maximum runtime 49.085958 ms and peak macOS RSS 22,413,312 bytes. The focused 12 writer medians improve by 0.318-0.570 ms against the extracted checkpoint. Root separately retained the initial noisy four-observation concurrency result and the successful 25-batch-per-condition repeated comparison; source stayed frozen.

Native macOS correctness was established with Python 3.13.14 and 3.14.6. Native Windows remains unverified. The earlier aggregate result remains 39/41 in its historical report; the two repaired suites now pass independently, including the helper suite under the actual root sandbox with warnings as errors. The documentation pass does not replace those reports with a fabricated new aggregate result.

## Current guidance

- [Shared hook rules](../../.agents/instructions/hooks.md) route provider-specific work.
- [Tool Guardian rules](../../.agents/instructions/hooks-security.md) own security constraints, installation checks, and decoding boundaries.
- [Security validation](../../.agents/instructions/testing/hooks-security.md) owns correctness, benchmark, and evidence requirements.
- [Script rules](../../.agents/instructions/scripts.md) and [script validation](../../.agents/instructions/testing/scripts.md) cover helper changes.

## Representation and checks

The recorded pass applied `okf-authoring` after semantic changes using `references/profile.md`; the source-summary branch was not applicable. Local links and referenced headings were inspected, including the retained latency-contract anchor.

From the isolated documentation worktree, with `RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db`:

- `rtk proxy python3 scripts/lint-okf.py`: exit 0, no diagnostics, both canonical bundles checked.
- `rtk proxy python3 scripts/generate-hooks.py --check`: exit 0, `Generated hooks are current (29 files).`
- `rtk git diff --check`: exit 0, no whitespace findings.

That documentation-only pass covered nine authorized canonical documents and this record. It changed no source, generated hooks, tests, skills, immutable sources, protected AGENTS sections, or installed files. It did not rerun full suites or heavy benchmarks. The retained feature folder is preserved because historical retention was explicitly requested.
