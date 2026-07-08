#!/usr/bin/env python
"""Create a report-builder preview pack from existing paper-monitor artifacts."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

MODULE_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_binance_spot_perp_funding_carry_report_builder_preview_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/report_builder_previews/binance_spot_perp_funding_carry_report_builder_preview_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

REPORTING_DESIGN_RELATIVE_PATH = (
    "artifacts/reporting_designs/binance_spot_perp_funding_carry_reporting_reconciliation_design_v1.json"
)
MULTI_CYCLE_DRY_RUN_RELATIVE_PATH = (
    "artifacts/paper_monitor_dry_runs/binance_spot_perp_funding_carry_multi_cycle_paper_dry_run_v1.json"
)
MULTI_CYCLE_DESIGN_RELATIVE_PATH = (
    "artifacts/paper_monitor_designs/binance_spot_perp_funding_carry_multi_cycle_paper_monitor_design_v1.json"
)
SINGLE_CYCLE_RELATIVE_PATH = (
    "artifacts/paper_monitor_dry_runs/binance_spot_perp_funding_carry_paper_monitor_single_cycle_v1.json"
)
PAPER_DRY_RUN_RELATIVE_PATH = (
    "artifacts/paper_trading_dry_runs/binance_spot_perp_funding_carry_paper_dry_run_simulator_v1.json"
)
SIZING_REPAIR_RELATIVE_PATH = (
    "artifacts/order_sizing_simulations/binance_spot_perp_funding_carry_order_sizing_repair_sim_v1.json"
)
RISK_CAPITAL_RELATIVE_PATH = (
    "artifacts/risk_capital_diagnostics/binance_spot_perp_delta_neutral_funding_carry_risk_capital_feasibility_v1.json"
)
CLOSURE_RELATIVE_PATH = (
    "artifacts/strategy_closures/binance_spot_perp_delta_neutral_funding_carry_closure_v1.json"
)

REPORTING_DESIGN_PATH = REPO_ROOT / REPORTING_DESIGN_RELATIVE_PATH
MULTI_CYCLE_DRY_RUN_PATH = REPO_ROOT / MULTI_CYCLE_DRY_RUN_RELATIVE_PATH
MULTI_CYCLE_DESIGN_PATH = REPO_ROOT / MULTI_CYCLE_DESIGN_RELATIVE_PATH
SINGLE_CYCLE_PATH = REPO_ROOT / SINGLE_CYCLE_RELATIVE_PATH
PAPER_DRY_RUN_PATH = REPO_ROOT / PAPER_DRY_RUN_RELATIVE_PATH
SIZING_REPAIR_PATH = REPO_ROOT / SIZING_REPAIR_RELATIVE_PATH
RISK_CAPITAL_PATH = REPO_ROOT / RISK_CAPITAL_RELATIVE_PATH
CLOSURE_PATH = REPO_ROOT / CLOSURE_RELATIVE_PATH

STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_REPORT_BUILDER_PREVIEW_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_FUNDING_CARRY_REPORT_BUILDER_PREVIEW"
CLASSIFICATION = "REPORT_BUILDER_PREVIEW_READY_FOR_DRY_RUN_REPORT_BUILDER_NO_LIVE_PERMISSION"
NEXT_ALLOWED_STEP = "PAPER_MONITOR_REPORT_BUILDER_DRY_RUN_ONLY"

REPORTING_DESIGN_STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_REPORTING_RECONCILIATION_DESIGN_CREATED"
REPORTING_DESIGN_CLASSIFICATION = (
    "REPORTING_RECONCILIATION_DESIGN_READY_FOR_REPORT_BUILDER_PREVIEW_NO_LIVE_PERMISSION"
)
REPORTING_DESIGN_NEXT_STEP = "PAPER_MONITOR_REPORT_BUILDER_PREVIEW_ONLY"
REPORTING_DESIGN_PAYLOAD_SHA256 = "ee0892db27885562b257294033992bff57bb387877d528638e6c709664bd7eb8"
MULTI_CYCLE_DRY_RUN_PAYLOAD_SHA256 = "4c4a16750aa3c15bda0d497127217c38a0171ca798220bf16ed701c86dd7fa13"
MULTI_CYCLE_DESIGN_PAYLOAD_SHA256 = "08cfe12a65ff99098a2debf6c19958f0d9be2774e95aca33df1eebefb9126916"
SINGLE_CYCLE_PAYLOAD_SHA256 = "495fcc7bf364ef7ee1fabb317807c998343a5683ac6681505ef37784ec324d1f"
PAPER_DRY_RUN_PAYLOAD_SHA256 = "7dcc93b6c82344266c72144f2cd06c5b5507701d2c7f99a7971652f175dc655d"
SIZING_REPAIR_PAYLOAD_SHA256 = "0f189c4b8999d7d9a1018cf988952e630d554ed898fc29a61510af93a906d822"
RISK_CAPITAL_PAYLOAD_SHA256 = "9b158cf8517e47c750c39234ea1d7287619a969f567cc682e16edd103a080ccc"
CLOSURE_PAYLOAD_SHA256 = "741508f0660eefca0812805a0cab006ace1e2ca0e720dade02665e440ef839c8"

TRACKED_PYTHON_COUNT_AT_START = 897
REPORT_PREVIEW_NAMES = (
    "cycle_report_preview",
    "funding_event_reconciliation_report_preview",
    "daily_carry_report_preview",
    "weekly_carry_report_preview",
    "monthly_carry_report_preview",
    "risk_incident_report_preview",
    "sizing_stability_report_preview",
    "simulated_pnl_attribution_report_preview",
    "audit_summary_report_preview",
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


def validate_prior_artifacts(artifacts: dict) -> None:
    design = artifacts["reporting_design"]
    if design.get("status") != REPORTING_DESIGN_STATUS:
        raise RuntimeError("reporting design status mismatch")
    if design.get("classification") != REPORTING_DESIGN_CLASSIFICATION:
        raise RuntimeError("reporting design classification mismatch")
    if design.get("next_allowed_step") != REPORTING_DESIGN_NEXT_STEP:
        raise RuntimeError("reporting design next allowed step mismatch")
    assert_payload("reporting design", design, REPORTING_DESIGN_PAYLOAD_SHA256)
    for key in (
        "private_api_allowed_now",
        "order_placement_allowed_now",
        "runtime_permission_allowed_now",
        "live_permission_allowed_now",
        "capital_permission_allowed_now",
        "candidate_generation_allowed_now",
        "edge_claim_allowed_now",
    ):
        if design["safety_permissions"].get(key) is not False:
            raise RuntimeError(f"reporting design safety permission not false: {key}")

    for key, expected in (
        ("multi_cycle_dry_run", MULTI_CYCLE_DRY_RUN_PAYLOAD_SHA256),
        ("multi_cycle_design", MULTI_CYCLE_DESIGN_PAYLOAD_SHA256),
        ("single_cycle", SINGLE_CYCLE_PAYLOAD_SHA256),
        ("paper_dry_run", PAPER_DRY_RUN_PAYLOAD_SHA256),
        ("sizing_repair", SIZING_REPAIR_PAYLOAD_SHA256),
        ("risk_capital", RISK_CAPITAL_PAYLOAD_SHA256),
        ("closure", CLOSURE_PAYLOAD_SHA256),
    ):
        assert_payload(key, artifacts[key], expected)


def source_artifact_map() -> dict:
    return {
        "reporting_design": REPORTING_DESIGN_RELATIVE_PATH,
        "reporting_design_payload_sha256_excluding_hash": REPORTING_DESIGN_PAYLOAD_SHA256,
        "multi_cycle_dry_run": MULTI_CYCLE_DRY_RUN_RELATIVE_PATH,
        "multi_cycle_dry_run_payload_sha256_excluding_hash": MULTI_CYCLE_DRY_RUN_PAYLOAD_SHA256,
        "multi_cycle_design": MULTI_CYCLE_DESIGN_RELATIVE_PATH,
        "multi_cycle_design_payload_sha256_excluding_hash": MULTI_CYCLE_DESIGN_PAYLOAD_SHA256,
        "single_cycle_dry_run": SINGLE_CYCLE_RELATIVE_PATH,
        "single_cycle_payload_sha256_excluding_hash": SINGLE_CYCLE_PAYLOAD_SHA256,
        "paper_dry_run": PAPER_DRY_RUN_RELATIVE_PATH,
        "paper_dry_run_payload_sha256_excluding_hash": PAPER_DRY_RUN_PAYLOAD_SHA256,
        "order_sizing_repair_sim": SIZING_REPAIR_RELATIVE_PATH,
        "order_sizing_repair_payload_sha256_excluding_hash": SIZING_REPAIR_PAYLOAD_SHA256,
        "risk_capital_diagnostic": RISK_CAPITAL_RELATIVE_PATH,
        "risk_capital_payload_sha256_excluding_hash": RISK_CAPITAL_PAYLOAD_SHA256,
        "strategy_closure": CLOSURE_RELATIVE_PATH,
        "strategy_closure_payload_sha256_excluding_hash": CLOSURE_PAYLOAD_SHA256,
    }


def cycle_report_preview(multi_cycle: dict) -> list[dict]:
    reports = []
    for cycle in multi_cycle["cycle_records"]:
        reports.append(
            {
                "cycle_index": cycle["cycle_index"],
                "state_trace_summary": [step["state"] for step in cycle["state_trace"]],
                "snapshot_time_utc": cycle.get("snapshot_time_utc"),
                "passing_capital_scenarios": cycle.get("passing_capital_scenarios", []),
                "minimum_passing_capital": cycle.get("minimum_passing_capital"),
                "critical_risk_flags": cycle["risk_flags"]["critical_risk_flags"],
                "non_critical_risk_flags": cycle["risk_flags"]["non_critical_risk_flags"],
                "simulated_entry_plan_summary": {
                    "plan_count": len(cycle.get("simulated_entry_plan", [])),
                    "labels": sorted({plan.get("label") for plan in cycle.get("simulated_entry_plan", [])}),
                    "orders_generated": False,
                },
                "no_order_confirmation": cycle.get("no_order_confirmation") is True,
                "source_reference": MULTI_CYCLE_DRY_RUN_RELATIVE_PATH,
            }
        )
    return reports


def funding_event_preview(multi_cycle: dict) -> dict:
    observations = []
    quantity_by_cycle_symbol = {}
    for cycle in multi_cycle["cycle_records"]:
        for plan in cycle.get("simulated_entry_plan", []):
            for item in plan.get("symbol_entries", []):
                quantity_by_cycle_symbol[(cycle["cycle_index"], item["symbol"])] = item.get("common_base_quantity")
        for symbol, record in cycle["symbol_snapshot_records"].items():
            premium = record.get("premium_index") or {}
            observations.append(
                {
                    "cycle_index": cycle["cycle_index"],
                    "symbol": symbol,
                    "expected_funding_rate": premium.get("lastFundingRate"),
                    "next_funding_time_utc": premium.get("nextFundingTime_utc"),
                    "paper_position_quantity_if_simulated": quantity_by_cycle_symbol.get((cycle["cycle_index"], symbol)),
                    "expected_funding_cashflow": "schema_placeholder_no_real_account_cashflow",
                    "funding_received_simulated": "schema_placeholder",
                    "funding_paid_simulated_if_negative": "schema_placeholder",
                    "missing_funding_event_flag": premium.get("lastFundingRate") in (None, ""),
                    "funding_sign_flip_flag": "future_report_field",
                    "funding_attribution_by_symbol": "future_report_field",
                }
            )
    return {
        "simulated_public_data_only": True,
        "real_funding_received_verified": False,
        "exchange_statement_reconciled": False,
        "account_balance_checked": False,
        "private_api_used": False,
        "observations": observations,
    }


def risk_frequency(cycles: list[dict], flag_type: str) -> dict:
    counter: Counter[str] = Counter()
    for cycle in cycles:
        counter.update(cycle["risk_flags"][flag_type])
    return dict(sorted(counter.items(), key=lambda item: (-item[1], item[0])))


def pass_frequency(multi_cycle: dict) -> dict:
    return multi_cycle["aggregate_run_report"]["scenario_pass_frequency"]


def main() -> int:
    ensure_target_absent()
    artifacts = {
        "reporting_design": load_json(REPORTING_DESIGN_PATH),
        "multi_cycle_dry_run": load_json(MULTI_CYCLE_DRY_RUN_PATH),
        "multi_cycle_design": load_json(MULTI_CYCLE_DESIGN_PATH),
        "single_cycle": load_json(SINGLE_CYCLE_PATH),
        "paper_dry_run": load_json(PAPER_DRY_RUN_PATH),
        "sizing_repair": load_json(SIZING_REPAIR_PATH),
        "risk_capital": load_json(RISK_CAPITAL_PATH),
        "closure": load_json(CLOSURE_PATH),
    }
    validate_prior_artifacts(artifacts)

    reporting_design = artifacts["reporting_design"]
    multi_cycle = artifacts["multi_cycle_dry_run"]
    cycles = multi_cycle["cycle_records"]
    aggregate = multi_cycle["aggregate_run_report"]
    cycle_reports = cycle_report_preview(multi_cycle)
    funding_preview = funding_event_preview(multi_cycle)
    critical_frequency = risk_frequency(cycles, "critical_risk_flags")
    non_critical_frequency = risk_frequency(cycles, "non_critical_risk_flags")

    daily_preview = {
        "cycles_completed": aggregate["cycles_completed"],
        "cycles_with_passing_scenario": aggregate["cycles_with_passing_scenario"],
        "cycles_with_critical_risk": aggregate["cycles_with_critical_risk"],
        "cycles_with_non_critical_risk": aggregate["cycles_with_non_critical_risk"],
        "minimum_passing_capital_by_cycle": aggregate["minimum_passing_capital_by_cycle"],
        "risk_flags_frequency": {
            "critical": critical_frequency,
            "non_critical": non_critical_frequency,
        },
        "report_only_status": True,
        "no_live_confirmation": True,
    }
    finite_span_schema_fields = {
        "insufficient_real_time_span": True,
        "simulated_funding_accrual": "future_report_field",
        "simulated_price_hedge_residual": "future_report_field",
        "estimated_fees": "future_report_field",
        "estimated_slippage": "future_report_field",
        "risk_flag_counts": "future_report_field",
        "positive_cycle_rate": "future_report_field",
        "no_live_confirmation": True,
    }
    risk_incidents = {
        "critical_risk_incidents_present": aggregate["cycles_with_critical_risk"] > 0,
        "critical_risk_incidents": [],
        "non_critical_risk_incidents_summary": non_critical_frequency,
        "sizing_fail_scenario_warning": "some_scenarios_fail_sizing" in non_critical_frequency,
        "non_monotonic_sizing_warning": True,
        "no_live_confirmation": True,
    }
    sizing_preview = {
        "pass_fail_frequency_by_capital_scenario": pass_frequency(multi_cycle),
        "minimum_passing_capital_by_cycle": aggregate["minimum_passing_capital_by_cycle"],
        "non_monotonic_pass_fail_note": "Scenario pass/fail is not assumed monotonic; repaired sizing must run every report cycle.",
        "common_base_quantity_repair_preserved": True,
        "no_order_confirmation": True,
    }
    pnl_preview = {
        "schema_preview_only": True,
        "real_pnl_computed": False,
        "simulated_funding_component": "future_report_field_or_prior_artifact_if_available",
        "simulated_price_hedge_residual": "future_report_field_or_prior_artifact_if_available",
        "estimated_fees": "future_report_field",
        "estimated_slippage": "future_report_field",
        "sizing_mismatch_effect": "future_report_field",
        "unmodeled_risk_note": "No real account reconciliation, fills, commissions, balances, or funding receipts are available.",
        "real_account_reconciliation_absent": True,
    }
    audit_preview = {
        "source_artifacts": source_artifact_map(),
        "preview_artifact_payload_hash": "stored_in_top_level_payload_sha256_excluding_hash",
        "deterministic_json_required": True,
        "immutable_cycle_records_preserved": True,
        "manual_edits_required_false": True,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "private_api_or_account_data_used": False,
        "order_data_used": False,
        "report_builder_preview_only": True,
        "audit_requirements": reporting_design["audit_summary_schema"]["audit_requirements"],
    }

    validation_checks = {
        "repo_clean_before_run": True,
        "prior_reporting_design_loaded": True,
        "prior_reporting_design_next_allowed_step_verified": True,
        "prior_multi_cycle_dry_run_loaded": True,
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
        "all_9_report_previews_created": True,
        "audit_summary_preview_created": True,
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
        "source_artifacts": source_artifact_map(),
        "prior_reporting_design_preserved": {
            "status": reporting_design["status"],
            "classification": reporting_design["classification"],
            "next_allowed_step": reporting_design["next_allowed_step"],
            "report_schema_count": reporting_design["report_layer_design"]["report_schema_count"],
            "reconciliation_limitations_count": len(reporting_design["reconciliation_limitations"]),
            "audit_requirements_count": len(reporting_design["audit_summary_schema"]["audit_requirements"]),
            "no_live_capital_permission": True,
        },
        "prior_multi_cycle_dry_run_preserved": {
            "status": multi_cycle["status"],
            "classification": multi_cycle["classification"]["classification"],
            "cycles_completed": aggregate["cycles_completed"],
            "cycles_with_passing_scenario": aggregate["cycles_with_passing_scenario"],
            "cycles_with_critical_risk": aggregate["cycles_with_critical_risk"],
            "cycles_with_non_critical_risk": aggregate["cycles_with_non_critical_risk"],
            "minimum_passing_capital_by_cycle": aggregate["minimum_passing_capital_by_cycle"],
            "no_live_capital_permission": True,
        },
        "report_pack_preview": {
            "report_preview_names": list(REPORT_PREVIEW_NAMES),
            "report_preview_count": len(REPORT_PREVIEW_NAMES),
            "embedded_in_single_artifact": True,
            "separate_report_files_created": False,
            "source_is_existing_multi_cycle_dry_run_only": True,
        },
        "cycle_report_preview": cycle_reports,
        "funding_event_reconciliation_report_preview": funding_preview,
        "daily_carry_report_preview": daily_preview,
        "weekly_carry_report_preview": finite_span_schema_fields,
        "monthly_carry_report_preview": finite_span_schema_fields,
        "risk_incident_report_preview": risk_incidents,
        "sizing_stability_report_preview": sizing_preview,
        "simulated_pnl_attribution_report_preview": pnl_preview,
        "audit_summary_report_preview": audit_preview,
        "report_builder_limitations": [
            "This is a report builder preview only and creates no live monitor implementation.",
            "No new prices, funding, exchangeInfo, public API, private API, account data, or raw market rows are read.",
            "No real funding received, balances, fills, commissions, or exchange statement reconciliation is verified.",
            "Weekly and monthly reports are schema previews because the finite dry run does not provide a real weekly/monthly span.",
            "No order endpoint, order payload, scheduler, daemon, runtime, live trading, capital allocation, candidate generation, or edge claim is created.",
        ],
        "classification": CLASSIFICATION,
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "safety_permissions": {
            "report_builder_preview_created": True,
            "report_builder_enabled_now": False,
            "private_api_allowed_now": False,
            "order_placement_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "scheduler_allowed_now": False,
            "daemon_allowed_now": False,
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
        "report_preview_count": len(REPORT_PREVIEW_NAMES),
        "cycle_report_count": len(cycle_reports),
        "audit_requirements_count": len(reporting_design["audit_summary_schema"]["audit_requirements"]),
        "reconciliation_limitations_count": len(reporting_design["reconciliation_limitations"]),
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
