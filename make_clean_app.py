from pathlib import Path

# Read the current applyflow.py
source = Path('C:/va-pipeline/applyflow.py').read_text(encoding='utf-8')

# app.py should be EXACTLY the same as applyflow.py
# No exec wrapper, no duplicate code
Path('C:/va-pipeline/app.py').write_text(source, encoding='utf-8')
print(f"app.py is now clean copy of applyflow.py ({len(source)} chars)")
