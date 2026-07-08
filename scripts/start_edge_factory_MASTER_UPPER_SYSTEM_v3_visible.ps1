$ErrorActionPreference = "Stop"

$USERDIR = "C:\Users\alike"
$WORKSPACE = "C:\Users\alike\OneDrive\Desktop\edge_lab_new"
$RUN = "$WORKSPACE\paper_run_gate_MASTER_UPPER_SYSTEM"
$GATE = "$RUN\global_gate_decisions.csv"
$FAMILY_CONFIG = "$RUN\family_config.json"
$SIZING_CONTRACT = "$WORKSPACE\edge_factory_position_sizing_contract\position_sizing_contract.json"
$LOG_DIR = "$RUN\startup_logs_v3_visible"

$PY_CANDIDATE = "C:\Users\alike\AppData\Local\Programs\Python\Python312\python.exe"
if (Test-Path $PY_CANDIDATE) {
    $PY = $PY_CANDIDATE
} else {
    $PY = "python"
}

New-Item -ItemType Directory -Force -Path $RUN | Out-Null
New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null

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

function Quote-PS {
    param([string]$s)
    return "'" + ($s -replace "'", "''") + "'"
}

function Test-ComponentRunning {
    param([string[]]$Patterns)

    $procs = Get-CimInstance Win32_Process | Where-Object {
        $cmd = $_.CommandLine
        if ([string]::IsNullOrWhiteSpace($cmd)) { return $false }

        foreach ($pat in $Patterns) {
            if ($cmd -match [regex]::Escape($pat)) {
                return $true
            }
        }
        return $false
    }

    return @($procs).Count -gt 0
}

function Start-VisibleComponent {
    param(
        [string]$Name,
        [string]$Script,
        [string[]]$ComponentArgs,
        [string[]]$Patterns
    )

    if (Test-ComponentRunning -Patterns $Patterns) {
        Write-Host "[SKIP] $Name already running" -ForegroundColor Yellow
        return
    }

    if (!(Test-Path $Script)) {
        Write-Host "[FAIL] Missing script for $Name : $Script" -ForegroundColor Red
        return
    }

    $log = "$LOG_DIR\$Name.combined.log"
    Remove-Item $log -ErrorAction SilentlyContinue

    $tokens = @()
    $tokens += Quote-PS $PY
    $tokens += "-u"
    $tokens += Quote-PS $Script

    foreach ($a in $ComponentArgs) {
        if ($a.StartsWith("--")) {
            $tokens += $a
        } else {
            $tokens += Quote-PS $a
        }
    }

    $pythonCmd = "& " + ($tokens -join " ")

    $psCmd = @"
`$Host.UI.RawUI.WindowTitle = 'EDGE_FACTORY_$Name'
Write-Host 'EDGE FACTORY COMPONENT: $Name' -ForegroundColor Cyan
Write-Host 'Command:' -ForegroundColor Yellow
Write-Host "$pythonCmd" -ForegroundColor DarkGray
Write-Host 'Log: $log' -ForegroundColor Yellow
Write-Host ''
$pythonCmd 2>&1 | Tee-Object -FilePath $(Quote-PS $log) -Append
Write-Host ''
Write-Host 'PROCESS EXITED. ExitCode=' `$LASTEXITCODE -ForegroundColor Red
Write-Host 'Window intentionally stays open for diagnosis.' -ForegroundColor Yellow
"@

    Write-Host "[START-VISIBLE] $Name" -ForegroundColor Green
    Write-Host "        $pythonCmd" -ForegroundColor DarkGray

    Start-Process `
        -FilePath "powershell.exe" `
        -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $psCmd) `
        -WorkingDirectory $USERDIR
}

$MAX_PER_FAMILY_JSON = '{"old_short":3,"impulse_long":2,"market_relative_short":3,"weak_market_short":2}'
$FAMILY_PRIORITY_JSON = '{"impulse_long":150,"old_short":100,"market_relative_short":70,"weak_market_short":30}'

Start-VisibleComponent `
    -Name "risk_manager" `
    -Script "$USERDIR\global_paper_risk_manager_v4_config.py" `
    -Patterns @("global_paper_risk_manager_v4_config.py", "global_paper_risk_manager_v3_priority.py") `
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

Start-VisibleComponent `
    -Name "old_short_logger" `
    -Script "$USERDIR\old_short_gate_aware_live_paper_logger.py" `
    -Patterns @("old_short_gate_aware_live_paper_logger.py") `
    -ComponentArgs @(
        "--out_dir", "$RUN\live_blowoff_short_paper_realistic",
        "--global_gate_path", $GATE,
        "--require_global_gate",
        "--sizing_contract", $SIZING_CONTRACT
    )

Start-VisibleComponent `
    -Name "impulse_long_logger" `
    -Script "$USERDIR\impulse_long_gate_aware_live_paper_logger.py" `
    -Patterns @("impulse_long_gate_aware_live_paper_logger.py") `
    -ComponentArgs @(
        "--out_dir", "$RUN\live_impulse_event_long_paper",
        "--coins", "AUTO",
        "--global_gate_path", $GATE,
        "--require_global_gate",
        "--sizing_contract", $SIZING_CONTRACT
    )

Start-VisibleComponent `
    -Name "market_relative_logger" `
    -Script "$USERDIR\market_relative_live_paper_logger.py" `
    -Patterns @("market_relative_live_paper_logger.py") `
    -ComponentArgs @(
        "--out_dir", "$RUN\live_market_relative_extreme_reversion_short_paper",
        "--global_gate_path", $GATE,
        "--require_global_gate",
        "--force_scan_now",
        "--sizing_contract", $SIZING_CONTRACT
    )

Start-VisibleComponent `
    -Name "weak_market_logger" `
    -Script "$USERDIR\weak_market_breakdown_short_live_paper_logger.py" `
    -Patterns @("weak_market_breakdown_short_live_paper_logger.py") `
    -ComponentArgs @(
        "--out_dir", "$RUN\live_weak_market_breakdown_short_paper",
        "--global_gate_path", $GATE,
        "--require_global_gate",
        "--force_scan_now",
        "--sizing_contract", $SIZING_CONTRACT
    )

Start-VisibleComponent `
    -Name "autopilot_v4" `
    -Script "$USERDIR\edge_factory_os_autopilot_loop_v4.py" `
    -Patterns @("edge_factory_os_autopilot_loop_v4.py") `
    -ComponentArgs @(
        "--interval_seconds", "300",
        "--safe_execute"
    )

Write-Host ""
Write-Host "Started visible MASTER_UPPER_SYSTEM launcher." -ForegroundColor Green
Write-Host "Each component should now have its own PowerShell window." -ForegroundColor Yellow
Write-Host "Logs: $LOG_DIR" -ForegroundColor Yellow
