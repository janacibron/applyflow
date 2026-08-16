from pathlib import Path
code = Path('C:/va-pipeline/auth.py').read_text(encoding='utf-8')
lines = code.split('\n')
for i, line in enumerate(lines):
    if 'def create_user' in line:
        for j in range(i, min(i+50, len(lines))):
            print(f"{j+1}: {lines[j]}")
        break
