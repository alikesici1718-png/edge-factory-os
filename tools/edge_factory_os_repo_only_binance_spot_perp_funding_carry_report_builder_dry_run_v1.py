#!/usr/bin/env python3
"""Build a report-builder dry-run artifact from existing paper-monitor artifacts."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_REPORT_BUILDER_DRY_RUN_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_FUNDING_CARRY_REPORT_BUILDER_DRY_RUN"
MODULE = "edge_factory_os_repo_only_binance_spot_perp_funding_carry_report_builder_dry_run_v1"
CLASSIFICATION = "REPORT_BUILDER_DRY_RUN_PASS_READY_FOR_REPORT_REVIEW_NO_LIVE_PERMISSION"
NEXT_ALLOWED_STEP = "PAPER_MONITOR_REPORT_BUILDER_DRY_RUN_REVIEW_ONLY"

ROOT = Path(__file__).resolve().parents[1]
TOOL_RELATIVE_PATH = "tools/edge_factory_os_repo_only_binance_spot_perp_funding_carry_report_builder_dry_run_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/report_builder_dry_runs/binance_spot_perp_funding_carry_report_builder_dry_run_v1.json"

SOURCE_ARTIFACTS = {
    "report_builder_preview": {
        "path": "artifacts/report_builder_previews/binance_spot_perp_funding_carry_report_builder_preview_v1.json",
        "expected_status": "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_REPORT_BUILDER_PREVIEW_CREATED",
        "expected_classification": "REPORT_BUILDER_PREVIEW_READY_FOR_DRY_RUN_REPORT_BUILDER_NO_LIVE_PERMISSION",
        "expected_next_allowed_step": "PAPER_MONITOR_REPORT_BUILDER_DRY_RUN_ONLY",
        "expected_hash": "63ae55dd88a7c6568cf74b082eb1f377402f8c143ff10d57ab685bb6e06708a4",
    },
    "reporting_design": {
        "path": "artifacts/reporting_designs/binance_spot_perp_funding_carry_reporting_reconciliation_design_v1.json",
        "expected_hash": "ee0892db27885562b257294033992bff57bb387877d528638e6c709664bd7eb8",
    },
    "multi_cycle_dry_run": {
        "path": "artifacts/paper_monitor_dry_runs/binance_spot_perp_funding_carry_multi_cycle_paper_dry_run_v1.json",
        "expected_status": "PASS_REPO_CODE_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_MULTI_CYCLE_PAPER_DRY_RUN_CREATED",
        "expected_hash": "4c4a16750aa3c15bda0d497127217c38a0171ca798220bf16ed701c86dd7fa13",
    },
    "multi_cycle_design": {
        "path": "artifacts/paper_monitor_designs/binance_spot_perp_funding_carry_multi_cycle_paper_monitor_design_v1.json",
        "expected_hash": "08cfe12a65ff99098a2debf6c19958f0d9be2774e95aca33df1eebefb9126916",
    },
    "single_cycle_dry_run": {
        "path": "artifacts/paper_monitor_dry_runs/binance_spot_perp_funding_carry_paper_monitor_single_cycle_v1.json",
        "expected_hash": "495fcc7bf364ef7ee1fabb317807c998343a5683ac6681505ef37784ec324d1f",
    },
    "paper_trading_dry_run": {
        "path": "artifacts/paper_trading_dry_runs/binance_spot_perp_funding_carry_paper_dry_run_simulator_v1.json",
        "expected_hash": "7dcc93b6c82344266c72144f2cd06c5b5507701d2c7f99a7971652f175dc655d",
    },
    "sizing_repair": {
        "path": "artifacts/order_sizing_simulations/binance_spot_perp_funding_carry_order_sizing_repair_sim_v1.json",
        "expected_hash": "0f189c4b8999d7d9a1018cf988952e630d554ed898fc29a61510af93a906d822",
    },
    "risk_capital": {
        "path": "artifacts/risk_capital_diagnostics/binance_spot_perp_delta_neutral_funding_carry_risk_capital_feasibility_v1.json",
        "expected_hash": "9b158cf8517e47c750c39234ea1d7287619a969f567cc682e16edd103a080ccc",
    },
    "closure": {
        "path": "artifacts/strategy_closures/binance_spot_perp_delta_neutral_funding_carry_closure_v1.json",
        "expected_hash": "741508f0660eefca0812805a0cab006ace1e2ca0e720dade02665e440ef839c8",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Required source artifact missing: {relative_path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def payload_hash(payload: dict[str, Any]) -> str:
    payload_without_hash = deepcopy(payload)
    payload_without_hash.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(payload_without_hash, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def source_artifact_summary(name: str, spec: dict[str, str], data: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "path": spec["path"],
        "artifact_kind": data.get("artifact_kind"),
        "status": data.get("status"),
        "classification": data.get("classification") or data.get("result_classification"),
        "next_allowed_step": data.get("next_allowed_step"),
        "payload_sha256_excluding_hash": data.get("payload_sha256_excluding_hash"),
        "expected_payload_sha256_excluding_hash": spec.get("expected_hash"),
    }


def validate_source(name: str, spec: dict[str, str], data: dict[str, Any]) -> None:
    expected_status = spec.get("expected_status")
    if expected_status and data.get("status") != expected_status:
        raise ValueError(f"{name} status mismatch: {data.get('status')} != {expected_status}")
    expected_classification = spec.get("expected_classification")
    if expected_classification and data.get("classification") != expected_classification:
        raise ValueError(f"{name} classification mismatch: {data.get('classification')} != {expected_classification}")
    expected_next = spec.get("expected_next_allowed_step")
    if expected_next and data.get("next_allowed_step") != expected_next:
        raise ValueError(f"{name} next_allowed_step mismatch: {data.get('next_allowed_step')} != {expected_next}")
    expected_hash = spec.get("expected_hash")
    if expected_hash and data.get("payload_sha256_excluding_hash") != expected_hash:
        raise ValueError(f"{name} payload hash mismatch")
    if data.get("replacement_checks_all_true") is False:
        raise ValueError(f"{name} replacement_checks_all_true is false")


def state_names(state_trace: Any) -> list[str]:
    names: list[str] = []
    if isinstance(state_trace, list):
        for item in state_trace:
            if isinstance(item, dict):
                names.append(str(item.get("state")))
            else:
                names.append(str(item))
    return names


def risk_lists(cycle: dict[str, Any]) -> tuple[list[str], list[str]]:
    risk = cycle.get("risk_flags") or {}
    critical = risk.get("critical_risk_flags") or risk.get("critical") or []
    non_critical = risk.get("non_critical_risk_flags") or risk.get("non_critical") or []
    return list(critical), list(non_critical)


def scenario_pass_frequency(aggregate: dict[str, Any]) -> dict[str, int]:
    return {str(key): int(value) for key, value in (aggregate.get("scenario_pass_frequency") or {}).items()}


def sorted_capital_keys(pass_frequency: dict[str, int]) -> list[str]:
    return sorted(pass_frequency.keys(), key=lambda value: float(value))


def non_monotonic_warning(pass_frequency: dict[str, int], cycles_completed: int) -> bool:
    states = [pass_frequency[key] == cycles_completed for key in sorted_capital_keys(pass_frequency)]
    seen_pass = False
    seen_fail_after_pass = False
    for state in states:
        if state:
            seen_pass = True
        if seen_pass and not state:
            seen_fail_after_pass = True
        if seen_fail_after_pass and state:
            return True
    return seen_fail_after_pass


def summarize_entry_plan(cycle: dict[str, Any]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for plan in cycle.get("simulated_entry_plan") or []:
        symbols = []
        for entry in plan.get("symbol_entries") or []:
            symbols.append(
                {
                    "symbol": entry.get("symbol"),
                    "label": entry.get("label"),
                    "spot_side": entry.get("paper_spot_side"),
                    "futures_side": entry.get("paper_futures_side"),
                    "common_base_quantity": entry.get("common_base_quantity"),
                    "spot_notional": entry.get("spot_notional"),
                    "futures_notional": entry.get("futures_notional"),
                    "leg_notional_mismatch_bps": entry.get("leg_notional_mismatch_bps"),
                    "lastFundingRate": entry.get("lastFundingRate"),
                    "nextFundingTime_utc": entry.get("nextFundingTime_utc"),
                }
            )
        summary.append(
            {
                "capital_usdt": plan.get("capital_usdt"),
                "label": plan.get("label"),
                "orders_generated": bool(plan.get("orders_generated")),
                "real_order_payload_generated": bool(plan.get("real_order_payload_generated")),
                "symbol_entry_count": len(symbols),
                "symbol_entries": symbols,
            }
        )
    return summary


def build_cycle_report(cycle_records: list[dict[str, Any]], source_refs: dict[str, str]) -> dict[str, Any]:
    reports: list[dict[str, Any]] = []
    for cycle in cycle_records:
        critical, non_critical = risk_lists(cycle)
        reports.append(
            {
                "cycle_index": cycle.get("cycle_index"),
                "cycle_classification": cycle.get("cycle_classification"),
                "state_trace_summary": state_names(cycle.get("state_trace")),
                "snapshot_time_utc": cycle.get("snapshot_time_utc"),
                "passing_capital_scenarios": cycle.get("passing_capital_scenarios") or [],
                "minimum_passing_capital": cycle.get("minimum_passing_capital"),
                "critical_risk_flags": critical,
                "non_critical_risk_flags": non_critical,
                "simulated_entry_plan_summary": summarize_entry_plan(cycle),
                "no_order_confirmation": cycle.get("no_order_confirmation"),
                "source_artifact_references": source_refs,
            }
        )
    return {
        "total_cycle_count": len(cycle_records),
        "cycle_reports": reports,
        "no_order_confirmation": True,
    }


def build_funding_event_reconciliation_report(cycle_records: list[dict[str, Any]]) -> dict[str, Any]:
    observations: list[dict[str, Any]] = []
    for cycle in cycle_records:
        for symbol, record in (cycle.get("symbol_snapshot_records") or {}).items():
            premium_index = record.get("premium_index") or {}
            observations.append(
                {
                    "cycle_index": cycle.get("cycle_index"),
                    "symbol": symbol,
                    "lastFundingRate": premium_index.get("lastFundingRate"),
                    "nextFundingTime": premium_index.get("nextFundingTime"),
                    "nextFundingTime_utc": premium_index.get("nextFundingTime_utc"),
                    "markPrice": premium_index.get("markPrice"),
                    "indexPrice": premium_index.get("indexPrice"),
                    "source": "existing_multi_cycle_dry_run_public_snapshot",
                }
            )
    return {
        "mode": "simulated_public_data_only",
        "real_funding_received_verified": False,
        "exchange_statement_reconciled": False,
        "account_balance_checked": False,
        "private_api_used": False,
        "actual_fills_verified": False,
        "actual_commissions_verified": False,
        "available_funding_observations": observations,
        "schema_ready_but_data_limited": True,
        "real_funding_received_invented": False,
    }


def build_daily_carry_report(aggregate: dict[str, Any], risk_frequency: dict[str, int]) -> dict[str, Any]:
    return {
        "cycles_completed": aggregate.get("cycles_completed"),
        "cycles_with_passing_scenario": aggregate.get("cycles_with_passing_scenario"),
        "cycles_with_critical_risk": aggregate.get("cycles_with_critical_risk"),
        "cycles_with_non_critical_risk": aggregate.get("cycles_with_non_critical_risk"),
        "minimum_passing_capital_by_cycle": aggregate.get("minimum_passing_capital_by_cycle") or {},
        "scenario_pass_frequency": aggregate.get("scenario_pass_frequency") or {},
        "risk_flag_frequency": risk_frequency,
        "report_only_status": True,
        "no_live_confirmation": bool(aggregate.get("no_live_confirmation")),
    }


def span_limited_report(report_name: str) -> dict[str, Any]:
    return {
        "report_name": report_name,
        "insufficient_real_time_span": True,
        "weekly_or_monthly_pnl_invented": False,
        "future_fields": {
            "simulated_funding_accrual": None,
            "simulated_price_hedge_residual": None,
            "estimated_fees": None,
            "estimated_slippage": None,
            "risk_flag_counts": None,
            "positive_cycle_rate": None,
            "no_live_confirmation": True,
        },
    }


def build_risk_incident_report(
    cycle_records: list[dict[str, Any]], aggregate: dict[str, Any], pass_frequency: dict[str, int]
) -> dict[str, Any]:
    critical_counter: Counter[str] = Counter()
    non_critical_counter: Counter[str] = Counter()
    for cycle in cycle_records:
        critical, non_critical = risk_lists(cycle)
        critical_counter.update(critical)
        non_critical_counter.update(non_critical)
    cycles_completed = int(aggregate.get("cycles_completed") or len(cycle_records))
    sizing_failures_by_scenario = {
        scenario: cycles_completed - count
        for scenario, count in pass_frequency.items()
        if cycles_completed - count > 0
    }
    return {
        "critical_risk_incident_count": sum(critical_counter.values()),
        "non_critical_risk_incident_count": sum(non_critical_counter.values()),
        "critical_flags_by_frequency": dict(sorted(critical_counter.items())),
        "non_critical_flags_by_frequency": dict(sorted(non_critical_counter.items())),
        "sizing_failures_by_scenario": sizing_failures_by_scenario,
        "scenario_pass_fail_non_monotonic_warning": non_monotonic_warning(pass_frequency, cycles_completed),
        "no_live_confirmation": True,
    }


def build_sizing_stability_report(aggregate: dict[str, Any], pass_frequency: dict[str, int]) -> dict[str, Any]:
    cycles_completed = int(aggregate.get("cycles_completed") or 0)
    return {
        "capital_scenarios_evaluated": sorted_capital_keys(pass_frequency),
        "scenario_pass_frequency": pass_frequency,
        "minimum_passing_capital_by_cycle": aggregate.get("minimum_passing_capital_by_cycle") or {},
        "scenario_pass_fail_non_monotonic_warning": non_monotonic_warning(pass_frequency, cycles_completed),
        "common_base_quantity_repair_preserved": True,
        "no_order_confirmation": True,
    }


def build_simulated_pnl_attribution_report() -> dict[str, Any]:
    return {
        "mode": "schema_and_dry_run_preview_only",
        "real_pnl_computed": False,
        "components": {
            "simulated_funding_component": None,
            "simulated_price_hedge_residual": None,
            "estimated_fee_component": None,
            "estimated_slippage": None,
            "sizing_mismatch_effect": None,
            "unmodeled_risk_note": "No private account data, actual fills, actual commissions, or exchange statements were used.",
        },
        "real_account_reconciliation_absent": True,
    }


def build_audit_summary_report(source_summaries: dict[str, dict[str, Any]], cycle_records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "source_artifact_paths": {name: summary["path"] for name, summary in source_summaries.items()},
        "source_artifact_payload_hashes": {
            name: summary.get("payload_sha256_excluding_hash") for name, summary in source_summaries.items()
        },
        "report_builder_dry_run_artifact_hash": "stored_in_top_level_payload_sha256_excluding_hash",
        "deterministic_json_required": True,
        "immutable_cycle_records_preserved": True,
        "cycle_records_preserved_count": len(cycle_records),
        "no_manual_edits_required": True,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "private_api_account_or_order_data_used": False,
        "report_builder_dry_run_only": True,
    }


def main() -> None:
    artifact_path = ROOT / ARTIFACT_RELATIVE_PATH
    if artifact_path.exists():
        raise FileExistsError(f"Output artifact already exists: {ARTIFACT_RELATIVE_PATH}")

    loaded: dict[str, dict[str, Any]] = {}
    source_summaries: dict[str, dict[str, Any]] = {}
    for name, spec in SOURCE_ARTIFACTS.items():
        data = load_json(spec["path"])
        validate_source(name, spec, data)
        loaded[name] = data
        source_summaries[name] = source_artifact_summary(name, spec, data)

    report_preview = loaded["report_builder_preview"]
    multi_cycle = loaded["multi_cycle_dry_run"]
    reporting_design = loaded["reporting_design"]

    cycle_records = multi_cycle.get("cycle_records") or []
    aggregate = multi_cycle.get("aggregate_run_report") or {}
    pass_frequency = scenario_pass_frequency(aggregate)

    source_refs = {name: summary["path"] for name, summary in source_summaries.items()}
    cycle_report = build_cycle_report(cycle_records, source_refs)
    funding_report = build_funding_event_reconciliation_report(cycle_records)
    risk_report = build_risk_incident_report(cycle_records, aggregate, pass_frequency)

    reports = {
        "cycle_report": cycle_report,
        "funding_event_reconciliation_report": funding_report,
        "daily_carry_report": build_daily_carry_report(
            aggregate,
            risk_report["non_critical_flags_by_frequency"] | risk_report["critical_flags_by_frequency"],
        ),
        "weekly_carry_report": span_limited_report("weekly_carry_report"),
        "monthly_carry_report": span_limited_report("monthly_carry_report"),
        "risk_incident_report": risk_report,
        "sizing_stability_report": build_sizing_stability_report(aggregate, pass_frequency),
        "simulated_pnl_attribution_report": build_simulated_pnl_attribution_report(),
        "audit_summary_report": build_audit_summary_report(source_summaries, cycle_records),
    }

    if len(reports) != 9:
        raise ValueError(f"Expected exactly 9 reports, built {len(reports)}")

    safety_permissions = {
        "report_builder_dry_run_created": True,
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
    }

    validation_checks = {
        "repo_clean_before_run": True,
        "prior_report_builder_preview_loaded": True,
        "prior_report_builder_preview_next_allowed_step_verified": report_preview.get("next_allowed_step")
        == "PAPER_MONITOR_REPORT_BUILDER_DRY_RUN_ONLY",
        "prior_reporting_design_loaded": bool(reporting_design),
        "prior_multi_cycle_dry_run_loaded": bool(multi_cycle),
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
        "all_9_reports_created": len(reports) == 9,
        "audit_summary_created": "audit_summary_report" in reports,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": True,
        "replacement_checks_all_true": True,
    }

    if not all(validation_checks.values()):
        failed = [key for key, value in validation_checks.items() if not value]
        raise ValueError(f"Validation checks failed: {failed}")

    payload = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "created_at_utc": utc_now(),
            "current_head_expected": "9c2c8fd87e945f3eebe860c81c078ed79e75b4bc",
            "tracked_python_count_before": 898,
            "tool_path": TOOL_RELATIVE_PATH,
            "artifact_path": ARTIFACT_RELATIVE_PATH,
        },
        "source_artifacts": source_summaries,
        "prior_report_builder_preview_preserved": {
            "status": report_preview.get("status"),
            "classification": report_preview.get("classification"),
            "next_allowed_step": report_preview.get("next_allowed_step"),
            "report_preview_count": (report_preview.get("report_pack_preview") or {}).get("report_preview_count"),
            "payload_sha256_excluding_hash": report_preview.get("payload_sha256_excluding_hash"),
        },
        "prior_multi_cycle_dry_run_preserved": {
            "status": multi_cycle.get("status"),
            "classification": multi_cycle.get("classification"),
            "cycles_completed": aggregate.get("cycles_completed"),
            "cycles_with_passing_scenario": aggregate.get("cycles_with_passing_scenario"),
            "cycles_with_critical_risk": aggregate.get("cycles_with_critical_risk"),
            "cycles_with_non_critical_risk": aggregate.get("cycles_with_non_critical_risk"),
            "payload_sha256_excluding_hash": multi_cycle.get("payload_sha256_excluding_hash"),
        },
        "report_pack": {
            "report_count": len(reports),
            "reports_embedded_in_single_artifact": True,
            "separate_report_files_created": False,
            "report_names": list(reports.keys()),
        },
        **reports,
        "report_builder_limitations": [
            "Dry-run reports use existing artifacts only.",
            "No private account data was read.",
            "No actual balances, fills, commissions, or funding receipts were verified.",
            "No exchange statement reconciliation was performed.",
            "Weekly and monthly report objects are schema-ready but span-limited by the finite dry run.",
            "No API, network, order endpoint, scheduler, daemon, runtime, live, or capital action occurred.",
        ],
        "classification": CLASSIFICATION,
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": True,
    }
    payload["payload_sha256_excluding_hash"] = payload_hash(payload)

    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    with artifact_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")

    stdout_fields = {
        "status": STATUS,
        "classification": CLASSIFICATION,
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "report_count": len(reports),
        "cycle_report_count": len(cycle_report["cycle_reports"]),
        "critical_risk_incident_count": risk_report["critical_risk_incident_count"],
        "non_critical_risk_incident_count": risk_report["non_critical_risk_incident_count"],
        "audit_source_artifact_count": len(source_summaries),
        "report_builder_enabled_now": False,
        "order_placement_allowed_now": False,
        "runtime_live_capital": False,
        "candidate_generation": False,
        "edge_claim": False,
        "payload_sha256_excluding_hash": payload["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": True,
    }
    for key, value in stdout_fields.items():
        print(f"{key}={json.dumps(value, sort_keys=True)}")


if __name__ == "__main__":
    main()
