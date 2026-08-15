import os, sys
sys.path.insert(0, '/opt/render/project/src')

PORT = int(os.environ.get('PORT', 8000))

# Import supabase
try:
    from supabase_config import SUPABASE_URL, SUPABASE_SECRET_KEY
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
    print(f"Supabase connected", flush=True)
except Exception as e:
    print(f"Supabase error: {e}", flush=True)
    supabase = None

# Read applyflow.py and strip the server startup lines
from pathlib import Path
code = Path('applyflow.py').read_text(encoding='utf-8')

# Remove the server startup at the bottom (last 5 lines)
lines = code.strip().split('\n')
# Find the last "print" and remove everything from there
for i in range(len(lines)-1, -1, -1):
    if 'HTTPServer' in lines[i] or 'serve_forever' in lines[i] or 'print(' in lines[i] and 'Running' in lines[i]:
        lines = lines[:i]
        break

code_without_server = '\n'.join(lines)
exec(code_without_server)

# Start server with correct binding
from http.server import HTTPServer
print(f"Starting server on 0.0.0.0:{PORT}", flush=True)
server = HTTPServer(('0.0.0.0', PORT), Handler)
server.serve_forever()
