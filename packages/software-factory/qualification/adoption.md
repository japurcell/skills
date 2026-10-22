# T14 adoption and revert evidence qualification

Status: the local bounded evidence API and fixture-only proof were exercised on 2026-10-22. This is not a learning promotion service, an approval authority, or an installer. No user prompt, skill, profile, installation, or live provider was changed.

## Ordinary operation protocol

`src/learning.ts` exports `prepareAdoption`, `confirmAdoption`, `prepareRevert`, and `confirmRevert` for an explicitly authored operation. The caller supplies a separate human approval reference. The factory does not authenticate the person behind that reference. Authorization to run the ordinary authoring or version-control action remains with the caller.

From a source checkout, an operator can use the exact pinned Node executable below and an absolute built-module import. `@local/software-factory` is a type-only alias inside authored `.factory/workflows/*.ts`; it does not expose runtime learning functions. T15 owns the manifest-bound absolute path to this same built module in an installed package. The following sequence is runnable after package build, with `approval.json` naming a disposable repository and the exact references described below:

```bash
cd /absolute/source/packages/software-factory
/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/factory-qualified-node-i2fv29e3/node-v24.22.1-darwin-arm64/bin/node --input-type=module -e '
import { readFileSync, writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
const packageRoot = process.cwd();
const { openRepositoryStore } = await import(pathToFileURL(`${packageRoot}/dist/store.js`).href);
const { sourceHistoryGateway, prepareAdoption } = await import(pathToFileURL(`${packageRoot}/dist/learning.js`).href);
const approval = JSON.parse(readFileSync("/absolute/disposable/approval.json", "utf8"));
const store = openRepositoryStore("/absolute/disposable/repository/.git");
try {
  const prepared = await prepareAdoption(sourceHistoryGateway(store, action => action()), approval);
  writeFileSync("/absolute/disposable/prepared.json", JSON.stringify(prepared));
} finally { store.close(); }
'
```

Only after that preparation is reviewed and the named action is explicitly authorized does the operator perform an ordinary one-file authoring and Git commit in the exact approved repository. The action is external to this API. Record its own result and reference, then run `confirmAdoption` using the saved `prepared.json` and the same absolute `dist/learning.js` import. Save its returned JSON whether it says `applied`, `not_applied`, or `uncertain`. `prepareRevert` and `confirmRevert` follow the same separate approval, external Git action, observation pattern. In the public fixture, each preparation and confirmation JSON is saved as a separate existing-store report capture in a finalized operation invocation. A production operator must preserve those reports and their capture references with the source history; the example file alone is a local review artifact.

An adoption approval identifies one extraction invocation and proposal key, one evaluation invocation plus exact report capture and SHA-256, one candidate invocation plus exact capture and SHA-256, and one repository root, repository-scoped relative path, expected Git commit and expected file SHA-256. `prepareAdoption` reads complete retained report and candidate captures through the bounded read-only `SourceHistoryGateway`. It requires a successfully finalized evaluation with a supported assessment and no limitations. The evaluation report must bind the selected extraction, candidate and target; its resolved baseline digest must equal the approved expected target content, and its resolved candidate digest must match the approved capture bytes. It observes the current Git commit and committed target bytes before returning a preparation. Missing or changed references, a changed candidate, changed target content or revision, an unsupported/inconclusive evaluation, shared scope, symlinks and uncommitted target edits stop preparation. The preparation retains the evaluation's extraction report and normalized result references; the source and evaluation records remain in history.

After preparation, the explicitly authorized operator uses an ordinary authoring/version-control path to change and commit the selected file. The operator records an independent action reference and one of `succeeded`, `failed`, or `uncertain`. `confirmAdoption` observes the target again. It records `applied` only when the action reports success and the new commit is a direct, single-parent child of the approved expected commit, the only changed path is the approved path, and both committed and working file bytes hash to the approved candidate. An unchanged target is `not_applied`; an observation failure, wrong bytes, extra path, merge commit, intervening commit, or mismatch is `uncertain`. Failed or uncertain actions cannot yield `applied`, even if matching bytes appear. The action result and observed applied revision are separate fields.

An explicit revert begins from a recorded `applied` adoption and a new human approval reference. `prepareRevert` checks the current target against the actual applied commit and candidate hash. After an ordinary version-control revert, `confirmRevert` requires a separately recorded successful action and a direct, single-parent commit changing only the same target back to its approved pre-adoption hash. `reverted` contains the actual observed reverting revision and the complete original adoption reference. Failure and uncertainty cannot claim a revert. A changed post-adoption target requires renewed review.

These observations bind to the local Git worktree and selected path. They do not make external Git actions atomic: a concurrent writer can race a prepare or observation. The ordinary action should recheck the expected commit immediately before authoring and stop on a mismatch. If a race, crash, or other uncertainty occurs, preserve the records and inspect the repository before any new explicit attempt. There is no automatic retry, replay, promotion, or rollback daemon.

## Fixture evidence

The public `test:learning -- --operation adopt` selector is registered by the integration owner. The focused source command is `node --test test/learning-adoption.test.mjs` from `packages/software-factory` after `npm run build`, with pinned Node v24.22.1 on `PATH`. The test uses disposable Git repositories only. It covers approval without application, changed candidate and scope, absent authorization, changed expected content and revision, failed/uncertain action, wrong and broader commits, an intervening target commit, actual application, and actual revert. One composed case runs the real `learn.ts` extraction and `evaluate.ts` comparison over retained captures, saves an inconclusive evaluation, reruns a supported comparison, then applies and reverts only the fixture target. It verifies original extraction and inconclusive evaluation remain readable and that the adoption and revert records retain the source/evaluation lineage. Fake provider reviews establish protocol behavior, not live model quality. `evaluate.ts` support describes only its supplied bounded cases and criteria.

Observed on the isolated `codex/factory-learning-adoption` branch from base `3ad871d5`, using pinned Node v24.22.1 on macOS arm64: final `npm run typecheck` and `npm run build` exited 0. After the baseline-to-target binding repair, `node --test test/learning-adoption.test.mjs test/learning-evaluation.test.mjs test/workflows.test.mjs test/store.test.mjs test/capture.test.mjs test/validated-results.test.mjs` passed all 91 cases in 86.408 seconds, including seven focused adoption cases. The existing public `npm run test:learning` selector passed all 33 registered extraction/evaluation cases (20 evaluation plus 13 extraction). Parent integration must register the new adoption file under `test:learning -- --operation adopt`, run that public selector and the composed source suite before milestone acceptance. No paid provider, desktop test, global install, remote push, or real repository adoption is part of this qualification.
