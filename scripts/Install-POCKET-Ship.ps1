# Install labeled shortcuts: YOUR POCKET vs USER FACING.
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Desktop = [Environment]::GetFolderPath("Desktop")
$StartMenu = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\POCKET"; New-Item -ItemType Directory -Force $StartMenu | Out-Null
$Wsh = New-Object -ComObject WScript.Shell
function Shortcut($Path,$Target,$Description) { $s=$Wsh.CreateShortcut($Path);$s.TargetPath=$Target;$s.WorkingDirectory=$Root;$s.Description=$Description;$s.Save() }
# Product 1 — your machine
Shortcut (Join-Path $Desktop "POCKET Owner.lnk") (Join-Path $Root "scripts\Open-POCKET-Owner.cmd") "POCKET Owner — your machine on :8787"
Shortcut (Join-Path $StartMenu "POCKET Owner.lnk") (Join-Path $Root "scripts\Open-POCKET-Owner.cmd") "POCKET Owner — your machine on :8787"
# Product 2 — what users get
Shortcut (Join-Path $Desktop "POCKET for Users.lnk") (Join-Path $Root "scripts\Open-POCKET-User.cmd") "POCKET for Users — customer product on :8788"
Shortcut (Join-Path $StartMenu "POCKET for Users.lnk") (Join-Path $Root "scripts\Open-POCKET-User.cmd") "POCKET for Users — customer product on :8788"
# Local Edge still opens the host desk (ribbon tells you which face)
Shortcut (Join-Path $Desktop "POCKET Edge (this machine).lnk") (Join-Path $Root "scripts\Open-POCKET-Edge.cmd") "Local Edge window onto this host"
Shortcut (Join-Path $StartMenu "POCKET Edge (this machine).lnk") (Join-Path $Root "scripts\Open-POCKET-Edge.cmd") "Local Edge window onto this host"
Write-Host "Installed:"
Write-Host "  POCKET Owner       = your machine :8787"
Write-Host "  POCKET for Users   = customer product :8788"
Write-Host "  POCKET Edge (this machine) = Owner Edge window"
Write-Host "Two products. Two ports. Do not mix them."
