$ErrorActionPreference = "Stop"

$USERDIR = "C:\Users\alike"
$WORKSPACE = "C:\Users\alike\OneDrive\Desktop\edge_lab_new"
$RUN = "$WORKSPACE\paper_run_gate_MASTER_UPPER_SYSTEM"
$GATE = "$RUN\global_gate_decisions.csv"
$FAMILY_CONFIG = "$RUN\family_config.json"
$SIZING_CONTRACT = "$WORKSPACE\edge_factory_position_sizing_contract\position_sizing_contract.json"
$LOG_DIR = "$RUN\startup_logs_v5_supervised"
$RUNNER_DIR = "$RUN\startup_runners_v5_supervised"

$PY_CANDIDATE = "C:\Users\alike\AppData\Local\Programs\Python\Python312\python.exe"
if (Test-Path $PY_CANDIDATE) { $PY = $PY_CANDIDATE } else { $PY = "python" }

New-Item -ItemType Directory -Force -Path $RUN | Out-Null
New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $RUNNER_DIR | Out-Null

if (!(Test-Path $SIZING_CONTRACT)) {
    Write-Host "Missing sizing contract: $SIZING_CONTRACT" -ForegroundColor Red
    exit 1
}

$configObj = [ordered]@{
    old_short = "$RUN\live_blowoff_short_paper_realistic"
    impulse_long = "$RUN\live_impulse_event_long_paper"
    market_relative_short = "$RUN\live_market_relative_extreme_reversion_short_paper"
    weak_market_short = "$RUN\live_weak_market_breakdown_short_paper"
}
$configJson = $configObj | ConvertTo-Json -Depth 4
[System.IO.File]::WriteAllText($FAMILY_CONFIG, $configJson, [System.Text.UTF8Encoding]::new($false))

foreach ($p in $configObj.Values) {
    New-Item -ItemType Directory -Force -Path $p | Out-Null
}

function Quote-PSLiteral {
    param([string]$s)
    return "'" + ($s -replace "'", "''") + "'"
}

function Test-ComponentRunning {
    param([string[]]$Patterns)

    $procs = Get-CimInstance Win32_Process | Where-Object {
        $cmd = $_.CommandLine
        if ([string]::IsNullOrWhiteSpace($cmd)) { return $false }

        foreach ($pat in $Patterns) {
            if ($cmd -match [regex]::Escape($pat)) { return $true }
        }
        return $false
    }

    return @($procs).Count -gt 0
}

function New-SupervisedRunnerFile {
    param(
        [string]$Name,
        [string]$Script,
        [string[]]$ComponentArgs,
        [int]$RestartDelaySeconds
    )

    $scriptBase = [System.IO.Path]::GetFileName($Script)
    $safeName = "$Name.$scriptBase.runner.ps1"
    $runner = "$RUNNER_DIR\$safeName"
    $log = "$LOG_DIR\$Name.combined.log"

    $argItems = @()
    $argItems += Quote-PSLiteral "-u"
    $argItems += Quote-PSLiteral $Script
    foreach ($a in $ComponentArgs) {
        $argItems += Quote-PSLiteral $a
    }
    $argArray = "@(" + ($argItems -join ", ") + ")"

    $runnerCode = @"
`$ErrorActionPreference = 'Continue'
`$Host.UI.RawUI.WindowTitle = 'EDGE_FACTORY_SUPERVISED_$Name'

`$PY = $(Quote-PSLiteral $PY)
`$PY_ARGS = $argArray
`$LOG = $(Quote-PSLiteral $log)
`$RESTART_DELAY_SECONDS = $RestartDelaySeconds

Write-Host 'EDGE FACTORY SUPERVISED COMPONENT: $Name' -ForegroundColor Cyan
Write-Host 'Python:' `$PY -ForegroundColor Yellow
Write-Host 'Args:' (`$PY_ARGS -join ' ') -ForegroundColor DarkGray
Write-Host 'Log:' `$LOG -ForegroundColor Yellow
Write-Host 'Restart delay seconds:' `$RESTART_DELAY_SECONDS -ForegroundColor Yellow
Write-Host ''

while (`$true) {
    `$start = (Get-Date).ToUniversalTime().ToString('o')
    Add-Content -Path `$LOG -Value "`n===== SUPERVISOR START $Name `$start ====="

    try {
        & `$PY @PY_ARGS 2>&1 | Tee-Object -FilePath `$LOG -Append
        `$code = `$LASTEXITCODE
    } catch {
        `$code = 999
        `$msg = 'EXCEPTION: ' + `$_.Exception.Message
        Write-Host `$msg -ForegroundColor Red
        Add-Content -Path `$LOG -Value `$msg
    }

    `$end = (Get-Date).ToUniversalTime().ToString('o')
    `$exitLine = "===== PROCESS EXITED $Name ExitCode=`$code End=`$end RestartIn=`$RESTART_DELAY_SECONDS sec ====="
    Write-Host ''
    Write-Host `$exitLine -ForegroundColor Red
    Add-Content -Path `$LOG -Value `$exitLine

    Start-Sleep -Seconds `$RESTART_DELAY_SECONDS
}
"@

    Set-Content -Path $runner -Value $runnerCode -Encoding UTF8
    return $runner
}

function Start-SupervisedComponent {
    param(
        [string]$Name,
        [string]$Script,
        [string[]]$ComponentArgs,
        [string[]]$Patterns,
        [int]$RestartDelaySeconds
    )

    if (Test-ComponentRunning -Patterns $Patterns) {
        Write-Host "[SKIP] $Name already running/supervised" -ForegroundColor Yellow
        return
    }

    if (!(Test-Path $Script)) {
        Write-Host "[FAIL] Missing script for $Name : $Script" -ForegroundColor Red
        return
    }

    $runner = New-SupervisedRunnerFile -Name $Name -Script $Script -ComponentArgs $ComponentArgs -RestartDelaySeconds $RestartDelaySeconds

    Write-Host "[START-SUPERVISED] $Name" -ForegroundColor Green
    Write-Host "        runner: $runner" -ForegroundColor DarkGray

    Start-Process `
        -FilePath "powershell.exe" `
        -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-File", $runner) `
        -WorkingDirectory $USERDIR
}

$MAX_PER_FAMILY_JSON = '{"old_short":3,"impulse_long":2,"market_relative_short":3,"weak_market_short":2}'
$FAMILY_PRIORITY_JSON = '{"impulse_long":150,"old_short":100,"market_relative_short":70,"weak_market_short":30}'

Start-SupervisedComponent `
    -Name "risk_manager" `
    -Script "$USERDIR\global_paper_risk_manager_v4_config.py" `
    -Patterns @("global_paper_risk_manager_v4_config.py", "global_paper_risk_manager_v3_priority.py") `
    -RestartDelaySeconds 10 `
    -ComponentArgs @(
        "--family_config", $FAMILY_CONFIG,
        "--out_dir", $RUN,
        "--global_max_positions", "6",
        "--max_short_positions", "5",
        "--max_long_positions", "2",
        "--max_per_family_json", $MAX_PER_FAMILY_JSON,
        "--family_priority_json", $FAMILY_PRIORITY_JSON,
        "--weak_market_backup_only",
        "--pending_grace_minutes", "180",
        "--poll_seconds", "10"
    )

Start-Sleep -Seconds 2

Start-SupervisedComponent `
    -Name "old_short_logger" `
    -Script "$USERDIR\old_short_gate_aware_live_paper_logger.py" `
    -Patterns @("old_short_gate_aware_live_paper_logger.py") `
    -RestartDelaySeconds 30 `
    -ComponentArgs @(
        "--out_dir", "$RUN\live_blowoff_short_paper_realistic",
        "--global_gate_path", $GATE,
        "--require_global_gate",
        "--sizing_contract", $SIZING_CONTRACT
    )

Start-SupervisedComponent `
    -Name "impulse_long_logger" `
    -Script "$USERDIR\impulse_long_gate_aware_live_paper_logger.py" `
    -Patterns @("impulse_long_gate_aware_live_paper_logger.py") `
    -RestartDelaySeconds 30 `
    -ComponentArgs @(
        "--out_dir", "$RUN\live_impulse_event_long_paper",
        "--coins", "AUTO",
        "--global_gate_path", $GATE,
        "--require_global_gate",
        "--sizing_contract", $SIZING_CONTRACT
    )

Start-SupervisedComponent `
    -Name "market_relative_logger" `
    -Script "$USERDIR\market_relative_live_paper_logger.py" `
    -Patterns @("market_relative_live_paper_logger.py") `
    -RestartDelaySeconds 60 `
    -ComponentArgs @(
        "--out_dir", "$RUN\live_market_relative_extreme_reversion_short_paper",
        "--global_gate_path", $GATE,
        "--require_global_gate",
        "--force_scan_now",
        "--sizing_contract", $SIZING_CONTRACT
    )

Start-SupervisedComponent `
    -Name "weak_market_logger" `
    -Script "$USERDIR\weak_market_breakdown_short_live_paper_logger.py" `
    -Patterns @("weak_market_breakdown_short_live_paper_logger.py") `
    -RestartDelaySeconds 60 `
    -ComponentArgs @(
        "--out_dir", "$RUN\live_weak_market_breakdown_short_paper",
        "--global_gate_path", $GATE,
        "--require_global_gate",
        "--force_scan_now",
        "--sizing_contract", $SIZING_CONTRACT
    )

Start-SupervisedComponent `
    -Name "autopilot_v4" `
    -Script "$USERDIR\edge_factory_os_autopilot_loop_v4.py" `
    -Patterns @("edge_factory_os_autopilot_loop_v4.py") `
    -RestartDelaySeconds 60 `
    -ComponentArgs @(
        "--interval_seconds", "300",
        "--safe_execute"
    )

Write-Host ""
Write-Host "Started MASTER_UPPER_SYSTEM v5 supervised launcher." -ForegroundColor Green
Write-Host "Runner dir: $RUNNER_DIR" -ForegroundColor Yellow
Write-Host "Logs      : $LOG_DIR" -ForegroundColor Yellow
Write-Host "Safety: active_paper/live/capital remain disabled by system configs." -ForegroundColor Yellow
