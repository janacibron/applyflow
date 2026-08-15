import os, sys, re
sys.path.insert(0, '/opt/render/project/src')
from pathlib import Path

PORT = int(os.environ.get('PORT', 8000))

# Connect Supabase
try:
    from supabase_config import SUPABASE_URL, SUPABASE_SECRET_KEY
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
    print(f"Supabase connected", flush=True)
except Exception as e:
    print(f"Supabase error: {e}", flush=True)
    supabase = None

# Read applyflow.py and STRIP the server startup
code = Path('applyflow.py').read_text(encoding='utf-8')

# Remove everything from the first "print("ApplyFlow" line onwards
# That's where the old server startup begins
lines = code.split('\n')
clean_lines = []
for line in lines:
    if 'print("ApplyFlow running' in line or 'PORT = int(os.environ' in line or 'HTTPServer' in line or 'serve_forever' in line or 'webbrowser.open' in line:
        break
    clean_lines.append(line)

clean_code = '\n'.join(clean_lines)
exec(clean_code)

# Start server ONCE
from http.server import HTTPServer
print(f"Starting server on 0.0.0.0:{PORT}", flush=True)
server = HTTPServer(('0.0.0.0', PORT), Handler)
server.serve_forever()
