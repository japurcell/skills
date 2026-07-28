# Phase 6 Minimum Non-Negotiable Subagent Steps

The feature-dev workflow mandates exactly **two subagent steps** in Phase 6, both marked "Always" — meaning they apply on every track (Light, Standard, and Deep) without exception:

## Required Subagent Steps

### Step 1 — code-simplifier subagent
**Role**: Refactoring / simplification  
**Mandate**: *"Always launch an independent `code-simplifier` subagent to identify refactoring opportunities after implementation."*  
One instance, always.

### Step 2 — code-reviewer agent(s)
**Role**: Quality review  
**Mandate**: *"Always run independent `code-reviewer` agents for quality review on every track."*  
Minimum one instance (Light track); multiple in parallel for Standard or Deep.

## What Is Not a Subagent Step

Actions 3–5 in Phase 6 (consolidate findings, fix high-severity issues, surface remaining risks) are performed by the orchestrating agent itself — not by subagents. They are not subagent steps and are therefore out of scope for this analysis.

## Summary Table

| Step | Subagent Role | When Required |
|------|---------------|---------------|
| 1 | `code-simplifier` | Always (all tracks) |
| 2 | `code-reviewer` | Always (all tracks); ≥1 on Light, multiple on Standard/Deep |

These two are the floor. Nothing else in Phase 6 is a mandated subagent invocation.
