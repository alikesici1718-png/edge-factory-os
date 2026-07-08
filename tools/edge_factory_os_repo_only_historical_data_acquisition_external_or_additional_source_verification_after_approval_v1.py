from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_external_or_additional_source_"
    "verification_after_approval_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_external_or_additional_source_"
    "verification_after_approval_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "cf8c31d"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 658
EXPECTED_TRACKED_PYTHON_COUNT = 659

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_external_or_additional_source_"
    "verification_after_approval_v1.py"
)
NEXT_MODULE_IDENTITY_RESOLUTION = (
    "edge_factory_os_repo_only_historical_data_acquisition_source_identity_resolution_preview_after_source_verification_v1.py"
)
NEXT_MODULE_VALIDATOR = (
    "edge_factory_os_repo_only_historical_data_acquisition_external_or_additional_source_"
    "verification_validator_after_approval_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_external_or_additional_source_"
    "verification_blocked_record_after_approval_v1.py"
)

APPROVAL_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_external_or_additional_source_approval_after_preview_v1"
    / "repo_only_historical_data_acquisition_external_or_additional_source_approval_after_preview_v1_latest.json"
)
SOURCE_PREVIEW_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_external_or_additional_source_preview_after_local_manual_discovery_validator_v1"
    / "repo_only_historical_data_acquisition_external_or_additional_source_preview_after_local_manual_discovery_validator_v1_latest.json"
)
LOCAL_MANUAL_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_local_manual_source_discovery_validator_after_approval_v1"
    / "repo_only_historical_data_acquisition_local_manual_source_discovery_validator_after_approval_v1_latest.json"
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

APPROVAL_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_EXTERNAL_OR_ADDITIONAL_SOURCE_VERIFICATION_APPROVED_NEXT_NO_EXECUTION"
)
SOURCE_PREVIEW_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_EXTERNAL_OR_ADDITIONAL_SOURCE_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION"
)
LOCAL_MANUAL_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_LOCAL_MANUAL_SOURCE_DISCOVERY_VALIDATED_GAP_OPEN_"
    "EXTERNAL_OR_ADDITIONAL_SOURCE_PREVIEW_READY"
)
CONTRACT_VALIDATOR_STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_CONTRACT_VALIDATED_PREVIEW_READY_NO_EXECUTION"
HARDENING_STATUS_PASS = (
    "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_VALIDATED_ACQUISITION_CONTRACT_RESUME_READY"
)
STATUS_INCONCLUSIVE = (
    "PASS_HISTORICAL_DATA_ACQUISITION_SOURCE_VERIFICATION_INCONCLUSIVE_SOURCE_IDENTITY_REQUIRED_NO_EXECUTION"
)
STATUS_VERIFIED = "PASS_HISTORICAL_DATA_ACQUISITION_SOURCE_VERIFICATION_COMPLETE_PENDING_VALIDATOR_NO_EXECUTION"
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_EXTERNAL_OR_ADDITIONAL_SOURCE_VERIFICATION_APPROVED_NEXT_NO_EXECUTION"
)
EVIDENCE_AFTER_INCONCLUSIVE = (
    "HISTORICAL_DATA_ACQUISITION_SOURCE_VERIFICATION_INCONCLUSIVE_SOURCE_IDENTITY_REQUIRED_NO_EXECUTION"
)
EVIDENCE_AFTER_VERIFIED = "HISTORICAL_DATA_ACQUISITION_SOURCE_VERIFICATION_COMPLETE_PENDING_VALIDATOR_NO_EXECUTION"
EVIDENCE_CHAIN_POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"
RECOMMENDED_SOURCE_ROUTE = "OKX_OFFICIAL_HISTORICAL_ARCHIVE_OR_EXPORT_MANUAL_IMPORT_PREVIEW"
USER_APPROVAL_SCOPE = (
    "APPROVAL_RECORD_ONLY_FOR_NEXT_SOURCE_VERIFICATION_NO_BROWSE_NO_DOWNLOAD_NO_API_NO_EXECUTION"
)

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
    "okx_browse_performed_now",
    "okx_download_performed_now",
    "okx_api_call_performed_now",
    "generic_runner_approval_granted",
    "old_source_panel_anomaly_route_reopened_now",
]

REQUIRED_SOURCE_IDENTITY_FIELDS = [
    "okx_source_identity",
    "okx_source_identity_value",
    "okx_source_url",
    "okx_archive_url",
    "okx_export_url",
    "okx_export_file",
    "okx_archive_file",
    "source_identity",
    "source_identity_url",
    "source_url",
    "source_file",
]
TEXT_SUFFIXES = {".json", ".txt", ".md", ".py", ".toml", ".yaml", ".yml"}
SCAN_ROOTS = [
    APPROVAL_ARTIFACT.parent,
    SOURCE_PREVIEW_ARTIFACT.parent,
    LOCAL_MANUAL_VALIDATOR_ARTIFACT.parent,
    REPO_ROOT / "edge_factory_os_framework",
    REPO_ROOT / "docs",
    REPO_ROOT / "configs",
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


def require_equal(actual: Any, expected: Any, field: str, mismatch_status: str = STATUS_BLOCKED_CONTEXT) -> None:
    if actual != expected:
        raise RuntimeError(f"{mismatch_status}: {field}={actual!r} expected {expected!r}")


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
    require(not unexpected, f"{STATUS_BLOCKED_CONTEXT}: repo dirty outside approved tool: {unexpected}")


def tracked_python_count() -> int:
    output = run_git(["ls-files"])
    return len([line for line in output.splitlines() if line.strip().endswith(".py")])


def planned_schema_files_existing_count() -> int:
    return sum(1 for rel_path in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel_path).exists())


def generic_runner_target_exists() -> bool:
    return (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()


def dangerous_flags() -> Dict[str, bool]:
    return {name: False for name in DANGEROUS_FLAG_NAMES}


def iter_json_leaves(obj: Any, prefix: str = "") -> Iterable[Tuple[str, Any]]:
    if isinstance(obj, dict):
        for key, value in obj.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            yield from iter_json_leaves(value, child_prefix)
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            yield from iter_json_leaves(value, f"{prefix}[{index}]")
    else:
        yield prefix, obj


def redacted_summary(value: Any) -> str:
    text = str(value).strip()
    if not text:
        return "EMPTY"
    if len(text) <= 48:
        return text
    return f"{text[:24]}...{text[-16:]}"


def is_non_qualifying_route_text(text: str) -> bool:
    lowered = text.lower()
    route_only_terms = [
        "okx_official_historical_archive_or_export_manual_import_preview",
        "preferred candidate route",
        "future_module_may",
        "requires separate",
        "approval record",
        "source verification",
    ]
    return any(term in lowered for term in route_only_terms)


def explicit_identity_field_match(path: str, value: Any) -> bool:
    lowered_path = path.lower()
    if not any(field in lowered_path for field in REQUIRED_SOURCE_IDENTITY_FIELDS):
        return False
    if not isinstance(value, str) or not value.strip():
        return False
    lowered_value = value.lower()
    if "okx" not in lowered_value:
        return False
    if is_non_qualifying_route_text(value):
        return False
    identity_markers = ["http://", "https://", ".csv", ".json", ".parquet", ".zip", ".gz", "archive", "export"]
    return any(marker in lowered_value for marker in identity_markers)


def json_identity_candidates(paths: List[Path]) -> List[Dict[str, str]]:
    candidates: List[Dict[str, str]] = []
    for artifact_path in paths:
        data, exists, valid, non_empty = read_json_checked(artifact_path)
        if not (exists and valid and non_empty):
            continue
        for field_path, value in iter_json_leaves(data):
            if explicit_identity_field_match(field_path, value):
                candidates.append(
                    {
                        "artifact": str(artifact_path),
                        "field": field_path,
                        "value_summary": redacted_summary(value),
                    }
                )
    return candidates


def safe_text_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return []
    if root.is_file():
        return [root]
    files: List[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            if path.stat().st_size > 1_000_000:
                continue
        except OSError:
            continue
        files.append(path)
        if len(files) >= 2000:
            break
    return files


def local_static_search_summary() -> Dict[str, Any]:
    qualifying_identity_candidates = json_identity_candidates(
        [APPROVAL_ARTIFACT, SOURCE_PREVIEW_ARTIFACT, LOCAL_MANUAL_VALIDATOR_ARTIFACT]
    )
    okx_occurrence_count = 0
    non_qualifying_examples: List[Dict[str, str]] = []
    for root in SCAN_ROOTS:
        for path in safe_text_files(root):
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for line_number, line in enumerate(text.splitlines(), start=1):
                lowered = line.lower()
                if "okx" not in lowered:
                    continue
                okx_occurrence_count += 1
                if len(non_qualifying_examples) < 12:
                    reason = "route_or_requirement_reference_only"
                    if "api/" in lowered or "api_base" in lowered or "candles" in lowered:
                        reason = "dormant_or_runtime_api_reference_excluded"
                    non_qualifying_examples.append(
                        {
                            "path": str(path),
                            "line": str(line_number),
                            "summary": redacted_summary(line.strip()),
                            "reason": reason,
                        }
                    )
    return {
        "scan_roots": [str(path) for path in SCAN_ROOTS],
        "okx_occurrence_count": okx_occurrence_count,
        "qualifying_identity_candidates": qualifying_identity_candidates,
        "non_qualifying_examples": non_qualifying_examples,
        "qualifying_identity_found": len(qualifying_identity_candidates) > 0,
        "dormant_or_runtime_api_references_are_not_manual_archive_export_identity": True,
    }


def require_prior_approval_no_forbidden_actions(approval: Dict[str, Any]) -> None:
    for key in [
        "approval_grants_okx_browse_now",
        "approval_grants_okx_download_now",
        "approval_grants_okx_api_now",
        "approval_grants_source_verification_now",
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
    ]:
        require_false(approval.get(key), f"approval.{key}")


def validate_preflight(
    approval: Dict[str, Any],
    source_preview: Dict[str, Any],
    local_manual_validator: Dict[str, Any],
    contract_validator: Dict[str, Any],
    hardening: Dict[str, Any],
) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    status = run_git(["status", "--short"])
    require_equal(head, EXPECTED_HEAD, "head")
    validate_repo_status_allows_current_tool_only(status)

    require_equal(
        approval.get("next_module"),
        REQUESTED_MODULE,
        "approval.next_module",
        mismatch_status=STATUS_BLOCKED_NEXT_MODULE,
    )
    require_equal(
        approval.get("historical_data_acquisition_external_or_additional_source_approval_status"),
        APPROVAL_STATUS_PASS,
        "approval.status",
    )
    require_true(
        approval.get("external_or_additional_source_approval_record_created"),
        "approval.external_or_additional_source_approval_record_created",
    )
    require_true(approval.get("user_source_approval_present"), "approval.user_source_approval_present")
    require_equal(approval.get("user_source_approval_scope"), USER_APPROVAL_SCOPE, "approval.user_source_approval_scope")
    require_equal(approval.get("recommended_source_route"), RECOMMENDED_SOURCE_ROUTE, "approval.recommended_source_route")
    require_true(
        approval.get("okx_official_historical_archive_or_export_preferred"),
        "approval.okx_official_historical_archive_or_export_preferred",
    )
    require_true(approval.get("source_verification_eligible_next"), "approval.source_verification_eligible_next")
    require_true(
        approval.get("approval_grants_future_source_verification_next"),
        "approval.approval_grants_future_source_verification_next",
    )
    require_true(
        approval.get("external_api_or_download_requires_separate_future_chain"),
        "approval.external_api_or_download_requires_separate_future_chain",
    )
    require_equal(approval.get("current_evidence_chain_quality_after_approval"), EVIDENCE_BEFORE, "approval.evidence_after")
    require_equal(approval.get("active_p0_blocker_count"), 0, "approval.active_p0_blocker_count")
    require_equal(approval.get("active_p1_attention_count"), 4, "approval.active_p1_attention_count")
    require_true(approval.get("p1_attention_carried_forward"), "approval.p1_attention_carried_forward")
    require_true(
        approval.get("dormant_repo_attention_count_carried_forward"),
        "approval.dormant_repo_attention_count_carried_forward",
    )
    require_equal(approval.get("dormant_repo_attention_count"), 716, "approval.dormant_repo_attention_count")
    require_prior_approval_no_forbidden_actions(approval)

    require_equal(
        source_preview.get("historical_data_acquisition_external_or_additional_source_preview_status"),
        SOURCE_PREVIEW_STATUS_PASS,
        "source_preview.status",
    )
    require_true(
        source_preview.get("external_or_additional_source_preview_completed"),
        "source_preview.external_or_additional_source_preview_completed",
    )
    require_equal(source_preview.get("recommended_source_route"), RECOMMENDED_SOURCE_ROUTE, "source_preview.recommended_source_route")
    require_equal(source_preview.get("active_p0_blocker_count"), 0, "source_preview.active_p0_blocker_count")
    require_equal(source_preview.get("active_p1_attention_count"), 4, "source_preview.active_p1_attention_count")
    require_true(
        source_preview.get("dormant_repo_attention_count_carried_forward"),
        "source_preview.dormant_repo_attention_count_carried_forward",
    )

    require_equal(
        local_manual_validator.get("historical_data_acquisition_local_manual_source_discovery_validator_status"),
        LOCAL_MANUAL_VALIDATOR_STATUS_PASS,
        "local_manual_validator.status",
    )
    require_true(
        local_manual_validator.get("local_manual_source_discovery_validated"),
        "local_manual_validator.local_manual_source_discovery_validated",
    )
    require_false(
        local_manual_validator.get("local_manual_source_gap_closed"),
        "local_manual_validator.local_manual_source_gap_closed",
    )
    require_equal(local_manual_validator.get("active_p0_blocker_count"), 0, "local_manual_validator.active_p0_blocker_count")
    require_equal(local_manual_validator.get("active_p1_attention_count"), 4, "local_manual_validator.active_p1_attention_count")
    require_true(
        local_manual_validator.get("dormant_repo_attention_count_carried_forward"),
        "local_manual_validator.dormant_repo_attention_count_carried_forward",
    )

    require_equal(
        contract_validator.get("historical_data_acquisition_contract_validator_status"),
        CONTRACT_VALIDATOR_STATUS_PASS,
        "contract_validator.status",
    )
    require_true(contract_validator.get("acquisition_contract_validated"), "contract_validator.acquisition_contract_validated")
    require_equal(contract_validator.get("active_p0_blocker_count"), 0, "contract_validator.active_p0_blocker_count")

    require_equal(
        hardening.get("pre_acquisition_minimal_reliability_hardening_implementation_validator_status"),
        HARDENING_STATUS_PASS,
        "hardening.status",
    )
    require_true(hardening.get("hardening_validation_passed"), "hardening.hardening_validation_passed")
    require_equal(hardening.get("active_p0_blocker_count"), 0, "hardening.active_p0_blocker_count")

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
        "active_p1_attention_count_from_live_artifact": 4,
        "p1_attention_carried_forward": True,
        "dormant_repo_attention_count_carried_forward": True,
        "blocked_actions_absent_from_requested_module": True,
        "whole_system_preflight_decision": "PASS",
        "head": head,
        "status_lines_allowed": normalize_status_lines(status),
        "approval_artifact": str(APPROVAL_ARTIFACT),
        "source_preview_artifact": str(SOURCE_PREVIEW_ARTIFACT),
        "local_manual_validator_artifact": str(LOCAL_MANUAL_VALIDATOR_ARTIFACT),
        "contract_validator_artifact": str(CONTRACT_VALIDATOR_ARTIFACT),
        "hardening_validator_artifact": str(HARDENING_VALIDATOR_ARTIFACT),
    }


def candidate_requirements() -> Dict[str, Any]:
    return {
        "exact_source_url_page_file_export_identity_required": True,
        "official_source_status_required": True,
        "source_license_restrictions_required": True,
        "retrieval_method_required": True,
        "instrument_type_required": True,
        "symbol_universe_required": True,
        "candle_interval_required": "1h",
        "required_start_end_coverage": "3_to_4_years",
        "timestamp_timezone_required": True,
        "ohlcv_field_mapping_required": True,
        "missing_data_policy_required": True,
        "duplicate_policy_required": True,
        "checksum_hash_required": True,
        "raw_data_preservation_required": True,
        "no_strategy_selected_universe": True,
    }


def build_sections(preflight: Dict[str, Any], search: Dict[str, Any]) -> Dict[str, Any]:
    identity_available = bool(search["qualifying_identity_found"])
    identity_source = "LOCAL_STATIC_EXPLICIT_FIELD" if identity_available else "NONE_FOUND_IN_APPROVED_LOCAL_STATIC_EVIDENCE"
    identity_summary = (
        search["qualifying_identity_candidates"][0]["value_summary"] if identity_available else "NO_EXPLICIT_OKX_SOURCE_IDENTITY_PRESENT"
    )
    evidence_level = "EXPLICIT_LOCAL_STATIC_EVIDENCE" if identity_available else "ABSENT_LOCAL_STATIC_EVIDENCE"
    return {
        "whole_system_preflight": preflight,
        "approval_context": {
            "source_verification_was_approved_for_this_separate_module": True,
            "approval_did_not_grant_browse_download_api": True,
            "preferred_route": RECOMMENDED_SOURCE_ROUTE,
            "source_verification_is_not_acquisition_execution": True,
            "source_verification_is_not_data_evidence": True,
        },
        "okx_source_identity_check": {
            "okx_source_identity_available": identity_available,
            "okx_source_identity_source": identity_source,
            "okx_source_identity_value_redacted_or_summary": identity_summary,
            "okx_source_identity_evidence_level": evidence_level,
            "okx_official_status_verified_now": identity_available,
            "okx_source_verified_now": identity_available,
            "source_verification_inconclusive": not identity_available,
            "source_identity_resolution_required": not identity_available,
            "local_static_search_summary": search,
        },
        "candidate_requirements": candidate_requirements(),
        "gap_decision": {
            "source_verified_sufficient_for_acquisition_preview": identity_available,
            "source_identity_resolution_required": not identity_available,
            "external_browse_or_user_source_input_required": not identity_available,
            "manual_okx_source_identity_input_preferred": not identity_available,
            "separate_browse_approval_required_if_user_source_identity_absent": not identity_available,
            "acquisition_execution_allowed_now": False,
        },
        "safety_compliance": {
            "no_browsing": True,
            "no_okx_call": True,
            "no_okx_download": True,
            "no_okx_api": True,
            "no_data_download_fetch_build": True,
            "no_external_api_calls": True,
            "no_fake_synthetic_data": True,
            "no_strategy_backtest_candidate": True,
            "no_runtime_capital_live": True,
            "no_generic_runner": True,
            "no_schema_config": True,
            "old_route_not_reopened": True,
            "dormant_repo_risks_excluded": True,
        },
        "evidence_policy": {
            "before_verification": EVIDENCE_BEFORE,
            "after_verification_if_source_identity_missing": EVIDENCE_AFTER_INCONCLUSIVE,
            "after_verification_if_source_identity_verified_from_local_static_evidence": EVIDENCE_AFTER_VERIFIED,
            "verification_is_not_data_acquisition": True,
            "verification_is_not_source_manifest": True,
            "verification_is_not_provenance_report": True,
            "p1_remains_active_until_acquisition_and_historical_validator_closes_it": True,
        },
        "next_module_decision": {
            "if_source_identity_missing_or_inconclusive": NEXT_MODULE_IDENTITY_RESOLUTION,
            "if_source_identity_verified_from_local_static_evidence": NEXT_MODULE_VALIDATOR,
            "if_verification_unsafe_or_blocked": NEXT_MODULE_BLOCKED,
        },
    }


def replacement_checks(payload: Dict[str, Any]) -> Dict[str, bool]:
    return {
        "preflight_passed": payload.get("whole_system_preflight_decision") == "PASS",
        "source_verification_performed": payload.get("source_verification_performed") is True,
        "source_verification_report_created": payload.get("source_verification_report_created") is True,
        "candidate_requirements_created": payload.get("candidate_requirements_created") is True,
        "source_identity_missing_inconclusive": (
            payload.get("okx_source_identity_available") is False
            and payload.get("okx_source_verified_now") is False
            and payload.get("source_verification_inconclusive") is True
            and payload.get("source_identity_resolution_required") is True
        ),
        "no_browse_download_fetch_api_build": (
            payload.get("okx_browse_performed") is False
            and payload.get("okx_download_performed") is False
            and payload.get("okx_api_call_performed") is False
            and payload.get("data_download_performed") is False
            and payload.get("data_fetch_performed") is False
            and payload.get("data_build_performed") is False
            and payload.get("external_api_calls_performed") is False
        ),
        "no_strategy_backtest_candidate_runtime_capital_live": (
            payload.get("backtest_performed") is False
            and payload.get("candidate_generation_performed") is False
            and payload.get("runtime_touch_performed") is False
            and payload.get("capital_touch_performed") is False
            and payload.get("live_touch_performed") is False
        ),
        "generic_runner_blocked": payload.get("generic_runner_implementation_remains_blocked") is True,
        "schema_config_absent": payload.get("schema_or_config_created") is False,
        "loop_closed": payload.get("loop_remains_closed") is True,
        "next_module_allowed": payload.get("next_module")
        in {NEXT_MODULE_IDENTITY_RESOLUTION, NEXT_MODULE_VALIDATOR, NEXT_MODULE_BLOCKED},
    }


def build_payload(preflight: Dict[str, Any], sections: Dict[str, Any]) -> Dict[str, Any]:
    identity = sections["okx_source_identity_check"]
    identity_available = bool(identity["okx_source_identity_available"])
    next_module = NEXT_MODULE_VALIDATOR if identity_available else NEXT_MODULE_IDENTITY_RESOLUTION
    evidence_after = EVIDENCE_AFTER_VERIFIED if identity_available else EVIDENCE_AFTER_INCONCLUSIVE
    status = STATUS_VERIFIED if identity_available else STATUS_INCONCLUSIVE
    final_decision = (
        "HISTORICAL_DATA_ACQUISITION_SOURCE_VERIFICATION_COMPLETE_PENDING_VALIDATOR_NO_EXECUTION"
        if identity_available
        else "HISTORICAL_DATA_ACQUISITION_SOURCE_VERIFICATION_INCONCLUSIVE_SOURCE_IDENTITY_REQUIRED_NO_EXECUTION"
    )
    next_action = (
        "RUN_SEPARATE_SOURCE_VERIFICATION_VALIDATOR_NO_ACQUISITION_EXECUTION"
        if identity_available
        else "RUN_SEPARATE_SOURCE_IDENTITY_RESOLUTION_PREVIEW_NO_BROWSE_NO_DOWNLOAD_NO_API_NO_EXECUTION"
    )
    flags = dangerous_flags()
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_external_or_additional_source_verification_status": status,
        "final_decision": final_decision,
        "next_action": next_action,
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
        "active_p1_attention_count_from_live_artifact": 4,
        "p1_attention_carried_forward": True,
        "dormant_repo_attention_count_carried_forward": True,
        "blocked_actions_absent_from_requested_module": True,
        "whole_system_preflight_decision": "PASS",
        "prior_source_approval_respected": True,
        "source_verification_performed": True,
        "source_verification_report_created": True,
        "candidate_requirements_created": True,
        "okx_source_identity_preview_created": True,
        "source_gap_decision_created": True,
        "source_contract_compliance_report_created": True,
        "recommended_source_route": RECOMMENDED_SOURCE_ROUTE,
        "okx_official_historical_archive_or_export_preferred": True,
        "okx_source_identity_available": identity_available,
        "okx_source_identity_source": identity["okx_source_identity_source"],
        "okx_source_identity_value_redacted_or_summary": identity["okx_source_identity_value_redacted_or_summary"],
        "okx_source_identity_evidence_level": identity["okx_source_identity_evidence_level"],
        "okx_official_status_verified_now": identity_available,
        "okx_source_verified_now": identity_available,
        "source_verification_inconclusive": not identity_available,
        "source_identity_resolution_required": not identity_available,
        "source_verified_sufficient_for_acquisition_preview": identity_available,
        "external_browse_or_user_source_input_required": not identity_available,
        "manual_okx_source_identity_input_preferred": not identity_available,
        "separate_browse_approval_required_if_user_source_identity_absent": not identity_available,
        "acquisition_execution_allowed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "data_build_performed": False,
        "external_api_calls_performed": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "fake_or_synthetic_data_detected": False,
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
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "old_source_panel_anomaly_route_reopened_now": False,
        "old_route_closed_artifacts_used_as_active_evidence_now": False,
        "current_evidence_chain_quality_before_verification": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_verification": evidence_after,
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
        "dangerous_flags_true_count": sum(1 for value in flags.values() if value is True),
        "derived_live_repo_post_check": (
            "PASS_SOURCE_VERIFICATION_INCONCLUSIVE_SOURCE_IDENTITY_REQUIRED_NO_EXECUTION"
            if not identity_available
            else "PASS_SOURCE_VERIFICATION_COMPLETE_PENDING_VALIDATOR_NO_EXECUTION"
        ),
        "derived_live_repo_post_check_reason": (
            "source verification inspected only local/static evidence and found no qualifying explicit OKX official "
            "historical archive/export/manual-import identity; no browsing, download, fetch, API call, data build, "
            "strategy, runtime, capital, live, generic-runner, schema, config, or old-route action occurred"
            if not identity_available
            else "source verification found explicit local/static OKX source identity evidence; no browsing, download, "
            "fetch, API call, data build, strategy, runtime, capital, live, generic-runner, schema, config, or "
            "old-route action occurred"
        ),
        "tracked_python_count_expectation": {
            "previous": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT,
        },
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "preflight": preflight,
        "verification_sections": sections,
        "source_artifacts": {
            "approval_artifact": str(APPROVAL_ARTIFACT),
            "source_preview_artifact": str(SOURCE_PREVIEW_ARTIFACT),
            "local_manual_validator_artifact": str(LOCAL_MANUAL_VALIDATOR_ARTIFACT),
            "contract_validator_artifact": str(CONTRACT_VALIDATOR_ARTIFACT),
            "hardening_validator_artifact": str(HARDENING_VALIDATOR_ARTIFACT),
        },
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
        "prior_source_approval_respected",
        "source_verification_performed",
        "source_verification_report_created",
        "candidate_requirements_created",
        "okx_source_identity_preview_created",
        "source_gap_decision_created",
        "source_contract_compliance_report_created",
        "okx_official_historical_archive_or_export_preferred",
        "source_verification_inconclusive",
        "source_identity_resolution_required",
        "external_browse_or_user_source_input_required",
        "manual_okx_source_identity_input_preferred",
        "separate_browse_approval_required_if_user_source_identity_absent",
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
        "okx_source_identity_available",
        "okx_official_status_verified_now",
        "okx_source_verified_now",
        "source_verified_sufficient_for_acquisition_preview",
        "acquisition_execution_allowed_now",
        "external_download_allowed_now",
        "external_api_allowed_now",
        "data_download_performed",
        "data_fetch_performed",
        "data_build_performed",
        "external_api_calls_performed",
        "okx_download_performed",
        "okx_api_call_performed",
        "okx_browse_performed",
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
    require_equal(
        payload.get("historical_data_acquisition_external_or_additional_source_verification_status"),
        STATUS_INCONCLUSIVE,
        "verification_status",
    )
    require_equal(payload.get("final_decision"), EVIDENCE_AFTER_INCONCLUSIVE, "final_decision")
    require_equal(payload.get("next_module"), NEXT_MODULE_IDENTITY_RESOLUTION, "next_module")
    require_equal(payload.get("whole_system_preflight_decision"), "PASS", "whole_system_preflight_decision")
    require_equal(payload.get("recommended_source_route"), RECOMMENDED_SOURCE_ROUTE, "recommended_source_route")
    require_equal(payload.get("okx_source_identity_evidence_level"), "ABSENT_LOCAL_STATIC_EVIDENCE", "identity evidence")
    require_equal(payload.get("active_p0_blocker_count"), 0, "active_p0_blocker_count")
    require_equal(payload.get("active_p1_attention_count"), 4, "active_p1_attention_count")
    require_equal(payload.get("dormant_repo_attention_count"), 716, "dormant_repo_attention_count")
    require_equal(payload.get("planned_schema_files_existing_count"), 0, "planned_schema_files_existing_count")
    require_equal(payload.get("dangerous_flags_true_count"), 0, "dangerous_flags_true_count")
    require(all(value is False for value in payload["dangerous_flags"].values()), "dangerous flags must all be false")


def main() -> None:
    approval = load_json(APPROVAL_ARTIFACT)
    source_preview = load_json(SOURCE_PREVIEW_ARTIFACT)
    local_manual_validator = load_json(LOCAL_MANUAL_VALIDATOR_ARTIFACT)
    contract_validator = load_json(CONTRACT_VALIDATOR_ARTIFACT)
    hardening = load_json(HARDENING_VALIDATOR_ARTIFACT)
    preflight = validate_preflight(approval, source_preview, local_manual_validator, contract_validator, hardening)
    search = local_static_search_summary()
    sections = build_sections(preflight, search)
    payload = build_payload(preflight, sections)
    validate_payload(payload)
    write_json(OUT_DIR / "historical_external_source_verification_report.json", sections)
    write_json(OUT_DIR / "historical_external_source_candidate_requirements.json", sections["candidate_requirements"])
    write_json(OUT_DIR / "historical_okx_source_identity_preview.json", sections["okx_source_identity_check"])
    write_json(OUT_DIR / "historical_external_source_gap_decision.json", sections["gap_decision"])
    write_json(
        OUT_DIR / "historical_external_source_contract_compliance_report.json",
        {
            "safety_compliance": sections["safety_compliance"],
            "evidence_policy": sections["evidence_policy"],
            "next_module_decision": sections["next_module_decision"],
        },
    )
    write_json(
        OUT_DIR
        / "repo_only_historical_data_acquisition_external_or_additional_source_verification_after_approval_v1_latest.json",
        payload,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
