---
name: council
description: Run a model-diverse subagent council to investigate the same problem from multiple perspectives, compare findings, and produce a final recommendation. Use when the user asks for a council or wants independent judgments from multiple model families on a problem, decision, or proposal.
---

# Council

Brief read-only delegates identically on question, evidence (excerpt inaccessible sources), constraints and criteria. Withhold peer reports. Request independent, cited conclusions and what would change them.

Configure current catalog IDs for OpenAI Sol, Claude Opus and Gemini Neon at high effort or its documented equivalent. Prefer native delegates, otherwise use authorized CLIs, APIs or runners within parent access and permissions.

For Codex `spawn_agent`, set Sol’s `model`, `reasoning_effort="high"` and `fork_turns="none"` when overrides require it. Verify the answering child’s turn-context `model` and `effort`.

Check `gh copilot -- --help`. Discover IDs via interactive `/model` or `gh copilot -- --acp` (`initialize`, then `session/new`, model options in `result.configOptions`). Run each seat from the checkout.

```sh
gh copilot -- --model "$model_id" --reasoning-effort high --output-format json -p "$brief"
```

Check `session.start.data.reasoningEffort`. Match `selectedModel` to the substantive `assistant.message` and successful `model.call_final_result` model. Elsewhere use equivalent metadata. Disclose requested-only settings.

Launch concurrently where supported. Discard failed, empty or mismatched replies. Retry only those seats via compatible routes. On exhaustion, mark incomplete, name missing models and blockers, and attribute partial findings.

Check decisive claims and test competing premises where possible. Once all three respond, lead with the answer and evidence. Preserve material dissent and uncertainty. Give each contributor’s exact versioned model ID and effort. Be proportionate.
