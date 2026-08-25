param([int]$Reps = 1000)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root
$Venv = Join-Path $Root ".venv"
$Python = Join-Path $Venv "Scripts\python.exe"
if (-not (Test-Path $Python)) { py -3.10 -m venv $Venv }
& $Python -m pip install -r (Join-Path $Root "requirements.txt")
& $Python (Join-Path $Root "src\joint_portal_model.py") --workdir $Root
Write-Host "Analytic models complete."
Write-Host "For the frozen 1000-replicate Wright-Fisher reference, see results/reference/."
Write-Host "The historical direct runner used for the frozen reference run is retained as src/wright_fisher_validation_legacy_runner.py."
Write-Host "Its original interface expects the original experiment workspace; see REPRODUCE.md before rerunning."
