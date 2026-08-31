import re, tempfile, subprocess, os, sys
sys.path.insert(0, r"C:\Users\Medin\OneDrive\pocket-os\src")
from pocket.app_ui import HTML
scripts = re.findall(r"<script[^>]*>([\s\S]*?)</script>", HTML)
js = max(scripts, key=len) if scripts else ""
path = os.path.join(tempfile.gettempdir(), "pocket-desk-check.js")
open(path, "w", encoding="utf-8").write(js)
r = subprocess.run(["node", "--check", path], capture_output=True, text=True)
print("node", r.returncode)
print((r.stderr or "OK")[:2500])
print("js_len", len(js))
for i, line in enumerate(js.splitlines(), 1):
    if "vmemOpen" in line or "hit(s)" in line:
        print(i, line[:180])
