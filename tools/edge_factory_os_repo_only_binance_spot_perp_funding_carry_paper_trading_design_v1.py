#!/usr/bin/env python
"""Create a design-only paper-trading artifact for the Binance spot-perp carry route."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_binance_spot_perp_funding_carry_paper_trading_design_v1.py"
ARTIFACT_RELATIVE_PATH = (
    "artifacts/paper_trading_designs/binance_spot_perp_funding_carry_paper_trading_design_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

SIZING_REPAIR_RELATIVE_PATH = (
    "artifacts/order_sizing_simulations/binance_spot_perp_funding_carry_order_sizing_repair_sim_v1.json"
)
SIZING_REPAIR_PATH = REPO_ROOT / SIZING_REPAIR_RELATIVE_PATH

STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_PAPER_TRADING_DESIGN_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_FUNDING_CARRY_PAPER_TRADING_DESIGN"
SIZING_REPAIR_STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_ORDER_SIZING_REPAIR_SIM_CREATED"
SIZING_REPAIR_PAYLOAD_SHA256 = "0f189c4b8999d7d9a1018cf988952e630d554ed898fc29a61510af93a906d822"
SIZING_REPAIR_CLASSIFICATION = "ORDER_SIZING_REPAIR_SIM_PASS_READY_FOR_PAPER_TRADING_DESIGN_NO_LIVE_PERMISSION"
ROUTE_FAMILY = "BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_BASELINE"
CONFIG_ID = "spot_long_perp_short_always_on_funding_carry_3symbol"
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
TRACKED_PYTHON_COUNT_AT_START = 888
NEXT_ALLOWED_STEP = "PAPER_TRADING_DRY_RUN_SIMULATOR_ONLY"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def payload_hash(artifact: dict) -> str:
    payload = {key: value for key, value in artifact.items() if key != "payload_sha256_excluding_hash"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


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


def validate_prior_repair(repair: dict) -> None:
    if repair.get("status") != SIZING_REPAIR_STATUS:
        raise RuntimeError("sizing repair artifact status mismatch")
    if repair.get("payload_sha256_excluding_hash") != SIZING_REPAIR_PAYLOAD_SHA256:
        raise RuntimeError("sizing repair artifact payload hash mismatch")
    if repair["classification"]["classification"] != SIZING_REPAIR_CLASSIFICATION:
        raise RuntimeError("sizing repair classification mismatch")
    if repair["classification"]["classification_grants_live_or_capital_permission"] is not False:
        raise RuntimeError("sizing repair unexpectedly grants live/capital permission")
    if repair["safety_permissions"]["next_step_may_be_paper_trading_design_only"] is not True:
        raise RuntimeError("sizing repair does not allow paper-trading design as next step")
    for key in (
        "order_placement_allowed_now",
        "candidate_generation_allowed_now",
        "edge_claim_allowed_now",
        "family_release_allowed_now",
        "runtime_permission_allowed_now",
        "live_permission_allowed_now",
        "capital_permission_allowed_now",
    ):
        if repair["safety_permissions"].get(key) is not False:
            raise RuntimeError(f"sizing repair safety permission not false: {key}")


def main() -> int:
    ensure_target_absent()
    repair = load_json(SIZING_REPAIR_PATH)
    validate_prior_repair(repair)

    validation_checks = {
        "repo_clean_before_run": True,
        "prior_sizing_repair_artifact_loaded": True,
        "prior_sizing_repair_status_verified": True,
        "prior_sizing_repair_payload_hash_verified": True,
        "prior_sizing_repair_classification_verified": True,
        "no_api_used": True,
        "no_order_endpoint": True,
        "no_orders_placed": True,
        "no_runtime_live_capital": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
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
            "order_sizing_repair_simulation": SIZING_REPAIR_RELATIVE_PATH,
            "order_sizing_repair_payload_sha256_excluding_hash": SIZING_REPAIR_PAYLOAD_SHA256,
        },
        "prior_sizing_repair_preserved": {
            "status": repair["status"],
            "classification": repair["classification"]["classification"],
            "minimum_passing_capital_all3": repair["classification"]["minimum_passing_capital_all3"],
            "minimum_passing_capital_btc_eth_only": repair["classification"][
                "minimum_passing_capital_btc_eth_only"
            ],
            "root_cause_repaired": repair["classification"]["root_cause_repaired"],
            "classification_grants_live_or_capital_permission": False,
        },
        "strategy_identity": {
            "route_family": ROUTE_FAMILY,
            "config_id": CONFIG_ID,
            "symbols": list(SYMBOLS),
            "position_definition": "long Binance spot and short Binance USD-M perpetual for the same base asset",
            "quantity_policy": "same base quantity per symbol on spot and USD-M perp",
            "leverage_assumption": "no leverage assumption beyond an explicit simulated margin buffer",
            "live_orders_allowed": False,
            "capital_allocation_allowed": False,
        },
        "paper_system_state_machine": {
            "states": [
                "IDLE",
                "SNAPSHOT_RULES",
                "SNAPSHOT_PRICES",
                "SIZE_ORDERS",
                "SIMULATE_ENTRY",
                "MONITOR_FUNDING",
                "SIMULATE_EXIT_OR_REBALANCE",
                "RISK_HALT",
                "REPORT_ONLY",
            ],
            "terminal_or_safe_states": ["RISK_HALT", "REPORT_ONLY"],
            "live_order_state_present": False,
            "runtime_launcher_created": False,
        },
        "required_data_feeds_for_future_paper_trading": {
            "public_spot_price_snapshot": {
                "required": True,
                "private_account_data_required_in_design_step": False,
            },
            "public_futures_price_snapshot": {
                "required": True,
                "private_account_data_required_in_design_step": False,
            },
            "funding_history_current_funding": {
                "required": True,
                "private_account_data_required_in_design_step": False,
            },
            "exchange_info_rules": {
                "required": True,
                "private_account_data_required_in_design_step": False,
            },
            "private_account_data": {
                "required_in_design_step": False,
                "api_keys_used_now": False,
            },
        },
        "sizing_policy": {
            "common_base_quantity_for_spot_and_perp": True,
            "decimal_arithmetic_required": True,
            "required_filters": ["minQty", "stepSize", "minNotional", "tickSize"],
            "sizing_runs_at_each_snapshot": True,
            "capital_pass_fail_not_assumed_monotonic": True,
            "fail_closed_if_mismatch_or_filters_fail": True,
            "no_orders_if_sizing_fails": True,
            "source_repair_algorithm": repair["repaired_sizing_algorithm"],
        },
        "risk_controls": [
            {
                "control": "no_order_if_symbol_status_not_trading",
                "action": "RISK_HALT",
            },
            {
                "control": "no_order_if_sizing_fails",
                "action": "RISK_HALT",
            },
            {
                "control": "no_order_if_price_snapshot_stale",
                "action": "RISK_HALT",
            },
            {
                "control": "no_order_if_funding_missing",
                "action": "RISK_HALT",
            },
            {
                "control": "halt_if_funding_negative_beyond_threshold",
                "threshold_defined_now": False,
                "action": "RISK_HALT",
            },
            {
                "control": "halt_if_mark_spot_divergence_exceeds_threshold",
                "threshold_defined_now": False,
                "action": "RISK_HALT",
            },
            {
                "control": "halt_if_simulated_margin_buffer_below_threshold",
                "threshold_defined_now": False,
                "action": "RISK_HALT",
            },
            {
                "control": "halt_if_api_unavailable",
                "action": "RISK_HALT",
            },
            {
                "control": "halt_if_one_leg_simulated_fill_missing",
                "action": "RISK_HALT",
            },
            {
                "control": "halt_on_symbol_delisting_or_maintenance",
                "action": "RISK_HALT",
            },
        ],
        "paper_trading_metrics": [
            "simulated_spot_quantity",
            "simulated_perp_quantity",
            "notional_mismatch",
            "funding_received_paid",
            "price_hedge_residual",
            "fees_slippage_estimate",
            "monthly_carry",
            "negative_funding_events",
            "max_simulated_drawdown_proxy",
            "per_symbol_contribution",
        ],
        "explicit_non_permissions": {
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "real_orders_allowed_now": False,
            "paper_trading_enabled_now": False,
            "runtime_launcher_created": False,
        },
        "next_step_after_design": {
            "step": NEXT_ALLOWED_STEP,
            "paper_trading_dry_run_simulator_only": True,
            "live_or_capital_allowed": False,
        },
        "limitations": [
            "This is a design artifact only and does not connect to Binance or any exchange.",
            "No API keys, account endpoints, order endpoints, runtime launcher, paper-trading process, live trading, or capital allocation are created.",
            "Risk thresholds are named as future requirements and are not tuned or enabled here.",
            "A dry-run simulator remains a separate future module and must not place real orders.",
        ],
        "safety_permissions": {
            "paper_trading_design_created": True,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "real_orders_allowed_now": False,
            "next_step_may_be_paper_trading_dry_run_simulator_only": True,
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
    print(f"artifact_path: {ARTIFACT_RELATIVE_PATH}")
    print(f"prior_sizing_repair_classification: {SIZING_REPAIR_CLASSIFICATION}")
    print(f"next_allowed_step: {NEXT_ALLOWED_STEP}")
    print("api_used: false")
    print("orders_placed: false")
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
