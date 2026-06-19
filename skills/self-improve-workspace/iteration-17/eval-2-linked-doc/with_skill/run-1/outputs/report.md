## Learnings

- Qualified: After editing rollout manifests, run `python3 scripts/release_sanity.py`.
- Qualified: Keep release-process detail in `docs/release.md` (not root `AGENTS.md`) because root already delegates that topic.
- Not qualified: Temporary scratch-file note (`notes.txt`) is one-off and not durable guidance.

## Applied updates

- Copied fixture repo to `outputs/repo/`.
- Updated `outputs/repo/docs/release.md` to add `python3 scripts/release_sanity.py` as a release step after `./scripts/check-release`.
- Left `outputs/repo/AGENTS.md` unchanged to preserve linked-doc structure.
