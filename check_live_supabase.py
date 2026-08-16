import requests, json

# Test the live API
r = requests.get("https://applyflow-xbi7.onrender.com/api/stats", timeout=60)
print(f"Status: {r.status_code}")
print(f"Body: {r.text}")

# The stats endpoint shows if Supabase is connected
# If jobs=0, Supabase is NOT connected on Render
