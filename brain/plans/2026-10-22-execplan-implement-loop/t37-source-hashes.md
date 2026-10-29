# T37 post-repair product source hash manifest

Integrated source pin: `c90d71fbfc3665b6fa6226de1576f5835328e737`.

Review base: `305ee3a3bc67c7d2ece26dba509cca3899854258`.

These 14 SHA-256 values were computed from the frozen post-repair source worktree and compared with the integration worktree after fast-forward. All 14 match. The manifest covers the two maintained public-CLI tests, seven bundle Python modules, and five published instruction/evaluation files. It excludes the plan and this evidence note.

| File | SHA-256 |
| --- | --- |
| `scripts/test-execplan-implement-loop.py` | `b191740ff1d0fa360cd46652f88b49d7c425e1025f097cb49c6b18030aec5396` |
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
| `skills/default/execplan-implement-loop/scripts/reporting.py` | `aadcd7a95b9118f90490076a3114b7ca0f7d084e44c4de393f11376b9ede4a5c` |
| `skills/default/execplan-implement-loop/scripts/run.py` | `6aadd31b2bd6c5c40bd704a3442ca14812cee5d045974733686f5eb364481750` |

## T37 verification record

- The process-enabled maintained runner passed 96/96 in 217.485 seconds (`/private/tmp/live-review1-final-runner-v2.log`); the qualification helper passed 33/33 in 56.150 seconds (`/private/tmp/live-review1-final-helper-v2.log`). The runner ran before the helper, serially, against the frozen source.
- The first full runner run passed 92/94 and failed two existing Bearer-redaction cases (`/private/tmp/live-review1-full-runner.log`). That failure is preserved. A corrected 94-case run passed (`/private/tmp/live-review1-final-runner.log`); additional red-first regressions for a 640 KiB input and an environment-label collision then passed in the final 96-case run.
- The frozen-source static summary records AST parsing for nine Python files, 14 source hashes, 68 resolved links, five unchanged instruction/evaluation files, unchanged coordinator-owned progress and acceptance regions at the frozen source pin, unchanged historical plan evidence, and exact `message.md` parity (`/private/tmp/live-review1-static-summary.json`). After the coordinator added this hash note and current statuses, a local scan resolved 73 relative links across 26 Markdown files with none unresolved; the skill validator reported `Skill is valid!`.
- The paired fake-provider instruction grades remain the original single sample: 17/17 for the updated skill and 16/17 for the old baseline. Metrics remain unknown. No actors or graders were rerun because the instruction/evaluation files and denied-boundary contract match the pinned artifacts. This does not prove live Gemini behavior or filesystem containment.
- No real Gemini/provider call was made.
