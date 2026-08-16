from pathlib import Path

code = Path('C:/va-pipeline/templates/login.html').read_text(encoding='utf-8')
print(f"Login template: {len(code)} chars")
print()

# Find the fetch/login logic
lines = code.split('\n')
for i, line in enumerate(lines):
    if 'fetch' in line or 'token' in line or 'redirect' in line or 'window.location' in line or 'dashboard' in line:
        print(f"{i+1}: {line}")
