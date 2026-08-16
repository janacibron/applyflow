import hashlib, json, os, re, secrets, time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs

BASE = Path(__file__).resolve().parent
USERS_FILE = BASE / 'data' / 'users.json'
SESSIONS_FILE = BASE / 'data' / 'sessions.json'
LOGIN_HISTORY_FILE = BASE / 'data' / 'login_history.jsonl'

DEFAULT_ADMIN = {
    'email': 'admin@applyflow.local',
    'password_hash': '',
    'name': 'Admin',
    'skills': [],
    'role': 'admin',
    'created': None,
    'login_count': 0,
    'last_login_at': None
}

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

# Optional Supabase backend
SUPABASE_ENABLED = False
_supabase = None
_supabase_checked = False

def _init_supabase():
    global SUPABASE_ENABLED, _supabase, _supabase_checked
    if _supabase_checked:
        return
    _supabase_checked = True
    try:
        # Load .env from project root if present
        _env_path = Path(__file__).resolve().parent / '.env'
        if _env_path.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(_env_path)
            except Exception:
                pass
        from supabase_config import SUPABASE_URL, SUPABASE_SECRET_KEY
        from supabase import create_client
        if SUPABASE_URL and SUPABASE_SECRET_KEY:
            _supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
            SUPABASE_ENABLED = True
            print(f"[auth] Supabase enabled: {SUPABASE_URL}", flush=True)
        else:
            print("[auth] Supabase disabled: missing URL or secret key", flush=True)
    except Exception as e:
        SUPABASE_ENABLED = False
        _supabase = None
        print(f"[auth] Supabase init failed: {e}", flush=True)

def _now():
    return datetime.utcnow().isoformat() + 'Z'


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + '::' + password).encode('utf-8')).hexdigest()
    return f'sha256${salt}${h}'


def _verify_password(stored: str, password: str) -> bool:
    if not stored or stored.count('$') < 2:
        return False
    _, salt, expected = stored.split('$', 2)
    h = hashlib.sha256((salt + '::' + password).encode('utf-8')).hexdigest()
    return secrets.compare_digest(h, expected)


# ---------- Local file fallbacks ----------

def _load_users():
    if not USERS_FILE.exists():
        return []
    try:
        data = json.loads(USERS_FILE.read_text(encoding='utf-8'))
        return data.get('users', [])
    except Exception:
        return []


def _save_users(users):
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(json.dumps({'users': users}, indent=2), encoding='utf-8')


def _load_sessions():
    if not SESSIONS_FILE.exists():
        return {}
    try:
        return json.loads(SESSIONS_FILE.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _save_sessions(sessions):
    SESSIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SESSIONS_FILE.write_text(json.dumps(sessions, indent=2), encoding='utf-8')


def _append_login_history(entry: dict):
    LOGIN_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOGIN_HISTORY_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


# ---------- Public API ----------

def validate_email(email: str):
    errors = []
    if email is None:
        email = ''
    email = str(email).strip()
    if email == '':
        errors.append('Email is required.')
    elif not EMAIL_RE.match(email):
        errors.append('Email format is invalid.')
    return email, errors


def validate_password(password: str):
    errors = []
    if password is None:
        password = ''
    password = str(password)
    if password == '':
        errors.append('Password is required.')
    elif len(password) < 6:
        errors.append('Password must be at least 6 characters.')
    return password, errors


def validate_login(email: str, password: str):
    email_errors = []
    password_errors = []
    email, e = validate_email(email)
    email_errors.extend(e)
    password, e = validate_password(password)
    password_errors.extend(e)
    return {
        'email': email,
        'password': password,
        'email_errors': email_errors,
        'password_errors': password_errors,
        'valid': not email_errors and not password_errors
    }


def get_user(email: str):
    _init_supabase()
    if SUPABASE_ENABLED:
        try:
            result = _supabase.table('users').select('*').eq('email', email).execute()
            if result.data:
                return result.data[0]
        except Exception:
            pass
    users = _load_users()
    for user in users:
        if user.get('email') == email:
            return user
    return None


def create_user(email: str, password: str, name: str = '', skills=None):
    _init_supabase()
    if SUPABASE_ENABLED:
        try:
            existing = _supabase.table('users').select('email').eq('email', email).execute()
            if existing.data:
                return None
            payload = {
                'email': email,
                'name': name or email.split('@')[0],
                'skills': skills or [],
                'password_hash': _hash_password(password),
                'role': 'user',
                'login_count': 0,
                'last_login_at': None
            }
            res = _supabase.table('users').insert(payload).execute()
            if res.data:
                return res.data[0]
            return None
        except Exception as e:
            print(f"[auth] create_user Supabase error: {e}", flush=True)
    users = _load_users()
    if get_user(email):
        return None
    user = {
        'email': email,
        'name': name or email.split('@')[0],
        'skills': skills or [],
        'password_hash': _hash_password(password),
        'role': 'user',
        'created': _now(),
        'login_count': 0,
        'last_login_at': None,
        'remote_id': None
    }
    users.append(user)
    _save_users(users)
    return user


def ensure_default_admin():
    _init_supabase()
    if SUPABASE_ENABLED:
        try:
            existing = _supabase.table('users').select('email').eq('email', DEFAULT_ADMIN['email']).execute()
            if not existing.data:
                payload = dict(DEFAULT_ADMIN)
                payload['password_hash'] = _hash_password('admin123')
                payload['created'] = _now()
                _supabase.table('users').insert(payload).execute()
                return
        except Exception:
            pass
    users = _load_users()
    emails = {u['email'] for u in users}
    if DEFAULT_ADMIN['email'] not in emails:
        DEFAULT_ADMIN['password_hash'] = _hash_password('admin123')
        DEFAULT_ADMIN['created'] = _now()
        users.append(DEFAULT_ADMIN)
        _save_users(users)


def login_user(email: str, password: str, ip: str = '', user_agent: str = ''):
    _init_supabase()
    validation = validate_login(email, password)
    if not validation['valid']:
        return {'ok': False, 'errors': validation['email_errors'] + validation['password_errors'], 'token': None}

    user = get_user(validation['email'])
    if not user:
        return {'ok': False, 'errors': ['Invalid credentials.'], 'token': None}

    if not _verify_password(user.get('password_hash', ''), validation['password']):
        return {'ok': False, 'errors': ['Invalid credentials.'], 'token': None}

    token = secrets.token_urlsafe(32)
    now = _now()
    session_payload = {
        'token': token,
        'email': user['email'],
        'created_at': now,
        'ip': ip,
        'user_agent': user_agent,
        'expires_at': None
    }

    # Persist session and update user counters
    if SUPABASE_ENABLED:
        try:
            _supabase.table('sessions').insert(session_payload).execute()
            new_count = int(user.get('login_count', 0)) + 1
            _supabase.table('users').update({
                'login_count': new_count,
                'last_login_at': now
            }).eq('email', user['email']).execute()
            _supabase.table('login_history').insert({
                'event': 'login',
                'email': user['email'],
                'name': user.get('name'),
                'ip': ip,
                'user_agent': user_agent,
                'login_count': new_count,
                'ts': now
            }).execute()
            user_payload = {
                'email': user['email'],
                'name': user.get('name'),
                'skills': user.get('skills', []),
                'login_count': new_count,
                'last_login_at': now
            }
            return {'ok': True, 'errors': [], 'token': token, 'user': user_payload}
        except Exception as e:
            print(f"[auth] login_user Supabase error: {e}", flush=True)

    # Local fallback
    sessions = _load_sessions()
    sessions[token] = {
        'email': user['email'],
        'created_at': now,
        'ip': ip,
        'user_agent': user_agent,
        'expires_at': None
    }
    _save_sessions(sessions)

    users = _load_users()
    for idx, u in enumerate(users):
        if u.get('email') == user['email']:
            users[idx]['login_count'] = int(u.get('login_count', 0)) + 1
            users[idx]['last_login_at'] = now
            break
    _save_users(users)

    _append_login_history({
        'ts': now,
        'event': 'login',
        'email': user['email'],
        'name': user.get('name'),
        'ip': ip,
        'user_agent': user_agent,
        'login_count': users[idx]['login_count']
    })

    return {
        'ok': True,
        'errors': [],
        'token': token,
        'user': {
            'email': user['email'],
            'name': user.get('name'),
            'skills': user.get('skills', []),
            'login_count': users[idx]['login_count'],
            'last_login_at': users[idx]['last_login_at']
        }
    }


def logout_user(token: str):
    _init_supabase()
    if SUPABASE_ENABLED:
        try:
            session = _supabase.table('sessions').select('*').eq('token', token).execute()
            if session.data:
                entry = session.data[0]
                _supabase.table('sessions').delete().eq('token', token).execute()
                _supabase.table('login_history').insert({
                    'event': 'logout',
                    'email': entry.get('email'),
                    'ip': entry.get('ip'),
                    'user_agent': entry.get('user_agent'),
                    'ts': _now()
                }).execute()
                return True
            return False
        except Exception:
            pass
    sessions = _load_sessions()
    if token in sessions:
        entry = sessions.pop(token)
        _save_sessions(sessions)
        _append_login_history({
            'ts': _now(),
            'event': 'logout',
            'email': entry.get('email'),
            'ip': entry.get('ip'),
            'user_agent': entry.get('user_agent')
        })
        return True
    return False


def get_session(token: str):
    _init_supabase()
    if SUPABASE_ENABLED:
        try:
            res = _supabase.table('sessions').select('*').eq('token', token).execute()
            if res.data:
                return res.data[0]
        except Exception:
            pass
    sessions = _load_sessions()
    return sessions.get(token)


def auth_middleware(headers):
    auth = headers.get('Authorization', '') if isinstance(headers, dict) else ''
    if not auth.startswith('Bearer '):
        return None
    token = auth.split(' ', 1)[1].strip()
    if not token:
        return None
    session = get_session(token)
    if not session:
        return None
    user = get_user(session['email'])
    if not user:
        return None
    return user
