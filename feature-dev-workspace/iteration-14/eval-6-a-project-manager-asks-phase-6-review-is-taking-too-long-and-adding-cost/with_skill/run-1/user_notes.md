Eval 6 — Minimum non-negotiable Phase 6 subagent steps

- Prompt: PM wants to cut Phase 6, what are the absolute minima?
- Key answer: exactly 2 required subagent steps, both "always" in workflow
- Step 1: code-simplifier — "Always launch" (Action 1), runs first
- Step 2: code-reviewer(s) — "Always run" (Action 2), runs after simplifier
- Ordering constraint: code-simplifier BEFORE code-reviewer (Actions listed in this sequence)
- Neither step can be dropped — workflow uses "always" for both
- Acceptable optimizations: single reviewer on Light track, tighter scope per agent, parallel reviewers on Standard/Deep
