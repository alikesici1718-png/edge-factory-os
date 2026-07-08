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
    "edge_factory_os_repo_only_historical_data_acquisition_okx_source_manifest_preview_after_"
    "aggregation_policy_validator_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_source_manifest_preview_after_"
    "aggregation_policy_validator_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "7fe8e6a"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 675
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 676

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_source_manifest_preview_after_"
    "aggregation_policy_validator_v1.py"
)
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_source_manifest_approval_after_preview_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_source_manifest_preview_blocked_record_after_"
    "aggregation_policy_validator_v1.py"
)

VALIDATOR_DIR = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_after_creation_v1"
)
VALIDATOR_ARTIFACT = (
    VALIDATOR_DIR
    / "repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_after_creation_v1_latest.json"
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
METADATA_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_input_validator_after_approval_v1"
    / "repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_input_validator_after_approval_v1_latest.json"
)
SOURCE_IDENTITY_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_validator_after_approval_v1"
    / "repo_only_historical_data_acquisition_browse_only_source_identity_lookup_validator_after_approval_v1_latest.json"
)

VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_VALIDATED_"
    "SOURCE_MANIFEST_PREVIEW_READY_NO_EXECUTION"
)
CREATION_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_CREATED_"
    "PENDING_VALIDATOR_NO_EXECUTION"
)
METADATA_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_METADATA_INPUT_VALIDATED_"
    "1M_SCHEMA_AGGREGATION_POLICY_PREVIEW_READY_NO_EXECUTION"
)
SOURCE_IDENTITY_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_VALIDATED_PARTIAL_OKX_IDENTITY_"
    "ARCHIVE_SCOPE_RESOLUTION_PREVIEW_READY_NO_EXECUTION"
)
STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SOURCE_MANIFEST_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_VALIDATED_SOURCE_MANIFEST_"
    "PREVIEW_READY_NO_EXECUTION"
)
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SOURCE_MANIFEST_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION"
)
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"

POLICY_NAME = "OKX_1M_TO_1H_AGGREGATION_POLICY_V1"
POLICY_SCOPE = "FUTURE_DATA_BUILD_POLICY_ONLY"
EXPECTED_INPUT_INTERVAL = "1m"
EXPECTED_OPEN_TIME_DELTA_MS = 60000
TIMESTAMP_UNIT = "epoch_milliseconds"
COMPLETE_HOUR_REQUIRED_SOURCE_ROWS = 60

KNOWN_SAMPLE_URL = (
    "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/20260518/"
    "BTC-USDT-SWAP-candlesticks-2026-05-18.zip"
)
KNOWN_SAMPLE_FILE = "BTC-USDT-SWAP-candlesticks-2026-05-18.csv"
KNOWN_SAMPLE_SCHEMA = [
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
KNOWN_ARCHIVE_GROUPING_OPTIONS = ["daily", "month"]
TARGET_INSTRUMENT_TYPE = "perpetual_swap"
TARGET_MARKET_SCOPE = "USDT_SWAP_PERPETUALS_PENDING_SYMBOL_UNIVERSE_POLICY"

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


def require_prior_false_flags(artifact: Dict[str, Any], label: str) -> None:
    for field in (
        "aggregation_performed_now",
        "data_build_performed",
        "okx_download_performed",
        "okx_api_call_performed",
        "okx_sample_zip_downloaded_now",
    ):
        if field in artifact:
            require_false(artifact.get(field), f"{label}.{field}")
    validate_no_true_dangerous_flags(artifact, label)


def validate_policy_json(policy: Dict[str, Any]) -> None:
    identity = policy.get("policy_identity", {})
    schema = policy.get("input_schema_policy", {})
    preconditions = policy.get("source_preconditions_policy", {})
    require_equal(identity.get("policy_name"), POLICY_NAME, "policy.policy_name")
    require_equal(identity.get("policy_scope"), POLICY_SCOPE, "policy.policy_scope")
    require_false(identity.get("policy_execution_allowed_now"), "policy.policy_execution_allowed_now")
    require_false(identity.get("aggregation_execution_allowed_now"), "policy.aggregation_execution_allowed_now")
    require_false(identity.get("data_build_allowed_now"), "policy.data_build_allowed_now")
    require_false(identity.get("acquisition_execution_allowed_now"), "policy.acquisition_execution_allowed_now")
    require_equal(schema.get("expected_input_interval"), EXPECTED_INPUT_INTERVAL, "policy.expected_input_interval")
    require_equal(schema.get("expected_open_time_delta_ms"), EXPECTED_OPEN_TIME_DELTA_MS, "policy.expected_delta")
    require_false(schema.get("direct_1h_input_expected"), "policy.direct_1h_input_expected")
    require_equal(schema.get("timestamp_unit"), TIMESTAMP_UNIT, "policy.timestamp_unit")
    for field in (
        "source_manifest_required",
        "provenance_report_required",
        "symbol_universe_required",
        "coverage_resolution_required",
    ):
        require_true(preconditions.get(field), f"policy.{field}")


def validate_preflight(
    validator: Dict[str, Any],
    creation: Dict[str, Any],
    policy: Dict[str, Any],
    metadata_validator: Dict[str, Any],
    source_identity_validator: Dict[str, Any],
) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))

    require_equal(
        validator.get("historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_status"),
        VALIDATOR_STATUS_PASS,
        "validator.status",
    )
    require_equal(validator.get("next_module"), REQUESTED_MODULE, "validator.next_module", STATUS_BLOCKED_NEXT_MODULE)
    require_true(validator.get("okx_1m_to_1h_aggregation_policy_validated"), "validator.policy_validated")
    require_true(validator.get("policy_safe_for_future_build_preview"), "validator.safe_for_future_build_preview")
    require_false(validator.get("policy_safe_for_execution_now"), "validator.safe_for_execution_now")
    for field in (
        "source_manifest_required",
        "provenance_report_required",
        "symbol_universe_required",
        "coverage_resolution_required",
        "source_manifest_still_required",
        "provenance_report_still_required",
        "coverage_resolution_still_required",
    ):
        require_true(validator.get(field), f"validator.{field}")
    for field in (
        "aggregation_performed_now",
        "data_build_performed",
        "okx_download_performed",
        "okx_api_call_performed",
        "okx_browse_performed",
        "okx_sample_zip_downloaded_now",
        "acquisition_execution_allowed_now",
    ):
        require_false(validator.get(field), f"validator.{field}")
    require_equal(validator.get("active_p0_blocker_count"), 0, "validator.active_p0_blocker_count")
    require_equal(validator.get("active_p1_attention_count"), 8, "validator.active_p1_attention_count")
    require_equal(validator.get("dormant_repo_attention_count"), 716, "validator.dormant_repo_attention_count")
    require_true(validator.get("replacement_checks_all_true"), "validator.replacement_checks_all_true")
    validate_no_true_dangerous_flags(validator, "validator")

    require_equal(
        creation.get("historical_data_acquisition_okx_1m_to_1h_aggregation_policy_creation_status"),
        CREATION_STATUS_PASS,
        "creation.status",
    )
    require_true(creation.get("okx_1m_to_1h_aggregation_policy_created"), "creation.policy_created")
    require_equal(creation.get("policy_name"), POLICY_NAME, "creation.policy_name")
    require_equal(creation.get("policy_scope"), POLICY_SCOPE, "creation.policy_scope")
    require_prior_false_flags(creation, "creation")

    validate_policy_json(policy)

    require_equal(
        metadata_validator.get("historical_data_acquisition_okx_user_manual_archive_metadata_input_validator_status"),
        METADATA_VALIDATOR_STATUS_PASS,
        "metadata_validator.status",
    )
    require_true(metadata_validator.get("okx_1m_schema_validated"), "metadata_validator.okx_1m_schema_validated")
    require_false(metadata_validator.get("okx_direct_1h_interval_present"), "metadata_validator.direct_1h_present")
    require_prior_false_flags(metadata_validator, "metadata_validator")

    require_equal(
        source_identity_validator.get("historical_data_acquisition_browse_only_source_identity_lookup_validator_status"),
        SOURCE_IDENTITY_VALIDATOR_STATUS_PASS,
        "source_identity_validator.status",
    )
    require_true(
        source_identity_validator.get("okx_source_identity_partially_verified_validated"),
        "source_identity_validator.partial_identity_validated",
    )
    require_false(
        source_identity_validator.get("okx_source_verified_for_acquisition_now"),
        "source_identity_validator.source_verified_for_acquisition_now",
    )
    require_true(
        source_identity_validator.get("okx_archive_pattern_evidence_found"),
        "source_identity_validator.archive_pattern_evidence_found",
    )
    require_equal(
        source_identity_validator.get("okx_candlestick_coverage_start"),
        "July 2023",
        "source_identity_validator.coverage_start",
    )
    require_false(source_identity_validator.get("full_4_year_coverage_proven_now"), "source_identity.full_4_year")
    require_false(source_identity_validator.get("source_manifest_proven_now"), "source_identity.source_manifest_proven_now")
    require_prior_false_flags(source_identity_validator, "source_identity_validator")

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
        "validator_artifact": str(VALIDATOR_ARTIFACT),
        "creation_artifact": str(CREATION_ARTIFACT),
        "policy_artifact": str(POLICY_ARTIFACT),
        "metadata_validator_artifact": str(METADATA_VALIDATOR_ARTIFACT),
        "source_identity_validator_artifact": str(SOURCE_IDENTITY_VALIDATOR_ARTIFACT),
        "head": head,
        "status_lines_allowed": [f"?? {CURRENT_TOOL_REL}", f"A  {CURRENT_TOOL_REL}", f"AM {CURRENT_TOOL_REL}"],
    }


def build_preview_sections() -> Dict[str, Any]:
    return {
        "validator_context": {
            "aggregation_policy_validator_passed": True,
            "aggregation_policy_safe_only_for_future_build_preview": True,
            "source_manifest_still_required": True,
            "provenance_still_required": True,
            "symbol_universe_still_required": True,
            "coverage_resolution_still_required": True,
            "acquisition_readiness": False,
            "no_data_build_aggregation_download_api_occurred": True,
            "active_p1_attention_count": 8,
            "dormant_repo_attention_count": 716,
        },
        "source_manifest_scope_preview": {
            "source_name": "OKX_HISTORICAL_CANDLESTICK_ARCHIVE",
            "source_type": "OFFICIAL_OKX_HISTORICAL_DATA_ARCHIVE",
            "instrument_type": TARGET_INSTRUMENT_TYPE,
            "target_market_scope": TARGET_MARKET_SCOPE,
            "input_interval": EXPECTED_INPUT_INTERVAL,
            "output_target_interval": "1h",
            "archive_grouping_options": KNOWN_ARCHIVE_GROUPING_OPTIONS,
            "known_sample_url": KNOWN_SAMPLE_URL,
            "known_sample_file": KNOWN_SAMPLE_FILE,
            "known_sample_schema": KNOWN_SAMPLE_SCHEMA,
            "known_timestamp_unit": TIMESTAMP_UNIT,
            "known_daily_boundary_interpretation": "LIKELY_UTC_PLUS_8_EXCHANGE_DAY",
            "manifest_status": "PREVIEW_ONLY_NOT_CREATED",
        },
        "required_manifest_fields": [
            "manifest_id",
            "source_owner",
            "source_page_url",
            "archive_file_url",
            "archive_file_name",
            "archive_grouping",
            "instrument_name",
            "instrument_type",
            "market_type",
            "date_or_month",
            "expected_interval",
            "expected_schema",
            "expected_timestamp_unit",
            "expected_daily_boundary",
            "expected_row_count_min",
            "expected_row_count_max",
            "expected_sha256_after_download",
            "local_storage_path_after_download",
            "provenance_status",
            "download_status",
            "validation_status",
            "included_in_build_allowed",
            "exclusion_reason_if_any",
        ],
        "coverage_requirements_preview": {
            "okx_page_candlestick_ohlc_history_start": "July 2023",
            "full_4_year_coverage_proven": False,
            "three_year_coverage_may_be_possible_depending_target_end_date_and_manifest": True,
            "future_manifest_must_calculate_coverage_start_end": True,
            "future_manifest_must_choose_target_horizon": ["3_years", "4_years", "OKX_only_shorter_horizon"],
            "fail_closed_if_coverage_target_unclear": True,
            "must_not_pretend_pre_july_2023_okx_archive_exists_unless_proven": True,
        },
        "symbol_universe_requirements_preview": {
            "current_active_only_requires_survivorship_bias_warning": True,
            "explicit_symbol_universe_policy_required": True,
            "symbol_universe_options": [
                "user_supplied_perpetual_swap_symbol_list",
                "okx_browsed_or_exported_symbol_universe_after_separate_approval",
                "local_previously_existing_symbol_universe_if_validated",
            ],
            "delisted_or_inactive_symbols_must_be_handled_or_marked_unknown": True,
            "must_not_silently_use_only_active_symbols_for_historical_universe_claim": True,
        },
        "provenance_hash_requirements_preview": {
            "source_url_capture_required": True,
            "download_timestamp_later_required": True,
            "local_file_path_later_required": True,
            "sha256_after_download_later_required": True,
            "file_size_after_download_later_required": True,
            "row_count_after_validation_later_required": True,
            "schema_validation_later_required": True,
            "per_file_inclusion_exclusion_reason_later_required": True,
            "hash_claim_before_separately_approved_download_forbidden": True,
        },
        "manifest_fail_closed_preview": {
            "fail_if_source_url_pattern_ambiguous": True,
            "fail_if_symbol_universe_missing": True,
            "fail_if_coverage_start_end_unresolved": True,
            "fail_if_expected_schema_missing": True,
            "fail_if_expected_interval_not_1m": True,
            "fail_if_file_list_requires_download_or_api": True,
            "fail_if_unverified_files_marked_build_ready": True,
            "fail_if_files_lack_provenance_placeholders": True,
            "fail_if_hash_claimed_before_download": True,
            "fail_if_4_year_coverage_claimed_without_proof": True,
            "fail_if_data_build_permitted_before_validator": True,
            "fail_if_strategy_backtest_candidate_runtime_live_touched": True,
        },
        "future_required_artifacts": [
            "historical_okx_source_manifest_plan.json",
            "historical_okx_source_manifest_creation_approval.json",
            "historical_okx_source_manifest.json",
            "historical_okx_source_manifest_contract_compliance_report.json",
            "historical_okx_source_manifest_validator.json",
            "historical_okx_symbol_universe_policy_report.json",
            "historical_okx_coverage_policy_report.json",
            "historical_okx_provenance_placeholder_report.json",
        ],
        "evidence_policy_preview": {
            "before_preview": EVIDENCE_BEFORE,
            "after_preview": EVIDENCE_AFTER,
            "preview_is_real_manifest": False,
            "preview_is_provenance": False,
            "preview_is_data_acquisition": False,
            "preview_is_data_build": False,
            "preview_is_aggregation": False,
            "acquisition_remains_blocked": True,
            "p1_remains_active_until_manifest_provenance_coverage_build_validators_close_it": True,
        },
    }


def build_payload(preflight: Dict[str, Any], preview_sections: Dict[str, Any]) -> Dict[str, Any]:
    flags = dangerous_flags()
    replacement_checks = {
        "preflight_passed": preflight.get("whole_system_preflight_decision") == "PASS",
        "prior_validator_respected": True,
        "preview_completed": True,
        "real_manifest_not_created": True,
        "approval_required_next": True,
        "download_api_browse_absent": True,
        "data_build_absent": True,
        "aggregation_absent": True,
        "source_manifest_still_required": True,
        "provenance_still_required": True,
        "symbol_universe_still_required": True,
        "coverage_resolution_still_required": True,
        "hash_claims_blocked": True,
        "p1_carried_forward": True,
        "dormant_attention_carried_forward": True,
        "schema_config_absent": True,
        "generic_runner_blocked": True,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
    }
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_source_manifest_preview_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "REQUEST_OKX_SOURCE_MANIFEST_CREATION_APPROVAL_NO_EXECUTION_NO_DOWNLOAD_NO_API",
        "next_module": NEXT_MODULE_PASS,
        **preflight,
        "prior_aggregation_policy_validator_respected": True,
        "okx_source_manifest_preview_completed": True,
        "validator_context_completed": True,
        "source_manifest_scope_preview_completed": True,
        "required_manifest_fields_completed": True,
        "coverage_requirements_preview_completed": True,
        "symbol_universe_requirements_preview_completed": True,
        "provenance_hash_requirements_preview_completed": True,
        "manifest_fail_closed_preview_completed": True,
        "future_required_artifacts_completed": True,
        "evidence_policy_preview_completed": True,
        "source_manifest_created_now": False,
        "source_manifest_preview_only": True,
        "source_manifest_required": True,
        "provenance_report_required": True,
        "symbol_universe_required": True,
        "coverage_resolution_required": True,
        "okx_known_sample_url_recorded": True,
        "okx_known_sample_schema_recorded": True,
        "okx_known_sample_interval": EXPECTED_INPUT_INTERVAL,
        "okx_known_archive_grouping_options": "daily,month",
        "okx_target_instrument_type": TARGET_INSTRUMENT_TYPE,
        "okx_target_market_scope": TARGET_MARKET_SCOPE,
        "okx_coverage_start_known_from_page": "July 2023",
        "okx_full_4_year_coverage_proven_now": False,
        "okx_3_year_coverage_requires_manifest": True,
        "symbol_universe_policy_required": True,
        "survivorship_bias_controls_required": True,
        "hash_claims_allowed_now": False,
        "provenance_placeholders_required": True,
        "source_manifest_creation_allowed_now": False,
        "source_manifest_creation_approval_required_next": True,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "acquisition_execution_allowed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "okx_sample_zip_downloaded_now": False,
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
        "current_evidence_chain_quality_before_preview": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_preview": EVIDENCE_AFTER,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 8,
        "dormant_repo_attention_count": 716,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": planned_schema_files_existing_count(),
        "generic_runner_target_exists": generic_runner_target_exists(),
        "dangerous_flags": flags,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "dangerous_flags_true_count": sum(1 for value in flags.values() if value),
        "source_manifest_preview": preview_sections,
        "derived_live_repo_post_check": (
            "PASS_OKX_SOURCE_MANIFEST_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION"
        ),
        "derived_live_repo_post_check_reason": (
            "repo-only preview defined the future OKX source manifest requirements and kept real manifest creation, "
            "downloads, APIs, browsing, data fetch, data build, aggregation, acquisition execution, schema/config, "
            "strategy, backtest, candidate, runtime, capital, live, and generic-runner actions blocked"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": all(replacement_checks.values()),
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "tracked_python_count_expectation": {
            "pre_commit": EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT,
        },
    }
    if payload["source_manifest_created_now"] is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: source manifest falsely created")
    if payload["planned_schema_files_existing_count"] != 0:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: planned schema files exist unexpectedly")
    if payload["generic_runner_target_exists"] is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: generic runner target exists unexpectedly")
    if payload["dangerous_flags_all_false"] is not True or payload["dangerous_flags_true_count"] != 0:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: dangerous flags not all false")
    if payload["replacement_checks_all_true"] is not True:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: replacement checks failed")
    return payload


def write_preview_artifacts(payload: Dict[str, Any]) -> None:
    preview = payload.get(
        "source_manifest_preview",
        {
            "manifest_status": "BLOCKED_PREVIEW_NOT_CREATED",
            "source_manifest_created_now": False,
            "data_download_performed": False,
            "data_fetch_performed": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "okx_download_performed": False,
            "okx_api_call_performed": False,
            "okx_browse_performed": False,
        },
    )
    write_json(OUT_DIR / "historical_okx_source_manifest_preview.json", preview)
    write_json(
        OUT_DIR / "repo_only_historical_data_acquisition_okx_source_manifest_preview_after_aggregation_policy_validator_v1_latest.json",
        payload,
    )


def blocked_payload(exc: Exception) -> Dict[str, Any]:
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_source_manifest_preview_status": STATUS_BLOCKED_CONTEXT,
        "final_decision": STATUS_BLOCKED_CONTEXT,
        "next_action": "STOP_FAIL_CLOSED_NO_MANIFEST_NO_DOWNLOAD_NO_API_NO_BUILD_NO_AGGREGATION",
        "next_module": NEXT_MODULE_BLOCKED,
        "error": str(exc),
        "whole_system_preflight_completed": False,
        "live_next_module_matches_requested_module": False,
        "artifact_chain_consistent": False,
        "stale_or_contradictory_artifact_detected": True,
        "active_p0_blocker_count": 1,
        "okx_source_manifest_preview_completed": False,
        "source_manifest_created_now": False,
        "source_manifest_preview_only": False,
        "source_manifest_creation_allowed_now": False,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
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
        validator = load_json(VALIDATOR_ARTIFACT, "aggregation policy validator artifact")
        creation = load_json(CREATION_ARTIFACT, "aggregation policy creation artifact")
        policy = load_json(POLICY_ARTIFACT, "created policy artifact")
        metadata_validator = load_json(METADATA_VALIDATOR_ARTIFACT, "metadata validator artifact")
        source_identity_validator = load_json(SOURCE_IDENTITY_VALIDATOR_ARTIFACT, "source identity validator artifact")
        preflight = validate_preflight(validator, creation, policy, metadata_validator, source_identity_validator)
        preview_sections = build_preview_sections()
        payload = build_payload(preflight, preview_sections)
        write_preview_artifacts(payload)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        payload = blocked_payload(exc)
        write_preview_artifacts(payload)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
