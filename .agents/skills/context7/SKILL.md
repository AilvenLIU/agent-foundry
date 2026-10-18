---
name: context7
description: Look up current official library or framework documentation through the Context7 MCP server. Use when an API, version, option or migration may have changed, or when precise upstream behaviour matters.
---

# Context7

Use the Context7 MCP tools: resolve the library id, then query docs for the specific
question. Prefer this over memory for fast-moving libraries. If the server is not
configured, say so and fall back to the project's own docs or source.

Setup for Claude Code: `claude plugin install context7@claude-plugins-official`.
For other agents, add the MCP endpoint `https://mcp.context7.com/mcp` to their settings.
