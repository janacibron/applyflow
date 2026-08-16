from pathlib import Path

code = Path('C:/va-pipeline/applyflow.py').read_text(encoding='utf-8')

# Fix the get_jobs method to always return valid JSON
old = """        jobs = []
        if supabase:
            try:
                result = supabase.table('jobs').select('*').execute()
                jobs = result.data or []
            except:
                pass"""

new = """        jobs = []
        if supabase is not None:
            try:
                result = supabase.table('jobs').select('*').execute()
                jobs = result.data or []
            except Exception as e:
                print(f"Supabase jobs error: {e}", flush=True)
                jobs = []"""

code = code.replace(old, new)

# Also fix get_applications
old2 = """        apps = []
        if supabase:
            try:
                result = supabase.table('applications').select('*').order('created_at', desc=True).execute()
                apps = result.data or []
            except:
                pass"""

new2 = """        apps = []
        if supabase is not None:
            try:
                result = supabase.table('applications').select('*').order('created_at', desc=True).execute()
                apps = result.data or []
            except Exception as e:
                print(f"Supabase apps error: {e}", flush=True)
                apps = []"""

code = code.replace(old2, new2)

# Also fix get_stats
old3 = """        try:
            jobs_count = supabase.table('jobs').select('count', count='exact').execute().count
            apps_count = supabase.table('applications').select('count', count='exact').execute().count
            users_count = supabase.table('users').select('count', count='exact').execute().count
        except:
            jobs_count = apps_count = users_count = 0"""

new3 = """        jobs_count = apps_count = users_count = 0
        if supabase is not None:
            try:
                jobs_count = supabase.table('jobs').select('count', count='exact').execute().count
                apps_count = supabase.table('applications').select('count', count='exact').execute().count
                users_count = supabase.table('users').select('count', count='exact').execute().count
            except Exception as e:
                print(f"Supabase stats error: {e}", flush=True)"""

code = code.replace(old3, new3)

Path('C:/va-pipeline/applyflow.py').write_text(code, encoding='utf-8')
print("Fixed Supabase None handling in get_jobs, get_applications, get_stats")
