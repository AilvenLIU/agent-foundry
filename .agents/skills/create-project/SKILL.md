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

Updating a repo from the template is a per-file three-way merge, not a copy:

1. Generate a reference of the same type: `printf '1\n' | python3 .agents/skills/create-project/scripts/init.py /tmp/ref` (1 python, 2 cpp, 3 hybrid).
2. On a branch cut from the repo's integration branch, run
   `python3 .agents/skills/create-project/scripts/sync.py <repo> /tmp/ref`. It detects the
   foundry commit the repo last synced from (or take `--base <commit>`), then per file:
   template-owned and untouched -> updated; changed only by the repo -> kept; changed by both ->
   merged; template-dropped and untouched (the old release shim, self-tests) -> removed. Resolve
   any `CONFLICT` by hand: take the template when it already contains the repo's fix, keep the
   repo's file when it carries project behaviour (for example a bounded build or a stricter
   commit guard).
3. `AGENTS.md` = `templates/common/AGENTS.md` + the language fragments (`_FRAGMENTS` in
   `init.py`) + a short `## Project` section of facts an agent cannot read from the code, taken
   from the repo's own README and docs. `CLAUDE.md` = `templates/common/CLAUDE.md`.
4. A CPU-only C++ or hybrid project has no CUDA: delete the CUDA bullets from the generated
   `AGENTS.md` and keep the rest. Adapt layout and build commands to the repo's real ones.
5. Remove the project's own shim assets (merge-gate and metadata-guard workflows, gate script, their
   tests). Do not bulk-delete product tests or docs; list the largest areas and let the user decide.
   Keep `agent_roadmaps/`: the roadmap tool reads existing `roadmap.yml` files.
6. Check: workflows and manifests parse, the init audit passes, `verify_skills.py` passes,
   `agent-roadmap validate` passes for every phase, and the repo's own lint and targeted tests.
