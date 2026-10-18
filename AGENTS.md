# Agent Foundry

Personal, vendor-neutral hub of agent skills, constraints and project blueprints for Python,
C++/CUDA and hybrid projects. `/create-project` generates a project whose `AGENTS.md` carries
the standing rules for Claude Code, Codex, Cursor and other `AGENTS.md` readers.

## Layout

- `templates/common/` - `AGENTS.md` and `CLAUDE.md` shared by every project.
- `templates/<python|cpp|hybrid>/` - `AGENTS.md` fragment, `.gitignore`, `project.yml`. The
  generator appends fragments to the common file (hybrid = cpp + python + hybrid).
- `.agents/skills/` - skills; `.claude/skills/` holds thin delegates. `create-project` stays here.
- `.agents/constraints/` - detailed rules, selected per project profile by `init`.
- `.agents/scripts/`, `.agents/bin/`, `.agents/hooks/` - the tooling behind the skills.
- `.githooks/commit-msg` - rejects `Co-Authored-By` and AI-attribution lines. Enable it with
  `git config core.hooksPath .githooks`.

## Editing this repo

The purpose is to make coding agents build focused software, not to police them.

- Governing principle: proportionality. Process, tests, validation and documentation are sized by
  the real complexity and risk of the work, so effort goes to the feature. The roadmap (phases,
  dependencies, a short handoff) is kept because it carries intent across sessions; its ceremony
  is not.
- Instructions state the user's decisions and the pitfalls models actually hit. Do not teach
  general engineering, and do not repeat a rule in two places.
- Do not add checklists, mandatory review rounds, coverage targets, report formats or enforcement
  scripts for prose. If a rule matters, one sentence is enough.
- Skills are for knowledge needed only sometimes: a `SKILL.md` with a precise description plus a
  few reference files.
- Commits never carry `Co-Authored-By` or any AI attribution. Python binding library is nanobind
  only; a fork keeps its upstream's.
- Workflow: feature branch, PR to `master`.

Run the tests with `python3 -m pytest tests .agents/scripts/tests` (needs pytest and PyYAML).
