---
name: delegate-to-subagents
description: Use when spawning subagents for parallelism, specialization, or context isolation. Use when the user mentions 'delegate to a subagent', create a subagent', 'spawn a subagent', or 'fan out'.
---

Delegating tasks to specialized subagents can reduce cost and latency, improve quality, or preserve the main context. Delegate when the benefit exceeds coordination overhead.

## Steps

For each task:

1. Define the tasks's **objective** including: context, constraints, deliverable, verification, and allowed files.
2. Activate the `subagent-model-router` skill and record its full result.
3. Apply `model` through the runtime's spawn configuration. Apply the effort/reasoning level if provided.
4. Subagent prompt:
   - Provide the subagent with the task's **objective**.
   - Keep the router result out of the subagent prompt.
   - Set a runtime limit appropriate to the task.

Wait for all subagents to complete their tasks before proceeding so that you don't duplicate work or encounter conflicts.

If an agent fails or times out, record and preserve it's output: all errors, mistakes, learnings, and partial progress. Then delegate the task to a replacement subagent with the preserved context.

**Important:** For parallel work, assign non-overlapping write ownership and make dependencies explicit. This is important to avoid conflicts and ensure smooth coordination among subagents.

## Efficiency

You are the orchestrator of subagents, responsible for delegating tasks efficiently and ensuring smooth coordination among them.

**Prevent double file reads:** Avoid reading task-specific files that are going to be read by the subagents unless absolutely necessary for orchestration purposes. Double-reading files is inefficient and expensive.

Suggestion: Delegate context gathering to an **exploration subagent** using the cheapest capable model available. It could read all required relevant codebase files or external documentation so that you and other subagents don't have to. It could save its markdown notes in a shared location accessible by all future subagents.
