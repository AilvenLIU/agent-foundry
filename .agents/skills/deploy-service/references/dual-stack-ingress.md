# Dual-stack reverse proxy and Cloudflare diagnostics

Ask the user before changing public DNS, firewall, certificates, privileged proxy config or live state.

## Keep IPv4 and IPv6 symmetric

Keep existing IPv4 listeners when adding IPv6. Current nginx enables HTTP/2 separately from `listen`:

```nginx
server { listen 80; listen [::]:80; }
server { listen 443 ssl; listen [::]:443 ssl; http2 on; }
```

Reuse a certificate only after confirming a known-good vhost's SANs cover the hostname. Keep keys root-owned and inspect paths and certificate metadata, not key contents. Validate with `sudo nginx -t`; `reload` only when nginx is active, otherwise a validated `restart` and `sudo ss -lntp '( sport = :80 or sport = :443 )'`.

## Find the first failing layer

Cloudflare-proxied DNS returns edge addresses, not the origin, so test layers separately:

```bash
dig @1.1.1.1 A <host>; dig @1.1.1.1 AAAA <host>
curl -g -k -i --resolve '<host>:443:[<origin-ipv6>]' https://<host>/healthz   # origin, real SNI
curl -i https://<host>/healthz                                                  # public
curl -i http://127.0.0.1:<port>/healthz                                         # loopback
```

| Symptom | Meaning | Next |
| --- | --- | --- |
| Edge 521 | Edge cannot connect to origin | listener, firewall, route, origin TLS, v4/v6 reachability |
| Direct origin 502 | TLS and proxy fine, upstream unreachable | loopback health, upstream port, unit state, proxy error log |
| Direct origin healthy, public fails | edge/DNS differs from the validated path | proxy mode, record target, edge TLS mode, cache/routing |
| Loopback refused | nothing on the upstream address | unit/container state, port mapping, activation |

A VPN resolver proves private DNS, not public edge reachability; probe from an external client too.

## Cloudflare 525 (origin TLS handshake failed)

Do not change DNS, reissue the Origin CA cert or weaken the edge TLS mode first.

1. Record hostname, UTC time, Ray ID. Test apex and canonical host.
2. Bypass the edge with the real hostname and SNI against every published address: `curl -kI --resolve 'example.com:443:203.0.113.10' https://example.com/` and the `-g` form with `[2001:db8::10]`. `-k` is expected for a direct Origin CA probe, never for the public check.
3. If direct works and another proxied host on the same origin works, diff the effective TLS config of the working and failing vhosts with `nginx -T` (not just the file you expect): cert/key paths, protocols, `ssl_ciphers`, `ssl_prefer_server_ciphers`, `ssl_ecdh_curve`, client-cert verification, `ssl_conf_command`, `ssl_reject_handshake`, default-server selection, includes.
4. Apply one reviewed TLS policy to equivalent vhosts (for example `ssl_ciphers HIGH:!aNULL:!MD5; ssl_prefer_server_ciphers on;` when the working vhost has it), `nginx -t`, reload, recheck v4, v6 and the redirect target. Keep the config backup until both pass.
5. A zero-byte pcap means the capture failed, not that Cloudflare sent nothing.

## Runtime, not just the proxy

Before blaming nginx for a 502, check `systemctl status --no-pager <web-unit> <worker-unit>`, the loopback health URL and `journalctl -u <unit> -n 150 --no-pager`. For containers check Compose status and logs. Do not fix production with `docker pull`, `docker login`, an ad-hoc build or a `latest` image; the helper loads the CI-built artefact. Restore the last known-good release rather than weakening a health gate or guessing across several layers.
