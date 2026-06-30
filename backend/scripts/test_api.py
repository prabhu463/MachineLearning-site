import urllib.request
import json
import sys

base = "http://localhost:8000/api/v1"
failures = []


def get(path):
    try:
        with urllib.request.urlopen(base + path) as r:
            return json.loads(r.read())
    except Exception as e:
        failures.append(f"GET {path}: {e}")
        return None


def post(path, body):
    try:
        data = json.dumps(body).encode()
        req = urllib.request.Request(
            base + path, data=data,
            headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except Exception as e:
        failures.append(f"POST {path}: {e}")
        return None


# 1. Health with DB check
d = get("/health")
print(f"[1] Health: {d}")
if d and d.get("database") != "ok":
    failures.append(f"database status not ok: {d}")

# 2. Dashboard summary
d = get("/dashboard/summary")
print(f"[2] Dashboard: {d}")

# 3. Predict endpoint
d = post(
    "/predict?auto_execute=true",
    {"service_name": "checkout", "cpu_usage": 84, "memory_usage": 78,
     "disk_usage": 66, "network_latency_ms": 260, "request_count": 980,
     "error_rate": 0.18, "response_time_ms": 730}
)
if d:
    print(f"[3] Predict: label={d['predicted_label']}, risk={d['risk_score']:.3f}, incident={d['incident_created']}")
else:
    print("[3] Predict: FAILED")

# 4. Incidents
d = get("/incidents?limit=5")
print(f"[4] Incidents: {len(d) if d else 0} found")

# 5. Actions
d = get("/actions?limit=5")
print(f"[5] Actions: {len(d) if d else 0} found")

# 6. Metrics
d = get("/metrics?limit=5")
print(f"[6] Metrics: {len(d) if d else 0} found")

print()
if failures:
    print("FAILURES:")
    for f in failures:
        print(" -", f)
    sys.exit(1)
else:
    print("ALL TESTS PASSED")
