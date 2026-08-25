$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root
$Venv = Join-Path $Root ".venv"
$Python = Join-Path $Venv "Scripts\python.exe"
if (-not (Test-Path $Python)) { py -3.10 -m venv $Venv }
& $Python -m pip install -r (Join-Path $Root "requirements.txt")
& $Python (Join-Path $Root "src\joint_portal_model.py") --workdir $Root
