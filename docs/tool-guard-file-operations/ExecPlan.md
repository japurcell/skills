# Make Tool Guardian file operations reliable and its policy easier to understand

This is the living ExecPlan at `docs/tool-guard-file-operations/ExecPlan.md`. Follow `.agents/skills/exec-plans/SKILL.md` and the applicable repository instructions. Keep Progress, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective synchronized with actual evidence.

## Purpose / Big Picture

Tool Guardian should allow ordinary file edits, patches, searches, and proven literal file writers without treating their contents as executable commands. It must continue denying dangerous executable actions and incomplete inspection. The user disabled the installed hook after repeated false blocks. Success means the recorded legitimate writers pass through generated public hook entrypoints, paired dangerous variants still deny, large native edits have an explicit usable capacity, and complete-hook latency remains within the existing acceptance gates.

Also simplify policy representation, result flow, reporting, and generation where this reduces the concepts needed to understand the hook. Preserve security behavior and benchmark complete subprocesses before replacing existing optimizations, including character-code rules, cached command representations, lazy imports, suffix summaries, and reporting fast paths. A simpler-looking alternative is not automatically an improvement.

### Authorization boundary

The user authorized creating and revising this plan and obtaining an Astra adversarial review, and explicitly said not to start implementation yet. The revisions and second review are complete. No baseline capture, prototype, test-code change, hook generation, installation, hook re-enablement, or implementation milestone is authorized by this document. The next action belongs to the user: authorize execution. After authorization, the implementation owner starts T1. Installation into real home-directory targets and re-enabling the disabled hook remain separate owner actions unless subsequently authorized. All source validation uses disposable homes.

## Progress

- [x] (2026-10-20) [milestone-0] P0: Inspect current source, instruction routes, test and benchmark interfaces, and prior incident evidence; write this plan without implementation changes.
- [x] (2026-10-20) [milestone-0] P0: Address the first Astra review's four gaps in transport sizing, versioned resource expectations, audit-failure evidence, and pre-proof writer admission.
- [x] (2026-10-20) [milestone-0] P0: Complete second Astra review; all four original findings resolved, no new actionable P1/P2 findings; record outcome without implementation.
- [ ] [milestone-1] T1: Reproduce the real file-writing failures through public entrypoints and freeze the current baseline and sanitized fixtures.
- [ ] [milestone-1] T2: Verify baseline selection, versioned shared fixtures, per-case decision/audit expectations, and pre-change throughput/resource evidence.
- [ ] [milestone-1] Record combined reproducer and baseline evidence; accept milestone 1.
- [ ] [milestone-2] T3: Resolve content budgets, escaped transport sizing, bounded pre-proof admission, and writer recognition through experiments including writers above 32 KiB.
- [ ] [milestone-2] Record exact chosen limits, interfaces, and promotion evidence before accepting milestone 2.
- [ ] [milestone-3] T4: Deliver native capacity, bounded admission to writer inspection, and truthful independent budget diagnostics.
- [ ] [milestone-3] T5: Deliver quoted shell heredoc proofs and executable/content accounting, including writers above 32 KiB.
- [ ] [milestone-3] T6: Deliver Python writer proofs, syntax/content accounting, and validated wrappers, including writers above 32 KiB.
- [ ] [milestone-3] Verify the integrated native, shell, Python, strict-fallback, and adversarial matrix; accept milestone 3.
- [ ] [milestone-4] T7: Simplify result/decision flow and reporting without losing safe actionable diagnostics.
- [ ] [milestone-4] T8: Evaluate rule representation, parser representation, runtime-source extraction, and survey-exemption simplifications separately; adopt only justified candidates.
- [ ] [milestone-4] Record per-candidate security and throughput evidence and reasons for retained optimizations; accept milestone 4.
- [ ] [milestone-5] T9: Complete integrated source, packaging, security, resource, throughput, and documentation validation.
- [ ] [milestone-5] Record remaining platform or owner actions and reconcile outcomes; accept milestone 5 only with its required evidence.

## Surprises & Discoveries

The current failure is not solely a patch-size problem. A Codex Markdown writer using `cat > ... <<'EOF'` was denied at 721 tokens against 256 despite being only 6,578 command bytes. A Python heredoc using `Path.write_text` was denied at 860 tokens against 256 with 7,101 characters. Prior investigation correlated original calls and outputs, then replayed only the hook subprocess with block mode, no skip, no allowlist, and temporary audit logs. Both still denied through `shell_v1` / `native`. Local supporting logs are `/Users/adam/.codex/archived_sessions/rollout-2026-10-15T06-31-26-01a13fc2-b0b7-70a3-81b0-ab88776d3bab.jsonl` at lines 94/96 and `/Users/adam/.codex/sessions/2026/10/08/rollout-2026-10-08T17-39-18-01a11e19-9f37-73b3-98b8-15a267e5852b.jsonl` at lines 286/288. T1 must produce portable sanitized reproductions; these machine-specific files are supplemental evidence, not execution prerequisites.

Five historical patch audit entries measured 77,089, 99,186, 80,666, 90,127, and 127,331 bytes against a former 65,536-byte ceiling. Current policy has a 262,144-byte native patch budget, so those historical entries do not prove today's patches still fail. Their exact original payloads were not replayed. `scripts/fixtures/tool_guard_vectors.py` already contains recent native patch sizes; reuse existing coverage before adding duplicates.

Copilot documentation edits containing the text `git clean -fd` were historically blocked. Current isolated replays allow both an edit and a patch with native `edit_v1` and `patch_v1` profiles. Do not restore broad command scanning of file contents, including source-code contents.

At planning time, the canonical policy remains embedded in `hooks/families/tool_guard.py`. It separates recognized native data from executable input, but shell/Python parsing, strict matching, and budgeting still overlap. `read_tool_scan_inputs()` mutates profile globals consumed later by reporting. `PATTERNS` and `RULE_DETAILS` are positionally paired, and the suggestions stored in `PATTERNS` are ignored by `_strict_threats()`.

`hooks/families/common.py` already bounds raw stdin collection at 2 MiB, with depth and completion deadlines. Guardian's own limits occur after decoding. Raw JSON transport bytes, decoded UTF-8 content bytes, normalized executable bytes, parser work, and retained reporting bytes are distinct budgets. Do not describe any one as a universal process-memory bound.

The maintained release verifier is pinned to historical revision `bc52d7d69aaa046ea97e323879402241a01fead7`, including baseline-specific expectations. The optimization-ablation script's original inline variants require revision `84eae394`; it cannot be applied unchanged to today's extracted policy helper. Baseline and harness adaptation must precede new optimization claims.

The first Astra review verified four planning gaps against current source: raw transport must be derived from worst encoded content rather than compared with decoded size; `scripts/benchmark-tool-guard-resources.py` hardcodes old-capacity denial expectations; `scripts/verify-hook-release.py` requires completed block-mode audit records except for its legacy malformed-input case; and native shell traversal plus `_InspectionBudget.source()` reject complete sources above 32 KiB before a writer proof can run. The tasks and acceptance below explicitly cover each gap. These are plan corrections, not implementation results.

## Decision Log

- Decision D1: Planning only until the user authorizes execution. Rationale: the latest explicit instruction overrides earlier general agreement to the changes. Date/Author: 2026-10-20, user and Codex.
- Decision D2: Preserve security boundaries and benchmark before replacing optimizations. Rationale: character codes or unusual representations may have a measured performance purpose; appearance alone does not justify removal. Date/Author: 2026-10-20, user and Codex.
- Decision D3: Separate inert content from executable structure; never allow arbitrary oversized or uninspectable executable input. Rationale: the confirmed writers fail because literal document text consumes execution budgets. Date/Author: 2026-10-20, Codex, reflecting approved scope.
- Decision D4: Retain exact native provider schemas, unknown-input strict fallback, existing patch delete/move-source protection, and incomplete-inspection denial in block and warn modes. Rationale: improving data handling must not create bypasses. Date/Author: 2026-10-20, Codex.
- Decision D5: Start feasibility with a 1 MiB aggregate decoded native-content target, compare 256 KiB and 4 MiB alternatives, and choose the largest justified default after resource evidence. No production limit changes before T3 records the exact choice and corresponding raw-envelope ceiling. Rationale: the historical maximum was about 127 KB, which does not justify an arbitrary unlimited or very large ceiling. Date/Author: 2026-10-20, Codex.
- Decision D6: Preserve current generated provider paths and explicit local delivery. Prefer a single ordinary canonical policy module before considering more runtime modules. Rationale: reduce source-string machinery without replacing it with a framework or unnecessary packaging changes. Date/Author: 2026-10-20, Codex.
- Decision D7: Separate behavior repairs from behavior-preserving refactors. Evaluate each optional simplification independently, keep the working alternative until evidence exists, and record rejected candidates as completed evaluations rather than forcing a rewrite. Date/Author: 2026-10-20, Codex.
- Decision D8: Derive raw-envelope capacity from worst encoded content plus bounded executable and metadata overhead at every proposed decoded capacity. Version shared benchmark fixtures and declare mode, decision, and audit outcome per case and condition. Large writers require finite admission before proof, followed by separate executable/content accounting; admission alone never authorizes execution. Rationale: addresses all four source-verified Astra findings without relaxing security or benchmark gates. Date/Author: 2026-10-20, Codex.

## Outcomes & Retrospective

The plan revision and second Astra review are complete. Astra verified that all four first-review gaps are resolved in the active contract and reported no new actionable P1/P2 findings. This is acceptance of the planning revisions, not proof of implementation security, feasibility, capacity, or throughput. Source inspection and prior session evidence establish two persistent ordinary writer failures and several already-repaired historical false positives. No implementation, new benchmarks, generation, installation, or re-enablement has occurred in this planning task. All implementation milestone acceptance remains unmet. The next action is user authorization before T1. The coordinated documentation pass found no new knowledge-base or skill changes warranted; existing guidance already owns the relevant invariants.

## Context and Orientation

Commands run from repository root, currently `/Users/adam/.codex/worktrees/05ea/skills`, using `rtk` by default. Planning started with a clean worktree at `260c578ace3514c4f2f741f51d970fc2e938786d`. This is the initial implementation baseline revision, not a claim that future worktrees are unchanged. Record runtime fingerprints and working-tree differences before use. RTK must be present; report a missing prerequisite rather than silently bypassing it.

`hooks/families/tool_guard.py` renders provider entrypoints and the identical provider-local `helpers/tool_guard_policy.py`. `_native_tool_shape()` and `_native_shell_shape()` recognize provider arguments; `read_tool_scan_inputs()` traverses and routes them. `_parse_native_patch()` separates patch bodies and operations. `_shell_representation()`, `_shell_threats()`, `_inline_operand()`, `_python_inspection()`, and `_python_threats()` inspect executable structure. `_strict_threats()` invokes the rule catalog. `main()`, `record_guard()`, `guard_report()`, and reason helpers own enforcement and reporting.

`hooks/families/common.py` owns the shared incremental JSON reader and provider JSON output. `hooks/families/allowlist.py` embeds `hooks/runtime/scan_allowlist.py`; `hooks/families/reporting.py` embeds primitives from `hooks/runtime/scan_reporting.py`. `hooks/families/audit.py` supplies shared logging. Do not change unrelated scanner behavior when reusing these helpers.

`hooks/manifest.py` registers generated assets. `scripts/generate-hooks.py --write` refreshes manifest-owned outputs; never hand-edit them. Current entrypoints are `.codex/hooks/tool-guard.py`, `.copilot/hooks/scripts/tool-guard.py`, and `.gemini/hooks/scripts/tool-guard.py`. Each uses its own local helper and provider response envelope. No runtime may import another provider's directory.

`scripts/tool_guard_corpus.py`, `scripts/fixtures/tool_guard_vectors.py`, and `scripts/tool_guard_test_support.py` supply fixtures, envelopes, decisions, and disposable launches. `scripts/test-tool-guard-{false-positives,native-data,shell-data,limits}.py` cover the policy. Three provider shell suites and `scripts/test-security-banners.py` cover public responses and logs. `scripts/benchmark-high-rate-hooks.py`, `scripts/verify-hook-release.py`, `scripts/benchmark-tool-guard-resources.py`, and `scripts/hook_benchmark_support.py` own performance evidence.

A native profile means a tool's exact argument shape was recognized. Strict fallback means unproved input remains subject to conservative inspection. An execution sink is an operation such as `eval`, `exec`, `os.system`, or a subprocess call that executes supplied text. A data proof establishes that one body is inert in its actual execution context; it does not exempt the rest of a command or promise that a saved script is safe to execute later.

Before future source work, load `tdd`, hook/security/provider instructions, and matching script/test routes. Begin bug fixes with the public stdin/stdout reproducer. Future code review or delegation must load its applicable skills. This plan does not require subagents; tasks sharing `hooks/families/tool_guard.py`, corpus expectations, generation, or installer fixtures must be serialized.

## Plan of Work

### Milestone 0: Deliver the planning contract

Status: done
Acceptance: met

Task P0 has no prerequisites. Its outcome is this self-contained plan with current source evidence, explicit authorization boundaries, independent tasks, security invariants, benchmark gates, and recovery instructions. Both review passes and the four revisions are complete. Proof is the saved document, documentation-only working-tree change, structural/reference checks, and Astra's second-review confirmation that the four original findings are resolved with no new actionable P1/P2 findings. It does not establish implementation acceptance.

### Milestone 1: Establish reproducible failures and a trustworthy baseline

Status: open
Acceptance: not met

#### Task T1: Reproduce and freeze the current behavior

Prerequisites: explicit user authorization to execute. Inputs: D1-D4, the incident facts above, current corpus, generated entrypoints, and baseline revision. Add sanitized equivalents of the 721-token quoted Markdown heredoc and 860-token `rtk proxy python3` writer only where existing fixtures do not capture them. Preserve relevant syntax, wrapper shape, punctuation, and approximate sizes, not private document text. Confirm old behavior through the complete hook, with no tool command execution and no live audit writes. Preserve meaningful baseline expectations separately from desired candidate expectations; do not relabel failures as passes.

Own `scripts/tool_guard_corpus.py`, `scripts/fixtures/tool_guard_vectors.py`, and focused assertions in `scripts/test-tool-guard-shell-data.py`. Freeze the untouched runtime and record revision, file hashes, Python executable/version, OS, and RTK version in disposable evidence. Stop after portable reproductions and the immutable baseline exist. Run the focused corpus and shell suites; the new candidate assertions must first demonstrate the expected false block. Existing unrelated failures remain failures and must be investigated.

#### Task T2: Make the performance comparison valid for this baseline

Prerequisites: T1. Own `scripts/verify-hook-release.py`, `scripts/benchmark-tool-guard-resources.py`, `scripts/test-verify-hook-release.py`, `scripts/test-benchmark-high-rate-hooks.py`, `scripts/hook_benchmark_support.py`, and shared benchmark fixtures. Preserve the historical verifier default, historical payloads/expectations, and pinned-source checks. Add explicit `--baseline-ref REV`, `--fixture-set ID`, and reviewed `--expectations PATH` options to the release verifier. Add `--fixture-set ID`, `--expectations PATH`, and `--condition baseline|candidate` to the standalone resource runner. Both runners must consume one canonical versioned resource-fixture generator at proposed `scripts/fixtures/tool_guard_resource_cases.py`; do not duplicate or independently update capacity assumptions.

Freeze existing timing and resource cases as `historical-v1`, preserving payload hashes, stable case names, and old expectations for historical invocations. Introduce `file-operations-v1` containing the unchanged old-boundary payloads plus separately named new-capacity and writer cases. Historical old-overflow cases stay present but may intentionally allow under candidate expectations. Add new maximum and maximum-plus-one cases under distinct capacity-specific names after T3 chooses limits. Never change the bytes behind an established case name; create a new fixture version when an established payload changes. Timing cases added to the corpus must not leak into historical default selection. Test historical default enumeration, payload hashes, and expectations explicitly.

The expectations document names its schema version and fixture-set ID, and maps each exact case and condition to mode, decision, audit outcome (`written`, `failed`, or `not_attempted`), and expected audit event/record count where applicable. It also declares required security/audit/enforcement attribution for cases that emit it. Normal cases require one completed record per invocation in the declared mode, matching decision and event. For audit-unavailable cases, require an intentionally established failure condition, explicit `audit_outcome=failed` response attribution, and the existing enforcement outcome; a missing record alone cannot establish the intended failure. Transport/bootstrap cases may require `not_attempted`, with a specific denial cause rather than an arbitrary no-log exception. Include block and warn cases without assuming every audit record is block mode. Do not relax successful logging globally. Failure injection and proof setup/cleanup stay outside measured hook elapsed time and confined to disposable homes.

Require complete, unique, valid entries for every selected case/condition; reject unknown or missing cases, mode mismatches, contradictory audit contracts, and changed fixture hashes. Do not infer expected outcomes from the implementation being measured. Verify the supplied baseline archive against the selected Git revision. Remove historical case overrides only in the new explicit-baseline path. Version new failure-mode expectations separately where the older baseline lacks attribution; do not require invented historical fields or treat their absence as candidate success. Candidate failures must satisfy the new declared contract.

Save portable reviewed expectations in `scripts/fixtures/tool_guard_file_operations_expectations.json`. Extend harness fingerprints to include fixture definitions, expectation inputs, and canonical runtime sources. Baseline allowance differences must be limited to named legitimate-data repairs. This is measurement support, not permission to weaken a security assertion. Keep payloads, mode, failure injection where applicable, and logging conditions matched between conditions. When T3 adds capacity cases, observe the untouched frozen baseline in a separate validation step, independently review expected outcomes, then freeze those expectations before measurement. A baseline too old to accept a large payload can correctly deny it; this must not rewrite the candidate requirement or disguise the old size-denial latency as equivalent inspection work.

After harness tests pass, run an A/A comparison of the frozen baseline using baseline observations for both conditions, then capture full pre-change timing and resources. Verify that both runners agree on inputs and condition-specific decisions/audit outcomes for the same fixture set. Harness negative tests must reject an unexpected allow, unexpected audit absence, wrong mode, and missing or stale expectations. Record each optional optimization's current implementation, attributable rationale from history where available, and existing measurements; absent evidence means unknown, not unnecessary. Stop after trustworthy A/A evidence, pre-change results, shared-fixture parity, and an optimization inventory are recorded. Do not replace optimizations in this task.

Milestone acceptance requires T1 and T2 together: the ordinary failures reproduce through public entrypoints, dangerous controls remain denied, and baseline fingerprints, observations, logging, and measurement mechanics are verified. No latency acceptance follows merely from benchmark exit 0.

### Milestone 2: Resolve budget and writer-recognition feasibility

Status: open
Acceptance: not met

#### Task T3: Prove the boundary before changing production limits

Prerequisites: milestone 1 accepted. Inputs: D3-D5 and D8, baseline evidence, raw-reader implementation, and actual parser behavior. Keep experiments in disposable copies and evidence under `.agents/scratchpad/tool-guard-file-operations/`; do not switch the production policy yet. Compare 256 KiB, 1 MiB, and 4 MiB aggregate decoded content across native writes/edits/patches, quoted `cat` heredocs, and Python literals. Exercise ASCII, multibyte UTF-8, NFKC expansion in metadata, escaped JSON, and maximum-plus-one rejection. Include complete public-entrypoint shell and wrapped Python writers whose bodies each exceed 32 KiB; passing the smaller original incidents alone is insufficient.

Specify a bounded admission/accounting interface spanning `read_tool_scan_inputs()`, `_InspectionBudget.source()`, `_bounded_normalized_text()`, shell parsing/proof, and Python preflight/AST inspection. Exact native-shell schemas may admit a finite larger source for inspection under explicit aggregate source-byte and parser-work limits. This is provisional inspection admission, never a data exemption. Routing must not reject every source above 32 KiB before a writer proof can run, and `_InspectionBudget.source()` must not normalize/charge the entire prospective literal body as executable text first. A complete proof assigns original literal body spans to the content budget; executable words, expansions, sinks, remaining arguments, and normalized executable context retain existing executable budgets. Unproved/unsupported text still uses strict executable limits or denies incomplete inspection; it must not inherit the larger content exemption merely because inspection admitted it.

Bound work before proof, including scanning large raw literal spans, quote/heredoc delimiter handling, Python parsing/preflight, nesting, and cumulative inspection through nested interpreters. Distinguish bounded syntax work from executable-token counts so a finite admitted literal is parseable without silently increasing executable authority. Track provenance and aggregate work across wrappers and nested sources; classification cannot omit a field, lose execution context, or evade budgets by splitting content. T3 must document exact interfaces, accounting ownership, and failure rules before implementation. This admission/accounting work belongs to T4 at routing and shared-budget boundaries, T5 at shell literal proofs, and T6 at Python literal/sink boundaries.

Prove quoted heredoc recognition only for a narrowly validated writer: literal supported `cat`, literal output destination, known redirect arrangement, quoted delimiter, and no uninspected arguments or side effects. `<<-` tab handling must preserve actual shell semantics. Unquoted heredocs must retain expansion inspection. Python writer recognition must inspect execution sinks independently, retain strict checks for unknown statements, and leave executable parser complexity finite. Recognize `rtk proxy` only through validated literal wrapper arguments and a supported child invocation; never treat arbitrary wrappers as inert.

Record separate limits for raw-envelope bytes, decoded aggregate content, normalized executable bytes, syntax work, nesting, metadata/operations, and reports. Keep executable limits unchanged unless a separately demonstrated counting defect requires correction. Native file/search bodies are data regardless of extension. Do not add a new small operation-count ceiling without observing its effect on real multi-file edits; existing byte/work bounds may suffice.

Choose the largest tested default that meets the finite-case 500 ms ceiling without unexplained superlinear CPU/RSS growth or baseline latency violations on unchanged cases. The 1 MiB value is the initial target, not a pre-approved performance result. If it fails, retain and explain the evidence, choose a passing smaller value that still handles the recorded workloads, or record the unresolved blocker rather than silently weakening acceptance. Any configurable override must have an explicit finite hard maximum tested at its boundary; if a safe larger override cannot be justified, ship a documented finite default first instead of an unbounded environment variable.

Always derive the required raw-envelope ceiling from all admitted decoded content, executable source, and bounded metadata plus JSON/envelope overhead. Raw JSON string escapes can require six raw bytes per decoded UTF-8 byte. Compare that derived raw requirement, not the decoded-content target, with the existing 2 MiB transport ceiling. A 1 MiB ASCII body encoded entirely as `\uXXXX` requires 6 MiB before overhead and therefore requires a transport change even though 1 MiB is below 2 MiB. Define the maximum count and encoded key/separator/metadata overhead rather than leaving overhead unbounded.

If the derived raw requirement exceeds 2 MiB, add a keyword-only bounded `max_bytes` parameter through `read_json_input()`, `_read_json_input_text()`, and trailing-byte collection in `hooks/families/common.py`. Preserve the current default for other hooks. Guardian supplies the derived finite ceiling for its admitted source/content and metadata. Keep completion deadlines, depth checks, UTF-8 validation, buffered trailing-data rejection, and Windows pipe handling. Test compact encoding, fully escaped ASCII at the chosen decoded maximum, raw-envelope maximum-plus-one, and aggregate metadata overhead. Reader allowance must not become executable allowance. Larger raw-envelope parsing and any configured hard maximum must also satisfy resource tests.

Stop after the plan's Decision Log contains exact proposed defaults/hard maxima, raw-ceiling derivation, diagnostic rule IDs/units, admission/proof/accounting API signatures, and feasibility evidence. Promote only tested choices to T4-T6. Discard or rework candidates that lose execution context, cannot inspect complete input, or exceed resource gates. T3 acceptance requires the chosen native, shell, Python, and transport boundaries to work together in the isolated prototype, including quoted shell and wrapped Python writers above 32 KiB and paired unproved/dangerous sources. Add reviewed capacity-specific shared fixtures/expectations through T2's versioned interface before resource measurements; never modify historical fixture bytes or leave standalone runner outcomes stale.

### Milestone 3: Make normal file operations pass while dangerous variants deny

Status: open
Acceptance: not met

#### Task T4: Implement native-content capacity and independent budgets

Prerequisites: milestone 2 accepted. Own `read_tool_scan_inputs()`, `_InspectionBudget.source()` and shared budget interfaces, native schema/patch handling and budget constants in `hooks/families/tool_guard.py`; any approved reader parameterization in `hooks/families/common.py`; native/limit fixtures; and shared-reader tests in `scripts/test_helpers.py`. Implement T3's finite inspection-admission boundary so recognized shell sources above 32 KiB can reach bounded writer inspection without being prematurely treated as wholly executable. Until T5/T6 supply a complete matching proof, those admitted sources remain unproved and must not allow through a content exemption. Verify this safe intermediate state explicitly.

Count proven native inert contents against the chosen content budget, keeping metadata and normalized operation checks independently bounded. Parse patches incrementally rather than materializing an extra complete list of lines if measurements support the change. Parse structural validity and preserve protected deletion/move-source checks; do not interpret added lines as shell or Python. Routing, shared budgets, transport, and resource fixtures must use the same T3 decisions. Extend only the new versioned fixture set with distinct capacity cases and reviewed condition-specific outcomes.

Verify allowed maxima, first rejected values, aggregate rather than per-field accounting, true byte/character units, invalid override behavior if applicable, malformed patches, invalid/extra schema fields, unknown aliases, normalization growth, and exact allowlist precedence. Incomplete inspection denies in warn mode and despite a matching valid allowlist. Stop after public native/reader tests pass and outputs are regenerated and checked. Do not modify writer proofs here.

#### Task T5: Correct quoted shell-writer content accounting

Prerequisites: T4. Own `_shell_representation()`, `_shell_threats()`, the shell side of the shared admission/accounting interface, and shell-writer tests. Complete T3's proof for admitted sources without charging a proven literal body as executable bytes, tokens, or commands. Retain cumulative normalized executable budgets on every unproved part. Bound parsing and content storage independently; do not bypass a source-byte gate without replacing it with the finite admission and proof accounting from T3/T4. Continue inspecting destination/redirect context under existing policy, substitutions outside the body, chained commands, and executable producer/consumer context. Retain strict handling for unsupported shapes. This must not become a general guarantee that writing to any destination is safe.

Verify the sanitized 721-token incident now allows, along with a quoted heredoc above 32 KiB, a body near chosen capacity, and a worst-escaped public envelope. Paired cases must deny a destructive command after the write, executable substitutions, output piped into an interpreter, and malformed/incomplete input. A large unproved source must still deny for its executable limit or inspection failure. Stop after shell, fallback, limit, and paired controls pass through all providers.

#### Task T6: Correct proven Python-writer accounting and wrapper handling

Prerequisites: T5; serialize shared policy edits. Own `_python_preflight()`, `_python_inspection()`, `_python_threats()`, `_inline_operand()`, the Python side of shared admission/accounting, validated wrapper recognition, and Python/wrapper tests. Keep the T3-defined supported language subset narrow. Proven literal file data must not consume shell token/segment or normalized executable-byte budgets. Replace premature whole-literal `_InspectionBudget.source()` charges and constant-byte rejections only with T3's finite source/parser/content accounting, not blanket larger executable limits. Preserve AST work limits, syntax depth, aggregate content limits, symbol/alias tracking, and independently discovered execution sinks. Preserve the remaining unproved interpreter arguments even after inspecting a body.

Verify the sanitized 860-token wrapped incident and a supported wrapped Python literal writer above 32 KiB now allow, including a near-capacity literal. Pair every newly exempted writer shape with resolved and unresolved subprocess/`eval`/`exec` execution, aliases, attached interpreter options, extra arguments, and nested/shared-stdout pipeline controls. Large unproved executable source retains the old executable budget; unknown wrapper options remain strict. Stop after both original incident families, larger writer cases, and dangerous pairs pass together; do not generalize to arbitrary Python execution.

Milestone integration uses the four policy suites, three provider suites, and security-banner suite. All previously required dangerous controls must still deny for the intended rule or inspection failure, rather than merely denying because of another tiny budget. New ordinary file operations must allow without warnings and record successful audits. Capture resource measurements before accepting the milestone.

### Milestone 4: Remove justified complexity without losing throughput

Status: open
Acceptance: not met

#### Task T7: Make results, enforcement, and diagnostics explicit

Prerequisites: milestone 3 accepted. Own routing/reporting/orchestration in `hooks/families/tool_guard.py` and focused banner/audit tests. Introduce an explicit inspection result containing profile, route, profile cause, findings, and completeness. Return it instead of mutating `TOOL_PROFILE`, `TOOL_ROUTE`, and `PROFILE_CAUSE`. Compute normal enforcement once from result and mode. Keep audit-failure handling as an explicit final decision step: ordinary warn findings may allow with an audit warning, while clean calls, exceptions, and incomplete inspection must preserve their current fail-closed behavior when auditing fails. Preserve skip semantics and malformed/bootstrap denial paths.

Prefer fixed trusted action summaries over rebuilding arbitrary surrounding command context. Preserve the existing banner obligations: safe action/tool, at most three distinct causes plus omitted count, an `Action:` summary capped at 160 characters, exact limit units/counts, bounded log parity, and no raw secrets. Do not remove redaction where labels or retained fields remain caller-controlled. Keep category/severity/rule IDs stable unless an intentional diagnostic change is explicitly recorded. Stop after public output/audit tests and full-process measurements show the result is simpler and preserves the contract.

#### Task T8: Evaluate remaining simplifications individually

Prerequisites: T7. Own the policy renderer, optional new canonical `hooks/runtime/tool_guard_policy.py`, rule and parser representations, relevant generator/packaging checks, and candidate-specific benchmarks. This is a sequence of bounded evaluations, not one combined rewrite. Record for each candidate what concepts disappear, tests exercised, timing/resource delta, and the adopt/retain decision.

First compare readable rule literals and unified records with existing `R(...)`, `PATTERNS`, and `RULE_DETAILS`. Keep precomputed matchers and stable rule order. Remove ignored suggestions only after verifying no consumer needs them; no deletion-only regression test is required. Do not claim character codes are faster or slower without measuring generation/import and complete subprocess cost.

Next prototype matching command and pipeline rules directly against existing parsed representations instead of repeatedly reconstructing text. Preserve raw provenance, strict fallback, Windows handling, nested consumers, sequential shared stdout, shell options, and normalized aggregate work. Keep old and candidate paths in disposable variants for differential tests; do not ship a permanent dual-engine switch. If the change only relocates complexity or loses throughput/security, retain the current implementation and explain why.

Then evaluate moving the embedded policy string to ordinary `hooks/runtime/tool_guard_policy.py`, rendered to the existing provider-local helper paths. Prefer the current single-helper delivery interface; keep adapter imports explicit and limited to public operations. A source extraction must reduce private-import and source-splitting machinery, preserve lazy imports, and include runtime sources in build identities and benchmark fingerprints. `hooks/families/reporting.py` and `hooks/families/allowlist.py` need changes only when eliminating their string-splicing behavior safely; do not broaden into scanner refactoring. If any new runtime helper is indispensable, register it in `hooks/manifest.py` and update both Codex installer copy lists in `scripts/install.sh` and `scripts/install.ps1` plus ownership checks before calling packaging complete.

Finally evaluate whether general literal-data handling subsumes Guardian-specific `_GUARD_TARGETS` and survey exemptions. Remove a special case only after its legitimate probing workflow still passes and nearby executable controls deny. Keep special cases that remain necessary; recognize their cost honestly.

Each adopted candidate must pass differential security tests and pre/post whole-hook timing before replacing the working version. An unexplained or repeatable performance violation means rework or retain the optimization, not relaxed gates. Stop after every named candidate has a recorded decision; adoption of every candidate is not required for acceptance.

### Milestone 5: Prove integrated behavior and finish source delivery

Status: open
Acceptance: not met

#### Task T9: Integrate, validate, review, and document

Prerequisites: T7 and T8 complete with their evidence. Own integration only; no new features. Regenerate manifest-owned outputs, run focused and packaging suites below, obtain security/code-quality review, and resolve material findings. Review must specifically check that proved data cannot erase executable pipeline context, content-budget accounting cannot omit fields, and every audit failure path retains its enforcement outcome. A partial or timed-out review is not security approval.

Freeze candidate, versioned fixtures, expectations, and harness before final measurements. Compare against both the original current baseline and relevant immediately preceding accepted candidates, so a cumulative regression cannot hide behind individually acceptable steps. Run complete warm/cold timing and resource gates serially, including new large-content boundary cases and failed-audit/error cases under T2's declared per-case mode/audit contract. Normal cases require successful completed logging; intentionally unavailable-audit cases require the injected failure, expected failed-audit attribution, and correct enforcement instead of an impossible completed-record requirement. Keep baseline observations and candidate requirements separate. Extend `README.md` only for changed user-facing limits, configuration, or diagnostics. Complete one coordinated `update-agent-docs` pass with the admission rubric; no new memory is required merely because code changed.

Acceptance requires all integrated source checks, security review, complete timing gates, finite-case resource gates, and packaging checks to pass with retained evidence. Native Windows execution is a separate platform proof where affected; record unavailable coverage as outstanding rather than treating a non-Windows skip as a pass. No live installation or re-enablement is required to claim source acceptance, and source acceptance must never be described as deployed proof. Any owner/platform action remains explicit in Outcomes. Stop at source delivery until installation/re-enablement is authorized.

### Task graph and shared invariants

P0, including second-review reconciliation, is complete. T1 requires new execution authorization and accepted P0. T2 requires T1; T3 requires accepted T1/T2; T4 requires accepted T3; T5 requires T4; T6 requires T5; T7 requires accepted T4/T5/T6; T8 requires T7; T9 requires T7/T8 and their evidence. T3 supplies new capacity fixtures through T2's already-delivered interface; this is a later input publication, not a circular prerequisite for T2's initial baseline. These prerequisites are explicit and do not derive merely from checklist order.

The shared invariants are whole-input inspection, exact schema validation, finite admission and post-proof budgets, preserved executable context, incomplete-inspection denial, redacted bounded diagnostics, isolated auditing with the declared success/failure outcome, and provider-local delivery. Milestone integration checks prove these jointly; passing individual tasks or merging cleanly is insufficient. The implementation owner reconciles the plan and generated outputs; tests that mutate fixtures, generation, and benchmarks must not run concurrently with repository edits.

## Concrete Steps

Plan revision, second Astra review, and reconciliation are complete. The next unfinished action is implementation authorization from the user; until then, stop. The following commands are future execution instructions, not commands run during planning.

After authorization, verify prerequisites from repository root:

    rtk --version
    rtk gain
    rtk git status --short
    rtk proxy python3 --version
    rtk proxy python3 scripts/generate-hooks.py --check
    rtk proxy python3 scripts/verify-hook-release.py --help
    rtk proxy python3 scripts/test-all.py --list

Record the actual interpreter used. Existing source uses modern Python syntax; a syntax/import error is an environment failure, not a security pass. Preserve unrelated worktree edits. Create disposable frozen roots and evidence directories under `/private/tmp` with unique names. Archive the recorded baseline revision with `rtk proxy git archive` into the empty baseline root, and verify runtime fingerprints. Freeze the candidate by copying maintained source and generated provider Python files, excluding `.git`, caches, runtime logs, and unrelated user artifacts. Never benchmark a live changing worktree.

At each source change, refresh outputs before dependent tests:

    rtk proxy python3 scripts/generate-hooks.py --write
    rtk proxy python3 scripts/generate-hooks.py --check

Stop on a nonzero result. Pause all repository edits before `scripts/test-generate-hooks.py` because its assertions snapshot the entire checkout.

After T2 adds and verifies the explicit baseline options, use its exact CLI as follows. Set `GUARD_BASELINE`, `GUARD_CANDIDATE`, and `GUARD_EVIDENCE` to the frozen roots and fresh disposable evidence directory; these are task variables, not replacements for HOME or CODEX_HOME:

    rtk proxy python3 scripts/verify-hook-release.py --baseline-root "$GUARD_BASELINE" --candidate-root "$GUARD_CANDIDATE" --baseline-ref 260c578ace3514c4f2f741f51d970fc2e938786d --fixture-set file-operations-v1 --expectations scripts/fixtures/tool_guard_file_operations_expectations.json --mode timing --output "$GUARD_EVIDENCE/timing-original-v-final.json"
    rtk proxy python3 scripts/verify-hook-release.py --baseline-root "$GUARD_BASELINE" --candidate-root "$GUARD_CANDIDATE" --baseline-ref 260c578ace3514c4f2f741f51d970fc2e938786d --fixture-set file-operations-v1 --expectations scripts/fixtures/tool_guard_file_operations_expectations.json --mode resources --output "$GUARD_EVIDENCE/resources-original-v-final.json"
    rtk proxy python3 scripts/benchmark-tool-guard-resources.py --script-root "$GUARD_CANDIDATE" --fixture-set file-operations-v1 --expectations scripts/fixtures/tool_guard_file_operations_expectations.json --condition candidate --output "$GUARD_EVIDENCE/resources-finite-cases.json" --samples 25 --warmups 3 --ceiling-ms 500

The new baseline, fixture-set, expectations, and condition options do not exist at planning time. Do not run these commands until T2 delivers them and T3 publishes capacity cases. Use the same fixture/expectation hashes for both runners. Retain original results and use a new output filename for every retry. The historical ablation command is not a substitute; either keep it on its documented frozen revision or build a separately verified candidate-specific comparison using the maintained measurement mechanics.

## Validation and Acceptance

### Functional and packaging commands

Run from repository root when the named source is affected; expected result is exit 0 with passing assertions, not a skip or suppressed failure:

    rtk proxy python3 scripts/test-tool-guard-false-positives.py
    rtk proxy python3 scripts/test-tool-guard-native-data.py
    rtk proxy python3 scripts/test-tool-guard-shell-data.py
    rtk proxy python3 scripts/test-tool-guard-limits.py
    rtk proxy python3 scripts/test-security-banners.py
    rtk proxy python3 scripts/test_helpers.py
    rtk proxy python3 scripts/test-benchmark-high-rate-hooks.py
    rtk proxy python3 scripts/test-verify-hook-release.py
    rtk proxy python3 scripts/test-generate-hooks.py
    rtk proxy python3 scripts/test-install-codex-hooks.py

Run the provider suites sequentially with `OBSERVABILITY_LOG_PATH` set to a unique writable file under a disposable directory, never the real observability database/log. Use the existing fixture helpers to isolate HOME and audit paths:

    rtk proxy bash scripts/test-hooks-tool-guard.sh
    rtk proxy bash scripts/test-codex-hooks-tool-guard.sh
    rtk proxy bash scripts/test-gemini-hooks-tool-guard.sh

After the suites, require `rtk proxy python3 scripts/generate-hooks.py --check` again. If helper delivery changes, run Bash installer tests with `rtk proxy bash scripts/test-install.sh` and native PowerShell installer checks with `rtk proxy pwsh -NoProfile -File scripts/test-install.ps1` in the appropriate environment. Changes to shared input/reporting helpers also require the affected scanner/public-input suites from `.agents/instructions/testing/hooks-security.md`; their exact selection must be recorded before implementation. Run native Windows hook coverage with `rtk proxy pwsh -NoProfile -File scripts/test-codex-hooks-windows.ps1` on Windows when parser/reader/delivery changes affect it. Missing platforms remain outstanding coverage.

### Observable scenarios and negative controls

Use public provider JSON stdin/stdout, the real generated script plus local helpers, block mode for ordinary reproductions, no `SKIP_TOOL_GUARD`, no allowlist, and isolated logs. Explicit warn-mode and allowlist/skip controls use only their declared settings. Codex shell payloads use `tool_name: exec_command` and `tool_input: {cmd: ...}` or the supported `Bash`/`command` shape; Copilot uses `toolName: bash` / `toolArgs: {command: ...}`; Gemini uses `tool_name: run_shell_command` / `tool_input: {command: ...}`. Reuse corpus adapters rather than guessing additional aliases.

The sanitized quoted Markdown writer and wrapped Python writer must first deny with `command_tokens`, then allow after repair without a warning and with a clean audit. Additionally require both shell and wrapped Python writers above 32 KiB, near-capacity bodies, and unproved large-source controls through the complete public entrypoint; this exposes routing and shared source-byte gates rather than only token accounting. Send their strings to Guardian only, never to a shell. Large valid native edits/patches must pass up to the chosen complete aggregate capacity, including a decoded 1 MiB ASCII body encoded entirely as `\uXXXX` when 1 MiB is selected. Verify derived raw-envelope bounds plus metadata and first-rejected raw/decoded/executable values independently. The first rejected byte must report its true budget and units. Protected `.env`/`.git` patch deletes and move sources still deny; valid updates containing dangerous-looking documentation remain data. A filename extension must not change that classification.

Pair every positive with dangerous execution in a following command, command substitution, unquoted expansion, interpreter operand, subprocess/eval/exec sink, unknown wrapper, and nested pipeline. Preserve sequential commands that share stdout with a downstream interpreter. Validate unknown/extra fields, invalid types, missing/corrupt helpers, malformed JSON, invalid UTF-8, open stdin, buffered trailing input, parser exhaustion, normalization expansion, and audit unavailability. Inspect actual cause and attribution; an unrelated size denial does not prove the dangerous operation was detected. Incomplete inspection denies in block and warn modes, even with a valid matching allowlist. Valid exact allowlist and explicit skip behavior remain unchanged.

### Throughput and resource gates

Use complete hook subprocesses with identical payloads, interpreter, provider, mode, and intended logging/failure conditions between baseline and candidate. Normal cases require successful completed logging; audit-unavailable and pre-audit failure cases follow the explicit case contract below. Run no edits, generation, other tests, or concurrent benchmark processes during measurements. Measure two matched warm pairs, each with 25 samples and three warmups; launch baseline and candidate adjacently and reverse order in pair 2. Gate each pair independently by candidate minus baseline median and p95, without pooling pairs. Each provider/case allows at most +2 ms warm median and +5 ms warm p95. Cold measurement requires at least 25 independent fresh-copy launches per condition/case, zero provider bytecode, and allowances of +5 ms median and +10 ms p95. OS/standard-library caches remain uncleared. Record first-process observations, raw samples, MAD, hashes, decisions, audit-outcome proof, and concurrency separately.

Both runners select `historical-v1` or `file-operations-v1` explicitly and verify immutable payload hashes against the same reviewed expectations. Preserve old-capacity cases as historical boundary observations, with candidate allows explicitly declared after capacity increases, and add separately named candidate maximum/overflow cases. The standalone runner's `--condition candidate` must use those outcomes rather than hardcoded old denials. Historical invocations keep their original inputs/expectations and cannot acquire new corpus cases silently.

Every case declares mode, decision, and audit outcome per condition. `written` requires the exact expected number of completed records with matching mode/event; missing or unexpected records fail. `failed` requires validated failure injection and expected response attribution/enforcement, not a successful-write assertion or a blanket missing-log exception. For example, audit failure denies a clean call in block and warn modes, allows an ordinary finding in warn mode with an audit warning, and denies incomplete inspection in either mode. `not_attempted` requires the specified transport/bootstrap failure and appropriate denial attribution where that version supports it. Establish and verify failure conditions outside the timed invocation and retain source-specific baseline expectations when historical attribution differs. Classify these cases separately in reports; they still receive their applicable latency/resource gates.

Retain and explain isolated violations, perform one exact targeted repeat with new evidence, and reject unexplained or repeatable violations. Filtered repeats and `--mechanics-only` runs are not full release acceptance. Compare unchanged workloads and repaired workloads separately, while retaining both in final evidence; repaired allow outcomes must still produce successful audit writes.

For finite resource cases, every first and measured call must meet 500 ms. Collect RSS separately using native macOS `/usr/bin/time -l`; its RSS unit is bytes and its wrapper cost is excluded from latency. Include native maxima and just-over-limit values, shell/Python writers above 32 KiB and near capacity, fully escaped ASCII/raw-envelope boundaries, aggregate Unicode/normalization, executable exhaustion, malformed inputs, and declared audit-failure cases. Compare the same raw payloads against baseline with reviewed condition-specific outcomes, retain peaks, and investigate unexplained superlinear growth. A fast baseline size rejection is not evidence that candidate processing of accepted large content is equally cheap. This does not prove a universal memory bound. An unavailable RSS collector or sandbox `sysctl kern.clockrate` denial is missing evidence, not a pass; retain the error and use an approved collector/environment.

## Idempotence and Recovery

Public hook replays are repeatable because they consume inert input strings and write only to disposable homes. Never execute a recorded command or copy raw session contents, secrets, or full user documents into fixtures/evidence. Sanitized fixtures must preserve the failing structure. Keep generated outputs and canonical changes synchronized; repeat generation safely after partial failure, then rerun the affected checks.

Keep the untouched baseline and each accepted candidate until final evidence is retained. Failed candidates remain disposable and must not replace the working policy. Roll back only this effort's scoped changes using reviewed diffs; do not reset or overwrite unrelated edits. Do not modify historical benchmark evidence, lower thresholds to manufacture a pass, disable failing tests, or use skip/allowlist settings to bypass a reproducer. If a new capacity cannot fit transport/deadline/resource limits, return to T3 and reconcile all affected decisions, tasks, and acceptance statements before continuing.

The user's installed hook remains disabled as previously configured. Do not install or re-enable it during source work. After separate authorization, follow `scripts/install.sh`, the live-hook testing route, and Codex trust review. A live validation failure leaves source evidence intact but deployment acceptance outstanding; the owner controls restoration or re-enablement.

## Interfaces and Dependencies

Use Python's standard library and existing generator/test/benchmark utilities. No new parser library, service, or long-lived process is planned. Additional dependencies require a documented need and security/performance assessment before adoption.

Keep `render(provider, target) -> str` and existing generated entrypoint/helper locations stable. Provider response JSON and exit-0 denial semantics remain unchanged. Missing/corrupt helper bootstrap continues to deny in block and warn modes. All new APIs must have explicit input ownership and bounded failure behavior.

The proposed result model in T7 carries profile, route, profile cause, immutable or owned findings, and completeness. Inspection returns this result; ordinary enforcement derives from result plus mode, audit records the decision, and an explicit audit-failure step can override it under existing policy. Avoid exposing parser-private helpers to adapters. T3 must record exact final declarations before dependent implementation; the model is not permission to import a large eager framework or add objects per token without measuring their cost.

T3's admission interface must distinguish a finitely admitted complete source from proved inert spans and unproved executable spans. T4 owns routing and shared source-budget admission, T5 owns shell proofs/accounting, and T6 owns Python proofs/accounting. Source admission must preserve finite aggregate parser work and must not mark the source clean. Unproved spans retain the current normalized executable limits, including failures encountered after nested interpretation. Record final signatures and raw-envelope derivation before T4 starts.

The proposed `scripts/fixtures/tool_guard_resource_cases.py` owns versioned resource payload construction for both runners. `scripts/fixtures/tool_guard_file_operations_expectations.json` owns reviewed per-condition mode/decision/audit expectations and fixture hashes. Neither may import the candidate policy to determine expected outcomes or limit values at measurement time. Fixture data is frozen from explicit reviewed T3 decisions. Both runners include these inputs in harness fingerprints and preserve historical default behavior.

If source extraction is adopted, create `hooks/runtime/tool_guard_policy.py` as the canonical ordinary Python module and continue rendering it into each provider's own `helpers/tool_guard_policy.py`. Preserve shared allowlist/reporting ownership without cross-provider imports. Extend build identities and runtime-footprint fingerprints for all newly authoritative sources. Keep optional command/language imports lazy. Update installers only if delivery assets actually change, and validate both platforms' exact asset closures.

## Artifacts and Notes

Planning evidence: current revision `260c578ace3514c4f2f741f51d970fc2e938786d`, clean initial `git status --short`, inspected policy/readers/corpus and benchmark CLIs. The first Astra review found four P2 contract gaps; their source-verified repairs are incorporated throughout the tasks, decisions, commands, and acceptance rather than appended as exceptions. On 2026-10-20, Astra's second read-only review confirmed all four resolved and found no new actionable P1/P2 findings. Its verification covered derived encoded capacity, both runners' versioned expectations, mode-specific failed-audit evidence, and the full routing/source-budget/writer-proof admission contract. No implementation tests or new benchmark runs were performed while authoring, revising, or reviewing this plan. Later implementation must establish feasibility and satisfy all remaining milestone gates.

Future temporary evidence belongs in `.agents/scratchpad/tool-guard-file-operations/` or a uniquely named `/private/tmp` directory. Retain hashes, environment, sanitized fixture IDs, raw timing samples, current decisions, and concise acceptance summaries. Keep the active plan sufficient to resume without private session logs. Do not store full transcripts as knowledge-base memory. Record the final end-of-session documentation disposition and all outstanding owner/platform actions here before closing the effort.
