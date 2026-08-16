import requests

r = requests.get("https://raw.githubusercontent.com/janacibron/applyflow/main/supabase_config.py", timeout=30)
print(f"supabase_config.py on GitHub:")
print(r.text)
