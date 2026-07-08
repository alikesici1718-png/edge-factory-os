$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoRoot

$PythonCandidates = @()
if ($env:PYTHON) {
    $PythonCandidates += $env:PYTHON
}
$PythonCandidates += "python"
$PythonCandidates += "py"
$PythonCandidates += "C:\Users\alike\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

$PythonExe = $null
foreach ($Candidate in $PythonCandidates) {
    try {
        & $Candidate --version *> $null
        if ($LASTEXITCODE -eq 0) {
            $PythonExe = $Candidate
            break
        }
    } catch {
    }
}

if (-not $PythonExe) {
    Write-Error "Python was not found."
}

$env:PYTHONDONTWRITEBYTECODE = "1"
& $PythonExe "src\edge_factory_anti_overfit_alpha_search_protocol_validator_v1.py"
$ExitCode = $LASTEXITCODE
exit $ExitCode
