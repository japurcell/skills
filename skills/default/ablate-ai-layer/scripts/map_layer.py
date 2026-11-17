#!/usr/bin/env python3
"""Map a repository's AI layer. Read-only. Agent-agnostic.

Maps known local instruction artifacts and reachable Markdown context,
classifies their loading scope, and estimates the always-loaded context cost.

  always-loaded : enters context every session whether the task needs it or not
  on-demand     : costs nothing until invoked or until its path matches
  enforcement   : deterministic, executes as code, spends no attention budget

Usage:
  python map_layer.py [repo_root] [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from collections import deque
from urllib.parse import unquote, urlsplit

ALWAYS, ONDEMAND, ENFORCE = "always-loaded", "on-demand", "enforcement"

# (glob, agent, default classification, note)
PATTERNS: list[tuple[str, str, str, str]] = [
    # --- Claude Code
    ("CLAUDE.md",                        "Claude Code", ALWAYS,   "root project instructions"),
    ("CLAUDE.local.md",                  "Claude Code", ALWAYS,   "personal, gitignored"),
    (".claude/CLAUDE.md",                "Claude Code", ALWAYS,   "alt project instructions"),
    (".claude/rules/**/*.md",            "Claude Code", ALWAYS,   "path-scoped if it has paths: frontmatter"),
    (".claude/skills/*/SKILL.md",        "Claude Code", ONDEMAND, "loads when invoked or matched"),
    (".claude/agents/*.md",              "Claude Code", ONDEMAND, "loads only inside a subagent"),
    (".claude/commands/**/*.md",         "Claude Code", ONDEMAND, "loads when the command runs"),
    (".claude/settings.json",            "Claude Code", ENFORCE,  "hooks and permissions"),
    (".claude/settings.local.json",      "Claude Code", ENFORCE,  "hooks and permissions"),
    # --- open standard / Codex / Amp / Gemini CLI / Zed
    ("AGENTS.md",                        "AGENTS.md",   ALWAYS,   "open standard, read by most agents"),
    ("GEMINI.md",                        "Gemini CLI",  ALWAYS,   "root project instructions"),
    (".gemini/GEMINI.md",                "Gemini CLI",  ALWAYS,   "project instructions"),
    (".agents/skills/*/SKILL.md",        "Codex",       ONDEMAND, "filesystem-discovered skills"),
    (".agents/rules/**/*.md",            "AGENTS.md",   ALWAYS,   "proposed rules dir"),
    # --- Cursor
    (".cursorrules",                     "Cursor",      ALWAYS,   "legacy single-file rules"),
    (".cursor/rules/**/*.mdc",           "Cursor",      ALWAYS,   "alwaysApply decides; parsed below"),
    # --- Windsurf
    (".windsurfrules",                   "Windsurf",    ALWAYS,   "root rules file"),
    (".windsurf/rules/**/*.md",          "Windsurf",    ALWAYS,   "rules dir"),
    # --- Cline
    (".clinerules",                      "Cline",       ALWAYS,   "root rules file"),
    (".clinerules/**/*.md",              "Cline",       ALWAYS,   "rules dir"),
    # --- GitHub Copilot
    (".github/copilot-instructions.md",  "Copilot",     ALWAYS,   "repo-wide instructions"),
    (".github/instructions/**/*.md",     "Copilot",     ONDEMAND, "applyTo-scoped"),
    # --- Aider
    ("CONVENTIONS.md",                   "Aider",       ALWAYS,   "conventions file"),
    (".aider.conf.yml",                  "Aider",       ENFORCE,  "config"),
]

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build",
             "__pycache__", ".next", "target", ".ablation"}
HISTORY_DIRS = {"plans", "archive", "archives"}
MARKDOWN_SUFFIXES = {".md", ".mdc", ".markdown"}
ENTRYPOINT_NAMES = {"AGENTS.md", "CLAUDE.md", "CLAUDE.local.md", "GEMINI.md",
                    "copilot-instructions.md", ".cursorrules", ".windsurfrules",
                    ".clinerules", "CONVENTIONS.md"}


def references(text: str, claude_imports: bool):
    """Recognize local Markdown links, path code spans, and Claude @ imports."""
    text = re.sub(r"(?ms)^\s*(```|~~~).*?^\s*\1[^\n]*$", "", text)
    for match in re.finditer(r"\[[^\]]*\]\(\s*(<[^>]+>|[^\s)]+)", text):
        yield match[1].strip("<>"), ONDEMAND
    for match in re.finditer(r"(?m)^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)", text):
        yield match[1].strip("<>"), ONDEMAND
    for match in re.finditer(r"`([^`\n]+)`", text):
        yield match[1], ONDEMAND
    if claude_imports:
        for match in re.finditer(r"(?:^|\s)@([^\s`]+)", text):
            yield match[1], ALWAYS


def local_targets(root: Path, source: Path, reference: str):
    """Resolve context paths without crossing the repo or traversing history."""
    try:
        url = urlsplit(reference)
    except ValueError:
        return
    if url.scheme or url.netloc or not url.path:
        return
    relative = Path(unquote(url.path))
    if relative.is_absolute():
        return
    for base in (source.parent, root):
        candidate = (base / relative).resolve()
        try:
            parts = candidate.relative_to(root).parts
        except ValueError:
            continue
        if not parts or any(part in SKIP_DIRS | HISTORY_DIRS for part in parts):
            continue
        if not candidate.exists():
            continue
        # Directory mentions in secondary documents are often code locations,
        # not instructions to load every document below them.
        if candidate.is_dir() and source.name not in ENTRYPOINT_NAMES:
            return
        paths = candidate.rglob("*") if candidate.is_dir() else [candidate]
        for path in paths:
            # Check lexical and resolved paths: directory aliases cannot bypass exclusions.
            if any(part in SKIP_DIRS | HISTORY_DIRS for part in path.relative_to(root).parts):
                continue
            resolved = path.resolve()
            if not resolved.is_relative_to(root):
                continue
            if any(part in SKIP_DIRS | HISTORY_DIRS for part in resolved.relative_to(root).parts):
                continue
            if resolved.is_file() and resolved.suffix.lower() in MARKDOWN_SUFFIXES:
                yield resolved, candidate.is_dir()
        return


def frontmatter(path: Path) -> dict:
    """Parse leading YAML frontmatter shallowly. No yaml dependency."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return {}
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    out = {}
    for line in text[3:end].splitlines():
        if ":" in line and not line.strip().startswith("#"):
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip()
    return out


def classify(path: Path, default: str) -> tuple[str, str]:
    """Refine classification using the file's own frontmatter."""
    name = path.name
    # Key PRESENCE, not truthiness: a YAML list renders as an empty value here
    # ("paths:\n  - src/**") and would otherwise read as absent.
    if name.endswith(".mdc"):                       # Cursor
        fm = frontmatter(path)
        if str(fm.get("alwaysApply", "")).lower() == "true":
            return ALWAYS, "alwaysApply: true"
        if "globs" in fm:
            return ONDEMAND, "glob-scoped"
        return ONDEMAND, "manual / description-matched"
    if "/.claude/rules/" in path.as_posix():
        fm = frontmatter(path)
        if "paths" in fm:
            return ONDEMAND, "path-scoped rule"
        return ALWAYS, "unscoped rule, loads every session"
    return default, ""


def iter_matches(root: Path):
    root = root.resolve()
    items = {}
    pending = deque()

    def add(path, agent, kind, note, source=None):
        path = path.resolve()
        if not path.is_relative_to(root):
            return
        if any(part in SKIP_DIRS | HISTORY_DIRS for part in path.relative_to(root).parts):
            return
        key = path.relative_to(root).as_posix()
        if key in items:
            item = items[key]
            if agent == "Claude Code" and item["agent"] != agent:
                item["agent"] = agent
                pending.append(path)
            if source and source not in item["referenced_by"]:
                item["referenced_by"].append(source)
            if kind == ALWAYS and item["kind"] == ONDEMAND:
                item["kind"] = ALWAYS
                pending.append(path)
            return
        items[key] = {
            "path": key, "agent": agent, "kind": kind, "note": note,
            "bytes": path.stat().st_size,
            "lines": len(path.read_text(encoding="utf-8", errors="replace").splitlines()),
            "referenced_by": [source] if source else [],
        }
        if kind != ENFORCE:
            pending.append(path)

    for pattern, agent, default, note in PATTERNS:
        for p in root.glob(pattern):
            if not p.is_file():
                continue
            if any(part in SKIP_DIRS | HISTORY_DIRS for part in p.relative_to(root).parts):
                continue
            kind, why = classify(p, default)
            add(p, agent, kind, why or note)

    visited = set()
    while pending:
        path = pending.popleft()
        key = path.relative_to(root).as_posix()
        item = items[key]
        state = (key, item["kind"], item["agent"])
        if state in visited:
            continue
        visited.add(state)
        text = path.read_text(encoding="utf-8", errors="replace")
        for reference, kind in references(text, item["agent"] == "Claude Code"):
            for target, directory in local_targets(root, path, reference):
                if item["kind"] != ALWAYS or directory:
                    kind = ONDEMAND
                add(target, item["agent"], kind,
                    "local context reference; review relevance before ablation", key)
    yield from items.values()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Map local agent instructions and their loading scope without modifying files.",
        allow_abbrev=False,
        epilog="Follows local Markdown references; instruction-directory context is on-demand. "
               "Excludes plans/archive/archives and paths outside the repository. "
               "Writes an inventory to stdout; diagnostics to stderr. Does not read stdin. "
               "Exit codes: 0 success, 2 invalid arguments or unreadable input.")
    parser.add_argument("repo_root", nargs="?", default=".", help="repository directory (default: current directory)")
    parser.add_argument("--json", action="store_true", help="emit root and artifacts as JSON")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    if not root.is_dir():
        parser.error(f"repository directory does not exist: {root}")

    try:
        items = sorted(iter_matches(root), key=lambda d: (d["kind"], d["path"]))
    except OSError as error:
        parser.error(f"cannot read instruction sources: {error}")
    if args.json:
        print(json.dumps({"root": str(root), "artifacts": items}, indent=2))
        return 0

    if not items:
        print(f"No AI layer artifacts found under {root}")
        print("Nothing to ablate. This repo has no agent instructions committed.")
        return 0

    agents = sorted({i["agent"] for i in items})
    print(f"AI layer under {root}")
    print(f"Agents detected: {', '.join(agents)}\n")

    for kind, header in ((ALWAYS, "ALWAYS LOADED  (paid on every session)"),
                         (ONDEMAND, "ON DEMAND  (free until it fires)"),
                         (ENFORCE, "ENFORCEMENT  (deterministic, no attention cost)")):
        group = [i for i in items if i["kind"] == kind]
        if not group:
            continue
        print(f"  {header}")
        for i in group:
            print(f"    {i['lines']:>5} ln  {i['path']:<52} {i['note']}")
            if i["referenced_by"]:
                print(f"             referenced by: {', '.join(i['referenced_by'])}")
        print()

    always = [i for i in items if i["kind"] == ALWAYS]
    total_bytes = sum(i["bytes"] for i in always)
    total_lines = sum(i["lines"] for i in always)
    print(f"  Always-loaded total: {total_lines} lines, roughly {total_bytes // 4:,} tokens "
          f"on every session before you type anything.")
    print()
    print("  Ablate the always-loaded set. Leave the on-demand set alone: it costs")
    print("  nothing until it fires, so deleting it buys you no context back.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
