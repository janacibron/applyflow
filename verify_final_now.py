import requests, time

print("Waiting 30 seconds for cold start...")
time.sleep(30)

r = requests.get("https://applyflow-xbi7.onrender.com/", timeout=60)
print(f"Status: {r.status_code}")
print(f"Length: {len(r.text)}")
print(f"Has HTML: {'<!DOCTYPE' in r.text or '<html' in r.text}")
print(f"Has ApplyFlow: {'ApplyFlow' in r.text or 'APPLYFLOW' in r.text}")
print(f"\nFirst 300 chars:")
print(r.text[:300])
