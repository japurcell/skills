# Mandatory Context and Fallback

**Type:** grilling
**Status:** closed
**Blocked By:** selector-contract-and-ranking.md
**Research Dir:** N/A

## Question

Which instructions and freshness gates bypass relevance ranking, how are mandatory and selected context combined within budgets, what sensitive-content boundaries apply, and exactly when must the consumer degrade or fall back to the current `INDEX.md` loading path?

---

<!-- Resolution will be appended here -->

## Resolution

Adopt an explicit mandatory-context contract around `agent-kb-selector@1.0.0`. Mandatory loading is deterministic policy, not a relevance score, trust claim, or authorization mechanism. Keep runtime-loaded `AGENTS.md` and the legacy `.agents/memory/INDEX.md` path outside selector output.

### Inputs and policy

Add required caller-supplied `task-scope`, containing exactly `trivial` or `nontrivial`, to the initial selector v1 input contract. The selector never infers scope from task text, task kind, paths, conversation state, or environment state. Because the selector is not implemented or released, this refines its initial `1.0.0` contract rather than creating a fictional migration version.

Advance the repository profile to `agent-kb@1.3.0` with a strictly validated, non-emitted `mandatory-context` policy section in `.agents/okf-profile.json`. Each rule has a stable identifier, one or more explicit match conditions over task scope, task kind, or the selector's existing committed path-to-area mapping, and one or more registered logical concept roots. Values within a condition are alternatives; all condition kinds present on a rule must match. Reject unknown fields or values, duplicate rule identifiers, empty conditions or roots, and missing or reserved concept targets. Rule declaration order has no meaning.

The initial policy is:

- `nontrivial` tasks require `/repo/architecture.md` and `/repo/conventions.md`.
- For `change`, `review`, `diagnose`, `validate`, and `operate`, every area resolved from a supplied normalized repository path activates the profile's explicit instruction root or roots for that area. Multiple paths union their roots. Areas without an applicable instruction concept add no invented root.
- `answer` and `plan` add no area root solely from task kind or paths; their non-trivial core rule still applies, and relevance ranking may select further context.
- No supplied path means no inferred area root. Task text, tags, prose, rank, directory enumeration, and concept bodies never create mandatory roots.

Use curated `requires` edges to attach matching known-issue and testing guidance where applicable. The policy and every relationship remain explicit profile data; do not add a per-concept mandatory flag or numeric priority.

### Closure, lifecycle, and ordering

Union all matching policy roots, then expand `requires` transitively. The producer already rejects `requires` cycles. Render the mandatory closure in dependency-first topological order, using normalized logical path ascending to break ties. Render mandatory concepts before relevance-ranked concepts.

Deduplicate across the complete result. If relevance ranking or `depends-on` expansion reaches an already mandatory concept, emit it once in the mandatory section and retain both mandatory and relevance reasons in its audit record.

If a mandatory root or required target is deprecated, follow its validated `superseded-by` graph to every current replacement, then compute each replacement's mandatory closure. Record the substitution. A stale mandatory concept, or a deprecated mandatory branch without a current non-stale replacement, is a hard stop: legacy loading must not silently revive invalid policy.

### Budgets and selection result

The caller's positive UTF-8 byte and concept-count budgets cover the combined output. Charge complete mandatory concepts, their stable path delimiters, and separators first; relevance-ranked concepts receive only the remainder. Never truncate, omit, or partially render a mandatory concept. If the mandatory closure does not fit either budget, return no OKF context and require legacy loading.

After mandatory packing succeeds, apply the closed relevance-ranking and `depends-on` rules. A valid selection must contain at least one relevance-selected concept. If no candidate is eligible or no relevance candidate fits the remaining budget, preserve the selector's `no_match` outcome and require atomic legacy loading rather than returning mandatory-only context.

Add `disposition` with the closed values `use_okf`, `use_legacy`, and `hard_stop` alongside the selector outcome. `use_okf` includes the rendered context plus ordered mandatory audit records, matching rule identifiers, lifecycle substitutions, mandatory and total byte/count totals, relevance records, and all applicable reasons. Mandatory-specific reasons are the closed initial set `mandatory_task_scope`, `mandatory_task_kind_area`, `mandatory_requires`, `mandatory_superseded`, and `mandatory_deduplicated`; retain applicable selector reason codes as well. Changing disposition or reason-code meaning is a selector-major change; additive optional fields or reason codes follow the selector's existing versioning rule.

### Fallback and hard-stop matrix

Return `use_legacy` with no rendered or partial OKF context for:

- a valid `no_match`, including the case where relevance candidates exist but none fits after mandatory packing;
- a missing or unavailable projection;
- projection integrity, relationship, supported-input I/O, or compatibility/version failures; or
- mandatory byte or concept-count exhaustion.

Return `hard_stop` with no rendered context for:

- malformed caller input, including absolute, traversing, or otherwise unsafe paths;
- any pending source-ingest hard gate, evaluated before selection;
- an access-boundary violation; or
- a stale mandatory concept or mandatory deprecated branch without valid current replacement.

On `use_legacy`, the provider adapter discards all OKF output, reads `.agents/memory/INDEX.md`, and follows its existing loading table plus `AGENTS.md`. The selector reports only that fallback is required; it never claims fallback succeeded. If legacy loading fails, the adapter returns a terminal error and must not retry OKF, mix the two modes, or recursively fall back.

Every non-`use_okf` result includes a stable reason code, `fallback_required: true` only for `use_legacy`, and privacy-safe metadata such as affected logical paths. Diagnostics and logs must not contain task text, concept bodies, or rendered context.

### Sensitive-content boundary

The selector reads only concepts explicitly registered in the validated projection manifest. Immutable raw sources are not projected or selected. Existing repository permissions, source allowlists, secret scanning, and provider-specific hook envelopes remain authoritative. Neither OKF metadata nor selector eligibility grants access, changes trust, redacts content, or permits loading outside the active workspace. This migration adds no security-classification vocabulary or selector-level redaction subsystem.
