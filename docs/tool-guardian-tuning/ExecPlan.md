# Fix Tool Guardian false positives within measured latency budgets

This ExecPlan is a living document. Maintain `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` according to the `exec-plans` skill. Its repository path is `docs/tool-guardian-tuning/ExecPlan.md`.

## Purpose / Big Picture


Users must be able to write documentation, source, and tests, search for command examples, and run the observed harmless analysis scripts without Tool Guardian rejecting their data as executable instructions. Fix every known false-positive category across Codex, Copilot, and Gemini. Preserve detection of actual dangerous operations, complete inspection of executable input, resource bounds, and existing provider response contracts.

The hook runs frequently. Apply the revised user-approved latency budgets below to existing inputs. The original zero-regression requirement is retained only as historical context in earlier failed reports. Measure the entire hook subprocess, including startup, input decoding, policy evaluation, logging, and response emission. Do not hide a regression behind a parser-only improvement. The user will run the installer after repository validation. Agents must not update real installed hooks as part of this plan.

## Progress


- [x] (2026-10-01) [planning] Review accessible session and guardian logs and identify false-positive categories.
- [x] (2026-10-01) [planning] Obtain user agreement on scope, security boundaries, fallback behavior, delivery, and latency requirements.
- [x] (2026-10-01 22:18Z) [milestone-1] Preserve 47 sanitized fixtures, reproduce baseline failures through 144 public provider checks, and retain two sequential complete-hook timing runs with 147 scenarios each.
- [x] (2026-10-01 22:16Z) [milestone-2] Separate recognized native tool content and search data from executable instructions; reviewed native change integrated at e373690d.
- [ ] [milestone-3] Support the observed shell and Python forms without broad interpreter exemptions, and remove repeated or quadratic scanning work.
- [ ] [milestone-3 repair] Remove repeatable normal-cache and cold startup/writer regressions from all frozen candidates, including the final B/C/C/B comparison; preserve failed reports and all security protections before retiming.
- [x] (2026-10-02 00:00Z) [optimization proof] Independently validate optional helper and suffix optimizations through public decisions and repeated complete-hook ablations; preserve measured growth benefits and the unresolved combined survey regression for startup repair.
- [ ] [milestone-4] Set measured resource bounds, validate security and latency, and regenerate all three providers.
- [x] (2026-10-01 23:45Z) [milestone-4] Update the old Gemini 33,000-byte native-write banner assertion to verify truthful overflow beyond the new 65,536-byte native bound, while retaining unsupported-input 32,768-byte strict-limit coverage.
- [ ] [milestone-5] Synchronize documentation and deliver repository changes with user-run installation instructions.

## Surprises & Discoveries


The final matched B/C/C/B sequence also fails latency acceptance. Clean medians increased by 3.053/4.906 ms for Copilot, 3.667/3.210 ms for Gemini, and 2.157/3.426 ms for Codex in the two pairings. The repeated baseline median spans are only 0.807, 0.799, and 0.655 ms respectively. Large-input improvements do not offset these frequent-path regressions. Root retained a complete descriptive comparison externally pending integration. Native macOS resource collection initially failed because the sandbox denied `/usr/bin/time -l` access to `sysctl kern.clockrate`; the hook emitted its correct allow decision. The harmless approved collector probe succeeds, and the unchanged resource run uses approved native collection.

The first valid frozen candidate passed all 147 benchmark decisions but failed latency acceptance. Clean-input medians were 30.815, 31.159, and 28.420 milliseconds for Copilot, Gemini, and Codex. Python-writer medians were about 32-33 milliseconds, above the corresponding baseline observations. Large-input scanning improved substantially, but that improvement cannot offset slower frequent paths. The original shell implementer owns the repair and subsequent frozen retiming. Independent review also reproduced missing download-execution findings for execution-preserving pipeline wrappers; those protections must be restored before the candidate is accepted.

Milestone 1 public-entrypoint controls exposed existing execution-sink gaps: protected-branch force push inside shell substitution and a Python execution sink was allowed by all three baseline hooks. Baseline expectations preserve those observations; candidate expectations still require denial. Native provider equivalents also have different pre-fix decisions for some literal examples, so the shared corpus records provider-specific baseline expectations.

The initial inbox description suggested a size-limit problem. Review found at least 23 falsely blocked file-write invocations: 12 input-limit failures and 11 command-pattern failures in inert documentation, source, or test text. The broader review also found false read-only search and analysis blocks. Raising limits alone cannot fix the accepted scope.

The first complete guardian-log snapshot contained 19 denials: 15 false file-write blocks, one false search block, and three actual forbidden operations. Eleven older transcript-only denials added eight false patch writes and three shell cases. The latter resolve to one genuine protected-branch force push, one harmless hook-fixture survey, and one harmless search. Correlate the historical search against the earlier search finding before publishing a combined unique-incident total. Two survey-generated read-only false blocks, and a further read-only search block during plan preparation, belong in separate evidence rather than silently increasing the original snapshot count.

The scanner applies shell-style segmentation to every string leaf and to a second serialized representation of structured input. It splits actual and escaped newlines and punctuation without first establishing whether the text is executable syntax. One 7,271-byte patch had 124 physical lines but 142 parsed segments. The reported count of 129 is the bounded splitter's overflow indicator, not the uncapped segment count.

An exploratory in-memory measurement found about 9.5, 35.4, 136.9, and 521.3 milliseconds for 256, 512, 1,024, and 2,048 repeated command tokens. This suggests approximately quadratic work in repeated tail scans. These numbers are diagnostic evidence, not a whole-hook baseline or a production timing guarantee.

The original native-write handling had no semantic model for patch deletion or movement. Milestone 2 now parses validated Codex patch operations and applies equivalent existing source-removal rules. It does not add general destination protection. Saved script contents are not read when a script is invoked. Do not describe the guardian as a general code security analyzer or claim protections that it does not provide.

Plan authoring reproduced another file-write false positive: the SQL rule's keyword matched a harmless English past-tense inflection in prose about complete inspection. Preserve that content case separately from the original incident count.

## Decision Log


- Decision: Apply separate steady-state and no-provider-bytecode cold budgets instead of zero measurable regression.
  Rationale: The user explicitly agrees that a few milliseconds are acceptable for this hook. Steady-state limits are +2 ms median/+5 ms p95; cold limits are +5 ms median/+10 ms p95 per provider and case. Maintain full inspection, successful logging and the 500 ms finite resource ceiling.
  Date/Author: 2026-10-02 00:09Z, user and implementation orchestrator.

- Decision: Extract unchanged provider-neutral policy into generated local helpers using ordinary Python imports, retaining provider-specific adapters in entrypoints.
  Rationale: The main script recompiles its growing policy on every subprocess launch. Standard helper bytecode caching is simpler than self-managed caches and preserves complete inspection. The original shell worker owns the manifest, generator and disposable installer coverage. Fresh-install/no-bytecode timing remains explicit; the implementation is not accepted until full-hook gates pass.
  Date/Author: 2026-10-01 23:41Z, implementation orchestrator.

- Decision: Measure unchanged hooks from an immutable external baseline while native-classifier work proceeds in its isolated candidate worktree.
  Rationale: The copied baseline preserves unchanged runtime code independently of candidate edits. Milestone 2 integration followed the frozen incident corpus and first complete unchanged-runtime report; the second sequential baseline and milestone 1 commit then integrated without conflicts.
  Date/Author: 2026-10-01, implementation orchestrator.
- Decision: Fix all known false positives, including related read-only operations, across Codex, Copilot, and Gemini.
  Rationale: Observed failures share scanner defects, and the three provider outputs derive from one canonical implementation.
  Date/Author: 2026-10-01, user and planning agent.
- Decision: Treat recognized file content as data regardless of extension and retain checks on executable instructions.
  Rationale: Documentation, source, and test examples are not operations performed by the tool. The user accepted an operation-based guard without adding a general code-content scanner.
  Date/Author: 2026-10-01, user.
- Decision: Keep existing strict scanning for unrecognized inputs, including its resource bounds.
  Rationale: Only reliably classified data may be excluded from executable-command matching. Arbitrary shell or Python bodies receive no blanket exemption.
  Date/Author: 2026-10-01, user.
- Historical decision (superseded by the 2026-10-02 revised budgets): Do not add measurable latency to existing hook workloads.
  Rationale: This hook runs frequently. Security, correctness, and speed are simultaneous acceptance gates, not trade-offs to relax silently.
  Date/Author: 2026-10-01, user.
- Decision: Deliver repository changes and regenerated provider outputs, leaving real installation to the user.
  Rationale: The user explicitly chose to run the installer personally.
  Date/Author: 2026-10-01, user.
- Decision: Choose numeric resource changes from complete-hook measurements and incident coverage rather than multiplying every constant.
  Rationale: Existing bounds protect inspection cost, and the parser exhibits adverse scaling. Preserve a fail-closed boundary beyond validated limits.
  Date/Author: 2026-10-01, planning agent, implementing the agreed security and latency constraints.

## Outcomes & Retrospective


Milestone 1 is complete. The shared corpus verifies 144 public-entrypoint checks in baseline mode, including all 20 direct rule controls. The candidate contract remains intentionally red on unchanged hooks. The benchmark CLI regression suite passes, the registry contract includes the new suites, and generator freshness is unchanged. Two sequential final baseline reports each retain 147 scenarios, 3,675 raw timing samples, first-run observations, and three four-worker concurrency scenarios. Per-case variation is retained in `evidence/baseline-variation.json`; these are baseline measurements rather than proof of candidate latency acceptance. An earlier adapter revision with briefly overlapping measurement is preserved separately as exploratory evidence and excluded from comparison. No policy or real installed hook was modified by milestone 1.

The reviewed native-classification change has separately been integrated by the orchestrator at e373690d. Its focused native suite is registered here for that integration. Remaining shell classification, truthful raised-native-limit banner coverage, adversarial verification, and candidate timing gates remain open. The formal agent-document pass is deferred until the entire implementation session ends.

Planning established the original unchanged guardian snapshot before implementation. At that checkpoint no guardian implementation, threshold changes, generated output changes, or real installation had occurred. Investigation corrected the original limit-only hypothesis. Implementation acceptance remains unmet until the public-entrypoint reproductions pass, actual dangerous operations remain blocked, and repeated full-hook benchmarks meet the current user-approved per-case budgets.

The inbox item has moved into this plan. The file map, repository routing, and current guardian known issues are synchronized. Canonical-document lint, generator freshness, and whitespace checks pass. These document checks do not establish implementation or performance acceptance.

## Context and Orientation


Work from the repository root. `hooks/families/tool_guard.py` is the canonical renderer and contains policy source embedded in a generated Python script. `hooks/manifest.py` lists its three outputs: `.codex/hooks/tool-guard.py`, `.copilot/hooks/scripts/tool-guard.py`, and `.gemini/hooks/scripts/tool-guard.py`. Change the canonical source, then use `scripts/generate-hooks.py` to regenerate outputs. Never edit generated scripts directly or introduce cross-provider runtime imports.

The relevant functions are `read_tool_scan_inputs`, `_command_segments`, `build_threats`, `build_input_threats`, the individual rule matchers, and `main`. `KNOWN_TOOL_FIELDS` labels trusted fields for diagnostics only. Milestone 2 adds a separate `NativeToolInput` classification for exact provider aliases and validated schemas. Validated native data has a provisional 65,536-byte aggregate bound, including keys and metadata, pending milestone 4 measurement. Unsupported inputs retain the original 32,768-byte inspection bound. Structural bounds remain 32 levels, 256 nodes, and 128 strings. Executable text still bounds characters and bytes at 32,768, segments at 128, and tokens per segment at 256 until measured changes prove necessary.

`scripts/test-security-banners.py` supplies cross-provider public-input and response assertions. The provider suites are `scripts/test-codex-hooks-tool-guard.sh`, `scripts/test-hooks-tool-guard.sh`, and `scripts/test-gemini-hooks-tool-guard.sh`. `scripts/test-all.py` owns the explicit test registry. `scripts/benchmark-high-rate-hooks.py` already measures full subprocess runtime on macOS with disposable repositories, log paths, and homes. Its results include median, 95th percentile, median absolute deviation, a first-run sample, and a concurrent batch. Median absolute deviation measures ordinary variation around the median. Provider delivery latency is distinct from subprocess runtime.

Load `.agents/instructions/hooks.md`, `.agents/memory/known-issues/hooks.md`, `.agents/memory/testing/hooks.md`, and the corresponding scripts guidance before implementation. Activate `tdd` for source changes and the security and performance skills for their respective validation. Read the applicable official provider references before changing provider schemas or delivery behavior. Existing output schemas and registrations do not need redesign for this effort.

## Plan of Work


### Milestone 1: Reproduce incidents and establish the performance baseline

Status: done
Acceptance: met

Begin with end-to-end reproductions at the generated provider scripts' stdin/stdout boundary. These scripts receive a provider-shaped JSON tool event and emit the provider's permission decision. They must not execute the represented tool operation. Use disposable destinations and audit paths, never real home-directory hooks. Add a shared public-envelope regression suite at `scripts/test-tool-guard-false-positives.py` and register it in `scripts/test-all.py`. Reuse existing security-banner fixture helpers where appropriate without turning semantic acceptance into banner-string assertions.

Preserve sanitized fixture cases for long patches, actual and escaped newline content, UTF-8 byte growth, command examples in documentation/source/tests, native edit replacements, native writes, safe searches, the two Python writers, the repository-hook survey, and the survey-generated analysis scripts. Attach each fixture to an incident category and source metadata. Do not copy private session contents into version control. Reconstruct the same operation, data role, and relevant size rather than retaining unrelated conversation text. Deduplicate matching log and transcript records by invocation identity where available, otherwise by provider, timestamp, tool, and matched failure. Do not count a test's captured guardian output as a denial of the test runner.

Include a 46,899-byte native patch, a 330-line patch, and the 124-line patch shape that produced 142 naive segments. The shell writers use a quoted Python heredoc, fixed pathlib reads/writes, literal text replacements, and a large literal body. One represented command measured 8,787 characters and 183 naive segments. Another had 120 physical lines and 139 naive segments, including 18 semicolons in literal data. The safe hook survey passes destructive-command examples as JSON stdin to fixed hook scripts rather than executing those examples. Searches pass matching vocabulary as literal patterns. Reproduce these roles, not just their lengths.

Add the harmless English inflection found during plan authoring, constructing the SQL rule keyword from its existing numeric fixture representation and appending the past-tense ending. It must be accepted as native-write prose while an actual database operation remains covered by the paired protection tests.

For each harmless fixture, add a nearby dangerous executable counterpart that must still be denied. Cover all current rule families, especially protected-branch force push, destructive Git cleanup, installer pipelines, protected removal targets, database operations, outbound upload, elevated operations, unsafe permissions, and package publication. Include commands before and after long data, executable shell substitutions inside arguments, interpreter execution sinks, malformed schemas, extra fields, and Unicode normalization. Construct threat examples using the existing numeric-string fixture convention so the installed old guardian does not block test authoring. Never disable it for maintenance.

Capture the unchanged runtime before modifying policy. Extend the existing benchmark runner to reuse the sanitized guard corpus and select a script root so the same runner and inputs can test an isolated baseline snapshot and candidate. Preserve current default behavior and add `--guard-only`, `--script-root PATH`, and `--expected-behavior baseline|candidate` options. The last option validates the known baseline denials separately from the desired candidate permissions. Add public CLI coverage for these options using temporary fixture scripts. Retain raw timing samples and explicit expected decisions. Copy generated baseline scripts and required local helpers into a disposable root before any policy changes. Never install this snapshot.

Run identical inputs and logging conditions for all three providers, including currently allowed calls, actual denials, and formerly blocked legitimate calls. Record Python version, machine, environment, input sizes, and first-run definition. Use 25 measured samples and three discarded warmups initially, repeat paired baseline/candidate runs in alternating order, and increase sampling only when noise prevents a decision. Each measured invocation starts a new Python process. Also retain the existing concurrency scenario and compare its results. Do not call an operating-system cache-warm first-run sample fully cold.

This milestone is complete when public fixtures reproduce current failures without executing dangerous operations, true-positive controls pass on the baseline, incident deduplication is documented, and complete-hook baseline data is retained for comparison.

### Milestone 2: Establish native tool and search data boundaries

Status: done
Acceptance: met

In `hooks/families/tool_guard.py`, introduce a bounded classification stage before command matching. Recognize exact provider tool aliases and validated input shapes for patch, edit, native write, and search operations. Use the schemas established by current provider fixtures and confirmed event envelopes. Tool name alone is not authority to exempt arbitrary fields. Unknown aliases, invalid types, additional executable-looking fields, and unsupported shapes must retain strict scanning.

Represent operation metadata, inert content, executable text, and unclassified text separately. Check structural and total input bounds before exempting content from command-pattern matching. Patch additions, edit old/new text, native write bodies, and literal search patterns are data regardless of extension. Parse patch operation headers separately so deletion or movement cannot disappear inside the content exemption. Preserve equivalent existing operation rules where applicable without inventing a general destination allowlist or claiming an existing native-path protection. Native file edits must not become a blanket exemption for arbitrary nested input.

Eliminate redundant serialized-object rescanning only after tests show every executable or unclassified string still reaches inspection. Dictionary keys, malformed structures, and unexpected fields must not provide a route around checks. Exact-match allowlist semantics and provider input precedence must remain intact. Tests must establish that inert command vocabulary is accepted while the corresponding actual operation is still blocked across all three providers.

### Milestone 3: Classify observed shell forms and remove expensive scanning work

Status: implementation integrated at 0003737c; growth and final latency acceptance remain open
Acceptance: not met

Replace punctuation-only shell segmentation with a bounded tokenizer that respects quotes, escapes, command separators, substitutions, redirections, and heredoc boundaries. A heredoc is a shell construct that passes multiline input to a command. A quoted delimiter suppresses shell expansion of that body, but the destination interpreter can still execute it. Do not treat every quoted argument or heredoc as inert: arguments to an interpreter's command option and bodies supplied to a shell remain executable. Executable substitutions inside apparent data must be inspected.

Support the observed Python forms through a bounded abstract syntax tree, Python's parsed representation of statements and expressions. Use standard-library parsing only when the command actually invokes Python with inline code or a heredoc. Recognize fixed pathlib imports, literal destinations, reads/writes, and constrained ordinary string transformations. Recognize the harmless survey only when the fixed hook subprocess target and its JSON stdin role are established. Inspect dangerous operations at execution sinks. Dynamic execution, arbitrary subprocess targets, dynamic imports, unresolved aliases, unsupported syntax, and language features outside the proven subset retain full strict scanning. Do not grant an exemption to Python, search commands, or test scripts as a class.

Tokenize each executable input once and reuse that representation across rules. Replace repeated suffix traversal with bounded linear processing where the same rule semantics can be proven. Keep unsupported constructs on the strict path rather than attempting general shell or Python interpretation. Avoid new runtime dependencies, network calls, helper subprocesses, or unconditional parser imports. Lazy-load language-specific parsing only for relevant inputs and measure its startup cost. Each optimization must have independent correctness and full-hook timing evidence.

This milestone is complete when the observed shell writers, safe searches, and hook-fixture surveys pass, their dangerous counterparts fail, and repeated-token stress no longer exhibits the diagnosed quadratic growth.

### Milestone 4: Validate resource limits, security, and runtime across providers

Status: source, correctness and finite resource evidence integrated at 84eae394; overall latency repair remains open
Acceptance: not met

Separate bounds on accepted native data from bounds on executable inspection work. Keep finite limits for aggregate bytes, structure, normalized text, commands, tokens, and language-parser work. Native body line count must not consume an executable-command budget. Choose the smallest validated limits that admit every preserved incident fixture with documented headroom. Record actual selected constants, worst-case memory and runtime evidence, and the reason for each change in this plan. Do not globally multiply every bound or add an environment setting that disables inspection. Partial-input acceptance, skipped overflow, and timeout-based allow responses are unacceptable.

Boundary tests must check the accepted maximum and the first rejected input for each resource class, including UTF-8 and normalized text expansion. Update old numeric assertions to the new truthful boundaries without removing overflow tests or weakening fail-closed behavior. Input-limit and inspection-failure denials still precede allowlisting and still deny in warn mode. Incomplete inspection is not a benign unknown construct. Known dangerous operations retain their existing block/warn semantics, severity, rule identities, safe banners, and log redaction. Normal passes remain silent.

Regenerate the provider outputs through `scripts/generate-hooks.py --write`. Run generator freshness checks, generator tests, the new false-positive suite, all three provider guard suites, security-banner tests, and benchmark-runner CLI tests. Run a native Windows public-envelope check if execution is available. A macOS skip or simulated Windows branch is not native Windows evidence. Report unavailable platform proof explicitly without silently changing the supported surface.

Use the same benchmark runner and corpus against the saved baseline and candidate. Add the raised-limit boundaries and adverse repeated-token, nested-input, quoting, and normalization cases. Retain measured data, not only rounded summaries. Compare median and 95th-percentile elapsed time per existing scenario and provider, first-run samples across repeated independent runs, and concurrency. Do not pool providers or scenarios in a way that hides a slower frequent path. Quantify run-to-run variation with median absolute deviation and repeated baseline runs. A repeatable slowdown exceeding the revised median or p95 budget fails acceptance. An inconclusive comparison also does not establish the latency gate: repeat or improve measurement, then optimize rather than relax the requirement.

Formerly denied legitimate inputs belong in the same-input comparison, not an unmeasured exception. Newly supported boundary sizes must have a documented bounded runtime ceiling based on the existing measured workload and configured hook deadlines. The exploratory parser-only measurements cannot supply that ceiling. Full subprocess timing does not prove provider-delivery timing. No real installer or live installed-hook timing is performed by the agent because installation is the user's step.

### Milestone 5: Synchronize documentation and deliver the repository change

Status: open
Acceptance: not met

Run `update-agent-docs` once at the end of implementation. Refresh hook conventions, known issues, testing routes, file and API maps as applicable, and this plan's actual constants, decisions, benchmark results, and milestone state. Preserve historical investigation facts but distinguish them from corrected behavior. The current self-maintenance workaround remains applicable until installed hooks are updated. Do not record an implemented capability while this plan is still open.

Deliver the canonical change, regenerated outputs, regression tests, documented benchmark comparisons, and user-run installer instructions. The user runs `rtk proxy ./scripts/install.sh` from the repository root, or the supported PowerShell installer on Windows. They review changed non-managed Codex hook definitions through `/hooks` before live validation. Do not bypass trust, disable guardian protections, rewrite unrelated registrations, or install into the real user home on the user's behalf. Repository validation and later installed/live validation are separate evidence.

## Concrete Steps


From the repository root, the baseline planning checks are read-only:

    rtk proxy python3 scripts/generate-hooks.py --check
    rtk proxy python3 scripts/test-all.py --list

During milestone 1, extend and test the shared benchmark runner before policy changes, then capture isolated baseline runtime using its new script-root and expected-behavior options. The following baseline options become executable after that milestone implements them:

    rtk proxy python3 scripts/benchmark-high-rate-hooks.py --guard-only --script-root /private/tmp/tool-guardian-baseline --expected-behavior baseline --samples 25 --warmups 3 --output /private/tmp/tool-guardian-before.json

After canonical source changes, regenerate and validate:

    rtk proxy python3 scripts/generate-hooks.py --write
    rtk proxy python3 scripts/generate-hooks.py --check
    rtk proxy python3 scripts/test-generate-hooks.py
    rtk proxy python3 scripts/test-tool-guard-false-positives.py
    rtk proxy python3 scripts/test-security-banners.py
    rtk proxy bash scripts/test-codex-hooks-tool-guard.sh
    rtk proxy bash scripts/test-hooks-tool-guard.sh
    rtk proxy bash scripts/test-gemini-hooks-tool-guard.sh
    rtk proxy python3 scripts/generate-hooks.py --check
    rtk proxy python3 scripts/benchmark-high-rate-hooks.py --guard-only --script-root . --expected-behavior candidate --samples 25 --warmups 3 --output /private/tmp/tool-guardian-after.json

The new regression suite and benchmark options do not exist at planning time. Add the regression suite and benchmark CLI test route to `scripts/test-all.py` and update these commands when their final paths or interfaces change. Each correctness command must exit zero with no failed assertions. The baseline false-positive reproductions are expected to demonstrate the bug before policy fixes. The candidate must allow legitimate cases and deny paired actual operations. Performance JSON must retain per-case decisions, input sizes, samples, timing summaries, and environment metadata. Exit zero from a benchmark is not proof of no regression: compare the paired measurements explicitly.

## Validation and Acceptance


### Revised latency budgets (2026-10-02)

The user approved defining separate steady-state and cold-start budgets after reviewing the measured few-millisecond cost. For every provider and scenario independently, steady-state candidate median may exceed its matched baseline by at most 2 ms and p95 by at most 5 ms. For a fresh copy with no provider bytecode, cold-start median may exceed its matched baseline by at most 5 ms and p95 by at most 10 ms. The 500 ms finite resource-case ceiling remains unchanged. These allowances never relax correctness, full inspection, fail-closed limits, successful logging, or provider responses.

Use the same input, interpreter, logging conditions and frozen source. Retain two independent matched normal-cache pairs, 25 measured samples and three warmups per case. Cold validation requires at least 25 independent fresh-copy launches per case and condition, with zero provider bytecode at each launch; operating-system and standard-library caches are not cleared. Check each paired median and p95 directly against its applicable budget. A budget violation needs repair or a targeted repeat to distinguish an isolated host scheduling event; an unexplained or repeatable violation does not pass. Preserve MAD, repeat variation, first processes and concurrency without pooling providers or workloads. Historical reports failed their original zero-regression rule; do not relabel those earlier conclusions as originally accepted.


Acceptance requires all preserved harmless incident shapes to receive an allow response from all supported provider entrypoints, with no extra pass message. Dangerous counterparts must receive the expected deny response in block mode without executing represented operations. Data classifications must survive realistic multiline JSON, aliases, escaped literals, literal search patterns, fixed Python writers, and hook fixtures. Unrecognized executable input must still receive strict inspection. Add cases where execution is hidden beside or inside apparently inert data and require the relevant protections to remain effective.

Over-limit, malformed, and uninspectable input must fail closed with accurate, redacted diagnostics. Allowlisting and warn mode must not bypass incomplete inspection. Existing banner bounds, credential redaction, and banner/log agreement must remain covered. Keep protections for actual force push, destructive cleanup, installer pipelines, and every other current rule family. Do not replace an execution test with a string-only assertion of the new classifier's implementation.

The revised per-case latency budgets apply to the fixed existing corpus. Check complete subprocess runtime per provider and per case, including process startup and repeated first runs. Measurements inside ordinary variation show no measurable change, not a claimed speedup. Retain functionality fixes that meet the agreed per-case latency budgets, but discard optional optimization complexity that buys no measured improvement. Reject repeatable slowdowns exceeding those budgets, hidden extra processes, or false speedups from omitted required inspection. Raised resource limits must additionally pass bounded worst-case runtime and memory checks.

## Idempotence and Recovery


Public-entrypoint fixtures represent operations without performing them. Keep all fixtures, logs, baseline copies, and benchmark reports in disposable directories or maintained sanitized test assets. Use fixture-local Git configuration and disable signing only for fixture commands. Do not globally change Git settings, hook modes, allowlists, trust, or user-installed files. Do not repurpose the shell's home variable for real installation.

Generator write mode is deterministic and may be rerun after canonical edits. If a correctness or timing gate fails, fix or revert the candidate changes while retaining the baseline, incident fixtures, and failed-attempt evidence. Never delete, disable, or weaken a failing protection test to pass acceptance. Restore generated outputs from the canonical renderer rather than manually repairing them. Remove only exact owned temporary paths after recording results.

## Artifacts and Notes


The original log corpus covered August 19 through October 1, 2026, with two nonempty provider guardian logs, 4,703 Codex records, and 922 Copilot records. Investigation searched 387 active Codex transcripts, two archived transcripts, and 30 primary Copilot event files. Eight saved Copilot transcript copies were excluded from primary counting. Retain these as survey coverage, not a claim that every historical invocation was available.

Useful original evidence is the Codex guardian log at `~/.codex/hooks/tool-guardian/guard.log`: line 348 records the 46,899-byte patch rejection, line 3272 the short patch's segment rejection, and lines 1565 and 3482 the Python writer rejections. Log lines can change or disappear, so implementation must preserve sanitized reproductions rather than depend on these files. The historical hook-fixture survey occurred at 2026-09-25T00:15:50Z. The protected-branch force-push denial occurred at 2026-09-23T22:55:41Z. No raw tool payloads or secrets belong in maintained evidence.

Keep before/after performance reports with the implementation evidence and describe exactly which input corpus and entrypoints they measure. Report known timing limitations. Source validation does not certify user-installed behavior. Update this plan's outcomes only when the corresponding acceptance is actually met.

Investigation dispatch audit follows. The selected and submitted configurations matched. The dispatch system did not report executed model or effort, so both remain unconfirmed. Active orchestrator deadline checks enforced runtime limits. The contract exploration was deliberately interrupted to answer the user's question, and a later exploration completed the remaining incident classifications.

    dispatches:
      - subtask_id: guardian_evidence
        selected: &selection {model: gpt-6.1-sol, reasoning_effort: high}
        submitted: *selection
        executed: &execution {model: unconfirmed, reasoning_effort: unconfirmed}
        runtime_limit: &limit {value: 10 minutes, mechanism: Active deadline monitoring with interruption at deadline}
        status: completed
        output_verified: true
        routing_compliant: true
      - subtask_id: all_write_denials
        selected: *selection
        submitted: *selection
        executed: *execution
        runtime_limit: *limit
        status: completed
        output_verified: true
        routing_compliant: true
      - subtask_id: guardian_contract
        selected: *selection
        submitted: *selection
        executed: *execution
        runtime_limit: *limit
        status: cancelled
        output_verified: true
        routing_compliant: true
      - subtask_id: remaining_incidents
        selected: *selection
        submitted: *selection
        executed: *execution
        runtime_limit: {value: 5 minutes, mechanism: Active deadline monitoring with interruption at deadline}
        status: completed
        output_verified: true
        routing_compliant: true

## Interfaces and Dependencies


Keep standard-library runtime dependencies and the existing generated-script provider adapters. The bounded classifier returns validated operation metadata, data payloads with byte accounting, executable fragments, and unclassified fragments with an explicit strict-fallback marker. Do not rely on user-provided labels such as a claimed safe mode to establish these roles. The matcher consumes a shared bounded command representation and emits the existing threat dictionaries used by banners and audit logs. Preserve fail-closed `ScanLimitExceeded` and inspection-failure handling.

The proposed shared regression suite owns sanitized incident and paired-danger fixtures. The existing benchmark runner adds `--guard-only`, `--script-root PATH`, and `--expected-behavior baseline|candidate` while preserving its current invocation defaults. Add a focused benchmark CLI test at `scripts/test-benchmark-high-rate-hooks.py`, register it beside the new regression suite, and validate its public flags without invoking the full high-rate benchmark recursively. Any final interface change must update this plan and area-scoped API/testing documentation before completion.

Revision note, 2026-10-01: Recorded the user-confirmed scope and security contract, all-provider coverage, strict fallback, user-run installation, and no-added-latency requirement. Replaced the inbox's limit-only hypothesis with incident-driven operation classification and measured resource tuning. Implementation remains unstarted.

Revision note, 2026-10-01 22:21Z: Integrated the reviewed native classifier and immutable-baseline corpus, synchronized historical versus current operation handling, and recorded the active shell implementation frontier. Native byte limits remain provisional and candidate latency acceptance remains open.

Revision note, 2026-10-01: Completed milestone 1 with sanitized provider-native fixture equivalents, immutable baseline fingerprints, exact baseline/candidate permission modes, public benchmark CLI coverage, two complete sequential baseline runs, per-case variation, and retained exploratory evidence. Updated the orchestrator-confirmed milestone 2 integration state and the milestone 4 truthful-limit test repair item. The plan is retained as explicitly requested.

Revision note, 2026-10-01 22:43Z: Began independent static security review and milestone 4 boundary-test preparation while milestone 3 measures a frozen candidate snapshot. The initial native review reached its deadline without a verified artifact; it supplies no approval evidence. Candidate reports produced with different sample settings or source edits during measurement are exploratory only. No candidate latency gate has passed.

Revision note, 2026-10-01 23:02Z: Integrated the shell/Python implementation at 0003737c after a conflict-free rebase, with 144 corpus checks, 11 focused shell test methods, 13 native test methods, and 25 generator tests passing. The original worker reproduced and repaired three independent-review bypass classes before integration. Both retained frozen candidates fail latency acceptance; the second predates the final narrow launcher and interpreter-option hardening. Removed the clean integrated worker checkout and branch. Rebased milestone 4 preparation without conflicts and granted that worker exclusive ownership of resource-bound repairs. No final security or performance approval is implied by integration.

Revision note, 2026-10-01 23:45Z: Integrated milestone 4 at 84eae394 after conflict-free rebases and verified matching branch tips. Retained all four failed no-regression reports plus per-case comparison and the successful 90-case finite resource report. Source fingerprints and decisions match. Maximum measured/first runtime was 60.986583 ms and peak RSS 28229632 bytes under the documented 500 ms ceiling; raw-envelope universal memory remains outside this claim. Correctness and truthful native overflow coverage pass. Removed the clean integrated worker checkout and branch. Startup repair and independent optional optimizer proof remain open.

Revision note, 2026-10-01 23:59Z: Independent optional ablations retain 594 initial and 432 Git-only public decisions, 12000 warm samples, frozen hashes and separate per-case results. Common lazy imports and the removal/Git growth summaries have measurable benefits, but the combined suffix report includes a Codex survey regression and supplies no blanket acceptance. The proof worker was interrupted at its 23:54:35 deadline before committing; root verified hashes/counts/CLI evidence and saved its exact checkpoint at 1a49a971. The startup-helper extraction passes correctness and disposable installer checks but fresh no-bytecode observations fail: clean medians add 2.121/1.619/2.732 ms and writer medians add 3.263/3.762/3.450 ms for Copilot/Gemini/Codex. The separately frozen ordinary-cache B/C/C/B measurement continues; neither that result nor warming may exempt the cold failure.

Revision note, 2026-10-02 00:04Z: Integrated independent proof at d602bbe1 after a conflict-free rebase and matching tips; removed its clean worktree and branch. Original private proof source is preserved equivalently at 84eae394 for reproducibility after helper extraction. Root preserved the worker timed-out status. The first ordinary-cache startup-module pair has correct decisions and no positive median deltas across 147 scenarios; the second pair and cold repair remain open. No source edits or hook probes overlap this frozen measurement.

Revision note, 2026-10-02 00:08Z: The user asked whether a few milliseconds are acceptable, then authorized defining separate budgets. Steady-state allowances are +2 ms median/+5 ms p95; no-provider-bytecode cold allowances are +5 ms median/+10 ms p95. The 500 ms measured finite-resource ceiling and all security/correctness obligations stay intact. Initial three-repeat cold evidence is descriptive only; collect 25 independent fresh copies for the cold p95 gate. Both frozen ordinary-cache pairs now retain 147 correct scenarios and zero positive median deltas, pending direct p95-budget review. The worker was interrupted before its deadline to answer the user and stop; its uncommitted tested checkpoint is preserved for original-node follow-up.
