# OKF Linter and Provider Hooks Contract

**Type:** grilling
**Status:** closed
**Blocked By:** in-place-okf-document-contract.md
**Research Dir:** N/A

## Question

What exact files, OKF rules, repository extensions, links, and diagnostics must the linter validate, and at which GitHub Copilot CLI and Gemini CLI hook events can validation block invalid edits reliably without injecting context or duplicating the existing source-ingest hooks?

---

<!-- Resolution will be appended here -->

## Resolution

The repository adopts the following OKF linter and provider-hook contract.

### Authority, implementation surface, and command

- `scripts/lint-okf.py` is the single provider-neutral mechanical authority for OKF v0.2 conformance and this repository's stricter profile. Every invocation recursively scans both `.agents/instructions/` and `.agents/memory/`; there is no changed-file or single-bundle success mode.
- The human commands are `./scripts/lint-okf.py` on POSIX and `python scripts/lint-okf.py` on Windows. `--format json` exposes the same complete, deterministically sorted findings for hook adapters and automation.
- Exit `0` means both bundles conform, exit `1` means lint findings exist, and exit `2` means the linter could not establish a trustworthy result because of a parser, dependency, configuration, or internal failure.
- YAML is parsed with a vendored, safe, pure-Python copy of PyYAML 6.0.3 under `scripts/vendor/yaml/`. Record its license and the upstream sdist SHA-256 `d76623373421df22fb4cf8817020cbb7ef15c725b9d5e45f17e189bfc384190f`; do not fetch or install dependencies at lint or hook runtime.
- Keep provider envelopes in thin, separate adapters at `.github/hooks/scripts/lint-okf.py` and `.gemini/hooks/scripts/lint-okf.py`. They invoke the same normalized linter result and contain no document-profile logic. Register them only in the repository-local `.github/hooks/hooks.json` and `.gemini/settings.json`; `.copilot/hooks/hooks.json` and `.gemini/global-settings.json` do not own this repository-specific gate.
- Add focused suites at `scripts/test-okf-lint.sh`, `scripts/test-hooks-okf-lint.sh`, and `scripts/test-gemini-hooks-okf-lint.sh`, following the repository's existing hook-test conventions.

### Files and profile rules

- Every `.md` file beneath either bundle root is a concept. Files outside those roots, including immutable `.agents/sources/`, repo-local skills, JSON manifests, and migration planning documents, are not concepts.
- Exact lowercase `index.md` and `log.md` are forbidden at every depth in both bundles. Uppercase `.agents/memory/INDEX.md` and `.agents/memory/LOG.md` remain ordinary concepts.
- Every concept must be UTF-8 Markdown beginning with delimited YAML frontmatter whose top level is a mapping. Non-empty string `type` and `description` are required.
- Derive types by path: all instruction concepts are `Agent Instruction`; memory `INDEX.md` is `Knowledge Index`; memory `LOG.md` is `Source Ingestion Log`; root `KNOWN_ISSUES.md` plus `known-issues/**` are `Known Issue`; root `TESTING_STRATEGY.md` plus `testing/**` are `Testing Guidance`; `adrs/**` are `Architecture Decision`; `sources/**/*.summary.md` are `Source Summary`; and remaining memory concepts are `Agent Memory`.
- Validate the standard OKF metadata shapes used by the corpus, including `title`, `description`, `resource`, `tags`, `sources`, `generated`, `verified`, `status`, and `stale_after`. When `generated` is present it requires non-empty `by` and `at`; `verified` must be a list of `{ by, at }` events; all timestamp-valued fields require valid ISO 8601 datetimes with explicit UTC offsets.
- Stable lifecycle status is represented by omitting `status`. Explicit `status: stable`, legacy `status: scaffold`, legacy `status: verified`, and the migrated-away `coverage` field are blocking profile violations. Genuine `draft` and `deprecated` remain allowed. Other unknown fields remain valid and must not be rejected.

### Links, resources, and source summaries

- Validate inline Markdown links, reference definitions, images, top-level `resource`, and every `sources[].resource`. Ignore apparent links inside inline code, fenced code, and HTML comments.
- External URI schemes remain allowed. For repository-local destinations, strip query and fragment components, percent-decode the path, reject filesystem-absolute and bundle-root-style `/...` paths, resolve relative to the owning document, require the target to remain inside the repository, and require it to exist as a regular file.
- Fragment-only links are allowed. The linter does not validate heading anchors because their slug behavior is renderer-specific.
- For each draft or completed source summary, read `.agents/memory/sources/source-ingest-manifest.json` only as the existing structural source-to-summary binding. Require exactly one `sources` entry whose file-relative `resource` resolves to that entry's matching immutable `.agents/sources/` file.
- The linter never reconciles content hashes or manifest states, writes the manifest, scaffolds summaries, removes orphans, or otherwise duplicates source-ingest freshness behavior.

### Stable diagnostics

Human and JSON output carry the same diagnostic ID, repository-relative path, line, column, and message, sorted by path, location, then ID:

| ID | Meaning |
| --- | --- |
| `OKF001` | Unreadable or non-UTF-8 concept |
| `OKF002` | Missing or malformed frontmatter delimiters |
| `OKF003` | Invalid YAML or non-mapping frontmatter |
| `OKF004` | Missing, empty, or incorrectly typed required field |
| `OKF005` | Invalid standard metadata shape or value |
| `OKF006` | Invalid timestamp or missing explicit UTC offset |
| `OKF007` | Forbidden lowercase reserved path |
| `OKF101` | Path-derived type mismatch |
| `OKF102` | Repository-local destination escapes the repository |
| `OKF103` | Repository-local destination does not resolve to a file |
| `OKF104` | Source-summary provenance does not match the manifest binding |
| `OKF105` | Prohibited legacy field or lifecycle representation |
| `OKF900` | Parser, dependency, configuration, or internal linter failure |

Direct CLI output reports every finding. Hook messages show at most the first 20 sorted findings, remain below 8 KiB, and include the omitted count plus the exact platform-appropriate rerun command.

### Provider events and failure behavior

- Copilot registers the adapter for `postToolUse`, `agentStop`, and `subagentStop`. Known editor and shell tool names receive immediate post-tool lint through provider-specific matchers verified against the deployed CLI. A post-tool failure returns diagnostics through `additionalContext`; it does not deny or undo the completed tool.
- At `agentStop` and `subagentStop`, any lint finding or `OKF900` returns exit `0` with `{ "decision": "block", "reason": "..." }`. Recheck on every forced continuation while invalid. The contract explicitly accepts Copilot's fail-open timeout behavior and host override after eight consecutive blocks; it does not claim an absolute filesystem invariant.
- Gemini registers the adapter for `AfterTool` and `AfterAgent`. Known mutation tools, initially including `write_file`, `replace`, and `run_shell_command`, are capability-tested in the deployed CLI. `AfterTool` returns exit `0` with `{ "decision": "deny", "reason": "..." }` when lint fails; this hides/replaces the tool result but does not roll back its filesystem effects.
- Gemini `AfterAgent` returns `decision: deny` for the first invalid completion so the agent receives one correction turn. If `stop_hook_active` is already true and lint still fails, return `continue: false` with a concise stop reason rather than create an unbounded retry loop.
- Both providers use a 10-second hook timeout. Adapters catch malformed input, missing parser/runtime resources, and unexpected exceptions and translate them to provider-valid structured blocking output with exit `0`; stdout stays JSON-only. Timeouts remain subject to provider behavior and cannot be presented as fail-closed.
- No pre-tool prediction, automatic repair, rollback, prompt rewriting, document-content injection, selection, or runtime state is introduced. Immediate matcher coverage is best effort; the unconditional final full-corpus scan is authoritative.
- Source-ingest hooks remain separate and run before lint hooks on shared stop events. Acceptance must prove that simultaneous pending-ingest and OKF failures still block and preserve both reasons. If a deployed provider cannot merge them correctly, use one thin provider coordinator to combine the two existing validator results while keeping their helpers, state, diagnostics, and responsibilities separate.

### Acceptance and capability gates

- Unit and CLI fixtures cover a valid two-bundle corpus, every diagnostic ID, unknown-field acceptance, every path-derived type, standard metadata shapes, timestamp offsets, link/resource resolution, lifecycle states, and manifest-backed source-summary binding.
- Human output, JSON output, Copilot responses, and Gemini responses must contain identical normalized diagnostics for the same corpus. Tests also cover malformed hook input, `OKF900`, output truncation, retry state, subagent stops, and simultaneous source-ingest/lint failures.
- Existing Copilot and Gemini source-ingest regression suites remain green, proving the linter neither replaces nor duplicates ingestion behavior.
- Live deployed-CLI probes must demonstrate each configured mutation matcher, Copilot `agentStop` and `subagentStop` behavior, and Gemini `AfterTool` and `AfterAgent` behavior. Record tested CLI versions, but gate on observed capability rather than an assumed version string.
- The reported open Gemini `AfterAgent` reliability issue is a release blocker: if the target CLI does not fire the configured event and reject an invalid final response, the in-place migration cannot be enabled or claimed complete. The same rule applies to any required Copilot stop behavior that fails its live probe.
- Record full-corpus lint duration during validation; correctness and the 10-second provider timeout are hard requirements, while no machine-dependent sub-second benchmark is a release gate.

These hooks enforce representation only. They add diagnostic correction messages when needed but never inject repository knowledge, and they preserve the existing `AGENTS.md` → `.agents/memory/INDEX.md` loading path.
