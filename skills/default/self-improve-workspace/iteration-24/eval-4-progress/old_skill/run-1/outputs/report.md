# Learnings
- Prefix validation must check decoded forms, not only raw strings.
- Auth/login tests should keep `it` blocks at `describe` root.
- Shared return-url policy, cached-read/fresh-mutation split, stable `aria-describedby` ordering, ranged time assertions, and single-rule targeting are reusable auth/login safeguards.
- Startup tests that need the production `_Host` branch may need a staged minimal `wwwroot/dist/browser/index.html` artifact.

# Applied updates
- Added the durable auth/login learnings to `outputs/repo/docs/auth.md`.

# Assumptions
- `docs/auth.md` is the correct home for these reusable auth/login notes because root `AGENTS.md` already routes auth guidance there.
