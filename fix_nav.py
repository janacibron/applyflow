from pathlib import Path

code = Path('C:/va-pipeline/templates/dashboard.html').read_text(encoding='utf-8')

# Find the nav section
old_nav = '<span id="user-name" class="tag">Guest</span><a href="/signup" class="btn-primary text-xs px-4 py-2 rounded">Sign Up</a>'
new_nav = '<span id="user-name" class="tag">Guest</span><a href="/signup" class="btn-primary text-xs px-4 py-2 rounded" id="signup-btn">Sign Up</a><a href="/logout" class="btn-ghost text-xs px-4 py-2 rounded" id="logout-btn" style="display:none">Sign Out</a>'

code = code.replace(old_nav, new_nav)

# Add JS to toggle signup/logout based on login state
old_js = "if(currentToken){document.getElementById('user-name').textContent=localStorage.getItem('va_email')||'User';}"
new_js = """if(currentToken){
    document.getElementById('user-name').textContent=localStorage.getItem('va_email')||'User';
    document.getElementById('signup-btn').style.display='none';
    document.getElementById('logout-btn').style.display='inline';
}
function logout(){
    localStorage.removeItem('va_token');
    localStorage.removeItem('va_email');
    document.cookie = 'va_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    window.location.href='/login';
}"""

code = code.replace(old_js, new_js)

# Add logout click handler
old_load = "loadData();"
new_load = "document.getElementById('logout-btn').addEventListener('click', logout);\nloadData();"
code = code.replace(old_load, new_load, 1)

Path('C:/va-pipeline/templates/dashboard.html').write_text(code, encoding='utf-8')
print("Fixed dashboard nav - Sign Out when logged in")
