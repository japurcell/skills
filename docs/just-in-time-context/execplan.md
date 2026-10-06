# Implement agent-brain across the selected provider surfaces

This ExecPlan is a living document at `docs/just-in-time-context/execplan.md`. Maintain it according to the repository's `exec-plans` skill. Keep Progress, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective synchronized at every stopping point.

## Purpose / Big Picture


After this work, an agent starting a task receives a compact knowledge map and the applicable guidance before relying on it. When the objective finishes, that same foreground agent records evidenced lessons, refreshes affected knowledge, and completes an assigned maintenance batch when due. The user never has to remember to invoke those stages. The `agent-brain` skill and Python CLI are reusable across repositories; knowledge stays isolated by repository and worktree.

The observable demonstration is a disposable repository with a policy, an outdated fact, and an unrelated custom hook. A certified provider must retrieve the policy before its governed action, correct the fact through a checked foreground learn pass, preserve the unrelated hook, and restore the corrected fact in a fresh session. An interrupted publication remains visibly incomplete and recovers at the next eligible event. A stopped turn alone never establishes successful task completion.

This plan derives execution steps from the ten closed Wayfinder contracts. The plan itself authorizes no implementation, installation, activation, provider launch, or model-evaluation spending. On 2026-10-05, the user invoked execplan-implement and authorized offline implementation milestones 1-9. Live milestones 10-11 still require explicit authorization after their frozen run counts and usage visibility are available. Actual-home installation, pilot activation, provider/model launch, and reopening Lavish remain out of scope. Milestone 12 cannot claim full success while a required target or acceptance gate is unmet.

## Progress


- [x] [milestone-1] Deliver the bundled CLI and an informational recall through the public process boundary.
- [x] (2026-10-06) [milestone-2] Retrieve complete, revision-bound guidance units and validate authoring.
- [x] (2026-10-06) [milestone-3] Automatically coordinate lifecycle checkpoints and verified no-change completion.
- [x] (2026-10-06) [milestone-4] Publish evidenced learn changes with interruption-safe recovery.
- [x] (2026-10-06) [milestone-5] Execute finite, bounded dream cycles and retention-safe cleanup.
- [x] [milestone-6] Join legacy skills and optional source ingestion into one lifecycle obligation.
- [x] (2026-10-06) [milestone-7] Generate and package provider-local native adapters.
- [ ] [milestone-8] Install versioned bundles and apply reversible repository activation.
- [ ] [milestone-9] Complete offline acceptance and freeze live certification inputs and counts.
- [x] (2026-10-06) [milestone-9] Repair public-hook suite isolation so baseline observability writes stay in disposable homes.
- [ ] [milestone-10] Certify selected native provider paths through separately authorized live tests.
- [ ] [milestone-11] Map the pilot KB and measure paired quality, guidance, duration, and usage.
- [ ] [milestone-12] Release only verified combinations and complete documentation and handoff.

## Surprises & Discoveries


Initial source inspection on 2026-10-05 found no `skills/agent-brain/` directory, stage schema, or agent-brain registration. It found the explicit generated-output registry in `hooks/manifest.py`, the maintained test registry in `scripts/test-all.py`, and separate Bash/PowerShell installers. These became extension points for the implementation.

Native events have different guarantees. The accepted contracts record Copilot timeouts as open, Gemini compression as advisory, uncertain Codex desktop behavior, and incomplete child-event coverage. Offline envelope tests cannot certify native delivery or enforcement. A target may remain unsupported after implementation if those constraints cannot be overcome within the selected core.

The pilot's protected whole-document reads can limit attainable context savings. Preserve those obligations and measure the result. Missing the savings gate requires improving retrieval or reporting an unmet target, never weakening policy.

The shared public-hook baseline previously wrote observability traces under the real `Path.home()` when a suite redirected only `AUDIT_LOG`; test fixtures also compared canonical `/var` paths against `/private/var`, leaked temporary-home cleanup, and left helper artifacts and probe streams behind. The M9 test-isolation repair is integrated. The parent verified `rtk proxy python3 scripts/test-all.py` at M2 integrated commit `02ab8c36deb07a186d5f99e764903e5764fdd7e2`: exit 0, 38 suites passed/0 failed in 316.0 seconds, both observability suites passing, and Windows-native cases visibly skipped on macOS. M9 full acceptance remains open.

M2 review exposed closure and delivery edges that need public tests: startup without a task should not preload conditional facts; contained units of whole reads must expand their own requirements even after a late loading-mode upgrade; candidates cannot satisfy required established policy even when already selected; and section artifacts must partition nested annotations without losing later parent exceptions. Ordinary evidence output is summarized per delivered unit, while explicit whole-artifact reads preserve source comments exactly.

The public recall suite reproduced Unicode output failures under `PYTHONIOENCODING=cp1252` for both text and JSON streams; configuring CLI output streams as UTF-8 fixed the complete-artifact paths. This subprocess check validates output behavior under that environment setting, not native Windows support. A final config review also found that `PurePosixPath` removes dot segments while the schema rejects them; typed validation now rejects dot and dot-dot path segments before normalization, and the schema rejects NUL characters as well.

M3 public fault slices exposed provisional output delivery, expanded child assignments, malformed nested durable state, and a reset contention allowance during output settlement. A closed output pipe now revokes authority and leaves completion incomplete; child scope changes require current assigned review; corrupt records return machine-readable unavailable/incomplete status; and one store carries the cumulative contention allowance through output settlement. Restoring the fresh-store behavior reproduced a 0.430-second settlement wait against the controlled 0.4-second operation budget. Raw UTF-8 stdin under cp1252 also reproduced REVIEW_SOURCE_INVALID for a non-ASCII source path; bridge and registered stage input now use UTF-8/strict, with authority validated before semantic input.

Final identity review reproduced startup accepting an uppercase configured certification UUID before later state validation rejected it. Provider certification UUIDs now require lowercase canonical formatting at configuration load, before any state mutation; support/event identities compare exactly, with matching schema patterns. Public coverage proves invalid registration creates no state and corrected registration completes normally.

Malformed numeric input also reproduced empty stdout and tracebacks: a 5000-digit configuration integer exceeded Python's decoder limit, and a 400-digit durable expiry overflowed float conversion. Decoder limits remain enabled; config errors are structured invalid setup/recall results, and oversized expected-state times report unavailable/incomplete without recreation. Nested malformed JSON is also exercised at configuration, bridge, and durable-state seams.

M4 public failures established publication boundaries beyond successful writes. Raw CRLF before-images must survive exact inverse restoration; competing eligible recovery events require exclusive effect ownership; missing/corrupt journals and inconsistent affected-path markers remain unavailable. Interrupted checked completion, including recovered completion, keeps durable delivery pending until flush. Failed-output reconciliation under a held SQLite lock reports unavailable, preserves the marker, and reconciles at a later eligible event using the exact selected config path. Ctrl-C and a second interrupt return structured interruption without a traceback.

Final output-marker review reproduced a damaged identity record escaping initial reconciliation and failing during bridge output settlement. Finite typed marker validation now runs before effects, damaged bytes remain unavailable without a traceback, clearing requires matching input/context generations, and restoring the exact recorded marker permits the next eligible recovery event.

Reference-style Markdown definitions, angle-wrapped paths with spaces, and affected heading fragments must be repaired with stable relocation. Whole-file membership alone overstates affected evidence: a public two-section correction now requires evidence for the changed unit while preserving its untouched neighbor and inherited notes. New/corrected learned units retain compact colocated source/verification notes, with full evidence in inverse history and selective recall detail. A small deletion of a JSON-escaped before-image previously prepared an unreadable journal; preparation now rejects an encoded set over the 8 MiB history limit before persisting preparation or changing guidance.

M5 public recovery tests exposed credit and delivery identity gaps: a recovered dream publication needs exact checked resulting-revision credit, and a new task's startup must settle the recovered prior task's marker before its own context. Final publication can change a previously credited required reference, so full-cycle closure rechecks all credits against current guidance. A structural gap must retain the mapped primary identity and incomplete assignment. Malformed targets, credits, batches, dispositions, and cleanup paths require typed cross-reference validation before projection or mutation. Python 3.13 also exposed unclosed fault-fixture SQLite connections; those fixtures now explicitly close them.

M7 public reviews reproduced a FIFO blocking registration before input; nested native source-gate settlement granting authority despite closed output; expired duplicate recovery tickets; callback scanner execution and new-source drift; repeated stop blocks after verified active/awaiting_user/pause/cancel; and empty context on subsequent stopped-task user work. Repairs reject special/linked/oversized pins before execution, keep nested gate authority unavailable, reissue expired opaque tickets without semantic attempt changes, compare recorded canonical source inputs without scanner execution, release only exact flushed parent checkpoints, and require issued new/resume/retain-stopped intent. Explicit paused resume preserves identity and attempts; cancellation cannot resume. A linked runnable directory also executed entrypoint code before core validation; launcher inventory now rejects each path component before launching it. Concurrent expiry tests exposed an alarm interrupting its own denial envelope; reserved bounded failure output now disarms that expired alarm. Parent public proof independently verifies the six original blockers and linked-directory repair. Fake payloads certify none of these native host consumption assumptions.

Final public command review reproduced rejection of a valid registered `learn start ... --json` and admission of a double-quoted shell substitution. Literal shell scanning now precedes argument splitting; unique standalone/value options and exact config/invocation/stage binding are validated separately. Public pre-tool cases preserve quoted literal paths and reject duplicate/unknown/malformed options, mismatched config/handle/stage, backticks, substitutions and composition. Parent independently verifies the exact substitution denial and valid JSON command admission. Final adapter/lifecycle/CLI reruns pass on all three exact runtimes. One validation command initially used a nonexistent CLI filename; the actual maintained suite was then run successfully, without skipping checks.

## Decision Log


Decision: Preserve the completed Wayfinder map and put execution sequencing in this separate file. Rationale: the map owns accepted decisions; implementing the system is a separate effort. Date/Author: 2026-10-05, Codex.

Decision: Use twelve sequential, independently observable milestones, with shared behavior exercised through public CLI processes before native adapters. Rationale: one deterministic core avoids provider-specific semantic implementations and permits fault tests without paid model runs. This is implementation sequencing, not a new product contract. Date/Author: 2026-10-05, Codex.

Decision: Use a bundled `agent_brain` Python package, a public CLI entrypoint, and a separate internal integration-bridge entrypoint. Rationale: six human commands remain understandable while adapters can register verified lifecycle context without caller-supplied identity becoming authority. Native messages and transcripts still require per-path proof. Date/Author: 2026-10-05, Codex.

Decision: Publish immutable software bundles under `~/.agents/agent-brain/versions/<version>/`, expose platform launchers, and pin repository activation to an installed bundle and certification identity. Rationale: the accepted immutable-version contract needs a concrete installation location; it stays separate from portable repository knowledge and worktree-local state. This path is a software layout choice, not a replacement for accepted repository-scoped paths. Date/Author: 2026-10-05, Codex.

Decision: Keep the initial bundle standard-library-only and make `repository_id` a canonical UUID in the typed validator and versioned schema from its first public release. Rationale: M1 can run without dependency installation, and the accepted repository identity must not acquire a looser schema meaning before later lifecycle milestones. Date/Author: 2026-10-05, Codex.

Decision: Configure CLI output as UTF-8 and reject noncanonical dot path segments before path normalization. Rationale: complete Unicode artifacts must remain printable under legacy ambient encodings, and runtime config validation must agree with its schema. Date/Author: 2026-10-05, Codex.

Decision: Unknown task scope returns required startup and universal policy; full-library retrieval is explicit, and every delivery gap remains visible in JSON and stderr. Rationale: avoid preloading unrelated guidance while preserving mandatory obligations and actionable failures. Date/Author: 2026-10-06, Codex.

Decision: Keep protocol delivery provisional until stdout flush, carry one contention allowance across operation phases, and bind no-change to actual foreground checks and current review revisions. Rationale: process exit, unseen output, stale receipts, and caller assertions cannot establish available guidance or semantic completion. Native output consumption remains a separate certification gate. Date/Author: 2026-10-06, Codex.

Decision: Validate foreground-authored proposals mechanically and publish only their exact recorded set, with portable raw-byte history, exclusive effect ownership, and managed affected gaps. Rationale: semantic evidence remains proportional and agent-authored while deterministic revisions, protected policy, references, actual checks, and attributable inverses prevent unsupported completion. One indivisible journal over 8 MiB remains unsupported without truncation. Date/Author: 2026-10-06, Codex.

Decision: Defer required native recovery checks to foreground work through an explicit recovery seam. Rationale: trusted subprocess checks can exceed the native callback watchdog; fixture bridge recovery proves the common protocol only. M7 must issue a supported foreground recovery stage without spending/resetting attempts on callback timeout. Date/Author: 2026-10-06, Codex.

Decision: Freeze finite cycle identities and revisions, assign one bounded foreground dream batch at eligible completion, and credit only checked exact dispositions after successful output settlement. Rationale: later additions cannot grow the current cycle indefinitely, changed targets cannot retain stale credit, and output failure/recovery cannot silently complete required work. Required references and guidance metadata count toward the batch target; oversized closures remain whole. Date/Author: 2026-10-06, Codex.

Decision: Keep native callbacks deterministic and short, issue opaque foreground continuations for checks/source reconciliation, and release a stopping turn only through its exact flushed checkpoint. A stopped-task arrival requires explicit issued new/resume/retain-stopped intent; only paused work may resume with the same identity. Rationale: stopping a turn does not complete an objective, callbacks cannot spend semantic retries or run scanner locks, and provider consumption/foreground route admission remain observed certification requirements. Date/Author: 2026-10-06, Codex.

## Outcomes & Retrospective

M7 delivers seven generated standalone entrypoints/assets, inactive templates, strict native envelopes, exact copied-bundle/build/mode/configuration pins, cumulative callback watchdogs and issued foreground recovery/task intent. Ordinary native source gates join the existing verified obligation without private fixture payload fields or fresh nested output authority. Long trusted checks/scanner locks stay foreground; callback source freshness compares recorded exact inputs. Expired duplicate tickets, checkpoint turn release, paused continuity, cancelled independent work and closed operational retention preserve semantic budgets and pending work.

The 27 independent adapter cases pass with ResourceWarning errors on exact Python 3.12.14 (83.371 seconds), 3.13.14 (79.999 seconds), and 3.14.6 (89.175 seconds). Latest lifecycle 38/38, publication 36/36, maintenance 17/17, compatibility 23/23 and registry 14/14 pass on all three builds; Final lifecycle 38/38 and CLI 26/26 reruns after command-admission repair pass on all three; retrieval 22/22 also passes on all three. Both legacy source suites, provider probe 10/10, generator 26/26/freshness for 33 outputs, OKF fixtures/full corpus, skill validation/exact disposable package of 59 shipping files, 31 JSON parses/88 local schema references/10 example shape checks, 45 broad and 25 changed-source compilations, changed-document links and diff checks pass. One formal update-agent-docs/OKF pass synchronizes ten existing canonical documents; INDEX needs no new entry, and protected AGENTS/raw sources/pilot semantics remain unchanged. M8 is next/open, and M9 retains full offline aggregate acceptance. No installed provider build/event consumption, watchdog enforcement, first-task foreground route, native Windows behavior, semantic quality, product timing/tokens/usage benefit or power-loss durability is verified.

M5 adds finite UTC-calendar dream cycles, foreground batches, exact revision/disposition credit, whole oversized and undeliverable closures, and selective 30-day operational retention through the existing publication engine. Its 17 independent public subprocess cases pass with ResourceWarning treated as an error on exact Python 3.12.14 (24.037 seconds), 3.13.14 (22.824 seconds), and 3.14.6 (21.120 seconds). Shared fixture helpers do not inherit publication checks. Final default-runtime lifecycle 38/38 (23.144 seconds), publication 36/36 (19.470 seconds), retrieval 22/22 (2.417 seconds), CLI 26/26 (2.935 seconds), and registry 14/14 pass. OKF fixtures/full corpus, quick skill validation, disposable package content, 23 JSON parses/local schema references, 21 source compilations, and diff checks pass. The formal update-agent-docs/OKF pass synchronizes eight existing canonical documents without protected AGENTS or pilot KB edits.

Parent public fault reproductions independently verify exact checked resulting-revision credit after interrupted dream recovery, including startup for a different task. The prior task's pending marker clears, its cycle closes with both exact credits, and the new task remains active/available. Parent malformed-credit injection verifies unavailable/incomplete public status without counting damaged credit. Full-cycle closure revalidates every prior credit after final publication or concurrent learn; required learn/child/source obligations remain separate completion gates. No reproduced blocking M5 review finding remains. No new broad aggregate, native support, semantic quality, total delivered tokens, timing/usage benefit, or OS-crash/power-loss proof is claimed.

Milestones 1-4 provide the staged source-checkout skill, scoped revision-bound retrieval, common-protocol lifecycle coordination, checked no-change, and evidenced exact-set learn publication with reversible interrupted recovery. M4's public publication suite passes 36/36 with ResourceWarning treated as an error on Python 3.14.6 (21.237 seconds), 3.13.14 (20.812 seconds), and bundled 3.12.14 (21.769 seconds). Final default-runtime lifecycle 38/38 (24.784 seconds), CLI 26/26 (3.078 seconds), retrieval 22/22 (2.652 seconds), and registry 14/14 (10.215 seconds) pass. Applicable OKF public fixtures and full-corpus linter, quick skill validation, disposable packaging/content verification, 21 JSON parses with local schema references resolved, 18 Python source compilations, and whitespace checks pass. The one formal update-agent-docs/OKF pass synchronizes eight existing instruction/memory documents; FILE_MAP/API_MAP/TESTING_STRATEGY route the new boundaries, and INDEX needs no new entry. Protected AGENTS sections and the pilot KB remain unchanged.

The parent verified the integrated M2 aggregate at 38 suites passed/0 failed in 316.0 seconds and integrated M3 at `270bce3de06b33cf26020a1e513c8718a58940a5` at 39 suites/0 failures in 344.0 seconds, with host-specific Windows skips explicit. M4 is reviewed and integrated at `0d7148fa04d456cb690a08632127d6b0d43409bf` through a conflict-free rebase and exact-tip fast-forward; its clean private worktree and branch are removed. Targeted M4 checks and parent public fault reproductions pass with no unresolved review finding. No new broad aggregate is claimed; M9 retains full offline aggregate acceptance. M5 is reviewed and integrated at `bb99a386e2cd60269cfcff64dfdac4fb60bf1e15` through a conflict-free rebase and exact-tip fast-forward. Its clean private worktree and branch are removed. M6 is reviewed and integrated at `9d8b5d9ccb66e2229b305ff408da18e2c84665de` through a conflict-free rebase and exact-tip fast-forward. Its clean private worktree and branch are removed. M8 and M9 full acceptance remain open. Offline milestones 1-9 are authorized; live milestones 10-11 require separate explicit authorization. Native provider builds/consumption/watchdogs, native Windows locking, quality, savings, timing, usage, and OS-crash/power-loss guarantees remain unobserved. One coherent encoded journal over 8 MiB is unsupported without truncation; individual replacements provide no unmanaged set-level atomic visibility. The closed Wayfinder map remains unchanged.

## Context and Orientation


The repository publishes reusable skill directories from `skills/`, installs them with `scripts/install.sh` or `scripts/install.ps1`, and generates provider-local Python hooks from canonical sources in `hooks/families/`. `hooks/manifest.py` enumerates owned generated files. `scripts/generate-hooks.py --write` refreshes those files; `--check` proves freshness without writing. Consumers of agent-brain receive runnable adapters and templates; they need neither this repository's generator nor its canonical hook families.

Canonical agent-facing policy lives in `.agents/instructions/`; descriptive knowledge lives in `.agents/memory/`. `AGENTS.md`, `.agents/memory/INDEX.md`, and provider entrypoints route readers to authoritative content. Existing repositories can map artifacts in place, including protected or externally owned documents. A new repository starts with a minimal map and configuration. Do not create a second KB, depend on uniform discovery of nested `AGENTS.md`, or copy knowledge between repositories automatically.

Before implementation edits, read `.agents/memory/INDEX.md`, then architecture/conventions, then affected-area instructions and known-issues/testing guidance. Relevant areas are skills, hooks, source auto-ingest, scripts, PowerShell, and repository docs. Load `create-skill` when creating the actual publishable skill, `tdd` before source design/edits, and `okf-authoring` for canonical Markdown changes. Use the public seams already accepted in Adoption and Validation Contract: CLI processes, provider JSON entrypoints/registrations, and resulting files, guidance delivery, task behavior, and completion/recovery status. Write one failing behavior test, implement that slice, and repeat. Do not test private database layout to prove public lifecycle behavior.

At the end of each code work session complete one formal `update-agent-docs` pass. Keep `.agents/memory/FILE_MAP.md`, API/test routing, affected instructions, and durable known issues synchronized. Do not modify the protected ExecPlans, Agent Orientation, End of Work Session Defined, or Validation Checklist sections in root `AGENTS.md`. This plan preserves their existing required reads, including their ordering. Raw `.agents/sources/` files remain immutable. Harness-owned source fixtures must be created only in disposable repositories.

### Terms and responsibilities


A task is the user's objective across clarification turns. A turn is one response cycle. A provider session is the conversation/runtime container. A work session finishes when the requested task or task batch, including delegated work, is done. Waiting for the user or ending a turn does not finish that objective.

Recall interprets current scope and retrieves the map and relevant guidance. Learn adds/corrects evidenced knowledge and refreshes guidance affected by completed work. Dream consolidates, repairs, reorganizes, and prunes under the same evidence policy. The active foreground provider agent performs semantic work, meaning judgments about relevance, lesson validity, factual uncertainty, and policy meaning. The Python core performs deterministic retrieval, state coordination, checks, and publication. A thin adapter translates a native event into this common protocol. The core launches no model, maintenance subagent, independent runner, or background service.

A guidance unit is a coherent section or small document with its exceptions and required references. A guidance closure is that unit plus all required linked guidance and whole-artifact loading obligations. A stable UUID identifies meaning independently of its current path. A revision is a derived SHA-256 digest of content, applicability, references, or inputs. A generation is an increasing integer that invalidates older ownership, input, or context records.

An obligation is required work with durable identity and scope. An attempt is one eligible execution of it. An opaque invocation handle is issued by an enabled integration and checked against its local registration; it is operational permission, not user instruction authority or protection against another process with the same local access. A lease is a finite registration or ownership lifetime. A delivery receipt records which guidance was delivered to which agent/context generation; it never proves the agent applied it or still has it after compaction. Certification is evidence that one exact build/configuration/entry path meets the required contract. Targeted does not mean certified.

### Accepted behavior to preserve


Startup provides applicable user/global instructions, universal repository policy, a compact map, and the retrieval procedure. Explicit loading requirements and order survive optimization. Retrieve conditional guidance before dependent edits, actions, or read-only conclusions. Scope includes task intent, planned actions, paths, concepts, dependencies, and provider/runtime. Reevaluate on meaningful scope or input changes. Uncertain scope broadens lookup. Check known mandatory coverage and complete delivery; this is not an exhaustive search of every useful fact. Recover missing guidance through focused search and authoritative fallback, pausing only dependent work when required context remains unavailable.

Established guidance precedes uncertainty relevant to the task. Candidates remain unverified and appear only for investigation. External content supplies evidence without becoming instruction authority. Preserve explicit policy meaning and applicability. Repair clear descriptive drift from controlling sources. Ask the user only about unresolved intent/policy or missing input that automatic recovery cannot obtain.

Evidence is proportional. A descriptive fact needs source identity/revision and a short verification note. A low-risk tip needs its observed failure, successful workaround, and scope, without a dedicated replay. Broader rules, corrections, and pruning need stronger appropriate checks. Record source/applicability/verification and reversible rationale. Prune only with evidence of error, obsolescence, or complete redundancy, preserving important exceptions and counterexamples. Age and inactivity prioritize review and never authorize deletion. Routine use requires no full transcripts, per-sentence claim records, or detailed usage attribution.

Every executing agent receives startup and assigned-scope context. Restore missing/current guidance on resume/compaction and verify child delivery rather than assuming inheritance. Optional authorized task children have their own registrations and return outcomes/candidates. The parent owns aggregate completion learning and its routine dream batch; a child stop does not create a second full maintenance pass. Missing verified child delivery keeps that child path unsupported.

At automatically initiated checkpoints, the foreground agent classifies the objective as active, awaiting user input, or ready to complete. The bridge validates observed scope and obligations; missing classification requests a compact checkpoint. Required learn/refresh and any assigned due dream batch must finish, including checked no-change, before successful completion. Injection, a process exit, a receipt, or an agent's assertion alone is insufficient. Interruption, exhausted retries, or continuation caps preserve visible incomplete work. Recovery runs at the next eligible startup/resume/task event with access and authorization, respecting pause/cancellation. Idle and shutdown do not promise unconditional execution.

### Existing source and validation boundaries


Source auto-ingest has one detector/manifest owner: `hooks/families/auto_ingest.py` renders the engine and provider wrappers from `hooks/families/auto_ingest_engine.py` and adjacent wrapper sources. The committed manifest is `.agents/memory/sources/source-ingest-manifest.json`. `.agents/skills/ingest-source/SKILL.md` is the focused semantic ingestion procedure. Generated startup/injector/gate code detects and blocks pending work; it does not perform semantic integration. Preserve existing source-summary and manifest contracts and join them into one learn pass. Codex currently lacks this repo's source-ingestion wiring; implement it through the optional common adapter rather than a second scanner.

`scripts/lint-okf.py` validates the canonical KB with its checked-in PyYAML runtime. Its public modes are `--format human|json`, with exit 0 clean, 1 findings, and 2 infrastructure failure. The reusable agent-brain core remains standard-library only: it does not parse arbitrary YAML or depend on the repo's vendored package. Preserve frontmatter bytes and validate new JSON annotations in the common core. The repo linter can call that validator and translate findings at its existing seam. `scripts/test-okf-lint.sh` and provider-specific OKF suites prove that existing behavior remains intact.

`scripts/test-all.py` maintains explicit offline suite registration. It does not run model evaluations. Existing Bash and PowerShell installer fixtures use disposable homes and prove preflight, preservation, and idempotence. Add agent-brain public suites to this registry without recursively executing it or adding live model runs.

## Plan of Work


Execute milestones in order. Each adds usable behavior through an agreed public boundary. New modules listed here are proposed paths, not existing implementation. Keep native registrations inactive in ordinary repositories until matching certification exists. Live proof is a separate phase with explicit execution authorization. Update Progress and the matching milestone state in the same edit whenever acceptance is met.

### Milestone 1: Run the bundled CLI and informational recall


Status: complete

Acceptance: met. Public subprocess behavior passes 26/26 under Python 3.14.6 and 3.13.14, including copied-bundle help/version bytecode checks, argument-placement and abbreviation rules, JSON/plain streams, guarded learn/dream inputs, read-only state commands, Unicode full-artifact recall under cp1252 ambient encoding, and invalid config paths. `quick_validate.py` reports the skill valid; the registry-focused suite passes 14/14; all 11 bundled JSON schema/example/eval files parse; seven Python sources compile; direct `--version` prints `agent-brain 0.1.0`. These checks do not certify Python 3.12 or native provider support.

Create `skills/agent-brain/SKILL.md`, progressive references `recall.md`, `learn.md`, and `dream.md` under its `references/`, and `scripts/agent-brain.py` under the skill as the source-checkout entrypoint. Put implementation in `skills/agent-brain/scripts/agent_brain/`. Start with `cli.py`, `config.py`, `records.py`, and `knowledge.py`; introduce later modules only with their behavior tests. Add version metadata and versioned schemas under `skills/agent-brain/schemas/`, with examples under `skills/agent-brain/examples/`.

Add `scripts/test-agent-brain-cli.py`, initially proving bare invocation, help aliases, version-only output, missing-state doctor/status, and whole-artifact informational recall in a disposable repository. Preserve the requested read order. Learn/dream without registered active context return exit 2 and an actionable message before creating state or changing knowledge. Show that provider-named environment variables do not bypass the guard. The command explains that the active provider agent performs semantic work and the CLI never launches a model. No startup/presentation path downloads dependencies or makes a model call.

Run `rtk proxy python3 scripts/test-agent-brain-cli.py` and `rtk proxy python3 skills/skill-creator/scripts/quick_validate.py skills/agent-brain`. Expect successful offline process assertions and a valid skill. Help and diagnostics leave the fixture tree unchanged; recall prints the complete mapped artifact but claims no agent-delivery receipt. Register this maintained suite in `scripts/test-all.py`.

### Milestone 2: Retrieve complete guidance and validate metadata


Status: done

Acceptance: met

Extend `knowledge.py` and add `metadata.py` and `retrieval.py` for document/section units, stable UUIDs, required-reference expansion, conservative applicability matching, and derived content/input revisions. Preserve arbitrary frontmatter as existing prose metadata rather than introducing a YAML dependency. Ignore annotations inside fenced, indented, and inline code examples. Defaults never assign an ID. Sections include unannotated subheadings through the next peer/higher heading and partition nested annotated sections without losing surrounding exceptions. Whole-artifact reads deliver complete content once while retaining contained identities and closing requirements for contained units; their input revisions bind exact artifact content and the full contained-unit dependency closure independent of retrieval selection order.

Add `scripts/test-agent-brain-retrieval.py` at the CLI seam. Independent fixture expectations cover startup-only scope, startup order, read-only relevance, selector expansion, uncertain scope, exception retention, required unit/whole closure, candidates for investigation only, unavailable or truncated delivery, metadata in code examples, duplicate IDs, moved units, unresolved references, evidence disclosure, and external read-only mappings. Use routes plus text search; no embedding or vector store is required. Missing facts never mean no mandatory guidance applies.

Extend `scripts/lint-okf.py` to call the common annotation/reference validator only for configured agent-brain metadata, preserving existing OKF diagnostics and no-config behavior. Update `.agents/skills/okf-authoring/references/profile.md` and its entrypoint with the new representation rules, and applicable authoring examples. This implements the user's accepted authoring/lint change; it does not alter other repo-local skills or protected AGENTS policy. Do not annotate the actual pilot KB yet. Retrieval/CLI, OKF fixture, linter, registry, and skill package checks pass. All current KB guidance remains valid without mandatory annotation or relocation.

### Milestone 3: Coordinate automatic checkpoints and checked no-change


Status: done

Acceptance: met. The public common-protocol lifecycle suite passes 38/38 on exact Python 3.12.14, 3.13.14, and 3.14.6 builds, including objective continuity, unknown checkpoints, actual checked no-change, joined callbacks, input/context drift, finite handles, ownership/recovery, isolated worktrees, missing/corrupt state, pause/cancel, child scope/settlement, failed output, cumulative contention, strict UTF-8/standard JSON input, canonical certification identity, and decoder-limit/durable-time rejection. CLI 26/26 and retrieval 22/22 pass on all three builds; registry 14/14, OKF fixture/linter, skill validation/package, JSON/schema/example alignment, compilation, and diff checks pass. Provider support records exist only in disposable protocol fixtures. Native support, source/publication/dream behavior, and live acceptance measurement remain later milestones.

Add `state.py`, `lifecycle.py`, `checks.py`, and `scripts/integration-bridge.py` to the bundle. The bridge receives normalized lifecycle events from enabled adapters, binds repository/worktree/work-session/task/agent identities, records scoped delivery, issues finite invocation files, and requests the progressively loaded foreground procedure. Add `scripts/test-agent-brain-lifecycle.py` using a disposable registered adapter fixture at the public bridge process boundary. Such fixtures prove protocol behavior, never provider support.

Deliver startup/recall, continue an objective across clarification turns, then classify it ready to complete. Start one learn obligation and complete a scoped no-change only after delivery, review evidence, and configured checks. Independent assertions distinguish successful command operations from incomplete stages and work sessions. Duplicate callbacks join the same obligation; stage-generated callbacks never recursively create learning. Changed relevant inputs make old results ineligible. Missing checkpoint information requests a compact checkpoint rather than running full maintenance on every turn.

Exercise invalid/expired/mismatched handles, restoration after context-generation changes, active-owner contention, stale generations, two agents in one worktree, independent worktrees, and missing/corrupt expected state through bridge/CLI status. A second owner cannot steal a valid lease or publish. Pause/cancel revokes authority without resurrecting the objective. Optional registered children receive scoped delivery and must settle assigned obligations before parent completion. No child means the same lifecycle works in one foreground agent. Run the lifecycle and CLI suites; every status is machine-readable and unverified/no-change assertions cannot complete the session.

### Milestone 4: Publish evidenced learn changes and recover interruption


Status: done

Acceptance: met

Add `stages.py`, `publication.py`, and `history.py`. Implement learn start/prepare/publish/complete, with the foreground agent creating a proposed change/evidence record outside canonical guidance. Prepare checks scope, authority, references, evidence requirements, current owner, input revisions, and configured check results. Publish writes only that validated set. Complete rechecks actual resulting artifacts and receipts against current inputs. No-change skips publication but still verifies review and applicable checks.

Add `scripts/test-agent-brain-publication.py`. Its subprocess cases learn a compact scoped tip, correct a seeded factual error, relocate a stable unit with repaired references, and reject policy-scope changes or unsupported pruning. Check source identity and inverse history independently. Journal before/after bytes and intent durably before writes, stage on each destination filesystem, sync content, replace paths, and verify references before completion. Managed recall either sees a verified coherent view or an explicit affected gap. Do not claim that SQLite makes multiple external files atomic or that unmanaged direct readers get set-level visibility.

Interrupt the public process before durable intent, after intent before files, between file replacements, after final replacement before checks, and after checks before completion. Controlled test barriers make these points reproducible without leaking production authority. At the next eligible bridge event, finish a still-valid set or restore only recorded changes, retaining unexpected edits and unresolved conflict records. Test harmful-update restoration, Ctrl-C and second interrupt, missing/corrupt state, stale bases, and bounded retry exhaustion. Public status and files prove recovery; direct database inspection is not the acceptance seam. Run publication, lifecycle, retrieval, and CLI suites for this changed behavior.

### Milestone 5: Complete bounded dream batches without losing coverage


Status: done

Acceptance: met

Add `maintenance.py` and extend dream's common stage operations. Activation makes the first routine cycle due. Use UTC calendar dates and a seven-day default, coalescing missed intervals. On an eligible completion assign one batch of at most five primary units/candidates, targeting at most 32 KiB UTF-8 complete guidance including references. Reserve one slot for rotating quiet-area review when available. Review flagged guidance and relevant candidates; cheap structural checks cover the mapped KB. An indivisible oversized closure runs alone, is marked oversized, and counts in measurements. Undeliverable content remains whole and the required batch remains incomplete.

Add `scripts/test-agent-brain-maintenance.py` with a fixture clock, never a changed host clock. Freeze finite cycle targets and revisions, credit verified reviewed dispositions, invalidate changed targets, and explicitly queue later additions. A no-change batch closes only its own obligation. Remaining unassigned coverage stays pending while the work session can complete; an unfinished assigned batch prevents completion. Reset the periodic clock only after every target credit remains valid and full-cycle obligations settle. Urgent factual repair still runs before dependent work.

Through dream/status and actual files, prove quiet-area progress despite new flags, two full cycles, evidence-backed pruning with preserved counterexamples, and retention. Retire only closed unreferenced operational records after 30 days, preserving unresolved candidates, active ownership/publication/recovery, required portable evidence/history, and validation-pinned records. Never remove the active database/identity container as cleanup. No idle model job is started. Run maintenance and affected lifecycle/publication suites.

### Milestone 6: Join legacy workflows and optional source ingestion


Status: complete

Acceptance: met

Add `source_ingestion.py` as an optional configured bridge to the existing scanner/manifest contract. Keep `hooks/families/auto_ingest_engine.py` as the single source-change reconciliation owner; do not copy a second freshness engine into agent-brain. Extend canonical wrappers/coordinators as needed to join the same learn obligation. The foreground learn procedure calls `.agents/skills/ingest-source/SKILL.md` once for all blocking entries, then refreshes affected knowledge. Existing gates observe the matching verified result. Repositories without source ingestion need no scanner or ingestion skill.

M6 provides the optional pinned canonical engine/bridge, early active-objective source learning, action/conclusion gaps, one joined obligation, exact current source/summary/knowledge evidence and separate orphan dispositions. Semantic summary and KB changes use M4's pre-effect checked reversible publication; direct writes followed by recover cannot satisfy learning. Early completion returns self-contained current guidance, including newly required units, while final objective learning remains separate. Assigned dream joins checked source learning without recursive ingestion. Known unresolved source gaps survive a different task identity; independent known scope can proceed without affected guidance, and canceled objectives remain stopped while later checked source work may settle shared prerequisites. Read-only external policy revisions restore context separately from owned semantic bases.

The 23 independent public compatibility cases pass with ResourceWarning as an error on exact Python 3.12.14 (35.563 seconds), 3.13.14 (35.568 seconds) and 3.14.6 (35.854 seconds). Lifecycle 38/38, publication 36/36 and maintenance 17/17 pass on all three runtimes; default CLI 26/26, retrieval 22/22 and registry 14/14 pass. Both legacy auto-ingest suites, generator 25/25 and freshness for 26 outputs, OKF fixtures/full corpus, skill validation/exact disposable package, 25 JSON parses/79 local schema references, 29 source compilations and 73 changed-doc links pass. Generator snapshot acceptance runs alone after concurrent review bytecode/edits invalidated an earlier read-only comparison; its assertions remain intact. Legacy summary-path basename sanitization remains supported, expected damaged manifests stay preserved before effects, linked parents are rejected, and locking fails closed with a controlled Windows byte-lock branch.

Parent public reproductions independently verify malformed-manifest/linked-parent preservation, checked source changed sets and exact inverses, interrupted inverse restoration after raw drift, prior-task unjournaled rejection, actual new required-unit delivery and combined source/dream completion. No reproduced blocking review finding remains. The single formal update-agent-docs/OKF pass synchronizes eleven existing canonical instruction/memory documents; INDEX requires no new entry, protected root sections and immutable raw sources remain untouched. No broad aggregate, native callbacks/consumption/watchdog or native Windows certification, semantic quality, performance/cost benefit, or OS-crash/power-loss proof is claimed. At M6 integration, M7 was next/open; M9 retains full offline aggregate acceptance.

Update `.agents/skills/update-agent-docs/SKILL.md` and `.agents/skills/clean-agent-docs/SKILL.md` with conditional delegation to the activated canonical learn/dream procedure. Preserve their current working behavior when agent-brain is not activated or unsupported; never silently bypass existing doc obligations. Delegating entries join current input generations rather than recursively start another pass. Keep the focused ingestion procedure separate. These specific compatibility changes are part of the accepted migration, not a general permission to edit unrelated local skills.

Add `scripts/test-agent-brain-compatibility.py` through the bridge, CLI, generated scanner/gate entrypoints, and output artifacts. Exercise new/changed/renamed/removed harness-owned sources, one coordinated pass requested by three gates, mid-pass source changes, missing ingestion access, and a no-source repository. Preserve immutable originals and existing summary/manifest states. Run the compatibility suite, both `test-hooks-auto-ingest.sh` and `test-gemini-hooks-auto-ingest.sh`, and generator freshness/tests after canonical renderer changes. An interrupted join remains visibly pending and cannot become a pass through a compatibility entry.

### Milestone 7: Generate thin adapters with provider-native envelopes


Status: complete

Acceptance: met

M7 offline implementation is complete in private worktree `/private/tmp/agent-brain-m7`, branch `codex/agent-brain-m7`, from clean checkpoint `20e896fb5b410b8a41fa3a8d5f8fe929a6edd267` over integrated M6. Public acceptance covers all generated entrypoints/copied assets, strict native envelopes, staggered UTF-8 pipe input without EOF, exact native pins, unsupported mode/event paths, tighter internal expiry, source-gate joins, compaction/children, foreground controls/task intent, delayed exact publication recovery, turn release and operational retention. The 27-case exact three-runtime matrix and affected shared suites pass. Generator output remains renderer-owned; registrations are inactive. M8 is next/open. No native build, model boundary, foreground route admission, consumption or provider watchdog is certified.

Parent review reproduced premature output settlement through the nested native legacy gate: closing the bridge stdout still permitted a subsequent tool. The repaired gate issues foreground restoration and invalidates existing context without settling fresh delivery because it cannot observe the outer hook flush. Public failed-output proof now requires the subsequent tool to deny. Previously checked completed results or exact flushed active/awaiting_user/pause/cancel parent checkpoints may release only that stopping turn read-only; pending source/publication and child review stay intact. The parent independently verifies FIFO rejection, output failure, expired ticket renewal, scanner exclusion/new-source drift, turn release, paused continuity and cancelled new-task behavior. First-task paths with no observed foreground continuation route remain unsupported for deployed activation and require M10 certification.

Create `hooks/families/agent_brain.py`, parameterized through `hooks/providers.py`. Add explicit generated outputs in `hooks/manifest.py` for `.codex/hooks/agent-brain.py`, `.copilot/hooks/scripts/agent-brain.py`, `.github/hooks/scripts/agent-brain.py`, and `.gemini/hooks/scripts/agent-brain.py`. Extend the generator's allowed outputs to packaged adapter copies under `skills/agent-brain/assets/adapters/` as explicitly owned targets, with the same source and freshness rules. Put inactive registration templates under `skills/agent-brain/assets/registrations/`. Consumers copy these runnable assets without importing a peer provider or installing the generator.

Add `scripts/test-agent-brain-adapters.py` for each provider's public JSON entrypoint. Bind events to the shared bridge, validate configured identity/version/scope, serialize only native-valid JSON on stdout, and preserve unrelated hooks. Read one complete native JSON value without waiting for pipe EOF; bound incomplete/trailing payload handling. A four-second internal watchdog must finish below a lower configured native deadline and emit the documented denial/incomplete response where supported. Long semantic/check work stays foreground. Avoid content-bearing high-rate pass messages and secret-bearing diagnostics.

Use the native candidate event bindings in Interfaces and Dependencies below. Tests of fake payloads prove translation, not native consumption. Distinguish internal core timeout from the provider killing or ignoring a hook; native timeout-open/advisory behavior remains a certification issue. Do not add an SDK supervisor, desktop attachment service, daemon, or independent model runner to mask a gap. Run adapter tests, `rtk proxy python3 scripts/generate-hooks.py --write`, then `--check` and `scripts/test-generate-hooks.py`. Existing project/global config receives no active agent-brain registration in this milestone.

### Milestone 8: Install immutable bundles and apply reversible activation


Status: open

Acceptance: not met

Add `scripts/install-agent-brain.py`, plus bundled `setup.py` and `diagnostics.py`. Extend both existing installers to preflight and install immutable bundles under the selected software location. Expose `~/.local/bin/agent-brain` on POSIX and `.cmd`/`.ps1` launchers under `%LOCALAPPDATA%/agent-brain/bin` on Windows; report required PATH changes without editing shell profiles. Use an explicitly discovered compatible interpreter, with no implicit download. The repository config pins installed core/adapter/schema versions; an unavailable pin is an actionable error, never an automatic substitution of a different bundle.

Plain setup plans exact mappings, prerequisites, ignored state, and managed registrations. Apply accepts a still-valid reviewed plan, verifies base/config/certification inputs again, records inverse changes, and enables only matching certified paths. Copilot defaults to managed `.github/hooks/agent-brain.json`; Codex to managed entries in `.codex/hooks.json`; Gemini to managed entries in `.gemini/settings.json`. Fresh/no-hook repositories need no special family source. Preserve unrelated hook entries, policy/user precedence, trust requirements, protected artifacts, and existing global installation behavior. Software installation alone never activates automatic stages.

Add `scripts/test-agent-brain-setup.py` and extend disposable-home Bash/PowerShell installer tests. Prove fresh minimal repositories, existing unrelated hooks, no canonical families, protected/read-only mappings, spaces/non-ASCII names, linked/ambiguous paths, repeated setup, stale plans, malformed configs, state capability failure, unsupported certification, interrupted apply, upgrades, deactivation, and rollback. Simulated certification records are confined to disposable fixtures. Upgrades preserve active ownership/pending work and require supported explicit migrations; unsupported downgrade stops before mutation. Deactivation removes only owned registrations and revokes authority while retaining portable knowledge/history and recoverable state. Run setup/CLI tests and matching installer suites; macOS PowerShell execution is not native Windows certification.

### Milestone 9: Finish offline acceptance and freeze live execution plans


Status: open

Acceptance: not met

Add `scripts/validate-agent-brain-pilot.py` for offline input checking and report calculation, with `scripts/test-agent-brain-pilot.py` at its process boundary. Put frozen fixture specifications under `scripts/fixtures/agent-brain/`; document planned certification in `docs/just-in-time-context/certification-plan.md` and a sanitized report template in `validation-report.md`. Keep raw operational validation records ignored and pinned. Create a checks manifest with predetermined assertions and per-case source contract traceability. Do not interpret a test's own generated output as its expected semantic truth.

Freeze exact installed provider builds, OS/filesystem, Python/SQLite, permissions, lifecycle configuration, adapter/core/schema versions, models, task variants, repetitions/order, observation methods, tokenizer, and sequence lengths before live execution. Version discovery uses passive metadata or documented version-only commands, never provider prompts. Unknown versions stay unknown until observed; no certification identity can use an invented build. The initial target is macOS ARM64/local APFS. Python 3.12/3.13/3.14 exact builds need deterministic checks. Later Linux CLI and native Windows Copilot/Gemini remain separate expansion; do not schedule Windows Codex desktop/CLI live tests in the user's environment.

Run all new offline suites, applicable existing hook/install/OKF suites, generator freshness, skill validation, and the aggregate runner with its prerequisites. Freeze process-interruption checks separately from OS/power-loss claims. Publish planned task/session counts, critical-case overlap, additional probes, and usage availability. No live model run occurs here. Missing prerequisites are explicit incomplete checks, not successful skips. Full offline acceptance and a reviewable live-run plan make this milestone complete, not provider certification or product acceptance.

### Milestone 10: Certify automatic lifecycle behavior on exact native paths


Status: open

Acceptance: not met

Execute only after explicit live-testing authorization. Use disposable repositories/homes and temporary test registrations, leaving ordinary activation disabled until a support record passes. Certify Codex desktop independently from Codex CLI, then Copilot CLI and Gemini CLI. The harness proves configuration discovery/trust, actual payload/event order, delivery before action or read-only conclusion, foreground stage execution, completion enforcement, and next-event recovery. Cover fresh interactive, resume/compaction, CLI noninteractive, and each selected child launch path separately. Child wrappers apply only to optional authorized task delegation.

Force internal watchdog failures and actual native timeouts as different cases. Verify native stop continuation and the shared retry budget. Test missing child hooks and compaction restoration rather than receipt reuse. Repeat each live semantic critical case three times per claimed path; retain independent human semantic review and deterministic artifact assertions. A required path that cannot meet the contract is an explicit support gap. Passing a different build/path or simulating denial does not conceal that gap. A validated native automatic guard may fill a gap within the accepted foreground design; introducing another model executor or new supervision architecture requires a separate scope decision.

Write exact evidence references and passed/unsupported/inconclusive status to a versioned sanitized support manifest. No automatic guarantees are enabled for nonmatching versions/configurations. If a required target remains unsupported, record partial engineering delivery and unmet overall acceptance; do not mark this milestone or the full plan complete. Do not keep spending repeated probes without new evidence or authorization.

### Milestone 11: Preserve the pilot KB and measure paired outcomes


Status: open

Acceptance: not met

Map the pilot's authoritative artifacts in place first, retaining protected reads and order. Apply section annotations selectively only after milestone 2's authoring/lint support and milestone 10's applicable certified path exist. Use disposable pilot copies for live workloads. Freeze the baseline workflow and equivalent initial guidance/sources in separate worktrees; each arm owns its own operational state and maintenance. Retain the true current workflow as baseline, including existing required docs and source gates. Do not weaken the baseline or move candidate maintenance outside the task window.

Run the ten task variants and repeated sequences in Validation and Acceptance below under the already published execution budget. Four isolated repeats per variant give 40 pairs. Add two paired sequences of at least ten tasks each, lengthened before execution if necessary for two complete dream cycles per sequence, followed by fresh-session checks. Vary order according to the frozen plan and retain every critical failure. Observe actual delivered guidance, monotonic timing through maintenance, paired quality, independent semantic review, and total provider-reported task usage where available. Do not add observer model sessions.

Use the offline report tool to compute per-cohort medians and nearest-rank empirical 95th percentiles and compare the accepted gates. Unknown visibility/tokenization/usage is disclosed, never zero. Missing validated delivery/tokenization makes performance inconclusive. Fix every unresolved system-caused task regression and refreeze changed experiments before new measurements. If required guidance or performance gates cannot pass, report the unmet result; never relax policy, omit costs, censor failures, or aggregate away a failing cohort. Actual certified pilot activation remains an explicit reviewed setup action, separate from measurement in disposable copies.

### Milestone 12: Release verified combinations and finish the handoff


Status: open

Acceptance: not met

Publish only immutable bundles and support records backed by actual tests. Update `README.md`, applicable `.agents/instructions/` and `.agents/memory/` routes, CLI/help references, supported setup/migration procedures, and the feature handoff with the exact implemented behavior and remaining gaps. The legacy skills delegate without duplicate semantic execution only on validated activation. Preserve knowledge/candidates/history and reversible managed changes through setup rollback and deactivation.

Perform the final formal doc pass, targeted checks, clean generated-output check, aggregate offline validation, and `git diff --check`. Update this plan's outcomes with measured gate results and exact certified builds/configurations. Product completion requires all intended initial target paths and predefined critical checks, no unresolved system-caused regression, and all accepted measured gates. A partial release may describe verified subsets but leaves the affected milestones and full-plan acceptance open. No push, external release, or broad repository rollout is implied by this plan.

## Concrete Steps


Run from the repository root, currently `/Users/adam/.codex/worktrees/171e/skills`. Prefix shell commands with RTK; use `rtk proxy` where raw output or an unsupported subcommand is required. Verify RTK exists rather than silently dropping it. The following future CLI commands become runnable in milestone 1; they are not commands executed while authoring this plan:

    rtk proxy python3 skills/agent-brain/scripts/agent-brain.py --help
    rtk proxy python3 skills/agent-brain/scripts/agent-brain.py recall --help
    rtk proxy python3 skills/agent-brain/scripts/agent-brain.py learn --help
    rtk proxy python3 skills/agent-brain/scripts/agent-brain.py dream --help
    rtk proxy python3 skills/agent-brain/scripts/agent-brain.py --version
    rtk proxy python3 skills/agent-brain/scripts/agent-brain.py doctor --json
    rtk proxy python3 skills/agent-brain/scripts/agent-brain.py learn --json

Help/version exits 0 without creating state, performing semantic work, or calling a model. Doctor on an unactivated repository reports that state is absent without creating it. The last invocation exits 2 without mutation and explains the need for an enabled active-agent integration. In JSON mode stdout contains one result object; diagnostic text belongs on stderr. An illustrative diagnostic is:

    agent-brain learn: a supported active-agent invocation is required.
    No knowledge was changed. Run this stage through an enabled integration.
    See agent-brain learn --help.

Use the source-checkout entrypoint in fixtures so an installed stale bundle cannot accidentally pass tests. The reusable command is `agent-brain`; its checkout entrypoint and installed launchers must expose the same behavior. Public stage operations have these forms once milestone 4 exists:

    agent-brain learn start --invocation-file PATH --input PATH --json
    agent-brain learn prepare --invocation-file PATH --input PATH --json
    agent-brain learn publish --invocation-file PATH --input PATH --json
    agent-brain learn complete --invocation-file PATH --input PATH --json

Dream has the same operations. Bare learn/dream means start only with valid integration context. `--input -` accepts UTF-8 JSON on stdin; invocation handles stay in an integration-issued file, never command-line identity flags. Keep parsed input and error behavior consistent across file/stdin transports. Start delivers a work package and procedure; it cannot report semantic completion. A completed no-change path uses prepare/complete with review/check evidence and skips publication.

Run the changed slice's suite after its red/green cycle. Once all offline behavior is implemented, these maintained suites must be registered and pass:

    rtk proxy python3 scripts/test-agent-brain-cli.py
    rtk proxy python3 scripts/test-agent-brain-retrieval.py
    rtk proxy python3 scripts/test-agent-brain-lifecycle.py
    rtk proxy python3 scripts/test-agent-brain-publication.py
    rtk proxy python3 scripts/test-agent-brain-maintenance.py
    rtk proxy python3 scripts/test-agent-brain-compatibility.py
    rtk proxy python3 scripts/test-agent-brain-adapters.py
    rtk proxy python3 scripts/test-agent-brain-setup.py
    rtk proxy python3 scripts/test-agent-brain-pilot.py

Use existing validation only for areas changed in that milestone; do not rerun the entire repository after every small slice. Canonical hook changes require generation followed by these checks:

    rtk proxy python3 scripts/generate-hooks.py --write
    rtk proxy python3 scripts/generate-hooks.py --check
    rtk proxy python3 scripts/test-generate-hooks.py

Compatibility changes require `rtk proxy bash scripts/test-hooks-auto-ingest.sh` and `rtk proxy bash scripts/test-gemini-hooks-auto-ingest.sh`. Annotation/lint changes require `rtk proxy bash scripts/test-okf-lint.sh`, `rtk proxy python3 scripts/lint-okf.py`, and the affected provider OKF suites. Installer changes require `rtk proxy bash -n scripts/install.sh`, `rtk proxy bash scripts/test-install.sh`, and `rtk proxy pwsh -NoProfile -File scripts/test-install.ps1`; load the PowerShell instructions first. Packaging checks are `rtk proxy python3 skills/skill-creator/scripts/quick_validate.py skills/agent-brain` and `rtk proxy env PYTHONPATH=skills/skill-creator python3 skills/skill-creator/scripts/package_skill.py skills/agent-brain /tmp/agent-brain-dist`.

At offline integration boundaries, run `rtk proxy python3 scripts/test-all.py` after checking prerequisites: Bash, Python, Git, jq, flock, sqlite3 shell, PowerShell 7+, and ordinary Unix utilities. The aggregate suite's SQLite shell dependency is a repo test prerequisite, not a dependency of agent-brain. Report missing tools as incomplete verification and do not install them implicitly. Windows deterministic suites can exercise launchers and filesystem behavior without live Codex runs; native Windows live certification is limited to Copilot/Gemini.

In a disposable repository after software installation, review the setup plan and then apply its exact saved JSON:

    agent-brain setup --json > setup-plan.json
    agent-brain setup --apply --plan setup-plan.json --json
    agent-brain doctor --json
    agent-brain status --json

Only a matching certified path becomes active. Fixture certificates are restricted to isolated tests and are not distributed as real support. Keep actual installation/activation out of the author's real home/repository until requested. Before future live testing, install the authorized tested bundle into the disposable home and verify the native registrations resolve to it; source-only tests are insufficient.

## Validation and Acceptance


Mechanical acceptance uses observable subprocess results and artifacts, with expected assertions fixed independently before each run. All predefined critical checks must pass on every claimed supported path. Independent human review assesses semantic quality where deterministic assertions cannot. Agent self-reports alone never pass. Investigate every baseline success that becomes a candidate failure; no unresolved task regression caused by agent-brain may remain. Lost policy, harmful unsupported updates/prunes, silent incomplete maintenance, unrecoverable edits, and broken knowledge links block acceptance.

The offline critical registry covers CLI discovery/help/version; input/JSON/TTY/streams; invalid invocation before mutation; metadata/whole-read/order/reference completeness; conservative matching/read-only scope; policy/evidence/candidate boundaries; joined lifecycle/child obligations; lease expiry and stale-owner rejection; bounded contention/retries; pause/cancel/interruption distinctions; source changes; coherent publication/recovery and unexpected-edit protection; finite revision-bound dream coverage, quiet rotation, oversized units, UTC cadence/coalescing, and reference-aware 30-day cleanup; preserved custom hooks/setup/upgrade/deactivation. Add malformed input, missing/corrupt state, unsupported runtime, and shared writable-root rejection. These are tested-case guarantees, not proof against every possible failure.

Native critical tests separately observe actual discovery/trust, context content before governed actions/conclusions, restoration after resume/compaction, foreground semantic execution, verified outcomes, native stop continuation, actual hook timeouts, and selected child paths. Force advisory/missing events and timeout-open behavior. Fake payloads and process exits cannot establish those guarantees. Repeat semantic critical cases three times per claimed entry path. A run may count toward both frozen critical checks and the workload if it meets both; do not repeat it solely because it belongs to two sets.

Freeze ten workload variants. They are: a read-only answer distinguishing the observed 128-command-segment Tool Guardian limit from its 32768-byte structured-input limit; an installation/layout/KB-routing answer; a publishable skill help/reference change checked with quick_validate; two scoped canonical hook-family changes checked with generated freshness and relevant provider suites; source correction and source rename/removal cases with summary/manifest refresh; a guidance move retaining stable IDs and required references; correction/pruning of seeded erroneous or completely redundant guidance while retaining counterexamples; and a task that expands after clarification/resume and needs restored guidance before new dependent work. Existing KB observations remain scoped observations, without inventing replay evidence. Use harness-owned source fixtures and independent expected artifacts.

For each certified surface/execution cohort, collect at least 60 paired task observations: 40 isolated pairs from four repetitions of each variant, plus two paired sequences of at least ten tasks each. A cohort groups one surface and interactive/noninteractive mode with frozen settings. Each sequence must have enough predetermined eligible completions to finish two entire dream cycles, followed by fresh-session checks. Calculate sequence length from frozen unit closures/targets and batch limits before measurement, including extra tasks/cost. Use a fixture date clock. Vary baseline/candidate order according to the frozen plan, retain all critical failures, and never extend or discard observations because the result looks favorable.

The four selected surfaces yield seven initial cohorts: desktop interactive and interactive/noninteractive for each of three CLIs. If all certify, the minimum is 840 baseline/candidate task executions, excluding extra cycle coverage and standalone probes. Publish total task/session counts, overlap, measurement coverage, and usage availability before requesting live execution authorization. Later native Windows expansion is limited to Copilot/Gemini here. This plan sets no paid evaluation in motion.

Delivered guidance counts repository instructions, knowledge, routing, procedures, native startup loading, repeated reads, and every attributable recall/learn/dream/retry/repair/recovery delivery. Include all model executors if the design later adds any. Exclude identical user task text, task source code, unrelated tool output, and unchanged provider/system scaffolding. It measures delivered guidance, not billed model-input tokens. Validate actual native delivery observations and a frozen model tokenizer, or a documented proxy validated on the pilot's Markdown/JSON/path content. Missing visibility or unvalidated tokenization makes the performance result inconclusive, not zero or a pass.

Measure each task with a monotonic clock from task arrival through verified required maintenance. Sum additional blocking retrieval across the task, including its retries/checks. Include learning, dream, repair, and recovery in total duration. Script equivalent clarification/interruption/resume timing in both arms. Compute conventional medians and nearest-rank empirical 95th percentiles separately for every cohort; for N ordered observations, nearest rank is the value at one-based position `ceil(0.95 * N)`. Retain paired outcomes and arm distributions. These are empirical pilot percentiles, not a population confidence guarantee.

Pass only if candidate median delivered-guidance tokens are at most 75% of baseline, candidate guidance 95th percentile is no higher than baseline, added blocking retrieval 95th percentile is at most five seconds, and total task duration 95th percentile is at most 120% of baseline. Equivalent models/tasks/settings/knowledge and complete workload windows are required. A gate failure calls for improvement or an explicit unmet result, never omission of required context or maintenance.

Also report total validated provider-reported task usage/credits and stage boundaries where available, including every executor. Account-wide usage percentages are not task usage. Mark missing/incomplete usage explicitly. No precise per-stage attribution, new cost threshold, or universal foreground-cheaper claim is required. Measurement tooling stays separate from the standard-library core, declares any dependencies, adds no observer model sessions, and downloads nothing implicitly. Keep frozen inputs, assertions, actual delivery traces, changes/checks/timing, independent semantic review, and usage availability in ignored validation-pinned records, then publish a sanitized portable report. Routine production does not retain full transcripts.

## Idempotence and Recovery


Plain setup/doctor/status/help/version are read-only; doctor/status never create missing state. Informational recall can rebuild an in-memory index and print content without issuing an agent receipt. Ordinary activation is explicit plan/apply, idempotent, version-bound, and stale-plan rejecting. Each managed setup change has base/result content revisions and an inverse. Applying or undoing a plan preserves unrelated edits; conflicts remain visibly unresolved rather than clobbered. Never reset the Git worktree or commit unrelated changes as recovery.

Before upgrading, inspect valid ownership and pending publication, use SQLite's supported backup operation rather than copying an actively written database, reconcile unfinished publication, and apply only supported explicit migrations. Retain identities, obligations, evidence, candidates, and history. An unsupported migration/downgrade stops before mutation. Deactivation removes only managed registrations and revokes active handles; re-enablement validates version, access, context, and pending recovery. It never silently clears obligations or restarts canceled tasks.

Recover journaled publication by comparing actual current bytes against recorded before/after versions. Complete a valid prepared set or reverse only safely attributable writes. Unexpected content is preserved with an affected gap and recovery-needed status. Managed recall with unrelated coherent scope may continue. Missing/corrupt expected durable state is not an empty queue or completed task; preserve recoverable records, rebuild only derived indexes, and expose unavailable inputs. A prior delivery receipt never reconstitutes missing current agent context.

Registrations and mutating ownership expire after 30 minutes and renew only through eligible integration events/checked operations with valid binding; no idle heartbeat exists. A short transaction claims one mutating learn/dream owner per worktree. Every write checks owner generation and handle. Reasoning holds no database transaction. Matching requests join; a different live owner yields pending/incomplete within the bounded wait. Only eligible integration recovery can reclaim confirmed expired/released ownership, and the old owner cannot publish.

Use two seconds cumulative contention wait per deterministic operation, monotonic remaining budgets, and transient retry delays of 250 ms then 750 ms. The shared stage/event limit is three total attempts with at most one semantic repair, reduced by tighter provider caps. Duplicate events never reset it. Invalid authority, unsupported capability, or unresolved policy do not blindly retry unchanged input. After exhaustion, show the reason, affected scope, and next eligible recovery event and retain pending work. Ctrl-C exits promptly with at most two seconds of safe deterministic reconciliation; a second interrupt exits immediately. Interrupting one CLI attempt is distinct from canceling the user's objective.

Worktree-local state and writable knowledge never share a first-version writer across worktrees. Shared external mappings are read-only. Avoid following writable configuration/knowledge/state symlinks or reparse points outside the declared scope; report ambiguous ownership/paths during setup. Runtime and portable history must not expose invocation handles or secrets. This is local operational discipline, not a security claim against another process with the same user access.

## Artifacts and Notes


The closed [Just-in-time Context](map.md) map remains the decision index. Source contracts are [Success Criteria](tickets/success-criteria.md), [Knowledge Evidence Policy](tickets/knowledge-evidence-policy.md), [Context Retrieval Contract](tickets/context-retrieval-contract.md), [Lifecycle Guarantees](tickets/lifecycle-guarantees.md), [Context Organization and Skill Boundary](tickets/context-organization-and-skill-boundary.md), [Maintenance Scheduling and Pruning](tickets/maintenance-scheduling-and-pruning.md), [Failure and Concurrency Contract](tickets/failure-and-concurrency-contract.md), and [Adoption and Validation Contract](tickets/adoption-and-validation-contract.md). [Provider Lifecycle Capabilities](tickets/provider-lifecycle-capabilities.md) and [Reference Evidence](tickets/reference-evidence.md) distinguish research facts from deployed proof. This plan embeds the necessary requirements so execution does not depend on conversation memory; source tickets own accepted decision history.

Supporting [provider binding facts](research/provider-binding-contract/findings.md), [CLI design contract](research/cli-design-contract/findings.md), [SQLite settings](research/sqlite-settings/findings.md), and [pilot workload facts](research/pilot-workload/facts.md) supply recorded facts and existing validation seams. Recheck provider documentation against the frozen versions before native implementation/testing. Research dated 2026-09-30 is not a live guarantee.

The editable annotation visual is `/Users/adam/.codex/visualizations/2026/09/29/01a0ef86-3a2f-7c13-85fa-b0b5baaf077f/agent-brain-design.html`. The received state contains no annotations. It remains a discussion surface; notes do not change closed contracts without agreement. [Feature handoff](handoff.md) points to this plan for the next authorized implementation session.

Expected future machine result, with runtime-issued identity/revisions/check receipts omitted here for readability:

    {"schema_version":1,"operation_status":"ok","stage_outcome":"no_change","work_session_status":"completed"}

That result is valid only after actual scoped review/checks and settled required obligations. An empty diff, printing this object, or claiming it from an agent never proves completion. Preserve exact real transcripts only where validation needs them; summarize routine results in the living plan.

## Interfaces and Dependencies


The core requires Python 3.12+, its `sqlite3` module, and SQLite 3.15.2+. Certify exact builds in the 3.12/3.13/3.14 lines instead of assuming future compatibility. Use standard-library argparse, json, pathlib, dataclasses, uuid, hashlib, sqlite3, subprocess, time, datetime, tempfile, and platform filesystem APIs. No third-party core package, optional SQLite shell, provider SDK, model executor, embedding service, or network call is required. Provider installations and any measurement-only dependencies are separate and explicit.

### Public process and internal bridge


Expose six human commands: recall, learn, dream, setup, doctor, status. Use top-level `--version`/`-V`, `help [COMMAND]`, and `-h`/`--help` before invocation validation. Bare invocation lists commands and begins no work. Every command supports explicit JSON output and explains purpose, inputs, effects, examples, and active-agent requirements. Use descriptive named flags: `--config`, `--input`, `--invocation-file`, `--json`, `--no-color`, and setup's `--apply --plan`. Accept presentation flags before or after the subcommand where unambiguous. No catch-all abbreviations, mandatory prompts, hidden model calls, or forced color/animations in pipes are introduced.

Result JSON stays on stdout; errors/progress stay on stderr. Exit 0 means command operation success, 1 execution/check failure or required stage incompletion, 2 invalid usage/input/invocation, and 130 Ctrl-C. A status query can exit 0 while reporting pending/incomplete work. Structured errors identify code, cause, affected scope, retry eligibility, and next action. An incomplete stage is not transformed to success by a warning. TTY-aware decoration, if introduced, respects the relevant stream, `TERM=dumb`, `NO_COLOR`, and `--no-color`.

`skills/agent-brain/scripts/agent-brain.py` calls `agent_brain.cli.main(argv: Sequence[str] | None) -> int`. `skills/agent-brain/scripts/integration-bridge.py` calls `agent_brain.lifecycle.bridge_main(argv: Sequence[str] | None) -> int` and reads one versioned event object on stdin. The bridge is an internal installed interface for registered adapters, not a seventh general human command. It validates effective configuration, adapter/core/certification identity, actual workspace binding, event eligibility, and state before issuing or renewing a handle. Directly setting identity flags or provider environment variables cannot create authority.

The bridge result contains context content with identities/revisions and completeness/gap information, next-stage work/checkpoint instructions, and verified native decision requirements. An adapter may deliver those only through the event's supported output. Missing post-compaction content availability triggers restoration before dependent work; a previous receipt does not substitute for content. Foreground classification/check proposals remain semantic assertions independently evaluated in pilot quality tests.

### Configuration and records


Default portable config is `.agents/context/config.json`; default ignored runtime directory is `.agents/context/state/`, containing `brain.sqlite3`. Portable candidates/history are `.agents/context/candidates/` and `.agents/context/history/`. Schema version is 1 with explicit supported migrations. Config contains `repository_id`, `knowledge_roots`, `mapped_units`, `startup`, `providers`, `source_ingestion`, `maintenance`, `limits`, `state_dir`, `candidate_dir`, `history_dir`, and `checks`. Startup lists required unit/whole reads in order. Knowledge roots declare read/write ownership. Providers declare native registrations, pinned bundle/adapter/schema and support records; unconfigured integrations stay disabled. Limits carry the accepted lease/wait/retry/batch defaults.

A `--config` selects a configuration, but its identity/revision still binds eligible operations. Presentation/search flags can override preferences; flags/environment cannot override instruction authority, workspace identity, mutation scope, or certification. Setup plans contain base revisions, exact managed forward/inverse changes, and certification inputs. Unknown schema versions, malformed/duplicate-key JSON, duplicate unit IDs, missing required references, and stale plan/input revisions are rejected before publication. Use explicit typed validators for the bundled records and publish JSON schemas/examples with the same constraints; no general-purpose third-party schema engine is required.

Metadata uses namespaced HTML comments beginning `agent-brain` followed by one JSON object. A defaults object appears after frontmatter and contains no unit ID; a unit object appears at document level or immediately after its heading. Fields are `schema_version`, `id`, `kind` policy/fact, `status` established/candidate, `applies`, `requires`, and `evidence`; defaults can be represented under `defaults` in the same schema. Inherit defaults, then apply section overrides. Protected/external artifacts use equivalent `mapped_units` configuration with document/section selectors; externally owned content need not be rewritten. Preserve OKF path identity and frontmatter. Derived indexes are disposable and never a second authoritative guidance store.

Applicability selectors cover paths/concepts/actions/dependencies/providers/runtimes. Normalize repository-relative paths with `/`; `*` matches within one segment, `?` matches one non-separator character, and `**` matches zero or more path segments. Define/test these semantics without relying on platform shell expansion. Within a selector list use OR; combine known independent applicability constraints with AND. Concepts also route lookups. Missing/uncertain scope broadens instead of filtering away possible mandatory guidance. Required references use stable UUID plus `unit` or `whole` loading mode; explicit full reads/order override smaller delivery preferences.

Stage records include integration-issued UUIDs for repository/worktree/work-session/task/agent/attempt/obligation, stage, authorized scope, input/context/ownership generations, relevant SHA-256 revisions, evidence/change references, and runtime check receipts. Result enums distinguish `operation_status` ok/error from `stage_outcome` completed/no_change/incomplete. Work-session checkpoints are active, awaiting_user, ready_to_complete, completed, incomplete, paused, cancelled. Invocation registrations record eligibility/expiry/revocation; provider IDs are verified mappings, not canonical semantic task identity.

Portable change history retains attributable forward/inverse changes, affected stable identities, before/after hashes, rationale, and proportional evidence. Evidence notes remain beside guidance and are selectively disclosed. A no-change record identifies reviewed scope and required check receipts. The checks registry names built-in checks and explicitly trusted repository checker IDs/argument lists. Execute argument lists without shell interpolation, bound them, and run applicable checks against prepared/current revisions at prepare/publish/complete. Run long checks in foreground operations; a caller-provided `passed` flag cannot create a receipt.

### State and publication


`state.py` opens worktree-local SQLite connections with `journal_mode=DELETE`, `synchronous=EXTRA`, and `foreign_keys=ON` before transactions. On the initial macOS target request `fullfsync=ON` and verify deployed filesystem/VFS assumptions. Use short transactions and remaining bounded lock waits; `busy_timeout` alone is not a whole-operation deadline. Store durable registrations, obligations, one mutating owner's generation/lease, outcomes, delivery revisions, publication journal, and finite dream targets/credits. Never share writable KB roots between worktrees in version 1.

`publication.py` coordinates the exact prepared change set, validates base/input revisions again, persists recoverable intent and before/after bytes, and syncs destination-local temporary files before individual replacement. Sync directory metadata where required/supported and verify content/references/checks before completion. Managed reads consult publication/recovery state and give a coherent verified view or an affected gap. External multi-file atomicity and unmanaged-read atomic visibility are explicitly absent. Process-interruption tests do not prove OS/power-loss durability; stronger claims need their own evidence.

### Native candidate bindings and support manifest


Codex defaults to repository `.codex/hooks.json`; candidate events are SessionStart including resume/compact, UserPromptSubmit, PreToolUse, supported compact/subagent events, and Stop. Certify desktop and CLI separately. Unsupported tool/event output and unknown timeout behavior must be forced and observed. Do not assume a supported desktop attachment endpoint or use experimental attachment services to complete this design.

Copilot CLI defaults to managed `.github/hooks/agent-brain.json`. Use camelCase `sessionStart`, model-facing `userPromptTransformed` where needed, `preToolUse`, `preCompact`, supported subagent events, and `agentStop`. Do not rely on ignored `userPromptSubmitted` output. Built-in general-purpose children lack the recorded lifecycle hooks; certify a separately registered authorized child wrapper or leave that path unsupported. Command timeout can open the path despite denial expectations. Preserve the shared three-attempt limit below the documented eight-consecutive-stop-block cap.

Gemini defaults to managed `.gemini/settings.json` entries. Candidate events are SessionStart, BeforeAgent, BeforeTool, validated BeforeModel request inspection/overrides, AfterAgent, and advisory PreCompress. No child lifecycle hook or post-compression order is established by this plan. Restore scoped context at a validated subsequent request/action boundary and test before read-only conclusions. SessionEnd is best effort, not the recovery or completion guarantee.

These bindings reproduce accepted planning inputs, not current-version certification. Recheck actual native schemas, merge/trust/permissions, response consumption, timeout handling, and continuation limits against each frozen build. Use a four-second adapter watchdog reduced below lower native deadlines. If supported native decisions or a validated automatic guard cannot pause dependent work and enforce completion/recovery, leave that path unsupported. Both VS Code harnesses remain deferred.

Support records key exact core/adapter/schema versions, provider build, platform/filesystem, entry mode, permissions, lifecycle config, native/fallback path, and child delivery when used. Record model/settings for semantic/performance results separately. Configuration/version changes outside the record need updated certification before re-enablement. Record quality/capability proof separately from measured guidance/performance proof, so a native contract test cannot stand in for the accepted product gates.

Revision note: 2026-10-05, replace the initial skeleton with twelve executable milestones, public interfaces, conservative provider boundaries, and the accepted offline/live acceptance procedure. The completed map remains closed; execution and live spending remain separate authorization steps.

Revision note: 2026-10-06, close M5 Progress/Status/Acceptance together after three-runtime public acceptance and parent fault review; make M6 the next open milestone. Record guidance byte accounting, current revision credit, exact recovered delivery identities, and reference-aware retention without expanding offline authorization.

Revision note: 2026-10-06, close M6 Progress/Status/Acceptance together after public source/legacy, three-runtime shared, generated hook and canonical-document acceptance. Preserve the single canonical source reconciler, checked reversible semantic artifacts, early current delivery, cross-task gaps and legacy fallbacks. M7 becomes next/open without expanding live authorization.

Revision note: 2026-10-06, close M7 Progress/Status/Acceptance after exact three-runtime adapter/shared acceptance, parent public fault proof and generated/package/document checks. Keep native consumption, first-task route admission, Windows and product measurements unverified; M8 is next/open.
