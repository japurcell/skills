# Reference evidence for just-in-time context

Checked 2026-09-29. Scope: reference mechanisms and their limits, without selecting an architecture. Provider versions are not pinned in this planning effort; the behavior below is current documentation, not a tested guarantee for an installed release.

## Strongest evidence

The references support bounded retrieval, incremental evidence-backed learning, and recurring maintenance. They do not establish that one skill with recall/learn/dream entry points, nested AGENTS.md files, or universal hooks will deliver those properties across providers. A lifecycle interface is a packaging hypothesis; publication authority, retrieval, and evaluation remain separate questions.

## Evidence ledger

| Reference | Evidence class | What it establishes | Limit or counterexample |
| --- | --- | --- | --- |
| Harness just-in-time context | Authored design guidance, linked reported practice | A small root map routes to local owners; context arrives during grounding, execution, and review. Skills teach approaches; runbooks retain repeatable contracts. Candidate observations are isolated from published retrieval. | Its context-sidecar publication policy includes domain-owner approval for judgment or policy. This differs from the user's authorized automatic semantic maintenance and needs an explicit authority contract. It is not a deployed three-provider implementation. [Source](https://github.com/lopopolo/harness-engineering/tree/trunk/docs/just-in-time-context) |
| Feedback | Authored design guidance | Corroborate failures against observable outcomes, identify the governing class, and promote a lesson into its smallest durable owner. Remove downstream defenses made redundant by stronger upstream ownership. | A failed run can arise from worker variance or a bad premise. More instructions are not necessarily the remedy; a type, test, API, or changed architecture can be the owner. [Source](https://github.com/lopopolo/harness-engineering/tree/trunk/docs/feedback) |
| MLD feedback example | Proposed operating protocol around reported practice | Mistakes, Learnings, and Desires are telemetry for the harness builder. Diffs, checks, traces, review, and outcomes corroborate them before promotion. | Automatically feeding raw self-reports into future runs risks self-reinforcing errors, stale state, duplication, and boundary leakage. Silence does not prove correctness. This directly challenges an automatic append-every-learning policy. [Source](https://github.com/lopopolo/harness-engineering/blob/trunk/docs/feedback/mld.md) |
| Domain-modeling overview | Design argument with anecdotes | Consistent source code is itself future context; canonical owners and regular examples reduce competing local idioms. | Its example of splitting a Ruby unpack implementation into regular modules is an anecdote, not a controlled study of a repository memory service. [Source](https://github.com/lopopolo/harness-engineering/tree/trunk/docs/domain-modeling) |
| Homelab example | First-party case description of private implementation | Short root routing, specialist documents, versioned automation contracts, and source comparisons. Freshness findings include the page, contradicting configuration, correction, and unresolved judgment. | Documentation freshness is report-only by default; follow-up edits require authorization. The private implementation cannot be independently inspected here. Treat it as a reported mechanism, not proof of autonomous semantic publication. [Source](https://github.com/lopopolo/harness-engineering/blob/trunk/docs/domain-modeling/homelab.md) |
| Blog-build example | Case description linked to author's account | Package ownership, typed boundaries, actionable diagnostics, and architectural documentation constrain recurring decisions. | Documentation is paired with executable controls; prose retrieval alone is not the mechanism. This is an analogy for memory boundaries, not an implementation of memory pruning. [Case](https://github.com/lopopolo/harness-engineering/blob/trunk/docs/domain-modeling/hyperbola.md), [author account](https://hyperbo.la/w/harness-engineering-the-blog-build/) |
| Architectures That Teach | Case descriptions | Canonical manifests own current facts; Artichoke traits expose capabilities without loading its C backend. | Architectural context boundaries can avoid needing more memory. A memory layer copying current versions would introduce a second semantic owner. [Source](https://github.com/lopopolo/harness-engineering/blob/trunk/docs/domain-modeling/implementations.md) |
| OpenAI harness essay | First-party reported production practice | A compact AGENTS map, indexed documentation, freshness/link checks, and recurring background repair tasks. | Cleanup produces targeted PRs, often reviewed or automerged. The author cautions that end-to-end autonomy depends on repository-specific structure; long-term coherence remains unknown. This is not controlled evidence of portable semantic pruning. [Source](https://openai.com/index/harness-engineering/) |

## What ACE actually evaluates

The referenced paper is **Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models**, arXiv 2510.04618v3, dated 29 March 2026. It adapts external inputs without updating model weights. Offline adaptation uses training examples; online adaptation predicts each test example before updating context.

Generator, Reflector, and Curator roles produce itemized deltas; deterministic merge logic preserves prior entries. Entries carry IDs and helpful/harmful counters. Semantic deduplication supports proactive or capacity-triggered refinement. AppWorld ablation reports average test-normal scores of 70.3 with incremental updates versus 56.9 without them.

Counterexamples matter: a whole-context rewrite shrank 18,282 tokens to 122 and reduced accuracy from 66.7 to 57.1. Sustained harmful reflection every iteration reduced FiNER accuracy to 66.7 versus a 70.7 baseline. The paper notes simple tasks may need only concise guidance. This supports incremental, evaluated memory changes, not indiscriminate growth or global rewrites.

These are benchmark experiments, not tests of AGENTS routing, hook delivery, source freshness, instruction precedence, Git rollback, or cross-repository maintenance. Their transfer to the pilot is a hypothesis requiring fresh-session outcome checks. [Paper, sections 2-5 and appendices A.4-A.5](https://arxiv.org/html/2510.04618v3)

Implementation check: the released orchestrator constructs distinct Generator/Reflector/Curator components, saves run configuration and intermediate playbooks, and invokes a bullet analyzer only when enabled. `use_bulletpoint_analyzer` defaults to false. Thus published grow-and-refine capability should not be assumed active in every default run. No experiment was reproduced here. [Source code](https://github.com/ace-agent/ace/blob/main/ace/ace.py)

## AIHero guide: useful practice, bounded platform claims

The guide advocates a minimal root file, linked specialist documents, and nested package guidance. Its 150-200 instruction estimate is attributed to another article, not supported by a benchmark in the guide. Its absolute claims about every-request loading and merged nested files should be qualified by provider and surface. Its warning against all auto-generated instructions is advice, not an established impossibility of evidence-backed generation. [Guide](https://www.aihero.dev/a-complete-guide-to-agents-md)

Primary documentation narrows the claims:

| Surface | Verified behavior | Consequence |
| --- | --- | --- |
| Codex CLI | Official model guidance describes global plus repository-root-to-CWD discovery, size/fallback configuration, root-to-leaf ordering, and user-role instruction messages. | The guide's universal placement below the system prompt is imprecise. This retrieved source does not establish automatic loading of every descendant guide when arbitrary tools touch files. [Official guidance](https://developers.openai.com/api/docs/guides/latest-model#using-agentsmd) |
| Copilot CLI | Discovers root, CWD, intermediate directories, and nested directories on a file's working path. Combines applicable files, deduplicates identical copies, and defines no general precedence among them. `@` references load immediately. | Nested guidance is supported, but conflict resolution and lazy Markdown links must not be inferred from eager imports. [Official docs](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions) |
| Gemini CLI | Defaults to GEMINI.md; `context.fileName` can include AGENTS.md. Workspace/ancestor loading is supplemented by tool-triggered JIT scans to a trusted root. `/memory show` and `/memory reload` expose or refresh loaded context. | AGENTS.md needs configuration here. JIT discovery is documented, but concatenation does not prove semantic conflict reconciliation or maintenance correctness. [Official docs](https://geminicli.com/docs/cli/gemini-md/) |

## Decision-relevant limits

- Unification may reduce duplicate entry points, but none of these sources compares one lifecycle skill against several skills. ACE separates responsibilities; that is compatible with either packaging choice.
- Pruning should be evaluated separately from retrieval budgets. Losing active-context detail is different from retiring a durable claim. ACE's collapse example challenges equating fewer tokens with better knowledge.
- Automatic reversible maintenance fits the user's authority choice, but differs from report-only and reviewer-publication examples. These references provide evidence shapes, not permission or a policy that overrides the user.
- A pilot needs to show that future agents retrieve and apply retained guidance, that counterexamples survive refinement, and that deletion or correction is attributable and reversible. This is an inference from the evidence, not a selected architecture.

## Access and verification limits

All originally linked pages and the domain-modeling examples were inspected through rendered web pages. GitHub Contents API and raw-page requests failed in this tool; verified rendered directory links supplied filenames. The detailed Codex AGENTS guide redirected to a page whose substantive content failed to retrieve, so the official model guidance supplies the narrower CLI claims above. Private homelab source, social-post evidence, and the Artichoke linked migration page were not independently verified. No provider runtime test, paper reproduction, or controlled comparison was performed. Hooks are intentionally left to the separately assigned provider research.
