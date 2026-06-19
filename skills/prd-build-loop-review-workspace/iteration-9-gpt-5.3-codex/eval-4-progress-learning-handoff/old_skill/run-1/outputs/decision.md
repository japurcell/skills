# Self-improve handoff decision (dry-run)

## What orchestrator must pass to `self-improve`
- Destination: nearby auth-focused `AGENTS.md` (prompt-worthy concise rules) plus linked auth docs for longer detail.
- Reusable guidance only; exclude story IDs, timestamps, raw progress blocks, one-off blockers, and temporary tracking notes.
- Keep exact technical tokens where they are part of durable rules (`shareReplay(1)`, `aria-describedby`, `wwwroot/dist/browser/index.html`).
- Distilled reusable rules, grouped at minimum by:
  1. Validation/safety
  2. Cache/state/replay
  3. UX/accessibility
  4. Testing/anti-flake
  5. Environment/setup

## Progress-file sections orchestrator must mine
- `## Codebase Patterns` (top-level durable patterns).
- Every `## ... - story-local-auth-returnurl` entry:
  - `Patterns discovered`
  - `Gotchas encountered`
  - `Useful context`
- `## ... - FINALIZATION` reviewer entry, especially its `Patterns discovered`, `Gotchas encountered`, and `Useful context` about recording durable guidance and placement in nearby auth docs.

## Reusable learnings to preserve
- **Validation/safety**
  - Validate return-url prefix safety against decoded forms, not raw-only strings.
  - Reuse shared return-url policy across guard/login/startup paths for consistent hardening.
  - Preserve single-rule validator targeting; avoid placeholder defaults that trigger unrelated validator failures.
- **Cache/state/replay**
  - Stable replay-bug fix shape: keep cached stream for reads, use fresh-fetch command path for mutations.
  - Treat stale-first `shareReplay(1)` behavior as replay-risk pattern in success flows.
- **UX/accessibility**
  - Preserve existing error/focus UX when extending login helpers.
  - Compose `aria-describedby` in stable order: helper text first, contextual errors after.
- **Testing/anti-flake**
  - Keep Jasmine test blocks at describe root (no nested `it`).
  - Use range-based assertions for time claims to reduce flake.
  - Keep targeted/filtered auth regression tests for fast, focused validation.
  - Preserve existing failed-login behavior coverage when adding success-path fixes.
- **Environment/setup**
  - Dev route prefix can affect browser path checks; account for route prefix in direct `/login` validation.
  - Startup production-route coverage may require staged dist artifact at `wwwroot/dist/browser/index.html`.
