import sys, os
sys.path.insert(0, 'C:/va-pipeline')

# Load credentials
try:
    exec(open('C:/va-pipeline/supabase_config_local.py').read())
    print(f"SUPABASE_URL: {SUPABASE_URL}")
    print(f"SUPABASE_SECRET_KEY present: {'YES' if SUPABASE_SECRET_KEY else 'NO'}")
except Exception as e:
    print(f"Config load error: {e}")
    exit(1)

# Try connecting
try:
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
    print(f"SUPABASE_CONNECTED: YES")
except Exception as e:
    print(f"SUPABASE_CONNECTED: NO - {e}")
    exit(1)

# Test jobs query
try:
    result = supabase.table('jobs').select('count', count='exact').execute()
    print(f"JOBS_QUERY: SUCCESS")
    print(f"JOB_COUNT: {result.count}")
except Exception as e:
    print(f"JOBS_QUERY: ERROR - {e}")

# Test first job
try:
    result = supabase.table('jobs').select('title, company, score').limit(1).execute()
    if result.data:
        job = result.data[0]
        print(f"FIRST_JOB: {job.get('title', 'N/A')[:50]} @ {job.get('company', 'N/A')} ({job.get('score', 'N/A')}/100)")
    else:
        print(f"FIRST_JOB: No jobs found")
except Exception as e:
    print(f"FIRST_JOB: ERROR - {e}")
