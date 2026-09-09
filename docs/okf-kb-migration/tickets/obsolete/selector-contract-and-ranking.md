# Selector Contract and Ranking

**Type:** grilling
**Status:** obsolete
**Blocked By:** none
**Research Dir:** N/A

## Question

What deterministic selector contract turns task signals into bounded context: input signals, candidate discovery, scoring and tie-breaking, task/path/type metadata, relationship traversal and cycle limits, lifecycle filtering, token budgeting, output format, reason codes, caching, and offline dependency limits?

---

<!-- Resolution will be appended here -->

## Resolution

Adopt independent selector contract `agent-kb-selector@1.0.0`. The selector is a deterministic, provider-neutral, read-only consumer of one current generated projection. It never repairs inputs, writes state, calls a network or subprocess, invokes an LLM or model tokenizer, or depends on anything outside the language standard library.

### Inputs and candidate discovery

The normalized input contains:

- required non-empty current task text;
- required evaluation time as an RFC 3339 timestamp with an explicit UTC offset, normalized to UTC;
- optional normalized repository-relative paths; and
- at most one optional task kind from `answer`, `plan`, `review`, `diagnose`, `change`, `validate`, or `operate`.

Build and refactor work map to `change`, tests and checks map to `validate`, and installation, execution, and monitoring map to `operate`. Callers supply the task kind; the selector never infers it. Conversation history, tool output, implicit wall-clock or other environment state, and model-generated classifications are not selector inputs. Provider adapters obtain and pass the evaluation time; the selector never reads the system clock. Include the normalized evaluation time in the structured result so identical complete inputs remain reproducible.

Paths use strict POSIX repository-relative form. Reject absolute paths, traversal, empty or malformed paths, then deduplicate and sort accepted paths. A committed selector table maps path prefixes to the profile's area vocabulary; do not infer areas from directory names at runtime.

Discover candidates exclusively from a valid, current `.agents/okf/.projection-manifest.json`. Generated `index.md` files remain progressive-navigation aids and are never the machine inventory. Missing, stale, unreadable, hash-mismatched, or structurally invalid projection evidence is fatal and produces no selected context.

### Profile metadata

Advance the concept profile from `agent-kb@1.1.0` to `agent-kb@1.2.0` by allowing optional `x-agent-kb.task-kinds`, containing only values from the closed selector vocabulary. Do not add a generic numeric priority or mandatory-load flag. Mandatory policy remains owned by **Mandatory Context and Fallback**.

Selector patch releases must preserve observable results for the same valid bundle and normalized input. Minor releases may add optional inputs or reason codes without changing existing meaning. Any change to eligibility, ordering, budgeting, rendered output semantics, or existing reason-code meaning requires a selector major release.

### Eligibility and deterministic ranking

Match task text only against concept metadata: `title`, `tags`, `description`, and `type`. Never search concept bodies. Normalize text using Unicode NFKC followed by case folding; split punctuation and kebab-case into tokens. Use no stemming, fuzzy matching, embeddings, or mutable stop-word list.

A direct candidate is eligible only when it has at least one path, area, exact-phrase, or token match. Task kind alone may refine an eligible candidate but cannot make one eligible. Exclude concepts whose `stale_after` is at or before the normalized evaluation time. A deprecated concept is not eligible itself: follow its validated `superseded-by` edge or edges to current replacements and record the lifecycle decision.

Sort eligible direct candidates by this descending integer tuple, with normalized logical concept path ascending as the final tie-breaker:

1. Path match class: exact canonical `source.path` match is `2`, an `x-agent-kb.paths` glob match is `1`, and no match is `0`. Use the best path evidence rather than rewarding repeated matching inputs.
2. Glob specificity: the matching pattern's literal-character count, or `0` for an exact or absent match.
3. Task-kind match: `1` or `0`.
4. Area match from the committed path-prefix mapping: `1` or `0`.
5. Exact normalized task-phrase match: title `4`, tags `3`, description `2`, or type `1`; use the highest matching field.
6. Token overlap: for each unique query token, use only its highest matching field weight—title `8`, tags `6`, description `4`, or type `2`—then sum those per-token values.
7. Normalized logical concept path ascending.

Glob syntax and the area-prefix table are versioned selector data and must be validated by the producer/linter contract; runtime filesystem enumeration or heuristic area discovery is forbidden.

### Relationships and budgets

After ranking direct seeds, expand at most one `depends-on` hop. Deduplicate targets, tolerate cycles through that deduplication, rank every direct match above every relationship-only addition, and add relationship targets only while budget remains. Do not traverse `governed-by` or `supersedes` for relevance. `requires` traversal belongs to the mandatory-context closure, not relevance ranking.

The caller supplies a positive UTF-8 byte budget and positive maximum concept count. Render only complete concept documents in rank order, separated by stable logical-path delimiters. Delimiters and separators count against the byte budget. Never truncate a concept.

Greedily consider candidates in rank order. If one concept does not fit, record its exclusion and continue considering smaller candidates until both budgets are exhausted or candidates end. If nothing is eligible or fits, return a successful empty selection with overall outcome `no_match`; never guess at broadly relevant context. **Mandatory Context and Fallback** decides whether empty or fatal results activate legacy loading.

### Provider-neutral result and explanations

Return one structured result containing:

- selector and profile versions plus projection digest;
- normalized inputs and requested budgets;
- overall outcome;
- ordered selected records;
- candidate exclusion records; and
- the rendered context string.

Each selected record contains logical path, canonical source path, rank tuple, reason codes, and rendered UTF-8 byte count. Keep the complete candidate audit outside rendered context; provider adapters inject only the rendered context.

The initial closed reason-code vocabulary is `path_exact`, `path_glob`, `task_kind_match`, `area_match`, `phrase_match`, `token_match`, `depends_on`, `no_signal`, `deprecated`, `stale`, `superseded`, `over_byte_budget`, and `over_concept_limit`. `no_match` is an overall outcome rather than a candidate reason. Fatal results use typed input, projection, relationship, version, or I/O errors and contain no partial context. Readers continue to tolerate unknown future fields and relationship kinds where the profile already requires that behavior.

### Caching and offline operation

Selector v1 deliberately has no cache. The initial bundle is only 42 concepts, and caching risks hiding mutated projection files or adding concurrency and invalidation complexity to one-shot hook processes. A future immutable process-local cache requires evaluation evidence and a selector-contract minor release. Persistent selector caches require a separate design.

The selector must be testable entirely offline: no network, subprocess, Git invocation, LLM, external tokenizer, or filesystem writes. Invalid normalized input returns a typed input error. Any projection-integrity failure is atomic: return a typed fatal result with no context rather than selecting from a partial bundle.
