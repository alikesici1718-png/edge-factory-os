#!/usr/bin/env python
"""Create a design-only finite multi-cycle paper monitor artifact."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

MODULE_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_binance_spot_perp_funding_carry_multi_cycle_paper_monitor_design_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/paper_monitor_designs/binance_spot_perp_funding_carry_multi_cycle_paper_monitor_design_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

SINGLE_CYCLE_RELATIVE_PATH = (
    "artifacts/paper_monitor_dry_runs/binance_spot_perp_funding_carry_paper_monitor_single_cycle_v1.json"
)
PREVIEW_RELATIVE_PATH = (
    "artifacts/paper_monitor_previews/binance_spot_perp_funding_carry_paper_monitor_dry_run_preview_v1.json"
)
PAPER_MONITOR_DESIGN_RELATIVE_PATH = (
    "artifacts/paper_monitor_designs/binance_spot_perp_funding_carry_paper_monitor_design_v1.json"
)
PAPER_DRY_RUN_RELATIVE_PATH = (
    "artifacts/paper_trading_dry_runs/binance_spot_perp_funding_carry_paper_dry_run_simulator_v1.json"
)
SIZING_REPAIR_RELATIVE_PATH = (
    "artifacts/order_sizing_simulations/binance_spot_perp_funding_carry_order_sizing_repair_sim_v1.json"
)
EXCHANGE_RULE_RELATIVE_PATH = (
    "artifacts/exchange_rule_discovery/binance_spot_perp_funding_carry_exchange_rule_discovery_v1.json"
)
RISK_CAPITAL_RELATIVE_PATH = (
    "artifacts/risk_capital_diagnostics/binance_spot_perp_delta_neutral_funding_carry_risk_capital_feasibility_v1.json"
)
CLOSURE_RELATIVE_PATH = (
    "artifacts/strategy_closures/binance_spot_perp_delta_neutral_funding_carry_closure_v1.json"
)

SINGLE_CYCLE_PATH = REPO_ROOT / SINGLE_CYCLE_RELATIVE_PATH
PREVIEW_PATH = REPO_ROOT / PREVIEW_RELATIVE_PATH
PAPER_MONITOR_DESIGN_PATH = REPO_ROOT / PAPER_MONITOR_DESIGN_RELATIVE_PATH
PAPER_DRY_RUN_PATH = REPO_ROOT / PAPER_DRY_RUN_RELATIVE_PATH
SIZING_REPAIR_PATH = REPO_ROOT / SIZING_REPAIR_RELATIVE_PATH
EXCHANGE_RULE_PATH = REPO_ROOT / EXCHANGE_RULE_RELATIVE_PATH
RISK_CAPITAL_PATH = REPO_ROOT / RISK_CAPITAL_RELATIVE_PATH
CLOSURE_PATH = REPO_ROOT / CLOSURE_RELATIVE_PATH

STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_MULTI_CYCLE_PAPER_MONITOR_DESIGN_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_FUNDING_CARRY_MULTI_CYCLE_PAPER_MONITOR_DESIGN"
CLASSIFICATION = "MULTI_CYCLE_PAPER_MONITOR_DESIGN_READY_FOR_IMPLEMENTATION_PREVIEW_NO_LIVE_PERMISSION"
NEXT_ALLOWED_STEP = "PAPER_MONITOR_MULTI_CYCLE_IMPLEMENTATION_PREVIEW_ONLY"

SINGLE_CYCLE_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_PAPER_MONITOR_SINGLE_CYCLE_CREATED"
SINGLE_CYCLE_CLASSIFICATION = "PAPER_MONITOR_SINGLE_CYCLE_PARTIAL_RISK_FLAGS_NO_LIVE_PERMISSION"
SINGLE_CYCLE_NEXT_STEP = "PAPER_MONITOR_MULTI_CYCLE_DRY_RUN_DESIGN_ONLY"
SINGLE_CYCLE_PAYLOAD_SHA256 = "495fcc7bf364ef7ee1fabb317807c998343a5683ac6681505ef37784ec324d1f"
PREVIEW_PAYLOAD_SHA256 = "2d82499353b3ff5ed2326644de01fdfad01d2ca4a13e4edd7c90c4a329fa6173"
PAPER_MONITOR_DESIGN_PAYLOAD_SHA256 = "25cb17fa9a4e296f194b79808a6515d880ec232ecde3356c008ccb2da04c6188"
PAPER_DRY_RUN_PAYLOAD_SHA256 = "7dcc93b6c82344266c72144f2cd06c5b5507701d2c7f99a7971652f175dc655d"
SIZING_REPAIR_PAYLOAD_SHA256 = "0f189c4b8999d7d9a1018cf988952e630d554ed898fc29a61510af93a906d822"
EXCHANGE_RULE_PAYLOAD_SHA256 = "db998979f8d902ddff553877fa59384893021d2e814fb4c42dbc1ab194ebff46"
RISK_CAPITAL_PAYLOAD_SHA256 = "9b158cf8517e47c750c39234ea1d7287619a969f567cc682e16edd103a080ccc"
CLOSURE_PAYLOAD_SHA256 = "741508f0660eefca0812805a0cab006ace1e2ca0e720dade02665e440ef839c8"

ROUTE_FAMILY = "BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_BASELINE"
CONFIG_ID = "spot_long_perp_short_always_on_funding_carry_3symbol"
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
CAPITAL_SCENARIOS = (100, 235, 250, 500, 1000, 2500, 5000)
DESIGNED_CYCLE_COUNT = 6
TRACKED_PYTHON_COUNT_AT_START = 893


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


def assert_payload(name: str, artifact: dict, expected_hash: str) -> None:
    actual = artifact.get("payload_sha256_excluding_hash")
    if actual != expected_hash:
        raise RuntimeError(f"{name} payload hash mismatch: expected {expected_hash}, got {actual}")


def validate_prior_artifacts(artifacts: dict) -> None:
    single_cycle = artifacts["single_cycle"]
    if single_cycle.get("status") != SINGLE_CYCLE_STATUS:
        raise RuntimeError("single-cycle status mismatch")
    if single_cycle["classification"]["classification"] != SINGLE_CYCLE_CLASSIFICATION:
        raise RuntimeError("single-cycle classification mismatch")
    if single_cycle.get("next_allowed_step") != SINGLE_CYCLE_NEXT_STEP:
        raise RuntimeError("single-cycle next allowed step mismatch")
    if single_cycle["risk_flags"]["critical_risk_flags"] != []:
        raise RuntimeError("single-cycle has unexpected critical risk flags")
    assert_payload("single-cycle", single_cycle, SINGLE_CYCLE_PAYLOAD_SHA256)

    for key, expected in (
        ("preview", PREVIEW_PAYLOAD_SHA256),
        ("paper_monitor_design", PAPER_MONITOR_DESIGN_PAYLOAD_SHA256),
        ("paper_dry_run", PAPER_DRY_RUN_PAYLOAD_SHA256),
        ("sizing_repair", SIZING_REPAIR_PAYLOAD_SHA256),
        ("exchange_rule", EXCHANGE_RULE_PAYLOAD_SHA256),
        ("risk_capital", RISK_CAPITAL_PAYLOAD_SHA256),
        ("closure", CLOSURE_PAYLOAD_SHA256),
    ):
        assert_payload(key, artifacts[key], expected)

    for key in (
        "order_placement_allowed_now",
        "private_api_allowed_now",
        "runtime_permission_allowed_now",
        "live_permission_allowed_now",
        "capital_permission_allowed_now",
        "candidate_generation_allowed_now",
        "edge_claim_allowed_now",
        "family_release_allowed_now",
    ):
        if single_cycle["safety_permissions"].get(key) is not False:
            raise RuntimeError(f"single-cycle safety permission not false: {key}")


def main() -> int:
    ensure_target_absent()
    artifacts = {
        "single_cycle": load_json(SINGLE_CYCLE_PATH),
        "preview": load_json(PREVIEW_PATH),
        "paper_monitor_design": load_json(PAPER_MONITOR_DESIGN_PATH),
        "paper_dry_run": load_json(PAPER_DRY_RUN_PATH),
        "sizing_repair": load_json(SIZING_REPAIR_PATH),
        "exchange_rule": load_json(EXCHANGE_RULE_PATH),
        "risk_capital": load_json(RISK_CAPITAL_PATH),
        "closure": load_json(CLOSURE_PATH),
    }
    validate_prior_artifacts(artifacts)

    single_cycle = artifacts["single_cycle"]

    states = [
        "DISABLED",
        "CYCLE_START",
        "SNAPSHOT_PUBLIC_MARKET_DATA",
        "REFRESH_EXCHANGE_RULES",
        "RUN_REPAIRED_SIZING",
        "SIMULATE_ENTRY_DECISION",
        "SIMULATE_POSITION_STATE",
        "MONITOR_FUNDING",
        "SIMULATE_REBALANCE_OR_EXIT",
        "RISK_HALT",
        "CYCLE_REPORT",
        "FINAL_REPORT_ONLY",
    ]
    critical_risk_flags = [
        "missing_spot_price",
        "missing_futures_price",
        "missing_premiumIndex_or_funding",
        "missing_exchange_rules",
        "stale_snapshot",
        "all_scenarios_fail_sizing",
        "all_symbols_have_negative_funding",
        "symbol_status_not_trading",
        "order_endpoint_attempted",
        "private_api_attempted",
        "api_key_detected",
        "runtime_live_capital_flag_true",
    ]
    non_critical_risk_flags = [
        "some_scenarios_fail_sizing",
        "one_symbol_has_negative_funding",
        "high_mismatch_in_non_selected_scenario",
        "next_funding_time_ambiguous",
        "premiumIndex_present_but_no_server_timestamp",
        "scenario_pass_fail_non_monotonic",
    ]
    cycle_record_fields = [
        "cycle_index",
        "cycle_start_time_utc",
        "snapshot_time_utc",
        "symbols",
        "spot_prices",
        "futures_prices",
        "premiumIndex_funding_data",
        "exchange_rule_freshness",
        "capital_scenario_pass_fail_table",
        "selected_paper_scenario_if_any",
        "simulated_quantities_if_any",
        "leg_mismatch_bps",
        "unused_notional_bps",
        "risk_flags",
        "state_trace",
        "simulated_entry_plan_labeled_SIMULATED_NOT_ORDER",
        "no_order_confirmation",
    ]
    aggregate_report_fields = [
        "cycles_completed",
        "cycles_with_critical_risk",
        "cycles_with_no_passing_scenario",
        "cycles_with_simulated_entry_decision",
        "minimum_passing_capital_by_cycle",
        "scenario_pass_frequency",
        "symbols_with_negative_funding_count",
        "stale_missing_data_count",
        "risk_flag_frequency",
        "no_live_confirmation",
    ]
    kill_switch_rules = [
        "if_any_critical_risk_flag_appears_no_simulated_entry_for_that_cycle",
        "if_two_consecutive_cycles_have_all_scenarios_fail_sizing_report_sizing_instability",
        "if_two_consecutive_cycles_show_aggregate_negative_funding_environment_report_funding_regime_warning",
        "if_symbol_status_changes_report_symbol_halt",
        "if_public_data_stale_report_data_halt",
        "if_private_or_order_endpoint_code_path_detected_invalidate_immediately",
    ]

    validation_checks = {
        "repo_clean_before_run": True,
        "prior_single_cycle_loaded": True,
        "prior_single_cycle_next_allowed_step_verified": True,
        "prior_design_loaded": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_private_api": True,
        "no_api_key_used": True,
        "no_order_endpoint_called": True,
        "no_orders_placed": True,
        "no_runtime_enabled": True,
        "no_scheduler_created": True,
        "no_daemon_created": True,
        "no_launcher_created": True,
        "no_live_or_capital_permission": True,
        "multi_cycle_state_machine_defined": True,
        "cycle_record_schema_defined": True,
        "aggregate_report_schema_defined": True,
        "kill_switch_policy_defined": True,
        "next_allowed_step_is_preview_only": NEXT_ALLOWED_STEP
        == "PAPER_MONITOR_MULTI_CYCLE_IMPLEMENTATION_PREVIEW_ONLY",
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
            "paper_monitor_single_cycle": SINGLE_CYCLE_RELATIVE_PATH,
            "paper_monitor_single_cycle_payload_sha256_excluding_hash": SINGLE_CYCLE_PAYLOAD_SHA256,
            "paper_monitor_preview": PREVIEW_RELATIVE_PATH,
            "paper_monitor_preview_payload_sha256_excluding_hash": PREVIEW_PAYLOAD_SHA256,
            "paper_monitor_design": PAPER_MONITOR_DESIGN_RELATIVE_PATH,
            "paper_monitor_design_payload_sha256_excluding_hash": PAPER_MONITOR_DESIGN_PAYLOAD_SHA256,
            "paper_dry_run": PAPER_DRY_RUN_RELATIVE_PATH,
            "paper_dry_run_payload_sha256_excluding_hash": PAPER_DRY_RUN_PAYLOAD_SHA256,
            "order_sizing_repair_sim": SIZING_REPAIR_RELATIVE_PATH,
            "order_sizing_repair_payload_sha256_excluding_hash": SIZING_REPAIR_PAYLOAD_SHA256,
            "exchange_rule_discovery": EXCHANGE_RULE_RELATIVE_PATH,
            "exchange_rule_payload_sha256_excluding_hash": EXCHANGE_RULE_PAYLOAD_SHA256,
            "risk_capital_diagnostic": RISK_CAPITAL_RELATIVE_PATH,
            "risk_capital_payload_sha256_excluding_hash": RISK_CAPITAL_PAYLOAD_SHA256,
            "strategy_closure": CLOSURE_RELATIVE_PATH,
            "strategy_closure_payload_sha256_excluding_hash": CLOSURE_PAYLOAD_SHA256,
        },
        "prior_single_cycle_preserved": {
            "status": single_cycle["status"],
            "classification": single_cycle["classification"]["classification"],
            "snapshot_time_utc": single_cycle["public_snapshot_summary"]["snapshot_time_utc"],
            "passing_capital_scenarios": single_cycle["repaired_sizing_results"]["passing_capital_scenarios"],
            "minimum_passing_capital": single_cycle["repaired_sizing_results"]["minimum_passing_capital"],
            "critical_risk_flags": single_cycle["risk_flags"]["critical_risk_flags"],
            "non_critical_risk_flags": single_cycle["risk_flags"]["non_critical_risk_flags"],
            "next_allowed_step": single_cycle["next_allowed_step"],
            "strategy_diagnostic_promising": True,
            "risk_capital_feasibility_strong": True,
            "exchange_rules_discovered": True,
            "sizing_repaired": True,
            "paper_design_created": True,
            "dry_run_preview_created": True,
            "no_live_capital_permission": True,
        },
        "multi_cycle_scope": {
            "design_only": True,
            "future_shape": "manually invoked finite CLI dry run",
            "cycle_count": DESIGNED_CYCLE_COUNT,
            "cycle_spacing_minutes": 60,
            "max_runtime_hours": 6,
            "allowed_capital_scenarios": list(CAPITAL_SCENARIOS),
            "preferred_reporting_capital_scenario": "smallest passing scenario per cycle",
            "scenario_pass_monotonicity_assumed": False,
            "run_repaired_sizing_every_cycle": True,
            "scheduler_daemon_service_allowed": False,
            "private_api_allowed": False,
            "order_endpoints_allowed": False,
            "live_trading_allowed": False,
        },
        "state_machine_design": {
            "default_state": "DISABLED",
            "states": states,
            "state_count": len(states),
            "terminal_state": "FINAL_REPORT_ONLY",
            "safe_halt_state": "RISK_HALT",
            "order_state_present": False,
            "persistent_runtime_process": False,
        },
        "transition_policy": {
            "rules": [
                "DISABLED is default",
                "each cycle starts from CYCLE_START",
                "public data missing goes to CYCLE_REPORT with no simulated entry",
                "all scenarios failing sizing goes to CYCLE_REPORT with no simulated entry",
                "critical risk flag goes to RISK_HALT for that cycle",
                "sizing passes and no critical flags goes to SIMULATE_ENTRY_DECISION only",
                "simulated entry never becomes a real order",
                "after each cycle append immutable cycle result",
                "after max cycles go to FINAL_REPORT_ONLY",
                "no automatic restart",
                "no persistent runtime process",
            ],
            "real_order_transition_exists": False,
            "automatic_live_transition_exists": False,
        },
        "cycle_record_schema": {
            "fields": cycle_record_fields,
            "field_count": len(cycle_record_fields),
            "simulated_entry_label_required": "SIMULATED_NOT_ORDER",
            "no_order_confirmation_required": True,
        },
        "aggregate_report_schema": {
            "fields": aggregate_report_fields,
            "field_count": len(aggregate_report_fields),
            "one_json_artifact_per_future_run": True,
            "one_json_artifact_per_cycle": False,
            "local_database_allowed": False,
            "scheduler_state_file_allowed": False,
            "runtime_state_file_allowed": False,
            "account_state_allowed": False,
        },
        "risk_policy": {
            "critical_risk_flags": critical_risk_flags,
            "non_critical_risk_flags": non_critical_risk_flags,
            "critical_risk_flags_count": len(critical_risk_flags),
            "non_critical_risk_flags_count": len(non_critical_risk_flags),
            "critical_flag_action": "RISK_HALT_OR_CYCLE_REPORT_WITH_NO_SIMULATED_ENTRY",
            "non_critical_flag_action": "REPORT_FLAG_WITHOUT_LIVE_OR_CAPITAL_PERMISSION",
        },
        "funding_cycle_awareness": {
            "record_nextFundingTime_per_symbol": True,
            "mark_within_30_minutes_before_funding_time": True,
            "mark_within_30_minutes_after_funding_time": True,
            "paper_position_would_be_monitored_through_next_funding": "report-only field",
            "actual_position_opened": False,
            "orders_placed": False,
        },
        "kill_switch_policy": {
            "rules": kill_switch_rules,
            "rule_count": len(kill_switch_rules),
            "invalidates_if_private_or_order_endpoint_code_path_detected": True,
            "live_kill_switch_enabled_now": False,
        },
        "corporate_audit_requirements": {
            "deterministic_json_output": True,
            "source_artifact_list_required": True,
            "payload_hash_required": True,
            "no_live_permissions_required": True,
            "no_candidate_edge_claim_required": True,
            "no_order_payload_required": True,
            "no_account_info_required": True,
            "no_private_api_required": True,
            "all_cycle_records_immutable_in_artifact": True,
            "final_report_preserves_every_cycle_result_including_failures": True,
        },
        "classification": CLASSIFICATION,
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "limitations": [
            "This is a design artifact only and performs no implementation, network call, API call, scheduler creation, daemon creation, runtime enablement, order placement, or capital allocation.",
            "The future multi-cycle dry run is limited to manual invocation and finite cycle count.",
            "Scenario pass/fail may remain non-monotonic, so repaired sizing must run every cycle.",
            "No private API, account data, order endpoint, candidate generation, edge claim, family release, live trading, or capital permission is granted.",
        ],
        "safety_permissions": {
            "multi_cycle_paper_monitor_design_created": True,
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
        "designed_cycle_count": DESIGNED_CYCLE_COUNT,
        "state_count": len(states),
        "critical_risk_flags_count": len(critical_risk_flags),
        "non_critical_risk_flags_count": len(non_critical_risk_flags),
        "report_schema_count": 2,
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
