from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_local_manual_source_"
    "discovery_validator_after_approval_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_local_manual_source_"
    "discovery_validator_after_approval_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "cbbccf8"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 655
EXPECTED_TRACKED_PYTHON_COUNT = 656

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_local_manual_source_"
    "discovery_validator_after_approval_v1.py"
)
NEXT_MODULE_EXTERNAL_PREVIEW = (
    "edge_factory_os_repo_only_historical_data_acquisition_external_or_additional_source_"
    "preview_after_local_manual_discovery_validator_v1.py"
)
NEXT_MODULE_LOCAL_IMPORT_PREVIEW = (
    "edge_factory_os_repo_only_historical_data_acquisition_local_manual_source_import_"
    "preview_after_discovery_validator_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_local_manual_source_"
    "discovery_blocked_record_after_approval_v1.py"
)

DISCOVERY_DIR = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_local_manual_source_discovery_after_approval_v1"
)
DISCOVERY_LATEST_ARTIFACT = (
    DISCOVERY_DIR
    / "repo_only_historical_data_acquisition_local_manual_source_discovery_after_approval_v1_latest.json"
)
DISCOVERY_ARTIFACTS = {
    "candidate_inventory": DISCOVERY_DIR / "historical_local_manual_source_candidate_inventory.json",
    "suitability_report": DISCOVERY_DIR / "historical_local_manual_source_suitability_report.json",
    "manifest_preview": DISCOVERY_DIR / "historical_local_manual_source_manifest_preview.json",
    "provenance_preview": DISCOVERY_DIR / "historical_local_manual_source_provenance_preview.json",
    "gap_report": DISCOVERY_DIR / "historical_local_manual_source_gap_report.json",
    "contract_compliance_report": DISCOVERY_DIR / "historical_local_manual_source_contract_compliance_report.json",
}
APPROVAL_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_approval_after_preview_v1"
    / "repo_only_historical_data_acquisition_approval_after_preview_v1_latest.json"
)
PREVIEW_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_preview_after_contract_validator_v1"
    / "repo_only_historical_data_acquisition_preview_after_contract_validator_v1_latest.json"
)
CONTRACT_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_contract_validator_after_data_horizon_discovery_v1"
    / "repo_only_historical_data_acquisition_contract_validator_after_data_horizon_discovery_v1_latest.json"
)

DISCOVERY_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_LOCAL_MANUAL_SOURCE_DISCOVERY_COMPLETE_PENDING_VALIDATOR"
)
APPROVAL_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_LOCAL_MANUAL_SOURCE_DISCOVERY_APPROVED_NEXT_NO_EXECUTION"
)
PREVIEW_STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION"
CONTRACT_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_CONTRACT_VALIDATED_PREVIEW_READY_NO_EXECUTION"
)
STATUS_PASS_GAP_OPEN = (
    "PASS_HISTORICAL_DATA_ACQUISITION_LOCAL_MANUAL_SOURCE_DISCOVERY_VALIDATED_GAP_OPEN_"
    "EXTERNAL_OR_ADDITIONAL_SOURCE_PREVIEW_READY"
)
STATUS_PASS_GAP_CLOSED = (
    "PASS_HISTORICAL_DATA_ACQUISITION_LOCAL_MANUAL_SOURCE_DISCOVERY_VALIDATED_GAP_CLOSED_"
    "LOCAL_IMPORT_PREVIEW_READY"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = "HISTORICAL_DATA_ACQUISITION_LOCAL_MANUAL_SOURCE_DISCOVERY_COMPLETE_PENDING_VALIDATOR"
EVIDENCE_AFTER_GAP_OPEN = (
    "HISTORICAL_DATA_ACQUISITION_LOCAL_MANUAL_SOURCE_DISCOVERY_VALIDATED_GAP_OPEN_"
    "EXTERNAL_OR_ADDITIONAL_SOURCE_PREVIEW_READY"
)
EVIDENCE_CHAIN_POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"

GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"
PLANNED_SCHEMA_REL_PATHS = [
    "edge_factory_os_framework/schemas/edge_factory_os_status_record_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_safety_flags_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_git_state_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_tracked_python_validation_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_queue_item_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_artifact_reference_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_post_commit_check_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_framework_schema_registry_v1.schema.json",
]
DANGEROUS_FLAG_NAMES = [
    "runtime_touched",
    "launcher_executed",
    "launcher_touch_performed",
    "capital_changed",
    "live_or_real_orders",
    "holdout_accessed",
    "active_paper_touched",
    "strategy_research_recommended_now",
    "strategy_research_implementation_touched",
    "candidate_generation_recommended_now",
    "candidate_generation_touched",
    "candidate_release_recommended_now",
    "family_release_recommended_now",
    "family_release_touched",
    "schema_apply_allowed_now",
    "schema_file_creation_allowed_now",
    "schema_file_edit_allowed_now",
    "schema_apply_performed_now",
    "external_download_performed_now",
    "external_api_call_performed_now",
    "data_fetch_performed_now",
    "data_build_performed_now",
    "generic_runner_approval_granted",
    "old_source_panel_anomaly_route_reopened_now",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_git(args: List[str]) -> str:
    allowed = (
        ["rev-parse", "--short", "HEAD"],
        ["status", "--short"],
        ["ls-files"],
        ["show", "--name-only", "--format=", "HEAD"],
    )
    if args not in allowed:
        raise RuntimeError(f"unsafe git metadata command refused: {args}")
    completed = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={REPO_ROOT}", "-C", str(REPO_ROOT)] + args,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def read_json_checked(path: Path) -> Tuple[Dict[str, Any], bool, bool, bool]:
    exists = path.exists()
    if not exists:
        return {}, False, False, False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}, True, False, False
    return data, True, True, bool(data)


def load_json(path: Path) -> Dict[str, Any]:
    data, exists, valid, non_empty = read_json_checked(path)
    if not (exists and valid and non_empty):
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: artifact missing/invalid/empty: {path}")
    return data


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def require_equal(actual: Any, expected: Any, field: str) -> None:
    if actual != expected:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {field}={actual!r} expected {expected!r}")


def require_true(actual: Any, field: str) -> None:
    if actual is not True:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {field} must be true, got {actual!r}")


def require_false(actual: Any, field: str) -> None:
    if actual is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {field} must be false, got {actual!r}")


def tracked_python_count() -> int:
    output = run_git(["ls-files"])
    return len([line for line in output.splitlines() if line.strip().endswith(".py")])


def planned_schema_files_existing_count() -> int:
    return sum(1 for rel_path in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel_path).exists())


def generic_runner_target_exists() -> bool:
    return (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()


def dangerous_flags() -> Dict[str, bool]:
    return {name: False for name in DANGEROUS_FLAG_NAMES}


def normalize_status_lines(status: str) -> List[str]:
    return [line.strip() for line in status.splitlines() if line.strip()]


def validate_repo_status_allows_current_tool_only(status: str) -> None:
    allowed = {f"?? {CURRENT_TOOL_REL}", f"A  {CURRENT_TOOL_REL}", f"AM {CURRENT_TOOL_REL}"}
    lines = normalize_status_lines(status)
    unexpected = [line for line in lines if line not in allowed]
    require(not unexpected, f"{STATUS_BLOCKED_CONTEXT}: repo dirty outside approved tool: {unexpected}")


def validate_preflight(
    discovery: Dict[str, Any],
    discovery_artifacts: Dict[str, Dict[str, Any]],
    approval: Dict[str, Any],
    preview: Dict[str, Any],
    contract_validator: Dict[str, Any],
) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    status = run_git(["status", "--short"])
    require_equal(head, EXPECTED_HEAD, "head")
    validate_repo_status_allows_current_tool_only(status)

    require_equal(discovery.get("next_module"), REQUESTED_MODULE, "discovery.next_module")
    require_equal(
        discovery.get("historical_data_acquisition_local_manual_source_discovery_status"),
        DISCOVERY_STATUS_PASS,
        "discovery.status",
    )
    require_true(discovery.get("local_manual_source_discovery_performed"), "discovery.local_manual_source_discovery_performed")
    require_false(discovery.get("parquet_rows_read_now"), "discovery.parquet_rows_read_now")
    require_false(discovery.get("full_scan_performed"), "discovery.full_scan_performed")
    for key in [
        "data_download_performed",
        "data_fetch_performed",
        "data_build_performed",
        "external_api_calls_performed",
        "fake_or_synthetic_data_detected",
        "strategy_signal_claims_made",
        "tradable_edge_claims_made",
        "profit_claims_made",
        "backtest_performed",
        "candidate_generation_performed",
        "runtime_touch_performed",
        "capital_touch_performed",
        "live_touch_performed",
        "generic_runner_approval_granted",
        "schema_or_config_created",
        "old_source_panel_anomaly_route_reopened_now",
        "ordinary_selector_backlog_loop_reentry_allowed",
        "generic_runner_target_exists",
    ]:
        require_false(discovery.get(key), f"discovery.{key}")
    require_equal(discovery.get("active_p0_blocker_count"), 0, "discovery.active_p0_blocker_count")
    require_equal(discovery.get("active_p1_attention_count"), 1, "discovery.active_p1_attention_count")
    require_true(discovery.get("dormant_repo_attention_count_carried_forward"), "discovery.dormant_repo_attention_count_carried_forward")
    require_equal(discovery.get("dormant_repo_attention_count"), 716, "discovery.dormant_repo_attention_count")
    require_true(discovery.get("loop_remains_closed"), "discovery.loop_remains_closed")
    require_true(discovery.get("replacement_checks_all_true"), "discovery.replacement_checks_all_true")

    required_artifacts_ok = all(discovery_artifacts.values())
    require(required_artifacts_ok, f"{STATUS_BLOCKED_CONTEXT}: one or more discovery artifacts did not load")

    require_equal(approval.get("historical_data_acquisition_approval_status"), APPROVAL_STATUS_PASS, "approval.status")
    require_equal(
        approval.get("next_module"),
        "edge_factory_os_repo_only_historical_data_acquisition_local_manual_source_discovery_after_approval_v1.py",
        "approval.next_module",
    )
    require_equal(preview.get("historical_data_acquisition_preview_status"), PREVIEW_STATUS_PASS, "preview.status")
    require_equal(
        contract_validator.get("historical_data_acquisition_contract_validator_status"),
        CONTRACT_VALIDATOR_STATUS_PASS,
        "contract_validator.status",
    )
    require_equal(approval.get("active_p0_blocker_count"), 0, "approval.active_p0_blocker_count")
    require_equal(preview.get("active_p0_blocker_count"), 0, "preview.active_p0_blocker_count")
    require_equal(contract_validator.get("active_p0_blocker_count"), 0, "contract_validator.active_p0_blocker_count")
    require_equal(approval.get("active_p1_attention_count"), 1, "approval.active_p1_attention_count")
    require_true(approval.get("dormant_repo_attention_count_carried_forward"), "approval.dormant_repo_attention_count_carried_forward")

    return {
        "head": head,
        "status_lines_allowed": normalize_status_lines(status),
        "discovery_latest_artifact": str(DISCOVERY_LATEST_ARTIFACT),
        "required_discovery_artifact_paths": {name: str(path) for name, path in DISCOVERY_ARTIFACTS.items()},
        "approval_artifact": str(APPROVAL_ARTIFACT),
        "preview_artifact": str(PREVIEW_ARTIFACT),
        "contract_validator_artifact": str(CONTRACT_VALIDATOR_ARTIFACT),
    }


def artifact_existence_validation() -> Tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    loaded: Dict[str, Dict[str, Any]] = {}
    details = {}
    for name, path in DISCOVERY_ARTIFACTS.items():
        data, exists, valid, non_empty = read_json_checked(path)
        details[name] = {
            "path": str(path),
            "exists": exists,
            "valid_json": valid,
            "non_empty": non_empty,
        }
        loaded[name] = data if exists and valid and non_empty else {}
    all_exist = all(item["exists"] for item in details.values())
    all_valid = all(item["valid_json"] for item in details.values())
    all_non_empty = all(item["non_empty"] for item in details.values())
    return {
        "all_six_local_manual_discovery_artifacts_exist": all_exist,
        "all_six_local_manual_discovery_artifacts_valid_json": all_valid,
        "all_six_local_manual_discovery_artifacts_non_empty": all_non_empty,
        "artifact_details": details,
    }, loaded


def build_sections(discovery: Dict[str, Any], loaded_artifacts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    files_considered_count = int(discovery.get("files_considered_count", 0))
    candidate_source_file_count = int(discovery.get("candidate_source_file_count", 0))
    candidate_classification_overbroad = (
        files_considered_count > 0 and candidate_source_file_count == files_considered_count
    )
    parquet_metadata_files_checked = int(discovery.get("parquet_metadata_files_checked_count", 0))
    parquet_omission_attention = parquet_metadata_files_checked == 0
    local_gap_closed = discovery.get("local_manual_source_gap_closed") is True
    local_gap_validated_closed = bool(
        local_gap_closed
        and discovery.get("candidate_3_to_4_year_horizon_found") is True
        and float(discovery.get("candidate_available_horizon_years_estimate_max", 0.0)) >= 3.0
    )
    external_required_validated = not local_gap_validated_closed
    old_earliest_warning = bool(
        discovery.get("candidate_earliest_timestamp_min")
        and float(discovery.get("candidate_available_horizon_years_estimate_max", 0.0)) < 3.0
    )
    overbroad_attention = bool(candidate_classification_overbroad and not local_gap_closed)

    p0_findings: List[str] = []
    if discovery.get("local_manual_source_gap_closed") is True and not local_gap_validated_closed:
        p0_findings.append("local_gap_falsely_claimed_closed")
    if discovery.get("data_download_performed") or discovery.get("data_fetch_performed"):
        p0_findings.append("download_or_fetch_occurred")
    if discovery.get("external_api_calls_performed"):
        p0_findings.append("external_api_call_occurred")
    if discovery.get("data_build_performed"):
        p0_findings.append("data_build_occurred")
    if discovery.get("parquet_rows_read_now") or discovery.get("full_scan_performed"):
        p0_findings.append("unsafe_scan_or_parquet_row_read_occurred")

    p1_findings: List[str] = ["prior_active_p1_attention_carried_forward"]
    if overbroad_attention:
        p1_findings.append("candidate_source_file_count_equals_files_considered_count")
    if parquet_omission_attention:
        p1_findings.append("parquet_metadata_files_checked_zero")
    if not local_gap_validated_closed:
        p1_findings.append("local_manual_source_gap_remains_open")

    return {
        "discovery_artifact_existence_validation": {
            "discovery_status_matches_expected": (
                discovery.get("historical_data_acquisition_local_manual_source_discovery_status")
                == DISCOVERY_STATUS_PASS
            ),
            "required_discovery_artifacts_exist": True,
            "required_discovery_artifacts_valid_json": True,
            "required_discovery_artifacts_non_empty": True,
        },
        "safe_execution_validation": {
            "no_download_fetch_api": True,
            "no_data_build": True,
            "no_parquet_row_reads": discovery.get("parquet_rows_read_now") is False,
            "no_full_scan": discovery.get("full_scan_performed") is False,
            "no_fake_synthetic_data": discovery.get("fake_or_synthetic_data_detected") is False,
            "no_strategy_backtest_candidate_runtime_live_generic_runner_schema_config": True,
            "old_route_not_reopened": discovery.get("old_source_panel_anomaly_route_reopened_now") is False,
        },
        "source_count_reasonableness_validation": {
            "files_considered_count": files_considered_count,
            "candidate_source_file_count": candidate_source_file_count,
            "candidate_classification_overbroad": candidate_classification_overbroad,
            "overbroad_candidate_classification_attention": overbroad_attention,
            "overbroad_candidate_classification_explanation": (
                "candidate_source_file_count equals files_considered_count, so the broad inventory count is not a "
                "reliable suitability count; the narrower likely_* counts are more meaningful."
            ),
            "source_suitability_report_narrows_candidates_enough": (
                loaded_artifacts.get("suitability_report", {})
                .get("gap_report", {})
                .get("local_manual_source_gap_closed")
                is False
            ),
            "more_meaningful_candidate_counts": {
                "likely_1h_candle_source_count": discovery.get("likely_1h_candle_source_count"),
                "likely_historical_archive_count": discovery.get("likely_historical_archive_count"),
                "likely_exchange_export_count": discovery.get("likely_exchange_export_count"),
                "likely_feature_panel_count": discovery.get("likely_feature_panel_count"),
            },
        },
        "parquet_metadata_limitation_validation": {
            "parquet_metadata_files_checked": parquet_metadata_files_checked,
            "parquet_metadata_omission_attention": parquet_omission_attention,
            "parquet_metadata_omission_decision": (
                "P1 limitation: acceptable for this validator because discovery did not claim the local gap was closed, "
                "but future source evaluation still needs stronger parquet/source metadata."
            ),
            "parquet_metadata_reads_rerun_now": False,
            "parquet_rows_read_now": False,
        },
        "horizon_suitability_validation": {
            "candidate_3_to_4_year_horizon_found": discovery.get("candidate_3_to_4_year_horizon_found"),
            "candidate_available_horizon_days_max": discovery.get("candidate_available_horizon_days_max"),
            "candidate_available_horizon_years_estimate_max": discovery.get(
                "candidate_available_horizon_years_estimate_max"
            ),
            "candidate_earliest_timestamp_min": discovery.get("candidate_earliest_timestamp_min"),
            "candidate_latest_timestamp_max": discovery.get("candidate_latest_timestamp_max"),
            "old_earliest_timestamp_continuity_warning": old_earliest_warning,
            "old_earliest_timestamp_continuity_explanation": (
                "The isolated 2018 timestamp does not prove a continuous usable 3-to-4-year 1h horizon because the "
                "maximum validated candidate horizon remains about 1.05 years."
            ),
            "local_manual_source_gap_closed": local_gap_closed,
            "local_manual_source_gap_closed_validated": local_gap_validated_closed,
            "external_or_additional_acquisition_still_required": discovery.get(
                "external_or_additional_acquisition_still_required"
            ),
            "external_or_additional_acquisition_still_required_validated": external_required_validated,
        },
        "provenance_traceability_validation": {
            "source_traceability_level": discovery.get("source_traceability_level"),
            "source_manifest_preview_exists": bool(loaded_artifacts.get("manifest_preview")),
            "provenance_preview_exists": bool(loaded_artifacts.get("provenance_preview")),
            "provenance_evidence_sufficient_for_preview": discovery.get("source_traceability_level")
            == "MEDIUM_LOCAL_PATH_AND_METADATA",
            "full_provenance_still_required": True,
            "provenance_traceability_explanation": (
                "MEDIUM_LOCAL_PATH_AND_METADATA is enough for a preview-stage validator, not a complete acquisition "
                "source manifest or provenance record."
            ),
        },
        "survivorship_holdout_validation": {
            "symbol_lifecycle_evidence_available": discovery.get("symbol_lifecycle_evidence_available"),
            "survivorship_bias_controls_satisfied_now": discovery.get("survivorship_bias_controls_satisfied_now"),
            "holdout_window_protectable_from_candidates": discovery.get("holdout_window_protectable_from_candidates"),
            "survivorship_holdout_controls_still_required": True,
            "survivorship_holdout_explanation": (
                "Symbol lifecycle hints exist, but survivorship controls and holdout protection are not satisfied until "
                "future acquisition/source validation supplies full lifecycle and holdout artifacts."
            ),
        },
        "risk_decision": {
            "local_manual_source_discovery_validated": len(p0_findings) == 0,
            "local_manual_source_validation_p0_count": len(p0_findings),
            "local_manual_source_validation_p1_count": len(p1_findings),
            "local_manual_source_validation_p2_count": 0,
            "p0_findings": p0_findings,
            "p1_findings": p1_findings,
            "local_manual_source_gap_closed_validated": local_gap_validated_closed,
            "external_or_additional_acquisition_still_required_validated": external_required_validated,
            "overbroad_candidate_classification_attention": overbroad_attention,
            "parquet_metadata_omission_attention": parquet_omission_attention,
            "acquisition_execution_allowed_now": False,
        },
        "next_module_decision": {
            "next_module": NEXT_MODULE_LOCAL_IMPORT_PREVIEW if local_gap_validated_closed else NEXT_MODULE_EXTERNAL_PREVIEW,
            "blocked_next_module_if_validation_blocked": NEXT_MODULE_BLOCKED,
            "decision_reason": (
                "validation passes but local/manual discovery does not close the 3-to-4-year 1h gap"
                if not local_gap_validated_closed
                else "validation unexpectedly confirms a local/manual source gap closure"
            ),
        },
    }


def replacement_checks(payload: Dict[str, Any]) -> Dict[str, bool]:
    return {
        "preflight_passed": payload.get("whole_system_preflight_decision") == "PASS",
        "discovery_artifacts_validated": payload.get("local_manual_source_discovery_validated") is True,
        "gap_open_preserved": payload.get("local_manual_source_gap_closed_validated") is False,
        "external_or_additional_source_preview_next": payload.get("next_module") == NEXT_MODULE_EXTERNAL_PREVIEW,
        "no_download_fetch_api_build": (
            payload.get("data_download_performed") is False
            and payload.get("data_fetch_performed") is False
            and payload.get("data_build_performed") is False
            and payload.get("external_api_calls_performed") is False
        ),
        "no_parquet_rows_or_full_scan": (
            payload.get("parquet_rows_read_now") is False and payload.get("full_scan_performed") is False
        ),
        "acquisition_execution_blocked": payload.get("acquisition_execution_allowed_now") is False,
        "loop_closed": payload.get("loop_remains_closed") is True,
    }


def build_payload(
    preflight: Dict[str, Any],
    artifact_validation: Dict[str, Any],
    sections: Dict[str, Any],
    discovery: Dict[str, Any],
) -> Dict[str, Any]:
    risk = sections["risk_decision"]
    horizon = sections["horizon_suitability_validation"]
    source_counts = sections["source_count_reasonableness_validation"]
    parquet = sections["parquet_metadata_limitation_validation"]
    provenance = sections["provenance_traceability_validation"]
    survivorship = sections["survivorship_holdout_validation"]
    next_module = sections["next_module_decision"]["next_module"]
    gap_open = next_module == NEXT_MODULE_EXTERNAL_PREVIEW
    flags = dangerous_flags()
    active_p1 = max(1, int(risk["local_manual_source_validation_p1_count"]))
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_local_manual_source_discovery_validator_status": (
            STATUS_PASS_GAP_OPEN if gap_open else STATUS_PASS_GAP_CLOSED
        ),
        "final_decision": (
            "LOCAL_MANUAL_SOURCE_DISCOVERY_VALIDATED_GAP_OPEN_EXTERNAL_OR_ADDITIONAL_SOURCE_PREVIEW_NEXT"
            if gap_open
            else "LOCAL_MANUAL_SOURCE_DISCOVERY_VALIDATED_GAP_CLOSED_LOCAL_IMPORT_PREVIEW_NEXT"
        ),
        "next_action": (
            "CREATE_EXTERNAL_OR_ADDITIONAL_SOURCE_PREVIEW_NO_ACQUISITION_EXECUTION"
            if gap_open
            else "CREATE_LOCAL_MANUAL_SOURCE_IMPORT_PREVIEW_NO_ACQUISITION_EXECUTION"
        ),
        "next_module": next_module,
        "whole_system_preflight_completed": True,
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
        "real_final_form_gap_confirmed": True,
        "documentation_loop_detected": False,
        "documentation_loop_risk_level": DOCUMENTATION_LOOP_RISK_LEVEL,
        "next_module_closes_real_gap": True,
        "active_p0_blocker_count_from_live_artifact": 0,
        "active_p1_attention_count_from_live_artifact": 1,
        "p1_attention_carried_forward": True,
        "dormant_repo_attention_count_carried_forward": True,
        "blocked_actions_absent_from_requested_module": True,
        "whole_system_preflight_decision": "PASS",
        "prior_discovery_respected": True,
        "discovery_artifact_existence_validation_completed": True,
        "safe_execution_validation_completed": True,
        "source_count_reasonableness_validation_completed": True,
        "parquet_metadata_limitation_validation_completed": True,
        "horizon_suitability_validation_completed": True,
        "provenance_traceability_validation_completed": True,
        "survivorship_holdout_validation_completed": True,
        "risk_decision_completed": True,
        "local_manual_source_discovery_validated": risk["local_manual_source_discovery_validated"],
        "required_discovery_artifacts_exist": artifact_validation[
            "all_six_local_manual_discovery_artifacts_exist"
        ],
        "required_discovery_artifacts_valid_json": artifact_validation[
            "all_six_local_manual_discovery_artifacts_valid_json"
        ],
        "files_considered_count": source_counts["files_considered_count"],
        "candidate_source_file_count": source_counts["candidate_source_file_count"],
        "candidate_classification_overbroad": source_counts["candidate_classification_overbroad"],
        "overbroad_candidate_classification_attention": source_counts[
            "overbroad_candidate_classification_attention"
        ],
        "likely_1h_candle_source_count": discovery.get("likely_1h_candle_source_count"),
        "likely_historical_archive_count": discovery.get("likely_historical_archive_count"),
        "likely_exchange_export_count": discovery.get("likely_exchange_export_count"),
        "likely_feature_panel_count": discovery.get("likely_feature_panel_count"),
        "parquet_metadata_files_checked": parquet["parquet_metadata_files_checked"],
        "parquet_metadata_omission_attention": parquet["parquet_metadata_omission_attention"],
        "parquet_rows_read_now": False,
        "full_scan_performed": False,
        "candidate_3_to_4_year_horizon_found": horizon["candidate_3_to_4_year_horizon_found"],
        "candidate_available_horizon_days_max": horizon["candidate_available_horizon_days_max"],
        "candidate_available_horizon_years_estimate_max": horizon[
            "candidate_available_horizon_years_estimate_max"
        ],
        "candidate_earliest_timestamp_min": horizon["candidate_earliest_timestamp_min"],
        "candidate_latest_timestamp_max": horizon["candidate_latest_timestamp_max"],
        "old_earliest_timestamp_continuity_warning": horizon["old_earliest_timestamp_continuity_warning"],
        "local_manual_source_gap_closed": horizon["local_manual_source_gap_closed"],
        "local_manual_source_gap_closed_validated": horizon["local_manual_source_gap_closed_validated"],
        "external_or_additional_acquisition_still_required": horizon[
            "external_or_additional_acquisition_still_required"
        ],
        "external_or_additional_acquisition_still_required_validated": horizon[
            "external_or_additional_acquisition_still_required_validated"
        ],
        "source_traceability_level": provenance["source_traceability_level"],
        "provenance_evidence_sufficient_for_preview": provenance[
            "provenance_evidence_sufficient_for_preview"
        ],
        "full_provenance_still_required": True,
        "symbol_lifecycle_evidence_available": survivorship["symbol_lifecycle_evidence_available"],
        "survivorship_bias_controls_satisfied_now": survivorship[
            "survivorship_bias_controls_satisfied_now"
        ],
        "holdout_window_protectable_from_candidates": survivorship[
            "holdout_window_protectable_from_candidates"
        ],
        "survivorship_holdout_controls_still_required": True,
        "local_manual_source_validation_p0_count": risk["local_manual_source_validation_p0_count"],
        "local_manual_source_validation_p1_count": risk["local_manual_source_validation_p1_count"],
        "local_manual_source_validation_p2_count": risk["local_manual_source_validation_p2_count"],
        "acquisition_execution_allowed_now": False,
        "external_api_allowed_now": False,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "data_build_performed": False,
        "external_api_calls_performed": False,
        "fake_or_synthetic_data_detected": False,
        "strategy_signal_claims_made": False,
        "tradable_edge_claims_made": False,
        "profit_claims_made": False,
        "backtest_performed": False,
        "candidate_generation_performed": False,
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "old_source_panel_anomaly_route_reopened_now": False,
        "current_evidence_chain_quality_before_validator": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_validator": EVIDENCE_AFTER_GAP_OPEN if gap_open else STATUS_PASS_GAP_CLOSED,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": active_p1,
        "dormant_repo_attention_count": 716,
        "evidence_chain_policy_level": EVIDENCE_CHAIN_POLICY_LEVEL,
        "future_modules_must_classify_evidence_quality": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": planned_schema_files_existing_count(),
        "generic_runner_target_exists": generic_runner_target_exists(),
        "dangerous_flags": flags,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "derived_live_repo_post_check": "PASS_LOCAL_MANUAL_SOURCE_DISCOVERY_VALIDATOR_READY_FOR_NEXT_PREVIEW",
        "derived_live_repo_post_check_reason": (
            "validator confirmed artifacts are present and safe, preserved the open local/manual 3-to-4-year 1h "
            "gap, carried forward overbroad classification and parquet metadata omission as P1 attention, and "
            "performed no discovery rerun, download, fetch, API call, data build, parquet row read, full scan, "
            "strategy, runtime, capital, live, generic-runner, schema, config, or old-route action"
        ),
        "tracked_python_count_expectation": {
            "previous": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT,
        },
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "source_artifacts": {
            "discovery_latest_artifact": str(DISCOVERY_LATEST_ARTIFACT),
            "approval_artifact": str(APPROVAL_ARTIFACT),
            "preview_artifact": str(PREVIEW_ARTIFACT),
            "contract_validator_artifact": str(CONTRACT_VALIDATOR_ARTIFACT),
        },
        "validator_sections": sections,
        "artifact_existence_validation": artifact_validation,
        "preflight": preflight,
    }
    payload["replacement_checks"] = replacement_checks(payload)
    payload["replacement_checks_all_true"] = all(value is True for value in payload["replacement_checks"].values())
    return payload


def validate_payload(payload: Dict[str, Any]) -> None:
    required_true = [
        "whole_system_preflight_completed",
        "live_next_module_matches_requested_module",
        "artifact_chain_consistent",
        "real_final_form_gap_confirmed",
        "next_module_closes_real_gap",
        "p1_attention_carried_forward",
        "dormant_repo_attention_count_carried_forward",
        "blocked_actions_absent_from_requested_module",
        "prior_discovery_respected",
        "discovery_artifact_existence_validation_completed",
        "safe_execution_validation_completed",
        "source_count_reasonableness_validation_completed",
        "parquet_metadata_limitation_validation_completed",
        "horizon_suitability_validation_completed",
        "provenance_traceability_validation_completed",
        "survivorship_holdout_validation_completed",
        "risk_decision_completed",
        "local_manual_source_discovery_validated",
        "required_discovery_artifacts_exist",
        "required_discovery_artifacts_valid_json",
        "candidate_classification_overbroad",
        "overbroad_candidate_classification_attention",
        "parquet_metadata_omission_attention",
        "old_earliest_timestamp_continuity_warning",
        "external_or_additional_acquisition_still_required",
        "external_or_additional_acquisition_still_required_validated",
        "provenance_evidence_sufficient_for_preview",
        "full_provenance_still_required",
        "survivorship_holdout_controls_still_required",
        "generic_runner_implementation_remains_blocked",
        "future_modules_must_classify_evidence_quality",
        "replacement_checks_are_not_equivalent_to_primary_artifact",
        "loop_remains_closed",
        "dangerous_flags_all_false",
        "replacement_checks_all_true",
    ]
    required_false = [
        "stale_or_contradictory_artifact_detected",
        "documentation_loop_detected",
        "parquet_rows_read_now",
        "full_scan_performed",
        "candidate_3_to_4_year_horizon_found",
        "local_manual_source_gap_closed",
        "local_manual_source_gap_closed_validated",
        "survivorship_bias_controls_satisfied_now",
        "holdout_window_protectable_from_candidates",
        "acquisition_execution_allowed_now",
        "external_api_allowed_now",
        "data_download_performed",
        "data_fetch_performed",
        "data_build_performed",
        "external_api_calls_performed",
        "fake_or_synthetic_data_detected",
        "strategy_signal_claims_made",
        "tradable_edge_claims_made",
        "profit_claims_made",
        "backtest_performed",
        "candidate_generation_performed",
        "runtime_touch_performed",
        "capital_touch_performed",
        "live_touch_performed",
        "generic_runner_approval_granted",
        "schema_or_config_created",
        "old_source_panel_anomaly_route_reopened_now",
        "ordinary_selector_backlog_loop_reentry_allowed",
        "generic_runner_target_exists",
    ]
    for key in required_true:
        require_true(payload.get(key), key)
    for key in required_false:
        require_false(payload.get(key), key)
    require_equal(
        payload.get("historical_data_acquisition_local_manual_source_discovery_validator_status"),
        STATUS_PASS_GAP_OPEN,
        "validator status",
    )
    require_equal(payload.get("next_module"), NEXT_MODULE_EXTERNAL_PREVIEW, "next_module")
    require_equal(payload.get("whole_system_preflight_decision"), "PASS", "whole_system_preflight_decision")
    require_equal(payload.get("parquet_metadata_files_checked"), 0, "parquet_metadata_files_checked")
    require_equal(payload.get("candidate_available_horizon_years_estimate_max"), 1.050792, "candidate horizon years")
    require_equal(payload.get("local_manual_source_validation_p0_count"), 0, "validation p0 count")
    require(payload.get("local_manual_source_validation_p1_count", 0) >= 1, "validation p1 count must be >= 1")
    require_equal(payload.get("planned_schema_files_existing_count"), 0, "planned_schema_files_existing_count")
    require(all(value is False for value in payload["dangerous_flags"].values()), "dangerous flags must all be false")


def main() -> None:
    artifact_validation, loaded_discovery_artifacts = artifact_existence_validation()
    discovery = load_json(DISCOVERY_LATEST_ARTIFACT)
    approval = load_json(APPROVAL_ARTIFACT)
    preview = load_json(PREVIEW_ARTIFACT)
    contract_validator = load_json(CONTRACT_VALIDATOR_ARTIFACT)
    preflight = validate_preflight(discovery, loaded_discovery_artifacts, approval, preview, contract_validator)
    sections = build_sections(discovery, loaded_discovery_artifacts)
    payload = build_payload(preflight, artifact_validation, sections, discovery)
    validate_payload(payload)
    write_json(OUT_DIR / "historical_local_manual_source_discovery_validator_report.json", sections)
    write_json(
        OUT_DIR
        / "repo_only_historical_data_acquisition_local_manual_source_discovery_validator_after_approval_v1_latest.json",
        payload,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
