# Ideas

Use this file as a lightweight inbox for ideas that are not ready for research or planning. Add each idea as one short bullet. When work starts, move the idea into the appropriate research, planning, or implementation artifact.

## Inbox

- [ ] **exec-plans progress disclosure**: exec plans can get really large, so it would be helpful to implement a progressive disclosure mechanism into the [exec-plans skill](../.agents/skills/exec-plans/SKILL.md) to show only the most relevant parts initially and reveal more details as needed.

- [ ] **SKILL audit**: Claude released updates to skill authoring best practices: [Official documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices). Even though I don't use Claude, I still want to incorporate these best practices into all skills in this repo unless they are blatantly incompatible with codex, copilot, or gemini: [../.agents/skills/](../.agents/skills/) and [../skills/](../skills/). Our audit will include all of the best practices, but a few stood out to me:
  - **Structure longer reference files with table of contents**: [Official documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#structure-longer-reference-files-with-table-of-contents)
  - **Workflows and feedback loops**: [Official documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#workflows-and-feedback-loops)
  - **Conditional workflow pattern**: [Official documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#conditional-workflow-pattern)
  - **Concise is key**: [Official documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#concise-is-key)
  - **Set appropriate degrees of freedom**: [Official documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#set-appropriate-degrees-of-freedom)
  - **Test with all models you plan to use**: [Official documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#test-with-all-models-you-plan-to-use)
    - we will keep this scoped to OpenAI models for the purposes of this audit
  - **Writing effective descriptions**: [Official documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#writing-effective-descriptions)
  - **Progressive disclosure patterns**: [Official documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#progressive-disclosure-patterns)

- [ ] **Just-in-time context**: The agents kb/memory management system is currently spread across AGENTS.md, .agents/skills/clean-agent-docs, .agents/skills/update-agent-docs. It tries to guide agents through a workflow:
  1. Session Start -> AGENTS.md##Agent Orientation: load the knowledge base map to find relevant context for a task
  2. Session End -> activate 'update-agents-docs' skill to repair and refresh the knowledge base with new information from the session for continual improvement
  3. Periodically -> activate 'clean-agent-docs' skill to maintain the knowledge base by removing outdated or irrelevant information

  I have a few ideas on how to improve the current system, but these are just ideas; they need to be validated, possibly challenged or thrown away if a better approach is found:
    1. Create a single skill that handles all aspects of the agents kb/memory management system using progressive disclosure by the use of subcommands for the different lifecycle stages (e.g., '/agent-brain recall', '/agent-brain learn', '/agent-brain dream'). Each subcommand is a navigation pointer to the guidance for that particular stage. Hooks can be used to trigger these subcommands at the corresponding hook event.
       - Session start -> '/agent-brain recall'
       - Session end -> '/agent-brain learn'
       - Periodically -> '/agent-brain dream'
    2. Study the use of nested AGENTS.md files as another just-in-time context mechanism [harness-engineering repo](https://github.com/lopopolo/harness-engineering), [use AGENTS.md as a map](https://github.com/lopopolo/harness-engineering/tree/trunk/docs/just-in-time-context#use-agentsmd-as-a-map).

  I think that a lot of ideas and insights can be drawn from these references:
  - [Just-in-time context reference](https://github.com/lopopolo/harness-engineering/tree/trunk/docs/just-in-time-context)
  - [Feedback reference](https://github.com/lopopolo/harness-engineering/tree/trunk/docs/feedback)
  - [Domain modeling reference](https://github.com/lopopolo/harness-engineering/tree/trunk/docs/domain-modeling)
  - [Self-improving LLMs](https://arxiv.org/html/2510.04618v3)
  - [A Complete Guide to AGENTS.md](https://www.aihero.dev/a-complete-guide-to-agents-md)

  **Goal**: a self-improving context management system the doesn't rely on agents remembering when to update or refresh their knowledge, but instead manages it autonomously through structured processes and hooks.

- [ ] **exec-plans tasks**: Should 'exec-plans' breakdown milestones into tasks similarly to how 'spec-to-tasks' does so that weaker models can handle them more effectively?

- [ ] **agentic workflows**: I want to investigate ways to run agent workflows (e.g. plan -> implement -> checkpoints -> prototypes -> review/fix loops).
  - the transcipt from this video describes shopify's process: <https://youtu.be/bBMp5tLxShQ?si=qgFTxY2TBbCXjlvd>
  - validation pipeline: <https://github.com/kunchenguid/no-mistakes>
  - [Super Simple Software Factory](https://github.com/disler/super-simple-software-factory)

- [ ] Look at migrating agent kb/memory to nested AGENTS.md files like [https://github.com/lopopolo/harness-engineering](https://github.com/lopopolo/harness-engineering)
