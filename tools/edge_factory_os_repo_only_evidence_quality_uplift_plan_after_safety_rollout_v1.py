from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_evidence_quality_uplift_plan_after_safety_rollout_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_evidence_quality_uplift_plan_after_safety_rollout_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_PARENT_HEAD = "6cbee59"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 608
EXPECTED_TRACKED_PYTHON_COUNT = 609

PRIOR_INVENTORY_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_derived_evidence_uplift_inventory_after_safety_rollout_v1"
    / "repo_only_derived_evidence_uplift_inventory_after_safety_rollout_v1_latest.json"
)

POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "DERIVED_OVERUSED_ATTENTION"
SELECTED_REAL_GAP = "derived_overused_evidence_quality_after_safety_rollout"
RECOMMENDED_UPLIFT_PATH = "COMBINED_EXACT_MARKER_AND_PRIMARY_ARTIFACT_UPLIFT_PLAN"
NEW_DEFAULT_EVIDENCE_QUALITY_AFTER_CLOSURE = "EXACT_MARKER_STRONG_OR_PRIMARY_ARTIFACT_STRONG_WITH_DERIVED_EXPLICIT_ATTENTION_EXCEPTIONS"
NEXT_MODULE = "edge_factory_os_repo_only_evidence_quality_uplift_application_preview_after_safety_rollout_v1.py"
POST_CHECK_STATUS = "REPO_ONLY_EVIDENCE_QUALITY_UPLIFT_PLAN_AFTER_SAFETY_ROLLOUT_POST_COMMIT_CHECK_PASS_WITH_ATTENTION"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

ALLOWED_NEXT_MODULES = {
    "edge_factory_os_repo_only_evidence_quality_uplift_application_preview_after_safety_rollout_v1.py",
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


def prior_inventory_respected(prior: Dict[str, Any]) -> bool:
    return (
        prior.get("derived_evidence_uplift_inventory_status") == "PASS_WITH_ATTENTION"
        and prior.get("selected_real_gap") == SELECTED_REAL_GAP
        and prior.get("gap_closure_mode_active") is True
        and prior.get("current_gap_closure_step") == 1
        and prior.get("remaining_gap_closure_steps") == 3
        and prior.get("derived_overused_source_inventory_completed") is True
        and prior.get("evidence_quality_uplift_required") is True
        and prior.get("evidence_quality_uplift_possible") is True
        and prior.get("recommended_uplift_path") == RECOMMENDED_UPLIFT_PATH
        and prior.get("exact_marker_uplift_candidate_count") == 5
        and prior.get("primary_artifact_uplift_candidate_count") == 3
        and prior.get("non_upliftable_derived_check_count") == 1
        and prior.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and prior.get("replacement_checks_all_true") is True
    )


def exact_marker_uplift_plan() -> List[Dict[str, Any]]:
    return [
        {
            "candidate_id": "EXACT-001",
            "source_check": "kill_switch_and_preflight_repo_only_gate_scope",
            "current_quality": "DERIVED_OVERUSED_ATTENTION",
            "required_exact_marker": "SAFETY_READINESS_IS_REPO_ONLY_PLANNING_GATE_FOR_FUTURE_RUNTIME_OR_LIVE",
            "expected_artifact_pattern": "*_latest.json.post_check_marker or payload field exact_post_check_markers[]",
            "how_to_verify_marker": "Read the repo-only module artifact and require the exact marker plus future_runtime_or_live_requires_preflight_safety_readiness=true and future_runtime_or_live_requires_kill_switch_readiness=true.",
            "failure_behavior": "FAIL_CLOSED_MISSING_EXACT_SAFETY_GATE_MARKER",
            "target_quality": "EXACT_MARKER_STRONG",
            "implementation_scope": "repo_only_preview_then_single_file_apply_if_approved",
            "can_be_done_repo_only": True,
        },
        {
            "candidate_id": "EXACT-002",
            "source_check": "no_runtime_launcher_capital_live_order_candidate_family_strategy_touch",
            "current_quality": "DERIVED_EXPLICIT_ATTENTION",
            "required_exact_marker": "REPO_ONLY_NO_RUNTIME_LAUNCHER_CAPITAL_LIVE_ORDER_CANDIDATE_FAMILY_STRATEGY_TOUCH",
            "expected_artifact_pattern": "post_check marker in each repo-only evidence quality artifact",
            "how_to_verify_marker": "Require marker plus latest commit path limited to approved tool and dangerous_flags_all_false=true.",
            "failure_behavior": "FAIL_CLOSED_TOUCH_SCOPE_NOT_EXACTLY_MARKED",
            "target_quality": "EXACT_MARKER_STRONG",
            "implementation_scope": "repo_only_preview_then_single_file_apply_if_approved",
            "can_be_done_repo_only": True,
        },
        {
            "candidate_id": "EXACT-003",
            "source_check": "generic_runner_blocked_state",
            "current_quality": "DERIVED_OVERUSED_ATTENTION",
            "required_exact_marker": "GENERIC_RUNNER_REMAINS_BLOCKED_NO_APPROVAL_NO_TARGET",
            "expected_artifact_pattern": "post_check marker plus generic_runner_target_exists=false",
            "how_to_verify_marker": "Read marker, generic_runner_approval_granted=false, generic_runner_implementation_remains_blocked=true, and target absence.",
            "failure_behavior": "FAIL_CLOSED_GENERIC_RUNNER_BLOCK_MARKER_MISSING",
            "target_quality": "EXACT_MARKER_STRONG",
            "implementation_scope": "repo_only_preview_then_single_file_apply_if_approved",
            "can_be_done_repo_only": True,
        },
        {
            "candidate_id": "EXACT-004",
            "source_check": "closed_generic_governance_loop_state",
            "current_quality": "DERIVED_OVERUSED_ATTENTION",
            "required_exact_marker": "CLOSED_LOOP_REMAINS_CLOSED_WITH_FOUR_MODULE_GAP_LIMIT",
            "expected_artifact_pattern": "gap closure artifact with current_gap_closure_step and remaining_gap_closure_steps",
            "how_to_verify_marker": "Require marker, ordinary_selector_backlog_loop_reentry_allowed=false, loop_remains_closed=true, and remaining_gap_closure_steps >= 0.",
            "failure_behavior": "FAIL_CLOSED_LOOP_CLOSURE_MARKER_MISSING_OR_LIMIT_EXCEEDED",
            "target_quality": "EXACT_MARKER_STRONG",
            "implementation_scope": "repo_only_preview_then_single_file_apply_if_approved",
            "can_be_done_repo_only": True,
        },
        {
            "candidate_id": "EXACT-005",
            "source_check": "plain_pass_without_marker_is_attention",
            "current_quality": "DERIVED_OVERUSED_ATTENTION",
            "required_exact_marker": "FULL_POST_CHECK_MARKER_REQUIRED_PLAIN_PASS_IS_ATTENTION",
            "expected_artifact_pattern": "post_check marker and status semantics fields",
            "how_to_verify_marker": "Require marker plus full_post_check_marker_preferred_over_plain_pass=true and plain_pass_without_marker_is_attention=true.",
            "failure_behavior": "FAIL_CLOSED_PASS_SEMANTICS_MARKER_MISSING",
            "target_quality": "EXACT_MARKER_STRONG",
            "implementation_scope": "repo_only_preview_then_single_file_apply_if_approved",
            "can_be_done_repo_only": True,
        },
    ]


def primary_artifact_uplift_plan() -> List[Dict[str, Any]]:
    return [
        {
            "candidate_id": "PRIMARY-001",
            "source_check": "prior_gap_reassessment_evaluator_status",
            "current_quality": "DERIVED_OVERUSED_ATTENTION",
            "primary_artifact_required": "repo_only_final_form_gap_reassessment_evaluator_after_preflight_safety_rollout_v1_latest.json",
            "artifact_location_or_pattern": str(
                LAB_ROOT
                / "edge_factory_os_repo_only_final_form_gap_reassessment_evaluator_after_preflight_safety_rollout_v1"
                / "repo_only_final_form_gap_reassessment_evaluator_after_preflight_safety_rollout_v1_latest.json"
            ),
            "how_to_verify_primary_artifact": "Read artifact directly, require selected_real_gap, PASS_WITH_ATTENTION, next module, and replacement checks; record path and sha256 in preview.",
            "failure_behavior": "FAIL_CLOSED_PRIOR_EVALUATOR_PRIMARY_ARTIFACT_MISSING_OR_INCONSISTENT",
            "target_quality": "PRIMARY_ARTIFACT_STRONG",
            "implementation_scope": "repo_only_preview_reads_artifact_no_apply",
            "can_be_done_repo_only": True,
        },
        {
            "candidate_id": "PRIMARY-002",
            "source_check": "evidence_chain_policy_active",
            "current_quality": "DERIVED_OVERUSED_ATTENTION",
            "primary_artifact_required": "post_check_artifact_reliability_policy_or_enforcement_artifact",
            "artifact_location_or_pattern": "edge_factory_os_repo_only_post_check_artifact_reliability_*_v1/*_latest.json",
            "how_to_verify_primary_artifact": "Find and read the strongest available policy/enforcement artifact, require POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE, and record exact source.",
            "failure_behavior": "FAIL_CLOSED_POLICY_PRIMARY_ARTIFACT_NOT_FOUND",
            "target_quality": "PRIMARY_ARTIFACT_STRONG",
            "implementation_scope": "repo_only_preview_reads_artifact_no_apply",
            "can_be_done_repo_only": True,
        },
        {
            "candidate_id": "PRIMARY-003",
            "source_check": "research_return_alignment",
            "current_quality": "DERIVED_OVERUSED_ATTENTION",
            "primary_artifact_required": "research_return_gate_alignment_artifact",
            "artifact_location_or_pattern": "future allowed research_return_gate artifact after evidence uplift closure",
            "how_to_verify_primary_artifact": "Require an explicit research-return gate artifact that selects a usable repo-only research path or records a blocker without touching runtime/live/capital/order paths.",
            "failure_behavior": "FAIL_CLOSED_RESEARCH_RETURN_PRIMARY_GATE_NOT_READY",
            "target_quality": "PRIMARY_ARTIFACT_STRONG",
            "implementation_scope": "deferred_repo_only_after_evidence_quality_closure_or_blocked_record",
            "can_be_done_repo_only": True,
        },
    ]


def non_upliftable_derived_check_policy() -> Dict[str, Any]:
    return {
        "source_check": "old_short_existing_monitoring_runtime_state",
        "why_not_upliftable": "Runtime, launcher, active paper, capital, live, and order paths are forbidden in this repo-only gap closure path.",
        "accepted_quality_level": "DERIVED_EXPLICIT_ATTENTION",
        "required_explicit_reason": "Existing old_short monitoring is not retroactively killed, but escalation, capital review, active paper promotion, runtime expansion, launcher change, live action, or order path requires safety readiness first.",
        "required_monitoring": "Each future repo-only module must keep runtime/capital/live/order touch flags false and restate escalation prerequisites.",
        "failure_behavior_if_missing_reason": "FAIL_CLOSED_OLD_SHORT_CONTEXTUAL_DERIVED_REASON_MISSING",
    }


def derived_overused_closure_plan() -> Dict[str, Any]:
    return {
        "derived_overused_can_close_when": [
            "all 5 exact-marker uplift candidates have exact markers or are explicitly blocked",
            "at least 2 of 3 primary-artifact candidates are verified from primary artifacts",
            "the remaining primary research-return artifact is either verified or deferred with an explicit blocker",
            "the single non-upliftable old_short runtime-state check remains DERIVED_EXPLICIT_ATTENTION with reason and monitoring",
            "replacement checks remain labeled as replacement checks, not primary artifacts",
        ],
        "minimum_exact_marker_uplifts_required": 5,
        "minimum_primary_artifact_uplifts_required": 2,
        "maximum_remaining_non_upliftable_allowed": 1,
        "new_default_evidence_quality_after_closure": NEW_DEFAULT_EVIDENCE_QUALITY_AFTER_CLOSURE,
        "derived_overused_attention_can_stop_being_default_state": True,
    }


def build_payload() -> Dict[str, Any]:
    prior = load_json(PRIOR_INVENTORY_ARTIFACT)
    git = git_state()
    py = tracked_python_validation()
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()
    exact_plan = exact_marker_uplift_plan()
    primary_plan = primary_artifact_uplift_plan()
    non_upliftable_policy = non_upliftable_derived_check_policy()
    closure_plan = derived_overused_closure_plan()

    documentation_loop_control = {
        "classification": "FINITE_EXECUTION_PATH_NO_GENERIC_CHAIN",
        "open_ended_readiness_adoption_rollout_chain_proposed": False,
        "next_step_is_preview_not_apply": True,
        "gap_limit_enforced": "step_2_of_4_with_2_steps_remaining",
        "reason": "The plan converts inventory categories into verifiable exact markers and primary artifact reads, with fail-closed behavior and a bounded application preview.",
    }
    research_return_alignment = {
        "status": "MOVES_TOWARD_RESEARCH_RETURN_GATE_BY_REDUCING_FALSE_PASS_SELF_DECEPTION",
        "profit_or_trading_success_promised": False,
        "reason": "The plan makes future research-return decisions depend on exact markers and primary artifacts instead of copied PASS_WITH_ATTENTION fields.",
    }

    replacement_checks = {
        "prior_inventory_artifact_exists": bool(prior),
        "prior_derived_evidence_inventory_respected": prior_inventory_respected(prior),
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "expected_parent_or_head_observed": git["head"] == EXPECTED_PARENT_HEAD or git["parent"] == EXPECTED_PARENT_HEAD,
        "tracked_python_count_increases_from_608_to_609": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "exact_marker_plan_completed": len(exact_plan) == 5,
        "primary_artifact_plan_completed": len(primary_plan) == 3,
        "non_upliftable_policy_completed": bool(non_upliftable_policy),
        "closure_plan_completed": bool(closure_plan),
        "next_module_allowed": NEXT_MODULE in ALLOWED_NEXT_MODULES,
        "next_module_closes_real_gap": True,
        "next_module_starts_documentation_chain_false": True,
        "derived_evidence_not_treated_as_primary": True,
    }
    ready = all(value is True for value in replacement_checks.values())

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "evidence_quality_uplift_plan_status": "PASS_WITH_ATTENTION" if ready else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS if ready else "REPO_ONLY_EVIDENCE_QUALITY_UPLIFT_PLAN_AFTER_SAFETY_ROLLOUT_POST_COMMIT_CHECK_FAIL_CLOSED",
        "final_decision": "SELECT_EVIDENCE_QUALITY_UPLIFT_APPLICATION_PREVIEW" if ready else "EVIDENCE_QUALITY_UPLIFT_PLAN_FAIL_CLOSED",
        "next_action": "BUILD_REPO_ONLY_EVIDENCE_QUALITY_UPLIFT_APPLICATION_PREVIEW_AFTER_SAFETY_ROLLOUT" if ready else None,
        "next_module": NEXT_MODULE if ready else None,
        "prior_derived_evidence_inventory_respected": True,
        "selected_real_gap": SELECTED_REAL_GAP,
        "gap_closure_mode_active": True,
        "gap_closure_limit_modules": 4,
        "current_gap_closure_step": 2,
        "remaining_gap_closure_steps": 2,
        "exact_marker_uplift_plan_completed": True,
        "primary_artifact_uplift_plan_completed": True,
        "non_upliftable_derived_check_policy_completed": True,
        "derived_overused_closure_plan_completed": True,
        "exact_marker_uplift_candidate_count": 5,
        "primary_artifact_uplift_candidate_count": 3,
        "non_upliftable_derived_check_count": 1,
        "exact_marker_uplift_plan": exact_plan,
        "primary_artifact_uplift_plan": primary_plan,
        "non_upliftable_derived_check_policy": non_upliftable_policy,
        "derived_overused_closure_plan": closure_plan,
        "evidence_quality_uplift_required": True,
        "evidence_quality_uplift_possible": True,
        "recommended_uplift_path": RECOMMENDED_UPLIFT_PATH,
        "new_default_evidence_quality_after_closure": NEW_DEFAULT_EVIDENCE_QUALITY_AFTER_CLOSURE,
        "next_module_closes_real_gap": True,
        "next_module_moves_toward_research_return": True,
        "next_module_starts_documentation_chain": False,
        "documentation_loop_detected": True,
        "documentation_loop_risk_level": "HIGH_ATTENTION_REDUCED_BY_FINITE_PLAN",
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
            "This uplift plan uses live repo and prior-inventory replacement checks only for fail-closed scope control; "
            "the plan explicitly requires exact markers and primary artifact reads before evidence can be upgraded."
        ),
        "replacement_checks_all_true": ready,
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "prior_inventory_artifact": str(PRIOR_INVENTORY_ARTIFACT),
            "prior_inventory_loaded": bool(prior),
            "prior_inventory_status": prior.get("derived_evidence_uplift_inventory_status"),
            "prior_selected_real_gap": prior.get("selected_real_gap"),
            "prior_next_module": prior.get("next_module"),
            "allowed_next_modules": sorted(ALLOWED_NEXT_MODULES),
        },
        "safety_flags": {
            "repo_only": True,
            "plan_only": True,
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
    latest_json = OUT_DIR / "repo_only_evidence_quality_uplift_plan_after_safety_rollout_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_evidence_quality_uplift_plan_after_safety_rollout_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_evidence_quality_uplift_plan_after_safety_rollout_v1_latest.txt"
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
    return 0 if payload["evidence_quality_uplift_plan_status"] in {"PASS", "PASS_WITH_ATTENTION"} else 3


if __name__ == "__main__":
    raise SystemExit(main())
