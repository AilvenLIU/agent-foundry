# Python Documentation

Documentation exists to help the next reader, not to demonstrate completeness.

- **README**: what the project is, how to set it up, run it, and test it. Keep
  it true; update it when those facts change.
- **Docstrings**: Google style, on public functions and classes whose name and
  signature do not already explain them. State units, invariants, and raised
  errors. Do not restate the signature.
- **Comments** explain why, not what.
- Do not create design documents, ADRs, reports, checklists, runbooks,
  changelogs, or progress notes unless the user asks. Temporary roadmap files
  under `agent_roadmaps/` are the exception and follow the roadmap skill.
- Never put secrets or real credentials in examples.
- Do not put roadmap labels (`phase-2`, "Phase 3") in code, config, or docs.
