# Fix Tool Guardian false positives within measured latency budgets

This retained ExecPlan is maintained under the `exec-plans` skill at `docs/tool-guardian-tuning/ExecPlan.md`. `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` describe current state. Earlier run narratives are historical evidence behind references.

Current status: repository implementation and independent repair review are complete. Human review, user-run installation, and installed/platform proof remain outstanding. The next authorized action is human review of the accepted change and its evidence. No implementation repair is currently open. Agents must not install real hooks, change user-global configuration, reopen settled design, or resume Lavish polling without a new request.

## Purpose / Big Picture


Users can write documentation, source, and tests, search for command examples, and run the observed harmless analysis scripts without Tool Guardian treating inert data as executable instructions. The implementation covers Codex, Copilot, and Gemini while retaining dangerous-operation detection, complete executable inspection, finite resource bounds, logging, and existing provider responses.

The accepted contract permits measured per-case latency increases: steady-state median/p95 budgets are +2/+5 ms, cold budgets are +5/+10 ms, and finite resource cases must remain below 500 ms. These allowances never relax security or inspection. Repository proof does not establish installed behavior; the user owns real installation.

## Progress


- [x] (2026-10-01) [milestone-1] Preserve 47 sanitized fixtures, reproduce baseline decisions through 144 public-provider checks, and retain two complete-hook baseline runs with 147 scenarios each.
- [x] (2026-10-01) [milestone-2] Integrate reviewed native-tool and search-data classification at e373690d.
- [x] (2026-10-02) [milestone-3] Complete bounded shell/Python classification and measured sanitizer/startup repair; retain rejected scans and failed candidates as historical evidence.
- [x] (2026-10-02) [milestone-4] Validate resource boundaries, regenerate providers, and meet the agreed warm/cold gates with retained initial failures and exact repeats.
- [x] (2026-10-02) [milestone-5] Synchronize canonical documentation and deliver repository source; repair two unrelated fixture failures without weakening assertions.
- [x] (2026-10-05 15:12Z) [milestone-6] Close all four independent review findings and the inherited-stdin pipeline gap after two repair/review rounds; preserve fresh frozen evidence and the final documentation pass.
- [ ] [milestone-7] Human reviews the accepted repository change and retained proof, and resolves any new findings explicitly.
- [ ] [milestone-7] User installs and reviews/trusts changed Codex definitions before live checks.
- [ ] [milestone-7] Record native Windows and live-provider proof when performed; neither is currently verified.

## Surprises & Discoveries


Execution context crosses nested shell boundaries. Inspecting an inline consumer in isolation lost inherited pipeline input and allowed downloader pipelines through intermediate commands. The repaired implementation retains producer order, shared stdout, and nested consumer context while preserving proven harmless controls.

Recognized code options and normalized text require fail-closed accounting. Unresolved recognized execution denies even in warn mode. Charge normalized UTF-8 aggregate bytes while retaining raw source provenance: 32,768 bytes allows and 32,769 denies at the execution aggregate boundary.

Complete-hook proof includes logging lifetime and startup. The first warm adapter checked logs after fixture-home cleanup; its failed run and drivers remain preserved. Corrected drivers defer external cleanup through outside-timer verification and clean in `finally`. Parser-only improvement or faster large inputs cannot offset a repeatable frequent-path violation.

The 2026-10-07 document reconciliation found obsolete planning statements and an absent original topic branch at checkout `f051d737`. The accepted runtime and generated guard files are unchanged from integration `14c03dee`; this check did not rerun performance or installed-provider validation. Earlier discoveries, revisions, failed experiments, and dispatch history remain in the [historical plan snapshot](history/2026-10-07-plan-before-reconciliation.md).

## Decision Log


- Decision: Preserve operation-based data classification regardless of file extension, without adding a general code-content analyzer or destination-protection claim. Rationale: Literal documentation, source, tests, and search patterns are data; actual executable operations remain inspected. Date/Author: 2026-10-01, user.
- Decision: Keep strict scanning and finite bounds for unrecognized input. Rationale: Unknown fields, schemas, aliases, or executable roles are not evidence of harmlessness. Date/Author: 2026-10-01, user.
- Decision: Use standard-library parsing and generated local policy helpers with ordinary Python imports. Rationale: Keep provider runtimes independent and reduce measured subprocess startup work without self-managed caches. Date/Author: 2026-10-01, implementation orchestrator.
- Decision: Use separate +2/+5 ms steady-state and +5/+10 ms no-provider-bytecode cold budgets, per provider and scenario. Rationale: The user accepted a few milliseconds while retaining full inspection, logging, and a 500 ms finite resource ceiling. Date/Author: 2026-10-02, user.
- Decision: Retain exact targeted noise repeats without relabeling initial failures or raising budgets. Rationale: Only the agreed repeat policy can distinguish an isolated scheduling event from a repeatable violation. Date/Author: 2026-10-02, user and implementation orchestrator.
- Decision: Accept strict fallback for unproved positional arguments, including possible harmless false alarms. Rationale: Additional positional-data proofs are outside the agreed repair scope; established native/search/writer/survey exemptions remain required. Date/Author: 2026-10-05, user.
- Decision: Deliver repository changes and leave real installation to the user. Rationale: The user explicitly owns installation and trust review. Date/Author: 2026-10-01, user.
- Decision: Keep current guidance self-contained and move obsolete run narratives behind historical references. Rationale: Completed code milestones must not coexist with active claims that implementation is unstarted. Date/Author: 2026-10-07, user.

## Outcomes & Retrospective


All six repository milestones are complete. Both original Standards and Spec reviewers approve frozen repair `27062fc6`. Conflict-free integration produces runtime `14c03deeac8943f271c00a274550c6dfa3d60310`, with all seven reviewed changed-file hashes unchanged. Evidence integrated at `260070f211189096dc4e77d623f004e66b450238`, with all 43 artifact hashes unchanged. The final canonical pass satisfied both-bundle OKF lint and freshness of all 29 generated files. Owned repair/performance worktrees and private branches were removed; unrelated worktrees and frozen roots were preserved.

Fresh frozen proof retains 17,100 correct warm observations, 7,350 fresh-copy cold launches plus the exact 50-launch repeat, 96 resource cases, and 1,200 measured concurrency calls. Initial warm pair 1 fails only Gemini patch p95; two exact repeat pairs pass with median/p95 deltas -5.456708/-3.852000 ms and -5.453917/-5.694874 ms. Initial cold fails only Codex writer-before median; its exact repeat passes +4.926083/+5.795166 ms. Cold median headroom is 0.073917 ms. Initial reports remain labeled FAIL. Maximum resource runtime is 40.894541 ms, with native macOS peak RSS of 22,331,392 bytes. Both concurrency pairs improve each provider's individual and batch median/p95.

The source worker passes shell 17, limits 17, native 13, corpus 144 and banners 14 on Python 3.14.6 and 3.13.14, plus provider suites, generator 25, CLI checks and freshness. Standards independently passes 402 public-hook checks; Spec passes 294 plus limits/native/corpus. Root verification decodes 28,840 retained native outputs and checks hashes, raw arithmetic, logging, exact repeat sets, copied-source maps, and failed-attempt bytes. Historical 39/41 aggregate evidence followed by two repaired suites is not a newly rerun full suite.

Milestone 7 remains open. Human review, real installation, native Windows execution, and provider-delivery/live proof have not been established. Source acceptance is met under the unchanged exact-repeat policy; those external actions remain separate. No runtime or performance tests were rerun by the 2026-10-07 documentation-only reconciliation.

## Context and Orientation


Work from the repository root. `hooks/families/tool_guard.py` is canonical build-time source. `hooks/manifest.py` owns three provider entrypoints and their local `helpers/tool_guard_policy.py` outputs. Generated entrypoints are `.codex/hooks/tool-guard.py`, `.copilot/hooks/scripts/tool-guard.py`, and `.gemini/hooks/scripts/tool-guard.py`. Future authorized source repairs must change canonical code and regenerate outputs; never hand-edit generated files or add cross-provider runtime imports.

`read_tool_scan_inputs`, `_command_segments`, `build_threats`, `build_input_threats`, individual rule matchers, and `main` perform classification and inspection. `KNOWN_TOOL_FIELDS` labels diagnostic fields; it does not authorize exemptions. `NativeToolInput` validates exact aliases and schemas. Native aggregate data is bounded at 65,536 bytes, including keys and metadata. Unsupported input retains 32,768 bytes. Structural bounds remain 32 levels, 256 nodes, and 128 strings. Recognized execution aggregates 32,768 normalized bytes, 128 commands, 256 tokens, and execution depth 16. Unsupported strict scanning retains its original per-segment token limit. Python preflight limits syntax depth to 32 and tokens to 1,024; abstract syntax tree depth/nodes are 32/2,048. These bounds prove the tested finite envelope, not arbitrary raw JSON-decoding memory.

The shared incident suite is `scripts/test-tool-guard-false-positives.py`; benchmark CLI coverage is `scripts/test-benchmark-high-rate-hooks.py`. Both already exist and are registered in `scripts/test-all.py`. `scripts/test-security-banners.py` checks public provider inputs and responses. `scripts/benchmark-high-rate-hooks.py` already supports `--guard-only`, `--script-root PATH`, and `--expected-behavior baseline|candidate`. It measures whole subprocesses with disposable repositories, log paths, and homes. Median absolute deviation describes ordinary timing variation. Provider-delivery latency is distinct from hook subprocess runtime.

Before any newly authorized implementation, load the hook and scripts instructions, known issues, and testing guidance. Use test-first development and applicable security/performance workflows. Provider-schema changes require authoritative provider references. Current output schemas and registrations remain unchanged.

## Plan of Work


### Milestone 1: Preserve incidents and baseline proof

Status: done
Acceptance: met

The corpus preserves sanitized provider-native incidents for long patches, actual/escaped newlines, UTF-8 growth, inert command examples, edits/writes, searches, fixed Python writers, and the hook-fixture survey. Important shapes include a 46,899-byte native patch, a 330-line patch, and a 124-line patch that originally produced 142 naive segments. Each harmless case has dangerous-operation controls, including substitutions, execution sinks, malformed schemas, extra fields, and normalization. Fixtures invoke only the guard, never the represented operation. Baseline copies and two full-hook runs remain evidence; private raw session payloads were not copied into version control.

### Milestone 2: Establish validated native and search-data boundaries

Status: done
Acceptance: met

Validated operation metadata, inert content, executable text, and unclassified text are distinct. Exact aliases and schemas establish data roles, with structural/aggregate bounds checked first. Unknown aliases, types, extra fields, keys, and unsupported shapes retain inspection. Patch deletion/movement metadata remains checked under existing operation rules; no new general destination protection is claimed. Saved script contents are not scanned merely because a script is invoked. Executable and unclassified strings are inspected without redundant serialized-object rescanning.

### Milestone 3: Classify observed shell/Python forms and reduce measured cost

Status: done
Acceptance: met

Bounded tokenization preserves quotes, escapes, separators, substitutions, redirections, and heredoc roles. A quoted heredoc suppresses shell expansion, but its receiving interpreter can still execute the body. Proven fixed Python writers and the fixed JSON-input hook survey receive constrained data proofs; arbitrary interpreters, dynamic execution/imports/targets, unresolved aliases, and unsupported syntax do not. Reused bounded representations replace repeated scans only where correctness and full-hook timing establish the benefit. Lazy imports and local helper extraction have measured proof; rejected literal scans remain historical failures.

### Milestone 4: Validate limits, security, and all-provider performance

Status: done
Acceptance: met

Native data lines do not consume executable-command budgets. Boundary tests preserve accepted maxima and the first rejected input, including normalized UTF-8 growth. Malformed, over-limit, and incomplete inspection fails closed before allowlisting and in warn mode. Known dangerous operations retain block/warn semantics, rule identities, diagnostics, redaction, and logging. Normal passes remain silent. Generated providers, generator tests, incident/security/provider suites, benchmark CLI coverage, frozen warm/cold comparisons, and finite resource/concurrency checks provide source acceptance. Native Windows and installed delivery are explicitly unverified.

### Milestone 5: Synchronize documentation and deliver source

Status: done
Acceptance: met

The completed formal pass updated canonical guidance, maps, implemented limits and APIs, test routes, and source-proof limitations. Two unrelated macOS/sandbox fixture failures were repaired without weakening assertions. Delivery kept real home-directory hooks and user-global configuration untouched. The user owns installation and Codex trust review.

### Milestone 6: Close independent review findings

Status: done
Acceptance: met

R1 preserves installer-pipeline detection through intermediates, inherited stdin, producer order, and shared sequential stdout. R2 keeps unproved positional arguments strict after shell-body proof. R3 recognizes attached Python code options and denies unresolved recognized code even in warn mode. R4 charges normalized aggregate bytes while preserving raw provenance. Unsupported Python builtin-alias inference remains outside scope. Two rounds with the original reviewers close every finding and the related nested pipeline gap; fresh frozen gates pass under unchanged budgets and exact repeats. Per-participant logs and dispatch audit preserve failed attempts and unconfirmed execution settings.

### Milestone 7: Complete owner review and external proof

Status: open
Acceptance: not met

The next action is human review of the accepted change and retained verification evidence. After review, the user runs the installer and reviews/trusts changed Codex definitions before live checks. Record actual installation, provider delivery, and native Windows evidence when available; source proof and simulated platforms do not supply it. A new finding must be recorded as new work with explicit current progress and acceptance, rather than silently reviving an expired checkpoint.

## Concrete Steps


Current review starts with `evidence/review-repair-root-verification.json`, `evidence/review-repair-final-verification.json`, the retained comparison/repeat reports, and `repair-logs/`. These paths are relative to `docs/tool-guardian-tuning/`. The reviewed source commits and fixed point are recorded below; the original topic branch is absent from this checkout, so it is not a required review prerequisite.

For a newly requested repository verification, existing read-only commands include:

    rtk proxy python3 scripts/generate-hooks.py --check
    rtk proxy python3 scripts/test-tool-guard-false-positives.py
    rtk proxy python3 scripts/test-security-banners.py
    rtk proxy python3 scripts/test-tool-guard-shell-data.py
    rtk proxy python3 scripts/test-tool-guard-limits.py
    rtk proxy python3 scripts/test-benchmark-high-rate-hooks.py
    rtk proxy bash scripts/test-codex-hooks-tool-guard.sh
    rtk proxy bash scripts/test-hooks-tool-guard.sh
    rtk proxy bash scripts/test-gemini-hooks-tool-guard.sh

Correctness commands must exit zero with no failed assertions. Future canonical edits require `scripts/generate-hooks.py --write`, freshness, generator tests, and focused source acceptance before new performance claims. Benchmark outputs must use new disposable paths and retain per-case decisions, sample data, input sizes, and environment metadata. Merely running a benchmark with exit zero does not establish its latency gate.

Only after human review, the user runs `rtk proxy ./scripts/install.sh` from the repository root, or the supported PowerShell installer on Windows. They inspect/trust changed non-managed Codex definitions through `/hooks` before live validation. Agents do not execute this owner action or bypass trust.

## Validation and Acceptance


Preserved harmless incident shapes must allow silently through all three public entrypoints. Dangerous counterparts must receive the expected decision without executing represented operations. Data classifications must survive multiline JSON, aliases, escaped literals, literal searches, fixed writers, and fixture surveys. Unsupported executable roles receive strict inspection; apparent data cannot hide execution. Native edit/delete/move semantics do not establish general destination protection.

Malformed, over-limit, and uninspectable input fails closed with accurate redacted diagnostics. Allowlisting and warn mode cannot bypass incomplete inspection. Banner bounds, credential redaction, and banner/log agreement remain covered. Preserve every current dangerous-operation rule and public response contract.

For each provider and scenario independently, steady-state median/p95 may exceed the matched baseline by at most 2/5 ms; fresh no-provider-bytecode cold median/p95 by at most 5/10 ms. Finite resource cases remain below 500 ms. Match input, interpreter, logging, and frozen source. Retain two alternating normal-cache pairs with 25 samples and three discarded warmups per case. Cold proof needs at least 25 fresh-copy launches per case/condition with zero provider bytecode; OS and standard-library caches remain uncleared. Preserve first-process observations, median absolute deviation, repeat variation, and concurrency without pooling away slow paths.

An isolated violation may use the agreed exact-case repeat to test scheduling noise. Unexplained or repeatable violations do not pass. Preserve initial FAIL reports separately; never raise budgets or relabel old zero-regression failures as accepted. Functionality, complete inspection, logging, and full subprocess work remain required. Finite-envelope memory proof is not a universal raw-decoding claim; subprocess timing is not installed provider delivery.

## Idempotence and Recovery


Preserve `/private/tmp/tool-guardian-baseline`, `/private/tmp/tool-guardian-profile-candidate`, `/private/tmp/tool-guardian-profile-checkpoint`, `/private/tmp/tool-guardian-review-candidate`, and `/private/tmp/tool-guardian-review-candidate-2`. Candidate 2 is the accepted runtime freeze; candidate 1 remains unchanged failed-adapter evidence. Retained drivers record original isolated worktree paths; replay requires recreating that disposable checkout and preserving existing report files. Inline optimization replay uses original `84eae394`, not the extracted-helper layout. Missing retained roots must be reported and reconstructed from recorded source before claiming a replay; their paths alone are not proof that they still exist.

Keep operations represented by fixtures inert. Use disposable destinations, homes, log paths, and fixture-local Git configuration. Never change global signing, hook modes, allowlists, trust, real installed files, or the shell's home variable. Use writable disposable `OBSERVABILITY_LOG_PATH` for Copilot/Gemini shell suites. `RTK_DB_PATH` may point to a writable task-local database. Native `/usr/bin/time -l` needs approved collection in this sandbox; preserve its `sysctl kern.clockrate` failure as historical evidence.

Serialize mutable generator/install fixtures and run timing probes alone against frozen source. If a newly authorized correctness or timing gate fails, retain failed evidence and fix or revert only owned candidate changes. Never delete, disable, or weaken protection tests. Regenerate provider output from canonical source; do not repair generated files manually. Remove only exact owned temporary paths after recording results. Logging adapters must defer external cleanup through outside-timer verification and clean in `finally`.

## Artifacts and Notes


Current proof is `evidence/review-repair-root-verification.json` and `evidence/review-repair-final-verification.json`. `evidence/review-repair-comparison.json` keeps initial FAIL and passing repeats separate. `evidence/review-repair-attempt-1/` preserves the failed logging-adapter run, original drivers, and freeze. Do not overwrite or relabel failures.

`repair-logs/repair-worker.md`, `standards-review.md`, `spec-review.md`, and `performance.md` preserve participant evidence. `repair-logs/orchestration.md` records integration; `dispatch-audit.json` records selected/submitted settings, runtime enforcement, and unconfirmed executed settings; `documentation.md` records the final canonical pass. Earlier implementation audit is `evidence/implementation-dispatch-audit.json`. Investigation transcripts, expired milestones, superseded budget statements, and revision history are in the [historical snapshot](history/2026-10-07-plan-before-reconciliation.md), loaded only for a specific historical question.

The independent review fixed point is `9bcc6ff56cf916f848e4b32314ded35757d240c2`; implementation before repair was `4bade608`. Accepted reviewed repair is `27062fc6`, integrated runtime is `14c03dee`, and fresh evidence integration is `260070f2`. These identities identify historical source and proof; none substitutes for current installed-state verification.

## Interfaces and Dependencies


Keep standard-library runtime dependencies, local generated policy helpers, and existing provider adapters. The bounded classifier separates validated operation metadata, data with byte accounting, executable fragments, and unclassified fragments with strict fallback. User-supplied claims of safe modes do not establish those roles. The matcher emits the existing threat dictionaries for banners/audit logs and preserves fail-closed `ScanLimitExceeded` and inspection failures.

The shared incident suite and benchmark CLI suite already exist and are registered. The benchmark runner's existing script-root and baseline/candidate expectation flags preserve default invocation behavior. Any future authorized interface change must update current API/testing knowledge and this contract before completion.

Current revision (2026-10-07): reconciled every active section with completed repository milestones and pending owner proof. Preserved earlier content as explicitly historical evidence; removed obsolete creation instructions and the absent-topic-branch prerequisite. Runtime code, acceptance budgets, original proof, and user-owned installation limits are unchanged.
