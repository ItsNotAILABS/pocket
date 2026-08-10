# POCKET multi-agent keep-alive — leave this window open (or use Permanent script)
$ErrorActionPreference = "Continue"
if (-not $PSScriptRoot) { $PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path }
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Src = Join-Path $Root "src"
. (Join-Path $PSScriptRoot "Use-POCKET-Auth.ps1")
$env:PYTHONPATH = $Src
Set-Location -LiteralPath $Root

try {
  if (-not (Get-NetFirewallRule -DisplayName "ITSNOTAI-POCKET-8787" -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -DisplayName "ITSNOTAI-POCKET-8787" -Direction Inbound -Protocol TCP -LocalPort 8787 -Action Allow -Profile Private | Out-Null
  }
} catch {}

function Get-LanIp {
  try {
    return (Get-NetIPAddress -AddressFamily IPv4 |
      Where-Object { $_.IPAddress -like "192.168.*" } |
      Select-Object -First 1 -ExpandProperty IPAddress)
  } catch { return "192.168.x.x" }
}

$lan = Get-LanIp
Write-Host ""
Write-Host "============================================"
Write-Host " POCKET Multi-Agent Console (keep-alive)"
Write-Host " Desktop: http://127.0.0.1:8787/"
Write-Host " Phone:   http://${lan}:8787/"
Write-Host " Root=$Root"
Write-Host " Auth:    $PocketAuthFile"
Write-Host "============================================"
Write-Host ""

function DeskOk {
  try {
    # curl is more reliable than Invoke-WebRequest under load
    $code = & curl.exe -s -m 2 -o NUL -w "%{http_code}" "http://127.0.0.1:8787/desk" 2>$null
    return ($code -eq "200")
  } catch { return $false }
}

function FailStreak([int]$need = 3) {
  $n = 0
  for ($i = 0; $i -lt $need; $i++) {
    if (DeskOk) { return $false }
    Start-Sleep -Seconds 2
    $n++
  }
  return $true
}

$py = "C:\Users\Medin\AppData\Local\Programs\Python\Python311-arm64\python.exe"
if (-not (Test-Path $py)) {
  $c = Get-Command python -ErrorAction SilentlyContinue
  if ($c) { $py = $c.Source } else { $py = "python" }
}

while ($true) {
  $listening = @(Get-NetTCPConnection -LocalPort 8787 -State Listen -ErrorAction SilentlyContinue)
  if ($listening.Count -gt 0) {
    if (DeskOk) {
      Write-Host ("[{0}] healthy — watching (no kill)" -f (Get-Date -Format "HH:mm:ss"))
      # Require 3 consecutive failures (~6s) before declaring hung
      while (-not (FailStreak 3)) {
        Start-Sleep -Seconds 8
      }
      Write-Host ("[{0}] desk failed 3x — restarting hung host" -f (Get-Date -Format "HH:mm:ss"))
      foreach ($c in $listening) {
        if ($c.OwningProcess -and $c.OwningProcess -gt 0) {
          Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
        }
      }
      Start-Sleep -Seconds 2
      continue
    } else {
      # listener present but not answering yet — wait before kill (startup grace)
      Write-Host ("[{0}] listener up, waiting for desk..." -f (Get-Date -Format "HH:mm:ss"))
      if (-not (FailStreak 5)) {
        continue
      }
      Write-Host ("[{0}] hung listener — kill" -f (Get-Date -Format "HH:mm:ss"))
      foreach ($c in $listening) {
        if ($c.OwningProcess -and $c.OwningProcess -gt 0) {
          Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
        }
      }
      Start-Sleep -Seconds 2
    }
  }

  Write-Host ("[{0}] {1} -m pocket serve" -f (Get-Date -Format "HH:mm:ss"), $py)
  try {
    & $py -u -m pocket serve --host 0.0.0.0 --port 8787
  } catch {
    Write-Host "error: $_"
  }
  Write-Host ("[{0}] exited — restart in 3s" -f (Get-Date -Format "HH:mm:ss"))
  Start-Sleep -Seconds 3
}
