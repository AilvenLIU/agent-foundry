# C++/CUDA Testing

> Tests exist to catch real regressions in logic that matters. There is no
> coverage target and no required test count.

## Tools and layout

- CTest runs the tests (`ctest --test-dir build --output-on-failure`). GoogleTest
  or Catch2 when the project already uses one; a plain `main` that returns
  non-zero is fine for a small project.
- Tests live under `tests/`, named `test_<module>.cpp` / `.cu`, registered from
  `tests/CMakeLists.txt` against the same targets the library exposes.
- Prefer exercising the real code over mocks and test doubles.

## What to test

- Core algorithms and data structures: boundaries, empty and size-1 inputs,
  error paths callers depend on, numerics and overflow.
- A regression test for each bug fixed.
- CUDA kernels: compare against a CPU reference (computed in higher precision)
  with a dtype-appropriate tolerance, on sizes that include 1 and sizes not
  divisible by the block or tile. See `kernel-correctness.md`.

## What not to test

- Trivial glue, accessors, configuration, build scripts, docs, or anything
  written only to raise a coverage number.
- Do not build test frameworks, fixture generators, harness layers, validation
  suites, or CI gates beyond what the project already has, unless a concrete
  risk calls for one.

## When to go deeper

When you change memory handling, threading, or kernels, run the relevant
sanitizer once: ASan/UBSan, TSan for threads, `compute-sanitizer` for device
code. Benchmarks back performance claims; they are not CI gates.

## Before committing

Build and run the tests that cover your change, then the formatter and linter
(see `/pre-commit`). Do not commit failing tests. Do not disable one to pass.
