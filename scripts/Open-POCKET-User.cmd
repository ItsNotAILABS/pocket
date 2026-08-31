@echo off
REM POCKET for Users — separate product on :8788
set "POCKET_CLIENT_ROLE=user"
set "POCKET_PRODUCT=users"
set "POCKET_EDITION=public"
set "POCKET_PORT=8788"
set "POCKET_PUBLIC_URL=http://127.0.0.1:8788"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-POCKET-Users.ps1"
call "%~dp0Open-POCKET-Electron.cmd"
