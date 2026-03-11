import re
import os
from pathlib import Path

file_path = "frontend/index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# 1. Extract CSS
css_match = re.search(r'<style>(.*?)</style>', html_content, re.DOTALL)
if css_match:
    css_content = css_match.group(1).strip()
    os.makedirs("frontend/css", exist_ok=True)
    with open("frontend/css/style.css", "w", encoding="utf-8") as f:
        f.write(css_content)

# 2. Extract JS
js_match = re.search(r'<script>(.*?)</script>', html_content, re.DOTALL)
if js_match:
    os.makedirs("frontend/js", exist_ok=True)
    js_content = js_match.group(1).strip()
    with open("frontend/js/app.js", "w", encoding="utf-8") as f:
        f.write(js_content)

# 3. Replace in HTML
new_html = re.sub(r'<style>.*?</style>', '<link rel="stylesheet" href="css/style.css">', html_content, flags=re.DOTALL)
new_html = re.sub(r'<script>.*?</script>', '<script src="js/app.js"></script>', new_html, flags=re.DOTALL)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_html)

print("Split complete. CSS logic moved to css/style.css, and JS logic moved to js/app.js.")
