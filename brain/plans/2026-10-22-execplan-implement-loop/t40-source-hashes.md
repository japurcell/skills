# T40/T41 source hashes and verification

This evidence note records the frozen source and current local proof for the cycle-2 repair. It is supplementary to the active status and acceptance contract in [ExecPlan.md](ExecPlan.md).

## Source pin and scope

- Tested source commit: `e8076847e56ea1057dbdc61f1c9fed132d9a88ec` (`fix(execplan-loop): classify credential labels by key family`), parent `c99a6e0206ababaa6dac6783c150e0ee8f29cb58`.
- The source commit changes only `skills/default/execplan-implement-loop/scripts/reporting.py` and `scripts/test-execplan-implement-loop.py`.
- The integrated source bytes match the commit and the frozen 14-file manifest below. No source edits occurred after the worker's final test run.
- T39's plan reconciliation was already present in parent commit `c99a6e0`; the source worker made no artificial plan changes. Previous reports and original live evidence were not modified by this source commit.

## Source hash manifest

SHA-256 for all 14 tested source and instruction/evaluation files:

| Repository path | SHA-256 |
| --- | --- |
| `scripts/test-execplan-implement-loop.py` | `97f7fa86af401bd85c9ab759038c9b3e69176177df5b2009c1f2676e6f1a3bf6` |
| `scripts/test-execplan-qualification.py` | `50f1e9f8c98e8a4e30686c57113be1f27563eae73b630124939a2ef17e9610f2` |
| `skills/default/execplan-implement-loop/README.md` | `c5707dfc6ec940e4b0dc4340ee7bfecb04b40b20c7a91f3707a965b3bc6ad5f9` |
| `skills/default/execplan-implement-loop/SKILL.md` | `1483d54e09c9ed01bd1e54ce4ef33449b125f8e453d08ea88efc4382d13a5cc9` |
| `skills/default/execplan-implement-loop/evals/evals.json` | `171288201d69204062a674a4e6b895fec1cc3e076877d91e5f04b9be8edbf46a` |
| `skills/default/execplan-implement-loop/references/protocol.md` | `cd7d0772021a06f285d22814d64901b891c225c231ac314075a116b9cb2669d5` |
| `skills/default/execplan-implement-loop/references/worker-prompt.md` | `38e2ee778f3d76581ab5ea4a0f385192b23378d6db194d34c64d1b9d0fcff3ab` |
| `skills/default/execplan-implement-loop/scripts/contracts.py` | `1f91361bf566fb369a34df831ef1f5321841dd1aad269a209f91f1f30d50401a` |
| `skills/default/execplan-implement-loop/scripts/engine.py` | `7bca7e3d8a4ed8770ee9f85de06e6c2c42b698b9de5b9f823f8d6e7d2fef0c2c` |
| `skills/default/execplan-implement-loop/scripts/processes.py` | `0fa82038b0d6120ae1925c8797c3a6d58d85c589f3883397559ba6b37f96d514` |
| `skills/default/execplan-implement-loop/scripts/qualify.py` | `c8a3a8f535bac2841f29225ed9aa0affbb8f02f2aedfb13cf3c4f5d7e8d142bf` |
| `skills/default/execplan-implement-loop/scripts/readiness.py` | `dcc01c675e96f80fec8da27aeeb53c757bbf448b480cdbd834ef969713fee68f` |
| `skills/default/execplan-implement-loop/scripts/reporting.py` | `66916d7e837bfe6c89f7dd5bb981c3377bb57e27422a164d51e6f9a10f1496a8` |
| `skills/default/execplan-implement-loop/scripts/run.py` | `6aadd31b2bd6c5c40bd704a3442ca14812cee5d045974733686f5eb364481750` |

## T40 red-first and final verification

- Public copied-runner regression `test_diagnostic_redacts_common_credential_key_families_before_retention` covers plain, case-varied, camel-case, and environment-prefixed token labels, plus existing secret families. It checks sentinels against stdout, stderr, and persisted run files.
- Public negative case `test_diagnostic_preserves_actionable_authentication_and_trust_errors` preserves exact actionable startup errors.
- Public bounds case `test_diagnostic_long_credential_keys_and_values_remain_bounded` exercises a 600,000-byte key and 900,000-byte value under the CLI deadline.
- Red-first evidence: `/private/tmp/live-review2-t40-red.log` and `/private/tmp/live-review2-t40-red-scheme-aliases.log`. The initial matrix and long input cases fail against the original source; the actionable startup-error negative remains intact. An extended alias case also exposed a scheme-value suffix before the final fix.
- Final focused diagnostic group: 12/12 in 13.280 seconds, `/private/tmp/live-review2-t40-final-focused.log`. Existing collision, capture, and ambiguous-quote guards: 3/3 in 2.605 seconds, `/private/tmp/live-review2-t40-final-guards.log`.
- Process-enabled full maintained runner: 99/99 in 219.204 seconds, `/private/tmp/live-review2-final-runner.log`. Process-enabled helper, run serially afterward: 33/33 in 55.985 seconds, `/private/tmp/live-review2-final-helper.log`.
- The earlier cycle-1 94-case runner failure remains preserved at `/private/tmp/live-review1-full-runner.log`; it was followed by corrected cycle-1 runs and is not hidden or counted as a cycle-2 result.

## T41 integrated static checks and limits

After fast-forwarding the exact source commit, the integration worktree matched all 14 hashes above with zero mismatches. Nine Python files parsed with `ast.parse`; `rtk git diff --check c99a6e0206ababaa6dac6783c150e0ee8f29cb58 HEAD`, the portable skill validator, exact `message.md` byte parity, and cycle-2 report byte comparisons passed. The worker static summary recorded 79 resolved local links and preservation of all prior plan reports/evidence. After adding this evidence note, a coordinator scan resolved 80/80 local links across the plan's 20 Markdown files. Cycle-2 report copies also byte-match `/private/tmp/execplan-live-standards-review-2.md` and `/private/tmp/execplan-live-spec-review-2.md`.

All five T31 instruction/evaluation files remain unchanged. The existing one-sample grading result is reused: updated skill 17/17, baseline 16/17, with metrics unknown. No grader or actor was rerun for unchanged inputs. These checks use fake providers only. They do not establish real Gemini behavior, arbitrary unknown-secret removal, or filesystem containment. New live behavioral and explicit-policy qualification remains owner-only.
