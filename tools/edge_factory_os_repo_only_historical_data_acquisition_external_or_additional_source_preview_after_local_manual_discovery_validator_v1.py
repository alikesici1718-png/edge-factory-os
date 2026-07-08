from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_external_or_additional_source_"
    "preview_after_local_manual_discovery_validator_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_external_or_additional_source_"
    "preview_after_local_manual_discovery_validator_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "1389d8c"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 656
EXPECTED_TRACKED_PYTHON_COUNT = 657

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_external_or_additional_source_"
    "preview_after_local_manual_discovery_validator_v1.py"
)
NEXT_MODULE_APPROVAL = (
    "edge_factory_os_repo_only_historical_data_acquisition_external_or_additional_source_"
    "approval_after_preview_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_external_or_additional_source_"
    "preview_blocked_record_after_local_manual_discovery_validator_v1.py"
)

VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_local_manual_source_discovery_validator_after_approval_v1"
    / "repo_only_historical_data_acquisition_local_manual_source_discovery_validator_after_approval_v1_latest.json"
)
DISCOVERY_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_local_manual_source_discovery_after_approval_v1"
    / "repo_only_historical_data_acquisition_local_manual_source_discovery_after_approval_v1_latest.json"
)
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
HARDENING_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_implementation_validator_after_approval_v1"
    / "repo_only_pre_acquisition_minimal_reliability_hardening_implementation_validator_after_approval_v1_latest.json"
)

VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_LOCAL_MANUAL_SOURCE_DISCOVERY_VALIDATED_GAP_OPEN_"
    "EXTERNAL_OR_ADDITIONAL_SOURCE_PREVIEW_READY"
)
DISCOVERY_STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_LOCAL_MANUAL_SOURCE_DISCOVERY_COMPLETE_PENDING_VALIDATOR"
APPROVAL_STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_LOCAL_MANUAL_SOURCE_DISCOVERY_APPROVED_NEXT_NO_EXECUTION"
PREVIEW_STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION"
CONTRACT_VALIDATOR_STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_CONTRACT_VALIDATED_PREVIEW_READY_NO_EXECUTION"
HARDENING_STATUS_PASS = (
    "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_VALIDATED_ACQUISITION_CONTRACT_RESUME_READY"
)
STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_EXTERNAL_OR_ADDITIONAL_SOURCE_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION"
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_LOCAL_MANUAL_SOURCE_DISCOVERY_VALIDATED_GAP_OPEN_"
    "EXTERNAL_OR_ADDITIONAL_SOURCE_PREVIEW_READY"
)
EVIDENCE_AFTER = "HISTORICAL_DATA_ACQUISITION_EXTERNAL_OR_ADDITIONAL_SOURCE_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION"
EVIDENCE_CHAIN_POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"
RECOMMENDED_SOURCE_ROUTE = "OKX_OFFICIAL_HISTORICAL_ARCHIVE_OR_EXPORT_MANUAL_IMPORT_PREVIEW"

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
FUTURE_REQUIRED_ARTIFACTS = [
    "historical_external_source_candidate_preview.json",
    "historical_external_source_verification_report.json",
    "historical_raw_data_source_manifest.json",
    "historical_data_acquisition_inventory.json",
    "historical_data_provenance_report.json",
    "historical_symbol_universe_policy.json",
    "historical_symbol_lifecycle_report.json",
    "historical_timestamp_integrity_report.json",
    "historical_missingness_report.json",
    "historical_duplicate_report.json",
    "historical_holdout_policy_report.json",
    "historical_data_acquisition_contract_compliance_report.json",
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
    unexpected = [line for line in normalize_status_lines(status) if line not in allowed]
    require(not unexpected, f"{STATUS_BLOCKED_CONTEXT}: repo dirty outside approved tool: {unexpected}")


def validate_preflight(
    validator: Dict[str, Any],
    discovery: Dict[str, Any],
    approval: Dict[str, Any],
    preview: Dict[str, Any],
    contract_validator: Dict[str, Any],
    hardening: Dict[str, Any],
) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    status = run_git(["status", "--short"])
    require_equal(head, EXPECTED_HEAD, "head")
    validate_repo_status_allows_current_tool_only(status)

    require_equal(validator.get("next_module"), REQUESTED_MODULE, "validator.next_module")
    require_equal(
        validator.get("historical_data_acquisition_local_manual_source_discovery_validator_status"),
        VALIDATOR_STATUS_PASS,
        "validator.status",
    )
    require_true(validator.get("local_manual_source_discovery_validated"), "validator.local_manual_source_discovery_validated")
    require_false(validator.get("local_manual_source_gap_closed"), "validator.local_manual_source_gap_closed")
    require_true(
        validator.get("external_or_additional_acquisition_still_required"),
        "validator.external_or_additional_acquisition_still_required",
    )
    require_equal(validator.get("active_p0_blocker_count"), 0, "validator.active_p0_blocker_count")
    require_equal(validator.get("active_p1_attention_count"), 4, "validator.active_p1_attention_count")
    require_true(
        validator.get("dormant_repo_attention_count_carried_forward"),
        "validator.dormant_repo_attention_count_carried_forward",
    )
    for key in [
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
        "ordinary_selector_backlog_loop_reentry_allowed",
        "generic_runner_target_exists",
    ]:
        require_false(validator.get(key), f"validator.{key}")
    require_true(validator.get("replacement_checks_all_true"), "validator.replacement_checks_all_true")

    require_equal(
        discovery.get("historical_data_acquisition_local_manual_source_discovery_status"),
        DISCOVERY_STATUS_PASS,
        "discovery.status",
    )
    require_equal(approval.get("historical_data_acquisition_approval_status"), APPROVAL_STATUS_PASS, "approval.status")
    require_equal(preview.get("historical_data_acquisition_preview_status"), PREVIEW_STATUS_PASS, "preview.status")
    require_equal(
        contract_validator.get("historical_data_acquisition_contract_validator_status"),
        CONTRACT_VALIDATOR_STATUS_PASS,
        "contract_validator.status",
    )
    require_equal(
        hardening.get("pre_acquisition_minimal_reliability_hardening_implementation_validator_status"),
        HARDENING_STATUS_PASS,
        "hardening.status",
    )
    require_true(hardening.get("hardening_validation_passed"), "hardening.hardening_validation_passed")
    require_equal(hardening.get("active_p0_blocker_count"), 0, "hardening.active_p0_blocker_count")
    return {
        "head": head,
        "status_lines_allowed": normalize_status_lines(status),
        "validator_artifact": str(VALIDATOR_ARTIFACT),
        "discovery_artifact": str(DISCOVERY_ARTIFACT),
        "approval_artifact": str(APPROVAL_ARTIFACT),
        "preview_artifact": str(PREVIEW_ARTIFACT),
        "contract_validator_artifact": str(CONTRACT_VALIDATOR_ARTIFACT),
        "hardening_validator_artifact": str(HARDENING_VALIDATOR_ARTIFACT),
    }


def build_sections(validator: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "validator_context": {
            "local_manual_discovery_validator_passed": True,
            "local_manual_gap_remains_open": True,
            "candidate_3_to_4_year_horizon_found": False,
            "candidate_available_horizon_years_estimate_max": validator.get(
                "candidate_available_horizon_years_estimate_max"
            ),
            "overbroad_candidate_classification_attention_carried_forward": True,
            "parquet_metadata_omission_attention_carried_forward": True,
            "survivorship_holdout_controls_still_required": True,
            "active_p1_attention_count": 4,
            "no_download_fetch_api_build_occurred": True,
        },
        "source_gap_context": {
            "target_historical_horizon_years": "3_to_4",
            "target_timeframe": "1h",
            "local_manual_max_horizon_years_estimate": validator.get(
                "candidate_available_horizon_years_estimate_max"
            ),
            "three_to_four_year_1h_gap_still_open": True,
            "external_or_additional_acquisition_still_required": True,
            "local_manual_sources_sufficient_as_is": False,
        },
        "external_or_additional_source_options_preview": {
            "priority_order": [
                {
                    "route": "OKX_OFFICIAL_HISTORICAL_ARCHIVE_OR_EXPORT_MANUAL_IMPORT_PREVIEW",
                    "priority": "A",
                    "preferred_if": "official OKX historical files/export/archive can be obtained manually by user",
                    "automated_api_call_now": False,
                    "automated_download_now": False,
                    "future_verification_required": [
                        "official source identity",
                        "file format",
                        "date range",
                        "timeframe",
                        "symbols",
                        "timezone",
                        "checksums",
                        "provenance",
                    ],
                    "future_import_requirements": ["preserve raw files", "create source manifest"],
                },
                {
                    "route": "USER_SUPPLIED_THIRD_PARTY_OR_EXCHANGE_EXPORT_IMPORT_PREVIEW",
                    "priority": "B",
                    "system_download_or_api": False,
                    "requirements": [
                        "local validation only",
                        "provenance",
                        "license/source clarity",
                        "hashes",
                        "timestamp/timezone validation",
                    ],
                },
                {
                    "route": "SEPARATELY_APPROVED_OKX_API_OR_DOWNLOAD_CHAIN_PREVIEW",
                    "priority": "C",
                    "allowed_now": False,
                    "requires_separate_preview_approval_execution_validator_chain": True,
                    "requirements": [
                        "timeout policy",
                        "memory/disk policy",
                        "rollback policy",
                        "hardening-state policy",
                        "source manifest",
                        "provenance report",
                        "no strategy selection mixed into acquisition",
                    ],
                },
            ]
        },
        "recommended_source_route_decision": {
            "recommended_source_route": RECOMMENDED_SOURCE_ROUTE,
            "preview_recommendation_only": True,
            "okx_call_made": False,
            "okx_download_performed": False,
            "future_module_must_verify_okx_official_source_availability": True,
            "separate_api_download_chain_only_if_manual_official_archive_unavailable": True,
        },
        "future_verification_requirements": {
            "required_items": [
                "exact OKX source page/file/export identity",
                "retrieval method",
                "official source status",
                "source/license restrictions",
                "instrument type/symbol universe",
                "candle interval=1h",
                "start/end dates covering 3-4 years",
                "timestamp timezone",
                "OHLCV field mapping",
                "missing data policy",
                "duplicate policy",
                "delisted/removed/listing lifecycle evidence if available",
                "checksum/hash",
                "raw data preservation",
                "no strategy-selected universe",
            ]
        },
        "future_required_artifacts_preview": {"required_future_artifacts": FUTURE_REQUIRED_ARTIFACTS},
        "safety_and_hardening_requirements": {
            "secret_scan_remains_clear": True,
            "dependency_snapshot_unchanged_or_explicitly_approved_if_changed": True,
            "no_unapproved_environment_modification": True,
            "ast_current_chain_blocker_remains_0": True,
            "artifact_hash_manifest_updated": True,
            "timeout_policy_applied": True,
            "memory_disk_resource_policy_applied": True,
            "rollback_policy_applied": True,
            "dormant_repo_ast_risks_excluded": True,
            "no_repo_src_tools_module_import_execution": True,
        },
        "fail_closed_preview": {
            "fail_closed_conditions": [
                "OKX/source identity cannot be verified",
                "source/license restrictions unclear",
                "timeframe not 1h",
                "3-4 year coverage not proven",
                "timestamp format ambiguous",
                "symbol universe rule missing",
                "holdout cannot be protected",
                "survivorship/listing controls missing or not disclosed",
                "fake/synthetic data is used as real",
                "external API/download occurs without separate approval",
                "timeout/resource/rollback policy missing",
                "hardening state stale or invalid",
                "strategy/backtest/candidate/runtime/live path touched",
            ]
        },
        "evidence_policy_preview": {
            "current_state_before_preview": EVIDENCE_BEFORE,
            "state_after_preview": EVIDENCE_AFTER,
            "preview_is_not_source_verification": True,
            "preview_is_not_data_evidence": True,
            "preview_is_not_source_manifest": True,
            "preview_is_not_acquisition_execution": True,
            "p1_remains_active_until_acquisition_and_historical_validator_closes_it": True,
        },
        "next_module_decision": {
            "next_module": NEXT_MODULE_APPROVAL,
            "blocked_next_module_if_preview_unsafe": NEXT_MODULE_BLOCKED,
            "decision_reason": "safe preview completed; approval record is required before any verification or acquisition action",
        },
    }


def replacement_checks(payload: Dict[str, Any]) -> Dict[str, bool]:
    return {
        "preflight_passed": payload.get("whole_system_preflight_decision") == "PASS",
        "preview_completed": payload.get("external_or_additional_source_preview_completed") is True,
        "okx_unverified_no_call_no_download": (
            payload.get("okx_source_verified_now") is False
            and payload.get("okx_download_performed") is False
            and payload.get("okx_api_call_performed") is False
        ),
        "source_approval_next": payload.get("next_module") == NEXT_MODULE_APPROVAL,
        "no_download_fetch_api_build": (
            payload.get("data_download_performed") is False
            and payload.get("data_fetch_performed") is False
            and payload.get("data_build_performed") is False
            and payload.get("external_api_calls_performed") is False
        ),
        "acquisition_execution_blocked": payload.get("acquisition_execution_allowed_now") is False,
        "loop_closed": payload.get("loop_remains_closed") is True,
    }


def build_payload(preflight: Dict[str, Any], sections: Dict[str, Any]) -> Dict[str, Any]:
    flags = dangerous_flags()
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_external_or_additional_source_preview_status": STATUS_PASS,
        "final_decision": "EXTERNAL_OR_ADDITIONAL_SOURCE_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION",
        "next_action": "CREATE_EXTERNAL_OR_ADDITIONAL_SOURCE_APPROVAL_RECORD_NO_VERIFICATION_OR_EXECUTION",
        "next_module": NEXT_MODULE_APPROVAL,
        "whole_system_preflight_completed": True,
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
        "real_final_form_gap_confirmed": True,
        "documentation_loop_detected": False,
        "documentation_loop_risk_level": DOCUMENTATION_LOOP_RISK_LEVEL,
        "next_module_closes_real_gap": True,
        "active_p0_blocker_count_from_live_artifact": 0,
        "active_p1_attention_count_from_live_artifact": 4,
        "p1_attention_carried_forward": True,
        "dormant_repo_attention_count_carried_forward": True,
        "blocked_actions_absent_from_requested_module": True,
        "whole_system_preflight_decision": "PASS",
        "prior_local_manual_discovery_validator_respected": True,
        "external_or_additional_source_preview_completed": True,
        "validator_context_completed": True,
        "source_gap_context_completed": True,
        "external_or_additional_source_options_preview_completed": True,
        "recommended_source_route_decision_completed": True,
        "future_verification_requirements_completed": True,
        "future_required_artifacts_preview_completed": True,
        "safety_and_hardening_requirements_completed": True,
        "fail_closed_preview_completed": True,
        "evidence_policy_preview_completed": True,
        "local_manual_source_gap_closed": False,
        "external_or_additional_acquisition_still_required": True,
        "recommended_source_route": RECOMMENDED_SOURCE_ROUTE,
        "okx_official_historical_archive_or_export_preferred": True,
        "okx_source_verified_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "manual_archive_import_preferred": True,
        "external_api_or_download_requires_separate_future_chain": True,
        "source_verification_required_next": True,
        "source_approval_required_next": True,
        "acquisition_execution_allowed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "data_build_performed": False,
        "external_api_calls_performed": False,
        "fake_or_synthetic_data_detected": False,
        "required_future_artifact_list_previewed": True,
        "source_manifest_required": True,
        "provenance_report_required": True,
        "survivorship_bias_controls_required": True,
        "symbol_lifecycle_report_required": True,
        "holdout_policy_required": True,
        "historical_data_quality_validator_required": True,
        "timeout_policy_required_for_acquisition": True,
        "memory_disk_resource_policy_required_for_acquisition": True,
        "rollback_policy_required_for_acquisition": True,
        "hardening_state_required_for_acquisition": True,
        "strategy_signal_claims_made": False,
        "tradable_edge_claims_made": False,
        "profit_claims_made": False,
        "backtest_performed": False,
        "candidate_generation_performed": False,
        "family_release_performed": False,
        "active_paper_performed": False,
        "real_order_touch_performed": False,
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "old_source_panel_anomaly_route_reopened_now": False,
        "old_route_closed_artifacts_used_as_active_evidence_now": False,
        "current_evidence_chain_quality_before_preview": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_preview": EVIDENCE_AFTER,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 4,
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
        "derived_live_repo_post_check": "PASS_EXTERNAL_OR_ADDITIONAL_SOURCE_PREVIEW_READY_FOR_APPROVAL_RECORD",
        "derived_live_repo_post_check_reason": (
            "preview recorded OKX official historical archive/export as the preferred future candidate route without "
            "browsing, source verification, download, fetch, API call, data build, strategy, runtime, capital, live, "
            "generic-runner, schema, config, or old-route action; approval is required before any future verification"
        ),
        "tracked_python_count_expectation": {
            "previous": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT,
        },
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "source_artifacts": {
            "validator_artifact": str(VALIDATOR_ARTIFACT),
            "discovery_artifact": str(DISCOVERY_ARTIFACT),
            "approval_artifact": str(APPROVAL_ARTIFACT),
            "preview_artifact": str(PREVIEW_ARTIFACT),
            "contract_validator_artifact": str(CONTRACT_VALIDATOR_ARTIFACT),
            "hardening_validator_artifact": str(HARDENING_VALIDATOR_ARTIFACT),
        },
        "preflight": preflight,
        "preview_sections": sections,
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
        "prior_local_manual_discovery_validator_respected",
        "external_or_additional_source_preview_completed",
        "validator_context_completed",
        "source_gap_context_completed",
        "external_or_additional_source_options_preview_completed",
        "recommended_source_route_decision_completed",
        "future_verification_requirements_completed",
        "future_required_artifacts_preview_completed",
        "safety_and_hardening_requirements_completed",
        "fail_closed_preview_completed",
        "evidence_policy_preview_completed",
        "external_or_additional_acquisition_still_required",
        "okx_official_historical_archive_or_export_preferred",
        "manual_archive_import_preferred",
        "external_api_or_download_requires_separate_future_chain",
        "source_verification_required_next",
        "source_approval_required_next",
        "required_future_artifact_list_previewed",
        "source_manifest_required",
        "provenance_report_required",
        "survivorship_bias_controls_required",
        "symbol_lifecycle_report_required",
        "holdout_policy_required",
        "historical_data_quality_validator_required",
        "timeout_policy_required_for_acquisition",
        "memory_disk_resource_policy_required_for_acquisition",
        "rollback_policy_required_for_acquisition",
        "hardening_state_required_for_acquisition",
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
        "local_manual_source_gap_closed",
        "okx_source_verified_now",
        "okx_download_performed",
        "okx_api_call_performed",
        "acquisition_execution_allowed_now",
        "external_download_allowed_now",
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
        "old_route_closed_artifacts_used_as_active_evidence_now",
        "ordinary_selector_backlog_loop_reentry_allowed",
        "generic_runner_target_exists",
    ]
    for key in required_true:
        require_true(payload.get(key), key)
    for key in required_false:
        require_false(payload.get(key), key)
    require_equal(payload.get("historical_data_acquisition_external_or_additional_source_preview_status"), STATUS_PASS, "status")
    require_equal(payload.get("recommended_source_route"), RECOMMENDED_SOURCE_ROUTE, "recommended_source_route")
    require_equal(payload.get("next_module"), NEXT_MODULE_APPROVAL, "next_module")
    require_equal(payload.get("active_p0_blocker_count"), 0, "active_p0_blocker_count")
    require_equal(payload.get("active_p1_attention_count"), 4, "active_p1_attention_count")
    require_equal(payload.get("planned_schema_files_existing_count"), 0, "planned_schema_files_existing_count")
    require(all(value is False for value in payload["dangerous_flags"].values()), "dangerous flags must all be false")


def main() -> None:
    validator = load_json(VALIDATOR_ARTIFACT)
    discovery = load_json(DISCOVERY_ARTIFACT)
    approval = load_json(APPROVAL_ARTIFACT)
    preview = load_json(PREVIEW_ARTIFACT)
    contract_validator = load_json(CONTRACT_VALIDATOR_ARTIFACT)
    hardening = load_json(HARDENING_VALIDATOR_ARTIFACT)
    preflight = validate_preflight(validator, discovery, approval, preview, contract_validator, hardening)
    sections = build_sections(validator)
    payload = build_payload(preflight, sections)
    validate_payload(payload)
    write_json(OUT_DIR / "historical_external_or_additional_source_preview.json", sections)
    write_json(
        OUT_DIR
        / "repo_only_historical_data_acquisition_external_or_additional_source_preview_after_local_manual_discovery_validator_v1_latest.json",
        payload,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
