# Concept Identity and Links

**Type:** grilling
**Status:** closed
**Blocked By:** bundle-publication-and-lifecycle.md, concept-profile-and-taxonomy.md
**Research Dir:** N/A

## Question

How will the projection assign stable concept paths and identities, map current files and headings, handle moves or renames, represent redirects or supersession, and distinguish navigation, dependency, provenance, ownership, and mandatory-read relationships?

---

<!-- Resolution will be appended here -->

## Resolution

Adopt stable logical OKF paths as concept identities. Author every identity explicitly in a committed `.agents/okf-profile.json`; never derive an existing identity again from its canonical source path, heading, title, type, or area. This registry is a canonical producer input, while `.agents/okf/.projection-manifest.json` remains generated freshness evidence.

Paths are bundle-root-relative, lowercase ASCII kebab-case segments ending in exactly one `.md`. Reject empty segments, `.` and `..`, concept paths whose filename is the reserved `index.md` or `log.md`, and all case-folded collisions. Organize the initial paths by stable domain and topic rather than by concept type. The emitted file lives below `.agents/okf/`; paths written below begin at the bundle root.

### Initial identity map

The current baseline contains 29 eligible canonical inputs and produces 42 concepts. Whole-file projections are:

| Canonical input | Concept path |
| --- | --- |
| `.agents/instructions/agents.md` | `/agents/instructions.md` |
| `.agents/instructions/powershell.md` | `/powershell/instructions.md` |
| `.agents/instructions/repo.md` | `/repo/instructions.md` |
| `.agents/instructions/scripts.md` | `/scripts/instructions.md` |
| `.agents/instructions/skills.md` | `/skills/instructions.md` |
| `.agents/memory/ARCHITECTURE.md` | `/repo/architecture.md` |
| `.agents/memory/CONVENTIONS.md` | `/repo/conventions.md` |
| `.agents/memory/FILE_MAP.md` | `/repo/file-map.md` |
| `.agents/memory/KNOWN_ISSUES.md` | `/repo/known-issues.md` |
| `.agents/memory/TESTING_STRATEGY.md` | `/repo/testing-strategy.md` |
| `.agents/memory/known-issues/powershell.md` | `/powershell/known-issues.md` |
| `.agents/memory/known-issues/scripts.md` | `/scripts/known-issues.md` |
| `.agents/memory/known-issues/skills.md` | `/skills/known-issues.md` |
| `.agents/memory/testing/hooks.md` | `/hooks/testing.md` |
| `.agents/memory/testing/powershell.md` | `/powershell/testing.md` |
| `.agents/memory/testing/scripts.md` | `/scripts/testing.md` |
| `.agents/memory/testing/skills.md` | `/skills/testing.md` |
| `.agents/memory/sources/12-factor-cli-apps-md.summary.md` | `/source-ingest/summaries/12-factor-cli-apps.md` |
| `.agents/memory/sources/cli-design-guidelines-md.summary.md` | `/source-ingest/summaries/cli-design-guidelines.md` |
| `.agents/memory/sources/clig-dev-md.summary.md` | `/source-ingest/summaries/clig-dev.md` |
| `.agents/memory/sources/copilot-hooks-ref-md.summary.md` | `/source-ingest/summaries/copilot-hooks-reference.md` |
| `.agents/memory/sources/gemini-hooks-best-practices-md.summary.md` | `/source-ingest/summaries/gemini-hooks-best-practices.md` |
| `.agents/memory/sources/gemini-hooks-md.summary.md` | `/source-ingest/summaries/gemini-hooks.md` |
| `.agents/memory/sources/gemini-hooks-writing-md.summary.md` | `/source-ingest/summaries/gemini-hooks-writing.md` |
| `.agents/memory/sources/llm-wiki-md.summary.md` | `/source-ingest/summaries/llm-wiki.md` |
| `.agents/memory/sources/vscode-agent-hooks-md.summary.md` | `/source-ingest/summaries/vscode-agent-hooks.md` |

Split `.agents/instructions/hooks.md` as follows. Its `Official References` section supplies `sources` metadata to the applicable concepts rather than becoming a concept:

| Source headings | Concept path |
| --- | --- |
| `Shared Runtime Rules` | `/hooks/runtime-and-maintenance.md` |
| `Output Schemas & Exit Behavior`; `Copilot and VS Code compatibility` | `/hooks/output-and-compatibility.md` |
| `Repo-specific hook gotchas` | `/hooks/repository-issues.md` |
| `Validation route`; `Gemini-specific validator guidance` | `/hooks/validation.md` |

Split `.agents/memory/adrs/hooks.md` one concept per ADR:

| Source heading | Concept path |
| --- | --- |
| `ADR-001: Python-first operational hook surface` | `/hooks/decisions/adr-001-python-first-operational-hook-surface.md` |
| `ADR-002: Local structured observability via NDJSON emitter` | `/hooks/decisions/adr-002-local-structured-observability-via-ndjson-emitter.md` |
| `ADR-003: Hot-path hook subprocess safety` | `/hooks/decisions/adr-003-hot-path-hook-subprocess-safety.md` |
| `ADR-004: Parser strategy for required skills and diff scanning` | `/hooks/decisions/adr-004-parser-strategy-for-required-skills-and-diff-scanning.md` |
| `ADR-005: Hot-path latency budget` | `/hooks/decisions/adr-005-hot-path-latency-budget.md` |
| `ADR-006: Runtime-local auto-ingest scanners with prompt-time injectors and one shared repo manifest` | `/hooks/decisions/adr-006-runtime-local-auto-ingest-scanners-with-prompt-time-injectors-and-one-shared-repo-manifest.md` |
| `ADR-007: Pending-ingest gate blocks normal work until summaries are truly resolved` | `/hooks/decisions/adr-007-pending-ingest-gate-blocks-normal-work-until-summaries-are-truly-resolved.md` |
| `ADR-008: SQLite-backed hook observability with NDJSON fallback` | `/hooks/decisions/adr-008-sqlite-backed-hook-observability-with-ndjson-fallback.md` |

Split `.agents/memory/known-issues/hooks.md` using these exact heading sets:

- `/hooks/known-issues/source-ingestion.md`: `Directory Traversal risk via summary_path in auto-ingest manifest`; `Infinite loop/DoS on workspace via loose substring check of status: scaffold`; `Copilot CLI prompt rewrite runs before sessionStart auto-ingest`; `Pending ingest gate needs a real /ingest-source skill and a final-response backstop`.
- `/hooks/known-issues/development.md`: `Active Tool Guardian blocks hook self-edits and policy maintenance`; `Mypy Duplicate module error on same-named files`; `Bash nounset trap unbound variable errors`; `Relative import failures when executing helper scripts directly`; `Secret Scanning Hook Blocks Dummy Secrets in Test Files`; `Final-response hook uses AfterAgent, not AfterModel`; `RTK empty stdout on non-optimized command treated as invalid JSON`; `Tool Guardian Severe False Positive Blocks on Multiline Serialized File Operations`.
- `/hooks/known-issues/observability.md`: `Concurrency and Lock Failures with SQLite WAL/SHM side-files`; `Unbounded Stack Recursion and Crashes on Cyclical Payload Objects`; `SQLite Database Lock Starvation and Timeouts during Maintenance physical unlinks`; `Finalization Status Transition Race Condition in Session Finalizer`; `Stale finalization sessions need maintenance retry, not passive cleanup`; `Concurrent finalizers need per-session locking to avoid duplicate transcript merges`; `Path Traversal and Arbitrary File Deletion via Registry Backfills`; `Temporary File Leakage on Write or Serialization Failures`; `Premature Hook Capture Completion on Progress/Auxiliary Messages`.
- `/hooks/known-issues/platform-portability.md`: `Cross-Platform Import Errors and Missing fcntl on Non-POSIX Systems`; `Extensionless Command Execution Failures on Windows when shell=False`; `PowerShell Parser Error on $HOME in Command Hooks (Windows)`; `PowerShell Argument Splitting on $GEMINI_PROJECT_DIR (Windows)`; `POSIX Path Mapping Failures in Windows Subsystems (WSL / Git Bash)`; `CP1252 Charmap Codec Encoding Crashes on Windows Stdout`.

The registry records the first included heading as `x-agent-kb.source.anchor` and separately lists every selected section needed to reproduce a multi-section split. Heading order in the output follows canonical source order.

### Moves, replacements, and tombstones

A canonical file or heading move updates the registered `source.path` or `source.anchor` without changing the concept path. A title edit that preserves meaning also preserves identity. Content hashes may report likely moves for review but never modify registry identities automatically.

A material semantic replacement, merge, or split receives new concept identities. Keep a minimal concept at every replaced path with `status: deprecated` and a `superseded-by` relationship to one or more replacements; replacements carry the inverse `supersedes` relationship. Tombstones remain until an explicit profile-major change removes them. This is concept supersession, not an HTTP-style redirect.

### Typed relationships

Add optional `x-agent-kb.relationships` in `agent-kb@1.1.0`. Each entry contains exactly:

```yaml
- kind: requires
  target: /hooks/testing.md
```

`target` must be an internal, bundle-root-relative Markdown path beginning `/` and ending `.md`, with no URL, query, or fragment. Writers allow only `kind` and `target` in each record and only the closed kinds `depends-on`, `requires`, `governed-by`, `supersedes`, and `superseded-by`. Readers ignore unknown future kinds.

Relationship meanings are deliberately separate:

- Navigation uses generated indexes and ordinary Markdown links, not typed relationships.
- Provenance uses standard OKF `sources`, not typed relationships.
- `depends-on` is a relevance and traversal signal; it never forces loading by itself.
- `requires` contributes its target transitively to the mandatory load closure.
- `governed-by` points to the concept holding canonical policy; it does not force loading unless a separate `requires` edge or selector rule does so.
- Selecting a deprecated concept follows `superseded-by` to its current replacement or replacements. `supersedes` is the informational inverse.

Typed relationships are curated registry entries only. Never infer them from Markdown links, directory hierarchy, tags, names, or prose. Later selector and mandatory-context decisions may add reviewed entries.

Generation fails on an unknown kind, unknown record field, malformed or non-normalized target, self-link, duplicate edge, missing internal target, reserved-file target, asymmetric supersession pair, or a cycle in `requires`, `governed-by`, or supersession. `depends-on` cycles are allowed, and consumers deduplicate traversal.
