# Whole POCKET + PhoneAI install: always-on runtime, then print tunnel URLs.
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
if (-not (Test-Path (Join-Path $Root "src\pocket"))) {
  $Root = "C:\Users\Medin\OneDrive\pocket-os"
}
$env:PYTHONPATH = Join-Path $Root "src"
$py = "$env:LOCALAPPDATA\Programs\Python\Python311-arm64\python.exe"
if (-not (Test-Path $py)) {
  $c = Get-Command python -ErrorAction SilentlyContinue
  if ($c) { $py = $c.Source } else { $py = "python" }
}
Write-Host "Installing always-on POCKET runtime from $Root"
& $py -m pocket install
Write-Host ""
Write-Host "Tunnel PhoneAI intro:  https://pocket.medinatechlabs.net/phoneai"
Write-Host "Local intro:           http://127.0.0.1:8787/phoneai"
Write-Host "Kernel:                http://127.0.0.1:8787/phoneai/app"
Write-Host "Setup:                 http://127.0.0.1:8787/setup"
Write-Host "Sign up:               http://127.0.0.1:8787/signup"
