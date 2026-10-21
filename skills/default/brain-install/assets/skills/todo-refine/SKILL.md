---
name: todo-refine
description: Sharpen todo items in brain/todos.md into precise, actionable prompts via targeted questioning. Use after brain/todos.md is modified or when the user asks to "refine", "refine todos", or "clarify todos".
---

# Refine

Read `brain/todos.md` and refine unclear items into actionable prompts through targeted questioning.

## Workflow

1. **Read** `brain/todos.md` and review open items.
2. **Triage** each item: is it clear enough to act on without further context? A clear item specifies _what_ is wrong, _where_ it happens, and _what the fix should be_. Skip items that already meet this bar.
3. **Ask** clarifying questions about unclear items. Group related questions - aim for one round of questions, not a back-and-forth (to minimize back-and-forth and user fatigue). Good clarifying questions target:
   - **What** - what exactly is the problem or desired behavior?
   - **Where** - which part of the app, which component, which flow?
   - **How** - how should it work instead? What does "fixed" look like?
4. **Rewrite** unclear items in-place, incorporating the user's answers. Each rewritten item should be a self-contained prompt that another agent could act on without additional context.
5. **Remove** any items the user says are already done or no longer relevant.
6. **Report** a summary of what changed.
