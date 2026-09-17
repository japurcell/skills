# Generate checked-in provider-local hook scripts

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept current as work proceeds. Maintain this document according to the repository-local `exec-plans` skill at `.agents/skills/exec-plans/SKILL.md`.

## Purpose / Big Picture

Copilot, Gemini, and repository-local GitHub hooks currently contain large copies of the same Python logic. A maintainer must repeat changes across provider trees, and security or reliability fixes can drift. After this plan, maintainers edit one canonical source for each selected hook family, run one explicit generator command, and commit readable provider-local outputs. Each provider still executes an independent local Python file, so installation and runtime isolation do not change.

The observable workflow will be:

    python3 scripts/generate-hooks.py --write
    python3 scripts/generate-hooks.py --check

The first command renders all declared hook families through an all-or-nothing write transaction. The second performs no filesystem writes and exits successfully only when every checked-in output is current. Running `python3 scripts/test-all.py` will include the freshness and generator test suite. Existing provider hook suites will continue proving provider-specific envelopes, failure modes, event handling, installation, and security behavior.

This plan covers a low-risk pilot followed by the high-value duplicate families: shared common and audit helpers, observability, Tool Guardian, secret scanning, and source auto-ingest. It does not migrate Codex or provider required-skill loaders, RTK forwarders, OKF adapters, audit-versus-observability primitives, YAML parser variants, `.github/hooks/scripts/validate-stop.py`, or `.copilot/hooks/scripts/bell.py`. The final milestone reassesses those deferred candidates using evidence from the completed generator.

## Progress

- [x] (2026-09-17 05:25Z) [milestone-1] Add generator architecture, CLI, tests, documentation, and the `send-event.py` pilot.
- [x] (2026-09-17 05:37Z) [milestone-2] Generate Copilot, Gemini, and GitHub common and audit helpers without changing runtime behavior.
- [x] (2026-09-17 05:47Z) [milestone-3] Generate Copilot and Gemini observability helpers without changing runtime behavior or latency expectations.
- [x] (2026-09-17 06:01Z) [milestone-4] Generate and validate Copilot and Gemini Tool Guardian scripts from one canonical policy with explicit provider adapters.
- [x] (2026-09-17 06:27Z) [milestone-4] Resolve the first independent security review's SEC-001, SEC-002, and SEC-003 findings with public-envelope regressions and regenerated outputs.
- [x] (2026-09-17 06:41Z) [milestone-4] Resolve the security rereview's separator, parser-bound, complete-syntax, SQL-comment, and raw-evidence findings with a second isolated TDD repair.
- [x] (2026-09-17 06:55Z) [milestone-4] Resolve compatibility-normalized allowlist equality plus home-variable removal and Git global-option detection in a third isolated TDD repair.
- [x] (2026-09-17 07:03Z) [milestone-4] Resolve object-valued tool-input scanning with bounded recursive string extraction, serialized fallback, and safe structured negatives.
- [x] (2026-09-17 07:08Z) [milestone-4] Obtain independent security approval with no unresolved high-confidence blocker and accept the milestone.
- [x] (2026-09-17 07:22Z) [milestone-5] Generate and validate Copilot and Gemini secret scanners, remove owned response duplication, and share provider-neutral detection and exact-allowlist vectors.
- [x] (2026-09-17 07:54Z) [milestone-5] Resolve the first independent security review's SEC-001 through SEC-006 findings with an isolated TDD repair, regenerated outputs, and public fail-closed/warn regressions.
- [x] (2026-09-17 08:17Z) [milestone-5] Resolve the security rereview's initial-probe, literal-pathspec, streaming-output/deadline, and staged-scope findings in a second isolated TDD repair.
- [x] (2026-09-17 08:31Z) [milestone-5] Resolve the next security rereview's ambiguous index-object and source-collapsing default-diff findings in a third isolated TDD repair.
- [x] (2026-09-17 08:48Z) [milestone-5] Resolve the next security rereview's unbounded finding retention, match-loop deadline, serialized-record, and incoming-record rotation findings in a fourth isolated TDD repair.
- [ ] [milestone-5] Obtain independent security approval for canonical secret patterns, Git subprocess boundaries, output envelopes, logging, timeouts, and rendered files.
- [ ] [milestone-6] Generate GitHub and Gemini auto-ingest engines and wrappers while preserving manifest and gate behavior.
- [ ] [milestone-7] Finish repository-wide validation, classify drift, update durable documentation, and publish the Phase 2 recommendation.

## Surprises & Discoveries

- Observation: No checked-in hook generator or freshness checker exists today.
  Evidence: Provider hook trees contain independently maintained scripts. The closest precedent is `scripts/install-codex-agents.py`, which emits generated headers, compares bytes, validates rendered TOML, uses atomic writes, and tests idempotence, but its generated files live in an installation target rather than this repository.

- Observation: Runtime isolation is an intentional architecture constraint, not accidental duplication.
  Evidence: `docs/adr/0001-auto-ingest-runtime-shape.md` and `.agents/instructions/hooks.md` require provider-local executable logic and prohibit cross-runtime imports. This plan shares build-time source only; generated runtime files remain local and self-contained.

- Observation: CLI guidance has one stream-placement disagreement.
  Evidence: `.agents/sources/12-factor-cli-apps.md` and `.agents/sources/clig-dev.md` put warnings and progress on standard error, while `.agents/sources/cli-design-guidelines.md` suggests warnings on standard output. This plan chooses standard error for warnings and progress so redirected standard output remains automation-safe.

- Observation: A real-home installer smoke test cannot run in this agent environment.
  Evidence: `./scripts/install.sh` stopped while copying to `/root/.agents/skills/addy-code-review-and-quality/SKILL.md` with `Read-only file system`. The targeted installer fixture and both observability suites passed, including installed-copy execution in their temporary homes.

- Observation: Common and audit helpers did not previously have shebangs, although the generator contract requires every generated output to be executable.
  Evidence: Their characterization hashes match the pre-generation runtime body after removing only the generated header and added shebang; `scripts/test-generate-hooks.py` proves this for all six helpers.

- Observation: The observability helpers have eight intentional provider adapter sites and are otherwise identical.
  Evidence: The pre-migration unified diff contains only runtime identity, runtime-prefixed environment variables, and the default runtime-home path. The generator regression normalizes only those eight exact expressions and rejects every other difference.

- Observation: Tool Guardian has no dedicated latency benchmark or numeric latency budget in its focused suites or hook guidance.
  Evidence: Repository search found latency requirements only for observability and bounded Git-probe timing for secret scanning. Tool Guardian extraction retains each provider's existing imports, adds no runtime template loading or cross-provider imports, and both startup suites pass under their existing hook timeouts.

- Observation: The first independent Tool Guardian security review rejected the extracted behavior with three high-confidence findings.
  Evidence: SEC-001 showed that substring allowlist entries authorized destructive content with surrounding commands; SEC-002 showed that reordered recursive-remove flags, force-push options after the refspec, and unfiltered SQL deletion without a semicolon bypassed detectors; SEC-003 showed that raw matched credentials reached responses and audit records while Gemini created a permissive, unlocked log. Provider-level regressions now reproduce each class through public JSON envelopes.

- Observation: The second security review correctly withheld approval because normalization and parser limits still created authorization and detection gaps.
  Evidence: Exact allowlist normalization collapsed control separators; bounded parsing silently ignored content past 32 KiB, 128 command segments, or 256 tokens; recursive removal inspected only its first operand; executable paths and full Git refspecs were incomplete; and SQL comments containing `where` were mistaken for a filter. The rereview also rejected redacted evidence as unnecessarily risky and required category/severity-only reporting.

- Observation: Compatibility normalization remained unsafe even after control separators were rejected, and command parsing still omitted common indirection.
  Evidence: NFKC made ASCII and fullwidth semicolon, ampersand, pipe, dollar, quote, and backtick inputs equal at the authorization boundary. Recursive forced removal through `$HOME`, `${HOME}`, PowerShell environment variables, and `%USERPROFILE%` was not classified, while a protected forced push following Git global options such as `-C`, `-c`, `--git-dir`, and `--work-tree` was missed.

- Observation: Compact JSON fallback was not sufficient for object-valued tool input because SQL string literals were deliberately masked by the SQL lexer.
  Evidence: A nested decoded `query` value containing unfiltered deletion was allowed after serialization wrapped it in JSON quotes, while the equivalent plain-string input was denied. Both provider-envelope regressions reproduced the bypass and also proved a nested filtered query remains allowed.

- Observation: The two handwritten secret scanners shared their complete detection, Git, file-selection, redaction, logging, and mode policy; only response envelopes, session-key precedence, default log paths, working-directory selection, and the final block reason differed.
  Evidence: The pre-extraction unified diff contained only those provider sites. Generated-output tests now remove exactly two marked adapters from each output and require the remaining three shared sections to be identical.

- Observation: Milestone 4's exact allowlist implementation was still embedded inside the Tool Guardian family renderer rather than exposed as a build-time canonical source.
  Evidence: Moving the unchanged implementation to `hooks/families/allowlist.py` and embedding it into both security families made `python3 scripts/generate-hooks.py --write` report all 14 outputs already current after the Tool Guardian renderer change.

- Observation: The first independent secret-scanner review found six fail-open, parsing, file-safety, resource-bound, log-permission, and lock-contention defects that extraction characterization did not expose.
  Evidence: SEC-001 through SEC-006 reproduced Git command failures being treated as empty results, ambiguous line-delimited paths and diff markers, binary credential files escaping token scans, link-following and unbounded candidate reads, permissive or redirected logs, and an unbounded blocking log lock. Shared generated-code tests and provider public-envelope suites now exercise each affected boundary with fake credentials only.

- Observation: The first repair still conflated a failed initial Git probe with a verified non-repository and bounded Git output only after the child had completed.
  Evidence: The rereview reproduced a corrupt repository marker being logged as a harmless skip, pathspec-shaped committed filenames escaping per-file diffs, output being captured before its size check, separate five-second Git calls exceeding the scanner's intended aggregate budget, and untracked files entering staged-only scans. Provider and shared regressions now cover the public envelopes and real Git filenames as well as early child termination and one cumulative deadline.

- Observation: Git's shorthand index-object syntax and a path-only default-diff union each hid a distinct index state.
  Evidence: `:0:notes.env` parses as stage zero of `notes.env`, not the staged file named `0:notes.env`; prefixing repository-relative paths with `:./` removes that ambiguity. Separately, `git diff HEAD` reported no change when a fake secret remained staged but the worktree file was restored to `HEAD`, so the scanner must retain cached, worktree, and untracked source identities instead of collapsing their pathnames.

- Observation: Input-byte limits did not bound the number or serialized size of secret findings.
  Evidence: A staged file below the per-file byte limit could contain thousands of compact token matches, causing every tuple and JSON object to be retained and appended in one audit record. Log rotation considered only the old file size, so a nearly full active log could grow well past its configured threshold after that record arrived.

## Decision Log

- Decision: Maintain canonical hook-family sources under top-level `hooks/` and commit generated provider-local outputs.
  Rationale: This removes duplicate human maintenance without weakening provider runtime isolation or making installation depend on generation.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Use small Python family renderers and explicit provider adapter blocks, not a general template language, runtime shared library, or textual search-and-replace.
  Rationale: Family renderers use only the standard library, keep provider differences visible, and can produce complete readable Python files deterministically.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Generated outputs are never edited directly and carry a source path plus do-not-edit header immediately after the shebang.
  Rationale: Ownership must be visible in ordinary diffs. The added comment is an accepted formatting-only change during initial migration.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Require one explicit CLI action, `--write` or `--check`; bare invocation prints help and exits `2` without mutation.
  Rationale: State changes must be explicit and automation must have a zero-write verification mode.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Preserve every current provider behavior during extraction. Evaluate observed drift immediately after each family migration, but implement confirmed fixes in separate tasks or diffs.
  Rationale: Structural equivalence and behavior correction need independent proof and rollback boundaries. Confirmed security or correctness defects block the next milestone; documented intentional or low-risk differences do not.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Migrate one independently verifiable family group at a time, beginning with byte-identical `send-event.py` as the generator pilot.
  Rationale: The pilot proves CLI, generation, freshness, headers, modes, and transactional writes before large or security-sensitive modules move.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Never delete stale generated outputs automatically.
  Rationale: Provider directories also contain handwritten scripts. The generator may report a previously generated but undeclared output, but removal requires an explicit reviewed repository edit.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Record the architecture in `docs/adr/0004-generated-provider-hooks.md`.
  Rationale: Build-time canonical sharing beside a strict runtime-isolation rule is consequential and surprising without context.
  Date/Author: 2026-09-17, user and Codex.

- Decision: The milestone-one manifest declares only the two `send_event` outputs.
  Rationale: The generator must never claim ownership of a future family's handwritten files. Subsequent milestones extend the explicit manifest at the same time as they add a renderer and generated output.
  Date/Author: 2026-09-17, Codex.

- Decision: Keep current common and audit differences as named provider adapters in their canonical renderers.
  Rationale: GitHub retains its bounded incomplete-input wait and does not use observability capture or a passive-log helper. Copilot and Gemini retain observability capture but differ in passive-log entrypoint, shadow mode, environment names, and default audit path. GitHub's audit writer retains its mode-prefixed shadow records and has no `audit_init` or `audit_log_passive_event` API.
  Date/Author: 2026-09-17, Codex.

- Decision: Represent observability provider variation with exact adapter expressions, not broad name replacement.
  Rationale: Exact replacements make the runtime name, environment precedence, and default path differences reviewable and cause the regression test to fail when a new provider divergence appears.
  Date/Author: 2026-09-17, Codex.

- Decision: Render Tool Guardian as one readable policy body surrounded by two marked provider-adapter blocks.
  Rationale: The policy body now owns all 21 threat matchers, aggregation, allowlist parsing, and allowlist matching once. Marked adapters keep response envelopes, payload-key precedence, logging, paths, and exception formatting explicit, while a generator regression rejects policy drift outside those blocks.
  Date/Author: 2026-09-17, Codex.

- Decision: Keep Milestone 4 in progress after extraction validation.
  Rationale: Generator, provider, startup, and installer validation is complete, but the required independent security review is intentionally delegated to a separate reviewer and remains the milestone's only acceptance gate.
  Date/Author: 2026-09-17, Codex.

- Decision: Replace Tool Guardian's comma-separated substring allowlist with a bounded JSON array of exact `{tool,input}` entries.
  Rationale: NFKC normalization plus whitespace normalization permits stable configuration while exact tool-scoped comparison prevents an approved fragment from authorizing surrounding commands or a different tool. Malformed and legacy unstructured values fail closed.
  Date/Author: 2026-09-17, Codex.

- Decision: Normalize and tokenize only bounded command text for the recursive-remove and force-push detectors, and parse bounded SQL statements through semicolon or end of input.
  Rationale: Equivalent option order, split flags, forced refspecs, JSON-encoded inputs, multiline SQL, and terminal SQL statements must produce the same decision without introducing unbounded parsing work on the hook hot path.
  Date/Author: 2026-09-17, Codex.

- Decision: Expose only category, severity, and a bounded redacted excerpt for Tool Guardian threats, and harden Gemini audit writes with owner-only no-follow files and a bounded cross-platform lock.
  Rationale: Tool input can contain URL credentials, query tokens, authorization headers, and credential-like values. Responses and audit records must not reproduce those values, while concurrent or redirected logging must fail closed instead of weakening confidentiality or record integrity.
  Date/Author: 2026-09-17, Codex.

- Decision: Preserve separators during allowlist normalization and reject both control characters and escaped control-separator spellings.
  Rationale: A newline, carriage return, tab, or escaped separator changes command structure and must never become equivalent to an ordinary space in an authorization decision. Both configured entries and runtime candidates fail closed at this boundary.
  Date/Author: 2026-09-17, Codex.

- Decision: Treat every scan-text, command-segment, or token-bound overflow as a critical threat instead of truncating the parse.
  Rationale: Bounded work protects hook latency only if content beyond the bound cannot hide destructive syntax. Limit validation runs before allowlist authorization and denies overflow even when warning mode is configured. The parser also inspects every recursive-remove operand, normalizes executable basenames and complete protected Git refspec destinations, and removes SQL comments and literals before deciding whether a real `where` clause exists.
  Date/Author: 2026-09-17, Codex.

- Decision: Supersede redacted threat excerpts with category/severity-only response and audit details.
  Rationale: Even bounded redaction is unnecessary exposure when the control-flow decision needs only the threat classification. Removing evidence fields entirely gives credentials and other command data no threat-reporting path to stdout or audit storage.
  Date/Author: 2026-09-17, Codex.

- Decision: Supersede NFKC allowlist normalization with exact code-point equality after trimming ASCII spaces only at both edges.
  Rationale: Compatibility characters can become shell-significant after later normalization or interpretation. Authorization must therefore distinguish fullwidth punctuation and preserve internal spacing byte-for-byte, while the existing control and escaped-separator rejection remains fail closed.
  Date/Author: 2026-09-17, Codex.

- Decision: Treat common home-variable expansions as protected recursive-remove targets and parse Git global options before locating `push`.
  Rationale: Shell expansion can make `$HOME`, `${HOME}`, `$env:HOME`, `$env:USERPROFILE`, or `%USERPROFILE%` equivalent to a protected home path. Git accepts global flag and option/value forms between its executable and subcommand, so detection must skip those forms before evaluating protected refspecs and force options.
  Date/Author: 2026-09-17, Codex.

- Decision: Scan bounded recursively extracted structured string values before retaining compact JSON as a compatibility fallback.
  Rationale: Decoded `command`, `query`, and nested string values must reach detectors without JSON quoting changing their meaning. Traversal is capped at 32 levels, 256 nodes, 128 strings, and 32 KiB of string data; exceeding a cap maps to the existing critical input-limit denial. Threats from extracted and serialized representations are deduplicated by category and severity.
  Date/Author: 2026-09-17, Codex.

- Decision: Accept Milestone 4 at commit `dd6d3f670b9181ab3ee73eaa48fb6785282a3db0` after independent security rereview.
  Rationale: The reviewer approved the canonical policy, generated provider outputs, failure paths, authorization boundaries, and regression coverage with no high-confidence blocker remaining.
  Date/Author: 2026-09-17, independent security reviewer and Codex.

- Decision: Embed one build-time canonical exact allowlist source into Tool Guardian and secret-scanner outputs.
  Rationale: Both security families now maintain identical structured, bounded, exact allowlist parsing and comparison once while every generated provider script remains self-contained with no runtime cross-provider import.
  Date/Author: 2026-09-17, Codex.

- Decision: Keep Milestone 5 in progress after extraction validation.
  Rationale: Canonical extraction, shared vectors, public provider tests, startup suites, and installer suites pass, but the required independent security review intentionally remains a separate acceptance gate.
  Date/Author: 2026-09-17, Codex.

- Decision: After successful repository detection, treat every Git diff, file-list, staged-content, or related candidate-read failure as a scanner error and route it through the provider's block-denial or warn-no-op envelope.
  Rationale: An operational failure cannot be represented as an empty clean result. NUL-delimited path output, pinned diff formatting, byte-safe decoding, and stateful hunk parsing make unusual filenames and added lines beginning with `++` unambiguous.
  Date/Author: 2026-09-17, Codex.

- Decision: Read worktree candidates descriptor-first without following links, validate staged object sizes before content reads, and enforce per-file, total-byte, file-count, Git-output, and elapsed-time bounds.
  Rationale: Repository-relative path validation alone does not prevent link races or resource exhaustion. Any rejected or exceeded boundary is a scanner error, so block mode fails closed while warning mode retains its compatibility no-op.
  Date/Author: 2026-09-17, Codex.

- Decision: Secure secret-scan logs and locks as owner-only regular files behind a bounded nonblocking cross-platform lock.
  Rationale: Log directories use mode `0700`, active and rotated files use `0600`, links and reparse points are rejected, and lock timeout follows the same provider failure policy instead of stalling the hook indefinitely.
  Date/Author: 2026-09-17, Codex.

- Decision: Treat an initial Git-probe failure as a verified non-repository only when no `.git` file or directory exists at the working directory or any ancestor.
  Rationale: A corrupt or inaccessible repository must not silently bypass scanning. Marker-backed failures use the existing provider block-denial or warn-no-op envelope, while a directory with no repository evidence retains the compatible skipped result.
  Date/Author: 2026-09-17, Codex.

- Decision: Give every Git child literal pathspec semantics, a streaming output cap, and the remaining portion of one deadline created at scanner entry.
  Rationale: Git syntax embedded in a real filename must remain data, output overflow must terminate before unbounded capture, and several individually successful slow commands must not multiply the scanner's total runtime budget. Staged scope lists only cached changes; untracked discovery remains exclusive to diff scope.
  Date/Author: 2026-09-17, Codex.

- Decision: Address staged objects as `:./<repository-relative-path>` and represent scan candidates as `(source, path)` pairs.
  Rationale: The explicit relative index form cannot confuse a filename beginning with `0:` for Git's staged-entry selector. Source-aware candidates let default diff scope independently enumerate `HEAD`-to-index cached changes, index-to-worktree changes, and untracked files; identical pathnames from different sources remain separate so each content view reaches its matching added-line scan.
  Date/Author: 2026-09-17, Codex.

- Decision: Retain at most 100 finding details, stop after 1,000 processed findings, and cap each encoded scan-log record at 64 KiB.
  Rationale: High-match inputs must reach a prompt fail-closed decision without building attacker-proportional Python or JSON structures. The log records how many processed findings were omitted and whether detail collection was truncated; match loops enforce the scanner's global deadline, and rotation compares the active file plus the incoming encoded record before appending.
  Date/Author: 2026-09-17, Codex.

## Outcomes & Retrospective

Milestone 1 introduced a deterministic standard-library generator, its two-file explicit manifest, transactional write/check behavior, and the `send-event.py` pilot. Both generated scripts retain their previous runtime body with only the ownership header added. Generator CLI and transaction tests, aggregate-registry tests, both observability suites, and the shell installer fixture passed. A direct real-home install remains unverified because this environment's `/root/.agents/skills` destination is read-only; temporary-home installed-copy tests passed. At completion, summarize the number of maintained duplicate lines removed, generated outputs owned, drift defects fixed separately, validation results, generator usability, and the disposition of every deferred candidate. Compare renderer complexity against maintenance savings before recommending Phase 2.

Milestone 2 now owns six generated common and audit helpers. The renderer contract preserves each pre-generation helper body byte-for-byte after excluding the generated ownership header and executable shebang. Provider behavior remains explicit: GitHub has bounded incomplete-input handling and an audit mode prefix, Copilot has standard passive logging, and Gemini has its separate passive shadow configuration. The generator tests and all listed Copilot, GitHub, Gemini, and installer fixture suites passed. No behavior defect or unclassified drift was observed.

Milestone 3 now owns the two observability helpers. The generated runtime bodies preserve SQLite/WAL tracing, transcript finalization, NDJSON fallback, retention, locking, maintenance, and fail-open behavior; only the generated header was added. The eight named adapter expressions cover runtime identity, environment precedence, and the default home-directory log path. Generator, both observability, both startup, and both installer fixture suites passed. PowerShell installer tests passed with the expected junction skip. The direct real-home installer remains unavailable because `/root/.agents/skills` is read-only, so temporary-home installed-copy coverage is the available installed-behavior evidence.

Milestone 4 extraction now owns the two Tool Guardian scripts through one canonical policy and explicit Copilot and Gemini adapters. Four independent-review repair passes tightened authorization, parser completeness, structured-input handling, information disclosure, and Gemini audit writes. The current policy uses exact allowlist equality with only ASCII edge-space trimming; rejects control and escaped separators; denies every configured parser or structured-traversal overflow; scans recursively extracted decoded strings before serialized fallback; inspects complete remove, home-variable, Git global-option/refspec, and SQL forms; and exposes only category and severity for detected threats. Shared vectors and public provider envelopes cover compatibility punctuation, encoded, control-separated, and nested structured payloads, credential-bearing matches, concurrent Gemini logging, linked destinations, complete command forms, SQL comments, safe structured negatives, and fail-closed over-limit input. Independent security rereview approved commit `dd6d3f670b9181ab3ee73eaa48fb6785282a3db0` with no high-confidence blocker, so Milestone 4 is accepted.

Milestone 4 security-fix validation on 2026-09-17 passed Python compilation, shell syntax checks, `scripts/test-generate-hooks.py` (11 tests), both Tool Guardian suites, both startup suites, the shell installer fixture, and the PowerShell installer fixture with its expected unsupported-junction skip. `scripts/generate-hooks.py --check` reported all 12 outputs current, and `git diff --check` passed. The startup suites remain the available bounded-runtime evidence because this family has no separate numeric latency benchmark.

Milestone 4 second-repair validation at 2026-09-17 06:46Z passed the same complete matrix after the SQL lexer also proved quoted table identifiers remain detectable and public envelopes proved parser overflow denies before allowlist authorization and even in warning mode: Python compilation, shell syntax checks, all 11 generator tests, both Tool Guardian public-envelope suites, both bounded startup suites, shell and PowerShell installer fixtures, generator freshness for all 12 outputs, and diff hygiene. The PowerShell fixture again reported only its expected unsupported-junction skip. The independent security rereview remains the sole acceptance gate.

Milestone 4 third-repair validation at 2026-09-17 06:56Z passed Python compilation, shell syntax checks, all 11 generator tests, both Tool Guardian public-envelope suites, both bounded startup suites, shell and PowerShell installer fixtures, generator freshness for all 12 outputs, and diff hygiene. Public regressions cover fullwidth semicolon, ampersand, pipe, dollar, single and double quote, and backtick equality collisions; quoted and unquoted common home-variable targets; and Git global flag plus option/value forms. The PowerShell fixture reported only its expected unsupported-junction skip. Final independent security rereview remains the acceptance gate.

Milestone 4 fourth-repair validation at 2026-09-17 07:05Z passed Python compilation, shell syntax checks, all 11 generator tests, both Tool Guardian public-envelope suites, both bounded startup suites, shell and PowerShell installer fixtures, generator freshness for all 12 outputs, and diff hygiene. Shared and provider regressions prove nested decoded unfiltered queries are denied, safe filtered structured queries remain allowed, duplicate findings from decoded plus serialized views collapse to one category/severity record, and overdeep structured input fails at the traversal boundary before fallback serialization. The PowerShell fixture reported only its expected unsupported-junction skip. Independent security rereview remains the acceptance gate.

Milestone 5 extraction now owns the two secret scanners through one canonical policy plus explicit Copilot and Gemini response/runtime adapters. The generated scripts retain provider-specific denial envelopes, reason text, session keys, default log paths, working-directory selection, audit behavior, fail-closed block mode, and warn-mode no-op compatibility. Copilot's missing-Git and audit-initialization branches now use its single response renderer. The scanner uses the same build-time canonical structured exact allowlist implementation as Tool Guardian, with self-contained generated runtime files. Shared fake-credential vectors cover all five patterns, negative boundaries, credential and environment paths, binary/text classification, line numbering, redaction, exact allowlists, and prompt-disabled five-second Git subprocess calls; public provider suites cover expected block decisions and stable missing-Git/audit failure reasons.

Milestone 5 extraction validation at 2026-09-17 07:22Z passed Python compilation, 13 generator tests, both secret-scanner suites, both Tool Guardian suites, both startup suites, the shell installer fixture, and the PowerShell installer fixture with its expected unsupported-junction skip. Generator write/check owns 14 outputs, rejects mismatched secret-scanner provider targets, and left the Tool Guardian files byte-current when the shared allowlist source was extracted. Independent security review remains the sole acceptance gate.

Milestone 5 security repair at 2026-09-17 07:54Z closes SEC-001 through SEC-006 in the canonical renderer and regenerated provider scripts. Git failures no longer become clean scans; Git filenames and unified diffs use unambiguous byte-oriented formats; credential paths and bounded ASCII tokens are inspected even for binary data; candidate reads are contained, descriptor-first, no-follow, regular-file-only, and resource-bounded; and logs use owner-only directories/files, link rejection, mode-preserving rotation, and a bounded POSIX/Windows lock. Public provider regressions prove block denial and warn no-op for Git errors, unsafe or oversized candidates, and lock timeout, while both providers cover unusual filenames, `++` added lines, and NUL-containing credential files. Final validation passed Python compilation, shell syntax checks, all 19 generator tests, both secret-scanner suites, both Tool Guardian suites, both startup suites, shell and PowerShell installer fixtures, generator freshness for all 14 outputs, and diff hygiene. The PowerShell fixture reported only its expected unsupported-junction skip. Milestone status and acceptance remain unchanged pending independent security rereview.

Milestone 5 second security repair at 2026-09-17 08:17Z closes the rereview's SEC-001, SEC-004, SEC-007, and SEC-008 findings. A failed initial probe now checks ancestor repository markers before deciding whether a directory is outside Git; every Git child receives literal pathspec semantics; stdout is read only to the configured cap and an overflowing child is terminated; every runtime Git call receives the remaining portion of one deadline created at `main()` entry; and staged scope no longer appends untracked files. Both provider suites prove corrupt initial probes deny or no-op by mode, real committed pathspec-shaped filenames are scanned, and staged changes ignore unrelated untracked fake credentials. Shared tests prove overflowing children terminate promptly and two individually successful slow Git calls exhaust the same deadline. Final validation passed Python compilation, shell syntax checks, all 20 generator tests, both secret-scanner suites, both Tool Guardian suites, both startup suites, shell and PowerShell installer fixtures, generator freshness for all 14 outputs, and diff hygiene. The PowerShell fixture reported only its expected unsupported-junction skip. Milestone status and acceptance remain unchanged pending independent security rereview.

Milestone 5 third security repair at 2026-09-17 08:31Z closes SEC-009 and SEC-010. Staged blob size and content reads now use the unambiguous `:./<path>` index-object form, while default diff scope separately enumerates cached changes against `HEAD`, worktree changes against the index, and untracked files. Candidate identity includes the source as well as the path, and added-line parsing uses the corresponding cached or worktree diff. Both provider suites prove a staged `0:`-prefixed filename containing a dynamically constructed fake token is scanned and a fake token that exists only in the index remains detectable after the worktree is restored to `HEAD`. Shared generated-code tests prove identical cached and worktree pathnames remain separate and pin the exact index-object arguments. Final validation passed Python compilation, shell syntax checks, all 20 generator tests, both secret-scanner suites, both Tool Guardian suites, both startup suites, shell and PowerShell installer fixtures, generator freshness for all 14 outputs, and diff hygiene. The PowerShell fixture reported only its expected unsupported-junction skip. Milestone status and acceptance remain unchanged pending independent security rereview.

Milestone 5 fourth security repair at 2026-09-17 08:48Z closes SEC-011. Finding processing now retains at most 100 redacted details and short-circuits at 1,000 processed findings while recording the known omitted-detail count and truncation state. The global scanner deadline is checked inside line, pattern, and match loops and immediately before logging; log-lock waits also honor the smaller remaining global budget. Audit records are encoded and rejected above 64 KiB, and rotation compares the existing file size plus the incoming record before append. Both provider suites prove a 10,000-match staged fake-token input returns a provider-correct denial within eight seconds, retains at most 100 redacted details, reports omitted findings, rotates a nearly full 64 KiB log, and keeps the active record bounded. Shared tests independently prove incoming-record-aware rotation and oversized-record rejection. Final validation passed Python compilation, shell syntax checks, all 20 generator tests, both secret-scanner suites, both Tool Guardian suites, both startup suites, shell and PowerShell installer fixtures, generator freshness for all 14 outputs, and diff hygiene. The PowerShell fixture reported only its expected unsupported-junction skip. Milestone status and acceptance remain unchanged pending independent security rereview.

## Context and Orientation

Repository root is `/Users/adam/dev/skills`. Run every command in this plan from that directory unless a step says otherwise.

A hook family is one logical behavior emitted for multiple providers. A provider adapter is the small provider-specific portion of that behavior, such as Copilot's `permissionDecision` response versus Gemini's `decision` response. A generated output is a checked-in Python script under a provider directory. It is executable runtime source, but humans change its canonical family renderer rather than the output itself. Freshness means the bytes produced from canonical sources exactly match the checked-in output bytes.

Current provider areas are:

- `.copilot/hooks/scripts/` for installed Copilot hooks.
- `.gemini/hooks/scripts/` for Gemini hooks.
- `.github/hooks/scripts/` for repository-local Copilot and GitHub hook behavior.
- `.codex/hooks/` for Codex hooks. Codex is outside this phase.

General hook contracts live in `.agents/instructions/hooks.md`. Source auto-ingest contracts live in `.agents/instructions/hooks-auto-ingest.md`. Observability contracts live in `.agents/instructions/hooks-observability.md`. CLI and helper-script rules live in `.agents/instructions/scripts.md`. Test commands live in `.agents/memory/testing/hooks.md`, `.agents/memory/testing/scripts.md`, and focused sibling files. `scripts/install.sh` copies maintained provider hooks into installed locations, while `.github/hooks/` executes from the checkout. Generated outputs must therefore stay checked in and keep their present paths.

The canonical tree to add is:

    hooks/
      families/
        __init__.py
        send_event.py
        common.py
        audit.py
        observability.py
        tool_guard.py
        scan_secrets.py
        auto_ingest.py
      __init__.py
      manifest.py
      providers.py

The generator and its tests will be:

    scripts/generate-hooks.py
    scripts/test-generate-hooks.py

`hooks/providers.py` defines immutable provider data and adapter source blocks. `hooks/manifest.py` defines the complete owned output map and executable modes. Each `hooks/families/*.py` module exposes a deterministic renderer for one family. `scripts/generate-hooks.py` is a thin CLI and transaction boundary; business rendering rules stay in family modules.

The exact Phase 1 target matrix is:

- `send_event`: `.copilot/hooks/scripts/send-event.py` and `.gemini/hooks/scripts/send-event.py`.
- `common`: `.copilot/hooks/scripts/helpers/common.py`, `.gemini/hooks/scripts/helpers/common.py`, and `.github/hooks/scripts/helpers/common.py`.
- `audit`: `.copilot/hooks/scripts/helpers/audit.py`, `.gemini/hooks/scripts/helpers/audit.py`, and `.github/hooks/scripts/helpers/audit.py`.
- `observability`: `.copilot/hooks/scripts/helpers/observability.py` and `.gemini/hooks/scripts/helpers/observability.py`.
- `tool_guard`: `.copilot/hooks/scripts/tool-guard.py` and `.gemini/hooks/scripts/tool-guard.py`.
- `scan_secrets`: `.copilot/hooks/scripts/scan-secrets.py` and `.gemini/hooks/scripts/scan-secrets.py`.
- `auto_ingest`: `.github/hooks/scripts/helpers/auto_ingest.py`, `.gemini/hooks/scripts/helpers/source_ingest.py`, `.github/hooks/scripts/auto-ingest-source.py`, `.gemini/hooks/scripts/auto-ingest.py`, `.github/hooks/scripts/inject-auto-ingest-context.py`, and `.gemini/hooks/scripts/inject-auto-ingest-context.py`.

The owning family migration also removes small duplication inside that boundary: repeated allowlist parsing in Tool Guardian and secret scanning, repeated Copilot secret-scanner denial construction, repeated auto-ingest manifest refresh sequences, and repeated auto-ingest audit wrappers. These removals happen in canonical sources and generated results, not through handwritten output edits.

Implementation is large enough to require subagent orchestration. The coordinator owns `hooks/providers.py`, `hooks/manifest.py`, `scripts/generate-hooks.py`, `scripts/test-generate-hooks.py`, `scripts/test-all.py`, this ExecPlan, the ADR, and final documentation. A family worker owns only its assigned `hooks/families/<family>.py`, the generated provider outputs listed for that family, and that family's targeted test edits. Family migrations run sequentially because they share provider outputs and behavior contracts. A separate validation or security-review agent remains read-only and reports findings before the coordinator accepts a milestone. Workers must be told that other agents share the worktree and must not revert others' edits.

## Plan of Work

All implementation follows test-first development. Before changing a family, add or identify characterization tests that fail when the current provider-specific behavior changes. First prove generator behavior with failing tests, then implement the smallest generator behavior to pass, then refactor canonical sources without weakening provider tests.

### Milestone 1: Build the generator and prove it with `send-event.py`
Status: done
Acceptance: met (repository and temporary-home installed-copy proof; real-home install unavailable in this environment)

Add `hooks/providers.py` with immutable provider identifiers and explicit adapter data. Add `hooks/manifest.py` with a `GeneratedTarget` record containing family name, provider name, repository-relative output path, and mode `0o755`. Reject duplicate output paths and paths outside the declared provider hook trees. Add `hooks/families/send_event.py` as the first renderer.

Add `scripts/generate-hooks.py` using `argparse` with abbreviation disabled and a required mutually exclusive `--write` or `--check` action. Both `-h` and `--help` exit `0`. Put examples near the start of help. Bare invocation prints concise help, performs no writes, and exits `2`. Do not add prompts, color, animation, configuration files, environment-controlled behavior, JSON mode, version output, family selection, or new dependencies.

The CLI uses these stable exits: `0` for a successful write or a fresh check, `1` when `--check` finds stale or missing outputs, `2` for usage, invalid canonical source, rendering, validation, lock, or filesystem failures, and `130` for Ctrl-C. Standard output contains concise primary results and changed or stale paths. Standard error contains warnings, progress, and errors. Error text names the affected path or input and states remediation when known. The CLI never accepts secrets.

Render all declared outputs into memory before any write. Validate UTF-8, LF line endings, the shebang, the exact generated header, Python syntax with `compile`, unique contained output paths, executable mode, and absence of undeclared provider paths. Resolve repository root from `Path(__file__)`, not caller working directory. Refuse output files or parent components that are symbolic links, Windows junctions, or reparse points. Do not follow paths outside the repository.

`--check` must not create files, directories, locks, or metadata. It compares expected bytes and modes against disk, reports every stale or missing path, and reports any file carrying this generator's ownership header that is no longer declared. It never deletes such a file.

`--write` takes a bounded exclusive lock. Stage every file beside its destination, flush and sync staged content, then replace outputs atomically. Preserve original bytes and modes until every replacement succeeds. On replacement failure or Ctrl-C, restore every replaced output atomically and remove all stage and lock artifacts. Validate all sources and targets before taking the first mutating step. A second write must report no changes and leave bytes and metadata stable.

Generated files place this shape immediately after the shebang, with the concrete canonical source path substituted:

    # Generated from hooks/families/send_event.py by scripts/generate-hooks.py. Do not edit.

Add `scripts/test-generate-hooks.py`. Test `-h`, `--help`, bare invocation, mutually exclusive actions, exit codes, stream separation, no ANSI escapes, path containment, link and reparse rejection where supported, no-write checking, missing and stale outputs, undeclared owned outputs, syntax rejection before writes, exact generated headers, executable modes, deterministic rendering, idempotent writes, lock timeout, transaction rollback, Ctrl-C cleanup, and invocation from a directory outside the checkout. Tests must prove `--check` leaves a recursive filesystem snapshot unchanged.

Register `("python3", "scripts/test-generate-hooks.py")` in `scripts/test-all.py`. Generate both `send-event.py` outputs. Apart from the ownership header, their runtime code must match current bytes. Run the generator suite, both provider observability suites because `send-event.py` enters observability capture, and installer tests.

This milestone is accepted when `--check` detects a manually stale pilot output without writing, `--write` repairs it transactionally, a second write is a no-op, existing provider and installer tests pass, and a direct installed-copy smoke test still consumes JSON and emits `{}`.

### Milestone 2: Generate common and audit helpers
Status: done
Acceptance: met

Add `hooks/families/common.py` and `hooks/families/audit.py`. Preserve all current differences explicitly in `hooks/providers.py` or named adapter blocks. Important differences include GitHub's bounded incomplete-input wait, Copilot and Gemini observability capture integration, passive logging behavior, Windows path conversion, provider environment names, default audit paths, shadow log semantics, permissions, locking, and rotation.

Before replacing outputs, add characterization cases for open stdin, multiline JSON, malformed and incomplete prefixes, buffered trailing input, UTF-8 output under non-UTF-8 host encodings, Windows path conversion, command lookup, audit lock timeouts, rotations, passive shadow modes, and `0o600` audit files. Generate the six target helper files and keep all public function names required by current imports.

Run startup, RTK, observability, auto-ingest, OKF, Tool Guardian, secret-scanner, and installer suites for all affected provider surfaces. Run mypy on same-named provider modules separately if type checking is part of the current suite; never pass duplicate module names in one mypy command.

After behavior-preserving migration, record every provider difference discovered. If evidence proves a security or correctness defect, add a failing regression test and fix it in a separate task or diff before Milestone 3. Record intentional and low-risk differences without blocking progress.

Acceptance requires byte-equivalent behavior at public stdin/stdout seams, current executable and audit modes, all targeted suites passing, and no direct edits needed in generated outputs.

### Milestone 3: Generate observability helpers
Status: done
Acceptance: met (repository and temporary-home installed-copy proof; real-home install unavailable in this environment)

Add `hooks/families/observability.py` and render Copilot and Gemini helpers. Preserve runtime name, environment-variable precedence, default paths, event normalization, transcript behavior, SQLite schema and WAL use, session and span finalization, maintenance, NDJSON fallback, retention, locking, corruption recovery, and fail-open control-flow behavior. The current files align almost completely; represent the small runtime differences as named provider data rather than hidden conditionals.

Add a regression test that renders both outputs and asserts the allowed difference set. An unexpected new difference must fail with a useful message. Preserve the hot-path latency expectations documented in `.agents/instructions/hooks-observability.md`; generation must not introduce runtime template loading or new imports.

Run `bash scripts/test-hooks-observability.sh`, `bash scripts/test-gemini-hooks-observability.sh`, `bash scripts/test-hooks-startup.sh`, `bash scripts/test-gemini-hooks-startup.sh`, `bash scripts/test-install.sh`, and PowerShell installer tests when `pwsh` is available. Perform installed-copy smoke tests only after `./scripts/install.sh`, because live runtimes do not execute repository source copies.

Classify drift and handle confirmed defects separately as defined above. Acceptance requires matching database, transcript, fallback, maintenance, and installed behavior with no regression in measured hot-path budgets.

### Milestone 4: Generate Tool Guardian and remove owned policy duplication
Status: done
Acceptance: met (full extraction validation and independent security approval at `dd6d3f670b9181ab3ee73eaa48fb6785282a3db0`)

Add `hooks/families/tool_guard.py`. Put shared threat detectors, encoded pattern definitions, threat aggregation, and allowlist behavior in one canonical source. Keep Copilot and Gemini payload extraction, decision envelopes, audit behavior, default paths, and fail-closed top-level handling in explicit provider adapters. Replace the duplicated `parse_allowlist_csv` substring behavior with one structured, exact `parse_allowlist` and `allowlist_contains` definition used in both generated scripts; generated files remain self-contained.

Before extraction, add provider-neutral matcher vectors covering every current positive, negative, boundary, multiline, encoded-threat, allowlist, malformed-input, and unexpected-exception case. Keep provider-envelope assertions separate. Avoid placing raw dangerous command strings directly in maintenance tool payloads; construct exact threat fixtures dynamically as required by `.agents/memory/known-issues/hooks.md`.

Run `bash scripts/test-hooks-tool-guard.sh`, `bash scripts/test-gemini-hooks-tool-guard.sh`, startup suites, installer suites, generator tests, and existing latency checks. Then assign an independent security reviewer read-only ownership of canonical policy, rendered outputs, failure paths, allowlist boundaries, and tests. Resolve every high-confidence security finding before acceptance. A confirmed behavior defect receives its own regression test and separate follow-up diff.

Acceptance requires identical detector outcomes across providers for shared vectors, correct provider-specific responses, fail-closed malformed and exception paths, unchanged latency compliance, and approved security review.

### Milestone 5: Generate secret scanners and remove owned response duplication
Status: in progress
Acceptance: not met

Add `hooks/families/scan_secrets.py`. Canonicalize Git probing, repository and candidate-file discovery, diff-added-line scanning, credential path rules, binary/text checks, redaction, allowlists, log rotation, findings construction, and mode normalization. Preserve provider-specific denial envelopes, payload keys, session fields, log paths, and audit behavior. Use the same canonical allowlist implementation chosen in Milestone 4 without creating a runtime cross-provider import.

Replace Copilot's inline missing-Git and audit-initialization denial dictionaries with the canonical response renderer so one maintained definition owns the envelope. Preserve reason text and exit `0` for expected block decisions.

Add shared detection vectors plus provider-specific public stdin/stdout tests. Retain stalling POSIX `git` and Windows `git.cmd` cases, prompt-disabled Git environment, warn-mode no-op behavior, block-mode fail-closed behavior, and sanitized logs. Use unmistakably fake credentials in fixtures.

Run `bash scripts/test-hooks-secrets-scanner.sh`, `bash scripts/test-gemini-hooks-secrets-scanner.sh`, startup suites, installer suites, and generator tests. Assign an independent security reviewer to the canonical patterns, Git subprocess boundary, output envelopes, logging, timeouts, and rendered files. Resolve high-confidence findings before acceptance, with behavior fixes separated from extraction.

Acceptance requires shared findings for equivalent inputs, provider-correct output, bounded Git operations, fail-closed block mode, warn-mode compatibility, stable log behavior, and approved security review.

### Milestone 6: Generate auto-ingest engines and wrappers
Status: open
Acceptance: not met

Add `hooks/families/auto_ingest.py`. Canonicalize source records, source hashing, frontmatter parsing, scaffold detection, blocking state, manifest reconciliation, rename and orphan handling, summary scaffolding, locking, atomic persistence, block-reason construction, and context rendering. Preserve GitHub's repository-root APIs and Gemini's payload-derived roots as provider adapters. Keep existing filenames even though GitHub uses `helpers/auto_ingest.py` and Gemini uses `helpers/source_ingest.py`.

Generate startup and prompt/final-response wrappers from canonical orchestration plus explicit provider adapters. Consolidate each repeated lock-scan-load-reconcile-save sequence into one generated helper operation. Consolidate repeated fail-open audit wrappers without changing failure policy. Preserve Gemini startup-only filtering, `BeforeAgent` and `AfterAgent` responses, stop-loop handling, GitHub transformed-prompt preservation, dynamic helper loading, stop coordination, source-ingest-first ordering, manifest location, and missing-skill recovery.

Before migration, strengthen characterization around safe previous `summary_path` handling, exact draft frontmatter semantics, body-text marker exclusion, paths containing spaces, `#`, or `?`, startup-before-prompt ordering, missing `cwd`, pending gates, simultaneous source-ingest and OKF failure reasons, and final-response backstops.

Run `bash scripts/test-hooks-auto-ingest.sh`, `bash scripts/test-gemini-hooks-auto-ingest.sh`, both OKF suites, both startup suites, installer suites, and generator tests. Because Gemini `AfterAgent` delivery is version-sensitive, repository tests prove envelopes only; retain the documented requirement for a live deployed-version probe before claiming live enforcement.

Classify drift and fix confirmed defects separately. Acceptance requires unchanged manifest bytes for equivalent inputs, matching pending-state decisions, preserved provider envelopes and ordering, safe path handling, and no cross-provider runtime imports.

### Milestone 7: Complete validation, documentation, and Phase 2 reassessment
Status: open
Acceptance: not met

Run the full maintained suite through `python3 scripts/test-all.py`. Run `python3 scripts/generate-hooks.py --check` before and after the full suite and confirm both return `0` without changing `git status`. Run `./scripts/install.sh` before live smoke tests, then verify installed scripts match checked-in generated sources and remain executable. Run `pwsh -NoProfile -File scripts/test-install.ps1` on a host with PowerShell 7; document any platform check that cannot run locally.

Update `README.md` with generator write/check commands and generated-file ownership. Update `.agents/memory/ARCHITECTURE.md` and `.agents/memory/FILE_MAP.md` for the new top-level `hooks/` source area. Update `.agents/instructions/hooks.md`, `.agents/instructions/scripts.md`, focused auto-ingest and observability instructions, `.agents/memory/API_MAP.md`, `.agents/memory/TESTING_STRATEGY.md`, and focused testing files with verified final behavior. Use `update-agent-docs` once after all code and delegated work finishes, then apply `okf-authoring` to changed `.agents/instructions/` and `.agents/memory/` Markdown. Keep `.agents/memory/INDEX.md` synchronized if a memory file is added, removed, or renamed.

Produce a Phase 2 recommendation for required-skill loaders, RTK forwarders, OKF adapters, audit-versus-observability primitives, YAML parser variants, and any newly observed candidates. Apply this admission test: at least two runtime outputs; meaningful shared logic rather than boilerplate; provider differences fit explicit adapters; runtime-local files remain necessary; and canonical generation removes more maintained complexity than the renderer adds. Do not automatically schedule every deferred candidate.

Record final duplicate-line reduction, generator source size, number of provider adapters, stale-output incidents caught, behavior defects separated and fixed, validation results, and any usability friction. Acceptance requires every approved family generated, no manual output edits, all available suites and security reviews passing, current documentation, classified drift, and a reasoned Phase 2 recommendation.

## Concrete Steps

Run commands from `/Users/adam/dev/skills`. Prefix shell commands with `rtk` unless the command must mutate files and RTK would change its behavior. The generator's write mode is itself the intended mutation, so run it directly; use RTK for reads, checks, tests, Git, and summaries.

Start each milestone by checking state:

    rtk git status --short
    rtk proxy python3 scripts/generate-hooks.py --check

During Milestone 1, the second command is expected to be unavailable until the CLI exists. After its tests fail for the intended missing behavior, implement the generator and run:

    python3 scripts/generate-hooks.py --write
    rtk proxy python3 scripts/generate-hooks.py --check
    rtk proxy python3 scripts/test-generate-hooks.py

Expected successful check output is concise and stable, for example:

    Generated hooks are current (2 files).

A stale check prints affected repository-relative paths to standard output and exits `1` without changing them. Usage or validation failure prints an actionable diagnostic to standard error and exits `2`.

After each family migration, run its commands from the milestone plus:

    rtk proxy python3 scripts/generate-hooks.py --check
    rtk git diff --check
    rtk git status --short

Before live installed validation:

    ./scripts/install.sh

At Phase 1 completion:

    rtk proxy python3 scripts/generate-hooks.py --check
    rtk proxy python3 scripts/test-all.py
    rtk git diff --check
    rtk git status --short

If `rtk` is unavailable, stop and report it instead of silently running raw alternatives. If PowerShell 7 or a supported live Gemini CLI is unavailable, record that exact unverified platform evidence in this plan and the final handoff.

## Validation and Acceptance

Generator CLI acceptance follows the applicable local source guidance in `.agents/sources/12-factor-cli-apps.md`, `.agents/sources/cli-design-guidelines.md`, and `.agents/sources/clig-dev.md`:

- Use `argparse`; disable ambiguous abbreviations.
- `-h` and `--help` exit `0` and describe purpose, flags, outputs, exit codes, and common examples near the beginning.
- Bare invocation explains both actions, performs no writes, and exits `2`.
- Exactly one of `--write` and `--check` is required.
- Success exits `0`; stale check exits `1`; usage or execution failure exits `2`; Ctrl-C exits `130`.
- Standard output contains primary results. Standard error contains warnings, progress, and diagnostics.
- No prompts, ANSI colors, animations, secrets, hidden configuration, or network access exist.
- Validate every render and output path before writes.
- `--check` creates, modifies, and deletes nothing, including temporary files and locks.
- Write mode reports changed paths, is deterministic, and is idempotent.
- Errors identify the problem and affected path and give remediation where known.

Family acceptance requires more than syntax. For every generated script, compare behavior through its public JSON stdin/stdout seam, provider-specific event and decision envelope, expected exit status, stderr discipline, file modes, install result, failure policy, and documented latency boundary. Existing provider suites remain authoritative unless characterization exposes an undocumented contradiction; resolve contradictions in the Decision Log before changing behavior.

Security-family acceptance additionally requires provider-neutral threat or secret-detection vectors, provider-specific envelope tests, malformed-input and unexpected-exception coverage, fail-closed block behavior, bounded subprocesses, safe logs, and independent security review with no unresolved high-confidence finding.

Phase 1 is complete only when all seven milestones show `Status: done` and `Acceptance: met`, their Progress entries are checked with timestamps, generator freshness passes, the full available suite passes, generated outputs need no manual edits, all drift is classified, confirmed blocking defects are resolved separately, documentation is current, and deferred candidates have a Phase 2 recommendation.

## Idempotence and Recovery

Rendering is deterministic. Repeated `--check` calls are read-only. Repeated `--write` calls produce no byte or mode changes after the first successful run. Family renderers depend only on checked-in canonical modules and explicit provider data; they do not read environment configuration or caller working directory.

Write mode stages and validates the complete output set before replacement. Preserve original bytes and modes until transaction completion. If staging fails, remove stages and leave outputs unchanged. If replacement fails, restore every already replaced file atomically, remove stages, release the bounded lock, print the failed path and recovery status, and exit `2`. If Ctrl-C arrives, report interruption immediately, perform bounded rollback and cleanup, and exit `130`; a repeated interrupt may skip slow cleanup, so the next run must detect and safely remove only generator-owned stale stage artifacts.

The generator never deletes a checked-in output. If `--check` reports an undeclared file with this generator's ownership marker, inspect its Git history and remove it through an explicit reviewed patch only when intended. Never broaden cleanup to a provider directory.

If a family migration fails validation, keep canonical and generated changes scoped to that family and restore the last known-good family diff. Do not weaken, delete, skip, or disable failing tests. Do not mix a behavior correction into the extraction retry. Record the failed approach and evidence in `Surprises & Discoveries` before trying a materially different renderer shape.

## Artifacts and Notes

The technical-debt audit measured these aligned-line baselines:

- Observability: 2,069 aligned lines out of 2,077 in each provider file.
- Secret scanning: 567 aligned lines across 595 Copilot and 577 Gemini lines.
- Tool Guardian: 312 aligned lines across 372 Copilot and 347 Gemini lines.
- Common helpers: 282 aligned Copilot/Gemini lines, with about 260 shared with GitHub.
- Audit helpers: 157 aligned Copilot/Gemini lines.
- Auto-ingest engine: 641 aligned lines across 678 GitHub and 698 Gemini lines.
- `send-event.py`: 21 byte-identical lines.

Use these numbers only as baseline evidence. Completion is based on maintained-source reduction and behavior proof, not maximizing deleted lines.

The architecture decision is recorded in `docs/adr/0004-generated-provider-hooks.md`. Do not supersede `docs/adr/0001-auto-ingest-runtime-shape.md`; generated canonical inputs preserve its runtime-local executable boundary.

## Interfaces and Dependencies

Use Python's standard library only. Do not add packages. The generator supports the Python versions already supported by repository scripts and Windows installer tests.

In `hooks/providers.py`, define an immutable provider record with stable fields needed by renderers. Keep fields semantic rather than exposing arbitrary textual replacements. A representative interface is:

    @dataclass(frozen=True)
    class Provider:
        name: str
        hook_root: PurePosixPath
        runtime_home_name: str

Provider-specific source blocks may use additional typed records per family when one generic record would become a bag of optional values.

In `hooks/manifest.py`, define:

    @dataclass(frozen=True)
    class GeneratedTarget:
        family: str
        provider: str
        output_path: PurePosixPath
        mode: int = 0o755

    def targets() -> tuple[GeneratedTarget, ...]: ...

The manifest owns only the explicit Phase 1 paths listed in Context and Orientation. It does not discover whole directories and does not delete anything.

Each module in `hooks/families/` exposes:

    def render(provider: Provider, target: GeneratedTarget) -> str: ...

`render` returns a complete Python file with LF endings, terminal newline, shebang, generated header, and readable provider-local implementation. It performs no I/O and reads no environment variables. If a family emits several distinct entrypoint shapes, expose named pure render functions and dispatch explicitly from the family module rather than using hidden mode flags.

In `scripts/generate-hooks.py`, keep rendering and validation callable from tests. Define interfaces equivalent to:

    def render_all(repo_root: Path) -> tuple[RenderedOutput, ...]: ...
    def check_outputs(repo_root: Path, outputs: tuple[RenderedOutput, ...]) -> CheckResult: ...
    def write_outputs(repo_root: Path, outputs: tuple[RenderedOutput, ...]) -> WriteResult: ...
    def main(argv: Sequence[str] | None = None) -> int: ...

Use immutable result records so the CLI layer formats output without mixing stream decisions into rendering or transactions. `render_all` and `check_outputs` are non-mutating. `write_outputs` is the only mutation boundary.

Do not make installers generate repository sources. `scripts/install.sh` and `scripts/install.ps1` continue copying checked-in provider-local files. Their tests must prove generated files install unchanged with executable modes.

Revision note, 2026-09-17: Initial ExecPlan created from the confirmed grilling design. It records canonical generation, explicit CLI behavior, transactional safety, migration order, validation, drift separation, security review, and Phase 2 reassessment.

Revision note, 2026-09-17: Completed Milestone 1. The pilot now renders the two provider-local `send-event.py` scripts; the generator test suite covers CLI, freshness, headers, output modes, path defenses, lock timeout, rollback, interruption cleanup, and external working directories. Targeted provider and installer fixture suites passed; the real-home install attempt is recorded above because its destination is read-only.

Revision note, 2026-09-17: Completed Milestone 2. Canonical common and audit renderers now own all six Copilot, Gemini, and GitHub helper outputs. Their runtime bodies are characterized against the pre-generation sources, with only the generator-required executable shebang and ownership header added. Targeted generator, provider hook, and installer fixture suites passed.

Revision note, 2026-09-17: Completed Milestone 3. Canonical observability rendering now owns the Copilot and Gemini helpers through eight exact, tested provider adapter expressions. Targeted generator, observability, startup, shell installer, and PowerShell installer fixture suites passed; direct real-home installation remained blocked by the existing read-only `/root/.agents/skills` destination.

Revision note, 2026-09-17: Completed the Milestone 4 extraction and validation portion. Canonical Tool Guardian policy now renders both provider-local scripts; shared matcher and allowlist vectors plus separate envelope tests pass, including malformed and unexpected-exception fail-closed paths. The milestone remains in progress until the independent security review is approved.

Revision note, 2026-09-17: Resolved the first Milestone 4 independent review's SEC-001, SEC-002, and SEC-003 findings in a separate TDD fix. Structured exact allowlists, bounded equivalent-syntax detection, redacted threat excerpts, and hardened Gemini logging now have shared and public-provider regressions. The milestone remains in progress until the independent rereview approves the fixes.

Revision note, 2026-09-17: The first fix did not satisfy security rereview. A second isolated TDD repair now preserves and rejects allowlist separators, denies parser-bound overflow, covers every remove operand plus normalized executable and full Git-refspec forms, lexes SQL comments, and removes threat evidence from responses and audit logs. Acceptance remains pending another independent rereview.

Revision note, 2026-09-17: A third isolated TDD repair removes NFKC from allowlist equality, proves fullwidth shell punctuation cannot collide with configured ASCII text, protects common home-variable removal targets, and parses Git global options before `push`. Milestone 4 remains in progress pending final independent rereview.

Revision note, 2026-09-17: A fourth focused TDD repair recursively extracts bounded string values from object-valued tool arguments before compact-JSON fallback, closing the nested unfiltered-query bypass while retaining safe structured negatives. Milestone 4 remains in progress pending independent rereview.

Revision note, 2026-09-17: Independent security rereview approved Milestone 4 at `dd6d3f670b9181ab3ee73eaa48fb6785282a3db0` with no high-confidence blocker. Progress, outcome, status, and acceptance are now synchronized as done and met.

Revision note, 2026-09-17: Completed the Milestone 5 extraction and targeted validation portion. One canonical secret-scanner policy now renders both provider-local scripts, the exact allowlist source is shared at generation time across both security families, shared fake-credential vectors and provider public-envelope regressions pass, and acceptance remains pending independent security review.

Revision note, 2026-09-17: Resolved the first Milestone 5 independent review's SEC-001 through SEC-006 findings in a separate TDD repair. Strict Git error propagation, unambiguous byte-oriented Git parsing, binary credential scanning, descriptor-first bounded candidate reads, owner-only no-follow logs, and bounded cross-platform log locking now have shared and public-provider regressions. Milestone 5 remains in progress pending independent security rereview.

Revision note, 2026-09-17: The first Milestone 5 repair did not satisfy security rereview. A second isolated TDD repair distinguishes corrupt repositories from verified non-repositories, forces literal Git pathspecs, terminates streaming-output overflow, shares one entry-time deadline across Git calls, and keeps untracked discovery out of staged scope. Milestone 5 remains in progress pending independent rereview.

Revision note, 2026-09-17: A third isolated Milestone 5 TDD repair disambiguates staged filenames from Git's stage-selector syntax and preserves cached, worktree, and untracked candidate identity throughout default diff scanning. Milestone 5 remains in progress pending independent rereview.

Revision note, 2026-09-17: A fourth isolated Milestone 5 TDD repair bounds finding retention and processing, enforces the global deadline inside match loops and at logging, caps encoded audit records, and makes rotation account for the incoming record. Milestone 5 remains in progress pending independent rereview.
