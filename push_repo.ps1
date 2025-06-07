<#
PowerShell helper to initialise, commit and push this repository.
Equivalent to *push_repo.sh* but native for Windows users.
#>
param(
    [string]$RemoteUrl = "https://github.com/jimenezjaime02/crypto.git"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Ensure we run in script directory
Set-Location $PSScriptRoot

if (-not (Test-Path .git)) {
    Write-Host "Initialising git repo…"
    git init | Out-Null
}

# Add origin if missing
if (-not (git remote | Select-String -Pattern '^origin$')) {
    git remote add origin $RemoteUrl
}

# Ensure main branch
$current = git branch --show-current
if ($current -ne "main") {
    git branch -M main
}

# Create .gitignore if absent
if (-not (Test-Path .gitignore)) {
@'
__pycache__/
*.py[cod]
.venv/
data/
knowledgebase.csv
coingecko.log
'@ | Out-File .gitignore -Encoding utf8
}

# Stage + commit pending changes
if (-not (git status --porcelain)) {
    Write-Host "Nothing to commit."
} else {
    git add -A
    try {
        git commit -m "Automated commit" | Out-Null
    } catch { }
}

# Push
$pushOutput = ""
$exitCode = 0
try {
    $pushOutput = git push -u origin main 2>&1
    $exitCode = $LASTEXITCODE
} catch {
    $pushOutput = $_.Exception.Message
    $exitCode = 1
}

# Determine success. Some git versions return 0 even on non-fast-forward. So check output keywords too.
$pushFailed = ($exitCode -ne 0) -or ($pushOutput -match 'rejected' -or $pushOutput -match 'failed')
if (-not $pushFailed) {
    Write-Host "Push succeeded." -ForegroundColor Green
    exit 0
}
# else continue to rebase attempt
Write-Warning "Initial push failed (exit $exitCode):`n$pushOutput"
Write-Host "Attempting to pull --rebase and retry..." -ForegroundColor Yellow
git pull --rebase origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Pull/rebase failed. Aborting." -ForegroundColor Red
    exit 1
}

# Retry push after successful rebase
$pushOutput = git push -u origin main 2>&1
$exitCode = $LASTEXITCODE
if ($exitCode -eq 0 -and ($pushOutput -notmatch 'rejected' -and $pushOutput -notmatch 'failed')) {
    Write-Host "Push succeeded after rebase." -ForegroundColor Green
    exit 0
}

Write-Host "Push failed." -ForegroundColor Red
exit 1
