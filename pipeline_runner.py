"""ApplyFlow pipeline runner.

Executes the end-to-end pipeline:
  scrape -> clean titles -> fix descriptions -> classify -> sync Supabase
"""
import json, re, subprocess, sys, os
from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\va-pipeline")
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT))

from dedupe import load_local_jobs, local_seen_ids, local_seen_urls
from governance import log_event


def run_step(name, cmd, cwd=ROOT):
    log_event("pipeline_step_start", {"step": name, "cmd": cmd})
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=600,
            cwd=str(cwd),
        )
        log_event(
            "pipeline_step_end",
            {
                "step": name,
                "returncode": result.returncode,
                "stdout_tail": (result.stdout or "")[-500:],
                "stderr_tail": (result.stderr or "")[-500:],
            },
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        log_event("pipeline_step_error", {"step": name, "error": str(e)})
        return False, "", str(e)


def scrape():
    return run_step("scrape", [sys.executable, str(ROOT / "olj_scraper_v7.py")])


def clean_titles():
    if not (ROOT / "clean_titles.py").exists():
        return True, "", ""
    return run_step("clean_titles", [sys.executable, str(ROOT / "clean_titles.py")])


def fix_descriptions():
    if not (ROOT / "fix_descriptions.py").exists():
        return True, "", ""
    return run_step("fix_descriptions", [sys.executable, str(ROOT / "fix_descriptions.py")])


def classify():
    if not (ROOT / "ollama_classify.py").exists():
        return True, "", ""
    return run_step("classify", [sys.executable, str(ROOT / "ollama_classify.py")])


def dedupe_and_update_local():
    """Remove duplicate jobs from local JSON, log outcome."""
    jobs_file = DATA / "jobs.json"
    try:
        data = json.loads(jobs_file.read_text(encoding="utf-8"))
        jobs = data.get("jobs", [])
    except Exception:
        return 0

    seen_ids = set()
    seen_urls = set()
    deduped = []
    removed = 0
    for job in jobs:
        jid = job.get("id")
        url = job.get("url", "")
        if jid and jid in seen_ids:
            removed += 1
            continue
        if url and url in seen_urls:
            removed += 1
            continue
        if jid:
            seen_ids.add(jid)
        if url:
            seen_urls.add(url)
        deduped.append(job)

    data["jobs"] = deduped
    jobs_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    log_event("local_dedupe", {"removed": removed, "total_after": len(deduped)})
    return removed


def sync_supabase():
    if not (ROOT / "sync_supabase.py").exists():
        return True, "", ""
    return run_step("sync_supabase", [sys.executable, str(ROOT / "sync_supabase.py")])


def run_pipeline():
    started = datetime.utcnow().isoformat()
    log_event("pipeline_start", {"started_at": started})

    steps = [scrape, clean_titles, fix_descriptions, classify, dedupe_and_update_local, sync_supabase]
    failed = []
    for step in steps:
        ok, out, err = step() if callable(step) else (True, "", "")
        if not ok:
            failed.append(step.__name__ if callable(step) else str(step))

    completed = datetime.utcnow().isoformat()
    log_event("pipeline_end", {"completed_at": completed, "failed": failed})
    return failed


if __name__ == "__main__":
    failed = run_pipeline()
    print("Pipeline complete")
    if failed:
        print("Failed steps:", failed)
