Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoPath = "C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo"
$ScanRoot = "C:\Users\alike\OneDrive\Desktop\edge_lab_new"
$DeleteAck = [Environment]::GetEnvironmentVariable("EDGE_FACTORY_CLEANUP_DELETE_SAFE")
$BundledPython = "C:\Users\alike\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$PythonExe = $null
if ($env:EDGE_FACTORY_PYTHON) {
    $PythonExe = $env:EDGE_FACTORY_PYTHON
} elseif (Test-Path -LiteralPath $BundledPython) {
    $PythonExe = $BundledPython
} else {
    $PythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($null -ne $PythonCommand) {
        $PythonExe = $PythonCommand.Source
    }
}
if (-not $PythonExe) {
    throw "No Python executable found. Set EDGE_FACTORY_PYTHON to a valid python.exe path."
}

Set-Location -LiteralPath $RepoPath
if (-not (Test-Path -LiteralPath ".git")) {
    throw "Refusing to run: repo path is not a git repo: $RepoPath"
}

Write-Host "SAFE DISK CLEANUP DELETE V1"
Write-Host "Repo: $RepoPath"
Write-Host "Scan root: $ScanRoot"
Write-Host "Python: $PythonExe"
Write-Host "EDGE_FACTORY_CLEANUP_DELETE_SAFE=$DeleteAck"
if ($DeleteAck -eq "YES") {
    Write-Host "WARNING: permanent deletion is enabled for strict whitelist candidates only."
} else {
    Write-Host "Mode: dry-run. No files or folders will be deleted."
    Write-Host 'To enable strict whitelist deletion after review:'
    Write-Host '$env:EDGE_FACTORY_CLEANUP_DELETE_SAFE="YES"'
    Write-Host '.\run_safe_disk_cleanup_delete_v1.ps1'
}

& $PythonExe "src\edge_factory_safe_disk_cleanup_delete_v1.py"
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Outputs:"
Write-Host "  outputs\safe_disk_cleanup_delete_summary.json"
Write-Host "  outputs\safe_disk_cleanup_delete_summary.md"
Write-Host "  outputs\safe_disk_cleanup_deleted_items.csv"
Write-Host "  outputs\safe_disk_cleanup_skipped_items.csv"
Write-Host ""
Write-Host "Git status:"
git -c safe.directory=$RepoPath status --short
