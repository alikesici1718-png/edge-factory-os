from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_month_stability_repair_contract_builder_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

REGIME_FILTERED_EVAL_LATEST = (
    BASE_DIR
    / "edge_factory_os_regime_filtered_candidate_evaluator_v1"
    / "regime_filtered_candidate_evaluator_latest.json"
)

REGIME_FILTERED_RUNNER_LATEST = (
    BASE_DIR
    / "edge_factory_os_regime_filtered_candidate_backtest_runner_v1"
    / "regime_filtered_candidate_backtest_runner_latest.json"
)

CANDIDATE_CONTRACT_LATEST = (
    BASE_DIR
    / "edge_factory_os_candidate_contracts"
    / "regime_filtered_impulse_candidate_contract_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"month_stability_repair_contract_builder_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "month_stability_repair_contract_builder_latest.json"
LATEST_MD = OUT_ROOT / "month_stability_repair_contract_builder_latest.md"

CONTRACT_ROOT = BASE_DIR / "edge_factory_os_research_direction_contracts"
CONTRACT_LATEST = CONTRACT_ROOT / "month_stability_repair_contract_latest.json"


def load_json(path: Path) -> Optional[Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, default=str)


def safe_get(d: Dict[str, Any], path: List[str], default=None):
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def build_contract(
    evaluator: Dict[str, Any],
    runner: Dict[str, Any],
    candidate_contract: Dict[str, Any],
) -> Dict[str, Any]:
    candidate_summary = evaluator.get("candidate_summary") or {}
    all_s = candidate_summary.get("all") or {}
    train_s = candidate_summary.get("train") or {}
    oos_s = candidate_summary.get("oos") or {}

    monthly_total = all_s.get("monthly_total_net_bps") or {}
    bad_months = [
        {"month": k, "total_net_bps": v}
        for k, v in monthly_total.items()
        if isinstance(v, (int, float)) and v < 0
    ]
    good_months = [
        {"month": k, "total_net_bps": v}
        for k, v in monthly_total.items()
        if isinstance(v, (int, float)) and v > 0
    ]

    bad_months.sort(key=lambda x: x["total_net_bps"])
    good_months.sort(key=lambda x: x["total_net_bps"], reverse=True)

    contract_id = f"MONTH_STABILITY_REPAIR_DIAGNOSTIC_CONTRACT_V1_{NOW.strftime('%Y%m%d_%H%M%S')}"

    return {
        "contract_schema": "edge_factory_os_research_contract_v1",
        "contract_id": contract_id,
        "created_at_utc": NOW.isoformat(),

        "research_key": "MONTH_STABILITY_REPAIR_DIAGNOSTIC_V1",
        "research_type": "DIAGNOSTIC_ONLY_NOT_RELEASE",
        "priority": 100,

        "purpose": (
            "Diagnose why the promising regime-filtered impulse candidate fails all-period positive month rate, "
            "and determine whether a non-overfit, pre-outcome month-stability repair contract is justified."
        ),

        "source_candidate": {
            "candidate_key": evaluator.get("candidate_key"),
            "contract_id": evaluator.get("contract_id"),
            "candidate_route_hash": evaluator.get("candidate_route_hash"),
            "evaluator_status": evaluator.get("evaluator_status"),
            "runner_status": runner.get("runner_status"),
            "candidate_promising": evaluator.get("candidate_promising"),
            "full_release_quality_pass": evaluator.get("full_release_quality_pass"),
            "only_month_stability_failed": evaluator.get("only_month_stability_failed"),
            "failed_checks": evaluator.get("failed_checks"),
            "passed_checks": evaluator.get("passed_checks"),
        },

        "candidate_metrics": {
            "all": all_s,
            "train": train_s,
            "oos": oos_s,
            "comparison_to_baseline": evaluator.get("comparison_to_baseline"),
            "bad_months": bad_months,
            "good_months": good_months,
        },

        "universe_input": {
            "panel_path": runner.get("panel_path"),
            "panel_rows": runner.get("panel_rows"),
            "panel_symbol_count": runner.get("panel_symbol_count"),
            "panel_start": runner.get("panel_start"),
            "panel_end": runner.get("panel_end"),
            "must_use_full_1y_okx_swap_panel": True,
            "paper_ledger_only_allowed": False,
            "single_symbol_only_allowed": False,
        },

        "diagnostic_questions": [
            {
                "question_id": "Q1_BAD_MONTH_ATTRIBUTION",
                "question": "Which features explain the candidate's negative months?",
                "target_bad_months": bad_months,
                "required_outputs": [
                    "bad_month_feature_profile",
                    "good_month_feature_profile",
                    "bad_vs_good_feature_differences",
                    "pre_outcome_feature_candidate_list",
                ],
            },
            {
                "question_id": "Q2_MONTH_STABILITY_REPAIR_FILTERS",
                "question": "Can any pre-outcome feature reduce bad months without destroying trade count, OOS quality, or symbol breadth?",
                "required_outputs": [
                    "candidate_repair_filter_table",
                    "monthly_stability_after_filter",
                    "trade_count_after_filter",
                    "train_oos_after_filter",
                    "symbol_concentration_after_filter",
                ],
            },
            {
                "question_id": "Q3_OVERFIT_GUARD",
                "question": "Is the repair just excluding known bad months after seeing PnL?",
                "required_outputs": [
                    "pre_outcome_availability_check",
                    "no_manual_month_blacklist_check",
                    "no_single_month_overfit_check",
                    "train_oos_repair_separation_check",
                ],
            },
            {
                "question_id": "Q4_NEXT_DECISION",
                "question": "Should the repair become a new candidate contract, or should the candidate remain blocked?",
                "required_outputs": [
                    "new_repair_candidate_contract_allowed",
                    "why_or_why_not",
                    "release_gate_preview",
                    "lesson_memory_route_hash_preview",
                ],
            },
        ],

        "allowed_repair_feature_space": {
            "allowed": [
                "cross_sectional_volatility_regime",
                "range_stress_regime",
                "liquidity_regime",
                "market_breadth_regime",
                "market_return_regime",
                "impulse_density_regime",
                "symbol_cluster_predefined_before_pnl",
                "calendar/month feature only if not a manual bad-month blacklist and validated OOS",
            ],
            "explicitly_disallowed": [
                "manual blacklist of negative months",
                "manual blacklist of losing symbols",
                "single-symbol dependency",
                "paper-ledger-only repair",
                "using outcome PnL as input feature",
                "runtime patch from this contract",
                "capital change from this contract",
                "family release from this contract",
            ],
        },

        "pass_fail_policy": {
            "diagnostic_pass_if": [
                "bad and good months are profiled",
                "at least one pre-outcome repair hypothesis is tested",
                "overfit guards are reported",
                "no runtime/capital/family release is recommended",
            ],
            "diagnostic_fail_if": [
                "repair uses manual month blacklist",
                "repair uses post-outcome PnL as feature",
                "repair destroys sample below minimum without explicit block",
                "module recommends live/runtime/capital/family release",
            ],
            "release_pass_possible_in_this_module": False,
        },

        "future_validation_required_if_repair_candidate_is_recommended": [
            "new route hash lesson-memory check",
            "full-universe offline backtest",
            "train/OOS validation",
            "all_positive_month_rate >= 0.55",
            "oos_positive_month_rate >= 0.50",
            "cost/slippage sensitivity",
            "symbol concentration risk",
            "release gate",
        ],

        "expected_next_module": {
            "module_name": "edge_factory_os_month_stability_repair_diagnostic_v1.py",
            "purpose": "Run diagnostic-only repair search for the candidate's positive-month-rate blocker.",
            "execution_allowed_after_contract": True,
            "candidate_generation_allowed_after_contract": False,
            "family_release_allowed_after_contract": False,
        },

        "safety": {
            "read_only": True,
            "offline_only": True,
            "mutate_runtime_allowed": False,
            "launcher_allowed": False,
            "patch_runtime_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "capital_change_allowed": False,
            "family_disable_allowed": False,
            "real_orders_allowed": False,
            "execution_performed": False,
        },
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    CONTRACT_ROOT.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    evaluator = load_json(REGIME_FILTERED_EVAL_LATEST)
    runner = load_json(REGIME_FILTERED_RUNNER_LATEST)
    candidate_contract = load_json(CANDIDATE_CONTRACT_LATEST)

    if not isinstance(evaluator, dict):
        critical.append("regime_filtered_candidate_evaluator_latest_missing")
        evaluator = {}

    if not isinstance(runner, dict):
        critical.append("regime_filtered_candidate_runner_latest_missing")
        runner = {}

    if not isinstance(candidate_contract, dict):
        critical.append("regime_filtered_candidate_contract_latest_missing")
        candidate_contract = {}

    if evaluator.get("evaluator_status") != "REGIME_FILTERED_CANDIDATE_EVALUATOR_PROMISING_MONTH_STABILITY_BLOCKED":
        critical.append(f"unexpected_evaluator_status:{evaluator.get('evaluator_status')}")

    if evaluator.get("candidate_promising") is not True:
        critical.append("candidate_not_promising")

    if evaluator.get("only_month_stability_failed") is not True:
        critical.append("only_month_stability_failed_not_true")

    failed = evaluator.get("failed_checks") or []
    if failed != ["all_positive_month_rate"]:
        critical.append(f"unexpected_failed_checks:{failed}")

    if runner.get("runner_status") != "REGIME_FILTERED_CANDIDATE_BACKTEST_COMPLETE":
        critical.append(f"runner_not_complete:{runner.get('runner_status')}")

    if evaluator.get("candidate_route_hash") != runner.get("candidate_route_hash"):
        critical.append("evaluator_runner_route_hash_mismatch")

    contract = None
    contract_written = False

    if critical:
        builder_status = "MONTH_STABILITY_REPAIR_CONTRACT_BUILDER_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_INPUTS_BEFORE_REPAIR_CONTRACT"
        reason = "; ".join(critical)

    else:
        contract = build_contract(evaluator, runner, candidate_contract)

        contract_path = RUN_DIR / f"{contract['contract_id']}.json"
        dump_json(contract_path, contract)
        dump_json(CONTRACT_LATEST, contract)

        contract["contract_path"] = str(contract_path)
        contract["contract_latest_path"] = str(CONTRACT_LATEST)

        builder_status = "MONTH_STABILITY_REPAIR_CONTRACT_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_MONTH_STABILITY_REPAIR_DIAGNOSTIC_RUNNER"
        reason = f"contract_id={contract['contract_id']}; blocker=all_positive_month_rate"
        contract_written = True

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "builder_status": builder_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "contract": contract,
        "contract_written": contract_written,
        "contract_latest_path": str(CONTRACT_LATEST),

        "sources": {
            "regime_filtered_candidate_evaluator": str(REGIME_FILTERED_EVAL_LATEST),
            "regime_filtered_candidate_runner": str(REGIME_FILTERED_RUNNER_LATEST),
            "candidate_contract": str(CANDIDATE_CONTRACT_LATEST),
        },

        "decision": {
            "repair_contract_ready": contract_written,
            "candidate_generation_recommended_now": False,
            "family_release_recommended": False,
            "promotion_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "next_module": "edge_factory_os_month_stability_repair_diagnostic_v1.py" if contract_written else None,
        },

        "safety": {
            "read_only": True,
            "offline_only": True,
            "mutate_runtime_allowed": False,
            "launcher_allowed": False,
            "patch_runtime_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "capital_change_allowed": False,
            "family_disable_allowed": False,
            "real_orders_allowed": False,
            "execution_performed": False,
        },

        "critical": critical,
        "attention": attention,
        "info": info,
    }

    out_json = RUN_DIR / "month_stability_repair_contract_builder_v1_state.json"
    out_md = RUN_DIR / "month_stability_repair_contract_builder_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS MONTH STABILITY REPAIR CONTRACT BUILDER v1

builder_status: {builder_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

contract_written: {contract_written}  
contract_latest_path: {CONTRACT_LATEST}

## Contract Summary

contract_id: {contract.get("contract_id") if contract else None}  
research_key: {contract.get("research_key") if contract else None}  
source_route_hash: {safe_get(contract or {}, ["source_candidate", "candidate_route_hash"])}  
blocker: all_positive_month_rate  
next_module: {safe_get(contract or {}, ["expected_next_module", "module_name"])}

## Decision

{json.dumps(result["decision"], indent=2, default=str)}

## Safety

read_only: True  
offline_only: True  
mutate_runtime_allowed: False  
launcher_allowed: False  
patch_runtime_allowed: False  
active_paper_allowed: False  
live_allowed: False  
capital_change_allowed: False  
family_disable_allowed: False  
real_orders_allowed: False  
execution_performed: False

critical: {critical}  
attention: {attention}  
info: {info}
"""

    out_md.write_text(md, encoding="utf-8")
    LATEST_MD.write_text(md, encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS MONTH STABILITY REPAIR CONTRACT BUILDER v1")
    print("=" * 100)
    print(f"builder_status: {builder_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("CONTRACT")
    print("-" * 100)
    if contract:
        print(f"contract_id: {contract.get('contract_id')}")
        print(f"research_key: {contract.get('research_key')}")
        print(f"source_route_hash: {safe_get(contract, ['source_candidate', 'candidate_route_hash'])}")
        print(f"contract_latest_path: {CONTRACT_LATEST}")
        print(f"next_module: {safe_get(contract, ['expected_next_module', 'module_name'])}")
    else:
        print(None)
    print()
    print("DECISION")
    print("-" * 100)
    print(json.dumps(result["decision"], indent=2, default=str))
    print()
    print("SAFETY")
    print("-" * 100)
    print("read_only: True")
    print("offline_only: True")
    print("mutate_runtime_allowed: False")
    print("launcher_allowed: False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print("family_disable_allowed: False")
    print("real_orders_allowed: False")
    print("execution_performed: False")
    print()
    print(f"latest_json: {LATEST_JSON}")
    print("=" * 100)

    return 0 if severity != "CRITICAL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
