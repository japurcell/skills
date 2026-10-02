# Tool Guardian tuning handoff

## Goal and status

All milestones in `docs/tool-guardian-tuning/ExecPlan.md` are complete on private topic branch `codex/tool-guardian-tuning`, ready for human review. Source repair integrated at `1a4610ad`; the single formal documentation pass integrated at `37c7cfd7`. Every owned implementer worktree and branch was removed. Unrelated worktrees remain. No push, real installation, or user-global configuration change occurred.

**Next step:** the user reviews the topic branch, then runs `rtk proxy ./scripts/install.sh` from `/Users/adam/.codex/worktrees/e61c/skills` and reviews changed non-managed Codex definitions through `/hooks` before live validation. Native Windows public-envelope validation remains unavailable in this environment.

## Verified outcome

- Both complete 147-case warm pairs pass. Maximum median deltas -1.841/-0.727 ms; maximum p95 deltas +1.618/+2.445 ms. All decisions match. Root independently verified 39 frozen source hashes against integrated source and the exact candidate snapshot.
- The full cold matrix retains 7,350 fresh-copy launches and its original 3 failures. The exact 150-launch repeat passes all 3: Copilot writer-after +4.584/+4.758 ms, Gemini recursive remove current +1.738/+1.889 ms, Codex writer-before +4.650/+4.884 ms. No failure was removed or pooled.
- Resource 90 cases at 25 samples/3 warmups pass. Maximum 49.085958 ms and peak native macOS RSS 22,413,312 bytes. Repeated four-worker B/C/C/B comparison retains 1,200 measured public calls; every provider's individual and batch median/p95 improves in both pairs. Original noisy diagnostics remain retained.
- Python 3.14.6 and native macOS 3.13.14 pass public banners 14, shell 13, native 13, limits 16, corpus 144 and generator 25/freshness 29. The aggregate run retains 39/41 earlier passes; both remaining repaired suites pass in the actual shared-root sandbox, including 16 helper tests with deprecation warnings as errors. No fabricated fresh aggregate result.
- Formal documentation pass updates 9 canonical docs plus `final-doc-notes.md`. Both-bundle OKF lint, generator freshness 29 and whitespace checks pass. The rebase was conflict-free; checks were not repeated solely for integration. Protected AGENTS sections remain unchanged. No runtime jobs remain.

## Evidence and replay

Current acceptance: `evidence/cold-profile-final-comparison.json`; raw warm/cold/resource/concurrency reports and frozen manifests remain alongside it. `cold-profile-notes.md` explains the measured sanitizer repair. `final-doc-notes.md` records the formal documentation pass. `evidence/implementation-dispatch-audit.json` preserves routing, runtime deadlines, partial review timeouts and the earlier routing-prompt violation; configured model/effort was explicit, executed configuration unconfirmed.

Immutable original baseline `/private/tmp/tool-guardian-baseline`; exact repaired snapshot `/private/tmp/tool-guardian-profile-candidate`; extracted checkpoint `/private/tmp/tool-guardian-profile-checkpoint`. Preserve these snapshots and retained source/payload/runner/corpus hashes. Optional optimization replay requires a disposable worktree at 84eae394; today's extracted entrypoints are not that inline ablation source. See `optimization-validation-notes.md`.

Historical zero-budget failures remain failures under their original criterion. The rejected literal-scan experiment showed no attributable full-hook gain; runtime changes were restored and its exact patch, failed reports and useful public characterizations remain at 15e323e5. Timed-out reviews supply partial findings, not security approval.

## Contract and durable findings

Per provider/case budgets: warm +2 ms median/+5 ms p95; cold fresh copy with zero provider bytecode +5/+10 ms; finite resource ceiling 500 ms. Preserve original failures when repeating isolated noise. Never raise budgets silently, pool cases, weaken inspection or skip logging.

Exact validated native schemas and proven shell/Python data roles receive data treatment. Unsupported forms retain strict inspection; unresolved inspection fails closed. Provider-local policy helpers are generated identically, delivered with adapters by both installers, and missing/corrupt helpers deny in block and warn modes. Ordinary bytecode only.

Native aggregate 65,536 bytes; unsupported/executable 32,768; structure depth 32/nodes 256/strings 128; executable depth 16/commands 128/tokens 256; Python syntax depth 32/tokens 1,024 and AST depth 32/nodes 2,048. Some later bounds are dominated. Raw JSON decoding precedes bounded traversal. Patch deletion/move checks protect source removals under existing policy, with no general destination or saved-script-inspection claim. Canonical current details are routed from `.agents/memory/API_MAP.md`.

Until the user installs, the old installed guardian can reject benign multiline patches above 128 segments. Split edits and construct dangerous fixture vocabulary dynamically; never disable the guard. Run generator mutable fixtures and installers serially; timing probes must run alone on frozen source. Source proof does not establish installed observability or provider-delivery timing.

Use `RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk ...` inside this sandbox. The default RTK database is unwritable. Git metadata outside the sandbox needs approved escalation. `/usr/bin/time -l` sandbox collection fails with `time: sysctl kern.clockrate: Operation not permitted`; approved native collection succeeds, with macOS RSS in bytes and wrapper cost excluded from latency. No automatic review rejection occurred.
