#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_os_interface_specs_v1"

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def main() -> int:
    out_dir = OUT_ROOT / f"os_interface_specs_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_to_runner = {
        "spec_version": "edge_factory_contract_to_test_runner_interface_v1",
        "purpose": "Convert a validated offline experiment contract into a safe offline test-run request.",
        "hard_rules": {
            "does_not_touch_MASTER_UPPER_SYSTEM": True,
            "does_not_start_live_or_paper_processes": True,
            "does_not_place_orders": True,
            "does_not_use_api_keys": True,
            "offline_only": True
        },
        "required_input_contract_status": [
            "CONTRACT_VALID_READY_FOR_OFFLINE_TESTING"
        ],
        "blocked_input_contract_status": [
            "CONTRACT_INVALID_CRITICAL",
            "CONTRACT_STRUCTURE_VALID_BUT_INCOMPLETE",
            "TEMPLATE_STRUCTURE_VALID_NOT_A_CANDIDATE"
        ],
        "input_mapping": {
            "candidate_key": "identity.candidate_key",
            "family_key": "identity.family_key",
            "side": "identity.side",
            "universe": "data_contract.universe",
            "timeframe": "data_contract.timeframe",
            "source_files": "data_contract.source_files",
            "required_columns": "data_contract.required_columns",
            "entry_rule": "signal_contract.entry_rule",
            "exit_rule": "signal_contract.exit_rule",
            "hold_time": "signal_contract.hold_time",
            "cooldown": "signal_contract.cooldown",
            "cost_model": "cost_model",
            "validation_plan": "validation_plan",
            "promotion_gates": "promotion_gates"
        },
        "runner_request_schema": {
            "candidate_key": "str",
            "family_key": "str",
            "side": "long|short|both",
            "mode": "offline_backtest|market_replay|walk_forward",
            "universe": "str|list",
            "source_files": "list[str]",
            "required_columns": "list[str]",
            "entry_rule": "serialized_rule",
            "exit_rule": "serialized_rule",
            "hold_time": "str|int",
            "cost_bps": "float",
            "split_plan": "dict",
            "output_dir": "path",
            "no_master_touch": True
        },
        "runner_must_emit": {
            "normalized_trades_csv": "one row per simulated trade",
            "summary_csv": "one row summary with aggregate metrics",
            "folds_csv": "walk-forward fold result rows",
            "symbol_breakdown_csv": "symbol distribution and contribution",
            "month_breakdown_csv": "monthly stability",
            "audit_json": "data coverage, dropped rows, assumptions",
            "result_state_json": "machine-readable validation result"
        },
        "pre_run_blocks": [
            "contract not valid",
            "source files missing",
            "required columns missing",
            "no cost model",
            "lookahead risk not declared",
            "output dir points inside MASTER_UPPER_SYSTEM",
            "mode requests live/paper execution"
        ]
    }

    result_to_lifecycle = {
        "spec_version": "edge_factory_result_to_lifecycle_adapter_v1",
        "purpose": "Convert offline/shadow/active-paper result artifacts into candidate lifecycle decisions.",
        "hard_rules": {
            "does_not_modify_MASTER_UPPER_SYSTEM": True,
            "does_not_promote_without_manual_approval": True,
            "does_not_enable_live": True,
            "does_not_change_capital": True
        },
        "required_result_artifacts": [
            "normalized_trades_csv",
            "summary_csv",
            "folds_csv",
            "symbol_breakdown_csv",
            "month_breakdown_csv",
            "audit_json",
            "result_state_json"
        ],
        "decision_ladder": [
            {
                "from": "IDEA",
                "to": "OFFLINE_TESTING",
                "requires": ["filled_contract_valid"]
            },
            {
                "from": "OFFLINE_TESTING",
                "to": "OFFLINE_PASS",
                "requires": [
                    "min_trades_pass",
                    "min_symbols_pass",
                    "profit_factor_pass",
                    "positive_month_rate_pass",
                    "walk_forward_pass"
                ]
            },
            {
                "from": "OFFLINE_PASS",
                "to": "REPLAY_PASS",
                "requires": [
                    "market_replay_positive_expectancy",
                    "realistic_costs_applied",
                    "drawdown_proxy_acceptable"
                ]
            },
            {
                "from": "REPLAY_PASS",
                "to": "SHADOW_WAIT",
                "requires": [
                    "shadow_adapter_compiles",
                    "shadow_runtime_self_test_pass",
                    "manual_shadow_approval"
                ]
            },
            {
                "from": "SHADOW_WAIT",
                "to": "ACTIVE_PAPER_CANDIDATE",
                "requires": [
                    "shadow_closed_sample_min_20",
                    "no_duplicate_or_stale_shadow",
                    "shadow_expectancy_non_negative",
                    "runtime_errors_zero",
                    "manual_active_paper_approval"
                ]
            }
        ],
        "archive_rules": [
            {
                "status": "ARCHIVE_WAIT",
                "reason": "duplicate_or_stale_shadow",
                "example": "rel_extreme_reversion_short"
            },
            {
                "status": "ARCHIVE_WAIT",
                "reason": "no_closed_shadow_sample"
            },
            {
                "status": "ARCHIVE_WAIT",
                "reason": "insufficient_distribution_or_liquidity"
            }
        ],
        "reject_rules": [
            {
                "status": "REJECTED",
                "reason": "negative_oos_expectancy"
            },
            {
                "status": "REJECTED",
                "reason": "failed_market_replay"
            },
            {
                "status": "REJECTED",
                "reason": "lookahead_detected"
            },
            {
                "status": "REJECTED",
                "reason": "unfixable_runtime_contract_violation"
            }
        ],
        "promotion_output_schema": {
            "candidate_key": "str",
            "previous_status": "str",
            "new_status": "str",
            "decision": "PROMOTE|ARCHIVE_WAIT|REJECT|KEEP_TESTING",
            "reasons": "list[str]",
            "blockers": "list[str]",
            "manual_approval_required": True,
            "active_paper_allowed": False,
            "live_allowed": False,
            "capital_change_allowed": False
        },
        "current_known_decisions": {
            "rel_extreme_reversion_short": {
                "decision": "ARCHIVE_WAIT",
                "reasons": [
                    "NO_SHADOW_CLOSED_SAMPLE",
                    "DUPLICATE_OR_STALE_SIGNAL_REPLAY_PATTERN"
                ],
                "active_paper_allowed": False,
                "live_allowed": False
            }
        }
    }

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "status": "OS_INTERFACE_SPECS_READY",
        "contract_to_runner_spec": "",
        "result_to_lifecycle_spec": "",
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Specs only.",
            "No experiments are run.",
            "MASTER_UPPER_SYSTEM is not touched.",
            "No process is started/stopped.",
            "No candidate is promoted.",
            "No live trading."
        ]
    }

    contract_path = out_dir / "contract_to_test_runner_interface_spec_v1.json"
    lifecycle_path = out_dir / "result_to_lifecycle_adapter_spec_v1.json"
    state_path = out_dir / "os_interface_specs_v1_state.json"
    report_path = out_dir / "os_interface_specs_v1_report.md"

    contract_path.write_text(json.dumps(contract_to_runner, indent=2, ensure_ascii=False), encoding="utf-8")
    lifecycle_path.write_text(json.dumps(result_to_lifecycle, indent=2, ensure_ascii=False), encoding="utf-8")

    state["contract_to_runner_spec"] = str(contract_path)
    state["result_to_lifecycle_spec"] = str(lifecycle_path)
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

    md = []
    md.append("# Edge Factory OS Interface Specs v1")
    md.append("")
    md.append("Status: `OS_INTERFACE_SPECS_READY`")
    md.append("")
    md.append("## Files")
    md.append(f"- Contract → runner: `{contract_path}`")
    md.append(f"- Result → lifecycle: `{lifecycle_path}`")
    md.append("")
    md.append("## Meaning")
    md.append("- A candidate contract can become an offline runner request only after validator pass.")
    md.append("- Offline/shadow results can update lifecycle only through the adapter rules.")
    md.append("- No direct promotion, no direct active paper, no live.")
    md.append("")
    md.append("## Current known decision")
    md.append("- `rel_extreme_reversion_short`: `ARCHIVE_WAIT`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS INTERFACE SPECS v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print("status    : OS_INTERFACE_SPECS_READY")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("FILES")
    print("-" * 100)
    print(f"ContractRunnerSpec : {contract_path}")
    print(f"LifecycleAdapterSpec: {lifecycle_path}")
    print(f"State              : {state_path}")
    print(f"Report             : {report_path}")
    print()
    print("CURRENT DECISION")
    print("-" * 100)
    print("rel_extreme_reversion_short = ARCHIVE_WAIT")
    print("new candidates require valid contract before any offline runner")

if __name__ == "__main__":
    main()
