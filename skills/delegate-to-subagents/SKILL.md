---
name: delegate-to-subagents
description: Use when delegating tasks to subagents for improved efficiency and specialization.
---

Activate or load the `subagent-model-router` skill and orchestrate execution using subagents whenever doing so would minimize cost and latency without sacrificing quality. Consider the work's size and scope because subagents can keep the main context focused.

When you do spawn subagents:
  - Before dispatch, record the router's `agent_type`, tier, exact model, reason, and fallback. Treat this result as the dispatch specification, not advice.
  - Select the narrowest available subagent or custom-agent role matching `agent_type`. If the runtime has no role field or matching named agent, put the selected role and its boundaries in the task prompt.
  - Apply the routed model through the runtime's supported per-agent mechanism, such as a spawn tool's model argument, a custom-agent profile's model field, or an agent override. Do not assume that the main session's model selection controls subagents.
  - If the exact model is unavailable or the runtime cannot set it per agent, use the router's same-tier fallback. If that is also unavailable, reroute using the models the runtime exposes and record the effective role, tier, model, and reason before dispatch.
  - After dispatch, report the effective role and model. Do not claim the route was applied when a supported routing field was omitted or inherited implicitly.
  - Give each subagent a max runtime based on the complexity and expected duration of the task. This helps prevent churn if a subagent chooses a wrong course of action or doesn't have enough context to effectively complete a task.
  - If a subagent times out or fails, it must report all failures, errors, mistakes, learnings and progress so that you can delegate the task to a new subagent based on the work of the previous subagent.
  - If you spawn parallel subagents, ensure that file ownership is explicitly defined to avoid collisions.
