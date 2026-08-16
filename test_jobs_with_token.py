import requests

# Login to get token
r = requests.post("http://localhost:8000/api/login",
    json={"email": "login_test@example.com", "password": "test123"},
    timeout=10)
token = r.json().get('token', '')
print(f"Token: {token[:20]}...")

# Call /api/jobs with token
r2 = requests.get("http://localhost:8000/api/jobs",
    headers={"Authorization": f"Bearer {token}"},
    timeout=15)
print(f"\n/api/jobs status: {r2.status_code}")
print(f"Response length: {len(r2.text)}")
print(f"First 300 chars: {r2.text[:300]}")
