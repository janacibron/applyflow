from pathlib import Path

code = Path('C:/va-pipeline/applyflow.py').read_text(encoding='utf-8')

# Fix the root route: if logged in, redirect to dashboard instead of landing
old = """        if path in ['/', '/index.html']:
            self.serve_html(self.landing_page())"""

new = """        if path in ['/', '/index.html']:
            if self._current_token():
                self.send_response(302)
                self.send_header('Location', '/dashboard')
                self.end_headers()
                return
            self.serve_html(self.landing_page())"""

code = code.replace(old, new)

Path('C:/va-pipeline/applyflow.py').write_text(code, encoding='utf-8')
print("Fixed: logged-in users skip landing page, go to dashboard")
