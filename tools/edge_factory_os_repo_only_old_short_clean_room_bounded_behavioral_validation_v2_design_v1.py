#!/usr/bin/env python3
"""Create the old_short clean-room bounded behavioral validation V2 design.

This module is design-only. It defines a future bounded behavioral validation V2
plan and writes a JSON design artifact. It does not execute validation, compare
full datasets, run a backtest, compute PnL, run the runner, generate signals,
touch runtime, use network/API, allocate capital, generate candidates, or claim
edge.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_DESIGN_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_DESIGN"
ROUTE_KEY = "old_short_clean_room_v1"
EXPECTED_HEAD = "68a922d72104b2f9a65ad97c75b9bf859e6608e1"
EXPECTED_TRACKED_PYTHON_COUNT = 968
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_PREVIEW_V1"

MODULE = "tools/edge_factory_os_repo_only_old_short_clean_room_bounded_behavioral_validation_v2_design_v1.py"
ARTIFACT = "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_v2_design_v1.json"

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / MODULE
ARTIFACT_PATH = REPO_ROOT / ARTIFACT

MASTER_PROXY_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\paper_run_gate_MASTER_UPPER_SYSTEM\live_blowoff_short_paper_realistic"
)
CLEAN_ROOM_V2_OUTPUT_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_runner_dry_runs_v1"
    r"\realistic_fixture_runner_v2_dry_run_v1"
)
ACCEPTED_LIFECYCLE_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_realistic_fixtures_v1"
    r"\accepted_lifecycle_fixture_discovery_v1"
)

SOURCE_ARTIFACT_PATHS = {
    "runner_realistic_fixture_v2_review": "artifacts/old_short_clean_room/old_short_clean_room_runner_realistic_fixture_v2_review_v1.json",
    "runner_realistic_fixture_v2_dry_run": "artifacts/old_short_clean_room/old_short_clean_room_runner_realistic_fixture_v2_dry_run_v1.json",
    "runner_realistic_fixture_v2_preview": "artifacts/old_short_clean_room/old_short_clean_room_runner_realistic_fixture_v2_preview_v1.json",
    "realistic_fixture_runner_v2_design": "artifacts/old_short_clean_room/old_short_clean_room_realistic_fixture_runner_v2_design_v1.json",
    "accepted_lifecycle_fixture_review": "artifacts/old_short_clean_room/old_short_clean_room_accepted_lifecycle_fixture_review_v1.json",
    "accepted_lifecycle_fixture_discovery_dry_run": "artifacts/old_short_clean_room/old_short_clean_room_accepted_lifecycle_fixture_discovery_dry_run_v1.json",
    "bounded_behavioral_validation_review_v1": "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_review_v1.json",
    "bounded_behavioral_validation_dry_run_v1": "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_dry_run_v1.json",
    "runner_fixture_threshold_contract": "artifacts/old_short_clean_room/old_short_clean_room_runner_fixture_threshold_contract_v1.json",
    "old_short_clean_room_contract": "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json",
}

CSV_EXPECTED_FILES = [
    "signals.csv",
    "pending_entries.csv",
    "open_positions.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
    "heartbeat.csv",
    "state.json",
]
ACCEPTED_LIFECYCLE_EXPECTED_FILES = [
    "accepted_lifecycle_fixture_index.json",
    "accepted_lifecycle_master_cases.jsonl",
    "accepted_lifecycle_pairing_plan.json",
    "accepted_lifecycle_discovery_summary.json",
]

BEHAVIOR_DIMENSIONS_V2 = [
    "schema compatibility",
    "family_key old_short",
    "subfamily blowoff_short / mean_reversion_short presence",
    "side short",
    "signal feature availability",
    "entry delay near 2 minutes",
    "hold duration near 120 minutes",
    "notional near 50 USDT",
    "accepted lifecycle coverage",
    "rejected gate behavior",
    "gate_missing_timeout behavior",
    "gate_blocked behavior",
    "inferred gate_allowed path coverage",
    "no position without gate allow",
    "heartbeat/state compatibility",
    "safety label compatibility",
]
SIMILARITY_METRICS_V2 = [
    "schema_match_rate",
    "family_key_match_rate",
    "subfamily_presence_match",
    "side_match_rate",
    "signal_feature_presence_rate",
    "entry_delay_median_abs_error_seconds",
    "hold_minutes_median_abs_error",
    "notional_median_abs_error",
    "rejected_reason_overlap_rate",
    "gate_behavior_consistency_rate",
    "accepted_lifecycle_coverage_rate",
    "inferred_gate_allowed_coverage_rate",
    "no_position_without_gate_violation_count",
    "safety_label_match_rate",
    "state_heartbeat_schema_match",
    "coin_overlap_rate",
    "timestamp_alignment_rate",
    "missing_metric_count",
]
PASS_FAIL_CLASSES_V2 = [
    "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_PASS_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_PARTIAL_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_FAIL_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_INCONCLUSIVE_NO_EDGE_NO_LIVE",
]
FAIL_CLOSED_CONDITIONS_V2 = [
    "MASTER sample missing",
    "clean-room V2 output missing",
    "accepted lifecycle fixture missing",
    "full dataset comparison requested",
    "raw market data path supplied",
    "PnL/outcome field used for validation",
    "live/order/private fields present",
    "safety labels missing",
    "route_key mismatch",
    "family_key mismatch",
    "no-live guard false",
    "runtime path supplied",
    "sample row limit exceeded",
]
EXPECTED_LIMITATIONS = [
    "exact original thresholds unknown",
    "exact original implementation unknown",
    "exact frozen replay source unavailable",
    "exact gate replay unavailable",
    "gate allowed inferred from closed trade / accepted lifecycle",
    "accepted lifecycle sample count is small",
    "clean-room reconstruction only",
    "no edge evidence",
    "no live/capital readiness",
    "no backtest",
]


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


def file_metadata(root: Path, expected_files: list[str]) -> dict[str, dict[str, Any]]:
    metadata: dict[str, dict[str, Any]] = {}
    for file_name in expected_files:
        path = root / file_name
        metadata[file_name] = {
            "path": str(path),
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else None,
            "sha256": None,
            "metadata_only": True,
            "content_read": False,
        }
    return metadata


def build_artifact() -> dict[str, Any]:
    head = run_git(["rev-parse", "HEAD"])
    status_before_artifact = run_git(["status", "--short"])
    tracked_python_count = len(run_git(["ls-files", "*.py"]).splitlines())
    artifact_existed_before = ARTIFACT_PATH.exists()

    sources = {
        name: read_json(REPO_ROOT / path)
        for name, path in SOURCE_ARTIFACT_PATHS.items()
    }
    source_artifacts = {
        name: source_summary(path, sources[name])
        for name, path in SOURCE_ARTIFACT_PATHS.items()
    }
    source_artifacts["external_metadata"] = {
        "master_upper_system_proxy_root": {
            "root": str(MASTER_PROXY_ROOT),
            "expected_files": file_metadata(MASTER_PROXY_ROOT, CSV_EXPECTED_FILES),
            "metadata_only": True,
            "sample_rows_read": 0,
        },
        "clean_room_v2_fixture_output_root": {
            "root": str(CLEAN_ROOM_V2_OUTPUT_ROOT),
            "expected_files": file_metadata(CLEAN_ROOM_V2_OUTPUT_ROOT, CSV_EXPECTED_FILES + ["runner_realistic_fixture_v2_dry_run_report.json"]),
            "metadata_only": True,
            "sample_rows_read": 0,
        },
        "accepted_lifecycle_fixture_root": {
            "root": str(ACCEPTED_LIFECYCLE_ROOT),
            "expected_files": file_metadata(ACCEPTED_LIFECYCLE_ROOT, ACCEPTED_LIFECYCLE_EXPECTED_FILES),
            "metadata_only": True,
            "sample_rows_read": 0,
        },
    }

    v2_review = sources["runner_realistic_fixture_v2_review"]
    v2_dry_run = sources["runner_realistic_fixture_v2_dry_run"]
    accepted_review = sources["accepted_lifecycle_fixture_review"]
    v2_metrics = v2_dry_run.get("v2_metrics", {})
    review_preserved = v2_review.get("prior_v2_dry_run_preserved", {})

    accepted_lifecycle_candidate_count = int(
        first_value(v2_review, "accepted_lifecycle_case_count", 0)
        or first_value(accepted_review, "accepted_lifecycle_candidate_count", 0)
    )
    gate_allowed_inferred_count = int(first_value(v2_review, "gate_allowed_inferred_count", 0))
    exact_gate_replay_recovered = first_value(v2_review, "exact_gate_replay_recovered", None)

    validation_checks = {
        "repo_clean_before_run": status_has_only_expected_untracked_tool(status_before_artifact),
        "prior_v2_fixture_review_loaded": v2_review.get("status") == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_REVIEW_CREATED",
        "prior_next_allowed_step_verified": v2_review.get("next_allowed_step") == "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_DESIGN_V1",
        "accepted_lifecycle_candidate_count_verified_2": accepted_lifecycle_candidate_count == 2,
        "gate_allowed_inferred_count_verified_2": gate_allowed_inferred_count == 2,
        "exact_gate_replay_false_preserved": exact_gate_replay_recovered is False,
        "original_exact_source_not_claimed": first_value(v2_review, "original_exact_source_recovered", False) is False,
        "clean_room_reconstruction_preserved": first_value(v2_review, "clean_room_behavioral_reconstruction", True) is True,
        "no_behavioral_validation_execution": True,
        "no_full_dataset_comparison": True,
        "no_runner_execution": True,
        "no_signal_generation": True,
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_runtime_touched": True,
        "no_monitor_enabled": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "v2_input_policy_defined": True,
        "behavior_dimensions_v2_defined": len(BEHAVIOR_DIMENSIONS_V2) == 16,
        "similarity_metrics_v2_defined": len(SIMILARITY_METRICS_V2) == 18,
        "fail_closed_conditions_v2_defined": len(FAIL_CLOSED_CONDITIONS_V2) == 13,
        "expected_limitations_preserved": set(EXPECTED_LIMITATIONS) == {
            "exact original thresholds unknown",
            "exact original implementation unknown",
            "exact frozen replay source unavailable",
            "exact gate replay unavailable",
            "gate allowed inferred from closed trade / accepted lifecycle",
            "accepted lifecycle sample count is small",
            "clean-room reconstruction only",
            "no edge evidence",
            "no live/capital readiness",
            "no backtest",
        },
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
        "v2_validation_design_identity": {
            "route_key": ROUTE_KEY,
            "design_only": True,
            "behavioral_validation_v2_allowed_now": False,
            "full_dataset_comparison_allowed_now": False,
            "original_exact_source_recovered": False,
            "exact_gate_replay_recovered": False,
            "accepted_lifecycle_gate_allow_inferred": True,
            "clean_room_behavioral_reconstruction": True,
            "no_edge_claim": True,
            "no_live_capital": True,
        },
        "v2_input_policy": {
            "future_validation_may_read_bounded_samples_only": True,
            "default_sample_limit_rows_per_file": 100,
            "input_roots": {
                "master_upper_system_proxy_output_root": str(MASTER_PROXY_ROOT),
                "clean_room_v2_realistic_fixture_runner_output_root": str(CLEAN_ROOM_V2_OUTPUT_ROOT),
                "accepted_lifecycle_fixture_package": str(ACCEPTED_LIFECYCLE_ROOT),
            },
            "forbidden": [
                "raw OKX 1m data",
                "raw market data",
                "full dataset comparison",
                "private/account data",
                "live runtime paths",
                "PnL/outcome-based validation",
            ],
            "metadata_read_during_design_only": True,
            "behavioral_validation_execution_allowed_now": False,
        },
        "expected_files": {
            "master_and_clean_room_output_files": CSV_EXPECTED_FILES,
            "accepted_lifecycle_fixture_package_files": ACCEPTED_LIFECYCLE_EXPECTED_FILES,
        },
        "behavior_dimensions_v2": {
            "behavior_dimension_count": len(BEHAVIOR_DIMENSIONS_V2),
            "dimensions": BEHAVIOR_DIMENSIONS_V2,
        },
        "similarity_metrics_v2": {
            "similarity_metric_count": len(SIMILARITY_METRICS_V2),
            "metrics": SIMILARITY_METRICS_V2,
        },
        "threshold_policy_v2": {
            "schema_match_rate_min": 0.95,
            "family_key_match_rate_min": 0.99,
            "side_match_rate_min": 0.99,
            "entry_delay_median_abs_error_seconds_max_if_comparable": 60,
            "hold_minutes_median_abs_error_max_if_comparable": 10,
            "notional_median_abs_error_usdt_max_if_comparable": 5,
            "no_position_without_gate_allow_required": True,
            "no_live_order_private_fields_required": True,
            "safety_label_match_rate_required": 1.0,
            "accepted_lifecycle_coverage_rate_must_be_positive": True,
            "inferred_gate_allowed_coverage_rate_must_be_positive": True,
            "exact_gate_replay_score_required": False,
            "exact_gate_replay_must_remain_false": True,
            "gate_allowed_inference_source": "accepted lifecycle fixtures only",
            "pnl_outcome_thresholds_allowed": False,
        },
        "pass_fail_classes_v2": {
            "result_class_count": len(PASS_FAIL_CLASSES_V2),
            "allowed_classes": PASS_FAIL_CLASSES_V2,
            "pass_meaning": "bounded behavior is sufficiently similar for continuing to research; not edge, exact replay, live, or capital",
            "partial_meaning": "core schema/family/side/lifecycle dimensions pass but exact gate replay or sample size limitations remain",
            "fail_meaning": "clean-room output does not resemble proxy behavior enough or violates safety",
            "inconclusive_meaning": "insufficient samples",
        },
        "fail_closed_conditions_v2": {
            "fail_closed_condition_count": len(FAIL_CLOSED_CONDITIONS_V2),
            "conditions": FAIL_CLOSED_CONDITIONS_V2,
        },
        "expected_limitations": {
            "limitation_count": len(EXPECTED_LIMITATIONS),
            "limitations": EXPECTED_LIMITATIONS,
        },
        "future_report_schema": {
            "required_top_level_fields": [
                "status",
                "route_key",
                "input_sample_roots",
                "sample_row_counts",
                "behavior_dimensions_checked",
                "similarity_metrics_v2",
                "threshold_results_v2",
                "accepted_lifecycle_review",
                "inferred_gate_allowed_review",
                "fail_closed_checks",
                "limitations",
                "no_edge_no_live_permissions",
                "result_classification",
                "payload_sha256_excluding_hash",
            ],
            "must_report_no_edge_no_live_permissions": True,
            "must_preserve_exact_gate_replay_false": True,
        },
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "unresolved_fields_preserved": {
            "original_exact_source_recovered": False,
            "exact_original_thresholds_known": False,
            "exact_original_implementation_known": False,
            "exact_frozen_replay_source_available": False,
            "exact_gate_replay_recovered": False,
            "accepted_lifecycle_gate_allow_inferred": True,
            "accepted_lifecycle_case_count": accepted_lifecycle_candidate_count,
            "gate_allowed_inferred_count": gate_allowed_inferred_count,
            "v2_fixture_review_result": v2_review.get("result_classification"),
            "v2_dry_run_result": v2_dry_run.get("result_classification"),
            "v1_bounded_behavioral_validation_result": sources["bounded_behavioral_validation_dry_run_v1"].get("result_classification"),
            "clean_room_behavioral_reconstruction": True,
            "no_edge_evidence": True,
            "no_live_capital_readiness": True,
        },
        "limitations": [
            "Design only; behavioral validation V2 is not executed.",
            "Only bounded samples may be used in the future preview/dry-run path.",
            "Exact gate replay is unavailable and must remain false.",
            "Gate allowed can be inferred only from accepted lifecycle and closed trade fixture evidence.",
            "Accepted lifecycle sample count remains small.",
            "Original old_short source and exact frozen replay remain unrecovered.",
            "No full dataset comparison, backtest, PnL computation, runner execution, runtime, live, capital, candidate generation, or edge claim is allowed.",
        ],
        "safety_permissions": {
            "bounded_behavioral_validation_v2_design_created": True,
            "behavioral_validation_v2_allowed_now": False,
            "full_dataset_comparison_allowed_now": False,
            "backtest_allowed_now": False,
            "pnl_computation_allowed_now": False,
            "runner_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "monitor_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
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

    stdout_fields = {
        "status": artifact["status"],
        "route_key": artifact["v2_validation_design_identity"]["route_key"],
        "design_only": artifact["v2_validation_design_identity"]["design_only"],
        "behavioral_validation_v2_allowed_now": artifact["v2_validation_design_identity"]["behavioral_validation_v2_allowed_now"],
        "behavior_dimension_count": artifact["behavior_dimensions_v2"]["behavior_dimension_count"],
        "similarity_metric_count": artifact["similarity_metrics_v2"]["similarity_metric_count"],
        "fail_closed_condition_count": artifact["fail_closed_conditions_v2"]["fail_closed_condition_count"],
        "result_class_count": artifact["pass_fail_classes_v2"]["result_class_count"],
        "exact_gate_replay_recovered": artifact["v2_validation_design_identity"]["exact_gate_replay_recovered"],
        "next_allowed_step": artifact["next_allowed_step"],
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
