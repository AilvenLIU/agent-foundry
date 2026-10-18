# Python Testing

> Tests exist to catch real regressions in logic that matters. There is no
> coverage target and no required test count.

## Tools and layout

- pytest, run with `poetry run pytest`. Add it with the dependency workflow
  (`.agents/bin/agent-dependency add pytest --dev`).
- Tests live in `tests/`, named `test_*.py`. Shared fixtures go in
  `tests/conftest.py` only when two or more files use them.
- Prefer real objects, a temp directory, or a real local service over mocks.
  Mock only what you cannot run (paid APIs, the network, the clock).

## What to test

- Core logic that could plausibly break: calculations, parsing, state
  transitions, boundary conditions, error paths that callers depend on.
- A regression test for each bug fixed.
- One end-to-end path through the feature, run for real.

## What not to test

- Trivial glue, getters, dataclasses, configuration, docs or instruction text,
  framework behaviour, or code whose only risk is a typo the type checker finds.
- Anything written only to raise a coverage number or fill a checklist.
- Do not build test frameworks, harnesses, fixture generators, mutation or
  contract-validation suites, or CI gates beyond what the project already has,
  unless a concrete risk calls for one.

Test code is usually smaller than the code it covers. If it is much larger,
the tests are probably testing the wrong thing.

## Before committing

Run the tests that cover your change and the formatter and linter (see
`/pre-commit`). Do not commit failing tests. Fixing or deleting a test that no
longer describes real behaviour is fine; disabling it to pass is not.
