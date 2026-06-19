# AGENTS.md

- Run `pnpm --dir web test -- --runInBand` after changing files under `web/`.
- Keep `web/` tests serial because shared fixtures fail in parallel.
