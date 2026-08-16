import requests
r = requests.get("https://applyflow-xbi7.onrender.com/login", timeout=60)
code = r.text
has_cookie = 'document.cookie' in code
print(f"Cookie fix deployed: {has_cookie}")
if has_cookie:
    print("The login page will set both localStorage AND cookie")
else:
    print("Cookie fix NOT deployed - need to push and redeploy")
