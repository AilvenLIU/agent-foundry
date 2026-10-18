# Agent Foundry

A personal hub of agent skills, constraints and blueprints for Python, C++/CUDA and hybrid
projects. It works with Claude Code and with Codex, Cursor and other `AGENTS.md` readers.

The design goal is small instructions that leave capable coding agents free to build the
product: proportional testing and verification, no process machinery around the code, and
roadmap-driven phases for work that spans sessions.

## Create a project

```bash
python3 .agents/skills/create-project/scripts/init.py /path/to/project
```

Choose Python, C++/CUDA or hybrid. The project gets `AGENTS.md` (common rules plus language
fragments), a short `CLAUDE.md` importing it, `.agents/` (skills, constraints, tooling),
`.claude/` and `.codex/` wiring, the `commit-msg` hook, a minimal build scaffold, and one
commit on `main`. Hybrid projects bind Python to C++/CUDA with nanobind only.

## Skills

| Skill | Use |
|-------|-----|
| `init` | Session start: profile, capability audit, constraint manifest |
| `roadmap` | Work spanning several sessions: dependency-ordered phases that each end in something that runs |
| `pre-commit`, `build`, `dependency`, `python-env-setup` | Everyday workflow wrappers |
| `navigate`, `context7`, `karpathy-guidelines` | Orientation, current docs, working discipline |
| `service-cicd`, `deploy-service`, `gpu-ci` | CI/CD, host deployment, GPU CI |
| `check-constraints` | Diagnose policy drift (optional) |
| `create-project` | This repository only; also slims older projects |

## Tests

```bash
python3 -m pytest tests .agents/scripts/tests
```

## Licence

CC BY-NC-SA 4.0. See `LICENSE`. Generated projects do not inherit it.
