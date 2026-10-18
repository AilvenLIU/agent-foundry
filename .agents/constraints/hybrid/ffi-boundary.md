---
id: hybrid/ffi-boundary
name: FFI Boundary
description: nanobind boundary between Python and C++/CUDA
category: hybrid
status: active
applies_to:
  - "*.py (when calling native extensions)"
  - "*.cpp (when exposing to Python)"
  - "*.cu (when exposing CUDA to Python)"
severity: advisory
---

# Python Bindings (nanobind)

nanobind is the only binding library for our own projects. The template generates `bindings/python/` with a module `_core_ext` (`NB_MODULE`, `nanobind_add_module(... STABLE_ABI)`) linked against the native core target and re-exported from `python/<pkg>/__init__.py`. nanobind is found with `python -m nanobind --cmake_dir`; pin its version in `pyproject.toml`. Do not add pybind11, an abstraction over both, or a switch. A fork of an upstream project keeps the upstream's binding library.

Keep bindings thin: convert, validate, call the native API, translate errors. Logic belongs in C++.

## Ownership and lifetime

- State who owns every pointer, view, capsule and callback that crosses. If Python receives a view into a C++ object, tie lifetimes with `nb::keep_alive<Nurse, Patient>()` or `nb::rv_policy::reference_internal`.
- Do not return a raw pointer or reference with `rv_policy::reference` unless the C++ object provably outlives every Python reference. Prefer returning by value, `std::unique_ptr` or `std::shared_ptr`.
- Touch `nb::object` handles only while the GIL is held. A C++ object that stores a Python callback must destroy it under the GIL; destructors that run on native threads are a common crash.
- Do not let a native thread outlive the module or the object that spawned it. Join in the destructor.

## GIL

- Release it (`nb::call_guard<nb::gil_scoped_release>()` or a scoped release) around native calls that block or run long (roughly over 1 ms), including CUDA synchronisation and I/O.
- Copy what you need out of Python objects first. Reacquire with `nb::gil_scoped_acquire` before any callback into Python or before raising from a native thread's context.
- CUDA host callbacks (`cudaLaunchHostFunc`, stream callbacks) run on driver threads without the GIL. Do not call Python from them directly; acquire the GIL explicitly or hand off to a queue.
- A `gil_scoped_release` call guard on a function that takes a Python object argument is a crash risk. Extract data first or reacquire inside.

## Exceptions

- nanobind maps `std::invalid_argument` to ValueError, `std::out_of_range` to IndexError, `std::bad_alloc` to MemoryError and other `std::exception` to RuntimeError. Register custom native error types with `nb::exception<T>(module, "Name", base)` so callers can catch them by type.
- Never let an exception escape a native thread, a destructor or a CUDA callback; it terminates the process.
- CUDA errors are asynchronous. A launch error shows at `cudaGetLastError()` right after the launch; execution errors show at the next sync or API call, possibly in an unrelated function. Check both, translate to a Python exception, and remember a sticky error leaves the context unusable.
- Retry and fallback policy does not belong in the binding; surface the error.

## Arrays and tensors

- Use `nb::ndarray<T, nb::shape<...>, nb::c_contig, nb::device::cpu|cuda>` to state dtype, rank, layout and device in the signature. Arguments are zero-copy views of NumPy, PyTorch, JAX or CuPy buffers via the buffer protocol or DLPack. A mismatch is converted implicitly where possible (a silent copy); add `.noconvert()` to the argument when a copy would lose writes or hide a wrong dtype.
- The view is valid only while the call holds the input alive. Do not keep the pointer after returning, and reject writes to read-only arrays.
- A returned ndarray over memory that C++ allocated needs an owner (`nb::capsule` with a deleter, or a handle to the owning object). Without one it dangles or leaks.
- Exchanged memory is shared. Treat it as read-only unless you control both sides. For GPU tensors, honour the stream passed to `__dlpack__` and keep the memory valid until the consumer's deleter runs.

## Device memory

- Wrap device allocations in a C++ RAII class and expose it as an opaque handle that carries device id, size, dtype and the stream it was produced on. Free on the owning device.
- Do not expose raw device pointers as Python ints outside an explicit interop API; they have no lifetime.
- A Python loop over fine-grained device calls hides launch overhead and sync points. Expose a batched native call.

## Build, ABI and wheels

- Bindings link the same native targets as the native tests. Compile definitions and ABI flags come from CMake; never mirror them in Python packaging. `_GLIBCXX_USE_CXX11_ABI` must match any framework you link (PyTorch).
- `STABLE_ABI` yields one wheel for Python 3.12+ (nanobind builds a version-specific module on older Python). Release matrix inputs: OS and manylinux baseline, CPU architecture, compiler and standard-library ABI, Python version and ABI tag, CUDA toolkit, driver floor, GPU architectures.
- Release builds use the shipped architecture list (`80 86 89 90`, see AGENTS.md), with PTX for the newest arch if forward compatibility matters. `native` only for local builds.
- Do not bundle CUDA runtime libraries (`libcudart`, `libcublas`, `libcudnn`, `libnccl`) in wheels. Exclude them in `auditwheel repair` and document the runtime requirement. Use PEP 440 local versions (`+cu121`) for per-CUDA variants and let the backend produce the filename.
- Test the actual wheel in a clean environment, without the source tree, then publish that file without rebuilding.

## System dependencies

- CUDA Toolkit, driver, cuDNN, NCCL and TensorRT are external prerequisites discovered by CMake, not fetched by CPM or Python. Prefer `find_package(CUDAToolkit)`; cuDNN, NCCL and TensorRT have no config files, so use `find_path`/`find_library` with `CUDNN_ROOT`, `NCCL_ROOT`, `TENSORRT_ROOT` hints and check that header and library both exist.
- Check minimum versions at configure time and fail there with a message saying what to set (`CUDA_HOME`, `CMAKE_CUDA_COMPILER`). When several CUDA versions are installed, set the compiler explicitly.
- Handle an absent GPU at runtime: import must succeed on a CPU-only host when CUDA is optional, and a promised-GPU call must raise a clear error, not crash.

## Boundary tests worth writing

An import smoke test; wrong dtype/shape/stride/device is rejected with the right exception; a native error maps to the expected Python type; a returned view stays valid after its parent goes out of scope (when you added `keep_alive`); concurrent calls from several threads when the GIL is released. Mark GPU tests `@pytest.mark.gpu`.
