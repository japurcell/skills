---
name: delegate-to-subagents
description: Use when spawning subagents for parallelism, specialization, or context isolation. Use when the user mentions 'create a subagent', 'spawn a subagent', or 'fan out'.
---

Delegating bounded tasks to specialized subagents can reduce cost and latency, improve quality, or preserve the main context. Delegate when the benefit exceeds coordination overhead.

Define each task's objective, context, constraints, deliverable, verification, and allowed files.

For each task:

1. Activate the `subagent-model-router` skill and record its full result.
2. Apply `agent_type` and `model` through the runtime's spawn configuration.
3. Keep the router result out of the subagent prompt.
4. Give the subagent only the information needed to perform the task.
5. Set a runtime limit appropriate to the task.

If the runtime has no role field, include only the role and its boundaries in the prompt. If it cannot apply the selected role or model, use the router's fallback or reroute using available options. Never put a model name in the prompt as a substitute for runtime configuration.

Verify each result before using it. If an agent fails or times out, preserve any output, errors, mistakes, learnings, and partial progress exposed by the runtime and pass the relevant state to a replacement agent.

For parallel work, assign non-overlapping write ownership and make dependencies explicit.
