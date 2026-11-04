# C2 Actions event-creation diagnosis

2026-11-04 09:47UTC. Bounded read-only diagnosis after the single authorized push. No dispatch, retry, source/workflow edit, authentication inspection/change, token/config output or permission mutation occurred. C3a owns the exclusive private local proof window; main performed no build/test/lifecycle load.

## Actual facts

- Local origin URL was parsed without printing credentials: github.com/japurcell/skills. GitHub repository API agrees: full_name japurcell/skills, ID1186424623, default branch main, public, archived=false, disabled=false.
- Branch codex/research-agentic-workflow-prototypes is remote-verified at927f78bf62fa5e3ce3f7f35f39046c6bf3d65504. Successful push range0b2bd128..927f78bf contains9commits/19changed files.
- Repository Actions policy: enabled=true, allowed_actions=all, sha_pinning_required=false. Existing native foundation392445278, Darwin timing406491211 and IR1 inspection406605629 workflows are active; Windows owned-image406355584 is active but its paths do not match this push.
- Exact new C2 workflow exists in the remote pushed tree: .github/workflows/software-factory-cleanup-backups.yml, blob9fa3ef359c644f60e6d43728110727842abdbe6e,3580bytes. Its Actions workflow lookup returns404 and it is absent from the registered workflow list. That registration fact does not explain why all existing matching workflows also have no runs.
- Existing foundation push is branch-unfiltered and matches changed src/cleanup-backups.ts. C2 and IR1 have the exact pushed branch and match the same source path. Darwin timing has the exact branch and matches changed scripts/test.mjs. Windows owned-image matches no changed path. All relevant YAML passed actionlint. No recognized [skip ci], [ci skip], [no ci], [skip actions], [actions skip] or skip-checks:true instruction occurs in the9pushed commit messages.
- Exact-head Actions run count and check-suite count are0; no native run IDs, jobs, results or acceptance exist. Latest returned global run remains41804985008 at prior0b2bd128. No push/run duplicate was created.
- Repository events50 returns no PushEvent for927f78bf. Visible events for this branch end at04:33:46/b3d7cc77, despite later already-observed Actions heads0b2bd128 and5d843426. The feed therefore cannot establish delivery failure or ordering for this push.

## Primary contracts and limits

[GitHub push contract](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#push) permits push workflows before default-branch merge and requires both branch and path filters when both are supplied. A single branch was pushed; the documented many-branches/tags event omission is not this shape.

[GitHub trigger contract](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow) documents suppression of new runs for most events originating through GITHUB_TOKEN. The actual push authentication origin was not inspected, so this is a documented possibility only, not the observed cause and not authority to change credentials.

[GitHub skip contract](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs) specifies commit instructions; none is present in the inspected push range. [Repository events contract](https://docs.github.com/en/rest/activity/events#list-repository-events) explicitly permits30seconds-6hours latency and does not support real-time diagnosis. Missing PushEvent is not a delivery receipt.

[Manual dispatch contract](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch) has its own default-branch/previous-run prerequisites. The new C2 workflow has no observed registration/run, so no dispatch route was assumed or tested.

## Outcome

Cause UNKNOWN. Repository/head, enablement, existing workflow state, changed-path matches and absence of skip instructions are verified. Public APIs expose neither an exact push delivery receipt nor a server rejection explaining the missing runs. New-workflow404, delayed events and the generic token rule are insufficient to select a correction. C2 ordinary735 is accepted; Linux/Darwin public43 remains pending without native evidence. Preserve current immutable head; root must choose a concrete next route before any dispatch/retry/source or authentication change.


## Root-selected finite execution route

- Identity-only API user is japurcell/id10947458/typeUser. Known gh executable /Users/adam/homebrew/bin/gh; its help confirms the credential helper protocol. No token/config values were inspected or printed.
- Root authorized one initial-event push using temporary command configuration to reset helpers and explicitly select gh auth git-credential for github.com. [Git credential helper reset](https://git-scm.com/docs/gitcredentials) and [Git command configuration](https://git-scm.com/docs/git) define this scoped override; the official [gh authenticated Git implementation](https://github.com/cli/cli/blob/trunk/git/client.go) uses the same empty-scoped-helper then explicit gh helper pattern. No gh auth setup-git/login/switch or permanent configuration change is made.
- Fixed qualification/cleanup-native-execution.json records initial POSIX C2 public43 and source-context foundation/Windows diagnostic4. Exact C2 workflow path and existing packages/** foundation witness select the next push. Existing real triggers remain; no timing/IR1/creator path matches this control-only diff.
- Existing CI case goes RED for missing record then full19/19 GREEN, zero skips1.902677s; actionlint/diff pass. Runtime snapshot729inputs/all171output hashes and receiptSHA98925fd6 remain unchanged; ordinary735 is the earlier actual proof ataba7af4e, not a new trigger-head suite.
- Check old927 jobs immediately before the one no-force push; reconcile any duplicate before execution. If event creation is still absent, stop with finite facts; no blind push/dispatch/auth changes. A successful later route would not establish the historical transport cause.


## Initial native event creation

The single root-authorized explicit-user-helper control push is clean/pushed2762f02960301faa29e2dbef0eea5df918cae66b. It creates exactly C2 POSIX authority41811099917 (Linux126510253073, Darwin126510253308) and native foundation41811099798 (Linux126510252620, Darwin126510252833, Windows126510257172), all initially in progress. Old927 remains0runs, no duplicates. No timing/IR1/creator run is selected. C2 public43 per target is underway; native acceptance pending. Source735 remains actual ataba7af4e, runtime729/171/all output hashes/receipt unchanged; control-only CI19 passes separately. A successful known helper route does not establish the historical missing-event cause. No retry/dispatch/permanent auth change or credential logging.

Reflection: the finite trigger record and existing CI path-witness assertions structurally preserve intended job selection without a global retry framework. The source proof and trigger head are distinct, and a successful user-helper push is not historical transport diagnosis. Existing scoped notes/commands capture this wave; no generic skill change is needed.


## Final native compatibility outcome

Foundation41811099798 at2762f029 is completed overallFAIL because Windows remainsRED; Linux and Darwin jobs succeed independently. Linuxjob126510252620 completedSUCCESS10:15:33UTC:14/14foundation phases, publicupgrade1/1zero237.201766s, dependencyownership12/12zero79.669055s, claim23/23zero236.023957s, backup11/11zero297.059256s. Logs/archive/validated artifacts `/tmp/factory-cleanup-native-control-linux-41811099798-{job.log,evidence.zip,artifacts/}`. Darwin15/15 phases/FULL31/31zero54.361905s; Windows13phases10pass/3fail(fixtures,learning-fixture-diagnostic,cleanup-reads), directdiagnostic2/4. No retries, all original expectations/bounds survive. Prior927 finalruncheck remains0, no duplicate or timing/IR1/creator event.
