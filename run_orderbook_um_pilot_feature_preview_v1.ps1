$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$RepoPath = 'C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo'
$DefaultDataRoot = 'C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_external_data'
$DataRoot = if ($env:EDGE_FACTORY_DATA_ROOT) { $env:EDGE_FACTORY_DATA_ROOT } else { $DefaultDataRoot }
$RepoFull = [System.IO.Path]::GetFullPath($RepoPath)
$DataFull = [System.IO.Path]::GetFullPath($DataRoot)

if (-not (Test-Path -LiteralPath (Join-Path $RepoFull '.git'))) {
  throw "Refusing to continue: repo path is not a git repo: $RepoFull"
}
if ($DataFull.StartsWith($RepoFull, [System.StringComparison]::OrdinalIgnoreCase)) {
  throw "Refusing to continue: data root resolves inside repo: $DataFull"
}

Set-Location -LiteralPath $RepoFull
function Resolve-Python {
  if ($env:PYTHON) { return $env:PYTHON }
  $Candidates = @(
    'C:\Users\alike\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe',
    'C:\Users\alike\AppData\Local\Programs\Python\Python312\python.exe'
  )
  foreach ($Candidate in $Candidates) {
    if (Test-Path -LiteralPath $Candidate) { return $Candidate }
  }
  $Command = Get-Command 'python' -ErrorAction SilentlyContinue
  if ($null -ne $Command) { return $Command.Source }
  throw 'Refusing to continue: Python interpreter not found. Set PYTHON to an explicit python.exe path.'
}
$Python = Resolve-Python
& $Python 'src\edge_factory_orderbook_um_pilot_feature_preview_v1.py'
$ExitCode = $LASTEXITCODE

Write-Host "status: pilot_feature_preview_exit_code=$ExitCode"
Write-Host "summary: outputs\orderbook_um_pilot_feature_preview_summary.json"
Write-Host "quantile_diagnostics: outputs\orderbook_um_pilot_feature_quantile_diagnostics.csv"
Write-Host "feature_sample: outputs\orderbook_um_pilot_feature_sample.csv"
Write-Host "external_data_root: $DataFull"
Write-Host "git_status_begin"
git -c "safe.directory=$RepoFull" status --short
Write-Host "git_status_end"
exit $ExitCode
