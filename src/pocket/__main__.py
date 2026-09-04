import os

# Copilot stays closed unless the operator sets POCKET_COPILOT_AUTO=1.
os.environ.setdefault("POCKET_COPILOT_AUTO", "0")

from pocket.server import main

raise SystemExit(main() or 0)
