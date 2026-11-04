# Exact dependency claim admission

This foundation admits one administrative `dependencies` claim in phase `preparing` and stops. Repository state remains `ready`; the claim excludes ordinary writers. No backup, operation directory, candidate, stage, handoff, compiler/npm execution, live-file/domain change or completion producer is provided. Verified backup is the next separate task. Public dependency mutation, publication/recovery and authored dependency installation remain later tasks.

## Package seams

- `inspectDependencyMaintenanceSelection(repository, {mode: 'repair', bundleRoot, manifestSha256})` authenticates the complete selected bundle and requires its exact manifest, declaration and lock to match the installed selection. It returns a deterministic digest and separately authenticated expected inventory and observed known-file damage.
- `admitDependencyMaintenance(repository, source, expectedSelectionDigest, owner?)` recomputes that selection and admits only an idle genuinely installed current-schema repository. The current Node/SQLite profile, database identity, exact previous completion, sole claim, immutable original ownership and selection are checked under the existing immediate writer transaction. Only `owner_claims` and one bounded `maintenance.started` event change.
- `assertDependencyMaintenance(repository, handle)` revalidates the exact operation/claim/token through a dedicated claimed-ownership gate. It re-derives the same original expected and observed facts, authenticates the selected bundle again and refuses changes without adopting them.
- `inspectDependencyMaintenance(repository, operationId)` returns bounded redacted preparing facts with `backupBound: false`; it never discloses the token or external provider paths. Generic maintenance inspection uses the same revalidation.

The compact typed claim binds original completion and receipt ownership, database/factory/toolchain identities, expected inventory SHA256 and independently measured observed-tree digest. These are separate facts, not interchangeable hashes. Missing or changed known regular selected files remain eligible for inspection; unowned/extra/link/special/missing-root/directory/mode/runtime/retained-original changes retain existing strict refusal. Ordinary startup and upgrade remain strict.

Generic dependency admission, clearance, release, handoff and reclaim cannot bypass this boundary. The existing generic handoff/recovery fixture now uses the still-generic `cleanup` kind because dependencies require genuine installed selection. Every original controller assertion remains intact; explicit generic-dependency rejection tests cover the stronger invariant. No automatic claim release, retry, restore, adoption or salvage was introduced.

## Verification

From `packages/software-factory`, on pinned Node 24.22.1, run `rtk proxy node --test test/dependency-maintenance.test.mjs test/maintenance-controller.test.mjs test/forward-schema.test.mjs` and `rtk proxy node --test qualification/dependency-claim-native.qualification.mjs`. The coordinator owns registry and CI wiring.

The explicit test areas are `rtk proxy node scripts/test.mjs release --area dependency-claim` and `rtk proxy node scripts/test.mjs qualification --area dependency-claim`. Linux CI invokes the native area in its own target-scoped 15-minute phase with exact Python/helper/cache inputs. This is claim-foundation qualification, not a public dependency repair operation; maintenance `--operation dependencies` remains unimplemented and refuses selection. Registration alone does not establish Linux acceptance.

The native fixture requires explicit Darwin arm64 or Linux x64, the matching manifest-pinned archive in `FACTORY_TEST_NODE_ARCHIVE`, an exact toolchain offline seed in `FACTORY_TEST_NPM_CACHE_SEED`, and qualified Python 3.13.14 in both `FACTORY_TEST_PYTHON` and `FACTORY_ATOMIC_PYTHON`. Missing or mismatched prerequisites fail without skips or network/interpreter fallback. Use canonical paths, pinned Node PATH, a fresh task-private cache and narrowly allowed fixture-owner queries. Freeze the whole checkout from build through complete proof exit.

Five genuine disposable scenarios cover installed and publicly upgraded baselines, two dependency callers, and simultaneous dashboard, runner and other-maintenance contenders. Exactly one request wins; an ordinary winner may close its own ordinary claim before a new explicit dependency request. A winning typed competing maintenance claim is retained and that scenario ends after checking its exclusive state and preservation. Other scenarios prove stale manifest/selection/completion/token refusal, claimed selected/runtime/selection tampering, generic recovery refusal, separate expected/observed facts, no new backup/stage, and byte/domain/history preservation. Fixture-owned corruption is restored only to finish negative controls; product restore is absent.

The prior ownership foundation's Linux proof does not qualify this new admission seam. Record native results by actual host. No provider, account, credential, desktop, global installation, real user repository or published release is involved.
