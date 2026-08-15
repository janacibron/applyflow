import os, sys
sys.path.insert(0, '/opt/render/project/src')
from pathlib import Path

PORT = int(os.environ.get('PORT', 8000))

try:
    from supabase_config import SUPABASE_URL, SUPABASE_SECRET_KEY
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
    print(f"Supabase connected", flush=True)
except Exception as e:
    print(f"Supabase error: {e}", flush=True)
    supabase = None

code = Path('applyflow.py').read_text(encoding='utf-8')

# Strip server startup lines
lines = code.split('\n')
clean_lines = []
for line in lines:
    if 'print("ApplyFlow running' in line or 'PORT = int(os.environ' in line or 'HTTPServer' in line or 'serve_forever' in line or 'webbrowser.open' in line:
        break
    clean_lines.append(line)

clean_code = '\n'.join(clean_lines)

# Execute with shared globals so Handler is accessible
namespace = {'__name__': '__main__'}
exec(clean_code, namespace)

# Get Handler from namespace
Handler = namespace.get('Handler')

if Handler is None:
    print("ERROR: Handler not found in namespace", flush=True)
    sys.exit(1)

# Start server
from http.server import HTTPServer
print(f"Starting server on 0.0.0.0:{PORT}", flush=True)
server = HTTPServer(('0.0.0.0', PORT), Handler)
server.serve_forever()
