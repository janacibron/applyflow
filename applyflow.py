import json, os, sys, threading
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Load .env from project root if present
_env_path = Path(__file__).resolve().parent / '.env'
if _env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_path)
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# Optional Supabase init (single source of truth: supabase_config.py)
try:
    from supabase_config import SUPABASE_URL, SUPABASE_SECRET_KEY
except Exception:
    SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
    SUPABASE_SECRET_KEY = os.environ.get('SUPABASE_SECRET_KEY', '')
supabase = None
try:
    if SUPABASE_URL and SUPABASE_SECRET_KEY:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
        print(f"[app] Supabase client initialized: {SUPABASE_URL}", flush=True)
except Exception as e:
    supabase = None
    print(f"[app] Supabase client init failed: {e}", flush=True)

# Ensure governance module is importable
try:
    from governance import log_event, read_events as _read_events
except Exception:
    def _read_events(limit=200): return []
    def log_event(*a, **k): pass

from auth import login_user, logout_user, get_session, validate_login, create_user, ensure_default_admin, get_user
from app_state import transition_application, can_transition, get_allowed_transitions, STATES, TERMINAL_STATES
from job_state import transition_job, can_transition as can_transition_job, get_allowed_transitions as get_job_transitions
from profile import get_profile, upsert_profile, profile_completeness, save_job, unsave_job, get_saved_jobs, is_job_saved

SKILL_OPTIONS = ["SEO", "Content Writing", "WordPress", "Social Media", "Email Management", "Calendar Management", "Data Entry", "Customer Service", "GoHighLevel", "Video Editing", "Canva", "Copywriting", "AI Tools", "Admin Support", "Marketing", "Sales"]

SCHEDULER_INTERVAL = int(os.environ.get("SCHEDULER_INTERVAL", "0"))

DATA = PROJECT_ROOT / 'data'
TEMPLATES = PROJECT_ROOT / 'templates'
STATIC = PROJECT_ROOT / 'static'


def start_scheduler():
    """Start background scheduler if enabled via SCHEDULER_INTERVAL > 0."""
    if SCHEDULER_INTERVAL <= 0:
        return
    from scheduler import main as scheduler_main
    t = threading.Thread(target=scheduler_main, args=(SCHEDULER_INTERVAL,), daemon=True)
    t.start()
    log_event("server_scheduler_start", {"interval_minutes": SCHEDULER_INTERVAL})

def score_job_for_user(job, user_skills):
    if not user_skills: return {"score": 0, "matched_skills": []}
    score = 0; matched = []
    combined = (job.get('title','') + ' ' + job.get('description','')).lower()
    aliases = {"SEO":["seo","keyword","ranking"],"Content Writing":["content","writing","blog"],"WordPress":["wordpress","wp"],"Social Media":["social","instagram","facebook"],"Email Management":["email","inbox"],"Calendar Management":["calendar","scheduling"],"Data Entry":["data entry","excel"],"Customer Service":["customer","support"],"GoHighLevel":["gohighlevel","ghl","crm"],"Video Editing":["video","capcut"],"Canva":["canva","design"],"Copywriting":["copywriting","copy"],"AI Tools":["ai","chatgpt"],"Admin Support":["admin","administrative"],"Marketing":["marketing","ads"],"Sales":["sales","cold call","b2b"]}
    for skill in user_skills:
        for alias in aliases.get(skill, [skill.lower()]):
            if alias in combined:
                matched.append(skill); break
    unique = list(set(matched))
    score += min(len(unique)*10, 60)
    rate = job.get('rate','') or ''
    if '$' in rate:
        import re
        amounts = re.findall(r'\$[\d,]+', rate)
        if amounts:
            try:
                rates = [float(a.replace('$','').replace(',','')) for a in amounts]
                if 4 <= min(rates) <= 15: score += 20
            except: pass
    if 'full' in (job.get('employment_type','') or '').lower(): score += 10
    dlen = len(job.get('description','') or '')
    if dlen > 500: score += 10
    elif dlen > 100: score += 5
    return {"score": min(score,100), "matched_skills": unique}

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path in ['/', '/index.html']:
            self.serve_html(self.landing_page())
        elif path == '/login':
            if self._current_token():
                self.send_response(302)
                self.send_header('Location', '/dashboard')
                self.end_headers()
                return
            html = self.render_template('login.html')
            if html is not None:
                self.serve_html(html)
        elif path == '/dashboard':
            token = self._current_token()
            if not token:
                qs = parse_qs(urlparse(self.path).query)
                token = qs.get('token', [''])[0]
            if not token:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return
            html = self.render_template('dashboard.html')
            if html is not None:
                self.serve_html(html)
        elif path == '/signup':
            if self._current_token():
                self.send_response(302)
                self.send_header('Location', '/dashboard')
                self.end_headers()
                return
            html = self.render_template('signup.html', {'skills_html': self._skills_html()})
            if html is not None:
                self.serve_html(html)
        elif path.startswith('/static/'):
            self.serve_static(path[len('/static/'):])
        elif path == '/api/jobs':
            self.serve_json(self.get_jobs(parse_qs(urlparse(self.path).query)))
        elif path == '/api/applications':
            self.serve_json(self.get_applications())
        elif path.startswith('/api/applications/') and path.endswith('/status'):
            self.do_POST()
            return
        elif path.startswith('/api/jobs/') and path.endswith('/status'):
            self.do_POST()
            return
        elif path.startswith('/api/jobs/') and path.endswith('/save'):
            self.do_POST()
            return
        elif path == '/api/stats':
            self.serve_json(self.get_stats())
        elif path == '/api/governance':
            self.serve_json({"events": _read_events(200)})
        elif path == '/api/me':
            self.serve_json(self.get_me())
        elif path == '/api/profile':
            self.serve_json(self.get_profile())
        elif path == '/api/saved-jobs':
            self.serve_json({"saved_jobs": self.get_saved_jobs()})
        elif path == '/logout':
            self.send_response(302)
            self.send_header('Location', '/login')
            self.send_header('Set-Cookie', 'va_token=; Path=/; Max-Age=0; Secure; SameSite=Strict')
            self.end_headers()
            return
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length else ""
        try: data = json.loads(body)
        except: data = parse_qs(body)
        path = urlparse(self.path).path
        if path == '/api/signup':
            result = create_user(data.get('email',''), data.get('password',''), data.get('name',''), data.get('skills',[]))
            if result is None:
                self.serve_json({"ok": False, "error": "Email already registered or signup failed"})
            else:
                self.serve_json({"ok": True, "user": result})
        elif path == '/api/login':
            ip = self.headers.get('X-Forwarded-For', self.client_address[0] if hasattr(self, 'client_address') else '')
            ua = self.headers.get('User-Agent', '')
            result = login_user(data.get('email',''), data.get('password',''), ip=ip, user_agent=ua)
            body = json.dumps(result).encode('utf-8')
            if not result.get('ok'):
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                if result.get('token'):
                    self.send_header('Set-Cookie', f"va_token=; Path=/; Max-Age=0; Secure; SameSite=Strict")
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                token = result.get('token', '')
                if token:
                    self.send_header('Set-Cookie', f"va_token={token}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age={86400}")
                self.end_headers()
                self.wfile.write(body)
        elif path == '/api/logout':
            token = data.get('token', '')
            result = {"ok": logout_user(token)}
            body = json.dumps(result).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Set-Cookie', 'va_token=; Path=/; Max-Age=0; Secure; SameSite=Strict')
            self.end_headers()
            self.wfile.write(body)
        elif path.startswith('/api/applications/') and path.endswith('/status'):
            parts = path.strip('/').split('/')
            app_id = parts[2] if len(parts) >= 3 else ''
            new_state = data.get('status', '')
            user = self._current_user()
            if not user:
                self.send_response(401); self.end_headers()
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
                return
            apps = self.get_applications().get('applications', [])
            app = next((a for a in apps if a.get('id') == app_id), None)
            if not app:
                self.send_response(404); self.end_headers()
                self.wfile.write(json.dumps({"error": "Application not found"}).encode())
                return
            if app.get('user_id') != user.get('email') and user.get('role') != 'admin':
                self.send_response(403); self.end_headers()
                self.wfile.write(json.dumps({"error": "Forbidden"}).encode())
                return
            reason = data.get('reason', '')
            updated, err = transition_application(app, new_state, actor='user', reason=reason)
            if err:
                self.send_response(422); self.end_headers()
                self.wfile.write(json.dumps({"error": err}).encode())
                return
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "application": updated}).encode())
        elif path.startswith('/api/jobs/') and path.endswith('/status'):
            parts = path.strip('/').split('/')
            job_id = parts[2] if len(parts) >= 3 else ''
            new_state = data.get('status', '')
            user = self._current_user()
            if not user:
                self.send_response(401); self.end_headers()
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
                return
            if user.get('role') not in ('admin', 'moderator'):
                self.send_response(403); self.end_headers()
                self.wfile.write(json.dumps({"error": "Forbidden — admin only"}).encode())
                return
            jobs = self.get_jobs({}).get('jobs', [])
            job = next((j for j in jobs if j.get('id') == job_id), None)
            if not job:
                self.send_response(404); self.end_headers()
                self.wfile.write(json.dumps({"error": "Job not found"}).encode())
                return
            actor = 'moderator' if user.get('role') == 'moderator' else 'system'
            updated, err = transition_job(job, new_state, actor=actor)
            if err:
                self.send_response(422); self.end_headers()
                self.wfile.write(json.dumps({"error": err}).encode())
                return
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "job": updated}).encode())
        elif path.startswith('/api/jobs/') and path.endswith('/save'):
            parts = path.strip('/').split('/')
            job_id = parts[2] if len(parts) >= 3 else ''
            user = self._current_user()
            if not user:
                self.send_response(401); self.end_headers()
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
                return
            action = data.get('action', 'save')
            if action == 'unsave':
                ok = unsave_job(user['email'], job_id)
            else:
                ok = save_job(user['email'], job_id)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": ok}).encode())
        elif path == '/api/profile':
            user = self._current_user()
            if not user:
                self.send_response(401); self.end_headers()
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
                return
            profile = upsert_profile(user['email'], data)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "profile": profile}).encode())
        else:
            self.send_response(404); self.end_headers()

    def serve_html(self, html):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def render_template(self, name, context=None):
        path = TEMPLATES / name
        if not path.exists():
            self.send_response(404)
            self.end_headers()
            return None
        html = path.read_text(encoding='utf-8')
        if context:
            for key, value in context.items():
                html = html.replace('{{ ' + key + ' }}', str(value))
        return html

    def serve_static(self, rel_path):
        safe = rel_path.replace('/', os.sep)
        if safe.startswith(os.sep) or '..' in safe:
            self.send_response(400)
            self.end_headers()
            return None
        path = STATIC / rel_path.replace('/', os.sep)
        if not path.exists() or not path.is_file():
            self.send_response(404)
            self.end_headers()
            return None
        mime = {
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.svg': 'image/svg+xml',
        }.get(path.suffix.lower(), 'application/octet-stream')
        self.send_response(200)
        self.send_header('Content-type', mime)
        self.end_headers()
        data = path.read_bytes()
        self.wfile.write(data)
        return None

    def serve_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def get_jobs(self, params):
        user = self._current_user()
        if not user:
            email = params.get('email', [''])[0]
            user = get_user(email)
        if not user: return {"jobs":[], "logged_in":False}

        jobs = []
        if supabase is not None:
            try:
                result = supabase.table('jobs').select('*').execute()
                jobs = result.data or []
            except Exception as e:
                print(f"Supabase jobs error: {e}", flush=True)
                jobs = []

        if not jobs:
            jobs_file = DATA / 'jobs.json'
            if jobs_file.exists():
                try:
                    raw = json.loads(jobs_file.read_text(encoding='utf-8'))
                    jobs = raw.get('jobs', raw) if isinstance(raw, dict) else raw
                except Exception:
                    jobs = []

        for job in jobs:
            scoring = score_job_for_user(job, user.get('skills', []))
            job['user_score'] = scoring['score']
            job['user_matched_skills'] = scoring['matched_skills']

        # Search/filter
        keyword = params.get('keyword', [''])[0].lower()
        platform = params.get('platform', [''])[0].lower()
        location = params.get('location', [''])[0].lower()
        min_score = int(params.get('min_score', ['0'])[0])
        sort_by = params.get('sort_by', ['score'])[0]
        limit = min(int(params.get('limit', ['30'])[0]), 100)

        if keyword:
            jobs = [j for j in jobs if keyword in (j.get('title','') + ' ' + j.get('description','')).lower()]
        if platform:
            jobs = [j for j in jobs if platform in (j.get('platform','') or '').lower()]
        if location:
            jobs = [j for j in jobs if location in (j.get('location','') or '').lower()]
        if min_score > 0:
            jobs = [j for j in jobs if j.get('user_score', 0) >= min_score]

        if sort_by == 'score':
            jobs = sorted(jobs, key=lambda x: x.get('user_score',0), reverse=True)
        elif sort_by == 'date':
            jobs = sorted(jobs, key=lambda x: x.get('posted_date',''), reverse=True)
        elif sort_by == 'rate':
            jobs = sorted(jobs, key=lambda x: x.get('rate',''), reverse=True)

        jobs = jobs[:limit]
        return {"jobs":jobs, "logged_in":True, "user_skills":user.get('skills',[])}

    def get_applications(self):
        apps = []
        if supabase is not None:
            try:
                result = supabase.table('applications').select('*').order('created_at', desc=True).execute()
                apps = result.data or []
            except Exception as e:
                print(f"Supabase apps error: {e}", flush=True)
                apps = []
        return {"applications": apps, "total": len(apps)}

    def get_stats(self):
        jobs_count = apps_count = users_count = 0
        if supabase is not None:
            try:
                jobs_count = supabase.table('jobs').select('count', count='exact').execute().count
                apps_count = supabase.table('applications').select('count', count='exact').execute().count
                users_count = supabase.table('users').select('count', count='exact').execute().count
            except Exception as e:
                print(f"Supabase stats error: {e}", flush=True)
        return {"total_jobs": jobs_count, "applications": apps_count, "tracked": 0, "responses": 0, "users": users_count}

    def log_message(self, *args): pass

    def _current_token(self):
        auth = self.headers.get('Authorization', '')
        if auth.startswith('Bearer '):
            token = auth.split(' ', 1)[1].strip()
            if token and get_session(token):
                return token
        cookie = self.headers.get('Cookie', '')
        for part in cookie.split(';'):
            part = part.strip()
            if part.startswith('va_token='):
                token = part.split('=', 1)[1]
                if token and get_session(token):
                    return token
        return None

    def _current_user(self):
        token = self._current_token()
        if not token:
            return None
        session = get_session(token)
        if not session:
            return None
        email = session.get('email')
        if not email:
            return None
        return get_user(email)

    def get_me(self):
        user = self._current_user()
        if not user:
            return {"logged_in": False}
        return {"logged_in": True, "user": {"email": user.get('email'), "name": user.get('name'), "skills": user.get('skills', [])}}

    def get_profile(self):
        user = self._current_user()
        if not user:
            return {"logged_in": False}
        profile = get_profile(user['email'])
        return {"logged_in": True, "profile": profile, "completeness": profile_completeness(user['email'])}

    def get_saved_jobs(self):
        user = self._current_user()
        if not user:
            return []
        return get_saved_jobs(user['email'])

    def _skills_html(self):
        return "".join(f'<label class="skill-check"><input type="checkbox" value="{s}" class="skill-box"> {s}</label>' for s in SKILL_OPTIONS)

    def landing_page(self):
        return self.render_template('landing.html') or ''

    def signup_page(self):
        return self.render_template('signup.html', {'skills_html': self._skills_html()}) or ''

    def dashboard_page(self):
        return self.render_template('dashboard.html') or ''

print("ApplyFlow running at http://localhost:8000 (Supabase backend)")
PORT = int(os.environ.get("PORT", 8000))
start_scheduler()
ensure_default_admin()
if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f'Running on 0.0.0.0:{PORT}', flush=True)
    server.serve_forever()
