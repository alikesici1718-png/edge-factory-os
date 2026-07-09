#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reviews and formalises the trading rule specification for the rel_extreme_reversion_short shadow candidate by reading the OOS robustness results, exact rule contract, and variant selector state to produce a locked spec JSON. Outputs the spec review JSON and a state file to the edge_factory_rel_extreme_shadow_spec_review_v1 directory with all live/active-paper flags set to False.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
CANDIDATE = "rel_extreme_reversion_short"

def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def latest_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    return sorted(ds, key=lambda x: x.stat().st_mtime, reverse=True)[0] if ds else None

def read_json(path: Optional[Path]) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def write_json(path: Path, obj: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

def read_csv(path: Optional[Path]) -> pd.DataFrame:
    if not path or not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

def pick_cap_policy(cap_df: pd.DataFrame) -> dict[str, Any]:
    if cap_df.empty:
        return {
            "cap_per_signal_hour": 1,
            "source": "fallback",
            "reason": "cap stress table missing; default conservative cap=1",
        }

    rows = []
    for _, r in cap_df.iterrows():
        label = str(r.get("label", ""))
        if not label.startswith("cap_"):
            continue
        try:
            cap = int(float(r.get("cap_per_hour")))
        except Exception:
            continue

        rows.append({
            "cap": cap,
            "label": label,
            "trades": int(r.get("trades", 0)),
            "symbols": int(r.get("symbols", 0)),
            "net_bps_mean": float(r.get("net_bps_mean", 0.0)),
            "profit_factor": float(r.get("profit_factor", 0.0)),
            "win_rate": float(r.get("win_rate", 0.0)),
            "drawdown_proxy_bps": float(r.get("drawdown_proxy_bps", 0.0)),
        })

    if not rows:
        return {
            "cap_per_signal_hour": 1,
            "source": "fallback",
            "reason": "no cap rows parsed; default conservative cap=1",
        }

    # Conservative policy:
    # choose the smallest cap that still has enough breadth and PF.
    viable = [
        r for r in rows
        if r["trades"] >= 2000
        and r["symbols"] >= 100
        and r["profit_factor"] >= 1.50
        and r["win_rate"] >= 0.55
    ]

    if viable:
        chosen = sorted(viable, key=lambda x: x["cap"])[0]
        chosen["source"] = "cap_stress_smallest_viable"
        chosen["reason"] = "smallest cap with enough trades, breadth, PF, and win rate"
        chosen["cap_per_signal_hour"] = chosen["cap"]
        return chosen

    chosen = sorted(rows, key=lambda x: (x["profit_factor"], x["net_bps_mean"]), reverse=True)[0]
    chosen["source"] = "cap_stress_best_pf_fallback"
    chosen["reason"] = "no row met conservative thresholds; chose best PF fallback"
    chosen["cap_per_signal_hour"] = chosen["cap"]
    return chosen

def main():
    out_dir = WORKSPACE / "edge_factory_rel_extreme_shadow_spec_review_v1" / f"rel_extreme_shadow_spec_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_dir = latest_dir(WORKSPACE / "edge_factory_rel_extreme_exact_rule_contract_v1", "rel_extreme_rule_contract_")
    robust_dir = latest_dir(WORKSPACE / "edge_factory_rel_extreme_oos_robustness_v1", "rel_extreme_oos_robust_")
    replay_dir = latest_dir(WORKSPACE / "edge_factory_rel_extreme_real_candle_replay_v1", "rel_extreme_real_replay_")

    contract_path = contract_dir / "rel_extreme_rule_contract.json" if contract_dir else None
    robust_state_path = robust_dir / "rel_extreme_oos_robustness_state.json" if robust_dir else None
    replay_state_path = replay_dir / "rel_extreme_real_candle_replay_state.json" if replay_dir else None

    contract = read_json(contract_path)
    robust = read_json(robust_state_path)
    replay = read_json(replay_state_path)

    cap_df = read_csv(robust_dir / "rel_extreme_signal_cap_stress.csv" if robust_dir else None)
    cost_df = read_csv(robust_dir / "rel_extreme_cost_stress.csv" if robust_dir else None)
    topdep_df = read_csv(robust_dir / "rel_extreme_top_symbol_dependency.csv" if robust_dir else None)
    split_df = read_csv(robust_dir / "rel_extreme_time_splits.csv" if robust_dir else None)

    cap_policy = pick_cap_policy(cap_df)

    gates = []

    def gate(name: str, passed: bool, reason: str):
        gates.append({
            "gate": name,
            "passed": bool(passed),
            "reason": str(reason),
        })

    gate(
        "contract_confirmed",
        contract.get("contract_status") == "REL_EXTREME_RULE_CONTRACT_CONFIRMED_FOR_MARKET_REPLAY",
        contract.get("contract_status"),
    )
    gate(
        "real_replay_passed",
        replay.get("status") == "REL_EXTREME_REAL_REPLAY_PASS_FOR_OOS_REVIEW",
        replay.get("status"),
    )
    gate(
        "robustness_passed",
        robust.get("status") == "REL_EXTREME_ROBUSTNESS_PASS_READY_FOR_SHADOW_SPEC_REVIEW",
        robust.get("status"),
    )
    gate(
        "robustness_gates_all_passed",
        int(robust.get("gates_passed") or 0) == int(robust.get("gates_total") or -1),
        f"{robust.get('gates_passed')}/{robust.get('gates_total')}",
    )
    gate(
        "cap_policy_selected",
        int(cap_policy.get("cap_per_signal_hour") or 0) >= 1,
        cap_policy,
    )
    gate(
        "cap_policy_conservative",
        int(cap_policy.get("cap_per_signal_hour") or 999) <= 2,
        cap_policy,
    )
    gate(
        "not_active_paper",
        robust.get("active_paper_allowed") is False and replay.get("active_paper_allowed") is False,
        "active_paper_allowed false upstream",
    )
    gate(
        "not_live",
        robust.get("live_allowed") is False and replay.get("live_allowed") is False,
        "live_allowed false upstream",
    )

    passed = sum(1 for g in gates if g["passed"])
    total = len(gates)

    spec_ready = passed == total

    shadow_root = WORKSPACE / "paper_run_shadow_rel_extreme_reversion_short"

    shadow_spec = {
        "schema_version": "rel_extreme_shadow_spec_v1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "candidate": CANDIDATE,
        "mode": "SHADOW_REVIEW_ONLY",
        "live_allowed": False,
        "active_paper_allowed": False,
        "shadow_start_allowed_by_this_file": False,
        "manual_approval_required": True,
        "sandbox_root": str(shadow_root),

        "rule": {
            "side": "short",
            "lookback_hours": contract.get("lookback_hours"),
            "coin_return_column": contract.get("coin_return_column"),
            "coin_threshold_bps": contract.get("coin_threshold_bps"),
            "relative_threshold_bps": contract.get("relative_threshold_bps"),
            "hold_hours": contract.get("hold_hours"),
            "entry_timing": "hourly_close_signal_then_shadow_entry_reference",
            "exit_timing": "fixed_hold_hours",
            "cost_bps_reference": 25,
            "market_method_reference": "median",
        },

        "allocator_constraints": {
            "cap_signals_per_hour": int(cap_policy.get("cap_per_signal_hour") or 1),
            "ranking": "highest rel_ret_bps, then highest coin_ret6_bps",
            "shadow_max_open_positions_suggested": 24,
            "active_portfolio_inclusion": False,
            "capital_allocation": 0,
        },

        "evidence": {
            "contract_path": str(contract_path) if contract_path else None,
            "replay_state_path": str(replay_state_path) if replay_state_path else None,
            "robustness_state_path": str(robust_state_path) if robust_state_path else None,
            "base_replay": robust.get("base"),
            "cap_policy": cap_policy,
            "concurrency_uncapped": robust.get("concurrency"),
            "gates_passed": robust.get("gates_passed"),
            "gates_total": robust.get("gates_total"),
        },

        "blockers_before_shadow_start": [
            "shadow logger implementation not built",
            "shadow logger implementation audit not run",
            "shadow preflight not run",
            "manual shadow approval not recorded",
            "must not modify MASTER_UPPER_SYSTEM active portfolio",
            "must not modify sizing contract",
        ],
    }

    status = (
        "REL_EXTREME_SHADOW_SPEC_READY_REVIEW_ONLY"
        if spec_ready
        else "REL_EXTREME_SHADOW_SPEC_BLOCKED"
    )

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "output_dir": str(out_dir),
        "status": status,
        "spec_ready": spec_ready,
        "gates_passed": passed,
        "gates_total": total,
        "gates": gates,
        "shadow_spec": shadow_spec,
        "active_paper_allowed": False,
        "live_allowed": False,
        "next_action": (
            "BUILD_REL_EXTREME_SHADOW_LOGGER_ADAPTER_REVIEW_ONLY"
            if spec_ready
            else "FIX_SHADOW_SPEC_BLOCKERS"
        ),
    }

    spec_path = out_dir / "rel_extreme_shadow_spec.json"
    state_path = out_dir / "rel_extreme_shadow_spec_review_state.json"
    gates_path = out_dir / "rel_extreme_shadow_spec_review_gates.csv"
    report_path = out_dir / "rel_extreme_shadow_spec_review_report.md"

    write_json(spec_path, shadow_spec)
    write_json(state_path, state)
    pd.DataFrame(gates).to_csv(gates_path, index=False)

    report = []
    report.append("# REL EXTREME SHADOW SPEC REVIEW v1")
    report.append("")
    report.append(f"status: `{status}`")
    report.append(f"gates: `{passed}/{total}`")
    report.append("")
    report.append("## Rule")
    report.append(f"- side: `{shadow_spec['rule']['side']}`")
    report.append(f"- lookback_hours: `{shadow_spec['rule']['lookback_hours']}`")
    report.append(f"- coin_threshold_bps: `{shadow_spec['rule']['coin_threshold_bps']}`")
    report.append(f"- relative_threshold_bps: `{shadow_spec['rule']['relative_threshold_bps']}`")
    report.append(f"- hold_hours: `{shadow_spec['rule']['hold_hours']}`")
    report.append("")
    report.append("## Allocator constraint")
    report.append(f"- cap_signals_per_hour: `{shadow_spec['allocator_constraints']['cap_signals_per_hour']}`")
    report.append(f"- shadow_max_open_positions_suggested: `{shadow_spec['allocator_constraints']['shadow_max_open_positions_suggested']}`")
    report.append("")
    report.append("## Safety")
    report.append("- active_paper_allowed: `False`")
    report.append("- live_allowed: `False`")
    report.append("- shadow_start_allowed_by_this_file: `False`")
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")

    ledger_dir = WORKSPACE / "edge_factory_research_result_ledger"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    ledger = ledger_dir / "master_research_result_ledger.jsonl"
    with ledger.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "module": "rel_extreme_shadow_spec_review_v1",
            "candidate": CANDIDATE,
            "status": status,
            "gates_passed": passed,
            "gates_total": total,
            "cap_signals_per_hour": shadow_spec["allocator_constraints"]["cap_signals_per_hour"],
            "active_paper_allowed": False,
            "live_allowed": False,
            "state_path": str(state_path),
            "spec_path": str(spec_path),
        }, ensure_ascii=False) + "\n")

    print("EDGE FACTORY REL EXTREME SHADOW SPEC REVIEW v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"status: {status}")
    print(f"gates: {passed}/{total}")
    print(f"cap_signals_per_hour: {shadow_spec['allocator_constraints']['cap_signals_per_hour']}")
    print(f"shadow_max_open_positions_suggested: {shadow_spec['allocator_constraints']['shadow_max_open_positions_suggested']}")
    print("shadow_start_allowed_by_this_file: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print()
    print("CAP POLICY")
    print("-" * 100)
    print(json.dumps(cap_policy, indent=2, ensure_ascii=False, default=str))
    print()
    print("GATES")
    print("-" * 100)
    print(pd.DataFrame(gates).to_string(index=False))
    print()
    print(f"State : {state_path}")
    print(f"Spec  : {spec_path}")
    print(f"Gates : {gates_path}")
    print(f"Report: {report_path}")
    print(f"Ledger: {ledger}")

if __name__ == "__main__":
    main()
