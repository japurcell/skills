# Maintaining agents-md-install

This skill replaces `agents-md-improver` and `create-agentsmd`. Invoke it explicitly to create, audit, or update project guidance. Runtime instructions are self-contained; this README records design evidence and evaluation procedure, not additional runtime steps.

## Source decisions

Reviewed 2026-10-21, in the requested priority order:

1. [Harness engineering](https://github.com/lopopolo/harness-engineering), especially [just-in-time context](https://github.com/lopopolo/harness-engineering/blob/trunk/docs/just-in-time-context/README.md), [repository teaching](https://github.com/lopopolo/harness-engineering/blob/trunk/docs/domain-modeling/README.md), and [authority](https://github.com/lopopolo/harness-engineering/blob/trunk/docs/authority/README.md). Adopt a small routing root, scoped guides, recoverable quality constraints, canonical owners, and verification. Adapt to the target's policies instead of copying the source repository's operating rules. Autonomous editing remains bounded by the user's scope.
2. [A Complete Guide to AGENTS.md](https://www.aihero.dev/a-complete-guide-to-agents-md). Adopt minimal always-loaded content and task-specific references. Prefer direct, explicit loading conditions over its casual pointers and multi-hop examples so required guidance is not accidentally skipped. Its objection to comprehensive auto-generated files motivates inspection and selective authoring, not a generic initializer.
3. Local `agents-md-improver/SKILL.md`. The requested singular `~/.agents/skill/` location was absent; the installed plural `~/.agents/skills/` source and published bundle were read. Preserve discovery, actionable commands, currency, concise assessment, and diff review. User approval on 2026-10-21 explicitly replaces additive-only updates and a repeated approval gate with meaning-preserving reconciliation within the requested scope.
4. [AGENTS.md](https://agents.md/). Use ordinary Markdown with project-appropriate sections and nested files. Do not mistake a flexible format for a compulsory template or assume identical host discovery behavior.
5. [Addy Osmani, AGENTS.md](https://addyosmani.com/agents/15-agents-md/). Adopt concrete examples, non-obvious rationale, and maintenance alongside project changes. Its 150-line suggestion is a conciseness heuristic, not an enforced quota or reason to omit valid policy.
6. [GitHub's analysis of over 2,500 repositories](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/). The article primarily describes custom agent personas. Transfer precise commands, examples, and boundaries; do not transfer persona frontmatter or `.github/agents/` output into repository instruction files.
7. [AAIF, Writing an effective AGENTS.md](https://aaif.io/blog/writing-an-effective-agents-md). Adopt decision-changing local knowledge, change-scoped validation, meaningful nested boundaries, and clear limits on performance claims. Enforcement belongs in existing tooling; this skill documents or recommends it without expanding into code changes.

## Preserved and superseded obligations

| Predecessor obligation | Replacement |
| --- | --- |
| Discover root and nested guidance | Complete scoped inventory, without the old 50-file truncation |
| Assess commands, architecture, gotchas, currency, actionability | Evidence-based assessment and task traces, without mandatory numerical scoring |
| Show rationale and changes | Assessment before edits; final changed paths and material dispositions |
| Additions only, preserve section structure | User-approved restructuring that preserves valid requirements and exceptions |
| Ask after every quality report | User-approved edits within install/update scope; audit remains read-only; unresolved policy requires a question |
| Comprehensive required root sections | User-approved minimal shared root and conditional disclosure |
| Nested files optional for monorepos | Required for meaningful directory-specific rules, without one-file-per-directory scaffolding |
| Test documented commands | Safe executed checks distinguished from static verification and unverified operations |
| Explicit invocation | `disable-model-invocation: true` and Codex `allow_implicit_invocation: false` retained |

## Evaluate changes

Use `evals/evals.json` and the fixture directory named by each case. Copy inputs into a separate run directory; preserve fixture sources. Run each prompt with this exact local SKILL.md and without it in fresh independent contexts. Do not consult installed copies. Keep run outputs in a sibling `agents-md-install-workspace/iteration-N/eval-*/` tree, never inside the published bundle. Save response, available transcript, and actual timing metadata; missing measurements stay missing.

Grade each assertion against actual files and the response using the [evaluation rubric and grader controls](evals/README.md). Use deterministic checks for file existence, unchanged excluded files, Markdown link destinations, and audit immutability. Inspect meaning for preserved exceptions, explicit loading conditions, and invented policy. Do not equate keyword presence with correct policy. Retain failed runs before revising anything.

Reinvoke the skill against a successful update output with unchanged evidence to check stability. Use the available skill-creator validator and standard `eval-viewer/generate_review.py` to create a review artifact. Report sampled results, not general performance gains or repeated-run variance. Repository source validation and `git diff --check` complement behavioral runs.
