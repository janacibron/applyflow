import json, subprocess
from pathlib import Path

DATA = Path("C:/va-pipeline/data")

def clean_with_llm(title):
    prompt = f'Clean this job title. Remove salary, compensation, location, duplicate words, and HTML artifacts. Return ONLY the clean title, nothing else: {title}'
    
    try:
        result = subprocess.run(
            ['ollama', 'run', 'llama3.2:3b', prompt],
            capture_output=True, timeout=30,
            encoding='utf-8', errors='ignore'
        )
        return result.stdout.strip()
    except Exception:
        return title

with open(DATA / 'jobs.json', encoding='utf-8') as f:
    data = json.load(f)

jobs = data.get('jobs', [])
messy = [j for j in jobs if j.get('title') and (len(j['title']) > 60 or '$' in j['title'] or ':' in j['title'])]

print(f"Cleaning {len(messy)} messy titles...")
print()

cleaned = 0
for i, job in enumerate(messy):
    old = job['title']
    new = clean_with_llm(old)
    
    if new and new != old and len(new) > 3:
        job['title'] = new
        job['original_title'] = old
        cleaned += 1
        print(f"[{i+1}/{len(messy)}] {new[:70]}")
    else:
        print(f"[{i+1}/{len(messy)}] KEPT: {old[:70]}")

with open(DATA / 'jobs.json', 'w', encoding='utf-8') as f:
    json.dump({"jobs": jobs}, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print(f"Cleaned: {cleaned} titles")
print(f"Total jobs: {len(jobs)}")
print(f"Saved to jobs.json")
