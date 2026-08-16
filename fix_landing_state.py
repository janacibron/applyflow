from pathlib import Path

code = Path('C:/va-pipeline/templates/landing.html').read_text(encoding='utf-8')

# Add JS before closing body
old = "</body>"
new = """<script>
const token = localStorage.getItem('va_token') || document.cookie.split('; ').find(r=>r.startsWith('va_token='))?.split('=')[1];
if (token) {
    const email = localStorage.getItem('va_email') || '';
    const navLinks = document.querySelectorAll('nav a');
    navLinks.forEach(a => {
        if (a.textContent === 'Login' || a.textContent === 'Sign Up') {
            a.style.display = 'none';
        }
    });
    const logout = document.createElement('a');
    logout.href = '/logout';
    logout.textContent = 'Sign Out';
    logout.className = 'hover:text-[var(--cyan)]';
    document.querySelector('nav').appendChild(logout);
}
</script>
</body>"""

code = code.replace(old, new, 1)
Path('C:/va-pipeline/templates/landing.html').write_text(code, encoding='utf-8')
print("Fixed landing page")
