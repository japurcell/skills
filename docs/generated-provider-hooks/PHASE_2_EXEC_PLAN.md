# Generate the RTK forwarders and fail installation on stale hooks

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds. Maintain this document in accordance with the repository-local `exec-plans` skill at `.agents/skills/exec-plans/SKILL.md`.

This plan follows the completed Phase 1 plan in `docs/generated-provider-hooks/EXEC_PLAN.md`. Phase 1 created the canonical `hooks/` source tree, the transactional `scripts/generate-hooks.py` command, and 20 checked-in provider-local outputs. This plan makes the final Phase 2 decisions concrete: the Copilot and Codex required-skill loaders remain independent, the Copilot and Gemini RTK forwarders become generated outputs, and both installers verify generated-hook freshness before changing any destination.

## Purpose / Big Picture

After this work, maintainers will change one canonical RTK hook family instead of manually synchronizing nearly identical Copilot and Gemini Python forwarders. Copilot will continue converting RTK's `permissionDecision: "ask"` response to `"allow"`; this is an intentional repository policy and must remain an explicit Copilot-only adapter. Gemini will continue forwarding RTK responses unchanged.

The RTK wrappers will stop waiting forever for end-of-file after receiving one complete JSON object. They will not impose input or output byte limits, reject RTK versions, or narrow RTK's output schema. The existing one-second RTK subprocess timeout remains, and Gemini's outer hook configuration gains a five-second timeout.

Installation will also become fail-fast. `scripts/install.sh` and `scripts/install.ps1` will run `scripts/generate-hooks.py --check` before the Codex agent converter, directory creation, copies, pruning, permission changes, or configuration merges. A stale generated output will stop the whole install and tell the user to run `python3 scripts/generate-hooks.py --write`. Invalid generator source will stop installation without suggesting a write. The preflight check will not write Python bytecode.

A maintainer can see the completed behavior by running the two RTK suites, both installer suites, the generator suite, and `python3 scripts/generate-hooks.py --check`. The final freshness message should report 22 files. A fixture install with one deliberately stale output should fail before its temporary home changes.

## Progress

- [x] (2026-09-17 20:40Z) [milestone-1] Strengthen RTK characterization without changing runtime behavior and record the required-skill-loader no-migration decision.
- [ ] [milestone-2] Fix RTK open-pipe completion and add the five-second Gemini outer timeout in an isolated behavior change.
- [ ] [milestone-3] Generate the two provider-local RTK forwarders from one canonical family while preserving every approved adapter difference.
- [ ] [milestone-4] Add read-only generated-hook freshness preflight to both installers before any destination mutation.
- [ ] [milestone-5] Run full validation, obtain focused review, synchronize documentation, and record final outcomes.

## Surprises & Discoveries

- Observation: The two required-skill loaders satisfy the two-output threshold but do not qualify as one generated family.
  Evidence: `.copilot/hooks/scripts/load-required-skills.py` and `.codex/hooks/load-required-skills.py` have only 30 exactly aligned lines across 394 combined lines, or 15.2 percent direct similarity. Copilot uses configurable environment paths, Copilot CLI and VS Code envelopes, progress objects, generated local helpers, and advisory failure context. Codex uses a fixed relative allowlist, strict containment and link checks, independent input and context limits, one fail-closed SessionStart envelope, and hardened audit storage. Their shared load-strip-wrap idea is smaller than the adapters and security boundaries a renderer would need.

- Observation: The RTK forwarders are a strong generation candidate.
  Evidence: `.copilot/hooks/scripts/rtk-hook-copilot.py` and `.gemini/hooks/scripts/rtk-hook-gemini.py` share 101 exactly aligned lines and have 92.2 percent measured similarity. Their material differences are the `rtk hook copilot` versus `rtk hook gemini` argument and diagnostic text, plus 13 Copilot-only lines that convert top-level and nested `permissionDecision: "ask"` values to `"allow"`.

- Observation: Copilot's `ask` to `allow` conversion is intended behavior, not a defect to repair during this effort.
  Evidence: `scripts/test-hooks-rtk.sh` already asserts both top-level and nested conversions, and the user explicitly confirmed that the conversion is the desired silent-rewrite policy. The canonical renderer must make this adapter visible and prevent it from leaking into Gemini.

- Observation: Fixed wrapper byte limits would create a second compatibility contract in front of RTK.
  Evidence: The installed RTK during planning was version 0.49.0 and its current input is bounded, but RTK publishes no stable cross-version response-size maximum. The user chose future RTK compatibility over new wrapper byte limits. The wrappers must therefore accept complete JSON without repository-defined input or output size ceilings.

- Observation: The current RTK wrappers can wait for end-of-file even after a complete JSON object is available.
  Evidence: Both wrappers call `sys.stdin.read()` before invoking RTK. Other repository hook readers use incremental JSON decoding and buffered-byte draining so a complete object can finish on an open pipe. The RTK-specific reader needs the same cross-platform property while preserving the accepted bytes passed to RTK.

- Observation: Installer tests use reduced fixture repositories rather than the live checkout.
  Evidence: `scripts/test-install.sh` and `scripts/test-install.ps1` currently copy the installers and selected Codex helpers but not `scripts/generate-hooks.py`, the canonical `hooks/` tree, `.github` generated targets, or every manifest-owned output. Adding a real freshness preflight requires each fixture to contain a complete fresh generator input/output set.

- Observation: A freshness check can create ignored `__pycache__` files unless bytecode is disabled.
  Evidence: `scripts/generate-hooks.py` imports `hooks.manifest`, `hooks.providers`, and each family module. Both installers must set `PYTHONDONTWRITEBYTECODE=1` only for the preflight subprocess so the check remains read-only in practical checkout state as well as provider output state.

- Observation: Preflight freshness is a check-time guarantee, not an installation transaction.
  Evidence: Another process can modify canonical or generated files after `--check` exits and before copying begins. Holding a repository lock through every installer copy or staging all rendered outputs would add a new transaction protocol. This plan intentionally accepts that race and makes no stronger claim.

- Observation: The handwritten RTK forwarders already implement the approved response boundary.
  Evidence: `bash scripts/test-hooks-rtk.sh` and `bash scripts/test-gemini-hooks-rtk.sh` both passed after adding public stdin/stdout characterization for malformed and non-object RTK output, missing executables, exact provider arguments, Copilot decision preservation and normalization, Gemini passthrough, and provider registration contracts.

## Decision Log

- Decision: Do not migrate the required-skill loaders into the generated-hook system.
  Rationale: The pair passes only the output-count and runtime-local-file tests. It fails the meaningful-shared-logic, adapter-size, and net-maintenance-reduction tests because its provider configuration and security contracts are intentionally different.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Migrate only the two RTK Python forwarders, not their provider configuration files.
  Rationale: The forwarders contain substantial shared implementation. `.copilot/hooks/rtk-rewrite.json` has dual Copilot event registrations, while `.gemini/global-settings.json` is a larger provider configuration with hook ordering and matcher semantics. Keeping configuration handwritten avoids widening generator ownership; focused tests will pin it instead.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Preserve Copilot's top-level and nested `ask` to `allow` conversion as an explicit adapter. Preserve Gemini output unchanged.
  Rationale: Silent Copilot RTK rewrites are desired repository policy. The difference must remain visible in canonical source and provider-level tests.
  Date/Author: 2026-09-17, user.

- Decision: Do not add RTK version checks, provider-output field allowlists, or wrapper input/output byte limits.
  Rationale: These restrictions could reject valid behavior from future RTK versions. The wrapper remains a thin compatibility layer: it verifies that input and output are JSON objects, applies the approved Copilot normalization, and otherwise defers to RTK.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Read one complete input JSON object without waiting for end-of-file, using a 0.5-second idle deadline only while an object remains incomplete.
  Rationale: This prevents an open pipe from hanging the wrapper. The reader forwards the accepted JSON bytes without reserialization and does not impose a size ceiling. Buffered trailing whitespace remains valid; buffered trailing non-whitespace remains invalid.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Keep the one-second RTK subprocess timeout and add `"timeout": 5000` to Gemini's RTK hook registration.
  Rationale: The subprocess timeout already defines current behavior. The outer timeout bounds wrapper-level stalls without changing successful calls. Gemini timeout values are milliseconds.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Both installers run `scripts/generate-hooks.py --check` before any destination mutation and never run `--write`.
  Rationale: Installations should never copy stale generated hooks, but must not modify repository sources. Stale output is an authoring error with an explicit recovery command.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Preserve generator exit classes through installer preflight.
  Rationale: Exit 1 means stale, missing, or undeclared generated output and should include the `--write` recovery command. Exit 2 means generator or canonical-source failure and must retain its diagnostic without advising a potentially invalid write. Both cases stop before destination changes.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Treat freshness as proof at check time; do not lock the repository through installation.
  Rationale: Cross-process locking or rendered staging would materially expand installer complexity for a small race in a local authoring workflow.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Use this new Phase 2 ExecPlan rather than reopening the completed Phase 1 milestones.
  Rationale: Phase 1 is accepted historical work. This plan records the later characterization, one approved migration, and installer policy as a separate restartable effort.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Keep the M1 tests as a behavior-only boundary before changing RTK runtime code.
  Rationale: The focused suites now prove the exact `rtk hook copilot` and `rtk hook gemini` calls, normal no-op failures, Copilot-only `ask` normalization, Gemini passthrough, and handwritten registration constraints. Subsequent open-pipe work must preserve these public observations.
  Date/Author: 2026-09-17, Codex.

## Outcomes & Retrospective

Planning and candidate characterization are complete. Milestone 1 added public JSON-seam characterization without changing either handwritten RTK runtime. The required-skill loaders are rejected as a generated family. The RTK forwarders are approved subject to the test-first open-pipe repair and exact adapter preservation described below. Installer freshness preflight is approved with distinct stale and generator-failure diagnostics.

At implementation completion, replace this paragraph with measured results: number of newly owned outputs, canonical renderer size, duplicate maintained lines removed, targeted and aggregate test results, review findings, installer stale-state proof, any unavailable platform checks, and whether a writable-home smoke test ran.

## Context and Orientation

Run every command in this plan from `/Users/adam/dev/skills` unless a step says otherwise. Prefix read-only shell commands and test commands with `rtk` as required by `AGENTS.md`. Do not prefix `python3 scripts/generate-hooks.py --write`, because write mode is the intended mutation and must not be converted into a check-only action.

A provider-local hook is a Python file executed from one provider's own directory. Copilot hooks live below `.copilot/hooks/`; Gemini hooks live below `.gemini/hooks/`; repository-local GitHub hooks live below `.github/hooks/`. Runtime-local files may import helpers within their own provider tree, but never import another provider's tree.

A canonical family is build-time Python source below `hooks/families/` with a `render(provider, target)` function. `scripts/generate-hooks.py` imports each family named in `hooks/manifest.py`, renders all declared outputs in memory, validates their headers and syntax, and either compares them with `--check` or replaces stale files transactionally with `--write`. Generated outputs carry a header naming their family and must remain mode `755`.

`hooks/providers.py` defines the three provider records. `hooks/manifest.py` currently declares 20 targets. This plan adds two `rtk` targets:

    GeneratedTarget("rtk", "copilot", PurePosixPath(".copilot/hooks/scripts/rtk-hook-copilot.py"))
    GeneratedTarget("rtk", "gemini", PurePosixPath(".gemini/hooks/scripts/rtk-hook-gemini.py"))

The two current handwritten forwarders parse hook JSON, record observability, locate `rtk` on `PATH`, call either `rtk hook copilot` or `rtk hook gemini` with `shell=False` and a one-second timeout, and emit a provider response. Errors are fail-open for command execution: they audit a bounded single-line reason, emit `{}`, and exit successfully so the original command can proceed. Empty successful RTK stdout is also a normal no-op.

Copilot has one deliberate extra transformation. If RTK returns `permissionDecision: "ask"` at the top level or inside `hookSpecificOutput`, `.copilot/hooks/scripts/rtk-hook-copilot.py` changes it to `"allow"` and audits the override. The generated family must retain both transformations. Gemini has no corresponding normalization.

`scripts/test-hooks-rtk.sh` and `scripts/test-gemini-hooks-rtk.sh` exercise the wrappers through their public stdin/stdout seams with a mock `rtk` executable. They are already registered in `scripts/test-all.py`. `scripts/test-generate-hooks.py` owns generator, ownership, parity, header, mode, and transaction coverage. Extend these existing suites instead of adding a new suite.

The installer entry points are `scripts/install.sh` and `scripts/install.ps1`. Their first current destination mutation is the Codex agent conversion: Bash invokes `scripts/install-codex-agents.py` at the current line 127, and PowerShell invokes it immediately after resolving Python near the current line 388. The new freshness preflight must run after required repository-source validation and Python discovery, but before those calls.

Installer fixture repositories are built by `create_fixture_repo` in `scripts/test-install.sh` and `New-FixtureRepo` in `scripts/test-install.ps1`. They redirect the child installer's home to a temporary directory. Do not repurpose the active agent process's `HOME`; keep redirection confined to the child fixture process.

## Plan of Work

### Milestone 1: Freeze RTK behavior and record Phase 2 admission
Status: done
Acceptance: met

Strengthen the focused RTK suites before changing runtime code. In `scripts/test-hooks-rtk.sh`, retain the existing two assertions that Copilot maps top-level and nested `ask` to `allow`. Add cases proving an omitted decision remains omitted, explicit `allow` remains `allow`, `deny` remains `deny`, empty RTK output remains a clean no-op, invalid or non-object RTK JSON becomes a no-op, a missing or failing RTK executable becomes a no-op, and the invoked argument vector remains exactly `rtk hook copilot`. Preserve the Windows executable-resolution case for `rtk.cmd` where the host can exercise it.

In `scripts/test-gemini-hooks-rtk.sh`, add matching cases for invalid and non-object RTK output, missing and failing RTK, and exact `rtk hook gemini` invocation. Prove that Gemini passes `allow`, `deny`, and `ask_user` decisions through without Copilot normalization. Expand configuration assertions: Copilot must retain both accepted case variants, Bash and PowerShell commands, `cwd: "."`, and its five-second outer timeout; Gemini must retain the `run_shell_command` matcher and its position after observability, Tool Guardian, and secret scanning.

Keep all new characterization tests green against the handwritten wrappers. Do not change runtime behavior in this milestone. Update the completed Phase 1 plan's Decision Log and Phase 2 recommendation to replace “characterize first” with the final pair-by-pair decisions, but do not reopen or add Phase 1 milestones. State that required-skill loaders are rejected and RTK forwarders are approved under this plan.

Acceptance is met when both focused suites pass before runtime edits, the approved Copilot conversion and Gemini passthrough are explicit, and the previous Phase 2 deferral is replaced by a concrete decision.

### Milestone 2: Repair open-pipe completion before extraction
Status: open
Acceptance: not met

Use test-driven development. First add public-process regressions to both RTK suites that launch each wrapper with a real pipe, write one complete UTF-8 JSON object, keep the pipe open, and require the wrapper to respond promptly. Add an incomplete-prefix case that completes within 0.5 seconds and succeeds, and a case that remains incomplete and returns the existing no-op within a bounded interval. Add exact-byte cases for compact JSON, multiline JSON, Unicode, and buffered trailing whitespace. Compare the mock RTK stdin bytes directly rather than normalizing them through `jq`. Buffered trailing non-whitespace must remain invalid and must not invoke RTK.

Prove that the wrapper adds no size ceiling by streaming a valid JSON object larger than 1 MiB through the test pipe and confirming that the mock RTK receives it. Construct the payload through Python or a file-backed pipe; do not place a multi-megabyte value in a shell argument or environment variable. Do not add a corresponding fixed maximum to production code.

Then change both handwritten forwarders with the smallest parallel implementation. Read stdin incrementally as bytes, decode UTF-8 incrementally only to detect one complete JSON object, drain bytes already buffered after completion, and forward the accepted bytes to RTK without JSON reserialization. Use `select` on POSIX and `PeekNamedPipe` on Windows versions where ordinary nonblocking pipe reads are unavailable. While JSON is incomplete, wait no more than `INPUT_COMPLETION_IDLE_SECONDS = 0.5` for another byte. Do not add input or output byte-count constants. Continue requiring the parsed input to be a JSON object.

Keep the existing one-second subprocess timeout, `shell=False`, empty-output handling, audit behavior, Copilot normalization, and Gemini passthrough. Add `"timeout": 5000` to the handwritten RTK entry in `.gemini/global-settings.json` and assert it in the Gemini suite. The timeout value is milliseconds. Do not add an RTK version check.

Run both focused suites and the relevant startup/observability suites because each wrapper invokes provider-local observability and audit helpers. Keep this behavior repair isolated from generated ownership so its diff and tests can be reviewed separately.

Acceptance is met when complete JSON on an open pipe returns, incomplete JSON stops within the defined idle window, a payload larger than 1 MiB reaches mock RTK, accepted bytes remain unchanged, every established provider response remains unchanged, and Gemini configuration has the five-second outer timeout.

### Milestone 3: Generate the RTK family
Status: open
Acceptance: not met

Create `hooks/families/rtk.py`. Follow existing family structure: define the shebang and generated ownership header, keep shared runtime code in one canonical body, and isolate provider differences in small explicit adapter data or renderer blocks. The `render(provider, target)` function must reject provider/target mismatches and unsupported providers. Do not add RTK-specific fields to the global `Provider` dataclass unless the implementation proves they serve more than this one family; a family-local adapter is clearer for two outputs.

The canonical body must include the open-pipe reader established in Milestone 2, RTK discovery through `shutil.which`, subprocess invocation with an argument list and `shell=False`, one-second timeout, JSON-object validation, no-op fallback, provider-local helper imports, and observability capture. The Copilot adapter owns both `ask` to `allow` transformations and their audit messages. The Gemini adapter contains no permission normalization. Neither adapter contains version checks, response field allowlists, or byte limits.

Add the two manifest entries shown in Context and Orientation. Extend `scripts/test-generate-hooks.py` with an `RTK_TARGETS` group and family-specific assertions. Require both outputs to have the correct header and executable mode, import only their own provider-local helpers, invoke the correct RTK provider argument, and differ only at declared adapter sites after the common generated body is normalized. Pin the Copilot-only permission normalization and prove that no equivalent code appears in Gemini. Preserve the Milestone 2 open-pipe and large-input cases in the provider suites; generator tests complement but do not replace public runtime tests.

Run `python3 scripts/generate-hooks.py --write` once after the canonical family and manifest are ready. Review both generated diffs. Remove any hand-edited-only structure that the renderer did not reproduce. Run `python3 scripts/generate-hooks.py --check` and expect:

    Generated hooks are current (22 files).

Acceptance is met when both RTK files carry generated ownership headers, all 22 outputs are current and executable, no cross-provider runtime import exists, both focused RTK suites pass unchanged, and the generator suite proves only the approved adapters differ.

### Milestone 4: Fail installation before copying stale generated hooks
Status: open
Acceptance: not met

In `scripts/install.sh`, define an absolute repository path for `scripts/generate-hooks.py`. Treat the generator file and canonical `hooks/` directory as required sources. After all required-source checks and before `scripts/install-codex-agents.py`, invoke:

    PYTHONDONTWRITEBYTECODE=1 python3 "$GENERATE_HOOKS" --check

Run the command as an `if` condition so `set -e` does not erase its exit class. On exit 1, retain the generator's stale path output, write a concise stderr instruction to run `python3 scripts/generate-hooks.py --write`, and exit 1. On exit 2, retain the generator diagnostic, write a generic freshness-preflight failure, do not recommend `--write`, and exit 2. No `mkdir`, converter, copy, prune, permission, or merge operation may precede this check.

In `scripts/install.ps1`, define `$GenerateHooksSrc`, include it and the canonical `hooks` directory in source validation, resolve Python with the existing `Get-PythonCommand`, and invoke the same `--check` command before the Codex converter. Temporarily set process-level `PYTHONDONTWRITEBYTECODE=1` around only the preflight call and restore its previous state in `finally`. Preserve exit 1 versus exit 2 and use the same recovery policy as Bash. Do not route these failures through a helper that always collapses them to exit 1.

Expand both installer fixture builders with a fresh generator environment: copy `scripts/generate-hooks.py`, the complete canonical `hooks/` package, and every output declared by `hooks.manifest.targets()` with its executable mode and parent directory. Derive the owned output list from the manifest rather than maintaining a second handwritten 22-path list in each suite. Exclude existing `__pycache__` directories from the fixture.

Add paired Bash and PowerShell tests for three states. A fresh fixture installs normally and does not create `__pycache__`. A fixture with one corrupted generated RTK output exits 1, names the stale repository-relative path, prints the `--write` recovery command, and leaves a pre-populated temporary destination tree byte-for-byte unchanged with no new destination directories. A fixture whose manifest names an unknown provider or otherwise triggers a controlled generator error exits 2, retains the generator diagnostic, omits the `--write` advice, and also leaves destinations unchanged.

Do not add repository locking or claim snapshot isolation. The acceptance statement is: files already stale when preflight runs cannot cause a partial install. Later failures and concurrent source changes remain outside that guarantee.

Acceptance is met when syntax checks and both installer suites pass, both failure classes stop before all destination mutation, a fresh install still copies the 22 current outputs, and preflight creates no bytecode cache.

### Milestone 5: Validate, review, and synchronize durable documentation
Status: open
Acceptance: not met

Run generator freshness before and after the full maintained suite and confirm neither check changes `git status`. Run the two RTK suites, generator tests, shell syntax and installer tests, PowerShell installer tests, relevant startup and observability suites, and finally `python3 scripts/test-all.py`. If the environment cannot run PowerShell or a real-home smoke test, record that limitation precisely and keep fixture evidence distinct from deployed evidence.

Request focused code review of the canonical RTK family, generated outputs, open-pipe reader, explicit Copilot normalization, Gemini passthrough, and installer preflight ordering. Tell the reviewer that `ask` to `allow` is approved policy and is not an authorization finding for this task. Security review should instead look for adapter leakage, shell invocation, malformed-input fail-open behavior, unbounded waiting, raw diagnostic leakage, cross-provider imports, and installer mutation before freshness proof.

Update `README.md` so installation states that installers run a read-only freshness preflight, never generate sources, and stop with the write command when outputs are stale. Update `docs/adr/0004-generated-provider-hooks.md` to clarify that “copy-only” forbids `--write` but permits `--check` before copying. Update `docs/generated-provider-hooks/EXEC_PLAN.md` with the final Phase 2 disposition without reopening Phase 1. Synchronize `.agents/memory/ARCHITECTURE.md`, `.agents/instructions/scripts.md`, `.agents/instructions/hooks.md`, `.agents/memory/testing/scripts.md`, `.agents/memory/testing/powershell.md`, `.agents/memory/testing/hooks.md`, and any API or file maps whose described interfaces changed.

Run the `update-agent-docs` skill once after all implementation and delegated reviews finish. Then run `okf-authoring` over changed Markdown under `.agents/instructions/` and `.agents/memory/`. Update this plan's Progress, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective with exact commands, results, review corrections, metrics, and remaining limitations before ending the work session.

Acceptance is met when all available maintained suites and focused reviews pass, both freshness checks report 22 current files, documentation describes the final behavior without contradiction, `git diff --check` passes, and this living plan matches actual repository state.

## Concrete Steps

Run from `/Users/adam/dev/skills`. Begin every milestone by checking current state:

    rtk git status --short --branch
    rtk git diff --check
    rtk python3 scripts/generate-hooks.py --check

For Milestone 1, run the existing characterization baseline before editing tests:

    rtk test bash scripts/test-hooks-rtk.sh
    rtk test bash scripts/test-gemini-hooks-rtk.sh

After adding characterization tests, run the same commands and expect both scripts to exit 0. Commit or otherwise preserve this test-only boundary before changing runtime code.

For Milestone 2, add failing open-pipe tests first. Run each focused suite to observe the timeout failure against `sys.stdin.read()`, then implement the repair and rerun:

    rtk test bash scripts/test-hooks-rtk.sh
    rtk test bash scripts/test-gemini-hooks-rtk.sh
    rtk test bash scripts/test-hooks-startup.sh
    rtk test bash scripts/test-hooks-observability.sh
    rtk test bash scripts/test-gemini-hooks-observability.sh

For Milestone 3, mutate generated files only through write mode:

    python3 scripts/generate-hooks.py --write
    rtk python3 scripts/generate-hooks.py --check
    rtk test python3 scripts/test-generate-hooks.py
    rtk test bash scripts/test-hooks-rtk.sh
    rtk test bash scripts/test-gemini-hooks-rtk.sh

The freshness output must be:

    Generated hooks are current (22 files).

For Milestone 4, run syntax and fixture coverage:

    rtk bash -n scripts/install.sh
    rtk test bash scripts/test-install.sh
    rtk test pwsh -NoProfile -File scripts/test-install.ps1

If `rtk test` cannot express a command correctly, use `rtk summary` or `rtk err` without changing command semantics. Do not silently fall back to an untracked raw command. Formatting commands that intentionally mutate files are exceptions and must run directly.

For Milestone 5, run focused validation, then the aggregate suite:

    rtk python3 scripts/generate-hooks.py --check
    rtk test bash scripts/test-hooks-rtk.sh
    rtk test bash scripts/test-gemini-hooks-rtk.sh
    rtk test python3 scripts/test-generate-hooks.py
    rtk test bash scripts/test-install.sh
    rtk test pwsh -NoProfile -File scripts/test-install.ps1
    rtk test python3 scripts/test-all.py
    rtk python3 scripts/generate-hooks.py --check
    rtk git diff --check
    rtk git status --short

`scripts/test-all.py` already registers both RTK suites, generator tests, and both installer suites. Do not add duplicate aggregate entries. Record the actual passed-suite count because it may increase independently of this plan.

## Validation and Acceptance

The required-skill-loader decision is accepted when no loader enters `hooks/manifest.py`, no `hooks/families/required_skills.py` is created, and the completed Phase 1 plan records the evidence-backed no-migration decision.

The RTK behavior repair is accepted when a complete object on an open pipe returns promptly, an incomplete object has a 0.5-second idle bound, valid JSON larger than 1 MiB reaches RTK, accepted bytes are not reserialized, Copilot still maps both `ask` locations to `allow`, Gemini still passes decisions through unchanged, and all errors still degrade to `{}` with exit 0.

The generation migration is accepted when humans edit `hooks/families/rtk.py`, not provider outputs; `hooks/manifest.py` owns exactly two new targets; both generated files remain executable and runtime-local; generator and provider suites prove only declared adapters differ; and `--check` reports 22 current files.

The installer change is accepted when a stale output or controlled generator failure stops before any destination mutation in Bash and PowerShell fixtures. Stale state must include the exact write recovery command. Generator failure must not include it. Fresh install behavior, file modes, link handling, Codex conversion, configuration merging, and existing unrelated destination preservation must remain green.

The whole effort is accepted when `python3 scripts/test-all.py` passes every available maintained suite, focused review finds no unresolved high-confidence blocker, documentation agrees that installers check but never write generated source, and the worktree contains no unexpected generated drift or bytecode caches.

## Idempotence and Recovery

Characterization and `--check` commands are read-only and safe to repeat. The open-pipe changes are ordinary source edits and can be retried through their focused tests.

`python3 scripts/generate-hooks.py --write` is transactional. It stages every stale output, replaces declared targets, and rolls back replacements on an injected or real write failure. If interrupted, rerun `--write`, then `--check`; never repair generated RTK files by hand.

Installer freshness preflight is read-only and occurs before destination changes. If it reports stale paths, run `python3 scripts/generate-hooks.py --write` from the repository root, review the generated diff, run `--check`, and retry installation. If it exits 2, repair the named canonical source or unsafe path first; do not assume `--write` is safe.

The preflight does not protect against another process changing repository files after the check. If concurrent authoring is suspected, stop the other writer, rerun `--check`, and restart installation. Do not add ad hoc lock deletion or bypass flags.

Installer tests may create only temporary fixture repositories and homes. Their cleanup must remain trap/finally based. Never point fixture cleanup at the repository root, the active home directory, or an unresolved environment variable.

## Artifacts and Notes

The final normal authoring transcript should contain:

    $ python3 scripts/generate-hooks.py --write
    .copilot/hooks/scripts/rtk-hook-copilot.py
    .gemini/hooks/scripts/rtk-hook-gemini.py

    $ python3 scripts/generate-hooks.py --check
    Generated hooks are current (22 files).

If only unchanged outputs exist, write mode may instead report that all 22 files are already current.

The final stale installer fixture should prove behavior equivalent to:

    .copilot/hooks/scripts/rtk-hook-copilot.py
    Generated hooks are stale. Run: python3 scripts/generate-hooks.py --write

The exact first line comes from the generator on stdout. The recovery instruction belongs on stderr. No installation success message may follow.

The final controlled generator-failure fixture should show a safe generator diagnostic and a generic preflight failure, with no `--write` instruction.

## Interfaces and Dependencies

Do not add third-party dependencies. Use Python's standard library, existing Bash and PowerShell facilities, and existing repository helpers.

In `hooks/families/rtk.py`, provide:

    def render(provider: Provider, target: GeneratedTarget) -> str:
        """Render one provider-local RTK forwarder."""

The renderer must accept only the Copilot and Gemini targets declared in `hooks/manifest.py`. It must return a complete UTF-8 Python script beginning with `#!/usr/bin/env python3`, followed by the generated ownership header expected by `scripts/generate-hooks.py`, and ending with one newline.

The generated runtime interface remains stdin/stdout JSON. Input must be one UTF-8 JSON object. Successful non-empty RTK stdout must be one JSON object. The wrapper invokes an executable resolved through `shutil.which("rtk")` when possible, using one of these exact argument lists:

    [rtk_bin, "hook", "copilot"]
    [rtk_bin, "hook", "gemini"]

No shell string execution is allowed. The subprocess timeout remains `1.0` seconds. Invalid input, missing RTK, subprocess error, timeout, nonzero exit, malformed output, or non-object output logs a sanitized fallback reason and emits `{}`. Empty successful output emits `{}` without an error audit.

The Copilot adapter changes string values equal to `ask`, ignoring surrounding whitespace and case exactly as current code does, to `allow` at top-level `permissionDecision` and nested `hookSpecificOutput.permissionDecision`. It audits each override. The Gemini adapter returns the parsed object unchanged.

In `.gemini/global-settings.json`, the existing RTK command registration keeps its matcher and command and adds:

    "timeout": 5000

In the installers, generated-hook preflight is a required phase with no public opt-out. It consumes the generator's existing exit codes rather than defining new ones. It must execute before every destination mutation and with Python bytecode disabled.

Revision note, 2026-09-17: Initial Phase 2 ExecPlan created after candidate characterization and a user-confirmed design-tree review. It rejects required-skill-loader generation, approves RTK generation with intentional Copilot normalization and no byte limits or version pin, and specifies fail-fast installer freshness checks before destination mutation.

Revision note, 2026-09-17: Completed Milestone 1. The focused Copilot and Gemini RTK suites now characterize malformed and non-object RTK output, missing executables, exact provider argument vectors, decision behavior, and handwritten registration order/configuration. Both suites passed without changing runtime code.
