I explored the repo first. The biggest finding is that there is no current root-level `copilot-install.sh`; it was renamed to `scripts/copilot-install.sh` in commit `324d435`, and today all repo docs point to `./scripts/copilot-install.sh`. The real duplication risk is now between the local installer and the overlapping copy/sync logic inside `scripts/addy-install.sh`, not between two live copies of the same file. That shapes the design space.

Key repo constraints I would preserve:
- `scripts/copilot-install.sh` remains the canonical documented entrypoint (`README.md`, `AGENTS.md`, `docs/agent-guides/repo-layout.md`, `docs/agent-guides/validation.md`).
- Current local install behavior stays the same: copy skills, top-level agents, optional references, optional hooks, and `.copilot/copilot-instructions.md`; skip `skills/*-workspace`; do not prune installed local content by default (`scripts/copilot-install.sh:17-97`).
- Addy import behavior remains distinct where needed: upstream sync, `addy-` prefixing, transitive skill discovery, reference rewriting, pruning of deselected imported skills, and `.addy-skills` state tracking (`scripts/addy-install.sh:146-540`, `scripts/test-addy-install.sh`).
- Future sync changes should be safer than today, especially because `scripts/copilot-install.sh` only has syntax-check coverage while addy install has behavior tests.

## Direction 1: Canonical pipeline library with thin entrypoints

This is the most conservative direction. Keep `./scripts/copilot-install.sh` as the only official command, optionally restore a root-level `./copilot-install.sh` as a compatibility shim, and move install mechanics into a shared shell library such as `scripts/lib/install-pipeline.sh`.

The shared library would own generic operations only: preflight checks, directory iteration, `*-workspace` exclusion, copy modes (`overlay tree`, `replace file`, `replace tree`, `mirror tree`), and consistent logging. Then there would be two small policy layers: one plan for local Copilot install behavior and one plan for addy import behavior. `scripts/copilot-install.sh` and `scripts/addy-install.sh` become thin wrappers over those plans.

Why it fits this repo:
- It matches the repo’s existing Bash-first helper style (`docs/agent-guides/authoring.md:19-24`).
- It preserves today’s UX with the least documentation churn.
- It lets you eliminate the real duplication with addy install instead of only papering over the missing root script.

Why it is safer:
- `*-workspace` exclusion becomes centralized, so future changes cannot forget it in one path.
- Copy semantics become explicit per asset class instead of reimplemented ad hoc.
- You can add a real `scripts/test-copilot-install.sh` beside the existing addy tests and validate shared behavior once.

Tradeoffs:
This is the simplest design and the fastest to implement correctly. It is specialized to this repo, which is good for ease of correct use, but it is less general-purpose than a manifest engine. The main misuse risk is that the library can become a “bag of helpers” unless the plan boundaries stay disciplined.

Supporting references: Google’s Shell Style Guide recommends keeping reusable shell logic in sourced libraries instead of duplicating executable scripts; the GNU `cp` docs are a good reminder that plain copy semantics are overlay-oriented, not true mirroring; mature shell installers like `nvm` also centralize helpers while keeping thin top-level commands. See: <https://google.github.io/styleguide/shellguide.html>, <https://www.gnu.org/software/coreutils/manual/html_node/cp-invocation.html>, <https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh>.

## Direction 2: Declarative manifest-driven installer engine

This direction introduces a single install manifest as the source of truth. Instead of embedding asset rules in Bash, define them declaratively: sources, destinations, exclusions, optional paths, transforms, and profile-specific behavior. Then both `scripts/copilot-install.sh` and `scripts/addy-install.sh` become very thin launchers for the same engine with different profiles.

For example, the `copilot` profile would declare:
- `skills/ -> ~/.agents/skills` with `exclude: ["*-workspace"]`
- `agents/ -> ~/.copilot/agents` as top-level files only
- optional `references/` and `hooks/`
- `.copilot/copilot-instructions.md` as a required single-file copy

The `addy` profile would declare the same destination classes plus transforms such as prefix-name, rewrite-references, resolve-deps, prune-unselected, and state-file updates.

Why it fits:
- It turns install behavior into data, which makes future asset additions safer.
- It provides one contract for both local install and external addy import.
- It makes dry-run, diff, and validation easier because the engine can reason about a structured plan.

Why it is safer:
- Adding a new installable class becomes a manifest edit instead of touching multiple scripts.
- Profile-level validation can detect missing required fields or dangerous path mappings before any copy happens.
- The same structured model can power documentation generation later.

Tradeoffs:
This is the most general-purpose design, but also the easiest to over-generalize. It introduces schema/versioning concerns and probably a parser dependency or a Python-based manifest reader. That makes correct use easier once the engine exists, but also creates more room for subtle misuse if the manifest grows too expressive. I would only choose this if you expect the set of installable asset types or install profiles to expand significantly.

Supporting references: YAML’s structure is well suited to a repo-managed manifest; Ansible and Homebrew are strong precedents for declarative install metadata driving imperative execution. See: <https://yaml.org/spec/1.2/spec.html>, <https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_intro.html>, <https://docs.brew.sh/Formula-Cookbook>.

## Direction 3: Staged publish/apply pipeline with verification and rollback

This is the safety-first option. Keep the repo tree as the source of truth, but stop copying directly into `~/.agents` and `~/.copilot`. Instead, `scripts/copilot-install.sh` becomes a small pipeline:
1. plan what would be installed
2. publish a staged install bundle
3. verify checksums, exclusions, and path invariants
4. apply the staged bundle to the real destinations with rollback records

A restored root-level `copilot-install.sh` could still exist, but only as a compatibility alias into the canonical script.

Why it fits:
- It directly addresses the biggest operational safety gap: today local install writes straight into live user directories.
- It creates a clean boundary between repo mutation and user-home mutation.
- It gives you somewhere to plug in future agent/skill sync validation before touching a live install.

Why it is safer:
- You can preview or diff changes before apply.
- Failed installs become recoverable instead of partial `cp -Rp` overlays.
- Future addy sync/import changes can reuse the same publish/verify/apply model before shipping into live Copilot directories.

Tradeoffs:
This design has the strongest “ease of correct use” story once built, but it is the heaviest. It adds state, staging, rollback semantics, and cleanup concerns. For a small repo, that can feel like infrastructure overkill unless you have already been burned by partial or unsafe installs. It is the least simple direction, but the most protective against misuse.

Supporting references: Terraform’s plan/apply split is the clearest precedent for previewable changes; POSIX `rename()` and `rsync --delay-updates` are useful building blocks for staged file replacement; Nix generations are a good model for recoverable installs. See: <https://developer.hashicorp.com/terraform/cli/commands/plan>, <https://developer.hashicorp.com/terraform/cli/commands/apply>, <https://pubs.opengroup.org/onlinepubs/9799919799/functions/rename.html>, <https://download.samba.org/pub/rsync/rsync.1>, <https://nix.dev/manual/nix/2.18/package-management/profiles>.

## Comparison

If your priority is simplicity, Direction 1 is clearly the best fit. It stays close to the repo’s current shell-centric style, minimizes new concepts, and solves the real maintenance problem by extracting shared install mechanics without inventing a new configuration layer. It is specialized rather than general-purpose, but that specialization is probably an advantage here because the repo’s install surface is small and well understood.

If your priority is future flexibility, Direction 2 goes furthest. It makes asset classes and install rules explicit, and it would scale best if you expect more install profiles, more asset categories, or richer metadata-driven sync behavior. The downside is that it is the easiest design to misuse through abstraction creep: once you have a manifest engine, every edge case tends to become another schema field.

If your priority is safety under change, Direction 3 is strongest. It creates the best boundary between “build the install set” and “mutate user home directories,” which is exactly where future agent/skill sync changes can go wrong. But that protection comes with the most implementation weight and the highest conceptual overhead for contributors.

The biggest divergence between the designs is where they put complexity. Direction 1 puts complexity in reusable shell code, Direction 2 puts it in declarative configuration and transform machinery, and Direction 3 puts it in operational safety and state management. All three can preserve current behavior; they mainly differ in how much future flexibility and safety you are willing to buy up front.

## My synthesis

If I were choosing now, I would take **Direction 1 as the base**, but borrow two ideas from Direction 3:
- an explicit computed install plan/dry-run mode before copying
- behavior tests for local install, not just `bash -n`

That hybrid gives you the best balance for this repo:
- keep `./scripts/copilot-install.sh` as the canonical documented path
- optionally restore `./copilot-install.sh` as a compatibility-only shim if you care about historical callers and stale benchmark/eval references
- extract shared install primitives so both local install and addy import stop duplicating traversal/copy policy
- add a small verification layer before mutating `~/.agents` and `~/.copilot`

I would **not** start with the full manifest engine unless you already know you want more install profiles or more asset classes soon. Right now, the repo looks more constrained than configurable.

Two decision questions remain:
1. Do you actually want to restore the root-level `./copilot-install.sh` as a compatibility alias, or would you rather declare `./scripts/copilot-install.sh` canonical and just clean up stale references?
2. Is the bigger problem “duplication in implementation” or “unsafe mutation of live install directories”? If it is the first, Direction 1 wins. If it is the second, Direction 3 becomes more attractive.
