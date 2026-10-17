---
name: cuda
description: Writing, reviewing or debugging CUDA code (.cu/.cuh, kernels, streams, device memory, tensor cores, CUDA graphs). Use for async error handling, launch configuration, architecture targets, numerical tolerance tests, compute-sanitizer and Nsight profiling.
---
# CUDA

Project-level rules (toolchain, CMake, RAII, testing stance) are in `AGENTS.md`. This file holds the kernel-level detail.

## Project decisions

- CUDA Toolkit 11.0 minimum, 12.0+ preferred. Compute capability 7.0+ (tensor cores need 7.0+).
- Architectures: `CMAKE_CUDA_ARCHITECTURES native` for local builds; shipped builds use `80 86 89 90`. Add 70/75 (legacy), 87 (Jetson Orin) or 100 (Blackwell, needs a recent 12.x toolkit) only when the project targets them. Never claim support for an architecture you did not compile for or run on.
- Per-target nvcc flags in use: `--expt-relaxed-constexpr`, `--expt-extended-lambda` (only if device lambdas are used), `--ptxas-options=-v` when tuning. `-use_fast_math` changes numerics, so enable it only when the tolerance tests still pass.
- Device-side warnings: `-Xcompiler=-Wall,-Wextra`; `-Werror` applies to first-party code only.

## Error surfaces

- `cudaGetLastError()` right after a launch catches only launch failures (bad configuration, missing kernel image). Execution failures (illegal address, assert, timeout) are reported later by whichever API call or sync happens next, possibly an unrelated one. A failure after a launch is often not about that call.
- Sticky errors (illegal address, hardware exception) poison the context. Everything after returns errors until the process restarts. Do not "recover" and continue.
- Do not `cudaDeviceSynchronize()` after every launch in production paths. Check the launch, and check execution at the points where results are consumed (copy back, stream/event sync). In debug builds and tests use `CUDA_LAUNCH_BLOCKING=1` or sync after launch so the failing kernel is identified.
- `cudaGetLastError()` clears the error. Use `cudaPeekAtLastError()` when you only want to look.
- Destructors must not throw: in RAII wrappers call `cudaFree`/`cudaStreamDestroy` and log or ignore the status. After a sticky error, cleanup calls fail too, which is expected.
- A launch with a zero-sized grid or block is an invalid-configuration error. Guard `n == 0`.
- Limits that fail only at launch: at most 1024 threads per block, `gridDim.y/z` at most 65535, and dynamic shared memory above 48 KB needs `cudaFuncSetAttribute(..., cudaFuncAttributeMaxDynamicSharedMemorySize, ...)`.

## Memory, streams, lifetime

- `cudaMemcpyAsync` with pageable host memory is not truly asynchronous and may stage through a bounce buffer. Use pinned memory (`cudaMallocHost`) for overlap. Host buffers must stay alive and unmodified until the stream reaches the copy.
- `cudaFree` and `cudaMalloc` synchronise the device implicitly. In pipelines use stream-ordered `cudaMallocAsync`/`cudaFreeAsync` with a memory pool (raise `cudaMemPoolAttrReleaseThreshold` to retain memory). Free on the same stream, or order it with an event, otherwise you free memory a kernel is still using.
- The legacy default stream synchronises with other blocking streams. Use explicit streams (or `--default-stream per-thread`) when overlap matters, and pass the stream to every launch and copy. A forgotten stream argument silently serialises.
- Time with CUDA events, not host clocks. Warm up first.
- Resources belong to a device. With multiple GPUs call `cudaSetDevice` in each thread before using them, and destroy on the device that created them.
- Unified memory (`cudaMallocManaged`) is for convenience or oversubscription. Prefetch (`cudaMemPrefetchAsync`) on hot paths, and say in a comment why it is used.
- Use `size_t` for element counts and index maths. `int` indices overflow past 2^31 elements and the symptom is wrong data, not a crash. For large `n` use a grid-stride loop.
- CUDA graphs suit repeated, fixed launch sequences that are launch-bound. During stream capture, synchronising calls and `cudaMalloc` are illegal, so use stream-ordered allocation. Update parameters on the instantiated graph (`cudaGraphExecKernelNodeSetParams`) instead of rebuilding.

## Kernels

- Default 1D launch: 256 threads, grid `(n + 255) / 256`, bounds check `if (i < n)`. Tune from profiler data, not guesses. `__launch_bounds__` only when `-Xptxas -v` shows register pressure or spills.
- Every thread in the block must reach `__syncthreads()`. Never put it inside a divergent branch or after an early `return`.
- Check coalescing and shared-memory bank conflicts before reaching for fancier tricks.
- Guard architecture-specific device code with `__CUDA_ARCH__ >= N`. It is undefined in host code. If the architecture list lacks a target, the runtime fails with "no kernel image is available". Dispatch at runtime from `prop.major * 10 + prop.minor` and throw for below 70.
- Feature floors: WMMA 70, BF16/TF32/`cp.async` 80, FP8 89, WGMMA/TMA 90. Prefer CUTLASS 3.x / CuTe over raw PTX on Hopper (CUTLASS 2.x for Ampere and older). Use `mma`/WMMA fragments with FP32 accumulation.
- Mixed precision: FP32 master weights and accumulation. BF16 for training activations and gradients on Ampere+, FP16 on Volta (needs loss scaling), FP8 E4M3 forward and E5M2 gradients on Ada/Hopper.
- Document each kernel: launch configuration, shared memory bytes, memory layout, whether the host wrapper synchronises.

## Numerics and tests

- Compare with a CPU reference computed in higher precision (double) on identical inputs, or cuBLAS/cuDNN/PyTorch when one exists. Without a reference, test invariants (softmax rows sum to 1, conservation, symmetry).
- Default tolerances (rtol = atol): FP32 1e-5, FP16 1e-3, BF16 1e-2, FP8 5e-2. For fused or multi-stage kernels multiply by `sqrt(stages)`. Tighten only with evidence.
- Atomics and parallel reductions reorder floating-point additions, so results vary run to run. Use tolerances, or a deterministic variant when bitwise equality is required.
- Shapes worth a case: 0 (if allowed), 1, sizes not divisible by block or tile (1023), power-of-two boundaries, odd inner dimensions (D = 63), and the largest advertised size.
- Test on hardware you have. Compile-only checks do not cover a different architecture's behaviour.

## Debugging and profiling

- `compute-sanitizer`: default memcheck (add `--leak-check full`), then `--tool racecheck`, `synccheck`, `initcheck` as symptoms suggest. It replaces the removed `cuda-memcheck`. Run it on the test binary, once, when you change kernel or memory code.
- Build with `-lineinfo` (not `-G`) to get source lines in sanitizer and profiler output. `-G` disables optimisation, so use it only for `cuda-gdb`.
- Profile with `nsys profile --stats=true` for timeline and overlap questions, and `ncu --kernel-name <k>` for per-kernel limits. `nvprof` is gone. Profile before optimising and only for performance-sensitive changes.
- Benchmark method: 10 warmup iterations, median of 100, CUDA events, realistic sizes. Record the GPU and toolkit version with the number.
