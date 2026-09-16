# Repair OKF Migration Review Defects

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must stay current as work proceeds. Maintain this document according to `.agents/skills/exec-plans/SKILL.md`. No repository-level `PLANS.md` exists.

This repair builds on the completed migration recorded in `docs/okf-kb-migration/implementation-execplan.md` and its five authoritative contracts under `docs/okf-kb-migration/tickets/`. Those checked-in documents remain historical context; this plan owns the new corrective work and must not rewrite the original acceptance record.

## Purpose / Big Picture

After this work, OKF validation will behave reliably at every public boundary found defective during final review. Copilot stop validation will finish after one complete JSON payload even when the host keeps stdin open, emit UTF-8 JSON on Windows, preserve source-ingest and OKF blocking reasons in their required order, and keep the complete serialized response below 8 KiB. Copilot diagnostic messages will always report the omitted count. The central linter will reject Windows absolute paths, allow source-summary footnotes, and apply Markdown comment and code-span masking correctly.

A human can see the repair working by running the public linter and provider contract suites. New regressions must fail against the current implementation before each production change, then pass after the minimal fix. The final matrix must leave the canonical corpus clean, print the exact empty JSON diagnostics envelope, and leave the Git worktree free of generated changes.

## Progress

- [x] (2026-09-16) [milestone-0] Reconciled eight review findings, identified their public test seams, and authored this repair plan.
- [x] (2026-09-16) [milestone-1] Added red Copilot regressions for open stdin, UTF-8 output, and oversized combined stop reasons.
- [x] (2026-09-16) [milestone-1] Made the repository-local Copilot reader and stop coordinator pass those regressions without changing provider envelope shapes or reason ordering.
- [x] (2026-09-16) [milestone-1] Added and satisfied review follow-up coverage for malformed or incomplete JSON on an open stdin pipe.
- [x] (2026-09-16) [milestone-2] Added red Copilot adapter regressions for zero omitted diagnostics and `OKF900` omitted-count reporting.
- [x] (2026-09-16) [milestone-2] Made every Copilot failure response include the omitted count while preserving the 20-diagnostic and 8 KiB limits.
- [x] (2026-09-16) [milestone-2] Preserved the real normalized diagnostic count when central lint exits `2` with `OKF900`.
- [x] (2026-09-16) [milestone-2] Preserved the real normalized diagnostic count when central lint returns diagnostics with an inconsistent exit `0`.
- [x] (2026-09-16) [milestone-3] Added and satisfied one public-CLI regression at a time for Windows absolute paths, footnotes, unclosed HTML comments, and exact backtick-run matching.
- [x] (2026-09-16) [milestone-3] Made HTML comment and code masking precedence-aware so comment markers inside code cannot hide later links.
- [x] (2026-09-16) [milestone-3] Made masking precedence fully left-to-right so code delimiters inside comments cannot hide later links.
- [x] (2026-09-16) [milestone-4] Added `--` to all 15 recursive cleanup commands in the Gemini OKF hook suite while retaining its area-specific dynamic `RETURN` traps.
- [x] (2026-09-16) [milestone-4] Ran the complete static matrix, resolved all independent code-review findings, completed the mandatory `update-agent-docs` and OKF representation passes, and recorded final outcomes.

## Surprises & Discoveries

- Observation: The repository-local Copilot helper still reads stdin with `sys.stdin.read()`, while the Gemini and installed Copilot helpers already contain incremental complete-JSON readers.
  Evidence: `.github/hooks/scripts/helpers/common.py` blocks until EOF; an open-pipe probe remained alive after receiving a complete JSON object. `.gemini/hooks/scripts/helpers/common.py` already uses `JSONDecoder.raw_decode`, buffered-byte draining, and `PeekNamedPipe` on Windows.
- Observation: Individually bounded validator responses do not imply a bounded coordinator response.
  Evidence: Concatenating a 7,741-byte OKF reason with a normal pending-ingest reason produced an 8,329-byte serialized stop response, above the strict 8,192-byte provider limit.
- Observation: The reference-definition scanner cannot currently distinguish link definitions from footnote definitions.
  Evidence: `[^claim]: Upstream documentation supports this claim.` produces `OKF103` for a nonexistent path named `Upstream`.
- Observation: Two documented cleanup rules conflict if read without path scope.
  Evidence: `.agents/instructions/scripts.md` prefers named cleanup functions, while the more specific `.agents/memory/testing/hooks.md` requires dynamically captured `RETURN` traps under `set -u`. The valid defect is missing `--` on recursive removal, not the area-approved trap shape.
- Observation: A complete-value reader also needs a bounded incomplete-value path when the writer keeps stdin open.
  Evidence: Independent review left stdin open after `{` and `{not json`; both public Copilot entry points remained alive instead of returning a provider-valid block response.
- Observation: Raising after normalizing an exit-`2` linter response discards the diagnostic count needed by the adapter summary.
  Evidence: A malformed-manifest probe returned one central `OKF900`, while the adapter reported `0 additional diagnostics omitted.`.
- Observation: Masking unclosed HTML comments before code regions gives comment markers inside code precedence over later Markdown.
  Evidence: An unclosed `<!--` inside a closed fence or matching code span hid a real missing link after that code region.
- Observation: Applying all code masking before all comment masking only reverses the precedence defect.
  Evidence: A fence or backtick inside an HTML comment paired with a delimiter after the comment and hid a later real missing link.
- Observation: Every failure after diagnostic normalization must carry those diagnostics, regardless of central exit status.
  Evidence: One valid diagnostic paired with exit `0` raised a plain `ValueError`, so the adapter incorrectly reported zero omitted.

## Decision Log

- Decision: Test only existing public seams: `./scripts/lint-okf.py`, `.github/hooks/scripts/lint-okf.py`, and the registered `.github/hooks/scripts/validate-stop.py` entry point.
  Rationale: These are the consumer-visible contracts. Tests against private helpers would couple the suite to implementation structure and violate the repository's TDD guidance.
  Date/Author: 2026-09-16 / Codex
- Decision: Port the proven incremental JSON reader into `.github/hooks/scripts/helpers/common.py`, then make the coordinator use `read_json_input` and `emit_json` from that helper.
  Rationale: One shared repository-local boundary fixes both the direct Copilot OKF adapter and the registered stop coordinator. Reimplementing pipe handling inside the coordinator would create a second reader and invite drift.
  Date/Author: 2026-09-16 / Codex
- Decision: Parse one payload in the coordinator and serialize that mapping once for both child validators.
  Rationale: Parsing at the public boundary rejects malformed or buffered trailing input deterministically. Both child validators still run as separate processes with unchanged responsibilities.
  Date/Author: 2026-09-16 / Codex
- Decision: Bound the final coordinator JSON, not only each child reason, and preserve a recognizable prefix from both reasons in source-ingest-first order.
  Rationale: The provider limit applies to the registered hook response. Truncation must never erase one independent blocker or reverse their ordering.
  Date/Author: 2026-09-16 / Codex
- Decision: Preserve every existing provider envelope and linter JSON field.
  Rationale: These are public interfaces documented in `.agents/memory/API_MAP.md`. The repair changes reliability and conformance only; it adds no version, field, event, matcher, or exit-code behavior.
  Date/Author: 2026-09-16 / Codex
- Decision: Reject Windows drive-rooted and UNC destinations before URI-scheme acceptance.
  Rationale: `urlsplit` treats a drive letter as a URI scheme. Filesystem absoluteness must therefore be checked first, independent of the host operating system.
  Date/Author: 2026-09-16 / Codex
- Decision: Treat `[^label]:` as a footnote definition, not a Markdown link definition.
  Rationale: The in-place OKF document contract explicitly permits per-claim footnotes. Ordinary `[label]: destination` definitions remain validated.
  Date/Author: 2026-09-16 / Codex
- Decision: Retain dynamic function-level cleanup traps in `scripts/test-gemini-hooks-okf-lint.sh`, but add `--` to every recursive removal command.
  Rationale: Area-specific hook testing guidance overrides the generic named-trap preference for `RETURN` traps under `set -u`. Exact-path quoting plus `--` resolves the valid safety gap.
  Date/Author: 2026-09-16 / Codex
- Decision: Treat all three independent-review findings as required acceptance defects and reopen their owning milestones.
  Rationale: Each finding violates an explicit public-boundary guarantee in this plan despite the initial green matrix.
  Date/Author: 2026-09-16 / Codex

## Outcomes & Retrospective

All planned public-boundary repairs are complete. Copilot adapters now finish on complete, malformed, or incomplete open-pipe input within a bounded interval, emit UTF-8 JSON, keep the final combined stop response below 8 KiB with both ordered blocker prefixes, and report accurate omitted-diagnostic counts across normal and inconsistent central-linter outcomes. The central linter now rejects Windows absolute destinations, permits source-summary footnotes, and masks comments, fences, and exact-run inline code with left-to-right precedence. Gemini test cleanup now uses `rm -rf --` without changing its approved dynamic traps.

The complete static matrix passes, canonical human lint is silent, canonical JSON lint is exactly `{"schema_version":1,"diagnostics":[]}`, and independent Premium rereview approved the final diff with no remaining findings. No provider-native session was required by this repair plan. Implementation stayed within the named public interfaces and test seams; four focused `.agents/memory/` files were synchronized with the repaired contracts and regressions.

## Context and Orientation

OKF is this repository's profile for canonical Markdown under `.agents/instructions/` and `.agents/memory/`. `scripts/lint-okf.py` is the only profile authority. It emits human diagnostics as `path:line:column: ID message` or JSON as `{"schema_version":1,"diagnostics":[...]}`. Exit `0` means clean, exit `1` means conformance findings, and exit `2` means an untrustworthy `OKF900` failure.

Provider adapters translate central diagnostics without owning document rules. `.github/hooks/scripts/lint-okf.py` serves repository-local Copilot `postToolUse` events and is also called by the final stop coordinator. `.gemini/hooks/scripts/lint-okf.py` serves Gemini. `.github/hooks/scripts/validate-stop.py` is the registered Copilot `agentStop` and `subagentStop` command. It runs `.github/hooks/scripts/inject-auto-ingest-context.py` first and `.github/hooks/scripts/lint-okf.py` second, then emits one allow or block decision.

An open stdin pipe is a pipe containing one complete JSON value whose writer has not closed its end. Hook readers must return after that complete value rather than wait for end-of-file. They must also drain bytes already buffered after the value and reject non-whitespace trailing data. On Windows before Python 3.12, pipe availability must use `PeekNamedPipe`; `os.set_blocking` is not portable there.

The 8 KiB limit means the final compact JSON document encoded as UTF-8 must contain fewer than 8,192 bytes. Measuring raw reason text is insufficient because JSON escaping adds bytes. The combined stop response must retain the pending-ingest reason before the independent OKF reason. If truncation is required, both reason prefixes and an explicit truncation marker must remain.

The central linter's destination scanner lives in `destination_diagnostics`, `reference_destinations`, and `ignored_ranges` inside `scripts/lint-okf.py`. Windows paths such as `C:/secrets.txt`, `C:\secrets.txt`, and `\\server\share\file.txt` are filesystem-absolute even on a POSIX host. A footnote definition has the form `[^claim]: explanatory body`; unlike `[target]: file.md`, its body is not a link destination. Markdown code spans close only on a backtick run of the same length as the opener. An HTML comment opened with `<!--` masks through `-->`, or through end-of-file when no closer exists.

Tests live at the existing public seams. `scripts/test-okf-lint.sh` exercises the CLI against copied fixture repositories. `scripts/test-hooks-okf-lint.sh` exercises the direct Copilot adapter and the registered stop command. `scripts/test-gemini-hooks-okf-lint.sh` exercises Gemini and contains the cleanup commands called out by review. Do not add dependencies, alter vendored PyYAML, modify immutable `.agents/sources/`, or add provider-specific document rules.

The review produced eight actionable behaviors. Seven require production changes; cleanup requires a test-only edit. The cleanup finding is valid only for missing `--`; the dynamic trap style is intentional under the more specific hook-testing guidance. Two smell candidates from the review are not work items: provider adapters must stay separate by repository rule, and the benchmark grader intentionally checks path-derived types independently to avoid trusting production code under test.

## Plan of Work

### Milestone 1: Harden the Copilot input and final-response boundary

Status: done
Acceptance: met

Start in `scripts/test-hooks-okf-lint.sh`. Extend the Python contract harness so it can launch a hook with `subprocess.Popen`, write one complete JSON object, flush without closing stdin, and require the process to exit within a short bound below the configured 10-second provider timeout. Exercise both `.github/hooks/scripts/lint-okf.py` and the registered `.github/hooks/scripts/validate-stop.py`. The tests must fail on the current blocking readers. Close or kill the child during test cleanup so a red run never leaves a process behind.

Add a Windows-encoding regression at the registered stop seam. Run the copied coordinator with `PYTHONIOENCODING=cp1252`, create a blocking reason containing a character outside CP1252, capture stdout as bytes, decode it as UTF-8, and parse one JSON object. The current `sys.stdout.write(... ensure_ascii=False)` path must fail before the production edit; the repaired path must emit valid UTF-8 JSON with exit `0`.

Add a combined-size regression while preserving the existing real simultaneous-failure integration case. At the same registered seam, arrange two child block responses whose individual JSON documents are below 8,192 bytes but whose naive concatenation exceeds that limit. Require the coordinator's complete compact UTF-8 JSON to be below 8,192 bytes, contain recognizable source-ingest and OKF prefixes in that order, and state that truncation occurred. This test may replace the copied validator entry points with deterministic test programs because the existing adjacent case continues to prove integration with both real validators.

After observing each red failure, update `.github/hooks/scripts/helpers/common.py`. Port the incremental `_read_available_stdin_bytes` and `_read_json_input_text` structure already used by `.gemini/hooks/scripts/helpers/common.py`, without importing across provider trees or adding observability behavior that the repository-local surface does not own. Keep `read_json_input()` returning one mapping and rejecting malformed JSON, non-object JSON, invalid UTF-8, and buffered non-whitespace trailing data.

Then update `.github/hooks/scripts/validate-stop.py`. Import `read_json_input` and `emit_json` from the repository-local helper. Parse once, compactly serialize the mapping for both child processes, run validators in the existing source-ingest-first order, and emit through `emit_json`. Add small pure helpers for compact serialized size, UTF-8-safe truncation, and bounded combined block construction. Keep the final JSON strictly below 8,192 bytes. Preserve `{"decision":"allow"}` only when both validators allow, and preserve `{"decision":"block","reason":"..."}` for all failure paths.

Finish the milestone by rerunning `scripts/test-hooks-okf-lint.sh`, `scripts/test-hooks-auto-ingest.sh`, `scripts/test-hooks-startup.sh`, and `scripts/test_helpers.py`. Acceptance is met only when open-pipe tests complete without stdin closure, the CP1252 simulation yields UTF-8 JSON, the oversized combined response stays below 8 KiB with both ordered reasons, and existing envelope/integration cases remain green.

### Milestone 2: Make Copilot diagnostic summaries contract-complete

Status: done
Acceptance: met

In `scripts/test-hooks-okf-lint.sh`, add one red assertion for a normal failure with no omitted diagnostics and one for a synthetic `OKF900` failure. Both must require the literal line `0 additional diagnostics omitted.`. Keep the existing 25-diagnostic case and require `5 additional diagnostics omitted.` so the change cannot hard-code zero.

Update `.github/hooks/scripts/lint-okf.py` only after the red tests fail. Make `_format_diagnostics` always append the omitted-count line, including zero. Make every `OKF900` reason and the emergency size fallback include an accurate count when known and zero when no normalized diagnostic list exists. Continue measuring the final serialized provider envelope, showing no more than 20 sorted findings, using the platform-specific rerun command, and exiting `0`.

Acceptance is met when direct post-tool and stop envelopes still match their existing shapes, zero and nonzero omitted counts are present, every response is below 8,192 bytes, and both provider OKF suites remain green. Gemini production code should not change because it already includes the count.

### Milestone 3: Correct path and Markdown interpretation in the central linter

Status: done
Acceptance: met

Work in four vertical red-green slices inside `scripts/test-okf-lint.sh` and `scripts/lint-okf.py`. Run the public CLI case after each test addition and record the short expected red result in `Artifacts and Notes` before implementing that slice.

First, add fixture cases for `C:/secrets.txt`, `C:\secrets.txt`, and a UNC destination. Each must yield `OKF102` at the destination location on every host. Add a host-independent filesystem-absolute predicate using `pathlib.PureWindowsPath` or an equivalently explicit drive/UNC check, and call it before accepting `urlsplit(...).scheme` as external. Keep valid external schemes allowed.

Second, add a conforming source-summary body containing `[^claim]: Upstream documentation supports this claim.` and require clean lint. Keep an ordinary missing reference definition failing with `OKF103`. Change `reference_destinations` to skip only the exact footnote-definition label form beginning with `^`; do not disable ordinary reference definitions.

Third, add an unclosed HTML comment containing an apparent missing link and require clean lint through end-of-file. Extend comment masking so `<!--` without `-->` masks to end-of-file while preserving every newline and character offset with spaces.

Fourth, add one case where a single-backtick opener is followed only by a double-backtick run around an apparent missing link; the link must remain visible to validation and produce `OKF103`. Retain or add a matching-run case that remains masked and clean. Change the inline-code scanner to accept a closing run only when its length exactly matches the opener and it is not a substring of a longer run.

Do not replace the deterministic Markdown scanner with a general parser or new dependency. Acceptance is met when all new cases pass through `./scripts/lint-okf.py`, existing balanced-link, escaped-destination, fence, location, metadata, provenance, and diagnostic-order cases remain green, and the real canonical corpus stays clean in both output modes.

### Milestone 4: Normalize test cleanup, synchronize knowledge, and close the repair

Status: done
Acceptance: met

In `scripts/test-gemini-hooks-okf-lint.sh`, add `--` to every `rm -rf` invocation, including copied-repository replacement, function-level `RETURN` cleanup, and vendor-removal cases. Retain exact quoting and the area-approved dynamic trap form so `set -u` does not evaluate an out-of-scope local variable. Run `bash -n` and the complete Gemini OKF hook suite after the mechanical edit.

Run the full validation matrix from the repository root. Then activate `addy-code-review-and-quality` and review the complete repair diff before merge. Required review focuses are public envelope stability, process cleanup in open-pipe tests, byte measurement after JSON encoding, UTF-8-safe truncation, exact diagnostic locations, and absence of provider-rule duplication in the central linter.

End the work session with the mandatory `update-agent-docs` skill. At minimum, inspect `.agents/memory/API_MAP.md`, `.agents/memory/testing/hooks.md`, `.agents/memory/testing/scripts.md`, and `.agents/memory/known-issues/scripts.md`. Record the repaired coordinator guarantees and new regressions where they add durable knowledge. Do not add or rename memory files unless necessary. If canonical `.agents/instructions/` or `.agents/memory/` Markdown changes, apply `.agents/skills/okf-authoring/SKILL.md`, load its shared profile and only the source-summary branch if a source summary changed, run full OKF lint, and verify the scoped canonical diff.

Update `docs/okf-kb-migration/handoff.md` only during implementation closure. Keep the completed migration history intact, link this repair plan, record tests and review results, and set the next step to no action only after all acceptance conditions pass. Finally synchronize every checkbox, milestone status, discovery, decision, and retrospective entry in this plan before stopping.

## Concrete Steps

Run all commands from `/Users/adam/dev/skills`, or from the root printed by `rtk git rev-parse --show-toplevel` in another checkout. Prefix shell commands with `rtk` as required by repository instructions.

Before editing, confirm a clean starting point:

    rtk git status --short
    rtk proxy ./scripts/lint-okf.py --format json

Expected JSON before and after the repair:

    {"schema_version":1,"diagnostics":[]}

For each production behavior, edit the named public test first, run its narrow suite, and preserve the decisive red assertion in this plan. Use `apply_patch` for repository edits. Run the affected suite again after the minimal production change.

Milestone 1 narrow checks:

    rtk test bash -n scripts/test-hooks-okf-lint.sh
    rtk test bash scripts/test-hooks-okf-lint.sh
    rtk test bash scripts/test-hooks-auto-ingest.sh
    rtk test bash scripts/test-hooks-startup.sh
    rtk test python3 scripts/test_helpers.py

Milestone 2 narrow checks:

    rtk test bash scripts/test-hooks-okf-lint.sh
    rtk test bash scripts/test-gemini-hooks-okf-lint.sh

Milestone 3 narrow checks:

    rtk test bash -n scripts/test-okf-lint.sh
    rtk test bash scripts/test-okf-lint.sh
    rtk proxy ./scripts/lint-okf.py
    rtk proxy ./scripts/lint-okf.py --format json

Milestone 4 cleanup checks:

    rtk test bash -n scripts/test-gemini-hooks-okf-lint.sh
    rtk test bash scripts/test-gemini-hooks-okf-lint.sh

Complete final matrix:

    rtk test bash scripts/test-okf-lint.sh
    rtk test bash scripts/test-hooks-okf-lint.sh
    rtk test bash scripts/test-gemini-hooks-okf-lint.sh
    rtk test bash scripts/test-hooks-auto-ingest.sh
    rtk test bash scripts/test-gemini-hooks-auto-ingest.sh
    rtk test bash scripts/test-hooks-startup.sh
    rtk test bash scripts/test-gemini-hooks-startup.sh
    rtk test bash scripts/test-install.sh
    rtk test python3 scripts/test_helpers.py
    rtk proxy ./scripts/lint-okf.py
    rtk proxy ./scripts/lint-okf.py --format json
    rtk git diff --check
    rtk git status --short

The human linter may be silent when clean. JSON lint must print the exact empty envelope above. Every test command must exit `0`. `git diff --check` must be silent. `git status --short` may list only intentional repair, test, plan, handoff, and synchronized `.agents/` documentation paths; no validation sandbox, bytecode, temporary transcript, or benchmark artifact may remain.

If milestone commits are authorized for the implementation session, create one reviewable commit after each green milestone and record its hash in `Artifacts and Notes`. If commits are not authorized, leave changes uncommitted and record `pending human commit`; never invent a checkpoint hash.

## Validation and Acceptance

The repair is accepted only when all following observable behavior holds through public entry points.

The Copilot adapter and registered stop coordinator consume one complete JSON object and exit while stdin remains open. Malformed, non-object, invalid UTF-8, and already-buffered trailing input still produce one provider-valid blocking response with exit `0`. A response containing non-CP1252 text remains UTF-8 JSON under a simulated CP1252 stdout environment.

The final coordinator response is compact UTF-8 JSON below 8,192 bytes. When both validators block, the reason contains a recognizable source-ingest prefix before a recognizable OKF prefix, even when truncation is necessary. A clean result remains exactly `{"decision":"allow"}`. Failure remains `{"decision":"block","reason":"..."}`.

Every Copilot OKF failure message contains an omitted-count line. A small finding set and `OKF900` say `0 additional diagnostics omitted.`. A 25-finding set displaying 20 says `5 additional diagnostics omitted.`. The rerun command remains `./scripts/lint-okf.py` on POSIX and `python scripts/lint-okf.py` on Windows.

The central CLI reports `OKF102` for Windows drive-rooted and UNC destinations on every host. It does not treat a footnote definition body as a file path. Apparent links inside an unclosed HTML comment remain ignored through end-of-file. Inline code masks links only when opener and closer use equal backtick-run lengths. Existing diagnostic IDs, ordering, locations, JSON schema, and exit meanings remain unchanged.

All recursive cleanup commands in `scripts/test-gemini-hooks-okf-lint.sh` use quoted exact paths and `rm -rf --`. The suite leaves no temporary directories after success or failure.

The complete final matrix passes, canonical human lint has no output, canonical JSON lint is exactly empty, final code review has no unresolved required finding, the agent documentation pass is complete, and this living plan matches actual status.

## Idempotence and Recovery

All public suites operate on temporary copied repositories and are safe to rerun. Open-pipe tests must kill and wait for a child when an assertion or timeout fires. Cleanup must target only the exact `mktemp` directory or copied fixture path and must pass `--` before the path. Never delete a repository root, user home, shared hook installation, or vendored dependency tree in place.

No database, network service, package installation, or schema migration is involved. Do not download or update PyYAML. No live Copilot or Gemini session is required because this repair changes static input/output handling already covered by public provider contract suites; the earlier user-approved waiver of provider-native Gate 6 proof remains intact.

If a red test exposes broader behavior than described here, stop that slice, record the discovery and decision in this plan, and revise the affected milestone before production edits. If a milestone must be undone after a commit, use `git revert <milestone-commit>` on a dedicated branch. If changes are uncommitted, reverse only owned hunks with `apply_patch`; do not use `git reset --hard` or broad checkout commands.

## Artifacts and Notes

Planning baseline is current `main` at `95f812d4` with a clean worktree before this plan was added. The prior review used migration baseline `b9a1d8a8a0542bec9eb6764cf4b4af3071eefad9` and the recorded 15-commit migration rollback unit.

Current decisive evidence:

    complete JSON with writer left open:
    still_running_after_complete_json=true

    Windows absolute destination probe:
    C:\Windows\win.ini []
    C:/Windows/win.ini []

    footnote probe:
    [('OKF103', 1, 11, 'local target does not resolve to a regular file')]

    Markdown masking probes:
    unclosed_html_comment [('OKF103', 1, 16)]
    mismatched_code_run []

    oversized combined stop response:
    8329 bytes

Add each red transcript, green transcript, milestone commit or pending-human-commit marker, review result, and final matrix result here as implementation proceeds. Keep evidence short; reference files instead of pasting full logs.

Milestone 1 is committed at `d2087c8f`. The public suite first failed with `lint-okf.py waited for stdin EOF`, then with `validate-stop.py waited for stdin EOF` after the shared-reader repair exposed the coordinator. Bash syntax, Copilot OKF, Copilot auto-ingest, Copilot startup, helper tests, and `git diff --check` all pass. Oversized combined reasons retain at least 512 UTF-8 bytes from each blocker in source-ingest-first order while the serialized envelope remains below 8 KiB.

Milestone 1 review follow-up is committed at `6f0a8f06`. Open `{` first reproduced `lint-okf.py waited for stdin EOF`; the reader now applies a 0.5-second idle/readiness bound through POSIX `select` or Windows `PeekNamedPipe` polling. Public adapter and coordinator cases cover incomplete, malformed, multiline, and buffered-trailing input, with child cleanup on failure.

Milestone 2 is committed at `fdb63ec73d47c4b3192ed73fba836b690b79e55a`. The public Copilot suite first failed because a normal failure omitted `0 additional diagnostics omitted.`. Copilot and Gemini OKF suites, Bash syntax, Python compilation, and `git diff --check` pass after normal, `OKF900`, and emergency fallback reasons gained accurate omitted counts; the 25-finding case reports exactly 5 omitted.

Milestone 2 review follow-up is committed at `c9f8af6dfcc506dc4329c1922d9ee7af2d5975f7`. A public central exit-`2` case first reported zero omitted despite one normalized `OKF900`; a typed failure now carries normalized diagnostics so the adapter reports the accurate suppressed count.

Milestone 2 second follow-up is committed at `05785c382e9b55bb7790dc7ea66333d70df96fcf`. A central exit `0` paired with one valid diagnostic first reported zero omitted; every post-normalization status mismatch now uses the count-preserving typed failure and the public adapter reports one omitted.

Milestone 3 is committed at `f3234d2643b34aa68bc1021cf1f2f59456c5e6b4`. The four public red slices respectively produced empty diagnostics for Windows absolute paths, `OKF103` for a footnote body, `OKF103` inside an unclosed HTML comment, and empty diagnostics for a mismatched backtick run. The linter suite, canonical human and exact-empty JSON lint, Bash syntax, and `git diff --check` pass after the fixes.

Milestone 3 review follow-up is committed at `e513eeb92585ce9c27f4d86cf19912c4e783b553`. A closed fence containing an unclosed comment marker first hid a later missing link; fence and inline-code regions now take precedence, and both public cases report the later link at its exact `OKF103` location.

Milestone 3 second follow-up is committed at `8c9f458ceceb80942aba932deb7469fccb9c4683`. A fence opener inside an HTML comment first paired with a later delimiter and hid a real link; one left-to-right scanner now gives the first active construct precedence for comments, fences, and exact-run inline code. Both inverse-nesting cases report the later `OKF103` at exact locations.

Milestone 4 cleanup is committed at `3bbd9436`. Bash syntax, the complete Gemini OKF hook suite, and `git diff --check` passed after adding `--` to 15 recursive removals (13 dynamic traps and 2 direct removals).

Independent review requested changes for three acceptance defects: incomplete open-pipe input can hang, exit-`2` normalized diagnostics lose their omitted count, and comment masking currently overrides closed code regions. The initial complete static matrix was green, confirming these were coverage gaps rather than existing-suite failures.

Two follow-up review rounds exposed the inverse masking precedence and an exit-`0` diagnostic-count mismatch. Commits `6f0a8f06`, `c9f8af6d`, `e513eeb9`, `05785c38`, and `8c9f458c` close all five findings. Final independent rereview approved the result with no remaining findings.

The final static matrix passed all nine listed test suites. Canonical human lint was silent, JSON lint printed exactly `{"schema_version":1,"diagnostics":[]}`, and `git diff --check` was silent. The `update-agent-docs` pass changed only `.agents/memory/API_MAP.md`, `.agents/memory/known-issues/scripts.md`, `.agents/memory/testing/hooks.md`, and `.agents/memory/testing/scripts.md`; the `okf-authoring` pass loaded `references/profile.md`, required no source-summary branch, passed full OKF lint, and confirmed exactly those four authorized canonical paths.

Closure records and synchronized agent knowledge are committed at `706b760`.

## Interfaces and Dependencies

Do not add dependencies. Continue using Python's standard library, the existing vendored PyYAML 6.0.3 for the central linter, Bash, and existing test helpers.

In `.github/hooks/scripts/helpers/common.py`, retain `read_json_input() -> dict`. Add or synchronize private incremental read helpers equivalent to `_read_available_stdin_bytes(stdin_fd: int) -> bytes` and `_read_json_input_text() -> str`. Keep `emit_json(payload: dict) -> None` as the sole repository-local Copilot JSON writer.

In `.github/hooks/scripts/validate-stop.py`, retain the registered command-line interface: one JSON mapping on stdin, one compact JSON mapping on stdout, and exit `0`. Keep child validators as separate processes. Add private helpers with clear names for serialized response size, UTF-8-safe text truncation, and bounded reason combination. Their exact names may follow existing file style, but the externally visible allow/block envelopes and validator order are fixed.

In `.github/hooks/scripts/lint-okf.py`, retain `MAX_DISPLAY_DIAGNOSTICS = 20`, `MAX_HOOK_OUTPUT_BYTES = 8192`, current event detection, and current response envelopes. `_format_diagnostics` and every `OKF900` construction must include one omitted-count line.

In `scripts/lint-okf.py`, retain `destination_diagnostics`, `reference_destinations`, `ignored_ranges`, `link_diagnostics`, and all existing diagnostic IDs. Add a small host-independent absolute-path predicate if that keeps drive/UNC logic readable. Do not change `Diagnostic`, JSON schema version `1`, sort order, or exit codes.

Revision note (2026-09-16): Initial plan created from the two-axis review. It resolves all confirmed findings, narrows the cleanup finding to its valid missing-`--` component under area-specific guidance, fixes tests at existing public seams, and keeps original migration acceptance history unchanged.

Revision note (2026-09-16): Milestone 4 cleanup is complete and verified at `3bbd9436`; final matrix, review, knowledge synchronization, and closure remain open.

Revision note (2026-09-16): Milestone 1 is complete and verified at `d2087c8f`; open-pipe, UTF-8, and final-envelope byte-boundary repairs now pass their public regressions.

Revision note (2026-09-16): Milestone 3 is complete and verified at `f3234d2643b34aa68bc1021cf1f2f59456c5e6b4`; cross-platform destinations and Markdown masking now follow the stated contract.

Revision note (2026-09-16): Milestone 2 is complete and verified at `fdb63ec73d47c4b3192ed73fba836b690b79e55a`; every Copilot OKF failure now reports an omitted count.

Revision note (2026-09-16): Independent review reopened Milestones 1–3 for three required boundary and masking fixes; closure remains blocked until focused regressions, rereview, and the final matrix pass.

Revision note (2026-09-16): Milestone 3 review follow-up is complete at `e513eeb92585ce9c27f4d86cf19912c4e783b553`; code regions now protect contained comment markers without hiding later Markdown.

Revision note (2026-09-16): Milestone 1 review follow-up is complete at `6f0a8f06`; incomplete or malformed open-pipe input now fails within a bounded interval.

Revision note (2026-09-16): Milestone 2 review follow-up is complete at `c9f8af6dfcc506dc4329c1922d9ee7af2d5975f7`; exit-`2` failures retain their normalized diagnostic count.

Revision note (2026-09-16): Follow-up review reopened Milestones 2 and 3 for an exit-`0` status mismatch and inverse comment/code nesting; both require public regressions before closure.

Revision note (2026-09-16): Second follow-up fixes are complete at `05785c38` and `8c9f458c`; all normalized failure paths retain counts and Markdown masking now uses left-to-right construct precedence.

Revision note (2026-09-16): Implementation is complete. Final rereview, complete static validation, agent-document synchronization, and OKF representation verification all pass with no remaining work.
