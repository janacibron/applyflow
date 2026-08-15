# ApplyFlow — Status & Roadmap

## Last Updated: 2026-08-16

---

## Directory Structure
C:\va-pipeline
├── applyflow.py 18.9 KB Dashboard + API server (port 8000)
├── clean_titles.py 1.4 KB LLM title cleaner (llama3.2)
├── fix_descriptions.py 3.3 KB Full description fetcher
├── olj_scraper_v7.py 6.3 KB OLJ scraper (cookie auth)
├── ollama_classify.py 1.8 KB Ollama classifier (llama3.2)
├── ollama_generate5.py 2.7 KB App generator top 5 (mistral:7b)
├── STATUS.md 3.2 KB This file
├── cookies
│ └── olj_cookies.txt 516 B OLJ session (persistent)
└── data
├── jobs.json 548.9 KB 153 jobs (full desc + scores)
├── applications.json 37.6 KB 30 applications (5 Ollama)
├── ledger.json 343 B Tracking entries
├── premium.json 19 B Premium users list
└── users.json 269 B Signups with skills

text

---

## Pipeline Components

| Component | Status | Details |
|-----------|--------|---------|
| OLJ Scraper | ✅ Working | 150 jobs, cookie auth, full descriptions |
| Remotive RSS | ✅ Working | 17 jobs (not in current DB) |
| RemoteOK | ⚠️ Accessible | HTML loads, not parsed |
| Working Nomads | ⚠️ Accessible | JSON API works, not parsed |
| We Work Remotely | ❌ 301 | Needs redirect fix |
| Ollama Classification | ✅ Complete | 153/153 scored (22-94 range) |
| Personalized Scoring | ✅ Working | Per-user skills matching |
| Application Generation | ✅ Working | 30 apps (5 mistral:7b quality) |
| Title Cleaning | ✅ Complete | 126 titles cleaned by LLM |
| Dashboard | ✅ Running | ApplyFlow at localhost:8000 |
| Signup with Skills | ✅ Working | 16 skill options |
| Login Gate | ✅ Working | No login = no scoring |
| Premium Gating | ✅ API Ready | Signup/Upgrade flow |

---

## Data Stats

- Total jobs: 153
- Full descriptions: 149/153 (3000 chars)
- Clean titles: 127/153
- Ollama scores: 153/153
- Applications: 30 total (5 Ollama-generated)
- Users: 1 test
- Skills options: 16

---

## Ollama Models Used

| Model | Size | Used For |
|-------|------|----------|
| mistral:7b | 4.4 GB | Application generation |
| llama3.2:3b | 2.0 GB | Classification + title cleaning |
| deepseek-r1:1.5b | 1.1 GB | Fallback (unused) |

---

## Pipeline Flow
Scrape OLJ (150 jobs) → olj_scraper_v7.py

Fetch full descriptions → fix_descriptions.py

Clean titles with LLM → clean_titles.py

Classify with Ollama → ollama_classify.py

Generate apps for top 5 → ollama_generate5.py

Serve dashboard + API → applyflow.py

Personalized scoring per user → applyflow.py (built-in)

text

---

## User Flow
Visit /signup → Enter email + name → Select skills (16 options)
→ Account created → Redirect to /app
→ Dashboard scores 153 jobs against user's skills
→ Top matches shown with scores
→ Generate applications (premium)
→ Track responses (ledger)

text

---

## Phase 1 — Core Pipeline (90% Complete)

- [x] OLJ scraper with cookie auth
- [x] Full descriptions (149/153)
- [x] LLM title cleaning (126)
- [x] Ollama classification (153)
- [x] Personalized scoring
- [x] Application generation (30)
- [x] Dashboard with login gate
- [x] Signup with skills
- [ ] RemoteOK parser
- [ ] Working Nomads parser
- [ ] Applications tab in dashboard
- [ ] We Work Remotely fix

## Phase 2 — Automation (Not Started)

- [ ] Scheduler (30 min auto-run)
- [ ] Telegram notifications
- [ ] Auto follow-ups (Day 3, 7)
- [ ] Response analytics
- [ ] Duplicate detection
- [ ] Governance logging

## Phase 3 — Deployment (Not Started)

- [ ] Deploy to server (Railway/Render)
- [ ] 5 beta testers
- [ ] Payment integration
- [ ] Email digest

## Phase 4 — Growth (Not Started)

- [ ] 20+ beta testers
- [ ] Agency partnerships
- [ ] Blog content from job data
- [ ] Learning loop

## Phase 5 — Flywheel (Not Started)

- [ ] 50+ users
- [ ] Premium revenue (/mo)
- [ ] Pruweba clients from proof
- [ ] Referral loop

---

## Next Actions (Priority)

1. Parse RemoteOK + Working Nomads (~50 more jobs)
2. Add applications tab to dashboard
3. Build scheduler (auto-run every 30 min)
4. Telegram notifications for high-score jobs
5. Deploy for beta testers

---

## Commands

`powershell
# Start dashboard
python C:\va-pipeline\applyflow.py

# Scrape OLJ jobs
python C:\va-pipeline\olj_scraper_v7.py

# Classify with Ollama
python C:\va-pipeline\ollama_classify.py

# Generate top 5 applications
python C:\va-pipeline\ollama_generate5.py

# Clean titles
python C:\va-pipeline\clean_titles.py
