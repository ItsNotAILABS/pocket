@echo off
setlocal EnableExtensions
title POCKET Production
set "ROOT=C:\Users\Medin\OneDrive\pocket-os"
set "PYTHONPATH=%ROOT%\src"
set "Path=C:\Users\Medin\.grok\bin;%Path%"
set "DESK=http://127.0.0.1:8787/desk"
set "POCKET_EDITION=founder"
set "POCKET_PUBLIC_URL=http://127.0.0.1:8787"
set "POCKET_MESH_HOOK_ASYNC=1"

echo.
echo  ============================================
echo   POCKET Production launch
echo   Desk  %DESK%
echo   Voice http://127.0.0.1:8790  (proxied via desk)
echo  ============================================
echo.

REM Host + Voice (Ensure starts both; never thrash healthy host)
powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%\scripts\Ensure-POCKET-Up.ps1"
if errorlevel 1 (
  echo [POCKET] Ensure reported issue — WMI start host...
  powershell -NoProfile -Command ^
    "$py='C:\Users\Medin\AppData\Local\Programs\Python\Python311-arm64\python.exe';" ^
    "$root='%ROOT%';" ^
    "$cmd=\"cmd.exe /c set PYTHONPATH=$root\src^& set POCKET_EDITION=founder^& set POCKET_PUBLIC_URL=http://127.0.0.1:8787^& set POCKET_MESH_HOOK_ASYNC=1^& cd /d $root^& `\"$py`\" -u -m pocket serve --host 0.0.0.0 --port 8787 >> %USERPROFILE%\.pocket\serve-out.log 2>> %USERPROFILE%\.pocket\serve-err.log\";" ^
    "Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine=$cmd;CurrentDirectory=$root}|Out-Null"
  timeout /t 5 /nobreak >nul
)

REM Wait for desk
powershell -NoProfile -Command "for($i=0;$i -lt 25;$i++){ try { $c=(curl.exe -s -m 2 -o NUL -w '%%{http_code}' http://127.0.0.1:8787/desk); if($c -eq '200'){ exit 0 } } catch {}; Start-Sleep -Milliseconds 400 }; exit 1"
if errorlevel 1 echo [POCKET] Desk slow — opening Edge anyway.

REM Ensure voice via host proxy (wakes :8790 if needed)
curl.exe -s -m 4 -X POST http://127.0.0.1:8787/v1/pocket-voice/ensure -H "Content-Type: application/json" -d "{}" >nul 2>&1
curl.exe -s -m 2 -o NUL -w "[POCKET] voice proxy %%{http_code}\n" http://127.0.0.1:8787/v1/pocket-voice/health

REM Edge app window
set "EDGE="
if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" set "EDGE=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" set "EDGE=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
if exist "%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe" set "EDGE=%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"

if "%EDGE%"=="" (
  start "" "%DESK%"
  exit /b 0
)

start "" "%EDGE%" --app=%DESK% --new-window --disable-features=msEdgeSidebar
echo [POCKET] Edge app launched.
exit /b 0
