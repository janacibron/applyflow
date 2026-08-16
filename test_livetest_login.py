import requests

r = requests.post("https://applyflow-xbi7.onrender.com/api/login",
    json={"email": "livetest@example.com", "password": "test123"},
    timeout=60)
print(f"Status: {r.status_code}")
print(f"Body: {r.text[:300]}")
