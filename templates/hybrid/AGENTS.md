## Hybrid Python/C++/CUDA

This project is C++ first. Python is a thin binding and packaging layer over a native core. The binding library is nanobind (STABLE_ABI, located via `python -m nanobind --cmake_dir`); do not mix in pybind11. For a fork of an upstream project, keep the upstream's binding library. Boundary detail (lifetime, GIL, buffers, ABI, wheels) is in `.agents/constraints/hybrid/ffi-boundary.md`.

### Precedence

- CMake owns the native build graph: libraries, kernels, native tests, benchmarks, compile and link options, CUDA architecture policy, ABI flags, dependency discovery (CPM and `find_package`), and install/export rules.
- scikit-build-core only bridges CMake into Python packaging. Poetry owns only the Python virtualenv and Python dependencies.
- Do not use `setup.py`, setuptools extensions, or Python-side compiler calls and native dependency discovery. They create a second native build graph.
- `pyproject.toml` carries metadata and the small `[tool.scikit-build]` block. No compiler flags, dependency fetching, or CUDA architecture lists there.
- `pip install -e .` is never the authoritative native build. Use `poetry run pip install -e . --no-build-isolation` only after the direct CMake build passes.

### Python's role

- Core algorithms, state, error types, retries and fallbacks live in C++. Python holds bindings, `__init__.py` re-exports, `.pyi` stubs, thin CLI dispatch, config parsing that feeds C++ structs, and tests.
- Design order: native interface, native implementation and test, binding, Python test. Do not grow Python modules that duplicate native logic; if one does, move the logic down and delete the Python copy.
- Avoid Python-controlled loops over fine-grained native calls. Expose a batched C++ API instead.
- Put significant logic in Python only when the user asks for it (for example a Python-only library with no native equivalent).

### Layout

```text
cpp/                  native core library (myproject_core target)
bindings/python/      nanobind module (_core_ext), links the same core target
python/<pkg>/         thin package; __init__.py re-exports _core_ext
tests/cpp/            native tests (ctest); tests/python/  binding tests (pytest)
CMakeLists.txt        root build graph; options PROJECT_ENABLE_{TESTS,BENCHMARKS,PYTHON}
```

- The binding target links the same native targets the native tests use. Do not keep a separate source list for Python.
- `PROJECT_ENABLE_PYTHON` gates `bindings/python`; scikit-build-core turns it on.

### Build and test

Native side first, always:

```bash
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo -DPROJECT_ENABLE_PYTHON=ON
cmake --build build -j
ctest --test-dir build --output-on-failure
```

Then the Python side:

```bash
poetry install
poetry run pip install -e . --no-build-isolation
poetry run pytest tests/python
```

A native or binding change is not done until the native build and `ctest` pass. Python-only changes need only the pytest step.

### Tests across the boundary

- Test native logic natively (GoogleTest/Catch2 under `tests/cpp`). Do not re-test it through Python.
- Python tests cover: an import smoke test, a few boundary cases (wrong dtype, shape, strides, device; native exception becomes the right Python exception), and anything Python-only such as wrapper defaults.
- Add a lifetime or GIL test only when a binding holds borrowed memory or releases the GIL. Run the real extension, not mocks.
- Mark GPU tests (`@pytest.mark.gpu`, gtest runtime skip) so CPU-only machines still run the rest.

### System dependencies and wheels

- CUDA Toolkit, drivers, cuDNN, NCCL and TensorRT are discovered prerequisites, not downloaded. Discover them in CMake (`find_package(CUDAToolkit)` etc.), check versions at configure time, and fail there with an actionable message.
- Release artefacts use the shipped architecture list from the C++/CUDA section, never `native`.
- Do not bundle CUDA runtime libraries in wheels; exclude them in the auditwheel repair step. Do not rename wheel files to fake tags.
- Test the built wheel in a clean environment and publish that exact artefact, not a rebuild.
