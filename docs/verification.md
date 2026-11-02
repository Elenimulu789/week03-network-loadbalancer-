# Preparation verification — what actually ran

## Verified in the preparation environment

- All Python files parsed successfully.
- Compose YAML parsed, including the shared backend definition.
- Static checks confirmed private-only backend membership, no backend host port mappings, and an internal private bridge declaration.
- Nginx **1.28.0** was built from official source and its configuration syntax check passed. Container-only filesystem paths and the listen port were adapted for the local test; a local user directive was added because this environment cannot change file ownership to container users.
- A native-process smoke test ran real Nginx in single-process mode with two actual Python backends. It used local loopback ports in place of Docker DNS service names. It observed alternating **5/5** responses over ten requests, **20 successful requests with zero dropped requests** after one backend stopped, and both backends serving again after restart.
- Browser-page, stylesheet, JSON, liveness, and readiness HTTP routes returned 200, and the favicon route returned 204. Expected response headers were present.
- With both local backends stopped, gateway liveness returned 200 while backend readiness returned 502, demonstrating that the two checks mean different things.
- The generated topology diagram was visually inspected.

The raw native smoke-test results are in [preparation-local-smoke.json](preparation-local-smoke.json). These results establish local Nginx/backend behavior; they are **not Docker execution evidence**.

## Still pending on a Docker machine

No Docker client, engine, or socket is available in the preparation environment. The actual Compose stack, container image builds, Docker DNS behavior, cross-network blocking, and GitHub Actions workflow have **not** been executed here. Browser DevTools inspection also remains a manual check.

Run `docker compose up -d --build --wait --wait-timeout 120` and `python scripts/qa.py all` on your computer, then complete the browser checks in `qa-checklist.md`. Keep those actual results for the submission.

## GitHub and recording

The connected account was verified as `Elenimulu789`. No existing `week03-network-loadbalancer` repository was present in the returned repository inventory, and the available GitHub integration has no repository-creation operation. No repository was created or updated. The package includes Git push instructions and a workflow ready for a new repository.

No live cloud URL or video was created. A local topology is permitted by the assignment. The student must make the required screen-and-face recording and supply its real video link.
