# C2 selected backup authority and recovery dependencies

- Scope: POSIX-only advisory package reads. `resolveOwnedCleanupBackup(repository, {operationId, backupId})` returns owned, protected, or refused; `inspectCleanupRecoveryDependencies(repository)` returns proven clear or an unassessed blocker. C1 snapshot authority remains unassessed.
- Source: `packages/software-factory/src/cleanup-backups.ts`, narrow `RepositoryStore.readCleanupOperationEvidence`, explicit compiled module triplets in both `src/release.ts` and `skills/default/software-factory/scripts/install.py`. Schema remains 7.
- The repository argument is resolved through the existing canonical Git identity seam. The caller supplies no file path or ownership assertion. Invalid selections return a fixed refusal with no untrusted object echo.
- Completed upgrade ownership joins the unique exact committed `upgrade.completed` event to the exact retained new receipt, its committed backup-receipt hash, original and intent hashes, fixed backup request, private single-link backup identity/hash/bytes, known copied schema, integrity, foreign keys, repository/release/ready state, historical count digest and sole originating upgrade claim.
- Historical counts are checked only inside the authenticated immutable copy. Old installed trees are not reasserted. The reader creates no synthetic live claim capability and enumerates no filesystem directories.
- Backup directory birth identities were never persisted. Returned ancestry explicitly records currently observed identities; it does not invent historical directory ownership. Exact receipt and copied-file facts remain the authority chain.
- Fixed `history.sqlite-wal`, `-shm` or `-journal` presence refuses, including links. All bytes and evidence sidecars are retained.
- Current claims, global bootstrap/upgrade markers, occupied attempts, unknown operation suffixes and malformed activity prevent clear recovery. A missing claim alone never proves completion.
- Ordinary resolved attempts must match accepted terminal, type and invocation/run/operation/owner relationships. Explicit clearance requires the bounded exact clearance row plus its unique committed `owner.cleared` event. Clearances can resolve unfinished/unknown-cleanup invocations, but cannot bless a later false-quiescent or otherwise inconsistent attempt.
- SQL validates event/claim types and byte lengths before bodies enter JavaScript. Cursors remain signed SQLite decimal64 strings. Activity predicates return only the first typed blocker; clearance bodies are bounded to 16 KiB because the accepted writer permits 8 KiB details plus its envelope. No hard interruptible SQL deadline is claimed.
- First-install-only, unknown, unbound, abandoned and unsupported future terminal ownership remains refused or conservatively protected. Current forward and dependency preparing copies are protected without asserting historical deletion ownership.

## Verification

- Qualified Darwin arm64 Node 24.22.1, SQLite 3.53.4, Python 3.13.14 and an independently copied offline npm seed with undici-types 7.24.6. Distinct empty user/global npm configs are used by genuine public fixtures.
- Initial public RED genuinely installed 1.2.3 and upgraded to 1.2.4, then failed on missing C2 module: `/tmp/factory-cleanup-c2-public-red.log`, 83.652 seconds.
- Sidecar safety RED exposed immutable-open acceptance of an unexpected adjacent WAL: `/tmp/factory-cleanup-c2-public-negatives-red.log`. The complete suite reached EOF and its receipt postflight passed before the fix.
- Activity and terminal-shape RED evidence: `/tmp/factory-cleanup-c2-activity-red.log` and `/tmp/factory-cleanup-c2-terminal-red.log`. No tests or bounds were removed or weakened.
- Final strict package and qualification typechecks/build: `/tmp/factory-cleanup-c2-terminal-build.log`.
- Final focused exact-read/activity tests: 8/8, zero skips, `/tmp/factory-cleanup-c2-terminal-green.log`.
- Final genuine external Python public proof: 43/43, zero skips, 166.103 seconds, `/tmp/factory-cleanup-c2-public-activity-final.log`. Includes install then upgrade, historical/live count divergence, old-tree independence, missing/tampered/linked/replaced evidence, claimless markers, duplicates/future/unfinished operations, a genuinely ended workflow owner followed by exact public clearance, ordinary finalization, an interrupted third upgrade and a separate genuine installed dependency preparing backup.
- Eight explicitly labeled fault injections rebind only this genuine fixture's outer hashes to inconsistent copies, independently checking count/schema/repository/sole-claim/source/oversize/missing-claim/FK contracts. These are corrupted test inputs, never genuine producer output or a supported repair mechanism.
- Existing affected store/C1/maintenance/forward/dependency regression: 54/54, zero skips, 12.307 seconds, `/tmp/factory-cleanup-c2-activity-affected-regression.log`.
- Full frozen EOF/postflight completed 09:18:40 UTC. Current build inputs 729 and outputs 171, actual executable/archive/test-file hashes and private cache profile are retained in `/private/tmp/factory-cleanup-backup-authority-profile/profile.json` and `/tmp/factory-cleanup-c2-activity-final-postflight.log`.

## Remaining boundaries

- Coordinator owns registration, CI, canonical plan/handoff updates, integrated ordinary composition and native Linux qualification. Focused C2 and public qualification are selected only on supported POSIX profiles. This Darwin evidence does not establish Linux execution or Windows admission; Windows C1 remains open.
- No C3 reference graph/selection, new claim or transfer, backup creation behavior, deletion/pruning/compaction, DDL, public CLI, provider/authentication, desktop execution, candidate preparation, held candidate-native qualification or preserved scanner/mutation probe was added or executed.
- Reflection: the durable safety lessons are encoded in production guards and focused/public tests. No additional general brain principle or skill change is needed. This note retains task-specific evidence only.


## Integrated ordinary proof

Ordinary integration acceptance MET at exactaba7af4e05ded06eace8e38a139965ba2077d496:59files/735tests,735pass,zero fail/cancelled/skips/todo,216.683029s/exit0. Freeze09:35:13-09:38:50UTC ended only after fullEOF and cleanhead/729input/171output/receiptSHA98925fd6/actualNodeSHA6f320694/pinnedchildPATH/Python/offlineundici postflight. Exactcommand `/tmp/factory-cleanup-c2-composed-command.sh`, entrylist `/tmp/factory-cleanup-c2-ordinary-entries.txt`, profile `/private/tmp/factory-cleanup-c2-integration-profile/profile.json`, full log `/tmp/factory-cleanup-c2-integrated-ordinary-composed.log`, exactfacts `/tmp/factory-cleanup-c2-composed-postflight.json`. An earlier <1s exit127 orchestration launch never started tests because the wrapper pinned its own PATH before resolving RTK; separate `*-launch127.*` logs retained. Corrected wrapper resolves RTK in the original parent environment before the unchanged saved command applies pinned child env. No source/test change, skip or bound/guard weakening. Linux/Darwin public43 each remain pending; Windows C2 unsupported/C1open.
