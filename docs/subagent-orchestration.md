# Orchestrating subagents for throughput and context quality

For `delegate-to-subagents` and `execplan-implement`, reuse a worker when the next assignment depends on reasoning it already did. Start a fresh worker with a short brief when the work is independent or calls for a second opinion. Keep enough state in the plan, repository and test results for either choice to work. These are proposed defaults for this repository, reviewed November 17, 2026.

## Choose coordination from the work graph

| Work shape | Coordination | Practical constraint |
|---|---|---|
| One bounded task or mostly sequential work | One worker at a time | Avoid coordination cost where little work can overlap |
| Independent research or implementation slices | Parallel workers, one integration owner | Give each worker an exclusive artifact or file set |
| Tasks become ready as dependencies resolve | Dispatch from the ready frontier | Update readiness after each accepted dependency |
| A producer and consumer can develop concurrently | Pair two owners | Give them a sample artifact and a direct channel for interface decisions |
| Shared interfaces, shared files, or tight dependencies | One owner and serialized changes | Agree on interfaces before parallel edits |
| Independent review | Fresh reviewer, separate from author | Keep review axes independent and pass findings to the author for narrow fixes |

A controlled study of 260 configurations across six benchmarks found relative performance changes against a single agent ranging from +80.8% on decomposable financial reasoning to -70.0% on sequential planning. Anthropic reports a 90.2% improvement over a single Opus 4 on its internal research evaluation. It separately reports that multi-agent systems used about 15 times as many tokens as ordinary chats. These results help explain why a broad source search and a chain of dependent coding decisions deserve different staffing. [Kim et al.](https://arxiv.org/abs/2512.08296v3) · [Anthropic’s multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)

Cursor’s swarm skill makes the parent choose how it will use worker results before dispatch. With **partitions**, each worker owns a different slice and a missing slice leaves a coverage gap. With **a race**, workers attempt the same problem and the parent declares whether it needs the first verified pass or a ranking of all candidates. A race buys alternative attempts at the cost of duplicate effort. [Cursor swarm skill](https://github.com/cursor/plugins/blob/main/pstack/skills/swarm/SKILL.md)

At the linked moment in OpenAI’s DevDay talk, the speaker describes asking a stronger specialist for help on a hard subproblem. At 14:33 he describes a different arrangement. One agent captured a legacy game scene and a second reconstructed it in Blender. The import format informed what the first agent needed to capture. For a comparable producer and consumer, let them exchange a sample, incompatible assumptions and agreed changes as they arise. Their raw tool logs can stay local. [OpenAI DevDay at 14:12](https://youtu.be/nAubbmlhPfI?t=852) · [Pair example at 14:33](https://youtu.be/nAubbmlhPfI?t=873)

## Context mode and workspace are separate choices

Make both choices explicit at dispatch and handoff.

| Context mode | What carries forward | Use when |
|---|---|---|
| Resume same worker and history | Same worker identity, transcript, and its available state | Prior reasoning remains useful and continuity is valuable |
| New worker with whole parent transcript | The starting context includes the parent’s reasoning and tool history | A specialist needs an intricate sequence of observations that would be costly or risky to reconstruct |
| New worker with compact brief and pointers | Fresh reasoning context plus selected task state, artifacts, and source pointers | Context is stale or noisy, or the assignment needs a clean independent perspective |

Choose workspace access separately. A fresh reviewer can inspect the same commit in a read-only checkout. Competing implementers can start from that commit in isolated worktrees.

Reuse pays when the worker can use the test it just ran and the alternatives it ruled out to resolve the next decision. Rotate when the task changes, old observations refer to a superseded revision, or the worker keeps pursuing a failed hypothesis. For a transfer, give the incoming worker the last verified revision, evidence, failed attempts and next open decision. Preserve the skills’ existing deadlines and verify the outgoing worker and its write-producing operations have stopped before transferring ownership.

Anthropic’s app-building harness used resets and written handoffs with Sonnet 4.5. With Opus 4.5 the team removed forced resets and used continuous sessions with automatic compaction. Matt Pocock’s experimental chief-of-staff skill starts every worker fresh. Each retrieves context through pointers, while a long-lived parent and dated wiki retain decisions. Both illustrate why project memory can outlive a particular worker. [Anthropic’s harness comparison](https://www.anthropic.com/research/harness-design-long-running-apps) · [Chief-of-staff skill](https://github.com/mattpocock/skills/blob/main/skills/in-progress/chief-of-staff/SKILL.md)

Two narrower experiments help with the decision. Across 13 long-horizon optimization tasks, Fork-and-Flush inherited the workspace, started several fresh chats and continued the highest-scoring branch. It beat single-run and best-of-N baselines under equal compute. The result applies to the combined search procedure and depends on a score for choosing branches. A separate 36-run technical report on 12 coding tasks found resetting every task cost 33.5% more in modeled spend than resetting every third task. Three, four and six tasks per session were statistically indistinguishable on cost. The agent wrote its own tests, limiting conclusions about quality. Neither experiment establishes a reset interval for this repository. [Fork-and-Flush](https://arxiv.org/abs/2610.07447) · [Corrected session-length study](https://doi.org/10.5281/zenodo.22759217) · [Author’s results and dataset index](https://arsentev.ai/research)

## Context through a worker's lifecycle

**Before dispatch**, give the worker the facts it would otherwise have to rediscover. Point to the source for detail. A hypothetical parser brief could read, “Own `parser/` in your task worktree. Older exports can omit `source_id`. The format is in `docs/import-format.md`. Acceptance is a passing `test_import_legacy_export` on the unmodified legacy fixture. The schema owner handles shared types.” The compatibility rule is worth putting inline because missing it would invalidate the implementation. [Anthropic on just-in-time context](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents) · [OpenAI on repository knowledge](https://openai.com/index/harness-engineering/)

**During work**, send new information to the person who can act on it. The parser worker might say, “The legacy fixture reaches the schema validator, which rejects a missing ID. The schema owner needs to decide how we represent that case before the importer can proceed.” The parent can assign that decision immediately while unrelated work continues.

**At completion**, return the outcome, evidence, remaining uncertainty and consequence for the next owner. After the schema decision, the example result could read, “Parser accepts the legacy fixture at `<commit>`. The focused contract test passed. The importer can now run its end-to-end check against that revision.” Keep long test output at an accessible path and attach the relevant excerpt if a check fails.

A checkpoint preserves facts another worker needs to resume. A prompt cache reuses computation over matching input. It can reduce the price of rereading history while that history still occupies the context window.

## Integration owner and backpressure

The existing ExecPlan skill already gives one persistent integration owner responsibility for merge waves, status and final checks. It verifies follow-up delivery and leaves the owner idle between bounded assignments. For each wave, send the tested base and task revisions, changed interfaces, checks performed and blockers. Keep these in the plan or existing coordination record so a replacement can resume.

Limit new implementation starts when completed work is accumulating faster than the integration owner or CI can accept it. Prefer the task that unblocks the next dependent slice. Cursor’s shared-lock experiment illustrates the cost of scheduling by worker count alone. Twenty agents sometimes delivered the effective throughput of two or three while the rest waited for locks. That figure describes Cursor’s experiment. Track the actual queue in this repository. [Cursor on scaling long-running coding](https://cursor.com/blog/scaling-agents)

## Review and fixes

Keep standards and spec review axes independent. Assign each to its own reviewer. Once a narrow issue is confirmed, the original author can fix it because they have the implementation context. Then use an independent reviewer to verify the fix and check it did not introduce a new issue. If the finding changes architecture or crosses ownership boundaries, create a new task on the ready frontier instead of silently expanding the narrow fix.

## Prompt caching and token accounting

OpenAI describes Codex retaining the prior prompt as an exact prefix of the next prompt, allowing prompt-cache reuse. Put stable instructions, tool definitions, and examples first, then append changing task content. Changing tools, model, sandbox, approval mode, or working directory can invalidate the prefix. Cache reuse saves repeated inference work but does not make a long context free or remove its attention cost. [OpenAI, Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/)

For Responses usage, inspect `input_tokens_details.cached_tokens` and, where supported, `cache_write_tokens`. Calculate ordinary input and cache-write charges from the provider’s reported categories and the selected model’s rates without double-counting. Cached input can cost less, but a high cache-hit rate alone does not show total savings. [Prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching) · [Pricing](https://platform.openai.com/pricing)

## Controlled workload evaluation

Keep skill-authoring evals for clarity and instruction following. Add separate workload evals comparing solo, parallel, sequential, persistent resume, new worker with full parent transcript, and compact fresh-context handoff. Hold the task, model, tools and compute ceiling constant. Record deviations and grade the resulting artifacts against the same acceptance checks.

Track accepted tasks per hour and total spend per accepted result as primary measures. Also report quality or acceptance rate, wall-clock time, uncached and cached input, output tokens, tool/model calls, merge/CI wait, and review effort. Slice by task family and policy. Do not set universal worker counts or reset intervals from a small benchmark.

For a first local comparison, replay an independent research task, a fix with a known failing test and a merge wave with a shared interface. Pin each starting revision and use the same external acceptance checks. Repeat each policy on the same tasks. First vary worker history with staffing held constant, then vary concurrency with the history policy held constant. Include failed runs, duplicate attempts and retries in the numerator for cost per accepted task.

## Proposed amendments

For [delegate-to-subagents](../skills/default/delegate-to-subagents/SKILL.md), add a decision *before* routing. Specify whether another worker buys independent coverage, overlapping work, an alternative attempt, or a clean review. Batch tightly coupled steps into one bounded assignment. After routing, reuse an eligible worker only when its prior context materially helps. Put the chosen context mode and expected evidence in the existing assignment record.

For [execplan-implement](../skills/default/execplan-implement/SKILL.md), keep the persistent integration role and make its state recoverable at each merge. Schedule ready tasks against merge and CI capacity. Reuse the relevant author for a narrow fix when the route still matches. A reviewer can resume to verify a specific finding. Start fresh, with the spec, diff and observable checks, when the assignment calls for independent discovery.
