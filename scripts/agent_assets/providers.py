"""Repository skill discovery paths established by the distribution research."""

# Official path evidence and precedence are recorded in
# docs/agent-asset-distribution/research/{codex-copilot,claude-gemini,portable-methods}/findings.md.
SKILL_ROOTS = {
    "codex": ".agents/skills", "copilot": ".agents/skills", "gemini": ".agents/skills",
    "claude": ".claude/skills", "cursor": ".agents/skills", "opencode": ".agents/skills",
}
CLIENTS = tuple(SKILL_ROOTS)
SKILLS_ONLY = {"claude", "cursor", "opencode"}


def skill_roots(clients):
    return sorted({SKILL_ROOTS[client] for client in clients})
