import subprocess, sys, time, requests, json

proc = subprocess.Popen(
    [sys.executable, 'C:/va-pipeline/applyflow.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
time.sleep(5)

# First login to get token
print("Testing /api/jobs with auth...")

# Try without email
try:
    r = requests.get("http://localhost:8000/api/jobs", timeout=10)
    print(f"  No email: {r.status_code}")
except Exception as e:
    print(f"  No email: ERROR - {e}")

# Try with email but no token
try:
    r = requests.get("http://localhost:8000/api/jobs?email=test@example.com", timeout=10)
    print(f"  Email, no token: {r.status_code}")
except Exception as e:
    print(f"  Email, no token: ERROR - {e}")

# Login to get token
try:
    r = requests.post("http://localhost:8000/api/login", 
                      json={"email": "test@example.com", "password": "test"},
                      timeout=10)
    print(f"\n  Login: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        token = data.get('token', '')
        print(f"  Token: {token[:20]}...")
        
        # Try with token
        r2 = requests.get("http://localhost:8000/api/jobs",
                         headers={"Authorization": f"Bearer {token}"},
                         timeout=10)
        print(f"  /api/jobs with token: {r2.status_code}")
        if r2.status_code == 200:
            jobs = r2.json().get('jobs', [])
            print(f"  Jobs returned: {len(jobs)}")
except Exception as e:
    print(f"  Login error: {e}")

proc.terminate()
