# T14 adoption and revert evidence qualification

Status: the local bounded evidence API and fixture-only proof were exercised on 2026-10-22. This is not a learning promotion service, an approval authority, or an installer. No user prompt, skill, profile, installation, or live provider was changed.

## Ordinary operation protocol

`src/learning.ts` exports `prepareAdoption`, `confirmAdoption`, `prepareRevert`, and `confirmRevert` for an explicitly authored operation. The caller supplies a separate human approval reference. The factory does not authenticate the person behind that reference. Authorization to run the ordinary authoring or version-control action remains with the caller.

From a source checkout, use pinned Node v24.22.1 and an absolute built-module import. `@local/software-factory` is a type-only alias inside authored `.factory/workflows/*.ts`; it does not expose runtime learning functions. T15 owns the manifest-bound absolute installed path. Build the package first. The following public API sequence uses the existing report-capture mechanism in an initialized disposable repository. The operator supplies the absolute package root, repository, and registered worktree ID. The existing authoring owner is responsible for retaining the exact reviewed preparation before the external action. It must preserve the returned capture ID and digest as the approved reference.

```js
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
const packageRoot = '/absolute/source/packages/software-factory';
const repository = '/absolute/disposable/repository';
const worktreeId = 'existing-registered-worktree-id';
const { openRepositoryStore } = await import(pathToFileURL(`${packageRoot}/dist/store.js`).href);
const { sourceHistoryGateway, prepareAdoption, confirmAdoption, prepareRevert, confirmRevert } =
  await import(pathToFileURL(`${packageRoot}/dist/learning.js`).href);
const store = openRepositoryStore(`${repository}/.git`);
const history = sourceHistoryGateway(store, action => action());
const sha = text => createHash('sha256').update(text).digest('hex');
const read = path => JSON.parse(readFileSync(path, 'utf8'));
const save = (path, value) => writeFileSync(path, JSON.stringify(value));

// The existing authoring/report owner executes this, outside the read-only gateway.
async function retainReport(value) {
  const text = JSON.stringify(value);
  const run = await store.createRun();
  const invocation = await store.startInvocation({ runId: run.id, worktreeId,
    owner: { host: 'explicit-authoring', pid: process.pid, start: null } });
  const capture = await store.createCapture({ invocationId: invocation.id, channel: 'report' });
  await store.appendCapture({ id: capture.id, chunks: [{ sequence: 1, text }], state: 'complete' });
  await store.finalizeInvocation({ id: invocation.id, outcome: 'succeeded', cleanup: 'complete',
    claimId: invocation.claim.id, token: invocation.claim.token });
  return { invocationId: invocation.id, captureId: capture.id, sha256: sha(text) };
}
```

Run each following phase separately with the shared setup above and close the store in `finally`. Phase 1 prepares the explicitly supplied approval and retains it for review. A JSON file containing the preparation is merely a display artifact. The separate retained reference is what confirmation accepts.

```js
try {
  const prepared = await prepareAdoption(history, read('/absolute/disposable/approval.json'));
  save('/absolute/disposable/prepared.json', prepared);
  save('/absolute/disposable/preparation-reference.json', await retainReport(prepared));
} finally { store.close(); }
```

After explicit authorization, perform the ordinary one-file authoring action and Git commit in the approved repository. Phase 2 supplies that action's separately recorded reference and status, resolves the retained preparation, and preserves the observed outcome even on failure or uncertainty. `action.json` is `{ "reference": "authoring-action-id", "status": "succeeded" }` only if the actual external action succeeded; the other supported statuses are `failed` and `uncertain`.

```js
try {
  const outcome = await confirmAdoption(history, read('/absolute/disposable/preparation-reference.json'),
    read('/absolute/disposable/action.json'));
  save('/absolute/disposable/adoption-result.json', outcome);
  save('/absolute/disposable/adoption-reference.json', await retainReport(outcome));
} finally { store.close(); }
```

Phase 3 requires a new explicit revert approval. It resolves the retained adoption outcome and its original retained preparation, validates their relationship, then retains the new revert preparation. `revert-approval.json` contains the new human approval reference, for example `{ "reference": "human-revert-approval-id" }`.

```js
try {
  const prepared = await prepareRevert(history, read('/absolute/disposable/adoption-reference.json'),
    read('/absolute/disposable/revert-approval.json'));
  save('/absolute/disposable/revert-prepared.json', prepared);
  save('/absolute/disposable/revert-preparation-reference.json', await retainReport(prepared));
} finally { store.close(); }
```

After the separately authorized ordinary revert commit, phase 4 resolves that retained revert approval, revalidates the retained original adoption and all learning evidence, and observes the resulting target. `revert-action.json` records the external revert action's own reference and actual status.

```js
try {
  const outcome = await confirmRevert(history, read('/absolute/disposable/revert-preparation-reference.json'),
    read('/absolute/disposable/revert-action.json'));
  save('/absolute/disposable/revert-result.json', outcome);
  save('/absolute/disposable/revert-reference.json', await retainReport(outcome));
} finally { store.close(); }
```

Every saved boundary accepts `{ invocationId, captureId, sha256 }`, resolves a complete report from a successfully finalized invocation, verifies the digest of its actual bytes, and revalidates its references. The gateway remains read-only. Missing, partial, pruned, foreign or changed records stop the operation. Editing a JSON preparation or confirmation cannot reuse its earlier retained reference, even if all local fields and hashes are changed consistently. A newly retained preparation is a new approval artifact, not proof of the earlier human decision. The system does not authenticate approval authors, protect against a malicious history provider or authorized store writer, or prevent callers from deliberately selecting another approval artifact. The external authoring owner must preserve and select the reviewed reference; arbitrary report writes must never be presented as authenticated human authorization.

An adoption approval identifies one extraction invocation and proposal key, one evaluation invocation plus exact report capture and SHA-256, one candidate invocation plus exact capture and SHA-256, and one repository root, repository-scoped relative path, expected Git commit and expected file SHA-256. `prepareAdoption` reads complete retained report and candidate captures through the bounded read-only `SourceHistoryGateway`. It requires a successfully finalized `.factory/workflows/evaluate.ts` producer with a supported assessment and no limitations. The producer path is only an initial check: the referenced extraction must have its actual `.factory/workflows/learn.ts` report, owned successful extraction attempt, complete raw and normalized results, and captured input context. The normalized proposals must equal the report proposals, and their source lineage must match retained source attempts, events, and captures. An event with an explicit `invocationId` must match the source even if another field names an owned capture. Without that ID, ownership must resolve to an actual source attempt or capture within the same three-page bound used by `learn.ts`; copied extractor claims do not establish ownership. Missing, foreign, partial, pruned, or unexamined evidence stops preparation. Evaluation command attempts must belong to that evaluation with the expected operation keys, outcomes, and captured settings; review attempts must have matching owned normalized results and read-only input contexts for the exact compared bytes and criteria. The bounded cases must show a consistent candidate success and observed baseline improvement. The evaluation report must bind the selected extraction, candidate and target; its resolved baseline digest must equal the approved expected target content, and its resolved candidate digest must match the approved capture bytes. It observes the current Git commit and committed target bytes before returning a preparation. Missing or changed references, a changed candidate, changed target content or revision, an unsupported/inconclusive evaluation, shared scope, symlinks and uncommitted target edits stop preparation. The preparation retains the evaluation's extraction report and normalized result references; the source and evaluation records remain in history.

After preparation, the explicitly authorized operator uses an ordinary authoring/version-control path to change and commit the selected file. The operator records an independent action reference and one of `succeeded`, `failed`, or `uncertain`. `confirmAdoption(history, preparationReference, action)` resolves the independently retained preparation and revalidates candidate, evaluation, extraction, and source provenance before checking the historical baseline bytes and observing the target again. Provenance validation is separate from the initial current-baseline observation, so a legitimate committed candidate can be confirmed. The outcome retains its `preparationReference`. Commit ancestry is derived from the approval rather than a mutable preparation field. It records `applied` only when the action reports success and the new commit is a direct, single-parent child of the approved expected commit, the only changed path is the approved path, and both committed and working file bytes hash to the approved candidate. An unchanged target is `not_applied`; an observation failure, wrong bytes, extra path, merge commit, intervening commit, or mismatch is `uncertain`. Failed or uncertain actions cannot yield `applied`, even if matching bytes appear. The action result and observed applied revision are separate fields.

An explicit revert begins from a recorded `applied` adoption and a new human approval reference. `prepareRevert(history, adoptionReference, approval)` resolves the retained confirmation and its retained original preparation, rejects any disagreement in approval or extraction evidence, and revalidates that the claimed applied commit is a direct single-parent child of the approved baseline, changes only the approved path, and contains the approved candidate bytes. It also checks the historical baseline bytes and current target against the applied commit. `confirmRevert(history, revertPreparationReference, action)` resolves the retained revert preparation, compares the complete embedded adoption against its independently retained confirmation, repeats all learning provenance and historical proof, and rejects a preparation whose expected identity differs from the original applied observation. After an ordinary version-control revert, `confirmRevert` requires a separately recorded successful action and a direct, single-parent commit changing only the same target back to its approved pre-adoption hash. `reverted` contains the actual observed reverting revision and the complete original adoption reference. Failure and uncertainty cannot claim a revert. A changed post-adoption target requires renewed review.

These observations bind to the local Git worktree and selected path. They do not make external Git actions atomic: a concurrent writer can race a prepare or observation. The ordinary action should recheck the expected commit immediately before authoring and stop on a mismatch. If a race, crash, or other uncertainty occurs, preserve the records and inspect the repository before any new explicit attempt. There is no automatic retry, replay, promotion, or rollback daemon.

## Fixture evidence

The public `test:learning -- --operation adopt` selector is registered by the integration owner. The focused source command is `node --test test/learning-adoption.test.mjs` from `packages/software-factory` after `npm run build`, with pinned Node v24.22.1 on `PATH`. The test uses disposable Git repositories only. It covers approval without application, changed candidate and scope, absent authorization, changed expected content and revision, failed/uncertain action, wrong and broader commits, an intervening target commit, actual application, and actual revert. One composed case runs the real `learn.ts` extraction and `evaluate.ts` comparison over retained captures, saves an inconclusive evaluation, reruns a supported comparison, then applies and reverts only the fixture target. It verifies original extraction and inconclusive evaluation remain readable and that the adoption and revert records retain the source/evaluation lineage. Fake provider reviews establish protocol behavior, not live model quality. `evaluate.ts` support describes only its supplied bounded cases and criteria.

Observed on the isolated `codex/factory-learning-adoption` branch from base `3ad871d5`, using pinned Node v24.22.1 on macOS arm64: final `npm run typecheck` and `npm run build` exited 0. After the baseline-to-target binding repair, `node --test test/learning-adoption.test.mjs test/learning-evaluation.test.mjs test/workflows.test.mjs test/store.test.mjs test/capture.test.mjs test/validated-results.test.mjs` passed all 91 cases in 86.408 seconds, including seven focused adoption cases (historical pre-review run). The existing public `npm run test:learning` selector passed all 33 registered extraction/evaluation cases (20 evaluation plus 13 extraction). Parent integration must register the new adoption file under `test:learning -- --operation adopt`, run that public selector and the composed source suite before milestone acceptance. No paid provider, desktop test, global install, remote push, or real repository adoption is part of this qualification.

## Independent review repair

The review reproducer `/private/tmp/adoption-review-repro.mjs` was run against the pre-repair built module and reproduced all three findings: an unrelated report with nonexistent extraction references prepared successfully, an edited saved expected revision yielded `applied` after an intervening commit, and that invalid adoption was accepted for revert. `/private/tmp/adoption-repair-red.log` records the saved-object public regression failing before the implementation change. The repair keeps `SourceHistoryGateway` unchanged and adds validation only to its adoption consumers.

The expanded adoption suite covers JSON reload identity substitution, original adoption ancestry and historical baseline checks, missing/foreign/partial/pruned extraction and evaluation captures, mismatched normalized proposals, dishonest objective claims, and retained unrelated/forged evaluation reports. The real workflow still preserves extraction, inconclusive evaluation, revised supported evaluation, and separate approval/action/revert reports. Final post-source-change validation used the same pinned Node v24.22.1 path above. `npm run typecheck` and `npm run build` exited 0 (`/private/tmp/adoption-repair-typecheck-final.log`, `/private/tmp/adoption-repair-build-final.log`). The affected six-file public-module run passed 94/94 tests in 53.064 seconds (`/private/tmp/adoption-repair-affected-final.log`), including all ten adoption tests. The unchanged independent repro now stops at its unrelated producer boundary (`/private/tmp/adoption-repair-review-repro-after.log`); later saved-object paths are independently exercised by the regression suite. `/private/tmp/adoption-repair-reference-red.log` records an additional red test for changing the revert approval reference during asynchronous observation; preparation now snapshots that input. Independent follow-up review and parent registration/base integration proof remain separate gates.

The final registered `npm run test:learning` run exited 0 with 20/20 evaluation tests and 13/13 extraction tests (49.656 and 9.967 seconds respectively; `/private/tmp/adoption-repair-public-final.log`). This checkout still does not register adoption under that selector: the ten adoption cases are included in the 94-test public-module run above, and the parent must register and prove `--operation adopt` after integration.


## Retained approval and event ownership follow-up

The second independent review found that editing only a JSON-reloaded candidate digest could still yield `applied`, then allow revert, and that a foreign retained event could be copied consistently into extractor context and report. Both supplied public-module reproducers reproduced before this change: `/private/tmp/adoption-retained-original-red.log` and `/private/tmp/adoption-event-original-red.log`. A separate composed real-store workflow reproduced the edited-candidate defect using actual extraction/evaluation reports and a disposable Git commit (`/private/tmp/adoption-retained-real-red.log`, expected rejection missing). `/private/tmp/adoption-event-red.log` captures the public-boundary foreign-event test failing before its ownership fix.

This repair changes the unreleased confirmation/revert signatures to the retained-reference forms shown above; there is no compatibility overload accepting mutable preparations or outcomes as authority. `SourceHistoryGateway` is unchanged. Each applied result names the retained preparation; each revert preparation names the retained applied result; each revert result names the retained revert preparation. All consumers resolve complete captures, compare their digests, revalidate extraction/evaluation/candidate relationships, and derive target identities from the retained approval. Revert also compares its complete embedded original outcome with the independently retained confirmation. Explicit event ownership takes precedence; absent invocation ownership is resolved against actual bounded source history. A valid owner on a later history page is accepted even when it is outside the selected extractor evidence; foreign or unexamined ownership is rejected.

Validation used `/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/factory-qualified-node-i2fv29e3/node-v24.22.1-darwin-arm64/bin/node` (v24.22.1) on macOS arm64. `npm run typecheck` exited 0 (`/private/tmp/adoption-retained-typecheck-final.log`); final source build exited 0 (`/private/tmp/adoption-event-build.log`). The focused twelve-case suite passed (`/private/tmp/adoption-retained-boundaries.log`), including the real-store reference-only authoring/confirmation/revert sequence and rejection of an actual unapproved commit. The affected command `node --test test/learning-adoption.test.mjs test/learning-evaluation.test.mjs test/workflows.test.mjs test/store.test.mjs test/capture.test.mjs test/validated-results.test.mjs` passed 96/96 in 60.629 seconds (`/private/tmp/adoption-retained-affected-final.log`). Registered `npm run test:learning` passed all 20 evaluation and 13 extraction cases (`/private/tmp/adoption-retained-public-final.log`). The unchanged event repro now fails at retained evidence ownership (`/private/tmp/adoption-event-repro-final.log`); the initial unrelated-evaluation repro remains rejected (`/private/tmp/adoption-initial-repro-final.log`). The old edited-preparation repro uses the superseded signature; the adapted real-store test proves both rejection of that object and `uncertain` for the unapproved bytes using the correct retained reference.

The mutation cases cover candidate, target, evaluation, extraction, human reference, partial/pruned/foreign retained approval, forged applied outcomes, forged embedded confirmations, and later pruning of previously accepted review evidence. Failed/uncertain/non-applied records cannot be used as applied adoption. The exact original/reverting revisions and original source history remain preserved. The official Node v24.22.1 [crypto documentation](https://nodejs.org/docs/latest-v24.x/api/crypto.html#cryptocreatehashalgorithm-options) confirms the existing SHA-256 byte-digest API; a digest is integrity evidence, not authentication of a human or store writer.

Self-review covered correctness, boundary design, bounded reads, and API migration. Reflection found the durable lesson encoded in the reference-only boundary and regression tests; no extra brain note was needed. Independent follow-up review and parent integration, including adoption registration under the public selector, remain acceptance gates. No real user repository was adopted, no new database schema or workflow facade was introduced, and no push or integration occurred.
