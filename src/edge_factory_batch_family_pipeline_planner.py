#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Plans batch pipeline execution tasks for active strategy families by evaluating their current lifecycle state, research candidate status, and evidence locator outputs. Reads family lifecycle, evidence synthesis, and robustness refresh outputs and writes a prioritized batch pipeline plan for offline validation and research tasks.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List
import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

ACTIVE_FAMILIES = {
    "old_short": {
        "role": "CORE_ENGINE",
        "current_policy": "KEEP_ACTIVE_PAPER_CORE",
        "priority": 100,
    },
    "impulse_long": {
        "role": "HIGH_PRIORITY_DIVERSIFIER",
        "current_policy": "KEEP_ACTIVE_PAPER_DIVERSIFIER",
        "priority": 150,
    },
    "market_relative_short": {
        "role": "CAPPED_REDUCED_SIZE_SHORT",
        "current_policy": "KEEP_CAPPED_REDUCED_SIZE",
        "priority": 70,
    },
    "weak_market_short": {
        "role": "BACKUP_ONLY",
        "current_policy": "KEEP_BACKUP_ONLY",
        "priority": 30,
    },
}

RESEARCH_CANDIDATES = {
    "ret60_reversal_short": {
        "role": "RESEARCH_CANDIDATE",
        "current_policy": "REJECTED_BY_MARKET_REPLAY_UNLESS_REWORKED",
        "priority": 10,
    },
    "rel_extreme_reversion_short": {
        "role": "RESEARCH_CANDIDATE",
        "current_policy": "NEEDS_RULE_EXTRACTION_AND_REPLAY",
        "priority": 50,
    },
    "relative_weakness_snapback_long": {
        "role": "RESEARCH_CANDIDATE",
        "current_policy": "NEEDS_RULE_EXTRACTION_AND_REPLAY",
        "priority": 50,
    },
    "market_panic_rebound_long": {
        "role": "RESEARCH_CANDIDATE",
        "current_policy": "NEEDS_RULE_EXTRACTION_AND_REPLAY",
        "priority": 45,
    },
    "capitulation_reversal_long": {
        "role": "RESEARCH_CANDIDATE",
        "current_policy": "NEEDS_RULE_EXTRACTION_AND_REPLAY",
        "priority": 45,
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

def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows

def latest_ret60_decision() -> Dict[str, Any]:
    d = latest_dir(WORKSPACE / "edge_factory_ret60_market_replay_decision_v4", "ret60_replay_decision_v4_")
    p = d / "ret60_market_replay_decision_v4_state.json" if d else None
    return read_json(p)

def latest_rolling_time_oos() -> Dict[str, Any]:
    d = latest_dir(WORKSPACE / "edge_factory_rolling_retrain_validator", "rolling_time_oos_")
    p = d / "rolling_time_oos_state.json" if d else None
    return read_json(p)

def latest_research_registry() -> list[dict[str, Any]]:
    p = WORKSPACE / "edge_factory_research_result_ledger" / "master_research_result_ledger.jsonl"
    return read_jsonl(p)

def classify_family(name: str, meta: Dict[str, Any], ret60: Dict[str, Any], ledger_rows: list[dict[str, Any]]) -> Dict[str, Any]:
    latest_rows = [r for r in ledger_rows if r.get("candidate") == name or r.get("family") == name or r.get("target") == name]
    latest = latest_rows[-1] if latest_rows else {}

    decision = "UNKNOWN"
    next_action = "INSPECT_MANUALLY"
    blockers = []
    evidence = {}

    if name == "ret60_reversal_short":
        d = ret60.get("decision")
        evidence = {
            "decision": d,
            "trade_count": ret60.get("trade_count"),
            "symbol_count": ret60.get("symbol_count"),
            "net_pnl_sum": ret60.get("net_pnl_sum"),
            "net_bps_mean": ret60.get("net_bps_mean"),
            "profit_factor": ret60.get("profit_factor"),
        }
        if d == "RET60_REJECT_MARKET_REPLAY_NEGATIVE_EXPECTANCY":
            decision = "REJECT_OR_WATCHLIST_DO_NOT_PROMOTE"
            next_action = "ARCHIVE_RET60_AS_FAILED_CANDIDATE_AND_MOVE_TO_NEXT_CANDIDATE"
            blockers = ["negative market replay expectancy", "profit factor below 1", "active/live forbidden"]
        else:
            decision = "RET60_NEEDS_REVIEW"
            next_action = "REVIEW_RET60_DECISION_STATE"

    elif name in ACTIVE_FAMILIES:
        decision = "ACTIVE_FAMILY_NEEDS_BATCH_ROBUSTNESS_REFRESH"
        next_action = "RUN_FAMILY_ROBUSTNESS_AND_DRIFT_REFRESH"
        evidence = {
            "role": meta["role"],
            "current_policy": meta["current_policy"],
            "priority": meta["priority"],
        }

    else:
        decision = "RESEARCH_CANDIDATE_NEEDS_RULE_EXTRACTION_AND_MARKET_REPLAY"
        next_action = "RUN_CANDIDATE_RULE_EXTRACTION_THEN_MARKET_REPLAY"
        evidence = {
            "latest_ledger_status": latest.get("decision") or latest.get("status") or latest.get("latest_result"),
            "role": meta["role"],
            "priority": meta["priority"],
        }

    return {
        "family_key": name,
        "role": meta["role"],
        "current_policy": meta["current_policy"],
        "priority": meta["priority"],
        "pipeline_decision": decision,
        "next_action": next_action,
        "blockers": " | ".join(blockers),
        "evidence": evidence,
        "promotion_allowed": False if "REJECT" in decision or "NEEDS" in decision else None,
        "active_paper_allowed": False if name == "ret60_reversal_short" else None,
        "live_allowed": False,
    }

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_batch_family_pipeline_planner" / f"batch_family_pipeline_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    ret60 = latest_ret60_decision()
    rolling = latest_rolling_time_oos()
    ledger_rows = latest_research_registry()

    all_families = {}
    all_families.update(ACTIVE_FAMILIES)
    all_families.update(RESEARCH_CANDIDATES)

    rows = []
    for name, meta in all_families.items():
        rows.append(classify_family(name, meta, ret60, ledger_rows))

    df = pd.DataFrame(rows).sort_values(["priority", "family_key"], ascending=[False, True])

    ready_active_refresh = df[df["pipeline_decision"] == "ACTIVE_FAMILY_NEEDS_BATCH_ROBUSTNESS_REFRESH"]
    ready_candidate_replay = df[df["pipeline_decision"] == "RESEARCH_CANDIDATE_NEEDS_RULE_EXTRACTION_AND_MARKET_REPLAY"]
    rejected = df[df["pipeline_decision"].str.contains("REJECT", na=False)]

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "planner_status": "BATCH_FAMILY_PIPELINE_PLAN_READY",
        "family_count": int(len(df)),
        "active_refresh_count": int(len(ready_active_refresh)),
        "candidate_replay_count": int(len(ready_candidate_replay)),
        "rejected_or_watchlist_count": int(len(rejected)),
        "ret60_decision": ret60.get("decision"),
        "ret60_net_pnl_sum": ret60.get("net_pnl_sum"),
        "ret60_profit_factor": ret60.get("profit_factor"),
        "next_os_action": "RUN_ACTIVE_FAMILY_ROBUSTNESS_REFRESH_FIRST_THEN_CANDIDATE_BATCH_REPLAY",
        "active_paper_allowed": False,
        "live_allowed": False,
        "hard_rules": [
            "Planner does not start paper/live.",
            "Planner does not promote strategy.",
            "Planner only routes families to next validation step.",
            "Ret60 remains rejected/watchlist unless reworked and retested.",
            "Active families require robustness/drift refresh before any capital change.",
        ],
    }

    write_json(out_dir / "batch_family_pipeline_planner_state.json", state)
    df.to_csv(out_dir / "batch_family_pipeline_plan.csv", index=False)

    print("EDGE FACTORY BATCH FAMILY PIPELINE PLANNER v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"planner_status: {state['planner_status']}")
    print(f"family_count: {state['family_count']}")
    print(f"active_refresh_count: {state['active_refresh_count']}")
    print(f"candidate_replay_count: {state['candidate_replay_count']}")
    print(f"rejected_or_watchlist_count: {state['rejected_or_watchlist_count']}")
    print(f"ret60_decision: {state['ret60_decision']}")
    print(f"ret60_net_pnl_sum: {state['ret60_net_pnl_sum']}")
    print(f"ret60_profit_factor: {state['ret60_profit_factor']}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print()
    print("TOP PLAN")
    print("-" * 100)
    print(df[["family_key", "role", "priority", "pipeline_decision", "next_action", "live_allowed"]].to_string(index=False))
    print()
    print(f"State: {out_dir / 'batch_family_pipeline_planner_state.json'}")
    print(f"Plan : {out_dir / 'batch_family_pipeline_plan.csv'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
