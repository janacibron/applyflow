import os, sys, json, requests
from pathlib import Path

ROOT = Path(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, str(ROOT))
try:
    from supabase_config import SUPABASE_URL, SUPABASE_SECRET_KEY
except ImportError:
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY", "")
if not SUPABASE_SECRET_KEY:
    SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
    raise SystemExit("Missing SUPABASE_URL or SUPABASE_SECRET_KEY / SUPABASE_SERVICE_ROLE_KEY")

KEY = SUPABASE_SECRET_KEY
HEADERS = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}

base = ROOT / "data"
jobs_local = json.loads((base / "jobs.json").read_text(encoding="utf-8")).get("jobs", [])
apps = json.loads((base / "applications.json").read_text(encoding="utf-8")).get("applications", [])
migration = json.loads((base / "migration_map.json").read_text(encoding="utf-8"))
user_map = migration.get("user_id_map", {})
job_map = migration.get("job_id_map", {})
local_users = {u["id"]: u for u in json.loads((base / "users.json").read_text(encoding="utf-8")).get("users", [])}

for lid in list(user_map.keys()):
    if lid not in local_users:
        rid = user_map[lid]
        r = requests.delete(f"{SUPABASE_URL}/rest/v1/users?id=eq.{rid}", headers=HEADERS, timeout=20)
        print("delete_user", lid, rid, r.status_code)
        user_map.pop(lid, None)

for lid, u in local_users.items():
    rid = user_map.get(lid)
    payload = {k: v for k, v in u.items() if k in ("email", "name", "skills", "is_premium")}
    if rid:
        requests.patch(f"{SUPABASE_URL}/rest/v1/users?id=eq.{rid}", headers=HEADERS, json=payload, timeout=20)
        print("patch_user", lid)
        continue
    pr = requests.post(f"{SUPABASE_URL}/rest/v1/users", headers=HEADERS, json=payload, timeout=20)
    print("create_user", lid, u.get("email"), pr.status_code)
    if pr.status_code == 201:
        try:
            user_map[lid] = pr.json()[0]["id"]
        except Exception:
            pass
    elif pr.status_code == 409:
        gr = requests.get(f"{SUPABASE_URL}/rest/v1/users?email=eq.{u.get('email')}", headers=HEADERS, timeout=20)
        if gr.status_code == 200 and gr.json():
            user_map[lid] = gr.json()[0]["id"]
            print("reuse_user", lid)

valid_apps = []
for a in apps:
    remote_job_id = job_map.get(a.get("job_id"))
    if not remote_job_id:
        continue
    a["remote_job_id"] = remote_job_id
    valid_apps.append(a)
print("valid_apps", len(valid_apps))

r = requests.get(f"{SUPABASE_URL}/rest/v1/applications", headers=HEADERS, timeout=20)
remote_apps = r.json() or []
for a in remote_apps:
    requests.delete(f"{SUPABASE_URL}/rest/v1/applications?id=eq.{a['id']}", headers=HEADERS, timeout=20)
    print("delete_app", a.get("id"))

inserted = 0
updated_apps = []
for a in valid_apps:
    rid = user_map.get(a.get("user_id"))
    payload = {
        "user_id": rid,
        "job_id": a.get("remote_job_id"),
        "text": a.get("text", ""),
        "score": a.get("score"),
        "status": a.get("status", "draft"),
        "generated_by": a.get("generated_by"),
    }
    if a.get("created_at"):
        payload["created_at"] = a["created_at"]
    pr = requests.post(f"{SUPABASE_URL}/rest/v1/applications", headers=HEADERS, json=payload, timeout=20)
    print("create_app", a.get("id"), pr.status_code)
    inserted += 1
    updated = dict(a)
    if pr.status_code == 201 and pr.json():
        updated["remote_id"] = pr.json()[0]["id"]
        updated["remote_user_id"] = rid
    updated_apps.append(updated)

with open(base / "applications.json", "w", encoding="utf-8") as f:
    json.dump({"applications": updated_apps}, f, indent=2, ensure_ascii=False)

updated_users = []
for u in local_users.values():
    rid = user_map.get(u.get("id"))
    nu = dict(u)
    if rid:
        nu["remote_id"] = rid
    updated_users.append(nu)
with open(base / "users.json", "w", encoding="utf-8") as f:
    json.dump({"users": updated_users}, f, indent=2, ensure_ascii=False)

try:
    migration["migrated_at"] = str(requests.get("https://worldtimeapi.org/api/timezone/Etc/UTC", timeout=15).json()["datetime"])
except Exception:
    pass
migration["user_id_map"] = user_map
migration["last_sync"] = {"users": len(local_users), "applications": len(updated_apps), "apps_inserted": inserted}
with open(base / "migration_map.json", "w", encoding="utf-8") as f:
    json.dump(migration, f, indent=2, ensure_ascii=False)
print("done")
