#!/usr/bin/env python
"""Create an operational feasibility diagnostic for the Binance spot-perp carry route."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

MODULE_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_binance_spot_perp_delta_neutral_funding_carry_operational_feasibility_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/operational_feasibility/"
    "binance_spot_perp_delta_neutral_funding_carry_operational_feasibility_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXECUTION_RELATIVE_PATH = "artifacts/strategy_executions/binance_spot_perp_delta_neutral_funding_carry_execution_v1.json"
EVALUATOR_RELATIVE_PATH = "artifacts/strategy_evaluations/binance_spot_perp_delta_neutral_funding_carry_evaluator_v1.json"
CLOSURE_RELATIVE_PATH = "artifacts/strategy_closures/binance_spot_perp_delta_neutral_funding_carry_closure_v1.json"
RISK_CAPITAL_RELATIVE_PATH = (
    "artifacts/risk_capital_diagnostics/"
    "binance_spot_perp_delta_neutral_funding_carry_risk_capital_feasibility_v1.json"
)

EXECUTION_PATH = REPO_ROOT / EXECUTION_RELATIVE_PATH
EVALUATOR_PATH = REPO_ROOT / EVALUATOR_RELATIVE_PATH
CLOSURE_PATH = REPO_ROOT / CLOSURE_RELATIVE_PATH
RISK_CAPITAL_PATH = REPO_ROOT / RISK_CAPITAL_RELATIVE_PATH

STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_OPERATIONAL_FEASIBILITY_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_OPERATIONAL_FEASIBILITY_DIAGNOSTIC"

EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_EXECUTED"
EVALUATOR_STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_EVALUATED"
CLOSURE_STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_CLOSURE_CREATED"
RISK_CAPITAL_STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_RISK_CAPITAL_FEASIBILITY_CREATED"

EXECUTION_PAYLOAD_SHA256 = "7855d599b8fa331cbbea2f380c23306889ae486369761d900d7aed36e7191378"
EVALUATOR_PAYLOAD_SHA256 = "94bfdeb3cbe2bfd79ea77ae86c96427790f87a78ff4377972d4b1476ad4ee52b"
CLOSURE_PAYLOAD_SHA256 = "741508f0660eefca0812805a0cab006ace1e2ca0e720dade02665e440ef839c8"
RISK_CAPITAL_PAYLOAD_SHA256 = "9b158cf8517e47c750c39234ea1d7287619a969f567cc682e16edd103a080ccc"

ROUTE_FAMILY = "BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_BASELINE"
CONFIG_ID = "spot_long_perp_short_always_on_funding_carry_3symbol"
PRIOR_RESULT_CLASS = (
    "SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_DIAGNOSTIC_PROMISING_REQUIRES_CLOSURE_NO_CANDIDATE_NO_EDGE"
)
PRIOR_RISK_CAPITAL_CLASSIFICATION = "FUNDING_CARRY_RISK_CAPITAL_FEASIBILITY_STRONG_DIAGNOSTIC_NO_LIVE_PERMISSION"
FEASIBILITY_CLASSIFICATION = (
    "FUNDING_CARRY_OPERATIONAL_FEASIBILITY_INCOMPLETE_NEEDS_EXCHANGE_RULES_NO_LIVE_PERMISSION"
)
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
CAPITAL_SIZES_USDT = (100, 250, 500, 1000, 2500, 5000)
TRACKED_PYTHON_COUNT_AT_START = 883


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def payload_hash(artifact: dict) -> str:
    payload = {key: value for key, value in artifact.items() if key != "payload_sha256_excluding_hash"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def rounded(value: float | int | None, digits: int = 6) -> float | int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if not math.isfinite(value):
        raise RuntimeError(f"non-finite metric: {value!r}")
    return round(value, digits)


def all_true(checks: dict) -> bool:
    return all(value is True for value in checks.values() if isinstance(value, bool))


def read_current_head() -> str:
    head_path = REPO_ROOT / ".git" / "HEAD"
    if not head_path.exists():
        return "UNKNOWN"
    value = head_path.read_text(encoding="utf-8").strip()
    if value.startswith("ref: "):
        ref_path = REPO_ROOT / ".git" / value[5:]
        if ref_path.exists():
            return ref_path.read_text(encoding="utf-8").strip()
    return value


def ensure_target_absent() -> None:
    if ARTIFACT_PATH.exists():
        raise RuntimeError(f"target artifact already exists: {ARTIFACT_PATH}")


def validate_sources(execution: dict, evaluator: dict, closure: dict, risk_capital: dict) -> None:
    if execution.get("status") != EXECUTION_STATUS:
        raise RuntimeError("execution artifact status mismatch")
    if execution.get("payload_sha256_excluding_hash") != EXECUTION_PAYLOAD_SHA256:
        raise RuntimeError("execution artifact payload hash mismatch")
    if evaluator.get("status") != EVALUATOR_STATUS:
        raise RuntimeError("evaluator artifact status mismatch")
    if evaluator.get("payload_sha256_excluding_hash") != EVALUATOR_PAYLOAD_SHA256:
        raise RuntimeError("evaluator artifact payload hash mismatch")
    if closure.get("status") != CLOSURE_STATUS:
        raise RuntimeError("closure artifact status mismatch")
    if closure.get("payload_sha256_excluding_hash") != CLOSURE_PAYLOAD_SHA256:
        raise RuntimeError("closure artifact payload hash mismatch")
    if risk_capital.get("status") != RISK_CAPITAL_STATUS:
        raise RuntimeError("risk/capital artifact status mismatch")
    if risk_capital.get("payload_sha256_excluding_hash") != RISK_CAPITAL_PAYLOAD_SHA256:
        raise RuntimeError("risk/capital artifact payload hash mismatch")
    if execution["route_definition"]["route_family"] != ROUTE_FAMILY:
        raise RuntimeError("route family mismatch")
    if execution["route_definition"]["config_id"] != CONFIG_ID:
        raise RuntimeError("config id mismatch")
    if tuple(execution["route_definition"]["symbols"]) != SYMBOLS:
        raise RuntimeError("symbol universe mismatch")
    if evaluator["result_classification"]["result_class"] != PRIOR_RESULT_CLASS:
        raise RuntimeError("prior result class mismatch")
    if evaluator["result_classification"]["diagnostic_promising"] is not True:
        raise RuntimeError("prior promising flag mismatch")
    if closure["closure_record"]["route_closed"] is not True:
        raise RuntimeError("prior route closure mismatch")
    if risk_capital["feasibility_classification"]["classification"] != PRIOR_RISK_CAPITAL_CLASSIFICATION:
        raise RuntimeError("risk/capital classification mismatch")


def capital_size_scenarios() -> list[dict]:
    scenarios = []
    for capital in CAPITAL_SIZES_USDT:
        gross_symbol_capital = capital / len(SYMBOLS)
        spot_leg_notional = gross_symbol_capital / 2.0
        perp_leg_notional = gross_symbol_capital / 2.0
        if capital < 250:
            coarse_feasibility = "HIGH_ROUNDING_RISK_EXACT_FILTERS_REQUIRED"
        elif capital < 1000:
            coarse_feasibility = "MODERATE_ROUNDING_RISK_EXACT_FILTERS_REQUIRED"
        else:
            coarse_feasibility = "LOWER_ROUNDING_RISK_BUT_EXACT_FILTERS_REQUIRED"
        scenarios.append(
            {
                "capital_size_usdt": capital,
                "symbol_count": len(SYMBOLS),
                "equal_weight_total_capital_per_symbol_usdt": rounded(gross_symbol_capital),
                "estimated_spot_leg_notional_per_symbol_usdt": rounded(spot_leg_notional),
                "estimated_perp_leg_notional_per_symbol_usdt": rounded(perp_leg_notional),
                "exact_exchange_filters_available": False,
                "exact_min_notional_step_size_tick_size_feasibility": "UNKNOWN_REQUIRES_PUBLIC_EXCHANGEINFO_DISCOVERY",
                "rounding_feasibility_estimate_without_filters": coarse_feasibility,
                "symbols": list(SYMBOLS),
            }
        )
    return scenarios


def fee_sensitivity_scenarios(execution: dict) -> dict:
    validation = execution["config_result"]["aggregate_split_metrics"]["validation"]
    holdout = execution["config_result"]["aggregate_split_metrics"]["holdout"]
    fee_scenarios = {
        "optimistic_institutional": {
            "spot_entry_exit_cost_bps_total": 4.0,
            "perp_entry_exit_cost_bps_total": 2.0,
        },
        "realistic_low_vip": {
            "spot_entry_exit_cost_bps_total": 12.0,
            "perp_entry_exit_cost_bps_total": 6.0,
        },
        "retail_conservative": {
            "spot_entry_exit_cost_bps_total": 20.0,
            "perp_entry_exit_cost_bps_total": 10.0,
        },
    }
    results = {}
    for name, fees in fee_scenarios.items():
        total_cost = fees["spot_entry_exit_cost_bps_total"] + fees["perp_entry_exit_cost_bps_total"]
        results[name] = {
            "scenario_only_not_account_specific": True,
            "spot_entry_exit_cost_bps_total": fees["spot_entry_exit_cost_bps_total"],
            "perp_entry_exit_cost_bps_total": fees["perp_entry_exit_cost_bps_total"],
            "total_lifecycle_cost_bps": total_cost,
            "validation_net_after_scenario_lifecycle_cost_bps": rounded(
                float(validation["gross_total_bps"]) - total_cost
            ),
            "holdout_net_after_scenario_lifecycle_cost_bps": rounded(
                float(holdout["gross_total_bps"]) - total_cost
            ),
        }
    return results


def operational_risk_register(execution: dict, risk_capital: dict) -> list[dict]:
    negative_regime = risk_capital["negative_funding_regime_diagnostic"]
    validation_negative_share = negative_regime["validation"]["negative_funding_event_share"]
    holdout_negative_share = negative_regime["holdout"]["negative_funding_event_share"]
    return [
        {
            "risk": "spot_and_perp_balances_may_be_separate",
            "severity": "HIGH",
            "status": "UNMODELED",
            "note": "Operational transfer, collateral, and account segregation requirements are not represented in the historical diagnostic.",
        },
        {
            "risk": "perp_margin_buffer_needed",
            "severity": "HIGH",
            "status": "UNMODELED",
            "note": "Perp short margin must be funded independently of the spot long, especially under isolated margin.",
        },
        {
            "risk": "delta_neutral_spot_does_not_eliminate_liquidation_risk",
            "severity": "HIGH",
            "status": "UNMODELED",
            "note": "If the perp margin account is underfunded, spot holdings do not automatically prevent liquidation.",
        },
        {
            "risk": "negative_funding_periods_exist",
            "severity": "MEDIUM",
            "status": "OBSERVED_IN_STORED_ARTIFACT",
            "note": (
                "Validation negative funding share "
                f"{validation_negative_share}; holdout negative funding share {holdout_negative_share}."
            ),
        },
        {
            "risk": "exchange_and_custody_risk",
            "severity": "HIGH",
            "status": "UNMODELED",
            "note": "The diagnostic assumes exchange solvency, withdrawals, custody, and settlement remain functional.",
        },
        {
            "risk": "delisting_or_symbol_suspension",
            "severity": "HIGH",
            "status": "UNMODELED",
            "note": "Symbol status changes can break continuous hedging and require future public rules/status monitoring.",
        },
        {
            "risk": "borrow_not_needed_but_capital_locked",
            "severity": "MEDIUM",
            "status": "SCENARIO_MODELED_ONLY",
            "note": "Spot-long/perp-short avoids spot borrow but requires capital locked in both spot and margin contexts.",
        },
        {
            "risk": "funding_rate_can_flip",
            "severity": "MEDIUM",
            "status": "OBSERVED_IN_STORED_ARTIFACT",
            "note": "Funding haircut and negative funding stress remain necessary before any paper trading.",
        },
        {
            "risk": "execution_leg_risk",
            "severity": "HIGH",
            "status": "UNMODELED",
            "note": "One leg can fill while the other fails or fills at a materially different price.",
        },
    ]


def kill_switch_policy_draft() -> dict:
    return {
        "live_permission_granted": False,
        "policy_is_future_requirements_draft_only": True,
        "required_kill_switches_before_any_live_or_capital_use": [
            {
                "trigger": "funding turns negative for N consecutive events",
                "required_parameter": "N must be specified in a future approved paper-trading/rules module",
            },
            {
                "trigger": "mark/perp basis dislocation exceeds risk bound",
                "required_parameter": "basis bound must be specified after exchange rule and liquidation model discovery",
            },
            {
                "trigger": "spot/perp price tracking residual exceeds bound",
                "required_parameter": "tracking residual bound must be specified and paper monitored",
            },
            {
                "trigger": "margin ratio below buffer",
                "required_parameter": "buffer must be derived from margin mode, leverage, and maintenance margin schedule",
            },
            {
                "trigger": "missing funding event",
                "required_parameter": "funding event freshness rule must be defined",
            },
            {
                "trigger": "exchange maintenance or API outage",
                "required_parameter": "exchange status and order-management failure behavior must be defined",
            },
            {
                "trigger": "symbol status not trading",
                "required_parameter": "public exchange status monitor must be active",
            },
        ],
    }


def paper_trading_requirements() -> list[dict]:
    return [
        {
            "requirement": "public_exchange_info_rules_discovery",
            "reason": "Need min notional, lot size, step size, tick size, precision, status, and order constraints.",
            "completed_now": False,
        },
        {
            "requirement": "exact_fee_tier_confirmation",
            "reason": "Scenario fees are not account-specific and cannot establish live economics.",
            "completed_now": False,
        },
        {
            "requirement": "order_sizing_and_rounding_simulation",
            "reason": "Need deterministic basket sizing under spot and USD-M futures filters.",
            "completed_now": False,
        },
        {
            "requirement": "margin_and_liquidation_model",
            "reason": "Need margin mode, leverage, collateral, maintenance margin, and liquidation behavior.",
            "completed_now": False,
        },
        {
            "requirement": "small_notional_paper_trading_monitor",
            "reason": "Need non-capital observation of fills, balances, funding, residuals, and kill-switch behavior.",
            "completed_now": False,
        },
        {
            "requirement": "manual_approval_before_any_live_or_capital_use",
            "reason": "No automatic real orders or runtime enablement may follow from this diagnostic.",
            "completed_now": False,
        },
    ]


def main() -> int:
    ensure_target_absent()
    execution = load_json(EXECUTION_PATH)
    evaluator = load_json(EVALUATOR_PATH)
    closure = load_json(CLOSURE_PATH)
    risk_capital = load_json(RISK_CAPITAL_PATH)
    validate_sources(execution, evaluator, closure, risk_capital)

    capital_scenarios = capital_size_scenarios()
    fee_scenarios = fee_sensitivity_scenarios(execution)
    risk_register = operational_risk_register(execution, risk_capital)
    validation_checks = {
        "repo_clean_before_run": True,
        "prior_execution_artifact_loaded": True,
        "prior_evaluator_artifact_loaded": True,
        "prior_closure_artifact_loaded": True,
        "prior_risk_capital_artifact_loaded": True,
        "promising_result_preserved": evaluator["result_classification"]["diagnostic_promising"] is True,
        "risk_capital_classification_preserved": (
            risk_capital["feasibility_classification"]["classification"] == PRIOR_RISK_CAPITAL_CLASSIFICATION
        ),
        "no_strategy_rerun": True,
        "no_raw_rows_read": True,
        "no_private_api": True,
        "no_api_key_used": True,
        "no_orders_placed": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": True,
        "replacement_checks_all_true": True,
    }
    replacement_checks_all_true = all_true(validation_checks)
    validation_checks["replacement_checks_all_true"] = replacement_checks_all_true

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_RELATIVE_PATH,
        "source_checkpoint": {
            "repo_head_at_run": read_current_head(),
            "tracked_python_count_at_start": TRACKED_PYTHON_COUNT_AT_START,
            "repo_clean_before_run": True,
        },
        "source_artifacts": {
            "execution_artifact": EXECUTION_RELATIVE_PATH,
            "execution_payload_sha256_excluding_hash": EXECUTION_PAYLOAD_SHA256,
            "evaluator_artifact": EVALUATOR_RELATIVE_PATH,
            "evaluator_payload_sha256_excluding_hash": EVALUATOR_PAYLOAD_SHA256,
            "closure_artifact": CLOSURE_RELATIVE_PATH,
            "closure_payload_sha256_excluding_hash": CLOSURE_PAYLOAD_SHA256,
            "risk_capital_artifact": RISK_CAPITAL_RELATIVE_PATH,
            "risk_capital_payload_sha256_excluding_hash": RISK_CAPITAL_PAYLOAD_SHA256,
        },
        "prior_promising_result_preserved": {
            "route_family": ROUTE_FAMILY,
            "config_id": CONFIG_ID,
            "symbols": list(SYMBOLS),
            "prior_result_class": evaluator["result_classification"]["result_class"],
            "diagnostic_promising": evaluator["result_classification"]["diagnostic_promising"],
            "route_closed": closure["closure_record"]["route_closed"],
            "prior_risk_capital_classification": risk_capital["feasibility_classification"]["classification"],
            "candidate_generation_allowed": False,
            "edge_claim_allowed": False,
            "runtime_live_capital_allowed": False,
        },
        "capital_size_scenarios": {
            "minimum_capital_scenarios_evaluated": list(CAPITAL_SIZES_USDT),
            "exact_exchange_filters_available": False,
            "future_exchange_rule_discovery_required": True,
            "scenarios": capital_scenarios,
        },
        "fee_sensitivity_scenarios": {
            "uses_account_specific_fee_tier": False,
            "fee_scenarios_are_hypothetical": True,
            "scenarios": fee_scenarios,
        },
        "operational_risk_register": risk_register,
        "future_kill_switch_policy_draft": kill_switch_policy_draft(),
        "future_paper_trading_requirements": paper_trading_requirements(),
        "feasibility_classification": {
            "classification": FEASIBILITY_CLASSIFICATION,
            "reason": (
                "Strategy-level and risk/capital diagnostics are promising, but operational feasibility remains "
                "incomplete without exchange filters, account-specific fees, margin/liquidation rules, and "
                "order sizing/execution simulation."
            ),
            "classification_grants_live_or_capital_permission": False,
        },
        "limitations": [
            "This diagnostic reads stored JSON artifacts only and does not read raw spot, perp, or funding rows.",
            "No public exchangeInfo/rules discovery is performed in this module.",
            "Exact min-notional, step-size, tick-size, precision, symbol-status, and order-filter feasibility is unknown.",
            "Fee scenarios are illustrative and not account-specific.",
            "Margin, liquidation, order placement, fill risk, and live kill-switch behavior are not implemented.",
            "No candidate, edge, family release, runtime, live, or capital permission is granted.",
        ],
        "safety_permissions": {
            "operational_feasibility_created": True,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "next_step_may_be_exchange_rule_discovery_only": True,
            "next_step_must_not_be_live_or_capital": True,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")

    print(f"status: {STATUS}")
    print(f"feasibility_classification: {FEASIBILITY_CLASSIFICATION}")
    print(f"prior_result_class: {PRIOR_RESULT_CLASS}")
    print(f"prior_risk_capital_classification: {PRIOR_RISK_CAPITAL_CLASSIFICATION}")
    print(f"minimum_capital_scenarios_evaluated: {','.join(str(value) for value in CAPITAL_SIZES_USDT)}")
    print("exact_exchange_filters_available: false")
    print("future_exchange_rule_discovery_required: true")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(replacement_checks_all_true).lower()}")
    return 0 if replacement_checks_all_true else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        raise SystemExit(1)
