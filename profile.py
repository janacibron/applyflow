"""VA Profile + Saved Jobs + Search/Filter extensions."""
import json
from pathlib import Path
from typing import Optional

DATA = Path(__file__).resolve().parent / 'data'
PROFILES_FILE = DATA / 'profiles.json'
SAVED_JOBS_FILE = DATA / 'saved_jobs.json'


# ---------- Profiles ----------

def load_profiles():
    if not PROFILES_FILE.exists():
        return {}
    try:
        return json.loads(PROFILES_FILE.read_text(encoding='utf-8'))
    except Exception:
        return {}


def save_profiles(profiles):
    PROFILES_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROFILES_FILE.write_text(json.dumps(profiles, indent=2), encoding='utf-8')


def get_profile(email: str) -> dict:
    return load_profiles().get(email, {})


def upsert_profile(email: str, data: dict) -> dict:
    profiles = load_profiles()
    profile = profiles.get(email, {})
    # Allowed fields
    allowed = [
        'professional_title', 'bio', 'skills', 'years_experience',
        'rate', 'availability', 'timezone', 'english_proficiency',
        'portfolio', 'resume', 'preferred_job_types', 'preferred_industries',
        'visibility'
    ]
    for field in allowed:
        if field in data:
            profile[field] = data[field]
    profile['email'] = email
    profile['updated_at'] = __import__('datetime').datetime.utcnow().isoformat() + 'Z'
    profiles[email] = profile
    save_profiles(profiles)
    return profile


def profile_completeness(email: str) -> float:
    """Return 0.0-1.0 completeness score."""
    profile = get_profile(email)
    if not profile:
        return 0.0
    key_fields = ['professional_title', 'bio', 'skills', 'years_experience', 'rate', 'availability', 'timezone']
    filled = sum(1 for f in key_fields if profile.get(f))
    return round(filled / len(key_fields), 2)


# ---------- Saved Jobs ----------

def load_saved_jobs():
    if not SAVED_JOBS_FILE.exists():
        return {}
    try:
        return json.loads(SAVED_JOBS_FILE.read_text(encoding='utf-8'))
    except Exception:
        return {}


def save_saved_jobs(data):
    SAVED_JOBS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SAVED_JOBS_FILE.write_text(json.dumps(data, indent=2), encoding='utf-8')


def save_job(email: str, job_id: str) -> bool:
    saved = load_saved_jobs()
    if email not in saved:
        saved[email] = []
    if job_id in saved[email]:
        return False
    saved[email].append(job_id)
    save_saved_jobs(saved)
    return True


def unsave_job(email: str, job_id: str) -> bool:
    saved = load_saved_jobs()
    if email not in saved or job_id not in saved[email]:
        return False
    saved[email].remove(job_id)
    save_saved_jobs(saved)
    return True


def get_saved_jobs(email: str) -> list:
    return load_saved_jobs().get(email, [])


def is_job_saved(email: str, job_id: str) -> bool:
    return job_id in get_saved_jobs(email)
