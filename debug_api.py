import subprocess, sys, time, requests, json

proc = subprocess.Popen(
    [sys.executable, 'C:/va-pipeline/applyflow.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)
time.sleep(4)

# Test /api/jobs and capture server output
try:
    r = requests.get("http://localhost:8000/api/jobs?email=test@example.com", timeout=5)
    print(f"Status: {r.status_code}")
    print(f"Body: {r.text[:200]}")
except Exception as e:
    print(f"Request error: {e}")

time.sleep(1)

# Check server logs
stdout, stderr = proc.communicate(timeout=5)
print(f"\nServer stdout (last 500 chars):")
print(stdout[-500:] if stdout else "No stdout")
print(f"\nServer stderr (last 500 chars):")
print(stderr[-500:] if stderr else "No stderr")
