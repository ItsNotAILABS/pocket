# Open POCKET desk as an Edge app window (reliable launcher)
$ErrorActionPreference = "Continue"
$Root = "C:\Users\Medin\OneDrive\pocket-os"
$Desk = "http://127.0.0.1:8787/desk"
$Ensure = Join-Path $Root "scripts\Ensure-POCKET-Up.ps1"

Write-Host "[POCKET] Ensuring host is up..."
if (Test-Path $Ensure) {
  try {
    & powershell -NoProfile -ExecutionPolicy Bypass -File $Ensure
  } catch {
    Write-Host $_.Exception.Message
  }
}

function Test-DeskOk {
  try {
    $code = & curl.exe -s -m 2 -o NUL -w "%{http_code}" $Desk 2>$null
    return ($code -eq "200")
  } catch {
    return $false
  }
}

if (-not (Test-DeskOk)) {
  Write-Host "[POCKET] Starting host..."
  $env:PYTHONPATH = Join-Path $Root "src"
  $py = "C:\Users\Medin\AppData\Local\Programs\Python\Python311-arm64\python.exe"
  if (-not (Test-Path $py)) {
    $c = Get-Command python -ErrorAction SilentlyContinue
    if ($c) { $py = $c.Source }
  }
  if ($py -and (Test-Path $py)) {
    $src = Join-Path $Root "src"
    $pocketDir = Join-Path $env:USERPROFILE ".pocket"
    New-Item -ItemType Directory -Force -Path $pocketDir | Out-Null
    $out = Join-Path $pocketDir "pocket-serve.log"
    $err = Join-Path $pocketDir "pocket-serve-err.log"
    # WMI escapes agent Job Objects (Start-Process children die when the shell ends)
    $inner = "set PYTHONPATH=$src& set POCKET_EDITION=founder& set POCKET_PUBLIC_URL=http://127.0.0.1:8787& set POCKET_MESH_HOOK_ASYNC=1& cd /d $Root& `"$py`" -u -m pocket serve --host 0.0.0.0 --port 8787 >> `"$out`" 2>> `"$err`""
    $cmd = "cmd.exe /c $inner"
    try {
      Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
        CommandLine = $cmd
        CurrentDirectory = $Root
      } | Out-Null
    } catch {
      Start-Process -FilePath $py -ArgumentList "-u","-m","pocket","serve","--host","0.0.0.0","--port","8787" -WorkingDirectory $Root -WindowStyle Hidden
    }
  }
  for ($i = 0; $i -lt 25; $i++) {
    if (Test-DeskOk) { break }
    Start-Sleep -Milliseconds 400
  }
}

if (Test-DeskOk) {
  Write-Host "[POCKET] Desk is up."
} else {
  Write-Host "[POCKET] WARNING: desk still not answering. Opening Edge anyway."
}

$edgeCandidates = @(
  (Join-Path ${env:ProgramFiles(x86)} "Microsoft\Edge\Application\msedge.exe"),
  (Join-Path $env:ProgramFiles "Microsoft\Edge\Application\msedge.exe"),
  (Join-Path $env:LOCALAPPDATA "Microsoft\Edge\Application\msedge.exe")
)
$edge = $null
foreach ($p in $edgeCandidates) {
  if ($p -and (Test-Path $p)) { $edge = $p; break }
}

if (-not $edge) {
  Write-Host "[POCKET] Edge not found - default browser."
  Start-Process $Desk
  exit 0
}

Write-Host "[POCKET] Launching Edge app: $edge"
try {
  Start-Process -FilePath $edge -ArgumentList @("--app=$Desk", "--new-window", "--disable-features=msEdgeSidebar")
} catch {
  Write-Host "[POCKET] App mode failed, opening tab."
  Start-Process -FilePath $edge -ArgumentList @("--new-window", $Desk)
}
