# Ensure POCKET is up. Founder-first: local desk, load founder.env.
# Kills hung listeners that do not answer HTTP (common hang).
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
if (-not (Test-Path (Join-Path $Root "src\pocket"))) {
  $Root = "C:\Users\Medin\OneDrive\pocket-os"
}
$Src = Join-Path $Root "src"
$LogDir = Join-Path $env:USERPROFILE ".pocket"
$Log = Join-Path $LogDir "alwayson.log"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$py = "C:\Users\Medin\AppData\Local\Programs\Python\Python311-arm64\python.exe"
if (-not (Test-Path $py)) {
  $c = Get-Command python -ErrorAction SilentlyContinue
  if ($c) { $py = $c.Source } else { throw "Python not found" }
}

function Log([string]$m) {
  $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $m
  Add-Content -Path $Log -Value $line -ErrorAction SilentlyContinue
  Write-Host $line
}

function Load-EnvFile([string]$path) {
  if (-not (Test-Path $path)) { return }
  Get-Content $path | ForEach-Object {
    if ($_ -match '^\s*([A-Z0-9_]+)=(.*)$') {
      Set-Item -Path ("env:" + $matches[1]) -Value $matches[2].Trim().Trim('"')
    }
  }
}

function HealthOk {
  # Prefer /desk first (HTML shell proves the app works for Edge).
  # Then /health (must stay instant). Short timeouts so we never thrash a slow host.
  foreach ($url in @(
    "http://127.0.0.1:8787/desk",
    "http://127.0.0.1:8787/health",
    "http://127.0.0.1:8787/"
  )) {
    try {
      $r = Invoke-WebRequest $url -UseBasicParsing -TimeoutSec 2
      if ($r.StatusCode -eq 200) { return $true }
    } catch {}
  }
  return $false
}

function Wait-Health([int]$seconds = 12) {
  $deadline = (Get-Date).AddSeconds($seconds)
  while ((Get-Date) -lt $deadline) {
    if (HealthOk) { return $true }
    Start-Sleep -Milliseconds 500
  }
  return (HealthOk)
}

function PortListeners {
  return @(Get-NetTCPConnection -LocalPort 8787 -State Listen -ErrorAction SilentlyContinue)
}

function Kill-Port8787 {
  $cs = PortListeners
  foreach ($c in $cs) {
    if ($c.OwningProcess -and $c.OwningProcess -gt 0) {
      Log "Killing hung host PID $($c.OwningProcess)"
      Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
    }
  }
  Start-Sleep -Seconds 2
}

function StartPocket {
  Log "Starting POCKET host (founder tree)"
  $env:PYTHONPATH = $Src
  $env:Path = "C:\Users\Medin\.grok\bin;" + $env:Path
  # Founder defaults first, then access.env (may override password vars only if set)
  Load-EnvFile (Join-Path $LogDir "founder.env")
  Load-EnvFile (Join-Path $LogDir "access.env")
  # Never leave public marketing URL as the only app URL for founder unless they chose it
  if (-not $env:POCKET_EDITION) { $env:POCKET_EDITION = "founder" }
  if (-not $env:POCKET_PUBLIC_URL -or $env:POCKET_PUBLIC_URL -match 'medinatechlabs') {
    if ($env:POCKET_EDITION -eq "founder" -and -not ($env:POCKET_FORCE_PUBLIC_URL -eq "1")) {
      $env:POCKET_PUBLIC_URL = "http://127.0.0.1:8787"
    }
  }
  $out = Join-Path $LogDir "pocket-serve.log"
  $err = Join-Path $LogDir "pocket-serve-err.log"
  # WMI Create escapes agent Job Objects (Start-Process children die when shell ends)
  $edition = $env:POCKET_EDITION
  $pub = $env:POCKET_PUBLIC_URL
  $inner = "set PYTHONPATH=$Src& set POCKET_EDITION=$edition& set POCKET_PUBLIC_URL=$pub& set POCKET_MESH_HOOK_ASYNC=1& cd /d $Root& `"$py`" -u -m pocket serve --host 0.0.0.0 --port 8787 >> `"$out`" 2>> `"$err`""
  $cmd = "cmd.exe /c $inner"
  try {
    $r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
      CommandLine = $cmd
      CurrentDirectory = $Root
    }
    Log ("Started via WMI pid=" + $r.ProcessId + " return=" + $r.ReturnValue)
  } catch {
    Log ("WMI start failed: " + $_.Exception.Message + " - Start-Process fallback")
    Start-Process -FilePath $py -ArgumentList "-u","-m","pocket","serve","--host","0.0.0.0","--port","8787" `
      -WorkingDirectory $Root -WindowStyle Hidden -RedirectStandardOutput $out -RedirectStandardError $err | Out-Null
  }
}

function VoiceHealthOk {
  try {
    $r = Invoke-WebRequest "http://127.0.0.1:8790/health" -UseBasicParsing -TimeoutSec 2
    if ($r.StatusCode -eq 200) { return $true }
  } catch {}
  return $false
}

function StartPocketVoice {
  # Pocket Voice API (patient VAD) for desk mic hybrid decide
  $voiceRoot = "C:\Users\Medin\OneDrive\pocket-voice-to-text"
  if (-not (Test-Path (Join-Path $voiceRoot "server\api.js"))) {
    $alt = Join-Path (Split-Path $Root -Parent) "pocket-voice-to-text"
    if (Test-Path (Join-Path $alt "server\api.js")) { $voiceRoot = $alt }
  }
  if (-not (Test-Path (Join-Path $voiceRoot "server\api.js"))) {
    Log "Pocket Voice not found - desk mic uses local 1400ms only"
    return
  }
  if (VoiceHealthOk) {
    Log "Pocket Voice already up - http://127.0.0.1:8790"
    return
  }
  $nodePath = $null
  $ncmd = Get-Command node -ErrorAction SilentlyContinue
  if ($ncmd -and $ncmd.Source) { $nodePath = $ncmd.Source }
  if (-not $nodePath) {
    $candidates = @()
    if ($env:ProgramFiles) { $candidates += (Join-Path $env:ProgramFiles "nodejs\node.exe") }
    $pf86 = ${env:ProgramFiles(x86)}
    if ($pf86) { $candidates += (Join-Path $pf86 "nodejs\node.exe") }
    if ($env:LOCALAPPDATA) { $candidates += (Join-Path $env:LOCALAPPDATA "Programs\nodejs\node.exe") }
    foreach ($c in $candidates) {
      if ($c -and (Test-Path $c)) { $nodePath = $c; break }
    }
  }
  # where.exe fallback
  if (-not $nodePath) {
    try {
      $w = & where.exe node 2>$null | Select-Object -First 1
      if ($w -and (Test-Path $w)) { $nodePath = $w }
    } catch {}
  }
  if (-not $nodePath -or -not (Test-Path $nodePath)) {
    Log "node not found - skip Pocket Voice (desk mic still works with local 1400ms)"
    return
  }
  $vOut = Join-Path $LogDir "pocket-voice.log"
  $vErr = Join-Path $LogDir "pocket-voice-err.log"
  Log "Starting Pocket Voice API on :8790 via $nodePath"
  Start-Process -FilePath $nodePath -ArgumentList "server\api.js" `
    -WorkingDirectory $voiceRoot -WindowStyle Hidden `
    -RedirectStandardOutput $vOut -RedirectStandardError $vErr | Out-Null
  Start-Sleep -Seconds 1
  if (VoiceHealthOk) { Log "Pocket Voice started OK" } else { Log "Pocket Voice start may have failed - see $vErr" }
}

# Bootstrap founder.env file if missing
$founderEnv = Join-Path $LogDir "founder.env"
if (-not (Test-Path $founderEnv)) {
  @"
POCKET_EDITION=founder
POCKET_PUBLIC_URL=http://127.0.0.1:8787
POCKET_MARKETING_URL=https://pocket.medinatechlabs.net
POCKET_HIDE_PUBLIC_GITHUB=1
POCKET_PUBLIC_LOCK=1
"@ | Set-Content $founderEnv -Encoding UTF8
  Log "Wrote default founder.env"
}

# Always try voice (fast no-op if already up)
StartPocketVoice

function Prune-ExtraServe {
  $keep = @{}
  foreach ($c in (PortListeners)) {
    if ($c.OwningProcess) { $keep[[int]$c.OwningProcess] = $true }
  }
  Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -and $_.CommandLine -match '-m pocket serve'
  } | ForEach-Object {
    $procId = [int]$_.ProcessId
    if ($keep.Count -gt 0 -and -not $keep.ContainsKey($procId)) {
      Log "Killing extra pocket serve PID $procId (not the :8787 listener)"
      Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    }
  }
}

if (HealthOk) {
  Prune-ExtraServe
  Log "POCKET already up - http://127.0.0.1:8787/desk"
  if (VoiceHealthOk) { Log "Pocket Voice OK - http://127.0.0.1:8790" }
  exit 0
}

# Listen but no HTTP = classic hung host — kill before start
if ((PortListeners).Count -gt 0) {
  Log "Port 8787 listening but HTTP not OK - restarting hung host"
  Kill-Port8787
}

StartPocket
if (Wait-Health 12) {
  Prune-ExtraServe
  Log "POCKET is UP http://127.0.0.1:8787/desk (edition=$($env:POCKET_EDITION))"
  if (VoiceHealthOk) { Log "Pocket Voice OK - http://127.0.0.1:8790" }
  exit 0
}
# one more kill+retry (never leave a zombie listener)
Log "First start failed health - retry once"
Kill-Port8787
Start-Sleep -Seconds 1
StartPocket
if (Wait-Health 14) {
  Prune-ExtraServe
  Log "POCKET is UP after retry"
  if (VoiceHealthOk) { Log "Pocket Voice OK - http://127.0.0.1:8790" }
  exit 0
}
# Final cleanup so we never leave a hung listener claiming :8787
if ((PortListeners).Count -gt 0 -and -not (HealthOk)) {
  Log "Cleaning hung listener after failed start"
  Kill-Port8787
}
Log "POCKET FAILED to start - see $LogDir\pocket-serve-err.log"
exit 1
