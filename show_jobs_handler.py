from pathlib import Path

code = Path('C:/va-pipeline/applyflow.py').read_text(encoding='utf-8')

# Find the get_jobs method
idx = code.find('def get_jobs')
if idx > 0:
    # Show 40 lines from there
    lines = code[idx:idx+2000].split('\n')
    for i, line in enumerate(lines[:40]):
        print(f"{i+1}: {line}")
