import requests, time

# Login
r = requests.post("https://applyflow-xbi7.onrender.com/api/login",
    json={"email": "login_test@example.com", "password": "test123"},
    timeout=60)
print(f"Login: {r.status_code}")
if r.status_code == 200:
    token = r.json().get('token', '')
    print(f"Token: {'YES' if token else 'NO'}")
    
    # Get jobs
    r2 = requests.get("https://applyflow-xbi7.onrender.com/api/jobs",
        headers={"Authorization": f"Bearer {token}"},
        timeout=60)
    print(f"\n/api/jobs: {r2.status_code}")
    print(f"Length: {len(r2.text)}")
    print(f"Body: {r2.text[:500]}")
else:
    print(f"Login failed: {r.text[:200]}")
