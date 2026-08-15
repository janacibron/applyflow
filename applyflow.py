import json, os, sys, webbrowser
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, 'C:/va-pipeline')
from supabase_config import SUPABASE_URL, SUPABASE_SECRET_KEY

from supabase import create_client

DATA = Path("C:/va-pipeline/data")
supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)

SKILL_OPTIONS = ["SEO", "Content Writing", "WordPress", "Social Media", "Email Management", "Calendar Management", "Data Entry", "Customer Service", "GoHighLevel", "Video Editing", "Canva", "Copywriting", "AI Tools", "Admin Support", "Marketing", "Sales"]

def get_user(email):
    try:
        result = supabase.table('users').select('*').eq('email', email).execute()
        if result.data:
            return result.data[0]
    except: pass
    return None

def signup(email, name, skills):
    if get_user(email): return {"error": "Email exists"}
    try:
        result = supabase.table('users').insert({
            'email': email, 'name': name or email.split('@')[0], 'skills': skills
        }).execute()
        if result.data:
            return result.data[0]
    except Exception as e:
        return {"error": str(e)}
    return {"error": "Failed"}

def score_job_for_user(job, user_skills):
    if not user_skills: return {"score": 0, "matched_skills": []}
    score = 0; matched = []
    combined = (job.get('title','') + ' ' + job.get('description','')).lower()
    aliases = {"SEO":["seo","keyword","ranking"],"Content Writing":["content","writing","blog"],"WordPress":["wordpress","wp"],"Social Media":["social","instagram","facebook"],"Email Management":["email","inbox"],"Calendar Management":["calendar","scheduling"],"Data Entry":["data entry","excel"],"Customer Service":["customer","support"],"GoHighLevel":["gohighlevel","ghl","crm"],"Video Editing":["video","capcut"],"Canva":["canva","design"],"Copywriting":["copywriting","copy"],"AI Tools":["ai","chatgpt"],"Admin Support":["admin","administrative"],"Marketing":["marketing","ads"],"Sales":["sales","cold call","b2b"]}
    for skill in user_skills:
        for alias in aliases.get(skill, [skill.lower()]):
            if alias in combined:
                matched.append(skill); break
    unique = list(set(matched))
    score += min(len(unique)*10, 60)
    rate = job.get('rate','') or ''
    if '$' in rate:
        import re
        amounts = re.findall(r'\\$[\d,]+', rate)
        if amounts:
            try:
                rates = [float(a.replace('$','').replace(',','')) for a in amounts]
                if 4 <= min(rates) <= 15: score += 20
            except: pass
    if 'full' in (job.get('employment_type','') or '').lower(): score += 10
    dlen = len(job.get('description','') or '')
    if dlen > 500: score += 10
    elif dlen > 100: score += 5
    return {"score": min(score,100), "matched_skills": unique}

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path in ['/', '/index.html']:
            self.serve_html(self.landing_page())
        elif path == '/app':
            self.serve_html(self.dashboard_page())
        elif path == '/signup':
            self.serve_html(self.signup_page())
        elif path == '/api/jobs':
            self.serve_json(self.get_jobs(parse_qs(urlparse(self.path).query)))
        elif path == '/api/applications':
            self.serve_json(self.get_applications())
        elif path == '/api/stats':
            self.serve_json(self.get_stats())
        else:
            self.send_response(404); self.end_headers()
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length else ""
        try: data = json.loads(body)
        except: data = parse_qs(body)
        path = urlparse(self.path).path
        if path == '/api/signup':
            self.serve_json(signup(data.get('email',''), data.get('name',''), data.get('skills',[])))
        else:
            self.send_response(404); self.end_headers()
    
    def serve_html(self, html):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def get_jobs(self, params):
        email = params.get('email', [''])[0]
        user = get_user(email)
        if not user: return {"jobs":[], "logged_in":False}
        
        try:
            result = supabase.table('jobs').select('*').execute()
            jobs = result.data or []
        except:
            jobs = []
        
        for job in jobs:
            scoring = score_job_for_user(job, user.get('skills', []))
            job['user_score'] = scoring['score']
            job['user_matched_skills'] = scoring['matched_skills']
        
        jobs = sorted(jobs, key=lambda x: x.get('user_score',0), reverse=True)
        return {"jobs":jobs, "logged_in":True, "user_skills":user.get('skills',[])}
    
    def get_applications(self):
        try:
            result = supabase.table('applications').select('*').order('created_at', desc=True).execute()
            apps = result.data or []
        except:
            apps = []
        return {"applications": apps, "total": len(apps)}
    
    def get_stats(self):
        try:
            jobs_count = supabase.table('jobs').select('count', count='exact').execute().count
            apps_count = supabase.table('applications').select('count', count='exact').execute().count
            users_count = supabase.table('users').select('count', count='exact').execute().count
        except:
            jobs_count = apps_count = users_count = 0
        return {"total_jobs": jobs_count, "applications": apps_count, "tracked": 0, "responses": 0, "users": users_count}
    
    def log_message(self, *args): pass
    
    def landing_page(self):
        return """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>ApplyFlow</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script><style>
:root{--graphite:#14171B;--graphite-panel:#1B1F25;--steel:#2A2F37;--steel-line:#363C46;--manifest:#EDEFF1;--manifest-dim:#9BA3AE;--amber:#F2A93B;--cyan:#4FD1C5;}
body{background:var(--graphite);color:var(--manifest);font-family:'IBM Plex Sans',sans-serif;}
.font-mono-brand{font-family:'IBM Plex Mono',monospace;}
.tag{font-family:'IBM Plex Mono',monospace;font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:var(--manifest-dim);}
.panel{background:var(--graphite-panel);border:1px solid var(--steel-line);border-radius:.5rem;}
.btn-primary{background:var(--amber);color:var(--graphite);font-family:'IBM Plex Mono',monospace;font-weight:600;}
.btn-ghost{border:1px solid var(--steel-line);color:var(--manifest);font-family:'IBM Plex Mono',monospace;}
.divider{border-top:1px solid var(--steel-line);}
</style></head><body>
<header class="sticky top-0 z-40 backdrop-blur bg-[var(--graphite)]/85 divider"><div class="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
<a href="/" class="font-mono-brand font-semibold">APPLYFLOW</a>
<nav class="flex items-center gap-6 tag"><a href="/signup" class="hover:text-[var(--cyan)]">Sign Up</a><a href="/app" class="hover:text-[var(--cyan)]">Dashboard</a></nav>
<a href="/signup" class="btn-primary text-xs px-4 py-2 rounded">Get Started</a>
</div></header>
<section class="max-w-6xl mx-auto px-6 pt-20 pb-16 grid md:grid-cols-2 gap-12 items-center">
<div><p class="tag mb-4">Supabase-powered VA job pipeline</p>
<h1 class="font-mono-brand font-semibold text-4xl md:text-5xl leading-tight">Jobs matched to YOUR skills.</h1>
<p class="mt-6 text-lg text-[var(--manifest-dim)] max-w-md">Select your skills. We scrape, score, and generate applications tailored to you.</p>
<div class="mt-8 flex gap-4"><a href="/signup" class="btn-primary px-6 py-3 rounded text-sm">Set Up Profile</a><a href="/app" class="btn-ghost px-6 py-3 rounded text-sm">View Dashboard</a></div></div>
<div class="panel p-5 font-mono-brand text-[13px]"><div class="flex justify-between mb-3"><span class="tag">supabase.log</span><span class="tag text-[var(--cyan)]">connected</span></div>
<div class="space-y-1"><div>[DB] 150 jobs in Supabase</div><div>[USER] Personalized scoring</div><div class="text-[var(--amber)]">[MATCH] Top jobs found</div></div></div>
</section>
<footer class="divider"><div class="max-w-6xl mx-auto px-6 py-10 text-center tag">ApplyFlow 2026</div></footer>
</body></html>"""
    
    def signup_page(self):
        skills_html = "".join(f'<label class="skill-check"><input type="checkbox" value="{s}" class="skill-box"> {s}</label>' for s in SKILL_OPTIONS)
        return """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>ApplyFlow - Sign Up</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script><style>
:root{--graphite:#14171B;--graphite-panel:#1B1F25;--steel:#2A2F37;--steel-line:#363C46;--manifest:#EDEFF1;--manifest-dim:#9BA3AE;--amber:#F2A93B;--cyan:#4FD1C5;}
body{background:var(--graphite);color:var(--manifest);font-family:'IBM Plex Sans',sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;}
.panel{background:var(--graphite-panel);border:1px solid var(--steel-line);border-radius:.5rem;}
.tag{font-family:'IBM Plex Mono',monospace;font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:var(--manifest-dim);}
.font-mono-brand{font-family:'IBM Plex Mono',monospace;}
.btn-primary{background:var(--amber);color:var(--graphite);font-family:'IBM Plex Mono',monospace;font-weight:600;cursor:pointer;border:none;}
.skill-check{display:inline-block;margin:4px;padding:6px 12px;background:var(--steel);border-radius:20px;font-size:.85em;cursor:pointer;transition:all .2s;}
.skill-check:has(input:checked){background:var(--cyan);color:var(--graphite);font-weight:600;}
.skill-box{display:none;}
input[type=text],input[type=email]{background:var(--steel);border:1px solid var(--steel-line);border-radius:.5rem;padding:10px 15px;color:var(--manifest);width:100%;outline:none;}
</style></head><body>
<div class="panel p-8 max-w-lg w-full"><div class="text-center mb-8"><h1 class="font-mono-brand font-bold text-2xl mb-2">APPLYFLOW</h1><p class="tag">Set up your profile</p></div>
<form id="signup-form" class="space-y-4">
<div><label class="tag">Email</label><input type="email" id="email" required placeholder="you@example.com"></div>
<div><label class="tag">Name</label><input type="text" id="name" placeholder="Your name"></div>
<div><label class="tag">Select your skills</label><div class="mt-2">""" + skills_html + """</div></div>
<button type="submit" class="btn-primary w-full py-3 rounded text-sm">Create Account</button>
</form></div>
<script>
document.getElementById('signup-form').addEventListener('submit',function(e){e.preventDefault();
const email=document.getElementById('email').value;const name=document.getElementById('name').value;
const skills=Array.from(document.querySelectorAll('.skill-box:checked')).map(cb=>cb.value);
if(skills.length===0){alert('Select at least one skill');return;}
fetch('/api/signup',{method:'POST',body:JSON.stringify({email:email,name:name,skills:skills}),headers:{'Content-Type':'application/json'}})
.then(r=>r.json()).then(data=>{localStorage.setItem('va_email',email);window.location.href='/app';});
});
</script></body></html>"""
    
    def dashboard_page(self):
        return """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>ApplyFlow Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script><style>
:root{--graphite:#14171B;--graphite-panel:#1B1F25;--steel:#2A2F37;--steel-line:#363C46;--manifest:#EDEFF1;--manifest-dim:#9BA3AE;--amber:#F2A93B;--cyan:#4FD1C5;}
body{background:var(--graphite);color:var(--manifest);font-family:'IBM Plex Sans',sans-serif;}
.font-mono-brand{font-family:'IBM Plex Mono',monospace;}
.tag{font-family:'IBM Plex Mono',monospace;font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:var(--manifest-dim);}
.panel{background:var(--graphite-panel);border:1px solid var(--steel-line);border-radius:.5rem;}
.btn-primary{background:var(--amber);color:var(--graphite);font-family:'IBM Plex Mono',monospace;font-weight:600;}
.btn-ghost{border:1px solid var(--steel-line);color:var(--manifest);font-family:'IBM Plex Mono',monospace;}
.btn-apply{background:var(--cyan);color:var(--graphite);font-family:'IBM Plex Mono',monospace;font-weight:600;text-decoration:none;}
.score-high{background:rgba(79,209,197,.15);color:var(--cyan);}
.score-medium{background:rgba(242,169,59,.15);color:var(--amber);}
.score-low{background:rgba(226,87,76,.15);color:var(--red);}
.tab-btn{padding:8px 16px;border-radius:.5rem;font-family:'IBM Plex Mono',monospace;font-size:.8rem;cursor:pointer;transition:all .3s;}
.tab-active{background:var(--amber);color:var(--graphite);font-weight:600;}
.tab-inactive{background:transparent;border:1px solid var(--steel-line);color:var(--manifest-dim);}
.desc-hidden{display:none;}
.desc-shown{display:block;margin-top:10px;padding:12px;background:var(--steel);border-radius:.5rem;font-size:.85em;color:var(--manifest-dim);white-space:pre-wrap;line-height:1.5;max-height:300px;overflow-y:auto;}
</style></head><body>
<header class="sticky top-0 z-40 backdrop-blur bg-[var(--graphite)]/85 divider"><div class="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
<a href="/" class="font-mono-brand font-semibold">APPLYFLOW</a>
<div class="flex items-center gap-4"><span id="user-name" class="tag">Guest</span><a href="/signup" class="btn-primary text-xs px-4 py-2 rounded">Sign Up</a></div>
</div></header>
<main class="max-w-6xl mx-auto px-6 py-12">
<div class="flex gap-3 mb-8">
<button class="tab-btn tab-active" id="tab-jobs-btn" onclick="switchTab('jobs')">Jobs</button>
<button class="tab-btn tab-inactive" id="tab-apps-btn" onclick="switchTab('apps')">Applications</button>
</div>
<div id="login-prompt" class="panel p-8 text-center mb-8" style="display:none">
<h2 class="font-mono-brand font-semibold text-xl mb-3">Set up your profile</h2>
<p class="text-[var(--manifest-dim)] mb-6">Select your skills to get personalized job matches.</p>
<a href="/signup" class="btn-primary px-8 py-3 rounded text-sm inline-block">Set Up Profile</a>
</div>
<div id="stats" class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8" style="display:none">
<div class="panel p-5 text-center"><div class="font-mono-brand text-3xl text-[var(--cyan)]" id="stat-jobs">0</div><div class="tag mt-1">Jobs</div></div>
<div class="panel p-5 text-center"><div class="font-mono-brand text-3xl text-[var(--amber)]" id="stat-apps">0</div><div class="tag mt-1">Applications</div></div>
<div class="panel p-5 text-center"><div class="font-mono-brand text-3xl text-[var(--cyan)]" id="stat-users">0</div><div class="tag mt-1">Users</div></div>
<div class="panel p-5 text-center"><div class="font-mono-brand text-3xl text-[var(--amber)]" id="stat-tracked">0</div><div class="tag mt-1">Tracked</div></div>
</div>
<div id="tab-jobs-content"><div id="job-list" class="grid gap-4"></div></div>
<div id="tab-apps-content" style="display:none"><div id="app-list" class="grid gap-4"></div></div>
</main>
<script>
let currentEmail=localStorage.getItem('va_email')||'';
function switchTab(tab){
document.getElementById('tab-jobs-btn').className='tab-btn '+(tab==='jobs'?'tab-active':'tab-inactive');
document.getElementById('tab-apps-btn').className='tab-btn '+(tab==='apps'?'tab-active':'tab-inactive');
document.getElementById('tab-jobs-content').style.display=tab==='jobs'?'block':'none';
document.getElementById('tab-apps-content').style.display=tab==='apps'?'block':'none';
if(tab==='apps')loadApplications();}
function loadData(){
if(!currentEmail){document.getElementById('login-prompt').style.display='block';document.getElementById('stats').style.display='none';return;}
document.getElementById('login-prompt').style.display='none';document.getElementById('stats').style.display='grid';
document.getElementById('user-name').textContent=currentEmail.split('@')[0];
fetch('/api/jobs?email='+currentEmail).then(r=>r.json()).then(data=>{
if(!data.logged_in){document.getElementById('login-prompt').style.display='block';return;}
renderJobs(data.jobs);});
fetch('/api/stats').then(r=>r.json()).then(s=>{
document.getElementById('stat-jobs').textContent=s.total_jobs;
document.getElementById('stat-apps').textContent=s.applications;
document.getElementById('stat-users').textContent=s.users||0;
document.getElementById('stat-tracked').textContent=s.tracked;});}
function loadApplications(){
fetch('/api/applications').then(r=>r.json()).then(data=>{
const apps=data.applications;
if(!apps||apps.length===0){document.getElementById('app-list').innerHTML='<div class="panel p-8 text-center text-[var(--manifest-dim)] font-mono-brand text-sm">No applications generated.</div>';return;}
let html='';
apps.forEach(app=>{
const score=app.score||0;
const sc=score>=70?'score-high':score>=40?'score-medium':'score-low';
html+='<div class="panel p-5"><div class="flex justify-between items-start mb-3"><div><div class="font-mono-brand font-semibold">'+(app.job_title||app.title||'Application').substring(0,60)+'</div><div class="text-sm text-[var(--manifest-dim)]">'+(app.generated_by||'')+'</div></div><span class="tag '+sc+'" style="padding:2px 10px;border-radius:20px">'+score+'/100</span></div><div class="panel p-4 text-sm text-[var(--manifest-dim)]" style="white-space:pre-wrap">'+(app.text||'').substring(0,400)+'...</div></div>';});
document.getElementById('app-list').innerHTML=html;});}
function renderJobs(jobs){
if(!jobs||jobs.length===0){document.getElementById('job-list').innerHTML='<div class="panel p-8 text-center text-[var(--manifest-dim)] font-mono-brand text-sm">No jobs.</div>';return;}
let html='';
jobs.slice(0,30).forEach((job,index)=>{
const sc=job.user_score>=70?'score-high':job.user_score>=40?'score-medium':'score-low';
const skills=(job.user_matched_skills||[]).slice(0,4).map(s=>'<span class="tag" style="margin-right:4px">'+s+'</span>').join('');
const url=job.url||'';
const applyBtn=url?'<a href="'+url+'" target="_blank" class="btn-apply text-xs px-4 py-2 rounded">Apply Now</a>':'';
const desc=(job.description||'').replace(/'/g,"\\'").substring(0,2000);
html+='<div class="panel p-5"><div class="flex justify-between items-start mb-3"><div><div class="font-mono-brand font-semibold">'+job.title.substring(0,60)+'</div><div class="text-sm text-[var(--manifest-dim)]">'+(job.company||'')+' &bull; '+(job.platform||'')+'</div></div><span class="tag '+sc+'" style="padding:2px 10px;border-radius:20px">'+(job.user_score||0)+'/100</span></div><div class="mb-3">'+skills+'</div><div class="flex gap-2">'+applyBtn+'<button class="btn-ghost text-xs px-3 py-2 rounded" onclick="toggleDesc('+index+')">View Description</button></div><div id="desc-'+index+'" class="desc-hidden">'+desc+'</div></div>';});
document.getElementById('job-list').innerHTML=html;}
function toggleDesc(i){const el=document.getElementById('desc-'+i);el.className=el.className==='desc-hidden'?'desc-shown':'desc-hidden';}
loadData();
</script></body></html>"""

print("ApplyFlow running at http://localhost:8000 (Supabase backend)")
PORT = int(os.environ.get('PORT', 8000))
server = HTTPServer(('0.0.0.0', PORT), Handler)
print(f'Running on 0.0.0.0:{PORT}', flush=True)
