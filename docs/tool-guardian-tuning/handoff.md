# Tool Guardian tuning handoff

## Status and next step

Repository implementation and independent repair review are complete. Both original Standards and Spec reviewers approve `27062fc6`, integrated as runtime `14c03deeac8943f271c00a274550c6dfa3d60310`. Fresh evidence integrated as `260070f211189096dc4e77d623f004e66b450238`. The final canonical pass satisfied both-bundle OKF lint and freshness of 29 generated files. The 2026-10-07 reconciliation confirms unchanged guard source and generated runtime against `14c03dee`; it does not rerun runtime/performance tests. Use the accepted commit references and retained proof for review; the original topic branch is not a prerequisite.

**Next step:** human reviews the accepted source and retained proof. Then the user runs `rtk proxy ./scripts/install.sh` and reviews/trusts changed Codex definitions through `/hooks` before live checks. Agents must not install into the real home or change user-global configuration. No source repair or unresolved independent-review finding remains. Real installation, native Windows, and live-provider delivery remain unverified.

## Current constraints and accepted behavior

Preserve strict fallback for harmless but unproved positional arguments; additional positional-data proofs remain outside scope. Keep established native/search/writer/survey exemptions. Unsupported roles receive strict inspection; recognized unresolved execution or incomplete inspection denies even in warn mode. Do not reopen settled design or resume Lavish polling without a new request.

- R1: preserve nested executable consumer/producer context, real pipeline ordering, inherited stdin, and all sequential commands sharing stdout. Anchors: `hooks/families/tool_guard.py:1283`, `:1353`, `:1372`, `:1386`.
- R2: shell-body proof does not exempt unproved positional arguments; anchor `hooks/families/tool_guard.py:1358`.
- R3: attached recognized Python code and unresolved option-prefix forms fail closed; anchor `hooks/families/tool_guard.py:1228`.
- R4: normalized aggregate UTF-8 bytes are charged while raw source remains available; anchor `hooks/families/tool_guard.py:762`. At that boundary 32,768 allows and 32,769 denies.

Unsupported Python builtin-alias inference is outside the agreed design. Any newly requested repair changes canonical `hooks/families/tool_guard.py` and regenerates outputs. Never hand-edit provider-local helpers. Rule IDs, provider interfaces, and numeric budgets remain unchanged.

## Verification state

Retained 2026-10-05 source proof includes shell 17, limits 17, native 13, corpus 144, banners 14 on Python 3.14.6/3.13.14, provider suites, generator 25, CLI checks, and freshness. Standards independently passes 402 public checks; Spec passes 294 plus limits/native/corpus. Represented dangerous operations never execute. Historical 39/41 aggregate evidence plus two repaired suites is not a new full-suite run.

Fresh frozen proof retains 17,100 correct warm observations, 7,350 cold launches plus the exact 50-launch repeat, 96 resource cases, and 1,200 concurrency calls. Initial warm Gemini patch p95 and cold Codex writer-before median reports remain FAIL. Exact repeats pass: warm median/p95 deltas -5.456708/-3.852000 ms and -5.453917/-5.694874 ms; cold +4.926083/+5.795166 ms. Cold median headroom is 0.073917 ms. Budgets remain +2/+5 ms warm and +5/+10 ms cold per provider/case; each cold launch has zero provider bytecode, while OS/stdlib caches remain uncleared. Resource maximum is 40.894541 ms against 500 ms; peak native macOS RSS is 22,331,392 bytes. Source proof does not establish installation, native Windows, or provider delivery.

## Evidence and recovery

Current contract and recovery details are in [ExecPlan.md](ExecPlan.md). Current proof is `evidence/review-repair-root-verification.json` and `evidence/review-repair-final-verification.json`. `evidence/review-repair-comparison.json` retains initial failures separately from repeats. `evidence/review-repair-attempt-1/` preserves failed logging-adapter evidence, original drivers, and frozen source. Participant logs and dispatch audit are under `repair-logs/`; failed attempts and unconfirmed executed settings remain recorded.

Preserve the original disposable baseline/profile roots and both review candidates: `/private/tmp/tool-guardian-baseline`, `/private/tmp/tool-guardian-profile-candidate`, `/private/tmp/tool-guardian-profile-checkpoint`, `/private/tmp/tool-guardian-review-candidate`, and `/private/tmp/tool-guardian-review-candidate-2`. Candidate 2 identifies the accepted runtime freeze; candidate 1 identifies failed-adapter evidence. Check that retained roots exist before replay. Recreate recorded isolated checkout paths and preserve reports when reconstruction is necessary. Inline optimization replay uses original `84eae394`, not today's extracted-helper layout. The independent-review fixed point is `9bcc6ff56cf916f848e4b32314ded35757d240c2`; pre-repair implementation was `4bade608`.

Use disposable writable `OBSERVABILITY_LOG_PATH` for Copilot/Gemini shell suites and a task-local `RTK_DB_PATH` in this sandbox. Native `/usr/bin/time -l` requires approved collection here. Serialize mutable generator/install fixtures; run timing probes alone against frozen source. Keep temporary logging homes until outside-timer verification, then clean in `finally`.

Earlier coordination failures and execution chronology are preserved in [historical handoff evidence](history/2026-10-07-handoff-before-reconciliation.md) and the participant logs. Read them only for a specific prior-run investigation; they do not supply current blockers or next actions.
