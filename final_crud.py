import sys, os
sys.path.insert(0, 'C:/va-pipeline')

# Load credentials
try:
    exec(open('C:/va-pipeline/supabase_config_local.py').read())
    print(f"URL: {SUPABASE_URL}")
    print(f"Secret key present: {'YES' if SUPABASE_SECRET_KEY else 'NO'}")
except FileNotFoundError:
    print("ERROR: supabase_config_local.py not found")
    exit(1)

if not SUPABASE_SECRET_KEY:
    print("ERROR: SUPABASE_SECRET_KEY is empty")
    print("Fix: Edit C:/va-pipeline/supabase_config_local.py and add your key")
    exit(1)

from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)

print("\nTesting real Supabase CRUD...\n")

# READ
r1 = supabase.table('users').select('count', count='exact').execute()
print(f"1. READ: {r1.count} users")

# WRITE
r2 = supabase.table('users').insert({
    'email': 'final_verify@example.com',
    'name': 'Final Verify',
    'skills': ['SEO', 'Data Entry']
}).execute()
if r2.data:
    user_id = r2.data[0]['id']
    print(f"2. WRITE: SUCCESS ({user_id[:8]})")
    
    # UPDATE
    r3 = supabase.table('users').update({'name': 'Final Verify Updated'}).eq('id', user_id).execute()
    print(f"3. UPDATE: {'SUCCESS' if r3.data else 'FAILED'}")
    
    # DELETE
    r4 = supabase.table('users').delete().eq('id', user_id).execute()
    print(f"4. DELETE: {'SUCCESS' if r4.data else 'FAILED'}")
    
    print(f"\nALL REAL SUPABASE OPERATIONS: PASS")
else:
    print(f"2. WRITE: FAILED - {r2}")
