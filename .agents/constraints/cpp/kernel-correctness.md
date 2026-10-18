---
id: cpp/kernel-correctness
name: Kernel Correctness
description: Numerical correctness checks for CUDA kernels
category: cpp
status: active
applies_to:
  - "*.cu"
  - "*.cuh"
severity: advisory
---

# Kernel Correctness

Line coverage says nothing about whether a kernel computes the right numbers.
Check the numbers, once, with a small set of cases.

- Compare against a reference on identical inputs: a CPU implementation in
  double, cuBLAS/cuDNN/PyTorch when one exists, or a closed-form answer. Without
  a reference, test invariants (softmax rows sum to 1, conservation, symmetry).
- Default tolerances (rtol = atol): FP32 1e-5, FP16 1e-3, BF16 1e-2, FP8 5e-2.
  Multiply by `sqrt(stages)` for fused kernels. Tighten only with evidence.
- Atomics and parallel reductions reorder floating-point additions, so results
  vary run to run. Use tolerances, or a deterministic variant when bitwise
  equality is required.
- Cases worth one test each: size 1 (and 0 if allowed), sizes not divisible by
  the block or tile (e.g. 1023), power-of-two boundaries, odd inner dimensions
  (D = 63), and the largest advertised size.
- Test on hardware you have; do not claim an architecture you did not run on.
- After changing kernel or memory code, run `compute-sanitizer` (memcheck, then
  racecheck/synccheck/initcheck as symptoms suggest) on the test binary once.
- Benchmark only to back a performance claim: warm up, use CUDA events, report
  the median with the GPU and toolkit version. A benchmark is not a CI gate.
