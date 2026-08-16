import requests

# First signup a test user
r1 = requests.post("http://localhost:8000/api/signup", 
    json={"email": "login_test@example.com", "password": "test123", "name": "Login Test", "skills": ["SEO"]},
    timeout=10)
print(f"Signup: {r1.status_code}")

# Now login
r2 = requests.post("http://localhost:8000/api/login",
    json={"email": "login_test@example.com", "password": "test123"},
    timeout=10)
print(f"\nLogin: {r2.status_code}")
print(f"Response body: {r2.text[:500]}")
