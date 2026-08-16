import requests

r = requests.post("http://localhost:8000/api/signup", 
    json={"email": "ui_test@example.com", "password": "test123", "name": "UI Test", "skills": ["SEO"]},
    timeout=10)
print(f"Status: {r.status_code}")
print(f"Body: {r.text[:300]}")
