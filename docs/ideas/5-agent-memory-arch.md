# Agent Memory Architecture

[Watch the video](https://youtu.be/mAKUL12h1n8?si=jo_E1lSoFM9btLqY)

In this episode of AI That Works, Dex is joined by Aaron for a hands-on walkthrough of a memory pipeline built by the Human Layer and Boundary teams. The goal is to turn coding-agent traces into useful, structured context that can help future sessions work more effectively. Rather than saving every conversation or filling a context file with generic advice, the system looks for the information that agents and developers would actually benefit from remembering.

The conversation explores how the pipeline identifies three kinds of information: facts agents discover about a codebase, corrections humans give agents, and questions or problems agents repeatedly investigate. It then filters and groups these findings, checks whether they represent useful knowledge beyond what the code already reveals, and generates proposed context updates with references to the sessions that support them. The result is a more systematic way to capture team-wide tribal knowledge without asking developers to manually review every coding session.

Aaron also walks through the engineering process behind the pipeline, including using BAML to define structured model inputs and outputs, experimenting with Jev for inexpensive classification, and building custom dashboards to inspect results. The team discusses why developers should start with a capable model to discover what works, then optimize for cost and latency; why inspecting prompts and outputs is essential; and how caching, replaying requests, and building evaluation datasets make iteration faster.

Finally, the conversation looks at what it takes to keep agent memory useful over time. Memories can become outdated, so a durable system needs to connect knowledge to the relevant parts of a codebase, incorporate user approval and rejection, and improve its own recommendations as feedback accumulates. The broader lesson is that better coding agents are not just about better models. They also depend on the pipelines, tools, evaluations, and feedback loops built around them.

GUEST BIO & LINKS
Aaron Villalpando— Co-founder and CTO

KEY TAKEAWAYS
Coding-agent traces contain valuable team knowledge, including codebase facts, recurring investigations, and human corrections.
Useful agent memory should capture information that is difficult to discover from the code alone, not repeat generic advice or existing documentation.
Grouping findings across sessions and teammates helps identify patterns that a single conversation would miss.
Start with a capable model to discover what works, then optimize the pipeline for cost, latency, and repeatability.
Inspect prompts, outputs, and intermediate steps instead of treating an AI pipeline as a black box.
Caching, replaying requests, and building custom evaluation tools make it much faster to iterate on AI pipelines.
Memory systems need provenance, user feedback, and a strategy for identifying stale information.

RESOURCES / PEOPLE MENTIONED
BAML — A programming language for building with AI and creating structured AI pipelines.

Jev — The fast, low-cost decision model used in the pipeline for classification and filtering tasks.

Human Layer — The team working on a multiplayer coding-agent workspace and collaborating on the memory pipeline.
Claude Code — Used during early exploration to investigate coding-session data and prototype the reporting workflow.

CLAUDE.md and AGENTS.md — Agent context files discussed as potential destinations for useful codebase knowledge, rules, and recommendations.

Jared Sumner / Bun — Mentioned in the discussion of caching requests and responses to a SQLite database.

Matt Pocock’s retro skill — Mentioned as an example of analyzing past agent sessions to learn from mistakes.

TOPICS COVERED
AI coding agents
Agent memory systems
Coding-session traces
Context engineering
Structured AI outputs
BAML
Jev
AI classification
Human feedback and agent corrections
Codebase documentation
Team-wide tribal knowledge
Prompt engineering
AI pipeline design
Model cost and latency
Caching and request replay
Evaluation datasets
AI observability
Custom developer tooling
Memory deduplication and grouping
Stale memory detection
Human-in-the-loop systems
Continuous pipeline improvement
