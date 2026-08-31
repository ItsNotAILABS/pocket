# POCKET for Users — separate product on :8788. Never the Owner desk.
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $Root "src\pocket"))) {
  $Root = "C:\Users\Medin\OneDrive\pocket-os"
}
$Src = Join-Path $Root "src"
$LogDir = Join-Path $env:USERPROFILE ".pocket"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Port = 8788

function Up {
  try {
    $r = Invoke-WebRequest "http://127.0.0.1:$Port/health" -UseBasicParsing -TimeoutSec 2
    return $r.StatusCode -eq 200
  } catch { return $false }
}

if (Up) {
  Write-Host "POCKET for Users already on :$Port"
  exit 0
}

$py = "$env:LOCALAPPDATA\Programs\Python\Python311-arm64\python.exe"
if (-not (Test-Path $py)) { $py = "python.exe" }
$out = Join-Path $LogDir "pocket-users-serve.log"
$err = Join-Path $LogDir "pocket-users-serve-err.log"
Write-Host "Starting POCKET for Users on :$Port (not Owner :8787)"
# WMI Create so the host survives the launcher Job Object (Start-Process children die with the shell).
$inner = "set PYTHONPATH=$Src& set POCKET_PORT=$Port& set POCKET_PRODUCT=users& set POCKET_EDITION=public& set POCKET_PUBLIC_URL=http://127.0.0.1:$Port& set POCKET_MESH_HOOK=0& set POCKET_AURO_TRAIN=0& cd /d $Root& `"$py`" -u -m pocket serve --host 127.0.0.1 --port $Port >> `"$out`" 2>> `"$err`""
try {
  $r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
    CommandLine = "cmd.exe /c $inner"
    CurrentDirectory = $Root
  }
  Write-Host ("Users WMI pid=" + $r.ProcessId + " return=" + $r.ReturnValue)
} catch {
  Write-Host ("WMI start failed: " + $_.Exception.Message + " - Start-Process fallback")
  $env:PYTHONPATH = $Src
  $env:POCKET_PORT = "$Port"
  $env:POCKET_PRODUCT = "users"
  $env:POCKET_EDITION = "public"
  $env:POCKET_PUBLIC_URL = "http://127.0.0.1:$Port"
  $env:POCKET_MESH_HOOK = "0"
  $env:POCKET_AURO_TRAIN = "0"
  Start-Process -FilePath $py -ArgumentList "-u","-m","pocket","serve","--host","127.0.0.1","--port","$Port" `
    -WorkingDirectory $Root -WindowStyle Hidden -RedirectStandardOutput $out -RedirectStandardError $err | Out-Null
}

1..60 | ForEach-Object { if (Up) { Write-Host "POCKET for Users ready http://127.0.0.1:$Port/"; exit 0 }; Start-Sleep -Milliseconds 500 }
if (Up) { Write-Host "POCKET for Users ready http://127.0.0.1:$Port/"; exit 0 }
Write-Host "Users host did not answer :$Port yet. Check $err"
exit 1
