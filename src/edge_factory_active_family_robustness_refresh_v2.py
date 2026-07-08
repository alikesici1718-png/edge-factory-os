#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

FAMILY_POLICY = {
    "old_short": {
        "role": "CORE_ENGINE",
        "base_policy": "KEEP_CORE_ENGINE",
        "priority": 100,
        "capital_action": "KEEP_CURRENT_SIZE_NO_INCREASE_UNTIL_DRIFT",
    },
    "impulse_long": {
        "role": "HIGH_PRIORITY_DIVERSIFIER",
        "base_policy": "KEEP_DIVERSIFIER",
        "priority": 150,
        "capital_action": "KEEP_CURRENT_SIZE_NO_INCREASE_UNTIL_DRIFT",
    },
    "market_relative_short": {
        "role": "CAPPED_REDUCED_SIZE_SHORT",
        "base_policy": "KEEP_CAPPED_REDUCED_SIZE_ONLY",
        "priority": 70,
        "capital_action": "NO_EXPANSION_DAMAGE_DECOMPOSITION_REQUIRED",
    },
    "weak_market_short": {
        "role": "BACKUP_ONLY",
        "base_policy": "BACKUP_ONLY",
        "priority": 30,
        "capital_action": "KEEP_BACKUP_ONLY_COLLECT_MORE_DATA",
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

def classify(row: pd.Series) -> Dict[str, Any]:
    fam = str(row.get("family_key", "UNKNOWN"))
    policy = FAMILY_POLICY.get(fam, {
        "role": "UNKNOWN",
        "base_policy": "UNKNOWN",
        "priority": 0,
        "capital_action": "MANUAL_REVIEW",
    })

    status = str(row.get("rolling_status", "UNKNOWN"))
    rows_after_cleaning = safe_int(row.get("rows_after_cleaning"))
    valid_folds = safe_int(row.get("valid_fold_count"))
    pos_fold = safe_float(row.get("positive_test_fold_rate"))
    month_pos = safe_float(row.get("monthly_positive_rate"))
    test_total = safe_float(row.get("test_total_sum"))
    pf = safe_float(row.get("test_pf_aggregate"))
    worst = safe_float(row.get("worst_test_fold"))
    symbols = safe_int(row.get("full_symbol_count"))

    decision = "MANUAL_REVIEW"
    severity = "UNKNOWN"
    next_action = "INSPECT_FAMILY"
    keep_allowed = False
    reduce_review = False
    retire_review = False
    drift_required = True
    damage_decomp_required = False

    if status == "TIME_OOS_PASS":
        keep_allowed = True
        severity = "GREEN_WITH_DRIFT_REQUIRED"

        if fam == "old_short":
            decision = "KEEP_CORE_ENGINE_BUT_REQUIRE_DRIFT_MONITOR"
            next_action = "RUN_LIVE_VS_BACKTEST_DRIFT_FOR_CORE"
        elif fam == "impulse_long":
            decision = "KEEP_DIVERSIFIER_BUT_REQUIRE_DRIFT_MONITOR"
            next_action = "RUN_LIVE_VS_BACKTEST_DRIFT_AND_CORRELATION_CHECK"
        else:
            decision = "KEEP_CURRENT_SIZE_NO_EXPANSION"
            next_action = "RUN_DRIFT_MONITOR_NO_CAPITAL_INCREASE"

    elif status == "TIME_OOS_FAIL":
        keep_allowed = False
        reduce_review = True
        damage_decomp_required = True
        severity = "RED_ORANGE"
        decision = "DO_NOT_EXPAND_FAILED_TIME_OOS_REDUCE_OR_QUARANTINE_REVIEW"
        next_action = "RUN_DAMAGE_DECOMPOSITION_AND_CAPITAL_GOVERNOR_REVIEW"

    elif status == "NEEDS_MORE_DATA":
        keep_allowed = fam == "weak_market_short"
        reduce_review = False
        severity = "YELLOW_INSUFFICIENT_SAMPLE"
        decision = "KEEP_BACKUP_ONLY_NEEDS_MORE_DATA"
        next_action = "KEEP_BACKUP_ONLY_COLLECT_MORE_SAMPLE"

    else:
        severity = "BLOCKED_UNKNOWN_STATUS"
        decision = "BLOCKED_UNCLASSIFIED_EVIDENCE"
        next_action = "REBUILD_OR_INSPECT_EVIDENCE"

    # Conservative overrides.
    capital_increase_allowed = False
    active_paper_change_allowed = False
    live_allowed = False
    promotion_allowed = False

    return {
        "family_key": fam,
        "role": policy["role"],
        "priority": policy["priority"],
        "base_policy": policy["base_policy"],
        "rolling_status": status,
        "rows_after_cleaning": rows_after_cleaning,
        "valid_fold_count": valid_folds,
        "positive_test_fold_rate": pos_fold,
        "monthly_positive_rate": month_pos,
        "test_total_sum": test_total,
        "test_pf_aggregate": pf,
        "worst_test_fold": worst,
        "full_symbol_count": symbols,
        "refresh_decision": decision,
        "severity": severity,
        "next_action": next_action,
        "keep_allowed": keep_allowed,
        "reduce_review_required": reduce_review,
        "retire_review_required": retire_review,
        "damage_decomposition_required": damage_decomp_required,
        "drift_required": drift_required,
        "capital_action": policy["capital_action"],
        "capital_increase_allowed": capital_increase_allowed,
        "active_paper_change_allowed": active_paper_change_allowed,
        "promotion_allowed": promotion_allowed,
        "live_allowed": live_allowed,
        "source_summary_path": row.get("summary_path"),
        "warnings": row.get("warnings"),
        "reasons": row.get("reasons"),
    }

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_active_family_robustness_refresh_v2" / f"active_family_refresh_v2_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    loc_dir = latest_dir(WORKSPACE / "edge_factory_active_family_evidence_locator_v2", "active_family_evidence_locator_v2_")
    loc_summary = loc_dir / "active_family_evidence_locator_v2_summary.csv" if loc_dir else None
    loc_state = loc_dir / "active_family_evidence_locator_v2_state.json" if loc_dir else None

    if not loc_summary or not loc_summary.exists():
        raise SystemExit("active family evidence locator summary not found; run edge_factory_active_family_evidence_locator_v2.py first")

    locator_state = read_json(loc_state)
    df = pd.read_csv(loc_summary)

    rows = [classify(r) for _, r in df.iterrows()]
    result_df = pd.DataFrame(rows).sort_values(["priority", "family_key"], ascending=[False, True])

    pass_count = int((result_df["rolling_status"] == "TIME_OOS_PASS").sum())
    fail_count = int((result_df["rolling_status"] == "TIME_OOS_FAIL").sum())
    needs_more_count = int((result_df["rolling_status"] == "NEEDS_MORE_DATA").sum())
    damage_count = int(result_df["damage_decomposition_required"].sum())
    drift_count = int(result_df["drift_required"].sum())

    if fail_count > 0:
        overall = "ACTIVE_FAMILY_REFRESH_WARN_FAILED_FAMILY_PRESENT"
        next_os_action = "RUN_DAMAGE_DECOMPOSITION_FOR_FAILED_FAMILIES_THEN_DRIFT_MONITOR"
    elif needs_more_count > 0:
        overall = "ACTIVE_FAMILY_REFRESH_PASS_WITH_INSUFFICIENT_BACKUP_SAMPLE"
        next_os_action = "RUN_DRIFT_MONITOR_FOR_PASSED_FAMILIES_KEEP_BACKUP_WAITING"
    else:
        overall = "ACTIVE_FAMILY_REFRESH_PASS_READY_FOR_DRIFT_MONITOR"
        next_os_action = "RUN_ACTIVE_FAMILY_DRIFT_MONITOR"

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "output_dir": str(out_dir),
        "overall_status": overall,
        "locator_state_path": str(loc_state) if loc_state else None,
        "locator_summary_path": str(loc_summary),
        "locator_status": locator_state.get("locator_status"),
        "family_count": int(len(result_df)),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "needs_more_data_count": needs_more_count,
        "damage_decomposition_required_count": damage_count,
        "drift_required_count": drift_count,
        "next_os_action": next_os_action,
        "capital_increase_allowed": False,
        "active_paper_change_allowed": False,
        "live_allowed": False,
        "hard_rules": [
            "This module does not start paper/live.",
            "This module does not change capital.",
            "This module does not promote any family.",
            "Failed family requires damage decomposition before keep/reduce/retire decision.",
            "Passed family still requires live-vs-backtest drift monitor before any capital increase.",
            "Weak-market family remains backup-only until enough sample exists.",
        ],
    }

    write_json(out_dir / "active_family_robustness_refresh_v2_state.json", state)
    result_df.to_csv(out_dir / "active_family_robustness_refresh_v2_summary.csv", index=False)

    ledger_dir = WORKSPACE / "edge_factory_research_result_ledger"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    ledger = ledger_dir / "master_research_result_ledger.jsonl"
    with ledger.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "module": "active_family_robustness_refresh_v2",
            "overall_status": overall,
            "family_count": int(len(result_df)),
            "pass_count": pass_count,
            "fail_count": fail_count,
            "needs_more_data_count": needs_more_count,
            "damage_decomposition_required_count": damage_count,
            "capital_increase_allowed": False,
            "active_paper_change_allowed": False,
            "live_allowed": False,
            "state_path": str(out_dir / "active_family_robustness_refresh_v2_state.json"),
        }, ensure_ascii=False) + "\n")

    print("EDGE FACTORY ACTIVE FAMILY ROBUSTNESS REFRESH v2")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"overall_status: {overall}")
    print(f"locator_summary_path: {loc_summary}")
    print(f"family_count: {len(result_df)}")
    print(f"pass_count: {pass_count}")
    print(f"fail_count: {fail_count}")
    print(f"needs_more_data_count: {needs_more_count}")
    print(f"damage_decomposition_required_count: {damage_count}")
    print(f"drift_required_count: {drift_count}")
    print("capital_increase_allowed: False")
    print("active_paper_change_allowed: False")
    print("live_allowed: False")
    print()
    print("SUMMARY")
    print("-" * 100)
    print(result_df[[
        "family_key",
        "role",
        "rolling_status",
        "rows_after_cleaning",
        "valid_fold_count",
        "full_symbol_count",
        "test_total_sum",
        "test_pf_aggregate",
        "worst_test_fold",
        "refresh_decision",
        "next_action",
        "live_allowed",
    ]].to_string(index=False))
    print()
    print(f"State  : {out_dir / 'active_family_robustness_refresh_v2_state.json'}")
    print(f"Summary: {out_dir / 'active_family_robustness_refresh_v2_summary.csv'}")
    print(f"Ledger : {ledger}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
