from pathlib import Path

code = Path('C:/va-pipeline/templates/dashboard.html').read_text(encoding='utf-8')
print(f"Dashboard template: {len(code)} chars")

# Find loading/spinner and fetch logic
lines = code.split('\n')
for i, line in enumerate(lines):
    if 'spinner' in line.lower() or 'loading' in line.lower() or 'fetch' in line or 'va_token' in line or 'Authorization' in line:
        print(f"{i+1}: {line.strip()[:100]}")
