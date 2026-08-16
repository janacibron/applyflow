from pathlib import Path

code = Path('C:/va-pipeline/templates/signup.html').read_text(encoding='utf-8')
lines = code.split('\n')
for i in range(44, 55):
    print(f"{i+1}: {lines[i]}")
