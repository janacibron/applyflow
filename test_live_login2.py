import requests

r = requests.post("https://applyflow-xbi7.onrender.com/api/login",
    json={"email": "test@example.com", "password": "test"},
    timeout=60)
print(f"Status: {r.status_code}")
print(f"Body: {r.text[:300]}")
