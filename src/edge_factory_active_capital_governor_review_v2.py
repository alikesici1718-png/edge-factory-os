#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

CURRENT_POLICY = {
    "old_short": {
        "current_notional_pct": 0.050,
        "role": "CORE_ENGINE",
        "max_action": "KEEP_NO_INCREASE_UNTIL_DRIFT",
    },
    "impulse_long": {
        "current_notional_pct": 0.050,
        "role": "DIVERSIFIER",
        "max_action": "KEEP_NO_INCREASE_UNTIL_DRIFT",
    },
    "market_relative_short": {
        "current_notional_pct": 0.025,
        "role": "CAPPED_REDUCED_SHORT",
        "max_action": "KEEP_CAPPED_OR_LOWER",
    },
    "weak_market_short": {
        "current_notional_pct": 0.025,
        "role": "BACKUP_ONLY",
        "max_action": "KEEP_BACKUP_ONLY",
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

def load_latest_refresh() -> tuple[Optional[Path], pd.DataFrame]:
    d = latest_dir(WORKSPACE / "edge_factory_active_family_robustness_refresh_v2", "active_family_refresh_v2_")
    p = d / "active_family_robustness_refresh_v2_summary.csv" if d else None
    if p and p.exists():
        return p, pd.read_csv(p)
    return p, pd.DataFrame()

def load_latest_damage() -> tuple[Optional[Path], pd.DataFrame]:
    d = latest_dir(WORKSPACE / "edge_factory_active_family_damage_decomposition_v1", "active_family_damage_v1_")
    p = d / "active_family_damage_decomposition_v1_summary.csv" if d else None
    if p and p.exists():
        return p, pd.read_csv(p)
    return p, pd.DataFrame()

def decision_for_family(fam: str, refresh_row: Dict[str, Any], damage_row: Dict[str, Any]) -> Dict[str, Any]:
    policy = CURRENT_POLICY[fam]

    rolling_status = str(refresh_row.get("rolling_status", "MISSING"))
    refresh_decision = str(refresh_row.get("refresh_decision", ""))
    damage_decision = str(damage_row.get("damage_decision", ""))
    damage_capital_action = str(damage_row.get("capital_action", ""))

    current_pct = policy["current_notional_pct"]
    recommended_pct = current_pct
    recommendation = "KEEP_CURRENT"
    reason = "Default keep-current policy."
    risk_state = "UNKNOWN"

    if fam in {"old_short", "impulse_long"}:
        if rolling_status == "TIME_OOS_PASS":
            recommendation = "KEEP_CURRENT_NO_INCREASE_PENDING_DRIFT"
            recommended_pct = current_pct
            risk_state = "PASSED_BUT_DRIFT_REQUIRED"
            reason = "Family passed time-OOS, but capital increase is blocked until live-vs-backtest drift confirms."
        else:
            recommendation = "FREEZE_AND_REVIEW"
            recommended_pct = current_pct
            risk_state = "MISSING_OR_BAD_REFRESH"
            reason = "Core/diversifier did not have clean pass evidence."

    elif fam == "market_relative_short":
        if "KEEP_CAPPED_REDUCED_SIZE_ONLY" in damage_decision:
            recommendation = "KEEP_CAPPED_2P5_NO_EXPANSION"
            recommended_pct = min(current_pct, 0.025)
            risk_state = "FAILED_TIME_OOS_BUT_AGGREGATE_POSITIVE"
            reason = "Damage decomposition says aggregate positive but unstable; keep capped/reduced size only."
        elif rolling_status == "TIME_OOS_FAIL":
            recommendation = "REDUCE_OR_QUARANTINE_REVIEW"
            recommended_pct = min(current_pct, 0.0125)
            risk_state = "FAILED_TIME_OOS"
            reason = "Failed family without capped justification."
        else:
            recommendation = "KEEP_CAPPED_PENDING_REVIEW"
            recommended_pct = min(current_pct, 0.025)
            risk_state = "CAPPED_PENDING_REVIEW"
            reason = "Capped family remains restricted."

    elif fam == "weak_market_short":
        recommendation = "KEEP_BACKUP_ONLY_NO_EXPANSION"
        recommended_pct = min(current_pct, 0.025)
        risk_state = "INSUFFICIENT_SAMPLE_BACKUP_ONLY"
        reason = "Needs more data; backup-only and no expansion."

    pct_delta = recommended_pct - current_pct

    return {
        "family_key": fam,
        "role": policy["role"],
        "rolling_status": rolling_status,
        "refresh_decision": refresh_decision,
        "damage_decision": damage_decision,
        "damage_capital_action": damage_capital_action,
        "current_notional_pct": current_pct,
        "recommended_notional_pct": recommended_pct,
        "pct_delta": pct_delta,
        "recommendation": recommendation,
        "risk_state": risk_state,
        "reason": reason,
        "capital_change_required": abs(pct_delta) > 1e-12,
        "capital_change_allowed_by_this_module": False,
        "active_paper_change_allowed": False,
        "live_allowed": False,
    }

def row_by_family(df: pd.DataFrame, fam: str) -> Dict[str, Any]:
    if df.empty or "family_key" not in df.columns:
        return {}
    m = df[df["family_key"].astype(str) == fam]
    if m.empty:
        return {}
    return m.iloc[-1].to_dict()

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_active_capital_governor_review_v2" / f"active_capital_governor_v2_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    refresh_path, refresh_df = load_latest_refresh()
    damage_path, damage_df = load_latest_damage()

    rows = []
    for fam in CURRENT_POLICY:
        rows.append(decision_for_family(
            fam,
            row_by_family(refresh_df, fam),
            row_by_family(damage_df, fam),
        ))

    result_df = pd.DataFrame(rows)

    change_required_count = int(result_df["capital_change_required"].sum())
    blocked_change_count = change_required_count

    if change_required_count == 0:
        overall = "CAPITAL_GOVERNOR_REVIEW_NO_CHANGE_RECOMMENDED"
        next_action = "RUN_ACTIVE_FAMILY_DRIFT_MONITOR"
    else:
        overall = "CAPITAL_GOVERNOR_REVIEW_CHANGE_RECOMMENDED_BUT_NOT_APPLIED"
        next_action = "REQUIRE_MANUAL_CAPITAL_CHANGE_GATE_OR_KEEP_CURRENT"

    total_current_pct = float(result_df["current_notional_pct"].sum())
    total_recommended_pct = float(result_df["recommended_notional_pct"].sum())

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "output_dir": str(out_dir),
        "overall_status": overall,
        "refresh_summary_path": str(refresh_path) if refresh_path else None,
        "damage_summary_path": str(damage_path) if damage_path else None,
        "family_count": int(len(result_df)),
        "change_required_count": change_required_count,
        "blocked_change_count": blocked_change_count,
        "total_current_notional_pct": total_current_pct,
        "total_recommended_notional_pct": total_recommended_pct,
        "next_os_action": next_action,
        "capital_change_allowed": False,
        "active_paper_change_allowed": False,
        "live_allowed": False,
        "hard_rules": [
            "This module does not mutate sizing contract.",
            "This module does not change active paper.",
            "This module does not start live.",
            "No capital increase before drift monitor.",
            "Failed/unstable family cannot be expanded.",
            "market_relative_short remains capped/reduced unless a later drift/capital gate says otherwise.",
        ],
    }

    write_json(out_dir / "active_capital_governor_review_v2_state.json", state)
    result_df.to_csv(out_dir / "active_capital_governor_review_v2_summary.csv", index=False)

    ledger_dir = WORKSPACE / "edge_factory_research_result_ledger"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    ledger = ledger_dir / "master_research_result_ledger.jsonl"
    with ledger.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "module": "active_capital_governor_review_v2",
            "overall_status": overall,
            "change_required_count": change_required_count,
            "total_current_notional_pct": total_current_pct,
            "total_recommended_notional_pct": total_recommended_pct,
            "capital_change_allowed": False,
            "active_paper_change_allowed": False,
            "live_allowed": False,
            "state_path": str(out_dir / "active_capital_governor_review_v2_state.json"),
        }, ensure_ascii=False) + "\n")

    print("EDGE FACTORY ACTIVE CAPITAL GOVERNOR REVIEW v2")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"overall_status: {overall}")
    print(f"refresh_summary_path: {refresh_path}")
    print(f"damage_summary_path: {damage_path}")
    print(f"family_count: {len(result_df)}")
    print(f"change_required_count: {change_required_count}")
    print(f"total_current_notional_pct: {total_current_pct}")
    print(f"total_recommended_notional_pct: {total_recommended_pct}")
    print("capital_change_allowed: False")
    print("active_paper_change_allowed: False")
    print("live_allowed: False")
    print()
    print("SUMMARY")
    print("-" * 100)
    print(result_df[[
        "family_key",
        "role",
        "rolling_status",
        "damage_decision",
        "current_notional_pct",
        "recommended_notional_pct",
        "recommendation",
        "risk_state",
        "capital_change_required",
        "live_allowed",
    ]].to_string(index=False))
    print()
    print(f"State  : {out_dir / 'active_capital_governor_review_v2_state.json'}")
    print(f"Summary: {out_dir / 'active_capital_governor_review_v2_summary.csv'}")
    print(f"Ledger : {ledger}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
