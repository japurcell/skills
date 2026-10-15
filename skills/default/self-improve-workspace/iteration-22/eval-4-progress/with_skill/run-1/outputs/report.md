## Learnings
Mined `progress.txt` for durable guidance related to the `story-local-auth-returnurl` feature:
- Security/validation: evaluate decoded forms for prefix safety; avoid placeholder defaults to prevent unrelated validation failures.
- Testing: Jasmine forbids nested `it`; keep test blocks at describe root. Time-based claim assertions should use ranges to avoid flake. Preserve single-rule targeting.
- Architecture/State: Keep cached stream for reads; use fresh-fetch command path for mutations to avoid replay bugs. `shareReplay(1)` stale-first behavior can cause false UI failure on success flows.
- Accessibility/UX: Compose `aria-describedby` in stable order: helper first, then contextual errors. Preserve existing error/focus UX.
- Environment: Dev route prefix matters for browser checks. Browser direct `/login` may not hit the right dev route.

## Applied updates
- Updated `docs/auth.md` to append the extracted learnings.
- Maintained the existing structure where auth/login guidance lives in `docs/auth.md` rather than polluting the root `AGENTS.md`.

## Assumptions
- The root `AGENTS.md` explicitly routes authentication and login detail to `docs/auth.md`. Following the rule "If one topic doc already owns a workflow, keep related test, accessibility, or state-management learnings with that topic unless they clearly stand alone as repo-wide rules", all learnings from the `story-local-auth-returnurl` sprint were grouped into `docs/auth.md` to avoid splitting related rules.
- The learning about `wwwroot/dist/browser/index.html` was already present in `docs/auth.md` and was preserved without duplication.
