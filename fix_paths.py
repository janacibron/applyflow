from pathlib import Path

code = Path('C:/va-pipeline/applyflow.py').read_text(encoding='utf-8')

# Replace Windows paths with relative paths
code = code.replace("sys.path.insert(0, 'C:/va-pipeline')", "sys.path.insert(0, str(Path(__file__).resolve().parent))")
code = code.replace('DATA = Path("C:/va-pipeline/data")', 'DATA = Path(__file__).resolve().parent / "data"')
code = code.replace("'C:/va-pipeline'", 'str(Path(__file__).resolve().parent)')

# Write to app.py
Path('C:/va-pipeline/app.py').write_text(code, encoding='utf-8')
print("app.py fixed with relative paths")

# Verify
check = Path('C:/va-pipeline/app.py').read_text(encoding='utf-8')
has_windows_path = 'C:/va-pipeline' in check
print(f"Windows paths remaining: {has_windows_path}")
