---
coverage: Primary-source research on Open Knowledge Format (OKF) v0.2 and a migration assessment for this repository's agent knowledge base
---

# OKF primary-source research: migration assessment for an agent knowledge base

## Scope and source status

**Version assessed:** OKF **v0.2**. The requested `knowledge-catalog/okf/`
subtree is a frozen snapshot: its own README tells readers to stop building
against that copy and points to
[GoogleCloudPlatform/open-knowledge-format](https://github.com/GoogleCloudPlatform/open-knowledge-format).
The canonical repository's current `SPEC.md` is also v0.2. This report checked
the requested snapshot at `fbbc7975388288244dfc62aea0066600b25b7c47` and the
canonical repository at `ad30107c31c06aec8a7d5636e0d1058118604e6f`, and links
normative claims to the canonical files. Re-check that repository before
implementation. [Frozen-snapshot notice](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/README.md) · [canonical specification](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md)

The Google Cloud announcement is a useful statement of intent, but it
introduced **v0.1** on 2026-06-12. Its example therefore uses the old
`timestamp` field; it is not the authority for v0.2 field requirements.
[Google Cloud blog](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing) · [v0.2 migration rules](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#13-changes-from-v01)

**Normative status used below:** only `SPEC.md` is the format specification.
The README, Python reference agent, visualizer, tests, recipes, and bundles
are first-party but illustrative implementation/convention evidence, not
additional conformance requirements. [Specification](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md) · [reference README](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/README.md)

## Executive finding

OKF is a strong *interchange and navigation envelope* for this repository's
Markdown knowledge base: it preserves human-readable files, makes the
existing hierarchical corpus progressively discoverable, and adds portable
provenance/freshness/trust signals. It does **not** replace the repository's
agent-loading contract, taxonomy, retrieval/ranking logic, validation policy,
or hook security model. A low-risk adoption is an additive, generated or
carefully maintained OKF projection first—not a move/rename of the Markdown
files that existing hooks and agent instructions address by exact paths.
That conclusion is an inference from OKF's deliberately minimal scope and
this repository's existing path-oriented knowledge-base layout. [OKF goals and non-goals](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#1-motivation) · [bundle structure](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#3-bundle-structure)

## What OKF is for—and explicitly is not for

### Goals

- A vendor-neutral, human- and agent-readable representation of metadata,
  context, and curated insight surrounding data and systems; it is intended
  to be authored by people or agents, exchanged across organizations, and
  consumed by either. [Definition and motivation](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#open-knowledge-format-okf)
- A small producer/consumer contract: a person, agent, or export pipeline can
  produce a bundle, while UIs, search indexes, deterministic code, and agents
  can consume it independently. [Goals](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#1-motivation)
- Knowledge that remains readable without an SDK, diffable in version control,
  and portable as files or a repository. The blog describes the same design as
  a response to fragmented context across catalogs, wikis, code comments, and
  tacit knowledge. [Specification motivation](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#1-motivation) · [Google Cloud rationale](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)
- First-class but optional provenance, credibility signals, generation and
  verification history, lifecycle/freshness, and (for values) sanctioned
  computations plus runtime attestation. [Trust and lifecycle](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#5-provenance-trust-and-lifecycle) · [attested computations](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#10-attested-computations-concept)

### Non-goals and resulting boundaries

- It has no fixed registry of concept types or taxonomy; producers select
  descriptive type strings and consumers must tolerate unknown ones. Thus
  `Agent Instruction`, `Memory`, `Source Summary`, and `Hook Contract` can be
  local types, but their semantics will not automatically interoperate with
  other producers. [Types and extensions](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#41-frontmatter)
- It does not prescribe storage, serving, query infrastructure, a schema
  registry, a runtime, or code/executor packaging. It references
  domain-specific schemas rather than replacing them. [Non-goals](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#1-motivation)
- It does not define typed relationship edges: ordinary Markdown links mean
  “a relationship,” while relation kind remains surrounding prose. A graph
  consumer will commonly see directed but untyped edges. [Cross-linking](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#61-links-between-concepts)
- Trust tiers are advisory—not access control—and attestation interfaces,
  sandboxing, portability, receipt/verdict wire formats, and caching are
  explicitly deferred. Therefore neither `verified` nor an attester is an
  authorization boundary for context-injection hooks. [Trust tiers](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#53-trust-tiers) · [deferred work](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#considered-and-deferred)

## Normative v0.2 data model

### Bundle, concept, identity, and files

| Element | Normative rule | KB implication |
| --- | --- | --- |
| Bundle | A self-contained hierarchy of Markdown documents; it may be a Git repo, archive, or subdirectory. | A dedicated `.agents/okf/` export or a bundle rooted at `.agents/` is possible; no server is required. [Spec §3](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#3-bundle-structure) |
| Concept | Every non-reserved `.md` file is one concept. It is UTF-8 Markdown with a YAML frontmatter block at the beginning and a free-form body. | One source summary, instruction, memory record, or hook contract maps naturally to one document. [Spec §4](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#4-concept-documents) |
| ID | The concept ID is its path within the bundle with `.md` removed. | Moving a file changes its ID and every absolute link; treat paths as stable public identity. [Terminology](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#2-terminology) |
| Reserved names | At every level, `index.md` and `log.md` have special roles and must not be concept documents. | Existing exact lower-case names require care; e.g. `INDEX.md` is not the reserved `index.md` on case-sensitive filesystems, but portability/case behavior should be tested. [Reserved filenames](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#31-reserved-filenames) |
| `index.md` | Optional directory listing for progressive disclosure; normally has no frontmatter, except bundle-root `okf_version`. | Use this as the agent's cheap first read, then load only selected documents. [Index files](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#8-index-files) |
| `log.md` | Optional, date-grouped newest-first update history; date headings must be ISO `YYYY-MM-DD`. | It can complement—not replace—Git history and the repository's current ingestion log. [Log files](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#9-log-files) |

### Frontmatter and body

The only always-required field is non-empty string-like `type`; a document
with only that field is conformant. `title`, `description`, `resource`, and
`tags` are recommended. Producers may add arbitrary keys; consumers must
preserve unknown keys on round trip and must not reject them. The specification
does **not** publish a JSON Schema, JSON serialization, schema registry, or
closed YAML vocabulary—the normative structural contract is YAML frontmatter
plus the rules below. [Frontmatter](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#41-frontmatter) · [Conformance](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#11-conformance)

The body has no required headings. `# Schema`, `# Examples`, and
`# Computation` have only conventional meanings; structural Markdown is
recommended because it helps people and retrieval agents. This makes existing
instructions and memory prose valid content without a forced rewrite.
[Body rules](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#42-body)

All timestamp-valued keys are ISO 8601 datetimes with an explicit UTC offset.
This applies to generated/verified, source modification time, usage window,
and stale deadline fields. [Timestamp rule](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#5-provenance-trust-and-lifecycle)

### Provenance, credibility, trust, lifecycle

| Family | Shape / required parts | Meaning and consumer behavior |
| --- | --- | --- |
| `sources` | List; every entry has required `resource`; optional stable `id`, `title`, `author`, `usage_count`, `last_modified`; a sibling or per-source `usage_window` qualifies usage count. | Captures external or internal origin. `resource` may be a URL, a bundle path, a path in `references/`, or an un-followable scope descriptor. Source `id` should key body footnotes for per-claim attribution. [Spec §5.1](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#51-provenance-sources) |
| Credibility | `author`, use count/window, and source modification time are optional facts, not a score. | Consumers infer credibility; they should treat usage counts as coarse liveness/trend signals, not comparable rankings across different artifact kinds. [Credibility signals](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#51-provenance-sources) |
| `generated` | Mapping with required `by` and `at`. | Records who/what made the current meaningful content change. It is deliberately separate from confirmation. [Generated and verified](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#52-trust-generated-and-verified) |
| `verified` | One `{ by, at }` mapping or a list of such events; a consumer **must** normalize a bare mapping to a one-element list. | No verifier = unverified; only non-`human:` actors = machine-confirmed; any `human:<id>` actor = human-reviewed. [Verification and trust tiers](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#52-trust-generated-and-verified) |
| Actor syntax | `<producer>/<version>` for a tool/agent, `human:<id>` for people, and `process:<id>` for automated processes. | The `human:` prefix is semantically important: it controls the derived tier. [Actor convention](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#7-actor-convention) |
| `status` | `draft`, `stable` (default when absent), or `deprecated`. | A deprecated document remains available for links/history rather than being silently removed. [Status](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#54-lifecycle-status) |
| `stale_after` | Optional absolute instant; stale when `now >= stale_after`. | Gives a deterministic freshness signal; it is not a relative read-time TTL. [Staleness](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#55-lifecycle-stale_after) |

### References, paths, and relationships

Use normal Markdown links. Bundle-root-relative links beginning `/` are
recommended because moving the source file within its directory will not
change their target; ordinary relative links are also supported. Consumers
must tolerate a broken link, and every path-valued field accepts an absolute
URL, bundle-root-relative path, or relative path. The `references/` directory
is a useful convention for mirrored source material, executor instructions,
or code—not a requirement. [Links and path-valued fields](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#6-cross-linking-and-paths)

### Attested Computation: only for sanctioned executable values

An `Attested Computation` is its own concept, linked from ordinary concepts.
It requires `runtime`; it may declare typed/named `parameters`, an external
`computation` file instead of one inline `# Computation` fence, an `executor`
with `resource` and declared `receipt` fields, and a deterministic
no-LLM `attester` with `resource`. An agent may supply values only for
declared parameters, not author or edit the computation. The runtime execution
sequence in §10.5 is expressly **informative**, while the frontmatter contract
is normative. [Contract fields](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#102-contract-fields) · [parameter constraint](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#103-the-computation) · [informative flow](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#105-how-a-consumer-uses-it-informative)

For this repository, do not model normal Markdown instructions or hooks as an
Attested Computation merely because an agent may act on them. Reserve this
type for a narrow, reviewable command/query whose exact result must be
verified. The specification intentionally leaves the attester ABI and
sandboxing unresolved, so adopting it for arbitrary local execution would
require a separate security design. This is a migration recommendation based
on the documented boundary, not an OKF requirement. [Format non-goal](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#1-motivation) · [deferred ABI/sandboxing](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#considered-and-deferred)

### Conformance and versioning

Conformance is deliberately permissive: all non-reserved Markdown must have
parseable frontmatter and a non-empty `type`; reserved files must use their
specified structures. Consumers must not reject missing optional families,
unknown types/keys, broken links, or a missing index. Minor versions add
backward-compatible optional conventions, while major versions may break
required names; root `index.md` may declare `okf_version: "0.2"`, but a
consumer that does not understand it should attempt best-effort consumption.
[Conformance](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#11-conformance) · [Versioning](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#12-versioning)

For v0.1 migration, `timestamp` is superseded by `generated.at`, and body
`# Citations` is superseded by frontmatter `sources`; v0.2 consumers may fall
back to the legacy forms. [v0.1 changes](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#13-changes-from-v01)

## Official tooling: useful evidence, not a normative validator

The frozen reference implementation is Python `reference-agent` 0.1.0 with
Python >=3.11 and a BigQuery source. Its producer does a metadata pass followed
by an optional bounded, same-host web-enrichment pass, then regenerates
indexes. It is a proof of concept, not a required OKF runtime or generic
knowledge-base migrator. [Package metadata](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/pyproject.toml) · [README workflow](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/README.md#how-the-reference-agent-works) · [runner implementation](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/src/reference_agent/runner.py)

Its document parser/validator demonstrates one consumer choice: validate only
`type`, preserve timestamp text rather than PyYAML's implicit datetime
rewrite, normalize bare `verified`, and derive trust/staleness. This does not
make its parser, its concept-ID segment regex, its field ordering, or its
failure behavior part of the standard. [Document implementation](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/src/reference_agent/bundle/document.py) · [document tests](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/tests/test_document.py)

The optional `visualize` command creates one HTML graph view. Its frozen
implementation skips `index.md`, extracts only relative Markdown `.md` links
(not root-relative links), and exposes directed graph edges plus derived trust
and stale state. Those details reveal that consumers can differ; a KB
integration must test the links it emits against its chosen consumer.
[Visualizer implementation](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/src/reference_agent/viewer/generator.py) · [README visualizer description](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/README.md#visualize)

## Meaningful first-party samples and what each teaches

The three recipes below are reproducible **reference-agent** demonstrations;
the produced data bundles are examples, not a fixed domain model. The Acme
Retail bundle is a separate hand-authored v0.2 attestation demonstration.
[Sample overview](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/README.md#samples)

| Sample | Evidence and coverage | Migration lesson |
| --- | --- | --- |
| GA4 Google Merchandise Store | The [recipe](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/samples/ga4_merch_store/README.md) runs on `bigquery-public-data.ga4_obfuscated_sample_ecommerce` using canonical GA4 seed URLs. Its [bundle](https://github.com/GoogleCloudPlatform/open-knowledge-format/tree/main/bundles/ga4) includes a dataset, dense event-table schema, generated indexes, and web-derived metric reference documents. | A single authoritative source page can enrich a base asset with many details; preserve base metadata and attach sources rather than replacing it. The table demonstrates per-claim source footnotes and nested-schema prose. [Events concept](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/bundles/ga4/tables/events_.md) |
| Stack Overflow | The [recipe](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/samples/stackoverflow/README.md) intentionally exercises multi-concept enrichment from cross-cutting schema pages. Its [bundle](https://github.com/GoogleCloudPlatform/open-knowledge-format/tree/main/bundles/stackoverflow) contains broad table coverage plus reference documents for joins, metrics, licenses, post types, and vote types. | “Reference” concepts can capture a relationship or an external definition instead of bloating each asset document; a source-summary KB can likewise make durable cross-cutting topics first-class. [Example join](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/bundles/stackoverflow/references/joins/posts_answers__posts_questions.md) · [example metric](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/bundles/stackoverflow/references/metrics/accepted_answer_rate.md) |
| Bitcoin | The [recipe](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/samples/crypto_bitcoin/README.md) targets four tightly related fact tables and says its purpose is surfacing cross-table foreign-key relationships in prose. Its [bundle](https://github.com/GoogleCloudPlatform/open-knowledge-format/tree/main/bundles/crypto_bitcoin) has tables, join reference concepts, and a derived metric. | Directory hierarchy alone is insufficient; add explicit links for meaningful dependency/reference relationships, while accepting that OKF does not type their edges. [Blocks–transactions join](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/bundles/crypto_bitcoin/references/joins/blocks___transactions.md) |
| Acme Retail | This [hand-authored bundle](https://github.com/GoogleCloudPlatform/open-knowledge-format/tree/main/bundles/acme_retail) exercises policy sources, source credibility, human review, `stale_after`, deprecation, two sanctioned SQL computations, executor instructions, and a deterministic attester. It is the most complete v0.2 example but has no recipe. | It is the relevant pattern only where a KB item authorizes a concrete, high-impact computed result. The [current/legacy metric pair](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/bundles/acme_retail/metrics/gross-margin.md) shows how to preserve historical knowledge with `status: deprecated`; the [computation](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/bundles/acme_retail/computations/revenue-ytd.md), [executor](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/bundles/acme_retail/skills/run-on-bq.md), and [attester](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/bundles/acme_retail/attesters/sql_equality.py) show one non-normative runtime convention. |

All bundle `viz.html` files are generated optional consumer artifacts, not
conforming concept documents or a required part of a bundle. [Reference README](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/README.md#visualize)

## Recommended migration for this repository's agent KB

### Preserve behavior first

Existing Markdown instructions, memory, source summaries, manifests, and
context-injection hooks have two jobs: store knowledge *and* direct specific
agents/tools to read particular paths at specific moments. OKF standardizes
the former representation, not hook discovery or invocation. Keep current
paths and loaders working during migration; do not infer that a generic OKF
consumer will discover the right context, enforce repository order, or carry
out hook actions. This is an inference from the specification's
producer/consumer independence and its non-prescribed runtime.
[Producer/consumer independence](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#1-motivation) · [no required tooling](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#open-knowledge-format-okf)

### Proposed additive mapping

| Current KB material | Suggested OKF representation | Notes |
| --- | --- | --- |
| Root loading map and directory maps | `index.md` listings at bundle root and each content directory | Generate/review concise descriptions from each child `description`; retain the existing root loader until hooks are deliberately changed. [Index convention](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#8-index-files) |
| `.agents/instructions/*.md` | `type: Agent Instruction`; local tags such as `area:hooks` may be added as extensions | Use body headings for trigger, scope, procedure, and validation. `type`/tag names are producer-owned; document their local semantics in a root concept. [Extensions](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#41-frontmatter) |
| `.agents/memory/*.md` and focused known-issue/testing records | `type: Agent Memory`, `Known Issue`, or `Testing Guidance` | Store `status`, `generated`, `verified`, and `stale_after` only when the team can maintain them honestly; missing optional fields remains conformant. [Optional families and conformance](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#11-conformance) |
| Source summaries plus immutable raw source inputs | `type: Source Summary` with `sources[]` pointing to the raw artifact or original authoritative URL; cite individual claims with `[^source-id]` | This gives source-to-summary traceability without needing a proprietary catalog. Use stable IDs rather than positional references. [Provenance and attribution](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#51-provenance-sources) |
| Hooks/configs and their documentation | Usually a `type: Hook Contract` document that links to the config/script; retain the executable file as the actual hook input | The Markdown describes the contract; it must not be mistaken for permission to execute. Use a domain-specific extension if typed hook event/permission fields are needed. [Extensibility](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#41-frontmatter) |
| Ingestion/update history | `log.md` at the smallest useful scope, plus Git as authoritative diffs/blame | Follow date headings and newest-first order; avoid duplicating every commit. [Log structure](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#9-log-files) |

Suggested navigation flow for a future context injector:

```text
bundle root index.md
  -> area index.md (instructions / memory / sources / hooks)
    -> selected concept document(s)
      -> follow only linked sources or dependencies needed for the task
```

This progressive-disclosure pattern is directly supported by optional indexes,
but relevance scoring, token budgets, task-to-area mapping, cycle handling,
and fallback behavior are implementation choices that must remain explicit in
the hook/loader contract. [Progressive disclosure](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#8-index-files) · [consumer freedom](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#1-motivation)

### Suggested rollout and quality gates

1. Build a read-only sidecar/projection from the existing KB and compare it
   with the current paths. Put `okf_version: "0.2"` only in the projection
   root's `index.md`; do not add it to ordinary concepts. [Version declaration](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#12-versioning)
2. Give every emitted concept `type`, a useful `title` and `description`, and
   a stable path; generate directory indexes. Leave prose intact initially.
   [Required/recommended frontmatter](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#41-frontmatter)
3. Add `sources`, keyed footnotes, `generated`, and `verified` only where
   provenance and a real reviewer/process are known. Do not manufacture a
   “human-reviewed” tier by naming an agent as `human:`. [Actor/trust rules](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#7-actor-convention) · [trust derivation](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#53-trust-tiers)
4. Add a repository-owned linter beyond minimum conformance: UTF-8,
   frontmatter parse, non-empty `type`, reserved-file form, valid timestamp
   offsets, unique local source IDs, resolvable internal links when desired,
   and local taxonomy/required-field policy. This is necessary because OKF
   intentionally allows unknown keys/types and broken links. [Permissive conformance](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#11-conformance)
5. Shadow-test the existing loader and an OKF loader on representative tasks:
   compare selected files, final context size, link traversal, and handling of
   missing or stale material. Only then switch a hook, with a rollback to the
   current path-driven loader.

## Ambiguities, gaps, and risks to manage

- **Canonical-source drift:** the requested subtree is frozen even though its
  v0.2 spec is useful. Pin a canonical commit/version and re-read the
  canonical repo before treating this report as an implementation contract.
  [Frozen-snapshot warning](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/README.md) · [canonical repo](https://github.com/GoogleCloudPlatform/open-knowledge-format)
- **No standard JSON schema or strict validator:** portable minimum
  conformance is intentionally tiny. Producers that need consistent types,
  source shapes, date parsing, relationship categories, or lifecycle policy
  need their own versioned profile and linter. [Conformance](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#11-conformance)
- **Untyped graph semantics:** a link can mean reference, dependency,
  supersession, ownership, or “read next.” For deterministic context routing,
  add a documented local extension or explicit prose conventions; do not infer
  policy from edge direction alone. [Link semantics](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#61-links-between-concepts)
- **Trust is not truth or security:** `verified` derives a tier solely from
  actor-string form and records no verification scope, signature, approval
  authority, or access control. Treat it as an audit/retrieval signal only.
  [Trust tiers](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#53-trust-tiers)
- **Attestation is immature for arbitrary execution:** receipt/verdict schema,
  attester ABI, portability, caching, and sandboxing are deferred. The Acme
  Python/BigQuery flow is a helpful example, not a safe general-purpose
  executor protocol. [Deferred runtime work](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#considered-and-deferred) · [Acme attester example](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/bundles/acme_retail/attesters/sql_equality.py)
- **Path/consumer variance:** the spec recommends root-relative links, but
  the frozen visualizer only extracts relative links; it also skips only
  `index.md`, not `log.md`. Test with the intended consumer rather than
  assuming the proof-of-concept defines interoperability. [Spec path rule](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#61-links-between-concepts) · [viewer code](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/src/reference_agent/viewer/generator.py)
- **Reserved-log ambiguity in examples:** §8 explicitly limits frontmatter in
  `index.md`, while §9 describes `log.md` as a flat date-grouped list without
  expressly saying whether frontmatter is forbidden. The Acme sample adds
  frontmatter to `log.md`. A local profile should choose one rule (safest:
  frontmatter-free logs) and test it. This is an observed specification/sample
  tension, not a stated nonconformance. [Index/log rules](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#8-index-files) · [Acme log](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/bundles/acme_retail/log.md)
- **Generated artifacts and duplicate truth:** a sidecar projection can drift
  from original Markdown. Establish one source of truth, an idempotent
  generator or explicit edit policy, and CI freshness checks before exposing
  it to hooks.
- **Sensitive context:** the plain-file portability that makes bundles useful
  also makes accidental broad context loading or distribution easier. Keep
  repository access control, secret scanning, allowlisted sources, and context
  budgets outside the format.

## Bottom line

Adopt OKF v0.2 as an interoperable metadata/provenance layer around the
existing agent knowledge base, not as a replacement for its operational
loading and security rules. Start with an additive projection, a documented
local taxonomy/profile, a strict repository linter, and shadow-tested
progressive context loading; reserve attested computations for narrowly
defined high-impact executions after a separate runtime security design.
