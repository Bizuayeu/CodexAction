param(
    [string]$WorktreePath = "",
    [switch]$AllowMissing
)

$ErrorActionPreference = "Stop"

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

if ([string]::IsNullOrWhiteSpace($WorktreePath)) {
    if (-not [string]::IsNullOrWhiteSpace($env:CODEX_WORKTREE_PATH)) {
        $WorktreePath = $env:CODEX_WORKTREE_PATH
    }
    else {
        $WorktreePath = (Get-Location).Path
    }
}

$scriptPath = Join-Path -Path $PSScriptRoot -ChildPath "Load-WeaveSessionContext.ps1"
$outputPath = Join-Path -Path $WorktreePath -ChildPath ".codex\weave-session-context.md"

$arguments = @{
    WorktreePath = $WorktreePath
    OutputPath = $outputPath
}

if ($AllowMissing) {
    $arguments.AllowMissing = $true
}

& $scriptPath @arguments
