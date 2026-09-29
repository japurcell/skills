# Evaluate Distribution References

**Type:** research
**Status:** closed
**Blocked By:** none
**Research Dir:** research/distribution-references

## Question

Which verified design insights from luisalima/skills-lock, obra/superpowers, wshobson/agents, and echohello-dev/skillet add something not already covered by the approved contract? Check current first-party docs and targeted source for frozen restoration, content integrity, canonical/generated adapters, native package distribution, transport, symlink portability, maintenance status, and license. Identify whether findings justify changing initial delivery versus retaining a future option. Do not install tools or execute installers.

---

## Resolution

**No change to the approved initial contract is warranted.** The four repositories reinforce existing requirements and offer details for implementation acceptance and later options:

- `skills-lock` demonstrates immutable commit pins plus content-tree SHA-256 verification in frozen mode, while explicitly describing itself as a working prototype without skill dependencies or global scope. Use frozen verification as an acceptance check; do not add a second remote lock workflow to the committed-copy design.
- Superpowers and `wshobson/agents` show that one maintained source can feed harness-native adapters, but each client has different package surfaces, recognized components, bootstrap requirements, and installation/update paths. This supports the already-approved canonical catalog and per-client adapters, with native packages remaining a later channel.
- `wshobson/agents` also demonstrates why bundle and skill-only selection are distinct: skills-only tools do not install the corresponding agents or commands. This aligns with the approved bundle and individual selectors plus dependency closure.
- Skillet demonstrates Git, safe archive, OCI, and local-directory transports, static multi-OS packaging, and symlink/copy behavior for skills. It is skills-only, and its README gives conflicting check/update maturity claims. These are future options, not a reason to expand the Python stdlib installer or replace committed copies with symlinks.

Keep the approved complete delivery for Codex, Copilot, and Gemini; skills-only fallback for Claude Code, Cursor, and OpenCode; committed copies with immutable source revision and digest; explicit update/ownership/pruning rules; current-revision restoration without rollback; and later native packages. See [the findings](../research/distribution-references/findings.md) for source evidence, versions, license observations, caveats, and verification limits. Research reviewed public repository documentation only; no code was executed and no client compatibility was tested.
