# Network reality check

The review-baseline files are deliberately incomplete AI-generated examples for this assignment. They are not a historical record of an earlier deployment. Review them before running the corrected configuration, and describe the specific changes you personally verified in your recording.

| Review finding | Why it matters | Corrected configuration | Verification |
| --- | --- | --- | --- |
| Backend `ports` publish 3001 and 3002 | Clients can bypass gateway controls | Remove backend `ports`; only container port 3000 remains | Inspect actual PortBindings, attempt localhost connections, test a public-side probe |
| A network named private is not automatically private | A name alone does not remove external routing | `internal: true`, private-only backend interfaces | Inspect running network's Internal property and membership |
| Gateway binds every host interface | A local exercise need not be accessible to the whole LAN | `127.0.0.1:8080:80` | Inspect the rendered Compose configuration |
| Initial upstream lacks explicit bounded retry behavior | A failed connection may become a gateway error, or waiting may be excessive | 1-second connect timeout, two upstream attempts, bounded read/retry timeouts | Stop one backend and issue 20 GET requests without client retries |
| Startup-only DNS can become stale after container replacement | Docker service IPs may change | Docker DNS resolver, shared upstream zone, `resolve` on Nginx >= 1.27.3 | Nginx syntax check; optional forced recreation test |
| No distinction between proxy health and application readiness | A live gateway can have no working backends | `/healthz` is gateway liveness; `/readyz` reaches a backend | Test both and explain the difference |

Round-robin is Nginx's default. There is no `round_robin;` directive to add. The final configuration does not use IP hash or sticky sessions. A one-worker demonstration plus sequential small API requests makes its alternating output easy to verify. Browser asset requests also count as traffic.

## Optional container-replacement check

After the basic suite passes:

```powershell
docker compose up -d --force-recreate --no-deps backend_1
```

Wait up to 10 seconds for the DNS cache and failure suppression windows, then run `python scripts/qa.py distribution`. This differs from stop/start: it can assign a new container IP. Record the actual outcome; do not claim it passed without executing it.

## Security interpretation

The private bridge prevents ordinary public-side container access and has no normal external route. It does not stop Docker administrators, guarantee that the Linux host cannot reach container IPs, or isolate peers already on that private bridge. The gateway can reach the backends by design. A compromised gateway could abuse that allowed path. Host and service hardening remain separate concerns.

This lab does not claim mTLS, application authentication, per-service authorization, encrypted HTTP, or a managed WAF. Those would be separate improvements.
