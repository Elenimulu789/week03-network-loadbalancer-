#!/usr/bin/env python3
"""Real Docker QA; uses the Python standard library and Docker Compose v2."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8080"
# Ignore system HTTP proxies for local tests.
HTTP = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def docker(*args):
    result = subprocess.run(["docker", *args], cwd=ROOT, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout


def compose(*args):
    return docker("compose", *args)


def get(path):
    # One request, no application-level retries: Nginx must hide node failure.
    with HTTP.open(BASE + path, timeout=8) as response:
        body = response.read()
        return response.status, dict(response.headers), body


def identity():
    status, headers, body = get("/api/whoami")
    require(status == 200, f"HTTP {status}")
    server = json.loads(body)["server_id"]
    require(server in {"backend_1", "backend_2"}, f"Unexpected backend: {server}")
    require(headers.get("X-Backend-ID") == server, "Backend header/body mismatch")
    return server


def wait_ready():
    deadline = time.monotonic() + 45
    last = "not started"
    while time.monotonic() < deadline:
        try:
            identity()
            return
        except Exception as exc:
            last = str(exc)
            time.sleep(0.5)
    raise RuntimeError(f"Gateway not ready after 45 seconds: {last}")


def audit():
    config = json.loads(compose("--profile", "tools", "config", "--format", "json"))
    services = config["services"]
    for name in ("backend_1", "backend_2"):
        service = services[name]
        require(not service.get("ports"), f"{name} publishes host ports")
        require(set(service["networks"]) == {"private_subnet"}, f"{name} is not private-only")
        require(not service.get("privileged"), f"{name} runs privileged")
        require(service.get("network_mode") != "host", "Host networking bypasses isolation")
        require(service.get("read_only"), f"{name} has a writable root filesystem")
    require(set(services["loadbalancer"]["networks"]) == {"public_subnet", "private_subnet"},
            "Gateway must be dual-homed")
    require(config["networks"]["private_subnet"].get("internal") is True,
            "private_subnet must be internal")
    for name, service in services.items():
        if name != "loadbalancer":
            require(len(service["networks"]) == 1, f"Unexpected dual-homed service: {name}")
    nginx_test = compose("exec", "-T", "loadbalancer", "nginx", "-t")
    text = (ROOT / "nginx/nginx.conf").read_text()
    active = "\n".join(line.split("#", 1)[0] for line in text.splitlines())
    require("proxy_next_upstream_tries 2;" in active, "Two-node retry policy is missing")
    require("server backend_1:3000 resolve" in active and "server backend_2:3000 resolve" in active,
            "Missing dynamic service-name upstreams")
    require(not any(x in active for x in ("least_conn;", "ip_hash;", "hash ")),
            "Round-robin test requires the default algorithm")
    return {"compose_audit": "pass", "nginx_config": "pass", "output": nginx_test.strip()}


def health():
    checks = {}
    for path in ("/", "/style.css", "/api/whoami", "/healthz", "/readyz"):
        status, headers, body = get(path)
        require(status == 200, f"{path}: HTTP {status}")
        require(headers.get("X-Content-Type-Options") == "nosniff", "Missing security header")
        if path == "/healthz":
            require(json.loads(body)["component"] == "loadbalancer", "Not gateway liveness")
        elif path == "/readyz":
            require(json.loads(body)["status"] == "ok", "Backend not ready")
        checks[path] = status
    return checks


def distribution():
    sequence = []
    for index in range(10):
        server = identity()
        sequence.append(server)
        print(f"  Request {index + 1:02}: {server}", flush=True)
    counts = dict(Counter(sequence))
    require(counts == {"backend_1": 5, "backend_2": 5}, f"Uneven distribution: {counts}")
    require(all(a != b for a, b in zip(sequence, sequence[1:])),
            "Responses did not alternate; close other clients and rerun")
    return {"sequence": sequence, "counts": counts}


def failover():
    # Preserve recovery even if a request fails or the user interrupts the test.
    try:
        compose("stop", "--timeout", "0", "backend_1")
        sequence = []
        for index in range(20):
            server = identity()
            require(server == "backend_2", f"Stopped node answered: {server}")
            sequence.append(server)
            print(f"  Failover {index + 1:02}: HTTP 200 / {server}", flush=True)
    finally:
        compose("start", "backend_1")
    # Passive health checks retry the recovered node after fail_timeout expires.
    recovered, recovery = set(), []
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        server = identity()
        recovery.append(server)
        recovered.add(server)
        if recovered == {"backend_1", "backend_2"}:
            print("  Recovery: both backends are serving again", flush=True)
            return {"requests": 20, "dropped": 0, "sequence": sequence, "recovery": recovery}
        time.sleep(0.5)
    raise AssertionError("backend_1 did not rejoin within 20 seconds")


def isolation():
    private_ips = []
    for name in ("backend_1", "backend_2"):
        container_id = compose("ps", "-q", name).strip()
        require(bool(container_id), f"{name} is not running")
        data = json.loads(docker("inspect", container_id))[0]
        require(not data["HostConfig"].get("PortBindings"), f"{name} has host port bindings")
        networks = data["NetworkSettings"]["Networks"]
        require(len(networks) == 1, f"{name} has extra network interfaces")
        network_name, attachment = next(iter(networks.items()))
        network = json.loads(docker("network", "inspect", network_name))[0]
        require(network["Internal"] is True, "Running backend network is not internal")
        private_ips.append(attachment["IPAddress"])
    rejected = []
    for port in (3000, 3001, 3002):
        try:
            connection = socket.create_connection(("127.0.0.1", port), timeout=1)
        except OSError:
            rejected.append(port)
        else:
            connection.close()
            raise AssertionError(f"Host port {port} is open; stop any unrelated service and rerun")
    # A genuine public-side negative test, stronger than localhost-port rejection.
    probe = '''import socket, sys
with socket.create_connection(("loadbalancer", 80), timeout=3):
    print("Public probe can reach gateway")
for host in sys.argv[1:]:
    try:
        s = socket.create_connection((host, 3000), timeout=2)
    except OSError:
        print("BLOCKED private backend:", host)
    else:
        s.close()
        raise SystemExit("FAIL: public probe reached " + host)
'''
    output = compose("--profile", "tools", "run", "--rm", "--no-deps", "probe", "-c", probe,
                     *private_ips, "backend_1", "backend_2")
    print(output.strip(), flush=True)
    return {"unpublished_host_ports": rejected, "private_ips_tested": private_ips,
            "public_probe": output.strip(), "boundary": "ordinary client/public-network container"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["all", "distribution", "failover", "isolation", "health"],
                        nargs="?", default="all")
    args = parser.parse_args()
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "mode": args.mode,
              "environment": "Docker Compose", "tests": {}}
    try:
        compose("version")
        wait_ready()
        report["tests"]["audit"] = audit()
        tests = {"health": health, "distribution": distribution,
                 "failover": failover, "isolation": isolation}
        for name, check in tests.items():
            if args.mode in ("all", name):
                print(f"\n{name.upper()}", flush=True)
                report["tests"][name] = check()
        report["result"] = "PASS"
    except (Exception, KeyboardInterrupt) as exc:
        report["result"] = "FAIL"
        report["error"] = str(exc) or "Test interrupted"
        print(f"\nFAIL: {report['error']}", file=sys.stderr)
    finally:
        output = ROOT / "artifacts"
        output.mkdir(exist_ok=True)
        path = output / f"qa-{args.mode}.json"
        path.write_text(json.dumps(report, indent=2) + "\n")
        print(f"\n{report['result']} — report: {path}", flush=True)
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
