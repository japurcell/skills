# Learnings

- Auth return-url checks should validate decoded prefixes and reuse shared policy coverage across guard and login paths.
- Auth mutation fixes should keep cached read streams separate from fresh-fetch mutation paths to avoid `shareReplay(1)` replay regressions.
- Login accessibility and regression work should preserve existing error/focus behavior while composing helper and error associations in stable order.
- Auth test guidance should capture Jasmine structure limits, time-assertion anti-flake ranges, focused validator targeting, dev-route caveats, and staged production `_Host` artifacts.

# Applied updates

- Updated `outputs/repo/docs/auth.md` with mined auth/login guidance from `progress.txt`.
- Left `outputs/repo/AGENTS.md` unchanged because it already keeps root guidance short and routes auth/login detail to `docs/auth.md`.

# Assumptions

- Interpreted the "right file" as `outputs/repo/docs/auth.md` because root `AGENTS.md` already delegates auth/login detail there.
- Treated this as a docs-only benchmark task, so no code or test files required updates.
