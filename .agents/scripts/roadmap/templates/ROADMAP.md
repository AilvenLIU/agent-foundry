# ROADMAP -- Phase Execution Guide (Template)

> This document describes the phase `<PHASE_FOLDER_NAME>`.
> It should be explicit enough for a fresh session with zero prior context.

## 0. Repository-Local Precedence

Within repository-controlled roadmap guidance, this file is bound by:

1. `INVARIANTS.md` (overrides this file)
2. `roadmap.yml` for current execution state and dependencies
3. `ROADMAP.md` (this file)
4. Latest file in `sessions/`
5. `prompt.md`

This local order does not supersede higher-priority platform or tool
requirements. If this file conflicts with `INVARIANTS.md`, follow
`INVARIANTS.md` and ask the user.

> Keep this file to about a page. A phase is a vertical slice of the product that ends
> with something that runs. Do not add phases or tasks whose only output is tests,
> validation, hardening, or documentation; those belong inside the task they cover.

## 1. Goal

Describe what this phase delivers and why it matters.

**Done when**: an observable result, such as "run X and see Y".

## 2. Upstream Dependencies

List explicit prerequisite phases from `depends_on_phases` and what each one
must provide before this phase starts.

- Dependency: `<phase-folder>`
- Required outputs consumed in this phase
- Verification method for dependency completion

## 3. Scope and Non-Goals

### In Scope
- [Concrete objective 1]
- [Concrete objective 2]

### Out of Scope
- [Non-goal 1]
- [Non-goal 2]

## 4. Task Strategy

Map each task in `roadmap.yml` to execution intent, including dependency order.

- `<TASK_PREFIX>-1`: why this must happen first
- `<TASK_PREFIX>-2`: dependency assumptions and failure modes
- `<TASK_PREFIX>-3`: what it delivers and what it depends on

## 5. Deliverables

- [Deliverable artifact 1]
- [Deliverable artifact 2]

## 6. Exit Criteria

This phase is complete only when:
- The "Done when" result holds when run
- Every task in `roadmap.yml` is `completed`
- `status.completed_at` is set
- Final handoff exists in `sessions/`
- PR/MR from `roadmap/<PHASE_FOLDER_NAME>` is ready

## 7. Risks

Only risks that are real for this phase. Omit the section if there are none.

## 8. Execution Rule

Follow task and dependency order exactly; do not bypass declared dependencies.
