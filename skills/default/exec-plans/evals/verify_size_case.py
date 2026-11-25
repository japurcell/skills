"""Verify the saved plan for one Atlas size fixture. See size-checkpoints.md."""

import argparse
from collections import Counter
import json
from pathlib import Path
import re
from urllib.parse import unquote

from grade_benchmark import find_block, heading_blocks
from prepare_size_case import CASES


LINK = re.compile(r"\[([^]\n]+)\]\(([^)\n]+)\)")
HEADING = re.compile(r"^(#{1,6})[ \t]+(.+)$", re.MULTILINE)
HISTORY = re.compile(r"^#{1,6}[ \t]+.*(?:histor(?:y|ical)|archiv).*$", re.I | re.M)
ROW = re.compile(
    r"^[ \t]*[-*+] +(?P<task>T\d{3})\s*\((?P<state>[^,\n]+),\s*(?P<owner>[^)\n]+)\):\s*"
    r"verify row (?P<number>\d+) is (?P<label>[^;\n]+);\s*prerequisite\s*:?\s*(?P<parent>T\d{3})[.;]\s*"
    r"(?P<stop>[^.\n]+)\.?[ \t]*$", re.M | re.I,
)


def plain(text):
    """Keep the visible values of Markdown fields, irrespective of inline markup."""
    return re.sub(r"\*\*|__|`", "", LINK.sub(r"\1", text))


def task_fields(row):
    # Wording and Markdown presentation may vary. The catalog label is case-sensitive.
    return (row["task"].upper(), row["state"].strip().casefold(), row["owner"].strip().casefold(),
            int(row["number"]), row["label"].strip(), row["parent"].upper(), row["stop"].strip().casefold())


def closed_milestones(text):
    progress = (find_block(text, ("progress",)) or {}).get("body", "")
    if re.search(r"^\s*[-*+] +\[ \]", progress, re.M):
        return False
    for number, task in [(1, r"\bD1\b|catalog"), (2, r"\bT001\b|first[- ](?:row|label)")]:
        blocks = [b["body"] for b in heading_blocks(text) if re.match(rf"Milestone\s+{number}\b", b["title"], re.I)]
        if len(blocks) != 1:
            return False
        metadata = re.split(r"^#", plain(blocks[0]), maxsplit=1, flags=re.M)[0].lower()
        for field, expected in [("status", "done"), ("acceptance", "met")]:
            states = re.findall(rf"^[ \t]*{field}:[ \t]*([^\n]+)", metadata, re.M)
            if {s.strip() for s in states} != {expected}:
                return False
        entries = [line for line in plain(progress).splitlines()
                   if re.match(r"^\s*[-*+] +\[[xX]\]", line) and f"[milestone-{number}]" in line.lower()]
        if not any(re.search(task, line, re.I) for line in entries):
            return False
    return True


def conflicts_with_assignment(action):
    """The fixture gives Mara one ready task, irrespective of how many times the entry mentions it."""
    for clause in re.split(r"[.!?;\n]", plain(action)):
        if re.search(r"\bMara is blocked\b", clause, re.I) and not re.search(r"\bif\b", clause, re.I):
            return True
        claim = re.search(r"\bnext\s+(?:authorized\s+)?(?:action|task|assignment|step)\b", clause, re.I)
        if claim:
            owner = re.search(r"\b(\w+)['’]s\s*$", clause[:claim.start()])
            task = re.search(r"\bT\d{3}\b", clause[claim.end():])
            if (owner and owner[1].casefold() != "mara") or (task and task[0] != "T001"):
                return True
    return False


def section(text, fragment):
    if not fragment:
        return text
    headings = list(HEADING.finditer(text))
    for i, header in enumerate(headings):
        slug = re.sub(r"[^\w -]", "", header[2].lower()).replace(" ", "-")
        if slug == fragment:
            end = next((h.start() for h in headings[i + 1:] if len(h[1]) <= len(header[1])), len(text))
            return text[header.start():end]
    return ""


def active_text(text):
    """Remove historical sections without discarding subsequent active headings."""
    for title in HISTORY.findall(text):
        fragment = re.sub(r"[^\w -]", "", title.lstrip("# ").lower()).replace(" ", "-")
        historical = section(text, fragment)
        if historical:
            text = text.replace(historical, "", 1)
    return text


def target(path, href):
    name, _, fragment = unquote(href.strip("<>")).partition("#")
    return ((path.parent / name).resolve() if name else path), fragment


class Plan:
    def __init__(self, root):
        self.entry = root.resolve() / "AtlasPlan.md"
        self.docs = {}
        self.active = set()
        self.broken = []
        # A historical link can reach a page before its active link does.
        pending = [(self.entry, True)]
        visited = set()
        while pending:
            path, active = pending.pop()
            if (path, active) in visited:
                continue
            visited.add((path, active))
            if not path.is_file() or not path.is_relative_to(self.entry.parent):
                self.broken.append(str(path))
                continue
            if active:
                self.active.add(path)
            text = path.read_text(encoding="utf-8")
            self.docs[path] = text
            active_links = set(LINK.findall(active_text(text))) if active else set()
            for label, href in LINK.findall(text):
                linked, fragment = target(path, href)
                if not linked.is_relative_to(self.entry.parent) or not linked.is_file():
                    self.broken.append(f"{path.name}: {href}")
                    continue
                if linked.suffix == ".md":
                    if fragment and not section(linked.read_text(encoding="utf-8"), fragment):
                        self.broken.append(f"{path.name}: {href}")
                    pending.append((linked, (label, href) in active_links))

    def worker_path(self):
        """Follow only direct assignment links and its cited prerequisite sections."""
        entry = active_text(self.docs.get(self.entry, ""))
        blocks = re.split(r"\n(?=#{1,6} )", entry)
        action = "\n".join(block for block in blocks if re.search(
            r"^#+ (?:Concrete Steps|Next\b)|\b(?:Mara.{0,35}(?:next|owns|runs)|next.{0,35}Mara)\b", block, re.I))
        if conflicts_with_assignment(entry):
            return "", None, {}
        for label, href in LINK.findall(action or entry):
            path, fragment = target(self.entry, href)
            if path not in self.active or path == self.entry:
                continue
            assignment = section(active_text(self.docs[path]), fragment)
            title = assignment.splitlines()[0] if assignment else ""
            if not re.search(r"\bT001\b|first[- ]label|assignment", f"{label} {title}", re.I) and not (
                "Mara" in assignment and "head -n 1 labels.txt" in assignment
            ):
                continue
            decisions = {}
            for line in assignment.splitlines():
                for citation, url in LINK.findall(line):
                    if not re.search(r"\bD1\b|prerequisite|catalog encoding", citation + " " + line, re.I):
                        continue
                    decision_path, anchor = target(path, url)
                    if decision_path not in self.active:
                        continue
                    decision = section(active_text(self.docs[decision_path]), anchor)
                    if all(fact in decision for fact in ("D1", "UTF-8", "ATLAS-7104")):
                        decisions[decision_path] = decision
            if decisions:
                return assignment, path, decisions
        return "", None, {}


def summary_errors(plan, path, text, rows):
    """Check explicit edge claims in a task page against its individual rows."""
    prerequisites = {row["task"]: row["parent"] for row in rows}
    first = rows[0]["task"]
    prose = ROW.sub("", plain(text))
    errors = []
    for sentence in re.split(r"[.!?\n]+", prose):
        if not re.search(r"prerequisite|depend", sentence, re.I) or not re.search(r"\bT\d{3}\b", sentence):
            continue
        ids = re.findall(r"\bT\d{3}\b", sentence)
        first_claim = re.search(r"first\b[^.]*?prerequisite\b[^.]*?\b(T\d{3})\b", sentence, re.I)
        if first_claim:
            correct = first_claim[1] == prerequisites[first]
        elif re.search(r"depend(?:s)? on", sentence, re.I) and len(ids) >= 2:
            correct = all(prerequisites.get(task) == ids[-1] for task in ids[:-1])
        elif re.search(r"prerequisite is in", sentence, re.I) and len(ids) == 1:
            correct = ids[0] in prerequisites.values()
        else:
            # Preserve an unfamiliar assertion for evidence review, rather than certifying it.
            correct = False
        if not correct:
            errors.append(sentence.strip())
    # A correct task ID can still point to a page or fragment containing a different task.
    for line in text.splitlines():
        if not re.search(r"prerequisite|depend", line, re.I):
            continue
        location = re.search(r"\b(T\d{3}) prerequisite is in\s+(?:the\s+)?\[([^]]+)\]", line, re.I)
        for label, url in LINK.findall(line):
            task = label if re.fullmatch(r"T\d{3}", label) else None
            if location and location[2] == label:
                task = location[1]
            if task:
                linked, anchor = target(path, url)
                cited = section(active_text(plan.docs.get(linked, "")), anchor) if linked in plan.active else ""
                cited = plain(cited)
                if not (any(row["task"] == task for row in ROW.finditer(cited)) or
                        re.search(rf"^#+ (?:task )?{task}(?=[: ]|$)", cited, re.I | re.M)):
                    errors.append(f"{task} has no assignment or index record at {url}")
    return errors


def record_counts(plan):
    """Compare content, including duplicates added to an existing assignment or archive."""
    files = [plan.entry, *(plan.entry.parent / "AtlasPlan").rglob("*.md")]
    counts = Counter()
    for path in files:
        for line in path.read_text(encoding="utf-8").splitlines():
            if re.match(r"^#+ .*\bT001\b", line, re.I):
                counts["T001 assignment headings"] += 1
            # An index link to an existing receipt is not a second historical record.
            if "HIST-194C" in line and not LINK.search(line):
                counts["HIST-194C receipt records"] += line.count("HIST-194C")
            if len(line.strip()) > 30:
                counts[" ".join(line.split()).casefold()] += 1
    return counts


def verify(case, initial, run, previous):
    plan = Plan(run)
    entry = plan.docs.get(plan.entry, "")
    failures = {}
    checks = []

    def check(name, passed, evidence=""):
        checks.append(name)
        if not passed:
            failures[name] = evidence

    check("Saved entry", bool(entry))
    check("All linked files and fragments resolve", not plan.broken, plan.broken)
    protected = ["DormantPlan.md", "labels.txt"] + (["release.txt"] if case == "close-only" else [])
    check("Unrelated plan and product inputs preserved", all(
        (run / f).is_file() and (run / f).read_bytes() == (initial / f).read_bytes() for f in protected))
    check("Retained historical and catalog receipts", all(
        any(receipt in text for text in plan.docs.values()) for receipt in ["HIST-194C", "ATLAS-7104"]))
    if case == "create-exact":
        check("Exact-boundary publication remains a single identical file",
              (initial / "draft.md").stat().st_size == 12288 and bool(entry) and
              plan.entry.read_bytes() == (initial / "draft.md").read_bytes() and not (run / "AtlasPlan").exists())
    elif case == "close-only":
        active = active_text(entry)
        check("Closed in place with completed milestones and acceptance evidence",
              not (run / "AtlasPlan").exists() and closed_milestones(active)
              and all(s in active for s in ("CLOSE-7104", "Mara", "Jo", "café-001")))
    else:
        pages = {p for p in plan.active if p.is_relative_to(run.resolve() / "AtlasPlan")}
        oversized = {str(p.relative_to(plan.entry.parent)): p.stat().st_size for p in plan.active if p.stat().st_size > 12288}
        check("Split at original entry with bounded routine pages", bool(pages) and not oversized, oversized)
        task, task_path, decisions = plan.worker_path()
        worker = "\n".join([active_text(entry), task, *decisions.values()])
        evidence = str(task_path.relative_to(plan.entry.parent)) if task_path else "No linked assignment with D1"
        check("Worker path identifies owner, action, expected label and stopping point",
              bool(task) and "Mara" in active_text(entry) and
              all(s in worker for s in ("head -n 1 labels.txt", "café-001", "record", "stop")), evidence)
        check("Assignment cites the current D1 decision and receipt", bool(decisions), evidence)
        progress = [line for p in plan.active for line in active_text(plan.docs[p]).splitlines()
                    if re.search(r"^\s*[-*] \[[ xX]\]", line) and re.search(r"\bT001\b|first[- ](?:label|row)", line, re.I)]
        check("First label task remains pending", bool(progress) and all("[ ]" in line for line in progress), progress)
        if case in ("resume-over", "repeat"):
            check("D1 heading moved from entry to a cited milestone", not section(entry, "catalog-encoding")
                  and any(p in pages and "milestone" in plan.docs[p].lower() for p in decisions))
        if case == "large-index":
            original = (initial / "AtlasPlan.md").read_text(encoding="utf-8")
            expected = Counter(task_fields(m) for m in ROW.finditer(plain(original)))
            found = Counter()
            summaries = []
            malformed = []
            for path in plan.active:
                text = active_text(plan.docs[path])
                visible = plain(text)
                rows = list(ROW.finditer(visible))
                found.update(task_fields(row) for row in rows)
                if rows:
                    malformed.extend(line for line in visible.splitlines()
                                     if re.match(r"^\s*[-*+] +T\d{3}\s*\(", line) and not ROW.fullmatch(line))
                    summaries.extend(f"{path.name}: {s}" for s in summary_errors(plan, path, text, rows))
            check("Every task record and edge preserved once", len(expected) == 191 and expected == found and not malformed,
                  {"missing": list((expected - found).elements()), "extra": list((found - expected).elements()),
                   "malformed": malformed})
            check("Page prerequisite summaries agree with their records", not summaries, summaries)
        if case == "repeat":
            before = record_counts(Plan(previous))
            after = record_counts(plan)
            duplicates = [record[:90] for record, count in after.items()
                          if count > max(1, before[record])]
            check("No duplicate assignment or historical records", not duplicates, duplicates)
    return {"case": case, "checks": checks, "failures": failures}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=(*CASES, "repeat"))
    parser.add_argument("initial", type=Path, help="pristine fixture used in the run")
    parser.add_argument("run", type=Path, help="finished workspace to verify")
    parser.add_argument("--previous", type=Path, help="saved first resumed checkpoint (required for repeat)")
    args = parser.parse_args()
    if args.case == "repeat" and (not args.previous or not (args.previous / "AtlasPlan.md").is_file()):
        parser.error("repeat requires --previous pointing to the first saved checkpoint")
    try:
        result = verify(args.case, args.initial, args.run, args.previous)
    except (OSError, UnicodeError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return bool(result["failures"])


if __name__ == "__main__":
    raise SystemExit(main())
