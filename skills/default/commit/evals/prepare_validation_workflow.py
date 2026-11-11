#!/usr/bin/env python3
"""Prepare an isolated, observed commit-skill evaluation (Python 3 and Git)."""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def prepare(run, skill, fixture_path=None):
    run.mkdir(parents=True, exist_ok=False)
    copied = run / "skill"
    copied.mkdir()
    shutil.copy2(skill / "SKILL.md", copied / "SKILL.md")
    for name in ("scripts", "references"):
        shutil.copytree(skill / name, copied / name)
    (run / "outputs").mkdir()
    events = run / "events.jsonl"
    events.touch()
    fixture = json.loads((fixture_path or Path(__file__).parent / "files/validation-before-commit/input.json").read_text())
    if (not isinstance(fixture, dict)
            or any(not isinstance(fixture.get(key), str) for key in ("before", "after", "draft"))):
        raise ValueError("workflow fixture needs string before, after, and draft fields")
    expected_coauthors = fixture.get("expected_coauthors", [])
    if (not isinstance(expected_coauthors, list)
            or any(not isinstance(author, str) or not author.strip() for author in expected_coauthors)
            or len(set(expected_coauthors)) != len(expected_coauthors)):
        raise ValueError("workflow fixture expected_coauthors must be unique nonempty identity strings")
    agent_edits = fixture.get("agent_edits", False)
    if type(agent_edits) is not bool:
        raise ValueError("workflow fixture agent_edits must be a boolean")
    policy_file = fixture.get("policy_file")
    repository_policy = fixture.get("repository_policy")
    if repository_policy is not None:
        if (not isinstance(policy_file, str) or not policy_file
                or Path(policy_file).name != policy_file or policy_file in {".", ".."}
                or not isinstance(repository_policy, str) or not repository_policy.strip()):
            raise ValueError("workflow fixture repository policy needs a safe filename and nonempty text")
    elif policy_file is not None:
        raise ValueError("workflow fixture policy_file requires repository_policy text")
    (run / "message.txt").write_bytes(fixture["draft"].encode("utf-8"))
    repo = run / "repo"
    repo.mkdir()

    def git(*args):
        return subprocess.run(
            ["git", *args], cwd=repo, check=True, capture_output=True, text=True, timeout=10,
        ).stdout.strip()

    git("init", "-q", "-b", "review/validation")
    for key, value in (
        ("user.name", "Workflow Fixture"), ("user.email", "fixture@example.com"),
        ("commit.gpgsign", "false"), ("core.hooksPath", str(repo / ".git/hooks")),
    ):
        git("config", key, value)
    notes = repo / "notes.txt"
    notes.write_text(fixture["before"], encoding="utf-8")
    if repository_policy is not None:
        (repo / policy_file).write_text(repository_policy, encoding="utf-8")
    git("add", "-A")
    git("-c", "core.hooksPath=/dev/null", "commit", "-qm", "docs: add support hours")
    fixture_metadata = {
        "initial_head": git("rev-parse", "HEAD"),
        "expected_draft": fixture["draft"],
        "expected_content": fixture["after"],
        "expected_coauthors": expected_coauthors,
        "policy_file": policy_file,
        "repository_policy": repository_policy,
    }
    (run / "fixture.json").write_text(json.dumps(fixture_metadata) + "\n")
    if not agent_edits:
        notes.write_text(fixture["after"], encoding="utf-8")
        git("add", "notes.txt")

    # Observe the real validator without changing its result or imposing a gate.
    validator = copied / "scripts/validate_message.py"
    validator.rename(validator.with_name("_validate_message.py"))
    validator.write_text(f'''#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path
message = Path(sys.argv[1]).resolve()
content = message.read_text(encoding="utf-8")
result = subprocess.run([sys.executable, str(Path(__file__).with_name("_validate_message.py")), *sys.argv[1:]], capture_output=True, text=True)
with Path({str(events)!r}).open("a", encoding="utf-8") as stream:
    stream.write(json.dumps({{"kind": "validation", "path": str(message), "message": content, "argv": sys.argv[1:], "exit_code": result.returncode}}) + "\\n")
sys.stdout.write(result.stdout)
sys.stderr.write(result.stderr)
sys.exit(result.returncode)
''', encoding="utf-8")

    # Record commit attempts, including attempts made after failed validation.
    hook = repo / ".git/hooks/commit-msg"
    hook.write_text(f'''#!{sys.executable}
import json
import sys
from pathlib import Path
with Path({str(events)!r}).open("a", encoding="utf-8") as stream:
    stream.write(json.dumps({{"kind": "commit", "message": Path(sys.argv[1]).read_text(encoding="utf-8")}}) + "\\n")
''', encoding="utf-8")
    hook.chmod(0o755)
    print(run)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("skill_snapshot", type=Path)
    parser.add_argument("--fixture", type=Path, help="workflow input fixture; defaults to validation-before-commit")
    args = parser.parse_args()
    prepare(args.run_directory.resolve(), args.skill_snapshot.resolve(), args.fixture.resolve() if args.fixture else None)


if __name__ == "__main__":
    main()
