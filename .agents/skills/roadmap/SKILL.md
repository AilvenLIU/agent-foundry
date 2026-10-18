---
name: roadmap
description: Plan and track work that spans several sessions or phases using one ROADMAP.md file. Use when a task is too large for one session or the user asks for a roadmap or phased plan.
---

# Roadmap

Keep one file, `agent_roadmaps/ROADMAP.md`. It is temporary coordination state, not
project documentation.

```markdown
# <goal in one line>

## Decisions
- <settled choice and why, one line each>

## Phases
1. [x] <phase> - done when: <observable acceptance criterion>
2. [ ] <phase> - done when: ...
   - [ ] <task>

## Next
<what to do first in the next session>
```

- The file stays a page or two. Phases are ordered by dependency and each has an
  observable "done when", checked by running the thing, not by new harnesses or reports.
- Work on the first unfinished phase. Do not start a later phase early, and do not
  re-open settled decisions without a reason.
- At the end of a session, tick what is done and update `Next`. That is the handoff.
- When every phase is done, delete `agent_roadmaps/ROADMAP.md`. Keep roadmap labels
  out of code, config and docs.
