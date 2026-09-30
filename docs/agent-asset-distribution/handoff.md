# Agent Asset Distribution Handoff

## Goal and status

Implement the accepted selected-asset installer under [the ExecPlan](../agent-asset-installer/ExecPlan.md). Implementation is explicitly authorized and resumes after the user installs flock. Base branch is `codex/research-agent-distribution-options`.

M1 through M5 are implemented, independently approved, integrated, and done/met. M5 tip is `865470e148acdca77835d1215ce0807e1d6e2266`; M4 is `5f78d78a77ec147d7c85ddf6119312a4a81ce55a`; M3 is `b1bcc63257ba3a32bf61d58f865ea5854eef15d5`. The approved local M6 checkpoint integrates at `74f9bcb59718c484b7bd5c181498ef2ffc68657c`. Its one Progress-only rebase conflict preserves all 13 non-plan patches/file bytes exactly. Matching clean tips are verified before removing integrated private worktrees/branches.

M6 remains in progress/not met: safe native Windows mutation implementation itself is unfinished, alongside native Windows/Linux, Python 3.11 runtime and client discovery/event proof. Production Windows mutation/recovery refuses with `ASSET_PLATFORM_UNSUPPORTED`.

The bounded M7 usage/help checkpoint receives independent APPROVE after four Required documentation repairs. Its original writer is completing the private commit in `/private/tmp/agent-assets-m7`, branch `codex/agent-assets-m7`; seven files comprise usage, README, one CLI purpose docstring, three canonical routes and the plan. Overall M7 remains in progress/not met because native acceptance depends on M6.

## Next step

Collect the clean M7 commit, record a fresh exclusive merger route in the plan, rebase the private branch onto a clean frozen base, validate documentation conflicts and unchanged source patch, then fast-forward and remove its worktree/branch after matching-tip verification. Complete the primary final `update-agent-docs` pass after all source/review work. Native gates stay open; do not claim full plan completion or repeat broad source tests merely for prose/help changes.

## Verification and concrete blockers

Latest integrated aggregate on macOS/Python 3.14.6 passes all 37 suites with zero failures in 544.1 seconds, including all 100 public installer cases in 131.971 seconds and all 25 generator cases in 10.064 seconds. No checkout edits occur during that run. Private M6 acceptance also passes 100 cases in 134.756 seconds; final team 28 and exported-bundle consumer 2 pass on Python 3.12.14. Older Python 3.13.14 evidence covers 98 cases before the final paired-schema repair. Python 3.11 grammar parsing is not runtime proof. Existing Windows-only skips do not establish Windows acceptance. Source CI wiring is not a remote run; Windows full mutation jobs remain explicitly unmet without weakened tests.

This Mac has Python 3.14.6, Git 2.50.1, Bash 3.2.57, PowerShell 7.6.6, RTK 0.50.0, Codex 0.159.0 and user-installed flock 0.4.0 (`/Users/adam/homebrew/bin/flock`). Other advertised clients and native Windows/Linux runners are unavailable. No dependency/client installation, personal credential access, real-home change, push or publication occurs.

The [native Codex probe](../agent-asset-installer/codex-native-probe.md) proves local deny-default filesystem/network confinement through permitted/refused sentinels and clean disposable help startup. Foreground `--no-daemon` reaches normal folder trust; selecting `Trust and continue` fails `Failed to synchronize managed preferences (code -32603)` and does not persist trust. No model prompt, distinctive-asset installation, native discovery, hook review or event occurs. All experiment processes/state are cleaned up. Apple's deprecated/private sandbox interface establishes this local experiment only. Next native Codex work needs an isolated environment where normal managed-preference synchronization/trust persistence works without personal-state access or managed-policy weakening. No provisioning or trust bypass is authorized by this checkpoint.

The [Windows research](../agent-asset-installer/windows-filesystem-research.md) records unresolved rooted-handle option combinations, attribute-only reparse changes, rename sharing and namespace reacquisition after process death. Read-only clone/refusal jobs cannot substitute for a safe writer and native concurrency/recovery experiments.

## Accepted decisions

Team setup commits selected payloads by default. Support private repo and personal modes, bundles and individual assets, required dependency closure, explicit preview/update, immutable provenance, exact-byte offline verification and pruning only unchanged owned files. No rollback command/history; only current-record restore and incomplete-operation recovery. Initial complete adapters cover Codex, Copilot CLI/VS Code and Gemini CLI; skills-only paths cover Claude Code, Cursor and OpenCode. Native packages remain later work. No cloud/IDE inference from CLI or direct-hook protocols.

Python 3.11+ and Git are required. Bash/PowerShell entry points use the same lifecycle engine. Tests use unique disposable targets and explicit state overrides, never real home or weakened assertions. Local mode refuses tracked configuration writes without a verified native override. The initial catalog has three hook families and no selectable RTK renderer. `review` remains unavailable because required workflow branches are genuinely missing.

All eight planning tickets are closed. Keep research under `docs/agent-asset-distribution/`, as requested. [The map](map.md), [distributor comparison](existing-repos-review.md) and the self-contained ExecPlan preserve decisions. The user accepts grilling/research without missing domain-modeling; do not ask again.

## Review findings and durable learnings

M7 repairs explain matching schema-2 records, mandatory `attribute_file_policy` (`["text", "eol=lf"]` for owned team blocks, null otherwise), genuine paired schema-1 migration, malformed/mixed refusal and offline authority limits; create disposable personal homes; clarify process-home-only inherited `CODEX_HOME` and repeated explicit overrides; and distinguish Python 3.11 minimum from actual runtime proof. Historical M2 catalog inventory is separate from current client validation. Independent recheck finds no blocking findings. Optional wording distinguishes adding a metadata LF rule from borrowing compatible effective policy.

M6 fixes untouched autocrlf clone drift from conversion of `.gitattributes` itself. A borrowed-rule false audit is repaired with paired version 2 and mandatory policy, replacing an optional omission that silently selects legacy semantics. Actual old-CLI migration, eight malformed variants, committed-damage drift, unrelated CRLF/index preservation and clone protocols pass. Offline audit trusts committed authority; coordinated rewriting of the complete pair is not cryptographic authentication. Explicit writes authenticate immutable ownership and refuse conflicting transforms.

M5 repairs authenticated Codex agent sharing before unmanaged-name preflight and effective Git ignore privacy, including negations, nested `.gitignore`, tracked private files and linked-worktree shared exclusions. M3 authenticates exact old ownership/origin bytes, checks final preimages and visible parent identity, and refuses ambiguous directory/leaf substitution recovery with pending evidence retained. M1/M2 preflight all tracked files under actual selected roots before Git status and evaluate effective attributes in a disposable mirror; equal-length edits can execute clean filters without that preflight.

The aggregate initially exposes SQLite maintenance contention, macOS `/var` aliases, protected fixture placement and inherited personal trace paths. Independent repairs preserve runtime/assertions, isolate state, normalize roots, use bounded fixture waits and reap processes. Repairs integrate at `82943218bbc2a484295337334df53c0e80f8b908` and `40f06f865ee4b6849b5b5585e3c89411438742a7`; [fixture](../agent-asset-installer/fixture-repair.md) and [observability](../agent-asset-installer/observability-repair.md) notes retain evidence.

Set assigned workdir and verify branch before worker mutation: one early worker inherits base cwd, and exactly its four hash-verified edits are transferred before restoring only those paths. Keep generator snapshot tests separate from edits. Tool Guardian rejects oversized patches before mutation; keep patches below 32,768 bytes/128 segments and match complete physical lines. Anchor milestone edits to exact headings, since a generic status block initially places an M7 note under M6. `apply_patch` also refuses delete-plus-add on the same path before mutation; replace an existing handoff once rather than submitting competing operations.

Fresh launches and writer reactivation encounter agent-thread limits. Record failed routes as unapplied; wait for active turns to finish, then retry the fresh node or same-node repair. Related read-only research can reuse a completed reviewer. Distinct implementation nodes require fresh writers. Earlier service content flags preserve interrupted work, not approval or sandbox rejection; later independent reviews approve repairs. No auto-review rejection occurs.

## Retained artifacts and documentation

Only `/private/tmp/agent-assets-m7` remains an implementation worktree. `/private/tmp/agent-assets-probes` retains historical research originals; corrected relevant notes are promoted, including the native probe byte-for-byte SHA-256 `6350992ce43b57cd27cb9fe2c646e2e4273a51b62dc3d3e9af731bc7e5f75df4`. Inspect contents before cleanup so unique evidence is not lost. Routing/service-error evidence remains `/private/tmp/agent-assets-routing.json` and `/private/tmp/agent-assets-review-failure.txt`; latest reactivation failure is `/private/tmp/agent-assets-m7-resume-failure.txt`.

[Client validation](../agent-asset-installer/client-validation.md) distinguishes integrated automated evidence, local containment and unmet native gates. Usage is available after M7 integration. Node-scoped canonical documentation is synchronized; the primary final `update-agent-docs` pass remains due. Preserve protected AGENTS sections, apply OKF to canonical Markdown, synchronize progress/status and update this feature-scoped handoff before stopping.
