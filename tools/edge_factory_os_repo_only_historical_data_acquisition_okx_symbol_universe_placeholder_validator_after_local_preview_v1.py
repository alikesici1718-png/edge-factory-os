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
    "edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_placeholder_validator_"
    "after_local_preview_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_placeholder_validator_"
    "after_local_preview_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "6cecc79"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 679
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 680

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_placeholder_validator_"
    "after_local_preview_v1.py"
)
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_preview_"
    "after_symbol_universe_validator_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_placeholder_validation_blocked_record_"
    "after_local_preview_v1.py"
)

INPUT_BUNDLE_DIR = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_input_or_local_artifact_preview_after_resolution_bundle_v1"
)
INPUT_BUNDLE_ARTIFACT = (
    INPUT_BUNDLE_DIR
    / "repo_only_historical_data_acquisition_okx_symbol_universe_input_or_local_artifact_preview_after_resolution_bundle_v1_latest.json"
)
PIPELINE_PLACEHOLDER_ARTIFACT = (
    INPUT_BUNDLE_DIR / "historical_okx_pipeline_validation_symbol_universe_placeholder.json"
)
SURVIVORSHIP_RISK_ARTIFACT = (
    INPUT_BUNDLE_DIR / "historical_okx_symbol_universe_survivorship_risk_report.json"
)
LOCAL_CANDIDATE_REPORT_ARTIFACT = (
    INPUT_BUNDLE_DIR / "historical_okx_local_symbol_universe_candidate_report.json"
)
SYMBOL_INPUT_SELF_VALIDATOR_ARTIFACT = (
    INPUT_BUNDLE_DIR / "historical_okx_symbol_universe_input_or_local_artifact_self_validator.json"
)
COVERAGE_PLACEHOLDER_ARTIFACT = (
    INPUT_BUNDLE_DIR / "historical_okx_coverage_decision_placeholder_after_symbol_universe_preview.json"
)
PROVENANCE_PLACEHOLDER_ARTIFACT = (
    INPUT_BUNDLE_DIR / "historical_okx_provenance_placeholder_after_symbol_universe_preview.json"
)

SOURCE_MANIFEST_DIR = (
    LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_source_manifest_approval_after_preview_v1"
)
SOURCE_MANIFEST_LATEST_ARTIFACT = (
    SOURCE_MANIFEST_DIR / "repo_only_historical_data_acquisition_okx_source_manifest_approval_after_preview_v1_latest.json"
)
SOURCE_MANIFEST_ARTIFACT = SOURCE_MANIFEST_DIR / "historical_okx_source_manifest.json"
SOURCE_MANIFEST_SELF_VALIDATOR_ARTIFACT = (
    SOURCE_MANIFEST_DIR / "historical_okx_source_manifest_self_validator.json"
)

INPUT_BUNDLE_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_PIPELINE_VALIDATION_SYMBOL_UNIVERSE_PLACEHOLDER_CREATED_"
    "PENDING_VALIDATOR_NO_EXECUTION"
)
STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SYMBOL_UNIVERSE_PLACEHOLDER_VALIDATED_SINGLE_SYMBOL_PIPELINE_"
    "SMOKE_TEST_PREVIEW_READY_NO_EXECUTION"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_OKX_PIPELINE_VALIDATION_SYMBOL_UNIVERSE_PLACEHOLDER_CREATED_PENDING_"
    "VALIDATOR_NO_EXECUTION"
)
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SYMBOL_UNIVERSE_PLACEHOLDER_VALIDATED_SINGLE_SYMBOL_PIPELINE_"
    "SMOKE_TEST_PREVIEW_READY_NO_EXECUTION"
)

UNIVERSE_SCOPE = "PIPELINE_VALIDATION_UNIVERSE_NOT_SURVIVORSHIP_SAFE"
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


def validate_common_closed_flags(data: Dict[str, Any], label: str) -> None:
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
        require_false(data.get(field), f"{label}.{field}")
    for field in ("downloaded_file_count", "sha256_claim_count", "build_ready_file_count"):
        require_zero(data.get(field), f"{label}.{field}")


def validate_required_artifacts() -> Dict[str, Dict[str, Any]]:
    paths = {
        "input_bundle": INPUT_BUNDLE_ARTIFACT,
        "pipeline_placeholder": PIPELINE_PLACEHOLDER_ARTIFACT,
        "survivorship_risk": SURVIVORSHIP_RISK_ARTIFACT,
        "local_candidate_report": LOCAL_CANDIDATE_REPORT_ARTIFACT,
        "symbol_input_self_validator": SYMBOL_INPUT_SELF_VALIDATOR_ARTIFACT,
        "coverage_placeholder": COVERAGE_PLACEHOLDER_ARTIFACT,
        "provenance_placeholder": PROVENANCE_PLACEHOLDER_ARTIFACT,
        "source_manifest_latest": SOURCE_MANIFEST_LATEST_ARTIFACT,
        "source_manifest": SOURCE_MANIFEST_ARTIFACT,
        "source_manifest_self_validator": SOURCE_MANIFEST_SELF_VALIDATOR_ARTIFACT,
    }
    return {label: load_json(path, label) for label, path in paths.items()}


def validate_preflight(artifacts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))

    bundle = artifacts["input_bundle"]
    placeholder = artifacts["pipeline_placeholder"]
    risk = artifacts["survivorship_risk"]
    candidate = artifacts["local_candidate_report"]
    symbol_self_validator = artifacts["symbol_input_self_validator"]
    coverage = artifacts["coverage_placeholder"]
    provenance = artifacts["provenance_placeholder"]
    source_manifest_latest = artifacts["source_manifest_latest"]
    source_manifest = artifacts["source_manifest"]
    source_manifest_self_validator = artifacts["source_manifest_self_validator"]

    require_equal(
        bundle.get("historical_data_acquisition_okx_symbol_universe_input_or_local_artifact_bundle_status"),
        INPUT_BUNDLE_STATUS_PASS,
        "input_bundle.status",
    )
    require_equal(bundle.get("next_module"), REQUESTED_MODULE, "input_bundle.next_module", STATUS_BLOCKED_NEXT_MODULE)
    require_equal(bundle.get("current_evidence_chain_quality_after_bundle"), EVIDENCE_BEFORE, "input_bundle.evidence_after")
    require_true(bundle.get("whole_system_preflight_completed"), "input_bundle.whole_system_preflight_completed")
    require_true(bundle.get("live_next_module_matches_requested_module"), "input_bundle.live_next_module_matches_requested_module")
    require_true(bundle.get("artifact_chain_consistent"), "input_bundle.artifact_chain_consistent")
    require_false(bundle.get("stale_or_contradictory_artifact_detected"), "input_bundle.stale_artifact")
    require_true(bundle.get("bounded_bundle_mode_used"), "input_bundle.bounded_bundle_mode_used")
    require_false(bundle.get("user_supplied_symbol_universe_present"), "input_bundle.user_supplied_present")
    require_false(bundle.get("user_supplied_symbol_universe_used"), "input_bundle.user_supplied_used")
    require_true(bundle.get("local_existing_symbol_universe_preview_performed"), "input_bundle.local_preview")
    require_true(bundle.get("local_artifact_sources_checked_are_json_or_status_only"), "input_bundle.json_status_only")
    require_false(bundle.get("parquet_row_read_performed"), "input_bundle.parquet_row_read")
    require_false(bundle.get("csv_row_read_performed"), "input_bundle.csv_row_read")
    require_false(bundle.get("zip_read_performed"), "input_bundle.zip_read")
    validate_common_closed_flags(bundle, "input_bundle")
    validate_no_true_dangerous_flags(bundle, "input_bundle")

    require_equal(bundle.get("local_symbol_universe_candidate_found"), "partial", "input_bundle.candidate_found")
    require_equal(bundle.get("local_symbol_universe_symbol_count"), 1, "input_bundle.symbol_count")
    require_true(bundle.get("local_symbol_universe_list_available"), "input_bundle.list_available")
    require_equal(bundle.get("local_symbol_universe_scope"), UNIVERSE_SCOPE, "input_bundle.scope")
    require_false(bundle.get("local_symbol_universe_survivorship_safe"), "input_bundle.local_survivorship_safe")
    require_false(
        bundle.get("local_symbol_universe_historical_lifecycle_complete"),
        "input_bundle.local_historical_lifecycle_complete",
    )
    require_true(bundle.get("pipeline_validation_universe_placeholder_created"), "input_bundle.placeholder_created")
    require_equal(bundle.get("universe_status"), "PLACEHOLDER_PIPELINE_VALIDATION_ONLY", "input_bundle.universe_status")
    require_false(bundle.get("universe_is_survivorship_safe"), "input_bundle.universe_survivorship_safe")
    require_false(bundle.get("universe_is_historical_complete"), "input_bundle.universe_historical_complete")
    require_false(bundle.get("universe_is_build_ready"), "input_bundle.universe_build_ready")
    require_false(bundle.get("universe_is_acquisition_ready"), "input_bundle.universe_acquisition_ready")
    require_true(bundle.get("symbol_list_still_required"), "input_bundle.symbol_list_still_required")
    require_true(bundle.get("lifecycle_evidence_required"), "input_bundle.lifecycle_evidence_required")
    require_true(bundle.get("delisted_inactive_handling_required"), "input_bundle.delisted_inactive_handling_required")
    require_false(bundle.get("coverage_resolved_now"), "input_bundle.coverage_resolved_now")
    require_false(bundle.get("provenance_resolved_now"), "input_bundle.provenance_resolved_now")
    require_true(bundle.get("okx_3_year_pipeline_validation_recommended"), "input_bundle.okx_3_year")
    require_true(bundle.get("okx_4_year_gap_recorded"), "input_bundle.okx_4_year_gap")
    require_equal(bundle.get("active_p0_blocker_count"), 0, "input_bundle.active_p0")
    if not isinstance(bundle.get("active_p1_attention_count"), int) or bundle["active_p1_attention_count"] < 8:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: input_bundle.active_p1_attention_count must be >= 8")
    require_equal(bundle.get("dormant_repo_attention_count"), 716, "input_bundle.dormant_attention")
    require_true(bundle.get("replacement_checks_all_true"), "input_bundle.replacement_checks_all_true")

    require_equal(placeholder.get("universe_status"), "PLACEHOLDER_PIPELINE_VALIDATION_ONLY", "placeholder.status")
    require_false(placeholder.get("universe_is_survivorship_safe"), "placeholder.survivorship_safe")
    require_false(placeholder.get("universe_is_historical_complete"), "placeholder.historical_complete")
    require_false(placeholder.get("universe_is_build_ready"), "placeholder.build_ready")
    require_false(placeholder.get("universe_is_acquisition_ready"), "placeholder.acquisition_ready")
    require_equal(placeholder.get("symbol_count"), 1, "placeholder.symbol_count")
    require_equal(placeholder.get("symbols"), ["BTC-USDT-SWAP"], "placeholder.symbols")
    require_equal(placeholder.get("allowed_use"), "PIPELINE_VALIDATION_ONLY_NOT_EDGE_CLAIM", "placeholder.allowed_use")
    require_equal(placeholder.get("prohibited_use"), "SURVIVORSHIP_SAFE_BACKTEST_OR_EDGE_CLAIM", "placeholder.prohibited_use")
    require_true(placeholder.get("lifecycle_evidence_required"), "placeholder.lifecycle_evidence_required")
    require_true(placeholder.get("delisted_inactive_handling_required"), "placeholder.delisted_inactive_handling_required")
    require_true(placeholder.get("validator_required"), "placeholder.validator_required")
    require_true(placeholder.get("pipeline_validation_universe_placeholder_created"), "placeholder.created")

    require_equal(candidate.get("local_symbol_universe_candidate_found"), "partial", "candidate.found")
    require_equal(candidate.get("local_symbol_universe_symbol_count"), 1, "candidate.symbol_count")
    require_true(candidate.get("local_symbol_universe_list_available"), "candidate.list_available")
    require_equal(candidate.get("local_symbol_universe_scope"), UNIVERSE_SCOPE, "candidate.scope")
    require_false(candidate.get("local_symbol_universe_survivorship_safe"), "candidate.survivorship_safe")
    require_false(candidate.get("local_symbol_universe_historical_lifecycle_complete"), "candidate.historical_complete")
    require_true(candidate.get("local_artifact_sources_checked_are_json_or_status_only"), "candidate.json_status_only")
    require_false(candidate.get("parquet_row_read_performed"), "candidate.parquet_row_read")
    require_false(candidate.get("csv_row_read_performed"), "candidate.csv_row_read")
    require_false(candidate.get("zip_read_performed"), "candidate.zip_read")

    for field in (
        "current_active_only_symbols_are_not_survivorship_safe",
        "local_artifact_symbols_may_reflect_existing_panel_coverage_not_full_historical_universe",
        "delisted_inactive_symbols_remain_unknown_without_lifecycle_evidence",
        "strategy_backtest_edge_claim_using_this_universe_forbidden",
        "okx_pipeline_validation_may_proceed_later_only_with_explicit_label",
    ):
        require_true(risk.get(field), f"survivorship_risk.{field}")

    require_true(symbol_self_validator.get("all_bundle_artifacts_exist"), "symbol_self_validator.artifacts_exist")
    require_true(symbol_self_validator.get("all_bundle_artifacts_valid_json"), "symbol_self_validator.valid_json")
    require_false(symbol_self_validator.get("csv_row_read_performed"), "symbol_self_validator.csv_row_read")
    require_false(symbol_self_validator.get("zip_read_performed"), "symbol_self_validator.zip_row_read")
    require_false(symbol_self_validator.get("parquet_row_read_performed"), "symbol_self_validator.parquet_row_read")
    require_false(
        symbol_self_validator.get("network_download_api_browse_performed"),
        "symbol_self_validator.network_download_api_browse",
    )
    require_true(symbol_self_validator.get("symbol_universe_not_survivorship_safe"), "symbol_self_validator.not_safe")
    require_true(symbol_self_validator.get("universe_not_build_ready"), "symbol_self_validator.not_build_ready")
    require_true(symbol_self_validator.get("universe_not_acquisition_ready"), "symbol_self_validator.not_acquisition_ready")
    require_false(symbol_self_validator.get("coverage_resolved_now"), "symbol_self_validator.coverage_resolved")
    require_false(symbol_self_validator.get("provenance_resolved_now"), "symbol_self_validator.provenance_resolved")
    require_false(symbol_self_validator.get("hash_claims_made"), "symbol_self_validator.hash_claims")
    require_true(symbol_self_validator.get("replacement_checks_all_true"), "symbol_self_validator.replacement")

    require_false(coverage.get("coverage_resolved_now"), "coverage.coverage_resolved_now")
    require_true(coverage.get("okx_3_year_pipeline_validation_recommended"), "coverage.okx_3_year")
    require_true(coverage.get("okx_4_year_gap_recorded"), "coverage.okx_4_year_gap")
    require_false(provenance.get("provenance_resolved_now"), "provenance.provenance_resolved_now")
    require_true(provenance.get("hashes_unavailable"), "provenance.hashes_unavailable")
    require_zero(provenance.get("downloaded_file_count"), "provenance.downloaded_file_count")

    require_true(source_manifest_latest.get("source_manifest_safe_for_download_preview"), "source_manifest_latest.download_preview")
    require_false(source_manifest_latest.get("source_manifest_safe_for_data_build_now"), "source_manifest_latest.data_build")
    require_false(source_manifest_latest.get("source_manifest_safe_for_acquisition_now"), "source_manifest_latest.acquisition")
    require_zero(source_manifest_latest.get("downloaded_file_count"), "source_manifest_latest.downloaded_file_count")
    require_zero(source_manifest_latest.get("sha256_claim_count"), "source_manifest_latest.sha256_claim_count")
    require_zero(source_manifest_latest.get("build_ready_file_count"), "source_manifest_latest.build_ready_file_count")
    validate_common_closed_flags(source_manifest_latest, "source_manifest_latest")
    validate_no_true_dangerous_flags(source_manifest_latest, "source_manifest_latest")

    require_true(source_manifest.get("manifest_is_placeholder_only"), "source_manifest.placeholder_only")
    require_false(source_manifest.get("manifest_is_build_ready"), "source_manifest.build_ready")
    require_false(source_manifest.get("manifest_is_download_ready"), "source_manifest.download_ready")
    require_false(source_manifest.get("manifest_is_acquisition_ready"), "source_manifest.acquisition_ready")
    require_zero(source_manifest.get("downloaded_file_count"), "source_manifest.downloaded_file_count")
    require_zero(source_manifest.get("sha256_claim_count"), "source_manifest.sha256_claim_count")
    require_zero(source_manifest.get("build_ready_file_count"), "source_manifest.build_ready_file_count")

    require_true(
        source_manifest_self_validator.get("source_manifest_validated_as_placeholder"),
        "source_manifest_self_validator.validated_placeholder",
    )
    require_true(source_manifest_self_validator.get("placeholder_manifest_exists_and_valid_json"), "source_manifest_self_validator.manifest_json")
    require_true(source_manifest_self_validator.get("symbol_universe_placeholder_exists"), "source_manifest_self_validator.symbol_placeholder")
    require_true(source_manifest_self_validator.get("replacement_checks_all_true"), "source_manifest_self_validator.replacement")

    return {
        "whole_system_preflight_completed": True,
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
        "input_bundle_artifact": str(INPUT_BUNDLE_ARTIFACT),
        "pipeline_placeholder_artifact": str(PIPELINE_PLACEHOLDER_ARTIFACT),
        "survivorship_risk_artifact": str(SURVIVORSHIP_RISK_ARTIFACT),
        "source_manifest_latest_artifact": str(SOURCE_MANIFEST_LATEST_ARTIFACT),
        "source_manifest_artifact": str(SOURCE_MANIFEST_ARTIFACT),
        "source_manifest_self_validator_artifact": str(SOURCE_MANIFEST_SELF_VALIDATOR_ARTIFACT),
        "head": head,
    }


def build_payload(preflight: Dict[str, Any], artifacts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    bundle = artifacts["input_bundle"]
    flags = dangerous_flags()
    replacement_checks = {
        "preflight_passed": preflight.get("whole_system_preflight_completed") is True,
        "live_next_module_matches_requested_module": preflight.get("live_next_module_matches_requested_module") is True,
        "artifact_chain_consistent": preflight.get("artifact_chain_consistent") is True,
        "required_symbol_universe_artifacts_exist": True,
        "required_symbol_universe_artifacts_valid_json": True,
        "json_status_only": True,
        "no_row_reads": True,
        "single_symbol_partial_universe": True,
        "pipeline_validation_only": True,
        "not_survivorship_safe": True,
        "not_research_backtest": True,
        "not_edge_claim": True,
        "not_build_ready": True,
        "not_acquisition_ready": True,
        "coverage_unresolved": True,
        "provenance_unresolved": True,
        "no_download_api_browse_build_aggregation": True,
        "schema_config_absent": planned_schema_files_existing_count() == 0,
        "generic_runner_absent": generic_runner_target_exists() is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
    }
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_symbol_universe_placeholder_validator_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "PREVIEW_SINGLE_SYMBOL_PIPELINE_SMOKE_TEST_DOWNLOAD_SCOPE_NO_EXECUTION",
        "next_module": NEXT_MODULE_PASS,
        **preflight,
        "symbol_universe_placeholder_validated": True,
        "required_symbol_universe_artifacts_exist": True,
        "required_symbol_universe_artifacts_valid_json": True,
        "local_symbol_universe_candidate_found": "partial",
        "local_symbol_universe_symbol_count": 1,
        "local_symbol_universe_list_available": True,
        "local_symbol_universe_scope": UNIVERSE_SCOPE,
        "single_symbol_pipeline_smoke_test_candidate": True,
        "universe_valid_for_pipeline_smoke_test": True,
        "universe_valid_for_research_backtest": False,
        "universe_valid_for_edge_claim": False,
        "universe_is_survivorship_safe": False,
        "universe_is_historical_complete": False,
        "universe_is_build_ready": False,
        "universe_is_acquisition_ready": False,
        "symbol_list_still_required": True,
        "lifecycle_evidence_required": True,
        "delisted_inactive_handling_required": True,
        "coverage_resolved_now": False,
        "provenance_resolved_now": False,
        "okx_3_year_pipeline_validation_recommended": True,
        "okx_4_year_gap_recorded": True,
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
        "current_evidence_chain_quality_before_validator": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_validator": EVIDENCE_AFTER,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": max(8, int(bundle.get("active_p1_attention_count", 8))),
        "dormant_repo_attention_count": 716,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": planned_schema_files_existing_count(),
        "generic_runner_target_exists": generic_runner_target_exists(),
        "dangerous_flags": flags,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "dangerous_flags_true_count": sum(1 for value in flags.values() if value),
        "derived_live_repo_post_check": (
            "PASS_OKX_SYMBOL_UNIVERSE_PLACEHOLDER_VALIDATED_SINGLE_SYMBOL_PIPELINE_SMOKE_TEST_PREVIEW_READY_NO_EXECUTION"
        ),
        "derived_live_repo_post_check_reason": (
            "repo-only validator accepted the partial one-symbol OKX placeholder only as a single-symbol pipeline smoke-test "
            "candidate; it remains non-survivorship-safe, non-historical-complete, not build-ready, not acquisition-ready, "
            "and invalid for research/backtest/edge claims with no download/API/browse/data build/aggregation performed"
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


def write_validator_artifacts(payload: Dict[str, Any]) -> None:
    outputs = {
        "historical_okx_symbol_universe_placeholder_validator.json": payload,
        "repo_only_historical_data_acquisition_okx_symbol_universe_placeholder_validator_after_local_preview_v1_latest.json": payload,
    }
    for name, artifact in outputs.items():
        write_json(OUT_DIR / name, artifact)


def blocked_payload(exc: Exception) -> Dict[str, Any]:
    flags = dangerous_flags()
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_symbol_universe_placeholder_validator_status": STATUS_BLOCKED_CONTEXT,
        "final_decision": STATUS_BLOCKED_CONTEXT,
        "next_action": "STOP_FAIL_CLOSED_NO_SYMBOL_UNIVERSE_PLACEHOLDER_VALIDATION_NO_DOWNLOAD_NO_API_NO_BUILD",
        "next_module": NEXT_MODULE_BLOCKED,
        "error": str(exc),
        "whole_system_preflight_completed": False,
        "live_next_module_matches_requested_module": False,
        "artifact_chain_consistent": False,
        "stale_or_contradictory_artifact_detected": True,
        "symbol_universe_placeholder_validated": False,
        "single_symbol_pipeline_smoke_test_candidate": False,
        "universe_valid_for_pipeline_smoke_test": False,
        "universe_valid_for_research_backtest": False,
        "universe_valid_for_edge_claim": False,
        "universe_is_survivorship_safe": False,
        "universe_is_historical_complete": False,
        "universe_is_build_ready": False,
        "universe_is_acquisition_ready": False,
        "coverage_resolved_now": False,
        "provenance_resolved_now": False,
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
        artifacts = validate_required_artifacts()
        preflight = validate_preflight(artifacts)
        payload = build_payload(preflight, artifacts)
        write_validator_artifacts(payload)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        payload = blocked_payload(exc)
        write_json(
            OUT_DIR
            / "repo_only_historical_data_acquisition_okx_symbol_universe_placeholder_validator_after_local_preview_v1_latest.json",
            payload,
        )
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
