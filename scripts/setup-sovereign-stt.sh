#!/usr/bin/env bash
# setup-sovereign-stt.sh — make POCKET speech-to-text sovereign (local, private).
#
# Installs faster-whisper and pre-downloads the Whisper model so the POCKET
# host transcribes audio ON THIS MACHINE instead of sending it to a cloud
# speech API (e.g. the browser vendor's Web Speech service).
#
# Usage:
#   scripts/setup-sovereign-stt.sh
#   POCKET_STT_MODEL=small scripts/setup-sovereign-stt.sh
#
# Env:
#   POCKET_STT_MODEL   tiny|base|small|medium|large-v3  (default: base)
#   PIP                pip executable override (default: python3 -m pip)
set -euo pipefail

MODEL="${POCKET_STT_MODEL:-base}"
PY="${PYTHON:-python3}"

echo "==> Sovereign STT setup (model: $MODEL)"
echo "    Target: local faster-whisper transcription on this host."
echo "    No audio will leave this machine for speech recognition."

if ! command -v "$PY" >/dev/null 2>&1; then
  echo "ERROR: $PY not found. Install Python 3.9+ first." >&2
  exit 1
fi

PIP_BIN="${PIP:-$PY -m pip}"
echo "==> Installing faster-whisper ..."
# shellcheck disable=SC2086
if ! $PIP_BIN install --quiet faster-whisper 2>/tmp/stt-pip.log; then
  echo "    plain pip failed, retrying with --user ..." >&2
  # shellcheck disable=SC2086
  $PIP_BIN install --quiet --user faster-whisper || {
    echo "ERROR: pip install failed. See /tmp/stt-pip.log" >&2
    exit 1
  }
fi

echo "==> Pre-downloading Whisper model '$MODEL' ..."
POCKET_STT_MODEL="$MODEL" "$PY" - "$MODEL" <<'EOF'
import sys
# Import from the repo's src layout when run from the repo root.
sys.path.insert(0, "src")
try:
    from pocket.stt_engine import ensure_model, model_name
except ImportError:
    # Fall back to a direct faster-whisper download (no repo import).
    from faster_whisper import WhisperModel
    WhisperModel(sys.argv[1], device="auto", compute_type="int8")
    print("model downloaded via faster-whisper directly")
    sys.exit(0)
r = ensure_model()
print(r)
if not r.get("ok"):
    sys.exit(1)
EOF

echo ""
echo "==> Done. Sovereign STT is ready."
echo "    POCKET host: POST /v1/voice/stt  (engine=local_whisper, the default)"
echo "    Pocket Voice: POST :8790/v1/stt/transcribe"
echo "    To verify:  $PY src/pocket/stt_engine.py   (prints engine list)"
echo "    Opt out (browser cloud STT):  POCKET_STT_ENGINE=webspeech"
