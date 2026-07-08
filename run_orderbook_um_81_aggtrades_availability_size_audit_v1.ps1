$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$RepoPath = 'C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo'
$DefaultDataRoot = 'C:\edge_factory_external_data'
$DataRoot = if ($env:EDGE_FACTORY_DATA_ROOT) { $env:EDGE_FACTORY_DATA_ROOT } else { $DefaultDataRoot }
$RepoFull = [System.IO.Path]::GetFullPath($RepoPath)
$DataFull = [System.IO.Path]::GetFullPath($DataRoot)

if (-not (Test-Path -LiteralPath (Join-Path $RepoFull '.git'))) {
  throw "Refusing to continue: repo path is not a git repo: $RepoFull"
}
if ($DataFull.Equals($RepoFull, [System.StringComparison]::OrdinalIgnoreCase) -or
    $DataFull.StartsWith($RepoFull + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
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
& $Python 'src\edge_factory_orderbook_um_81_aggtrades_availability_size_audit_v1.py'
$ExitCode = $LASTEXITCODE

Write-Host "status: aggtrades_availability_size_audit_exit_code=$ExitCode"
Write-Host "manifest_csv: outputs\orderbook_um_81_aggtrades_availability_manifest.csv"
Write-Host "manifest_jsonl: outputs\orderbook_um_81_aggtrades_availability_manifest.jsonl"
Write-Host "coverage_summary_json: outputs\orderbook_um_81_aggtrades_coverage_summary.json"
Write-Host "coverage_summary_md: outputs\orderbook_um_81_aggtrades_coverage_summary.md"
Write-Host "coverage_gaps_csv: outputs\orderbook_um_81_aggtrades_vs_bookdepth_coverage_gaps.csv"
Write-Host "external_data_root: $DataFull"
Write-Host "git_status_begin"
git -c "safe.directory=$RepoFull" status --short
Write-Host "git_status_end"
exit $ExitCode
