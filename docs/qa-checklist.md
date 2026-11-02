# QA checklist

Start with `docker compose up -d --build --wait --wait-timeout 120`.

Do not mark a check complete until you observe it in your own Docker run or an actual GitHub Actions run. The expected outcomes below are not recorded passes.

| Check | Command / action | Required evidence | My result |
| --- | --- | --- | --- |
| Configuration | `docker compose config`; `docker compose exec loadbalancer nginx -t` | Backends have no host ports; Nginx syntax valid | Pending |
| 10-request distribution | `python scripts/qa.py distribution` | Alternating backend IDs, exactly 5/5 | Pending |
| Failover and recovery | `python scripts/qa.py failover` | 20 HTTP 200 results from backend_2 while backend_1 is stopped; both return after restart | Pending |
| Host negative check | `curl.exe --max-time 2 http://127.0.0.1:3001` | Connection rejected/unreachable | Pending |
| Actual network isolation | `python scripts/qa.py isolation` | No published backend ports; public probe reaches gateway but cannot reach backend IPs/names | Pending |
| Health and headers | `python scripts/qa.py health` | All five tested routes return HTTP 200; security headers present | Pending |
| Browser Network | F12 → Network, refresh page | `/` and `/style.css` return 200; no failed resources | Pending — manual |
| Browser Console | F12 → Console, refresh | No application-origin console errors | Pending — manual |
| Connection reuse | Network tab, enable Connection ID if supported | Inspect connection behavior; browsers may open more than one connection | Pending — manual |
| Logs | `docker compose logs --tail 30 loadbalancer` | Backend addresses/statuses; a retried request may show both upstream attempts | Pending |

The combined run is `python scripts/qa.py all`. It writes `artifacts/qa-all.json`. Individual runs write `qa-distribution.json`, `qa-failover.json`, etc. Each report identifies its environment, executed checks, and PASS/FAIL result. Browser inspection is manual and is not certified by this script.

## Run record

- Date/time: ____________________
- Operating system and Docker version: ____________________
- Git commit: ____________________
- Automated result and file: ____________________
- Browser checked and outcome: ____________________
- Problems found and changes made: ____________________

## How to interpret failure

If an HTTP request drops, the script fails; it does not silently retry in Python. A failed distribution count may indicate another client generated traffic. A failed negative port test may indicate an unrelated program owns that port. Investigate instead of checking the box anyway.

One failed backend is the tested fault. Both backends failing or the gateway/host failing are outside this topology's high-availability boundary.
