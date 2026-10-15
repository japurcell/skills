# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `ab2cc46c-7681-430c-9bf5-b362014cf2b1`  
> - **Started:** 6/18/2026, 12:30:52 PM  
> - **Duration:** 25s  
> - **Exported:** 6/18/2026, 12:31:17 PM  

---

<sub>⏱️ 0s</sub>

### ⚠️ Warning

Third-party MCP servers are disabled by your organization's Copilot policy. Only built-in servers are available.

---

<sub>⏱️ 1s</sub>

### ℹ️ Info

Disabled tools: bash, fetch_copilot_cli_documentation, github-mcp-server-get_copilot_space, github-mcp-server-get_file_contents, github-mcp-server-list_copilot_spaces, github-mcp-server-search_code, github-mcp-server-search_users, glob, list_agents, list_bash, read_agent, read_bash, report_intent, rg, session_store_sql, skill, sql, stop_bash, task, web_fetch, write_agent

---

<sub>⏱️ 1s</sub>

### 👤 User

Read and follow only the skill definition at `/home/adam/dev/personal/skills/skills/code-review-workspace/skill-snapshot-old/SKILL.md`. Ignore any other installed copy of `code-review`. Do not...

---

<sub>⏱️ 4s</sub>

### 💬 Copilot

I’ll load that exact skill file first and follow it as the sole instruction source for this task.

---

<sub>⏱️ 5s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/code-review-workspace/skill-snapshot-old/SKILL.md.**

/home/adam/dev/personal/skills/skills/code-review-workspace/skill-snapshot-old/SKILL.md

<details>
<summary>166 lines</summary>

```
1. ---
2. name: code-review
3. description: Review a pull request, branch, recent commits, staged or unstaged changes, or AI-generated code for correctness, readability, architecture, security, performance, standards/spec adherence, and maintainability. Use when reviewing a PR before merge, reviewing changes since a fixed point, reviewing work-in-progress changes, reviewing another agent's code, asking to "review since X", requesting a thermo-nuclear / thermonuclear / deep code quality / especially harsh maintainability review, or when machine-readable output is needed.
4. disable-model-invocation: true
5. ---
6. 
7. # Code Review
8. 
9. Review only the requested change scope. Anchor every finding to that change. Prefer behavior-preserving simplification: smaller, clearer, more direct code over cleverness or incidental complexity.
10. 
11. ## Scope
12. 
13. Review for correctness, readability, architecture, security, performance, documented standards, spec adherence if a spec exists, and maintainability.
14. 
15. Report only issues introduced by, exposed by, or clearly reachable through the reviewed change.
16. 
17. ## Required-agent rule
18. 
19. If this skill requires a dedicated agent, run it. Do not merge, combine, substitute, skip, or manually emulate required agents.
20. 
21. ## Process
22. 
23. 1. Invoke `subagent-model-router` and `addy-code-review-and-quality`.
24. 
25. 2. Make a todo list.
26. 
27. 3. Set the review target only. Do not read PR or issue content directly in this step.
28.    - PR review: target the PR.
29.    - Fixed-point review: use exactly the user-provided target.
30.    - If the user says “review since X” but X is not a fixed point, ask: `Review against what — a branch, a commit, or main?` Stop until answered.
31. 
32. 4. Follow the main-agent GitHub intake rule:
33.    - The main agent must not read PR or GitHub issue content directly.
34.    - All GitHub PR/issue intake must be done by a fast-tier subagent using `gh`, not web fetch.
35.    - The main agent may use only the subagent summary unless a later required agent needs more detail.
36. 
37. 5. Capture inputs with fast-tier subagents.
38.    - Fixed-point review:
39.      - `git diff <fixed-point>...HEAD`
40.      - `git log <fixed-point>..HEAD --oneline`
41.    - PR review:
42.      - PR status and early-stop recommendation: open / closed / draft / review not needed / already reviewed by you
43.      - title, body summary, branch info, changed files, linked issues, referenced specs, notable metadata
44.      - compact summary of linked or referenced GitHub issues relevant to scope or spec
45.      - likely spec-source candidates in priority order
46.    - If not reviewing a PR but GitHub issues are referenced, fetch and summarize them.
47. 
48. 6. Stop early if intake says a PR is closed, draft, does not need review, or already has a review from you.
49. 
50. 7. Gather only relevant standards/context files via a fast-tier subagent, checking repo root and touched paths as applicable:
51.    - `AGENTS.md`
52.    - `CLAUDE.md`
53.    - `GEMINI.md`
54.    - `CONTRIBUTING.md`
55.    - `CONTEXT.md`
56.    - `CONTEXT-MAP.md`
57.    - `STYLE.md`
58.    - `STANDARDS.md`
59.    - `STYLEGUIDE.md`
60.    - `docs/adr/*`
61.    - `.editorconfig`
62.    - `eslint.config.*`
63.    - `biome.json`
64.    - `prettier.config.*`
65.    - `tsconfig.json`
66. 
67. 8. Identify the spec source in this order:
68.    1. issue references from commit messages or PR metadata
69.    2. user-supplied path
70.    3. matching spec / PRD under `docs/`, `specs/`, `.scratch/`, or `.agents/scratchpad/**`
71.    4. if none is found, ask where the spec is; if there is no spec, record `no spec available` and skip the Spec agent
72. 
73. 9. Preflight required agents. Hard stop if any required agent is missing.
74. 
75.    Always required:
76.    - `addy-code-reviewer`
77.    - `addy-security-auditor`
78.    - `addy-test-engineer`
79.    - Maintainability agent
80.    - Standards agent
81. 
82.    Required only if a spec exists:
83.    - Spec agent
84. 
85.    Required only for PR reviews:
86.    - History agent
87.    - Related-PR agent
88.    - Code-comment agent
89. 
90. 10. Spawn required agents in parallel.
91. 
92.     PR-only agents:
93.     - History agent: use `git blame` and modified-code history to identify historically supported issues.
94.     - Related-PR agent: review prior PRs touching the same files for comments that still apply.
95.     - Code-comment agent: check whether the change violates guidance in comments within modified files.
96. 
97.     All-review agents:
98.     - `addy-code-reviewer`: correctness, readability, architecture, security, performance
99.     - `addy-security-auditor`: OWASP Top 10, secrets, auth/authz, threat model, dependency CVEs
100.     - `addy-test-engineer`: test gaps in happy path, edge cases, error paths, concurrency
101.     - Spec agent, if a spec exists: missing or partial requirements, scope creep, incorrect implementation
102.     - Maintainability agent: apply `MAINTAINABILITY_CRITERIA.md`
103.     - Standards agent: report only documented standards violations; cite file and rule; skip anything tooling enforces
104. 
105. 11. Filter false positives.
106.     - For each issue, spawn a parallel fast-tier subagent to score whether it is real or a false positive.
107.     - Use `FALSE_POSITIVE_RUBRIC.md` verbatim.
108.     - For standards findings, confirm the standards file explicitly supports the finding.
109.     - Filter out issues with score below 75.
110. 
111. 12. Produce output.
112.     - For PR comment mode, use `OUTPUT_FORMATS.md`, repeat the PR eligibility check before commenting, and post with `gh pr comment` only if still eligible.
113.     - For machine-readable mode, use `OUTPUT_FORMATS.md`.
114.     - If the user requested a different output format, satisfy it while preserving the same filtering and evidence requirements.
115. 
116. ## Exclusions
117. 
118. Do not report:
119. 
120. - speculative bugs that do not survive light scrutiny
121. - pedantic nitpicks
122. - issues tooling should catch
123. - generic requests for more tests, docs, or security review unless explicitly required by a standards file or clearly broken in the change
124. - likely intentional functional changes tied to the broader change
125. - issues on unchanged lines unless the change clearly exposes or activates them
126. 
127. Do not run builds, typechecks, linters, or benchmarks unless the user explicitly asks.
128. 
129. ## Review priorities
130. 
131. 1. correctness bugs
132. 2. documented repo standards violations
133. 3. spec mismatches
134. 4. structural maintainability regressions
135. 5. missed opportunities for dramatic simplification when a clear path is visible
136. 6. architecture boundary problems
137. 7. security and performance issues supported by the change
138. 8. readability issues that materially affect comprehension
139. 
140. ## Primary review questions
141. 
142. - Is there a code-judo move that would make this dramatically simpler?
143. - Did the diff add branching complexity where a better abstraction should exist?
144. - Is this logic in the right file and layer?
145. - Is this abstraction earning its keep, or is it just a wrapper?
146. - Did the diff introduce casts, optionality, or ad-hoc object shapes that obscure the real invariant?
147. 
148. ## Tone
149. 
150. Be direct, serious, and brief. Do not be rude. Do not soften major maintainability or correctness problems into mild suggestions. Do not treat a change as no-issue merely because behavior seems correct if it clearly makes the codebase structurally worse.
151. 
152. ## Final checks
153. 
154. Before returning or commenting, verify:
155. 
156. - [ ] every required dedicated agent for this review type was run
157. - [ ] no required agent was merged, combined, substituted, skipped, or manually emulated
158. - [ ] every finding is tied to the reviewed change
159. - [ ] every finding has a concrete file reference
160. - [ ] every standards-based finding is explicitly supported by a standards file
161. - [ ] no excluded false positives are included
162. - [ ] false-positive scoring from `FALSE_POSITIVE_RUBRIC.md` was applied
163. - [ ] if a plausible restructuring would delete substantial incidental complexity, call it out
164. - [ ] if a major maintainability problem is present, do not hide it behind minor wording
165. - [ ] output matches the requested mode exactly
166.
```

</details>


---

<sub>⏱️ 23s</sub>

### 💬 Copilot

**Hard stop:** I can’t complete the review under that skill because its required dedicated agents are not available/invokable in this runtime.

Per `/home/adam/dev/personal/skills/skills/code-review-workspace/skill-snapshot-old/SKILL.md`, the process requires running `subagent-model-router`, `addy-code-review-and-quality`, and then preflighting/running required agents (e.g., `addy-code-reviewer`, `addy-security-auditor`, `addy-test-engineer`, maintainability, standards, plus PR-only/spec agents as applicable). The skill explicitly requires stopping if any required agent is missing, so I did not proceed with a manual or substituted review.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
