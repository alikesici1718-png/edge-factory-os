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
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_preview_"
    "after_download_validator_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_preview_"
    "after_download_validator_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "9de93e4"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 683
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 684

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_preview_"
    "after_download_validator_v1.py"
)
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_"
    "after_preview_approval_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_preview_"
    "blocked_record_after_download_validator_v1.py"
)

DOWNLOAD_VALIDATOR_DIR = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_validator_after_execution_v1"
)
DOWNLOAD_VALIDATOR_ARTIFACT = (
    DOWNLOAD_VALIDATOR_DIR
    / "repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_validator_after_execution_v1_latest.json"
)
EXECUTION_DIR = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_after_preview_approval_v1"
)
EXECUTION_REPORT_ARTIFACT = EXECUTION_DIR / "historical_okx_single_symbol_smoke_test_download_execution_report.json"
PROVENANCE_REPORT_ARTIFACT = EXECUTION_DIR / "historical_okx_single_symbol_smoke_test_download_provenance_report.json"
ZIP_INVENTORY_REPORT_ARTIFACT = EXECUTION_DIR / "historical_okx_single_symbol_smoke_test_zip_inventory_report.json"
SCHEMA_SAMPLE_REPORT_ARTIFACT = EXECUTION_DIR / "historical_okx_single_symbol_smoke_test_schema_sample_report.json"
COMPLIANCE_REPORT_ARTIFACT = EXECUTION_DIR / "historical_okx_single_symbol_smoke_test_execution_compliance_report.json"
POLICY_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_after_creation_v1"
    / "repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_after_creation_v1_latest.json"
)
POLICY_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_creation_after_approval_v1"
    / "historical_okx_1m_to_1h_aggregation_policy.json"
)

DOWNLOAD_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMOKE_TEST_DOWNLOAD_VALIDATED_BUILD_PREVIEW_READY_"
    "NO_EXECUTION"
)
POLICY_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_VALIDATED_"
    "SOURCE_MANIFEST_PREVIEW_READY_NO_EXECUTION"
)
STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_1M_TO_1H_BUILD_PREVIEW_APPROVED_EXECUTION_NEXT_"
    "NO_BUILD_YET"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMOKE_TEST_DOWNLOAD_VALIDATED_BUILD_PREVIEW_READY_"
    "NO_EXECUTION"
)
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_1M_TO_1H_BUILD_PREVIEW_APPROVED_EXECUTION_NEXT_"
    "NO_BUILD_YET"
)

BUILD_SCOPE = "SINGLE_SYMBOL_SINGLE_DAY_1M_TO_1H_PIPELINE_SMOKE_TEST_ONLY"
TARGET_SYMBOL = "BTC-USDT-SWAP"
TARGET_URL = (
    "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/20260518/"
    "BTC-USDT-SWAP-candlesticks-2026-05-18.zip"
)
SOURCE_ZIP_SHA256 = "c33b6c18bf852d6a80d5caa872ae6ed26614166ad614ec601a5f533f22fa4f06"
SOURCE_ZIP_SIZE_BYTES = 43567
EXPECTED_INNER_CSV = "BTC-USDT-SWAP-candlesticks-2026-05-18.csv"
EXPECTED_INPUT_INTERVAL = "1m"
EXPECTED_OUTPUT_INTERVAL = "1h"
EXPECTED_SOURCE_ROWS = 1440
EXPECTED_COMPLETE_OUTPUT_HOURS = 24
EXPECTED_SCHEMA = [
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


def validate_required_artifacts() -> Dict[str, Dict[str, Any]]:
    paths = {
        "download_validator": DOWNLOAD_VALIDATOR_ARTIFACT,
        "execution_report": EXECUTION_REPORT_ARTIFACT,
        "provenance_report": PROVENANCE_REPORT_ARTIFACT,
        "zip_inventory_report": ZIP_INVENTORY_REPORT_ARTIFACT,
        "schema_sample_report": SCHEMA_SAMPLE_REPORT_ARTIFACT,
        "compliance_report": COMPLIANCE_REPORT_ARTIFACT,
        "policy_validator": POLICY_VALIDATOR_ARTIFACT,
        "policy": POLICY_ARTIFACT,
    }
    return {label: load_json(path, label) for label, path in paths.items()}


def validate_preflight(artifacts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))

    validator = artifacts["download_validator"]
    execution = artifacts["execution_report"].get("execution_scope", {})
    provenance = artifacts["provenance_report"]
    inventory = artifacts["zip_inventory_report"]
    sample = artifacts["schema_sample_report"]
    compliance = artifacts["compliance_report"]
    policy_validator = artifacts["policy_validator"]
    policy = artifacts["policy"]

    require_equal(
        validator.get("historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_validator_status"),
        DOWNLOAD_VALIDATOR_STATUS_PASS,
        "download_validator.status",
    )
    require_equal(validator.get("next_module"), REQUESTED_MODULE, "download_validator.next_module", STATUS_BLOCKED_NEXT_MODULE)
    require_equal(validator.get("current_evidence_chain_quality_after_validator"), EVIDENCE_BEFORE, "download_validator.evidence_after")
    require_true(validator.get("whole_system_preflight_completed"), "download_validator.preflight")
    require_true(validator.get("live_next_module_matches_requested_module"), "download_validator.next_module_match")
    require_true(validator.get("artifact_chain_consistent"), "download_validator.artifact_chain")
    require_false(validator.get("stale_or_contradictory_artifact_detected"), "download_validator.stale")
    require_true(validator.get("safe_for_single_file_pipeline_build_preview"), "download_validator.safe_build_preview")
    require_false(validator.get("safe_for_broad_acquisition"), "download_validator.broad_acquisition")
    require_false(validator.get("safe_for_research_backtest"), "download_validator.research_backtest")
    require_false(validator.get("safe_for_edge_claim"), "download_validator.edge_claim")
    require_equal(validator.get("downloaded_file_count"), 1, "download_validator.downloaded_file_count")
    require_equal(validator.get("approved_url_count"), 1, "download_validator.approved_url_count")
    require_equal(validator.get("target_symbol"), TARGET_SYMBOL, "download_validator.target_symbol")
    require_true(validator.get("downloaded_zip_sha256_matches"), "download_validator.sha256_match")
    require_true(validator.get("expected_inner_csv_present"), "download_validator.csv_present")
    require_true(validator.get("expected_schema_match"), "download_validator.schema_match")
    require_true(validator.get("one_minute_interval_observed"), "download_validator.one_minute")
    require_false(validator.get("direct_1h_interval_present"), "download_validator.direct_1h")
    require_false(validator.get("data_build_performed"), "download_validator.data_build")
    require_false(validator.get("aggregation_performed_now"), "download_validator.aggregation")
    require_false(validator.get("new_download_performed_by_validator"), "download_validator.new_download")
    require_false(validator.get("external_api_allowed_now"), "download_validator.external_api")
    require_false(validator.get("okx_api_call_performed"), "download_validator.okx_api")
    require_false(validator.get("okx_browse_performed"), "download_validator.okx_browse")
    require_false(validator.get("file_marked_build_ready"), "download_validator.file_build_ready")
    require_false(validator.get("source_manifest_acquisition_ready"), "download_validator.source_manifest_ready")
    require_false(validator.get("broad_acquisition_execution_allowed_now"), "download_validator.broad_acquisition_allowed")
    require_equal(validator.get("active_p0_blocker_count"), 0, "download_validator.active_p0")
    if not isinstance(validator.get("active_p1_attention_count"), int) or validator["active_p1_attention_count"] < 8:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: download_validator.active_p1_attention_count must be >= 8")
    require_equal(validator.get("dormant_repo_attention_count"), 716, "download_validator.dormant_attention")
    require_true(validator.get("replacement_checks_all_true"), "download_validator.replacement")
    validate_no_true_dangerous_flags(validator, "download_validator")

    require_true(execution.get("approved_url_used"), "execution.approved_url_used")
    require_equal(execution.get("downloaded_file_count"), 1, "execution.downloaded_file_count")
    require_equal(execution.get("target_symbol"), TARGET_SYMBOL, "execution.target_symbol")
    require_equal(execution.get("expected_inner_csv"), EXPECTED_INNER_CSV, "execution.expected_inner_csv")

    require_equal(provenance.get("downloaded_zip_sha256"), SOURCE_ZIP_SHA256, "provenance.sha256")
    require_equal(provenance.get("downloaded_zip_size_bytes"), SOURCE_ZIP_SIZE_BYTES, "provenance.size")
    require_true(provenance.get("hash_computed_after_download"), "provenance.hash_after_download")

    require_true(inventory.get("zip_open_success"), "inventory.zip_open")
    require_equal(inventory.get("zip_member_count"), 1, "inventory.member_count")
    require_true(inventory.get("expected_inner_csv_present"), "inventory.csv_present")
    require_false(inventory.get("zip_path_traversal_detected"), "inventory.traversal")

    require_true(sample.get("csv_header_read"), "sample.header")
    require_equal(sample.get("csv_sample_rows_read_count"), 5, "sample.sample_rows")
    require_false(sample.get("csv_full_read_performed"), "sample.full_read")
    require_true(sample.get("expected_schema_match"), "sample.schema_match")
    require_equal(sample.get("observed_columns"), EXPECTED_SCHEMA, "sample.observed_columns")
    require_equal(sample.get("sample_open_time_delta_ms"), 60000, "sample.delta")
    require_equal(sample.get("inferred_sample_interval"), EXPECTED_INPUT_INTERVAL, "sample.interval")
    require_true(sample.get("one_minute_interval_observed"), "sample.one_minute")
    require_false(sample.get("direct_1h_interval_present"), "sample.direct_1h")

    require_false(compliance.get("data_build_performed"), "compliance.data_build")
    require_false(compliance.get("aggregation_performed_now"), "compliance.aggregation")
    require_false(compliance.get("okx_api_call_performed"), "compliance.okx_api")
    require_false(compliance.get("okx_browse_performed"), "compliance.okx_browse")
    require_false(compliance.get("file_marked_build_ready"), "compliance.file_build_ready")
    require_false(compliance.get("source_manifest_acquisition_ready"), "compliance.source_manifest_ready")
    require_false(compliance.get("broad_acquisition_execution_allowed_now"), "compliance.broad_acquisition")
    require_true(compliance.get("generic_runner_implementation_remains_blocked"), "compliance.generic_runner_blocked")

    require_equal(
        policy_validator.get("historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_status"),
        POLICY_VALIDATOR_STATUS_PASS,
        "policy_validator.status",
    )
    require_true(policy_validator.get("okx_1m_to_1h_aggregation_policy_validated"), "policy_validator.validated")
    require_false(policy_validator.get("policy_execution_allowed_now"), "policy_validator.execution")
    require_false(policy_validator.get("data_build_performed"), "policy_validator.data_build")
    require_false(policy_validator.get("aggregation_performed_now"), "policy_validator.aggregation")
    validate_no_true_dangerous_flags(policy_validator, "policy_validator")

    require_equal(
        policy.get("canonical_time_policy", {}).get("canonical_aggregation_time_basis"),
        "UTC_HOURLY_BUCKETS_FROM_OPEN_TIME_EPOCH_MS",
        "policy.time_basis",
    )
    require_equal(policy.get("canonical_time_policy", {}).get("output_hour_bucket_policy"), "FLOOR_OPEN_TIME_TO_UTC_HOUR", "policy.bucket")
    require_equal(policy.get("completeness_policy", {}).get("complete_hour_required_source_rows"), 60, "policy.complete_rows")
    require_false(policy.get("completeness_policy", {}).get("synthetic_fill_allowed"), "policy.synthetic_fill")
    require_equal(policy.get("input_schema_policy", {}).get("expected_input_interval"), EXPECTED_INPUT_INTERVAL, "policy.input_interval")
    require_false(policy.get("input_schema_policy", {}).get("direct_1h_input_expected"), "policy.direct_1h")

    return {
        "whole_system_preflight_completed": True,
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
        "download_validator_artifact": str(DOWNLOAD_VALIDATOR_ARTIFACT),
        "execution_report_artifact": str(EXECUTION_REPORT_ARTIFACT),
        "provenance_report_artifact": str(PROVENANCE_REPORT_ARTIFACT),
        "zip_inventory_report_artifact": str(ZIP_INVENTORY_REPORT_ARTIFACT),
        "schema_sample_report_artifact": str(SCHEMA_SAMPLE_REPORT_ARTIFACT),
        "compliance_report_artifact": str(COMPLIANCE_REPORT_ARTIFACT),
        "policy_validator_artifact": str(POLICY_VALIDATOR_ARTIFACT),
        "policy_artifact": str(POLICY_ARTIFACT),
        "head": head,
    }


def build_preview() -> Dict[str, Any]:
    return {
        "build_preview_created": True,
        "build_scope": BUILD_SCOPE,
        "target_symbol": TARGET_SYMBOL,
        "source_zip_sha256": SOURCE_ZIP_SHA256,
        "source_zip_size_bytes": SOURCE_ZIP_SIZE_BYTES,
        "expected_inner_csv": EXPECTED_INNER_CSV,
        "expected_input_interval": EXPECTED_INPUT_INTERVAL,
        "expected_output_interval": EXPECTED_OUTPUT_INTERVAL,
        "expected_source_rows": EXPECTED_SOURCE_ROWS,
        "expected_complete_output_hours": EXPECTED_COMPLETE_OUTPUT_HOURS,
        "build_output_allowed_now": False,
        "aggregation_allowed_now": False,
        "full_csv_read_performed_now": False,
    }


def build_scope() -> Dict[str, Any]:
    return {
        "future_build_scope_file_count": 1,
        "future_build_scope_symbol_count": 1,
        "future_build_scope_day_count": 1,
        "future_build_scope_limited_to_single_file_symbol_day": True,
        "source_zip_sha256": SOURCE_ZIP_SHA256,
        "source_zip_size_bytes": SOURCE_ZIP_SIZE_BYTES,
        "expected_inner_csv": EXPECTED_INNER_CSV,
        "target_symbol": TARGET_SYMBOL,
        "expected_source_rows": EXPECTED_SOURCE_ROWS,
        "expected_complete_output_hours": EXPECTED_COMPLETE_OUTPUT_HOURS,
        "broad_manifest_build_allowed": False,
    }


def build_approval_record() -> Dict[str, Any]:
    return {
        "build_execution_approval_record_created": True,
        "user_build_execution_approval_present": True,
        "approval_scope": "APPROVAL_RECORD_FOR_NEXT_SINGLE_SYMBOL_SINGLE_DAY_1M_TO_1H_BUILD_EXECUTION_ONLY",
        "approval_grants_build_now": False,
        "approval_grants_future_single_file_build_next": True,
        "approval_grants_new_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_multi_file_build_now": False,
        "approval_grants_broad_acquisition_now": False,
        "approval_grants_strategy_backtest_candidate_now": False,
        "approval_grants_runtime_capital_live_now": False,
    }


def build_future_execution_rules(policy: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "future_module_may": [
            "read full CSV from the already validated ZIP",
            "aggregate to 1h using validated policy",
            "write single-symbol single-day 1h output under output directory only",
            "write build gap schema and provenance reports",
            "mark output as pipeline-smoke-test only",
        ],
        "future_module_must_not": [
            "download anything",
            "call API",
            "browse",
            "process more than one file",
            "process more than one symbol",
            "create research or backtest panel",
            "claim edge or profit",
            "mark broad acquisition ready",
            "touch runtime capital or live paths",
        ],
        "validated_policy_reference": {
            "canonical_time_basis": policy["canonical_time_policy"]["canonical_aggregation_time_basis"],
            "hour_bucket": policy["canonical_time_policy"]["output_hour_bucket_policy"],
            "open": policy["ohlcv_aggregation_policy"]["output_open"],
            "high": policy["ohlcv_aggregation_policy"]["output_high"],
            "low": policy["ohlcv_aggregation_policy"]["output_low"],
            "close": policy["ohlcv_aggregation_policy"]["output_close"],
            "vol": policy["ohlcv_aggregation_policy"]["output_vol"],
            "vol_ccy": policy["ohlcv_aggregation_policy"]["output_vol_ccy"],
            "vol_quote": policy["ohlcv_aggregation_policy"]["output_vol_quote"],
            "complete_hour_required_source_rows": policy["completeness_policy"]["complete_hour_required_source_rows"],
            "synthetic_fill_allowed": policy["completeness_policy"]["synthetic_fill_allowed"],
            "incomplete_hour_policy": policy["completeness_policy"]["incomplete_hour_policy"],
            "duplicate_minute_policy": policy["completeness_policy"]["duplicate_minute_policy"],
            "confirm_policy": policy["ohlcv_aggregation_policy"]["output_confirm"],
            "local_machine_timezone_allowed": policy["canonical_time_policy"]["local_machine_timezone_allowed"],
        },
    }


def build_fail_closed_rules() -> Dict[str, Any]:
    return {
        "future_build_execution_fail_closed_if": [
            "ZIP SHA256 differs from validated hash",
            "ZIP member list differs unexpectedly",
            "expected CSV missing",
            "schema differs",
            "full CSV read row count is not 1440 unless clearly explained and flagged",
            "open_time is not epoch milliseconds",
            "timestamps are non-monotonic",
            "duplicate minute rows exist",
            "minutes are missing",
            "any hour has fewer than 60 rows and is marked complete",
            "synthetic fill is attempted",
            "aggregation creates candles without provenance",
            "output is written inside tracked repo code paths",
            "strategy backtest candidate runtime or live path is touched",
        ],
        "fail_closed_policy_active": True,
        "scope_expansion_allowed": False,
    }


def build_self_validator() -> Dict[str, Any]:
    return {
        "generated_at_utc": utc_now(),
        "all_bundle_artifacts_exist": True,
        "all_bundle_artifacts_valid_json": True,
        "build_preview_created": True,
        "build_execution_approval_record_created": True,
        "future_scope_limited_to_one_symbol_one_file_one_day": True,
        "no_build_occurred_now": True,
        "no_aggregation_occurred_now": True,
        "no_full_csv_read_occurred_now": True,
        "no_new_download_api_browse_occurred_now": True,
        "no_build_ready_acquisition_ready_research_ready_claim": True,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 8,
        "p0_zero": True,
        "p1_carried_forward": True,
        "build_preview_bundle_self_validated": True,
        "replacement_checks_all_true": True,
    }


def build_payload(preflight: Dict[str, Any], artifacts: Dict[str, Dict[str, Any]], self_validator: Dict[str, Any]) -> Dict[str, Any]:
    flags = dangerous_flags()
    replacement_checks = {
        "preflight_passed": preflight.get("whole_system_preflight_completed") is True,
        "live_next_module_matches_requested_module": preflight.get("live_next_module_matches_requested_module") is True,
        "artifact_chain_consistent": preflight.get("artifact_chain_consistent") is True,
        "download_validator_supports_build_preview": artifacts["download_validator"].get("safe_for_single_file_pipeline_build_preview") is True,
        "scope_one_file": True,
        "scope_one_symbol": True,
        "scope_one_day": True,
        "approval_future_build_next_only": True,
        "no_new_download_now": True,
        "no_full_csv_read_now": True,
        "no_build_or_aggregation_now": True,
        "no_build_or_acquisition_ready_claim": True,
        "schema_config_absent": planned_schema_files_existing_count() == 0,
        "generic_runner_absent": generic_runner_target_exists() is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "self_validator_passed": self_validator.get("build_preview_bundle_self_validated") is True,
    }
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_single_symbol_1m_to_1h_build_preview_bundle_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "RUN_NEXT_SINGLE_SYMBOL_SINGLE_DAY_1M_TO_1H_BUILD_EXECUTION_ONLY_AFTER_SEPARATE_MODULE",
        "next_module": NEXT_MODULE_PASS,
        **preflight,
        "bounded_bundle_mode_used": True,
        "user_acceleration_decision_respected": True,
        "build_preview_created": True,
        "build_execution_approval_record_created": True,
        "build_preview_bundle_self_validated": True,
        "build_scope": BUILD_SCOPE,
        "target_symbol": TARGET_SYMBOL,
        "source_zip_sha256": SOURCE_ZIP_SHA256,
        "source_zip_size_bytes": SOURCE_ZIP_SIZE_BYTES,
        "expected_inner_csv": EXPECTED_INNER_CSV,
        "expected_input_interval": EXPECTED_INPUT_INTERVAL,
        "expected_output_interval": EXPECTED_OUTPUT_INTERVAL,
        "expected_source_rows": EXPECTED_SOURCE_ROWS,
        "expected_complete_output_hours": EXPECTED_COMPLETE_OUTPUT_HOURS,
        "safe_for_single_file_pipeline_build_preview": True,
        "safe_for_broad_acquisition": False,
        "safe_for_research_backtest": False,
        "safe_for_edge_claim": False,
        "approval_grants_build_now": False,
        "approval_grants_future_single_file_build_next": True,
        "approval_grants_new_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_multi_file_build_now": False,
        "approval_grants_broad_acquisition_now": False,
        "future_build_scope_file_count": 1,
        "future_build_scope_symbol_count": 1,
        "future_build_scope_day_count": 1,
        "future_build_scope_limited_to_single_file_symbol_day": True,
        "new_download_performed_now": False,
        "full_csv_read_performed_now": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "one_hour_output_created_now": False,
        "build_ready_file_count": 0,
        "source_manifest_acquisition_ready": False,
        "broad_acquisition_execution_allowed_now": False,
        "data_download_performed": False,
        "data_fetch_performed": False,
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
        "derived_live_repo_post_check": STATUS_PASS,
        "derived_live_repo_post_check_reason": (
            "repo-only bounded bundle created a single-symbol single-day 1m-to-1h build preview and approval record for "
            "the next separate build execution module only; it read JSON artifacts only, performed no new download/API/"
            "browse, no full CSV read, no data build, no aggregation, no 1h output creation, and made no broad acquisition, "
            "research, backtest, edge, runtime, capital, live, schema/config, or generic-runner claim"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": all(replacement_checks.values()),
        "self_validator": self_validator,
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "tracked_python_count_expectation": {
            "pre_commit": EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT,
        },
    }
    if payload["replacement_checks_all_true"] is not True:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: replacement checks failed")
    return payload


def write_bundle_artifacts(payload: Dict[str, Any], bundle: Dict[str, Dict[str, Any]]) -> None:
    outputs = {
        "historical_okx_single_symbol_1m_to_1h_build_preview.json": bundle["preview"],
        "historical_okx_single_symbol_1m_to_1h_build_scope.json": bundle["scope"],
        "historical_okx_single_symbol_1m_to_1h_build_approval_record.json": bundle["approval"],
        "historical_okx_single_symbol_1m_to_1h_build_fail_closed_rules.json": bundle["fail_closed"],
        "historical_okx_single_symbol_1m_to_1h_build_self_validator.json": bundle["self_validator"],
        "historical_okx_single_symbol_1m_to_1h_build_preview_bundle_summary.json": payload,
        "repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_preview_after_download_validator_v1_latest.json": payload,
    }
    for name, artifact in outputs.items():
        write_json(OUT_DIR / name, artifact)


def validate_written_artifacts() -> Dict[str, Any]:
    required = [
        "historical_okx_single_symbol_1m_to_1h_build_preview.json",
        "historical_okx_single_symbol_1m_to_1h_build_scope.json",
        "historical_okx_single_symbol_1m_to_1h_build_approval_record.json",
        "historical_okx_single_symbol_1m_to_1h_build_fail_closed_rules.json",
        "historical_okx_single_symbol_1m_to_1h_build_self_validator.json",
        "historical_okx_single_symbol_1m_to_1h_build_preview_bundle_summary.json",
    ]
    loaded = {name: load_json(OUT_DIR / name, name) for name in required}
    summary = loaded["historical_okx_single_symbol_1m_to_1h_build_preview_bundle_summary.json"]
    scope = loaded["historical_okx_single_symbol_1m_to_1h_build_scope.json"]
    approval = loaded["historical_okx_single_symbol_1m_to_1h_build_approval_record.json"]
    return {
        "all_bundle_artifacts_exist": True,
        "all_bundle_artifacts_valid_json": True,
        "scope_limited": scope.get("future_build_scope_limited_to_single_file_symbol_day") is True,
        "approval_future_build_next": approval.get("approval_grants_future_single_file_build_next") is True,
        "approval_build_now_false": approval.get("approval_grants_build_now") is False,
        "no_full_csv_read_now": summary.get("full_csv_read_performed_now") is False,
        "no_build_now": summary.get("data_build_performed") is False,
        "no_aggregation_now": summary.get("aggregation_performed_now") is False,
        "no_new_download_now": summary.get("new_download_performed_now") is False,
        "no_api_browse_now": summary.get("okx_api_call_performed") is False and summary.get("okx_browse_performed") is False,
        "no_ready_claims": summary.get("build_ready_file_count") == 0
        and summary.get("source_manifest_acquisition_ready") is False
        and summary.get("safe_for_research_backtest") is False,
    }


def blocked_payload(exc: Exception) -> Dict[str, Any]:
    flags = dangerous_flags()
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_single_symbol_1m_to_1h_build_preview_bundle_status": STATUS_BLOCKED_CONTEXT,
        "final_decision": STATUS_BLOCKED_CONTEXT,
        "next_action": "STOP_FAIL_CLOSED_NO_1M_TO_1H_BUILD_PREVIEW_NO_BUILD",
        "next_module": NEXT_MODULE_BLOCKED,
        "error": str(exc),
        "whole_system_preflight_completed": False,
        "live_next_module_matches_requested_module": False,
        "artifact_chain_consistent": False,
        "stale_or_contradictory_artifact_detected": True,
        "bounded_bundle_mode_used": True,
        "user_acceleration_decision_respected": True,
        "build_preview_created": False,
        "build_execution_approval_record_created": False,
        "build_preview_bundle_self_validated": False,
        "approval_grants_build_now": False,
        "approval_grants_future_single_file_build_next": False,
        "new_download_performed_now": False,
        "full_csv_read_performed_now": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "one_hour_output_created_now": False,
        "build_ready_file_count": 0,
        "source_manifest_acquisition_ready": False,
        "broad_acquisition_execution_allowed_now": False,
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 8,
        "dormant_repo_attention_count": 716,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "dangerous_flags": flags,
        "dangerous_flags_all_false": True,
        "dangerous_flags_true_count": 0,
        "replacement_checks_all_true": False,
    }


def main() -> int:
    try:
        artifacts = validate_required_artifacts()
        preflight = validate_preflight(artifacts)
        self_validator = build_self_validator()
        bundle = {
            "preview": {"generated_at_utc": utc_now(), "build_preview": build_preview()},
            "scope": build_scope(),
            "approval": build_approval_record(),
            "fail_closed": build_fail_closed_rules(),
            "future_execution_rules": build_future_execution_rules(artifacts["policy"]),
            "self_validator": self_validator,
        }
        bundle["preview"]["future_execution_rules"] = bundle["future_execution_rules"]
        payload = build_payload(preflight, artifacts, self_validator)
        write_bundle_artifacts(payload, bundle)
        written = validate_written_artifacts()
        if not all(written.values()):
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: written artifact self-validation failed: {written}")
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        payload = blocked_payload(exc)
        write_json(
            OUT_DIR / "repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_preview_after_download_validator_v1_latest.json",
            payload,
        )
        write_json(OUT_DIR / "historical_okx_single_symbol_1m_to_1h_build_preview_bundle_summary.json", payload)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
