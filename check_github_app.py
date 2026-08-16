import requests

r = requests.get("https://raw.githubusercontent.com/janacibron/applyflow/main/app.py", timeout=30)
code = r.text
print(f"app.py on GitHub: {len(code)} chars")
print()

# Check if do_GET handles root path
if "path in ['/', '/index.html']" in code:
    print("Root route: YES")
if "render_template" in code:
    print("render_template: YES")
if "landing_page" in code:
    print("landing_page: YES")
if "templates" in code:
    print("templates path: YES")

# Show first 30 lines
print("\nFirst 30 lines:")
for line in code.split('\n')[:30]:
    print(f"  {line}")
