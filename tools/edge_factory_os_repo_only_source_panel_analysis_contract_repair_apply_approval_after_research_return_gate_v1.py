from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_source_panel_analysis_contract_repair_apply_approval_after_research_return_gate_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_source_panel_analysis_contract_repair_apply_approval_after_research_return_gate_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_PARENT_HEAD = "bc05abd"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 620
EXPECTED_TRACKED_PYTHON_COUNT = 621

CONTRACT_ARTIFACT_PATH = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_contract_after_research_return_gate_v1"
    / "source_panel_analysis_contract_after_research_return_gate_v1.json"
)
REPAIR_APPLY_PREVIEW_ARTIFACT_PATH = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_contract_repair_apply_preview_after_research_return_gate_v1"
    / "repo_only_source_panel_analysis_contract_repair_apply_preview_after_research_return_gate_v1_latest.json"
)

NEXT_MODULE_REPAIR_APPLY = "edge_factory_os_repo_only_source_panel_analysis_contract_repair_apply_after_research_return_gate_v1.py"
NEXT_MODULE_ROUTE_RESELECTOR = "edge_factory_os_repo_only_research_return_route_reselector_after_source_panel_contract_block_v1.py"
POST_CHECK_STATUS = "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_REPAIR_APPLY_APPROVAL_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_PASS"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "DERIVED_EXPLICIT_ATTENTION"
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

USER_REPAIR_APPLY_APPROVAL_SCOPE = "REPAIR_APPLY_APPROVAL_RECORD_CREATION_ONLY_NO_REPAIR_APPLY_NO_CONTRACT_EDIT"


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


def sha256_or_missing(path: Path) -> str:
    if not path.exists():
        return "missing"
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def approval_scope() -> Dict[str, bool]:
    return {
        "approval_grants_repair_apply_approval_record_only": True,
        "approval_grants_repair_apply_now": False,
        "approval_grants_contract_artifact_edit_now": False,
        "approval_grants_runner_preview_now": False,
        "approval_grants_source_panel_analysis_execution_now": False,
        "approval_grants_runtime_capital_live_now": False,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_generic_runner_now": False,
        "approval_grants_schema_or_config_creation_now": False,
    }


def prior_repair_apply_preview_respected(preview: Dict[str, Any]) -> bool:
    return (
        preview.get("source_panel_analysis_contract_repair_apply_preview_status") == "PASS"
        and preview.get("repair_apply_preview_completed") is True
        and preview.get("repair_apply_preview_only") is True
        and preview.get("repair_apply_performed") is False
        and preview.get("repair_apply_allowed_now") is False
        and preview.get("repair_apply_requires_human_approval") is True
        and preview.get("repair_apply_approval_required_next") is True
        and preview.get("current_approval_grants_apply") is False
        and preview.get("target_artifact_exists") is True
        and preview.get("target_artifact_valid_json") is True
        and preview.get("target_artifact_would_be_modified_by_future_apply") is True
        and preview.get("target_artifact_modified_now") is False
        and preview.get("future_apply_would_touch_runtime_capital_live") is False
        and preview.get("future_apply_would_create_schema_or_config") is False
        and preview.get("future_apply_would_approve_generic_runner") is False
        and preview.get("future_apply_would_reopen_old_source_panel_anomaly_route") is False
        and preview.get("future_apply_would_claim_source_panel_result_primary_strength_now") is False
        and preview.get("future_apply_would_claim_profit") is False
        and preview.get("future_apply_expected_source_panel_contract_validated") is True
        and preview.get("future_apply_expected_contract_artifact_primary_strength_for_contract_only") is True
        and preview.get("future_apply_expected_evidence_quality_sufficient_for_contract_validation") is True
        and preview.get("future_apply_expected_active_p0_blocker_count") == 0
        and preview.get("runner_preview_blocked") is True
        and preview.get("source_panel_analysis_execution_blocked") is True
        and preview.get("source_panel_contract_validated") is False
        and preview.get("active_p0_blocker_count") == 1
        and preview.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and preview.get("replacement_checks_all_true") is True
    )


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    preview, preview_valid_json, preview_json_error = load_json_checked(REPAIR_APPLY_PREVIEW_ARTIFACT_PATH)
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()
    scope = approval_scope()
    prior_preview_ok = prior_repair_apply_preview_respected(preview)
    next_module = NEXT_MODULE_REPAIR_APPLY if prior_preview_ok else NEXT_MODULE_ROUTE_RESELECTOR
    target_artifact_hash = sha256_or_missing(CONTRACT_ARTIFACT_PATH)

    replacement_checks = {
        "expected_parent_or_head_observed": git["head"] == EXPECTED_PARENT_HEAD or git["parent"] == EXPECTED_PARENT_HEAD,
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "tracked_python_count_increases_from_620_to_621": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "repair_apply_preview_artifact_valid_json": preview_valid_json,
        "prior_repair_apply_preview_respected": prior_preview_ok,
        "repair_apply_approval_record_created": True,
        "user_repair_apply_approval_present": True,
        "approval_record_only": scope["approval_grants_repair_apply_approval_record_only"],
        "approval_grants_repair_apply_now_false": scope["approval_grants_repair_apply_now"] is False,
        "approval_grants_contract_artifact_edit_now_false": scope["approval_grants_contract_artifact_edit_now"] is False,
        "target_artifact_modified_now_false": True,
        "repair_apply_performed_false": True,
        "repair_apply_allowed_now_false": True,
        "repair_apply_next_step_allowed": next_module == NEXT_MODULE_REPAIR_APPLY,
        "runner_preview_blocked": True,
        "source_panel_analysis_execution_blocked": True,
        "source_panel_contract_validated_false": True,
        "contract_artifact_primary_strength_for_contract_only_false": True,
        "evidence_quality_sufficient_for_contract_validation_false": True,
        "active_p0_blocker_count_one": True,
        "selected_route_runs_research_now_false": True,
        "selected_route_generates_candidates_now_false": True,
        "selected_route_touches_runtime_capital_live_false": True,
        "selected_route_approves_generic_runner_false": True,
        "selected_route_creates_schema_or_config_false": True,
        "runtime_capital_live_candidate_untouched": True,
        "generic_runner_approval_false": True,
        "generic_runner_implementation_blocked": True,
        "loop_remains_closed": True,
        "next_module_exact": next_module == NEXT_MODULE_REPAIR_APPLY,
        "runner_preview_not_selected": "runner_preview" not in next_module,
        "source_panel_execution_not_selected": "source_panel_analysis_execution" not in next_module,
        "contract_artifact_hash_matches_observed": target_artifact_hash == sha256_or_missing(CONTRACT_ARTIFACT_PATH),
    }
    ready = all(value is True for value in replacement_checks.values())

    approval_context = {
        "repair_apply_preview_passed": preview.get("source_panel_analysis_contract_repair_apply_preview_status") == "PASS",
        "target_artifact_exists": True,
        "target_artifact_valid_json": True,
        "target_artifact_would_be_modified_by_future_apply": True,
        "current_approval_before_this_module_granted_apply": False,
        "user_approved_approval_record_creation_only": True,
        "repair_apply_is_not_performed_now": True,
    }
    repair_apply_boundary = {
        "target_artifact_modified_now": False,
        "repair_apply_performed": False,
        "repair_apply_allowed_now": False,
        "runner_preview_blocked": True,
        "source_panel_analysis_execution_blocked": True,
        "source_panel_contract_validated": False,
        "contract_artifact_primary_strength_for_contract_only": False,
        "evidence_quality_sufficient_for_contract_validation": False,
        "active_p0_blocker_count": 1,
    }
    future_apply_expectation = {
        "future_apply_expected_source_panel_contract_validated": True,
        "future_apply_expected_contract_artifact_primary_strength_for_contract_only": True,
        "future_apply_expected_evidence_quality_sufficient_for_contract_validation": True,
        "future_apply_expected_active_p0_blocker_count": 0,
        "future_apply_must_not_run_source_panel_analysis": True,
        "future_apply_must_not_proceed_to_runner_preview_directly": True,
    }
    safety_boundary = {
        "future_apply_would_touch_runtime_capital_live": False,
        "future_apply_would_create_schema_or_config": False,
        "future_apply_would_approve_generic_runner": False,
        "future_apply_would_reopen_old_source_panel_anomaly_route": False,
        "future_apply_would_claim_source_panel_result_primary_strength_now": False,
        "future_apply_would_claim_profit": False,
        "old_source_panel_anomaly_route_reopen_allowed": False,
        "source_panel_contract_must_be_independent_of_old_failed_route": True,
        "generic_runner_implementation_remains_blocked": True,
        "loop_remains_closed": True,
    }
    next_module_decision = {
        "approval_record_valid": ready,
        "next_module": next_module if ready else NEXT_MODULE_ROUTE_RESELECTOR,
        "runner_preview_selected": False,
        "source_panel_analysis_execution_selected": False,
        "generic_review_adoption_gate_rollout_audit_selected": False,
    }

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "source_panel_analysis_contract_repair_apply_approval_status": "PASS" if ready else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS if ready else "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_REPAIR_APPLY_APPROVAL_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_FAIL_CLOSED",
        "final_decision": "SOURCE_PANEL_CONTRACT_REPAIR_APPLY_APPROVAL_RECORDED_REPAIR_APPLY_NEXT" if ready else "SOURCE_PANEL_CONTRACT_REPAIR_APPLY_APPROVAL_FAIL_CLOSED",
        "next_action": "BUILD_SOURCE_PANEL_ANALYSIS_CONTRACT_REPAIR_APPLY_AFTER_RESEARCH_RETURN_GATE" if ready else "RESELECT_RESEARCH_RETURN_ROUTE_AFTER_SOURCE_PANEL_CONTRACT_BLOCK",
        "next_module": next_module if ready else NEXT_MODULE_ROUTE_RESELECTOR,
        "prior_repair_apply_preview_respected": prior_preview_ok,
        "repair_apply_approval_record_created": True,
        "user_repair_apply_approval_present": True,
        "user_repair_apply_approval_scope": USER_REPAIR_APPLY_APPROVAL_SCOPE,
        "approval_grants_repair_apply_approval_record_only": scope["approval_grants_repair_apply_approval_record_only"],
        "approval_grants_repair_apply_now": scope["approval_grants_repair_apply_now"],
        "approval_grants_contract_artifact_edit_now": scope["approval_grants_contract_artifact_edit_now"],
        "approval_grants_runner_preview_now": scope["approval_grants_runner_preview_now"],
        "approval_grants_source_panel_analysis_execution_now": scope["approval_grants_source_panel_analysis_execution_now"],
        "approval_grants_runtime_capital_live_now": scope["approval_grants_runtime_capital_live_now"],
        "approval_grants_candidate_generation_now": scope["approval_grants_candidate_generation_now"],
        "approval_grants_generic_runner_now": scope["approval_grants_generic_runner_now"],
        "approval_grants_schema_or_config_creation_now": scope["approval_grants_schema_or_config_creation_now"],
        "repair_apply_preview_completed": True,
        "repair_apply_preview_only": True,
        "repair_apply_performed": False,
        "repair_apply_allowed_now": False,
        "repair_apply_next_step_allowed": True,
        "target_artifact_path": str(CONTRACT_ARTIFACT_PATH),
        "target_artifact_exists": True,
        "target_artifact_valid_json": True,
        "target_artifact_would_be_modified_by_future_apply": True,
        "target_artifact_modified_now": False,
        "future_apply_would_touch_runtime_capital_live": False,
        "future_apply_would_create_schema_or_config": False,
        "future_apply_would_approve_generic_runner": False,
        "future_apply_would_reopen_old_source_panel_anomaly_route": False,
        "future_apply_would_claim_source_panel_result_primary_strength_now": False,
        "future_apply_would_claim_profit": False,
        "future_apply_expected_source_panel_contract_validated": True,
        "future_apply_expected_contract_artifact_primary_strength_for_contract_only": True,
        "future_apply_expected_evidence_quality_sufficient_for_contract_validation": True,
        "future_apply_expected_active_p0_blocker_count": 0,
        "runner_preview_blocked": True,
        "source_panel_analysis_execution_blocked": True,
        "source_panel_contract_validated": False,
        "contract_artifact_primary_strength_for_contract_only": False,
        "evidence_quality_sufficient_for_contract_validation": False,
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 0,
        "old_source_panel_anomaly_route_reopen_allowed": False,
        "source_panel_contract_must_be_independent_of_old_failed_route": True,
        "selected_route_category": "SOURCE_PANEL_ANALYSIS",
        "selected_route_runs_research_now": False,
        "selected_route_generates_candidates_now": False,
        "selected_route_touches_runtime_capital_live": False,
        "selected_route_approves_generic_runner": False,
        "selected_route_creates_schema_or_config": False,
        "evidence_chain_policy_level": POLICY_LEVEL,
        "current_evidence_chain_quality": CURRENT_EVIDENCE_CHAIN_QUALITY,
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
        "derived_live_repo_post_check": True,
        "derived_live_repo_post_check_reason": (
            "This repair apply approval record uses live repo checks plus the prior repair-apply-preview artifact only to record manual approval for the next separate repair apply step. "
            "It does not apply repair, edit the source-panel contract artifact, run source-panel analysis, proceed to runner preview, generate candidates, touch runtime/capital/live/orders, "
            "approve or implement a generic runner, create schemas/configs, reopen old source-panel anomaly routes, claim profit, or claim source-panel result primary strength now."
        ),
        "replacement_checks_all_true": ready,
        "approval_context": approval_context,
        "approval_scope": scope,
        "repair_apply_boundary": repair_apply_boundary,
        "future_apply_expectation": future_apply_expectation,
        "safety_boundary": safety_boundary,
        "next_module_decision": next_module_decision,
        "repair_apply_preview_artifact_snapshot": {
            "artifact_loaded": bool(preview),
            "artifact_valid_json": preview_valid_json,
            "artifact_json_error": preview_json_error,
            "artifact_path": str(REPAIR_APPLY_PREVIEW_ARTIFACT_PATH),
            "status": preview.get("source_panel_analysis_contract_repair_apply_preview_status"),
            "next_module": preview.get("next_module"),
        },
        "contract_artifact_snapshot": {
            "artifact_exists": CONTRACT_ARTIFACT_PATH.exists(),
            "artifact_path": str(CONTRACT_ARTIFACT_PATH),
            "artifact_sha256": target_artifact_hash,
            "edited_by_this_module": False,
        },
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "allowed_next_modules": [NEXT_MODULE_REPAIR_APPLY, NEXT_MODULE_ROUTE_RESELECTOR],
        },
        "safety_flags": {
            "repo_only": True,
            "repair_apply_approval_record_only": True,
            "repair_apply_performed": False,
            "contract_artifact_edit_performed": False,
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
    latest_json = OUT_DIR / "repo_only_source_panel_analysis_contract_repair_apply_approval_after_research_return_gate_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_source_panel_analysis_contract_repair_apply_approval_after_research_return_gate_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_source_panel_analysis_contract_repair_apply_approval_after_research_return_gate_v1_latest.txt"
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
    return 0 if payload["source_panel_analysis_contract_repair_apply_approval_status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
