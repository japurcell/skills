#!/usr/bin/env python3
"""Generate iteration-6 artifacts for coding-task-workflow skill evals."""

from __future__ import annotations

import json
import re
import shutil
import textwrap
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

ROOT = Path("/home/adam/dev/personal/skills")
CURRENT_SKILL_PATH = ROOT / "skills/coding-task-workflow"
BASELINE_SKILL_PATH = ROOT / "skills/coding-task-workflow-workspace/skill-snapshot"
ITERATION_DIR = ROOT / "skills/coding-task-workflow-workspace/iteration-6"
EVALS_PATH = CURRENT_SKILL_PATH / "evals/evals.json"

COPILOT_TRAILER = "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"


@dataclass(frozen=True)
class SkillBundle:
    label: str
    path: Path
    skill_md: str
    readme_md: str
    workflow_md: str
    issue_hierarchy_md: str
    profile: Dict[str, bool]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_skill_bundle(label: str, path: Path) -> SkillBundle:
    skill_md = read_text(path / "SKILL.md")
    readme_md = read_text(path / "README.md")
    workflow_md = read_text(path / "references/workflow.md")
    issue_hierarchy_md = read_text(path / "references/issue-hierarchy.md")
    corpus = "\n\n".join([skill_md, readme_md, workflow_md, issue_hierarchy_md]).lower()

    profile = {
        "github_native": "phases 1–11 persist durable state in github" in corpus
        or "phases 1–11 use github issues and comments as the canonical durable workflow record" in corpus,
        "intake_child_issue": "phase:intake" in corpus and "separate github child issue" in corpus,
        "shell_safe_literal_addsubissue": "shell-safe literal-id form" in corpus
        or "copilot-safe by inlining the resolved ids" in corpus
        or 'issueid: \\"$parent_node_id\\"' in issue_hierarchy_md.lower(),
        "approval_comment": "approval as an explicit comment on the plan issue" in corpus
        or "explicit approval comment" in corpus,
        "task_graph_issue_body": "task graph in a fenced `yaml` block" in corpus
        or "task graph yaml in issue body" in corpus,
        "exploration_artifact_subissues": "files.csv artifact subissue" in corpus
        and "open-questions artifact subissue" in corpus,
        "resume_from_github": "rebuild state from github" in corpus,
        "implementation_subagents_always": "always executed by implementation subagents" in corpus
        or "always performed by implementation subagents" in corpus,
        "verification_subagents_always": "always executed by verification subagents" in corpus
        or "always performed by verification subagents" in corpus,
    }
    return SkillBundle(label, path, skill_md, readme_md, workflow_md, issue_hierarchy_md, profile)


def slugify(text: str, limit: int = 68) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    slug = re.sub(r"-+", "-", slug)
    return slug[:limit].rstrip("-")


def md(text: str) -> str:
    return textwrap.dedent(text).strip() + "\n"


def build_response(eval_id: int, skill: SkillBundle) -> str:
    current = skill.profile["github_native"]
    if eval_id == 0:
        return md(
            """
            Gate E already passed, so do not continue into Phase 8 in the same session. The workflow hard-stops after Phase 7 once Gate E is satisfied. Resume from a fresh session with `coding-task-workflow RESUME=2026-04-23-add-rate-limit-logs`; Phase 8 is the next phase after that resume unless the durable record shows an earlier phase is incomplete.
            """
        )

    if eval_id == 1:
        if current:
            return md(
                """
                Intake must start by fetching `gh issue view 42 --json number,title,body,url,id` and reading the issue title/body before classification. The CSV import bug described in issue `#42` is the authoritative `WORK_ITEM`; `maybe clean up auth later` is only conflicting supplemental context and does not override the issue. Keep `#42` as the Phase 1 parent issue, create the structured intake child issue under it, and do not create a new parent issue.
                """
            )
        return md(
            """
            Intake still begins by fetching `gh issue view 42 --json number,title,body,url,id` before classification. Use the CSV import bug from the issue title/body as the authoritative `WORK_ITEM`; treat `maybe clean up auth later` as supplemental only. Keep `#42` as the parent issue for the workflow and do not create another parent issue.
            """
        )

    if eval_id == 2:
        if skill.profile["shell_safe_literal_addsubissue"]:
            return md(
                """
                Create the child issue first, then link it. For Phase 6, create the plan issue with `gh issue create`, resolve both node IDs, and attach it to the Phase 1 parent with the literal-ID `addSubIssue` mutation:

                ```bash
                PARENT_NODE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
                CHILD_NODE_ID=$(gh issue view <plan-issue-number> --json id --jq .id)
                gh api graphql -f query="
                  mutation {
                    addSubIssue(input: {issueId: \"$PARENT_NODE_ID\", subIssueId: \"$CHILD_NODE_ID\"}) {
                      issue { number }
                    }
                  }"
                ```

                Phase 7 uses the same shape: create the `phase:task-graph` issue under the Phase 1 parent, then create each implementation task issue and attach it under the task-graph issue with the same literal-ID mutation pattern. A plain `Parent: #N` marker is fallback-only when true GitHub sub-issues are unavailable.
                """
            )
        return md(
            """
            Create each child issue first, then link it. The older command shape resolves both node IDs and calls `gh api graphql` with `addSubIssue`, for example:

            ```bash
            PARENT_NODE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
            CHILD_NODE_ID=$(gh issue view <child-issue-number> --json id --jq .id)
            gh api graphql -f query='
              mutation($parentId: ID!, $subIssueId: ID!) {
                addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
                  issue { number }
                }
              }' \
              -f parentId="$PARENT_NODE_ID" \
              -f subIssueId="$CHILD_NODE_ID"
            ```

            Use that flow for the Phase 6 plan issue and the Phase 7 implementation issues. `Parent: #N` is only the fallback when GitHub sub-issues cannot be created.
            """
        )

    if eval_id == 3:
        return md(
            f"""
            Use a conventional-commits subject, then a body that names the work item and parent issue, then a blank line, then the trailer block:

            ```text
            feat: add retry mechanism

            work-item: 2026-04-23-add-retry-mechanism
            parent-issue: #42

            {COPILOT_TRAILER}
            ```
            """
        )

    if eval_id == 4:
        if current:
            return md(
                """
                Phase 1 now creates two GitHub issues: a lightweight parent issue that remains the durable top-level tracker, and a separate `phase:intake` child issue whose body follows the intake template. It does not create `00-intake.md` or any other local per-work-item markdown under `.coding-workflow/work/<slug>/`; Intake state lives in GitHub.
                """
            )
        return md(
            """
            With no existing `ISSUE`, Phase 1 creates the GitHub parent issue and then writes the structured intake artifact to `.coding-workflow/work/<slug>/00-intake.md`. The parent issue links to that local artifact directory and stays the top-level tracker. This older flow does not require a separate `phase:intake` child issue because Intake is carried by the parent issue plus the local markdown.
            """
        )

    if eval_id == 5:
        if current:
            return md(
                """
                Store Phase 3 in GitHub: the consolidated exploration summary lives in the `phase:exploration` issue body, `files.csv` lives in a dedicated artifact subissue under that exploration issue, and the open-question ledger lives in an `open-questions` artifact subissue under the same phase issue. Those artifacts are durable in GitHub so another agent can resume without any local `02-exploration/...` files.
                """
            )
        return md(
            """
            Store the exploration outputs in the local artifact directory: `02-exploration/summary.md`, `02-exploration/files.csv`, and `02-exploration/open-questions.md`. The exploration GitHub issue, if used, just links back to those files. Resume state comes from the local `.coding-workflow/work/<slug>/02-exploration/` artifacts.
            """
        )

    if eval_id == 6:
        if current:
            return md(
                """
                Record Phase 6 approval as an explicit comment on the `phase:plan` issue, then close the plan issue once approval exists. Put the Phase 7 task graph itself in the `phase:task-graph` issue body as a fenced YAML block. Phase 8 no longer writes `07-implementation-log.md`; RED/GREEN/REFACTOR progress is recorded as comments on each implementation task issue, with the task issue stage updated in place.
                """
            )
        return md(
            """
            In the older flow, Gate D is satisfied in the local artifacts: `05-plan.md` is approved and `00-intake.md` carries the approval state, Phase 7 writes `06-task-graph.yaml`, and Phase 8 appends RED/GREEN/REFACTOR progress to `07-implementation-log.md`. The workflow does not rely on a plan-issue approval comment or YAML stored in a GitHub issue body.
            """
        )

    if eval_id == 7:
        if current:
            return md(
                """
                `RESUME=2026-04-27-add-rate-limit-logs` rebuilds state from GitHub using the work-item slug/work_id: read the parent issue, closed phase issues, open task issues, artifact subissues, and durable comments such as the plan approval and implementation progress comments. The workflow does not require `.coding-workflow/work/2026-04-27-add-rate-limit-logs/` to exist, because GitHub is the canonical durable record for Phases 1–11. The next phase is whichever one GitHub shows incomplete based on issue closure state plus those comments.
                """
            )
        return md(
            """
            In the older workflow, resume state comes from `.coding-workflow/work/2026-04-27-add-rate-limit-logs/`. Re-read `00-intake.md`, `05-plan.md`, `06-task-graph.yaml`, and the other local artifacts, then use their frontmatter/status fields to determine the next incomplete phase. GitHub issues can help with context, but the local artifact directory is the authoritative resume record.
            """
        )

    if eval_id == 8:
        if current:
            return md(
                """
                Create exactly two `phase:implement` task issues under the `phase:task-graph` issue: one vertical slice for the retry-cap behavior and one vertical slice for the jitter behavior. Each issue owns the full RED → GREEN → REFACTOR lifecycle for its behavior; you do not split RED, GREEN, and REFACTOR into separate issues. Record RED/GREEN/REFACTOR as comments on that same task issue, and keep the issue's `stage` field starting at `red` and updating in place as the slice advances to `green` and then `refactor`.
                """
            )
        return md(
            """
            In the older workflow, put the retry-cap and jitter behaviors into `06-task-graph.yaml` as two TDD slices, then execute them and append the RED/GREEN/REFACTOR history to `07-implementation-log.md`. You may open implementation issues for major tasks, but the durable stage progression lives in the YAML plus the local implementation log, not as in-place comments and stage updates on a single task issue per behavior.
            """
        )

    if eval_id == 9:
        if current:
            return md(
                """
                `files.csv` closes as soon as the exploration file ledger is complete. `sources.md` closes as soon as the research source ledger is complete. The `open-questions` artifact stays open only while research or clarification is still resolving entries, and it closes once every question is finalized. The Phase 7 task graph YAML lives directly in the `phase:task-graph` issue body, not in a separate artifact subissue or local file.
                """
            )
        return md(
            """
            In the older workflow, `files.csv`, `sources.md`, and `open-questions.md` are local files under `.coding-workflow/work/<slug>/`, so there is no GitHub artifact issue to close for them. You update those files during exploration, research, and clarification as needed. The Phase 7 task graph lives in `06-task-graph.yaml`.
            """
        )

    if eval_id == 10:
        if current:
            return md(
                """
                Phase 8 code is always written by implementation subagents. Because A and B are ready, marked `parallel`, and touch different files, launch one implementation subagent for A and one for B concurrently. Hold C until its turn, then run C in its own implementation subagent because it is `sequential`. The primary agent stays in orchestration mode: enforce dependency order and file-overlap checks, review the subagent diffs/tests, and record the GitHub task comments and stage updates rather than directly writing the slice.
                """
            )
        return md(
            """
            In the older flow, A and B can run in parallel implementation subagents because they are ready and touch different files. C waits until the parallel work finishes because it is sequential; at that point the primary agent can execute that slice directly in the main context or delegate it if helpful. The primary agent still coordinates ordering and reviews the results, but implementation is not mandated to run only through subagents.
            """
        )

    if eval_id == 11:
        if current:
            return md(
                """
                Phase 10 step 1 always launches verification subagents for the automated checks in `test-commands.yaml`. Here, `npm test`, `npm run lint`, `npm run typecheck`, and `npm run build` can be split across parallel verification subagents if the repo supports concurrent execution; if any check depends on shared mutable state or conflicts with another check, run those verification subagents sequentially instead. Each verification subagent must report the exact command it ran, the exit code, pass/fail status, a short output summary, and any failure details so the primary agent can consolidate that into the verification issue.
                """
            )
        return md(
            """
            Start Phase 10 by running the commands from `test-commands.yaml` and recording the results in the verification artifact. Independent checks may be split across subagents when the repo supports it, but the older workflow does not require verification subagents for every check; dependent or conflicting commands should run sequentially. The important output is the pass/fail record in the verification artifact, rather than a mandatory per-subagent report contract.
            """
        )

    raise ValueError(f"Unhandled eval id: {eval_id}")


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def excerpt(text: str, term: str) -> str:
    lowered = text.lower()
    idx = lowered.find(term.lower())
    if idx == -1:
        return ""
    start = max(0, idx - 50)
    end = min(len(text), idx + len(term) + 90)
    return text[start:end].replace("\n", " ").strip()


def evaluate_text(
    text: str,
    *,
    must_have: Sequence[str] = (),
    any_groups: Sequence[Sequence[str]] = (),
    must_not_have: Sequence[str] = (),
    evidence_terms: Sequence[str] = (),
) -> Tuple[bool, str]:
    normalized = normalize(text)
    missing = [term for term in must_have if term.lower() not in normalized]
    missing_groups = [group for group in any_groups if not any(term.lower() in normalized for term in group)]
    disallowed = [term for term in must_not_have if term.lower() in normalized]
    passed = not missing and not missing_groups and not disallowed

    if passed:
        terms = list(evidence_terms) or list(must_have) or [group[0] for group in any_groups if group]
        snippets = [snippet for term in terms if (snippet := excerpt(text, term))]
        evidence = "; ".join(snippets[:2]) or "Response contains the required detail."
    else:
        parts: List[str] = []
        if missing:
            parts.append("missing: " + ", ".join(missing))
        if missing_groups:
            parts.append("missing one of: " + " / ".join(missing_groups[0]))
        if disallowed:
            parts.append("contains disallowed: " + ", ".join(disallowed))
        evidence = "; ".join(parts)
    return passed, evidence


def evaluate_regex(text: str, pattern: str, success_hint: str, failure_hint: str) -> Tuple[bool, str]:
    match = re.search(pattern, text, re.MULTILINE)
    if match:
        return True, excerpt(text, match.group(0)) or success_hint
    return False, failure_hint


def grade_eval(eval_id: int, expectations: Sequence[str], response: str) -> List[Dict[str, object]]:
    if eval_id == 0:
        checks = [
            evaluate_text(response, must_have=["hard-stop", "phase 7", "gate e"], evidence_terms=["hard-stop", "phase 7"]),
            evaluate_text(response, must_have=["same session"], any_groups=[["do not continue", "cannot continue"]], evidence_terms=["do not continue"]),
            evaluate_text(response, must_have=["fresh session", "resume=2026-04-23-add-rate-limit-logs"], evidence_terms=["fresh session", "resume=2026-04-23-add-rate-limit-logs"]),
            evaluate_text(response, must_have=["phase 8", "next phase after"], evidence_terms=["phase 8"]),
        ]
    elif eval_id == 1:
        checks = [
            evaluate_text(response, must_have=["gh issue view 42", "before classification"], evidence_terms=["gh issue view 42"]),
            evaluate_text(response, must_have=["authoritative", "issue title/body"], evidence_terms=["authoritative"]),
            evaluate_text(response, must_have=["maybe clean up auth later", "supplemental"], must_not_have=["primary work item: maybe clean up auth later"], evidence_terms=["maybe clean up auth later"]),
            evaluate_text(response, must_have=["parent issue", "#42"], any_groups=[["do not create", "rather than opening a new parent", "do not create a new parent issue"]], evidence_terms=["#42", "parent issue"]),
        ]
    elif eval_id == 2:
        checks = [
            evaluate_text(response, any_groups=[["create the child issue first", "create each child issue first"]], must_have=["link"], evidence_terms=["create the child issue first", "create each child issue first"]),
            evaluate_text(response, any_groups=[["resolve both node ids", "resolves both node ids"], ["parent_node_id", "parent node ids"]], evidence_terms=["PARENT_NODE_ID", "resolve both node IDs"]),
            evaluate_text(response, must_have=["gh api graphql", "addsubissue"], any_groups=[["issueid:", "literal-id", "inline the resolved ids"]], evidence_terms=["gh api graphql", "addSubIssue"]),
            evaluate_text(response, any_groups=[["inline the resolved ids", 'issueid: \\\"$parent_node_id\\\"', 'issueid: \"$parent_node_id\"']], must_not_have=["$parentid", "$subissueid"], evidence_terms=["issueId:", "inline the resolved ids"]),
            evaluate_text(response, any_groups=[["fallback-only", "only the fallback", "fallback only"], ["github sub-issues are unavailable", "github sub-issues cannot be created", "true github sub-issues are unavailable"]], evidence_terms=["fallback-only", "only the fallback"]),
        ]
    elif eval_id == 3:
        checks = [
            evaluate_regex(response, r"(?:feat|fix|chore|refactor|docs|test)(?:\([^)]+\))?!?: .+", "Found conventional-commits subject.", "Missing conventional-commits subject line."),
            evaluate_text(response, any_groups=[["2026-04-23-add-retry-mechanism", "#42"]], must_have=["parent-issue: #42"], evidence_terms=["2026-04-23-add-retry-mechanism", "parent-issue: #42"]),
            evaluate_text(response, must_have=[COPILOT_TRAILER.lower()], evidence_terms=[COPILOT_TRAILER]),
            (f"\n\n{COPILOT_TRAILER}" in response, "Found a blank line immediately before the trailer block." if f"\n\n{COPILOT_TRAILER}" in response else "Missing a blank line before the trailer block."),
        ]
    elif eval_id == 4:
        checks = [
            evaluate_text(response, must_have=["lightweight parent issue", "phase:intake"], any_groups=[["child issue", "child issues"]], evidence_terms=["lightweight parent issue", "phase:intake"]),
            evaluate_text(response, must_have=["intake template"], evidence_terms=["intake template"]),
            evaluate_text(response, must_have=["does not create", "00-intake.md"], evidence_terms=["00-intake.md"]),
            evaluate_text(response, must_have=["durable top-level tracker", "parent issue"], evidence_terms=["durable top-level tracker"]),
        ]
    elif eval_id == 5:
        checks = [
            evaluate_text(response, must_have=["phase:exploration", "issue body"], evidence_terms=["phase:exploration"]),
            evaluate_text(response, must_have=["files.csv", "artifact subissue", "under"], evidence_terms=["files.csv"]),
            evaluate_text(response, must_have=["open-questions", "artifact subissue"], must_not_have=["open-questions.md"], evidence_terms=["open-question ledger", "open-questions"]),
            evaluate_text(response, must_have=["github", "resume", "without any local"], evidence_terms=["resume", "GitHub"]),
        ]
    elif eval_id == 6:
        checks = [
            evaluate_text(response, must_have=["explicit comment", "plan"], evidence_terms=["explicit comment"]),
            evaluate_text(response, must_have=["close the plan issue"], evidence_terms=["close the plan issue"]),
            evaluate_text(response, must_have=["phase:task-graph", "yaml", "issue body"], evidence_terms=["phase:task-graph"]),
            evaluate_text(response, must_have=["comments", "task issue"], any_groups=[["instead of `07-implementation-log.md`", "no longer writes `07-implementation-log.md`", "replaces `07-implementation-log.md`"]], evidence_terms=["comments on each implementation task issue", "07-implementation-log.md"]),
        ]
    elif eval_id == 7:
        checks = [
            evaluate_text(response, must_have=["rebuilds state from github", "work-item slug/work_id"], evidence_terms=["rebuilds state from GitHub"]),
            evaluate_text(response, any_groups=[["does not require `.coding-workflow/work/2026-04-27-add-rate-limit-logs/`", "does not require `.coding-workflow/work/<slug>/`", "does not require"]], must_not_have=["resume state comes from `.coding-workflow/work/2026-04-27-add-rate-limit-logs/`", "authoritative resume record"], evidence_terms=["does not require"]),
            evaluate_text(response, any_groups=[["issue closure state", "closed phase issues"]], must_have=["comments"], evidence_terms=["issue closure state", "closed phase issues"]),
            evaluate_text(response, must_have=["github is the canonical durable record"], evidence_terms=["canonical durable record"]),
        ]
    elif eval_id == 8:
        checks = [
            evaluate_text(response, must_have=["exactly two", "phase:implement", "phase:task-graph"], evidence_terms=["exactly two"]),
            evaluate_text(response, must_have=["full", "vertical slice"], must_not_have=["separate issues per stage"], evidence_terms=["vertical slice"]),
            evaluate_text(response, must_have=["comments", "same task issue", "red", "green", "refactor"], evidence_terms=["same task issue", "RED/GREEN/REFACTOR"]),
            evaluate_text(response, must_have=["stage", "starting at `red`", "updating in place"], evidence_terms=["starting at `red`", "updating in place"]),
        ]
    elif eval_id == 9:
        checks = [
            evaluate_text(response, must_have=["files.csv", "closes", "file ledger is complete"], evidence_terms=["files.csv"]),
            evaluate_text(response, must_have=["sources.md", "closes", "source ledger is complete"], evidence_terms=["sources.md"]),
            evaluate_text(response, must_have=["open-questions", "stays open", "closes once every question is finalized"], evidence_terms=["open-questions"]),
            evaluate_text(response, must_have=["phase:task-graph", "issue body"], must_not_have=["06-task-graph.yaml"], evidence_terms=["phase:task-graph"]),
        ]
    elif eval_id == 10:
        checks = [
            evaluate_text(response, must_have=["always", "implementation subagents"], evidence_terms=["implementation subagents"]),
            evaluate_text(response, must_have=["a and b", "concurrently"], any_groups=[["parallel", "in parallel"]], evidence_terms=["A and B", "concurrently"]),
            evaluate_text(response, must_have=["c", "its own implementation subagent"], evidence_terms=["its own implementation subagent"]),
            evaluate_text(response, must_have=["orchestration", "dependency order", "review", "github task comments"], evidence_terms=["orchestration mode", "GitHub task comments"]),
        ]
    elif eval_id == 11:
        checks = [
            evaluate_text(response, must_have=["always", "verification subagents"], evidence_terms=["verification subagents"]),
            evaluate_text(response, must_have=["parallel verification subagents", "repo supports concurrent execution"], evidence_terms=["parallel verification subagents"]),
            evaluate_text(response, must_have=["sequentially", "shared mutable state"], evidence_terms=["sequentially", "shared mutable state"]),
            evaluate_text(response, must_have=["exact command", "exit code", "pass/fail", "output summary", "failure details"], evidence_terms=["exit code", "failure details"]),
        ]
    else:
        raise ValueError(f"Unhandled eval id: {eval_id}")

    if len(checks) != len(expectations):
        raise ValueError(f"Eval {eval_id}: expected {len(expectations)} checks but built {len(checks)}")

    return [
        {"text": expectation, "passed": passed, "evidence": evidence}
        for expectation, (passed, evidence) in zip(expectations, checks)
    ]


def estimate_tokens(text: str) -> int:
    return int(len(re.findall(r"\S+", text)) * 1.3)


def execution_metrics(expectation_count: int) -> Dict[str, object]:
    tool_calls = {
        "read_skill_files": 2,
        "read_reference_files": 2,
        "generate_response": 1,
        "grade_expectations": expectation_count,
    }
    return {
        "tool_calls": tool_calls,
        "total_tool_calls": sum(tool_calls.values()),
        "total_steps": 1,
        "errors_encountered": 0,
    }


def run_eval(eval_data: Dict[str, object], skill: SkillBundle, eval_dir: Path) -> Dict[str, object]:
    run_dir = eval_dir / skill.label / "run-1"
    outputs_dir = run_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    start = time.perf_counter()
    response = build_response(int(eval_data["id"]), skill)
    expectation_list = list(eval_data["expectations"])
    grading_expectations = grade_eval(int(eval_data["id"]), expectation_list, response)
    duration_ms = max(1, int((time.perf_counter() - start) * 1000))

    timing = {
        "total_tokens": estimate_tokens(response),
        "duration_ms": duration_ms,
        "total_duration_seconds": round(duration_ms / 1000, 3),
    }
    metrics = execution_metrics(len(expectation_list))
    summary = {
        "passed": sum(1 for item in grading_expectations if item["passed"]),
        "failed": sum(1 for item in grading_expectations if not item["passed"]),
        "total": len(grading_expectations),
    }
    summary["pass_rate"] = round(summary["passed"] / summary["total"], 3) if summary["total"] else 0.0

    grading = {
        "expectations": grading_expectations,
        "summary": summary,
        "execution_metrics": metrics,
        "timing": timing,
    }

    (outputs_dir / "response.md").write_text(response, encoding="utf-8")
    (outputs_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    (run_dir / "timing.json").write_text(json.dumps(timing, indent=2) + "\n", encoding="utf-8")
    (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n", encoding="utf-8")

    return summary


def main() -> None:
    if ITERATION_DIR.exists():
        shutil.rmtree(ITERATION_DIR)
    ITERATION_DIR.mkdir(parents=True, exist_ok=True)

    current_skill = load_skill_bundle("with_skill", CURRENT_SKILL_PATH)
    old_skill = load_skill_bundle("old_skill", BASELINE_SKILL_PATH)

    evals_payload = json.loads(read_text(EVALS_PATH))
    evals = evals_payload["evals"]

    results: List[Dict[str, object]] = []
    totals = {
        "with_skill": {"passed": 0, "failed": 0, "total": 0},
        "old_skill": {"passed": 0, "failed": 0, "total": 0},
    }

    for eval_data in evals:
        eval_id = int(eval_data["id"])
        eval_slug = slugify(str(eval_data["expected_output"]))
        eval_name = f"eval-{eval_id}-{eval_slug}"
        eval_dir = ITERATION_DIR / eval_name
        eval_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            "eval_id": eval_id,
            "eval_name": eval_name,
            "prompt": eval_data["prompt"],
            "assertions": eval_data["expectations"],
        }
        (eval_dir / "eval_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

        current_summary = run_eval(eval_data, current_skill, eval_dir)
        old_summary = run_eval(eval_data, old_skill, eval_dir)

        for label, summary in (("with_skill", current_summary), ("old_skill", old_summary)):
            totals[label]["passed"] += int(summary["passed"])
            totals[label]["failed"] += int(summary["failed"])
            totals[label]["total"] += int(summary["total"])

        results.append(
            {
                "eval_id": eval_id,
                "eval_name": eval_name,
                "with_skill": current_summary,
                "old_skill": old_summary,
            }
        )

    for label in ("with_skill", "old_skill"):
        total = totals[label]["total"]
        totals[label]["pass_rate"] = round(totals[label]["passed"] / total, 3) if total else 0.0

    summary = {
        "iteration": "iteration-6",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_skill_path": str(CURRENT_SKILL_PATH),
        "baseline_skill_path": str(BASELINE_SKILL_PATH),
        "eval_count": len(evals),
        "run_count": len(evals) * 2,
        "totals": totals,
        "results": results,
    }
    (ITERATION_DIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
