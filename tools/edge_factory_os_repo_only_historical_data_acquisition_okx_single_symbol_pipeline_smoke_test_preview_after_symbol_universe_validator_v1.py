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
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_preview_"
    "after_symbol_universe_validator_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_preview_"
    "after_symbol_universe_validator_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "2cc4aca"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 680
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 681

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_preview_"
    "after_symbol_universe_validator_v1.py"
)
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_"
    "after_preview_approval_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_preview_"
    "blocked_record_after_symbol_universe_validator_v1.py"
)

VALIDATOR_DIR = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_placeholder_validator_after_local_preview_v1"
)
SYMBOL_UNIVERSE_VALIDATOR_ARTIFACT = (
    VALIDATOR_DIR
    / "repo_only_historical_data_acquisition_okx_symbol_universe_placeholder_validator_after_local_preview_v1_latest.json"
)
INPUT_BUNDLE_DIR = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_input_or_local_artifact_preview_after_resolution_bundle_v1"
)
PIPELINE_PLACEHOLDER_ARTIFACT = (
    INPUT_BUNDLE_DIR / "historical_okx_pipeline_validation_symbol_universe_placeholder.json"
)
SOURCE_MANIFEST_DIR = (
    LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_source_manifest_approval_after_preview_v1"
)
SOURCE_MANIFEST_ARTIFACT = SOURCE_MANIFEST_DIR / "historical_okx_source_manifest.json"
SOURCE_MANIFEST_SELF_VALIDATOR_ARTIFACT = (
    SOURCE_MANIFEST_DIR / "historical_okx_source_manifest_self_validator.json"
)
AGGREGATION_POLICY_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_after_creation_v1"
    / "repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_after_creation_v1_latest.json"
)

SYMBOL_UNIVERSE_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SYMBOL_UNIVERSE_PLACEHOLDER_VALIDATED_SINGLE_SYMBOL_PIPELINE_"
    "SMOKE_TEST_PREVIEW_READY_NO_EXECUTION"
)
AGGREGATION_POLICY_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_VALIDATED_"
    "SOURCE_MANIFEST_PREVIEW_READY_NO_EXECUTION"
)
STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_PIPELINE_SMOKE_TEST_PREVIEW_APPROVED_DOWNLOAD_"
    "EXECUTION_NEXT_NO_EXECUTION_YET"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SYMBOL_UNIVERSE_PLACEHOLDER_VALIDATED_SINGLE_SYMBOL_PIPELINE_"
    "SMOKE_TEST_PREVIEW_READY_NO_EXECUTION"
)
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_PIPELINE_SMOKE_TEST_PREVIEW_APPROVED_DOWNLOAD_"
    "EXECUTION_NEXT_NO_EXECUTION_YET"
)

TARGET_SYMBOL_FALLBACK = "BTC-USDT-SWAP"
TARGET_URL = (
    "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/20260518/"
    "BTC-USDT-SWAP-candlesticks-2026-05-18.zip"
)
TARGET_FILE_NAME = "BTC-USDT-SWAP-candlesticks-2026-05-18.zip"
EXPECTED_INNER_CSV = "BTC-USDT-SWAP-candlesticks-2026-05-18.csv"
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
EXPECTED_INTERVAL = "1m"
SMOKE_TEST_SCOPE = "SINGLE_SYMBOL_SINGLE_FILE_PIPELINE_SMOKE_TEST_ONLY"

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


def require_zero(actual: Any, field: str) -> None:
    require_equal(actual, 0, field)


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


def validate_no_execution_flags(data: Dict[str, Any], label: str) -> None:
    for field in (
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
    ):
        if field in data:
            require_false(data.get(field), f"{label}.{field}")
    for field in ("downloaded_file_count", "sha256_claim_count", "build_ready_file_count"):
        if field in data:
            require_zero(data.get(field), f"{label}.{field}")


def validate_required_artifacts() -> Dict[str, Dict[str, Any]]:
    paths = {
        "symbol_universe_validator": SYMBOL_UNIVERSE_VALIDATOR_ARTIFACT,
        "pipeline_placeholder": PIPELINE_PLACEHOLDER_ARTIFACT,
        "source_manifest": SOURCE_MANIFEST_ARTIFACT,
        "source_manifest_self_validator": SOURCE_MANIFEST_SELF_VALIDATOR_ARTIFACT,
        "aggregation_policy_validator": AGGREGATION_POLICY_VALIDATOR_ARTIFACT,
    }
    return {label: load_json(path, label) for label, path in paths.items()}


def validate_preflight(artifacts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))

    validator = artifacts["symbol_universe_validator"]
    placeholder = artifacts["pipeline_placeholder"]
    manifest = artifacts["source_manifest"]
    manifest_self_validator = artifacts["source_manifest_self_validator"]
    aggregation_validator = artifacts["aggregation_policy_validator"]

    require_equal(
        validator.get("historical_data_acquisition_okx_symbol_universe_placeholder_validator_status"),
        SYMBOL_UNIVERSE_VALIDATOR_STATUS_PASS,
        "symbol_universe_validator.status",
    )
    require_equal(validator.get("next_module"), REQUESTED_MODULE, "symbol_universe_validator.next_module", STATUS_BLOCKED_NEXT_MODULE)
    require_equal(validator.get("current_evidence_chain_quality_after_validator"), EVIDENCE_BEFORE, "symbol_universe_validator.evidence_after")
    require_true(validator.get("whole_system_preflight_completed"), "symbol_universe_validator.preflight")
    require_true(validator.get("live_next_module_matches_requested_module"), "symbol_universe_validator.next_module_match")
    require_true(validator.get("artifact_chain_consistent"), "symbol_universe_validator.artifact_chain")
    require_false(validator.get("stale_or_contradictory_artifact_detected"), "symbol_universe_validator.stale_artifact")
    require_true(validator.get("symbol_universe_placeholder_validated"), "symbol_universe_validator.placeholder_validated")
    require_equal(validator.get("local_symbol_universe_candidate_found"), "partial", "symbol_universe_validator.candidate")
    require_equal(validator.get("local_symbol_universe_symbol_count"), 1, "symbol_universe_validator.symbol_count")
    require_true(validator.get("single_symbol_pipeline_smoke_test_candidate"), "symbol_universe_validator.smoke_candidate")
    require_true(validator.get("universe_valid_for_pipeline_smoke_test"), "symbol_universe_validator.pipeline_valid")
    require_false(validator.get("universe_valid_for_research_backtest"), "symbol_universe_validator.research_backtest")
    require_false(validator.get("universe_valid_for_edge_claim"), "symbol_universe_validator.edge_claim")
    require_false(validator.get("universe_is_survivorship_safe"), "symbol_universe_validator.survivorship_safe")
    require_false(validator.get("universe_is_build_ready"), "symbol_universe_validator.build_ready")
    require_false(validator.get("universe_is_acquisition_ready"), "symbol_universe_validator.acquisition_ready")
    validate_no_execution_flags(validator, "symbol_universe_validator")
    validate_no_true_dangerous_flags(validator, "symbol_universe_validator")
    require_equal(validator.get("active_p0_blocker_count"), 0, "symbol_universe_validator.active_p0")
    if not isinstance(validator.get("active_p1_attention_count"), int) or validator["active_p1_attention_count"] < 8:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: symbol_universe_validator.active_p1_attention_count must be >= 8")
    require_equal(validator.get("dormant_repo_attention_count"), 716, "symbol_universe_validator.dormant_attention")
    require_true(validator.get("replacement_checks_all_true"), "symbol_universe_validator.replacement_checks")

    require_equal(placeholder.get("symbol_count"), 1, "pipeline_placeholder.symbol_count")
    symbols = placeholder.get("symbols")
    if not isinstance(symbols, list) or len(symbols) != 1:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: pipeline_placeholder.symbols must contain exactly one symbol")
    require_equal(symbols[0], TARGET_SYMBOL_FALLBACK, "pipeline_placeholder.symbol")
    require_equal(placeholder.get("universe_status"), "PLACEHOLDER_PIPELINE_VALIDATION_ONLY", "pipeline_placeholder.status")
    require_false(placeholder.get("universe_is_survivorship_safe"), "pipeline_placeholder.survivorship_safe")
    require_false(placeholder.get("universe_is_build_ready"), "pipeline_placeholder.build_ready")
    require_false(placeholder.get("universe_is_acquisition_ready"), "pipeline_placeholder.acquisition_ready")

    require_equal(manifest.get("known_sample_url"), TARGET_URL, "source_manifest.known_sample_url")
    require_equal(manifest.get("known_sample_file"), EXPECTED_INNER_CSV, "source_manifest.known_sample_file")
    require_equal(manifest.get("known_sample_schema"), EXPECTED_SCHEMA, "source_manifest.known_sample_schema")
    require_equal(manifest.get("known_sample_direct_interval"), EXPECTED_INTERVAL, "source_manifest.known_sample_direct_interval")
    require_true(manifest.get("manifest_is_placeholder_only"), "source_manifest.placeholder_only")
    require_false(manifest.get("manifest_is_download_ready"), "source_manifest.download_ready")
    require_false(manifest.get("manifest_is_build_ready"), "source_manifest.build_ready")
    require_false(manifest.get("manifest_is_acquisition_ready"), "source_manifest.acquisition_ready")
    require_zero(manifest.get("downloaded_file_count"), "source_manifest.downloaded_file_count")
    require_zero(manifest.get("sha256_claim_count"), "source_manifest.sha256_claim_count")
    require_zero(manifest.get("build_ready_file_count"), "source_manifest.build_ready_file_count")
    planned_files = manifest.get("planned_file_records")
    if not isinstance(planned_files, list) or len(planned_files) != 1:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: source_manifest.planned_file_records must contain exactly one file")
    planned = planned_files[0]
    require_equal(planned.get("archive_file_url"), TARGET_URL, "source_manifest.planned_file.url")
    require_equal(planned.get("archive_file_name"), TARGET_FILE_NAME, "source_manifest.planned_file.name")
    require_equal(planned.get("instrument_name"), TARGET_SYMBOL_FALLBACK, "source_manifest.planned_file.symbol")
    require_equal(planned.get("download_status"), "NOT_DOWNLOADED", "source_manifest.planned_file.download_status")
    require_false(planned.get("included_in_build_allowed"), "source_manifest.planned_file.included_in_build")
    require_equal(planned.get("expected_sha256_after_download"), None, "source_manifest.planned_file.sha256")

    require_true(
        manifest_self_validator.get("source_manifest_validated_as_placeholder"),
        "source_manifest_self_validator.placeholder",
    )
    require_true(manifest_self_validator.get("placeholder_manifest_exists_and_valid_json"), "source_manifest_self_validator.json")
    require_true(manifest_self_validator.get("replacement_checks_all_true"), "source_manifest_self_validator.replacement")
    require_false(manifest_self_validator.get("source_manifest_safe_for_data_build_now"), "source_manifest_self_validator.data_build")
    require_false(
        manifest_self_validator.get("source_manifest_safe_for_acquisition_now"),
        "source_manifest_self_validator.acquisition",
    )

    require_equal(
        aggregation_validator.get("historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_status"),
        AGGREGATION_POLICY_VALIDATOR_STATUS_PASS,
        "aggregation_policy_validator.status",
    )
    require_equal(aggregation_validator.get("expected_input_interval"), EXPECTED_INTERVAL, "aggregation_policy_validator.interval")
    require_false(aggregation_validator.get("aggregation_execution_allowed_now"), "aggregation_policy_validator.execution")
    require_false(aggregation_validator.get("aggregation_performed_now"), "aggregation_policy_validator.aggregation")
    require_false(aggregation_validator.get("data_build_performed"), "aggregation_policy_validator.data_build")
    require_false(aggregation_validator.get("external_download_allowed_now"), "aggregation_policy_validator.download")
    require_false(aggregation_validator.get("external_api_allowed_now"), "aggregation_policy_validator.api")
    require_false(aggregation_validator.get("okx_download_performed"), "aggregation_policy_validator.okx_download")
    require_false(aggregation_validator.get("okx_api_call_performed"), "aggregation_policy_validator.okx_api")
    require_false(aggregation_validator.get("okx_browse_performed"), "aggregation_policy_validator.okx_browse")
    require_true(aggregation_validator.get("replacement_checks_all_true"), "aggregation_policy_validator.replacement")
    validate_no_true_dangerous_flags(aggregation_validator, "aggregation_policy_validator")

    return {
        "whole_system_preflight_completed": True,
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
        "symbol_universe_validator_artifact": str(SYMBOL_UNIVERSE_VALIDATOR_ARTIFACT),
        "pipeline_placeholder_artifact": str(PIPELINE_PLACEHOLDER_ARTIFACT),
        "source_manifest_artifact": str(SOURCE_MANIFEST_ARTIFACT),
        "source_manifest_self_validator_artifact": str(SOURCE_MANIFEST_SELF_VALIDATOR_ARTIFACT),
        "aggregation_policy_validator_artifact": str(AGGREGATION_POLICY_VALIDATOR_ARTIFACT),
        "head": head,
    }


def build_preview_scope(target_symbol: str) -> Dict[str, Any]:
    return {
        "smoke_test_preview_created": True,
        "smoke_test_scope": SMOKE_TEST_SCOPE,
        "target_symbol": target_symbol,
        "target_url": TARGET_URL,
        "target_file_name": TARGET_FILE_NAME,
        "expected_inner_csv": EXPECTED_INNER_CSV,
        "expected_schema": EXPECTED_SCHEMA,
        "expected_schema_recorded": True,
        "expected_interval": EXPECTED_INTERVAL,
        "expected_output_use": "PIPELINE_VALIDATION_ONLY_NOT_RESEARCH_NOT_EDGE",
        "smoke_test_not_survivorship_safe": True,
        "smoke_test_not_research_backtest_ready": True,
        "download_performed_now": False,
        "zip_read_performed_now": False,
        "csv_read_performed_now": False,
        "data_build_performed_now": False,
        "aggregation_performed_now": False,
    }


def build_download_scope(target_symbol: str) -> Dict[str, Any]:
    return {
        "future_download_scope_url_count": 1,
        "future_download_scope_file_count": 1,
        "future_download_scope_limited_to_one_file": True,
        "approved_url": TARGET_URL,
        "approved_archive_file_name": TARGET_FILE_NAME,
        "expected_inner_csv": EXPECTED_INNER_CSV,
        "target_symbol": target_symbol,
        "expected_schema": EXPECTED_SCHEMA,
        "expected_interval": EXPECTED_INTERVAL,
        "scope_expansion_allowed": False,
        "multi_day_download_allowed": False,
        "multi_symbol_download_allowed": False,
        "full_source_manifest_download_allowed": False,
        "source_file_hash_claimed_now": False,
        "downloaded_file_count": 0,
        "sha256_claim_count": 0,
        "build_ready_file_count": 0,
    }


def build_approval_record() -> Dict[str, Any]:
    return {
        "smoke_test_download_approval_record_created": True,
        "user_smoke_test_approval_present": True,
        "approval_scope": "APPROVAL_RECORD_FOR_NEXT_SINGLE_FILE_OKX_SMOKE_TEST_DOWNLOAD_EXECUTION_ONLY",
        "approval_grants_download_now": False,
        "approval_grants_future_single_file_download_next": True,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_multi_file_download_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_aggregation_now": False,
        "approval_grants_acquisition_execution_now": False,
        "approval_grants_strategy_backtest_candidate_now": False,
        "approval_grants_runtime_capital_live_now": False,
    }


def build_future_download_execution_rules() -> Dict[str, Any]:
    return {
        "future_execution_may": [
            "download exactly one ZIP from the approved known sample URL",
            "save it only into an established quarantine or smoke-test output directory",
            "compute SHA256 after download",
            "record file size",
            "optionally list ZIP members",
            "optionally read only header plus minimal sample rows for schema validation",
            "write provenance report",
            "write smoke-test validator inputs",
        ],
        "future_execution_must_not": [
            "download more than one file",
            "iterate URLs",
            "call API",
            "browse",
            "build data",
            "aggregate 1m to 1h",
            "create research or backtest panel",
            "mark broad acquisition ready",
            "touch runtime capital or live paths",
            "claim edge or profit",
        ],
    }


def build_fail_closed_rules() -> Dict[str, Any]:
    return {
        "fail_closed_if": [
            "URL differs from approved URL",
            "more than one URL is requested",
            "download target is outside smoke-test output directory",
            "ZIP size exceeds resource limit",
            "ZIP member path traversal risk exists",
            "expected CSV is absent",
            "schema differs",
            "interval is not 1m",
            "timestamp unit cannot be validated",
            "hash cannot be computed",
            "download is partial or corrupt",
            "network API or browse scope expands",
            "data build or aggregation is attempted",
            "strategy backtest candidate runtime or live path is touched",
        ],
        "fail_closed_policy_active": True,
        "scope_expansion_allowed": False,
    }


def build_artifacts(preflight: Dict[str, Any], upstream: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    generated_at_utc = utc_now()
    placeholder = upstream["pipeline_placeholder"]
    target_symbol = placeholder.get("symbols", [TARGET_SYMBOL_FALLBACK])[0]
    preview_scope = build_preview_scope(target_symbol)
    download_scope = build_download_scope(target_symbol)
    approval_record = build_approval_record()
    fail_closed_rules = build_fail_closed_rules()
    future_rules = build_future_download_execution_rules()
    preview = {
        "generated_at_utc": generated_at_utc,
        "preview_scope": preview_scope,
        "future_download_scope": download_scope,
        "future_download_execution_rules": future_rules,
        "approval_record_summary": approval_record,
        "fail_closed_summary": fail_closed_rules,
    }
    return {
        "preview": preview,
        "download_scope": download_scope,
        "approval_record": approval_record,
        "fail_closed_rules": fail_closed_rules,
        "future_download_execution_rules": future_rules,
        "preflight": preflight,
    }


def build_payload(preflight: Dict[str, Any], artifacts: Dict[str, Dict[str, Any]], self_validator: Dict[str, Any]) -> Dict[str, Any]:
    flags = dangerous_flags()
    preview_scope = artifacts["preview"]["preview_scope"]
    download_scope = artifacts["download_scope"]
    approval = artifacts["approval_record"]
    replacement_checks = {
        "preflight_passed": preflight.get("whole_system_preflight_completed") is True,
        "live_next_module_matches_requested_module": preflight.get("live_next_module_matches_requested_module") is True,
        "artifact_chain_consistent": preflight.get("artifact_chain_consistent") is True,
        "scope_exactly_one_url": download_scope.get("future_download_scope_url_count") == 1,
        "scope_exactly_one_file": download_scope.get("future_download_scope_file_count") == 1,
        "approved_url_exact": download_scope.get("approved_url") == TARGET_URL,
        "approval_future_single_file_next_only": approval.get("approval_grants_future_single_file_download_next") is True
        and approval.get("approval_grants_download_now") is False,
        "no_download_api_browse_now": True,
        "no_data_build_aggregation_now": True,
        "no_sha256_claim_now": True,
        "no_build_or_acquisition_ready_claim": True,
        "not_research_backtest_edge": True,
        "schema_config_absent": planned_schema_files_existing_count() == 0,
        "generic_runner_absent": generic_runner_target_exists() is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "self_validator_passed": self_validator.get("smoke_test_bundle_self_validated") is True,
    }
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_preview_bundle_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "RUN_NEXT_SINGLE_FILE_OKX_SMOKE_TEST_DOWNLOAD_EXECUTION_ONLY_AFTER_SEPARATE_MODULE",
        "next_module": NEXT_MODULE_PASS,
        **preflight,
        "bounded_bundle_mode_used": True,
        "user_acceleration_decision_respected": True,
        "smoke_test_preview_created": True,
        "smoke_test_download_approval_record_created": True,
        "smoke_test_bundle_self_validated": True,
        "smoke_test_scope": SMOKE_TEST_SCOPE,
        "target_symbol": preview_scope["target_symbol"],
        "target_url": TARGET_URL,
        "expected_inner_csv": EXPECTED_INNER_CSV,
        "expected_schema_recorded": True,
        "expected_interval": EXPECTED_INTERVAL,
        "single_symbol_pipeline_smoke_test_candidate": True,
        "universe_valid_for_pipeline_smoke_test": True,
        "universe_valid_for_research_backtest": False,
        "universe_valid_for_edge_claim": False,
        "smoke_test_not_survivorship_safe": True,
        "smoke_test_not_research_backtest_ready": True,
        "approval_grants_download_now": False,
        "approval_grants_future_single_file_download_next": True,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_multi_file_download_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_aggregation_now": False,
        "approval_grants_acquisition_execution_now": False,
        "future_download_scope_url_count": 1,
        "future_download_scope_file_count": 1,
        "future_download_scope_limited_to_one_file": True,
        "downloaded_file_count": 0,
        "sha256_claim_count": 0,
        "build_ready_file_count": 0,
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
            "repo-only bounded bundle created a one-symbol one-file OKX smoke-test preview and approval record for the "
            "next separate download execution module only; no file was downloaded, no URL header was fetched, no API or "
            "browse occurred, no CSV/ZIP/parquet rows were read, no hash was claimed, and build/acquisition/research/"
            "backtest/edge/runtime/capital/live paths remain closed"
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


def write_bundle_artifacts(payload: Dict[str, Any], artifacts: Dict[str, Dict[str, Any]], self_validator: Dict[str, Any]) -> None:
    outputs = {
        "historical_okx_single_symbol_pipeline_smoke_test_preview.json": artifacts["preview"],
        "historical_okx_single_symbol_pipeline_smoke_test_download_scope.json": artifacts["download_scope"],
        "historical_okx_single_symbol_pipeline_smoke_test_approval_record.json": artifacts["approval_record"],
        "historical_okx_single_symbol_pipeline_smoke_test_fail_closed_rules.json": artifacts["fail_closed_rules"],
        "historical_okx_single_symbol_pipeline_smoke_test_self_validator.json": self_validator,
        "historical_okx_single_symbol_pipeline_smoke_test_bundle_summary.json": payload,
        "repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_preview_after_symbol_universe_validator_v1_latest.json": payload,
    }
    for name, artifact in outputs.items():
        write_json(OUT_DIR / name, artifact)


def validate_written_json_artifacts() -> Dict[str, Any]:
    required = [
        "historical_okx_single_symbol_pipeline_smoke_test_preview.json",
        "historical_okx_single_symbol_pipeline_smoke_test_download_scope.json",
        "historical_okx_single_symbol_pipeline_smoke_test_approval_record.json",
        "historical_okx_single_symbol_pipeline_smoke_test_fail_closed_rules.json",
        "historical_okx_single_symbol_pipeline_smoke_test_self_validator.json",
        "historical_okx_single_symbol_pipeline_smoke_test_bundle_summary.json",
    ]
    loaded: Dict[str, Dict[str, Any]] = {}
    for name in required:
        loaded[name] = load_json(OUT_DIR / name, name)
    download_scope = loaded["historical_okx_single_symbol_pipeline_smoke_test_download_scope.json"]
    approval = loaded["historical_okx_single_symbol_pipeline_smoke_test_approval_record.json"]
    summary = loaded["historical_okx_single_symbol_pipeline_smoke_test_bundle_summary.json"]
    return {
        "all_bundle_artifacts_exist": True,
        "all_bundle_artifacts_valid_json": True,
        "scope_is_exactly_one_url": download_scope.get("future_download_scope_url_count") == 1,
        "scope_is_exactly_one_file": download_scope.get("future_download_scope_file_count") == 1,
        "scope_limited_to_approved_url": download_scope.get("approved_url") == TARGET_URL,
        "approval_grants_future_single_file_download_next": approval.get("approval_grants_future_single_file_download_next") is True,
        "approval_grants_download_now_false": approval.get("approval_grants_download_now") is False,
        "no_download_api_browse_occurred_now": (
            summary.get("data_download_performed") is False
            and summary.get("okx_download_performed") is False
            and summary.get("okx_api_call_performed") is False
            and summary.get("okx_browse_performed") is False
        ),
        "no_data_build_or_aggregation_occurred_now": (
            summary.get("data_build_performed") is False and summary.get("aggregation_performed_now") is False
        ),
        "no_sha256_claim_occurred_now": summary.get("sha256_claim_count") == 0,
        "no_build_ready_or_acquisition_ready_claim_occurred_now": (
            summary.get("build_ready_file_count") == 0 and summary.get("acquisition_execution_allowed_now") is False
        ),
        "active_p0_blocker_count": summary.get("active_p0_blocker_count"),
        "active_p1_attention_count": summary.get("active_p1_attention_count"),
        "p0_zero": summary.get("active_p0_blocker_count") == 0,
        "p1_carried_forward": isinstance(summary.get("active_p1_attention_count"), int)
        and summary.get("active_p1_attention_count") >= 8,
    }


def build_self_validator(pre_write: bool = False) -> Dict[str, Any]:
    base = {
        "generated_at_utc": utc_now(),
        "smoke_test_bundle_self_validated": not pre_write,
        "all_bundle_artifacts_exist": not pre_write,
        "all_bundle_artifacts_valid_json": not pre_write,
        "scope_is_exactly_one_url": True,
        "scope_is_exactly_one_file": True,
        "approval_grants_future_single_file_download_next": True,
        "approval_grants_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "no_download_api_browse_occurred_now": True,
        "no_data_build_or_aggregation_occurred_now": True,
        "no_sha256_claim_occurred_now": True,
        "no_build_ready_or_acquisition_ready_claim_occurred_now": True,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 8,
        "p0_zero": True,
        "p1_carried_forward": True,
        "replacement_checks_all_true": not pre_write,
    }
    return base


def finalize_self_validator() -> Dict[str, Any]:
    validator = build_self_validator(pre_write=False)
    written = validate_written_json_artifacts()
    validator.update(written)
    validator["smoke_test_bundle_self_validated"] = all(
        validator.get(field) is True
        for field in (
            "all_bundle_artifacts_exist",
            "all_bundle_artifacts_valid_json",
            "scope_is_exactly_one_url",
            "scope_is_exactly_one_file",
            "scope_limited_to_approved_url",
            "approval_grants_future_single_file_download_next",
            "approval_grants_download_now_false",
            "no_download_api_browse_occurred_now",
            "no_data_build_or_aggregation_occurred_now",
            "no_sha256_claim_occurred_now",
            "no_build_ready_or_acquisition_ready_claim_occurred_now",
            "p0_zero",
            "p1_carried_forward",
        )
    )
    validator["replacement_checks_all_true"] = validator["smoke_test_bundle_self_validated"]
    return validator


def blocked_payload(exc: Exception) -> Dict[str, Any]:
    flags = dangerous_flags()
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_preview_bundle_status": STATUS_BLOCKED_CONTEXT,
        "final_decision": STATUS_BLOCKED_CONTEXT,
        "next_action": "STOP_FAIL_CLOSED_NO_SMOKE_TEST_PREVIEW_NO_DOWNLOAD_NO_API_NO_BUILD",
        "next_module": NEXT_MODULE_BLOCKED,
        "error": str(exc),
        "whole_system_preflight_completed": False,
        "live_next_module_matches_requested_module": False,
        "artifact_chain_consistent": False,
        "stale_or_contradictory_artifact_detected": True,
        "bounded_bundle_mode_used": True,
        "user_acceleration_decision_respected": True,
        "smoke_test_preview_created": False,
        "smoke_test_download_approval_record_created": False,
        "smoke_test_bundle_self_validated": False,
        "approval_grants_download_now": False,
        "approval_grants_future_single_file_download_next": False,
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
        "active_p0_blocker_count": 1,
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
        upstream = validate_required_artifacts()
        preflight = validate_preflight(upstream)
        artifacts = build_artifacts(preflight, upstream)
        preliminary_self_validator = build_self_validator(pre_write=True)
        preliminary_payload = build_payload(preflight, artifacts, {**preliminary_self_validator, "smoke_test_bundle_self_validated": True})
        write_bundle_artifacts(preliminary_payload, artifacts, preliminary_self_validator)
        self_validator = finalize_self_validator()
        payload = build_payload(preflight, artifacts, self_validator)
        write_bundle_artifacts(payload, artifacts, self_validator)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        payload = blocked_payload(exc)
        write_json(
            OUT_DIR
            / "repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_preview_after_symbol_universe_validator_v1_latest.json",
            payload,
        )
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
