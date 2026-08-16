from pathlib import Path

code = Path('C:/va-pipeline/templates/landing.html').read_text(encoding='utf-8')

# Fix nav: replace /app with /login, add Dashboard link
old_nav = '<nav class="flex items-center gap-6 tag"><a href="/signup" class="hover:text-[var(--cyan)]">Sign Up</a><a href="/app" class="hover:text-[var(--cyan)]">Dashboard</a></nav>'
new_nav = '<nav class="flex items-center gap-6 tag"><a href="/login" class="hover:text-[var(--cyan)]">Login</a><a href="/signup" class="hover:text-[var(--cyan)]">Sign Up</a><a href="/dashboard" class="hover:text-[var(--cyan)]">Dashboard</a></nav>'

code = code.replace(old_nav, new_nav)

# Also fix hero buttons
old_hero = '<a href="/signup" class="btn-primary px-6 py-3 rounded text-sm">Set Up Profile</a><a href="/app" class="btn-ghost px-6 py-3 rounded text-sm">View Dashboard</a>'
new_hero = '<a href="/signup" class="btn-primary px-6 py-3 rounded text-sm">Get Started</a><a href="/login" class="btn-ghost px-6 py-3 rounded text-sm">Login</a>'

code = code.replace(old_hero, new_hero)

Path('C:/va-pipeline/templates/landing.html').write_text(code, encoding='utf-8')
print("Fixed landing page nav - added Login, fixed Dashboard link")
