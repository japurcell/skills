# Agentic workflows/software factory

I want to investigate ways to run agent workflows (e.g. plan -> implement -> checkpoints -> prototypes -> review/fix loops).

- the transcipt from this video describes shopify's process: <https://youtu.be/bBMp5tLxShQ?si=qgFTxY2TBbCXjlvd>
- validation pipeline: <https://github.com/kunchenguid/no-mistakes>
- [Super Simple Software Factory](https://github.com/disler/super-simple-software-factory)
  - I love the real-time observability UI
  - I love how it is packaged as a skill to be installed in any repo
- [Noodle](https://github.com/poteto/noodle)
  - I love the brain metaphor for managing agent knowledge and memory

What I want so far:

- packaged in a skill that can be installed in any repo
- I should be able to customize the agentic workflow and have multiple of them
- it should be self-improving by observing previous runs
- it should be able to route to different models and coding agents harnesses (e.g. Codex, Github Copilot, Gemini, OpenCode, Pi)
- UI
  - A way to observe all agent workflows in real-time
  - I should be able to view past sessions in the same way I view the real-time sessions
  - I should be able to drill down on details in the session view (e.g. the user prompt, responses, tool calls, skills loaded, errors, tokens used, etc)
  - the workflow should customizable
