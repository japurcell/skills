web/ scoped rules

- Use pnpm.
- Run tests serially (shared fixtures): `pnpm --dir web test -- --runInBand`.
- Run `pnpm --dir web test` after changing anything in `web/`.
