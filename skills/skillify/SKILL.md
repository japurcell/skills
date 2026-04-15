---
name: skillify
description: Capture the repeatable workflow from the current or just-finished session and turn it into a reusable skill. Use when the user asks to create a skill from this session, extract a reusable workflow, "skillify" a conversation, or save a multi-step process as a slash-invocable skill.
argument-hint: "session summary or workflow goal"
disable-model-invocation: true
metadata:
  compatibility: "Designed for Agent Skills-compatible clients that can ask the user questions and write files."
  allowed_tools: "Read Grep Glob Edit Write AskUserQuestions"
  when_to_use: "Use when the user wants to turn the current or just-completed session into a reusable skill. Trigger on requests like 'create a skill from this session', 'turn this into a skill', 'skillify this', or 'save this workflow as a skill'."
  arguments: "session-summary"
---

# /skillify

## Your Task

Capture the repeatable workflow from the current or just-finished session and turn it into a reusable skill.

### Step 1: Analyze the Session

Before asking any questions, analyze the session to identify:

- What repeatable process was performed
- What the inputs/parameters were
- The distinct steps (in order)
- The success artifacts/criteria (e.g. not just "writing code," but "an open PR")
- Where the user corrected or steered you
- What tools and permissions were needed
- What agents were used
- What the goals and success criteria were

### Step 2: Interview the User

You will use the AskUserQuestion to understand what the user want to automate. Important notes:

- Use AskUserQuestions for ALL questions! Never ask questions via plain text.
- For each round, iterate as much as needed until the user is happy.
- The user always has a freeform "Other" option to type edits or feedback -- do NOT add your own "Needs tweaking"

**Round 1: High level confirmation**

- Suggest a name and description for the skill based on your analysis. Ask the user to confirm or rename.
- Suggest high-level goal(s) and specific success criteria for the skill.

**Round 2: More details**

- Present the high-level steps you identified as a numbered list. Tell the usser you will dig into the detail in the next
- If you think the skill will require arguments, suggest arguments based on what you observed. Makesure you understand
- If it's not clear, ask if this skill should run inline (in the current conversation) or forked (as a sub-agent)
- Ask where the skill should be saved. Suggest a default based on context (repo-specific workflows -> repo, cross-repo -> personal)
  - **This repo** (\`.agents/skills/<name>/SKILL.md\`) - for workflows specific to the project
  - **Personal** (\`~/.agents/skills/<name>/SKILL.md\`) - follows you across all repos

**Round 3: Breaking down each step**

For each major step, if it's not glaringly obvious, ask:

- What does this step produce that later steps need? (data, artifacts, IDs)
- What proves that this step succeeded, and that we can move on?
- Should the userbe asked to confirm before proceeding? (especially for irreversible actions like merging, sending )
- Are any steps independent and could run in parallel? (e.g., posting to Slack and monitoring CI at the same time)
- How should the skill be executed? (e.g. always use a Task agent to conduct code review, or invoke an agent team)
- What are the hard constraints or hard preferences? Things that must or must not happen?

You may do multiple rounds of AskUserQuestion here, one round per step, especially if there are more than 3 steps

IMPORTANT: Pay special attention to places where the user corrected you during the session, to help inform your design.

**Round 4: Final questions**

- Confirm when this skill should be invoked, and suggest/confirm trigger phrases too. (e.g. for a cherrypick workflow)
- You can also ask for any other gotchas or things to watch out for, if it's still unclear.

Stop interviewing once you have enough information. IMPORTANT: Don't over-ask for simple processes!

### Step 3: Write the SKILL.md

Create the skill directory and file at the location the user chose in Round 2.

Use this format:

```markdown
---
name: {{skill-name}}
description: {{one-line description}}
allowed-tools:
{{list of tool permission patterns observed during session}}
argument-hint: "{{hint showing argument placeholders}}"
arguments:
{{list of argument names}}
context: {{inline or fork -- omit for inline}}
---

# {{Skill Title}}

Description of skill

## Inputs

- \`$arg_name\`: Description of this input

## Goal

Clearly stated goal for this workflow. Best if you have clearly defined artifacts or criteria for completion.

## Steps

### 1. Step Name

What to do in this step. Be specific and actionable. Include commands when appropriate.

**Success criteria**: ALWAYS include this! This shows that the step is done and we can move on. Can be a list.

IMPORTANT: see the next section below for the per-step annotations you can optionally include for each step.

'''
```

**Per-step annotations**:

- **Success criteria** is REQUIRED on every step. This helps the model understand what the user expects from their workflow.
- **Executions**: \`Direct\` (default), \`Task agent\` (straightforward subagents), \`Terminate\`
- **Artifacts**: Data this step produces that later steps need (e.g., PR number, commit SHA). Only include if later steps need.
- **Human checkpoint**: When to pause and ask the user before proceeding. Include for irreversible actions (merging, deleting, etc)
- **Rules**: Hard rules for the workflow. User corrections during the reference session can be especially useful here.

**Step structure tips:**

- Steps that can run concurrently use sub-numbers: 3a, 3b
- Steps requiring the user to act get \`[human]\` in the title
- Keep simple skills simple -- a 2-step skill doesn't need annotations on every step

**Frontmatter rules:**

- \`allowed-tools\`: Minimum permissions needed (use patterns like \`Bash(gh:\*)\` not 'Bash')
- \`context\`: Only set \`context: fork\` for self-contained skills that don't need mid-process user input.
- \`when_to_use\` is CRITICAL -- tells the model when to auto-invoke. Start with "Use when..." and include trigger phrases.
- \`arguments\` and \`argument-hint\`: Only include if the skill takes parameters. Use \`$name\` in the body for substitution.

### Step 4: Confirm and Save

Before writing the file, output the complete SKILL.md context as a yaml code block in your response so the user can review it.

After writing, tell the user:

- Where the skill was saved
- How to invoke it: \`/{{skill-name}} [arguments]\`
- That they can edit the SKILL.md directly to refine it
