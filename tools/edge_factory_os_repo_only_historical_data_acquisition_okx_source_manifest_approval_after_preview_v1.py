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
    "edge_factory_os_repo_only_historical_data_acquisition_okx_source_manifest_approval_after_preview_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_source_manifest_approval_after_preview_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "ec5aa98"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 676
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 677

REQUESTED_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_source_manifest_approval_after_preview_v1.py"
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_coverage_provenance_"
    "resolution_preview_after_source_manifest_bundle_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_source_manifest_bundle_blocked_record_after_preview_v1.py"
)

PREVIEW_DIR = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_source_manifest_preview_after_aggregation_policy_validator_v1"
)
PREVIEW_ARTIFACT = (
    PREVIEW_DIR
    / "repo_only_historical_data_acquisition_okx_source_manifest_preview_after_aggregation_policy_validator_v1_latest.json"
)
AGGREGATION_POLICY_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_after_creation_v1"
    / "repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_after_creation_v1_latest.json"
)
AGGREGATION_POLICY_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_creation_after_approval_v1"
    / "historical_okx_1m_to_1h_aggregation_policy.json"
)
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

PREVIEW_STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SOURCE_MANIFEST_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION"
AGGREGATION_POLICY_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_VALIDATED_"
    "SOURCE_MANIFEST_PREVIEW_READY_NO_EXECUTION"
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
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SOURCE_MANIFEST_PLACEHOLDER_BUNDLE_VALIDATED_"
    "SYMBOL_UNIVERSE_COVERAGE_PROVENANCE_RESOLUTION_PREVIEW_READY_NO_EXECUTION"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = "HISTORICAL_DATA_ACQUISITION_OKX_SOURCE_MANIFEST_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION"
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SOURCE_MANIFEST_PLACEHOLDER_BUNDLE_VALIDATED_SYMBOL_UNIVERSE_"
    "COVERAGE_PROVENANCE_RESOLUTION_PREVIEW_READY_NO_EXECUTION"
)

POLICY_NAME = "OKX_1M_TO_1H_AGGREGATION_POLICY_V1"
POLICY_SCOPE = "FUTURE_DATA_BUILD_POLICY_ONLY"
SOURCE_PAGE_URL = "https://tr.okx.com/en/historical-data"
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
EXPECTED_INPUT_INTERVAL = "1m"
OUTPUT_TARGET_INTERVAL = "1h"
TIMESTAMP_UNIT = "epoch_milliseconds"
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


def require_false_fields(artifact: Dict[str, Any], label: str, fields: List[str]) -> None:
    for field in fields:
        if field in artifact:
            require_false(artifact.get(field), f"{label}.{field}")


def validate_preflight(
    preview: Dict[str, Any],
    policy_validator: Dict[str, Any],
    policy: Dict[str, Any],
    metadata_validator: Dict[str, Any],
    source_identity_validator: Dict[str, Any],
) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))

    require_equal(preview.get("historical_data_acquisition_okx_source_manifest_preview_status"), PREVIEW_STATUS_PASS, "preview.status")
    require_equal(preview.get("next_module"), REQUESTED_MODULE, "preview.next_module", STATUS_BLOCKED_NEXT_MODULE)
    for field in (
        "okx_source_manifest_preview_completed",
        "source_manifest_preview_only",
        "source_manifest_required",
        "provenance_report_required",
        "symbol_universe_required",
        "coverage_resolution_required",
        "source_manifest_creation_approval_required_next",
        "provenance_placeholders_required",
    ):
        require_true(preview.get(field), f"preview.{field}")
    require_false(preview.get("source_manifest_created_now"), "preview.source_manifest_created_now")
    require_false(preview.get("source_manifest_creation_allowed_now"), "preview.source_manifest_creation_allowed_now")
    require_false(preview.get("hash_claims_allowed_now"), "preview.hash_claims_allowed_now")
    require_false_fields(
        preview,
        "preview",
        [
            "data_download_performed",
            "data_fetch_performed",
            "data_build_performed",
            "aggregation_performed_now",
            "acquisition_execution_allowed_now",
            "external_download_allowed_now",
            "external_api_allowed_now",
            "okx_download_performed",
            "okx_api_call_performed",
            "okx_browse_performed",
            "okx_sample_zip_downloaded_now",
        ],
    )
    require_equal(preview.get("active_p0_blocker_count"), 0, "preview.active_p0_blocker_count")
    require_equal(preview.get("active_p1_attention_count"), 8, "preview.active_p1_attention_count")
    require_equal(preview.get("dormant_repo_attention_count"), 716, "preview.dormant_repo_attention_count")
    require_true(preview.get("replacement_checks_all_true"), "preview.replacement_checks_all_true")
    validate_no_true_dangerous_flags(preview, "preview")

    require_equal(
        policy_validator.get("historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_status"),
        AGGREGATION_POLICY_VALIDATOR_STATUS_PASS,
        "policy_validator.status",
    )
    require_true(policy_validator.get("okx_1m_to_1h_aggregation_policy_validated"), "policy_validator.validated")
    require_true(policy_validator.get("policy_safe_for_future_build_preview"), "policy_validator.future_preview")
    require_false(policy_validator.get("policy_safe_for_execution_now"), "policy_validator.execution_now")
    require_equal(policy_validator.get("active_p1_attention_count"), 8, "policy_validator.active_p1_attention_count")
    require_equal(policy_validator.get("dormant_repo_attention_count"), 716, "policy_validator.dormant_repo_attention_count")
    validate_no_true_dangerous_flags(policy_validator, "policy_validator")

    identity = policy.get("policy_identity", {})
    schema = policy.get("input_schema_policy", {})
    require_equal(identity.get("policy_name"), POLICY_NAME, "policy.policy_name")
    require_equal(identity.get("policy_scope"), POLICY_SCOPE, "policy.policy_scope")
    require_false(identity.get("policy_execution_allowed_now"), "policy.policy_execution_allowed_now")
    require_false(identity.get("aggregation_execution_allowed_now"), "policy.aggregation_execution_allowed_now")
    require_false(identity.get("data_build_allowed_now"), "policy.data_build_allowed_now")
    require_false(identity.get("acquisition_execution_allowed_now"), "policy.acquisition_execution_allowed_now")
    require_equal(schema.get("expected_input_interval"), EXPECTED_INPUT_INTERVAL, "policy.expected_input_interval")
    require_equal(schema.get("timestamp_unit"), TIMESTAMP_UNIT, "policy.timestamp_unit")
    require_false(schema.get("direct_1h_input_expected"), "policy.direct_1h_input_expected")

    require_equal(
        metadata_validator.get("historical_data_acquisition_okx_user_manual_archive_metadata_input_validator_status"),
        METADATA_VALIDATOR_STATUS_PASS,
        "metadata_validator.status",
    )
    require_true(metadata_validator.get("okx_1m_schema_validated"), "metadata_validator.okx_1m_schema_validated")
    require_false(metadata_validator.get("okx_direct_1h_interval_present"), "metadata_validator.direct_1h_present")
    validate_no_true_dangerous_flags(metadata_validator, "metadata_validator")

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
        "source_identity_validator.acquisition_ready",
    )
    require_true(source_identity_validator.get("okx_archive_pattern_evidence_found"), "source_identity.archive_pattern")
    require_equal(source_identity_validator.get("okx_candlestick_coverage_start"), "July 2023", "source_identity.coverage_start")
    require_false(source_identity_validator.get("source_manifest_proven_now"), "source_identity.source_manifest_proven_now")
    require_false(source_identity_validator.get("full_4_year_coverage_proven_now"), "source_identity.full_4_year")
    validate_no_true_dangerous_flags(source_identity_validator, "source_identity_validator")

    return {
        "whole_system_preflight_completed": True,
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
        "whole_system_preflight_decision": "PASS",
        "preview_artifact": str(PREVIEW_ARTIFACT),
        "aggregation_policy_validator_artifact": str(AGGREGATION_POLICY_VALIDATOR_ARTIFACT),
        "aggregation_policy_artifact": str(AGGREGATION_POLICY_ARTIFACT),
        "metadata_validator_artifact": str(METADATA_VALIDATOR_ARTIFACT),
        "source_identity_validator_artifact": str(SOURCE_IDENTITY_VALIDATOR_ARTIFACT),
        "head": head,
    }


def build_approval_record(generated_at_utc: str) -> Dict[str, Any]:
    return {
        "generated_at_utc": generated_at_utc,
        "source_manifest_approval_record_created": True,
        "user_source_manifest_approval_present": True,
        "user_source_manifest_approval_scope": (
            "BOUNDED_BUNDLE_APPROVAL_FOR_PLACEHOLDER_SOURCE_MANIFEST_NO_DOWNLOAD_NO_API_NO_BUILD"
        ),
        "approval_grants_approval_record_only": False,
        "approval_grants_placeholder_manifest_creation_now": True,
        "approval_grants_real_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_aggregation_now": False,
        "approval_grants_acquisition_execution_now": False,
    }


def build_placeholder_manifest(generated_at_utc: str) -> Dict[str, Any]:
    planned_sample_record = {
        "manifest_id": "OKX_PLACEHOLDER_SAMPLE_BTC_USDT_SWAP_2026_05_18_DAILY",
        "source_owner": "OKX",
        "source_page_url": SOURCE_PAGE_URL,
        "archive_file_url": KNOWN_SAMPLE_URL,
        "archive_file_name": KNOWN_SAMPLE_FILE.replace(".csv", ".zip"),
        "archive_grouping": "daily",
        "instrument_name": "BTC-USDT-SWAP",
        "instrument_type": TARGET_INSTRUMENT_TYPE,
        "market_type": "USDT_SWAP_PERPETUALS",
        "date_or_month": "2026-05-18",
        "expected_interval": EXPECTED_INPUT_INTERVAL,
        "expected_schema": KNOWN_SAMPLE_SCHEMA,
        "expected_timestamp_unit": TIMESTAMP_UNIT,
        "expected_daily_boundary": "LIKELY_UTC_PLUS_8_EXCHANGE_DAY",
        "expected_row_count_min": None,
        "expected_row_count_max": None,
        "download_status": "NOT_DOWNLOADED",
        "sha256_status": "NOT_AVAILABLE_UNTIL_DOWNLOAD",
        "expected_sha256_after_download": None,
        "local_storage_path_after_download": None,
        "included_in_build_allowed": False,
        "validation_status": "PENDING_DOWNLOAD_AND_VALIDATOR",
        "provenance_status": "PLACEHOLDER_ONLY",
        "exclusion_reason_if_any": "NOT_DOWNLOADED_NOT_VALIDATED_NOT_BUILD_READY",
    }
    return {
        "generated_at_utc": generated_at_utc,
        "manifest_status": "PLACEHOLDER_PLANNED_NOT_ACQUISITION_READY",
        "manifest_created_now": True,
        "manifest_is_placeholder_only": True,
        "manifest_is_build_ready": False,
        "manifest_is_download_ready": False,
        "manifest_is_acquisition_ready": False,
        "source_name": "OKX_HISTORICAL_CANDLESTICK_ARCHIVE",
        "source_type": "OFFICIAL_OKX_HISTORICAL_DATA_ARCHIVE_PARTIALLY_VERIFIED",
        "source_page_url": SOURCE_PAGE_URL,
        "instrument_type": TARGET_INSTRUMENT_TYPE,
        "target_market_scope": TARGET_MARKET_SCOPE,
        "input_interval": EXPECTED_INPUT_INTERVAL,
        "output_target_interval": OUTPUT_TARGET_INTERVAL,
        "archive_grouping_options": KNOWN_ARCHIVE_GROUPING_OPTIONS,
        "known_sample_url": KNOWN_SAMPLE_URL,
        "known_sample_file": KNOWN_SAMPLE_FILE,
        "known_sample_schema": KNOWN_SAMPLE_SCHEMA,
        "known_timestamp_unit": TIMESTAMP_UNIT,
        "known_sample_direct_interval": EXPECTED_INPUT_INTERVAL,
        "known_daily_boundary_interpretation": "LIKELY_UTC_PLUS_8_EXCHANGE_DAY",
        "aggregation_policy": POLICY_NAME,
        "aggregation_policy_validated": True,
        "coverage_start_from_page": "July 2023",
        "full_4_year_coverage_proven": False,
        "three_year_coverage_requires_manifest": True,
        "planned_file_records": [planned_sample_record],
        "downloaded_file_count": 0,
        "downloaded_files": [],
        "sha256_claim_count": 0,
        "build_ready_file_count": 0,
        "acquisition_ready": False,
        "source_manifest_validator_required": True,
    }


def build_symbol_universe_placeholder(generated_at_utc: str) -> Dict[str, Any]:
    return {
        "generated_at_utc": generated_at_utc,
        "symbol_universe_required": True,
        "symbol_universe_resolved_now": False,
        "target_scope": TARGET_MARKET_SCOPE,
        "current_active_only_not_allowed_without_survivorship_warning": True,
        "delisted_inactive_handling_required": True,
        "user_supplied_symbol_list_allowed_future": True,
        "browse_or_exported_symbol_universe_requires_separate_approval": True,
        "local_existing_symbol_universe_requires_validator": True,
    }


def build_coverage_placeholder(generated_at_utc: str) -> Dict[str, Any]:
    return {
        "generated_at_utc": generated_at_utc,
        "coverage_resolution_required": True,
        "okx_coverage_start_known_from_page": "July 2023",
        "full_4_year_coverage_proven_now": False,
        "three_year_coverage_possible_but_requires_manifest": True,
        "coverage_target_unresolved": True,
        "allowed_future_coverage_decisions": [
            "target 3 years OKX-only if manifest proves complete coverage",
            "target 4 years requires second source or explicit shorter-horizon policy decision",
        ],
        "no_coverage_claim_without_manifest": True,
    }


def build_provenance_placeholder(generated_at_utc: str) -> Dict[str, Any]:
    return {
        "generated_at_utc": generated_at_utc,
        "provenance_report_required": True,
        "provenance_resolved_now": False,
        "source_urls_recorded_as_static_identity_only": True,
        "download_timestamps_available": False,
        "file_hashes_available": False,
        "file_sizes_available": False,
        "row_counts_available": False,
        "local_paths_available": False,
        "hash_claims_allowed_now": False,
        "future_download_chain_required_for_hashes": True,
    }


def build_compliance_report(generated_at_utc: str) -> Dict[str, Any]:
    return {
        "generated_at_utc": generated_at_utc,
        "no_download": True,
        "no_api": True,
        "no_browse": True,
        "no_data_fetch": True,
        "no_data_build": True,
        "no_aggregation": True,
        "no_csv_read": True,
        "no_zip_read": True,
        "no_strategy_backtest_candidate": True,
        "no_runtime_capital_live": True,
        "no_generic_runner": True,
        "no_repo_schema_config": True,
        "no_hash_claims": True,
        "no_build_ready_files": True,
        "no_acquisition_ready_claim": True,
        "placeholder_only": True,
    }


def validate_placeholder_manifest(manifest: Dict[str, Any]) -> None:
    require_true(manifest.get("manifest_created_now"), "manifest.manifest_created_now")
    require_true(manifest.get("manifest_is_placeholder_only"), "manifest.placeholder_only")
    require_false(manifest.get("manifest_is_build_ready"), "manifest.build_ready")
    require_false(manifest.get("manifest_is_download_ready"), "manifest.download_ready")
    require_false(manifest.get("manifest_is_acquisition_ready"), "manifest.acquisition_ready")
    require_equal(manifest.get("downloaded_file_count"), 0, "manifest.downloaded_file_count")
    require_equal(manifest.get("sha256_claim_count"), 0, "manifest.sha256_claim_count")
    require_equal(manifest.get("build_ready_file_count"), 0, "manifest.build_ready_file_count")
    for record in manifest.get("planned_file_records", []):
        require_equal(record.get("download_status"), "NOT_DOWNLOADED", "planned_record.download_status")
        require_equal(record.get("sha256_status"), "NOT_AVAILABLE_UNTIL_DOWNLOAD", "planned_record.sha256_status")
        require_equal(record.get("expected_sha256_after_download"), None, "planned_record.expected_sha256")
        require_equal(record.get("local_storage_path_after_download"), None, "planned_record.local_path")
        require_false(record.get("included_in_build_allowed"), "planned_record.included_in_build_allowed")
        require_equal(record.get("validation_status"), "PENDING_DOWNLOAD_AND_VALIDATOR", "planned_record.validation_status")
        require_equal(record.get("provenance_status"), "PLACEHOLDER_ONLY", "planned_record.provenance_status")


def build_self_validator(
    generated_at_utc: str,
    approval: Dict[str, Any],
    manifest: Dict[str, Any],
    compliance: Dict[str, Any],
    symbol: Dict[str, Any],
    coverage: Dict[str, Any],
    provenance: Dict[str, Any],
) -> Dict[str, Any]:
    validate_placeholder_manifest(manifest)
    checks = {
        "approval_record_exists": bool(approval),
        "placeholder_manifest_exists_and_valid_json": bool(manifest),
        "compliance_report_exists_and_valid_json": bool(compliance),
        "symbol_universe_placeholder_exists": bool(symbol),
        "coverage_placeholder_exists": bool(coverage),
        "provenance_placeholder_exists": bool(provenance),
        "manifest_is_placeholder_only": manifest.get("manifest_is_placeholder_only") is True,
        "manifest_is_build_ready_false": manifest.get("manifest_is_build_ready") is False,
        "manifest_is_download_ready_false": manifest.get("manifest_is_download_ready") is False,
        "downloaded_file_count_zero": manifest.get("downloaded_file_count") == 0,
        "sha256_claim_count_zero": manifest.get("sha256_claim_count") == 0,
        "build_ready_file_count_zero": manifest.get("build_ready_file_count") == 0,
    }
    return {
        "generated_at_utc": generated_at_utc,
        **checks,
        "source_manifest_validated_as_placeholder": all(checks.values()),
        "source_manifest_safe_for_download_preview": True,
        "source_manifest_safe_for_data_build_now": False,
        "source_manifest_safe_for_acquisition_now": False,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 8,
        "replacement_checks_all_true": all(checks.values()),
    }


def build_artifacts() -> Dict[str, Dict[str, Any]]:
    generated_at_utc = utc_now()
    approval = build_approval_record(generated_at_utc)
    manifest = build_placeholder_manifest(generated_at_utc)
    symbol = build_symbol_universe_placeholder(generated_at_utc)
    coverage = build_coverage_placeholder(generated_at_utc)
    provenance = build_provenance_placeholder(generated_at_utc)
    compliance = build_compliance_report(generated_at_utc)
    self_validator = build_self_validator(generated_at_utc, approval, manifest, compliance, symbol, coverage, provenance)
    return {
        "approval_record": approval,
        "manifest": manifest,
        "symbol_universe_placeholder": symbol,
        "coverage_placeholder": coverage,
        "provenance_placeholder": provenance,
        "compliance_report": compliance,
        "self_validator": self_validator,
    }


def build_payload(preflight: Dict[str, Any], artifacts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    manifest = artifacts["manifest"]
    self_validator = artifacts["self_validator"]
    flags = dangerous_flags()
    replacement_checks = {
        "preflight_passed": preflight.get("whole_system_preflight_decision") == "PASS",
        "approval_record_created": True,
        "placeholder_manifest_created": True,
        "placeholder_manifest_self_validated": self_validator.get("source_manifest_validated_as_placeholder") is True,
        "no_downloaded_files": manifest.get("downloaded_file_count") == 0,
        "no_hash_claims": manifest.get("sha256_claim_count") == 0,
        "no_build_ready_files": manifest.get("build_ready_file_count") == 0,
        "not_acquisition_ready": manifest.get("acquisition_ready") is False,
        "schema_config_absent": planned_schema_files_existing_count() == 0,
        "generic_runner_absent": generic_runner_target_exists() is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
    }
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_source_manifest_bundle_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "PREVIEW_OKX_SYMBOL_UNIVERSE_COVERAGE_PROVENANCE_RESOLUTION_NO_DOWNLOAD_NO_API_NO_BUILD",
        "next_module": NEXT_MODULE_PASS,
        **preflight,
        "bounded_bundle_mode_used": True,
        "user_acceleration_decision_respected": True,
        "approval_record_created": True,
        "placeholder_manifest_created": True,
        "placeholder_manifest_self_validated": True,
        "source_manifest_created_now": True,
        "source_manifest_placeholder_only": True,
        "source_manifest_build_ready": False,
        "source_manifest_download_ready": False,
        "source_manifest_acquisition_ready": False,
        "downloaded_file_count": 0,
        "sha256_claim_count": 0,
        "build_ready_file_count": 0,
        "symbol_universe_resolved_now": False,
        "coverage_resolved_now": False,
        "provenance_resolved_now": False,
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
        "provenance_placeholders_created": True,
        "source_manifest_safe_for_download_preview": True,
        "source_manifest_safe_for_data_build_now": False,
        "source_manifest_safe_for_acquisition_now": False,
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
        "current_evidence_chain_quality_before_bundle": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_bundle": EVIDENCE_AFTER,
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
        "derived_live_repo_post_check": (
            "PASS_OKX_SOURCE_MANIFEST_PLACEHOLDER_BUNDLE_VALIDATED_SYMBOL_UNIVERSE_COVERAGE_"
            "PROVENANCE_RESOLUTION_PREVIEW_READY_NO_EXECUTION"
        ),
        "derived_live_repo_post_check_reason": (
            "repo-only bounded bundle created the approval record, placeholder source manifest, placeholder policy reports, "
            "compliance report, and self-validator; no files were downloaded, no hashes were claimed, no files were marked "
            "build-ready or acquisition-ready, and download/API/browse/data fetch/data build/aggregation/runtime/capital/live/"
            "generic-runner/schema/config paths remain blocked"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": all(replacement_checks.values()),
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "tracked_python_count_expectation": {
            "pre_commit": EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT,
        },
    }
    if payload["replacement_checks_all_true"] is not True:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: replacement checks failed")
    return payload


def write_bundle_artifacts(payload: Dict[str, Any], artifacts: Dict[str, Dict[str, Any]]) -> None:
    output_artifacts = {
        "historical_okx_source_manifest_approval_record.json": artifacts["approval_record"],
        "historical_okx_source_manifest.json": artifacts["manifest"],
        "historical_okx_source_manifest_contract_compliance_report.json": artifacts["compliance_report"],
        "historical_okx_symbol_universe_policy_placeholder_report.json": artifacts["symbol_universe_placeholder"],
        "historical_okx_coverage_policy_placeholder_report.json": artifacts["coverage_placeholder"],
        "historical_okx_provenance_placeholder_report.json": artifacts["provenance_placeholder"],
        "historical_okx_source_manifest_self_validator.json": artifacts["self_validator"],
        "historical_okx_source_manifest_bundle_summary.json": payload,
        "repo_only_historical_data_acquisition_okx_source_manifest_approval_after_preview_v1_latest.json": payload,
    }
    for name, artifact in output_artifacts.items():
        write_json(OUT_DIR / name, artifact)


def blocked_payload(exc: Exception) -> Dict[str, Any]:
    flags = dangerous_flags()
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_source_manifest_bundle_status": STATUS_BLOCKED_CONTEXT,
        "final_decision": STATUS_BLOCKED_CONTEXT,
        "next_action": "STOP_FAIL_CLOSED_NO_MANIFEST_BUNDLE_NO_DOWNLOAD_NO_API_NO_BUILD",
        "next_module": NEXT_MODULE_BLOCKED,
        "error": str(exc),
        "whole_system_preflight_completed": False,
        "live_next_module_matches_requested_module": False,
        "artifact_chain_consistent": False,
        "stale_or_contradictory_artifact_detected": True,
        "bounded_bundle_mode_used": True,
        "active_p0_blocker_count": 1,
        "source_manifest_created_now": False,
        "source_manifest_build_ready": False,
        "source_manifest_download_ready": False,
        "source_manifest_acquisition_ready": False,
        "downloaded_file_count": 0,
        "sha256_claim_count": 0,
        "build_ready_file_count": 0,
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
        "dangerous_flags": flags,
        "dangerous_flags_all_false": True,
        "dangerous_flags_true_count": 0,
    }


def main() -> int:
    try:
        preview = load_json(PREVIEW_ARTIFACT, "source manifest preview artifact")
        policy_validator = load_json(AGGREGATION_POLICY_VALIDATOR_ARTIFACT, "aggregation policy validator artifact")
        policy = load_json(AGGREGATION_POLICY_ARTIFACT, "aggregation policy artifact")
        metadata_validator = load_json(METADATA_VALIDATOR_ARTIFACT, "metadata validator artifact")
        source_identity_validator = load_json(SOURCE_IDENTITY_VALIDATOR_ARTIFACT, "source identity validator artifact")
        preflight = validate_preflight(preview, policy_validator, policy, metadata_validator, source_identity_validator)
        artifacts = build_artifacts()
        payload = build_payload(preflight, artifacts)
        write_bundle_artifacts(payload, artifacts)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        payload = blocked_payload(exc)
        write_json(OUT_DIR / "repo_only_historical_data_acquisition_okx_source_manifest_approval_after_preview_v1_latest.json", payload)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
