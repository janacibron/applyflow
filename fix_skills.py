import sys
sys.path.insert(0, 'C:/va-pipeline')
exec(open('C:/va-pipeline/supabase_config_local.py').read())

from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)

skills = ["SEO", "Content Writing", "WordPress", "Social Media", "Email Management", "Calendar Management", "Data Entry", "Customer Service", "GoHighLevel", "Canva", "AI Tools", "Admin Support"]

result = supabase.table('users').update({'skills': skills}).eq('email', 'livetest@example.com').execute()
if result.data:
    print(f"Updated: {result.data[0].get('email')}")
    print(f"Skills: {result.data[0].get('skills')}")
else:
    print("Failed - user not found or Supabase not connected")
