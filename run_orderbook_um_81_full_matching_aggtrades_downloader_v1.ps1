$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$RepoPath = 'C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo'
$DefaultDataRoot = 'C:\edge_factory_external_data'
$DataRoot = if ($env:EDGE_FACTORY_DATA_ROOT) { $env:EDGE_FACTORY_DATA_ROOT } else { $DefaultDataRoot }
$RepoFull = [System.IO.Path]::GetFullPath($RepoPath)
$DataFull = [System.IO.Path]::GetFullPath($DataRoot)
$RawFull = [System.IO.Path]::GetFullPath((Join-Path $DataFull 'binance_um_81_full_matching_aggtrades_raw'))
$LogsFull = [System.IO.Path]::GetFullPath((Join-Path $DataFull 'binance_um_81_full_matching_aggtrades_logs'))
$WorkersValue = if ($env:AGGTRADES_DOWNLOAD_WORKERS) { $env:AGGTRADES_DOWNLOAD_WORKERS } else { '8 (default)' }
$ConnectTimeoutValue = if ($env:AGGTRADES_DOWNLOAD_CONNECT_TIMEOUT) { $env:AGGTRADES_DOWNLOAD_CONNECT_TIMEOUT } else { '20 (default)' }
$ReadTimeoutValue = if ($env:AGGTRADES_DOWNLOAD_READ_TIMEOUT) { $env:AGGTRADES_DOWNLOAD_READ_TIMEOUT } else { '120 (default)' }
$MaxRetriesValue = if ($env:AGGTRADES_DOWNLOAD_MAX_RETRIES) { $env:AGGTRADES_DOWNLOAD_MAX_RETRIES } else { '5 (default)' }

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
Assert-OutsideRepo -PathValue $DataFull -Label 'data root'
Assert-OutsideRepo -PathValue $RawFull -Label 'raw target directory'
Assert-OutsideRepo -PathValue $LogsFull -Label 'logs directory'

Write-Host "EDGE_FACTORY_DATA_ROOT=$DataFull"
Write-Host "AGGTRADES_DOWNLOAD_WORKERS=$WorkersValue"
Write-Host "AGGTRADES_DOWNLOAD_CONNECT_TIMEOUT=$ConnectTimeoutValue"
Write-Host "AGGTRADES_DOWNLOAD_READ_TIMEOUT=$ReadTimeoutValue"
Write-Host "AGGTRADES_DOWNLOAD_MAX_RETRIES=$MaxRetriesValue"
Write-Host 'example_parallel_command_begin'
Write-Host '$env:EDGE_FACTORY_DATA_ROOT="C:\edge_factory_external_data"'
Write-Host '$env:AGGTRADES_81_FULL_MATCHING_DOWNLOAD="YES"'
Write-Host '$env:AGGTRADES_DOWNLOAD_WORKERS="16"'
Write-Host '.\run_orderbook_um_81_full_matching_aggtrades_downloader_v1.ps1'
Write-Host 'example_parallel_command_end'

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
& $Python 'src\edge_factory_orderbook_um_81_full_matching_aggtrades_manifest_validator_v1.py'
$ManifestExitCode = $LASTEXITCODE
if ($ManifestExitCode -ne 0) {
  Write-Host "status: downloader_blocked_manifest_validator_exit_code=$ManifestExitCode"
  Write-Host "git_status_begin"
  git -c "safe.directory=$RepoFull" status --short
  Write-Host "git_status_end"
  exit $ManifestExitCode
}

$ValidationPath = Join-Path $RepoFull 'outputs\orderbook_um_81_full_matching_aggtrades_manifest_validation.json'
$Validation = Get-Content -Raw -LiteralPath $ValidationPath | ConvertFrom-Json
Write-Host "FULL_MATCHING_AGGTRADES_WARNING_EXPECTED_FILE_COUNT=$($Validation.expected_file_count)"
Write-Host "FULL_MATCHING_AGGTRADES_WARNING_ESTIMATED_MATCHING_GB=$($Validation.estimated_matching_size_gb)"
Write-Host "FULL_MATCHING_AGGTRADES_WARNING_ESTIMATED_REMAINING_GB=$($Validation.disk.estimated_remaining_download_gb)"
Write-Host "FULL_MATCHING_AGGTRADES_WARNING_REQUIRED_FREE_GB=$($Validation.disk.required_free_gb)"
Write-Host "FULL_MATCHING_AGGTRADES_WARNING_FREE_GB=$($Validation.disk.free_gb)"
Write-Host "FULL_MATCHING_AGGTRADES_WARNING_RAW_TARGET=$RawFull"
Write-Host "ACK_ENV_AGGTRADES_81_FULL_MATCHING_DOWNLOAD=$env:AGGTRADES_81_FULL_MATCHING_DOWNLOAD"

& $Python 'src\edge_factory_orderbook_um_81_full_matching_aggtrades_downloader_v1.py'
$ExitCode = $LASTEXITCODE

Write-Host "status: downloader_exit_code=$ExitCode"
Write-Host "download_summary_json: outputs\orderbook_um_81_full_matching_aggtrades_download_summary.json"
Write-Host "download_summary_md: outputs\orderbook_um_81_full_matching_aggtrades_download_summary.md"
Write-Host "file_status_csv: outputs\orderbook_um_81_full_matching_aggtrades_file_status.csv"
Write-Host "symbol_coverage_csv: outputs\orderbook_um_81_full_matching_aggtrades_symbol_coverage.csv"
Write-Host "blocked_not_acknowledged: outputs\orderbook_um_81_full_matching_aggtrades_BLOCKED_DOWNLOAD_NOT_ACKNOWLEDGED.md"
Write-Host "external_data_root: $DataFull"
Write-Host "raw_target_directory: $RawFull"
Write-Host "logs_directory: $LogsFull"
Write-Host "git_status_begin"
git -c "safe.directory=$RepoFull" status --short
Write-Host "git_status_end"
exit $ExitCode
