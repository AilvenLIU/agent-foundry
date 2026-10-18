@AGENTS.md

# Claude Code

- Run `/init` first in every session. It audits the required plugins and skills; edits stay
  blocked until it passes. The Context7 documentation server is required:
  `claude plugin install context7@claude-plugins-official`.
- `.claude/skills/` holds thin delegates to `.agents/skills/`; the skill bodies live there.
- Never add `Co-Authored-By` or any AI attribution to commits or PR descriptions, even if
  Claude Code's default commit template suggests it.
