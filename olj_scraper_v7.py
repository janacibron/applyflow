import json, re, http.cookiejar, urllib.request, sys
from pathlib import Path
from datetime import datetime
import html as html_module
import hashlib

COOKIE_FILE = Path("C:/va-pipeline/cookies/olj_cookies.txt")
DATA = Path("C:/va-pipeline/data")
ROOT = Path("C:/va-pipeline")
sys.path.insert(0, str(ROOT))
from governance import log_event
from dedupe import load_local_jobs, local_seen_ids, local_seen_urls


def get_opener():
    cookie_jar = http.cookiejar.MozillaCookieJar(str(COOKIE_FILE))
    cookie_jar.load(ignore_discard=True, ignore_expires=True)
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')]
    return opener


def scrape_olj(opener, category):
    url = f"https://www.onlinejobs.ph/jobseekers/search/c/{category}"
    response = opener.open(url, timeout=15)
    html = response.read().decode('utf-8', errors='ignore')
    html = html_module.unescape(html)
    
    anchors = re.findall(r'<a[^>]*href="(/jobseekers/job/[^"]*?)"[^>]*>(.*?)</a>', html, re.DOTALL)
    
    jobs = []
    seen_urls = set()
    
    for href, raw_text in anchors:
        if href in seen_urls:
            continue
        seen_urls.add(href)
        
        # Clean text
        text = re.sub(r'<[^>]+>', ' ', raw_text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        if not text or text.lower() == 'see more':
            continue
        if len(text) < 5:
            continue
        
        # Extract posted date
        posted_date = ""
        date_match = re.search(r'Posted on\s*([\d-]+)', text)
        if date_match:
            posted_date = date_match.group(1)
            text = text.replace(date_match.group(0), '').strip()
        
        # Extract rate from text
        rate = ""
        rate_patterns = [
            r'\$[\d,]+(?:\.\d{2})?\s*(?:-\s*\$[\d,]+)?\s*/?\s*(?:per\s*)?(?:month|hour|hr|mo)?',
            r'\b\d+(?:K)?\s*(?:PHP|Php|₱)\b',
            r'\$[\d,]+(?:\.\d{2})?',
        ]
        for pattern in rate_patterns:
            rate_match = re.search(pattern, text, re.IGNORECASE)
            if rate_match:
                rate = rate_match.group(0).strip()
                text = text.replace(rate_match.group(0), '').strip()
                break
        
        # Extract employment type
        emp_type = ""
        for etype in ["Full Time", "Part-Time", "Part Time", "Gig", "Freelance"]:
            if etype.lower() in text.lower():
                emp_type = etype
                text = re.sub(re.escape(etype), '', text, flags=re.IGNORECASE).strip()
                break
        
        # Extract company - pattern is "Title CompanyName •" or "Title • CompanyName"
        company = ""
        # Look for separator patterns
        sep_patterns = [r'\s*•\s*([^•]+?)$', r'\s+([A-Z][A-Za-z\s&]+?)$']
        for pattern in sep_patterns:
            company_match = re.search(pattern, text)
            if company_match:
                potential_company = company_match.group(1).strip()
                # Only treat as company if it looks like a name (not description)
                if len(potential_company) < 50 and not any(kw in potential_company.lower() for kw in ['posted', 'full time', 'part time', 'see more']):
                    company = potential_company
                    text = text.replace(company_match.group(0), '').strip()
                    break
        
        # Remaining text is the title
        title = text.strip()
        
        if not title:
            continue
        
        # Extract skills
        skills = []
        skill_keywords = ["GoHighLevel", "SEO", "WordPress", "Excel", "Social Media", "Canva", "Customer Service", "Data Entry", "Email", "Calendar", "Communication", "Writing", "Content", "Marketing", "Sales", "Support", "Photoshop", "Video", "Capcut", "Cold Call", "B2B", "Collections", "Payroll", "Amazon", "FBA", "Bookkeeping", "Accounting", "Medical", "Dental", "Credit", "AI", "Copywriting", "NDIS", "ShiftCare", "Compliance", "Creative", "Ecom", "Account Executive", "Call Handling", "Receptionist", "Real Estate", "Mortgage"]
        combined_text = title + " " + company
        for kw in skill_keywords:
            if kw.lower() in combined_text.lower():
                if kw not in skills:
                    skills.append(kw)
        
        job_id = hashlib.md5(href.encode()).hexdigest()[:10]
        
        jobs.append({
            "id": f"olj_{job_id}",
            "title": title,
            "company": company or "OLJ Employer",
            "platform": "OnlineJobs.ph",
            "url": f"https://www.onlinejobs.ph{href}",
            "description": title,
            "rate": rate,
            "employment_type": emp_type,
            "posted_date": posted_date,
            "skills": skills[:8],
            "location": "Philippines",
            "scraped_at": str(datetime.now()),
            "fresh": True
        })
    
    return jobs


if __name__ == "__main__":
    opener = get_opener()
    print("="*60)
    print("OLJ SCRAPER V7 - Clean Data")
    print("="*60)

    all_jobs = []
    categories = ["virtual-assistant", "seo", "social-media-marketing", "data-entry", "customer-support"]
    for cat in categories:
        print(f"\nCategory: {cat}")
        try:
            jobs = scrape_olj(opener, cat)
            all_jobs.extend(jobs)
            print(f"  Jobs: {len(jobs)}")
        except Exception as e:
            print(f"  Error: {e}")

    # Merge with existing while deduping by URL/id
    jobs_file = DATA / "jobs.json"
    existing_jobs = load_local_jobs()
    existing_ids = local_seen_ids()
    existing_urls = local_seen_urls()

    new_jobs = []
    seen_ids = set(existing_ids)
    seen_urls = set(existing_urls)
    for job in existing_jobs:
        seen_ids.add(job.get("id", ""))
        seen_urls.add(job.get("url", ""))
    for job in all_jobs:
        jid = job.get("id", "")
        url = job.get("url", "")
        if jid and jid in seen_ids:
            continue
        if url and url in seen_urls:
            continue
        new_jobs.append(job)
        if jid:
            seen_ids.add(jid)
        if url:
            seen_urls.add(url)

    combined = existing_jobs + new_jobs
    with open(jobs_file, 'w') as f:
        json.dump({"jobs": combined}, f, indent=2)

    log_event(
        "scrape_complete",
        {
            "olj_new": len(new_jobs),
            "olj_raw": len(all_jobs),
            "total": len(combined),
            "skipped_duplicates": len(all_jobs) - len(new_jobs),
        },
    )
    print(f"\n{'='*60}")
    print(f"OLJ new: {len(new_jobs)}")
    print(f"Skipped duplicates: {len(all_jobs) - len(new_jobs)}")
    print(f"Total DB: {len(combined)}")
    print(f"{'='*60}")

    print(f"\nClean sample:")
    for job in new_jobs[:15]:
        print(f"\n  Title: {job['title'][:70]}")
        if job.get('company') and job['company'] != 'OLJ Employer': print(f"  Company: {job['company']}")
        if job.get('rate'): print(f"  Rate: {job['rate']}")
        if job.get('employment_type'): print(f"  Type: {job['employment_type']}")
        if job.get('posted_date'): print(f"  Posted: {job['posted_date']}")
        if job.get('skills'): print(f"  Skills: {', '.join(job['skills'][:5])}")
