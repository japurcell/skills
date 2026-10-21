Goal: finish the tenant purge staging rollout.

Current state:
- Implementation is complete in `src/tenant_purge.py`.
- `python3 -m unittest tests.test_tenant_purge` passed all 4 tests after the implementation change.
- No staging or production rollout has occurred, and no staging smoke test has run.

Owner action:
- The workspace owner must enable `TENANT_PURGE_ENABLED` in the staging secret store, then run the release smoke test and share its result.
- The agent has no access to the staging secret store and is not authorized to change rollout settings or deploy.
- Keep the handoff open until the owner reports the smoke-test result. Do not describe staging as verified.
