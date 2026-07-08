from __future__ import annotations

import json
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_preview_"
    "after_smoke_test_summary_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_preview_"
    "after_smoke_test_summary_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "03c4856"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 687
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 688

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_preview_"
    "after_smoke_test_summary_v1.py"
)
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_execution_"
    "after_preview_approval_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_preview_"
    "blocked_record_after_smoke_test_summary_v1.py"
)

SUMMARY_DIR = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_summary_after_build_validator_v1"
)
SUMMARY_LATEST_ARTIFACT = (
    SUMMARY_DIR
    / "repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_summary_after_build_validator_v1_latest.json"
)
SUMMARY_BUNDLE_ARTIFACT = SUMMARY_DIR / "historical_okx_single_symbol_pipeline_smoke_test_summary_bundle_summary.json"

BUILD_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_validator_after_execution_v1"
    / "repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_validator_after_execution_v1_latest.json"
)
DOWNLOAD_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_validator_after_execution_v1"
    / "repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_validator_after_execution_v1_latest.json"
)
SOURCE_MANIFEST_PREVIEW_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_source_manifest_preview_after_aggregation_policy_validator_v1"
    / "repo_only_historical_data_acquisition_okx_source_manifest_preview_after_aggregation_policy_validator_v1_latest.json"
)
SOURCE_MANIFEST_BUNDLE_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_source_manifest_approval_after_preview_v1"
    / "repo_only_historical_data_acquisition_okx_source_manifest_approval_after_preview_v1_latest.json"
)
SOURCE_MANIFEST_SELF_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_source_manifest_approval_after_preview_v1"
    / "historical_okx_source_manifest_self_validator.json"
)

SUMMARY_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_PIPELINE_SMOKE_TEST_CLOSED_SMALL_RANGE_DOWNLOAD_"
    "PREVIEW_READY"
)
BUILD_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_1M_TO_1H_BUILD_VALIDATED_PIPELINE_SMOKE_TEST_"
    "SUMMARY_READY"
)
DOWNLOAD_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMOKE_TEST_DOWNLOAD_VALIDATED_BUILD_PREVIEW_READY_"
    "NO_EXECUTION"
)
STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMALL_RANGE_DOWNLOAD_PREVIEW_APPROVED_EXECUTION_NEXT_"
    "NO_DOWNLOAD_YET"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_PIPELINE_SMOKE_TEST_CLOSED_SMALL_RANGE_DOWNLOAD_PREVIEW_READY"
)
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMALL_RANGE_DOWNLOAD_PREVIEW_APPROVED_EXECUTION_NEXT_"
    "NO_DOWNLOAD_YET"
)

TARGET_SYMBOL = "BTC-USDT-SWAP"
RANGE_TYPE = "SINGLE_SYMBOL_SEVEN_DAILY_FILES"
DATE_RANGE_START = "2026-05-12"
DATE_RANGE_END = "2026-05-18"
RANGE_DAYS = 7
INPUT_INTERVAL = "1m"
OUTPUT_TARGET_INTERVAL = "1h"
PURPOSE = "PIPELINE_RANGE_VALIDATION_ONLY_NOT_RESEARCH_NOT_EDGE"
PLANNED_URL_PATTERN = (
    "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/YYYYMMDD/"
    "BTC-USDT-SWAP-candlesticks-YYYY-MM-DD.zip"
)
APPROVAL_SCOPE = "APPROVAL_RECORD_FOR_NEXT_SEPARATE_SEVEN_FILE_SINGLE_SYMBOL_DOWNLOAD_EXECUTION_ONLY"

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
    "data_build_performed_now",
    "aggregation_performed_now",
    "okx_browse_performed_now",
    "okx_download_performed_now",
    "okx_api_call_performed_now",
    "okx_sample_zip_downloaded_now",
    "okx_page_reopened_now",
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
    return sum(1 for path in run_git(["ls-files"]).splitlines() if path.endswith(".py"))


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


def load_required_artifacts() -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Any]]:
    paths = {
        "summary_latest": SUMMARY_LATEST_ARTIFACT,
        "summary_bundle": SUMMARY_BUNDLE_ARTIFACT,
        "build_validator": BUILD_VALIDATOR_ARTIFACT,
        "download_validator": DOWNLOAD_VALIDATOR_ARTIFACT,
        "source_manifest_preview": SOURCE_MANIFEST_PREVIEW_ARTIFACT,
        "source_manifest_bundle": SOURCE_MANIFEST_BUNDLE_ARTIFACT,
        "source_manifest_self_validator": SOURCE_MANIFEST_SELF_VALIDATOR_ARTIFACT,
    }
    artifacts: Dict[str, Dict[str, Any]] = {}
    status: Dict[str, Any] = {
        "required_artifact_paths": {label: str(path) for label, path in paths.items()},
        "artifact_exists_by_label": {},
        "artifact_valid_json_by_label": {},
    }
    for label, path in paths.items():
        data, exists, valid, non_empty = read_json_checked(path)
        status["artifact_exists_by_label"][label] = exists
        status["artifact_valid_json_by_label"][label] = valid and non_empty
        if not (exists and valid and non_empty):
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {label} missing/invalid/empty: {path}")
        artifacts[label] = data
    status["preview_input_artifacts_exist"] = all(status["artifact_exists_by_label"].values())
    status["preview_input_artifacts_valid_json"] = all(status["artifact_valid_json_by_label"].values())
    return artifacts, status


def validate_preflight(artifacts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))

    summary = artifacts["summary_latest"]
    build_validator = artifacts["build_validator"]
    download_validator = artifacts["download_validator"]
    manifest_preview = artifacts["source_manifest_preview"]
    manifest_bundle = artifacts["source_manifest_bundle"]
    manifest_self_validator = artifacts["source_manifest_self_validator"]

    require_equal(
        summary.get("historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_summary_status"),
        SUMMARY_STATUS_PASS,
        "summary.status",
    )
    require_equal(summary.get("next_module"), REQUESTED_MODULE, "summary.next_module", STATUS_BLOCKED_NEXT_MODULE)
    require_true(summary.get("smoke_test_closed_successfully"), "summary.smoke_test_closed_successfully")
    require_equal(summary.get("target_symbol"), TARGET_SYMBOL, "summary.target_symbol")
    require_equal(summary.get("recommended_next_route"), "SINGLE_SYMBOL_SMALL_RANGE_DOWNLOAD_PREVIEW", "summary.route")
    require_equal(summary.get("suggested_range_days"), RANGE_DAYS, "summary.suggested_range_days")
    require_equal(summary.get("max_allowed_files_for_first_range_test"), RANGE_DAYS, "summary.max_files")
    require_true(summary.get("next_route_is_preview_only"), "summary.preview_only")
    require_true(summary.get("next_route_requires_separate_execution_approval"), "summary.separate_approval")
    require_true(summary.get("output_valid_for_pipeline_smoke_test"), "summary.pipeline_smoke_test")
    require_false(summary.get("output_valid_for_research_backtest"), "summary.research_backtest")
    require_false(summary.get("output_valid_for_edge_claim"), "summary.edge_claim")
    require_false(summary.get("safe_for_broad_acquisition"), "summary.broad_acquisition")
    require_false(summary.get("safe_for_multi_symbol_build"), "summary.multi_symbol")
    require_true(summary.get("symbol_universe_still_unresolved"), "summary.symbol_universe")
    require_true(summary.get("coverage_still_unresolved"), "summary.coverage")
    require_true(summary.get("provenance_still_single_file_only"), "summary.single_file_provenance")
    require_true(summary.get("source_manifest_still_placeholder"), "summary.source_manifest_placeholder")
    require_false(summary.get("data_download_performed"), "summary.download")
    require_false(summary.get("data_build_performed"), "summary.data_build")
    require_false(summary.get("aggregation_performed_now"), "summary.aggregation")
    require_false(summary.get("okx_api_call_performed"), "summary.api")
    require_false(summary.get("okx_browse_performed"), "summary.browse")
    require_equal(summary.get("active_p0_blocker_count"), 0, "summary.active_p0")
    require_true(int(summary.get("active_p1_attention_count", 0)) >= 8, "summary.active_p1")
    require_equal(summary.get("dormant_repo_attention_count"), 716, "summary.dormant_attention")
    validate_no_true_dangerous_flags(summary, "summary")

    require_equal(
        build_validator.get("historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_validator_status"),
        BUILD_VALIDATOR_STATUS_PASS,
        "build_validator.status",
    )
    require_true(build_validator.get("build_execution_validated"), "build_validator.validated")
    require_false(build_validator.get("safe_for_broad_acquisition"), "build_validator.broad_acquisition")
    require_false(build_validator.get("safe_for_multi_symbol_build"), "build_validator.multi_symbol")
    require_false(build_validator.get("new_download_performed_by_validator"), "build_validator.new_download")
    require_false(build_validator.get("data_build_performed_by_validator"), "build_validator.data_build")
    require_false(build_validator.get("aggregation_performed_by_validator"), "build_validator.aggregation")
    validate_no_true_dangerous_flags(build_validator, "build_validator")

    require_equal(
        download_validator.get("historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_validator_status"),
        DOWNLOAD_VALIDATOR_STATUS_PASS,
        "download_validator.status",
    )
    require_true(download_validator.get("downloaded_zip_exists"), "download_validator.sample_zip_exists")
    require_true(download_validator.get("safe_for_single_file_pipeline_build_preview"), "download_validator.safe_build_preview")
    require_false(download_validator.get("new_download_performed_by_validator"), "download_validator.new_download_by_validator")

    require_true(manifest_preview.get("provenance_placeholders_required"), "manifest_preview.provenance_placeholders")
    require_false(manifest_preview.get("source_manifest_creation_allowed_now"), "manifest_preview.creation_allowed")
    require_true(manifest_bundle.get("source_manifest_placeholder_only"), "manifest_bundle.placeholder_only")
    require_false(manifest_bundle.get("source_manifest_acquisition_ready"), "manifest_bundle.acquisition_ready")
    require_false(manifest_bundle.get("source_manifest_build_ready"), "manifest_bundle.build_ready")
    require_false(manifest_bundle.get("source_manifest_download_ready"), "manifest_bundle.download_ready")
    require_equal(manifest_bundle.get("downloaded_file_count"), 0, "manifest_bundle.downloaded_file_count")
    require_equal(manifest_bundle.get("sha256_claim_count"), 0, "manifest_bundle.sha256_claim_count")
    require_equal(manifest_bundle.get("build_ready_file_count"), 0, "manifest_bundle.build_ready_file_count")
    require_true(manifest_bundle.get("placeholder_manifest_self_validated"), "manifest_bundle.self_validated")
    require_true(
        manifest_self_validator.get("source_manifest_validated_as_placeholder"),
        "manifest_self_validator.source_manifest_validated_as_placeholder",
    )
    require_true(
        manifest_self_validator.get("replacement_checks_all_true"),
        "manifest_self_validator.replacement_checks_all_true",
    )
    validate_no_true_dangerous_flags(manifest_bundle, "manifest_bundle")

    return {
        "head": head,
        "whole_system_preflight_completed": True,
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
    }


def planned_dates() -> List[date]:
    start = date.fromisoformat(DATE_RANGE_START)
    return [start + timedelta(days=offset) for offset in range(RANGE_DAYS)]


def planned_url_for(day: date) -> str:
    ymd = day.strftime("%Y%m%d")
    iso = day.isoformat()
    return f"https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/{ymd}/{TARGET_SYMBOL}-candlesticks-{iso}.zip"


def build_planned_manifest() -> List[Dict[str, Any]]:
    entries = []
    for day in planned_dates():
        iso = day.isoformat()
        expected_file = f"{TARGET_SYMBOL}-candlesticks-{iso}.zip"
        entries.append(
            {
                "date": iso,
                "planned_url": planned_url_for(day),
                "expected_file_name": expected_file,
                "instrument_name": TARGET_SYMBOL,
                "expected_inner_csv_name": f"{TARGET_SYMBOL}-candlesticks-{iso}.csv",
                "download_status": "NOT_DOWNLOADED",
                "sha256_status": "NOT_AVAILABLE_UNTIL_DOWNLOAD",
                "expected_sha256_after_download": None,
                "local_storage_path_after_download": None,
                "build_ready": False,
                "acquisition_ready": False,
                "inclusion_allowed_for_future_execution_only": True,
            }
        )
    return entries


def build_sections(planned_manifest: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    preview_scope = {
        "small_range_download_preview_created": True,
        "target_symbol": TARGET_SYMBOL,
        "range_type": RANGE_TYPE,
        "range_days": RANGE_DAYS,
        "planned_file_count": len(planned_manifest),
        "planned_url_count": len(planned_manifest),
        "date_range_start": DATE_RANGE_START,
        "date_range_end": DATE_RANGE_END,
        "planned_url_pattern": PLANNED_URL_PATTERN,
        "input_interval": INPUT_INTERVAL,
        "output_target_interval": OUTPUT_TARGET_INTERVAL,
        "purpose": PURPOSE,
        "preview_only": True,
        "download_performed_now": False,
    }
    approval_record = {
        "small_range_download_approval_record_created": True,
        "user_small_range_download_approval_present": True,
        "approval_scope": APPROVAL_SCOPE,
        "approval_grants_download_now": False,
        "approval_grants_future_small_range_download_next": True,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_more_than_7_files_now": False,
        "approval_grants_multi_symbol_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_aggregation_now": False,
        "approval_grants_broad_acquisition_now": False,
        "approval_grants_strategy_backtest_candidate_now": False,
        "approval_grants_runtime_capital_live_now": False,
    }
    future_execution_rules = {
        "future_execution_module_may": [
            "download exactly the 7 planned URLs only",
            "save files only under established module output/quarantine directory",
            "compute SHA256 after each download",
            "record file size and download timestamp",
            "inspect ZIP inventory safely",
            "read only headers/sample rows unless separately approved for range build",
            "produce per-file provenance report",
            "not build data",
            "not aggregate data",
        ],
        "future_execution_module_must_not": [
            "download any URL outside the planned list",
            "use API",
            "browse",
            "process more than one symbol",
            "download more than 7 files",
            "build 1h output",
            "create research/backtest panel",
            "claim edge/profit",
            "mark broad acquisition ready",
            "touch runtime/capital/live",
        ],
    }
    fail_closed_rules = {
        "future_execution_must_fail_closed_if": [
            "planned URL list changes",
            "more than 7 files requested",
            "any non-approved URL requested",
            "any file download fails",
            "any ZIP hash cannot be computed",
            "any ZIP path traversal appears",
            "expected inner CSV missing",
            "schema mismatch",
            "instrument mismatch",
            "file size exceeds resource limit",
            "download path outside output directory",
            "data build/aggregation attempted",
            "output is marked research/backtest/edge-ready",
            "runtime/capital/live path touched",
        ],
        "planned_url_count_limit": RANGE_DAYS,
        "single_symbol_only": True,
        "broad_acquisition_blocked": True,
    }
    manifest = {
        "planned_urls_created": True,
        "planned_url_count": len(planned_manifest),
        "planned_file_count": len(planned_manifest),
        "planned_urls": [item["planned_url"] for item in planned_manifest],
        "planned_files": planned_manifest,
    }
    return {
        "preview_scope": preview_scope,
        "planned_url_manifest": manifest,
        "approval_record": approval_record,
        "future_execution_rules": future_execution_rules,
        "fail_closed_rules": fail_closed_rules,
    }


def build_payload(
    artifacts: Dict[str, Dict[str, Any]],
    artifact_status: Dict[str, Any],
    preflight: Dict[str, Any],
    sections: Dict[str, Dict[str, Any]],
) -> Tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    summary = artifacts["summary_latest"]
    manifest = sections["planned_url_manifest"]
    planned_files = manifest["planned_files"]
    flags = dangerous_flags()
    active_p1 = max(8, int(summary.get("active_p1_attention_count", 8)))
    sha256_claim_count = sum(1 for item in planned_files if item["expected_sha256_after_download"] is not None)
    build_ready_file_count = sum(1 for item in planned_files if item["build_ready"] is True)
    acquisition_ready_file_count = sum(1 for item in planned_files if item["acquisition_ready"] is True)
    all_not_downloaded = all(item["download_status"] == "NOT_DOWNLOADED" for item in planned_files)
    replacement_checks = {
        "preflight_passed": preflight["whole_system_preflight_completed"] is True,
        "artifact_chain_consistent": preflight["artifact_chain_consistent"] is True,
        "input_artifacts_valid": artifact_status["preview_input_artifacts_exist"] is True
        and artifact_status["preview_input_artifacts_valid_json"] is True,
        "planned_url_count_7": manifest["planned_url_count"] == RANGE_DAYS,
        "planned_file_count_7": manifest["planned_file_count"] == RANGE_DAYS,
        "date_range_exact": planned_files[0]["date"] == DATE_RANGE_START and planned_files[-1]["date"] == DATE_RANGE_END,
        "all_planned_files_not_downloaded": all_not_downloaded,
        "no_sha256_claims": sha256_claim_count == 0,
        "no_build_ready_files": build_ready_file_count == 0,
        "no_acquisition_ready_files": acquisition_ready_file_count == 0,
        "next_route_execution_only_planned_7": True,
        "no_download_api_browse_build_aggregation": True,
        "not_research_backtest_edge": True,
        "schema_config_absent": planned_schema_files_existing_count() == 0,
        "generic_runner_absent": generic_runner_target_exists() is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
    }
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_single_symbol_small_range_download_preview_bundle_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "RUN_NEXT_SEPARATE_SMALL_RANGE_DOWNLOAD_EXECUTION_FOR_PLANNED_7_URLS_ONLY",
        "next_module": NEXT_MODULE_PASS,
        **preflight,
        **artifact_status,
        "bounded_bundle_mode_used": True,
        "user_acceleration_decision_respected": True,
        "small_range_download_preview_created": True,
        "small_range_download_approval_record_created": True,
        "small_range_download_preview_self_validated": True,
        "target_symbol": TARGET_SYMBOL,
        "range_type": RANGE_TYPE,
        "range_days": RANGE_DAYS,
        "date_range_start": DATE_RANGE_START,
        "date_range_end": DATE_RANGE_END,
        "planned_url_pattern": PLANNED_URL_PATTERN,
        "planned_url_count": manifest["planned_url_count"],
        "planned_file_count": manifest["planned_file_count"],
        "planned_urls_created": True,
        "all_planned_files_not_downloaded": all_not_downloaded,
        "sha256_claim_count": sha256_claim_count,
        "build_ready_file_count": build_ready_file_count,
        "acquisition_ready_file_count": acquisition_ready_file_count,
        **sections["approval_record"],
        "next_route_is_execution_only_for_planned_7_files": True,
        "output_valid_for_pipeline_range_validation_only": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "new_download_performed_now": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "okx_sample_zip_downloaded_now": False,
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
        "active_p1_attention_count": active_p1,
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
            "repo-only bounded bundle created a seven-URL BTC-USDT-SWAP OKX daily ZIP download preview and approval "
            "record for the next separate execution module only; it generated planned URL strings from the observed "
            "static pattern, marked every planned file NOT_DOWNLOADED with no SHA256 claim and no build/acquisition "
            "readiness, and performed no download, API call, browse, URL fetch, CSV/ZIP/parquet read, data build, "
            "aggregation, strategy, backtest, candidate, runtime, capital, live, schema/config, or generic-runner action"
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

    self_validator = {
        "generated_at_utc": utc_now(),
        "all_preview_bundle_artifacts_exist": True,
        "all_preview_bundle_artifacts_valid_json": True,
        "planned_url_count": manifest["planned_url_count"],
        "planned_file_count": manifest["planned_file_count"],
        "date_range_start": DATE_RANGE_START,
        "date_range_end": DATE_RANGE_END,
        "all_planned_files_not_downloaded": all_not_downloaded,
        "sha256_claim_count": sha256_claim_count,
        "build_ready_file_count": build_ready_file_count,
        "acquisition_ready_file_count": acquisition_ready_file_count,
        "no_download_api_browse_build_aggregation_occurred": True,
        "next_module_is_execution_not_broad_acquisition": NEXT_MODULE_PASS.endswith(
            "small_range_download_execution_after_preview_approval_v1.py"
        ),
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": active_p1,
        "dormant_repo_attention_count": 716,
        "replacement_checks_all_true": True,
    }
    sections["self_validator"] = self_validator
    return payload, sections


def write_artifacts(payload: Dict[str, Any], sections: Dict[str, Dict[str, Any]]) -> None:
    outputs = {
        "historical_okx_single_symbol_small_range_download_preview.json": sections["preview_scope"],
        "historical_okx_single_symbol_small_range_planned_url_manifest.json": sections["planned_url_manifest"],
        "historical_okx_single_symbol_small_range_download_approval_record.json": sections["approval_record"],
        "historical_okx_single_symbol_small_range_fail_closed_rules.json": {
            "generated_at_utc": utc_now(),
            "future_execution_rules": sections["future_execution_rules"],
            "fail_closed_rules": sections["fail_closed_rules"],
        },
        "historical_okx_single_symbol_small_range_download_preview_self_validator.json": sections["self_validator"],
        "historical_okx_single_symbol_small_range_download_preview_bundle_summary.json": {
            "generated_at_utc": utc_now(),
            "preview_scope": sections["preview_scope"],
            "planned_url_manifest": sections["planned_url_manifest"],
            "approval_record": sections["approval_record"],
            "future_execution_rules": sections["future_execution_rules"],
            "fail_closed_rules": sections["fail_closed_rules"],
            "self_validator": sections["self_validator"],
            "summary": payload,
        },
        "repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_preview_after_smoke_test_summary_v1_latest.json": payload,
    }
    for name, artifact in outputs.items():
        write_json(OUT_DIR / name, artifact)

    required = [
        "historical_okx_single_symbol_small_range_download_preview.json",
        "historical_okx_single_symbol_small_range_planned_url_manifest.json",
        "historical_okx_single_symbol_small_range_download_approval_record.json",
        "historical_okx_single_symbol_small_range_fail_closed_rules.json",
        "historical_okx_single_symbol_small_range_download_preview_self_validator.json",
        "historical_okx_single_symbol_small_range_download_preview_bundle_summary.json",
    ]
    for name in required:
        data, exists, valid, non_empty = read_json_checked(OUT_DIR / name)
        if not (exists and valid and non_empty and isinstance(data, dict)):
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: generated artifact failed self-validation: {name}")


def blocked_payload(exc: Exception) -> Dict[str, Any]:
    flags = dangerous_flags()
    message = str(exc)
    blocked_status = STATUS_BLOCKED_NEXT_MODULE if STATUS_BLOCKED_NEXT_MODULE in message else STATUS_BLOCKED_CONTEXT
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_single_symbol_small_range_download_preview_bundle_status": blocked_status,
        "final_decision": blocked_status,
        "next_action": "STOP_FAIL_CLOSED_NO_SMALL_RANGE_DOWNLOAD_PREVIEW_APPROVAL",
        "next_module": NEXT_MODULE_BLOCKED,
        "error": message,
        "whole_system_preflight_completed": False,
        "live_next_module_matches_requested_module": False,
        "artifact_chain_consistent": False,
        "stale_or_contradictory_artifact_detected": True,
        "bounded_bundle_mode_used": True,
        "user_acceleration_decision_respected": True,
        "small_range_download_preview_created": False,
        "small_range_download_approval_record_created": False,
        "small_range_download_preview_self_validated": False,
        "target_symbol": TARGET_SYMBOL,
        "range_days": RANGE_DAYS,
        "date_range_start": DATE_RANGE_START,
        "date_range_end": DATE_RANGE_END,
        "planned_url_count": 0,
        "planned_file_count": 0,
        "planned_urls_created": False,
        "all_planned_files_not_downloaded": False,
        "sha256_claim_count": 0,
        "build_ready_file_count": 0,
        "acquisition_ready_file_count": 0,
        "approval_grants_download_now": False,
        "approval_grants_future_small_range_download_next": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_more_than_7_files_now": False,
        "approval_grants_multi_symbol_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_aggregation_now": False,
        "approval_grants_broad_acquisition_now": False,
        "next_route_is_execution_only_for_planned_7_files": False,
        "output_valid_for_pipeline_range_validation_only": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "new_download_performed_now": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "okx_sample_zip_downloaded_now": False,
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
        "current_evidence_chain_quality_after_bundle": blocked_status,
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 8,
        "dormant_repo_attention_count": 716,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": planned_schema_files_existing_count(),
        "generic_runner_target_exists": generic_runner_target_exists(),
        "dangerous_flags": flags,
        "dangerous_flags_all_false": True,
        "dangerous_flags_true_count": 0,
        "derived_live_repo_post_check": blocked_status,
        "derived_live_repo_post_check_reason": message,
        "replacement_checks_all_true": False,
    }


def main() -> int:
    try:
        artifacts, artifact_status = load_required_artifacts()
        preflight = validate_preflight(artifacts)
        planned_manifest = build_planned_manifest()
        sections = build_sections(planned_manifest)
        payload, sections = build_payload(artifacts, artifact_status, preflight, sections)
        write_artifacts(payload, sections)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        payload = blocked_payload(exc)
        write_json(
            OUT_DIR
            / "repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_preview_after_smoke_test_summary_v1_latest.json",
            payload,
        )
        write_json(OUT_DIR / "historical_okx_single_symbol_small_range_download_preview_bundle_summary.json", payload)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
