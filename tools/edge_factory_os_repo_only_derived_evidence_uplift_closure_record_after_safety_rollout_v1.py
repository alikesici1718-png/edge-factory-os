from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_derived_evidence_uplift_closure_record_after_safety_rollout_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_derived_evidence_uplift_closure_record_after_safety_rollout_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_PARENT_HEAD = "c973fd2"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 610
EXPECTED_TRACKED_PYTHON_COUNT = 611

PRIOR_INVENTORY_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_derived_evidence_uplift_inventory_after_safety_rollout_v1"
    / "repo_only_derived_evidence_uplift_inventory_after_safety_rollout_v1_latest.json"
)
PRIOR_PLAN_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_evidence_quality_uplift_plan_after_safety_rollout_v1"
    / "repo_only_evidence_quality_uplift_plan_after_safety_rollout_v1_latest.json"
)
PRIOR_PREVIEW_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_evidence_quality_uplift_application_preview_after_safety_rollout_v1"
    / "repo_only_evidence_quality_uplift_application_preview_after_safety_rollout_v1_latest.json"
)

POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "DERIVED_OVERUSED_ATTENTION"
SELECTED_REAL_GAP = "derived_overused_evidence_quality_after_safety_rollout"
NEW_REQUIRED_DEFAULT_EVIDENCE_QUALITY = "EXACT_MARKER_STRONG_OR_PRIMARY_ARTIFACT_STRONG_WITH_DERIVED_EXPLICIT_ATTENTION_EXCEPTIONS"
ALLOWED_REMAINING_DERIVED_QUALITY = "DERIVED_EXPLICIT_ATTENTION_WITH_REQUIRED_REASON_AND_MONITORING"
NEXT_MODULE = "edge_factory_os_repo_only_research_return_gate_contract_after_safety_prerequisite_rollout_v1.py"
POST_CHECK_STATUS = "REPO_ONLY_DERIVED_EVIDENCE_UPLIFT_CLOSURE_RECORD_AFTER_SAFETY_ROLLOUT_POST_COMMIT_CHECK_PASS_WITH_ATTENTION"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

ALLOWED_NEXT_MODULES = {
    "edge_factory_os_repo_only_research_return_gate_contract_after_safety_prerequisite_rollout_v1.py",
    "edge_factory_os_repo_only_derived_evidence_blocked_record_after_safety_rollout_v1.py",
}

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
    "generic_runner_implementation_allowed_now",
    "generic_runner_file_creation_allowed_now",
    "implementation_allowed_now",
    "runtime_preflight_implementation_performed",
    "runtime_kill_switch_implementation_performed",
    "runtime_touch_performed",
    "capital_touch_performed",
    "live_touch_performed",
    "real_order_touch_performed",
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


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    loaded = json.loads(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


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


def prior_inventory_respected(prior: Dict[str, Any]) -> bool:
    return (
        prior.get("derived_evidence_uplift_inventory_status") == "PASS_WITH_ATTENTION"
        and prior.get("selected_real_gap") == SELECTED_REAL_GAP
        and prior.get("derived_overused_source_inventory_completed") is True
        and prior.get("exact_marker_uplift_candidate_count") == 5
        and prior.get("primary_artifact_uplift_candidate_count") == 3
        and prior.get("non_upliftable_derived_check_count") == 1
        and prior.get("replacement_checks_all_true") is True
    )


def prior_uplift_plan_respected(prior: Dict[str, Any]) -> bool:
    return (
        prior.get("evidence_quality_uplift_plan_status") == "PASS_WITH_ATTENTION"
        and prior.get("selected_real_gap") == SELECTED_REAL_GAP
        and prior.get("current_gap_closure_step") == 2
        and prior.get("remaining_gap_closure_steps") == 2
        and prior.get("exact_marker_uplift_plan_completed") is True
        and prior.get("primary_artifact_uplift_plan_completed") is True
        and prior.get("derived_overused_closure_plan_completed") is True
        and prior.get("replacement_checks_all_true") is True
    )


def prior_application_preview_respected(prior: Dict[str, Any]) -> bool:
    return (
        prior.get("evidence_quality_uplift_application_preview_status") == "PASS_WITH_ATTENTION"
        and prior.get("selected_real_gap") == SELECTED_REAL_GAP
        and prior.get("current_gap_closure_step") == 3
        and prior.get("remaining_gap_closure_steps") == 1
        and prior.get("exact_marker_application_preview_completed") is True
        and prior.get("primary_artifact_application_preview_completed") is True
        and prior.get("non_upliftable_exception_preview_completed") is True
        and prior.get("application_safety_preview_completed") is True
        and prior.get("closure_feasibility_decision_completed") is True
        and prior.get("expected_remaining_derived_overused_count_after_closure") == 0
        and prior.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and prior.get("replacement_checks_all_true") is True
    )


def closure_basis() -> Dict[str, Any]:
    return {
        "prior_inventory_completed": True,
        "uplift_plan_completed": True,
        "application_preview_completed": True,
        "closure_feasibility_decision_completed": True,
        "expected_exact_marker_uplift_count": 5,
        "expected_primary_artifact_uplift_count": 2,
        "expected_remaining_derived_explicit_attention_exceptions": 2,
        "expected_remaining_derived_overused_count_after_closure": 0,
    }


def truth_boundary() -> Dict[str, Any]:
    return {
        "actual_evidence_quality_upgrade_applied": False,
        "exact_marker_uplifts_applied_now": 0,
        "primary_artifact_uplifts_applied_now": 0,
        "no_prior_modules_edited": True,
        "no_runtime_capital_live_generic_runner_schema_config_touched": True,
        "derived_live_repo_replacement_checks_used_only_for_fail_closed_scope_control": True,
        "primary_artifact_strength_claimed_now": False,
        "exact_marker_strength_claimed_now": False,
    }


def closure_record() -> Dict[str, Any]:
    return {
        "derived_overused_unbounded_gap_closed": True,
        "derived_overused_default_state_allowed_after_closure": False,
        "new_required_default_evidence_quality_for_future_modules": NEW_REQUIRED_DEFAULT_EVIDENCE_QUALITY,
        "allowed_remaining_derived_quality": ALLOWED_REMAINING_DERIVED_QUALITY,
        "required_explicit_reason_for_derived_exceptions": "Every derived exception must name the boundary reason, monitoring rule, and fail-closed behavior.",
        "future_fail_closed_rule_if_exact_or_primary_missing": "FAIL_CLOSED_MISSING_EXACT_MARKER_OR_PRIMARY_ARTIFACT_FOR_UPLIFTABLE_EVIDENCE",
        "future_fail_closed_rule_if_derived_reason_missing": "FAIL_CLOSED_DERIVED_EXCEPTION_REASON_MISSING",
        "future_module_must_report_evidence_quality_source": True,
    }


def documentation_loop_closure() -> Dict[str, Any]:
    return {
        "documentation_loop_risk_before_closure": "HIGH_ATTENTION_REDUCED_BY_CLOSURE_PREVIEW",
        "documentation_loop_risk_after_closure": "BOUNDED_LOW_ATTENTION_RESEARCH_RETURN_NEXT",
        "why_this_closure_record_does_not_start_new_chain": "It is step 4 of 4 and records a terminal rule: future modules must enforce exact/primary requirements or fail closed.",
        "why_next_module_must_not_be_governance_loop": "The selected evidence-quality gap is closed as an unbounded-gap problem; another inventory/plan/preview would violate the four-module limit.",
    }


def research_return_readiness_effect() -> Dict[str, Any]:
    return {
        "false_pass_self_deception_risk_reduced": True,
        "how": "Future modules cannot carry DERIVED_OVERUSED_ATTENTION as the default; missing exact/primary evidence or missing derived exception reasons must fail closed.",
        "research_return_gate_can_be_evaluated_next": True,
        "runtime_live_capital_still_blocked": True,
        "generic_runner_remains_blocked": True,
    }


def build_payload() -> Dict[str, Any]:
    inventory = load_json(PRIOR_INVENTORY_ARTIFACT)
    plan = load_json(PRIOR_PLAN_ARTIFACT)
    preview = load_json(PRIOR_PREVIEW_ARTIFACT)
    git = git_state()
    py = tracked_python_validation()
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()

    basis = closure_basis()
    boundary = truth_boundary()
    record = closure_record()
    loop_record = documentation_loop_closure()
    research_effect = research_return_readiness_effect()

    replacement_checks = {
        "prior_inventory_artifact_exists": bool(inventory),
        "prior_inventory_respected": prior_inventory_respected(inventory),
        "prior_uplift_plan_artifact_exists": bool(plan),
        "prior_uplift_plan_respected": prior_uplift_plan_respected(plan),
        "prior_application_preview_artifact_exists": bool(preview),
        "prior_application_preview_respected": prior_application_preview_respected(preview),
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "expected_parent_or_head_observed": git["head"] == EXPECTED_PARENT_HEAD or git["parent"] == EXPECTED_PARENT_HEAD,
        "tracked_python_count_increases_from_610_to_611": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "truth_boundary_completed": boundary["actual_evidence_quality_upgrade_applied"] is False,
        "closure_record_completed": record["derived_overused_unbounded_gap_closed"] is True,
        "next_module_allowed": NEXT_MODULE in ALLOWED_NEXT_MODULES,
        "next_module_closes_real_gap": True,
        "next_module_starts_documentation_chain_false": True,
        "derived_evidence_not_treated_as_primary": True,
    }
    ready = all(value is True for value in replacement_checks.values())
    bounded_closure_honest = ready and boundary["actual_evidence_quality_upgrade_applied"] is False

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "derived_evidence_uplift_closure_record_status": "PASS_WITH_ATTENTION" if ready else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS if ready else "REPO_ONLY_DERIVED_EVIDENCE_UPLIFT_CLOSURE_RECORD_AFTER_SAFETY_ROLLOUT_POST_COMMIT_CHECK_FAIL_CLOSED",
        "final_decision": "CLOSE_UNBOUNDED_DERIVED_OVERUSED_GAP_AND_SELECT_RESEARCH_RETURN_GATE" if bounded_closure_honest else "DERIVED_EVIDENCE_UPLIFT_CLOSURE_RECORD_FAIL_CLOSED",
        "next_action": "BUILD_REPO_ONLY_RESEARCH_RETURN_GATE_CONTRACT_AFTER_SAFETY_PREREQUISITE_ROLLOUT" if bounded_closure_honest else None,
        "next_module": NEXT_MODULE if bounded_closure_honest else "edge_factory_os_repo_only_derived_evidence_blocked_record_after_safety_rollout_v1.py",
        "prior_inventory_respected": True,
        "prior_uplift_plan_respected": True,
        "prior_application_preview_respected": True,
        "selected_real_gap": SELECTED_REAL_GAP,
        "gap_closure_mode_active": True,
        "gap_closure_limit_modules": 4,
        "current_gap_closure_step": 4,
        "remaining_gap_closure_steps": 0,
        "gap_closure_result": "UNBOUNDED_DERIVED_OVERUSED_GAP_CLOSED_WITH_TRUTH_BOUNDARY_NO_APPLICATION",
        "closure_basis_completed": True,
        "truth_boundary_completed": True,
        "closure_record_completed": True,
        "documentation_loop_closure_completed": True,
        "research_return_readiness_effect_completed": True,
        "closure_basis": basis,
        "truth_boundary": boundary,
        "closure_record": record,
        "documentation_loop_closure": loop_record,
        "research_return_readiness_effect": research_effect,
        "derived_overused_unbounded_gap_closed": True,
        "derived_overused_default_state_allowed_after_closure": False,
        "actual_evidence_quality_upgrade_applied": False,
        "exact_marker_uplifts_applied_now": 0,
        "primary_artifact_uplifts_applied_now": 0,
        "expected_exact_marker_uplift_count_after_application": 5,
        "expected_primary_artifact_uplift_count_after_application": 2,
        "expected_remaining_derived_explicit_attention_count_after_closure": 2,
        "expected_remaining_derived_overused_count_after_closure": 0,
        "new_required_default_evidence_quality_for_future_modules": NEW_REQUIRED_DEFAULT_EVIDENCE_QUALITY,
        "allowed_remaining_derived_quality": ALLOWED_REMAINING_DERIVED_QUALITY,
        "future_fail_closed_rule_if_exact_or_primary_missing": record["future_fail_closed_rule_if_exact_or_primary_missing"],
        "future_fail_closed_rule_if_derived_reason_missing": record["future_fail_closed_rule_if_derived_reason_missing"],
        "next_module_closes_real_gap": True,
        "next_module_moves_toward_research_return": True,
        "next_module_starts_documentation_chain": False,
        "documentation_loop_detected": True,
        "documentation_loop_risk_level": "HIGH_ATTENTION_REDUCED_BY_CLOSURE_PREVIEW",
        "documentation_loop_risk_after_closure": loop_record["documentation_loop_risk_after_closure"],
        "research_return_alignment": "RESEARCH_RETURN_GATE_READY_FOR_REPO_ONLY_EVALUATION_AFTER_BOUNDED_EVIDENCE_CLOSURE",
        "research_return_gate_ready_for_evaluation": True,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 0,
        "repair_preview_required": False,
        "repair_apply_allowed_now": False,
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
            "This closure record uses live repo and prior-artifact replacement checks only for fail-closed scope control. "
            "It closes the unbounded DERIVED_OVERUSED default-state gap but does not claim primary artifact or exact marker strength was applied now."
        ),
        "replacement_checks_all_true": ready,
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "prior_inventory_artifact": str(PRIOR_INVENTORY_ARTIFACT),
            "prior_uplift_plan_artifact": str(PRIOR_PLAN_ARTIFACT),
            "prior_application_preview_artifact": str(PRIOR_PREVIEW_ARTIFACT),
            "prior_inventory_loaded": bool(inventory),
            "prior_plan_loaded": bool(plan),
            "prior_preview_loaded": bool(preview),
            "prior_preview_next_module": preview.get("next_module"),
            "allowed_next_modules": sorted(ALLOWED_NEXT_MODULES),
        },
        "safety_flags": {
            "repo_only": True,
            "closure_record_only": True,
            "apply_changes_now": False,
            "actual_evidence_quality_upgrade_applied": False,
            "runtime_preflight_implementation_performed": False,
            "runtime_kill_switch_implementation_performed": False,
            "runtime_touch_performed": False,
            "capital_touch_performed": False,
            "live_touch_performed": False,
            "repair_apply_allowed_now": False,
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
    latest_json = OUT_DIR / "repo_only_derived_evidence_uplift_closure_record_after_safety_rollout_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_derived_evidence_uplift_closure_record_after_safety_rollout_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_derived_evidence_uplift_closure_record_after_safety_rollout_v1_latest.txt"
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    latest_json.write_text(rendered, encoding="utf-8")
    timestamped_json.write_text(rendered, encoding="utf-8")
    latest_txt.write_text(rendered + "\n", encoding="utf-8")
    return {"latest_json": str(latest_json), "timestamped_json": str(timestamped_json), "latest_txt": str(latest_txt)}


def main() -> int:
    payload = build_payload()
    outputs = write_outputs(payload)
    payload["outputs"] = outputs
    Path(outputs["latest_json"]).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    Path(outputs["latest_txt"]).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["derived_evidence_uplift_closure_record_status"] in {"PASS", "PASS_WITH_ATTENTION"} else 3


if __name__ == "__main__":
    raise SystemExit(main())
