# Agentic Team (Parallel Sub-Agents)

Sub-agents are an option, not a duty. Use them when they save real time or
protect the main context.

## When it helps

- The work splits into independent, read-heavy pieces (codebase search,
  documentation lookup, comparing several options) that would otherwise fill
  the main context.
- The pieces touch disjoint files, or only one of them writes.

## When it does not

- The remaining work fits in a few direct tool calls.
- The pieces share write targets, or depend on each other's results.
- It would only be used to add review or validation layers around finished work.

## How

- Give each sub-agent a self-contained prompt and say what artefact you expect.
- Synthesis and the answer to the user stay with the main agent.
- A sub-agent report is evidence, not ground truth: verify any claim that names
  a specific file, symbol, or flag before acting on it.
- Parallel work never bypasses protected-branch rules or roadmap dependency order.
- In Claude Code use the `Agent` tool (`Explore` for search, `Plan` for design,
  `general-purpose` otherwise) and launch independent calls in one turn.
