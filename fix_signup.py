from pathlib import Path

code = Path('C:/va-pipeline/templates/signup.html').read_text(encoding='utf-8')

old = "if(data && data.error){alert(data.error);return;}"
new = "if(!data){alert('Signup failed. Try again.');return;}\n        if(data && data.error){alert(data.error);return;}"

code = code.replace(old, new)

Path('C:/va-pipeline/templates/signup.html').write_text(code, encoding='utf-8')
print("Fixed signup.html null check")
