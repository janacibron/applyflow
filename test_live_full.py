import requests

# Signup first
r1 = requests.post("https://applyflow-xbi7.onrender.com/api/signup",
    json={"email": "livetest@example.com", "password": "test123", "name": "Live Test", "skills": ["SEO", "Data Entry"]},
    timeout=60)
print(f"Signup: {r1.status_code}")
print(f"Body: {r1.text[:200]}")

# Then login
r2 = requests.post("https://applyflow-xbi7.onrender.com/api/login",
    json={"email": "livetest@example.com", "password": "test123"},
    timeout=60)
print(f"\nLogin: {r2.status_code}")
print(f"Body: {r2.text[:300]}")

if r2.status_code == 200:
    token = r2.json().get('token', '')
    print(f"\nToken: {'YES' if token else 'NO'}")
    
    # Get jobs
    r3 = requests.get("https://applyflow-xbi7.onrender.com/api/jobs",
        headers={"Authorization": f"Bearer {token}"},
        timeout=60)
    print(f"\n/api/jobs: {r3.status_code}")
    print(f"Length: {len(r3.text)}")
    print(f"First 300: {r3.text[:300]}")
