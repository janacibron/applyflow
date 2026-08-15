import json, os, sys, re
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT = int(os.environ.get('PORT', 8000))

# Load the dashboard code
sys.path.insert(0, '/opt/render/project/src')
try:
    from supabase_config import SUPABASE_URL, SUPABASE_SECRET_KEY
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
    print(f"Supabase connected", flush=True)
except Exception as e:
    print(f"Supabase error: {e}", flush=True)
    supabase = None

# Read applyflow.py content
applyflow_path = Path(__file__).parent / 'applyflow.py'
if applyflow_path.exists():
    code = applyflow_path.read_text(encoding='utf-8')
    
    # Replace the server binding
    code = code.replace(
        "server = HTTPServer(('localhost', 8000), Handler)",
        f"server = HTTPServer(('0.0.0.0', {PORT}), Handler)"
    )
    code = code.replace(
        "webbrowser.open('http://localhost:8000')",
        f"print('Running on 0.0.0.0:{PORT}', flush=True)"
    )
    code = code.replace(
        "webbrowser.open(f'http://localhost:{PORT}')",
        f"print('Running on 0.0.0.0:{PORT}', flush=True)"
    )
    code = code.replace(
        "'localhost'",
        "'0.0.0.0'"
    )
    
    # Execute the modified code
    exec(code)
else:
    print("applyflow.py not found", flush=True)
