---
name: create-project
description: Create a new Python, C++/CUDA or hybrid project from Agent Foundry, or slim down an existing project that carries an older copy of the foundry scaffolding. Use only inside the Agent Foundry source repository.
---

# Create or slim a project

## New project

```bash
python3 .agents/skills/create-project/scripts/init.py <target-dir> [--type python|cpp|hybrid]
```

It writes `AGENTS.md` (common section plus the language fragments), a one-line `CLAUDE.md`
that imports it, the relevant skills in `.agents/skills/` (linked from `.claude/skills`),
a `.gitignore`, a minimal CMake/pyproject scaffold for native and hybrid types, and a git
repository with one commit on `main`. Python projects: run `poetry init` next.

## Existing project with the old scaffolding

Older projects carry `.agents/constraints`, `scripts`, `bin`, `hooks`, `adr`, `.claude`
stubs and settings, `.codex`, the master-merge-gate workflow, `CONTRIBUTING.md`, and a long
`AGENTS.md`/`CLAUDE.md`. To slim one:

1. Replace `AGENTS.md` with the composed template (common + language fragments, see
   `_FRAGMENTS` in `init.py`). Move project-specific facts from the old file into a short
   `## Project` section; drop anything restating the template. `CLAUDE.md` becomes `@AGENTS.md`.
2. Delete the old scaffolding listed above. Keep project-owned skills and files.
3. Copy the needed skills from `.agents/skills/` and point `.claude/skills` at them.
4. Do not bulk-delete the project's tests or docs. List the largest test and doc areas and
   let the user decide what to cut. Finish or archive any old-format `agent_roadmaps/` phases.
5. Projects that used the develop/master release shim now follow the plain feature-branch flow;
   say so in the summary.
