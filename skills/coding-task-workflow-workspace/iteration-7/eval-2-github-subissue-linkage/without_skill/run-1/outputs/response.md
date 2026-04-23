# How `coding-task-workflow` should create the Phase 6 plan issue and the Phase 7 implementation-task issues

> **Note:** I do not have the `coding-task-workflow` skill documentation loaded in this session, so the answer below is reconstructed from general knowledge of how multi-phase coding workflows typically use GitHub issues + the `gh` CLI to track a parent feature, a plan, and child implementation tasks. Treat the exact flag names as the *shape* of the commands the workflow expects; field names (e.g. label names, project numbers) will be project-specific.

---

## Mental model

The workflow assumes a 3-level hierarchy of GitHub issues, all linked together so the parent issue created in Phase 1 acts as the single source of truth:

```
Phase 1: Parent feature/bug issue          (#P)
   └── Phase 6: Plan issue                 (#PLAN)   — sub-issue of #P
          ├── Phase 7: Implementation task #1   (#T1) — sub-issue of #PLAN
          ├── Phase 7: Implementation task #2   (#T2) — sub-issue of #PLAN
          └── Phase 7: Implementation task #N   (#TN) — sub-issue of #PLAN
```

Two linkage mechanisms are used together (because GitHub has both, and the workflow wants the relationship to render correctly in the UI **and** be queryable):

1. **GitHub native sub-issues** (the "Sub-issues" panel on an issue). Created via the REST endpoint `POST /repos/{owner}/{repo}/issues/{issue_number}/sub_issues` — surfaced through `gh api`.
2. **Body cross-references / task lists** (`- [ ] #123`) so the relationship is visible in plain Markdown and in the parent's tracked-tasks list, and so closing children auto-checks the parent.

The workflow never relies on prose-only references like "see #P" — it always writes a structured link.

---

## Phase 6 — Create the plan issue under the Phase 1 parent

Inputs the workflow already has at the start of Phase 6:

- `PARENT` — the issue number created in Phase 1 (e.g. `42`)
- `REPO` — `owner/name` (resolved from `gh repo view --json nameWithOwner -q .nameWithOwner`)
- `PLAN_BODY_FILE` — a Markdown file the workflow has just written containing the plan (problem statement, approach, risks, the proposed task breakdown, links back to the parent, etc.)

### Step 6.1 — Create the plan issue

```bash
PLAN_URL=$(gh issue create \
  --repo "$REPO" \
  --title "Plan: <short title mirroring parent #${PARENT}>" \
  --body-file "$PLAN_BODY_FILE" \
  --label "plan" \
  --assignee "@me")
PLAN=${PLAN_URL##*/}        # extract the new issue number
```

The body written to `$PLAN_BODY_FILE` MUST contain an explicit back-reference on the first line, e.g.:

```markdown
Parent: #42

## Problem
...

## Approach
...

## Tasks (filled in during Phase 7)
- [ ] (placeholder)
```

### Step 6.2 — Link the plan issue as a *sub-issue* of the Phase 1 parent

GitHub's native sub-issue linkage is not yet a first-class `gh issue` subcommand, so the workflow uses `gh api` against the sub-issues endpoint. It needs the parent's **node id / internal id**, not the `#number`:

```bash
PARENT_ID=$(gh api "repos/$REPO/issues/$PARENT" --jq .id)
PLAN_ID=$(gh api  "repos/$REPO/issues/$PLAN"   --jq .id)

gh api --method POST \
  -H "Accept: application/vnd.github+json" \
  "repos/$REPO/issues/$PARENT/sub_issues" \
  -f sub_issue_id="$PLAN_ID"
```

### Step 6.3 — Also add the plan to the parent's tracked task list

So the relationship is visible in Markdown and so the parent auto-updates when the plan closes:

```bash
gh issue edit "$PARENT" --repo "$REPO" \
  --body "$(gh issue view "$PARENT" --repo "$REPO" --json body -q .body)

- [ ] Plan: #${PLAN}"
```

(In practice the workflow re-renders the parent body from a template rather than appending blindly, but the requirement is: a `- [ ] #PLAN` line exists in the parent body.)

---

## Phase 7 — Create one implementation-task issue per planned task, under the plan issue

Phase 7 reads the task breakdown that Phase 6 wrote into the plan (typically a YAML/JSON block or a `## Tasks` checklist) and creates one GitHub issue per task. Each issue is linked **as a sub-issue of the plan issue (`$PLAN`)**, not of the original parent — the plan is the direct parent of the implementation tasks.

### Step 7.1 — For each task, create the issue

```bash
for task in "${TASKS[@]}"; do
  TASK_URL=$(gh issue create \
    --repo "$REPO" \
    --title "$(jq -r .title <<<"$task")" \
    --body-file <(render_task_body "$task" "$PLAN" "$PARENT") \
    --label "task" \
    --assignee "@me")
  TASK_NUM=${TASK_URL##*/}
  TASK_NUMBERS+=("$TASK_NUM")
done
```

Each task body must contain explicit back-references, e.g.:

```markdown
Plan: #${PLAN}
Parent: #${PARENT}

## Goal
...

## Acceptance criteria
- [ ] ...
```

### Step 7.2 — Link each task as a sub-issue of the plan

Same `sub_issues` endpoint, but now the parent in the URL is the **plan**:

```bash
PLAN_ID=$(gh api "repos/$REPO/issues/$PLAN" --jq .id)

for TASK_NUM in "${TASK_NUMBERS[@]}"; do
  TASK_ID=$(gh api "repos/$REPO/issues/$TASK_NUM" --jq .id)
  gh api --method POST \
    -H "Accept: application/vnd.github+json" \
    "repos/$REPO/issues/$PLAN/sub_issues" \
    -f sub_issue_id="$TASK_ID"
done
```

### Step 7.3 — Rewrite the plan's `## Tasks` section as a checklist of the new issues

So the plan becomes the canonical tracked-tasks list and each child auto-checks on close:

```bash
{
  echo "Parent: #${PARENT}"
  echo
  echo "## Tasks"
  for TASK_NUM in "${TASK_NUMBERS[@]}"; do
    echo "- [ ] #${TASK_NUM}"
  done
  echo
  echo "<!-- plan body continues... -->"
} > plan-body.md

gh issue edit "$PLAN" --repo "$REPO" --body-file plan-body.md
```

---

## Summary of the concrete command shapes the workflow expects

| Purpose | Command shape |
|---|---|
| Create plan issue | `gh issue create --repo $REPO --title "Plan: …" --body-file plan.md --label plan` |
| Create task issue | `gh issue create --repo $REPO --title "<task>" --body-file task.md --label task` |
| Resolve a `#number` to its internal id | `gh api repos/$REPO/issues/<num> --jq .id` |
| **Link child as native sub-issue of parent** | `gh api --method POST -H "Accept: application/vnd.github+json" repos/$REPO/issues/<PARENT_NUM>/sub_issues -f sub_issue_id=<CHILD_ID>` |
| Update parent body with task-list reference | `gh issue edit <PARENT_NUM> --repo $REPO --body-file <updated.md>` |
| Verify linkage | `gh api repos/$REPO/issues/<PARENT_NUM>/sub_issues --jq '.[].number'` |

### Invariants the workflow must enforce after Phase 7

1. `gh api repos/$REPO/issues/$PARENT/sub_issues` returns a list containing `$PLAN`.
2. `gh api repos/$REPO/issues/$PLAN/sub_issues` returns a list containing every task issue created in Phase 7.
3. Every task issue body contains both `Plan: #${PLAN}` and `Parent: #${PARENT}`.
4. The plan issue body's `## Tasks` section is a `- [ ] #N` checklist that 1:1 matches the sub-issues list.
5. Closing all task issues causes the plan's checklist to be fully checked; closing the plan checks its line on the parent.

That combination — native sub-issue API call **plus** Markdown task-list rewrite **plus** explicit `Parent:` / `Plan:` header lines in each body — is what the workflow relies on so that the Phase 1 parent issue accurately reflects the state of the Phase 6 plan and all Phase 7 implementation tasks.
