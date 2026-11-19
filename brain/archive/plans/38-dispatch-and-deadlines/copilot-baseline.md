# B1. Capture the Copilot baseline

Owner: Copilot operator. Prerequisites: reviewed architecture in the entry's Decision Log and baseline skill bytes at 7fc651a7. First inspect `copilot --version` and the supplied host model restrictions. The earlier disposable COPILOT_HOME hid provider login and failed the OAuth loopback. Reuse the existing provider-managed login with a disposable project. Never inspect or copy credentials. Request sandbox approval for ordinary native execution where required.

Use the old published caller and router from Git and a benign local fixture. For each caller launch one quick worker and one silent worker with a bounded deadline. Retain timestamps, actual router calls, worker IDs, schedule/notification events, parent actions and exit status. Verify that early completion clears its deadline, quiet time has no status-only wakeup, and silence triggers enforcement. Distinguish baseline failure, passing trace and unavailable host. Capture the actual worker-scoped availability surface if accessible. A session picker or examples alone cannot establish an enforced worker restriction. Pin the parent settings, project and prompts for later matching. Record native command, source IDs and artifact path. Stop at baseline evidence or evidenced host blocker; candidate dispatches belong to P1.

## Native setup and controls

Copilot CLI 1.0.114 used the existing authenticated provider session. The interactive `/subagents` picker showed a preference. The separate custom worker definition supports a required model. For the matched gate trial, retain the worker frontmatter, the restriction visible to the parent before dispatch and the actual host events. [GitHub CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#custom-agent-frontmatter-fields)

The first `--fleet` pilot created eight workers. The ordinary interactive pilot intentionally requested only one. Its native session `198893da-78eb-49a0-a097-52f2bfb14483` started `baseline-quick` at 03:31:46.689Z on November 19 and completed at 03:31:48.708Z. Worker `999ee39b-89db-4737-8035-de05c9837ad7` returned 73. The task explicitly selected `gpt-6-luna` and omitted effort. The configured effort reported by the host was medium. These observations verify the one-worker control only. A second task sheet mistakenly named the delegate caller in the ExecPlan project and was discarded before running the paired case.

The next two ordinary prompt-mode sessions used separate clean checkouts, the correct pinned caller, one quick and one silent assignment, and the project trust flag. Both exited 0 after the CLI denied the pinned router's Python command without an interactive approval. Count both as setup failures. The rerun supplies narrow, per-process permissions for `route38` and `scheduler38`, executables that invoke the same frozen Python scripts. No user settings are needed. Local evidence for these attempts and their exact argument lists is under `/private/tmp/todo38-1795057091956/copilot/{b1,combined-baseline,combined-tools}`. The output is private. Inspect public tool names, model controls, IDs, timestamps and outcomes only.

## Baseline verdict

Both `combined-tools` sessions exited 0. Native events show both parents launched the requested two workers. Neither met the full timing contract.

| Old caller | Quick worker | Silent worker | First observed miss |
| --- | --- | --- | --- |
| Delegate | `5fefefbe` completed 03:43:21.359Z | `abc913ed` started 03:42:52.032Z | Parent retried a bad registration with synthetic `--now 1800000000`. At 03:43:38.740Z it also queried the silent worker before the 55-second real deadline. |
| ExecPlan | `a7a7861b` completed 03:43:01.024Z | `d44f6126` started 03:42:48.250Z | Parent armed separate 55- and 45-second sleeps. It cancelled the quick alarm, then sent the silent worker a checkpoint request at 03:43:51.869Z, 8.6 seconds after the assigned deadline. |

The helper rejected the delegate parent's expired registration. Its test-clock option then allowed the parent to enforce a different timeline. ExecPlan used parent-owned timers and did act on silence. The historical five-minute prompts came from Copilot's recurring host schedule. These controlled misses and that historical schedule have different mechanisms.

The eight ordinary two-worker sessions in `combined-tools`, `n1-clock-old`, `n1-clock-new` and `delivery-control` took 206 to 366 seconds each. Their individual durations sum to about 34 provider-session minutes. Pairs ran concurrently. These times exclude setup, the original fleet pilot and the separate gate comparison. See the [native lifecycle replay](../../../../scripts/tests/orchestration/native-lifecycle.md) for the disposable project and commands.

## Worker restriction control for P1

In `worker-control`, the required profile declared only `claude-haiku-5.5`. Copilot accepted the explicit `gpt-6-luna` override and ran worker `6d1cb489` on it. Treat the profile alone as insufficient evidence of exclusion in this version. In `hook-control` a disposable repository `preToolUse` policy denied the same native `task` call before launch. The matching call started and completed `claude-haiku-5.5` worker `6ac48eeb`. P1 can use that verified worker-specific restriction for every pair, with identical policy bytes in old and new. This reproduces the known-exclusion decision under native enforcement. The source of the remote account's original selection error remains unknown. [GitHub hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference)

The first control used the camelCase frontmatter field `modelPolicy: required`. In `profile-spelling`, the same synthetic prompt and profile used `model-policy: required`. The outside-model task argument still appeared in the native call, but the worker started and completed on the authored Haiku model. The matching positive control also ran on Haiku. Thus neither a returned child ID nor a permitted final model proves the parent avoided the excluded request. Keep P1's calibrated hook constant. [GitHub's custom CLI agent example](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli)
