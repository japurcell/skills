Pass `self-improve` the nearby auth-scoped `AGENTS.md` update target (or its linked auth guidance doc if that `AGENTS.md` delegates there), plus a distilled evidence packet from `progress.txt`. Tell it that `progress.txt` is mined only for durable guidance, not story completion, and that it must keep only reusable auth guidance rather than story-specific notes or timestamps.

Mine these `progress.txt` sections:
1. `## Codebase Patterns`
2. Every `## 2026-06-12... - story-local-auth-returnurl` entry, but only the `**Learnings for future iterations:**` subsections (`Patterns discovered`, `Gotchas encountered`, `Useful context`)
3. `## 2026-06-12T12:00:00Z - FINALIZATION`, especially the reviewer note that final recording must capture reusable auth, validation, accessibility, and startup-test rules, and that nearby auth docs should own them instead of root guidance

Preserve reusable learnings in these categories:
1. Module conventions and file relationships: keep auth/login guidance in one scoped location; reuse one shared return-url policy across login, validation, guard, and startup paths; validate decoded prefixes, not only raw strings
2. Non-obvious implementation gotchas: replay-prone login flows should keep cached read streams and use fresh-fetch command paths for mutations; `shareReplay(1)` can cause stale-first failures; compose `aria-describedby` in stable order with helper text before contextual errors while preserving existing focus/error UX
3. Testing expectations: preserve existing failed-login behavior coverage; filtered auth tests are useful fast coverage; Jasmine forbids nested `it`; time-based claim assertions should use ranges; keep single-rule validator targeting; avoid placeholder defaults that trigger unrelated validators
4. Environment and route requirements: dev route prefix matters for browser checks, and startup production-route coverage may require staged `wwwroot/dist/browser/index.html`
