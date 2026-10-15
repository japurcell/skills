# Diagnose recurring hook failures and define a resilient design

This living investigation plan is `docs/hook-resilience/ExecPlan.md`. Follow `.agents/skills/exec-plans/SKILL.md`, repository instructions, and the current user request. The deliverable is a reproduced diagnosis and a concrete improvement proposal for both security hooks. Proposed production changes must remain distinguishable from observed behavior.

## Purpose / Big Picture

Explain why the updated `docs/scan-secrets-hook-bug.txt` still blocks ordinary Copilot work, and identify durable ways to make both `scan-secrets` and `tool-guard` usable without silently accepting incomplete security inspection. Success means a reader can reproduce the defect, distinguish the actual cause from the report's hypotheses, and implement a bounded hardening sequence with explicit security and usability acceptance tests.

## Progress

- [x] (2026-10-14) [milestone-1] D1: Reproduced the exact 2,030,848-byte denial through the public Copilot scanner entrypoint with a synthetic repository.
- [x] (2026-10-14) [milestone-1] D1: Clean repository and nine individually small files totaling 2,030,848 bytes both pass. The report's 1 MiB aggregate-limit interpretation is incorrect for current source.
- [x] (2026-10-14) [milestone-1] D1: Completed tracked-file, provider, and fake-secret controls; recorded exact scope and limitations.
- [x] (2026-10-14) [milestone-2] D2: Analyzed scanner streaming, detection semantics, and recovery design.
- [x] (2026-10-14) [milestone-2] D3: Analyzed Guardian schema, parser, limits, deployment, and incident attribution; reproduced optional-field misclassification.
- [x] (2026-10-14) [milestone-2] D4: Proved configured fsmonitor execution during status; checked official CLI activation behavior and recorded unverified extension delivery.
- [x] (2026-10-14) [milestone-3] D5: Saved the evidence-backed proposal, H1-H6 implementation sequence, and negative-test matrix in [investigation.md](investigation.md).
- [x] (2026-10-14) [milestone-3] Completed one coordinated knowledge-maintenance pass after both agents finished; no canonical KB changes warranted.
- [x] (2026-10-14) [milestone-3] Artifact links, YAML syntax, typography, and whitespace checks passed.

## Surprises & Discoveries

- `file_bytes_limit/candidate_read` is an individual worktree file bound. `_read_bounded_descriptor()` obtains the reported count from `fstat()` before reading an already oversized file. The aggregate candidate limit is separately 8 MiB.
- Current scanner `main()` selects pending repository snapshots regardless of the requested tool or its arguments. A benign `git status` request therefore inherits unrelated candidate failures.
- The prior repair deliberately added incomplete-scan diagnostics while retaining the 1 MiB per-file policy. Identical limits after an update do not establish stale deployment. The new typed diagnostic itself is evidence that some diagnostic-capable implementation ran; it does not fingerprint the remote installation.
- Adding valid `max_output_tokens` metadata to a Codex shell request changes a safe quoted search from allow to `command_segments` denial. Existing 22 native-data and 144 corpus fixtures pass despite this missing envelope coverage.
- An incomplete JSON prefix kept the public Copilot Guardian alive for 10,507 ms without output, beyond its configured ten-second host timeout. Actual authenticated-host timeout behavior was not exercised.
- A configured fsmonitor fixture ran during `git status --porcelain`. A command-name allowlist cannot establish a safe recovery boundary.

## Decision Log

- 2026-10-14: Use source baseline `bc52d7d69aaa046ea97e323879402241a01fead7` in `/Users/adam/.codex/worktrees/c164/skills`, branch `codex/fix-hook-bug-reports-2`.
- 2026-10-14: Reproduce through generated public subprocesses first, with disposable homes, logs, and Git repositories. Keep production hooks enabled and do not alter the original report.
- 2026-10-14: Treat the report's suggested allowlist and streaming design as hypotheses to test. Command names, filename extensions, and a metadata label are not sufficient safety proofs.
- 2026-10-14: Keep investigation findings and future implementation distinct. The current request asks for diagnosis and investigation; the output will define the implementation work precisely.

## Outcomes & Retrospective

The diagnosis and design investigation are complete. [The report](investigation.md) records public reproductions, current detection semantics, two additional structural defects, and proposed H1-H6 hardening work with acceptance gates. [The delegation audit](delegation-audit.yml) records the two completed read-only analyses. Artifact links, YAML syntax, typography, and whitespace checks passed. No production source or installed settings have changed. The original Linux repository, offending filename, installed build, authenticated provider delivery, and native Windows behavior remain unverified.

## Context and Orientation

Canonical source lives in `hooks/families/scan_secrets.py` and `hooks/families/tool_guard.py`. `scripts/generate-hooks.py` renders independent installed-provider outputs under `.copilot/hooks/scripts/`, `.gemini/hooks/scripts/`, and `.codex/hooks/`; generated copies must not be edited directly. Copilot registers both hooks at `preToolUse`; scanner also has a later warning-mode invocation. Generated output and installed behavior are separate evidence levels.

Scanner candidates are staged, working-tree, untracked, and merge-stage snapshots selected from Git. One path can contribute multiple snapshots. Current bounds are 256 snapshots, 1 MiB per file, 8 MiB total candidate bytes, 8 MiB Git capture, and eight seconds. The scanner reads a full candidate before deciding whether to scan its full contents or only added diff lines. It is not a general scanner of requested tool output or newly submitted patch bodies.

Guardian classifies exact provider argument forms before applying native-data or executable-input inspection. The previous repair recognizes raw Copilot patches and Codex `command` object patches, with a 256 KiB patch bound. Unknown shapes remain strict. The new report repeats an older 129-segment denial without a fresh payload or execution identity; that excerpt does not establish a fresh patch regression. Independent probes did establish a current optional-field false positive for shell requests.

## Plan of Work

### Milestone 1: Establish the new scanner failure precisely

Status: complete
Acceptance: met; exact denial, aggregate counterexample, tracked-file parity, and all six provider/scenario controls verified.

D1 is coordinator-owned and has no prerequisites. Read the supplied report, trace the relevant source, and invoke the public scanner on clean, one-large-file, and many-small-file repositories. Extend the probe to tracked modifications and fake-secret controls. Check the reported command without executing user repository changes. Acceptance requires the exact diagnostic, a counterexample to the aggregate-size hypothesis, and an explicit statement of what the local probes do not prove about the remote host.

### Milestone 2: Find structural fragility and evaluate alternatives

Status: complete
Acceptance: met; joined threat model, source-backed analyses, public counterexamples, and provider-evidence limits recorded.

D2 depends on D1's initial reproduction and is a read-only scanner analysis task. Trace full/diff/binary/index/merge detection and allowlist semantics. Propose bounded incremental processing with explicit long-token, long-line, chunk-boundary, race, and timeout behavior. Stop with source-backed findings and an implementable test matrix.

D3 depends on D1's initial reproduction and independently analyzes Guardian. Trace provider schemas, inert-data classification, parser fallbacks, resource limits, and safe telemetry. Reuse prior sanitized incident evidence and optionally inspect bounded local log tails without retaining commands or payloads. Distinguish supported current behavior, strict unsupported behavior, and newly reproduced defects. Stop with ranked improvements and negative controls.

D4 is coordinator-owned and runs alongside D2/D3. Test whether suggested metadata commands are intrinsically safe, inspect configured executable hooks, and consult official provider/Git references for version-sensitive behavior. Record configuration reload separately from script replacement. Do not deploy a broad metadata-command exemption or claim provider-dispatch proof from direct subprocess tests.

Milestone acceptance requires a joined threat model: which boundary each hook actually protects, which availability failures are avoidable, and what remains outside its guarantees. The scanner's operational recovery must not disable Guardian, turn content-scan errors into clean results, or expose credentials in filenames/logs.

### Milestone 3: Deliver a concrete hardening proposal

Status: complete
Acceptance: met; report, coordinated maintenance, and final artifact checks complete.

D5 depends on D1-D4 and is coordinator-owned. Reconcile findings into this plan and a concise investigation report under `docs/hook-resilience/`. State the recommended architecture, rejected shortcuts, ordered implementation tasks, resource/deployment gates, and testable user outcomes. Preserve report ambiguities as uncertainties rather than inventing remote state.

After all agents finish, perform one `update-agent-docs` pass under knowledge admission. No new memory is required. Check local links and diff whitespace. Acceptance is an accurate, reviewable proposal with reproducible evidence, not a claim that production fixes have already shipped.

## Concrete Steps

No investigation steps remain. Future production work is proposed separately as H1-H6 in the report; none has been implemented here. Reproduction context: run from `/Users/adam/.codex/worktrees/c164/skills`; public fixture probes use `scripts/tool_guard_test_support.py` with `SCAN_MODE=block`, `SCAN_SCOPE=diff`, isolated `SECRETS_LOG_DIR`, and `OBSERVABILITY_TESTING=1`. Remove inherited skip/allowlist overrides from fixture environments.

## Validation and Acceptance

Observed first probe: clean repository allows; one 2,030,848-byte safe untracked file denies with `file_bytes_limit/candidate_read`, measured 2030848, limit 1048576; nine safe files totaling the same bytes allow. Source confirms `MAX_TOTAL_BYTES=8388608` and the pre-read `fstat()` check. The public hook returns exit zero with denial JSON, so exit status alone is not acceptance.

Additional observed evidence: tracked large-file edits fail before diff inspection; all three public providers deny oversized candidates and detect fake credentials without values; validated Guardian output metadata causes a false positive; incomplete JSON remains blocked past the configured Copilot timeout; configured fsmonitor executes during status. Native-data and false-positive corpus suites passed 22 and 144 cases respectively. A recovery capability is specified, not implemented or runtime-validated. No actual credential, raw session body, or user repository content belongs in artifacts. Native Windows and authenticated Linux provider delivery remain separate unverified dimensions.

Knowledge-maintenance result: Added: None. Changed: None. Split or moved: None. Deduplicated: None. Index updates: None. Remaining doc quality TODOs: None. Existing strict-schema, incomplete-scan, raw-envelope, and snapshot-consistency guidance remains accurate. New proposal details belong in this investigation, not canonical policy. No skill improvements identified.

## Idempotence and Recovery

All experiments use unique disposable repositories and logs. Do not change live hook settings, suppress security checks, or mutate the original Linux repository. If a probe fails for an environment prerequisite, retain the distinction from a product failure. Keep report edits scoped to this effort. Future implementation must change canonical renderers, regenerate provider outputs, and satisfy the source/installed/platform gates before any deployment claim.
