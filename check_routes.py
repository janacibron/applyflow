import re
from pathlib import Path

code = Path('C:/va-pipeline/applyflow.py').read_text(encoding='utf-8')

# Find all route definitions
routes = re.findall(r"elif path == '([^']+)'|if path in \['([^']+)'", code)
print("Routes in applyflow.py:")
for r in routes:
    route = r[0] or r[1]
    print(f"  {route}")

# Check templates directory
templates = Path('C:/va-pipeline/templates')
if templates.exists():
    print(f"\nTemplates:")
    for f in templates.glob('*'):
        print(f"  {f.name}")
else:
    print("\nNo templates directory")
