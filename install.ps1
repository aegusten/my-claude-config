# install.ps1
# Run this on any new PC to symlink your Claude config
# Usage: .\install.ps1
# Requires: Run as Administrator (for symlinks on Windows)

$repoDir = $PSScriptRoot
$claudeDir = "$env:USERPROFILE\.claude"

Write-Host "🤖 Setting up Claude config for aegusten..." -ForegroundColor Cyan
Write-Host "Repo: $repoDir"
Write-Host "Target: $claudeDir"
Write-Host ""

# Create .claude dir if needed
if (-not (Test-Path $claudeDir)) {
    New-Item -ItemType Directory -Path $claudeDir | Out-Null
    Write-Host "✅ Created $claudeDir"
}

# Helper function to create symlink
function Link-Item($source, $target) {
    if (Test-Path $target) {
        Remove-Item $target -Recurse -Force
    }
    New-Item -ItemType SymbolicLink -Path $target -Target $source | Out-Null
    Write-Host "✅ Linked: $target → $source"
}

# Symlink CLAUDE.md
Link-Item "$repoDir\CLAUDE.md" "$claudeDir\CLAUDE.md"

# Symlink agents/
Link-Item "$repoDir\agents" "$claudeDir\agents"

# Symlink skills/
Link-Item "$repoDir\skills" "$claudeDir\skills"

Write-Host ""
Write-Host "✅ Done! Run 'claude' in any project to start." -ForegroundColor Green
Write-Host "💡 Your agents: senior-backend, senior-architect, security-reviewer, code-reviewer"
