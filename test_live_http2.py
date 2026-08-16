import subprocess, sys, time, requests

proc = subprocess.Popen(
    [sys.executable, 'C:/va-pipeline/applyflow.py'],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
time.sleep(5)

endpoints = ['/', '/signup', '/login', '/dashboard', '/api/stats', '/api/applications', '/api/jobs?email=test@example.com']
print("Live HTTP test (corrected routes):")
all_pass = True
for path in endpoints:
    try:
        r = requests.get(f"http://localhost:8000{path}", timeout=10)
        status = r.status_code
        passed = status == 200
        if not passed: all_pass = False
        print(f"  {'PASS' if passed else 'FAIL'}  {status} - {path}")
    except Exception as e:
        print(f"  FAIL  ERROR - {path}: {e}")
        all_pass = False

proc.terminate()
print(f"\n{'='*50}")
print(f"OVERALL: {'ALL PASS' if all_pass else 'SOME FAILED'}")
print(f"{'='*50}")
