import requests

r = requests.get("https://applyflow-xbi7.onrender.com/", timeout=60)
print(f"Status: {r.status_code}")
print(f"Content length: {len(r.content)}")
print(f"First 500 chars:")
print(r.text[:500])
