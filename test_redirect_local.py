import requests

# Test login locally
r = requests.post("http://localhost:8000/api/login",
    json={"email": "livetest@example.com", "password": "test123"},
    timeout=10)
print(f"Login: {r.status_code}")
if r.status_code == 200:
    token = r.json().get('token', '')
    print(f"Token: {token[:20]}...")
    
    # Test dashboard with token
    r2 = requests.get("http://localhost:8000/dashboard",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10)
    print(f"Dashboard: {r2.status_code}")
    print(f"Has HTML: {'<!DOCTYPE' in r2.text}")
