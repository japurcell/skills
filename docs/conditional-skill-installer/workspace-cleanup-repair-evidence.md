# Workspace cleanup boundary repair evidence

WS1R was implemented on 2026-10-15 in `/private/tmp/skills-workspace-boundary-m8`, branch `codex/workspace-boundary-m8`, starting at rebased WS1 commit `eee6854af46d381deb59e588b748606c82c6b389`. Its scope is the cleanup CLI, its existing public-process suite, and this evidence. The coordinator owns plan reconciliation, final knowledge admission, integration, and composed Milestone 8 acceptance.

## Reproduced deletion before repair

The public CLI seam is `CLEANUP_SKILLS_ROOT=<disposable-root> bash scripts/cleanup-skill-workspaces.sh`. The independent reproducer created these directories, with two immediate iteration directories in each nested workspace:

```text
skills/direct-workspace/snapshot-workspace/iteration-{1,2}/
skills/owner/SKILL.md
skills/owner/nested-workspace/iteration-{1,2}/
```

The saved disposable reproducer `/private/tmp/ws1r-reproduce.sh` accepts a cleanup CLI path, invokes that public process, checks both original iteration directories independently, prints the CLI report, and returns failure when either pair changes. The exact command was:

```sh
rtk proxy bash /private/tmp/ws1r-reproduce.sh /private/tmp/skills-workspace-boundary-m8/scripts/cleanup-skill-workspaces.sh
```

Before implementation, it exited 1 and retained fixture `/private/tmp/ws1r-boundary.nEcIAO`:

```text
FAIL: deleted direct-workspace/snapshot-workspace iterations
FAIL: deleted owner/nested-workspace iterations
Evidence: /private/tmp/ws1r-boundary.nEcIAO
workspace=direct-workspace kept=none deleted=nothing-to-prune
workspace=snapshot-workspace kept=iteration-2 deleted=iteration-1
workspace=nested-workspace kept=iteration-2 deleted=iteration-1
```

This reproduced both reported destructive cases on the rebased WS1 input. A maximum depth of two alone entered a direct workspace payload and a direct flat-root skill bundle.

## Public-process red and green cycles

Every suite run used `rtk proxy bash scripts/test-cleanup-skill-workspaces.sh` from the worktree root. Tests invoke the actual CLI with an explicit disposable root or copy the actual CLI into a disposable repository and unset the override; none source private cleanup functions.

1. Added `test_stops_at_direct_workspace_payloads` before changing implementation. It checks that the outer workspace's immediate old iteration is deleted, its new iteration remains, and both nested snapshot-workspace iterations remain. The full suite exited 1 with `Expected the nested workspace payload's first iteration to remain.` Added `-prune` after emitting a workspace. The full suite then exited 0.
2. Added `test_stops_at_direct_skill_bundles`. It checks both iterations nested under a flat `owner/SKILL.md` bundle and both immediate iterations of a real `owner-workspace/SKILL.md` bundle. The full suite exited 1 with `Expected the real skill bundle's nested first iteration to remain.` Added a real skill boundary before workspace selection. The full suite then exited 0.

After both changes, the same independent reproducer command exited 0 and retained fresh fixture `/private/tmp/ws1r-boundary.OEtWaY`:

```text
PASS: preserved direct-workspace/snapshot-workspace iterations
PASS: preserved owner/nested-workspace iterations
Evidence: /private/tmp/ws1r-boundary.OEtWaY
workspace=direct-workspace kept=none deleted=nothing-to-prune
```

The maintained suite contains the lasting reproductions; the temporary fixture paths are supplementary local evidence.

## Safety algorithm and final checks

`scan_workspace_root` retains physical no-follow `find -P`, the existing finite depth, null-separated paths, and deterministic sorting. It prunes archives first, then directories with a regular `SKILL.md` marker, before matching workspace names. A selected workspace is printed and pruned, so only `prune_workspace_iterations` enters that workspace. That function still considers only immediate real `iteration-*` directories, retains the newest directory using the existing creation-time/modification-time ordering, and leaves snapshots alone. Real skill detection takes priority even when a skill's directory name ends in `-workspace`.

No root-selection behavior changed: an explicitly configured root is exclusive, an explicitly empty root fails, and default invocation scans published direct/category siblings plus repo-local direct siblings. The test cleanup now uses the existing named `cleanup_test_workdir` trap with the exact temporary path; recursive iteration removal also uses `--`.

The final full suite includes eight cases. Existing positive/negative assertions remain, and the copied default-root fixture now also checks Forest Service category pruning and a linked iteration directory. The suite covers newest-iteration selection, single iterations, non-workspaces, snapshots, literal space/bracket names, default and Forest Service categories, repo-local siblings, maximum depth, archives at both scanned levels, linked workspaces/categories/iterations, explicit-root isolation, and empty-root failure.

Observed final commands and outcomes:

```text
rtk proxy bash scripts/test-cleanup-skill-workspaces.sh
test-cleanup-skill-workspaces.sh: all tests passed.
exit 0

rtk proxy bash -n scripts/cleanup-skill-workspaces.sh scripts/test-cleanup-skill-workspaces.sh
exit 0

rtk proxy git diff --exit-code HEAD -- skills .agents/skills
exit 0

rtk git diff --check
exit 0
```

All ten moved workspace trees, other skill payloads, the ExecPlan, existing move evidence, canonical guidance, and other implementation files are unchanged by this repair. Only disposable fixtures were cleaned. No real benchmark cleanup, real-home installation, human-only import script, live evaluation, push, or CI run was performed. These results establish local cleanup behavior on this host; composed layout/installer/grader verification and Milestone 8 acceptance remain the coordinator's work. No new native Windows proof is claimed.
