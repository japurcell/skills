# Agent Asset Distribution Handoff

## Status

All eight planning tickets are closed. Implementation is authorized through the user's explicit `execplan-implement` request and resumed after the user installs flock. Base branch is `codex/research-agent-distribution-options`.

Milestones 1 through 3 are integrated. M3 tip is `b1bcc63257ba3a32bf61d58f865ea5854eef15d5`; 64 public cases (24 team, 17 selection, 23 lifecycle) and final independent review pass. Its original clean worktree/branch are removed. Exclusive merger resolves only the ExecPlan conflict and verifies unchanged source/test patch, 25 documents/168 links, milestone synchronization, OKF, and whitespace. Earlier writer/review turns ended with service content flags; their findings were repaired and separately approved, never assumed green.

Independent aggregate repairs are integrated: fixture portability/pipe cleanup at `82943218bbc2a484295337334df53c0e80f8b908`, observability test isolation/maintenance coordination at `40f06f865ee4b6849b5b5585e3c89411438742a7`. Their clean worktrees/branches are removed. M4 starts in `/private/tmp/agent-assets-m4` on private `codex/agent-assets-m4`; M5 through M7 remain open. Native package publication and real-home changes are outside the authorization.

## Next step

Complete M4 native repository agents/hooks, explicit runtime configuration and relocated state, selective native configuration ownership, and installed-hook subprocess proof. Review, validate, commit, and serialize integration. The full aggregate after M3 and both test repairs is green: 37 passed, zero failed in 378.4 seconds. Preserve that baseline and run affected checks for new source changes. Follow [the ExecPlan](../agent-asset-installer/ExecPlan.md). M5 depends on M4, then M6 native OS/client proof and M7 final documentation remain.

## Decisions and constraints

The user accepts complete repository adapters for Codex, Copilot CLI/VS Code, and Gemini CLI, plus skills for Claude Code, Cursor, and OpenCode. Team setup commits actual selected payloads by default; private repo and personal modes, dependency closure, explicit preview/update, immutable provenance, owned-only pruning, and exact-byte offline verification remain required. No rollback command or retained version history is authorized; only incomplete-operation recovery and current-record restoration.

The engine uses Python 3.11+ and Git, with Bash/PowerShell compatibility entry points. Tests use unique disposable targets and explicit trace-state overrides; never test against real home or weaken assertions. Non-POSIX mutation/recovery currently fails closed with `ASSET_PLATFORM_UNSUPPORTED`; safe native Windows operations and actual native proof are required in M6. Local mode must refuse tracked configuration changes without a verified native local override. Gemini has no documented project `settings.local.json`.

Keep retained research under `docs/agent-asset-distribution/` as requested. [The map](map.md) indexes closed decisions, [the comparison](existing-repos-review.md) records distributor evidence, and [the ExecPlan](../agent-asset-installer/ExecPlan.md) embeds execution requirements. The user already accepts the grilling/research fallback without domain-modeling; do not ask again. Genuinely missing distribution dependencies remain unavailable.

## Review findings and durable corrections

M3 now authenticates old file ownership and retained baseline origins against recorded immutable source before changing/pruning files. POSIX writes check final preimage/type/inode, parent identity, and desired bytes/mode; journal directory identities prevent ambiguous recovery after directory movement. Concurrent leaf replacement is preserved and requires explicit resolution. Selection/lock source kind, location, and policy must agree. Owned paths and proposed attributes now reject unsupported filters/encodings/ident/crlf transforms before writes. Final independent review approves these repairs and an eight-shape malformed-record sweep across status/update/restore; strict status stays offline.

M1/M2 source reads preserve both indexes, preflight all tracked files under selected actual roots before Git status, and never execute clean filters. Equal-length edits can trigger filters even when other edits do not. Nested/info attribute rules can cancel root policy, so a disposable mirror evaluates effective policy. Explicit maintained `.agents/skills/<name>` source roots permit the required exec-plans prerequisite without editing protected authored skills or distributing unrelated context. Missing required conditional workflow branches fail with complete chains.

The resumed aggregate exposed three existing failures: detached-maintenance SQLite contention, macOS `/var` alias expectations, and helper tests writing under protected checkout state. Operational provider tests also inherited personal trace paths despite an audit override. Repairs isolate capture explicitly without disabling it, seed sentinels only outside intentional maintenance tests, use bounded SQLite fixture waits for deliberate concurrency, normalize fixture roots, use system temporary directories, and close/reap probe processes. [Observability notes](../agent-asset-installer/observability-repair.md) and [fixture notes](../agent-asset-installer/fixture-repair.md) record exact evidence.

A fixture worker initially edited base due inherited cwd. Exactly its four files were copied by verified hashes into its private worktree, then only those base edits were restored. No other changes were reverted. Future commands must explicitly set the assigned worktree and verify the branch before mutation. Tool Guardian oversized patches previously failed before mutation; keep document patches below 32,768 bytes and 128 segments. Match complete physical lines when replacing existing prose.

## Verification and external gates

M3: 64 public cases, 14 runner cases, compilation, OKF, whitespace, and final independent review pass. M2's original 17 selection and M1's 24 team cases remain unchanged. The resumed aggregate baseline ran all 37 suites in 315.6 seconds: 34 passed, three failed. Both repair nodes now pass focused tests; the combined aggregate after integration passes all 37 suites with zero failures in 378.4 seconds. Existing host-specific Windows skips do not establish Windows acceptance.

This Mac has Python 3.14.6 (`/Users/adam/.pyenv/versions/3.14.6/bin/python3`), Git 2.50.1, Bash 3.2.57, PowerShell 7.6.6, RTK 0.50.0, Codex CLI 0.159.0, and user-installed flock 0.4.0 (`/Users/adam/homebrew/bin/flock`). Other advertised client commands and native Windows/Linux runners are unavailable. No native client discovery/hook event or native Windows/Linux job has run. [Codex prerequisite inspection](../agent-asset-installer/codex-cli-prerequisites.md) distinguishes CLI options and native trust from actual acceptance. No agent installed dependencies or changed real home. No push or publication occurred.

## Retained artifacts and documentation

Keep `/private/tmp/agent-assets-m4` until verified integration; the completed M3 worktree is removed. Updated prerequisites are promoted to `docs/agent-asset-installer/prerequisites.md`. The temporary original prerequisite note is historical. `/private/tmp/agent-assets-probes/docs/agent-asset-installer/provider-runtime-audit.md` remains for M4 promotion; the CI/runtime explorer adds `ci-runtime-audit.md` for M6. Promote corrected relevant content before cleaning that worktree. The older temporary catalog audit is superseded by the committed [catalog audit](../agent-asset-installer/catalog-audit.md). Routing and service-error context are preserved at `/private/tmp/agent-assets-routing.json` and `/private/tmp/agent-assets-review-failure.txt`.

Node-specific canonical script and observability docs are synchronized with implemented behavior. The primary final `update-agent-docs` pass remains due at session end after all implementation/review. Preserve protected AGENTS sections, apply OKF authoring to canonical Markdown, synchronize the plan before stopping, and keep this feature-scoped handoff current.
