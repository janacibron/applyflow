from pathlib import Path

code = Path('C:/va-pipeline/applyflow.py').read_text(encoding='utf-8')

# Find the supabase creation and wrap it
old = """from supabase import create_client

DATA = Path(__file__).resolve().parent / "data"
supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)"""

new = """from supabase import create_client

DATA = Path(__file__).resolve().parent / "data"

# Safely connect to Supabase
supabase = None
try:
    if SUPABASE_SECRET_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
        print(f"Supabase connected", flush=True)
    else:
        print(f"Supabase skipped - no secret key", flush=True)
except Exception as e:
    print(f"Supabase connection failed: {e}", flush=True)
    supabase = None"""

code = code.replace(old, new)

Path('C:/va-pipeline/applyflow.py').write_text(code, encoding='utf-8')
print("Fixed Supabase connection at top level")
