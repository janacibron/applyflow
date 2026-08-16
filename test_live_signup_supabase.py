import requests, json

# Signup a new test user on live
r = requests.post("https://applyflow-xbi7.onrender.com/api/signup",
    json={"email": "supabase_test@example.com", "password": "test123", "name": "Supabase Test", "skills": ["SEO"]},
    timeout=60)
print(f"Signup: {r.status_code}")
print(f"Response: {r.text[:300]}")

# Now check if user exists in Supabase via stats
r2 = requests.get("https://applyflow-xbi7.onrender.com/api/stats", timeout=60)
print(f"\nStats after signup: {r2.text}")
