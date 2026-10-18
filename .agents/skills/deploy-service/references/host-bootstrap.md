# Host bootstrap, supervision, TLS/DNS, firewall

## Identities and persistence

- Create `deploy` as described in SKILL.md. Keep private keys and privileged config root-owned with restrictive modes. Give the reverse-proxy worker directory traversal only; do not make parents or release roots broadly writable to satisfy it.
- GitHub Actions deploys with a repository- and environment-scoped credential for `deploy` and one fixed forced command or exact `sudo -n` allow-list. A co-located runner uses a different identity.
- With a local database: create the deploy-managed root, delegate only the engine child, and prove backup and restore before cutover.
- Persistent state, logs and secrets live outside release directories, each with documented ownership and backup.

## Restart policy for dependency daemons

Packaged units (nginx, MTA, php-fpm and similar) often ship `Restart=no` with the default `OOMPolicy=stop`: one OOM-killed child then leaves the whole unit dead until someone intervenes. Check, do not assume:

```bash
systemctl show <unit> -p Restart -p RestartSec -p OOMPolicy -p FragmentPath
```

Fix with a drop-in, never by editing the packaged unit (`/etc/systemd/system/<unit>.service.d/restart-policy.conf`):

```ini
[Unit]
StartLimitIntervalSec=300
StartLimitBurst=10

[Service]
Restart=on-failure
RestartSec=5
OOMPolicy=continue
```

Then `systemctl daemon-reload` (adopts new properties without restarting the unit) and read back `systemctl show <unit> -p Restart -p OOMPolicy -p DropInPaths`. Make the installer do that read-back and fail on mismatch: an installed but ineffective drop-in looks identical to a working one until the outage.

`OOMPolicy=continue` suits a master/worker daemon that respawns children. For a single-process service that cannot survive losing its only worker, let the unit stop and rely on `Restart=`. These units are shared by every site or service on the host, so confirm co-tenants still work, and note that a self-healing unit no longer signals an OOM kill through unit state; add separate OOM detection if alerting depends on it.

## TLS and DNS cutover

1. Configure and validate origin TLS before touching public DNS.
2. Test the new origin with the real hostname and SNI while pointing the request at the new address.
3. Behind a TLS-terminating edge, require authenticated origin TLS: Cloudflare Origin CA with Full (strict), never Flexible or non-validating Full.
4. Change only the intended web records; preserve mail and unrelated records. Test IPv4 and IPv6 if both are published.
5. Keep the previous origin until edge health and rollback are proven. Track certificate expiry; an Origin CA cert is not trusted by direct browser clients, so a direct-origin probe is a diagnostic, not the public path.

## Firewall

Write a port-and-route plan before enabling or replacing policy. Keep required UDP listeners, VPN-interface DNS, forwarding and NAT. Keep an out-of-band recovery route or provider console open while changing remote access. Test three ways: host loopback to the app; through the proxy with the real hostname; an external client via public DNS and the edge.
