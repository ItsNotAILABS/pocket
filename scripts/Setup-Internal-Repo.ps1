# Setup-Internal-Repo.ps1
# Founder tree: local git only. No public GitHub remote.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
if (-not (Test-Path (Join-Path $Root "src\pocket"))) {
  $Root = "C:\Users\Medin\OneDrive\pocket-os"
}
Set-Location $Root

$InternalBare = Join-Path $env:USERPROFILE ".pocket\repos\pocket-internal.git"
$FounderEnv = Join-Path $env:USERPROFILE ".pocket\founder.env"
$Marker = Join-Path $Root "INTERNAL.md"

Write-Host "=== POCKET internal (founder) setup ===" -ForegroundColor Cyan
Write-Host "Tree: $Root"

New-Item -ItemType Directory -Force -Path (Split-Path $InternalBare) | Out-Null
if (-not (Test-Path $InternalBare)) {
  git init --bare $InternalBare | Out-Null
  Write-Host "Created bare repo: $InternalBare"
} else {
  Write-Host "Bare repo exists: $InternalBare"
}

# Detach from public GitHub completely
$remotes = @(git remote 2>$null)
foreach ($r in $remotes) {
  if ($r -eq "origin" -or $r -eq "public") {
    $url = ""
    try { $url = git remote get-url $r 2>$null } catch {}
    Write-Host "Removing remote $r ($url)"
    git remote remove $r
  }
}

$haveInternal = (@(git remote 2>$null) -contains "internal")
if (-not $haveInternal) {
  git remote add internal $InternalBare
  Write-Host "Added remote internal -> $InternalBare"
} else {
  git remote set-url internal $InternalBare
  Write-Host "Updated remote internal -> $InternalBare"
}

$status = git status --porcelain
if (-not $status) {
  try {
    git push -u internal HEAD:main 2>&1 | ForEach-Object { Write-Host $_ }
  } catch {
    Write-Host "Push note: commit first, then git push -u internal main" -ForegroundColor Yellow
  }
} else {
  Write-Host "Uncommitted changes present. When ready:" -ForegroundColor Yellow
  Write-Host "  git add -A; git commit -m 'founder work'; git push -u internal main"
}

New-Item -ItemType Directory -Force -Path (Join-Path $env:USERPROFILE ".pocket") | Out-Null
@(
  "# POCKET founder (internal) - daily desk on THIS PC",
  "# Public face is separate: github.com/ItsNotAILABS/pocket + pocket.medinatechlabs.net",
  "POCKET_EDITION=founder",
  "POCKET_PUBLIC_URL=http://127.0.0.1:8787",
  "POCKET_MARKETING_URL=https://pocket.medinatechlabs.net",
  "POCKET_HIDE_PUBLIC_GITHUB=1",
  "POCKET_PUBLIC_LOCK=1"
) | Set-Content -Path $FounderEnv -Encoding UTF8
Write-Host "Wrote $FounderEnv"

@(
  "# This tree is INTERNAL (founder)",
  "",
  "You use this folder every day. It is NOT the public product face.",
  "",
  "- This repo: your running POCKET. Git remote = internal (local bare only).",
  "- Public GitHub: ItsNotAILABS/pocket - marketing + customer releases. NOT a remote here.",
  "- Your desk: http://127.0.0.1:8787/desk",
  "- Customer host: https://pocket.medinatechlabs.net - only if you run the tunnel.",
  "",
  "## Git",
  "",
  "    git add -A",
  "    git commit -m '...'",
  "    git push internal main",
  "",
  "Never re-add origin to github.com/ItsNotAILABS/pocket from this tree.",
  "",
  "## Ship to public (deliberate)",
  "",
  "1. Stabilize here.",
  "2. Promote a clean copy/branch to public GitHub only when users should see it.",
  "3. Do not auto-connect public remotes on this machine.",
  "",
  "See FOUNDER.md"
) | Set-Content -Path $Marker -Encoding UTF8

Write-Host ""
Write-Host "DONE. Remotes now:" -ForegroundColor Green
git remote -v
Write-Host ""
Write-Host "Desk (you):     http://127.0.0.1:8787/desk"
Write-Host "Marketing host: https://pocket.medinatechlabs.net (separate; optional)"
Write-Host "Public GitHub:  not linked"
