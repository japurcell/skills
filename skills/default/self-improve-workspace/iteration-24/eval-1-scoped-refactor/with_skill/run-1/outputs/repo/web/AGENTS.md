Run `pnpm --dir web test -- --runInBand` after changing anything in `web/`.

`web/` uses shared fixtures, so test runs must stay serial.
