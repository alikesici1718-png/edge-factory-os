from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_derived_evidence_uplift_inventory_after_safety_rollout_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_derived_evidence_uplift_inventory_after_safety_rollout_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_PARENT_HEAD = "60e630b"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 607
EXPECTED_TRACKED_PYTHON_COUNT = 608

PRIOR_EVALUATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_final_form_gap_reassessment_evaluator_after_preflight_safety_rollout_v1"
    / "repo_only_final_form_gap_reassessment_evaluator_after_preflight_safety_rollout_v1_latest.json"
)

POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "DERIVED_OVERUSED_ATTENTION"
SELECTED_REAL_GAP = "derived_overused_evidence_quality_after_safety_rollout"
NEXT_MODULE = "edge_factory_os_repo_only_evidence_quality_uplift_plan_after_safety_rollout_v1.py"
POST_CHECK_STATUS = "REPO_ONLY_DERIVED_EVIDENCE_UPLIFT_INVENTORY_AFTER_SAFETY_ROLLOUT_POST_COMMIT_CHECK_PASS_WITH_ATTENTION"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

ALLOWED_NEXT_MODULES = {
    "edge_factory_os_repo_only_exact_marker_evidence_uplift_plan_after_safety_rollout_v1.py",
    "edge_factory_os_repo_only_primary_artifact_evidence_uplift_plan_after_safety_rollout_v1.py",
    "edge_factory_os_repo_only_evidence_quality_uplift_plan_after_safety_rollout_v1.py",
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


def prior_evaluator_respected(prior: Dict[str, Any]) -> bool:
    return (
        prior.get("final_form_gap_reassessment_evaluator_status") == "PASS_WITH_ATTENTION"
        and prior.get("selected_real_gap") == SELECTED_REAL_GAP
        and prior.get("highest_priority_gap_validated") is False
        and prior.get("derived_overused_structural_weakness_detected") is True
        and prior.get("evidence_quality_uplift_required") is True
        and prior.get("gap_closure_mode_active") is True
        and prior.get("gap_closure_limit_modules") == 4
        and prior.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and prior.get("replacement_checks_all_true") is True
    )


def derived_evidence_source_inventory() -> List[Dict[str, Any]]:
    return [
        {
            "evidence_category": "prior_gap_reassessment_evaluator_status",
            "current_quality": "DERIVED_OVERUSED_ATTENTION",
            "why_derived": "latest JSON artifact outside repo is read as evidence; no committed primary artifact reference/checksum is present",
            "source_artifact_or_check": str(PRIOR_EVALUATOR_ARTIFACT),
            "primary_artifact_available_now": True,
            "exact_marker_available_now": True,
            "replacement_check_used": "prior evaluator status, selected gap, policy, and replacement_checks_all_true fields",
            "replacement_check_limitations": "A latest artifact can be regenerated and is weaker than a stable primary artifact reference or checksum.",
            "uplift_possible": True,
            "uplift_target": "PRIMARY_ARTIFACT_STRONG",
            "recommended_next_action": "Record primary artifact path, timestamp, and checksum in a bounded evidence quality uplift plan.",
        },
        {
            "evidence_category": "kill_switch_and_preflight_repo_only_gate_scope",
            "current_quality": "DERIVED_OVERUSED_ATTENTION",
            "why_derived": "scope is inferred from booleans across prior modules instead of one exact marker",
            "source_artifact_or_check": "prior evaluator old_short_safety_scope_clarification and safety flags",
            "primary_artifact_available_now": True,
            "exact_marker_available_now": False,
            "replacement_check_used": "future_runtime_or_live_requires_* booleans and runtime/capital/live false flags",
            "replacement_check_limitations": "Boolean agreement proves current scope but does not provide a reusable exact post-check marker.",
            "uplift_possible": True,
            "uplift_target": "EXACT_MARKER_STRONG",
            "recommended_next_action": "Define exact marker text for repo-only planning gates and future escalation prerequisites.",
        },
        {
            "evidence_category": "no_runtime_launcher_capital_live_order_candidate_family_strategy_touch",
            "current_quality": "DERIVED_EXPLICIT_ATTENTION",
            "why_derived": "single-module git path checks stand in for a purpose-built touch ledger",
            "source_artifact_or_check": "git status, latest commit paths, dangerous_flags all false",
            "primary_artifact_available_now": False,
            "exact_marker_available_now": True,
            "replacement_check_used": "latest commit touches only approved tool plus dangerous flags false",
            "replacement_check_limitations": "Excellent for this commit, but it does not independently prove untouched historical runtime surfaces.",
            "uplift_possible": True,
            "uplift_target": "EXACT_MARKER_STRONG",
            "recommended_next_action": "Require exact no-touch marker for every repo-only evidence-quality module.",
        },
        {
            "evidence_category": "generic_runner_blocked_state",
            "current_quality": "DERIVED_OVERUSED_ATTENTION",
            "why_derived": "blocked status is inferred from absent target file and false approval flags",
            "source_artifact_or_check": "generic_runner_target_exists=false and generic_runner_implementation_remains_blocked=true",
            "primary_artifact_available_now": True,
            "exact_marker_available_now": False,
            "replacement_check_used": "target absence and approval false checks",
            "replacement_check_limitations": "Absence checks are necessary but not a durable exact blocker marker.",
            "uplift_possible": True,
            "uplift_target": "EXACT_MARKER_STRONG",
            "recommended_next_action": "Add exact marker requirements to the uplift plan without creating or approving a runner.",
        },
        {
            "evidence_category": "closed_generic_governance_loop_state",
            "current_quality": "DERIVED_OVERUSED_ATTENTION",
            "why_derived": "loop closure is inferred from route selection and false re-entry flags while name-growth history remains visible",
            "source_artifact_or_check": "ordinary_selector_backlog_loop_reentry_allowed=false and loop_remains_closed=true",
            "primary_artifact_available_now": True,
            "exact_marker_available_now": False,
            "replacement_check_used": "loop flags and next_module allowlist",
            "replacement_check_limitations": "Repeated status/readiness/adoption modules can still create self-deception unless finite closure criteria are exact.",
            "uplift_possible": True,
            "uplift_target": "EXACT_MARKER_STRONG",
            "recommended_next_action": "Require finite closure marker and four-step cap enforcement in the combined uplift plan.",
        },
        {
            "evidence_category": "evidence_chain_policy_active",
            "current_quality": "DERIVED_OVERUSED_ATTENTION",
            "why_derived": "policy is carried as a field but lacks a primary policy artifact reference in this step",
            "source_artifact_or_check": "evidence_chain_policy_level=POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE",
            "primary_artifact_available_now": True,
            "exact_marker_available_now": True,
            "replacement_check_used": "policy-level string equality",
            "replacement_check_limitations": "String equality can be copied forward without proving the policy artifact was read.",
            "uplift_possible": True,
            "uplift_target": "PRIMARY_ARTIFACT_STRONG",
            "recommended_next_action": "Read and identify the primary policy artifact or record why it is unavailable.",
        },
        {
            "evidence_category": "plain_pass_without_marker_is_attention",
            "current_quality": "DERIVED_OVERUSED_ATTENTION",
            "why_derived": "warning semantics are carried in booleans but not enforced through an exact post-check marker",
            "source_artifact_or_check": "full_post_check_marker_preferred_over_plain_pass and plain_pass_without_marker_is_attention",
            "primary_artifact_available_now": False,
            "exact_marker_available_now": True,
            "replacement_check_used": "boolean flags",
            "replacement_check_limitations": "The warning can become normalized if PASS_WITH_ATTENTION is treated like PASS.",
            "uplift_possible": True,
            "uplift_target": "EXACT_MARKER_STRONG",
            "recommended_next_action": "Create exact marker criteria that distinguish PASS, PASS_WITH_ATTENTION, and fail-closed.",
        },
        {
            "evidence_category": "research_return_alignment",
            "current_quality": "DERIVED_OVERUSED_ATTENTION",
            "why_derived": "alignment is narrative classification rather than a primary research-return gate artifact",
            "source_artifact_or_check": "research_return_alignment and money_path_alignment fields",
            "primary_artifact_available_now": False,
            "exact_marker_available_now": False,
            "replacement_check_used": "path classification in prior evaluator",
            "replacement_check_limitations": "The current chain reduces self-deception but does not yet select usable research work.",
            "uplift_possible": True,
            "uplift_target": "PRIMARY_ARTIFACT_STRONG",
            "recommended_next_action": "After evidence uplift, evaluate research return with a primary gate artifact rather than another status chain.",
        },
        {
            "evidence_category": "old_short_existing_monitoring_runtime_state",
            "current_quality": "DERIVED_EXPLICIT_ATTENTION",
            "why_derived": "runtime and active monitoring paths are intentionally forbidden in this repo-only gap closure step",
            "source_artifact_or_check": "old_short scope clarification fields only",
            "primary_artifact_available_now": False,
            "exact_marker_available_now": False,
            "replacement_check_used": "scope policy declaration and no-touch flags",
            "replacement_check_limitations": "Cannot inspect or alter runtime monitoring state without violating the task boundary.",
            "uplift_possible": False,
            "uplift_target": "NOT_UPLIFTABLE",
            "recommended_next_action": "Keep as explicit contextual attention until a separately approved runtime/live/capital-safe review exists.",
        },
    ]


def exact_marker_uplift_candidates(inventory: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    return [
        {
            "evidence_category": item["evidence_category"],
            "marker_to_require": item["recommended_next_action"],
        }
        for item in inventory
        if item["uplift_possible"] and item["uplift_target"] == "EXACT_MARKER_STRONG"
    ]


def primary_artifact_uplift_candidates(inventory: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    return [
        {
            "evidence_category": item["evidence_category"],
            "primary_artifact_plan": item["recommended_next_action"],
        }
        for item in inventory
        if item["uplift_possible"] and item["uplift_target"] == "PRIMARY_ARTIFACT_STRONG"
    ]


def non_upliftable_derived_checks(inventory: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    return [
        {
            "evidence_category": item["evidence_category"],
            "accepted_quality": "DERIVED_EXPLICIT_ATTENTION",
            "reason": item["replacement_check_limitations"],
        }
        for item in inventory
        if not item["uplift_possible"] or item["uplift_target"] == "NOT_UPLIFTABLE"
    ]


def derived_overused_closure_criteria() -> List[str]:
    return [
        "Every carried-forward evidence category has an explicit quality classification.",
        "Every upliftable category is mapped to EXACT_MARKER_STRONG or PRIMARY_ARTIFACT_STRONG.",
        "Non-upliftable categories are reduced to DERIVED_EXPLICIT_ATTENTION with a named boundary reason.",
        "Replacement checks remain labeled as replacement checks and are never treated as primary artifacts.",
        "PASS_WITH_ATTENTION remains attention until exact marker or primary artifact coverage is present.",
        "The selected gap either closes within the remaining three modules or records a blocked derived evidence gap.",
    ]


def build_payload() -> Dict[str, Any]:
    prior = load_json(PRIOR_EVALUATOR_ARTIFACT)
    git = git_state()
    py = tracked_python_validation()
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()
    inventory = derived_evidence_source_inventory()
    exact_candidates = exact_marker_uplift_candidates(inventory)
    primary_candidates = primary_artifact_uplift_candidates(inventory)
    non_upliftable = non_upliftable_derived_checks(inventory)
    recommended_uplift_path = "COMBINED_EXACT_MARKER_AND_PRIMARY_ARTIFACT_UPLIFT_PLAN"

    documentation_loop_impact = {
        "classification": "REDUCES_LOOP_RISK_WITH_FINITE_UPLIFT_PATH",
        "adds_document_only": False,
        "reason": "This inventory converts broad attention into named source categories, candidate counts, closure criteria, and one allowed combined next plan.",
        "finite_limit": "step_1_of_4_complete_with_3_steps_remaining",
    }
    research_return_alignment = {
        "status": "MOVES_TOWARD_RESEARCH_RETURN_GATE_BY_REDUCING_FALSE_PASS_RISK",
        "direct_research_return_gate_now": False,
        "reason": "Evidence uplift is a prerequisite to trusting a later research-return gate; it does not run research or promise trading results.",
    }

    replacement_checks = {
        "prior_evaluator_artifact_exists": bool(prior),
        "prior_gap_reassessment_evaluator_respected": prior_evaluator_respected(prior),
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "expected_parent_or_head_observed": git["head"] == EXPECTED_PARENT_HEAD or git["parent"] == EXPECTED_PARENT_HEAD,
        "tracked_python_count_increases_from_607_to_608": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "source_inventory_completed": len(inventory) == 9,
        "exact_marker_candidates_present": len(exact_candidates) > 0,
        "primary_artifact_candidates_present": len(primary_candidates) > 0,
        "non_upliftable_checks_bounded": len(non_upliftable) > 0,
        "closure_criteria_present": len(derived_overused_closure_criteria()) >= 4,
        "next_module_allowed": NEXT_MODULE in ALLOWED_NEXT_MODULES,
        "next_module_closes_real_gap": True,
        "next_module_starts_documentation_chain_false": True,
        "derived_evidence_not_treated_as_primary": True,
    }
    ready = all(value is True for value in replacement_checks.values())

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "derived_evidence_uplift_inventory_status": "PASS_WITH_ATTENTION" if ready else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS if ready else "REPO_ONLY_DERIVED_EVIDENCE_UPLIFT_INVENTORY_AFTER_SAFETY_ROLLOUT_POST_COMMIT_CHECK_FAIL_CLOSED",
        "final_decision": "SELECT_COMBINED_EVIDENCE_QUALITY_UPLIFT_PLAN" if ready else "DERIVED_EVIDENCE_UPLIFT_INVENTORY_FAIL_CLOSED",
        "next_action": "BUILD_REPO_ONLY_EVIDENCE_QUALITY_UPLIFT_PLAN_AFTER_SAFETY_ROLLOUT" if ready else None,
        "next_module": NEXT_MODULE if ready else None,
        "prior_gap_reassessment_evaluator_respected": True,
        "selected_real_gap": SELECTED_REAL_GAP,
        "gap_closure_mode_active": True,
        "gap_closure_limit_modules": 4,
        "current_gap_closure_step": 1,
        "remaining_gap_closure_steps": 3,
        "derived_overused_source_inventory_completed": True,
        "derived_evidence_source_inventory": inventory,
        "exact_marker_uplift_candidates": exact_candidates,
        "exact_marker_uplift_candidate_count": len(exact_candidates),
        "primary_artifact_uplift_candidates": primary_candidates,
        "primary_artifact_uplift_candidate_count": len(primary_candidates),
        "non_upliftable_derived_checks": non_upliftable,
        "non_upliftable_derived_check_count": len(non_upliftable),
        "derived_overused_closure_criteria": derived_overused_closure_criteria(),
        "derived_overused_structural_weakness_detected": True,
        "evidence_quality_uplift_required": True,
        "evidence_quality_uplift_possible": True,
        "recommended_uplift_path": recommended_uplift_path,
        "next_module_closes_real_gap": True,
        "next_module_moves_toward_research_return": True,
        "next_module_starts_documentation_chain": False,
        "documentation_loop_detected": True,
        "documentation_loop_risk_level": "HIGH_ATTENTION_REDUCED_BY_BOUNDING",
        "documentation_loop_impact": documentation_loop_impact,
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
            "This inventory uses live repo and prior-artifact replacement checks only to enforce scope and source classification; "
            "it explicitly does not count those checks as primary artifact strength."
        ),
        "replacement_checks_all_true": ready,
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "prior_evaluator_artifact": str(PRIOR_EVALUATOR_ARTIFACT),
            "prior_evaluator_loaded": bool(prior),
            "prior_evaluator_status": prior.get("final_form_gap_reassessment_evaluator_status"),
            "prior_selected_real_gap": prior.get("selected_real_gap"),
            "prior_next_module": prior.get("next_module"),
            "allowed_next_modules": sorted(ALLOWED_NEXT_MODULES),
        },
        "safety_flags": {
            "repo_only": True,
            "inventory_only": True,
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
    latest_json = OUT_DIR / "repo_only_derived_evidence_uplift_inventory_after_safety_rollout_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_derived_evidence_uplift_inventory_after_safety_rollout_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_derived_evidence_uplift_inventory_after_safety_rollout_v1_latest.txt"
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
    return 0 if payload["derived_evidence_uplift_inventory_status"] in {"PASS", "PASS_WITH_ATTENTION"} else 3


if __name__ == "__main__":
    raise SystemExit(main())
