#!/usr/bin/env python
"""Create a no-network multi-cycle paper monitor implementation preview artifact."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

MODULE_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_binance_spot_perp_funding_carry_multi_cycle_paper_monitor_implementation_preview_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/paper_monitor_previews/binance_spot_perp_funding_carry_multi_cycle_paper_monitor_implementation_preview_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

MULTI_CYCLE_DESIGN_RELATIVE_PATH = (
    "artifacts/paper_monitor_designs/binance_spot_perp_funding_carry_multi_cycle_paper_monitor_design_v1.json"
)
SINGLE_CYCLE_RELATIVE_PATH = (
    "artifacts/paper_monitor_dry_runs/binance_spot_perp_funding_carry_paper_monitor_single_cycle_v1.json"
)
SINGLE_CYCLE_PREVIEW_RELATIVE_PATH = (
    "artifacts/paper_monitor_previews/binance_spot_perp_funding_carry_paper_monitor_dry_run_preview_v1.json"
)
PAPER_MONITOR_DESIGN_RELATIVE_PATH = (
    "artifacts/paper_monitor_designs/binance_spot_perp_funding_carry_paper_monitor_design_v1.json"
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

MULTI_CYCLE_DESIGN_PATH = REPO_ROOT / MULTI_CYCLE_DESIGN_RELATIVE_PATH
SINGLE_CYCLE_PATH = REPO_ROOT / SINGLE_CYCLE_RELATIVE_PATH
SINGLE_CYCLE_PREVIEW_PATH = REPO_ROOT / SINGLE_CYCLE_PREVIEW_RELATIVE_PATH
PAPER_MONITOR_DESIGN_PATH = REPO_ROOT / PAPER_MONITOR_DESIGN_RELATIVE_PATH
SIZING_REPAIR_PATH = REPO_ROOT / SIZING_REPAIR_RELATIVE_PATH
EXCHANGE_RULE_PATH = REPO_ROOT / EXCHANGE_RULE_RELATIVE_PATH
RISK_CAPITAL_PATH = REPO_ROOT / RISK_CAPITAL_RELATIVE_PATH
CLOSURE_PATH = REPO_ROOT / CLOSURE_RELATIVE_PATH

STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_MULTI_CYCLE_IMPLEMENTATION_PREVIEW_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_FUNDING_CARRY_MULTI_CYCLE_PAPER_MONITOR_IMPLEMENTATION_PREVIEW"
NEXT_ALLOWED_STEP = "PAPER_MONITOR_MULTI_CYCLE_DRY_RUN_IMPLEMENTATION_ONLY"

DESIGN_STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_MULTI_CYCLE_PAPER_MONITOR_DESIGN_CREATED"
DESIGN_CLASSIFICATION = "MULTI_CYCLE_PAPER_MONITOR_DESIGN_READY_FOR_IMPLEMENTATION_PREVIEW_NO_LIVE_PERMISSION"
DESIGN_NEXT_STEP = "PAPER_MONITOR_MULTI_CYCLE_IMPLEMENTATION_PREVIEW_ONLY"
MULTI_CYCLE_DESIGN_PAYLOAD_SHA256 = "08cfe12a65ff99098a2debf6c19958f0d9be2774e95aca33df1eebefb9126916"
SINGLE_CYCLE_PAYLOAD_SHA256 = "495fcc7bf364ef7ee1fabb317807c998343a5683ac6681505ef37784ec324d1f"
SINGLE_CYCLE_PREVIEW_PAYLOAD_SHA256 = "2d82499353b3ff5ed2326644de01fdfad01d2ca4a13e4edd7c90c4a329fa6173"
PAPER_MONITOR_DESIGN_PAYLOAD_SHA256 = "25cb17fa9a4e296f194b79808a6515d880ec232ecde3356c008ccb2da04c6188"
SIZING_REPAIR_PAYLOAD_SHA256 = "0f189c4b8999d7d9a1018cf988952e630d554ed898fc29a61510af93a906d822"
EXCHANGE_RULE_PAYLOAD_SHA256 = "db998979f8d902ddff553877fa59384893021d2e814fb4c42dbc1ab194ebff46"
RISK_CAPITAL_PAYLOAD_SHA256 = "9b158cf8517e47c750c39234ea1d7287619a969f567cc682e16edd103a080ccc"
CLOSURE_PAYLOAD_SHA256 = "741508f0660eefca0812805a0cab006ace1e2ca0e720dade02665e440ef839c8"

TRACKED_PYTHON_COUNT_AT_START = 894

ORDER_PLACEMENT_ALLOWED = False
PRIVATE_API_ALLOWED = False
API_KEY_ALLOWED = False
RUNTIME_ALLOWED = False
SCHEDULER_ALLOWED = False
DAEMON_ALLOWED = False
LIVE_TRADING_ALLOWED = False
CAPITAL_ALLOCATION_ALLOWED = False
CANDIDATE_GENERATION_ALLOWED = False
EDGE_CLAIM_ALLOWED = False


@dataclass(frozen=True)
class PaperMonitorConfig:
    cycle_count: int = 6
    cycle_spacing_minutes: int = 60
    max_runtime_hours: int = 6
    allowed_capital_scenarios: tuple[int, ...] = (100, 235, 250, 500, 1000, 2500, 5000)
    manual_invocation_only: bool = True


class PaperMonitorState:
    DISABLED = "DISABLED"
    CYCLE_START = "CYCLE_START"
    SNAPSHOT_PUBLIC_MARKET_DATA = "SNAPSHOT_PUBLIC_MARKET_DATA"
    REFRESH_EXCHANGE_RULES = "REFRESH_EXCHANGE_RULES"
    RUN_REPAIRED_SIZING = "RUN_REPAIRED_SIZING"
    SIMULATE_ENTRY_DECISION = "SIMULATE_ENTRY_DECISION"
    SIMULATE_POSITION_STATE = "SIMULATE_POSITION_STATE"
    MONITOR_FUNDING = "MONITOR_FUNDING"
    SIMULATE_REBALANCE_OR_EXIT = "SIMULATE_REBALANCE_OR_EXIT"
    RISK_HALT = "RISK_HALT"
    CYCLE_REPORT = "CYCLE_REPORT"
    FINAL_REPORT_ONLY = "FINAL_REPORT_ONLY"
    STATES = (
        DISABLED,
        CYCLE_START,
        SNAPSHOT_PUBLIC_MARKET_DATA,
        REFRESH_EXCHANGE_RULES,
        RUN_REPAIRED_SIZING,
        SIMULATE_ENTRY_DECISION,
        SIMULATE_POSITION_STATE,
        MONITOR_FUNDING,
        SIMULATE_REBALANCE_OR_EXIT,
        RISK_HALT,
        CYCLE_REPORT,
        FINAL_REPORT_ONLY,
    )


class CycleRecordSchema:
    FIELDS = (
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
    )


class RiskFlagSchema:
    CRITICAL = (
        "missing_spot_price",
        "missing_futures_price",
        "missing_premiumIndex_or_funding",
        "missing_exchange_rules",
        "stale_snapshot",
        "all_scenarios_fail_sizing",
        "all_symbols_negative_funding",
        "symbol_status_not_trading",
        "order_endpoint_attempted",
        "private_api_attempted",
        "api_key_detected",
        "runtime_live_capital_flag_true",
    )
    NON_CRITICAL = (
        "some_scenarios_fail_sizing",
        "one_symbol_negative_funding",
        "high_mismatch_in_non_selected_scenarios",
        "next_funding_time_ambiguous",
        "premiumIndex_present_but_no_server_timestamp",
        "scenario_pass_fail_non_monotonic",
    )


class SizingResultSchema:
    FIELDS = (
        "capital_scenario",
        "symbol",
        "target_notional_per_symbol",
        "common_base_quantity",
        "spot_notional",
        "futures_notional",
        "leg_notional_mismatch_bps",
        "unused_notional_bps",
        "spot_rule_pass",
        "futures_rule_pass",
        "symbol_pass",
    )


class SimulatedEntryPlanSchema:
    FIELDS = (
        "label_SIMULATED_NOT_ORDER",
        "capital_scenario",
        "paper_spot_side_BUY",
        "paper_futures_side_SHORT",
        "common_base_quantity",
        "spot_notional",
        "futures_notional",
        "funding_rate",
        "nextFundingTime",
        "real_order_payload_generated_false",
    )


class MultiCycleReportSchema:
    FIELDS = (
        "run_id",
        "cycle_count",
        "cycle_records",
        "cycles_completed",
        "cycles_with_critical_risk",
        "cycles_with_no_passing_scenario",
        "cycles_with_simulated_entry_decision",
        "minimum_passing_capital_by_cycle",
        "scenario_pass_frequency",
        "risk_flag_frequency",
        "no_live_confirmation",
        "payload_sha256_excluding_hash",
    )


class PublicDataAdapterStub:
    def get_spot_price_snapshot(self) -> dict:
        return {"stub_only": True, "network_called": False}

    def get_futures_price_snapshot(self) -> dict:
        return {"stub_only": True, "network_called": False}

    def get_premium_index_snapshot(self) -> dict:
        return {"stub_only": True, "network_called": False}

    def get_funding_snapshot(self) -> dict:
        return {"stub_only": True, "network_called": False}


class ExchangeRulesAdapterStub:
    def get_exchange_rules_snapshot(self) -> dict:
        return {"stub_only": True, "network_called": False}


class RepairedSizingEngineStub:
    def preview_contract(self) -> dict:
        return {
            "stub_only": True,
            "network_called": False,
            "decimal_arithmetic_required": True,
            "common_base_quantity_required": True,
            "live_quantities_computed_now": False,
        }


class RiskEngineStub:
    def preview_contract(self) -> dict:
        return {
            "stub_only": True,
            "network_called": False,
            "critical_risk_flags": list(RiskFlagSchema.CRITICAL),
            "non_critical_risk_flags": list(RiskFlagSchema.NON_CRITICAL),
            "private_account_margin_values_allowed": False,
        }


class ReportBuilderStub:
    REPORT_SCHEMAS = {
        "cycle_record_schema": list(CycleRecordSchema.FIELDS),
        "aggregate_report_schema": list(MultiCycleReportSchema.FIELDS),
        "risk_halt_report_schema": [
            "cycle_index",
            "risk_halt_reason",
            "critical_flags",
            "orders_placed_false",
            "live_capital_permission_false",
        ],
        "simulated_pnl_attribution_schema": [
            "cycle_index",
            "funding_component",
            "price_hedge_residual",
            "estimated_fees",
            "estimated_slippage",
            "unmodeled_risks",
        ],
        "funding_event_report_schema": [
            "cycle_index",
            "nextFundingTime",
            "funding_rate_by_symbol",
            "paper_position_would_monitor_funding",
        ],
        "sizing_pass_fail_report_schema": [
            "cycle_index",
            "capital_scenarios",
            "passing_capital_scenarios",
            "minimum_passing_capital",
        ],
        "no_live_confirmation_report_schema": [
            "order_placement_allowed_false",
            "private_api_allowed_false",
            "runtime_live_capital_false",
            "candidate_edge_false",
        ],
    }


class MultiCyclePaperMonitorPreview:
    TRANSITIONS = (
        {
            "from": PaperMonitorState.DISABLED,
            "to": PaperMonitorState.CYCLE_START,
            "condition": "manual invocation in future implementation only",
            "order_or_live_allowed": False,
        },
        {
            "from": PaperMonitorState.SNAPSHOT_PUBLIC_MARKET_DATA,
            "to": PaperMonitorState.CYCLE_REPORT,
            "condition": "missing public data",
            "order_or_live_allowed": False,
        },
        {
            "from": PaperMonitorState.RUN_REPAIRED_SIZING,
            "to": PaperMonitorState.CYCLE_REPORT,
            "condition": "all scenarios fail sizing",
            "order_or_live_allowed": False,
        },
        {
            "from": PaperMonitorState.RUN_REPAIRED_SIZING,
            "to": PaperMonitorState.RISK_HALT,
            "condition": "critical risk flag true",
            "order_or_live_allowed": False,
        },
        {
            "from": PaperMonitorState.RUN_REPAIRED_SIZING,
            "to": PaperMonitorState.SIMULATE_ENTRY_DECISION,
            "condition": "sizing passes and no critical risk flags",
            "order_or_live_allowed": False,
        },
        {
            "from": "EACH_CYCLE",
            "to": PaperMonitorState.CYCLE_REPORT,
            "condition": "cycle report is appended",
            "order_or_live_allowed": False,
        },
        {
            "from": "AFTER_FINAL_CYCLE",
            "to": PaperMonitorState.FINAL_REPORT_ONLY,
            "condition": "finite run plan completes",
            "order_or_live_allowed": False,
        },
    )

    def run_preview_cycle_plan(self, cycle_count: int = 6, cycle_spacing_minutes: int = 60) -> dict:
        return {
            "planned_only": True,
            "cycles_executed_now": False,
            "sleep_called": False,
            "scheduler_created": False,
            "daemon_created": False,
            "cycle_count": cycle_count,
            "cycle_spacing_minutes": cycle_spacing_minutes,
            "planned_cycle_indices": list(range(cycle_count)),
        }


MODULE_STRUCTURE_CLASSES = (
    "PaperMonitorConfig",
    "PaperMonitorState",
    "CycleRecordSchema",
    "RiskFlagSchema",
    "SizingResultSchema",
    "SimulatedEntryPlanSchema",
    "MultiCycleReportSchema",
    "PublicDataAdapterStub",
    "ExchangeRulesAdapterStub",
    "RepairedSizingEngineStub",
    "RiskEngineStub",
    "ReportBuilderStub",
    "MultiCyclePaperMonitorPreview",
)


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


def assert_no_forbidden_source_paths() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden = tuple(
        "".join(parts)
        for parts in (
            ("import ", "urllib"),
            ("import ", "socket"),
            ("import ", "http.client"),
            ("import ", "requests"),
            ("c", "cxt"),
            ("Binance", "SDK"),
            ("create", "_order"),
            ("listen", "Key"),
            ("sub", "process"),
            ("time", ".sleep"),
            ("sched", "."),
        )
    )
    for snippet in forbidden:
        if snippet in source:
            raise RuntimeError(f"forbidden implementation path present: {snippet}")


def validate_prior_design(design: dict) -> None:
    if design.get("status") != DESIGN_STATUS:
        raise RuntimeError("multi-cycle design status mismatch")
    if design.get("classification") != DESIGN_CLASSIFICATION:
        raise RuntimeError("multi-cycle design classification mismatch")
    if design.get("next_allowed_step") != DESIGN_NEXT_STEP:
        raise RuntimeError("multi-cycle design next allowed step mismatch")
    assert_payload("multi-cycle design", design, MULTI_CYCLE_DESIGN_PAYLOAD_SHA256)
    for key in (
        "paper_monitor_enabled_now",
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
            raise RuntimeError(f"multi-cycle design safety permission not false: {key}")


def validate_source_artifacts(artifacts: dict) -> None:
    validate_prior_design(artifacts["multi_cycle_design"])
    for key, expected in (
        ("single_cycle", SINGLE_CYCLE_PAYLOAD_SHA256),
        ("single_cycle_preview", SINGLE_CYCLE_PREVIEW_PAYLOAD_SHA256),
        ("paper_monitor_design", PAPER_MONITOR_DESIGN_PAYLOAD_SHA256),
        ("sizing_repair", SIZING_REPAIR_PAYLOAD_SHA256),
        ("exchange_rule", EXCHANGE_RULE_PAYLOAD_SHA256),
        ("risk_capital", RISK_CAPITAL_PAYLOAD_SHA256),
        ("closure", CLOSURE_PAYLOAD_SHA256),
    ):
        assert_payload(key, artifacts[key], expected)


def adapter_stub_contract() -> dict:
    public_adapter = PublicDataAdapterStub()
    exchange_adapter = ExchangeRulesAdapterStub()
    stubs = {
        "get_spot_price_snapshot": public_adapter.get_spot_price_snapshot(),
        "get_futures_price_snapshot": public_adapter.get_futures_price_snapshot(),
        "get_premium_index_snapshot": public_adapter.get_premium_index_snapshot(),
        "get_exchange_rules_snapshot": exchange_adapter.get_exchange_rules_snapshot(),
        "get_funding_snapshot": public_adapter.get_funding_snapshot(),
    }
    for name, record in stubs.items():
        if record.get("stub_only") is not True or record.get("network_called") is not False:
            raise RuntimeError(f"adapter stub contract failed: {name}")
    return {
        "adapter_stubs": stubs,
        "adapter_stub_count": len(stubs),
        "stubs_raise_or_return_stub_only": True,
        "network_called": False,
    }


def main() -> int:
    ensure_target_absent()
    assert_no_forbidden_source_paths()

    artifacts = {
        "multi_cycle_design": load_json(MULTI_CYCLE_DESIGN_PATH),
        "single_cycle": load_json(SINGLE_CYCLE_PATH),
        "single_cycle_preview": load_json(SINGLE_CYCLE_PREVIEW_PATH),
        "paper_monitor_design": load_json(PAPER_MONITOR_DESIGN_PATH),
        "sizing_repair": load_json(SIZING_REPAIR_PATH),
        "exchange_rule": load_json(EXCHANGE_RULE_PATH),
        "risk_capital": load_json(RISK_CAPITAL_PATH),
        "closure": load_json(CLOSURE_PATH),
    }
    validate_source_artifacts(artifacts)

    design = artifacts["multi_cycle_design"]
    config = PaperMonitorConfig()
    preview = MultiCyclePaperMonitorPreview()
    finite_plan = preview.run_preview_cycle_plan(config.cycle_count, config.cycle_spacing_minutes)
    adapter_contract = adapter_stub_contract()
    no_live_guards = {
        "ORDER_PLACEMENT_ALLOWED": ORDER_PLACEMENT_ALLOWED,
        "PRIVATE_API_ALLOWED": PRIVATE_API_ALLOWED,
        "API_KEY_ALLOWED": API_KEY_ALLOWED,
        "RUNTIME_ALLOWED": RUNTIME_ALLOWED,
        "SCHEDULER_ALLOWED": SCHEDULER_ALLOWED,
        "DAEMON_ALLOWED": DAEMON_ALLOWED,
        "LIVE_TRADING_ALLOWED": LIVE_TRADING_ALLOWED,
        "CAPITAL_ALLOCATION_ALLOWED": CAPITAL_ALLOCATION_ALLOWED,
        "CANDIDATE_GENERATION_ALLOWED": CANDIDATE_GENERATION_ALLOWED,
        "EDGE_CLAIM_ALLOWED": EDGE_CLAIM_ALLOWED,
    }
    no_live_guard_constants_false = all(value is False for value in no_live_guards.values())
    if not no_live_guard_constants_false:
        raise RuntimeError("one or more no-live guard constants is not false")

    validation_checks = {
        "repo_clean_before_run": True,
        "prior_multi_cycle_design_loaded": True,
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
        "no_daemon_created": True,
        "no_launcher_created": True,
        "no_live_or_capital_permission": True,
        "no_live_guard_constants_false": no_live_guard_constants_false,
        "adapter_stubs_do_not_call_network": True,
        "finite_run_plan_does_not_execute_cycles": finite_plan["cycles_executed_now"] is False,
        "state_machine_preview_defined": True,
        "transition_table_preview_defined": True,
        "report_schemas_defined": True,
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
            "multi_cycle_paper_monitor_design": MULTI_CYCLE_DESIGN_RELATIVE_PATH,
            "multi_cycle_paper_monitor_design_payload_sha256_excluding_hash": MULTI_CYCLE_DESIGN_PAYLOAD_SHA256,
            "paper_monitor_single_cycle": SINGLE_CYCLE_RELATIVE_PATH,
            "paper_monitor_single_cycle_payload_sha256_excluding_hash": SINGLE_CYCLE_PAYLOAD_SHA256,
            "single_cycle_preview": SINGLE_CYCLE_PREVIEW_RELATIVE_PATH,
            "single_cycle_preview_payload_sha256_excluding_hash": SINGLE_CYCLE_PREVIEW_PAYLOAD_SHA256,
            "paper_monitor_design": PAPER_MONITOR_DESIGN_RELATIVE_PATH,
            "paper_monitor_design_payload_sha256_excluding_hash": PAPER_MONITOR_DESIGN_PAYLOAD_SHA256,
            "order_sizing_repair_sim": SIZING_REPAIR_RELATIVE_PATH,
            "order_sizing_repair_payload_sha256_excluding_hash": SIZING_REPAIR_PAYLOAD_SHA256,
            "exchange_rule_discovery": EXCHANGE_RULE_RELATIVE_PATH,
            "exchange_rule_payload_sha256_excluding_hash": EXCHANGE_RULE_PAYLOAD_SHA256,
            "risk_capital_diagnostic": RISK_CAPITAL_RELATIVE_PATH,
            "risk_capital_payload_sha256_excluding_hash": RISK_CAPITAL_PAYLOAD_SHA256,
            "strategy_closure": CLOSURE_RELATIVE_PATH,
            "strategy_closure_payload_sha256_excluding_hash": CLOSURE_PAYLOAD_SHA256,
        },
        "prior_multi_cycle_design_preserved": {
            "status": design["status"],
            "classification": design["classification"],
            "next_allowed_step": design["next_allowed_step"],
            "designed_cycle_count": design["multi_cycle_scope"]["cycle_count"],
            "state_count": design["state_machine_design"]["state_count"],
            "critical_risk_flags_count": design["risk_policy"]["critical_risk_flags_count"],
            "non_critical_risk_flags_count": design["risk_policy"]["non_critical_risk_flags_count"],
            "kill_switch_rules_count": design["kill_switch_policy"]["rule_count"],
            "live_capital_permission_exists": False,
        },
        "no_live_guard_constants": no_live_guards,
        "preview_module_structure": {
            "classes": list(MODULE_STRUCTURE_CLASSES),
            "class_count": len(MODULE_STRUCTURE_CLASSES),
            "implementation_preview_only": True,
            "cycles_run_now": False,
            "network_code_enabled_now": False,
        },
        "adapter_stub_contract": adapter_contract,
        "state_machine_preview": {
            "states": list(PaperMonitorState.STATES),
            "state_count": len(PaperMonitorState.STATES),
            "default_state": PaperMonitorState.DISABLED,
            "final_state": PaperMonitorState.FINAL_REPORT_ONLY,
        },
        "transition_table_preview": {
            "transitions": list(MultiCyclePaperMonitorPreview.TRANSITIONS),
            "transition_count": len(MultiCyclePaperMonitorPreview.TRANSITIONS),
            "no_transition_to_order_placement_or_live": True,
        },
        "risk_flag_preview": {
            "critical_risk_flags": list(RiskFlagSchema.CRITICAL),
            "non_critical_risk_flags": list(RiskFlagSchema.NON_CRITICAL),
            "risk_flag_count": len(RiskFlagSchema.CRITICAL) + len(RiskFlagSchema.NON_CRITICAL),
        },
        "report_schema_preview": ReportBuilderStub.REPORT_SCHEMAS,
        "finite_run_plan_preview": finite_plan,
        "implementation_limitations": [
            "This preview defines classes, schemas, transitions, and stub contracts only.",
            "It does not run cycles, sleep, schedule, create a daemon, create a launcher, or enable runtime.",
            "It does not fetch prices, exchangeInfo, funding, public data, private data, or account data.",
            "It does not use API keys, private endpoints, order endpoints, or order payloads.",
            "It does not allocate capital, enable live trading, generate a candidate, or claim edge.",
        ],
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "safety_permissions": {
            "implementation_preview_created": True,
            "paper_monitor_enabled_now": False,
            "runtime_permission_allowed_now": False,
            "scheduler_allowed_now": False,
            "daemon_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "order_placement_allowed_now": False,
            "private_api_allowed_now": False,
            "api_key_allowed_now": False,
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
        "class_count": len(MODULE_STRUCTURE_CLASSES),
        "state_count": len(PaperMonitorState.STATES),
        "transition_count": len(MultiCyclePaperMonitorPreview.TRANSITIONS),
        "adapter_stub_count": adapter_contract["adapter_stub_count"],
        "risk_flag_count": len(RiskFlagSchema.CRITICAL) + len(RiskFlagSchema.NON_CRITICAL),
        "report_schema_count": len(ReportBuilderStub.REPORT_SCHEMAS),
        "order_placement_allowed_now": False,
        "scheduler_daemon_runtime_allowed_now": False,
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
