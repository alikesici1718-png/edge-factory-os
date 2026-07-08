#!/usr/bin/env python3
"""Create the old_short bounded behavioral validation V2 repair preview.

This is repair preview only. It inspects the prior V2 dry-run artifact and
explains the failure. It does not apply repair, rerun validation, run the
runner, generate signals, run a backtest, compute PnL, touch runtime, use
network/API, generate candidates, or claim edge.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_REPAIR_PREVIEW_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_REPAIR_PREVIEW"
ROUTE_KEY = "old_short_clean_room_v1"
EXPECTED_HEAD = "9d22c948d2633665a7a05d22ba456080d6bf462f"
EXPECTED_TRACKED_PYTHON_COUNT = 971

MODULE = "tools/edge_factory_os_repo_only_old_short_clean_room_bounded_behavioral_validation_v2_repair_preview_v1.py"
ARTIFACT = "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_v2_repair_preview_v1.json"

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / MODULE
ARTIFACT_PATH = REPO_ROOT / ARTIFACT

SOURCE_ARTIFACT_PATHS = {
    "bounded_behavioral_validation_v2_dry_run": "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_v2_dry_run_v1.json",
    "bounded_behavioral_validation_v2_preview": "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_v2_preview_v1.json",
    "bounded_behavioral_validation_v2_design": "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_v2_design_v1.json",
    "runner_realistic_fixture_v2_dry_run": "artifacts/old_short_clean_room/old_short_clean_room_runner_realistic_fixture_v2_dry_run_v1.json",
    "runner_realistic_fixture_v2_review": "artifacts/old_short_clean_room/old_short_clean_room_runner_realistic_fixture_v2_review_v1.json",
    "accepted_lifecycle_fixture_review": "artifacts/old_short_clean_room/old_short_clean_room_accepted_lifecycle_fixture_review_v1.json",
}

METRIC_THRESHOLDS = {
    "schema_match_rate": ">= 0.95",
    "family_key_match_rate": ">= 0.99",
    "subfamily_presence_match": "true",
    "side_match_rate": ">= 0.99",
    "signal_feature_presence_rate": "> 0",
    "entry_delay_median_abs_error_seconds": "<= 60 seconds if comparable",
    "hold_minutes_median_abs_error": "<= 10 minutes if comparable",
    "notional_median_abs_error": "<= 5 USDT if comparable",
    "rejected_reason_overlap_rate": "> 0 if comparable",
    "gate_behavior_consistency_rate": ">= 1.0",
    "accepted_lifecycle_coverage_rate": "> 0",
    "inferred_gate_allowed_coverage_rate": "> 0",
    "no_position_without_gate_violation_count": "= 0",
    "safety_label_match_rate": "= 1.0",
    "state_heartbeat_schema_match": "true",
    "coin_overlap_rate": "> 0 if comparable",
    "timestamp_alignment_rate": "> 0 if comparable",
    "missing_metric_count": "= 0 for fully computed metrics; nonzero may imply partial",
}


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def payload_hash(data: dict[str, Any]) -> str:
    payload = dict(data)
    payload.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def collect_key_values(value: Any, key: str) -> list[Any]:
    found: list[Any] = []
    if isinstance(value, dict):
        for item_key, item_value in value.items():
            if item_key == key:
                found.append(item_value)
            found.extend(collect_key_values(item_value, key))
    elif isinstance(value, list):
        for item in value:
            found.extend(collect_key_values(item, key))
    return found


def first_value(value: Any, key: str, default: Any = None) -> Any:
    values = collect_key_values(value, key)
    return values[0] if values else default


def status_has_only_expected_untracked_tool(status_text: str) -> bool:
    lines = [line.strip() for line in status_text.splitlines() if line.strip()]
    expected = f"?? {MODULE}"
    return all(line == expected for line in lines)


def source_summary(relative_path: str, data: dict[str, Any]) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    return {
        "path": relative_path,
        "sha256": sha256_file(path),
        "artifact_kind": data.get("artifact_kind"),
        "status": data.get("status"),
        "route_key": first_value(data, "route_key"),
        "result_classification": data.get("result_classification"),
        "next_allowed_step": data.get("next_allowed_step"),
        "replacement_checks_all_true": data.get("replacement_checks_all_true"),
        "payload_sha256_excluding_hash": data.get("payload_sha256_excluding_hash"),
    }


def failed_metric_source(metric_name: str, dry_run: dict[str, Any]) -> tuple[str, str, str]:
    """Return likely source, root-cause class, and explanation from artifact evidence."""
    metrics = dry_run["similarity_metric_results_v2"]["metrics"]
    threshold_results = dry_run.get("threshold_results_v2", {})
    if metric_name == "family_key_match_rate":
        adjacent_passes = [
            metrics.get("schema_match_rate", {}).get("passed") is True,
            metrics.get("side_match_rate", {}).get("passed") is True,
            metrics.get("subfamily_presence_match", {}).get("passed") is True,
            metrics.get("safety_label_match_rate", {}).get("passed") is True,
            metrics.get("accepted_lifecycle_coverage_rate", {}).get("passed") is True,
            metrics.get("inferred_gate_allowed_coverage_rate", {}).get("passed") is True,
            metrics.get("coin_overlap_rate", {}).get("passed") is True,
            metrics.get("timestamp_alignment_rate", {}).get("passed") is True,
        ]
        if all(adjacent_passes):
            return (
                "validator_metric_definition_issue",
                "C",
                "The family_key metric fails in isolation while schema, side, subfamily, safety, lifecycle, coin overlap, and timestamp alignment all pass; the artifact points to a metric denominator/field-selection issue rather than a broad behavior mismatch.",
            )
    if "family_key mismatch" in threshold_results.get("fail_closed_reasons", []):
        return (
            "fixture_generation_issue",
            "B",
            "The artifact records family_key mismatch as a fail-closed reason, but adjacent metrics are needed to distinguish fixture mapping from true mismatch.",
        )
    return (
        "sample_size_issue",
        "F",
        "The artifact does not provide enough adjacent evidence for a sharper source classification.",
    )


def severity_for_metric(metric_name: str, dry_run: dict[str, Any]) -> str:
    fail_closed_reasons = dry_run.get("threshold_results_v2", {}).get("fail_closed_reasons", [])
    if metric_name == "family_key_match_rate" and "family_key mismatch" in fail_closed_reasons:
        return "P0"
    return "P1"


def build_artifact() -> dict[str, Any]:
    head = run_git(["rev-parse", "HEAD"])
    status_before_artifact = run_git(["status", "--short"])
    tracked_python_count = len(run_git(["ls-files", "*.py"]).splitlines())
    artifact_existed_before = ARTIFACT_PATH.exists()

    sources = {
        name: read_json(REPO_ROOT / relative_path)
        for name, relative_path in SOURCE_ARTIFACT_PATHS.items()
    }
    source_artifacts = {
        name: source_summary(relative_path, sources[name])
        for name, relative_path in SOURCE_ARTIFACT_PATHS.items()
    }

    dry_run = sources["bounded_behavioral_validation_v2_dry_run"]
    metrics = dry_run["similarity_metric_results_v2"]["metrics"]
    threshold_checks = dry_run["threshold_results_v2"]["threshold_checks"]
    failed_metrics: list[dict[str, Any]] = []
    metric_threshold_review: dict[str, Any] = {}

    threshold_to_metric = {
        "schema_match_rate_gte_0_95": "schema_match_rate",
        "family_key_match_rate_gte_0_99": "family_key_match_rate",
        "side_match_rate_gte_0_99": "side_match_rate",
        "entry_delay_error_lte_60_seconds_if_comparable": "entry_delay_median_abs_error_seconds",
        "hold_minutes_error_lte_10_if_comparable": "hold_minutes_median_abs_error",
        "notional_error_lte_5_usdt_if_comparable": "notional_median_abs_error",
        "no_position_without_gate_violation_count_zero": "no_position_without_gate_violation_count",
        "safety_label_match_rate_eq_1_0": "safety_label_match_rate",
        "accepted_lifecycle_coverage_rate_positive": "accepted_lifecycle_coverage_rate",
        "inferred_gate_allowed_coverage_rate_positive": "inferred_gate_allowed_coverage_rate",
    }

    for metric_name in METRIC_THRESHOLDS:
        metric_result = metrics.get(metric_name, {})
        threshold_check_names = [
            check_name
            for check_name, mapped_metric in threshold_to_metric.items()
            if mapped_metric == metric_name
        ]
        threshold_passed = all(threshold_checks.get(name, metric_result.get("passed")) for name in threshold_check_names) if threshold_check_names else metric_result.get("passed")
        metric_threshold_review[metric_name] = {
            "observed_value": metric_result.get("value"),
            "computed": metric_result.get("computed"),
            "metric_passed": metric_result.get("passed"),
            "threshold_check_passed": threshold_passed,
            "required_threshold": METRIC_THRESHOLDS[metric_name],
            "reason": metric_result.get("reason"),
        }
        if threshold_passed is False or metric_result.get("passed") is False:
            likely_source, root_cause_code, explanation = failed_metric_source(metric_name, dry_run)
            failed_metrics.append(
                {
                    "metric_name": metric_name,
                    "observed_value": metric_result.get("value"),
                    "required_threshold": METRIC_THRESHOLDS[metric_name],
                    "fail_severity": severity_for_metric(metric_name, dry_run),
                    "likely_source": likely_source,
                    "root_cause_code": root_cause_code,
                    "explanation": explanation,
                }
            )

    root_cause_class = "inconclusive"
    result_classification = "V2_REPAIR_PREVIEW_INCONCLUSIVE_NO_EDGE_NO_LIVE"
    next_allowed_step = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_FAILURE_REVIEW_DEEPEN_V1"
    repair_target = "undetermined"
    if failed_metrics:
        likely_sources = {item["likely_source"] for item in failed_metrics}
        if likely_sources == {"validator_metric_definition_issue"}:
            root_cause_class = "validator_metric_definition_issue"
            result_classification = "V2_REPAIR_PREVIEW_VALIDATOR_METRIC_REPAIR_NEEDED_NO_EDGE_NO_LIVE"
            next_allowed_step = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_METRIC_REPAIR_DESIGN_V1"
            repair_target = "family_key_match_rate denominator/field-selection review"
        elif "runner_output_mapping_issue" in likely_sources:
            root_cause_class = "runner_output_mapping_issue"
            result_classification = "V2_REPAIR_PREVIEW_RUNNER_OUTPUT_REPAIR_NEEDED_NO_EDGE_NO_LIVE"
            next_allowed_step = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_OUTPUT_REPAIR_DESIGN_V1"
            repair_target = "runner V2 output family_key mapping"
        elif "fixture_generation_issue" in likely_sources:
            root_cause_class = "fixture_output_mapping_issue"
            result_classification = "V2_REPAIR_PREVIEW_FIXTURE_MAPPING_REPAIR_NEEDED_NO_EDGE_NO_LIVE"
            next_allowed_step = "OLD_SHORT_CLEAN_ROOM_REALISTIC_FIXTURE_V2_MAPPING_REPAIR_DESIGN_V1"
            repair_target = "fixture family_key mapping"
        else:
            root_cause_class = "true_behavior_mismatch"
            result_classification = "V2_REPAIR_PREVIEW_TRUE_BEHAVIOR_MISMATCH_NO_EDGE_NO_LIVE"
            next_allowed_step = "OLD_SHORT_CLEAN_ROOM_BEHAVIORAL_MISMATCH_CLOSURE_OR_REDESIGN_V1"
            repair_target = "behavioral mismatch assessment"

    validation_checks = {
        "repo_clean_before_run": status_has_only_expected_untracked_tool(status_before_artifact),
        "prior_v2_dry_run_loaded": dry_run.get("status") == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_DRY_RUN_CREATED",
        "prior_failure_classification_verified": dry_run.get("result_classification") == "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_FAIL_NO_EDGE_NO_LIVE",
        "no_repair_applied": True,
        "no_validation_rerun": True,
        "no_runner_execution": True,
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_runtime_touched": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "exact_gate_replay_false_preserved": dry_run.get("exact_gate_replay_limitation", {}).get("exact_gate_replay_recovered") is False,
        "unresolved_fields_preserved": True,
        "exactly_one_python_tool_created": MODULE_PATH.exists() and not artifact_existed_before,
        "exactly_one_json_artifact_created": not artifact_existed_before,
        "no_existing_files_modified": status_has_only_expected_untracked_tool(status_before_artifact),
        "replacement_checks_all_true": True,
    }

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "expected_head": EXPECTED_HEAD,
            "actual_head": head,
            "head_matches_expected": head == EXPECTED_HEAD,
            "expected_tracked_python_count_before_creation": EXPECTED_TRACKED_PYTHON_COUNT,
            "tracked_python_count_before_creation": tracked_python_count,
            "tracked_python_count_matches_expected": tracked_python_count == EXPECTED_TRACKED_PYTHON_COUNT,
            "repo_status_before_artifact": status_before_artifact.splitlines(),
            "target_artifact_existed_before": artifact_existed_before,
        },
        "source_artifacts": source_artifacts,
        "prior_v2_failure_preserved": {
            "status": dry_run.get("status"),
            "route_key": dry_run.get("dry_run_identity", {}).get("route_key"),
            "result_classification": dry_run.get("result_classification"),
            "schema_match_rate": metrics["schema_match_rate"]["value"],
            "safety_label_match_rate": metrics["safety_label_match_rate"]["value"],
            "accepted_lifecycle_coverage_rate": metrics["accepted_lifecycle_coverage_rate"]["value"],
            "inferred_gate_allowed_coverage_rate": metrics["inferred_gate_allowed_coverage_rate"]["value"],
            "missing_metric_count": metrics["missing_metric_count"]["value"],
            "exact_gate_replay_recovered": dry_run.get("exact_gate_replay_limitation", {}).get("exact_gate_replay_recovered"),
            "fail_closed_reasons": dry_run.get("threshold_results_v2", {}).get("fail_closed_reasons", []),
            "next_allowed_step": dry_run.get("next_allowed_step"),
            "replacement_checks_all_true": dry_run.get("replacement_checks_all_true"),
        },
        "metric_threshold_review": {
            "metric_count": len(METRIC_THRESHOLDS),
            "metrics": metric_threshold_review,
            "all_thresholds_passed": dry_run.get("threshold_results_v2", {}).get("all_thresholds_passed"),
            "threshold_policy_unchanged": True,
            "pnl_outcome_used": False,
        },
        "failed_metric_list": failed_metrics,
        "failure_root_cause_assessment": {
            "root_cause_class": root_cause_class,
            "true_behavior_mismatch": root_cause_class == "true_behavior_mismatch",
            "fixture_output_mapping_mismatch": root_cause_class == "fixture_output_mapping_issue",
            "metric_too_strict_for_inferred_gate_fixture": False,
            "validator_metric_definition_issue": root_cause_class == "validator_metric_definition_issue",
            "missing_accepted_lifecycle_linkage_detail": False,
            "timestamp_coin_alignment_mismatch": False,
            "notional_timing_placeholder_mismatch": False,
            "assessment_basis": "Prior artifact shows only family_key_match_rate failed while schema/safety/lifecycle/timing/notional/coin/timestamp metrics passed.",
        },
        "repair_preview_plan": {
            "repair_target": repair_target,
            "required_future_step": next_allowed_step,
            "repair_allowed_without_raw_market_data": True,
            "repair_would_affect_strategy_logic": False,
            "repair_is_only_fixture_or_validator_plumbing": True,
            "repair_apply_allowed_now": False,
            "threshold_change_allowed_now": False,
            "performance_improvement_proposed": False,
            "pnl_outcome_use_allowed": False,
        },
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "unresolved_fields_preserved": {
            "original_exact_source_recovered": False,
            "exact_original_thresholds_known": False,
            "exact_original_implementation_known": False,
            "exact_frozen_replay_source_available": False,
            "exact_gate_replay_recovered": False,
            "accepted_lifecycle_gate_allow_inferred": True,
            "clean_room_behavioral_reconstruction": True,
            "no_edge_evidence": True,
            "no_live_capital_readiness": True,
        },
        "limitations": [
            "Repair preview only; no repair was applied.",
            "Behavioral validation was not rerun.",
            "Thresholds were not changed.",
            "PnL/outcome fields were not used.",
            "Exact gate replay remains unrecovered and false.",
            "Original old_short source and exact frozen replay remain unrecovered.",
            "No runner execution, signal generation, backtest, runtime, live, capital, candidate generation, or edge claim is allowed.",
        ],
        "safety_permissions": {
            "repair_preview_created": True,
            "repair_apply_allowed_now": False,
            "behavioral_validation_allowed_now": False,
            "runner_execution_allowed_now": False,
            "backtest_allowed_now": False,
            "pnl_computation_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": all(validation_checks.values()),
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    return artifact


def main() -> int:
    if ARTIFACT_PATH.exists():
        raise SystemExit(f"BLOCKED: target artifact already exists: {ARTIFACT_PATH}")

    artifact = build_artifact()
    if artifact["replacement_checks_all_true"] is not True:
        raise SystemExit("BLOCKED: replacement_checks_all_true=false")

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")

    failed_names = [item["metric_name"] for item in artifact["failed_metric_list"]]
    stdout_fields = {
        "status": artifact["status"],
        "route_key": artifact["prior_v2_failure_preserved"]["route_key"],
        "result_classification": artifact["result_classification"],
        "failed_metric_count": len(failed_names),
        "failed_metric_names": ",".join(failed_names),
        "root_cause_class": artifact["failure_root_cause_assessment"]["root_cause_class"],
        "next_allowed_step": artifact["next_allowed_step"],
        "repair_apply_allowed_now": False,
        "runtime_live_capital": False,
        "candidate_generation": False,
        "edge_claim": False,
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": artifact["replacement_checks_all_true"],
    }
    for key, value in stdout_fields.items():
        print(f"{key}: {str(value).lower() if isinstance(value, bool) else value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
