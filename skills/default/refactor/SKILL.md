---
name: refactor
description: Preserve behavior while restructuring code. Use when asked to simplify changes, consolidate duplicate logic, or make a codebase easier to navigate.
argument-hint: '[task or scope:<path or git diff range>]'
---

Edit within scope. Search wider as needed. For simplification and deduplication, default to changed hunks and new files. Stop on empty scope.

- **Simplify.** Activate the `addy-code-simplification` skill. Keep already-clear code.
- **Deduplicate.** Start from supplied candidates or `scope:` when given. Find exact copies, near copies and reimplementations. Check repository, standard library, platform and installed direct dependencies. Compare defaults, errors and effect order. Keep different rules separate. Prefer nearby existing helpers. Default to 1-3 safe candidates.
- **Navigate.** Trace a real question through a named area or change hotspot. Record files and decisions from entry point to rule. Repeat after restructuring. Keep demonstrably easier navigation.

Keep single investigations local. For independent read-only exploration, activate the `fan-out` skill. The primary agent reconciles findings and edits. Delegate only disjoint, independently verifiable edits.

Before restructuring, establish a passing entry-point test or replay. Narrow or skip unverifiable changes. Check deletion candidates for convention, configuration, dynamic and external callers. Ask before changing public contracts, behavior or architectural scope.

Verify each edit and replay the baseline. Undo failing edits.

After editing, dispatch a new read-only review subagent if any decision involved cross-owner consolidation, subtle equivalence, or dynamic reachability (including a decision to keep code). Give it the resulting diff, behavior contract and relevant entry point to check. Wait for its verdict, resolve findings and report verification and meaningful no-ops.
