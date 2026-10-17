# Release models and artefact compatibility

## Static directory

Activation steps: take the host lock; receive the archive in a release-specific temp path outside `current`; validate id, digest, members and containment; extract into `staging/` on the same filesystem as `releases/`; check required files, modes and ownership; rename to the final `releases/<id>`; create a temporary relative symlink and `rename` it over `current`; run direct-origin and public checks that identify the release; record previous and current before any pruning.

## Containers, native binaries, long-running services

- Container: deploy by immutable image digest, never a floating tag as the only identity. Give the stack a stable Compose project name and labels for service, release, channel, source SHA and image digest. The helper loads the CI-built image and selects the validated reference; it does not `docker pull`, `docker login` or build.
- Native: install immutable versioned paths with a recorded checksum; systemd references a stable pointer or a validated environment file.
- Define the expected topology exactly. Detect both missing units and stale duplicate stacks. The reverse proxy and monitoring are not a second application stack.
- Activation metadata names the data root (under `/data/`, `~/data/` or an approved volume, owned by `deploy`) and rejects system-owned roots; with a local database it also names the separate database root.
- Health covers: release identity and digest, exact unit or container set, loopback per role, worker heartbeat, proxy route with the real hostname, authenticated and unauthenticated routes, and native/FFI/DB/GPU checks.

## Per-profile compatibility

- **Python**: ship a CI-built wheel, archive or container with locked dependencies and recorded Python ABI. No Poetry or pip at activation. If a container copies a venv from a builder stage, builder and runtime paths and interpreter ABI must match. Migrations are explicit, serialised release steps.
- **C++/CUDA**: ship a CMake-built archive or container with target OS, arch, compiler/runtime ABI, shared libraries and CUDA compatibility; executable, libraries, resources, licences and service metadata in one release. No compile or CPM resolve on the host. The NVIDIA driver is a host prerequisite: never bundle or replace it. When a GPU is required, health must include device discovery and a representative kernel.
- **Hybrid**: ship a wheel, archive or container whose native graph was built by CMake and packaged through scikit-build-core. Verify Python ABI, native library loading and FFI error propagation before activation. Record both Python and native/GPU requirements.
- **Fleets**: reject an incompatible artefact before stopping the live release. Use separate artefacts and canary activation for heterogeneous OS, arch, ABI or GPU.
