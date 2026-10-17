# Agent Foundry

A personal hub of agent instructions, skills and blueprints for Python, C++/CUDA and hybrid
projects. It works with Claude Code and with Codex, Cursor and other `AGENTS.md` readers.

The design goal is small instructions that leave capable coding agents free to build the
product: simplicity by default, testing and verification in proportion to real risk, and no
process machinery around the code.

## Create a project

```bash
python3 .agents/skills/create-project/scripts/init.py /path/to/project --type python   # or cpp, hybrid
```

The project gets:

- `AGENTS.md` - the standing instructions (common section plus language fragments)
- `CLAUDE.md` - one line importing `AGENTS.md`
- `.agents/skills/` - on-demand skills, also exposed to Claude Code through `.claude/skills`
- a minimal CMake or pyproject scaffold for native and hybrid types

## Skills

| Skill | Use |
|-------|-----|
| `roadmap` | Work spanning several sessions |
| `context7` | Current library documentation |
| `python-env` | pyenv and Poetry recovery (Python, hybrid) |
| `cuda` | Kernel-level CUDA guidance (C++, hybrid) |
| `python-bindings` | Native-to-Python boundary (hybrid) |
| `gpu-ci`, `service-cicd`, `deploy-service` | CI/CD and host deployment |
| `create-project` | This repository only; also slims older projects |

## Tests

```bash
python3 -m pytest tests
```

## Licence

CC BY-NC-SA 4.0. See `LICENSE`. Generated projects do not inherit it.
