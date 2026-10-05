# Tool Guardian repair worker

The root agent authorized this worker to implement R1 through R4 from the 2026-10-05 review. The public test seam is each generated provider hook's stdin JSON and stdout decision. Represented operations will never execute. Root owns the ExecPlan, handoff, final documentation, review coordination, and performance probes.

I read AGENTS.md, the memory index, architecture, conventions, hooks and scripts instructions, matching testing and known-issues guidance, the input policy, the feature handoff, and milestone 6. I activated handoff, TDD, security, and performance guidance. The existing user-authorized public provider seam satisfies TDD's seam agreement requirement.

All shell commands use `RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk`; exact-output reads use `proxy`. This avoids the documented unwritable default RTK database. No real-home install, commit, timing probe, or additional delegation is permitted.

## Verification state

R1 red command: `python3 scripts/test-tool-guard-shell-data.py ShellDataTests.test_installer_pipeline_intermediates_keep_existing_protection` returned exit 1 with 48 failed provider/mode checks. All intermediate cases silently allowed. The canonical repair restores original pipeline matchers over retained executable text, replacing literal pipe characters with spaces and preserving actual parsed pipe operators.

`python3 scripts/generate-hooks.py --write` initially failed with Operation not permitted in protected repository `.codex/`; transactional rollback completed. The same command with approved sandbox escalation succeeded and refreshed the three local policy helpers only. The focused three-method pipeline run then showed all block behavior repaired and both pre-existing methods passing; eight new Codex warn assertions failed because the test helper incorrectly required an explicit allow field. Codex correctly emits only `systemMessage` for warnings; the helper now accepts that established envelope while still requiring warning text.

Root moved implementation into isolated `/private/tmp/tool-guardian-review-repair`, branch `codex/tool-guardian-review-repair`, base `4bade608`. `rtk git apply /private/tmp/tool-guardian-review-repair-transfer.patch` succeeded. The log copy initially failed because the destination parent did not exist; creating that parent and retrying succeeded. Root is restoring only the transferred paths in the shared root. No further edits occur there. Commands in the isolated worktree use `login:false` to avoid an unrelated pyenv rehash warning. Root now authorizes one private unpushed fix commit containing only this worker's paths after verification; root-owned plan/handoff copies will be reverted before committing.

R1 focused green command: `python3 scripts/test-tool-guard-shell-data.py ShellDataTests.test_installer_pipeline_intermediates_keep_existing_protection ShellDataTests.test_pipeline_operators_follow_shell_quote_boundaries ShellDataTests.test_wrapped_pipeline_operations_keep_existing_protection`: 3 methods passed.

R2 red command: `python3 scripts/test-tool-guard-shell-data.py ShellDataTests.test_inline_shell_arguments_and_input_remain_inspected`: 33 failures. The executable positional and installer-consumer cases silently allowed. Six failures were incorrect warning expectations for unresolved `eval` bodies; the established fail-closed contract requires denial in warn mode, so those expectations were corrected before green. The repair removes only the inspected inline shell body from outer rendering, preserving interpreter, options, all other arguments, and producer inspection. Regeneration succeeded without escalation in the isolated worktree. The same focused method passed after repair, including safe arguments and proven search bodies.

R3 red command: `python3 scripts/test-tool-guard-shell-data.py ShellDataTests.test_attached_unresolved_python_code_fails_closed`: 48 failures for attached unresolved forms across four launchers, three providers, and both modes. Spaced forms and harmless controls passed. Moving attached code-option recognition before the nonliteral fallback closes these failures. Regeneration and the same focused method passed.

R4 red command: `python3 scripts/test-tool-guard-limits.py ResourceLimitTests.test_nested_execution_charges_normalized_aggregate_bytes`. The first run stopped its main loop after three Copilot failures because the review case lacked a subtest scope; adding that scope produced 12 failures covering all providers and both modes, with allowlist enabled. Each silently allowed. The repair charges normalized UTF-8 bytes in the existing aggregate while returning raw source. Regeneration and the same focused method passed: exact 32,768 normalized bytes allow, first 32,769 deny, and the original 700-character review case denies with 46,218 bytes. ASCII behavior remains covered by the existing limits suite.

The pipeline rendering reuses one lowercase value and supplies empty text when there is no parsed pipe operator, avoiding unnecessary secondary normalization on the common no-pipeline path. No inspection budgets or exemptions changed.

## Broader verification

Each command below uses the recorded RTK prefix in the isolated worktree. These are correctness checks; their suite runtimes are not performance acceptance measurements.

- `python3 scripts/test-tool-guard-shell-data.py`: 16 methods passed.
- `python3 scripts/test-tool-guard-limits.py`: 17 methods passed.
- `python3 scripts/test-tool-guard-native-data.py`: 13 methods passed.
- `python3 scripts/test-tool-guard-false-positives.py`: 144 public fixture checks passed, zero failures.
- `python3 scripts/test-security-banners.py`: 14 methods passed.
- `bash scripts/test-hooks-tool-guard.sh`: exit 0, but six observability readonly-database stderr errors from default real-home paths. A writable disposable log-path rerun is pending.
- `bash scripts/test-gemini-hooks-tool-guard.sh`: exit 0 with the same six observability stderr errors; disposable-path rerun pending.
- `bash scripts/test-codex-hooks-tool-guard.sh`: exit 0; its shared banner run passed 14 methods.
- `python3 scripts/test_test_all.py`: 14 CLI methods passed.
- `python3 scripts/test-generate-hooks.py`: 25 methods passed, run after all provider checks completed so its mutable fixtures were serialized.

Self-check found a remaining R3 attached-option case behind an unresolved option prefix: `python3 "$FLAGS" -c"$BODY"` and its quoted attached equivalent still allowed, while the spaced form denied. Extending the maintained R3 method to this launcher reproduced 12 failures across providers/modes before any edit. Widening the existing unresolved option-prefix check to recognize attached Python code options repaired it. `python3 scripts/generate-hooks.py --write` and the focused R3 method passed afterward. Only that one-line source change followed the broader passes above, so final affected verification and freshness will be rerun. Root was notified before review dispatch.

No timing, install, native Windows execution, or guardian disabling occurred. Root owns the formal documentation pass.

Final source-freeze verification on native macOS 26.7.1 arm64, Python 3.14.6:

- `env OBSERVABILITY_LOG_PATH=/private/tmp/tool-guardian-repair-observability/copilot/observability.ndjson bash scripts/test-hooks-tool-guard.sh`: exit 0, empty stdout/stderr; initial readonly observability errors resolved by fixture isolation.
- `env OBSERVABILITY_LOG_PATH=/private/tmp/tool-guardian-repair-observability/gemini/observability.ndjson bash scripts/test-gemini-hooks-tool-guard.sh`: exit 0, empty stdout/stderr.
- `python3 scripts/test-tool-guard-shell-data.py`: all 16 methods passed after the R3 prefix fix.
- `bash scripts/test-codex-hooks-tool-guard.sh`: exit 0, shared banner suite all 14 methods passed after freeze.
- `python3 scripts/generate-hooks.py --check`: all 29 generated files current.

`python3 scripts/test-generate-hooks.py` passed all 25 methods after freeze, with mutable fixtures serialized. A subsequent `python3 scripts/generate-hooks.py --check` again reported 29 current files. `git diff --check` passed. Root-owned copied ExecPlan and handoff were restored to this isolated branch's HEAD before staging; they are not part of the repair commit. Existing suites already register the added regression methods, so no test-runner registration changes are needed.

Changed files are the canonical family, its three generated local policy helpers, the existing shell-data and limits regression suites, and this log. No corpus fixtures or runner registration changed. Remaining verification belongs to root: independent original-reviewer closure, fresh frozen performance/resource gates, integration/rebase, and the formal synchronized documentation pass. Native Windows and real installed/provider-delivery behavior remain unverified. No commit has been pushed.

The initial scoped `git restore --source=HEAD -- docs/tool-guardian-tuning/ExecPlan.md docs/tool-guardian-tuning/handoff.md` failed because the worktree Git index is outside writable roots. Approved escalation of the same two-path command succeeded. The sandbox limitation affects Git metadata mutations, so staging and the authorized private commit require the same approved route. No automatic review rejection occurred.

## Repair round 2

Root authorized a follow-up commit after both original reviewers completed round 1. Their shared logs were read in full. They closed R2, R3, and R4 but reproduced another R1 variant: a downloader pipes to `sh -c` whose inspected body launches Bash with inherited stdin. Removing the body from outer pipeline rendering hides that consumer. Baseline denied or warned for direct, `exec`, and intermediate `cat` variants; candidate silently allowed. The harmless `printf safe` body must remain allowed.

TDD remains active at the same authorized public-provider seam. Round 2 preserves commit `94704adb` and all existing assertions. Proposed implementation propagates only already-classified executable context from nested inspection into outer pipeline matching. Proven search, writer, and survey data contributes no context. No represented command will execute, and no general shell interpreter, timing probe, or installation will be added.

Round 2 red command: `python3 scripts/test-tool-guard-shell-data.py ShellDataTests.test_pipeline_nested_consumers_keep_inherited_input_context` returned exit 1 with 48 failed checks. Seven curl nested-shell/exec/eval/wrapper/Python-sink cases and one wget Python-to-shell sink silently allowed at all three providers in both modes. The direct wget/Bash-to-shell case already passed under existing matcher semantics. Harmless `printf safe`, literal Python printing, proven nested search, and proven nested writer controls all passed before implementation. Root approved propagating retained context with a small bounded collector and requested explicit survey and wrapper controls before freezing.

The maintained method was expanded with nested eval/search controls and both exact guardian survey forms, in block and warn modes. It still reproduced the same 48 failures; every harmless control passed. The first collector implementation then passed the method after canonical regeneration. It reuses retained source or shell rendering, propagates only execution sinks, and omits proven data. No second parse or source budget charge was added.

Self-check found that collected producer text must precede its real outgoing pipe, rather than follow it. Two added public variants put the downloader in an inline shell body, directly and through eval, before piping to Bash. The same focused method reproduced 12 new silent-allow failures across providers/modes before the ordering repair. Root was notified. This remains original installer-rule matching over retained executable context, not general language interpretation.

After ordering repair and regeneration, the focused method passed. A further producer control put a literal search in the inline body and fed its output to Bash. The focused method reproduced six silent-allow failures, showing that the existing unsafe-output classification was lost at the shell-body boundary. Propagating that existing flag to the terminal nested command restores strict inspection when search output becomes code. The incoming downloader-to-safe-search control remains exempt, as do writers and surveys; there is no blanket interpreter or search ban. Regeneration and the complete focused method passed again. All prior assertions remain intact. Root was notified of these self-checks and the final source freeze.

The optional execution-context collector stores already-retained bounded fragments, preserves parsed shell pipe ordering, and propagates existing sink/output roles. It does not parse fragments again, add source budget charges, or rescan proven data. Python retained context masks literal pipe characters; actual shell operators come from the parsed shell representation. Unsupported shell syntax retains its existing strict source treatment. Full frozen verification and native Python 3.13 checks are next.

Frozen round 2 on Python 3.14.6: `python3 scripts/test-tool-guard-shell-data.py` passed all 17 methods; `python3 scripts/test-tool-guard-limits.py` passed 17; `python3 scripts/test-tool-guard-native-data.py` passed 13; `python3 scripts/test-tool-guard-false-positives.py` passed all 144 public checks. No failures. `/Users/adam/.pyenv/versions/3.13.14/bin/python3.13 --version` confirmed native Python 3.13.14 is available for the requested second-version verification.

The same four suites also passed on native Python 3.13.14 with counts 17, 17, 13, and 144. Python 3.14 security banners passed 14 methods. Before review dispatch, root requested a sequential-producer check: an inline search followed by harmless printing still shares the outer pipe. The new public case reproduced six silent allows before repair, while the paired incoming-pipeline search-plus-print and proven writer-plus-print controls passed. The prior unsafe-output propagation applied only to the terminal child. Its two-line correction applies inherited output context to all sequential child commands using that stdout. Source was unfrozen for this correction; affected suites will be rerun on both versions before a new final freeze. No prior assertion was weakened.

Final round 2 source after the sequential-output correction:

- `python3 scripts/test-tool-guard-shell-data.py`: 17 methods passed.
- `python3 scripts/test-tool-guard-limits.py`: 17 methods passed.
- `python3 scripts/test-tool-guard-native-data.py`: 13 methods passed.
- `python3 scripts/test-tool-guard-false-positives.py`: 144 public checks passed, zero failures.
- `/Users/adam/.pyenv/versions/3.13.14/bin/python3.13` running each of those same four script arguments: 17, 17, 13, and 144 passed respectively, zero failures.

Final provider verification completed with the exact disposable observability override commands recorded for round 1: Copilot and Gemini suites exited 0 with empty stdout/stderr. `bash scripts/test-codex-hooks-tool-guard.sh` exited 0 and its Python 3.14 shared banners passed all 14 methods. `/Users/adam/.pyenv/versions/3.13.14/bin/python3.13 scripts/test-security-banners.py` passed 14 methods. `git diff --check` passed. Generator mutable fixtures began only after all public checks finished: `python3 scripts/test-generate-hooks.py` passed all 25 methods. `scripts/generate-hooks.py --check` passed on both native Python versions, reporting 29 current outputs each time.

Round 2 changes only six owned files: the canonical family, three generated local helpers, the existing shell-data suite, and this log. The first repair commit and every prior test assertion are retained. No CLI registry, corpus fixture, limits-suite assertion, shared-root document, real installed hook, or `.agents` file changed in this round. Native Windows remains unverified; re-review, performance/resource gates, integration, and final synchronized documentation remain root-owned.
