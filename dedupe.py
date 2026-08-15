"""ApplyFlow duplicate detection / idempotency guard."""
import json, hashlib
from pathlib import Path
from datetime import datetime

DATA = Path("C:/va-pipeline/data")
LOCAL_JOBS = DATA / "jobs.json"


def load_local_jobs():
    if not LOCAL_JOBS.exists():
        return []
    try:
        return json.loads(LOCAL_JOBS.read_text(encoding="utf-8")).get("jobs", [])
    except Exception:
        return []


def local_seen_urls():
    return {j.get("url", "") for j in load_local_jobs() if j.get("url")}


def local_seen_ids():
    return {j.get("id") for j in load_local_jobs() if j.get("id")}


def job_key(job):
    url = job.get("url", "") or job.get("id", "")
    return hashlib.sha256(url.encode("utf-8", errors="ignore")).hexdigest()[:16]
