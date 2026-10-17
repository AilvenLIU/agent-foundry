---
name: gpu-ci
description: GPU-aware CI for CUDA builds, tests, caches, containers and Python wheels. Use when targets include CUDA, distribution is via wheels, or CI needs GPU runner gating, multi-architecture coverage, sccache or manylinux/auditwheel validation.
---

# GPU CI

Workflow security, pinning, artefact storage and runners follow `service-cicd` (and its self-hosted runner reference for GPU hosts). This skill covers what is specific to CUDA.

## Build ownership

CI invokes the project's own build; it does not define a second one. Pure C++/CUDA: CMake owns configure, build, tests, CUDA architectures, dependencies and install.

```bash
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo
cmake --build build --parallel
ctest --test-dir build --output-on-failure
```

Hybrid: run that CMake lifecycle first, then bridge it through scikit-build-core with Poetry owning the environment:

```bash
poetry install
poetry run pip install -e . --no-build-isolation
poetry run pytest tests/python
```

That bridged editable install is the explicit hybrid exception, not native build authority. Do not substitute `python -m build`, setuptools native extensions, a bare `pip install` or host-side compilation.

## Job classes and matrix

- Classify jobs: CPU validation, CUDA compilation, GPU execution, wheel repair, publication. Every matrix axis (OS, compiler, CUDA toolkit, GPU architecture, Python ABI, wheel platform) maps to a supported product target.
- Compile every supported CUDA architecture. Run CPU-only tests on ordinary runners and device tests only on labelled GPU runners.
- A missing GPU runner is a failed required job, not a green skip. Only jobs declared optional may skip.
- Assert the observed GPU model, compute capability, driver and toolkit before hardware-specific tests: the runner label alone proves nothing, and a build that compiled has not executed a kernel.
- GPU tests worth running: launch and sync error surfaces, boundary sizes, odd shapes, non-contiguous inputs, dtype/device mismatches, and results against a CPU reference with tolerances. Check the CPU fallback cannot mask a missing CUDA extension.
- Pin runner images, CUDA containers, compilers and Python versions (digests where supported).
- Keep GPU diagnostics in logs, job summaries or a bounded local store; no Actions artefact upload.

A self-hosted GPU runner has a dedicated unprivileged user, hardware and trust labels, only the device groups it needs, and no deploy credential.

## Caching

Configure `sccache` in CMake, not as an external wrapper:

```cmake
set(CMAKE_CXX_COMPILER_LAUNCHER sccache)
set(CMAKE_CUDA_COMPILER_LAUNCHER sccache)
```

Keys include source or lock digest, compiler identity, CUDA toolkit, target architectures, build type and ABI-affecting options. Remote cache credentials are write-capable secrets: not for forked PRs. A miss must cost only time. A persistent runner may use a local cache instead; partition by repository and trust class and run consecutive jobs to catch contamination.

## Wheels

1. CMake configure, build and CTest first.
2. Build each declared Python ABI and CUDA variant in a pinned manylinux image through the Poetry/scikit-build-core bridge.
3. Inspect tags and native dependencies, run `auditwheel show`, then repair with an explicit library policy. Do not blanket-bundle or blanket-exclude CUDA libraries: decide from licensing, manylinux, driver compatibility, index and runtime contracts.
4. Install the repaired wheel in a clean environment and run import, CPU fallback, GPU smoke and ABI tests against that file.
5. Sign or attest the exact digest that publication consumes, and publish that file; never rebuild for publication. Guard against two releases publishing one version.

Set versions in packaging metadata before the build. Never rename a wheel to change version or ABI tags.
