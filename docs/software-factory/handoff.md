# Software factory handoff

Updated: 2026-10-21. Scope: software-factory.

## Current goal and authorization

Implement the accepted foreground software factory through [ExecPlan.md](ExecPlan.md). The 2026-10-21 execplan-implement invocation authorizes implementation, commits, disposable development verification and plan-defined harmless provider qualification when credentials/native prerequisites exist. The latest user instruction requests Linux/Windows/macOS Actions, defers live desktop notification tests until the final plan stage, and directs implementation to continue. The user then explicitly approved pushing this branch and running qualification. Base `6f94f4b5` was pushed; no release publication, real repository installation or real learning adoption occurred. Destructive qualification requires disposable machines.

## Current state and next action

Base branch is `codex/research-agentic-workflow-prototypes`. T1, local macOS T2, T3 and T4 are verified. Milestone 2 acceptance is met locally. Reviewed CI commits `3c86993d` and `764f559b` are fast-forwarded onto base. Shared placement is now wired into the store and test registry. Pinned Node 24.22.1 typecheck/build, 29 store/capture/placement/composed tests, six fixtures and four runtime/CI contract tests pass on this integrated tree. CI definitions pass actionlint. Hosted run `39718601088` passed Linux x64 and macOS arm64 foundation checks; Windows direct storage passed but Git fixture configuration and qualifier contention failed. No complete Windows or release support claim exists.

T5 is under independent review in clean private branch `codex/factory-invoke`, worktree `/Users/adam/.codex/worktrees/factory-invoke/skills`. Initial commit `6f037f0` passed 45 checks, but review reproduced premature success for unawaited context `needsInput`, `progress`, `agent` and whole `scope` callbacks. Review also reproduced wrong-repository selection for trailing-space Git paths and OOM from unbounded history materialization. The implementer owns all three repairs and public CLI E2E tests there. Do not integrate until every asynchronous context API participates in invocation lifetime and terminal failures/questions are retained. Parent owns CLI smoke, lifecycle registry, canonical documents and integration. Native CI repair runs separately in `/Users/adam/.codex/worktrees/factory-native-repair/skills`, branch `codex/factory-native-repair`, owning only the Git fixture, SQLite qualifier worker/regression and CI evidence. Review, integrate and push those repairs for a new native run. After repaired T5 review, rebase onto current base, verify, fast-forward, register startup tests and run composed checks. Then execute T6 bounded shutdown/manual clearance.

## Files and verification

Runtime source is `packages/software-factory/src/`; explicit dispatch is `packages/software-factory/scripts/test.mjs`. CI is `.github/workflows/software-factory-qualification.yml`. `qualification/ci.md`, `runtime.md`, `capture.md` and the pending T5 `invocation.md` retain mechanisms, evidence and limits. The workflow uses reviewed official action SHAs, exact archive integrity, read-only credentials, three matching native architectures, bounded foundation checks and retained failure artifacts. Windows byte-range WAL write denial preserves the original POSIX file-size failure test and its public recorder assertions; native Windows behavior remains pending.

From repository root, put the qualified Node directory first on PATH and run `rtk proxy python3 scripts/test-software-factory.py --suite store`, `rtk proxy npm --prefix packages/software-factory run test:fixtures`, and `rtk proxy npm --prefix packages/software-factory run test:qualification`. Current pinned binary: `/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/factory-qualified-node-i2fv29e3/node-v24.22.1-darwin-arm64/bin/node`. This temporary runtime was downloaded from the official exact release and SHA-verified; startup never downloads. `test:all` still fails at unfinished lifecycle registration. Do not report aggregate acceptance.

## Constraints and recovery

Current scripts run from entry with one isolated claimed worktree and one build. No replay, automatic infrastructure retry, profile fallback, task scheduler, live human bridge, PR publication or automatic learning adoption. Claims never expire. Unknown descendants retain ownership/capacity; PID alone cannot justify clearance or a kill. Windows normal command cleanup stays conservative until T6/native qualification. Native process inspection must respect the accepted manual fallback, without adding a universal process scanner or Job Object subsystem.

Integrate only clean stopped private branches by rebase and fast-forward, then run composed proof on base. Archive only clean integrated managed worktrees and delete their integrated local branches. Capture worktree was archived and its integrated branch deleted. CI worktree was archived and its integrated branch deleted; preserve the active invocation repair worktree. Use `login:false` and explicit workdir in shell calls. Prefix commands with `rtk`; narrow Git metadata/worktree escalations may be required.

Desktop visible delivery is T17-desktop, after T12 deterministic implementation/helper packaging and other acceptance. Provider credentials/desktop access and passing Windows rerun remain evidence gates. The user disabled a previously blocking secret-scan hook; [incident report](hook-scan-limit-incident.md) retains the issue. No repair/re-enablement or clean security scan is claimed.

## Historical references

[Historical handoff checkpoint](handoff.history-2026-10-21.md) preserves prior authoring/prototype evidence and old preview details. [Research plan snapshot](ExecPlan.history-2026-10-20.md) preserves superseded prototype planning. Historical recommendations do not override the active plan. Accepted design and UI remain in [map.md](map.md), [lifecycle specification](lifecycle-specification.md) and [UI contract](observability-ui-specification.md).
