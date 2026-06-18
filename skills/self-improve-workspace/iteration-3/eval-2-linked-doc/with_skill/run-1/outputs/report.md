# Report

## Learnings

- After editing rollout manifests, run `python3 scripts/release_sanity.py`.
- Release process detail belongs in `docs/release.md`, not root `AGENTS.md`.

## Applied updates

- Copied fixture repo into `outputs/repo/`, excluding `session_notes.md`.
- Updated `outputs/repo/docs/release.md` to add `python3 scripts/release_sanity.py` immediately after rollout manifest edits.
- Left `outputs/repo/AGENTS.md` unchanged because it already points release detail to `docs/release.md`.
