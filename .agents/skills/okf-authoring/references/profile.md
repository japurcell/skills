# Repository OKF Profile

`.agents/instructions/` and `.agents/memory/` are separate physical bundles. A concept keeps its existing bundle-relative path and its identity is that path without `.md`. Exact lowercase `index.md` and `log.md` are reserved and prohibited; uppercase `INDEX.md` and `LOG.md` remain ordinary concepts.

Every canonical Markdown concept has parseable YAML frontmatter with non-empty string `type` and `description`. Derive `type` from the path:

- `.agents/instructions/**/*.md` → `Agent Instruction`
- `.agents/memory/INDEX.md` → `Knowledge Index`
- `.agents/memory/LOG.md` → `Source Ingestion Log`
- `.agents/memory/KNOWN_ISSUES.md` and `.agents/memory/known-issues/**/*.md` → `Known Issue`
- `.agents/memory/TESTING_STRATEGY.md` and `.agents/memory/testing/**/*.md` → `Testing Guidance`
- `.agents/memory/adrs/**/*.md` → `Architecture Decision`
- `.agents/memory/sources/**/*.summary.md` → `Source Summary`
- other `.agents/memory/**/*.md` → `Agent Memory`

`title`, `resource`, and `tags` are optional. Unknown fields remain tolerable, but do not add a repository extension without a contract change. Use file-relative paths for local Markdown links and path-valued fields; they may cross bundles or point to repository files, including immutable raw sources, but must resolve inside the repository. External URLs are allowed.

Lifecycle fields describe real state. Stable concepts omit `status`; use `status: draft` only for a real draft. Do not manufacture `generated`, `verified`, or `stale_after`. If present, `generated` has `by` and `at`; `verified` is a list of `{ by, at }`; every timestamp has an explicit UTC offset.
