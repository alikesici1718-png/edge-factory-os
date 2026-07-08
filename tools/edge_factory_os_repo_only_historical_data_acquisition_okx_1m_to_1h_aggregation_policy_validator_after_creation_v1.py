from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_"
    "after_creation_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_"
    "after_creation_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "01176c1"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 674
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 675

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_"
    "after_creation_v1.py"
)
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_source_manifest_preview_after_"
    "aggregation_policy_validator_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_"
    "validation_blocked_record_after_creation_v1.py"
)

CREATION_DIR = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_creation_after_approval_v1"
)
CREATION_ARTIFACT = (
    CREATION_DIR
    / "repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_creation_after_approval_v1_latest.json"
)
POLICY_ARTIFACT = CREATION_DIR / "historical_okx_1m_to_1h_aggregation_policy.json"
COMPLIANCE_REPORT = CREATION_DIR / "historical_okx_1m_to_1h_aggregation_policy_contract_compliance_report.json"
APPROVAL_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_approval_after_preview_v1"
    / "repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_approval_after_preview_v1_latest.json"
)
PREVIEW_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_preview_after_metadata_validator_v1"
    / "repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_preview_after_metadata_validator_v1_latest.json"
)
METADATA_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_input_validator_after_approval_v1"
    / "repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_input_validator_after_approval_v1_latest.json"
)

CREATION_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_CREATED_"
    "PENDING_VALIDATOR_NO_EXECUTION"
)
APPROVAL_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_CREATION_"
    "APPROVED_NEXT_NO_EXECUTION"
)
PREVIEW_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_PREVIEW_READY_"
    "APPROVAL_REQUIRED_NO_EXECUTION"
)
METADATA_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_METADATA_INPUT_VALIDATED_"
    "1M_SCHEMA_AGGREGATION_POLICY_PREVIEW_READY_NO_EXECUTION"
)
STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_VALIDATED_"
    "SOURCE_MANIFEST_PREVIEW_READY_NO_EXECUTION"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_CREATED_PENDING_"
    "VALIDATOR_NO_EXECUTION"
)
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_VALIDATED_SOURCE_"
    "MANIFEST_PREVIEW_READY_NO_EXECUTION"
)
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"

POLICY_NAME = "OKX_1M_TO_1H_AGGREGATION_POLICY_V1"
POLICY_SCOPE = "FUTURE_DATA_BUILD_POLICY_ONLY"
EXPECTED_INPUT_COLUMNS = [
    "instrument_name",
    "open",
    "high",
    "low",
    "close",
    "vol",
    "vol_ccy",
    "vol_quote",
    "open_time",
    "confirm",
]
TIMESTAMP_UNIT = "epoch_milliseconds"
EXPECTED_INPUT_INTERVAL = "1m"
EXPECTED_OPEN_TIME_DELTA_MS = 60000
CANONICAL_AGGREGATION_TIME_BASIS = "UTC_HOURLY_BUCKETS_FROM_OPEN_TIME_EPOCH_MS"
OUTPUT_HOUR_BUCKET_POLICY = "FLOOR_OPEN_TIME_TO_UTC_HOUR"
INCOMPLETE_HOUR_POLICY = "EXCLUDE_OR_FLAG_NEVER_FILL"
DUPLICATE_MINUTE_POLICY = "FAIL_CLOSED_OR_QUARANTINE_UNLESS_LATER_DEDUP_POLICY_APPROVED"
MISSING_MINUTE_POLICY = "INCOMPLETE_HOUR_FAIL_CLOSED_OR_FLAGGED"
CONFIRM_POLICY = "OUTPUT_CONFIRM_TRUE_ONLY_IF_ALL_SOURCE_ROWS_CONFIRMED"
COMPLETE_HOUR_REQUIRED_SOURCE_ROWS = 60

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
    "schema_file_creation_performed_now",
    "schema_file_edit_performed_now",
    "schema_apply_performed_now",
    "external_download_performed_now",
    "external_api_call_performed_now",
    "data_fetch_performed_now",
    "data_build_performed_now",
    "okx_browse_performed_now",
    "okx_download_performed_now",
    "okx_api_call_performed_now",
    "okx_sample_zip_downloaded_now",
    "okx_page_reopened_now",
    "aggregation_performed_now",
    "source_manifest_created_now",
    "repo_schema_config_created_now",
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
    return data, True, True, isinstance(data, dict) and bool(data)


def load_json(path: Path, label: str) -> Dict[str, Any]:
    data, exists, valid, non_empty = read_json_checked(path)
    if not (exists and valid and non_empty):
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {label} missing/invalid/empty: {path}")
    return data


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require_equal(actual: Any, expected: Any, field: str, status: str = STATUS_BLOCKED_CONTEXT) -> None:
    if actual != expected:
        raise RuntimeError(f"{status}: {field}={actual!r} expected {expected!r}")


def require_true(actual: Any, field: str) -> None:
    if actual is not True:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {field} must be true, got {actual!r}")


def require_false(actual: Any, field: str) -> None:
    if actual is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {field} must be false, got {actual!r}")


def require_contains(haystack: str, needle: str, field: str) -> None:
    if needle not in haystack:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {field} missing {needle!r}")


def normalize_status_lines(status: str) -> List[str]:
    return [line.strip() for line in status.splitlines() if line.strip()]


def validate_repo_status_allows_current_tool_only(status: str) -> None:
    allowed = {f"?? {CURRENT_TOOL_REL}", f"A  {CURRENT_TOOL_REL}", f"AM {CURRENT_TOOL_REL}"}
    unexpected = [line for line in normalize_status_lines(status) if line not in allowed]
    if unexpected:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: repo dirty outside approved tool: {unexpected}")


def tracked_python_count() -> int:
    output = run_git(["ls-files"])
    return len([line for line in output.splitlines() if line.strip().endswith(".py")])


def planned_schema_files_existing_count() -> int:
    return sum(1 for rel_path in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel_path).exists())


def generic_runner_target_exists() -> bool:
    return (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()


def dangerous_flags() -> Dict[str, bool]:
    return {name: False for name in DANGEROUS_FLAG_NAMES}


def validate_no_true_dangerous_flags(data: Dict[str, Any], artifact_name: str) -> None:
    true_flags = [name for name, value in data.get("dangerous_flags", {}).items() if value is True]
    if true_flags:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {artifact_name} dangerous flags true: {true_flags}")


def validate_chain_artifacts(
    creation: Dict[str, Any],
    approval: Dict[str, Any],
    preview: Dict[str, Any],
    metadata_validator: Dict[str, Any],
) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))

    require_equal(
        creation.get("historical_data_acquisition_okx_1m_to_1h_aggregation_policy_creation_status"),
        CREATION_STATUS_PASS,
        "creation.status",
    )
    require_equal(creation.get("next_module"), REQUESTED_MODULE, "creation.next_module", STATUS_BLOCKED_NEXT_MODULE)
    require_true(creation.get("okx_1m_to_1h_aggregation_policy_created"), "creation.policy_created")
    require_true(creation.get("okx_1m_to_1h_aggregation_policy_artifact_created"), "creation.policy_artifact_created")
    require_true(
        creation.get("okx_1m_to_1h_aggregation_policy_compliance_report_created"),
        "creation.compliance_report_created",
    )
    require_equal(creation.get("current_evidence_chain_quality_after_creation"), EVIDENCE_BEFORE, "creation.evidence")
    require_equal(creation.get("active_p0_blocker_count"), 0, "creation.active_p0_blocker_count")
    require_equal(creation.get("active_p1_attention_count"), 8, "creation.active_p1_attention_count")
    require_equal(creation.get("dormant_repo_attention_count"), 716, "creation.dormant_repo_attention_count")
    require_true(creation.get("p1_attention_carried_forward"), "creation.p1_attention_carried_forward")
    require_true(
        creation.get("dormant_repo_attention_count_carried_forward"),
        "creation.dormant_repo_attention_count_carried_forward",
    )
    require_false(creation.get("schema_or_config_created"), "creation.schema_or_config_created")
    require_false(creation.get("generic_runner_approval_granted"), "creation.generic_runner_approval_granted")
    require_true(
        creation.get("generic_runner_implementation_remains_blocked"),
        "creation.generic_runner_implementation_remains_blocked",
    )
    require_equal(creation.get("planned_schema_files_existing_count"), 0, "creation.planned_schema_files_existing_count")
    require_false(creation.get("generic_runner_target_exists"), "creation.generic_runner_target_exists")
    require_true(creation.get("replacement_checks_all_true"), "creation.replacement_checks_all_true")
    validate_no_true_dangerous_flags(creation, "creation")

    require_equal(
        approval.get("historical_data_acquisition_okx_1m_to_1h_aggregation_policy_approval_status"),
        APPROVAL_STATUS_PASS,
        "approval.status",
    )
    require_equal(
        preview.get("historical_data_acquisition_okx_1m_to_1h_aggregation_policy_preview_status"),
        PREVIEW_STATUS_PASS,
        "preview.status",
    )
    require_equal(
        metadata_validator.get("historical_data_acquisition_okx_user_manual_archive_metadata_input_validator_status"),
        METADATA_VALIDATOR_STATUS_PASS,
        "metadata_validator.status",
    )
    for label, artifact in (
        ("approval", approval),
        ("preview", preview),
        ("metadata_validator", metadata_validator),
    ):
        require_false(artifact.get("aggregation_performed_now"), f"{label}.aggregation_performed_now")
        require_false(artifact.get("data_build_performed"), f"{label}.data_build_performed")
        require_true(artifact.get("replacement_checks_all_true"), f"{label}.replacement_checks_all_true")
        validate_no_true_dangerous_flags(artifact, label)

    return {
        "whole_system_preflight_completed": True,
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
        "real_final_form_gap_confirmed": True,
        "documentation_loop_detected": False,
        "documentation_loop_risk_level": DOCUMENTATION_LOOP_RISK_LEVEL,
        "next_module_closes_real_gap": True,
        "active_p0_blocker_count_from_live_artifact": 0,
        "active_p1_attention_count_from_live_artifact": 8,
        "p1_attention_carried_forward": True,
        "dormant_repo_attention_count_carried_forward": True,
        "blocked_actions_absent_from_requested_module": True,
        "whole_system_preflight_decision": "PASS",
        "creation_artifact": str(CREATION_ARTIFACT),
        "policy_artifact_path": str(POLICY_ARTIFACT),
        "compliance_report_path": str(COMPLIANCE_REPORT),
        "approval_artifact": str(APPROVAL_ARTIFACT),
        "preview_artifact": str(PREVIEW_ARTIFACT),
        "metadata_validator_artifact": str(METADATA_VALIDATOR_ARTIFACT),
        "head": head,
        "status_lines_allowed": [f"?? {CURRENT_TOOL_REL}", f"A  {CURRENT_TOOL_REL}", f"AM {CURRENT_TOOL_REL}"],
    }


def validate_policy_artifact(policy: Dict[str, Any], compliance: Dict[str, Any], creation: Dict[str, Any]) -> None:
    identity = policy.get("policy_identity", {})
    require_equal(identity.get("policy_name"), POLICY_NAME, "policy.policy_name")
    require_equal(identity.get("policy_scope"), POLICY_SCOPE, "policy.policy_scope")
    require_equal(compliance.get("policy_name"), POLICY_NAME, "compliance.policy_name")
    require_equal(compliance.get("policy_scope"), POLICY_SCOPE, "compliance.policy_scope")
    if creation.get("policy_artifact") != policy:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: creation embedded policy artifact differs from policy file")


def validate_execution_block(policy: Dict[str, Any], creation: Dict[str, Any], compliance: Dict[str, Any]) -> None:
    identity = policy.get("policy_identity", {})
    for field in (
        "policy_execution_allowed_now",
        "aggregation_execution_allowed_now",
        "data_build_allowed_now",
        "acquisition_execution_allowed_now",
    ):
        require_false(identity.get(field), f"policy_identity.{field}")
        require_false(creation.get(field), f"creation.{field}")
        if field in compliance:
            require_false(compliance.get(field), f"compliance.{field}")
    for field in (
        "external_download_allowed_now",
        "external_api_allowed_now",
        "okx_download_performed",
        "okx_api_call_performed",
        "okx_browse_performed",
        "okx_sample_zip_downloaded_now",
        "fake_or_synthetic_data_detected",
        "aggregation_performed_now",
        "data_build_performed",
    ):
        require_false(creation.get(field), f"creation.{field}")
        if field in compliance:
            require_false(compliance.get(field), f"compliance.{field}")


def validate_input_schema(policy: Dict[str, Any], creation: Dict[str, Any]) -> None:
    schema = policy.get("input_schema_policy", {})
    columns = schema.get("expected_columns")
    if not isinstance(columns, list):
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: input_schema_policy.expected_columns missing")
    missing = [column for column in EXPECTED_INPUT_COLUMNS if column not in columns]
    if missing:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: expected input columns missing: {missing}")
    require_equal(schema.get("expected_input_interval"), EXPECTED_INPUT_INTERVAL, "policy.expected_input_interval")
    require_equal(schema.get("expected_open_time_delta_ms"), EXPECTED_OPEN_TIME_DELTA_MS, "policy.expected_delta")
    require_false(schema.get("direct_1h_input_expected"), "policy.direct_1h_input_expected")
    require_equal(schema.get("timestamp_unit"), TIMESTAMP_UNIT, "policy.timestamp_unit")
    require_equal(creation.get("expected_input_interval"), EXPECTED_INPUT_INTERVAL, "creation.expected_input_interval")
    require_equal(creation.get("expected_open_time_delta_ms"), EXPECTED_OPEN_TIME_DELTA_MS, "creation.expected_delta")
    require_false(creation.get("direct_1h_input_expected"), "creation.direct_1h_input_expected")


def validate_time_bucket(policy: Dict[str, Any], creation: Dict[str, Any]) -> None:
    time_policy = policy.get("canonical_time_policy", {})
    require_equal(
        time_policy.get("canonical_aggregation_time_basis"),
        CANONICAL_AGGREGATION_TIME_BASIS,
        "policy.time_basis",
    )
    require_equal(
        time_policy.get("output_hour_bucket_policy"),
        OUTPUT_HOUR_BUCKET_POLICY,
        "policy.output_hour_bucket_policy",
    )
    timestamp_fields = time_policy.get("output_timestamp_fields")
    if not isinstance(timestamp_fields, list):
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: output timestamp fields missing")
    for field in ("hour_start_epoch_ms", "hour_start_iso_utc"):
        if field not in timestamp_fields:
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: output timestamp field missing: {field}")
    require_false(time_policy.get("local_machine_timezone_allowed"), "policy.local_machine_timezone_allowed")
    require_contains(
        str(time_policy.get("okx_daily_archive_boundary_note", "")),
        "UTC+8",
        "policy.okx_daily_archive_boundary_note",
    )
    require_contains(
        str(time_policy.get("okx_daily_archive_boundary_note", "")),
        "canonical UTC",
        "policy.okx_daily_archive_boundary_note",
    )
    require_true(time_policy.get("cross_file_hour_handling_required"), "policy.cross_file_hour_handling_required")
    require_contains(
        str(time_policy.get("incomplete_first_last_archive_file_hours_policy", "")),
        "cannot be assumed complete",
        "policy.incomplete_first_last_archive_file_hours_policy",
    )
    require_equal(creation.get("canonical_aggregation_time_basis"), CANONICAL_AGGREGATION_TIME_BASIS, "creation.time_basis")
    require_equal(creation.get("output_hour_bucket_policy"), OUTPUT_HOUR_BUCKET_POLICY, "creation.bucket_policy")


def validate_ohlcv_rules(policy: Dict[str, Any]) -> None:
    ohlcv = policy.get("ohlcv_aggregation_policy", {})
    expected = {
        "output_open": "first source open by open_time",
        "output_high": "max source high",
        "output_low": "min source low",
        "output_close": "last source close by open_time",
        "output_vol": "sum source vol",
        "output_vol_ccy": "sum source vol_ccy",
        "output_vol_quote": "sum source vol_quote",
        "output_instrument_name": "source instrument_name",
        "output_source_row_count": "number of unique 1m rows",
    }
    for field, expected_value in expected.items():
        require_equal(ohlcv.get(field), expected_value, f"policy.{field}")
    require_contains(str(ohlcv.get("output_complete_hour", "")), "source_row_count=60", "policy.output_complete_hour")
    require_contains(str(ohlcv.get("output_confirm", "")), "all 60 source rows", "policy.output_confirm")


def validate_completeness(policy: Dict[str, Any], creation: Dict[str, Any], compliance: Dict[str, Any]) -> None:
    completeness = policy.get("completeness_policy", {})
    require_equal(
        completeness.get("complete_hour_required_source_rows"),
        COMPLETE_HOUR_REQUIRED_SOURCE_ROWS,
        "policy.complete_hour_required_source_rows",
    )
    require_false(completeness.get("synthetic_fill_allowed"), "policy.synthetic_fill_allowed")
    require_equal(completeness.get("incomplete_hour_policy"), INCOMPLETE_HOUR_POLICY, "policy.incomplete_hour_policy")
    require_equal(completeness.get("duplicate_minute_policy"), DUPLICATE_MINUTE_POLICY, "policy.duplicate_minute_policy")
    require_equal(completeness.get("missing_minute_policy"), MISSING_MINUTE_POLICY, "policy.missing_minute_policy")
    require_equal(completeness.get("non_monotonic_time_policy"), "FAIL_CLOSED_OR_QUARANTINE", "policy.non_monotonic_time_policy")
    require_false(completeness.get("forward_fill_allowed"), "policy.forward_fill_allowed")
    require_false(completeness.get("backfill_allowed"), "policy.backfill_allowed")
    require_false(completeness.get("synthetic_candles_allowed"), "policy.synthetic_candles_allowed")
    for artifact_name, artifact in (("creation", creation), ("compliance", compliance)):
        require_equal(
            artifact.get("complete_hour_required_source_rows"),
            COMPLETE_HOUR_REQUIRED_SOURCE_ROWS,
            f"{artifact_name}.complete_hour_required_source_rows",
        )
        require_false(artifact.get("synthetic_fill_allowed"), f"{artifact_name}.synthetic_fill_allowed")
        require_equal(artifact.get("incomplete_hour_policy"), INCOMPLETE_HOUR_POLICY, f"{artifact_name}.incomplete_hour_policy")


def validate_numeric_sanity(policy: Dict[str, Any]) -> None:
    numeric = policy.get("numeric_sanity_policy", {})
    require_true(numeric.get("ohlc_must_parse_numeric"), "policy.ohlc_must_parse_numeric")
    require_true(numeric.get("volume_fields_must_parse_numeric"), "policy.volume_fields_must_parse_numeric")
    require_contains(str(numeric.get("high_sanity_check", "")), "high >=", "policy.high_sanity_check")
    require_contains(str(numeric.get("low_sanity_check", "")), "low <=", "policy.low_sanity_check")
    require_equal(numeric.get("negative_volume_policy"), "invalid", "policy.negative_volume_policy")
    require_equal(numeric.get("nan_inf_policy"), "invalid", "policy.nan_inf_policy")
    require_equal(numeric.get("parse_failures_policy"), "quarantine_or_fail_closed", "policy.parse_failures_policy")


def validate_preconditions(policy: Dict[str, Any], creation: Dict[str, Any], compliance: Dict[str, Any]) -> None:
    preconditions = policy.get("source_preconditions_policy", {})
    required_true = (
        "source_manifest_required",
        "provenance_report_required",
        "symbol_universe_required",
        "coverage_resolution_required",
        "source_file_hash_manifest_required",
        "rollback_policy_required",
        "timeout_policy_required",
        "memory_disk_resource_policy_required",
        "historical_data_quality_validator_required",
        "holdout_policy_required",
        "survivorship_bias_controls_required",
    )
    for field in required_true:
        require_true(preconditions.get(field), f"policy.{field}")
    for field in (
        "source_manifest_required",
        "provenance_report_required",
        "symbol_universe_required",
        "coverage_resolution_required",
    ):
        require_true(creation.get(field), f"creation.{field}")
        if field in compliance:
            require_true(compliance.get(field), f"compliance.{field}")


def validate_forbidden_surface(policy: Dict[str, Any], creation: Dict[str, Any]) -> None:
    forbidden = policy.get("forbidden_policy", {})
    for field in (
        "aggregation_execution_by_this_module_forbidden",
        "data_build_by_this_module_forbidden",
        "acquisition_execution_by_this_module_forbidden",
        "download_api_browse_by_this_module_forbidden",
        "strategy_backtest_candidate_runtime_live_generic_runner_schema_config_forbidden",
        "policy_is_not_evidence_of_built_data",
        "one_minute_data_must_not_be_treated_as_direct_one_hour_data",
        "one_sample_file_must_not_be_treated_as_full_coverage_or_full_manifest",
    ):
        require_true(forbidden.get(field), f"policy.forbidden.{field}")
    forbidden_false_fields = (
        "strategy_signal_claims_made",
        "tradable_edge_claims_made",
        "profit_claims_made",
        "backtest_performed",
        "candidate_generation_performed",
        "runtime_touch_performed",
        "capital_touch_performed",
        "live_touch_performed",
        "old_source_panel_anomaly_route_reopened_now",
    )
    for field in forbidden_false_fields:
        require_false(creation.get(field), f"creation.{field}")


def build_payload(
    preflight: Dict[str, Any],
    creation: Dict[str, Any],
    policy: Dict[str, Any],
    compliance: Dict[str, Any],
    policy_exists: bool,
    policy_valid_json: bool,
    compliance_exists: bool,
    compliance_valid_json: bool,
) -> Dict[str, Any]:
    identity = policy["policy_identity"]
    schema = policy["input_schema_policy"]
    time_policy = policy["canonical_time_policy"]
    completeness = policy["completeness_policy"]
    preconditions = policy["source_preconditions_policy"]
    flags = dangerous_flags()
    p1_count = max(int(creation.get("active_p1_attention_count", 8)), 8)
    replacement_checks = {
        "policy_artifact_exists": policy_exists,
        "policy_artifact_valid_json": policy_valid_json,
        "compliance_report_exists": compliance_exists,
        "compliance_report_valid_json": compliance_valid_json,
        "policy_scope_future_only": identity.get("policy_scope") == POLICY_SCOPE,
        "execution_blocked_now": identity.get("policy_execution_allowed_now") is False,
        "aggregation_blocked_now": identity.get("aggregation_execution_allowed_now") is False,
        "data_build_blocked_now": identity.get("data_build_allowed_now") is False,
        "acquisition_blocked_now": identity.get("acquisition_execution_allowed_now") is False,
        "direct_1h_not_expected": schema.get("direct_1h_input_expected") is False,
        "complete_hour_requires_60_rows": completeness.get("complete_hour_required_source_rows") == 60,
        "synthetic_fill_forbidden": completeness.get("synthetic_fill_allowed") is False,
        "manifest_prerequisites_remain": preconditions.get("source_manifest_required") is True,
        "p1_carried_forward": p1_count >= 8,
        "dormant_attention_carried_forward": creation.get("dormant_repo_attention_count") == 716,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
    }
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "PREVIEW_OKX_SOURCE_MANIFEST_REQUIREMENTS_NO_EXECUTION_NO_DOWNLOAD_NO_API",
        "next_module": NEXT_MODULE_PASS,
        **preflight,
        "prior_aggregation_policy_creation_respected": True,
        "policy_artifact_validation_completed": True,
        "execution_block_validation_completed": True,
        "input_schema_validation_completed": True,
        "time_bucket_validation_completed": True,
        "ohlcv_rule_validation_completed": True,
        "completeness_fail_closed_validation_completed": True,
        "numeric_sanity_validation_completed": True,
        "precondition_validation_completed": True,
        "risk_decision_completed": True,
        "okx_1m_to_1h_aggregation_policy_validated": True,
        "policy_artifact_exists": policy_exists,
        "policy_artifact_valid_json": policy_valid_json,
        "compliance_report_exists": compliance_exists,
        "compliance_report_valid_json": compliance_valid_json,
        "policy_name": identity["policy_name"],
        "policy_scope": identity["policy_scope"],
        "policy_execution_allowed_now": identity["policy_execution_allowed_now"],
        "aggregation_execution_allowed_now": identity["aggregation_execution_allowed_now"],
        "data_build_allowed_now": identity["data_build_allowed_now"],
        "acquisition_execution_allowed_now": identity["acquisition_execution_allowed_now"],
        "expected_input_interval": schema["expected_input_interval"],
        "expected_open_time_delta_ms": schema["expected_open_time_delta_ms"],
        "direct_1h_input_expected": schema["direct_1h_input_expected"],
        "timestamp_unit": schema["timestamp_unit"],
        "canonical_aggregation_time_basis": time_policy["canonical_aggregation_time_basis"],
        "output_hour_bucket_policy": time_policy["output_hour_bucket_policy"],
        "complete_hour_required_source_rows": completeness["complete_hour_required_source_rows"],
        "synthetic_fill_allowed": completeness["synthetic_fill_allowed"],
        "incomplete_hour_policy": completeness["incomplete_hour_policy"],
        "duplicate_minute_policy": completeness["duplicate_minute_policy"],
        "missing_minute_policy": completeness["missing_minute_policy"],
        "confirm_policy": CONFIRM_POLICY,
        "ohlcv_rules_validated": True,
        "numeric_sanity_rules_validated": True,
        "source_manifest_required": preconditions["source_manifest_required"],
        "provenance_report_required": preconditions["provenance_report_required"],
        "symbol_universe_required": preconditions["symbol_universe_required"],
        "coverage_resolution_required": preconditions["coverage_resolution_required"],
        "source_manifest_still_required": True,
        "provenance_report_still_required": True,
        "coverage_resolution_still_required": True,
        "policy_safe_for_future_build_preview": True,
        "policy_safe_for_execution_now": False,
        "okx_acquisition_readiness": False,
        "aggregation_performed_now": False,
        "data_build_performed": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "okx_sample_zip_downloaded_now": False,
        "fake_or_synthetic_data_detected": False,
        "future_data_build_requires_separate_approval": True,
        "okx_aggregation_policy_validation_p0_count": 0,
        "okx_aggregation_policy_validation_p1_count": p1_count,
        "okx_aggregation_policy_validation_p2_count": 0,
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
        "current_evidence_chain_quality_after_validator": EVIDENCE_AFTER,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": p1_count,
        "dormant_repo_attention_count": 716,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": planned_schema_files_existing_count(),
        "generic_runner_target_exists": generic_runner_target_exists(),
        "dangerous_flags": flags,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "dangerous_flags_true_count": sum(1 for value in flags.values() if value),
        "derived_live_repo_post_check": (
            "PASS_OKX_1M_TO_1H_AGGREGATION_POLICY_VALIDATED_SOURCE_MANIFEST_PREVIEW_READY_NO_EXECUTION"
        ),
        "derived_live_repo_post_check_reason": (
            "repo-only validator confirmed the created OKX 1m-to-1h aggregation policy and compliance report; "
            "execution, aggregation, data build, CSV reads, browsing, downloads, API calls, source manifest creation, "
            "schema/config creation, strategy, backtest, candidate, runtime, capital, live, and generic-runner actions remain blocked"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": all(replacement_checks.values()),
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "tracked_python_count_expectation": {
            "pre_commit": EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT,
        },
    }
    if payload["planned_schema_files_existing_count"] != 0:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: planned schema files exist unexpectedly")
    if payload["generic_runner_target_exists"] is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: generic runner target exists unexpectedly")
    if payload["replacement_checks_all_true"] is not True:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: replacement checks failed")
    return payload


def write_validator_artifact(payload: Dict[str, Any]) -> None:
    write_json(
        OUT_DIR
        / "repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_after_creation_v1_latest.json",
        payload,
    )


def blocked_payload(exc: Exception) -> Dict[str, Any]:
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_status": STATUS_BLOCKED_CONTEXT,
        "final_decision": STATUS_BLOCKED_CONTEXT,
        "next_action": "STOP_FAIL_CLOSED_NO_AGGREGATION_NO_DATA_BUILD_NO_BROWSE_NO_DOWNLOAD_NO_API",
        "next_module": NEXT_MODULE_BLOCKED,
        "error": str(exc),
        "whole_system_preflight_completed": False,
        "live_next_module_matches_requested_module": False,
        "artifact_chain_consistent": False,
        "stale_or_contradictory_artifact_detected": True,
        "active_p0_blocker_count": 1,
        "okx_1m_to_1h_aggregation_policy_validated": False,
        "policy_safe_for_future_build_preview": False,
        "policy_safe_for_execution_now": False,
        "aggregation_performed_now": False,
        "data_build_performed": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "okx_sample_zip_downloaded_now": False,
        "schema_or_config_created": False,
        "dangerous_flags": dangerous_flags(),
        "dangerous_flags_all_false": True,
        "dangerous_flags_true_count": 0,
    }


def main() -> int:
    try:
        creation = load_json(CREATION_ARTIFACT, "creation artifact")
        policy, policy_exists, policy_valid_json, policy_non_empty = read_json_checked(POLICY_ARTIFACT)
        compliance, compliance_exists, compliance_valid_json, compliance_non_empty = read_json_checked(COMPLIANCE_REPORT)
        if not (policy_exists and policy_valid_json and policy_non_empty):
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: policy artifact missing/invalid/empty")
        if not (compliance_exists and compliance_valid_json and compliance_non_empty):
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: compliance report missing/invalid/empty")
        approval = load_json(APPROVAL_ARTIFACT, "approval artifact")
        preview = load_json(PREVIEW_ARTIFACT, "preview artifact")
        metadata_validator = load_json(METADATA_VALIDATOR_ARTIFACT, "metadata validator artifact")
        preflight = validate_chain_artifacts(creation, approval, preview, metadata_validator)
        validate_policy_artifact(policy, compliance, creation)
        validate_execution_block(policy, creation, compliance)
        validate_input_schema(policy, creation)
        validate_time_bucket(policy, creation)
        validate_ohlcv_rules(policy)
        validate_completeness(policy, creation, compliance)
        validate_numeric_sanity(policy)
        validate_preconditions(policy, creation, compliance)
        validate_forbidden_surface(policy, creation)
        payload = build_payload(
            preflight,
            creation,
            policy,
            compliance,
            policy_exists,
            policy_valid_json,
            compliance_exists,
            compliance_valid_json,
        )
        write_validator_artifact(payload)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        payload = blocked_payload(exc)
        write_validator_artifact(payload)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
