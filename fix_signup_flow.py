from pathlib import Path

code = Path('C:/va-pipeline/templates/signup.html').read_text(encoding='utf-8')

old = """if(data && data.error){alert(data.error);return;}
        localStorage.setItem('va_token', data.token || '');
        window.location.href='/dashboard';"""

new = """if(data && data.error){alert(data.error);return;}
        if(!data){alert('Signup failed. Try again.');return;}
        localStorage.setItem('va_email', email);
        alert('Account created! Please login.');
        window.location.href='/login';"""

code = code.replace(old, new)

Path('C:/va-pipeline/templates/signup.html').write_text(code, encoding='utf-8')
print("Fixed: Signup now redirects to login instead of expecting token")
