import requests
r = requests.get("https://applyflow-xbi7.onrender.com/login", timeout=60)
code = r.text
if 'Account created' in code or 'window.location.href' in code:
    print("Live has latest code")
elif 'data.token' in code:
    print("Live has OLD code - needs redeploy")
else:
    print(f"Unknown version: {code[:200]}")
