#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Refreshes robustness validation status for all active strategy families by reading the latest rolling time-OOS summary. Produces a per-family robustness refresh summary CSV and state JSON with policy and capital action recommendations for each family.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

ACTIVE_FAMILIES = {
    "old_short": {
        "role": "CORE_ENGINE",
        "current_policy": "KEEP_ACTIVE_PAPER_CORE",
        "expected_position": "main short engine",
        "priority": 100,
    },
    "impulse_long": {
        "role": "HIGH_PRIORITY_DIVERSIFIER",
        "current_policy": "KEEP_ACTIVE_PAPER_DIVERSIFIER",
        "expected_position": "long diversifier",
        "priority": 150,
    },
    "market_relative_short": {
        "role": "CAPPED_REDUCED_SIZE_SHORT",
        "current_policy": "KEEP_CAPPED_REDUCED_SIZE",
        "expected_position": "reduced-size short sleeve",
        "priority": 70,
    },
    "weak_market_short": {
        "role": "BACKUP_ONLY",
        "current_policy": "KEEP_BACKUP_ONLY",
        "expected_position": "backup-only short sleeve",
        "priority": 30,
    },
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

def read_latest_rolling_summary() -> tuple[Optional[Path], pd.DataFrame]:
    d = latest_dir(WORKSPACE / "edge_factory_rolling_retrain_validator", "rolling_time_oos_")
    if not d:
        return None, pd.DataFrame()

    candidates = [
        d / "rolling_time_oos_summary.csv",
        d / "rolling_time_oos_folds.csv",
    ]

    for p in candidates:
        if p.exists():
            try:
                return p, pd.read_csv(p)
            except Exception:
                pass

    return None, pd.DataFrame()

def normalize_family_col(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    out = df.copy()
    candidates = ["family_key", "family", "candidate", "target", "name"]
    fam_col = None
    for c in candidates:
        if c in out.columns:
            fam_col = c
            break

    if fam_col is None:
        out["family_key"] = "UNKNOWN"
    elif fam_col != "family_key":
        out["family_key"] = out[fam_col].astype(str)

    return out

def row_for_family(df: pd.DataFrame, family: str) -> Dict[str, Any]:
    if df.empty or "family_key" not in df.columns:
        return {}

    m = df[df["family_key"].astype(str) == family]
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

def safe_int(x: Any, default: int = 0) -> int:
    try:
        if pd.isna(x):
            return default
        return int(float(x))
    except Exception:
        return default

def get_any(row: Dict[str, Any], names: list[str], default: Any = None) -> Any:
    for n in names:
        if n in row and not pd.isna(row[n]):
            return row[n]
    return default

def classify_active_family(family: str, meta: Dict[str, Any], row: Dict[str, Any]) -> Dict[str, Any]:
    status = str(get_any(row, ["status", "time_oos_status", "verdict"], "MISSING_ROLLING_OOS"))
    clean = safe_int(get_any(row, ["clean", "clean_rows", "trade_count", "trades"], 0))
    folds = safe_int(get_any(row, ["folds", "valid_folds", "fold_count"], 0))
    symbols = safe_int(get_any(row, ["symbols", "symbol_count", "unique_symbols"], 0))
    test_total = safe_float(get_any(row, ["test_total", "net_pnl_sum", "total_pnl", "pnl_sum"], 0.0))
    test_pf = safe_float(get_any(row, ["test_pf", "profit_factor", "pf"], 0.0))
    worst = safe_float(get_any(row, ["worst", "worst_fold", "worst_test", "min_fold"], 0.0))
    pos_fold = safe_float(get_any(row, ["pos_fold", "positive_fold_rate", "pos_fold_rate"], 0.0))
    month_pos = safe_float(get_any(row, ["month_pos", "positive_month_rate", "month_positive_rate"], 0.0))

    decision = "UNKNOWN_NEEDS_MANUAL_REVIEW"
    action = "INSPECT_ACTIVE_FAMILY_ARTIFACTS"
    risk = "UNKNOWN"
    allow_capital_increase = False
    allow_active_keep = False
    allow_reduction = False

    if status == "TIME_OOS_PASS":
        if family == "old_short":
            decision = "KEEP_CORE_ACTIVE_REFRESH_PASSED"
            action = "KEEP_CORE_BUT_REQUIRE_LIVE_DRIFT_MONITOR"
            risk = "CONTROLLED_CORE_RISK"
            allow_active_keep = True
        elif family == "impulse_long":
            decision = "KEEP_DIVERSIFIER_ACTIVE_REFRESH_PASSED"
            action = "KEEP_DIVERSIFIER_AND_MONITOR_CORRELATION"
            risk = "USEFUL_DIVERSIFIER"
            allow_active_keep = True
        else:
            decision = "KEEP_ACTIVE_REFRESH_PASSED_BUT_NO_EXPANSION"
            action = "KEEP_CURRENT_SIZE_NO_CAPITAL_INCREASE"
            risk = "PASSED_BUT_NOT_CORE"
            allow_active_keep = True

    elif status == "TIME_OOS_FAIL":
        decision = "REDUCE_OR_QUARANTINE_ACTIVE_FAMILY_REFRESH_FAILED"
        action = "DO_NOT_EXPAND_RUN_DAMAGE_DECOMPOSITION"
        risk = "FAILED_TIME_OOS"
        allow_reduction = True

    elif status == "NEEDS_MORE_DATA":
        decision = "KEEP_BACKUP_ONLY_NEEDS_MORE_DATA"
        action = "KEEP_BACKUP_ONLY_COLLECT_MORE_PAPER_SAMPLE"
        risk = "INSUFFICIENT_SAMPLE"
        allow_active_keep = family == "weak_market_short"

    elif status == "MISSING_ROLLING_OOS":
        decision = "BLOCKED_MISSING_ROLLING_OOS_EVIDENCE"
        action = "RUN_ROLLING_RETRAIN_VALIDATOR_FOR_ACTIVE_FAMILY"
        risk = "MISSING_EVIDENCE"

    else:
        decision = f"REVIEW_STATUS_{status}"
        action = "MANUAL_REVIEW_OR_REFRESH_VALIDATOR"
        risk = "UNCLASSIFIED_STATUS"

    # Hard safety overrides.
    live_allowed = False
    promotion_allowed = False
    capital_increase_allowed = False

    return {
        "family_key": family,
        "role": meta["role"],
        "priority": meta["priority"],
        "current_policy": meta["current_policy"],
        "expected_position": meta["expected_position"],
        "rolling_status": status,
        "clean_rows_or_trades": clean,
        "folds": folds,
        "symbols": symbols,
        "test_total": test_total,
        "test_pf": test_pf,
        "worst": worst,
        "pos_fold": pos_fold,
        "month_pos": month_pos,
        "refresh_decision": decision,
        "next_action": action,
        "risk_class": risk,
        "allow_active_keep": allow_active_keep,
        "allow_reduction_review": allow_reduction,
        "capital_increase_allowed": capital_increase_allowed,
        "promotion_allowed": promotion_allowed,
        "active_paper_allowed_by_this_module": False,
        "live_allowed": live_allowed,
    }

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_active_family_robustness_refresh_v1" / f"active_family_refresh_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    rolling_path, rolling_df = read_latest_rolling_summary()
    rolling_df = normalize_family_col(rolling_df)

    rows = []
    for family, meta in ACTIVE_FAMILIES.items():
        rows.append(classify_active_family(family, meta, row_for_family(rolling_df, family)))

    result_df = pd.DataFrame(rows).sort_values(["priority", "family_key"], ascending=[False, True])

    passed = int(result_df["refresh_decision"].astype(str).str.contains("PASSED").sum())
    failed = int(result_df["refresh_decision"].astype(str).str.contains("FAILED").sum())
    needs_more = int(result_df["refresh_decision"].astype(str).str.contains("NEEDS_MORE_DATA").sum())
    missing = int(result_df["refresh_decision"].astype(str).str.contains("MISSING").sum())

    if failed > 0:
        overall = "ACTIVE_FAMILY_REFRESH_WARN_FAILURES_PRESENT"
        next_os_action = "RUN_DAMAGE_DECOMPOSITION_FOR_FAILED_ACTIVE_FAMILIES"
    elif missing > 0:
        overall = "ACTIVE_FAMILY_REFRESH_BLOCKED_MISSING_EVIDENCE"
        next_os_action = "REBUILD_ROLLING_OOS_EVIDENCE"
    else:
        overall = "ACTIVE_FAMILY_REFRESH_COMPLETE_NO_LIVE_APPROVAL"
        next_os_action = "RUN_ACTIVE_FAMILY_DRIFT_AND_CAPITAL_GOVERNOR_REVIEW"

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "output_dir": str(out_dir),
        "overall_status": overall,
        "rolling_summary_path": str(rolling_path) if rolling_path else None,
        "family_count": len(result_df),
        "passed_count": passed,
        "failed_count": failed,
        "needs_more_data_count": needs_more,
        "missing_count": missing,
        "next_os_action": next_os_action,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_increase_allowed": False,
        "hard_rules": [
            "Refresh does not start paper/live.",
            "Refresh does not change capital.",
            "Refresh does not promote families.",
            "Failed active family requires damage decomposition before any keep/retire decision.",
            "Passed active family still requires live-vs-backtest drift monitor before capital changes.",
        ],
    }

    write_json(out_dir / "active_family_robustness_refresh_state.json", state)
    result_df.to_csv(out_dir / "active_family_robustness_refresh_summary.csv", index=False)

    # Append safe ledger row.
    ledger_dir = WORKSPACE / "edge_factory_research_result_ledger"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    ledger = ledger_dir / "master_research_result_ledger.jsonl"
    with ledger.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "module": "active_family_robustness_refresh_v1",
            "overall_status": overall,
            "family_count": len(result_df),
            "passed_count": passed,
            "failed_count": failed,
            "needs_more_data_count": needs_more,
            "active_paper_allowed": False,
            "live_allowed": False,
            "state_path": str(out_dir / "active_family_robustness_refresh_state.json"),
        }, ensure_ascii=False) + "\n")

    print("EDGE FACTORY ACTIVE FAMILY ROBUSTNESS REFRESH v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"overall_status: {overall}")
    print(f"rolling_summary_path: {rolling_path}")
    print(f"family_count: {len(result_df)}")
    print(f"passed_count: {passed}")
    print(f"failed_count: {failed}")
    print(f"needs_more_data_count: {needs_more}")
    print(f"missing_count: {missing}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_increase_allowed: False")
    print()
    print("SUMMARY")
    print("-" * 100)
    print(result_df[[
        "family_key",
        "role",
        "rolling_status",
        "clean_rows_or_trades",
        "folds",
        "symbols",
        "test_total",
        "test_pf",
        "worst",
        "refresh_decision",
        "next_action",
        "live_allowed",
    ]].to_string(index=False))
    print()
    print(f"State  : {out_dir / 'active_family_robustness_refresh_state.json'}")
    print(f"Summary: {out_dir / 'active_family_robustness_refresh_summary.csv'}")
    print(f"Ledger : {ledger}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
