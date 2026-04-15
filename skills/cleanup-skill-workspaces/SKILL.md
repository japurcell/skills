---
name: cleanup-skill-workspaces
description: Scan all *-workspace directories under the skills root, keep only the most recently created iteration folder (by filesystem creation date) plus any skill-snapshot directories, and delete all older iterations. Use when asked to clean up workspace directories, prune old eval iterations, or free up space in skill workspaces.
allowed-tools:
  - Bash(find:*)
  - Bash(rm:*)
  - Bash(stat:*)
---

# Cleanup Skill Workspaces

Prune old iteration directories from all skill workspace folders, keeping only the most recently created iteration and any skill-snapshots.

## Goal

Each `*-workspace` directory is left with at most one iteration folder (the newest by creation date) plus any `skill-snapshot*` directories. Older iterations are deleted.

## Steps

### 1. Find all workspace directories

Use `find` to locate all `*-workspace` directories directly under the skills root.

**Success criteria**: A list of workspace directories is identified.

### 2. For each workspace, identify iteration directories

List subdirectories matching `iteration-*` and sort them by filesystem creation date (`stat -f %B` on macOS, `stat -c %W` on Linux). Identify the newest.

**Success criteria**: For each workspace, you know which iteration is most recently created and which are older.

### 3. Preview and confirm

Show the user a summary table of what will be kept and what will be deleted across all workspaces.

**Human checkpoint**: Ask the user to confirm before proceeding with any deletions.

**Success criteria**: User has confirmed the plan.

### 4. Delete older iterations

For each workspace, delete all `iteration-*` directories except the newest one. Leave `skill-snapshot*` directories untouched.

**Rules**:
- Sort by filesystem creation date, NOT by folder name or numeric suffix — names like `iteration-14` may predate `iteration-2` if created in a different session.
- Never delete `skill-snapshot*` directories.
- Never delete the single remaining (newest) iteration.
- If a workspace has only one iteration, skip it — nothing to prune.

**Success criteria**: Older iteration directories are removed; the newest iteration and all skill-snapshots remain intact.

### 5. Report

Print a final summary: workspace name, iteration kept, iterations deleted (or "nothing to prune" if only one existed).

**Success criteria**: User can confirm exactly what was cleaned up.
