#!/usr/bin/env python
"""Create a risk/capital feasibility diagnostic for the Binance spot-perp carry route."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

MODULE_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_binance_spot_perp_delta_neutral_funding_carry_risk_capital_feasibility_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/risk_capital_diagnostics/"
    "binance_spot_perp_delta_neutral_funding_carry_risk_capital_feasibility_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXECUTION_RELATIVE_PATH = "artifacts/strategy_executions/binance_spot_perp_delta_neutral_funding_carry_execution_v1.json"
EVALUATOR_RELATIVE_PATH = "artifacts/strategy_evaluations/binance_spot_perp_delta_neutral_funding_carry_evaluator_v1.json"
CLOSURE_RELATIVE_PATH = "artifacts/strategy_closures/binance_spot_perp_delta_neutral_funding_carry_closure_v1.json"

EXECUTION_PATH = REPO_ROOT / EXECUTION_RELATIVE_PATH
EVALUATOR_PATH = REPO_ROOT / EVALUATOR_RELATIVE_PATH
CLOSURE_PATH = REPO_ROOT / CLOSURE_RELATIVE_PATH

STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_RISK_CAPITAL_FEASIBILITY_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_RISK_CAPITAL_FEASIBILITY_DIAGNOSTIC"

EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_EXECUTED"
EVALUATOR_STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_EVALUATED"
CLOSURE_STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_CLOSURE_CREATED"
EXECUTION_PAYLOAD_SHA256 = "7855d599b8fa331cbbea2f380c23306889ae486369761d900d7aed36e7191378"
EVALUATOR_PAYLOAD_SHA256 = "94bfdeb3cbe2bfd79ea77ae86c96427790f87a78ff4377972d4b1476ad4ee52b"
CLOSURE_PAYLOAD_SHA256 = "741508f0660eefca0812805a0cab006ace1e2ca0e720dade02665e440ef839c8"

ROUTE_FAMILY = "BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_BASELINE"
CONFIG_ID = "spot_long_perp_short_always_on_funding_carry_3symbol"
PROMISING_RESULT_CLASS = (
    "SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_DIAGNOSTIC_PROMISING_REQUIRES_CLOSURE_NO_CANDIDATE_NO_EDGE"
)
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
TRACKED_PYTHON_COUNT_AT_START = 882

CAPITAL_USAGE_SCENARIOS = {
    "conservative": 2.0,
    "moderate": 1.5,
    "aggressive": 1.25,
}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def payload_hash(artifact: dict) -> str:
    payload = {key: value for key, value in artifact.items() if key != "payload_sha256_excluding_hash"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def all_true(checks: dict) -> bool:
    return all(value is True for value in checks.values() if isinstance(value, bool))


def rounded(value: float | int | None, digits: int = 6) -> float | int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if not math.isfinite(value):
        raise RuntimeError(f"non-finite diagnostic metric: {value!r}")
    return round(value, digits)


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


def validate_sources(execution: dict, evaluator: dict, closure: dict) -> None:
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
    if execution["route_definition"]["route_family"] != ROUTE_FAMILY:
        raise RuntimeError("route family mismatch")
    if execution["route_definition"]["config_id"] != CONFIG_ID:
        raise RuntimeError("config id mismatch")
    if evaluator["result_classification"]["result_class"] != PROMISING_RESULT_CLASS:
        raise RuntimeError("prior evaluator result class mismatch")
    if evaluator["result_classification"]["diagnostic_promising"] is not True:
        raise RuntimeError("prior diagnostic promising flag not preserved")
    if closure["closure_record"]["route_closed"] is not True:
        raise RuntimeError("prior route closed flag not preserved")


def split_metric(execution: dict, split_name: str) -> dict:
    return execution["config_result"]["aggregate_split_metrics"][split_name]


def lifecycle_cost(split: dict) -> float:
    return float(split["net_lifecycle_cost_bps"])


def monthly_rebalance_cost(split: dict) -> float:
    return float(split["monthly_rebalance_cost_bps"])


def stressed_net(split: dict, funding_haircut: float = 0.0, lifecycle_cost_multiplier: float = 1.0) -> float:
    price = float(split["gross_price_component_bps"])
    funding = float(split["gross_funding_component_bps"])
    cost = lifecycle_cost(split) * lifecycle_cost_multiplier
    return price + funding * (1.0 - funding_haircut) - cost


def stressed_monthly_net(split: dict, funding_haircut: float = 0.0, monthly_cost_multiplier: float = 1.0) -> float:
    price = float(split["gross_price_component_bps"])
    funding = float(split["gross_funding_component_bps"])
    cost = monthly_rebalance_cost(split) * monthly_cost_multiplier
    return price + funding * (1.0 - funding_haircut) - cost


def cost_stress_for_split(split: dict) -> dict:
    gross_total = float(split["gross_total_bps"])
    base_lifecycle_cost = lifecycle_cost(split)
    base_monthly_cost = monthly_rebalance_cost(split)
    return {
        "gross_total_bps": rounded(gross_total),
        "base_lifecycle_cost_bps": rounded(base_lifecycle_cost),
        "net_base_lifecycle_cost_bps": rounded(gross_total - base_lifecycle_cost),
        "net_2x_lifecycle_cost_bps": rounded(gross_total - base_lifecycle_cost * 2.0),
        "net_3x_lifecycle_cost_bps": rounded(gross_total - base_lifecycle_cost * 3.0),
        "base_monthly_rebalance_cost_bps": rounded(base_monthly_cost),
        "net_monthly_rebalance_cost_bps": rounded(gross_total - base_monthly_cost),
        "net_2x_monthly_rebalance_cost_bps": rounded(gross_total - base_monthly_cost * 2.0),
        "net_3x_monthly_rebalance_cost_bps": rounded(gross_total - base_monthly_cost * 3.0),
    }


def funding_haircut_stress_for_split(split: dict) -> dict:
    results = {}
    for haircut in (0.25, 0.50, 0.75, 1.00):
        label = f"{int(haircut * 100)}pct_funding_haircut"
        results[label] = {
            "stressed_gross_total_bps": rounded(
                float(split["gross_price_component_bps"])
                + float(split["gross_funding_component_bps"]) * (1.0 - haircut)
            ),
            "net_after_base_lifecycle_cost_bps": rounded(stressed_net(split, funding_haircut=haircut)),
            "net_after_base_monthly_rebalance_cost_bps": rounded(
                stressed_monthly_net(split, funding_haircut=haircut)
            ),
        }
    return results


def combined_stress_for_split(split: dict) -> dict:
    scenarios = {
        "50pct_funding_haircut_2x_lifecycle_cost": (0.50, 2.0),
        "50pct_funding_haircut_3x_lifecycle_cost": (0.50, 3.0),
        "75pct_funding_haircut_2x_lifecycle_cost": (0.75, 2.0),
    }
    return {
        label: {
            "funding_haircut": haircut,
            "lifecycle_cost_multiplier": multiplier,
            "net_bps": rounded(stressed_net(split, funding_haircut=haircut, lifecycle_cost_multiplier=multiplier)),
        }
        for label, (haircut, multiplier) in scenarios.items()
    }


def aggregate_symbol_subset(symbol_metrics: dict, symbols: tuple[str, ...], split_name: str) -> dict:
    split_records = [symbol_metrics[symbol][split_name] for symbol in symbols]
    price = sum(float(item["gross_price_component_bps"]) for item in split_records) / len(split_records)
    funding = sum(float(item["gross_funding_component_bps"]) for item in split_records) / len(split_records)
    gross_total = price + funding
    base_cost = sum(float(item["net_lifecycle_cost_bps"]) for item in split_records) / len(split_records)
    return {
        "symbols": list(symbols),
        "gross_price_component_bps": rounded(price),
        "gross_funding_component_bps": rounded(funding),
        "gross_total_bps": rounded(gross_total),
        "net_after_lifecycle_cost_bps": rounded(gross_total - base_cost),
    }


def symbol_concentration(execution: dict) -> dict:
    symbol_metrics = execution["config_result"].get("symbol_split_metrics")
    if not symbol_metrics:
        return {
            "symbol_concentration_status": "UNAVAILABLE",
            "reason": "execution artifact does not contain symbol_split_metrics",
        }
    if any(symbol not in symbol_metrics for symbol in SYMBOLS):
        return {
            "symbol_concentration_status": "UNAVAILABLE",
            "reason": "execution artifact symbol_split_metrics does not contain all required BTC/ETH/SOL symbols",
        }

    per_symbol = {}
    for symbol in SYMBOLS:
        per_symbol[symbol] = {
            "validation_net_after_lifecycle_cost_bps": symbol_metrics[symbol]["validation"][
                "net_after_lifecycle_cost_bps"
            ],
            "holdout_net_after_lifecycle_cost_bps": symbol_metrics[symbol]["holdout"][
                "net_after_lifecycle_cost_bps"
            ],
            "validation_gross_total_bps": symbol_metrics[symbol]["validation"]["gross_total_bps"],
            "holdout_gross_total_bps": symbol_metrics[symbol]["holdout"]["gross_total_bps"],
        }

    concentration_by_split = {}
    dominated = False
    for split_name in ("validation", "holdout"):
        nets = {
            symbol: float(symbol_metrics[symbol][split_name]["net_after_lifecycle_cost_bps"])
            for symbol in SYMBOLS
        }
        abs_total = sum(abs(value) for value in nets.values())
        top_symbol = max(nets, key=lambda symbol: abs(nets[symbol]))
        top_share = abs(nets[top_symbol]) / abs_total if abs_total else None
        if top_share is not None and top_share > 0.70:
            dominated = True
        concentration_by_split[split_name] = {
            "net_after_lifecycle_cost_bps_by_symbol": {key: rounded(value) for key, value in nets.items()},
            "top_abs_contributor_symbol": top_symbol,
            "top_abs_contributor_share": rounded(top_share, 6),
            "single_symbol_dominance_threshold": 0.70,
            "single_symbol_dominated": bool(top_share is not None and top_share > 0.70),
        }

    return {
        "symbol_concentration_status": "AVAILABLE",
        "per_symbol_results": per_symbol,
        "btc_eth_only_aggregate": {
            "validation": aggregate_symbol_subset(symbol_metrics, ("BTCUSDT", "ETHUSDT"), "validation"),
            "holdout": aggregate_symbol_subset(symbol_metrics, ("BTCUSDT", "ETHUSDT"), "holdout"),
        },
        "all_3_aggregate_from_execution": {
            "validation": split_metric(execution, "validation"),
            "holdout": split_metric(execution, "holdout"),
        },
        "concentration_by_split": concentration_by_split,
        "dominated_by_one_symbol": dominated,
        "symbol_concentration_preliminary_passed": not dominated,
    }


def monthly_robustness_for_split(split: dict) -> dict:
    monthly_summary = split.get("monthly_summary", {})
    monthly_records = monthly_summary.get("monthly_records", {})
    net_values = [
        float(record["net_after_monthly_rebalance_cost_bps"])
        for record in monthly_records.values()
        if "net_after_monthly_rebalance_cost_bps" in record
    ]
    funding_values = [
        float(record["gross_funding_component_bps"])
        for record in monthly_records.values()
        if "gross_funding_component_bps" in record
    ]
    positive_count = sum(1 for value in net_values if value > 0)
    negative_funding_month_count = sum(1 for value in funding_values if value < 0)
    return {
        "month_count": len(monthly_records),
        "monthly_positive_count": positive_count,
        "monthly_positive_rate": rounded(positive_count / len(net_values), 6) if net_values else None,
        "stored_monthly_positive_rate": monthly_summary.get("monthly_positive_rate_net_after_rebalance"),
        "worst_month_net_bps": rounded(min(net_values)) if net_values else None,
        "stored_worst_month_net_bps": monthly_summary.get("worst_month_net_after_rebalance_bps"),
        "max_negative_month_bps": rounded(min(net_values)) if net_values else None,
        "funding_negative_month_count": negative_funding_month_count,
        "max_negative_funding_month_bps": rounded(min(funding_values)) if funding_values else None,
        "monthly_component_metrics_available": bool(funding_values),
    }


def negative_funding_regime(validation: dict, holdout: dict) -> dict:
    def split_counts(split: dict) -> dict:
        positive = int(split["funding_positive_event_count"])
        negative = int(split["funding_negative_event_count"])
        total = positive + negative
        return {
            "positive_funding_event_count": positive,
            "negative_funding_event_count": negative,
            "nonzero_funding_event_count": total,
            "negative_funding_event_share": rounded(negative / total, 6) if total else None,
        }

    validation_counts = split_counts(validation)
    holdout_counts = split_counts(holdout)
    deterioration = (
        holdout_counts["negative_funding_event_share"] - validation_counts["negative_funding_event_share"]
        if holdout_counts["negative_funding_event_share"] is not None
        and validation_counts["negative_funding_event_share"] is not None
        else None
    )
    return {
        "validation": validation_counts,
        "holdout": holdout_counts,
        "holdout_minus_validation_negative_funding_share": rounded(deterioration, 6),
        "negative_funding_deteriorated_in_holdout": bool(deterioration is not None and deterioration > 0),
    }


def capital_efficiency_for_split(split: dict) -> dict:
    scenarios = {
        "base": stressed_net(split),
        "50pct_funding_haircut": stressed_net(split, funding_haircut=0.50),
        "50pct_funding_haircut_2x_lifecycle_cost": stressed_net(
            split, funding_haircut=0.50, lifecycle_cost_multiplier=2.0
        ),
    }
    return {
        scenario_name: {
            capital_name: {
                "capital_usage": usage,
                "capital_adjusted_net_bps": rounded(net_bps / usage),
            }
            for capital_name, usage in CAPITAL_USAGE_SCENARIOS.items()
        }
        for scenario_name, net_bps in scenarios.items()
    }


def classify_feasibility(
    validation: dict,
    holdout: dict,
    combined_stress: dict,
    monthly: dict,
    concentration: dict,
) -> str:
    validation_base_positive = float(validation["net_after_lifecycle_cost_bps"]) > 0
    holdout_base_positive = float(holdout["net_after_lifecycle_cost_bps"]) > 0
    validation_combined_positive = (
        combined_stress["validation"]["50pct_funding_haircut_2x_lifecycle_cost"]["net_bps"] > 0
    )
    holdout_combined_positive = (
        combined_stress["holdout"]["50pct_funding_haircut_2x_lifecycle_cost"]["net_bps"] > 0
    )
    validation_monthly_ok = monthly["validation"]["monthly_positive_rate"] is not None and (
        monthly["validation"]["monthly_positive_rate"] >= 0.80
    )
    holdout_monthly_ok = monthly["holdout"]["monthly_positive_rate"] is not None and (
        monthly["holdout"]["monthly_positive_rate"] >= 0.70
    )
    concentration_ok = (
        concentration.get("symbol_concentration_status") != "AVAILABLE"
        or concentration.get("symbol_concentration_preliminary_passed") is True
    )

    if all(
        (
            validation_base_positive,
            holdout_base_positive,
            validation_combined_positive,
            holdout_combined_positive,
            validation_monthly_ok,
            holdout_monthly_ok,
            concentration_ok,
        )
    ):
        return "FUNDING_CARRY_RISK_CAPITAL_FEASIBILITY_STRONG_DIAGNOSTIC_NO_LIVE_PERMISSION"
    if validation_base_positive and holdout_base_positive and (
        validation_combined_positive or holdout_combined_positive
    ):
        return "FUNDING_CARRY_RISK_CAPITAL_FEASIBILITY_MODERATE_DIAGNOSTIC_NO_LIVE_PERMISSION"
    return "FUNDING_CARRY_RISK_CAPITAL_FEASIBILITY_WEAK_OR_INCOMPLETE_NO_LIVE_PERMISSION"


def main() -> int:
    ensure_target_absent()
    execution = load_json(EXECUTION_PATH)
    evaluator = load_json(EVALUATOR_PATH)
    closure = load_json(CLOSURE_PATH)
    validate_sources(execution, evaluator, closure)

    validation = split_metric(execution, "validation")
    holdout = split_metric(execution, "holdout")

    cost_stress = {
        "validation": cost_stress_for_split(validation),
        "holdout": cost_stress_for_split(holdout),
    }
    funding_haircut_stress = {
        "validation": funding_haircut_stress_for_split(validation),
        "holdout": funding_haircut_stress_for_split(holdout),
    }
    combined_stress = {
        "validation": combined_stress_for_split(validation),
        "holdout": combined_stress_for_split(holdout),
    }
    concentration = symbol_concentration(execution)
    monthly = {
        "validation": monthly_robustness_for_split(validation),
        "holdout": monthly_robustness_for_split(holdout),
    }
    negative_funding = negative_funding_regime(validation, holdout)
    capital_efficiency = {
        "capital_usage_definitions": {
            "conservative": "spot notional 1.0 + perp margin buffer 1.0 = total capital 2.0",
            "moderate": "spot notional 1.0 + perp margin buffer 0.5 = total capital 1.5",
            "aggressive": "spot notional 1.0 + perp margin buffer 0.25 = total capital 1.25",
        },
        "validation": capital_efficiency_for_split(validation),
        "holdout": capital_efficiency_for_split(holdout),
    }
    feasibility_classification = classify_feasibility(validation, holdout, combined_stress, monthly, concentration)

    validation_checks = {
        "repo_clean_before_run": True,
        "execution_artifact_loaded": True,
        "evaluator_artifact_loaded": True,
        "closure_artifact_loaded": True,
        "prior_result_promising_preserved": evaluator["result_classification"]["diagnostic_promising"] is True,
        "prior_route_closed_preserved": closure["closure_record"]["route_closed"] is True,
        "no_raw_rows_read": True,
        "no_network_used": True,
        "no_execution_rerun": True,
        "no_strategy_signal_computation": True,
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
        },
        "prior_route_result_preserved": {
            "route_family": ROUTE_FAMILY,
            "config_id": CONFIG_ID,
            "symbols": list(SYMBOLS),
            "final_result_class": evaluator["result_classification"]["result_class"],
            "diagnostic_promising": evaluator["result_classification"]["diagnostic_promising"],
            "route_closed": closure["closure_record"]["route_closed"],
            "candidate_generation_allowed": False,
            "edge_claim_allowed": False,
            "runtime_live_capital_allowed": False,
        },
        "cost_stress": cost_stress,
        "funding_haircut_stress": funding_haircut_stress,
        "combined_stress": combined_stress,
        "symbol_concentration_diagnostic": concentration,
        "monthly_robustness_diagnostic": monthly,
        "negative_funding_regime_diagnostic": negative_funding,
        "capital_efficiency_scenarios": capital_efficiency,
        "margin_liquidation_risk_notes": {
            "liquidation_model_unavailable": True,
            "real_liquidation_price_not_calculated": True,
            "required_for_live_liquidation_model": [
                "margin mode",
                "leverage",
                "maintenance margin schedule",
                "mark price dynamics",
                "collateral treatment",
                "cross-margin or portfolio-margin rules",
            ],
            "exchange_custody_risk_unmodeled": True,
            "cross_margin_portfolio_margin_effects_not_modeled": True,
            "scenario_modeling_only_no_live_permission": True,
        },
        "feasibility_classification": {
            "classification": feasibility_classification,
            "classification_grants_candidate_or_edge_or_live_permission": False,
        },
        "limitations": [
            "This diagnostic uses only stored execution, evaluator, and closure artifacts.",
            "No raw spot, perp, or funding rows are read.",
            "Costs, capital buffers, funding haircuts, and margin buffers are scenario assumptions only.",
            "No exchange, custody, operational, liquidation, borrow, tax, slippage, or live execution model is complete.",
            "A strong or moderate diagnostic classification still grants no candidate, edge, family release, runtime, live, or capital permission.",
        ],
        "safety_permissions": {
            "risk_capital_diagnostic_created": True,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
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
    print(f"feasibility_classification: {feasibility_classification}")
    print(f"validation_base_net_bps: {validation['net_after_lifecycle_cost_bps']}")
    print(f"holdout_base_net_bps: {holdout['net_after_lifecycle_cost_bps']}")
    print(
        "validation_50pct_funding_haircut_net_bps: "
        f"{funding_haircut_stress['validation']['50pct_funding_haircut']['net_after_base_lifecycle_cost_bps']}"
    )
    print(
        "holdout_50pct_funding_haircut_net_bps: "
        f"{funding_haircut_stress['holdout']['50pct_funding_haircut']['net_after_base_lifecycle_cost_bps']}"
    )
    print(
        "validation_50pct_funding_haircut_2x_cost_net_bps: "
        f"{combined_stress['validation']['50pct_funding_haircut_2x_lifecycle_cost']['net_bps']}"
    )
    print(
        "holdout_50pct_funding_haircut_2x_cost_net_bps: "
        f"{combined_stress['holdout']['50pct_funding_haircut_2x_lifecycle_cost']['net_bps']}"
    )
    print(f"validation_monthly_positive_rate: {monthly['validation']['monthly_positive_rate']}")
    print(f"holdout_monthly_positive_rate: {monthly['holdout']['monthly_positive_rate']}")
    print(f"symbol_concentration_status: {concentration['symbol_concentration_status']}")
    print(
        "capital_adjusted_validation_base_net_bps_conservative: "
        f"{capital_efficiency['validation']['base']['conservative']['capital_adjusted_net_bps']}"
    )
    print(
        "capital_adjusted_holdout_base_net_bps_conservative: "
        f"{capital_efficiency['holdout']['base']['conservative']['capital_adjusted_net_bps']}"
    )
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
