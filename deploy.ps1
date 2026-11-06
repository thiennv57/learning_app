param(
    [Parameter(Mandatory = $true)]
    [string]$PAUser,

    [string]$SSHHost = "ssh.pythonanywhere.com",
    [string]$Branch = "main",
    [string]$RemoteAppDir = "~/learning_app",
    [string]$VirtualEnv = "learning_app",
    [string]$WSGIPath,
    [string]$CommitMessage = "deploy: update $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",

    [switch]$SkipPip,
    [switch]$SkipCommit
)

$ErrorActionPreference = "Stop"

if (-not $WSGIPath) {
    $WSGIPath = "/var/www/${PAUser}_pythonanywhere_com_wsgi.py"
}

Write-Host "==> Checking git repo..." -ForegroundColor Cyan
if (-not (Test-Path ".git")) {
    throw "Current folder is not a git repository. Run this script inside your git project."
}

git rev-parse --is-inside-work-tree | Out-Null

if (-not $SkipCommit) {
    Write-Host "==> Commit local changes..." -ForegroundColor Cyan
    git add -A

    $hasChanges = (git status --porcelain)
    if ($hasChanges) {
        git commit -m $CommitMessage
    } else {
        Write-Host "No local changes to commit." -ForegroundColor Yellow
    }
}

Write-Host "==> Push to origin/$Branch..." -ForegroundColor Cyan
git push origin $Branch

Write-Host "==> Deploy on PythonAnywhere..." -ForegroundColor Cyan
$remotePip = if ($SkipPip) { "echo 'Skip pip install'" } else { "pip install -r requirements.txt" }

$remoteCommands = @"
set -e
cd $RemoteAppDir
workon $VirtualEnv
git pull origin $Branch
$remotePip
touch $WSGIPath
echo 'Deploy done.'
"@

ssh "$PAUser@$SSHHost" $remoteCommands

Write-Host "==> Success: app reloaded on PythonAnywhere" -ForegroundColor Green
Write-Host "Tip: first run example" -ForegroundColor DarkGray
Write-Host ".\deploy.ps1 -PAUser yourusername -RemoteAppDir '~/your-repo/learning_app' -VirtualEnv myenv" -ForegroundColor DarkGray
