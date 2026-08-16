import subprocess, sys, time, requests

# Start server in background
proc = subprocess.Popen(
    [sys.executable, 'C:/va-pipeline/applyflow.py'],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
time.sleep(5)

# Test endpoints
endpoints = ['/', '/signup', '/app', '/api/stats', '/api/applications']
print("Live HTTP test:")
for path in endpoints:
    try:
        r = requests.get(f"http://localhost:8000{path}", timeout=10)
        print(f"  {r.status_code} - {path}")
    except Exception as e:
        print(f"  FAIL - {path}: {e}")

# Kill server
proc.terminate()
print("\nServer killed. Test complete.")
