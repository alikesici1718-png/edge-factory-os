#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Learning controller for the Edge Factory OS research pipeline that reads candidate validation results, classifies failure modes, and appends structured lessons to a persistent JSONL memory log. Inputs are the latest research result artifacts; output is appended records in edge_factory_research_learning_memory_master.jsonl.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_os_research_learning_controller_v1"
MASTER_MEMORY = OUT_ROOT / "edge_factory_research_learning_memory_master.jsonl"

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def latest_file(root: Path, pattern: str) -> Path | None:
    files = list(root.rglob(pattern))
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def read_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e)}

def append_jsonl(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, default=str) + "\n")

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

def classify_failure(decision: str, metrics: dict[str, Any]) -> dict[str, Any]:
    pf = metrics.get("profit_factor")
    mean_net = metrics.get("mean_net_ret_bps")
    median_net = metrics.get("median_net_ret_bps")
    win_rate = metrics.get("win_rate")
    trade_count = int(metrics.get("closed_selftest_trades") or 0)

    tags = []
    lessons = []
    redesign_requirements = []

    if decision == "FULL_RUN_BLOCKED_NEGATIVE_SELFTEST":
        tags.append("negative_selftest")
        lessons.append("Do not full-run candidates with strongly negative self-test expectancy.")

    if pf is not None and float(pf) < 0.75:
        tags.append("profit_factor_collapse")
        lessons.append("Profit factor below 0.75 is a hard warning before full offline runner.")

    if mean_net is not None and float(mean_net) < -25:
        tags.append("strong_negative_mean")
        lessons.append("Mean net return below -25 bps indicates the rule is structurally wrong or mistimed.")

    if median_net is not None and float(median_net) < 0:
        tags.append("negative_median")
        lessons.append("Negative median means the edge is not just tail-risk; ordinary trades are bad.")

    if win_rate is not None and float(win_rate) < 0.45:
        tags.append("low_win_rate_for_reversion_long")
        lessons.append("Reversion long candidate with low win rate likely catches falling knives.")

    if trade_count >= 300:
        tags.append("high_sample_failure")
        lessons.append("Failure happened on enough self-test trades to treat it as meaningful, not noise.")

    # Domain-specific lesson for this candidate type.
    tags.append("panic_rebound_without_stabilization")
    lessons.append("Market panic + coin crash alone is not a rebound signal; it needs stabilization or reversal confirmation.")

    redesign_requirements.extend([
        "Add stabilization confirmation before long entry.",
        "Require short-term reversal evidence, not only negative return.",
        "Add one or more: coin_ret1_bps > 0, close above recent 3h low, range compression after flush, or market_ret1_bps recovery.",
        "Avoid entering while market_ret6_bps and coin_ret6_bps are both still accelerating downward.",
        "Test 6h/12h holds only after stabilization filter exists.",
    ])

    return {
        "failure_tags": tags,
        "lessons": lessons,
        "redesign_requirements": redesign_requirements,
    }

def main() -> int:
    out_dir = OUT_ROOT / f"research_learning_controller_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    triage_path = latest_file(
        WORKSPACE / "edge_factory_offline_candidate_selftest_triage_v1",
        "offline_candidate_selftest_triage_v1_state.json"
    )
    triage = read_json(triage_path)

    request_path = latest_file(
        WORKSPACE / "edge_factory_contract_to_runner_adapter_v1",
        "offline_runner_request_v1.json"
    )
    request = read_json(request_path)

    contract_path = latest_file(
        WORKSPACE / "edge_factory_candidate_contract_artifact_planner_v1",
        "*_offline_experiment_contract_v1_completed.json"
    )
    contract = read_json(contract_path)

    blockers = []
    if not triage_path or not triage_path.exists():
        blockers.append("TRIAGE_STATE_NOT_FOUND")
    if "__read_error__" in triage:
        blockers.append("TRIAGE_STATE_READ_ERROR")

    candidate_key = triage.get("candidate_key", "UNKNOWN")
    family_key = triage.get("family_key", "UNKNOWN")
    decision = triage.get("decision", "UNKNOWN")
    metrics = triage.get("metrics", {}) if isinstance(triage.get("metrics"), dict) else {}

    classification = classify_failure(decision, metrics)

    if blockers:
        learning_status = "RESEARCH_LEARNING_BLOCKED"
        lifecycle_update = "NO_UPDATE"
        next_action = "FIX_LEARNING_INPUTS"
    elif decision == "FULL_RUN_BLOCKED_NEGATIVE_SELFTEST":
        learning_status = "RESEARCH_LEARNING_RECORDED_NEGATIVE_EDGE"
        lifecycle_update = "ARCHIVE_WAIT_REDESIGN_REQUIRED"
        next_action = "UPDATE_RESEARCH_POLICY_AND_SELECT_NEXT_IDEA"
    else:
        learning_status = "RESEARCH_LEARNING_RECORDED_NON_FATAL"
        lifecycle_update = "KEEP_TESTING"
        next_action = "CONTINUE_RESEARCH_QUEUE"

    entry = {
        "created_at": now_iso(),
        "candidate_key": candidate_key,
        "family_key": family_key,
        "source": "offline_selftest_triage",
        "triage_path": str(triage_path) if triage_path else None,
        "contract_path": str(contract_path) if contract_path else None,
        "request_path": str(request_path) if request_path else None,
        "decision": decision,
        "learning_status": learning_status,
        "lifecycle_update": lifecycle_update,
        "metrics": metrics,
        "failure_tags": classification["failure_tags"],
        "lessons": classification["lessons"],
        "redesign_requirements": classification["redesign_requirements"],
        "promotion_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
    }

    if not blockers:
        append_jsonl(MASTER_MEMORY, entry)

    memory_rows = read_jsonl(MASTER_MEMORY)

    policy = {
        "policy_version": "edge_factory_research_learning_policy_v1",
        "generated_at": now_iso(),
        "purpose": "Use failed offline/self-test evidence to prevent repeated bad research patterns.",
        "negative_pattern_rules": [
            {
                "pattern_key": "panic_rebound_without_stabilization",
                "applies_to": ["panic_rebound_long", "market_panic_rebound_long_v1"],
                "problem": "Market dump + coin dump alone produced negative self-test expectancy.",
                "observed_metrics": metrics,
                "policy": "Do not full-run or promote panic rebound long rules unless stabilization confirmation is added.",
                "required_before_retest": [
                    "coin_ret1_bps or shorter-term reversal feature",
                    "recent low recovery feature",
                    "market stabilization feature",
                    "range/volatility exhaustion feature",
                    "new self-test pass before full run"
                ],
                "hard_block_exact_rule": True
            },
            {
                "pattern_key": "negative_selftest_full_run_block",
                "applies_to": ["all_candidates"],
                "policy": "If self-test PF < 0.75, mean_net < -25 bps, and median_net < 0, block full offline runner and require redesign.",
                "thresholds": {
                    "profit_factor_min_before_full_run": 0.75,
                    "mean_net_ret_bps_min_before_full_run": -25,
                    "median_net_ret_bps_min_before_full_run": 0
                }
            }
        ],
        "candidate_specific_updates": {
            candidate_key: {
                "new_lifecycle_status": lifecycle_update,
                "full_offline_runner_allowed": False,
                "threshold_search_allowed": True,
                "exact_current_rule_blocked": True,
                "reason": classification["lessons"]
            }
        },
        "next_research_selection_policy": {
            "do_not_repeat_failed_pattern": True,
            "prefer_next_idea_if_orthogonal": True,
            "candidate_order_hint": [
                "relative_weakness_snapback_long_v1",
                "post_impulse_drift_long_v1",
                "extreme_blowoff_reversion_short_v1",
                "market_relative_continuation_short_v1"
            ],
            "reason": "market_panic_rebound_long_v1 failed strongly; choose next candidate not requiring same panic rebound assumption."
        },
        "safety": {
            "touch_master": False,
            "run_backtest": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "capital_change_allowed": False,
            "real_orders": False
        }
    }

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "learning_status": learning_status,
        "candidate_key": candidate_key,
        "family_key": family_key,
        "decision": decision,
        "lifecycle_update": lifecycle_update,
        "next_action": next_action,
        "blockers": blockers,
        "entry": entry,
        "memory_count": len(memory_rows),
        "master_memory": str(MASTER_MEMORY),
        "policy_path": "",
        "promotion_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Learning controller only records research memory and policy.",
            "Does not run full backtest.",
            "Does not touch MASTER_UPPER_SYSTEM.",
            "Does not start/stop processes.",
            "Does not place orders.",
            "Does not enable live trading.",
            "Does not change capital."
        ],
    }

    state_path = out_dir / "research_learning_controller_v1_state.json"
    policy_path = out_dir / "research_learning_policy_v1.json"
    memory_csv = out_dir / "research_learning_memory_snapshot.csv"
    report_path = out_dir / "research_learning_controller_v1_report.md"

    policy_path.write_text(json.dumps(policy, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    state["policy_path"] = str(policy_path)
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    if memory_rows:
        flat_rows = []
        for r in memory_rows:
            flat_rows.append({
                "created_at": r.get("created_at"),
                "candidate_key": r.get("candidate_key"),
                "family_key": r.get("family_key"),
                "decision": r.get("decision"),
                "learning_status": r.get("learning_status"),
                "lifecycle_update": r.get("lifecycle_update"),
                "failure_tags": ",".join(r.get("failure_tags", [])),
                "profit_factor": (r.get("metrics") or {}).get("profit_factor"),
                "mean_net_ret_bps": (r.get("metrics") or {}).get("mean_net_ret_bps"),
                "median_net_ret_bps": (r.get("metrics") or {}).get("median_net_ret_bps"),
                "closed_selftest_trades": (r.get("metrics") or {}).get("closed_selftest_trades"),
            })
        pd.DataFrame(flat_rows).to_csv(memory_csv, index=False)
    else:
        pd.DataFrame().to_csv(memory_csv, index=False)

    md = []
    md.append("# Edge Factory OS Research Learning Controller v1")
    md.append("")
    md.append(f"Learning status: `{learning_status}`")
    md.append(f"Candidate: `{candidate_key}`")
    md.append(f"Decision learned: `{decision}`")
    md.append(f"Lifecycle update: `{lifecycle_update}`")
    md.append(f"Next action: `{next_action}`")
    md.append("")
    md.append("## Lessons")
    for x in classification["lessons"]:
        md.append(f"- {x}")
    md.append("")
    md.append("## Redesign requirements")
    for x in classification["redesign_requirements"]:
        md.append(f"- {x}")
    md.append("")
    md.append("## Safety")
    md.append("- promotion_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS RESEARCH LEARNING CONTROLLER v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"learning_status: {learning_status}")
    print(f"candidate : {candidate_key}")
    print(f"family    : {family_key}")
    print(f"decision_learned: {decision}")
    print(f"lifecycle_update: {lifecycle_update}")
    print(f"memory_count: {len(memory_rows)}")
    print(f"next_action: {next_action}")
    print("promotion_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("FAILURE TAGS")
    print("-" * 100)
    for x in classification["failure_tags"]:
        print("-", x)
    print()
    print("LESSONS")
    print("-" * 100)
    for x in classification["lessons"]:
        print("-", x)
    print()
    print("REDESIGN REQUIREMENTS")
    print("-" * 100)
    for x in classification["redesign_requirements"]:
        print("-", x)
    print()
    print(f"State : {state_path}")
    print(f"Policy: {policy_path}")
    print(f"Memory: {MASTER_MEMORY}")
    print(f"CSV   : {memory_csv}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
