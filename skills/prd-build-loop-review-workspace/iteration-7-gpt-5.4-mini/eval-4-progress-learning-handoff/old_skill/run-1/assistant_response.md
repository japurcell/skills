Pass `self-improve` the reusable guidance distilled from `progress.txt`, plus the nearby `AGENTS.md` that should receive the update. Treat `progress.txt` as resume data only; do not copy story-specific details or completion status into guidance.

Mine these sections from `progress.txt`:
- `## Codebase Patterns`
- every latest story entry, including the final `FINALIZATION` entry

Preserve only reusable learnings:
- auth/login guidance belongs in one scoped place; do not scatter it
- preserve existing focus and error behavior when extending auth helpers
- validate decoded prefixes, not just raw strings
- reuse shared return-url policy coverage across login and guard paths
- keep cached read streams separate from fresh-fetch mutation paths
- compose `aria-describedby` in stable order: helper first, then contextual errors
- keep time-based assertions range-based to avoid flake
- use single-rule targeting to avoid unrelated validator noise
- avoid placeholder defaults that trigger unrelated validation failures
- startup-route tests may need the staged dist artifact path
- final recording should capture reusable auth, validation, accessibility, and startup-test rules

Do not preserve:
- per-run timestamps
- story IDs
- implementation-only file lists
- pass/fail metadata
- one-off troubleshooting notes that are not reusable
