---
name: deploy-service
description: Secure host-side deployment of a static, Python, C++/CUDA, hybrid, native-binary or container service on a Linux host. Covers data roots, the unprivileged deploy account, immutable releases, restricted activation helpers, health gates, rollback, retention, systemd, reverse proxy, TLS, DNS and firewall. Use for server bootstrap, activation helpers, service units and deploy or rollback runbooks; use service-cicd for the GitHub Actions side.
---

# Deploy Service

Deploy a CI-built immutable artefact into a fixed data root and activate it through a narrow, persistent host interface. This skill owns the host. `service-cicd` owns the workflow that calls it.

## Host defaults

- **Deployment root**: `/data/www/<service>`, `~/data/www/<service>` or another dedicated data volume (`/mnt/<volume>/www/<service>`). Resolve `~` to the `deploy` account's home (normally `/home/deploy/data/`) and write absolute paths into unit and proxy config. Never default to `/var`, `/srv`, `/opt`, `/usr` or `/usr/local`. A legacy system path needs an explicit decision from the user; "the host already does it" is not one. Do not migrate a sound live layout only to match this.
- **Root is trusted config.** A branch, release id, workflow input or archive path never selects or builds it. If the root is a symlink, resolve it and confirm it stays on the approved filesystem.
- **Account**: one unprivileged `deploy` user (no interactive shell, no broad sudo) owns the root and its staging, releases, metadata, locks and deploy-managed state. Root owns privileged helpers, sudoers, unit policy and proxy config. The runtime service runs as its own identity with only the read, traverse or writable-state access it needs. Several services may share the account name, never credentials or helper allow-lists: one credential per repository and environment.
- **Local database**: separate `deploy`-owned root `/data/database/<service-or-engine>` or `~/data/database/<service-or-engine>`, outside releases. Delegate only the engine child directory when the engine's own identity must own raw files. Deploy, rollback and prune never touch database contents; migration, restore and deletion are separate, explicit operations.
- **Promotion authority**: automatic activation runs only after `main` is updated and deploys the artefact built from that exact SHA. Other branches may validate but never activate production. Manual deploy and rollback are operator actions and also use a verified `main` artefact.
- **Same-machine CI**: a self-hosted runner shares no credentials, groups, helpers, control sockets or writable paths with `deploy` or production state, and cannot modify live releases. Docker-group membership is root-equivalent and does not count as separation.

Before changing a host, inventory identities, mounts and free space, listeners (IPv4 and IPv6), services and containers, firewall, VPN, DNS, TLS and recovery access. Existing network services are dependencies: opening only SSH/HTTP/HTTPS can break a VPN gateway or local resolver.

Ask the user before changing public DNS, firewall policy, credentials, production data, privileged command boundaries, destructive retention or an existing live layout.

## Release layout

```text
<root>/
  releases/<release-id>/     immutable
  staging/                   same filesystem as releases/ (atomic rename)
  metadata/<release-id>.env
  shared/                    uploads, runtime data (or a separate data root)
  current -> releases/<release-id>
  locks/
```

The proxy serves only `current`. Never expose staging, metadata, helpers, credentials or `.git`. Size the disk for staged + live + rollback + growth during activation. Artefact specifics per profile and activation model: [service-releases.md](references/service-releases.md).

## Invariants

- Deploy an immutable CI-built artefact. No `git pull`, dependency resolution, package install or source compilation on the host.
- The input comes from the fixed server-local artefact store or a fixed host interface, not GitHub Actions artefact storage (see `service-cicd`). Keep that store outside the root, releases and persistent state; `deploy` may promote a selected digest but cannot write or prune it.
- Each release has a validated id joining source SHA, artefact digest, compatibility, timestamps, previous live release, status and retention reason.
- Verify digest, provenance if available, archive members and host compatibility (OS, arch, ABI, CUDA/driver) before stopping the live release. Reject absolute members, `..`, unexpected links and device files; canonicalise every path before use and never follow user-made symlinks in cleanup.
- Privileged activation is a persistent root-owned helper behind a forced-command SSH key or an exact `sudo -n` rule. Never run an uploaded script as root. Revalidate every argument (id, channel, SHA, digest, paths) inside the helper against strict allow-lists.
- Pin the SSH host key. Deploy keys have no shell, PTY, forwarding, agent, X11 or user-selected command. Never give CI general sudo, Docker daemon access, unrestricted `systemctl`, package managers or interpreters.
- Serialise activation and pruning per environment with a host lock. Traffic sees the whole old release or the whole new one: atomic rename plus symlink swap, or a validated environment file that systemd reads.
- Keep secrets and keys out of artefacts and logs.

## Activation

```text
received -> verified -> staged -> activating -> healthy -> live
                                       +-- failed --> rollback -> restored
```

The helper locks, validates, refuses unknown parallel or legacy instances, stages without stopping the current release where possible, switches, runs health gates, then marks live and records the previous release. Never overwrite an existing release directory: verify its digest and treat a repeat as a no-op. On failure it restores the previous release automatically when that is safe. A failed health gate stays failed; do not weaken it.

Success means all of: release identity and digest match; exact process or container set (no stale duplicate stack); loopback health for every role; worker progress, not just an open port; proxy route with the production hostname and SNI; a representative real request; native, FFI, DB and GPU checks where relevant (a kernel actually runs; HTTP 200 does not prove FFI health). The helper returns a non-secret host identity (target label, hostname, release id, UTC time) so CI can confirm it hit the intended server.

A red deploy is not automatically a bad release: if ingress checks fail while a host dependency such as the proxy is down, fix the dependency first.

## Rollback and retention

- Rollback picks a retained verified release and uses the same helper family and the same health gates. It never rebuilds or repairs a checkout.
- A release that changes persistent schema needs a stated compatibility with the previous version; otherwise rollback is a deliberate operator procedure.
- Retain at least live and one known-good rollback target, plus activating, pinned and held releases. Cleanup supports dry-run, stays under the root, refuses symlink escapes and fails closed on malformed metadata or unknown state.

## Host services and edge

Bootstrap, systemd restart policy for dependency daemons, TLS/DNS cutover and firewall: [host-bootstrap.md](references/host-bootstrap.md). Dual-stack nginx, Cloudflare 521/525/502 diagnosis: [dual-stack-ingress.md](references/dual-stack-ingress.md).
