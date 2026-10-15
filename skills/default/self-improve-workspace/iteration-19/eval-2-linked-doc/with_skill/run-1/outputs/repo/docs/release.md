# Release process

1. Update rollout manifests.
2. Run `./scripts/check-release`.
3. Tag the release.

## Post-edit checklist

- After editing rollout manifests, run `python3 scripts/release_sanity.py`.
- Release details belong in docs/release.md (not root AGENTS.md).
