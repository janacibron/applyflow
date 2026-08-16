from pathlib import Path

code = Path('C:/va-pipeline/applyflow.py').read_text(encoding='utf-8')

# Add supabase check before using it
old = """        try:
            result = supabase.table('jobs').select('*').execute()
            jobs = result.data or []
        except:
            jobs = []"""

new = """        jobs = []
        if supabase:
            try:
                result = supabase.table('jobs').select('*').execute()
                jobs = result.data or []
            except:
                pass"""

code = code.replace(old, new)

# Also fix get_applications and get_stats
old2 = """        try:
            result = supabase.table('applications').select('*').order('created_at', desc=True).execute()
            apps = result.data or []
        except:
            apps = []"""

new2 = """        apps = []
        if supabase:
            try:
                result = supabase.table('applications').select('*').order('created_at', desc=True).execute()
                apps = result.data or []
            except:
                pass"""

code = code.replace(old2, new2)

Path('C:/va-pipeline/applyflow.py').write_text(code, encoding='utf-8')
print("Fixed supabase None checks in get_jobs and get_applications")
