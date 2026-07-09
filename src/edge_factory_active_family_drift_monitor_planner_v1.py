#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Plans and schedules drift monitoring checks for active strategy families based on rolling time-OOS validator outputs. Reads the latest rolling OOS summary CSVs and writes a drift monitor plan specifying which families require re-validation and minimum trade thresholds.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
PAPER_DIR = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"

ACTIVE_FAMILIES = ["old_short", "impulse_long", "market_relative_short", "weak_market_short"]

FAMILY_ALIASES = {
    "old_short": ["old_short", "old-short", "old short"],
    "impulse_long": ["impulse_long", "impulse-long", "impulse long"],
    "market_relative_short": ["market_relative_short", "market-relative-short", "market relative short"],
    "weak_market_short": ["weak_market_short", "weak-market-short", "weak market short"],
}

PNL_COLS = ["net_pnl_usdt", "pnl_usdt", "pnl", "net_pnl", "paper_pnl_usdt"]
BPS_COLS = ["net_return_bps_native", "net_bps", "return_bps", "pnl_bps"]
FAMILY_COLS = ["family_key", "family", "strategy", "strategy_key", "candidate_key", "logger_family"]
TIME_COLS = ["exit_time", "entry_time", "event_time", "signal_time", "timestamp", "time", "created_at"]
STATUS_COLS = ["status", "trade_status", "state"]

MIN_TRADES_FOR_DRIFT = {
    "old_short": 50,
    "impulse_long": 25,
    "market_relative_short": 25,
    "weak_market_short": 20,
}

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def latest_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    return sorted(ds, key=lambda x: x.stat().st_mtime, reverse=True)[0] if ds else None

def read_json(path: Optional[Path]) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

def find_col(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    lower = {str(c).lower(): c for c in df.columns}
    for c in candidates:
        if c.lower() in lower:
            return lower[c.lower()]
    for col in df.columns:
        cl = str(col).lower()
        for c in candidates:
            if c.lower() in cl:
                return col
    return None

def family_from_path(path: Path) -> Optional[str]:
    s = str(path).lower()
    for fam, aliases in FAMILY_ALIASES.items():
        if any(a.lower() in s for a in aliases):
            return fam
    return None

def family_from_row_value(v: Any) -> Optional[str]:
    s = str(v).lower()
    for fam, aliases in FAMILY_ALIASES.items():
        if any(a.lower() == s or a.lower() in s for a in aliases):
            return fam
    return None

def load_capital_governor() -> tuple[Optional[Path], pd.DataFrame]:
    d = latest_dir(WORKSPACE / "edge_factory_active_capital_governor_review_v2", "active_capital_governor_v2_")
    p = d / "active_capital_governor_review_v2_summary.csv" if d else None
    if p and p.exists():
        return p, pd.read_csv(p)
    return p, pd.DataFrame()

def load_refresh() -> tuple[Optional[Path], pd.DataFrame]:
    d = latest_dir(WORKSPACE / "edge_factory_active_family_robustness_refresh_v2", "active_family_refresh_v2_")
    p = d / "active_family_robustness_refresh_v2_summary.csv" if d else None
    if p and p.exists():
        return p, pd.read_csv(p)
    return p, pd.DataFrame()

def collect_csvs() -> list[Path]:
    if not PAPER_DIR.exists():
        return []
    files = []
    for p in PAPER_DIR.rglob("*.csv"):
        s = str(p).lower()
        if any(x in s for x in ["closed", "trade", "event", "native", "paper"]):
            files.append(p)
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)

def normalize_trade_file(path: Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

    if df.empty:
        return pd.DataFrame()

    out = df.copy()
    family_col = find_col(out, FAMILY_COLS)
    pnl_col = find_col(out, PNL_COLS)
    bps_col = find_col(out, BPS_COLS)
    time_col = find_col(out, TIME_COLS)
    status_col = find_col(out, STATUS_COLS)

    if family_col:
        out["_family_key"] = out[family_col].apply(family_from_row_value)
    else:
        fam = family_from_path(path)
        out["_family_key"] = fam

    if pnl_col:
        out["_pnl"] = pd.to_numeric(out[pnl_col], errors="coerce")
    else:
        out["_pnl"] = pd.NA

    if bps_col:
        out["_bps"] = pd.to_numeric(out[bps_col], errors="coerce")
    else:
        out["_bps"] = pd.NA

    if time_col:
        out["_time"] = pd.to_datetime(out[time_col], errors="coerce", utc=True)
    else:
        out["_time"] = pd.NaT

    if status_col:
        out["_status"] = out[status_col].astype(str)
    else:
        out["_status"] = "UNKNOWN"

    out["_source_csv"] = str(path)
    out["_source_mtime"] = datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")

    out = out[out["_family_key"].isin(ACTIVE_FAMILIES)].copy()
    if out.empty:
        return out

    # Prefer closed trades, but don't discard rows if status is unknown and pnl exists.
    closed_mask = out["_status"].astype(str).str.upper().str.contains("CLOSED|EXIT|DONE|FILLED", regex=True)
    pnl_exists = out["_pnl"].notna()
    out = out[closed_mask | pnl_exists].copy()

    return out

def row_by_family(df: pd.DataFrame, fam: str) -> Dict[str, Any]:
    if df.empty or "family_key" not in df.columns:
        return {}
    m = df[df["family_key"].astype(str) == fam]
    if m.empty:
        return {}
    return m.iloc[-1].to_dict()

def safe_float(x: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(x):
            return default
        return float(x)
    except Exception:
        return default

def analyze_family(fam: str, trades: pd.DataFrame, refresh_row: Dict[str, Any], capital_row: Dict[str, Any]) -> Dict[str, Any]:
    ft = trades[trades["_family_key"] == fam].copy() if not trades.empty else pd.DataFrame()

    trade_count = int(len(ft))
    min_trades = MIN_TRADES_FOR_DRIFT.get(fam, 30)

    pnl_sum = float(pd.to_numeric(ft["_pnl"], errors="coerce").sum()) if trade_count else 0.0
    pnl_mean = float(pd.to_numeric(ft["_pnl"], errors="coerce").mean()) if trade_count else 0.0
    win_rate = float((pd.to_numeric(ft["_pnl"], errors="coerce") > 0).mean()) if trade_count else 0.0
    bps_mean = float(pd.to_numeric(ft["_bps"], errors="coerce").mean()) if trade_count and ft["_bps"].notna().any() else None

    rolling_status = str(refresh_row.get("rolling_status", "UNKNOWN"))
    recommendation = str(capital_row.get("recommendation", "UNKNOWN"))

    if trade_count == 0:
        drift_status = "DRIFT_BLOCKED_NO_PAPER_TRADES"
        decision = "KEEP_WAITING_FOR_SAMPLE_OR_START_SUPERVISED_PAPER"
        severity = "WAITING"
    elif trade_count < min_trades:
        drift_status = "DRIFT_BLOCKED_INSUFFICIENT_SAMPLE"
        decision = "KEEP_WAITING_FOR_MORE_CLOSED_TRADES"
        severity = "WAITING"
    else:
        if rolling_status == "TIME_OOS_PASS" and pnl_sum < 0:
            drift_status = "DRIFT_WARN_BACKTEST_PASS_PAPER_NEGATIVE"
            decision = "DO_NOT_INCREASE_CAPITAL_REVIEW_FAMILY"
            severity = "WARN"
        elif rolling_status == "TIME_OOS_FAIL":
            drift_status = "DRIFT_RESTRICT_FAILED_FAMILY"
            decision = "KEEP_CAPPED_OR_REVIEW_REDUCTION"
            severity = "RESTRICT"
        elif rolling_status == "NEEDS_MORE_DATA":
            drift_status = "DRIFT_BACKUP_SAMPLE_ONLY"
            decision = "KEEP_BACKUP_ONLY"
            severity = "WAITING"
        else:
            drift_status = "DRIFT_SAMPLE_PRESENT_NO_CRITICAL_ALERT"
            decision = "KEEP_CURRENT_PENDING_CONTINUED_MONITORING"
            severity = "OK"

    first_time = str(ft["_time"].min()) if trade_count and ft["_time"].notna().any() else None
    last_time = str(ft["_time"].max()) if trade_count and ft["_time"].notna().any() else None

    return {
        "family_key": fam,
        "rolling_status": rolling_status,
        "capital_recommendation": recommendation,
        "trade_count": trade_count,
        "min_trades_for_drift": min_trades,
        "pnl_sum": pnl_sum,
        "pnl_mean": pnl_mean,
        "win_rate": win_rate,
        "bps_mean": bps_mean,
        "first_trade_time": first_time,
        "last_trade_time": last_time,
        "drift_status": drift_status,
        "decision": decision,
        "severity": severity,
        "capital_increase_allowed": False,
        "active_paper_change_allowed": False,
        "live_allowed": False,
    }

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_active_family_drift_monitor_planner_v1" / f"active_family_drift_plan_v1_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    capital_path, capital_df = load_capital_governor()
    refresh_path, refresh_df = load_refresh()

    csvs = collect_csvs()
    chunks = []
    file_audit = []

    for p in csvs:
        df = normalize_trade_file(p)
        file_audit.append({
            "path": str(p),
            "rows_detected_for_active_families": int(len(df)),
            "mtime": datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds"),
        })
        if not df.empty:
            chunks.append(df)

    trades = pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()

    rows = []
    for fam in ACTIVE_FAMILIES:
        rows.append(analyze_family(
            fam,
            trades,
            row_by_family(refresh_df, fam),
            row_by_family(capital_df, fam),
        ))

    summary_df = pd.DataFrame(rows)

    blocked_no_sample = int((summary_df["drift_status"] == "DRIFT_BLOCKED_NO_PAPER_TRADES").sum())
    insufficient = int((summary_df["drift_status"] == "DRIFT_BLOCKED_INSUFFICIENT_SAMPLE").sum())
    warn = int(summary_df["drift_status"].astype(str).str.contains("WARN|RESTRICT", regex=True).sum())

    if blocked_no_sample == len(ACTIVE_FAMILIES):
        overall = "ACTIVE_FAMILY_DRIFT_BLOCKED_NO_PAPER_SAMPLE"
        next_action = "START_OR_KEEP_SUPERVISED_PAPER_THEN_RERUN_DRIFT"
    elif insufficient > 0:
        overall = "ACTIVE_FAMILY_DRIFT_WAITING_FOR_MORE_SAMPLE"
        next_action = "KEEP_COLLECTING_PAPER_TRADES"
    elif warn > 0:
        overall = "ACTIVE_FAMILY_DRIFT_WARNINGS_PRESENT"
        next_action = "RUN_FAMILY_REVIEW_FOR_WARNINGS"
    else:
        overall = "ACTIVE_FAMILY_DRIFT_SAMPLE_PRESENT_NO_CRITICAL_ALERT"
        next_action = "CONTINUE_MONITORING_NO_CAPITAL_INCREASE"

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "paper_dir": str(PAPER_DIR),
        "output_dir": str(out_dir),
        "overall_status": overall,
        "capital_summary_path": str(capital_path) if capital_path else None,
        "refresh_summary_path": str(refresh_path) if refresh_path else None,
        "csv_files_scanned": len(csvs),
        "csv_files_with_active_rows": int(sum(1 for x in file_audit if x["rows_detected_for_active_families"] > 0)),
        "total_active_trade_rows_detected": int(len(trades)),
        "blocked_no_sample_count": blocked_no_sample,
        "insufficient_sample_count": insufficient,
        "warning_count": warn,
        "next_os_action": next_action,
        "capital_increase_allowed": False,
        "active_paper_change_allowed": False,
        "live_allowed": False,
        "hard_rules": [
            "This planner does not start paper/live.",
            "This planner does not mutate active config.",
            "This planner does not change capital.",
            "Paper sample is required before drift approval.",
            "No capital increase without sufficient paper sample and separate manual gate.",
        ],
    }

    write_json(out_dir / "active_family_drift_monitor_planner_v1_state.json", state)
    summary_df.to_csv(out_dir / "active_family_drift_monitor_planner_v1_summary.csv", index=False)
    pd.DataFrame(file_audit).to_csv(out_dir / "active_family_drift_monitor_file_audit.csv", index=False)

    ledger_dir = WORKSPACE / "edge_factory_research_result_ledger"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    ledger = ledger_dir / "master_research_result_ledger.jsonl"
    with ledger.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "module": "active_family_drift_monitor_planner_v1",
            "overall_status": overall,
            "total_active_trade_rows_detected": int(len(trades)),
            "capital_increase_allowed": False,
            "active_paper_change_allowed": False,
            "live_allowed": False,
            "state_path": str(out_dir / "active_family_drift_monitor_planner_v1_state.json"),
        }, ensure_ascii=False) + "\n")

    print("EDGE FACTORY ACTIVE FAMILY DRIFT MONITOR PLANNER v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"paper_dir : {PAPER_DIR}")
    print(f"output_dir: {out_dir}")
    print(f"overall_status: {overall}")
    print(f"csv_files_scanned: {len(csvs)}")
    print(f"csv_files_with_active_rows: {state['csv_files_with_active_rows']}")
    print(f"total_active_trade_rows_detected: {len(trades)}")
    print(f"blocked_no_sample_count: {blocked_no_sample}")
    print(f"insufficient_sample_count: {insufficient}")
    print(f"warning_count: {warn}")
    print("capital_increase_allowed: False")
    print("active_paper_change_allowed: False")
    print("live_allowed: False")
    print()
    print("SUMMARY")
    print("-" * 100)
    print(summary_df.to_string(index=False))
    print()
    print(f"State  : {out_dir / 'active_family_drift_monitor_planner_v1_state.json'}")
    print(f"Summary: {out_dir / 'active_family_drift_monitor_planner_v1_summary.csv'}")
    print(f"Audit  : {out_dir / 'active_family_drift_monitor_file_audit.csv'}")
    print(f"Ledger : {ledger}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
