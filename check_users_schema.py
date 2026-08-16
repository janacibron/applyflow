import sys, os
sys.path.insert(0, 'C:/va-pipeline')
exec(open('C:/va-pipeline/supabase_config_local.py').read())

from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)

# Get one user to see columns
r = supabase.table('users').select('*').limit(1).execute()
if r.data:
    user = r.data[0]
    print("Users table columns:")
    for key in user.keys():
        print(f"  {key}")
else:
    print("No users in Supabase")
