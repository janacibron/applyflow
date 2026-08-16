from pathlib import Path

code = Path('C:/va-pipeline/templates/landing.html').read_text(encoding='utf-8')
print(f"Landing template: {len(code)} chars")

# Find nav/button/login links
lines = code.split('\n')
for i, line in enumerate(lines):
    if 'login' in line.lower() or 'signup' in line.lower() or 'sign up' in line.lower() or 'sign in' in line.lower() or 'btn' in line.lower() or 'nav' in line.lower() or 'href' in line.lower():
        print(f"{i+1}: {line.strip()[:120]}")
