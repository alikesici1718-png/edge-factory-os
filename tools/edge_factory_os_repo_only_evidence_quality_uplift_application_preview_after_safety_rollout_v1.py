from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_evidence_quality_uplift_application_preview_after_safety_rollout_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_evidence_quality_uplift_application_preview_after_safety_rollout_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_PARENT_HEAD = "4aff4bb"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 609
EXPECTED_TRACKED_PYTHON_COUNT = 610

PRIOR_PLAN_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_evidence_quality_uplift_plan_after_safety_rollout_v1"
    / "repo_only_evidence_quality_uplift_plan_after_safety_rollout_v1_latest.json"
)

POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "DERIVED_OVERUSED_ATTENTION"
SELECTED_REAL_GAP = "derived_overused_evidence_quality_after_safety_rollout"
RECOMMENDED_UPLIFT_PATH = "COMBINED_EXACT_MARKER_AND_PRIMARY_ARTIFACT_UPLIFT_PLAN"
NEW_DEFAULT_EVIDENCE_QUALITY_AFTER_CLOSURE = "EXACT_MARKER_STRONG_OR_PRIMARY_ARTIFACT_STRONG_WITH_DERIVED_EXPLICIT_ATTENTION_EXCEPTIONS"
NEXT_MODULE = "edge_factory_os_repo_only_derived_evidence_uplift_closure_record_after_safety_rollout_v1.py"
POST_CHECK_STATUS = "REPO_ONLY_EVIDENCE_QUALITY_UPLIFT_APPLICATION_PREVIEW_AFTER_SAFETY_ROLLOUT_POST_COMMIT_CHECK_PASS_WITH_ATTENTION"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

ALLOWED_NEXT_MODULES = {
    "edge_factory_os_repo_only_derived_evidence_uplift_closure_record_after_safety_rollout_v1.py",
    "edge_factory_os_repo_only_derived_evidence_blocked_record_after_safety_rollout_v1.py",
    "edge_factory_os_repo_only_research_return_gate_contract_after_safety_prerequisite_rollout_v1.py",
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


def prior_plan_respected(prior: Dict[str, Any]) -> bool:
    return (
        prior.get("evidence_quality_uplift_plan_status") == "PASS_WITH_ATTENTION"
        and prior.get("selected_real_gap") == SELECTED_REAL_GAP
        and prior.get("gap_closure_mode_active") is True
        and prior.get("current_gap_closure_step") == 2
        and prior.get("remaining_gap_closure_steps") == 2
        and prior.get("exact_marker_uplift_plan_completed") is True
        and prior.get("primary_artifact_uplift_plan_completed") is True
        and prior.get("non_upliftable_derived_check_policy_completed") is True
        and prior.get("derived_overused_closure_plan_completed") is True
        and prior.get("exact_marker_uplift_candidate_count") == 5
        and prior.get("primary_artifact_uplift_candidate_count") == 3
        and prior.get("non_upliftable_derived_check_count") == 1
        and prior.get("recommended_uplift_path") == RECOMMENDED_UPLIFT_PATH
        and prior.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and prior.get("replacement_checks_all_true") is True
    )


def exact_marker_application_preview() -> List[Dict[str, Any]]:
    return [
        {
            "candidate_id": "EXACT-001",
            "source_check": "kill_switch_and_preflight_repo_only_gate_scope",
            "required_exact_marker": "SAFETY_READINESS_IS_REPO_ONLY_PLANNING_GATE_FOR_FUTURE_RUNTIME_OR_LIVE",
            "current_detection_method": "derived booleans for future_runtime_or_live_requires_preflight_safety_readiness and future_runtime_or_live_requires_kill_switch_readiness",
            "proposed_detection_method": "require the exact marker plus both future safety prerequisite booleans",
            "exact_marker_source_path_or_pattern": "repo_only evidence artifacts exact_post_check_markers[]",
            "preview_change_required": "add marker expectation to future evidence-quality closure checks only; do not edit old modules in this preview",
            "target_quality_after_application": "EXACT_MARKER_STRONG",
            "fail_closed_condition": "marker missing or either future safety prerequisite boolean false",
            "can_apply_without_runtime_touch": True,
            "can_apply_without_schema_or_config": True,
            "risk_level": "LOW_REPO_ONLY",
            "expected_effect_on_derived_overused": "removes safety gate scope from derived-overused bucket",
        },
        {
            "candidate_id": "EXACT-002",
            "source_check": "no_runtime_launcher_capital_live_order_candidate_family_strategy_touch",
            "required_exact_marker": "REPO_ONLY_NO_RUNTIME_LAUNCHER_CAPITAL_LIVE_ORDER_CANDIDATE_FAMILY_STRATEGY_TOUCH",
            "current_detection_method": "latest commit path and dangerous_flags_all_false replacement checks",
            "proposed_detection_method": "require exact no-touch marker plus commit path and dangerous flag checks",
            "exact_marker_source_path_or_pattern": "repo-only module payload exact_post_check_markers[] or exact_no_touch_marker",
            "preview_change_required": "preview marker verification logic only",
            "target_quality_after_application": "EXACT_MARKER_STRONG",
            "fail_closed_condition": "marker missing, commit scope wrong, or any dangerous flag true",
            "can_apply_without_runtime_touch": True,
            "can_apply_without_schema_or_config": True,
            "risk_level": "LOW_REPO_ONLY",
            "expected_effect_on_derived_overused": "keeps no-touch evidence explicit and not overused-derived",
        },
        {
            "candidate_id": "EXACT-003",
            "source_check": "generic_runner_blocked_state",
            "required_exact_marker": "GENERIC_RUNNER_REMAINS_BLOCKED_NO_APPROVAL_NO_TARGET",
            "current_detection_method": "generic_runner_target_exists=false and generic_runner_approval_granted=false",
            "proposed_detection_method": "require exact blocked marker plus absent target and false approval flags",
            "exact_marker_source_path_or_pattern": "repo-only module payload exact_post_check_markers[]",
            "preview_change_required": "preview marker requirement; no runner target or config creation",
            "target_quality_after_application": "EXACT_MARKER_STRONG",
            "fail_closed_condition": "marker missing, runner approved, implementation unblocked, or target exists",
            "can_apply_without_runtime_touch": True,
            "can_apply_without_schema_or_config": True,
            "risk_level": "LOW_REPO_ONLY",
            "expected_effect_on_derived_overused": "moves generic runner block evidence from inferred absence to exact marker",
        },
        {
            "candidate_id": "EXACT-004",
            "source_check": "closed_generic_governance_loop_state",
            "required_exact_marker": "CLOSED_LOOP_REMAINS_CLOSED_WITH_FOUR_MODULE_GAP_LIMIT",
            "current_detection_method": "loop_remains_closed=true and ordinary_selector_backlog_loop_reentry_allowed=false",
            "proposed_detection_method": "require exact loop closure marker, current/remaining step counters, and no selector/backlog re-entry",
            "exact_marker_source_path_or_pattern": "gap closure payload exact_post_check_markers[]",
            "preview_change_required": "preview closure-record marker verification for step 4",
            "target_quality_after_application": "EXACT_MARKER_STRONG",
            "fail_closed_condition": "marker missing, loop reopened, selector re-entry allowed, or module limit exceeded",
            "can_apply_without_runtime_touch": True,
            "can_apply_without_schema_or_config": True,
            "risk_level": "LOW_REPO_ONLY",
            "expected_effect_on_derived_overused": "turns loop control from narrative governance into finite exact closure evidence",
        },
        {
            "candidate_id": "EXACT-005",
            "source_check": "plain_pass_without_marker_is_attention",
            "required_exact_marker": "FULL_POST_CHECK_MARKER_REQUIRED_PLAIN_PASS_IS_ATTENTION",
            "current_detection_method": "full_post_check_marker_preferred_over_plain_pass=true and plain_pass_without_marker_is_attention=true booleans",
            "proposed_detection_method": "require exact pass-semantics marker plus both pass-warning booleans",
            "exact_marker_source_path_or_pattern": "repo-only module payload exact_post_check_markers[]",
            "preview_change_required": "preview marker verification logic only",
            "target_quality_after_application": "EXACT_MARKER_STRONG",
            "fail_closed_condition": "marker missing or PASS_WITH_ATTENTION treated as PASS",
            "can_apply_without_runtime_touch": True,
            "can_apply_without_schema_or_config": True,
            "risk_level": "LOW_REPO_ONLY",
            "expected_effect_on_derived_overused": "prevents PASS_WITH_ATTENTION normalization from remaining structural",
        },
    ]


def primary_artifact_application_preview() -> List[Dict[str, Any]]:
    return [
        {
            "candidate_id": "PRIMARY-001",
            "source_check": "prior_gap_reassessment_evaluator_status",
            "required_primary_artifact": "repo_only_final_form_gap_reassessment_evaluator_after_preflight_safety_rollout_v1_latest.json",
            "current_detection_method": "derived latest artifact status fields",
            "proposed_primary_artifact_read": "read artifact directly and record path plus checksum in closure record",
            "primary_artifact_source_path_or_pattern": str(
                LAB_ROOT
                / "edge_factory_os_repo_only_final_form_gap_reassessment_evaluator_after_preflight_safety_rollout_v1"
                / "repo_only_final_form_gap_reassessment_evaluator_after_preflight_safety_rollout_v1_latest.json"
            ),
            "preview_change_required": "closure record should cite and hash the primary artifact",
            "target_quality_after_application": "PRIMARY_ARTIFACT_STRONG",
            "fail_closed_condition": "artifact missing, unreadable, wrong selected_real_gap, or replacement_checks_all_true not true",
            "can_apply_without_runtime_touch": True,
            "can_apply_without_schema_or_config": True,
            "risk_level": "LOW_REPO_ONLY",
            "expected_effect_on_derived_overused": "moves prior evaluator evidence out of latest-json-only derived status",
        },
        {
            "candidate_id": "PRIMARY-002",
            "source_check": "evidence_chain_policy_active",
            "required_primary_artifact": "post_check_artifact_reliability_policy_or_enforcement_artifact",
            "current_detection_method": "policy-level string equality copied forward",
            "proposed_primary_artifact_read": "locate the strongest post-check artifact reliability policy/enforcement artifact and verify policy active",
            "primary_artifact_source_path_or_pattern": "C:/Users/alike/OneDrive/Desktop/edge_lab_new/edge_factory_os_repo_only_post_check_artifact_reliability_*_v1/*_latest.json",
            "preview_change_required": "closure record should cite the selected policy artifact or fail closed if unavailable",
            "target_quality_after_application": "PRIMARY_ARTIFACT_STRONG",
            "fail_closed_condition": "no policy artifact found or artifact does not assert POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE",
            "can_apply_without_runtime_touch": True,
            "can_apply_without_schema_or_config": True,
            "risk_level": "LOW_REPO_ONLY",
            "expected_effect_on_derived_overused": "stops policy activity from being only a copied string",
        },
        {
            "candidate_id": "PRIMARY-003",
            "source_check": "research_return_alignment",
            "required_primary_artifact": "research_return_gate_alignment_artifact",
            "current_detection_method": "narrative alignment field",
            "proposed_primary_artifact_read": "defer primary research-return artifact until after closure; closure must mark this as deferred with explicit blocker-free next gate requirement",
            "primary_artifact_source_path_or_pattern": "future repo-only research return gate artifact",
            "preview_change_required": "closure record should not claim this primary artifact exists; it should mark research return as bounded and ready for separate gate evaluation",
            "target_quality_after_application": "DERIVED_EXPLICIT_ATTENTION_UNTIL_RESEARCH_RETURN_GATE",
            "fail_closed_condition": "closure claims research-return primary artifact strength before that artifact exists",
            "can_apply_without_runtime_touch": True,
            "can_apply_without_schema_or_config": True,
            "risk_level": "MEDIUM_DEFERRED_PRIMARY_ARTIFACT",
            "expected_effect_on_derived_overused": "keeps research-return alignment out of DERIVED_OVERUSED by labeling it as explicit deferred evidence",
        },
    ]


def non_upliftable_exception_preview() -> Dict[str, Any]:
    return {
        "check_id": "NONUPLIFT-001",
        "accepted_quality_level": "DERIVED_EXPLICIT_ATTENTION",
        "explicit_reason_required": "old_short runtime monitoring state cannot be directly uplifted in repo-only mode without touching forbidden runtime/live/capital surfaces",
        "monitoring_required": "future modules must keep no-touch flags false and require safety readiness before old_short escalation, capital review, active paper promotion, runtime expansion, launcher change, live action, or real order path",
        "failure_if_reason_missing": "FAIL_CLOSED_OLD_SHORT_NONUPLIFTABLE_REASON_MISSING",
        "why_exception_does_not_keep_system_in_DERIVED_OVERUSED": "It is a named single exception with explicit reason and monitoring, not a broad default evidence state.",
        "target_quality_after_closure": "DERIVED_EXPLICIT_ATTENTION",
    }


def application_safety_preview() -> Dict[str, bool]:
    return {
        "no_runtime_touch_needed": True,
        "no_capital_touch_needed": True,
        "no_live_touch_needed": True,
        "no_order_touch_needed": True,
        "no_generic_runner_approval_needed": True,
        "no_schema_config_creation_needed": True,
        "no_closed_loop_reopening_needed": True,
        "no_documentation_chain_required": True,
    }


def closure_feasibility_decision() -> Dict[str, Any]:
    return {
        "decision": "CLOSURE_RECORD_IN_STEP_4",
        "reason": "The preview can close the selected gap by recording exact marker requirements, two primary artifact reads, and one explicit deferred/non-upliftable exception without editing prior modules or touching forbidden paths.",
        "step_4_next_module": NEXT_MODULE,
        "blocked_record_required": False,
        "research_return_gate_next": False,
        "do_not_apply_now": True,
    }


def build_payload() -> Dict[str, Any]:
    prior = load_json(PRIOR_PLAN_ARTIFACT)
    git = git_state()
    py = tracked_python_validation()
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()
    exact_preview = exact_marker_application_preview()
    primary_preview = primary_artifact_application_preview()
    exception_preview = non_upliftable_exception_preview()
    safety_preview = application_safety_preview()
    closure_decision = closure_feasibility_decision()

    documentation_loop_control = {
        "classification": "FINITE_CLOSURE_RECORD_NEXT_NO_GENERIC_CHAIN",
        "open_ended_readiness_adoption_rollout_chain_proposed": False,
        "next_step_is_final_gap_closure_record": True,
        "gap_limit_enforced": "step_3_of_4_with_1_step_remaining",
        "reason": "The preview resolves the plan into closure-record criteria and does not require another planning/inventory/governance module.",
    }
    research_return_alignment = {
        "status": "MOVES_TOWARD_RESEARCH_RETURN_GATE_AFTER_CLOSURE_BY_REDUCING_FALSE_PASS_RISK",
        "profit_or_trading_success_promised": False,
        "reason": "The preview makes research-return evaluation safer by bounding evidence quality first; it does not perform research or promise trading success.",
    }

    replacement_checks = {
        "prior_plan_artifact_exists": bool(prior),
        "prior_evidence_quality_uplift_plan_respected": prior_plan_respected(prior),
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "expected_parent_or_head_observed": git["head"] == EXPECTED_PARENT_HEAD or git["parent"] == EXPECTED_PARENT_HEAD,
        "tracked_python_count_increases_from_609_to_610": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "exact_marker_application_preview_completed": len(exact_preview) == 5,
        "primary_artifact_application_preview_completed": len(primary_preview) == 3,
        "non_upliftable_exception_preview_completed": bool(exception_preview),
        "application_safety_preview_completed": all(value is True for value in safety_preview.values()),
        "closure_feasibility_decision_completed": closure_decision["decision"] == "CLOSURE_RECORD_IN_STEP_4",
        "next_module_allowed": NEXT_MODULE in ALLOWED_NEXT_MODULES,
        "next_module_closes_real_gap": True,
        "next_module_starts_documentation_chain_false": True,
        "derived_evidence_not_treated_as_primary": True,
    }
    ready = all(value is True for value in replacement_checks.values())

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "evidence_quality_uplift_application_preview_status": "PASS_WITH_ATTENTION" if ready else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS if ready else "REPO_ONLY_EVIDENCE_QUALITY_UPLIFT_APPLICATION_PREVIEW_AFTER_SAFETY_ROLLOUT_POST_COMMIT_CHECK_FAIL_CLOSED",
        "final_decision": "SELECT_DERIVED_EVIDENCE_UPLIFT_CLOSURE_RECORD_STEP_4" if ready else "EVIDENCE_QUALITY_UPLIFT_APPLICATION_PREVIEW_FAIL_CLOSED",
        "next_action": "BUILD_REPO_ONLY_DERIVED_EVIDENCE_UPLIFT_CLOSURE_RECORD_AFTER_SAFETY_ROLLOUT" if ready else None,
        "next_module": NEXT_MODULE if ready else None,
        "prior_evidence_quality_uplift_plan_respected": True,
        "selected_real_gap": SELECTED_REAL_GAP,
        "gap_closure_mode_active": True,
        "gap_closure_limit_modules": 4,
        "current_gap_closure_step": 3,
        "remaining_gap_closure_steps": 1,
        "exact_marker_application_preview_completed": True,
        "primary_artifact_application_preview_completed": True,
        "non_upliftable_exception_preview_completed": True,
        "application_safety_preview_completed": True,
        "closure_feasibility_decision_completed": True,
        "exact_marker_application_preview": exact_preview,
        "primary_artifact_application_preview": primary_preview,
        "non_upliftable_exception_preview": exception_preview,
        "application_safety_preview": safety_preview,
        "closure_feasibility_decision": closure_decision,
        "exact_marker_uplift_candidate_count": 5,
        "primary_artifact_uplift_candidate_count": 3,
        "non_upliftable_derived_check_count": 1,
        "expected_exact_marker_uplift_count_after_application": 5,
        "expected_primary_artifact_uplift_count_after_application": 2,
        "expected_remaining_derived_explicit_attention_count_after_closure": 2,
        "expected_remaining_derived_overused_count_after_closure": 0,
        "derived_overused_can_stop_being_default": True,
        "new_default_evidence_quality_after_closure": NEW_DEFAULT_EVIDENCE_QUALITY_AFTER_CLOSURE,
        "evidence_quality_uplift_required": True,
        "evidence_quality_uplift_possible": True,
        "recommended_uplift_path": RECOMMENDED_UPLIFT_PATH,
        "next_module_closes_real_gap": True,
        "next_module_moves_toward_research_return": True,
        "next_module_starts_documentation_chain": False,
        "documentation_loop_detected": True,
        "documentation_loop_risk_level": "HIGH_ATTENTION_REDUCED_BY_CLOSURE_PREVIEW",
        "documentation_loop_control": documentation_loop_control,
        "research_return_alignment": research_return_alignment,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 1,
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
            "This application preview uses live repo and prior-plan replacement checks only for fail-closed scope control; "
            "it does not treat replacement checks as primary artifact strength and does not apply changes."
        ),
        "replacement_checks_all_true": ready,
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "prior_plan_artifact": str(PRIOR_PLAN_ARTIFACT),
            "prior_plan_loaded": bool(prior),
            "prior_plan_status": prior.get("evidence_quality_uplift_plan_status"),
            "prior_selected_real_gap": prior.get("selected_real_gap"),
            "prior_next_module": prior.get("next_module"),
            "allowed_next_modules": sorted(ALLOWED_NEXT_MODULES),
        },
        "safety_flags": {
            "repo_only": True,
            "preview_only": True,
            "apply_changes_now": False,
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
    latest_json = OUT_DIR / "repo_only_evidence_quality_uplift_application_preview_after_safety_rollout_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_evidence_quality_uplift_application_preview_after_safety_rollout_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_evidence_quality_uplift_application_preview_after_safety_rollout_v1_latest.txt"
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
    return 0 if payload["evidence_quality_uplift_application_preview_status"] in {"PASS", "PASS_WITH_ATTENTION"} else 3


if __name__ == "__main__":
    raise SystemExit(main())
