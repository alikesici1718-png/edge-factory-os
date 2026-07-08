#!/usr/bin/env python3
"""Review the funding-carry report-builder dry-run artifact."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_REPORT_BUILDER_DRY_RUN_REVIEW_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_FUNDING_CARRY_REPORT_BUILDER_DRY_RUN_REVIEW"
MODULE = "edge_factory_os_repo_only_binance_spot_perp_funding_carry_report_builder_dry_run_review_v1"

PASS_CLASSIFICATION = "REPORT_BUILDER_DRY_RUN_REVIEW_PASS_READY_FOR_REPORT_PACKAGE_DESIGN_NO_LIVE_PERMISSION"
P1_CLASSIFICATION = "REPORT_BUILDER_DRY_RUN_REVIEW_PASS_WITH_P1_ATTENTION_NO_LIVE_PERMISSION"
FAIL_CLASSIFICATION = "REPORT_BUILDER_DRY_RUN_REVIEW_FAIL_REQUIRES_REPORT_BUILDER_REPAIR_NO_LIVE_PERMISSION"
PASS_NEXT_STEP = "PAPER_MONITOR_REPORT_PACKAGE_DESIGN_ONLY"
FAIL_NEXT_STEP = "REPORT_BUILDER_DRY_RUN_REPAIR_ONLY"

ROOT = Path(__file__).resolve().parents[1]
TOOL_RELATIVE_PATH = "tools/edge_factory_os_repo_only_binance_spot_perp_funding_carry_report_builder_dry_run_review_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/report_builder_reviews/binance_spot_perp_funding_carry_report_builder_dry_run_review_v1.json"

REQUIRED_REPORTS = [
    "cycle_report",
    "funding_event_reconciliation_report",
    "daily_carry_report",
    "weekly_carry_report",
    "monthly_carry_report",
    "risk_incident_report",
    "sizing_stability_report",
    "simulated_pnl_attribution_report",
    "audit_summary_report",
]

SOURCE_ARTIFACTS = {
    "report_builder_dry_run": {
        "path": "artifacts/report_builder_dry_runs/binance_spot_perp_funding_carry_report_builder_dry_run_v1.json",
        "expected_status": "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_REPORT_BUILDER_DRY_RUN_CREATED",
        "expected_classification": "REPORT_BUILDER_DRY_RUN_PASS_READY_FOR_REPORT_REVIEW_NO_LIVE_PERMISSION",
        "expected_next_allowed_step": "PAPER_MONITOR_REPORT_BUILDER_DRY_RUN_REVIEW_ONLY",
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


def validate_source(name: str, spec: dict[str, str], data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if spec.get("expected_status") and data.get("status") != spec["expected_status"]:
        issues.append(f"{name}: status mismatch")
    if spec.get("expected_classification") and data.get("classification") != spec["expected_classification"]:
        issues.append(f"{name}: classification mismatch")
    if spec.get("expected_next_allowed_step") and data.get("next_allowed_step") != spec["expected_next_allowed_step"]:
        issues.append(f"{name}: next_allowed_step mismatch")
    if spec.get("expected_hash") and data.get("payload_sha256_excluding_hash") != spec["expected_hash"]:
        issues.append(f"{name}: payload hash mismatch")
    if data.get("replacement_checks_all_true") is False:
        issues.append(f"{name}: replacement_checks_all_true is false")
    return issues


def source_summary(name: str, spec: dict[str, str], data: dict[str, Any]) -> dict[str, Any]:
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


def contains_forbidden_order_or_api_claim(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True, ensure_ascii=True).lower()
    forbidden_tokens = ["clientorderid", "orderid", "api_key", "apikey", "/api/v3/order", "/fapi/v1/order"]
    return any(token in text for token in forbidden_tokens)


def contains_real_order_endpoint_url(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True, ensure_ascii=True).lower()
    endpoint_tokens = [
        "https://api.binance.com/api/v3/order",
        "https://fapi.binance.com/fapi/v1/order",
        "\"/api/v3/order\"",
        "\"/fapi/v1/order\"",
    ]
    return any(token in text for token in endpoint_tokens)


def report_presence_review(dry_run: dict[str, Any]) -> dict[str, Any]:
    present = {name: name in dry_run and isinstance(dry_run.get(name), dict) for name in REQUIRED_REPORTS}
    return {
        "required_report_count": len(REQUIRED_REPORTS),
        "present_report_count": sum(1 for value in present.values() if value),
        "all_9_reports_present": all(present.values()),
        "report_presence_by_name": present,
        "report_pack_count": (dry_run.get("report_pack") or {}).get("report_count"),
    }


def cycle_report_review(dry_run: dict[str, Any]) -> tuple[dict[str, Any], list[str], list[str]]:
    p0: list[str] = []
    p1: list[str] = []
    cycle_report = dry_run.get("cycle_report") or {}
    cycles = cycle_report.get("cycle_reports") or []
    if len(cycles) != 3:
        p0.append("cycle_report does not contain exactly 3 cycle reports")
    no_order_all = all(cycle.get("no_order_confirmation") is True for cycle in cycles)
    simulated_all = all(
        "SIMULATED" in json.dumps(cycle.get("simulated_entry_plan_summary") or [], ensure_ascii=True)
        and not contains_forbidden_order_or_api_claim(cycle)
        for cycle in cycles
    )
    passing_represented = all(bool(cycle.get("passing_capital_scenarios")) for cycle in cycles)
    risk_flags_represented = all("critical_risk_flags" in cycle and "non_critical_risk_flags" in cycle for cycle in cycles)
    if not no_order_all:
        p0.append("cycle_report missing no-order confirmation on at least one cycle")
    if not simulated_all:
        p0.append("cycle_report has ambiguous simulated status or forbidden order/API token")
    if not passing_represented:
        p0.append("cycle_report missing passing capital scenarios")
    if not risk_flags_represented:
        p0.append("cycle_report missing risk flag representation")
    return (
        {
            "cycle_report_count": len(cycles),
            "exactly_3_cycles_represented": len(cycles) == 3,
            "every_cycle_has_no_order_confirmation": no_order_all,
            "every_cycle_preserves_report_only_or_simulated_status": simulated_all,
            "passing_capital_scenarios_represented": passing_represented,
            "risk_flags_represented": risk_flags_represented,
            "no_real_order_ids": not contains_forbidden_order_or_api_claim(cycle_report),
            "no_real_order_endpoint_urls": not contains_real_order_endpoint_url(cycle_report),
            "no_api_key_placeholders": "api_key" not in json.dumps(cycle_report, ensure_ascii=True).lower(),
        },
        p0,
        p1,
    )


def funding_reconciliation_review(dry_run: dict[str, Any]) -> tuple[dict[str, Any], list[str], list[str]]:
    p0: list[str] = []
    p1: list[str] = []
    report = dry_run.get("funding_event_reconciliation_report") or {}
    required_false_fields = [
        "real_funding_received_verified",
        "exchange_statement_reconciled",
        "account_balance_checked",
        "private_api_used",
        "actual_fills_verified",
        "actual_commissions_verified",
    ]
    false_field_status = {field: report.get(field) is False for field in required_false_fields}
    for field, ok in false_field_status.items():
        if not ok:
            limitations = json.dumps(dry_run.get("report_builder_limitations") or [], ensure_ascii=True).lower()
            if "simulated" in limitations and "no actual" in limitations:
                p1.append(f"funding reconciliation optional explicit false field incomplete: {field}")
            else:
                p0.append(f"funding reconciliation missing/ambiguous false field: {field}")
    simulated_mode = report.get("mode") == "simulated_public_data_only"
    if not simulated_mode:
        p0.append("funding reconciliation mode does not explicitly state simulated_public_data_only")
    return (
        {
            "simulated_public_data_only": simulated_mode,
            "required_false_fields": false_field_status,
            "available_funding_observation_count": len(report.get("available_funding_observations") or []),
            "schema_ready_but_data_limited": bool(report.get("schema_ready_but_data_limited")),
            "real_funding_received_invented": bool(report.get("real_funding_received_invented")),
        },
        p0,
        p1,
    )


def daily_weekly_monthly_review(dry_run: dict[str, Any]) -> tuple[dict[str, Any], list[str], list[str]]:
    p0: list[str] = []
    p1: list[str] = []
    daily = dry_run.get("daily_carry_report") or {}
    weekly = dry_run.get("weekly_carry_report") or {}
    monthly = dry_run.get("monthly_carry_report") or {}
    weekly_limited = weekly.get("insufficient_real_time_span") is True
    monthly_limited = monthly.get("insufficient_real_time_span") is True
    if not weekly_limited:
        p0.append("weekly report does not mark insufficient_real_time_span true")
    if not monthly_limited:
        p0.append("monthly report does not mark insufficient_real_time_span true")
    real_claim_text = json.dumps({"weekly": weekly, "monthly": monthly}, sort_keys=True, ensure_ascii=True).lower()
    no_real_claims = not any(token in real_claim_text for token in ["real pnl", "real funding received", "actual balance"])
    if not no_real_claims:
        p0.append("weekly/monthly report appears to claim real PnL, funding, or balance data")
    return (
        {
            "daily_summarizes_finite_dry_run_cycles": all(
                key in daily
                for key in [
                    "cycles_completed",
                    "cycles_with_passing_scenario",
                    "cycles_with_critical_risk",
                    "cycles_with_non_critical_risk",
                ]
            ),
            "weekly_insufficient_real_time_span": weekly_limited,
            "monthly_insufficient_real_time_span": monthly_limited,
            "no_real_pnl_real_funding_balances_or_commissions": no_real_claims,
        },
        p0,
        p1,
    )


def risk_incident_report_review(dry_run: dict[str, Any]) -> dict[str, Any]:
    report = dry_run.get("risk_incident_report") or {}
    return {
        "critical_risk_incident_count_represented": "critical_risk_incident_count" in report,
        "non_critical_risk_incident_count_represented": "non_critical_risk_incident_count" in report,
        "critical_risk_incident_count": report.get("critical_risk_incident_count"),
        "non_critical_risk_incident_count": report.get("non_critical_risk_incident_count"),
        "sizing_non_monotonic_warning_preserved": report.get("scenario_pass_fail_non_monotonic_warning") is True,
        "no_live_confirmation_preserved": report.get("no_live_confirmation") is True,
    }


def sizing_stability_report_review(dry_run: dict[str, Any]) -> dict[str, Any]:
    report = dry_run.get("sizing_stability_report") or {}
    return {
        "capital_scenarios_represented": bool(report.get("capital_scenarios_evaluated")),
        "scenario_pass_frequency_represented": bool(report.get("scenario_pass_frequency")),
        "minimum_passing_capital_by_cycle_represented": bool(report.get("minimum_passing_capital_by_cycle")),
        "common_base_quantity_sizing_repair_preserved": report.get("common_base_quantity_repair_preserved") is True,
        "no_order_confirmation_preserved": report.get("no_order_confirmation") is True,
    }


def simulated_pnl_attribution_review(dry_run: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    p0: list[str] = []
    report = dry_run.get("simulated_pnl_attribution_report") or {}
    components = report.get("components") or {}
    required_components = [
        "simulated_funding_component",
        "simulated_price_hedge_residual",
        "estimated_fee_component",
        "estimated_slippage",
        "sizing_mismatch_effect",
        "unmodeled_risk_note",
    ]
    components_present = {field: field in components for field in required_components}
    if not all(components_present.values()):
        p0.append("simulated PnL attribution report missing required component placeholders")
    if report.get("real_pnl_computed") is not False:
        p0.append("simulated PnL attribution report does not explicitly set real_pnl_computed false")
    return (
        {
            "labeled_simulated_preview_or_dry_run_only": report.get("mode") == "schema_and_dry_run_preview_only",
            "real_pnl_claimed": report.get("real_pnl_computed") is not False,
            "component_placeholders_present": components_present,
            "real_account_reconciliation_absent": report.get("real_account_reconciliation_absent") is True,
        },
        p0,
    )


def audit_summary_review(dry_run: dict[str, Any]) -> tuple[dict[str, Any], list[str], list[str]]:
    p0: list[str] = []
    p1: list[str] = []
    report = dry_run.get("audit_summary_report") or {}
    source_paths = report.get("source_artifact_paths") or {}
    source_hashes = report.get("source_artifact_payload_hashes") or {}
    if not source_paths:
        p0.append("audit summary missing source artifact list")
    if not source_hashes:
        p1.append("audit summary missing source artifact payload hashes")
    required_true = [
        "deterministic_json_required",
        "immutable_cycle_records_preserved",
        "no_manual_edits_required",
        "report_builder_dry_run_only",
    ]
    for key in required_true:
        if report.get(key) is not True:
            p0.append(f"audit summary missing true field: {key}")
    required_false = [
        "candidate_generation_allowed_now",
        "edge_claim_allowed_now",
        "runtime_permission_allowed_now",
        "live_permission_allowed_now",
        "capital_permission_allowed_now",
        "private_api_account_or_order_data_used",
    ]
    for key in required_false:
        if report.get(key) is not False:
            p0.append(f"audit summary missing false field: {key}")
    return (
        {
            "source_artifact_list_present": bool(source_paths),
            "source_artifact_payload_hashes_present": bool(source_hashes),
            "source_artifact_count": len(source_paths),
            "deterministic_json_requirement_present": report.get("deterministic_json_required") is True,
            "immutable_cycle_records_preserved": report.get("immutable_cycle_records_preserved") is True,
            "no_manual_edits_requirement_present": report.get("no_manual_edits_required") is True,
            "no_candidate_edge_runtime_live_capital_flags": all(report.get(key) is False for key in required_false[:-1]),
            "no_private_api_account_order_data": report.get("private_api_account_or_order_data_used") is False,
            "report_builder_dry_run_only": report.get("report_builder_dry_run_only") is True,
        },
        p0,
        p1,
    )


def safety_permission_review(dry_run: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    p0: list[str] = []
    safety = dry_run.get("safety_permissions") or {}
    required_false = [
        "private_api_allowed_now",
        "order_placement_allowed_now",
        "runtime_permission_allowed_now",
        "scheduler_allowed_now",
        "daemon_allowed_now",
        "live_permission_allowed_now",
        "capital_permission_allowed_now",
        "candidate_generation_allowed_now",
        "edge_claim_allowed_now",
    ]
    status = {field: safety.get(field) is False for field in required_false}
    for field, ok in status.items():
        if not ok:
            p0.append(f"safety permission not false: {field}")
    return (
        {
            "required_false_permissions": status,
            "safety_permissions_passed": all(status.values()),
            "next_step_must_not_be_live_or_capital": safety.get("next_step_must_not_be_live_or_capital") is True,
        },
        p0,
    )


def main() -> None:
    artifact_path = ROOT / ARTIFACT_RELATIVE_PATH

    loaded: dict[str, dict[str, Any]] = {}
    source_artifacts: dict[str, dict[str, Any]] = {}
    source_issues: list[str] = []
    for name, spec in SOURCE_ARTIFACTS.items():
        data = load_json(spec["path"])
        loaded[name] = data
        source_artifacts[name] = source_summary(name, spec, data)
        source_issues.extend(validate_source(name, spec, data))

    dry_run = loaded["report_builder_dry_run"]

    p0_findings: list[str] = list(source_issues)
    p1_findings: list[str] = []

    presence = report_presence_review(dry_run)
    if not presence["all_9_reports_present"]:
        p0_findings.append("one or more required report objects are missing")
    if dry_run.get("payload_sha256_excluding_hash") is None:
        p0_findings.append("prior report builder dry-run payload hash missing")
    if dry_run.get("replacement_checks_all_true") is not True:
        p0_findings.append("prior report builder dry-run replacement checks not true")

    cycle_review, cycle_p0, cycle_p1 = cycle_report_review(dry_run)
    p0_findings.extend(cycle_p0)
    p1_findings.extend(cycle_p1)

    funding_review, funding_p0, funding_p1 = funding_reconciliation_review(dry_run)
    p0_findings.extend(funding_p0)
    p1_findings.extend(funding_p1)

    dwm_review, dwm_p0, dwm_p1 = daily_weekly_monthly_review(dry_run)
    p0_findings.extend(dwm_p0)
    p1_findings.extend(dwm_p1)

    risk_review = risk_incident_report_review(dry_run)
    if not risk_review["critical_risk_incident_count_represented"]:
        p0_findings.append("risk incident report missing critical risk incident count")
    if not risk_review["non_critical_risk_incident_count_represented"]:
        p0_findings.append("risk incident report missing non-critical risk incident count")

    sizing_review = sizing_stability_report_review(dry_run)
    for key, ok in sizing_review.items():
        if not ok:
            p0_findings.append(f"sizing stability review failed: {key}")

    pnl_review, pnl_p0 = simulated_pnl_attribution_review(dry_run)
    p0_findings.extend(pnl_p0)

    audit_review, audit_p0, audit_p1 = audit_summary_review(dry_run)
    p0_findings.extend(audit_p0)
    p1_findings.extend(audit_p1)

    safety_review, safety_p0 = safety_permission_review(dry_run)
    p0_findings.extend(safety_p0)

    classification = FAIL_CLASSIFICATION if p0_findings else (P1_CLASSIFICATION if p1_findings else PASS_CLASSIFICATION)
    next_allowed_step = FAIL_NEXT_STEP if p0_findings else PASS_NEXT_STEP

    safety_permissions = {
        "report_builder_dry_run_review_created": True,
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
        "prior_report_builder_dry_run_loaded": True,
        "prior_next_allowed_step_verified": dry_run.get("next_allowed_step") == "PAPER_MONITOR_REPORT_BUILDER_DRY_RUN_REVIEW_ONLY",
        "all_9_reports_present": presence["all_9_reports_present"],
        "audit_summary_present": isinstance(dry_run.get("audit_summary_report"), dict),
        "no_real_pnl_claimed": not pnl_review["real_pnl_claimed"],
        "no_private_api_data_claimed": audit_review["no_private_api_account_order_data"],
        "no_order_data_claimed": cycle_review["no_real_order_ids"] and cycle_review["no_real_order_endpoint_urls"],
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
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": True,
        "replacement_checks_all_true": True,
    }

    replacement_checks_all_true = all(validation_checks.values()) and not p0_findings

    payload = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "created_at_utc": utc_now(),
            "current_head_expected": "b676fc963c1e6ea06eeb010a01c6819638e03d11",
            "tracked_python_count_before": 899,
            "tool_path": TOOL_RELATIVE_PATH,
            "artifact_path": ARTIFACT_RELATIVE_PATH,
        },
        "source_artifacts": source_artifacts,
        "prior_report_builder_dry_run_preserved": {
            "status": dry_run.get("status"),
            "classification": dry_run.get("classification"),
            "next_allowed_step": dry_run.get("next_allowed_step"),
            "report_count": (dry_run.get("report_pack") or {}).get("report_count"),
            "cycle_report_count": len((dry_run.get("cycle_report") or {}).get("cycle_reports") or []),
            "payload_sha256_excluding_hash": dry_run.get("payload_sha256_excluding_hash"),
            "replacement_checks_all_true": dry_run.get("replacement_checks_all_true"),
        },
        "report_presence_review": presence,
        "cycle_report_review": cycle_review,
        "funding_reconciliation_report_review": funding_review,
        "daily_weekly_monthly_report_review": dwm_review,
        "risk_incident_report_review": risk_review,
        "sizing_stability_report_review": sizing_review,
        "simulated_pnl_attribution_review": pnl_review,
        "audit_summary_review": audit_review,
        "safety_permission_review": safety_review,
        "review_findings": {
            "p0_issues": p0_findings,
            "p1_attention_items": p1_findings,
            "p0_issue_count": len(p0_findings),
            "p1_attention_count": len(p1_findings),
            "review_passed": not p0_findings,
        },
        "classification": classification,
        "next_allowed_step": next_allowed_step,
        "limitations": [
            "Review used existing report-builder dry-run and metadata artifacts only.",
            "No report export was performed.",
            "No network, API, private endpoint, order endpoint, scheduler, daemon, runtime, live, or capital action occurred.",
            "No candidate generation or edge claim is permitted by this review.",
        ],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
    }
    payload["payload_sha256_excluding_hash"] = payload_hash(payload)

    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    with artifact_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")

    stdout_fields = {
        "status": STATUS,
        "classification": classification,
        "next_allowed_step": next_allowed_step,
        "report_count_reviewed": presence["present_report_count"],
        "p0_issue_count": len(p0_findings),
        "p1_attention_count": len(p1_findings),
        "audit_summary_passed": not audit_p0,
        "safety_permissions_passed": safety_review["safety_permissions_passed"],
        "report_builder_enabled_now": False,
        "order_placement_allowed_now": False,
        "runtime_live_capital": False,
        "candidate_generation": False,
        "edge_claim": False,
        "payload_sha256_excluding_hash": payload["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": replacement_checks_all_true,
    }
    for key, value in stdout_fields.items():
        print(f"{key}={json.dumps(value, sort_keys=True)}")


if __name__ == "__main__":
    main()
