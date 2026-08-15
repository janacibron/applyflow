import json, subprocess, re
from pathlib import Path
from datetime import datetime

DATA = Path("C:/va-pipeline/data")

def ollama_classify(job, model="llama3.2:3b"):
    title = job.get('title', '')[:100]
    desc = job.get('description', '')[:300]
    skills = ', '.join(job.get('skills', [])[:5])
    
    prompt = f"""Score this VA job 0-100 for a VA skilled in SEO, Content Writing, WordPress, Social Media, GoHighLevel, Customer Service, Data Entry.

Title: {title}
Skills: {skills}
Description: {desc}

Return ONLY a number. No text."""

    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            numbers = re.findall(r'\d+', output)
            if numbers:
                return min(max(int(numbers[0]), 0), 100)
        return None
    except Exception:
        return None

with open(DATA / 'jobs.json') as f:
    data = json.load(f)

jobs = data.get('jobs', [])
print(f"Classifying {len(jobs)} jobs with llama3.2:3b...")

scored = 0
for i, job in enumerate(jobs):
    if job.get('ollama_score') is not None:
        continue
    
    title = job.get('title', 'N/A')[:50]
    score = ollama_classify(job)
    
    if score is not None:
        job['ollama_score'] = score
        job['score'] = score
        job['classified_by'] = 'ollama'
        job['classified_at'] = str(datetime.now())
        scored += 1
        print(f"[{i+1}/{len(jobs)}] {score}/100 - {title}")
    else:
        print(f"[{i+1}/{len(jobs)}] FAIL - {title}")

with open(DATA / 'jobs.json', 'w') as f:
    json.dump({"jobs": jobs}, f, indent=2)

print(f"\nScored {scored} jobs with Ollama")
