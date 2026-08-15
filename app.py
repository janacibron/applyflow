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
lines = code.split('\n')

# Remove only the LAST 4 lines (server startup)
# They are: print, PORT=, HTTPServer, print, serve_forever
# Find the index of the FIRST "print(\"ApplyFlow running" line
startup_idx = None
for i, line in enumerate(lines):
    if 'print(\"ApplyFlow running' in line or "print('ApplyFlow running" in line:
        startup_idx = i
        break

if startup_idx:
    lines = lines[:startup_idx]
    print(f"Stripped {len(lines) - startup_idx} lines of server startup", flush=True)
else:
    print("No server startup found, using full file", flush=True)

clean_code = '\n'.join(lines)

# Execute in global namespace
global_ns = globals()
exec(clean_code, global_ns)

# Handler should now be in globals
Handler = global_ns.get('Handler')

if Handler is None:
    # Try to find it another way
    print("Handler not in globals, searching...", flush=True)
    for name, obj in global_ns.items():
        if name == 'Handler':
            Handler = obj
            break

if Handler is None:
    print("ERROR: Cannot find Handler class", flush=True)
    sys.exit(1)

print(f"Handler found: {Handler}", flush=True)

# Start server
from http.server import HTTPServer
print(f"Starting server on 0.0.0.0:{PORT}", flush=True)
server = HTTPServer(('0.0.0.0', PORT), Handler)
server.serve_forever()
