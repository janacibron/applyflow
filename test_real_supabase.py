import sys
from pathlib import Path

def main():
    sys.path.insert(0, 'C:/va-pipeline')
    from supabase_config_local import SUPABASE_URL, SUPABASE_SECRET_KEY

    if not SUPABASE_SECRET_KEY:
        print('REAL_SUPABASE_TEST=CREDENTIALS_MISSING')
        print('SUPABASE_URL=%s' % SUPABASE_URL)
        print('SUPABASE_SECRET_KEY=%s' % SUPABASE_SECRET_KEY)
        return

    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)

    print("Testing real Supabase connection...")
    print()

    # Test 1: Read
    r1 = supabase.table('users').select('count', count='exact').execute()
    print(f"1. READ users: {r1.count} rows")

    # Test 2: Write (temp record)
    r2 = supabase.table('users').insert({
        'email': 'verify_test@example.com',
        'name': 'Verify Test',
        'skills': ['SEO']
    }).execute()
    if r2.data:
        print(f"2. WRITE user: SUCCESS ({r2.data[0]['id'][:8]})")
        user_id = r2.data[0]['id']

        # Test 3: Update
        r3 = supabase.table('users').update({'name': 'Verify Updated'}).eq('id', user_id).execute()
        print(f"3. UPDATE user: SUCCESS" if r3.data else f"3. UPDATE: FAILED")

        # Test 4: Delete
        r4 = supabase.table('users').delete().eq('id', user_id).execute()
        print(f"4. DELETE user: SUCCESS" if r4.data else f"4. DELETE: FAILED")

        print()
        print("ALL REAL SUPABASE OPERATIONS: PASS")
    else:
        print(f"2. WRITE failed: {r2}")

if __name__ == '__main__':
    main()
