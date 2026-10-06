---
type: Known Issue
description: Known issues, quirks, and workarounds for `skills`.
---

# Skills - Known Issues

Layer-specific quirks for skills. Cross-cutting issues live in `.agents/memory/KNOWN_ISSUES.md`.

**Affected area:** `skills/*/SKILL.md`
**Description:** `python3 skills/skill-creator/scripts/quick_validate.py` rejects `disable-model-invocation` frontmatter even when a skill needs to keep it.
**Workaround:** Preserve the key when a human has approved it; expect validation to fail until the validator supports it.

**Affected area:** `skills/skill-creator/scripts/quick_validate.py`
**Description:** The validator requires the undeclared `PyYAML` package and fails with `ModuleNotFoundError: No module named 'yaml'` when it is unavailable.
**Workaround:** Do not install dependencies implicitly. Run it with the checked-in runtime: `PYTHONPATH=scripts/vendor python3 skills/skill-creator/scripts/quick_validate.py skills/<skill-name>`.

**Affected area:** Agent-brain status/doctor SQLite capability output.
**Description:** SQLite synchronous and fullfsync settings are connection-local. A read-only inspection can report synchronous `2` while mutation connections request and verify EXTRA (`3`); status does not change connection settings to imply durability.
**Workaround:** Interpret observed values with the reported access mode. The common-protocol fixture proves requested/observed mutation settings, not filesystem/VFS, OS-crash, or power-loss guarantees.

**Affected area:** Agent-brain bridge and registered stage JSON stdin.
**Description:** Ambient `PYTHONIOENCODING=cp1252` can silently corrupt non-ASCII source paths and provider IDs before JSON validation.
**Workaround:** Reconfigure stdin to UTF-8/strict at each public JSON input seam. Registered stages must validate invocation authority before configuring or reading semantic input. Preserve subprocess coverage with raw UTF-8 bytes and invalid UTF-8.

**Affected area:** Agent-brain configuration and durable numeric input.
**Description:** Python's JSON decoder raises a broader `ValueError` for integer digit limits; `math.isfinite` can raise `OverflowError` for a decoded oversized integer timestamp.
**Workaround:** Preserve decoder limits and report numeric-limit/range failures as structured invalid configuration. Bound durable time values before float conversion so status/doctor remain unavailable/incomplete and bridge recovery preserves damaged expected state.

**Affected area:** Agent-brain publication and inverse history.
**Description:** `Path.read_text()` normalizes CRLF while file revisions hash raw bytes. A normalized journal cannot compare or restore the exact recorded artifact. Concurrent recovery also needs exclusive effect ownership, not just an observed SQLite owner.
**Workaround:** Read UTF-8 from raw bytes, retain exact before/after content and hashes in portable history, and hold the worktree publication lock while claiming/revalidating ownership around effects. Unexpected bytes stay untouched with an affected conflict. This gives managed recall a coherent view or gap, without multi-file atomicity for unmanaged readers or power-loss guarantees.

**Affected area:** Agent-brain exact inverse journal size.
**Description:** A small deletion proposal can capture a large before-image, and JSON escaping can make the serialized record exceed the raw artifact size.
**Workaround:** Prepare checks the 8 MiB encoded history bound with reserved completion metadata before persisting preparation; every journal save enforces the same reader bound. `PUBLICATION_TOO_LARGE` leaves guidance unchanged. Reduce independently coherent scope without truncation; an indivisible oversized artifact remains unsupported.

**Affected area:** Agent-brain completion output and eligible recovery.
**Description:** A process can finish checked effects before output flush, including during recovered completion. SQLite may also be unavailable when known failed output tries to revoke authority.
**Workaround:** Durably mark unfinished delivery before completion, validate marker shape/identities/generations before reconciliation effects, preserve damaged or unavailable markers, and settle only matching generations after successful flush. Recovery must use the exact selected config path and revision. A new task can deliver a recovered prior task's completion; settle that journal-bound identity before new context, preserving failed output and granting dream credit only for checked current result bytes. Native adapters defer subprocess recovery checks to an issued foreground stage; nested legacy gates cannot settle fresh authority before their outer provider output. Actual provider output consumption and timeout behavior remain unverified. See [the lifecycle protocol](../../../skills/agent-brain/references/lifecycle.md).

**Affected area:** Native adapter pinned input and cumulative callback work.
**Description:** A FIFO masquerading as registration can block before JSON input; even a read-only source scanner can outlive the native callback budget. Returning an expired duplicate foreground ticket strands automatic recovery.
**Workaround:** Reject special/linked/oversized pinned files before reads, retain a cumulative watchdog through output/cleanup, and compare bounded recorded canonical source hashes/inventories in callbacks. Drift issues foreground work before checks/effects/attempts. Reissue expired opaque tickets without resetting ownership or semantic attempt counts. A flushed active/awaiting_user/pause/cancel parent checkpoint needs an exact turn release through both adapter and legacy source stop gate, retaining pending work without marking completion or bypassing children. Internal expiry is not observed provider fail-closed behavior; deployment requires an observed foreground route, especially when a first-task prompt denial might prevent recovery execution.

**Affected area:** Native task arrival after pause/cancel.
**Description:** Reusing a stopped objective for every provider turn can return empty context and strand the conversation; automatically making every clarification a new task loses continuity and resets budgets.
**Workaround:** Issue explicit bound foreground intent on stopped-task arrival. `--objective new` registers independent work while preserving the old stopped identity; `resume` restores only the same paused task and its current context without spending/resetting semantic attempts; `retain_stopped` keeps it stopped and releases that turn. Cancelled tasks reject resume. Startup/provider resume alone cannot unpause an objective; active clarifications retain identity. Preserve pending source/publication and child obligations throughout.

### Registered native commands require literal shell parsing
**Description:** Alternating flag/value parsing rejects standalone `--json`, while `shlex.split` alone discards quoting information and can admit double-quoted command substitution as an ordinary argument.
**Workaround:** Reject shell evaluation syntax before splitting literal arguments, then validate unique known flags, the exact selected config and current invocation/stage binding. Preserve single/double quoted literal paths and public pre-tool regressions for substitutions, backticks, composition and malformed options.

**Affected area:** Optional agent-brain source publication and early readiness.
**Description:** Internal receipt revision updates cannot stand in for actual guidance delivery; source proposals can introduce requirements to previously undisclosed units. A checked source learn also must not force duplicate ingestion evidence onto its assigned dream.
**Workaround:** Bind existing knowledge-document bases before source publication, return the complete current relevant delivery after checked changes, and settle matching output generations after flush. Preserve unfinished objectives and their final post-work learn obligation. Dream joins the current checked source revision without another ingest pass; later drift invalidates readiness. Source semantic writes use the existing reversible journal, while the pinned canonical scanner owns mechanical source state.
