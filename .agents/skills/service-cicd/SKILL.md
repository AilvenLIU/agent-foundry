---
name: service-cicd
description: GitHub Actions CI/CD for Python, C++/CUDA and hybrid services. Covers workflow YAML, hosted and self-hosted runners, immutable artefact builds, the server-local artefact store, auto-deploy after merge to main, protected environments, concurrency, provenance and rollback. Use when writing or reviewing workflows, deploy or publish jobs, Actions secrets or artefact promotion.
---

# Service CI/CD

Use Actions to validate source, build one immutable artefact, and promote those exact bytes through protected deploy jobs. This skill owns the automation. `deploy-service` owns the host: roots, `deploy` account, activation helper, rollback. 

## Authority and defaults

- **Automatic publish and deploy run only on a `push` to `main`**, gated on `github.ref == 'refs/heads/main'`, promoting the artefact for the event's `github.sha`. Pull requests, tags, schedules, manual dispatch, and feature branches have no automatic release or deploy authority. Manual deploy and rollback are operator actions on a verified `main` artefact.
- **Build authority is the project's own**: Poetry for Python; direct CMake + Ninja (+ CPM) for C++/CUDA; for hybrid, direct CMake configure/build/ctest first, then scikit-build-core as packaging bridge with Poetry owning the Python environment. Do not invent a parallel build graph in Actions. Keep CPU-native build and ctest on ordinary runners and put GPU tests on labelled runners (see `gpu-ci`). One artefact per target platform or ABI; a manifest maps each target to digest and compatibility. One runner's success says nothing about another arch, ABI or GPU generation.
- **Build once, promote the same bytes.** Validation, then one build that writes the artefact and manifest (source SHA, release id, digest, compatibility, toolchain, lock identity, run id) into the server-local store. Publish and deploy verify and promote that record; neither rebuilds, and neither resolves a branch, tag or `latest` later.
- **Deploy job**: a GitHub-hosted job in a protected environment authenticates as the unprivileged `deploy` user with a repository- and environment-scoped credential (short-lived federation if available, otherwise one rotated restricted key) and calls one fixed host command with validated scalar arguments. It never uses the self-hosted runner identity and never builds a shell or SSH program from event data.
- **Serialise per environment** with a `concurrency` group and `cancel-in-progress: false`. Concurrency does not prove freshness: the activation boundary re-reads the `main` tip and refuses a rerun of an older event.
- **Rollback** is a separate protected workflow selecting a retained release id or digest, using the same helper and health gates. No rebuild.

## Workflow rules

- Pin every third-party action to a reviewed full 40-character commit SHA with a release comment (`# v4.2.1`). A tag or branch is not a pin. Resolve SHAs from the official repository at write time; never invent placeholders.
- Set `permissions` explicitly and minimally at workflow and job level (`contents: read` by default); isolate any job needing `contents: write`, packages, attestations or deployments.
- Pull-request jobs get no production secrets, deploy identities or write tokens. Never check out or run untrusted contents under `pull_request_target`.
- Treat event fields and dispatch inputs as untrusted: validate before checkout or interpolation, resolve refs to full SHAs, keep them out of shell and SSH strings.
- Production secrets live in protected GitHub environments (reviewers, branch rules). Never print keys, env files or credential-bearing command lines.
- A persistent self-hosted runner needs the extra rules in [self-hosted-runners.md](references/self-hosted-runners.md); prefer private repositories.

## Artefact storage (default-deny on GitHub)

Do not use `actions/upload-artifact`, `actions/download-artifact`, the Actions artefact API/CLI or `gh run download` for build, test, release, deploy or rollback bytes. Bytes that must cross a job or host boundary go to the fixed server-local store, a fixed direct transfer, or a protected build-and-promote job. If none exists for a GitHub-hosted build, stop and ask the user to provision one. GitHub Release assets, GitHub Packages and GHCR are public or byte-publication surfaces, not transport, retention or rollback: use them only when the user explicitly asks for that named surface. Attestations and provenance are metadata, not licence to upload bytes. Store layout, rolling retention and the one-day exception: [artifact-storage.md](references/artifact-storage.md).

## Pipeline shape

```text
validate -> build -> attest -> deploy (protected env) -> verify
                                   \-- failure -> protected rollback
```

- `validate`: format, lint, static analysis, tests; no secrets.
- `build`: profile build; commits the immutable store record.
- `attest`: provenance with minimal write scope.
- `deploy`: transfer to a release-specific temp path under the host staging area (or let the helper copy), verify host key and digest, call the fixed helper, wait for release-specific health.

Publishing a package or image: use trusted publishing or short-lived identity, push images by digest (tags are aliases, deploy the digest), verify uploaded version and digest afterwards. Release ids and versions are immutable: a retry may complete missing surfaces or confirm identical bytes, and must reject an existing object with different bytes.

## After activation

Confirm the host-reported identity (target label, hostname, release id, time) matches the intended environment and release, then probe loopback, origin (real hostname and SNI, every address family) and public. Stale unit timestamp, missing release record or absent listener after a green run means secret drift, a different server or an incomplete helper: stop, keep the logs, fix the boundary; do not rerun the workflow repeatedly. Keep the last known-good release on failure.
