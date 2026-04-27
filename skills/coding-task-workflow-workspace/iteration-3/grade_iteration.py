#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text() if path.exists() else ""


def contains_all(text: str, *needles: str) -> bool:
    lowered = text.lower()
    return all(needle.lower() in lowered for needle in needles)


def add(expectations: list[dict], text: str, passed: bool, evidence: str) -> None:
    expectations.append({"text": text, "passed": passed, "evidence": evidence})


def build_expectations(eval_id: int, response_text: str) -> list[dict]:
    lowered = response_text.lower()
    expectations: list[dict] = []

    if eval_id == 5:
        add(expectations, "Places the exploration summary in the `phase:exploration` issue body", contains_all(lowered, 'phase:exploration', 'issue body'), "Matched `phase:exploration` + `issue body`" if contains_all(lowered, 'phase:exploration', 'issue body') else "Missing clear `phase:exploration` issue-body placement")
        add(expectations, "Places `files.csv` in an artifact subissue under the Phase 3 issue", 'files.csv' in lowered and ('artifact subissue' in lowered or 'artifact issue' in lowered) and ('phase 3' in lowered or 'exploration issue' in lowered), "Matched files.csv + artifact subissue + exploration context" if ('files.csv' in lowered and ('artifact subissue' in lowered or 'artifact issue' in lowered) and ('phase 3' in lowered or 'exploration issue' in lowered)) else "Missing clear files.csv artifact-subissue placement")
        open_questions_ok = ('open-questions' in lowered or 'open questions' in lowered) and 'artifact' in lowered and any(token in lowered for token in ['rather than', 'instead of', 'not local', 'not `02-exploration/open-questions.md`'])
        add(expectations, "Places open questions in a durable GitHub artifact issue rather than `02-exploration/open-questions.md`", open_questions_ok, "Matched open-questions artifact phrasing with explicit non-local contrast" if open_questions_ok else "Missing clear open-questions artifact placement or explicit non-local contrast")
        resume_ok = (
            'github' in lowered
            and any(token in lowered for token in ['resume', 'durable resume source', 'durable resume'])
            and any(
                token in lowered
                for token in [
                    'without local',
                    'without local files',
                    'without `.coding-workflow/work/',
                    'do not use `02-exploration/',
                    'do not use 02-exploration',
                    'do not use local',
                ]
            )
        )
        add(expectations, "Makes clear that these artifacts exist in GitHub so another agent can resume without local files", resume_ok, "Matched GitHub-backed resume without local files" if resume_ok else "Missing GitHub-only resume explanation")

    elif eval_id == 6:
        approval_ok = 'approval' in lowered and 'comment' in lowered and 'plan issue' in lowered
        add(expectations, "Records Gate D approval as an explicit comment on the Phase 6 plan issue", approval_ok, "Matched approval comment on the plan issue" if approval_ok else "Missing explicit plan-issue approval comment")
        closed_ok = 'plan issue' in lowered and 'close' in lowered
        add(expectations, "Says the plan issue is closed after approval", closed_ok, "Matched plan issue closure after approval" if closed_ok else "Missing explicit plan issue closure")
        task_graph_ok = ('task graph' in lowered or 'phase 7' in lowered) and 'issue body' in lowered and 'yaml' in lowered and any(token in lowered for token in ['rather than', 'instead of', 'no longer writes', 'not stored as'])
        add(expectations, "Stores the Phase 7 task graph in the issue body as YAML rather than a physical `06-task-graph.yaml` file", task_graph_ok, "Matched task-graph YAML in issue body with explicit file replacement" if task_graph_ok else "Missing clear task-graph issue-body/YAML replacement")
        impl_ok = ('comments on task issues' in lowered or ('task issue' in lowered and 'comment' in lowered)) and '07-implementation-log.md' in response_text
        add(expectations, "Stores implementation progress as comments on task issues instead of `07-implementation-log.md`", impl_ok, "Matched task-issue comments instead of 07-implementation-log.md" if impl_ok else "Missing clear task-issue comment based implementation log")

    elif eval_id == 8:
        retry_cap_mentioned = 'retry cap' in lowered or 'retry-cap' in lowered
        jitter_mentioned = 'jitter' in lowered
        issue_count_mentioned = (
            'exactly two' in lowered
            or 'two implementation task issues' in lowered
            or 'two task issues' in lowered
        )
        task_graph_parent_mentioned = 'task-graph issue' in lowered or 'phase 7 task-graph issue' in lowered
        one_per_behavior_mentioned = (
            'one per behavior' in lowered
            or 'one per vertical slice' in lowered
            or 'one task issue per slice' in lowered
            or ('one vertical-slice issue' in lowered and 'retry cap' in lowered and 'jitter' in lowered)
        )
        one_issue_ok = retry_cap_mentioned and jitter_mentioned and issue_count_mentioned and task_graph_parent_mentioned and one_per_behavior_mentioned
        add(expectations, "Says there are exactly two implementation task issues under the Phase 7 task-graph issue, one per behavior or vertical slice", one_issue_ok, "Matched two-issue / task-graph-parent / one-per-behavior wording tied to retry cap and jitter" if one_issue_ok else "Missing explicit two-issue model under the task-graph issue for retry cap and jitter")
        full_slice_ok = any(
            token in lowered
            for token in [
                'owns one full vertical slice',
                'owns a full vertical slice',
                'represents one full vertical slice',
                'owns the full behavior',
                'covers the behavior end-to-end',
            ]
        ) and not any(
            token in lowered
            for token in [
                'red slice',
                'green slice',
                'refactor slice',
                'separate red issue',
                'separate green issue',
                'separate refactor issue',
            ]
        )
        add(expectations, "Explains that each task issue owns a full vertical slice rather than a single RED, GREEN, or REFACTOR stage", full_slice_ok, "Matched full-vertical-slice ownership without split-stage wording" if full_slice_ok else "Missing explicit full-slice ownership or still implies split-stage issues")
        comments_ok = ('same task issue' in lowered or 'that same issue' in lowered) and 'comment' in lowered and 'red' in lowered and 'green' in lowered and 'refactor' in lowered
        add(expectations, "Records RED, GREEN, and REFACTOR progress as comments on the same task issue", comments_ok, "Matched same-task-issue comment logging across red/green/refactor" if comments_ok else "Missing same-task-issue comment logging")
        stage_ok = '`stage`' in response_text and 'red' in lowered and any(token in lowered for token in ['updated in place', 'advance', 'moves to green', 'moves to refactor'])
        add(expectations, "Explains that the task issue `stage` field starts at `red` and is updated in place as the slice advances", stage_ok, "Matched stage starts at red and updates in place" if stage_ok else "Missing clear stage-field progression")

    elif eval_id == 9:
        files_ok = 'files.csv' in lowered and 'close' in lowered and any(token in lowered for token in ['exploration', 'file ledger', 'phase 3'])
        add(expectations, "Closes `files.csv` after the exploration file ledger is complete", files_ok, "Matched files.csv closure in exploration" if files_ok else "Missing files.csv closure rule")
        sources_ok = 'sources.md' in lowered and 'close' in lowered and any(token in lowered for token in ['research', 'source ledger', 'phase 4'])
        add(expectations, "Closes `sources.md` after the research source ledger is complete", sources_ok, "Matched sources.md closure in research" if sources_ok else "Missing sources.md closure rule")
        questions_ok = (
            ('open-questions' in lowered or 'open questions' in lowered)
            and 'close' in lowered
            and any(
                token in lowered
                for token in [
                    'while unresolved',
                    'once every entry is finalized',
                    'once every entry is resolved',
                    'research or clarification',
                    'phase 4',
                    'phase 5',
                    'once every question is finalized',
                ]
            )
        )
        add(expectations, "Keeps `open-questions` open only while unresolved questions remain and closes it once every entry is finalized", questions_ok, "Matched open-questions lifecycle across research/clarification" if questions_ok else "Missing clear open-questions closure lifecycle")
        task_graph_ok = (
            ('phase:task-graph' in lowered or 'task-graph issue' in lowered)
            and 'issue body' in lowered
            and (
                'not in a separate artifact subissue' in lowered
                or 'rather than a separate artifact subissue' in lowered
                or 'instead of a separate artifact subissue' in lowered
                or 'artifact subissue' not in lowered
            )
        )
        add(expectations, "Places the Phase 7 task graph YAML in the `phase:task-graph` issue body rather than a separate artifact subissue", task_graph_ok, "Matched task-graph issue-body placement" if task_graph_ok else "Missing clear task-graph issue-body placement")

    else:
        raise ValueError(f"Unsupported eval_id {eval_id}")

    return expectations


def write_grading(run_dir: Path, expectations: list[dict]) -> None:
    response_text = read_text(run_dir / 'outputs' / 'final.md') or read_text(run_dir / 'outputs' / 'response.md')
    passed = sum(1 for item in expectations if item['passed'])
    total = len(expectations)
    failed = total - passed
    timing = {'executor_duration_seconds': 0.0, 'grader_duration_seconds': 0.1, 'total_duration_seconds': 0.1}
    timing_file = run_dir / 'timing.json'
    if timing_file.exists():
        timing_data = json.loads(timing_file.read_text())
        exec_seconds = float(timing_data.get('total_duration_seconds', 0.0))
        timing = {
            'executor_duration_seconds': exec_seconds,
            'grader_duration_seconds': 0.1,
            'total_duration_seconds': round(exec_seconds + 0.1, 1),
        }
    grading = {
        'expectations': expectations,
        'summary': {
            'passed': passed,
            'failed': failed,
            'total': total,
            'pass_rate': round(passed / total, 2) if total else 0.0,
        },
        'execution_metrics': {
            'tool_calls': {},
            'total_tool_calls': 0,
            'total_steps': 0,
            'errors_encountered': 0,
            'output_chars': len(response_text),
            'transcript_chars': len(read_text(run_dir / 'transcript.md')),
        },
        'timing': timing,
        'claims': [],
        'user_notes_summary': {
            'uncertainties': [],
            'needs_review': [],
            'workarounds': [],
        },
        'eval_feedback': {
            'suggestions': [],
            'overall': 'Deterministic text grading against the eval expectations.',
        },
    }
    (run_dir / 'grading.json').write_text(json.dumps(grading, indent=2) + '\n')


def main() -> int:
    if len(sys.argv) != 2:
        print('Usage: grade_iteration.py <iteration-dir>')
        return 1
    iteration_dir = Path(sys.argv[1])
    for eval_dir in sorted(iteration_dir.glob('eval-*')):
        metadata = json.loads((eval_dir / 'eval_metadata.json').read_text())
        eval_id = metadata['eval_id']
        for config_dir in sorted(path for path in eval_dir.iterdir() if path.is_dir()):
            for run_dir in sorted(config_dir.glob('run-*')):
                response_text = read_text(run_dir / 'outputs' / 'final.md') or read_text(run_dir / 'outputs' / 'response.md')
                if not response_text.strip():
                    continue
                expectations = build_expectations(eval_id, response_text)
                write_grading(run_dir, expectations)
    print('Wrote grading.json for iteration')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
