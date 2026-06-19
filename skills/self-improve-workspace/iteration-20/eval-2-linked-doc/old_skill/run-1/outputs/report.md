# Learnings

- Durable: after editing rollout manifests, run `python3 scripts/release_sanity.py`.
- Durable placement: keep release-detail guidance in `docs/release.md`, not root `AGENTS.md`, because root already links there.
- Excluded: `notes.txt` was one-off scratch noise and not durable guidance.

# Applied updates

- Copied fixture repo to `outputs/repo/`.
- Updated `outputs/repo/docs/release.md` to add `python3 scripts/release_sanity.py` after rollout manifest edits and before the existing release check/tag steps.
- Left `outputs/repo/AGENTS.md` unchanged so root guidance stays short and continues pointing release detail at `docs/release.md`.
