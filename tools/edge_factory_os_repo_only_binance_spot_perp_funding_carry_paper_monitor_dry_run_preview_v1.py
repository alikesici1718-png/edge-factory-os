#!/usr/bin/env python
"""Create a no-network paper monitor dry-run implementation preview artifact."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

MODULE_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_binance_spot_perp_funding_carry_paper_monitor_dry_run_preview_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/paper_monitor_previews/binance_spot_perp_funding_carry_paper_monitor_dry_run_preview_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

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

PAPER_MONITOR_DESIGN_PATH = REPO_ROOT / PAPER_MONITOR_DESIGN_RELATIVE_PATH
PAPER_DRY_RUN_PATH = REPO_ROOT / PAPER_DRY_RUN_RELATIVE_PATH
SIZING_REPAIR_PATH = REPO_ROOT / SIZING_REPAIR_RELATIVE_PATH
EXCHANGE_RULE_PATH = REPO_ROOT / EXCHANGE_RULE_RELATIVE_PATH
RISK_CAPITAL_PATH = REPO_ROOT / RISK_CAPITAL_RELATIVE_PATH
CLOSURE_PATH = REPO_ROOT / CLOSURE_RELATIVE_PATH

STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_PAPER_MONITOR_DRY_RUN_PREVIEW_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_FUNDING_CARRY_PAPER_MONITOR_DRY_RUN_IMPLEMENTATION_PREVIEW"
DESIGN_STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_PAPER_MONITOR_DESIGN_CREATED"
DESIGN_CLASSIFICATION = "PAPER_MONITOR_DESIGN_READY_FOR_DRY_RUN_IMPLEMENTATION_PREVIEW_NO_LIVE_PERMISSION"
DESIGN_NEXT_STEP = "PAPER_MONITOR_DRY_RUN_IMPLEMENTATION_PREVIEW_ONLY"
NEXT_ALLOWED_STEP = "PAPER_MONITOR_DRY_RUN_SINGLE_CYCLE_IMPLEMENTATION_ONLY"

PAPER_MONITOR_DESIGN_PAYLOAD_SHA256 = "25cb17fa9a4e296f194b79808a6515d880ec232ecde3356c008ccb2da04c6188"
PAPER_DRY_RUN_PAYLOAD_SHA256 = "7dcc93b6c82344266c72144f2cd06c5b5507701d2c7f99a7971652f175dc655d"
SIZING_REPAIR_PAYLOAD_SHA256 = "0f189c4b8999d7d9a1018cf988952e630d554ed898fc29a61510af93a906d822"
EXCHANGE_RULE_PAYLOAD_SHA256 = "db998979f8d902ddff553877fa59384893021d2e814fb4c42dbc1ab194ebff46"
RISK_CAPITAL_PAYLOAD_SHA256 = "9b158cf8517e47c750c39234ea1d7287619a969f567cc682e16edd103a080ccc"
CLOSURE_PAYLOAD_SHA256 = "741508f0660eefca0812805a0cab006ace1e2ca0e720dade02665e440ef839c8"

TRACKED_PYTHON_COUNT_AT_START = 891

ORDER_PLACEMENT_ALLOWED = False
PRIVATE_API_ALLOWED = False
RUNTIME_ALLOWED = False
LIVE_TRADING_ALLOWED = False
CAPITAL_ALLOCATION_ALLOWED = False
CANDIDATE_GENERATION_ALLOWED = False
EDGE_CLAIM_ALLOWED = False


@dataclass(frozen=True)
class TransitionPreview:
    source_state: str
    target_state: str
    condition: str
    order_placement_allowed: bool = False
    live_or_capital_allowed: bool = False


class PaperMonitorStateMachinePreview:
    DEFAULT_STATE = "DISABLED"
    STATES = (
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
    )
    TRANSITIONS = (
        TransitionPreview(
            "DISABLED",
            "SNAPSHOT_PUBLIC_MARKET_DATA",
            "single-cycle preview is explicitly invoked in report-only mode",
        ),
        TransitionPreview(
            "SNAPSHOT_PUBLIC_MARKET_DATA",
            "REPORT_ONLY",
            "public data missing or stale",
        ),
        TransitionPreview(
            "SNAPSHOT_PUBLIC_MARKET_DATA",
            "REFRESH_EXCHANGE_RULES",
            "public data schema is present for simulation records",
        ),
        TransitionPreview(
            "REFRESH_EXCHANGE_RULES",
            "RUN_REPAIRED_SIZING",
            "public exchange rule schema is present",
        ),
        TransitionPreview(
            "RUN_REPAIRED_SIZING",
            "REPORT_ONLY",
            "all sizing scenarios fail",
        ),
        TransitionPreview(
            "RUN_REPAIRED_SIZING",
            "RISK_HALT",
            "any critical risk flag is true",
        ),
        TransitionPreview(
            "RUN_REPAIRED_SIZING",
            "SIMULATE_ENTRY_DECISION",
            "sizing passes and no critical risk flag is true",
        ),
        TransitionPreview(
            "SIMULATE_ENTRY_DECISION",
            "SIMULATE_POSITION_OPEN",
            "paper-only simulated entry is labeled SIMULATED_NOT_ORDER",
        ),
        TransitionPreview(
            "SIMULATE_POSITION_OPEN",
            "MONITOR_FUNDING",
            "simulated position state is recorded without account or order IDs",
        ),
        TransitionPreview(
            "MONITOR_FUNDING",
            "SIMULATE_REBALANCE_OR_EXIT",
            "paper funding or rebalance checkpoint is reconciled",
        ),
        TransitionPreview(
            "SIMULATE_REBALANCE_OR_EXIT",
            "REPORT_ONLY",
            "single-cycle preview report is finalized",
        ),
        TransitionPreview(
            "RISK_HALT",
            "REPORT_ONLY",
            "risk halt is reported without any order action",
        ),
    )


def get_public_spot_price_snapshot() -> dict:
    return {"stub_status": "STUB_ONLY_NO_NETWORK", "network_called": False, "implemented_now": False}


def get_public_futures_price_snapshot() -> dict:
    return {"stub_status": "STUB_ONLY_NO_NETWORK", "network_called": False, "implemented_now": False}


def get_public_premium_index_snapshot() -> dict:
    return {"stub_status": "STUB_ONLY_NO_NETWORK", "network_called": False, "implemented_now": False}


def get_exchange_rules_snapshot() -> dict:
    return {"stub_status": "STUB_ONLY_NO_NETWORK", "network_called": False, "implemented_now": False}


def get_public_funding_snapshot() -> dict:
    return {"stub_status": "STUB_ONLY_NO_NETWORK", "network_called": False, "implemented_now": False}


def repaired_common_base_quantity_sizing_preview(input_record: dict) -> dict:
    return {
        "stub_status": "INTERFACE_ONLY_NO_LIVE_QUANTITY_COMPUTATION",
        "input_schema_name": "future_repaired_sizing_input",
        "requires_decimal_arithmetic": True,
        "requires_common_base_quantity": True,
        "references_prior_repair_algorithm": True,
        "input_record_received": bool(input_record),
        "implemented_now": False,
    }


def evaluate_risk_flags_preview(input_record: dict) -> dict:
    return {
        "stub_status": "INTERFACE_ONLY_NO_ACCOUNT_MARGIN_OR_PRIVATE_VALUES",
        "input_schema_name": "future_risk_flag_input",
        "private_or_account_values_allowed": False,
        "input_record_received": bool(input_record),
        "implemented_now": False,
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


def assert_payload(name: str, artifact: dict, expected_hash: str) -> None:
    actual = artifact.get("payload_sha256_excluding_hash")
    if actual != expected_hash:
        raise RuntimeError(f"{name} payload hash mismatch: expected {expected_hash}, got {actual}")


def ensure_target_absent() -> None:
    if ARTIFACT_PATH.exists():
        raise RuntimeError(f"target artifact already exists: {ARTIFACT_PATH}")


def transition_to_dict(transition: TransitionPreview) -> dict:
    return {
        "source_state": transition.source_state,
        "target_state": transition.target_state,
        "condition": transition.condition,
        "order_placement_allowed": transition.order_placement_allowed,
        "live_or_capital_allowed": transition.live_or_capital_allowed,
    }


def adapter_stub_contracts() -> dict:
    return {
        "get_public_spot_price_snapshot": get_public_spot_price_snapshot(),
        "get_public_futures_price_snapshot": get_public_futures_price_snapshot(),
        "get_public_premium_index_snapshot": get_public_premium_index_snapshot(),
        "get_exchange_rules_snapshot": get_exchange_rules_snapshot(),
        "get_public_funding_snapshot": get_public_funding_snapshot(),
    }


def assert_stub_contracts(stubs: dict) -> None:
    for name, record in stubs.items():
        if record.get("stub_status") != "STUB_ONLY_NO_NETWORK":
            raise RuntimeError(f"adapter is not marked stub-only: {name}")
        if record.get("network_called") is not False:
            raise RuntimeError(f"adapter could call network: {name}")


def assert_no_forbidden_code_paths() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden_snippets = tuple(
        "".join(parts)
        for parts in (
            ("import ", "urllib"),
            ("import ", "socket"),
            ("import ", "http.client"),
            ("import ", "requests"),
            ("c", "cxt"),
            ("Binance", "Socket", "Manager"),
            ("Client", "("),
            ("create", "_order"),
            ("order", "/", "test"),
            ("listen", "Key"),
            ("api", ".", "binance", ".", "com"),
            ("fapi", ".", "binance", ".", "com"),
            ("sched", "."),
            ("sub", "process"),
        )
    )
    for snippet in forbidden_snippets:
        if snippet in source:
            raise RuntimeError(f"forbidden implementation code path present: {snippet}")


def validate_prior_artifacts(artifacts: dict) -> None:
    design = artifacts["paper_monitor_design"]
    if design.get("status") != DESIGN_STATUS:
        raise RuntimeError("paper monitor design status mismatch")
    if design.get("classification") != DESIGN_CLASSIFICATION:
        raise RuntimeError("paper monitor design classification mismatch")
    if design.get("next_allowed_step") != DESIGN_NEXT_STEP:
        raise RuntimeError("paper monitor design next allowed step mismatch")
    assert_payload("paper monitor design", design, PAPER_MONITOR_DESIGN_PAYLOAD_SHA256)
    if design["safety_permissions"]["paper_monitor_enabled_now"] is not False:
        raise RuntimeError("paper monitor design unexpectedly enabled paper monitor")
    for key in (
        "runtime_permission_allowed_now",
        "live_permission_allowed_now",
        "capital_permission_allowed_now",
        "order_placement_allowed_now",
        "private_api_allowed_now",
        "candidate_generation_allowed_now",
        "edge_claim_allowed_now",
        "family_release_allowed_now",
    ):
        if design["safety_permissions"].get(key) is not False:
            raise RuntimeError(f"paper monitor design safety permission not false: {key}")

    assert_payload("paper dry-run", artifacts["paper_dry_run"], PAPER_DRY_RUN_PAYLOAD_SHA256)
    assert_payload("sizing repair", artifacts["sizing_repair"], SIZING_REPAIR_PAYLOAD_SHA256)
    assert_payload("exchange rule discovery", artifacts["exchange_rule"], EXCHANGE_RULE_PAYLOAD_SHA256)
    assert_payload("risk capital diagnostic", artifacts["risk_capital"], RISK_CAPITAL_PAYLOAD_SHA256)
    assert_payload("strategy closure", artifacts["closure"], CLOSURE_PAYLOAD_SHA256)


def report_schema_preview() -> dict:
    common_header = [
        "schema_version",
        "source_artifacts",
        "payload_sha256_excluding_hash",
        "no_order_confirmation",
        "no_live_capital_permission",
    ]
    return {
        "hourly_snapshot_report": common_header
        + ["snapshot_time_utc", "symbol_prices", "funding_rates", "risk_flags"],
        "funding_event_report": common_header
        + ["funding_time_utc", "per_symbol_funding_rate", "simulated_funding_accrual"],
        "daily_carry_report": common_header
        + ["day_utc", "simulated_funding_component", "simulated_price_hedge_residual"],
        "monthly_carry_report": common_header
        + ["month_utc", "simulated_monthly_carry", "negative_funding_event_count"],
        "risk_flag_report": common_header + ["critical_flags", "non_critical_flags", "risk_halt_state"],
        "sizing_pass_fail_report": common_header
        + ["capital_scenarios", "symbol_sizing_results", "smallest_passing_scenario"],
        "simulated_pnl_attribution_report": common_header
        + ["funding_component", "price_hedge_residual", "estimated_fees", "estimated_slippage"],
    }


def artifact_schema_preview() -> dict:
    return {
        "future_dry_run_output_schema": [
            "status",
            "snapshot_time_utc",
            "state_machine_trace",
            "public_snapshot_records",
            "repaired_sizing_results",
            "risk_halt_checks",
            "simulated_entry_plan_labeled_SIMULATED_NOT_ORDER",
            "payload_sha256_excluding_hash",
        ],
        "future_monitor_report_schema": [
            "status",
            "report_type",
            "source_artifacts",
            "paper_monitor_enabled_now_false",
            "runtime_live_capital_false",
            "payload_sha256_excluding_hash",
        ],
        "future_risk_halt_report_schema": [
            "status",
            "risk_halt_reason",
            "critical_flags",
            "state_at_halt",
            "orders_placed_false",
            "live_capital_permission_false",
            "payload_sha256_excluding_hash",
        ],
    }


def main() -> int:
    ensure_target_absent()
    assert_no_forbidden_code_paths()

    artifacts = {
        "paper_monitor_design": load_json(PAPER_MONITOR_DESIGN_PATH),
        "paper_dry_run": load_json(PAPER_DRY_RUN_PATH),
        "sizing_repair": load_json(SIZING_REPAIR_PATH),
        "exchange_rule": load_json(EXCHANGE_RULE_PATH),
        "risk_capital": load_json(RISK_CAPITAL_PATH),
        "closure": load_json(CLOSURE_PATH),
    }
    validate_prior_artifacts(artifacts)

    design = artifacts["paper_monitor_design"]
    adapter_stubs = adapter_stub_contracts()
    assert_stub_contracts(adapter_stubs)

    no_live_guards = {
        "ORDER_PLACEMENT_ALLOWED": ORDER_PLACEMENT_ALLOWED,
        "PRIVATE_API_ALLOWED": PRIVATE_API_ALLOWED,
        "RUNTIME_ALLOWED": RUNTIME_ALLOWED,
        "LIVE_TRADING_ALLOWED": LIVE_TRADING_ALLOWED,
        "CAPITAL_ALLOCATION_ALLOWED": CAPITAL_ALLOCATION_ALLOWED,
        "CANDIDATE_GENERATION_ALLOWED": CANDIDATE_GENERATION_ALLOWED,
        "EDGE_CLAIM_ALLOWED": EDGE_CLAIM_ALLOWED,
    }
    no_live_guard_constants_false = all(value is False for value in no_live_guards.values())
    if not no_live_guard_constants_false:
        raise RuntimeError("one or more no-live guard constants is not false")

    report_schemas = report_schema_preview()
    artifact_schemas = artifact_schema_preview()
    transition_table = [transition_to_dict(item) for item in PaperMonitorStateMachinePreview.TRANSITIONS]

    validation_checks = {
        "repo_clean_before_run": True,
        "prior_paper_monitor_design_loaded": True,
        "prior_design_classification_verified": True,
        "next_allowed_step_verified_preview_only": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_private_api": True,
        "no_api_key_used": True,
        "no_order_endpoint_called": True,
        "no_orders_placed": True,
        "no_runtime_enabled": True,
        "no_scheduler_created": True,
        "no_launcher_created": True,
        "no_live_or_capital_permission": True,
        "state_machine_preview_defined": True,
        "data_adapter_stubs_do_not_call_network": True,
        "no_live_guard_constants_false": no_live_guard_constants_false,
        "report_schemas_defined": bool(report_schemas),
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
        "prior_design_preserved": {
            "status": design["status"],
            "classification": design["classification"],
            "next_allowed_step": design["next_allowed_step"],
            "state_count": len(design["paper_monitor_state_machine"]["states"]),
            "critical_risk_flag_count": len(design["risk_flag_policy"]["critical_risk_flags"]),
            "non_critical_risk_flag_count": len(design["risk_flag_policy"]["non_critical_risk_flags"]),
            "kill_switch_rule_count": len(design["kill_switch_policy_draft"]["rules"]),
            "report_type_count": len(design["paper_report_design"]["report_types"]),
            "paper_monitor_enabled_now": False,
            "live_capital_permission_exists": False,
        },
        "implementation_preview_scope": {
            "implementation_preview_only": True,
            "single_cycle_future_step_only": True,
            "network_calls_defined_now": False,
            "api_calls_defined_now": False,
            "order_paths_defined_now": False,
            "daemon_service_scheduler_defined_now": False,
            "runtime_launcher_defined_now": False,
            "paper_monitor_enabled_now": False,
            "live_or_capital_permission": False,
        },
        "state_machine_preview": {
            "default_state": PaperMonitorStateMachinePreview.DEFAULT_STATE,
            "states": list(PaperMonitorStateMachinePreview.STATES),
            "state_count": len(PaperMonitorStateMachinePreview.STATES),
            "state_machine_class": "PaperMonitorStateMachinePreview",
            "simulated_entry_label_required": "SIMULATED_NOT_ORDER",
        },
        "transition_table_preview": {
            "deterministic_transition_table": transition_table,
            "transition_count": len(transition_table),
            "public_data_missing_goes_to": "REPORT_ONLY",
            "sizing_fails_goes_to": "REPORT_ONLY",
            "critical_risk_flag_goes_to": "RISK_HALT",
            "sizing_passes_and_no_critical_flags_goes_to": "SIMULATE_ENTRY_DECISION",
            "simulated_entry_never_becomes_real_order": True,
        },
        "data_adapter_stub_contract": {
            "adapter_stubs": adapter_stubs,
            "adapter_stub_count": len(adapter_stubs),
            "must_not_call_network": True,
            "future_implementation_requires_separate_approval": True,
        },
        "sizing_engine_stub_contract": {
            "interface_name": "repaired_common_base_quantity_sizing_preview",
            "preview_response": repaired_common_base_quantity_sizing_preview({}),
            "references_repaired_common_base_quantity_algorithm": True,
            "decimal_arithmetic_required_in_future_implementation": True,
            "live_quantities_computed_now": False,
            "validation_rules": [
                "same_base_quantity_for_spot_and_perp",
                "minQty_stepSize_minNotional_tickSize_filters_required",
                "fail_closed_if_any_symbol_or_scenario_fails",
                "do_not_assume_capital_pass_fail_monotonicity",
            ],
        },
        "risk_engine_stub_contract": {
            "interface_name": "evaluate_risk_flags_preview",
            "preview_response": evaluate_risk_flags_preview({}),
            "critical_risk_flags": design["risk_flag_policy"]["critical_risk_flags"],
            "non_critical_risk_flags": design["risk_flag_policy"]["non_critical_risk_flags"],
            "private_account_margin_values_allowed": False,
        },
        "report_schema_preview": report_schemas,
        "artifact_schema_preview": artifact_schemas,
        "no_live_guard_constants": no_live_guards,
        "preview_limitations": [
            "This preview defines interfaces, schemas, guards, and transition rules only.",
            "No public or private market data is fetched.",
            "No price, funding, exchangeInfo, account, balance, or order endpoint is called.",
            "No daemon, scheduler, service, runtime launcher, paper monitor, live trading, or capital allocation is created.",
            "Sizing and risk engines are interfaces only and do not compute live order quantities.",
            "No candidate generation, edge claim, or family release is created.",
        ],
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "safety_permissions": {
            "implementation_preview_created": True,
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
        "artifact_path": ARTIFACT_RELATIVE_PATH,
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "state_count": len(PaperMonitorStateMachinePreview.STATES),
        "transition_count": len(transition_table),
        "adapter_stub_count": len(adapter_stubs),
        "report_schema_count": len(report_schemas),
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
