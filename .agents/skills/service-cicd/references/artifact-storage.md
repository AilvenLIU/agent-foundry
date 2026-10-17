# Server-local artefact store and rolling retention

GitHub Actions artefact storage is default-deny: uploads use repository quota, are not a durable rollback store, and can fail before a verified build can be promoted.

## Store

- Fixed operator-approved data root, for example `/data/ci-artifacts/<repository>` or `~/data/ci-artifacts/<repository>` (resolve `~` for the runner account). Keep it apart from the deployment root, releases, databases, uploads, logs, credentials and the runner workspace.
- The runner identity owns it and writes only under its repository namespace. `deploy` reads one selected immutable record through a fixed host helper; it cannot write or prune.
- A GitHub-hosted job never receives the runner or `deploy` identity. It may reach a separate, repository- and environment-scoped writer interface with a fixed endpoint that creates one digest-verified staging record and cannot list, prune or touch production; the host validates event SHA and digest before an atomic commit.
- The root is host config; no branch, input, archive name, release id or event payload selects it.
- Each record has a manifest: repository, branch (from the immutable event, not input), source SHA, run id, release id, digest, target compatibility, created time, status, retention reason.

## Promotion

1. Validate and build once on the trusted build host.
2. Write bytes and manifest to a run-specific staging dir on the same filesystem.
3. Verify digest, manifest, archive paths and compatibility; commit atomically into the immutable record.
4. Downstream jobs use the record id and digest. Deploy or publish reads that exact record and fails closed when it is missing, malformed, superseded or has a different digest.

## One-day GitHub upload exception

Allowed only when the local store, a fixed direct transfer and a pull interface demonstrably cannot meet a concrete cross-host need, and the user explicitly asks for that specific upload. Contents are non-secret, size-capped, tied to a source SHA and digest, `retention-days: 1`, and never release or rollback authority. The upload action is pinned to a full SHA with a single `with.name`. Keep the local record until normal retention prunes it. An upload hidden in a composite action, helper script or `gh run download` is not an exception.

## Rolling retention

Keep the three newest verified `main` records, and any record marked `live`, `rollback`, `pinned`, `held` or `activating`. Do not retain records from PRs, feature branches, tags, cancelled or failed runs. Keep failure information in ordinary logs or a short-lived local diagnostic store. Retaining a `develop` record gives it no deploy authority.

Pruning: take a repository-specific host lock; dry-run before the first activation and after policy changes; preserve live, rollback, pinned, held, activating and unknown-state records; refuse malformed manifests, symlink escapes, digest mismatches and paths outside the store; delete only identified expired records under the repository root. Run after a successful commit, on a host timer and before promotion. Promotion marks its record `activating` or `held` under the same lock first, so cleanup cannot race it. Watch record count, bytes, failed cleanups and free space. Rollback stays valid while the retained record and digest exist, regardless of Actions expiry.
