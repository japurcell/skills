# Tool Guardian tuning handoff

## Goal and next step

Complete every milestone in `docs/tool-guardian-tuning/ExecPlan.md` on private branch `codex/tool-guardian-tuning`. The user runs real installation later.

**Next step:** complete the formal milestone 5 documentation pass, integrate its clean private branch, synchronize final plan and handoff, and deliver the topic branch for review.

## Current state

- Frozen sanitizer repair integrated without conflicts at `1a4610ad60461e1bd00ed220af882c4cfa49ff32`. Root independently matched all 39 source hashes against both the committed manifest and candidate snapshot. Owned implementation worktree and branch were removed.
- Cold full matrix retains all 7,350 launches and its original three failures. The exact three-case repeat retains 150 launches and passes: Copilot writer-after +4.584/+4.758 ms, Gemini recursive remove current +1.738/+1.889 ms, Codex writer-before +4.650/+4.884 ms. No failed observation was removed.
- Resource report passes 90 cases with 25 samples and 3 warmups. Maximum elapsed 49.085958 ms, maximum native macOS peak RSS 22,413,312 bytes. All frozen source hashes remain identical.
- Warm B/C/C/B run completed. Both pairs pass all 147 cases. Maximum median deltas -1.841/-0.727 ms; maximum p95 deltas +1.618/+2.445 ms. All expected decisions and frozen hashes match. Raw reports, manifest and final comparison remain in feature evidence. No runtime jobs remain.
- Immutable original baseline `/private/tmp/tool-guardian-baseline`; exact repaired snapshot `/private/tmp/tool-guardian-profile-candidate`; extracted checkpoint `/private/tmp/tool-guardian-profile-checkpoint`. Preserve these snapshots and source/payload/runner/corpus hashes.
- Milestones 1 through 4 and repository fixture repair are complete. Milestone 5 is the remaining frontier. Root activated the formal final documentation pass once at19:53UTC; a fresh implementer follows.
- Aggregate repository verification passed 39/41 initially. The remaining physical-path and sandbox audit fixture repairs integrated at `a1f3280a`. Both repaired suites now pass in the actual shared-root sandbox: shell root resolution and 16 helper tests with DeprecationWarnings as errors. Assertions remain intact. No conflict-only reruns are required.

## Decisions and boundaries

Per provider and case, warm budget is +2 ms median/+5 ms p95. Fresh-copy cold budget with zero provider bytecode is +5 ms median/+10 ms p95. Finite resource ceiling is 500 ms. Retain original failures when repeating an isolated noisy case. Never pool providers, cherry-pick persistent violations, weaken inspection or raise budgets silently.

Policy extraction keeps byte-identical generated local helpers, explicit original exports and provider adapters. Both Codex installer lists deliver the helper. Missing/corrupt helpers deny in block and warn modes. Only ordinary Python bytecode is used.

The accepted five-line tool-name fast path runs after identical NFKC normalization, excludes credential token prefixes and preserves clipping. All 12 focused cold writer medians improve 0.318-0.570 ms against the exact checkpoint. Action redaction and executable inspection remain unchanged. Python 3.14.6 and native macOS 3.13.14 pass banners14, shell13, native13, limits16, corpus144, generator25 and freshness29. Native Windows is unavailable.

The prior literal-scan experiment had no attributable full-hook gain and failed cold budgets. Its runtime changes were restored; the rejected patch, failed reports and useful public characterizations remain preserved at `15e323e5`. Historical zero-budget failures remain failures under their original criterion. Optional ablations at `d602bbe1` establish some helper and growth benefits, with a mixed-suffix regression retained rather than blanket approval.

## Final documentation and delivery

After final warm acceptance, activate `update-agent-docs` once, then `okf-authoring`, before any `.agents/` edits. Delegate milestone 5 to a fresh implementer in a private worktree. Synchronize hooks, scripts and PowerShell instructions, testing, known issues, FILE_MAP/API_MAP/INDEX as applicable. Preserve the installed-old-hook workaround until the user installs. Protected AGENTS sections remain unchanged.

Root coordinates and integrates implementation; only original-node repairs may reuse their implementer. Private branches never push. Integrate serially: clean worktree, rebase, fast-forward, verify matching tips, remove only owned worktrees/branches. Configured models and effort were applied at initial spawn; executed configuration is unconfirmed. The dispatch audit retains the earlier routing-prompt violation and review timeouts. Timed-out reviews supply partial findings, not final approval.

Only report the branch ready after every gate and documentation pass finishes. User command: `rtk proxy ./scripts/install.sh`, then review changed non-managed Codex definitions through `/hooks`. No real hooks were installed by agents.

## Durable findings

- Exact validated native content/search schemas only. Native aggregate 65,536 bytes; unsupported/executable 32,768. Structure depth32/nodes256/strings128; shell depth16/commands128/totaltokens256; Python syntax depth32/tokens1024 and AST depth32/nodes2048. Some limits are dominated by earlier bounds. Raw JSON decoding remains outside post-decode inspection bounds.
- Patch delete/move protection checks source removals under existing rules. No general destination protection or saved-script reading. Wrapped sinks and interpreter options have public red-to-green controls.
- `/usr/bin/time -l` in the sandbox fails with `time: sysctl kern.clockrate: Operation not permitted`; approved native collection succeeds. Timing excludes the RSS wrapper. macOS RSS units are bytes.
- Use `RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk ...`; the default RTK database is unwritable. Git metadata outside the sandbox needs approved escalation. No automatic review rejection occurred.
- Run generator mutable fixtures and installers serially. Gemini installed smoke needs a separate directory log path from Copilot's regular-file path. Existing provider shell suites can print read-only observability diagnostics while guard assertions pass; do not claim installed observability proof.
- Existing installed guardian can reject benign multiline patches above 128 segments. Split edits until the user installs; never disable the hook.
- Never use an em dash. Persisted documents and commits use normal English. Conventional commit subject <=72 characters; Summary/Rationale/Tests bullets and Copilot co-author trailer are required.
