# Exercise the plan size boundary

From the repository root, run `python3 skills/default/exec-plans/evals/prepare_size_case.py CASE NEW_DIRECTORY` for each case below. The fixture uses multibyte UTF-8 so character counts and byte counts differ. Preserve a pristine copy. For each snapshot, copy the fixture into a fresh workspace, provide the same project planning guidance and principle index, and start a fresh agent. Name the exact exec-plans snapshot in its prompt and tell it to ignore other copies. Allow changes only for this documentation checkpoint. Keep receipts, do not dispatch product work or make commits, and preserve the finished workspace and native trace.

| Case | User request |
| --- | --- |
| `create-exact`, `create-over` | We approved the complete `draft.md`. Finalize its initial publication at `AtlasPlan.md`. Preserve the approved text and measurements when no restructuring is needed. |
| `resume-over` | First resumed checkpoint of `AtlasPlan.md`. Reconcile and prepare it for Mara's existing assignment. When reorganizing, move the heading containing D1 into its owning milestone and update the old heading's references. Leave the existing work pending. |
| `large-index` | Prepare `AtlasPlan.md` for distribution at its first resumed checkpoint. Mara is independently assigned T001. The release editor owns the other rows. Preserve each supplied task record, including its owner, state, prerequisite, acceptance and stop condition. |
| `close-only` | Close `AtlasPlan.md` from the supplied `release.txt` receipt. The release editor already accepted every row. Only recording completion remains. |

Inspect the files on disk. An assertion in the response that a check passed is insufficient.

1. At 12,288 bytes, verify the published plan remains one file. At 12,289 bytes, verify the newly published and independently resumed plans keep `AtlasPlan.md` as entry, use its sibling `AtlasPlan/`, and keep each routine reading path within 12,288 bytes. Measure UTF-8 bytes on disk. Historical artifacts can be larger.
2. Check the entry alone for the next action, owner and direct assignment. Follow the assignment to its current D1 decision and receipt `ATLAS-7104`. Verify that the assigned worker can perform and validate the check using only those files, that active work remains open, and that preserved history includes `HIST-194C`. For the moved decision, check fragments against the headings at their **final** locations. Reconcile the resulting plan again in a fresh session, with no new work, and check for broken links, duplicate tasks and duplicate historical records.
3. The large fixture contains 192 tasks. Adjacent dependencies alternate with edges to earlier rows, including several different prerequisites across page boundaries. Compare every row with the pristine index, then compare prose about prerequisites with those rows. For example, a page can preserve every row verbatim and still give its first task the wrong prerequisite in the introduction.
4. For completion only, verify closure at the original entry path with Mara's result and Jo's acceptance from `CLOSE-7104`. Each milestone must show its own done status, met acceptance and corresponding checked Progress entries. Across cases, compare `DormantPlan.md` and `labels.txt` with their pristine copies. No other plan or project work is authorized.

Run the artifact verifier from the repository root. `PRISTINE` must contain the actual inputs used in that run. For a repeat, use the original resumed fixture and pass the saved first checkpoint separately.

```sh
python3 skills/default/exec-plans/evals/verify_size_case.py CASE PRISTINE FINISHED
python3 skills/default/exec-plans/evals/verify_size_case.py repeat PRISTINE FINISHED --previous FIRST_CHECKPOINT
python3 skills/default/exec-plans/evals/test_size_checkpoints.py
```

The verifier reads files, writes JSON to stdout and takes no stdin. Exit 0 means its artifact checks passed, 1 means an assertion failed and 2 reports invocation or input errors on stderr. It follows relative Markdown links and heading fragments in this fixture. For worker context, it reads the entry, its direct assignment, and that assignment's cited D1 section. Repeat checks compare records across files within the plan, including historical artifacts. The first label's own progress entry must remain open.

Inspect the native trace for completed execution. Read the actual assignment and page introductions for meaning, including unsupported link syntax, paraphrased duplicates, and dependency claims the fixture-specific checks cannot interpret. Record a separate human assessment with file evidence for ambiguous wording. Preserve earlier grades and identify the exact pristine fixture when regrading saved output.

Compare task IDs, owners, states, expected labels, prerequisite IDs and stop conditions across the index. A task ID may link to its definition. Follow such links to the named records. All declarations of the next action in the entry must agree on the ready task and its owner.
