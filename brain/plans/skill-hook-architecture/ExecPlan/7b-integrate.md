# T7b, integration

The coordinator inspects the candidate, brings over product and test changes including both copies of the extractor, and reconciles the candidate plan's results with this plan. Then run the two commands below, followed by the combined M2/M7 bundle tests once both candidates land. Run the relocated synthetic caller and compare actual recorded worker inputs with the exact `manifests` array, in order. The Windows runner executes the four existing workspace ACL cases on that integrated revision with `rtk proxy python3 -m unittest discover -s skills/default/brain-install/tests -p test_skill_workflows.py -k windows`. Expect all four to run and pass. Exercise the project-mode workflow there as part of the full bundle suite. Stop after recording both the integrated caller result and native permissions evidence.

The integration coordinator owns applying the tested product changes from 149a2661 while preserving this plan. Run relocated synthetic caller checks, bundle suite and source validation. Record branch-local vs integrated proof. Rerun combined bundle tests after T2b integration and obtain the Windows results specified in the milestone.

Use the [milestone contract and verification commands](7-conversation-batches.md) and the [integration plan](../ExecPlan.md). Record results and remaining evidence here.

## Integration evidence

On 2026-11-19, applied the product and test diff from candidate `149a266172310a0bc9c4595973f6bb0f22596171` to integration base `1eaf63dc`, retaining the rewritten plan. On macOS arm64, Python 3.14.6:

- `rtk proxy python3 -m unittest discover -s skills/default/brain-install/tests` exited 0: 55 tests, four Windows cases skipped.
- `rtk proxy python3 -m unittest discover -s skills/default/brain-install/tests -p test_skill_workflows.py -k relocated_documented_invocation` exited 0: one test. It compares recorded worker inputs in order to the emitted `manifests`, verifies their files exist, and checks empty and failed runs with a stale manifest.
- `rtk proxy python3 scripts/validate-skill-sources.py skills`, both portable/local `cmp` checks, and `rtk proxy git diff --check` exited 0.
- `which prlctl VBoxManage multipass virsh pwsh` found only PowerShell; `which qemu-system-aarch64 qemu-system-x86_64 tart utmctl limactl` found none, and the Applications listing showed no VM application. No authorized native Windows runner was identified locally. PowerShell on macOS does not establish Windows ACL behavior.

At that checkpoint, combined M2/M7 bundle verification and the four native Windows ACL cases plus project-mode workflow remained open. The candidate's earlier macOS proof is distinct from the integrated-tree run. Reflection found no new durable lesson beyond the existing plan and platform boundaries; no brain, skill, structural, or todo updates are needed.

On 2026-11-19, the combined tree based on `ffe630df` with M2 `658ab7e8` merged passed `rtk proxy python3 -m unittest discover -s skills/default/brain-install/tests` (58 tests, four Windows skips, exit 0). The merge also exposed three generator-suite assertions expecting 14 outputs after M2 added the fifteenth. Correcting the expected count made all 12 generator tests pass. The [native qualification](7c-native-bundle.md) subsequently covered Windows ACLs and the relocated workflow.
