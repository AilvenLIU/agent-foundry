---
name: create-project
description: Create a new Python, C++/CUDA or hybrid project from Agent Foundry, or slim down an existing project that carries an older copy of the foundry scaffolding. Use only inside the Agent Foundry source repository.
---

# Create or slim a project

## New project

```bash
python3 .agents/skills/create-project/scripts/init.py <target-dir>
```

It prompts for the project type, then writes `AGENTS.md` (common section plus language
fragments), a `CLAUDE.md` that imports it, `.agents/` (skills, constraints, tooling),
`.claude/` and `.codex/` wiring, the `commit-msg` hook, `.gitignore`, a minimal CMake or
pyproject scaffold for native and hybrid types, and a git repository with one commit on `main`.
Python projects: run `poetry init` next. Hybrid projects use nanobind only.

## Existing project with an older copy

Older projects may carry the develop/master release shim (`master-merge-gate` workflow,
`agent-release`, the `branch-governance` skill, ADRs 0002-0005), `CONTRIBUTING.md`, long
`AGENTS.md`/`CLAUDE.md` files, and the foundry's own `.agents/scripts/tests`. To update one:

1. Replace `AGENTS.md` with the composed template (common plus fragments, see `_FRAGMENTS` in
   `init.py`) and `CLAUDE.md` with `templates/common/CLAUDE.md`. Move project-specific facts from
   the old files into a short `## Project` section; drop anything restating the template.
2. Refresh `.agents/` and `.claude/skills` from this repository; keep project-owned skills.
3. Remove the shim pieces listed above and move to feature branch -> PR -> default branch.
4. Do not bulk-delete the project's tests or docs. List the largest test and doc areas and let the
   user decide what to cut. Keep `agent_roadmaps/`: the roadmap tool reads existing
   `roadmap.yml` files; fold any invariant that still matters into the phase's `ROADMAP.md` and
   do not write phases ahead of time.
