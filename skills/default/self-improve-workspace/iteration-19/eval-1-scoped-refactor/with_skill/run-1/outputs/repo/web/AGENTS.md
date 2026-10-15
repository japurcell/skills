# AGENTS.md (web)

- Tests: run `pnpm --dir web test -- --runInBand` after changing anything in `web/`.
  - Reason: shared fixtures require serial test runs; passing `--runInBand` forces serial execution.
- Use `pnpm` as project package manager for web.
- Keep scoped test guidance near the web code to avoid root bloat.
