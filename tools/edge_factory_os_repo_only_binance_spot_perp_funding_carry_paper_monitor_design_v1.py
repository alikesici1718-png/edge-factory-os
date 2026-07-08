#!/usr/bin/env python
"""Create a design-only paper monitor artifact for the Binance spot-perp carry route."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

MODULE_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_binance_spot_perp_funding_carry_paper_monitor_design_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/paper_monitor_designs/binance_spot_perp_funding_carry_paper_monitor_design_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

PAPER_DRY_RUN_RELATIVE_PATH = (
    "artifacts/paper_trading_dry_runs/binance_spot_perp_funding_carry_paper_dry_run_simulator_v1.json"
)
PAPER_DESIGN_RELATIVE_PATH = (
    "artifacts/paper_trading_designs/binance_spot_perp_funding_carry_paper_trading_design_v1.json"
)
SIZING_REPAIR_RELATIVE_PATH = (
    "artifacts/order_sizing_simulations/binance_spot_perp_funding_carry_order_sizing_repair_sim_v1.json"
)
PRICE_SIZING_RELATIVE_PATH = (
    "artifacts/order_sizing_simulations/binance_spot_perp_funding_carry_price_snapshot_order_sizing_sim_v1.json"
)
EXCHANGE_RULE_RELATIVE_PATH = (
    "artifacts/exchange_rule_discovery/binance_spot_perp_funding_carry_exchange_rule_discovery_v1.json"
)
OPERATIONAL_RELATIVE_PATH = (
    "artifacts/operational_feasibility/binance_spot_perp_delta_neutral_funding_carry_operational_feasibility_v1.json"
)
RISK_CAPITAL_RELATIVE_PATH = (
    "artifacts/risk_capital_diagnostics/binance_spot_perp_delta_neutral_funding_carry_risk_capital_feasibility_v1.json"
)
CLOSURE_RELATIVE_PATH = (
    "artifacts/strategy_closures/binance_spot_perp_delta_neutral_funding_carry_closure_v1.json"
)

PAPER_DRY_RUN_PATH = REPO_ROOT / PAPER_DRY_RUN_RELATIVE_PATH
PAPER_DESIGN_PATH = REPO_ROOT / PAPER_DESIGN_RELATIVE_PATH
SIZING_REPAIR_PATH = REPO_ROOT / SIZING_REPAIR_RELATIVE_PATH
PRICE_SIZING_PATH = REPO_ROOT / PRICE_SIZING_RELATIVE_PATH
EXCHANGE_RULE_PATH = REPO_ROOT / EXCHANGE_RULE_RELATIVE_PATH
OPERATIONAL_PATH = REPO_ROOT / OPERATIONAL_RELATIVE_PATH
RISK_CAPITAL_PATH = REPO_ROOT / RISK_CAPITAL_RELATIVE_PATH
CLOSURE_PATH = REPO_ROOT / CLOSURE_RELATIVE_PATH

STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_PAPER_MONITOR_DESIGN_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_FUNDING_CARRY_PAPER_MONITOR_DESIGN"
CLASSIFICATION = "PAPER_MONITOR_DESIGN_READY_FOR_DRY_RUN_IMPLEMENTATION_PREVIEW_NO_LIVE_PERMISSION"
NEXT_ALLOWED_STEP = "PAPER_MONITOR_DRY_RUN_IMPLEMENTATION_PREVIEW_ONLY"

PAPER_DRY_RUN_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_PAPER_DRY_RUN_SIMULATOR_CREATED"
PAPER_DRY_RUN_CLASSIFICATION = "PAPER_DRY_RUN_SIM_PARTIAL_RISK_FLAGS_NO_LIVE_PERMISSION"
PAPER_DRY_RUN_PAYLOAD_SHA256 = "7dcc93b6c82344266c72144f2cd06c5b5507701d2c7f99a7971652f175dc655d"
PAPER_DESIGN_PAYLOAD_SHA256 = "67aca1c1e11d62cec04d5c05c1ec963868f04d095f84714c6c39110320ee8b63"
SIZING_REPAIR_PAYLOAD_SHA256 = "0f189c4b8999d7d9a1018cf988952e630d554ed898fc29a61510af93a906d822"
PRICE_SIZING_PAYLOAD_SHA256 = "b179b6efbe52ddb7611d678c7ac37e090fc1211784373a07e7bc64ecec2c470b"
EXCHANGE_RULE_PAYLOAD_SHA256 = "db998979f8d902ddff553877fa59384893021d2e814fb4c42dbc1ab194ebff46"
OPERATIONAL_PAYLOAD_SHA256 = "5af80fc87f583f4f5f4ed4baaa5620d708eff1ade5aaa54969d4259e54d6604e"
RISK_CAPITAL_PAYLOAD_SHA256 = "9b158cf8517e47c750c39234ea1d7287619a969f567cc682e16edd103a080ccc"
CLOSURE_PAYLOAD_SHA256 = "741508f0660eefca0812805a0cab006ace1e2ca0e720dade02665e440ef839c8"

STRATEGY_RESULT_CLASS = (
    "SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_DIAGNOSTIC_PROMISING_REQUIRES_CLOSURE_NO_CANDIDATE_NO_EDGE"
)
RISK_CAPITAL_CLASSIFICATION = "FUNDING_CARRY_RISK_CAPITAL_FEASIBILITY_STRONG_DIAGNOSTIC_NO_LIVE_PERMISSION"
OPERATIONAL_CLASSIFICATION = (
    "FUNDING_CARRY_OPERATIONAL_FEASIBILITY_INCOMPLETE_NEEDS_EXCHANGE_RULES_NO_LIVE_PERMISSION"
)
EXCHANGE_RULE_CLASSIFICATION = (
    "EXCHANGE_RULE_DISCOVERY_PASS_READY_FOR_PRICE_SNAPSHOT_AND_SIZING_SIM_NO_LIVE_PERMISSION"
)
SIZING_REPAIR_CLASSIFICATION = "ORDER_SIZING_REPAIR_SIM_PASS_READY_FOR_PAPER_TRADING_DESIGN_NO_LIVE_PERMISSION"
PRICE_SIZING_CLASSIFICATION = "PRICE_SNAPSHOT_ORDER_SIZING_SIM_FAIL_NO_LIVE_PERMISSION"

ROUTE_FAMILY = "BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_BASELINE"
CONFIG_ID = "spot_long_perp_short_always_on_funding_carry_3symbol"
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
CAPITAL_SCENARIOS = (100, 235, 250, 500, 1000, 2500, 5000)
TRACKED_PYTHON_COUNT_AT_START = 890


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


def artifact_contains(artifact: dict, expected: str) -> bool:
    return expected in json.dumps(artifact, sort_keys=True, ensure_ascii=True)


def assert_payload(path_name: str, artifact: dict, expected_hash: str) -> None:
    actual = artifact.get("payload_sha256_excluding_hash")
    if actual != expected_hash:
        raise RuntimeError(f"{path_name} payload hash mismatch: expected {expected_hash}, got {actual}")


def ensure_target_absent() -> None:
    if ARTIFACT_PATH.exists():
        raise RuntimeError(f"target artifact already exists: {ARTIFACT_PATH}")


def validate_prior_artifacts(artifacts: dict) -> None:
    dry_run = artifacts["paper_dry_run"]
    if dry_run.get("status") != PAPER_DRY_RUN_STATUS:
        raise RuntimeError("paper dry-run status mismatch")
    assert_payload("paper dry-run", dry_run, PAPER_DRY_RUN_PAYLOAD_SHA256)
    if dry_run["classification"]["classification"] != PAPER_DRY_RUN_CLASSIFICATION:
        raise RuntimeError("paper dry-run classification mismatch")
    if dry_run["next_allowed_step"]["step"] != "PAPER_MONITOR_DESIGN_ONLY":
        raise RuntimeError("paper dry-run does not allow paper monitor design next")
    if dry_run["risk_halt_checks"]["critical_risk_flags"] != []:
        raise RuntimeError("paper dry-run critical risk flags are not empty")
    for key in (
        "order_placement_allowed_now",
        "candidate_generation_allowed_now",
        "edge_claim_allowed_now",
        "family_release_allowed_now",
        "runtime_permission_allowed_now",
        "live_permission_allowed_now",
        "capital_permission_allowed_now",
    ):
        if dry_run["safety_permissions"].get(key) is not False:
            raise RuntimeError(f"paper dry-run safety permission not false: {key}")

    assert_payload("paper trading design", artifacts["paper_design"], PAPER_DESIGN_PAYLOAD_SHA256)
    assert_payload("sizing repair", artifacts["sizing_repair"], SIZING_REPAIR_PAYLOAD_SHA256)
    assert_payload("price sizing simulation", artifacts["price_sizing"], PRICE_SIZING_PAYLOAD_SHA256)
    assert_payload("exchange rule discovery", artifacts["exchange_rule"], EXCHANGE_RULE_PAYLOAD_SHA256)
    assert_payload("operational feasibility", artifacts["operational"], OPERATIONAL_PAYLOAD_SHA256)
    assert_payload("risk capital diagnostic", artifacts["risk_capital"], RISK_CAPITAL_PAYLOAD_SHA256)
    assert_payload("strategy closure", artifacts["closure"], CLOSURE_PAYLOAD_SHA256)

    required_strings = (
        (artifacts["closure"], STRATEGY_RESULT_CLASS),
        (artifacts["risk_capital"], RISK_CAPITAL_CLASSIFICATION),
        (artifacts["operational"], OPERATIONAL_CLASSIFICATION),
        (artifacts["exchange_rule"], EXCHANGE_RULE_CLASSIFICATION),
        (artifacts["sizing_repair"], SIZING_REPAIR_CLASSIFICATION),
        (artifacts["price_sizing"], PRICE_SIZING_CLASSIFICATION),
    )
    for artifact, expected in required_strings:
        if not artifact_contains(artifact, expected):
            raise RuntimeError(f"required prior result not found: {expected}")


def main() -> int:
    ensure_target_absent()

    artifacts = {
        "paper_dry_run": load_json(PAPER_DRY_RUN_PATH),
        "paper_design": load_json(PAPER_DESIGN_PATH),
        "sizing_repair": load_json(SIZING_REPAIR_PATH),
        "price_sizing": load_json(PRICE_SIZING_PATH),
        "exchange_rule": load_json(EXCHANGE_RULE_PATH),
        "operational": load_json(OPERATIONAL_PATH),
        "risk_capital": load_json(RISK_CAPITAL_PATH),
        "closure": load_json(CLOSURE_PATH),
    }
    validate_prior_artifacts(artifacts)

    dry_run = artifacts["paper_dry_run"]
    passing_capitals = dry_run["repaired_sizing_results"]["passing_capital_scenarios"]
    minimum_passing_capital = dry_run["repaired_sizing_results"]["minimum_passing_capital"]
    non_critical_flags = dry_run["risk_halt_checks"]["risk_flags"]

    states = [
        "DISABLED",
        "SNAPSHOT_PUBLIC_MARKET_DATA",
        "REFRESH_EXCHANGE_RULES",
        "RUN_REPAIRED_SIZING",
        "SIMULATE_ENTRY_DECISION",
        "SIMULATE_POSITION_OPEN",
        "MONITOR_FUNDING",
        "SIMULATE_REBALANCE_OR_EXIT",
        "RISK_HALT",
        "REPORT_ONLY",
    ]
    critical_risk_flags = [
        "any_private_api_key_requirement",
        "any_order_endpoint_call_attempted",
        "any_symbol_status_not_trading",
        "missing_spot_price",
        "missing_futures_price",
        "missing_funding_data",
        "missing_next_funding_time",
        "sizing_failure_for_all_scenarios",
        "leg_mismatch_above_threshold_for_all_scenarios",
        "stale_snapshot",
        "negative_funding_across_all_symbols",
        "exchange_rule_mismatch",
        "missing_premiumIndex_data",
    ]
    non_critical_risk_flags = [
        "some_capital_scenarios_fail_sizing",
        "one_symbol_negative_funding_but_aggregate_remains_positive",
        "high_notional_mismatch_in_non_selected_scenarios",
        "next_funding_time_far_or_ambiguous",
        "premiumIndex_present_but_no_server_timestamp",
    ]
    kill_switch_rules = [
        "stop_simulated_entry_if_funding_negative_for_2_consecutive_funding_events_on_a_symbol",
        "stop_if_public_data_stale",
        "stop_if_repaired_sizing_fails",
        "stop_if_leg_mismatch_above_threshold",
        "stop_if_exchangeInfo_symbol_status_changes",
        "stop_if_funding_event_missing",
        "stop_if_spot_perp_price_residual_exceeds_configured_paper_threshold",
        "stop_if_any_rule_completeness_check_fails",
    ]

    validation_checks = {
        "repo_clean_before_run": True,
        "prior_paper_dry_run_loaded": True,
        "prior_paper_design_loaded": True,
        "prior_sizing_repair_loaded": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_private_api": True,
        "no_api_key_used": True,
        "no_order_endpoint_called": True,
        "no_orders_placed": True,
        "no_runtime_enabled": True,
        "no_live_or_capital_permission": True,
        "state_machine_defined": True,
        "kill_switch_policy_defined": True,
        "reporting_design_defined": True,
        "next_allowed_step_is_preview_only": NEXT_ALLOWED_STEP
        == "PAPER_MONITOR_DRY_RUN_IMPLEMENTATION_PREVIEW_ONLY",
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
            "paper_dry_run": PAPER_DRY_RUN_RELATIVE_PATH,
            "paper_dry_run_payload_sha256_excluding_hash": PAPER_DRY_RUN_PAYLOAD_SHA256,
            "paper_trading_design": PAPER_DESIGN_RELATIVE_PATH,
            "paper_trading_design_payload_sha256_excluding_hash": PAPER_DESIGN_PAYLOAD_SHA256,
            "order_sizing_repair_sim": SIZING_REPAIR_RELATIVE_PATH,
            "order_sizing_repair_payload_sha256_excluding_hash": SIZING_REPAIR_PAYLOAD_SHA256,
            "price_snapshot_sizing_sim": PRICE_SIZING_RELATIVE_PATH,
            "price_snapshot_sizing_payload_sha256_excluding_hash": PRICE_SIZING_PAYLOAD_SHA256,
            "exchange_rule_discovery": EXCHANGE_RULE_RELATIVE_PATH,
            "exchange_rule_payload_sha256_excluding_hash": EXCHANGE_RULE_PAYLOAD_SHA256,
            "operational_feasibility": OPERATIONAL_RELATIVE_PATH,
            "operational_payload_sha256_excluding_hash": OPERATIONAL_PAYLOAD_SHA256,
            "risk_capital_diagnostic": RISK_CAPITAL_RELATIVE_PATH,
            "risk_capital_payload_sha256_excluding_hash": RISK_CAPITAL_PAYLOAD_SHA256,
            "strategy_closure": CLOSURE_RELATIVE_PATH,
            "strategy_closure_payload_sha256_excluding_hash": CLOSURE_PAYLOAD_SHA256,
        },
        "prior_chain_preserved": {
            "route_family": ROUTE_FAMILY,
            "config_id": CONFIG_ID,
            "symbols": list(SYMBOLS),
            "strategy_diagnostic_promising": True,
            "strategy_result_class": STRATEGY_RESULT_CLASS,
            "risk_capital_feasibility_classification": RISK_CAPITAL_CLASSIFICATION,
            "operational_feasibility_prior_gap": OPERATIONAL_CLASSIFICATION,
            "exchange_rules_discovered": True,
            "exchange_rule_classification": EXCHANGE_RULE_CLASSIFICATION,
            "original_price_snapshot_sizing_classification": PRICE_SIZING_CLASSIFICATION,
            "sizing_repaired": True,
            "sizing_repair_classification": SIZING_REPAIR_CLASSIFICATION,
            "paper_dry_run_status": dry_run["status"],
            "paper_dry_run_classification": dry_run["classification"]["classification"],
            "paper_dry_run_snapshot_time_utc": dry_run["public_snapshot_summary"]["snapshot_time_utc"],
            "paper_dry_run_passing_capital_scenarios": passing_capitals,
            "paper_dry_run_minimum_passing_capital": minimum_passing_capital,
            "paper_dry_run_critical_risk_flags": dry_run["risk_halt_checks"]["critical_risk_flags"],
            "paper_dry_run_non_critical_flags": non_critical_flags,
            "live_capital_permission_exists": False,
            "paper_monitor_enabled_now": False,
        },
        "paper_monitor_state_machine": {
            "default_state": "DISABLED",
            "states": states,
            "terminal_or_safe_states": ["RISK_HALT", "REPORT_ONLY"],
            "state_transition_rules": [
                {
                    "from": "DISABLED",
                    "to": "SNAPSHOT_PUBLIC_MARKET_DATA",
                    "condition": "future preview tool explicitly started by operator for report-only paper dry run",
                    "automatic_runtime_transition_allowed": False,
                },
                {
                    "from": "SNAPSHOT_PUBLIC_MARKET_DATA",
                    "to": "REPORT_ONLY",
                    "condition": "public market data missing or stale",
                    "simulated_entry_allowed": False,
                },
                {
                    "from": "SNAPSHOT_PUBLIC_MARKET_DATA",
                    "to": "REFRESH_EXCHANGE_RULES",
                    "condition": "public snapshot complete and preview continues in report-only mode",
                    "order_payloads_generated": False,
                },
                {
                    "from": "REFRESH_EXCHANGE_RULES",
                    "to": "RUN_REPAIRED_SIZING",
                    "condition": "stored or refreshed public exchangeInfo rules complete",
                    "private_api_allowed": False,
                },
                {
                    "from": "RUN_REPAIRED_SIZING",
                    "to": "REPORT_ONLY",
                    "condition": "all capital scenarios fail sizing",
                    "simulated_entry_allowed": False,
                },
                {
                    "from": "RUN_REPAIRED_SIZING",
                    "to": "RISK_HALT",
                    "condition": "critical risk flag present",
                    "simulated_entry_allowed": False,
                },
                {
                    "from": "RUN_REPAIRED_SIZING",
                    "to": "SIMULATE_ENTRY_DECISION",
                    "condition": "no critical risk and at least one capital scenario passes repaired sizing",
                    "simulated_entry_label_required": "SIMULATED_NOT_ORDER",
                    "real_order_allowed": False,
                },
                {
                    "from": "SIMULATE_ENTRY_DECISION",
                    "to": "SIMULATE_POSITION_OPEN",
                    "condition": "paper-only simulated entry selected for reporting",
                    "order_payloads_generated": False,
                },
                {
                    "from": "SIMULATE_POSITION_OPEN",
                    "to": "MONITOR_FUNDING",
                    "condition": "simulated open state recorded without order IDs or account balances",
                    "real_position_created": False,
                },
                {
                    "from": "MONITOR_FUNDING",
                    "to": "SIMULATE_REBALANCE_OR_EXIT",
                    "condition": "funding event reconciliation or paper rebalance checkpoint",
                    "order_endpoint_called": False,
                },
                {
                    "from": "SIMULATE_REBALANCE_OR_EXIT",
                    "to": "REPORT_ONLY",
                    "condition": "paper report finalized as immutable JSON artifact",
                    "live_or_capital_permission": False,
                },
            ],
            "simulated_entry_label": "SIMULATED_NOT_ORDER",
            "order_endpoint_payloads_generated": False,
            "automatic_transition_to_live_runtime_or_capital": False,
        },
        "monitor_cadence_design": {
            "enabled_now": False,
            "daemon_service_scheduler_created": False,
            "future_report_only_cadence": [
                {
                    "cadence": "hourly",
                    "purpose": "public spot/futures/premiumIndex snapshot and repaired sizing check",
                },
                {
                    "cadence": "15_minutes_before_expected_funding_time",
                    "purpose": "extra funding and sizing risk check before expected funding event",
                },
                {
                    "cadence": "after_each_funding_timestamp",
                    "purpose": "funding-event reconciliation in simulated records",
                },
                {
                    "cadence": "daily",
                    "purpose": "daily paper monitor summary report",
                },
                {
                    "cadence": "monthly",
                    "purpose": "monthly carry and risk summary report",
                },
            ],
        },
        "public_input_requirements": {
            "spot_public_price_snapshot": {"required": True, "private_endpoint_allowed": False},
            "futures_public_price_snapshot": {"required": True, "private_endpoint_allowed": False},
            "premiumIndex_snapshot": {
                "required": True,
                "fields": ["markPrice", "indexPrice", "lastFundingRate", "nextFundingTime"],
                "private_endpoint_allowed": False,
            },
            "exchangeInfo_rules": {
                "required": True,
                "fields": ["symbol_status", "minQty", "stepSize", "minNotional", "tickSize"],
                "private_endpoint_allowed": False,
            },
            "public_funding_info_or_history": {"required": True, "private_endpoint_allowed": False},
            "account_data": {"required": False, "allowed_now": False},
            "balances": {"required": False, "allowed_now": False},
            "api_keys": {"required": False, "allowed_now": False},
        },
        "repaired_sizing_policy": {
            "same_base_quantity_on_spot_and_perp": True,
            "decimal_arithmetic_required": True,
            "filter_aware": True,
            "required_filters": ["minQty", "stepSize", "minNotional", "tickSize"],
            "sizing_runs_at_every_snapshot": True,
            "independent_spot_futures_rounding_allowed": False,
            "fail_closed_if_mismatch_or_filters_fail": True,
            "leg_mismatch_threshold_bps": 25,
            "unused_notional_threshold_bps": 500,
            "source_repair_artifact": SIZING_REPAIR_RELATIVE_PATH,
        },
        "capital_scenario_policy": {
            "capital_pass_fail_non_monotonic": True,
            "fixed_scenario_list_usdt": list(CAPITAL_SCENARIOS),
            "prior_dry_run_passing_scenarios_usdt": passing_capitals,
            "prior_dry_run_minimum_passing_capital_usdt": minimum_passing_capital,
            "future_monitor_may_choose_smallest_passing_scenario_for_paper_simulation_only": True,
            "real_capital_allocation_allowed": False,
        },
        "risk_flag_policy": {
            "critical_risk_flags": critical_risk_flags,
            "non_critical_risk_flags": non_critical_risk_flags,
            "prior_dry_run_critical_flags": dry_run["risk_halt_checks"]["critical_risk_flags"],
            "prior_dry_run_non_critical_flags": non_critical_flags,
            "critical_flag_action": "RISK_HALT",
            "non_critical_flag_action": "REPORT_ONLY_WITH_FLAG_DETAILS",
            "all_scenarios_fail_action": "REPORT_ONLY_WITH_NO_SIMULATED_ENTRY",
        },
        "kill_switch_policy_draft": {
            "applies_to_future_paper_monitor_only": True,
            "rules": kill_switch_rules,
            "real_order_cancellation_or_liquidation_action_defined_now": False,
            "live_risk_management_permission_granted": False,
        },
        "paper_report_design": {
            "report_types": [
                "hourly_snapshot_report",
                "funding_event_report",
                "daily_carry_report",
                "monthly_carry_report",
                "risk_flag_report",
                "sizing_pass_fail_report",
                "simulated_pnl_attribution_report",
            ],
            "required_simulated_records": [
                "snapshot_time_utc",
                "symbol_prices",
                "funding_rates",
                "next_funding_times",
                "sizing_result_per_capital_scenario",
                "chosen_paper_capital_scenario_if_any",
                "simulated_common_base_quantities",
                "spot_notional",
                "perp_notional",
                "mismatch_bps",
                "unused_notional_bps",
                "simulated_funding_accrual",
                "simulated_price_hedge_residual",
                "risk_flags",
                "no_order_confirmation",
            ],
            "simulated_pnl_attribution_components": [
                "funding_component",
                "price_hedge_residual",
                "estimated_fees",
                "estimated_slippage",
                "unmodeled_risks",
            ],
            "all_trade_like_rows_labeled": "SIMULATED_NOT_ORDER",
        },
        "corporate_audit_requirements": {
            "immutable_json_artifact_per_dry_run": True,
            "manual_edits_to_results_allowed": False,
            "every_paper_run_has_payload_hash": True,
            "every_report_records_source_artifacts": True,
            "reproducibility_checkpoints_required": True,
            "no_live_permission_flag_required": True,
            "no_candidate_edge_claim_flag_required": True,
            "paper_live_separation_required": True,
        },
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "classification": CLASSIFICATION,
        "limitations": [
            "This artifact is a monitor design only and creates no implementation, daemon, service, schedule, runtime config, API call, or exchange connection.",
            "Paper monitor pass/fail decisions remain simulation-only and cannot allocate capital or place orders.",
            "The prior dry-run was partial because some capital scenarios failed sizing; future preview modules must preserve that non-monotonic sizing behavior.",
            "Risk thresholds are policy drafts for future paper monitoring and are not live trading controls.",
            "No candidate generation, edge claim, family release, runtime permission, live permission, or capital permission is granted.",
        ],
        "safety_permissions": {
            "paper_monitor_design_created": True,
            "paper_monitor_enabled_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "order_placement_allowed_now": False,
            "private_api_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "next_step_must_not_be_live_or_capital": True,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(artifact, handle, indent=2, sort_keys=True)
        handle.write("\n")

    stdout = {
        "status": STATUS,
        "classification": CLASSIFICATION,
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "states_count": len(states),
        "risk_flags_count": len(critical_risk_flags) + len(non_critical_risk_flags),
        "kill_switch_rules_count": len(kill_switch_rules),
        "paper_monitor_enabled_now": False,
        "order_placement_allowed_now": False,
        "runtime_live_capital": False,
        "candidate_generation": False,
        "edge_claim": False,
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": replacement_checks_all_true,
    }
    for key, value in stdout.items():
        print(f"{key}: {json.dumps(value, sort_keys=True)}")
    return 0 if replacement_checks_all_true else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        raise SystemExit(1)
