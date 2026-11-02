# Video walkthrough — aim for 6 minutes

Use OBS, Zoom, or another recorder that shows your screen **and face**. You do not need a slide deck for this assignment. Show the diagram, files, browser, and terminal. Practice once and keep the final video between 5 and 7 minutes.

Before recording: install Docker Desktop, start the project, and run the full QA suite once. Keep Docker Desktop running. Use a large terminal font. Open the diagram, `compose.yaml`, `nginx/nginx.conf`, and the two review-draft text files. Close other browser tabs pointed at the lab while running the exact distribution test.

The words below describe expected behavior. Change them if your actual run differs. Do not claim a pass before seeing the result.

## 0:00–1:30 — Architecture and AI audit

**Show:** `docs/network-topology.png`.

“For this project, I used Docker to create two separate networks. The public side receives requests, and the private side contains two copies of my application. Nginx connects to both sides and forwards requests to the backends. Each backend returns its own name so I can see which one answered.”

**Show:** `docs/review-draft-compose.txt`, then corrected `compose.yaml`.

“I used AI assistance and included a review example with problems to inspect. In that draft, ports 3001 and 3002 are published from the backends. That would let clients bypass the gateway. In the corrected file, neither backend publishes a host port. They only join the private network, and that network is marked internal.”

**Show:** `nginx/nginx.conf`.

“I also checked the retry settings. If one backend cannot answer, Nginx can try the other one. These retries have time limits so a request does not wait forever. The upstreams use Docker service names instead of fixed backend addresses.”

## 1:30–3:00 — Start and distribution

**Run:**

```powershell
docker compose up -d --build --wait --wait-timeout 120
docker compose ps
docker compose exec loadbalancer nginx -t
```

“Both backends and the gateway should be healthy. The Nginx check confirms the configuration is valid.”

**Show:** `http://127.0.0.1:8080` and its backend ID. Then leave the browser idle.

```powershell
python scripts/qa.py distribution
```

“This sends ten requests. Nginx uses round-robin, which takes turns between the two servers. The output should show five responses from each backend. I use the JSON endpoint because browser requests for stylesheets can also advance the sequence.”

## 3:00–5:00 — Failover, isolation, and browser checks

```powershell
python scripts/qa.py failover
```

“This stops backend one, sends twenty requests, and then starts it again. While it is stopped, every response should come from backend two with HTTP 200. After restart, the script waits until both are serving again. Python does not retry failed requests, so Nginx has to handle the failover.”

```powershell
curl.exe --max-time 2 http://127.0.0.1:3001
python scripts/qa.py isolation
```

“The direct localhost connection should fail because the backend port is not published. The isolation test also uses a temporary container on the public network. It should reach the gateway but fail to reach the private backends. A Docker administrator still controls the host, so this is not protection against someone who already controls Docker.”

```powershell
python scripts/qa.py health
docker compose logs --tail 20 loadbalancer
```

**Show:** browser DevTools Network and Console. Refresh once. Point out 200 responses, backend headers on the main request, and the actual console outcome. Do not count an extension-origin message as an application error without checking its source.

“The gateway health endpoint checks Nginx itself. The readiness endpoint reaches a backend. The routing logs show the backend addresses and response codes.”

## 5:00–6:30 — Takeaways

**Show:** QA checklist or the generated `artifacts/qa-all.json` from your completed run.

“This project showed me that naming a network private is not enough. I also have to check which services join it, whether its ports are published, and what traffic is actually allowed. The load balancer provides one entry point and distributes requests between the backends.”

“The failover test covers one backend stopping while the other remains available. It does not mean the entire system can never go down. There is still one gateway and one Docker host. The demo also uses local HTTP; a public deployment would need HTTPS and more security controls.”

“My main takeaway is that an AI-generated configuration needs to be reviewed and tested. The diagram explains the intended design, but the request counts, failure test, and isolation checks show what it actually does.”

After recording, upload the video to YouTube as Unlisted or Public and paste its real URL into `docs/submission.md`. Include a face camera throughout.
