param([int]$Reps = 1000)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root
$Venv = Join-Path $Root ".venv"
$Python = Join-Path $Venv "Scripts\python.exe"
if (-not (Test-Path $Python)) { py -3.10 -m venv $Venv }
& $Python -m pip install -r (Join-Path $Root "requirements.txt")
& $Python (Join-Path $Root "src\joint_portal_model.py") --workdir $Root
if ($LASTEXITCODE -ne 0) { throw "ANALYTIC_FAILED" }
& $Python (Join-Path $Root "src\wright_fisher_validation.py") --workdir $Root --reps $Reps --seed 20260823
if ($LASTEXITCODE -ne 0) { throw "WF_FAILED" }
& $Python (Join-Path $Root "src\summarize_results.py") --wf-json (Join-Path $Root "results\wf_direct_reps${Reps}_result.json") --analytic-json (Join-Path $Root "results\analytic_predictions_N500.json") --outdir (Join-Path $Root "results")
