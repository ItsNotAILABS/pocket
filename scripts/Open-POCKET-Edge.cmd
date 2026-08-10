@echo off
setlocal EnableExtensions
title POCKET Edge App
set "ROOT=C:\Users\Medin\OneDrive\pocket-os"
set "PYTHONPATH=%ROOT%\src"
set "Path=C:\Users\Medin\.grok\bin;%Path%"
set "DESK=http://127.0.0.1:8787/desk"

REM 1) Bring host + voice up (production path)
powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%\scripts\Ensure-POCKET-Up.ps1"
if errorlevel 1 (
  echo [POCKET] Ensure-POCKET-Up reported an issue — trying direct start...
  start "" /MIN "C:\Users\Medin\AppData\Local\Programs\Python\Python311-arm64\python.exe" -m pocket serve --host 0.0.0.0 --port 8787
  timeout /t 4 /nobreak >nul
)

REM 2) Wait briefly for desk HTTP
powershell -NoProfile -Command "for($i=0;$i -lt 20;$i++){ try { $c=(curl.exe -s -m 2 -o NUL -w '%%{http_code}' http://127.0.0.1:8787/desk 2>$null); if($c -eq '200'){ exit 0 } } catch {} ; Start-Sleep -Milliseconds 400 }; exit 1"
if errorlevel 1 (
  echo [POCKET] Desk not answering on :8787 — open browser anyway.
)

REM 2b) Wake voice via same-origin proxy (mic / Aria)
curl.exe -s -m 3 -X POST http://127.0.0.1:8787/v1/pocket-voice/ensure -H "Content-Type: application/json" -d "{}" >nul 2>&1

REM 3) Find Edge (x86, x64, user install)
set "EDGE="
if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" set "EDGE=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" set "EDGE=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
if exist "%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe" set "EDGE=%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"

if "%EDGE%"=="" (
  echo [POCKET] msedge.exe not found — opening default browser.
  start "" "%DESK%"
  exit /b 0
)

REM 4) Edge app window (installed-app feel). Fallback: normal tab if app mode fails.
REM    Sovereign: local host only; desk is the product surface.
start "" "%EDGE%" --app=%DESK% --new-window --disable-features=msEdgeSidebar
if errorlevel 1 (
  start "" "%EDGE%" --new-window %DESK%
)

REM 5) Optional: warm docs/mail endpoints (no extra windows)
curl.exe -s -m 2 http://127.0.0.1:8787/v1/catalog >nul 2>&1
curl.exe -s -m 2 http://127.0.0.1:8787/v1/agent-mail >nul 2>&1
exit /b 0
