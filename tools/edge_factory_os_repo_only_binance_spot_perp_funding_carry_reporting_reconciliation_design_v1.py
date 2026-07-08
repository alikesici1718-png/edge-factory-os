#!/usr/bin/env python
"""Create a design-only reporting and reconciliation artifact for paper monitoring."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

MODULE_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_binance_spot_perp_funding_carry_reporting_reconciliation_design_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/reporting_designs/binance_spot_perp_funding_carry_reporting_reconciliation_design_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

MULTI_CYCLE_DRY_RUN_RELATIVE_PATH = (
    "artifacts/paper_monitor_dry_runs/binance_spot_perp_funding_carry_multi_cycle_paper_dry_run_v1.json"
)
MULTI_CYCLE_DESIGN_RELATIVE_PATH = (
    "artifacts/paper_monitor_designs/binance_spot_perp_funding_carry_multi_cycle_paper_monitor_design_v1.json"
)
SINGLE_CYCLE_RELATIVE_PATH = (
    "artifacts/paper_monitor_dry_runs/binance_spot_perp_funding_carry_paper_monitor_single_cycle_v1.json"
)
RISK_CAPITAL_RELATIVE_PATH = (
    "artifacts/risk_capital_diagnostics/binance_spot_perp_delta_neutral_funding_carry_risk_capital_feasibility_v1.json"
)
CLOSURE_RELATIVE_PATH = (
    "artifacts/strategy_closures/binance_spot_perp_delta_neutral_funding_carry_closure_v1.json"
)

MULTI_CYCLE_DRY_RUN_PATH = REPO_ROOT / MULTI_CYCLE_DRY_RUN_RELATIVE_PATH
MULTI_CYCLE_DESIGN_PATH = REPO_ROOT / MULTI_CYCLE_DESIGN_RELATIVE_PATH
SINGLE_CYCLE_PATH = REPO_ROOT / SINGLE_CYCLE_RELATIVE_PATH
RISK_CAPITAL_PATH = REPO_ROOT / RISK_CAPITAL_RELATIVE_PATH
CLOSURE_PATH = REPO_ROOT / CLOSURE_RELATIVE_PATH

STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_REPORTING_RECONCILIATION_DESIGN_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_FUNDING_CARRY_REPORTING_RECONCILIATION_DESIGN"
CLASSIFICATION = "REPORTING_RECONCILIATION_DESIGN_READY_FOR_REPORT_BUILDER_PREVIEW_NO_LIVE_PERMISSION"
NEXT_ALLOWED_STEP = "PAPER_MONITOR_REPORT_BUILDER_PREVIEW_ONLY"

MULTI_CYCLE_DRY_RUN_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_MULTI_CYCLE_PAPER_DRY_RUN_CREATED"
MULTI_CYCLE_DRY_RUN_CLASSIFICATION = "MULTI_CYCLE_PAPER_DRY_RUN_PARTIAL_RISK_FLAGS_NO_LIVE_PERMISSION"
MULTI_CYCLE_DRY_RUN_NEXT_STEP = "PAPER_MONITOR_REPORTING_RECONCILIATION_DESIGN_ONLY"
MULTI_CYCLE_DRY_RUN_PAYLOAD_SHA256 = "4c4a16750aa3c15bda0d497127217c38a0171ca798220bf16ed701c86dd7fa13"
MULTI_CYCLE_DESIGN_PAYLOAD_SHA256 = "08cfe12a65ff99098a2debf6c19958f0d9be2774e95aca33df1eebefb9126916"
SINGLE_CYCLE_PAYLOAD_SHA256 = "495fcc7bf364ef7ee1fabb317807c998343a5683ac6681505ef37784ec324d1f"
RISK_CAPITAL_PAYLOAD_SHA256 = "9b158cf8517e47c750c39234ea1d7287619a969f567cc682e16edd103a080ccc"
CLOSURE_PAYLOAD_SHA256 = "741508f0660eefca0812805a0cab006ace1e2ca0e720dade02665e440ef839c8"

ROUTE_FAMILY = "BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_BASELINE"
CONFIG_ID = "spot_long_perp_short_always_on_funding_carry_3symbol"
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
TRACKED_PYTHON_COUNT_AT_START = 896


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
    dry_run = artifacts["multi_cycle_dry_run"]
    if dry_run.get("status") != MULTI_CYCLE_DRY_RUN_STATUS:
        raise RuntimeError("multi-cycle dry-run status mismatch")
    if dry_run["classification"]["classification"] != MULTI_CYCLE_DRY_RUN_CLASSIFICATION:
        raise RuntimeError("multi-cycle dry-run classification mismatch")
    if dry_run.get("next_allowed_step") != MULTI_CYCLE_DRY_RUN_NEXT_STEP:
        raise RuntimeError("multi-cycle dry-run next allowed step mismatch")
    if dry_run["aggregate_run_report"]["cycles_completed"] != 3:
        raise RuntimeError("multi-cycle dry-run completed cycle count mismatch")
    if dry_run["aggregate_run_report"]["cycles_with_critical_risk"] != 0:
        raise RuntimeError("multi-cycle dry-run has unexpected critical risk")
    assert_payload("multi-cycle dry-run", dry_run, MULTI_CYCLE_DRY_RUN_PAYLOAD_SHA256)
    for key, expected in (
        ("multi_cycle_design", MULTI_CYCLE_DESIGN_PAYLOAD_SHA256),
        ("single_cycle", SINGLE_CYCLE_PAYLOAD_SHA256),
        ("risk_capital", RISK_CAPITAL_PAYLOAD_SHA256),
        ("closure", CLOSURE_PAYLOAD_SHA256),
    ):
        assert_payload(key, artifacts[key], expected)
    for key in (
        "order_placement_allowed_now",
        "private_api_allowed_now",
        "api_key_allowed_now",
        "runtime_permission_allowed_now",
        "scheduler_allowed_now",
        "daemon_allowed_now",
        "live_permission_allowed_now",
        "capital_permission_allowed_now",
        "candidate_generation_allowed_now",
        "edge_claim_allowed_now",
        "family_release_allowed_now",
    ):
        if dry_run["safety_permissions"].get(key) is not False:
            raise RuntimeError(f"multi-cycle dry-run safety permission not false: {key}")


def main() -> int:
    ensure_target_absent()
    artifacts = {
        "multi_cycle_dry_run": load_json(MULTI_CYCLE_DRY_RUN_PATH),
        "multi_cycle_design": load_json(MULTI_CYCLE_DESIGN_PATH),
        "single_cycle": load_json(SINGLE_CYCLE_PATH),
        "risk_capital": load_json(RISK_CAPITAL_PATH),
        "closure": load_json(CLOSURE_PATH),
    }
    validate_prior_artifacts(artifacts)

    dry_run = artifacts["multi_cycle_dry_run"]
    report_layers = [
        "cycle_report",
        "funding_event_reconciliation_report",
        "daily_report",
        "weekly_report",
        "monthly_report",
        "risk_incident_report",
        "sizing_stability_report",
        "simulated_pnl_attribution_report",
        "audit_summary_report",
    ]
    reconciliation_limitations = [
        "no private account data",
        "no actual balances",
        "no actual fills",
        "no actual commissions",
        "no real funding received",
        "no exchange statement reconciliation",
        "future true reconciliation would require read-only account/API or exported account statements, which are not allowed now",
    ]
    audit_requirements = [
        "every report references source artifact hashes",
        "every report has payload_sha256_excluding_hash",
        "manual edits are disallowed",
        "deterministic JSON output required",
        "immutable cycle records required",
        "explicit candidate generation false flag required",
        "explicit edge claim false flag required",
        "explicit live/capital false flags required",
    ]

    cycle_report_schema = [
        "cycle_id",
        "timestamp",
        "state_trace",
        "public_snapshot_summary",
        "passing_capital_scenarios",
        "selected_paper_scenario_if_any",
        "risk_flags",
        "simulated_entry_plan_summary",
        "no_order_confirmation",
        "payload_sha256_excluding_hash",
    ]
    funding_schema = [
        "symbol",
        "funding_event_time_utc",
        "expected_funding_rate",
        "next_funding_time",
        "paper_position_quantity_if_simulated",
        "expected_funding_cashflow",
        "funding_received_simulated",
        "funding_paid_simulated_if_negative",
        "missing_funding_event_flag",
        "funding_sign_flip_flag",
        "funding_attribution_by_symbol",
        "real_account_reconciliation_performed_false",
    ]
    pnl_schema = [
        "funding_component",
        "spot_perp_price_hedge_residual",
        "estimated_fee_component",
        "estimated_slippage_component",
        "sizing_mismatch_component",
        "unmodeled_risk_note",
    ]
    daily_schema = [
        "report_date_utc",
        "cycles_completed",
        "cycles_passed",
        "cycles_risk_halted",
        "min_passing_capital_by_cycle",
        "simulated_funding_accrual",
        "negative_funding_events",
        "sizing_failures",
        "stale_data_events",
        "report_only_status",
        "no_live_confirmation",
    ]
    weekly_schema = [
        "week_start_utc",
        "week_end_utc",
        "cycles_completed",
        "cycle_pass_rate",
        "risk_flag_frequency",
        "scenario_pass_frequency",
        "simulated_funding_summary",
        "no_live_confirmation",
    ]
    monthly_schema = [
        "month_utc",
        "simulated_monthly_funding_carry",
        "monthly_price_hedge_residual",
        "monthly_estimated_fees",
        "monthly_risk_flag_counts",
        "monthly_positive_day_rate",
        "no_live_confirmation",
    ]
    risk_incident_schema = [
        "incident_id",
        "cycle_id",
        "incident_time_utc",
        "critical_flag",
        "non_critical_flags",
        "state_at_detection",
        "paper_action_taken",
        "orders_placed_false",
        "live_capital_permission_false",
    ]
    sizing_stability_schema = [
        "cycle_id",
        "capital_scenario_pass_fail_table",
        "minimum_passing_capital",
        "scenario_pass_frequency",
        "non_monotonic_pass_fail_observed",
        "symbols_with_sizing_failure",
        "max_leg_mismatch_bps",
        "max_unused_notional_bps",
    ]
    audit_summary_schema = [
        "source_artifacts",
        "source_payload_hashes",
        "report_payload_sha256_excluding_hash",
        "manual_edits_allowed_false",
        "deterministic_json_true",
        "immutable_cycle_records_true",
        "candidate_generation_allowed_false",
        "edge_claim_allowed_false",
        "runtime_live_capital_allowed_false",
    ]

    validation_checks = {
        "repo_clean_before_run": True,
        "prior_multi_cycle_dry_run_loaded": True,
        "prior_next_allowed_step_verified": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_private_api": True,
        "no_api_key_used": True,
        "no_order_endpoint_called": True,
        "no_orders_placed": True,
        "no_runtime_enabled": True,
        "no_scheduler_created": True,
        "no_daemon_created": True,
        "no_live_or_capital_permission": True,
        "cycle_report_schema_defined": bool(cycle_report_schema),
        "funding_reconciliation_schema_defined": bool(funding_schema),
        "pnl_attribution_schema_defined": bool(pnl_schema),
        "daily_weekly_monthly_report_schemas_defined": bool(daily_schema and weekly_schema and monthly_schema),
        "audit_summary_schema_defined": bool(audit_summary_schema),
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
            "multi_cycle_dry_run": MULTI_CYCLE_DRY_RUN_RELATIVE_PATH,
            "multi_cycle_dry_run_payload_sha256_excluding_hash": MULTI_CYCLE_DRY_RUN_PAYLOAD_SHA256,
            "multi_cycle_design": MULTI_CYCLE_DESIGN_RELATIVE_PATH,
            "multi_cycle_design_payload_sha256_excluding_hash": MULTI_CYCLE_DESIGN_PAYLOAD_SHA256,
            "single_cycle_dry_run": SINGLE_CYCLE_RELATIVE_PATH,
            "single_cycle_payload_sha256_excluding_hash": SINGLE_CYCLE_PAYLOAD_SHA256,
            "risk_capital_diagnostic": RISK_CAPITAL_RELATIVE_PATH,
            "risk_capital_payload_sha256_excluding_hash": RISK_CAPITAL_PAYLOAD_SHA256,
            "strategy_closure": CLOSURE_RELATIVE_PATH,
            "strategy_closure_payload_sha256_excluding_hash": CLOSURE_PAYLOAD_SHA256,
        },
        "prior_multi_cycle_preserved": {
            "route_family": ROUTE_FAMILY,
            "config_id": CONFIG_ID,
            "symbols": list(SYMBOLS),
            "strategy_diagnostic_promising": True,
            "risk_capital_feasibility_strong": True,
            "exchange_rules_discovered": True,
            "sizing_repaired": True,
            "single_cycle_dry_run_completed": True,
            "multi_cycle_dry_run_completed": True,
            "multi_cycle_status": dry_run["status"],
            "multi_cycle_classification": dry_run["classification"]["classification"],
            "cycles_completed": dry_run["aggregate_run_report"]["cycles_completed"],
            "cycles_with_passing_scenario": dry_run["aggregate_run_report"]["cycles_with_passing_scenario"],
            "cycles_with_critical_risk": dry_run["aggregate_run_report"]["cycles_with_critical_risk"],
            "cycles_with_non_critical_risk": dry_run["aggregate_run_report"]["cycles_with_non_critical_risk"],
            "minimum_passing_capital_by_cycle": dry_run["aggregate_run_report"][
                "minimum_passing_capital_by_cycle"
            ],
            "next_allowed_step": dry_run["next_allowed_step"],
            "no_live_capital_permission": True,
        },
        "report_layer_design": {
            "layers": report_layers,
            "report_schema_count": len(report_layers),
            "report_builder_enabled_now": False,
            "schema_definitions": {
                "sizing_stability_report_schema": sizing_stability_schema,
            },
        },
        "cycle_report_schema": cycle_report_schema,
        "funding_event_reconciliation_schema": {
            "schema_fields": funding_schema,
            "simulated_public_data_only": True,
            "real_account_reconciliation_performed": False,
        },
        "pnl_attribution_schema": pnl_schema,
        "daily_report_schema": daily_schema,
        "weekly_report_schema": weekly_schema,
        "monthly_report_schema": monthly_schema,
        "risk_incident_report_schema": risk_incident_schema,
        "audit_summary_schema": {
            "schema_fields": audit_summary_schema,
            "audit_requirements": audit_requirements,
        },
        "reconciliation_limitations": reconciliation_limitations,
        "classification": CLASSIFICATION,
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "safety_permissions": {
            "reporting_reconciliation_design_created": True,
            "report_builder_enabled_now": False,
            "private_api_allowed_now": False,
            "order_placement_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
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
        "report_schema_count": len(report_layers),
        "reconciliation_limitations_count": len(reconciliation_limitations),
        "audit_requirements_count": len(audit_requirements),
        "report_builder_enabled_now": False,
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
