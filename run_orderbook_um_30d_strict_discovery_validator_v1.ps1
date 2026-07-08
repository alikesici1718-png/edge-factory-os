Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoPath = "C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo"
Set-Location -LiteralPath $RepoPath

if (-not (Test-Path -LiteralPath ".git")) {
    throw "Refusing to continue: repo path is not a git repo: $RepoPath"
}

$DataRoot = if ($env:EDGE_FACTORY_DATA_ROOT) { $env:EDGE_FACTORY_DATA_ROOT } else { "C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_external_data" }
$RepoFull = [System.IO.Path]::GetFullPath($RepoPath).TrimEnd('\') + '\'
$DataRootFull = [System.IO.Path]::GetFullPath($DataRoot).TrimEnd('\') + '\'
if ($DataRootFull.StartsWith($RepoFull, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to continue: external data root resolves inside repo: $DataRootFull"
}

$Python = "C:\Users\alike\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    $Python = "python"
}

& $Python "src\edge_factory_orderbook_um_30d_strict_discovery_validator_v1.py"
$ExitCode = $LASTEXITCODE

Write-Host "status: strict_discovery_validator_exit_code=$ExitCode"
Write-Host "validator_report: outputs\orderbook_um_30d_strict_discovery_validator_report.json"
Write-Host "summary: outputs\orderbook_um_30d_strict_discovery_summary.json"
Write-Host "external_data_root: $DataRootFull"
Write-Host "git_status_begin"
git -c safe.directory=$RepoPath status --short --untracked-files=all
Write-Host "git_status_end"
exit $ExitCode
