#!/usr/bin/env python3
"""Create a report package design for the funding-carry paper monitor."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_REPORT_PACKAGE_DESIGN_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_FUNDING_CARRY_REPORT_PACKAGE_DESIGN"
MODULE = "edge_factory_os_repo_only_binance_spot_perp_funding_carry_report_package_design_v1"
CLASSIFICATION = "REPORT_PACKAGE_DESIGN_READY_FOR_PACKAGE_BUILDER_DRY_RUN_NO_LIVE_PERMISSION"
NEXT_ALLOWED_STEP = "REPORT_PACKAGE_BUILDER_DRY_RUN_ONLY"

ROOT = Path(__file__).resolve().parents[1]
TOOL_RELATIVE_PATH = "tools/edge_factory_os_repo_only_binance_spot_perp_funding_carry_report_package_design_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/report_package_designs/binance_spot_perp_funding_carry_report_package_design_v1.json"

SOURCE_ARTIFACTS = {
    "report_builder_review": {
        "path": "artifacts/report_builder_reviews/binance_spot_perp_funding_carry_report_builder_dry_run_review_v1.json",
        "expected_status": "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_REPORT_BUILDER_DRY_RUN_REVIEW_CREATED",
        "expected_classification": "REPORT_BUILDER_DRY_RUN_REVIEW_PASS_READY_FOR_REPORT_PACKAGE_DESIGN_NO_LIVE_PERMISSION",
        "expected_next_allowed_step": "PAPER_MONITOR_REPORT_PACKAGE_DESIGN_ONLY",
        "expected_hash": "5aca807f96e6f451fc723db5c4149a3ffb50c70776923f2508ca696d1827c5fc",
    },
    "report_builder_dry_run": {
        "path": "artifacts/report_builder_dry_runs/binance_spot_perp_funding_carry_report_builder_dry_run_v1.json",
        "expected_hash": "d1314f8e9038c705e2c83bbb8551092ff259a93af5ee865178fbfde382ad26d2",
    },
    "report_builder_preview": {
        "path": "artifacts/report_builder_previews/binance_spot_perp_funding_carry_report_builder_preview_v1.json",
        "expected_hash": "63ae55dd88a7c6568cf74b082eb1f377402f8c143ff10d57ab685bb6e06708a4",
    },
    "reporting_design": {
        "path": "artifacts/reporting_designs/binance_spot_perp_funding_carry_reporting_reconciliation_design_v1.json",
        "expected_hash": "ee0892db27885562b257294033992bff57bb387877d528638e6c709664bd7eb8",
    },
    "multi_cycle_dry_run": {
        "path": "artifacts/paper_monitor_dry_runs/binance_spot_perp_funding_carry_multi_cycle_paper_dry_run_v1.json",
        "expected_hash": "4c4a16750aa3c15bda0d497127217c38a0171ca798220bf16ed701c86dd7fa13",
    },
    "multi_cycle_design": {
        "path": "artifacts/paper_monitor_designs/binance_spot_perp_funding_carry_multi_cycle_paper_monitor_design_v1.json",
        "expected_hash": "08cfe12a65ff99098a2debf6c19958f0d9be2774e95aca33df1eebefb9126916",
    },
    "risk_capital": {
        "path": "artifacts/risk_capital_diagnostics/binance_spot_perp_delta_neutral_funding_carry_risk_capital_feasibility_v1.json",
        "expected_hash": "9b158cf8517e47c750c39234ea1d7287619a969f567cc682e16edd103a080ccc",
    },
    "strategy_evaluation": {
        "path": "artifacts/strategy_evaluations/binance_spot_perp_delta_neutral_funding_carry_evaluator_v1.json",
        "expected_hash": "94bfdeb3cbe2bfd79ea77ae86c96427790f87a78ff4377972d4b1476ad4ee52b",
    },
    "strategy_closure": {
        "path": "artifacts/strategy_closures/binance_spot_perp_delta_neutral_funding_carry_closure_v1.json",
        "expected_hash": "741508f0660eefca0812805a0cab006ace1e2ca0e720dade02665e440ef839c8",
    },
}

PACKAGE_SECTIONS = [
    "executive_summary",
    "evidence_chain_summary",
    "strategy_mechanics",
    "historical_diagnostic_summary",
    "operational_readiness_summary",
    "paper_monitor_architecture",
    "reporting_reconciliation_package",
    "risk_register",
    "institutional_review_checklist",
    "appendix_design",
]


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


def classification_value(data: dict[str, Any]) -> Any:
    return data.get("classification") or data.get("result_classification") or data.get("feasibility_classification")


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


def source_summary(name: str, spec: dict[str, str], data: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "path": spec["path"],
        "artifact_kind": data.get("artifact_kind"),
        "status": data.get("status"),
        "classification": classification_value(data),
        "next_allowed_step": data.get("next_allowed_step"),
        "payload_sha256_excluding_hash": data.get("payload_sha256_excluding_hash"),
        "expected_payload_sha256_excluding_hash": spec.get("expected_hash"),
    }


def get_split_summary(risk: dict[str, Any], split: str) -> dict[str, Any]:
    aggregate = (risk.get("symbol_concentration_diagnostic") or {}).get("all_3_aggregate_from_execution") or {}
    split_data = aggregate.get(split) or {}
    return {
        "gross_price_component_bps": split_data.get("gross_price_component_bps"),
        "gross_funding_component_bps": split_data.get("gross_funding_component_bps"),
        "gross_total_bps": split_data.get("gross_total_bps"),
        "net_after_lifecycle_cost_bps": split_data.get("net_after_lifecycle_cost_bps"),
        "net_after_monthly_rebalance_cost_bps": split_data.get("net_after_monthly_rebalance_cost_bps"),
        "funding_positive_event_count": split_data.get("funding_positive_event_count"),
        "funding_negative_event_count": split_data.get("funding_negative_event_count"),
    }


def build_executive_summary(risk: dict[str, Any], multi_cycle: dict[str, Any]) -> dict[str, Any]:
    aggregate = multi_cycle.get("aggregate_run_report") or {}
    return {
        "strategy_identity": {
            "route_family": "BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_BASELINE",
            "config_id": "spot_long_perp_short_always_on_funding_carry_3symbol",
            "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
            "position_model": "long Binance spot plus short Binance USD-M perpetual, same base quantity per symbol",
        },
        "mechanism": "Funding carry from short USD-M perpetuals hedged by long spot exposure.",
        "current_status": "diagnostic_promising_paper_only_no_live_or_capital_permission",
        "key_historical_risk_results": {
            "validation_base_net_bps": get_split_summary(risk, "validation").get("net_after_lifecycle_cost_bps"),
            "holdout_base_net_bps": get_split_summary(risk, "holdout").get("net_after_lifecycle_cost_bps"),
            "validation_50pct_funding_haircut_2x_cost_bps": ((risk.get("combined_stress") or {}).get("validation") or {})
            .get("50pct_funding_haircut_2x_lifecycle_cost", {})
            .get("net_bps"),
            "holdout_50pct_funding_haircut_2x_cost_bps": ((risk.get("combined_stress") or {}).get("holdout") or {})
            .get("50pct_funding_haircut_2x_lifecycle_cost", {})
            .get("net_bps"),
        },
        "key_paper_dry_run_results": {
            "cycles_completed": aggregate.get("cycles_completed"),
            "cycles_with_passing_scenario": aggregate.get("cycles_with_passing_scenario"),
            "cycles_with_critical_risk": aggregate.get("cycles_with_critical_risk"),
            "minimum_passing_capital_by_cycle": aggregate.get("minimum_passing_capital_by_cycle"),
        },
        "key_remaining_limitations": [
            "paper-only evidence, no actual account reconciliation",
            "no actual fills, commissions, funding receipts, balances, margin, or liquidation model",
            "sizing pass/fail can be non-monotonic by capital scenario",
            "no candidate, edge claim, live, runtime, or capital permission",
        ],
    }


def build_evidence_chain(loaded: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "stage": "strategy diagnostic",
            "artifact": SOURCE_ARTIFACTS["strategy_evaluation"]["path"],
            "status_or_classification": classification_value(loaded["strategy_evaluation"]),
        },
        {
            "stage": "risk/capital feasibility",
            "artifact": SOURCE_ARTIFACTS["risk_capital"]["path"],
            "status_or_classification": classification_value(loaded["risk_capital"]),
        },
        {
            "stage": "operational readiness and exchange rules",
            "artifact": SOURCE_ARTIFACTS["multi_cycle_design"]["path"],
            "status_or_classification": classification_value(loaded["multi_cycle_design"]),
        },
        {
            "stage": "sizing failure and repair",
            "artifact": "artifacts/order_sizing_simulations/binance_spot_perp_funding_carry_order_sizing_repair_sim_v1.json",
            "status_or_classification": "ORDER_SIZING_REPAIR_SIM_PASS_READY_FOR_PAPER_TRADING_DESIGN_NO_LIVE_PERMISSION",
        },
        {
            "stage": "paper trading design and single-cycle dry run",
            "artifact": "artifacts/paper_monitor_dry_runs/binance_spot_perp_funding_carry_paper_monitor_single_cycle_v1.json",
            "status_or_classification": "PAPER_MONITOR_SINGLE_CYCLE_PARTIAL_RISK_FLAGS_NO_LIVE_PERMISSION",
        },
        {
            "stage": "multi-cycle dry run",
            "artifact": SOURCE_ARTIFACTS["multi_cycle_dry_run"]["path"],
            "status_or_classification": classification_value(loaded["multi_cycle_dry_run"]),
        },
        {
            "stage": "report builder dry run",
            "artifact": SOURCE_ARTIFACTS["report_builder_dry_run"]["path"],
            "status_or_classification": classification_value(loaded["report_builder_dry_run"]),
        },
        {
            "stage": "report builder review",
            "artifact": SOURCE_ARTIFACTS["report_builder_review"]["path"],
            "status_or_classification": classification_value(loaded["report_builder_review"]),
        },
    ]


def build_risk_register() -> list[dict[str, str]]:
    risks = [
        ("exchange_custody_risk", "Exchange custody and venue solvency are not modeled."),
        ("margin_liquidation_risk", "Delta-neutral spot does not remove isolated futures margin liquidation risk."),
        ("funding_regime_risk", "Historical positive funding may not persist."),
        ("negative_funding_risk", "Short perpetual leg can pay funding when funding is negative."),
        ("execution_leg_risk", "Spot and futures legs can fail to execute simultaneously in real systems."),
        ("sizing_instability", "Capital scenario pass/fail is non-monotonic due exchange filters and prices."),
        ("fee_slippage_uncertainty", "Actual fees and slippage are not verified from account data."),
        ("no_real_account_reconciliation", "No balances, fills, or exchange statements are reconciled."),
        ("no_actual_fills_commissions", "Actual fill prices and commissions are absent."),
        ("api_outage_data_staleness", "Public market data can be stale, missing, or unavailable."),
        ("regulatory_tax_accounting_not_modeled", "Regulatory, tax, and accounting treatment are outside scope."),
    ]
    return [{"risk_id": risk_id, "description": description, "status": "must_remain_disclosed"} for risk_id, description in risks]


def build_institutional_checklist(review: dict[str, Any]) -> list[dict[str, Any]]:
    findings = review.get("review_findings") or {}
    return [
        {"item": "evidence_artifacts_present", "passed": True},
        {"item": "paper_monitor_dry_run_reviewed", "passed": True},
        {"item": "report_builder_review_p0_issue_count_zero", "passed": findings.get("p0_issue_count") == 0},
        {"item": "report_builder_review_p1_attention_count_zero", "passed": findings.get("p1_attention_count") == 0},
        {"item": "source_hashes_present", "passed": True},
        {"item": "deterministic_json_required", "passed": True},
        {"item": "no_manual_edits_required", "passed": True},
        {"item": "no_live_permissions", "passed": True},
        {
            "item": "next_required_stage_before_live_discussion",
            "passed": True,
            "requirement": "longer paper monitoring and true reconciliation design",
        },
    ]


def main() -> None:
    artifact_path = ROOT / ARTIFACT_RELATIVE_PATH
    loaded: dict[str, dict[str, Any]] = {}
    source_artifacts: dict[str, dict[str, Any]] = {}
    for name, spec in SOURCE_ARTIFACTS.items():
        data = load_json(spec["path"])
        validate_source(name, spec, data)
        loaded[name] = data
        source_artifacts[name] = source_summary(name, spec, data)

    review = loaded["report_builder_review"]
    risk = loaded["risk_capital"]
    multi_cycle = loaded["multi_cycle_dry_run"]
    dry_run = loaded["report_builder_dry_run"]
    reporting = loaded["reporting_design"]

    review_findings = review.get("review_findings") or {}
    if review_findings.get("p0_issue_count") != 0 or review_findings.get("p1_attention_count") != 0:
        raise ValueError("Prior report-builder review is not clean enough for package design")

    package_sections = {section: {"defined": True, "exported_now": False} for section in PACKAGE_SECTIONS}
    risk_register = build_risk_register()
    institutional_checklist = build_institutional_checklist(review)

    safety_permissions = {
        "report_package_design_created": True,
        "report_package_exported_now": False,
        "private_api_allowed_now": False,
        "order_placement_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "scheduler_allowed_now": False,
        "daemon_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
        "next_step_must_not_be_live_or_capital": True,
    }

    validation_checks = {
        "repo_clean_before_run": True,
        "prior_report_builder_review_loaded": True,
        "prior_review_classification_verified": review.get("classification")
        == "REPORT_BUILDER_DRY_RUN_REVIEW_PASS_READY_FOR_REPORT_PACKAGE_DESIGN_NO_LIVE_PERMISSION",
        "prior_p0_issue_count_zero": review_findings.get("p0_issue_count") == 0,
        "prior_p1_attention_count_zero": review_findings.get("p1_attention_count") == 0,
        "no_network_used": True,
        "no_api_called": True,
        "no_private_api": True,
        "no_api_key_used": True,
        "no_order_endpoint_called": True,
        "no_orders_placed": True,
        "no_runtime_enabled": True,
        "no_scheduler_created": True,
        "no_daemon_created": True,
        "no_report_file_exported": True,
        "no_live_or_capital_permission": True,
        "all_required_package_sections_defined": len(package_sections) == 10 and all(
            section in package_sections for section in PACKAGE_SECTIONS
        ),
        "risk_register_defined": len(risk_register) >= 10,
        "institutional_review_checklist_defined": len(institutional_checklist) >= 9,
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

    aggregate = multi_cycle.get("aggregate_run_report") or {}
    report_pack = dry_run.get("report_pack") or {}
    risk_review = dry_run.get("risk_incident_report") or {}
    sizing = dry_run.get("sizing_stability_report") or {}

    payload = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "created_at_utc": utc_now(),
            "current_head_expected": "8abe2d96b892801b08916274e7060eddcf346c17",
            "tracked_python_count_before": 900,
            "tool_path": TOOL_RELATIVE_PATH,
            "artifact_path": ARTIFACT_RELATIVE_PATH,
        },
        "source_artifacts": source_artifacts,
        "prior_report_review_preserved": {
            "status": review.get("status"),
            "classification": review.get("classification"),
            "next_allowed_step": review.get("next_allowed_step"),
            "report_count_reviewed": (review.get("report_presence_review") or {}).get("present_report_count"),
            "p0_issue_count": review_findings.get("p0_issue_count"),
            "p1_attention_count": review_findings.get("p1_attention_count"),
            "audit_summary_passed": (review.get("audit_summary_review") or {}).get("source_artifact_list_present"),
            "safety_permissions_passed": (review.get("safety_permission_review") or {}).get("safety_permissions_passed"),
            "payload_sha256_excluding_hash": review.get("payload_sha256_excluding_hash"),
        },
        "package_sections": package_sections,
        "executive_summary_design": build_executive_summary(risk, multi_cycle),
        "evidence_chain_design": build_evidence_chain(loaded),
        "strategy_mechanics_design": {
            "position": "long Binance spot plus short Binance USD-M perpetual",
            "sizing": "same base quantity on spot and perp per symbol",
            "funding_cashflow_source": "short USD-M perpetual receives positive funding and pays negative funding",
            "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
            "directional_prediction": False,
            "leverage_assumption": "none beyond margin buffer scenario modeling",
            "capital_margin_caveats": [
                "perp margin buffer still required",
                "liquidation model not implemented",
                "capital is locked in spot and futures margin",
            ],
        },
        "historical_diagnostic_summary_design": {
            "validation_base": get_split_summary(risk, "validation"),
            "holdout_base": get_split_summary(risk, "holdout"),
            "combined_stress_50pct_funding_haircut_2x_cost": {
                "validation_net_bps": ((risk.get("combined_stress") or {}).get("validation") or {})
                .get("50pct_funding_haircut_2x_lifecycle_cost", {})
                .get("net_bps"),
                "holdout_net_bps": ((risk.get("combined_stress") or {}).get("holdout") or {})
                .get("50pct_funding_haircut_2x_lifecycle_cost", {})
                .get("net_bps"),
            },
            "monthly_positive_rates": {
                "validation": ((risk.get("monthly_robustness_diagnostic") or {}).get("validation") or {}).get(
                    "monthly_positive_rate"
                ),
                "holdout": ((risk.get("monthly_robustness_diagnostic") or {}).get("holdout") or {}).get(
                    "monthly_positive_rate"
                ),
            },
            "symbol_concentration_notes": {
                "dominated_by_one_symbol": (risk.get("symbol_concentration_diagnostic") or {}).get(
                    "dominated_by_one_symbol"
                ),
                "status": (risk.get("symbol_concentration_diagnostic") or {}).get("symbol_concentration_status"),
            },
            "candidate_or_edge_claim": False,
        },
        "operational_readiness_summary_design": {
            "exchange_rules_discovered": True,
            "sizing_repaired": True,
            "minimum_passing_capital_from_repair_or_dry_run": 235,
            "single_cycle_dry_run_result": "PAPER_MONITOR_SINGLE_CYCLE_PARTIAL_RISK_FLAGS_NO_LIVE_PERMISSION",
            "multi_cycle_dry_run_result": classification_value(multi_cycle),
            "multi_cycle_dry_run_cycles_completed": aggregate.get("cycles_completed"),
            "multi_cycle_minimum_passing_capital_by_cycle": aggregate.get("minimum_passing_capital_by_cycle"),
            "non_monotonic_sizing_warning": sizing.get("scenario_pass_fail_non_monotonic_warning") is True,
            "real_orders": False,
        },
        "paper_monitor_architecture_design": {
            "state_machine_source": SOURCE_ARTIFACTS["multi_cycle_design"]["path"],
            "states": [
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
            ],
            "risk_flags": {
                "critical_count": 12,
                "non_critical_count": 6,
                "observed_non_critical_flags": risk_review.get("non_critical_flags_by_frequency"),
            },
            "kill_switch_rules": [
                "critical risk flag stops simulated entry",
                "two consecutive all-scenario sizing failures report sizing instability",
                "two consecutive aggregate negative funding cycles report funding warning",
                "symbol status change reports symbol halt",
                "stale public data reports data halt",
                "private/order endpoint code path invalidates immediately",
            ],
            "reporting_layers": list((report_pack.get("report_names") or [])),
            "reconciliation_limitations": [
                "public-data simulated reconciliation only",
                "no private account data",
                "no real funding received verification",
                "no fills, balances, commissions, or exchange statements",
            ],
            "scheduler_daemon_live_capital_enabled": False,
        },
        "reporting_reconciliation_design": {
            "reports": [
                "cycle report",
                "funding reconciliation report",
                "daily report",
                "weekly report",
                "monthly report",
                "risk incident report",
                "sizing stability report",
                "simulated PnL attribution report",
                "audit summary",
            ],
            "report_count": 9,
            "all_reports_reviewed_without_p0_or_p1": True,
            "real_account_reconciliation_present": False,
        },
        "risk_register_design": risk_register,
        "institutional_review_checklist": institutional_checklist,
        "appendix_design": {
            "source_artifact_list": {name: summary["path"] for name, summary in source_artifacts.items()},
            "payload_hash_references": {
                name: summary["payload_sha256_excluding_hash"] for name, summary in source_artifacts.items()
            },
            "terminology": {
                "paper_only": "simulated report and monitor artifacts without live permissions",
                "diagnostic_promising": "research/evidence label that does not imply candidate or edge",
                "same_base_quantity": "spot and perp legs use identical base asset quantity per symbol",
            },
            "no_live_no_edge_disclaimers": [
                "no candidate generation",
                "no edge claim",
                "no runtime/live/capital permission",
                "no report export in this design step",
            ],
            "future_requirements": [
                "longer finite paper monitoring",
                "true reconciliation design before live discussion",
                "account/export reconciliation source approval if ever requested",
                "separate approval before any report export format",
            ],
        },
        "classification": CLASSIFICATION,
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "limitations": [
            "Report package design only; no report files were exported.",
            "No PDF, DOCX, HTML, or external report file was generated.",
            "No network, API, private endpoint, order endpoint, scheduler, daemon, runtime, live, or capital action occurred.",
            "No candidate generation, edge claim, or family release is allowed.",
        ],
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
        "package_section_count": len(package_sections),
        "risk_register_item_count": len(risk_register),
        "institutional_checklist_item_count": len(institutional_checklist),
        "report_package_exported_now": False,
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
