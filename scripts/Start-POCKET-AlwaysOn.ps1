# POCKET Always-On — keeps http://127.0.0.1:8787 up (required for Cloudflare)
$ErrorActionPreference = "Continue"
$Root = "C:\Users\Medin\OneDrive\pocket-os"
$Src = Join-Path $Root "src"
$LogDir = Join-Path $env:USERPROFILE ".pocket"
$Log = Join-Path $LogDir "alwayson.log"
$RunBat = Join-Path $LogDir "run-pocket.cmd"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$py = "C:\Users\Medin\AppData\Local\Programs\Python\Python311-arm64\python.exe"
if (-not (Test-Path $py)) {
  $c = Get-Command python -ErrorAction SilentlyContinue
  if ($c) { $py = $c.Source } else { $py = "python" }
}

function Log([string]$m) {
  $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $m
  Add-Content -Path $Log -Value $line -ErrorAction SilentlyContinue
  Write-Host $line
}

function HealthOk {
  # Prefer /desk and /health with short timeout. Never use a slow path that
  # false-fails under Edge load and thrash-kills a healthy host.
  foreach ($url in @(
    "http://127.0.0.1:8787/desk",
    "http://127.0.0.1:8787/health"
  )) {
    try {
      $code = & curl.exe -s -m 2 -o NUL -w "%{http_code}" $url 2>$null
      if ($code -eq "200") { return $true }
    } catch {}
  }
  return $false
}

function FailStreak([int]$need = 3) {
  for ($i = 0; $i -lt $need; $i++) {
    if (HealthOk) { return $false }
    Start-Sleep -Seconds 2
  }
  return $true
}

function KillPort8787 {
  # ONLY used when we are sure the listener is dead/zombie — prefer not to kill
  Log "WARNING: freeing port 8787 (zombie recovery only)"
  Get-NetTCPConnection -LocalPort 8787 -State Listen -ErrorAction SilentlyContinue |
    ForEach-Object {
      try { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue } catch {}
    }
  Start-Sleep -Seconds 1
}

function Read-AccessEnv {
  $user = "pocket"
  $pass = ""
  $f = Join-Path $LogDir "access.env"
  if (-not (Test-Path $f)) { $f = Join-Path $Root ".pocket\access.env" }
  if (Test-Path $f) {
    Get-Content $f | ForEach-Object {
      if ($_ -match "^\s*POCKET_BASIC_AUTH_USER=(.+)$") { $user = $Matches[1].Trim() }
      if ($_ -match "^\s*POCKET_BASIC_AUTH_PASSWORD=(.+)$") { $pass = $Matches[1].Trim() }
    }
  }
  if (-not $pass -and (Test-Path (Join-Path $LogDir "ACCESS.txt"))) {
    $t = Get-Content (Join-Path $LogDir "ACCESS.txt") -Raw
    if ($t -match "Password:\s*(\S+)") { $pass = $Matches[1] }
  }
  return @{ User = $user; Pass = $pass }
}

function StartPocket {
  $cred = Read-AccessEnv
  Log ("Starting POCKET py=$py user=$($cred.User)")
  $lines = @(
    "@echo off",
    "cd /d `"$Root`"",
    "set PYTHONPATH=$Src",
    "set Path=C:\Users\Medin\.grok\bin;%Path%",
    "set POCKET_PUBLIC_URL=https://pocket.medinatechlabs.net",
    "set POCKET_BASIC_AUTH_USER=$($cred.User)",
    "set POCKET_BASIC_AUTH_PASSWORD=$($cred.Pass)",
    "`"$py`" -m pocket serve --host 0.0.0.0 --port 8787 >> `"$LogDir\pocket-serve.log`" 2>&1"
  )
  Set-Content -Path $RunBat -Value ($lines -join "`r`n") -Encoding ASCII
  Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "`"$RunBat`"" -WindowStyle Hidden | Out-Null
}

Log "Always-On watchdog started (will NOT thrash a healthy host)"
if (HealthOk) {
  Log "HEART ok — already up, not restarting"
} else {
  $listening = [bool](Get-NetTCPConnection -LocalPort 8787 -State Listen -ErrorAction SilentlyContinue)
  if ($listening) {
    Log "Port listening but health failed — wait, do not kill cloudflared/host blindly"
    Start-Sleep -Seconds 8
  }
  if (-not (HealthOk)) {
    if ($listening) { KillPort8787 }  # only if still broken after wait
    StartPocket
    Start-Sleep -Seconds 5
  }
}
if (HealthOk) { Log "HEART ok" } else { Log "HEART failed initial start — see pocket-serve.log" }

while ($true) {
  if (HealthOk) {
    # ok — leave the host alone
  } else {
    # Require 3 consecutive failures before kill (avoids thrash under load)
    if (FailStreak 3) {
      Log "HEART STOPPED (3x) — restarting"
      KillPort8787
      StartPocket
      Start-Sleep -Seconds 8
      if (HealthOk) { Log "HEART RESTARTED" } else { Log "RESTART FAILED" }
    }
  }
  Start-Sleep -Seconds 15
}
