# Windows metadata-only collection workflow

This source-only Phase B task adds a separate fixed metadata collection workflow. Phase A's historical workflow, bootstrap MJS and checks remain unchanged. Root owns integration, CI registration, execution control and any actual registration push or Windows execution. Downloads, collector execution, discovered tools, SDK acquisition, build/native actions, providers and desktop actions remain unreleased. Formal and independent reviews are deferred.

## Purpose / Big Picture

After a separate root execution release, the fixed workflow can collect bounded installed-tool metadata on the independently selected GitHub-hosted windows-2025/WinPS/protected-namespace profile. The only artifacts are closed `metadata.json` and redacted `control.json`. An observed record carries no selection, build or native authority. A valid blocked record is retained for diagnosis while the collection step and job still fail.

## Progress

- [x] (2026-11-04) [milestone-1] T1: Observe meaningful RED for the fixed CLI/capture seam, then implement the fixed result helper.
- [x] (2026-11-04) [milestone-1] T1: Prove strict full-wire/exit coupling, process failure refusal and fresh two-file artifacts.
- [x] (2026-11-04) [milestone-2] T2: Add the fixed Node bootstrap and new workflow without changing Phase A sources.
- [x] (2026-11-04) [milestone-2] T2: Complete scheduled portable/static proof and normally merge current integration; exact tested source hashes are retained below.

## Context and Orientation

The existing `windows-storage-loader-metadata.mjs --metadata-only` controller exports `captureMetadataProcess` and `validateMetadataWire`. It alone starts the fixed System32 Windows PowerShell collector and never invokes discovered programs. Source10 is independently frozen at Git commit `222924947e2a9b4c24a1d7c3eddaa426b0d15403`. The selected controller JSON is canonical1540-byte UTF8 with LF and SHA256 `719d27ea0ed7cb4e554adf02e0384c8a67a50bae61c6cdb80f832f4991335650`.

Root selected the actual host observations from Phase A source `172b285e3d3ba07f3d2e6e42a9ef7fb791253c4a`, run41838587575/job126603881179/artifact13325489670, under already accepted external trusted-host prerequisites. Windows version means exactly `[Environment]::OSVersion.Version.ToString()` and equals `10.0.26100.0`. The selected System32 WinPS executable SHA is `41796f1f3d81f921fdb4030c865f9dcf5032a2a1b49dde148bbc99e8d10f6e8c`; observed WinPS is5.1.26100.33648/x64. Hashes, marker strings and these observations do not authenticate the external premises or any SDK/tool.

## Plan of Work

### Milestone 1: Retain only validated bounded metadata

Status: done
Acceptance: met

T1 has no implementation prerequisite. The no-argument result helper's sole execution route is exact `process.execPath` plus adjacent `windows-storage-loader-metadata.mjs --metadata-only`. It verifies pinned Node, the literal root selection digest and source10 before and after capture, copies selection into a fresh private input leaf outside candidate output, supplies only minimal trusted Windows runtime context plus the two existing selection environment variables, and reuses the existing bounded transport. An early finite CLI refusal is rejected without export; only a full `validateMetadataWire` record may be retained. Initial3 RED1pass/2fail86.930292ms reached EOF13:56:27UTC; minimal GREEN3/3 153.56425ms reached EOF13:57:27UTC. Coherent9 RED7pass/2fail988.481458ms reached EOF13:59:41UTC; GREEN9/9 971.000125ms reached EOF14:01:58UTC. Each was root-scheduled with immediate proof-slot release and zero skips/cancelled/todo.

### Milestone 2: Add a separately releasable fixed workflow

Status: done
Acceptance: met

T2 depends on T1's accepted protocol. The new workflow and fixed bootstrap PS1 are source-written. The bootstrap fetches the exact official Node24.22.1 archive with redirects refused,150000000-byte/120s bounds, verifies archive SHA `d2046d28c2c3dcd211ac5145c0bf30e2047ef9dfb306693c8c6e2eccd8b95fa5`, extracts only node.exe and verifies SHA `d702daa815eabbff763c7d3808e235cf031cf2ca70211b56847bc72f51e240e5` before Node invocation. The new branch/path push plus no-input dispatch workflow is job10min, each step at most5min. Root must separately release registration; dispatch requires default-branch registration and is not assumed available for a new file. The10-test workflow RED reached EOF14:04:31UTC with9pass/1fail973.226208ms; only the absent new YAML failed. Final portable/static proof passed as recorded below.

## Trust Boundaries and Abuse Cases

Downloaded bytes, child stdout/stderr, exit/EOF state and candidate metadata are untrusted. The independently selected source/OS/controller installations and protected namespaces are external prerequisites, not established by self-hash. Candidate output must not choose selection, paths, commands, mode, authority or artifact names. Refuse wrong selection/source context, forged authority, unknown fields, invalid canonical bytes, extra stderr, overflow, incomplete EOF, wrong exit/state coupling and pre-existing artifact destinations. Never export raw output or environment, credentials, repository walks or machine/user inventories. Selected installed-tool paths are allowed only within the existing closed builder metadata wire.

Both capture levels retain the existing294000ms deadline plus at most1000ms teardown,1MiB stdout and8192-byte stderr bounds. Actual exit and both actual EOF are required; stderr is always refusal. The original collector's256-file-fact and512MiB total observed-input ceilings remain unchanged. The copied root selection is outside the fixed upload leaf. No complete consumed dependency closure, all-descendant containment, hostile-administrator custody or tool eligibility follows from capture or artifact publication.

## Concrete Steps

Root's next action is to integrate the clean private branch, register any desired portable CI checks, and assess a concrete execution-control record before separately releasing ONE registration push. No actual workflow run is authorized by this source handback. To reproduce portable proof after coordinator scheduling, from `/private/tmp/windows-metadata-collect` run `rtk proxy /private/tmp/factory-qualified-node-342t16a/node-v24.22.1-darwin-arm64/bin/node --test packages/software-factory/qualification/windows-storage-loader-metadata-collect-checks.test.mjs`. Expect11/11, no skips/cancelled/todo. No further author proof is pending.

## Validation and Acceptance

Agreed public seams are the actual fixed CLI/non-Windows refusal, an already-created inert child's bounded output/exit/EOF observer, and fixed two-file artifact publication. Synthetic records test only parser/coupling controls and cannot authenticate Microsoft tooling. Secondary static checks cover fixed workflow routes, pins and artifact paths. After portable checks, scheduled PS `Parser.ParseFile` is AST-only and never executes or dot-sources bootstrap/collector source. The selected actionlint parses only the new YAML. Existing source10, original Phase A three blobs, ordinary848 and full31/13/36/windows12 contracts and bounds remain unchanged.

The11-test source-drift RED reached full EOF14:11:00UTC:10pass/1expected missing-export failure968.883166ms. The accepted fixed no-argument checker now validates its own module-relative exact source10 and is reused in production pre/post checks. A disposable explicit source copy first passes, then refuses after one copied source changes. Production separately verifies the exact pinned Windows Node executable; portable source checks do not pretend the local Node has that Windows image identity.

Final portable GREEN11/11 reached full EOF14:12:26UTC,966.605375ms, zero failures/cancelled/skipped/todo. It ran at normal integration merge `9dee0773704ec4f92220c3e2f8326a4b0aa84b14`, parents source commit `ebb66cadab2df04d9b6ae5e15a51d644f80a0960` and local integration `c4c7ad4da45aa9d9db0a1431b807a560c2addcec`; no rebase. All19 owned/root-selection/source10/PhaseA file hashes matched before/after both final RED and GREEN. Logs/manifests: `/private/tmp/windows-metadata-collect-red11-{before,result,after}.log` and `/private/tmp/windows-metadata-collect-green11-{before,result,after}.log`.

Final static proof reached full EOF14:15:03UTC in1.553s: selected Node syntax2; selected PS AST-only bootstrap1 plus workflow2 blocks; selected actionlint1; source10 equal known Git2229249; historical PhaseA3 equal known Git172b285; owned5 diff check. All19 before/after hashes matched. Logs/manifests are `/private/tmp/windows-metadata-collect-static-{before,result,after}.log`; the parser-only driver is `/private/tmp/windows-metadata-collect-ast.ps1`. No bootstrap or collector source was executed. Only this evidence note changed after proof.

| Tested executable source | SHA256 |
| --- | --- |
| New workflow | `6ff77a15af255fb8deb8f3dbe4f1f66c51821583d41990c52df98a20067e0025` |
| Fixed Node bootstrap PS1 | `bb1d8f6de3bbe7398dc6ce9e82feaf041088566ee36b70ebca2f7fc5be8f6d0b` |
| Fixed result MJS | `b10e76d2908c389488bbe6f174a9c24aaa0df87a9af409769647581694d369eb` |
| Standalone checks | `c0bf6dfb6db588368c81a8a548c5c0c1535328df2ffe5d6154271b10da41b45f` |

## Idempotence and Recovery

Every runtime/input/artifact leaf must be fresh. Refuse an existing destination rather than overwrite or broaden cleanup. No source task retry, remote workflow run or automatic reselection is authorized. Root alone assesses actual facts and decides subsequent builder/tool selection or a separately scoped build-only task.

## Surprises & Discoveries

- The original controller emits a separate finite early-refusal schema when a safe full metadata record cannot be serialized. The wrapper must refuse that record without exporting it.

## Decision Log

-2026-11-04: Root accepted a fixed no-argument wrapper, existing transport/validator reuse, strict observed0/blocked1 coupling, and full-record-only artifact publication. No arbitrary executable, argument list or user-selected mode is introduced.
-2026-11-04: Nested transport deadlines stay294s plus at most1s teardown. A parent capture timeout refuses rather than accepting late success; no all-descendant containment or consumed closure claim follows.

## Outcomes & Retrospective

All5 owned source files are complete, normally integrated locally and author-proven. This source handback establishes bounded portable/static behavior only. Actual downloads, Windows collector behavior, Microsoft signatures/catalog associations, protected namespaces, installed-tool/SDK availability, tool/build/native/private-storage/Windows C1/helper/provider/desktop admission remain unproven and unreleased. Root alone independently assesses actual metadata before any builder/tool tuple selection or new build-only task. Formal and independent reviews remain deferred; there are no formal review claims.

Reflection reviewed the brain index and accepted builder contract. The authority limits are already durable there; exact root/source selection, full-wire/exit coupling, no-export refusals and copied-source drift are enforced structurally in this implementation and checks. No separate brain/skill/todo edit is needed. No skill improvements identified. Root owns canonical handoff/plan and registry/CI integration.

## Sources

Platform choices reuse the accepted Phase A primary-source evidence: [GitHub dispatch registration](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow), [workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), [hosted runner labels and privileges](https://docs.github.com/en/actions/reference/runners/github-hosted-runners), and [official Node24.22.1 checksum manifest](https://nodejs.org/download/release/v24.22.1/SHASUMS256.txt). No new network/source acquisition is performed in this source task.
