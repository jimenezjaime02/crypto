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
$pushOutput = git push -u origin main 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Push succeeded." -ForegroundColor Green
    exit 0
}

Write-Warning "Initial push failed:`n$pushOutput"
Write-Host "Attempting to pull --rebase and retry..." -ForegroundColor Yellow
git pull --rebase origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Pull/rebase failed. Aborting." -ForegroundColor Red
    exit 1
}

git push -u origin main
if ($LASTEXITCODE -eq 0) {
    Write-Host "Push succeeded after rebase." -ForegroundColor Green
    exit 0
}

Write-Host "Push failed." -ForegroundColor Red
exit 1
