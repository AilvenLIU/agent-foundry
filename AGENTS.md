# Agent Foundry

Personal hub of agent instructions, skills and project blueprints for Python,
C++/CUDA and hybrid projects. Generated projects get a short `AGENTS.md`, a one-line
`CLAUDE.md` importing it, and a few on-demand skills. Nothing else.

## Layout

- `templates/common/` - `AGENTS.md` section and `CLAUDE.md` shared by every project.
- `templates/<python|cpp|hybrid>/` - `AGENTS.md` fragment, `.gitignore`, `poetry.toml`.
  The generator appends fragments to the common section (hybrid = cpp + python + hybrid).
- `.agents/skills/` - skills, copied into generated projects. `.claude/skills` is a symlink
  to it, so Claude Code and Codex read the same files. `create-project` stays here.
- `tests/` - a test for project generation.

## Editing this repo

The purpose is to make coding agents build focused software, not to police them. Keep it small.

- Instructions state the user's decisions and the pitfalls models actually hit. Do not
  teach general engineering, and do not repeat a rule in two places.
- Do not add checklists, mandatory review rounds, coverage targets, audit or session
  machinery, report formats or enforcement scripts for prose. If a rule matters, one
  sentence in `AGENTS.md` is enough.
- Skills are for knowledge needed only sometimes. A skill is a `SKILL.md` with a precise
  description, plus at most a few reference files.
- Do not write tests that check instruction text. Test code that has logic.

Run the tests with `python3 -m pytest tests`.
