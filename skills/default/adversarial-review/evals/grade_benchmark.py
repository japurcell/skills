#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path

def read_text(p: Path) -> str:
    return p.read_text(errors="replace") if p.exists() else ""

def load_json(p: Path) -> dict:
    try: return json.loads(p.read_text()) if p.exists() else {}
    except Exception: return {}

def normalize(v: object) -> str:
    return " ".join(str(v).strip().lower().split())

def output_chars(d: Path) -> int:
    return sum(len(read_text(p)) for p in d.rglob("*") if p.is_file()) if d.exists() else 0

def expectation(t: str, p: bool, e: str) -> dict:
    return {"text": t, "passed": p, "evidence": e}

def build_grading(exps: list[dict], r_dir: Path) -> dict:
    passed = sum(1 for x in exps if x["passed"])
    total = len(exps)
    timing = load_json(r_dir / "timing.json")
    dur = timing.get("total_duration_seconds", 0.0)
    trans = read_text(r_dir / "transcript.md") + read_text(r_dir / "session.jsonl")
    return {
        "expectations": exps,
        "summary": {
            "passed": passed, "failed": total - passed, "total": total,
            "pass_rate": round(passed / total, 2) if total else 0.0,
        },
        "execution_metrics": {
            "tool_calls": {}, "total_tool_calls": 0, "total_steps": 0, "errors_encountered": 0,
            "output_chars": output_chars(r_dir / "outputs"), "transcript_chars": len(trans),
        },
        "timing": {
            "executor_duration_seconds": dur, "grader_duration_seconds": 0.0, "total_duration_seconds": dur,
        },
        "claims": [],
        "user_notes_summary": {"uncertainties": [], "needs_review": [], "workarounds": []},
        "eval_feedback": {"suggestions": [], "overall": "No evaluator suggestions."},
    }

def eval_id_for(d: Path) -> int | None:
    mid = load_json(d / "eval_metadata.json").get("eval_id")
    if mid is not None:
        try: return int(mid)
        except Exception: pass
    m = re.match(r"eval-(\d+)", d.name)
    return int(m.group(1)) if m else None

def load_out(d: Path, f: str) -> tuple[str, dict]:
    p = d / "outputs" / f
    return read_text(p), load_json(p)

def grade(eid: int, r_dir: Path) -> list[dict]:
    if eid == 0:
        txt, p = load_out(r_dir, "review_plan.json")
        agent, tier, strg = normalize(p.get("agent_type", "")), normalize(p.get("tier", "")), normalize(p.get("adversarial_prompt_strength", ""))
        return [
            expectation("The JSON key 'load_router' is true.", p.get("load_router") is True, txt),
            expectation("The agent_type is review-focused (e.g. 'addy-security-auditor' or 'code-reviewer').", any(x in agent for x in ["reviewer", "security", "auditor"]), txt),
            expectation("The routing tier is 'Premium'.", tier == "premium", txt),
            expectation("The adversarial prompt strength is high/brutal.", any(x in strg for x in ["high", "brutal", "adversarial"]), txt),
        ]
    if eid == 1:
        txt, p = load_out(r_dir, "review_plan.json")
        prompt = normalize(p.get("adversarial_prompt", ""))
        return [
            expectation("The JSON key 'red_flag_detected' is true.", p.get("red_flag_detected") is True, txt),
            expectation("The adversarial prompt is non-empty.", bool(prompt), txt),
            expectation("The prompt requests an audit or critical examination of edge cases/failure conditions.", any(x in prompt for x in ["audit", "critique", "break", "migration", "fail", "edge", "error"]), txt),
        ]
    if eid == 2:
        txt, d = load_out(r_dir, "decision.json")
        reason = normalize(d.get("reason", ""))
        return [
            expectation("The decision sets 'should_review' to false.", d.get("should_review") is False, txt),
            expectation("The reason explains that the change is trivial or non-functional.", any(x in reason for x in ["trivial", "typo", "doc", "comment", "receive"]), txt),
        ]
    return [expectation(f"Unknown eval id {eid}.", False, f"Unsupported: {eid}")]

def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 grade_benchmark.py <iteration-dir>")
        return 1
    idir = Path(sys.argv[1]).resolve()
    if not idir.exists():
        return 1
    for edir in sorted(p for p in idir.iterdir() if p.is_dir() and p.name.startswith("eval-")):
        eid = eval_id_for(edir)
        if eid is None: continue
        for cdir in sorted(p for p in edir.iterdir() if p.is_dir()):
            for rdir in sorted(p for p in cdir.iterdir() if p.is_dir() and p.name.startswith("run-")):
                grading = build_grading(grade(eid, rdir), rdir)
                (rdir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")
    print(f"Wrote grading.json files in {idir}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
