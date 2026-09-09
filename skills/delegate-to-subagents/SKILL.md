---
name: delegate-to-subagents
description: Use when delegating tasks to subagents for improved efficiency and specialization.
---

Activate or load the `subagent-model-router` skill and orchestrate execution using subagents whenever doing so would minimize cost and latency while not sacrificing quality. You should also consider the size and scope of the work to be done because subagents can help prevent your context window from bloating.

When you do spawn subagents:
  - Assign the model type based on the result of `subagent-model-router`.
  - Give each subagent a max runtime based on the complexity and expected duration of the task. This helps prevent churn if a subagent chooses a wrong course of action or doesn't have enough context to effectively complete a task.
  - If a subagent times out or fails, it must report all failures, errors, mistakes, learnings and progress so that you can delegate the task to a new subagent based on the work of the previous subagent.
  - If you spawn parallel subagents, ensure that file ownership is explicitly defined to avoid collisions.
