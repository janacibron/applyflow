import requests, time

print("Waiting for deploy...")
time.sleep(120)  # Wait 2 minutes for build

for i in range(3):
    try:
        r = requests.get("https://applyflow-xbi7.onrender.com/", timeout=60)
        print(f"Attempt {i+1}: Status={r.status_code}, Length={len(r.text)}")
        if r.status_code == 200 and len(r.text) > 500:
            print(f"\nSUCCESS!")
            print(f"Has ApplyFlow: {'ApplyFlow' in r.text or 'APPLYFLOW' in r.text}")
            print(f"First 200 chars:")
            print(r.text[:200])
            break
    except Exception as e:
        print(f"Attempt {i+1}: {e}")
    time.sleep(30)
