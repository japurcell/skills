# Notification selector timing repair

The public `notifications` selector in `test/dispatch.test.mjs` retains its 15-second process deadline. At base `dea5f4db7ff3cae6de0d0a096e744bf755b1c9bd`, hosted foundation run `39845101897` reached that deadline on Darwin and Windows. The retained log is `/tmp/factory-native-39845101897-failed.log`. Linux passed. This is the end-user CLI reproducer. A local pinned Node 24.22.1 run at the same base passed in 7.75 seconds, so local timing alone did not reproduce hosted contention.

`test/notification-repository-fixture.mjs` previously copied the entire 51 MB development `node_modules` tree into every disposable Git repository. Workflow compilation needs TypeScript, its platform compiler, `@types/node`, and `undici-types`; Playwright is unrelated to these fixtures. The fixture now copies only those four packages. `fs.cpSync` uses `COPYFILE_FICLONE`, which [Node 24 documents as attempting a copy-on-write clone with an ordinary copy fallback](https://nodejs.org/docs/latest-v24.x/api/fs.html#fscpsyncsrc-dest-options). It dereferences any source symlink so the disposable toolchain owns its files. No dependency symlink or hard link points into the worktree install.

The seven original record tests now run in three registered files instead of one serial worker. Their test bodies are byte-identical to the base version; the notification group still runs all 22 original tests with its existing four-worker limit. The 5-second native sender bound, 500 ms preflight bound, 450 ms helper bound, and 15-second public selector deadline are unchanged. New reminder tests and their registration are owned by another task and are not part of this branch.

## Private worktree evidence

Worktree: `/Users/adam/.codex/worktrees/factory-notification-native-selector/skills`, branch `codex/factory-notification-native-selector`, pinned Node `v24.22.1` on Darwin arm64. Dependencies were installed independently with offline `npm ci --ignore-scripts --offline --cache /tmp/software-factory-npm-cache`.

- Before the edit, `node --test --test-name-pattern='notification group runs sender and bounded preflight checks without a desktop' test/dispatch.test.mjs` passed in 7.75 seconds locally. The direct notification group passed 22/22 in 7.74 seconds.
- After the edit, the direct group passed 22/22 in 8.52 seconds. The unchanged public selector passed in 8.57 and 8.66 seconds. These are local passes under 15 seconds, with no claim of a local speedup.
- `npm run typecheck` and `npm run build` passed after the edit. The existing `missing shared dependencies refuse without installation or source changes` startup case passed.
- A source comparison found all seven original record test bodies byte-identical, with no missing or duplicate body. A disposable fixture's copied `typescript/package.json` was overwritten; the worktree source remained unchanged and the destination was not a symlink.

Hosted proof remains open. After integration with the reminder worker's registration, run the unchanged public selector under the foundation workflow on the exact pushed head for Linux, Darwin, and Windows. Retain each platform's status and duration. A local pass and a source-level scheduling change do not establish hosted acceptance.
