# Self-hosted Actions runners

Pattern A (self-hosted runner) supplies CI compute. Pattern B (GitHub-hosted deploy job + scoped SSH to `deploy`) promotes to production. They are independent and often combined; Pattern B stays the deploy path even when the runner built the artefact.

## Trust boundary

- Treat the runner as arbitrary code execution for anyone who can trigger an authorised workflow. Prefer a private repository and a repository-scoped runner; an organisation runner needs a repository allow-list. Never route public-fork code to a persistent runner without disposable workers and a reviewed approval model.
- On a machine shared with production, the runner user is not `deploy`, holds no deploy key, cannot call the activation helper, and has no write access to the `deploy` root, live releases, persistent state or database namespace. No shared groups, sudo rules, sockets or helpers. Container-daemon membership is root-equivalent; use another host or stronger isolation, or record the risk instead of claiming least privilege.
- Dedicated system user, no login, no sudo, only the device or build groups the job matrix needs. Use specific labels (repository, OS, arch, hardware, trust class), not bare `self-hosted`.
- Registration tokens are short-lived and kept out of files, logs, service environments and shell history; registration is administration, not a workflow step.

## Bootstrap: one committed, idempotent root script

1. Create runner user, home, work, tool, cache and service dirs with deliberate ownership. Fix the whole runner-owned cache tree, including parents root created.
2. Install packages, compilers and container support there; workflow steps get no sudo.
3. Download a pinned runner release and verify its recorded SHA-256 before extraction. Never resolve `latest`.
4. Register at the narrowest scope, install via the runner's service installer.
5. systemd drop-in with `Restart=on-failure` and `RestartSec=10`. A protective `OOMScoreAdjust` for the listener does not protect memory-heavy job children.
6. Set the service PATH explicitly: the installer may capture root's PATH, so add the runner user's tool dirs such as `~/.local/bin`.
7. Provision swap and persistent caches once on the host, never per job.
8. Skip restart or upgrade with a warning while a job worker is active.

Re-running the script must converge without duplicating registrations, services, groups, swap or directories.

## Workflow adjustments

- Remove `sudo apt-get` and other privileged setup from steps; put prerequisites in the bootstrap or a reviewed worker image.
- Assume workspace, `runner.temp` and caches persist between jobs: use run-specific paths, clean sensitive temp data, keep retries idempotent. Run the workflow twice to expose stale state.
- Prefer a local build cache over a remote cache action; partition by repository and trust class, put all ABI and toolchain inputs in the key, make a miss cost only speed.
- Remove per-run swapfile creation.
- If a marketplace or composite action that bootstraps its own interpreter breaks on the host, use a pinned top-level setup action plus the tool's pinned CLI; do not weaken pinning or patch library paths globally.
- Record the host compiler, standard library, runtime, container engine and hardware. A first failure under a newer toolchain may be a real latent defect: reproduce before calling it runner noise.
- Keep matrix entries for supported product targets; one self-hosted machine is not evidence for another OS, arch, ABI or GPU.
- Artefacts go to the server-local store ([artifact-storage.md](artifact-storage.md)), not Actions upload.
