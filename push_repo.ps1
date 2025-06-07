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
try {
    git push -u origin main
    Write-Host "Push succeeded." -ForegroundColor Green
    exit 0
} catch {
    Write-Host "Push failed: $_" -ForegroundColor Red
    exit 1
}
