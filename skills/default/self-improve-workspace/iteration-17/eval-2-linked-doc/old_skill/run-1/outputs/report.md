# Learnings

- Durable guidance from session notes: after editing rollout manifests, run `python3 scripts/release_sanity.py`.
- Placement correction: release workflow details belong in `docs/release.md` (linked from root `AGENTS.md`), not in root guidance.

# Applied updates

- Updated `outputs/repo/docs/release.md` to insert `python3 scripts/release_sanity.py` immediately after rollout manifest edits and before `./scripts/check-release`.
- Left `outputs/repo/AGENTS.md` unchanged to preserve short root guidance and linked-doc ownership.
