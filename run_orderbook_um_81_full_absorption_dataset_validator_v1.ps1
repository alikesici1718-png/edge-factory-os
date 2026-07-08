$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$RepoPath = 'C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo'
$DefaultOutputRoot = 'C:\edge_factory_external_data\binance_um_81_full_absorption_dataset_v1'
$OutputRoot = if ($env:ABSORPTION_DATASET_OUTPUT_ROOT) { $env:ABSORPTION_DATASET_OUTPUT_ROOT } else { $DefaultOutputRoot }
$RepoFull = [System.IO.Path]::GetFullPath($RepoPath)
$OutputFull = [System.IO.Path]::GetFullPath($OutputRoot)

function Assert-OutsideRepo {
  param([string]$PathValue, [string]$Label)
  if ($PathValue.Equals($RepoFull, [System.StringComparison]::OrdinalIgnoreCase) -or
      $PathValue.StartsWith($RepoFull + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to continue: $Label resolves inside repo: $PathValue"
  }
}

if (-not (Test-Path -LiteralPath (Join-Path $RepoFull '.git'))) {
  throw "Refusing to continue: repo path is not a git repo: $RepoFull"
}
Assert-OutsideRepo -PathValue $OutputFull -Label 'absorption dataset output root'

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
& $Python 'src\edge_factory_orderbook_um_81_full_absorption_dataset_validator_v1.py'
$ExitCode = $LASTEXITCODE

Write-Host "status: absorption_dataset_validator_exit_code=$ExitCode"
Write-Host "validator_json: outputs\orderbook_um_81_full_absorption_dataset_validator_report.json"
Write-Host "validator_md: outputs\orderbook_um_81_full_absorption_dataset_validator_report.md"
Write-Host "output_root: $OutputFull"
Write-Host "git_status_begin"
git -c "safe.directory=$RepoFull" status --short
Write-Host "git_status_end"
exit $ExitCode
