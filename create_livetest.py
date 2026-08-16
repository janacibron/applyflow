import sys
sys.path.insert(0, 'C:/va-pipeline')
exec(open('C:/va-pipeline/supabase_config_local.py').read())

from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)

r = supabase.table('users').select('email').execute()
print("Existing Supabase users:")
for u in r.data or []:
    print(f"  {u.get('email')}")

skills = ["SEO", "Content Writing", "WordPress", "Social Media", "Email Management", "Calendar Management", "Data Entry", "Customer Service", "GoHighLevel", "Canva", "AI Tools", "Admin Support"]

result = supabase.table('users').insert({
    'email': 'livetest@example.com',
    'name': 'Live Test',
    'skills': skills,
    'password_hash': 'test',
    'role': 'user',
    'login_count': 0
}).execute()

if result.data:
    print(f"\nCreated: {result.data[0]['email']}")
    print(f"Skills: {len(result.data[0]['skills'])} skills")
else:
    print("\nFailed")
