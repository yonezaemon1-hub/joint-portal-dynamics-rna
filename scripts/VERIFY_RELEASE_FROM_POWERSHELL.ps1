$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "=== VERIFY JOINT PORTAL DYNAMICS RELEASE ==="

$required = @(
    "README.md",
    "paper\Joint_Portal_Dynamics_RNA_Preprint_Final_v1_1.docx",
    "paper\Joint_Portal_Dynamics_RNA_Preprint_Final_v1_1.pdf",
    "results\reference\final_summary.json",
    "results\reference\final_comparison_1000x6.csv",
    "docs\PRIOR_ART_AND_CLAIM_BOUNDARY.md",
    "SHA256SUMS.txt"
)
foreach ($rel in $required) {
    if (-not (Test-Path (Join-Path $Root $rel))) { throw "REQUIRED_FILE_MISSING: $rel" }
}

$hashFile = Join-Path $Root "SHA256SUMS.txt"
$lines = Get-Content -LiteralPath $hashFile | Where-Object { $_.Trim() }
$listed = New-Object System.Collections.Generic.List[string]
$checked = 0
foreach ($line in $lines) {
    if ($line -notmatch '^([0-9a-fA-F]{64})  (.+)$') { throw "BAD_SHA256_LINE: $line" }
    $expected = $Matches[1].ToLowerInvariant()
    $rel = $Matches[2]
    $path = Join-Path $Root ($rel -replace '/', '\')
    if (-not (Test-Path -LiteralPath $path)) { throw "HASHED_FILE_MISSING: $rel" }
    $actual = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $expected) { throw "SHA256_MISMATCH: $rel" }
    $listed.Add($rel)
    $checked++
}

if (Test-Path (Join-Path $Root ".git")) {
    $tracked = @(git ls-files | Where-Object { $_ -and $_ -ne 'SHA256SUMS.txt' } | Sort-Object)
    $manifest = @($listed | Sort-Object)
    if ($tracked.Count -ne $manifest.Count) { throw "HASH_MANIFEST_TRACKED_COUNT_MISMATCH" }
    for ($i=0; $i -lt $tracked.Count; $i++) {
        if ($tracked[$i] -ne $manifest[$i]) { throw "HASH_MANIFEST_TRACKED_SET_MISMATCH: $($tracked[$i]) != $($manifest[$i])" }
    }
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
$docx = Join-Path $Root "paper\Joint_Portal_Dynamics_RNA_Preprint_Final_v1_1.docx"
$zip = [System.IO.Compression.ZipFile]::OpenRead($docx)
try {
    $entry = $zip.Entries | Where-Object { $_.FullName -eq 'word/document.xml' } | Select-Object -First 1
    if (-not $entry) { throw "DOCX_DOCUMENT_XML_MISSING" }
    $reader = New-Object System.IO.StreamReader($entry.Open())
    try { $paperXml = $reader.ReadToEnd() } finally { $reader.Dispose() }
} finally {
    $zip.Dispose()
}
if ($paperXml -match 'AUTHOR NAME REQUIRED BEFORE PUBLICATION|\[Author name\]') { throw "MANUSCRIPT_AUTHOR_PLACEHOLDER" }
if ($paperXml -notmatch 'Ryutaro Yonezu') { throw "MANUSCRIPT_AUTHOR_MISSING" }

Write-Host "FILES_HASHED=$checked"
Write-Host "FINAL=PASS_RELEASE_INTEGRITY"
