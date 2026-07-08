# EDGE FACTORY MASTER UPPER SYSTEM STARTER - repaired gate-compatible version
#
# Starts supervised paper windows only.
# REAL ORDERS: NO
# live_allowed: False

$PY = "python"
$USERDIR = "C:\Users\alike"
$BASE = "C:\Users\alike\OneDrive\Desktop\edge_lab_new"
$RUN = "$BASE\paper_run_gate_MASTER_UPPER_SYSTEM"

# IMPORTANT:
# Risk manager writes gate decisions to root run folder.
# Loggers must read the same file.
$GATE = "$RUN\global_gate_decisions.csv"

$FAMILY_CONFIG = "$RUN\family_config.json"
$MAIN_CONFIG = "$RUN\edge_factory_config_MASTER_UPPER_SYSTEM.json"
$SIZING_CONTRACT = "$BASE\edge_factory_position_sizing_contract\position_sizing_contract.json"

$MAX_PER_FAMILY_JSON = '{"old_short":3,"impulse_long":2,"market_relative_short":3,"weak_market_short":2}'
$FAMILY_PRIORITY_JSON = '{"impulse_long":150,"old_short":100,"market_relative_short":70,"weak_market_short":30}'
$MAX_PER_FAMILY_JSON_ARG = "'" + ($MAX_PER_FAMILY_JSON -replace '"', '\"') + "'"
$FAMILY_PRIORITY_JSON_ARG = "'" + ($FAMILY_PRIORITY_JSON -replace '"', '\"') + "'"

if (!(Test-Path $SIZING_CONTRACT)) {
    Write-Host "Missing sizing contract: $SIZING_CONTRACT" -ForegroundColor Red
    Write-Host "Run: python `"C:\Users\alike\edge_factory_position_sizing_contract.py`"" -ForegroundColor Yellow
    exit 1
}

New-Item -ItemType Directory -Force -Path $RUN | Out-Null

$configObj = [ordered]@{
  old_short = "$RUN\live_blowoff_short_paper_realistic"
  impulse_long = "$RUN\live_impulse_event_long_paper"
  market_relative_short = "$RUN\live_market_relative_extreme_reversion_short_paper"
  weak_market_short = "$RUN\live_weak_market_breakdown_short_paper"
}
$config = $configObj | ConvertTo-Json -Depth 4
[System.IO.File]::WriteAllText($FAMILY_CONFIG, $config, [System.Text.UTF8Encoding]::new($false))

$mainObj = [ordered]@{
  run_dir = $RUN
  global_out_dir = $RUN
  family_folders = $configObj
  risk = [ordered]@{
    global_max_positions = 6
    max_short_positions = 5
    max_long_positions = 2
    pending_grace_minutes = 180
    poll_seconds = 10
  }
  max_per_family = [ordered]@{
    old_short = 3
    impulse_long = 2
    market_relative_short = 3
    weak_market_short = 2
  }
  family_priority = [ordered]@{
    old_short = 100
    impulse_long = 150
    market_relative_short = 70
    weak_market_short = 30
  }
  capital_fraction = [ordered]@{
    old_short = 0.05
    impulse_long = 0.05
    market_relative_short = 0.025
    weak_market_short = 0.025
  }
  weak_market_backup_only = $true
  sizing_contract = $SIZING_CONTRACT
  gate_path = $GATE
}
$mainJson = $mainObj | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText($MAIN_CONFIG, $mainJson, [System.Text.UTF8Encoding]::new($false))

function Start-LoggerWindow($Title, $Command) {
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "Write-Host '$Title' -ForegroundColor Cyan; $Command"
    )
}

Write-Host "Starting Edge Factory MASTER_UPPER_SYSTEM paper run..." -ForegroundColor Green
Write-Host "Run folder: $RUN" -ForegroundColor Green
Write-Host "Gate file: $GATE" -ForegroundColor Green
Write-Host "Family config: $FAMILY_CONFIG" -ForegroundColor Green
Write-Host "Sizing contract: $SIZING_CONTRACT" -ForegroundColor Green

Start-LoggerWindow "GLOBAL RISK MANAGER MASTER_UPPER_SYSTEM" "$PY `"$USERDIR\global_paper_risk_manager_v4_config.py`" --family_config `"$FAMILY_CONFIG`" --out_dir `"$RUN`" --global_max_positions 6 --max_short_positions 5 --max_long_positions 2 --max_per_family_json $MAX_PER_FAMILY_JSON_ARG --family_priority_json $FAMILY_PRIORITY_JSON_ARG --weak_market_backup_only --pending_grace_minutes 180 --poll_seconds 10"

Start-Sleep -Seconds 2

Start-LoggerWindow "OLD SHORT MASTER_UPPER_SYSTEM" "$PY `"$USERDIR\old_short_gate_aware_live_paper_logger.py`" --out_dir `"$RUN\live_blowoff_short_paper_realistic`" --global_gate_path `"$GATE`" --require_global_gate --sizing_contract `"$SIZING_CONTRACT`""

Start-LoggerWindow "IMPULSE LONG MASTER_UPPER_SYSTEM" "$PY `"$USERDIR\impulse_long_gate_aware_live_paper_logger.py`" --out_dir `"$RUN\live_impulse_event_long_paper`" --coins AUTO --global_gate_path `"$GATE`" --require_global_gate --sizing_contract `"$SIZING_CONTRACT`""

Start-LoggerWindow "MARKET RELATIVE SHORT MASTER_UPPER_SYSTEM" "$PY `"$USERDIR\market_relative_live_paper_logger.py`" --out_dir `"$RUN\live_market_relative_extreme_reversion_short_paper`" --global_gate_path `"$GATE`" --require_global_gate --force_scan_now --sizing_contract `"$SIZING_CONTRACT`""

Start-LoggerWindow "WEAK MARKET SHORT MASTER_UPPER_SYSTEM BACKUP" "$PY `"$USERDIR\weak_market_breakdown_short_live_paper_logger.py`" --out_dir `"$RUN\live_weak_market_breakdown_short_paper`" --global_gate_path `"$GATE`" --require_global_gate --force_scan_now --sizing_contract `"$SIZING_CONTRACT`""

Write-Host ""
Write-Host "Started MASTER_UPPER_SYSTEM paper windows." -ForegroundColor Green
Write-Host "Health:" -ForegroundColor Yellow
Write-Host "python `"C:\Users\alike\edge_factory_live_health_check_v5.py`" --base_dir `"$RUN`""
Write-Host ""
Write-Host "Performance:" -ForegroundColor Yellow
Write-Host "python `"C:\Users\alike\edge_factory_live_performance_analyzer_v3.py`" --base_dir `"$RUN`""
Write-Host ""
Write-Host "Pending/Open diagnoser:" -ForegroundColor Yellow
Write-Host "python `"C:\Users\alike\edge_factory_pending_to_open_diagnoser_v1.py`""
