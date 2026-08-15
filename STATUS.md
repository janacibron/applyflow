# ApplyFlow — Status & Roadmap

## Last Updated: 2026-08-16

---

## 🚀 LIVE

**URL:** https://applyflow-xbi7.onrender.com
**GitHub:** https://github.com/janacibron/applyflow  
**Supabase:** xmpakpmhzioxwaiwijnn.supabase.co  
**Local:** http://localhost:8000

---

## Directory Structure
C:\va-pipeline
├── applyflow.py Dashboard + API server
├── app.py Render deployment entry point
├── requirements.txt Dependencies (pinned)
├── Procfile Start command
├── runtime.txt Python version
├── .python-version Render Python version
├── supabase_config.py Supabase config (env vars)
├── supabase_config_local.py Local keys backup
├── olj_scraper_v7.py OLJ scraper (cookie auth)
├── ollama_classify.py Ollama classifier
├── ollama_generate5.py App generator (top 5)
├── clean_titles.py LLM title cleaner
├── fix_descriptions.py Full description fetcher
├── governance.py Append-only event log
├── dedupe.py Duplicate detection / idempotency
├── pipeline_runner.py End-to-end pipeline orchestrator
├── scheduler.py Background auto-scrape scheduler
├── sync_supabase.py Supabase sync
├── STATUS.md This file
├── cookies
│ └── olj_cookies.txt OLJ session
└── data
├── jobs.json 150 jobs (local backup)
├── applications.json 30 applications (local backup)
├── ledger.json 2 entries (local backup)
├── users.json 2 users (local backup)
├── premium.json Premium users
└── migration_map.json Supabase ID mappings

text

---

## Deployment Stack

| Layer | Technology | Status |
|-------|-----------|--------|
| Frontend | HTML + Tailwind + JS | ✅ Live |
| Backend | Python HTTPServer | ✅ Live |
| Database | Supabase (Postgres) | ✅ 150 jobs |
| AI | Ollama (local) | ✅ Scoring + Generation |
| Hosting | Render (free tier) | ✅ Live |
| Code | GitHub | ✅ janacibron/applyflow |

---

## Supabase Schema

| Table | Rows | Purpose |
|-------|------|---------|
| users | 2 | Email, name, skills[], is_premium |
| jobs | 150 | Title, company, description, score |
| applications | 29 | Generated applications |
| ledger | 1 | Tracking entries |

---

## Phase 1 — Core Pipeline ✅ COMPLETE

- [x] OLJ scraper with cookie auth (150 jobs)
- [x] Full descriptions (3000 chars)
- [x] LLM title cleaning (126 titles)
- [x] Ollama classification (153 scored)
- [x] Personalized scoring per user
- [x] Application generation (30 apps)
- [x] Supabase migration
- [x] Dashboard with login gate
- [x] Signup with skills (16 options)
- [x] Applications tab
- [x] Apply Now buttons
- [x] View Description expand
- [x] Deploy to Render
- [x] Public URL live

## Phase 2 — Automation (Next)

- [ ] Scheduler (auto-scrape every 30 min)
- [ ] Telegram notifications for high-score jobs
- [ ] Auto follow-ups (Day 3, Day 7)
- [ ] Response analytics
- [ ] Duplicate detection
- [ ] Governance logging
- [ ] RemoteOK parser (~25 more jobs)
- [ ] Working Nomads parser (~25 more jobs)

## Phase 3 — Beta Testing

- [ ] Share URL with 5 beta testers
- [ ] Collect feedback
- [ ] Fix bugs
- [ ] Optimize cold start
- [ ] Payment integration (Stripe)

## Phase 4 — Growth

- [ ] 20+ beta testers
- [ ] Premium subscriptions (/mo)
- [ ] Agency partnerships
- [ ] Blog content from job data
- [ ] Learning loop

## Phase 5 — Flywheel

- [ ] 50+ users
- [ ] AI recommends Pruweba from content
- [ ] Pruweba clients from proof
- [ ] Referral loop: VAs → businesses

---

## User Flow (Live)
Visit applyflow-xbi7.onrender.com → Click Sign Up
→ Enter email + name → Select skills (16 options)
→ Account created in Supabase
→ Dashboard scores 150 jobs against user skills
→ Top matches shown (up to 80/100)
→ Apply Now → opens OLJ posting
→ View Description → expands full text
→ Applications tab → shows 29 generated apps

text

---

## Commands

`powershell
# Local dashboard
python C:\va-pipeline\applyflow.py

# Deploy to Render (auto-deploys on push)
cd C:\va-pipeline; git add .; git commit -m "Update"; git push

# Scrape new jobs
python C:\va-pipeline\olj_scraper_v7.py

# Classify with Ollama
python C:\va-pipeline\ollama_classify.py

# Generate top 5 apps
python C:\va-pipeline\ollama_generate5.py
Next Actions (Priority)
Test live URL with real user

Build scheduler (auto-scrape)

Telegram notifications

Parse RemoteOK + Working Nomads

Fix cold start (upgrade to Starter /mo when ready)
