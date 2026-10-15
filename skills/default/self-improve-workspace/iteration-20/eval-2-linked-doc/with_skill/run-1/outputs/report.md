# Learnings

- After editing rollout manifests, run `python3 scripts/release_sanity.py`.
- Release workflow detail belongs in `docs/release.md`, not root `AGENTS.md`, because root already links there.
- Scratch file note (`notes.txt`) did not qualify as durable guidance.

# Applied updates

- Copied fixture repo to `outputs/repo/`.
- Updated `outputs/repo/docs/release.md` to add `python3 scripts/release_sanity.py` after rollout manifest edits and before `./scripts/check-release`.
- Left `outputs/repo/AGENTS.md` unchanged so root guidance stays short and continues pointing release details at `docs/release.md`.
