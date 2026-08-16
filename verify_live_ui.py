import requests
r = requests.get("https://applyflow-xbi7.onrender.com/", timeout=60)
print(f"Status: {r.status_code}")
print(f"Length: {len(r.text)}")
print(f"Has ApplyFlow: {'ApplyFlow' in r.text or 'APPLYFLOW' in r.text}")
print(f"First 200 chars: {r.text[:200]}")
