import json, subprocess, uuid
from pathlib import Path
from datetime import datetime

DATA = Path("C:/va-pipeline/data")

def ollama_generate(job, model="mistral:7b"):
    title = job.get('title', 'Position')
    company = job.get('company', 'your team')
    desc = job.get('description', '')[:300]
    skills = ', '.join(job.get('matched_skills', job.get('skills', []))[:5])
    
    prompt = f"""Write a job application for this position.

Job Title: {title}
Company: {company}
Skills: {skills}
Description: {desc}

Write from Jan Michael Acibron. Be natural and professional. No placeholders."""

    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True, timeout=60,
            encoding='utf-8', errors='ignore'
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None

with open(DATA / 'jobs.json') as f:
    data = json.load(f)

jobs = data.get('jobs', [])
# Top 5 by score
top5 = sorted(jobs, key=lambda x: x.get('score', 0), reverse=True)[:5]

print("Top 5 jobs:")
for i, job in enumerate(top5):
    print(f"  {i+1}. {job.get('score')}/100 - {job.get('title', 'N/A')[:60]}")

print(f"\nGenerating applications...")

applications = []
for i, job in enumerate(top5):
    print(f"\n[{i+1}/5] {job.get('title', 'N/A')[:60]}")
    app_text = ollama_generate(job)
    
    if app_text:
        applications.append({
            "id": f"app_{uuid.uuid4().hex[:8]}",
            "job_id": job.get('id'),
            "job_title": job.get('title'),
            "company": job.get('company'),
            "text": app_text,
            "created_at": str(datetime.now()),
            "status": "draft",
            "score": job.get('score', 0),
            "generated_by": "ollama_mistral"
        })
        print(f"  Generated {len(app_text)} chars")
    else:
        print(f"  Failed")

# Save
apps_file = DATA / 'applications.json'
existing = {"applications": []}
if apps_file.exists():
    try:
        with open(apps_file) as f: existing = json.load(f)
    except: pass

existing_job_ids = {a.get('job_id') for a in existing.get('applications', [])}
new_apps = [a for a in applications if a.get('job_id') not in existing_job_ids]
combined = existing.get('applications', []) + new_apps

with open(apps_file, 'w') as f:
    json.dump({"applications": combined}, f, indent=2)

print(f"\nGenerated {len(new_apps)} applications")
print(f"Total: {len(combined)}")

# Show first application
if new_apps:
    print(f"\n{'='*60}")
    print("SAMPLE APPLICATION")
    print(f"{'='*60}")
    print(new_apps[0]['text'][:500])
