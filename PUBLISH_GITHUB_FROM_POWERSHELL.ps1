$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

Write-Host "=== JOINT PORTAL DYNAMICS - GITHUB PUBLIC RELEASE V1.1 ==="

$git = Get-Command git.exe -ErrorAction SilentlyContinue
if (-not $git) { throw "GIT_NOT_FOUND" }
$gh = Get-Command gh.exe -ErrorAction SilentlyContinue
if (-not $gh) {
    Write-Host "GitHub CLI (gh) is not installed."
    Write-Host "Install it, then rerun: winget install --id GitHub.cli"
    throw "GH_CLI_NOT_FOUND"
}

& gh auth status
if ($LASTEXITCODE -ne 0) {
    Write-Host "Run: gh auth login"
    throw "GH_NOT_AUTHENTICATED"
}

$login = (& gh api user --jq .login).Trim()
if (-not $login) { throw "GITHUB_LOGIN_UNKNOWN" }
Write-Host "GitHub user: $login"
Write-Host "Public author: Ryutaro Yonezu"

$pdf = Join-Path $Root "paper\Joint_Portal_Dynamics_RNA_Preprint_Final_v1_1.pdf"
$docx = Join-Path $Root "paper\Joint_Portal_Dynamics_RNA_Preprint_Final_v1_1.docx"
if (-not (Test-Path $pdf)) { throw "PAPER_PDF_MISSING" }
if (-not (Test-Path $docx)) { throw "PAPER_DOCX_MISSING" }

$cffTemplate = Get-Content -LiteralPath (Join-Path $Root "CITATION_TEMPLATE.cff") -Raw
$cff = $cffTemplate.Replace('[GITHUB USER]', $login)
[IO.File]::WriteAllText((Join-Path $Root "CITATION.cff"), $cff, $Utf8NoBom)

$zenodoPath = Join-Path $Root "metadata\ZENODO_PREPRINT_METADATA.md"
$zenodo = Get-Content -LiteralPath $zenodoPath -Raw
$zenodo = $zenodo.Replace('[GITHUB USER]', $login)
[IO.File]::WriteAllText($zenodoPath, $zenodo, $Utf8NoBom)

$scanFiles = Get-ChildItem -LiteralPath $Root -Recurse -File | Where-Object {
    $_.FullName -notmatch '[\\/]\.git[\\/]' -and
    $_.FullName -notmatch '[\\/]\.venv[\\/]' -and
    $_.FullName -notmatch '[\\/]__pycache__[\\/]' -and
    $_.Name -ne 'CITATION_TEMPLATE.cff' -and
    $_.Name -ne 'PUBLISH_GITHUB_FROM_POWERSHELL.ps1' -and
    $_.Name -ne 'VERIFY_RELEASE_FROM_POWERSHELL.ps1'
}
foreach ($f in $scanFiles) {
    if ($f.Extension -in @('.png','.pdf','.docx','.zip','.pyc')) { continue }
    $txt = Get-Content -LiteralPath $f.FullName -Raw -ErrorAction SilentlyContinue
    if ($txt -match '\[GITHUB USER\]|AUTHOR NAME REQUIRED BEFORE PUBLICATION|\[Author name\]') {
        throw "UNRESOLVED_PUBLICATION_PLACEHOLDER: $($f.FullName)"
    }
}

if (-not (Test-Path (Join-Path $Root ".git"))) {
    git init
    if ($LASTEXITCODE -ne 0) { throw "GIT_INIT_FAILED" }
    git branch -M main
}
if (-not (git config user.name)) { git config user.name "Ryutaro Yonezu" }
if (-not (git config user.email)) { git config user.email "$login@users.noreply.github.com" }

git add .
if ($LASTEXITCODE -ne 0) { throw "GIT_STAGE_FAILED" }

$hashPath = Join-Path $Root "SHA256SUMS.txt"
$tracked = @(git ls-files | Where-Object { $_ -and $_ -ne 'SHA256SUMS.txt' } | Sort-Object)
if ($tracked.Count -eq 0) { throw "NO_TRACKED_RELEASE_FILES" }
$hashLines = foreach ($rel in $tracked) {
    $path = Join-Path $Root ($rel -replace '/', '\\')
    if (-not (Test-Path -LiteralPath $path)) { throw "TRACKED_FILE_MISSING: $rel" }
    $h = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    "$h  $rel"
}
[IO.File]::WriteAllLines($hashPath, $hashLines, $Utf8NoBom)
git add SHA256SUMS.txt
if ($LASTEXITCODE -ne 0) { throw "HASH_STAGE_FAILED" }

& (Join-Path $Root "scripts\VERIFY_RELEASE_FROM_POWERSHELL.ps1")
if ($LASTEXITCODE -ne 0) { throw "RELEASE_VERIFY_FAILED" }

git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "Public research release v1.1.0"
    if ($LASTEXITCODE -ne 0) { throw "GIT_COMMIT_FAILED" }
}

$repo = "joint-portal-dynamics-rna"
$exists = $false
& gh repo view "$login/$repo" *> $null
if ($LASTEXITCODE -eq 0) { $exists = $true }

if (-not $exists) {
    & gh repo create $repo --public --source . --remote origin --push --description "State-resolved joint portal dynamics on an RNA neutral network"
    if ($LASTEXITCODE -ne 0) { throw "GH_REPO_CREATE_FAILED" }
} else {
    if (-not (git remote | Select-String '^origin$')) {
        git remote add origin "https://github.com/$login/$repo.git"
    }
    git push -u origin main
    if ($LASTEXITCODE -ne 0) { throw "GH_PUSH_FAILED" }
}

& gh release view v1.1.0 *> $null
if ($LASTEXITCODE -ne 0) {
    & gh release create v1.1.0 $pdf --title "v1.1.0 - Prior-art boundary re-audited" --notes-file (Join-Path $Root "RELEASE_NOTES_v1.1.md")
    if ($LASTEXITCODE -ne 0) { throw "GH_RELEASE_FAILED" }
}

Write-Host ""
Write-Host "FINAL=GITHUB_PUBLIC_RELEASE_COMPLETE"
Write-Host "REPO=https://github.com/$login/$repo"
Write-Host "NEXT=Enable this repository in Zenodo, then archive release v1.1.0."
