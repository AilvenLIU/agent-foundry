# .agents

Vendor-neutral agent tooling, shared by Claude Code, Codex and other `AGENTS.md` readers.

- `skills/<name>/SKILL.md` - skill bodies. Claude Code reaches them through `.claude/skills/`.
- `constraints/` - detailed rules; `common/` always, plus `python/`, `cpp/`, `hybrid/` per profile.
- `project.yml` - the project profile (language, build system, bindings, hardware).
- `capabilities.yml` - skills and tools `init` expects to find.
- `bin/agent-*` - wrappers behind the skills; `scripts/` - their implementation.
- `hooks/` - the init gate for Claude Code and Codex.
- `adr/` - decisions worth keeping.
