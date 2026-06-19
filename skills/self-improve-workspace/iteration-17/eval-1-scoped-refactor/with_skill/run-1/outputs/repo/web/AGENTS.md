# AGENTS.md

Web package guidance.

- After changing anything in `web/`, run `pnpm --dir web test -- --runInBand`.
- Keep web test runs serial because shared fixtures fail in parallel.
