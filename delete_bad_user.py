import sys
sys.path.insert(0, 'C:/va-pipeline')
exec(open('C:/va-pipeline/supabase_config_local.py').read())

from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)

# Delete the user with invalid hash
r = supabase.table('users').delete().eq('email', 'livetest@example.com').execute()
print(f"Deleted: {r.data}")
