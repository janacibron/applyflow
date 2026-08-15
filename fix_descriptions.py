import json, re, http.cookiejar, urllib.request, time
from pathlib import Path
from datetime import datetime
import html as html_module

DATA = Path("C:/va-pipeline/data")
COOKIE_FILE = Path("C:/va-pipeline/cookies/olj_cookies.txt")

def get_opener():
    cookie_jar = http.cookiejar.MozillaCookieJar(str(COOKIE_FILE))
    cookie_jar.load(ignore_discard=True, ignore_expires=True)
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')]
    return opener

def fetch_description(opener, url):
    try:
        response = opener.open(url, timeout=15)
        html = response.read().decode('utf-8', errors='ignore')
        html = html_module.unescape(html)
        
        # Find text after APPLY FOR THIS JOB
        apply_pos = html.find('APPLY FOR THIS JOB')
        if apply_pos > 0:
            after = html[apply_pos + 20:]
            # Take until REPORT
            end = after.find('REPORT')
            if end > 0:
                after = after[:end]
            
            clean = re.sub(r'<script[^>]*>.*?</script>', '', after, flags=re.DOTALL)
            clean = re.sub(r'<style[^>]*>.*?</style>', '', clean, flags=re.DOTALL)
            clean = re.sub(r'<[^>]+>', ' ', clean)
            clean = re.sub(r'\s+', ' ', clean).strip()
            clean = html_module.unescape(clean)
            
            if len(clean) > 50:
                return clean[:3000]
        
        # Fallback: largest text block
        text_blocks = re.findall(r'>([^<]{100,})<', html)
        if text_blocks:
            longest = max(text_blocks, key=len)
            clean = re.sub(r'\s+', ' ', longest).strip()
            if len(clean) > 100:
                return clean[:3000]
        
        return ""
    except Exception as e:
        return ""

# Load jobs
with open(DATA / 'jobs.json', encoding='utf-8') as f:
    data = json.load(f)

jobs = data.get('jobs', [])

# Find jobs needing description fix
need_fix = []
for job in jobs:
    desc = job.get('description', '')
    dlen = len(desc)
    has_truncation = 'see more' in desc.lower() or desc.endswith('...') or desc.endswith('…')
    has_html = '<' in desc or '&amp;' in desc or '&#39;' in desc
    
    if dlen < 50 or has_truncation or has_html:
        if job.get('url'):
            need_fix.append(job)

print(f"Jobs needing description fix: {len(need_fix)}")
print(f"Fetching full descriptions...")

opener = get_opener()
fixed = 0

for i, job in enumerate(need_fix):
    url = job.get('url', '')
    if not url:
        continue
    
    print(f"[{i+1}/{len(need_fix)}] {job.get('title', 'N/A')[:50]}")
    new_desc = fetch_description(opener, url)
    
    if new_desc and len(new_desc) > 100:
        job['description'] = new_desc
        job['has_full_description'] = True
        fixed += 1
        print(f"  Fixed: {len(new_desc)} chars")
    else:
        print(f"  Skipped (no good description found)")
    
    time.sleep(1)

# Save
with open(DATA / 'jobs.json', 'w', encoding='utf-8') as f:
    json.dump({"jobs": jobs}, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print(f"Fixed: {fixed} descriptions")
print(f"Total jobs: {len(jobs)}")
