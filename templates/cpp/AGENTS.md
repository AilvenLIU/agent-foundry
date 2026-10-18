## C++/CUDA

Core logic is implemented in C++/CUDA, not in Python helpers, glue or prototypes.

### Toolchain

- C++17 minimum, C++20 where the toolchain allows. Extensions off (`CMAKE_CXX_EXTENSIONS OFF`). Set the CUDA standard to match.
- CMake 3.24+, Ninja generator.
- CUDA Toolkit 11.0 minimum, 12.0+ preferred. Compute capability 7.0+ (Volta and newer).
- Host compilers: GCC 9+, Clang 10+. With CUDA 11.5+ use GCC 10+. The host compiler must be one the installed nvcc supports.
- `project(<name> VERSION x.y.z LANGUAGES CXX CUDA)` in the root `CMakeLists.txt` is the version source of truth.

### Build and test

CMake owns the native build graph. Direct commands, always out-of-source:

```bash
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo
cmake --build build -j
ctest --test-dir build --output-on-failure
```

- Targets only: `target_link_libraries` / `target_include_directories` / `target_compile_options` with explicit visibility. No global `include_directories`, `add_definitions` or `link_libraries`.
- First-party targets build with `-Wall -Wextra -Wpedantic -Werror` set per target (`PRIVATE`), not globally. Third-party headers are `SYSTEM` includes so their warnings do not break the build. Pass host flags to nvcc with `-Xcompiler=`.
- `CMAKE_CUDA_ARCHITECTURES`: `native` for local builds; `80 86 89 90` for anything shipped. Add 70/75, 87 or 100 only when the project targets them.
- Cross-compilation goes through a toolchain file in `cmake/Toolchains/`.
- Options are declared in the root `CMakeLists.txt`: `PROJECT_ENABLE_TESTS` (ON), `PROJECT_ENABLE_BENCHMARKS` (OFF), `PROJECT_ENABLE_PYTHON` (OFF).

### Layout

```text
CMakeLists.txt   cpp/{include,src}   cuda/{include,src}   tests/   benchmarks/
cmake/   (toolchain files and CPM setup, created when first needed)
3rdparty/{cpm-cache,patches,licenses}   (created when first needed)
```

The generated `cpp/CMakeLists.txt` is an interface library and `tests/CMakeLists.txt` is empty. Wire in `cuda/`, `benchmarks/` and real targets when the first code arrives. Keep `3rdparty/cpm-cache/` out of Git. Name test files `test_<module>.cpp` / `.cu`, benchmarks `benchmark_<feature>.cpp`.

### Dependencies

- CPM is the default for source-buildable C++ libraries. On the first one, add a pinned `cmake/CPM.cmake` release, declare every dependency in `cmake/Dependencies.cmake` with `CPM_SOURCE_CACHE` set to `3rdparty/cpm-cache`, and link the imported target (`fmt::fmt`), not raw paths.
- Pin by tag, commit SHA or `URL_HASH`. Never a floating branch (`main`, `master`, `develop`). Do not add FetchContent as a second mechanism.
- Do not install C++ libraries with `apt`, `brew` or similar. CUDA Toolkit, cuDNN, NCCL, TensorRT, MPI, drivers and compilers are discovered prerequisites: `find_package`, cache variables or toolchain files.
- Patches go in `3rdparty/patches/`, licence notes in `3rdparty/licenses/`. Do not vendor large trees.
- Conan, vcpkg, Bazel and git submodules need a written justification from the user (a short ADR) first.

### Style and static analysis

- clang-format with a root `.clang-format` (Google base, 4-space indent, 100 columns, left pointer alignment). clang-tidy with a root `.clang-tidy` (`bugprone-*`, `performance-*`, `modernize-*`, `cppcoreguidelines-*` minus noisy checks) using `compile_commands.json` (`CMAKE_EXPORT_COMPILE_COMMANDS=ON`).
- Run both on the files you changed. Fix real findings, add a specific `NOLINTNEXTLINE(check)` with a reason for false positives, never a blanket `NOLINT`. cppcheck is optional.
- Naming: files `snake_case` (`.hpp`, `.cpp`, `.cu`, `.cuh`), types `PascalCase`, functions and variables `snake_case`, members `trailing_`, constants `kPascalCase`, namespaces lowercase. Macros are `UPPER_CASE` with a project prefix. Use `#pragma once`. Follow the existing code if it differs.
- Document public APIs with short Doxygen comments where the contract is not obvious. For kernels state launch configuration, shared memory use, ownership and whether the call synchronises.

### Testing

- Register tests with CTest. Use GoogleTest (or Catch2) only if the project already has one; otherwise a plain `main` returning non-zero is fine for a small project.
- CUDA kernels: compare against a CPU reference with a dtype-appropriate tolerance. Include sizes that are not multiples of the block or tile, size 1, and size 0. See `.agents/constraints/cpp/kernel-correctness.md`.
- When you touch memory handling, threading or kernels, run the relevant sanitizer once: ASan/UBSan (`-fsanitize=address,undefined`), TSan for threads, `compute-sanitizer` for device code.
- Benchmarks are for performance claims, not CI gates. Build with `-DPROJECT_ENABLE_BENCHMARKS=ON`.

### C++/CUDA rules worth stating

- Ownership is RAII. No owning raw pointers, no `new`/`delete` in application code. Wrap device memory, streams, events and handles in move-only types. Destructors never throw, including cleanup calls such as `cudaFree`.
- Error policy: throw exceptions derived from `std::exception`. Do not use `catch (...)` unless it rethrows. Do not use exceptions for control flow.
- Check every CUDA API call and every kernel launch (`CUDA_CHECK`-style macro that throws with file and line, and a `cudaGetLastError()` after each launch). Synchronous failure is not the only failure mode, so read `.agents/constraints/cpp/cuda.md` before writing kernels.
- Use C++ casts, not C-style casts. No `using namespace` in headers.
- ABI-sensitive choices (exported symbols, standard library, `-D_GLIBCXX_USE_CXX11_ABI`, struct layout in public headers, CUDA arch list, install/export targets) are the user's decisions. Do not change them as a side effect.
- Read `.agents/constraints/cpp/cuda.md` and `cuda-modern.md` when writing or reviewing `.cu` / `.cuh` code.
