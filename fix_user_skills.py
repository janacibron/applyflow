import requests, json

# Login to get token
r = requests.post("https://applyflow-xbi7.onrender.com/api/login",
    json={"email": "livetest@example.com", "password": "test123"},
    timeout=60)
token = r.json().get('token', '')
print(f"Token: {token[:20]}...")

# Update skills
skills = ["SEO", "Content Writing", "WordPress", "Social Media", "Email Management", "Calendar Management", "Data Entry", "Customer Service", "GoHighLevel", "Canva", "AI Tools", "Admin Support"]

# Try to update via Supabase directly
import sys, os
sys.path.insert(0, 'C:/va-pipeline')
exec(open('C:/va-pipeline/supabase_config_local.py').read())

from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)

# Update user
result = supabase.table('users').update({'skills': skills}).eq('email', 'livetest@example.com').execute()
if result.data:
    print(f"Updated skills: {result.data[0].get('skills')}")
else:
    print("Failed to update")
