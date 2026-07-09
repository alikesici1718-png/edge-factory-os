#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generates and writes the canonical offline experiment contract schema (version edge_factory_offline_experiment_contract_v1), defining required fields, hard safety rules, and allowed metadata for offline strategy experiments.
Outputs the schema JSON to a timestamped directory under edge_factory_offline_experiment_contract_schema_v1 in the workspace.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_offline_experiment_contract_schema_v1"

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def main() -> int:
    out_dir = OUT_ROOT / f"offline_experiment_contract_schema_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    schema: dict[str, Any] = {
        "schema_version": "edge_factory_offline_experiment_contract_v1",
        "purpose": "Standard contract for offline strategy-family experiments before any shadow/paper/live consideration.",
        "hard_rules": {
            "does_not_touch_MASTER_UPPER_SYSTEM": True,
            "does_not_start_processes": True,
            "does_not_place_orders": True,
            "does_not_enable_live": True,
            "does_not_change_capital": True,
            "offline_only": True
        },
        "required_sections": [
            "identity",
            "hypothesis",
            "data_contract",
            "signal_contract",
            "execution_assumptions",
            "cost_model",
            "validation_plan",
            "promotion_gates",
            "kill_conditions",
            "artifact_outputs"
        ],
        "section_requirements": {
            "identity": {
                "required": ["candidate_key", "family_key", "side", "created_at", "owner"],
                "allowed_side": ["long", "short", "both"]
            },
            "hypothesis": {
                "required": ["plain_english_edge", "expected_regime", "why_it_should_work", "failure_modes"]
            },
            "data_contract": {
                "required": [
                    "universe",
                    "timeframe",
                    "lookback_window",
                    "source_files",
                    "required_columns",
                    "ready_universe_filter",
                    "deduplication_policy"
                ]
            },
            "signal_contract": {
                "required": [
                    "entry_rule",
                    "exit_rule",
                    "hold_time",
                    "cooldown",
                    "max_signals_per_symbol",
                    "max_signals_per_time_bucket",
                    "no_lookahead_statement"
                ]
            },
            "execution_assumptions": {
                "required": [
                    "entry_price_model",
                    "exit_price_model",
                    "slippage_bps",
                    "latency_assumption",
                    "liquidity_filter",
                    "spread_filter"
                ]
            },
            "cost_model": {
                "required": [
                    "fee_bps",
                    "slippage_bps",
                    "total_cost_bps",
                    "funding_handling"
                ]
            },
            "validation_plan": {
                "required": [
                    "in_sample_period",
                    "out_of_sample_period",
                    "walk_forward_folds",
                    "market_replay_required",
                    "symbol_oos_required",
                    "month_stability_required",
                    "parameter_robustness_required"
                ]
            },
            "promotion_gates": {
                "required": [
                    "min_trades",
                    "min_symbols",
                    "min_positive_month_rate",
                    "min_walk_forward_pass_rate",
                    "min_profit_factor",
                    "max_drawdown_proxy",
                    "market_replay_pass_required",
                    "shadow_runtime_required",
                    "shadow_duplicate_guard_required",
                    "manual_approval_required"
                ]
            },
            "kill_conditions": {
                "required": [
                    "negative_oos_expectancy",
                    "failed_market_replay",
                    "duplicate_or_stale_shadow",
                    "insufficient_liquidity",
                    "live_vs_backtest_drift",
                    "unexplained_runtime_errors"
                ]
            },
            "artifact_outputs": {
                "required": [
                    "normalized_trades_csv",
                    "summary_csv",
                    "state_json",
                    "audit_csv",
                    "ledger_entry"
                ]
            }
        }
    }

    policy: dict[str, Any] = {
        "policy_version": "edge_factory_candidate_validation_gate_policy_v1",
        "purpose": "Prevent weak, stale, overfit, or operationally broken candidates from entering active paper.",
        "hard_blocks": [
            {
                "gate": "NO_DIRECT_TO_MASTER",
                "rule": "No candidate can modify MASTER_UPPER_SYSTEM directly."
            },
            {
                "gate": "NO_DIRECT_TO_LIVE",
                "rule": "No live trading, API key, private endpoint, or real order path is allowed."
            },
            {
                "gate": "OFFLINE_OOS_REQUIRED",
                "rule": "Candidate must pass time OOS / walk-forward before shadow."
            },
            {
                "gate": "MARKET_REPLAY_REQUIRED",
                "rule": "Candidate must survive market replay with positive expectancy after realistic costs."
            },
            {
                "gate": "SYMBOL_DISTRIBUTION_REQUIRED",
                "rule": "Candidate cannot rely on one or two symbols only unless explicitly classified as narrow-specialist and capped."
            },
            {
                "gate": "MONTH_STABILITY_REQUIRED",
                "rule": "Candidate must not depend on a single lucky month."
            },
            {
                "gate": "SHADOW_REQUIRED",
                "rule": "Candidate must run in isolated shadow sandbox before active paper."
            },
            {
                "gate": "NO_DUPLICATE_OR_STALE_SHADOW",
                "rule": "Candidate with duplicate/stale shadow signals is ARCHIVE_WAIT, not promote."
            },
            {
                "gate": "MANUAL_APPROVAL_REQUIRED",
                "rule": "Even after automated pass, human approval is required before active paper."
            },
            {
                "gate": "MASTER_SAMPLE_PRIORITY",
                "rule": "While MASTER initial sample is immature, new family execution is blocked."
            }
        ],
        "minimum_thresholds": {
            "offline_min_trades": 300,
            "offline_min_symbols": 20,
            "walk_forward_min_folds": 4,
            "walk_forward_min_positive_fold_rate": 0.60,
            "monthly_positive_rate_min": 0.55,
            "profit_factor_min": 1.10,
            "market_replay_net_bps_mean_min": 0.0,
            "shadow_min_closed_trades_before_review": 20,
            "active_paper_min_closed_trades_before_capital_review": 50
        },
        "lifecycle_statuses": {
            "IDEA": "Unimplemented concept.",
            "OFFLINE_TESTING": "Offline backtest / OOS in progress.",
            "OFFLINE_PASS": "Offline tests pass but not replayed.",
            "REPLAY_PASS": "Market replay passed, can build shadow.",
            "SHADOW_WAIT": "Shadow running or waiting for sample.",
            "ARCHIVE_WAIT": "Blocked but not deleted; may be revisited after fixing blocker.",
            "REJECTED": "Killed due to failed evidence.",
            "ACTIVE_PAPER_CANDIDATE": "Eligible for manual active-paper review.",
            "ACTIVE_PAPER": "Running in supervised paper system.",
            "LIVE_BLOCKED": "Live remains forbidden unless separately approved."
        },
        "current_known_candidates": {
            "rel_extreme_reversion_short": {
                "status": "ARCHIVE_WAIT",
                "reason": [
                    "NO_SHADOW_CLOSED_SAMPLE",
                    "DUPLICATE_OR_STALE_SIGNAL_REPLAY_PATTERN"
                ],
                "promotion_allowed": False,
                "active_paper_allowed": False,
                "live_allowed": False
            }
        }
    }

    template_contract: dict[str, Any] = {
        "schema_version": "edge_factory_offline_experiment_contract_v1",
        "identity": {
            "candidate_key": "example_candidate_key",
            "family_key": "example_family",
            "side": "short",
            "created_at": now_iso(),
            "owner": "Ali"
        },
        "hypothesis": {
            "plain_english_edge": "",
            "expected_regime": "",
            "why_it_should_work": "",
            "failure_modes": []
        },
        "data_contract": {
            "universe": "OKX USDT swaps ready universe",
            "timeframe": "1h candles or specified",
            "lookback_window": "",
            "source_files": [],
            "required_columns": [],
            "ready_universe_filter": True,
            "deduplication_policy": "candidate_key + symbol + signal_time must be unique"
        },
        "signal_contract": {
            "entry_rule": "",
            "exit_rule": "",
            "hold_time": "",
            "cooldown": "",
            "max_signals_per_symbol": None,
            "max_signals_per_time_bucket": None,
            "no_lookahead_statement": "All features must be known at or before signal_time."
        },
        "execution_assumptions": {
            "entry_price_model": "",
            "exit_price_model": "",
            "slippage_bps": None,
            "latency_assumption": "",
            "liquidity_filter": "",
            "spread_filter": ""
        },
        "cost_model": {
            "fee_bps": None,
            "slippage_bps": None,
            "total_cost_bps": None,
            "funding_handling": ""
        },
        "validation_plan": {
            "in_sample_period": "",
            "out_of_sample_period": "",
            "walk_forward_folds": None,
            "market_replay_required": True,
            "symbol_oos_required": True,
            "month_stability_required": True,
            "parameter_robustness_required": True
        },
        "promotion_gates": {
            "min_trades": 300,
            "min_symbols": 20,
            "min_positive_month_rate": 0.55,
            "min_walk_forward_pass_rate": 0.60,
            "min_profit_factor": 1.10,
            "max_drawdown_proxy": None,
            "market_replay_pass_required": True,
            "shadow_runtime_required": True,
            "shadow_duplicate_guard_required": True,
            "manual_approval_required": True
        },
        "kill_conditions": {
            "negative_oos_expectancy": True,
            "failed_market_replay": True,
            "duplicate_or_stale_shadow": True,
            "insufficient_liquidity": True,
            "live_vs_backtest_drift": True,
            "unexplained_runtime_errors": True
        },
        "artifact_outputs": {
            "normalized_trades_csv": "",
            "summary_csv": "",
            "state_json": "",
            "audit_csv": "",
            "ledger_entry": ""
        }
    }

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "status": "OFFLINE_EXPERIMENT_CONTRACT_SCHEMA_READY",
        "schema_path": "",
        "policy_path": "",
        "template_path": "",
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "This module only writes schema/policy/template files.",
            "It does not run experiments.",
            "It does not touch MASTER_UPPER_SYSTEM.",
            "It does not start processes.",
            "It does not place orders.",
            "It does not enable live trading."
        ]
    }

    schema_path = out_dir / "offline_experiment_contract_schema_v1.json"
    policy_path = out_dir / "candidate_validation_gate_policy_v1.json"
    template_path = out_dir / "offline_experiment_contract_template_v1.json"
    state_path = out_dir / "offline_experiment_contract_schema_v1_state.json"
    report_path = out_dir / "offline_experiment_contract_schema_v1_report.md"

    schema_path.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")
    policy_path.write_text(json.dumps(policy, indent=2, ensure_ascii=False), encoding="utf-8")
    template_path.write_text(json.dumps(template_contract, indent=2, ensure_ascii=False), encoding="utf-8")

    state["schema_path"] = str(schema_path)
    state["policy_path"] = str(policy_path)
    state["template_path"] = str(template_path)
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

    md = []
    md.append("# Edge Factory Offline Experiment Contract Schema v1")
    md.append("")
    md.append("Status: `OFFLINE_EXPERIMENT_CONTRACT_SCHEMA_READY`")
    md.append("")
    md.append("## Purpose")
    md.append("Every future candidate must be described, tested, replayed, shadowed, and gated through this standard before any active paper consideration.")
    md.append("")
    md.append("## Hard blocks")
    for x in policy["hard_blocks"]:
        md.append(f"- `{x['gate']}` — {x['rule']}")
    md.append("")
    md.append("## Current candidate state")
    md.append("- `rel_extreme_reversion_short`: `ARCHIVE_WAIT`; no promotion; no active paper; no live.")
    md.append("")
    md.append("## Files")
    md.append(f"- Schema: `{schema_path}`")
    md.append(f"- Policy: `{policy_path}`")
    md.append(f"- Template: `{template_path}`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OFFLINE EXPERIMENT CONTRACT SCHEMA v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print("status    : OFFLINE_EXPERIMENT_CONTRACT_SCHEMA_READY")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("FILES")
    print("-" * 100)
    print(f"Schema  : {schema_path}")
    print(f"Policy  : {policy_path}")
    print(f"Template: {template_path}")
    print(f"State   : {state_path}")
    print(f"Report  : {report_path}")
    print()
    print("CURRENT POLICY")
    print("-" * 100)
    print("rel_extreme_reversion_short = ARCHIVE_WAIT / DO_NOT_PROMOTE")
    print("new active paper family = BLOCKED until MASTER initial sample is mature")
    print("drift review = closed >= 20")
    print("capital review = closed >= 50")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
