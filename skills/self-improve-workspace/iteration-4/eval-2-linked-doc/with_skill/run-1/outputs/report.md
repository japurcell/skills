# Report

## Learnings

- After editing rollout manifests, run `python3 scripts/release_sanity.py` to validate rollout changes.
- Release details belong in `docs/release.md` (root `AGENTS.md` should remain brief and link to detailed docs).
- Avoid creating ephemeral scratch files like `notes.txt` in repo; prefer session-only artifacts.

## Applied updates

- Updated `outputs/repo/docs/release.md`: added step to run `python3 scripts/release_sanity.py` after editing rollout manifests.
- No changes made to `outputs/repo/AGENTS.md` to preserve concise root guidance.
- Copied fixture repo into `outputs/repo/`, excluding `session_notes.md`, as required.

Summary of changed files

- outputs/repo/docs/release.md
- outputs/report.md
