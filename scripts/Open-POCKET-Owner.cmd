@echo off
REM POCKET Owner — your machine on :8787
set "POCKET_CLIENT_ROLE=operator"
set "POCKET_PRODUCT=owner"
set "POCKET_EDITION=founder"
set "POCKET_PORT=8787"
set "POCKET_PUBLIC_URL=http://127.0.0.1:8787"
call "%~dp0Open-POCKET-Electron.cmd" --local
