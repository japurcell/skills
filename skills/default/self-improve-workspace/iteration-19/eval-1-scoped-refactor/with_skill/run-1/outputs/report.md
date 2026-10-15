Learnings

- Root AGENTS.md was too broad; scoped rules (web tests, api schema validation) belong near the code they affect.
- Web tests require serial runs due to shared fixtures; use `pnpm --dir web test -- --runInBand`.
- After editing `api/schema/*.json` run `python3 scripts/validate_schema.py`.
- Repo has README (no durable changes required for README now).

Applied updates

- Edited: outputs/repo/AGENTS.md (made root file minimal, added pointers to scoped AGENTS files).
- Created: outputs/repo/web/AGENTS.md (web test command + reason).
- Created: outputs/repo/api/AGENTS.md (schema validation + location of API contract notes).

Moved guidance

- Moved web test command and serial-test note from root AGENTS.md → web/AGENTS.md.
- Moved schema validation note from root AGENTS.md → api/AGENTS.md.
- Root file now points to scoped AGENTS.md files.

Grouped files

- Root: outputs/repo/AGENTS.md
- Web-scoped: outputs/repo/web/AGENTS.md
- API-scoped: outputs/repo/api/AGENTS.md

Notes

- No other durable learnings qualified for root placement; no deletions beyond moving scoped lines were necessary.
- If more detailed API-contract guidance is needed, create `outputs/repo/api/README.md` and link from api/AGENTS.md.
