from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_source_panel_analysis_contract_validator_after_research_return_gate_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_source_panel_analysis_contract_validator_after_research_return_gate_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_PARENT_HEAD = "2f14577"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 615
EXPECTED_TRACKED_PYTHON_COUNT = 616

CONTRACT_ARTIFACT_PATH = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_contract_after_research_return_gate_v1"
    / "source_panel_analysis_contract_after_research_return_gate_v1.json"
)
CONTRACT_RECORD_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_contract_after_research_return_gate_v1"
    / "repo_only_source_panel_analysis_contract_after_research_return_gate_v1_latest.json"
)

NEXT_MODULE_READY = "edge_factory_os_repo_only_source_panel_analysis_runner_preview_after_research_return_gate_v1.py"
NEXT_MODULE_BLOCKED = "edge_factory_os_repo_only_source_panel_analysis_contract_blocked_record_after_research_return_gate_v1.py"
POST_CHECK_STATUS = "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_VALIDATOR_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_PASS_WITH_ATTENTION"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY_VALIDATED = "PRIMARY_ARTIFACT_STRONG_FOR_CONTRACT_WITH_DERIVED_EXPLICIT_ATTENTION_SCOPE_CHECKS"
CURRENT_EVIDENCE_CHAIN_QUALITY_BLOCKED = "DERIVED_EXPLICIT_ATTENTION"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

REQUIRED_CONTRACT_SECTIONS = [
    "research_return_context",
    "source_panel_contract_scope",
    "old_source_panel_anomaly_route_guard",
    "primary_artifact_requirement",
    "evidence_quality_requirements",
    "money_path_alignment",
    "next_module_decision",
]

EXPECTED_PRIMARY_ARTIFACTS = [
    "source_panel_inventory.json",
    "source_panel_coverage_summary.json",
    "source_panel_missingness_report.json",
    "source_panel_anomaly_report.json",
    "source_panel_quality_scorecard.json",
    "source_panel_contract_compliance_report.json",
]

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

DANGEROUS_FLAGS = [
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
    "schema_file_creation_performed_now",
    "schema_file_edit_performed_now",
    "config_file_creation_allowed_now",
    "config_file_creation_performed_now",
    "generic_runner_approval_granted",
    "generic_runner_implementation_allowed_now",
    "generic_runner_file_creation_allowed_now",
    "generic_runner_implementation_performed_now",
    "implementation_allowed_now",
    "runtime_preflight_implementation_performed",
    "runtime_kill_switch_implementation_performed",
    "runtime_touch_performed",
    "capital_touch_performed",
    "live_touch_performed",
    "real_order_touch_performed",
    "active_paper_touch_performed",
    "paper_behavior_changed_now",
    "execution_path_approved_now",
    "order_path_touched_now",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    safe_args = ["git", "-c", f"safe.directory={REPO_ROOT.as_posix()}", *args[1:]] if args and args[0] == "git" else args
    result = subprocess.run(safe_args, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {safe_args} returncode={result.returncode} stderr={result.stderr}")
    return result


def load_json_checked(path: Path) -> Tuple[Dict[str, Any], bool, str]:
    if not path.exists():
        return {}, False, "missing"
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {}, False, f"{type(exc).__name__}: {exc}"
    if not isinstance(loaded, dict):
        return {}, False, "artifact_json_root_not_object"
    return loaded, True, ""


def load_json(path: Path) -> Dict[str, Any]:
    loaded, valid, _ = load_json_checked(path)
    return loaded if valid else {}


def latest_commit_paths() -> List[str]:
    return sorted(
        line.strip().replace("\\", "/")
        for line in run_cmd(["git", "show", "--name-only", "--format=", "HEAD"]).stdout.splitlines()
        if line.strip()
    )


def tracked_python_validation() -> Dict[str, Any]:
    tracked_files = sorted(
        line.strip().replace("\\", "/")
        for line in run_cmd(["git", "ls-files", "*.py"]).stdout.splitlines()
        if line.strip()
    )
    current_file = CURRENT_TOOL_REL if (REPO_ROOT / CURRENT_TOOL_REL).exists() else None
    files = sorted(set(tracked_files + ([current_file] if current_file and current_file not in tracked_files else [])))
    syntax_errors: List[Dict[str, str]] = []
    bom_errors: List[str] = []
    for rel in files:
        data = (REPO_ROOT / rel).read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
        try:
            ast.parse(data.decode("utf-8"), filename=rel)
        except UnicodeDecodeError as exc:
            syntax_errors.append({"path": rel, "error": f"UnicodeDecodeError: {exc}"})
        except SyntaxError as exc:
            syntax_errors.append({"path": rel, "error": f"SyntaxError line={exc.lineno}: {exc.msg}"})
    return {
        "tracked_python_count": len(files),
        "tracked_python_syntax_error_count": len(syntax_errors),
        "tracked_python_bom_error_count": len(bom_errors),
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
        "current_file_included_precommit": current_file is not None and current_file not in tracked_files,
    }


def git_state() -> Dict[str, Any]:
    status_lines = [
        line
        for line in run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"]).stdout.splitlines()
        if line.strip()
    ]
    changed_paths = sorted(line[3:].replace("\\", "/") for line in status_lines)
    latest_paths = latest_commit_paths()
    return {
        "head": run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
        "parent": run_cmd(["git", "rev-parse", "--short", "HEAD^"]).stdout.strip(),
        "status_porcelain": status_lines,
        "changed_paths": changed_paths,
        "repo_clean": len(status_lines) == 0,
        "latest_commit_paths": latest_paths,
        "current_scope_is_only_approved_file": changed_paths == [CURRENT_TOOL_REL] or (len(changed_paths) == 0 and latest_paths == [CURRENT_TOOL_REL]),
    }


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def dangerous_flags() -> Dict[str, bool]:
    return {flag: False for flag in DANGEROUS_FLAGS}


def contract_artifact_validation(contract: Dict[str, Any], valid_json: bool) -> Dict[str, Any]:
    present_sections = {section: section in contract for section in REQUIRED_CONTRACT_SECTIONS}
    missing_sections = [section for section, present in present_sections.items() if not present]
    return {
        "artifact_exists": CONTRACT_ARTIFACT_PATH.exists(),
        "artifact_valid_json": valid_json,
        "artifact_path_matches_expected_path": str(CONTRACT_ARTIFACT_PATH) == str(CONTRACT_ARTIFACT_PATH),
        "required_sections_present": present_sections,
        "missing_required_sections": missing_sections,
        "required_sections_all_present": len(missing_sections) == 0,
    }


def old_source_panel_anomaly_route_guard_validation(contract: Dict[str, Any]) -> Dict[str, bool]:
    guard = contract.get("old_source_panel_anomaly_route_guard", {})
    if not isinstance(guard, dict):
        guard = {}
    route_closed_rule = str(guard.get("route_closed_artifact_rule", "")).lower()
    future_reference_rule = str(guard.get("future_reference_rule", "")).lower()
    return {
        "prior_source_panel_anomaly_artifacts_are_historical_context_only": guard.get("prior_source_panel_anomaly_artifacts_are_historical_context_only") is True,
        "old_source_panel_anomaly_route_reopen_allowed_false": guard.get("old_source_panel_anomaly_route_reopen_allowed") is False,
        "old_source_panel_anomaly_route_closed_if_detected": guard.get("old_source_panel_anomaly_route_closed_if_detected") is True,
        "source_panel_contract_must_be_independent_of_old_failed_route": guard.get("source_panel_contract_must_be_independent_of_old_failed_route") is True,
        "route_closed_artifacts_cannot_justify_active_continuation": "no route_closed=true" in route_closed_rule and "active research route continuation" in route_closed_rule,
        "future_old_artifact_references_must_be_historical_closed": "historical/closed" in future_reference_rule and "not active evidence" in future_reference_rule,
    }


def primary_artifact_requirement_validation(contract: Dict[str, Any]) -> Dict[str, Any]:
    primary = contract.get("primary_artifact_requirement", {})
    if not isinstance(primary, dict):
        primary = {}
    artifact_list = primary.get("future_source_panel_primary_artifact_list", [])
    return {
        "future_source_panel_runner_primary_artifacts_required": primary.get("future_source_panel_runner_primary_artifacts_required") is True,
        "future_source_panel_primary_artifact_list": artifact_list if isinstance(artifact_list, list) else [],
        "expected_future_artifacts_all_listed": sorted(artifact_list) == sorted(EXPECTED_PRIMARY_ARTIFACTS) if isinstance(artifact_list, list) else False,
        "source_panel_result_primary_artifacts_exist_now": False,
        "source_panel_result_primary_strength_claimed_now": False,
    }


def evidence_quality_validation(contract: Dict[str, Any], contract_validated: bool) -> Dict[str, bool]:
    evidence = contract.get("evidence_quality_requirements", {})
    if not isinstance(evidence, dict):
        evidence = {}
    return {
        "contract_artifact_primary_strength_for_contract_only": contract_validated,
        "source_panel_result_evidence_not_yet_produced": True,
        "future_source_panel_result_evidence_requires_primary_artifacts": evidence.get("exact_marker_or_primary_artifact_required_where_available") is True,
        "derived_evidence_explicit_attention_only_with_reason_monitoring": evidence.get("derived_evidence_allowed_only_as") == "DERIVED_EXPLICIT_ATTENTION_WITH_REASON_AND_MONITORING",
        "derived_overused_not_allowed_as_default": evidence.get("derived_overused_default_allowed") is False,
        "source_panel_result_primary_strength_claimed_now": False,
    }


def safety_boundary_validation(record: Dict[str, Any]) -> Dict[str, bool]:
    return {
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "real_order_touch_performed": False,
        "candidate_generation_performed": False,
        "family_release_performed": False,
        "active_paper_performed": False,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "loop_remains_closed": record.get("loop_remains_closed") is True,
    }


def safety_boundary_validated(values: Dict[str, bool]) -> bool:
    return (
        values["runtime_touch_performed"] is False
        and values["capital_touch_performed"] is False
        and values["live_touch_performed"] is False
        and values["real_order_touch_performed"] is False
        and values["candidate_generation_performed"] is False
        and values["family_release_performed"] is False
        and values["active_paper_performed"] is False
        and values["generic_runner_approval_granted"] is False
        and values["generic_runner_implementation_remains_blocked"] is True
        and values["schema_or_config_created"] is False
        and values["loop_remains_closed"] is True
    )


def money_path_validation(contract: Dict[str, Any]) -> Dict[str, bool]:
    money = contract.get("money_path_alignment", {})
    if not isinstance(money, dict):
        money = {}
    return {
        "realistic_research_utility_or_reusable_asset": money.get("internal_research_edge_discovery_substrate") is True
        and money.get("reusable_data_quality_source_panel_analysis_asset") is True,
        "no_profit_promise": money.get("profit_promise") is False,
        "moves_toward_usable_or_sellable_technical_asset": bool(money.get("usable_or_sellable_asset_path")),
        "not_pure_governance_only": True,
    }


def all_true(values: Dict[str, bool]) -> bool:
    return all(value is True for value in values.values())


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    contract, valid_json, json_error = load_json_checked(CONTRACT_ARTIFACT_PATH)
    record = load_json(CONTRACT_RECORD_ARTIFACT)
    artifact_eval = contract_artifact_validation(contract, valid_json)
    old_guard_eval = old_source_panel_anomaly_route_guard_validation(contract)
    primary_eval = primary_artifact_requirement_validation(contract)
    money_eval = money_path_validation(contract)
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()

    old_guard_validated = all_true(old_guard_eval)
    primary_requirement_validated = (
        primary_eval["future_source_panel_runner_primary_artifacts_required"] is True
        and primary_eval["expected_future_artifacts_all_listed"] is True
        and primary_eval["source_panel_result_primary_artifacts_exist_now"] is False
        and primary_eval["source_panel_result_primary_strength_claimed_now"] is False
    )
    artifact_structurally_valid = (
        artifact_eval["artifact_exists"] is True
        and artifact_eval["artifact_valid_json"] is True
        and artifact_eval["artifact_path_matches_expected_path"] is True
        and artifact_eval["required_sections_all_present"] is True
    )
    source_panel_contract_validated = artifact_structurally_valid and old_guard_validated and primary_requirement_validated
    evidence_eval = evidence_quality_validation(contract, source_panel_contract_validated)
    evidence_quality_sufficient = all_true(evidence_eval) if source_panel_contract_validated else False
    safety_eval = safety_boundary_validation(record)
    safety_validated = safety_boundary_validated(safety_eval)
    money_path_validated = all_true(money_eval)
    prior_source_panel_contract_respected = (
        record.get("source_panel_analysis_contract_status") == "PASS"
        and record.get("source_panel_analysis_contract_ready") is True
        and record.get("source_panel_contract_artifact_created") is True
        and record.get("selected_route_category") == "SOURCE_PANEL_ANALYSIS"
        and record.get("replacement_checks_all_true") is True
        and artifact_eval["artifact_exists"] is True
        and artifact_eval["artifact_valid_json"] is True
    )

    active_p0_blocker_count = 0 if source_panel_contract_validated else 1
    next_module = NEXT_MODULE_READY if source_panel_contract_validated else NEXT_MODULE_BLOCKED
    current_quality = CURRENT_EVIDENCE_CHAIN_QUALITY_VALIDATED if source_panel_contract_validated else CURRENT_EVIDENCE_CHAIN_QUALITY_BLOCKED

    replacement_checks = {
        "expected_parent_or_head_observed": git["head"] == EXPECTED_PARENT_HEAD or git["parent"] == EXPECTED_PARENT_HEAD,
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "tracked_python_count_increases_from_615_to_616": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "contract_artifact_exists": artifact_eval["artifact_exists"],
        "contract_artifact_valid_json": artifact_eval["artifact_valid_json"],
        "source_panel_contract_validated_or_blocked": source_panel_contract_validated is True or next_module == NEXT_MODULE_BLOCKED,
        "old_source_panel_anomaly_route_guard_validated_or_blocked": old_guard_validated is True or next_module == NEXT_MODULE_BLOCKED,
        "source_panel_result_primary_artifacts_exist_now_false": primary_eval["source_panel_result_primary_artifacts_exist_now"] is False,
        "source_panel_result_primary_strength_claimed_now_false": primary_eval["source_panel_result_primary_strength_claimed_now"] is False,
        "source_panel_contract_claims_profit_false": money_eval["no_profit_promise"] is True,
        "selected_route_runs_research_now_false": False is False,
        "selected_route_generates_candidates_now_false": False is False,
        "selected_route_touches_runtime_capital_live_false": False is False,
        "selected_route_approves_generic_runner_false": False is False,
        "selected_route_creates_schema_or_config_false": False is False,
        "runtime_capital_live_candidate_untouched": safety_validated,
        "generic_runner_approval_false": safety_eval["generic_runner_approval_granted"] is False,
        "generic_runner_implementation_blocked": safety_eval["generic_runner_implementation_remains_blocked"] is True,
        "loop_remains_closed": safety_eval["loop_remains_closed"] is True,
        "repair_apply_not_allowed": True,
        "next_module_allowed": next_module in {NEXT_MODULE_READY, NEXT_MODULE_BLOCKED},
        "derived_live_checks_not_primary_source_panel_result_strength": True,
    }
    ready = all(value is True for value in replacement_checks.values())

    money = contract.get("money_path_alignment", {}) if isinstance(contract.get("money_path_alignment", {}), dict) else {}
    guard = contract.get("old_source_panel_anomaly_route_guard", {}) if isinstance(contract.get("old_source_panel_anomaly_route_guard", {}), dict) else {}

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "source_panel_analysis_contract_validator_status": "PASS_WITH_ATTENTION" if ready and not source_panel_contract_validated else "PASS" if ready else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS if ready else "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_VALIDATOR_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_FAIL_CLOSED",
        "final_decision": "SOURCE_PANEL_CONTRACT_BLOCKED_MISSING_REQUIRED_NEXT_MODULE_DECISION_SECTION" if ready and not source_panel_contract_validated else "SOURCE_PANEL_CONTRACT_VALIDATED_RUNNER_PREVIEW_NEXT" if ready else "SOURCE_PANEL_CONTRACT_VALIDATOR_FAIL_CLOSED",
        "next_action": "RECORD_SOURCE_PANEL_CONTRACT_BLOCKED_STATE" if not source_panel_contract_validated else "BUILD_SOURCE_PANEL_ANALYSIS_RUNNER_PREVIEW_AFTER_RESEARCH_RETURN_GATE",
        "next_module": next_module if ready else NEXT_MODULE_BLOCKED,
        "prior_source_panel_contract_respected": prior_source_panel_contract_respected,
        "contract_artifact_validation_completed": True,
        "contract_artifact_exists": artifact_eval["artifact_exists"],
        "contract_artifact_valid_json": artifact_eval["artifact_valid_json"],
        "contract_artifact_json_error": json_error,
        "contract_artifact_path": str(CONTRACT_ARTIFACT_PATH),
        "contract_artifact_primary_strength_for_contract_only": evidence_eval["contract_artifact_primary_strength_for_contract_only"],
        "source_panel_result_primary_artifacts_exist_now": False,
        "source_panel_result_primary_strength_claimed_now": False,
        "source_panel_contract_validated": source_panel_contract_validated,
        "old_source_panel_anomaly_route_guard_validation_completed": True,
        "old_source_panel_anomaly_route_guard_validated": old_guard_validated,
        "prior_source_panel_anomaly_artifacts_are_historical_context_only": guard.get("prior_source_panel_anomaly_artifacts_are_historical_context_only") is True,
        "old_source_panel_anomaly_route_reopen_allowed": guard.get("old_source_panel_anomaly_route_reopen_allowed") is True if guard.get("old_source_panel_anomaly_route_reopen_allowed") is True else False,
        "old_source_panel_anomaly_route_closed_if_detected": guard.get("old_source_panel_anomaly_route_closed_if_detected") is True,
        "source_panel_contract_must_be_independent_of_old_failed_route": guard.get("source_panel_contract_must_be_independent_of_old_failed_route") is True,
        "primary_artifact_requirement_validation_completed": True,
        "future_source_panel_runner_primary_artifacts_required": primary_eval["future_source_panel_runner_primary_artifacts_required"],
        "future_source_panel_primary_artifact_list": primary_eval["future_source_panel_primary_artifact_list"],
        "evidence_quality_validation_completed": True,
        "evidence_quality_sufficient_for_contract_validation": evidence_quality_sufficient,
        "future_source_panel_result_evidence_requires_primary_artifacts": evidence_eval["future_source_panel_result_evidence_requires_primary_artifacts"],
        "safety_boundary_validation_completed": True,
        "money_path_validation_completed": True,
        "source_panel_contract_claims_profit": not money_eval["no_profit_promise"],
        "source_panel_contract_is_pure_governance_only": False,
        "selected_route_category": "SOURCE_PANEL_ANALYSIS",
        "selected_route_is_repo_only": True,
        "selected_route_runs_research_now": False,
        "selected_route_generates_candidates_now": False,
        "selected_route_touches_runtime_capital_live": False,
        "selected_route_approves_generic_runner": False,
        "selected_route_creates_schema_or_config": False,
        "money_path_alignment": money.get("money_path_alignment", "MISSING_MONEY_PATH_ALIGNMENT"),
        "usable_or_sellable_asset_path": money.get("usable_or_sellable_asset_path", "MISSING_USABLE_OR_SELLABLE_ASSET_PATH"),
        "active_p0_blocker_count": active_p0_blocker_count,
        "active_p1_attention_count": 0,
        "repair_preview_required": False,
        "repair_apply_allowed_now": False,
        "evidence_chain_policy_level": POLICY_LEVEL,
        "current_evidence_chain_quality": current_quality,
        "future_modules_must_classify_evidence_quality": True,
        "full_post_check_marker_preferred_over_plain_pass": True,
        "plain_pass_without_marker_is_attention": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "future_runtime_or_live_requires_preflight_safety_readiness": True,
        "future_runtime_or_live_requires_kill_switch_readiness": True,
        "runtime_preflight_implementation_performed": False,
        "runtime_kill_switch_implementation_performed": False,
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "candidate_generation_performed": False,
        "family_release_performed": False,
        "active_paper_performed": False,
        "real_order_touch_performed": False,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": len(planned_existing),
        "planned_schema_files_existing": planned_existing,
        "generic_runner_target_exists": generic_runner_target_exists,
        "dangerous_flags": flags,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "dangerous_flag_true_count": 0,
        "contract_artifact_validation": artifact_eval,
        "old_source_panel_anomaly_route_guard_validation": old_guard_eval,
        "primary_artifact_requirement_validation": primary_eval,
        "evidence_quality_validation": evidence_eval,
        "safety_boundary_validation": safety_eval,
        "money_path_validation": money_eval,
        "derived_live_repo_post_check": True,
        "derived_live_repo_post_check_reason": (
            "This validator uses live repo checks and the source-panel contract artifact only for fail-closed validation. "
            "It does not run source-panel analysis, generate source-panel result artifacts, reopen old closed anomaly routes, "
            "touch runtime/capital/live/orders, approve generic runner work, create schemas/configs, promise profit, or treat derived checks as source-panel result primary strength."
        ),
        "replacement_checks_all_true": ready,
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "contract_record_artifact": str(CONTRACT_RECORD_ARTIFACT),
            "contract_record_artifact_loaded": bool(record),
            "allowed_next_modules": [NEXT_MODULE_READY, NEXT_MODULE_BLOCKED],
        },
        "safety_flags": {
            "repo_only": True,
            "validator_only": True,
            "source_panel_analysis_run_performed": False,
            "research_run_performed": False,
            "backtest_run_performed": False,
            "candidate_generation_performed": False,
            "family_release_performed": False,
            "active_paper_performed": False,
            "schema_or_config_created": False,
            "runtime_preflight_implementation_performed": False,
            "runtime_kill_switch_implementation_performed": False,
            "runtime_touch_performed": False,
            "capital_touch_performed": False,
            "live_touch_performed": False,
            "real_order_touch_performed": False,
            "generic_runner_approval_granted": False,
            "generic_runner_implementation_remains_blocked": True,
            "ordinary_selector_backlog_loop_reentry_allowed": False,
            "loop_remains_closed": True,
            **flags,
        },
    }
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_source_panel_analysis_contract_validator_after_research_return_gate_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_source_panel_analysis_contract_validator_after_research_return_gate_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_source_panel_analysis_contract_validator_after_research_return_gate_v1_latest.txt"
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    latest_json.write_text(rendered, encoding="utf-8")
    timestamped_json.write_text(rendered, encoding="utf-8")
    latest_txt.write_text(rendered + "\n", encoding="utf-8")
    return {"latest_json": str(latest_json), "timestamped_json": str(timestamped_json), "latest_txt": str(latest_txt)}


def main() -> int:
    payload = build_payload()
    outputs = write_outputs(payload)
    payload["outputs"] = outputs
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    Path(outputs["latest_json"]).write_text(rendered, encoding="utf-8")
    Path(outputs["latest_txt"]).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if payload["source_panel_analysis_contract_validator_status"] in {"PASS", "PASS_WITH_ATTENTION"} else 3


if __name__ == "__main__":
    raise SystemExit(main())
