#!/usr/bin/env python3

import json
import re
import sys
from collections import Counter
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(errors="replace") if path.exists() else ""


def read_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


def load_timing(run_dir: Path) -> dict:
    timing_path = run_dir / "timing.json"
    if not timing_path.exists():
        return {}
    try:
        return json.loads(timing_path.read_text())
    except json.JSONDecodeError:
        return {}


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def expectation(text: str, passed: bool, evidence: str) -> dict:
    return {"text": text, "passed": passed, "evidence": evidence}


def build_grading(expectations: list[dict], run_dir: Path) -> dict:
    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
    outputs_dir = run_dir / "outputs"
    output_chars = 0
    if outputs_dir.exists():
        for path in outputs_dir.rglob("*"):
            if path.is_file():
                output_chars += len(read_text(path))
    transcript = read_text(run_dir / "transcript.md") + read_text(run_dir / "session.jsonl")
    timing = load_timing(run_dir)
    duration_seconds = timing.get("total_duration_seconds", 0.0)
    return {
        "expectations": expectations,
        "summary": {
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "pass_rate": round(passed / total, 2) if total else 0.0,
        },
        "execution_metrics": {
            "tool_calls": {},
            "total_tool_calls": 0,
            "total_steps": 0,
            "errors_encountered": 0,
            "output_chars": output_chars,
            "transcript_chars": len(transcript),
        },
        "timing": {
            "executor_duration_seconds": duration_seconds,
            "grader_duration_seconds": 0.0,
            "total_duration_seconds": duration_seconds,
        },
        "claims": [],
        "user_notes_summary": {
            "uncertainties": [],
            "needs_review": [],
            "workarounds": [],
        },
        "eval_feedback": {
            "suggestions": [],
            "overall": "No evaluator suggestions.",
        },
    }


def eval_id_for(eval_dir: Path) -> int | None:
    metadata_path = eval_dir / "eval_metadata.json"
    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text())
            if "eval_id" in metadata:
                return int(metadata["eval_id"])
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
    match = re.match(r"eval-(\d+)", eval_dir.name)
    if match:
        return int(match.group(1))
    return None


def find_output(run_dir: Path) -> tuple[Path | None, Path | None]:
    candidates = [
        run_dir / "outputs" / "prd.json",
        run_dir / "outputs" / "generated" / "prd.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate, run_dir / "outputs" / "summary.md"
    return None, run_dir / "outputs" / "summary.md"


def load_stories(run_dir: Path):
    prd_path, summary_path = find_output(run_dir)
    data = read_json(prd_path) if prd_path else None
    stories = data.get("userStories", []) if isinstance(data, dict) else []
    return prd_path, summary_path, data, stories


def story_blob(story: dict) -> str:
    return normalize(json.dumps(story, sort_keys=True))


def story_content(story: dict) -> str:
    parts = [
        str(story.get("title", "")),
        str(story.get("description", "")),
        " ".join(str(item) for item in story.get("acceptanceCriteria", [])),
        " ".join(str(item) for item in story.get("filesLikelyTouched", [])),
    ]
    return normalize(" ".join(parts))


def story_titles(stories: list[dict]) -> list[str]:
    return [normalize(str(story.get("title", ""))) for story in stories]


def priorities_ascending(stories: list[dict]) -> bool:
    priorities = [story.get("priority") for story in stories]
    return (
        bool(stories)
        and all(isinstance(priority, int) for priority in priorities)
        and priorities == sorted(priorities)
        and len(set(priorities)) == len(priorities)
    )


def sequential_ids(stories: list[dict]) -> bool:
    expected = [f"US-{index:03d}" for index in range(1, len(stories) + 1)]
    actual = [story.get("id") for story in stories]
    return actual == expected


def id_to_story(stories: list[dict]) -> dict[str, dict]:
    mapping: dict[str, dict] = {}
    for story in stories:
        story_id = story.get("id")
        if isinstance(story_id, str):
            mapping[story_id] = story
    return mapping


def dependency_fields_present(stories: list[dict]) -> bool:
    return bool(stories) and all(
        isinstance(story.get("dependsOn"), list)
        and all(isinstance(dep, str) for dep in story.get("dependsOn", []))
        and isinstance(story.get("parallelBatch"), int)
        and story.get("parallelBatch", 0) > 0
        for story in stories
    )


def dependency_graph_valid(stories: list[dict]) -> bool:
    if not dependency_fields_present(stories):
        return False
    story_index = {
        story.get("id"): index
        for index, story in enumerate(stories)
        if isinstance(story.get("id"), str)
    }
    if len(story_index) != len(stories):
        return False
    for index, story in enumerate(stories):
        depends_on = story.get("dependsOn", [])
        if len(depends_on) != len(set(depends_on)):
            return False
        for dep in depends_on:
            dep_index = story_index.get(dep)
            if dep_index is None or dep_index >= index:
                return False
    return True


def parallel_batches_dense(stories: list[dict]) -> bool:
    if not dependency_fields_present(stories):
        return False
    batches = [story.get("parallelBatch") for story in stories]
    return sorted(set(batches)) == list(range(1, max(batches) + 1))


def batches_follow_dependencies(stories: list[dict]) -> bool:
    if not dependency_graph_valid(stories):
        return False
    story_map = id_to_story(stories)
    for story in stories:
        batch = story.get("parallelBatch")
        depends_on = story.get("dependsOn", [])
        if not depends_on:
            if batch != 1:
                return False
            continue
        max_dep_batch = max(story_map[dep]["parallelBatch"] for dep in depends_on)
        if batch <= max_dep_batch:
            return False
    return True


def priorities_follow_batches(stories: list[dict]) -> bool:
    if not priorities_ascending(stories) or not dependency_fields_present(stories):
        return False
    priority_sorted = sorted(stories, key=lambda story: story["priority"])
    batches = [story["parallelBatch"] for story in priority_sorted]
    return batches == sorted(batches)


def has_parallel_batch(stories: list[dict], minimum_size: int = 2) -> bool:
    if not dependency_fields_present(stories):
        return False
    counts = Counter(story["parallelBatch"] for story in stories)
    return any(count >= minimum_size for count in counts.values())


def all_story_defaults(stories: list[dict]) -> bool:
    return bool(stories) and all(
        story.get("passes") is False
        and story.get("notes") == ""
        and "Typecheck passes" in story.get("acceptanceCriteria", [])
        for story in stories
    )


def any_story_matches(stories: list[dict], include_terms: list[str]) -> bool:
    return any(all(term in story_blob(story) for term in include_terms) for story in stories)


def any_story_has_terms(stories: list[dict], required: list[str], any_of: tuple[str, ...] = ()) -> bool:
    for story in stories:
        blob = story_blob(story)
        if all(term in blob for term in required) and (not any_of or any(term in blob for term in any_of)):
            return True
    return False


def first_story_matching(stories: list[dict], required: list[str], any_of: tuple[str, ...] = ()) -> dict | None:
    for story in stories:
        blob = story_blob(story)
        if all(term in blob for term in required) and (not any_of or any(term in blob for term in any_of)):
            return story
    return None


def ui_story_has_browser_check(stories: list[dict]) -> bool:
    ui_terms = ("badge", "list", "filter", "dropdown", "control", "modal", "form", "page", "card", "row", "button", "table")
    ui_candidates = [story for story in stories if any(term in story_content(story) for term in ui_terms)]
    return bool(ui_candidates) and all(
        "Verify in browser using playwright-cli skill" in story.get("acceptanceCriteria", [])
        for story in ui_candidates
    )


def backend_only_no_ui(stories: list[dict]) -> bool:
    ui_terms = ("badge", "list", "filter", "dropdown", "control", "modal", "form", "page", "card", "row", "button", "table", "browser")
    return bool(stories) and all(
        not any(term in story_content(story) for term in ui_terms)
        and "Verify in browser using playwright-cli skill" not in story.get("acceptanceCriteria", [])
        for story in stories
    )


def no_horizontal_titles(stories: list[dict]) -> bool:
    banned = (
        "build backend",
        "build frontend",
        "implement the feature",
        "implement notification center",
        "implement workspace member management",
        "implement personal access token backend",
    )
    return not any(any(item in title for item in banned) for title in story_titles(stories))


def dependency_and_batch_shape(stories: list[dict]) -> bool:
    return (
        dependency_fields_present(stories)
        and dependency_graph_valid(stories)
        and parallel_batches_dense(stories)
        and batches_follow_dependencies(stories)
        and priorities_follow_batches(stories)
    )


def grade_eval_0(run_dir: Path) -> list[dict]:
    prd_path, _, data, stories = load_stories(run_dir)
    output_text = read_text(prd_path) if prd_path else "missing outputs/prd.json"
    return [
        expectation(
            "The output is valid prd.json with at least 5 user stories.",
            bool(isinstance(data, dict) and len(stories) >= 5),
            output_text,
        ),
        expectation(
            "The stories separately cover status storage, backend status updates, badge display, status controls, and filtering.",
            any_story_has_terms(stories, ["status"], ("schema", "migration", "storage", "persist"))
            and any_story_has_terms(stories, ["status"], ("update", "action", "endpoint", "server"))
            and any_story_matches(stories, ["badge"])
            and any_story_has_terms(stories, ["status"], ("control", "dropdown", "select", "inline"))
            and any_story_matches(stories, ["filter"]),
            output_text,
        ),
        expectation(
            "Every story includes dependsOn, parallelBatch, passes=false, notes=\"\", and Typecheck passes.",
            dependency_fields_present(stories) and all_story_defaults(stories),
            output_text,
        ),
        expectation(
            "Dependencies point backward, batches are dense, and at least one batch contains parallel-safe stories.",
            dependency_and_batch_shape(stories) and has_parallel_batch(stories),
            output_text,
        ),
        expectation(
            "UI stories include Verify in browser using playwright-cli skill.",
            ui_story_has_browser_check(stories),
            output_text,
        ),
    ]


def grade_eval_1(run_dir: Path) -> list[dict]:
    prd_path, _, data, stories = load_stories(run_dir)
    output_text = read_text(prd_path) if prd_path else "missing outputs/generated/prd.json"
    branch_name = data.get("branchName") if isinstance(data, dict) else None
    return [
        expectation(
            "The output is saved to outputs/generated/prd.json.",
            prd_path is not None and prd_path.as_posix().endswith("outputs/generated/prd.json"),
            prd_path.as_posix() if prd_path else output_text,
        ),
        expectation(
            "branchName is derived from the feature title.",
            branch_name == "workspace-member-management",
            json.dumps(data, indent=2) if isinstance(data, dict) else output_text,
        ),
        expectation(
            "The stories separately cover invite, role change, revoke access, and audit-log or audit-view work.",
            any_story_matches(stories, ["invite"])
            and any_story_matches(stories, ["role"])
            and any_story_matches(stories, ["revoke"])
            and any(any_story_matches(stories, [term]) for term in ("audit", "audit log", "audit view")),
            output_text,
        ),
        expectation(
            "Dependencies point backward, batches are dense, and at least one batch contains parallel-safe stories.",
            dependency_and_batch_shape(stories) and has_parallel_batch(stories),
            output_text,
        ),
        expectation(
            "No story title is a horizontal layer split such as build backend or build frontend.",
            no_horizontal_titles(stories),
            output_text,
        ),
    ]


def grade_eval_2(run_dir: Path) -> list[dict]:
    prd_path, _, data, stories = load_stories(run_dir)
    output_text = read_text(prd_path) if prd_path else "missing outputs/prd.json"
    return [
        expectation(
            "The output is valid prd.json with multiple user stories.",
            bool(isinstance(data, dict) and len(stories) >= 4),
            output_text,
        ),
        expectation(
            "The stories separately cover persistence, badge or list UI, read-state updates, filtering, and clearing read notifications.",
            any_story_matches(stories, ["persist"])
            and (any_story_matches(stories, ["badge"]) or any_story_matches(stories, ["list"]))
            and any(any_story_matches(stories, [term]) for term in ("read state", "mark", "read", "unread"))
            and any_story_matches(stories, ["filter"])
            and any_story_matches(stories, ["clear"]),
            output_text,
        ),
        expectation(
            "The output does not collapse the feature into one umbrella implementation story.",
            no_horizontal_titles(stories) and len(stories) > 1,
            output_text,
        ),
        expectation(
            "Each story has sequential IDs, ascending priorities, valid dependsOn fields, and valid parallelBatch values.",
            sequential_ids(stories) and dependency_and_batch_shape(stories),
            output_text,
        ),
    ]


def grade_eval_3(run_dir: Path) -> list[dict]:
    prd_path, _, data, stories = load_stories(run_dir)
    output_text = read_text(prd_path) if prd_path else "missing outputs/prd.json"
    storage_story = first_story_matching(stories, ["token"], ("storage", "hash", "revoked"))
    create_story = first_story_matching(stories, ["token"], ("create", "issue", "generate"))
    revoke_story = first_story_matching(stories, ["token"], ("revoke", "revoked"))
    create_revoke_parallel = bool(
        storage_story
        and create_story
        and revoke_story
        and create_story["parallelBatch"] == revoke_story["parallelBatch"]
        and create_story["parallelBatch"] > storage_story["parallelBatch"]
    )
    return [
        expectation(
            "The output contains exactly 3 user stories and does not invent UI stories or browser verification.",
            bool(isinstance(data, dict) and len(stories) == 3 and backend_only_no_ui(stories)),
            output_text,
        ),
        expectation(
            "The stories separately cover token storage, create token, and revoke token work.",
            bool(storage_story and create_story and revoke_story),
            output_text,
        ),
        expectation(
            "Every story includes dependsOn, parallelBatch, passes=false, notes=\"\", and Typecheck passes.",
            dependency_fields_present(stories) and all_story_defaults(stories),
            output_text,
        ),
        expectation(
            "The create-token and revoke-token stories share a later parallel batch after the storage story.",
            dependency_and_batch_shape(stories) and create_revoke_parallel,
            output_text,
        ),
    ]


def grade(eval_id: int, run_dir: Path) -> list[dict]:
    if eval_id == 0:
        return grade_eval_0(run_dir)
    if eval_id == 1:
        return grade_eval_1(run_dir)
    if eval_id == 2:
        return grade_eval_2(run_dir)
    if eval_id == 3:
        return grade_eval_3(run_dir)
    return [expectation(f"Unknown eval id {eval_id}.", False, "Unsupported eval")]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 skills/prd-to-tasks/evals/grade_benchmark.py skills/prd-to-tasks-workspace/<iteration-dir>")
        return 1

    iteration_dir = Path(sys.argv[1]).resolve()
    if not iteration_dir.exists():
        print(f"Iteration directory not found: {iteration_dir}")
        return 1

    for eval_dir in sorted(iteration_dir.glob("eval-*")):
        eval_id = eval_id_for(eval_dir)
        if eval_id is None:
            print(f"Skipping {eval_dir}: could not determine eval id")
            continue
        for config_dir in sorted(path for path in eval_dir.iterdir() if path.is_dir()):
            for run_dir in sorted(config_dir.glob("run-*")):
                grading = build_grading(grade(eval_id, run_dir), run_dir)
                (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")

    print(f"Wrote grading.json files in {iteration_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
