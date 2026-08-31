# Keep POCKET host online (desk + phone tunnel).
# Usage: powershell -File scripts/keep_pocket_serve.ps1
$ErrorActionPreference = "SilentlyContinue"
$env:PYTHONPATH = "C:\Users\Medin\OneDrive\pocket-os\src"
$root = "C:\Users\Medin\OneDrive\pocket-os"
$logDir = Join-Path $env:USERPROFILE ".pocket"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$out = Join-Path $logDir "serve-out.log"
$err = Join-Path $logDir "serve-err.log"

function Test-PocketUp {
  try {
    $r = Invoke-WebRequest "http://127.0.0.1:8787/v1/health" -UseBasicParsing -TimeoutSec 3
    return $r.StatusCode -eq 200
  } catch { return $false }
}

function Start-Pocket {
  Get-NetTCPConnection -LocalPort 8787 -ErrorAction SilentlyContinue |
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
  Start-Sleep -Seconds 1
  Start-Process python -ArgumentList "-u","-m","pocket","serve" -WorkingDirectory $root -WindowStyle Hidden `
    -RedirectStandardOutput $out -RedirectStandardError $err
  Start-Sleep -Seconds 3
}

if (-not (Test-PocketUp)) {
  Write-Host "[keep] starting pocket serve…"
  Start-Pocket
}
if (Test-PocketUp) {
  $h = Invoke-RestMethod "http://127.0.0.1:8787/v1/health" -TimeoutSec 5
  Write-Host "[keep] UP version=$($h.version) heart=$($h.heart)"
  exit 0
}
Write-Host "[keep] FAILED - see $err"
exit 1
