#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reads self-test output files from previous offline candidate pipeline runs and triages them into pass/warn/fail categories based on validation results and error signals.
Outputs a triage summary JSON to the edge_factory_offline_candidate_selftest_triage_v1 workspace directory.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_offline_candidate_selftest_triage_v1"

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

def main() -> int:
    out_dir = OUT_ROOT / f"selftest_triage_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    selftest_state_path = latest_file(
        WORKSPACE / "edge_factory_offline_runner_selftest_controller_v1",
        "offline_runner_selftest_controller_v1_state.json"
    )
    selftest = read_json(selftest_state_path)

    blockers = []
    if not selftest_state_path or not selftest_state_path.exists():
        blockers.append("SELFTEST_STATE_NOT_FOUND")
    if "__read_error__" in selftest:
        blockers.append("SELFTEST_STATE_READ_ERROR")

    candidate_key = selftest.get("candidate_key", "UNKNOWN")
    family_key = selftest.get("family_key", "UNKNOWN")
    status = selftest.get("selftest_status", "UNKNOWN")
    summary = selftest.get("summary", {}) if isinstance(selftest.get("summary"), dict) else {}

    trade_count = int(summary.get("closed_selftest_trades") or 0)
    signal_count = int(summary.get("signal_count") or 0)
    symbol_count = int(summary.get("trade_symbol_count") or 0)
    win_rate = summary.get("win_rate")
    mean_net = summary.get("mean_net_ret_bps")
    median_net = summary.get("median_net_ret_bps")
    pf = summary.get("profit_factor")

    reasons = []
    decision = "UNKNOWN"
    lifecycle_recommendation = "UNKNOWN"
    full_offline_runner_allowed = False
    threshold_search_allowed = False

    if blockers:
        decision = "TRIAGE_BLOCKED"
        lifecycle_recommendation = "KEEP_WAITING"
        reasons.extend(blockers)

    elif status == "OFFLINE_RUNNER_SELFTEST_NO_SIGNALS":
        decision = "THRESHOLD_REVIEW_REQUIRED_NO_SIGNALS"
        lifecycle_recommendation = "KEEP_TESTING"
        threshold_search_allowed = True
        reasons.append("selftest produced no signals; rule may be too strict")

    elif status not in {"OFFLINE_RUNNER_SELFTEST_PASS", "OFFLINE_RUNNER_SELFTEST_PASS_LOW_SAMPLE"}:
        decision = "TRIAGE_BLOCKED_SELFTEST_NOT_PASS"
        lifecycle_recommendation = "KEEP_WAITING"
        reasons.append(f"selftest status is {status}")

    elif trade_count < 50:
        decision = "FULL_RUN_BLOCKED_LOW_SELFTEST_SAMPLE"
        lifecycle_recommendation = "KEEP_TESTING"
        threshold_search_allowed = True
        reasons.append(f"closed_selftest_trades too low: {trade_count}")

    else:
        pf_val = float(pf) if pf is not None else -999.0
        mean_val = float(mean_net) if mean_net is not None else -999.0
        median_val = float(median_net) if median_net is not None else -999.0
        wr_val = float(win_rate) if win_rate is not None else 0.0

        if pf_val < 0.75 and mean_val < -25 and median_val < 0:
            decision = "FULL_RUN_BLOCKED_NEGATIVE_SELFTEST"
            lifecycle_recommendation = "ARCHIVE_WAIT_OR_THRESHOLD_REDESIGN"
            full_offline_runner_allowed = False
            threshold_search_allowed = True
            reasons.append(f"profit_factor too low: {pf_val}")
            reasons.append(f"mean_net_ret_bps strongly negative: {mean_val}")
            reasons.append(f"median_net_ret_bps negative: {median_val}")
            reasons.append("do not spend full-run compute on this exact rule")
        elif pf_val >= 1.05 and mean_val > 0:
            decision = "FULL_RUN_ALLOWED_PROMISING_SELFTEST"
            lifecycle_recommendation = "RUN_FULL_OFFLINE_BACKTEST"
            full_offline_runner_allowed = True
            threshold_search_allowed = False
            reasons.append("selftest has positive expectancy")
        else:
            decision = "FULL_RUN_DEFER_THRESHOLD_SEARCH_FIRST"
            lifecycle_recommendation = "KEEP_TESTING"
            full_offline_runner_allowed = False
            threshold_search_allowed = True
            reasons.append("selftest is mixed or weak; search thresholds before full run")

    next_action = (
        "RUN_THRESHOLD_AND_HOLD_DIAGNOSTIC"
        if threshold_search_allowed
        else "RUN_FULL_OFFLINE_BACKTEST"
        if full_offline_runner_allowed
        else "FIX_SELFTEST_INPUTS_OR_KEEP_ARCHIVED"
    )

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "candidate_key": candidate_key,
        "family_key": family_key,
        "triage_status": "SELFTEST_TRIAGE_READY",
        "decision": decision,
        "lifecycle_recommendation": lifecycle_recommendation,
        "reasons": reasons,
        "metrics": {
            "selftest_status": status,
            "signal_count": signal_count,
            "closed_selftest_trades": trade_count,
            "trade_symbol_count": symbol_count,
            "win_rate": win_rate,
            "mean_net_ret_bps": mean_net,
            "median_net_ret_bps": median_net,
            "profit_factor": pf,
        },
        "full_offline_runner_allowed": full_offline_runner_allowed,
        "threshold_search_allowed": threshold_search_allowed,
        "next_action": next_action,
        "promotion_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Triage only evaluates self-test evidence.",
            "Does not run full backtest.",
            "Does not touch MASTER_UPPER_SYSTEM.",
            "Does not start/stop processes.",
            "Does not place orders.",
            "Does not enable live trading.",
            "Does not change capital."
        ],
    }

    state_path = out_dir / "offline_candidate_selftest_triage_v1_state.json"
    report_path = out_dir / "offline_candidate_selftest_triage_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    md = []
    md.append("# Edge Factory Offline Candidate Self-Test Triage v1")
    md.append("")
    md.append(f"Candidate: `{candidate_key}`")
    md.append(f"Decision: `{decision}`")
    md.append(f"Lifecycle recommendation: `{lifecycle_recommendation}`")
    md.append(f"Next action: `{next_action}`")
    md.append("")
    md.append("## Metrics")
    md.append("```json")
    md.append(json.dumps(state["metrics"], indent=2, ensure_ascii=False, default=str))
    md.append("```")
    md.append("")
    md.append("## Reasons")
    for r in reasons:
        md.append(f"- {r}")
    md.append("")
    md.append("## Safety")
    md.append("- promotion_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OFFLINE CANDIDATE SELF-TEST TRIAGE v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"candidate : {candidate_key}")
    print(f"family    : {family_key}")
    print(f"decision  : {decision}")
    print(f"lifecycle_recommendation: {lifecycle_recommendation}")
    print(f"next_action: {next_action}")
    print(f"full_offline_runner_allowed: {full_offline_runner_allowed}")
    print(f"threshold_search_allowed: {threshold_search_allowed}")
    print("promotion_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("METRICS")
    print("-" * 100)
    print(json.dumps(state["metrics"], indent=2, ensure_ascii=False, default=str))
    print()
    print("REASONS")
    print("-" * 100)
    for r in reasons:
        print("-", r)
    print()
    print(f"State : {state_path}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
