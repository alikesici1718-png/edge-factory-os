Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoPath = "C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo"
$ScanRoot = "C:\Users\alike\OneDrive\Desktop\edge_lab_new"
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

Write-Host "SAFE DISK CLEANUP AUDIT V1"
Write-Host "Repo: $RepoPath"
Write-Host "Scan root: $ScanRoot"
Write-Host "Python: $PythonExe"
Write-Host "Mode: dry-run audit only; no deletion is performed."

& $PythonExe "src\edge_factory_safe_disk_cleanup_audit_v1.py"
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Outputs:"
Write-Host "  outputs\safe_disk_cleanup_audit_summary.json"
Write-Host "  outputs\safe_disk_cleanup_audit_summary.md"
Write-Host "  outputs\safe_disk_cleanup_delete_whitelist_candidates.csv"
Write-Host "  outputs\safe_disk_cleanup_report_only_large_items.csv"
Write-Host "  outputs\safe_disk_cleanup_protected_items.md"
Write-Host ""
Write-Host "Git status:"
git -c safe.directory=$RepoPath status --short
