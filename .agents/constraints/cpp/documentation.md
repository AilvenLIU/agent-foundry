# C++/CUDA Documentation

Documentation exists to help the next reader, not to demonstrate completeness.

- **README**: what the project is, how to build, run, and test it. Keep it true.
- **Public APIs**: a short Doxygen comment (`///`) where the contract is not
  obvious: ownership, preconditions, units, thrown errors, thread safety. Do
  not restate the signature or document trivial accessors.
- **Kernels**: state launch configuration, shared memory use, memory layout,
  and whether the host wrapper synchronises.
- **Comments** explain why, not what.
- Do not create design documents, ADRs, reports, checklists, changelogs, or
  progress notes unless the user asks. Temporary roadmap files under
  `agent_roadmaps/` are the exception and follow the roadmap skill.
- Do not put roadmap labels (`phase-2`, "Phase 3") in code, comments, or docs.
