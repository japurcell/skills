Self-improve handoff must include a compact guidance packet built from `progress.txt` (supplemental) while keeping `prd.json` as official completion source.

Required payload to `self-improve`:
1. Target update scope: nearby auth-focused `AGENTS.md` (not root/global unless that is the nearby owner doc).
2. Source artifacts: path to `progress.txt`, path to `prd.json`, and extracted durable bullets only.
3. Inclusion rule: preserve reusable guidance only (module conventions, non-obvious gotchas, important file relationships, testing expectations, config/environment requirements).
4. Exclusion rule: omit story-specific chronology, one-off fixes, timestamps, and implementation-only status notes.

Progress sections to mine:
1. `## Codebase Patterns` block at top.
2. Each entry’s `**Learnings for future iterations:**` subsections:
   - `Patterns discovered`
   - `Gotchas encountered`
   - `Useful context`
3. `## ... - FINALIZATION` reviewer entry, especially its recording guidance and placement guidance.

Reusable learnings to preserve from this fixture:
1. Centralize auth/login guidance in scoped auth docs; avoid bloating root notes.
2. Return-URL hardening rule: validate decoded prefixes and reuse one shared policy across guard/login/startup paths.
3. Reactive-flow stability rule: keep cached read stream separate from fresh-fetch mutation path to avoid replay/stale-first regressions (notably `shareReplay(1)` behavior).
4. Accessibility composition rule: keep `aria-describedby` order stable (helper text before contextual errors) while preserving existing error/focus UX.
5. Test reliability rules: avoid nested Jasmine `it`; use range-based time claim assertions to reduce flake; keep validator targeting narrow to prevent unrelated false negatives.
6. Environment/path gotchas: dev route prefix affects browser checks; direct `/login` may miss intended dev route; startup production-route tests may require staged dist artifact (`wwwroot/dist/browser/index.html`).
