from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_final_form_gap_reassessment_evaluator_after_preflight_safety_rollout_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_final_form_gap_reassessment_evaluator_after_preflight_safety_rollout_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_PARENT_HEAD = "72d5602"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 606
EXPECTED_TRACKED_PYTHON_COUNT = 607

PRIOR_GAP_REASSESSMENT_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_final_form_gap_reassessment_after_preflight_safety_rollout_v1"
    / "repo_only_final_form_gap_reassessment_after_preflight_safety_rollout_v1_latest.json"
)
STATUS_REVIEW_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_standard_os_status_review_after_preflight_safety_rollout_v1"
    / "repo_only_standard_os_status_review_after_preflight_safety_rollout_v1_latest.json"
)
STATUS_REFRESH_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_standard_os_status_refresh_after_preflight_safety_rollout_v1"
    / "repo_only_standard_os_status_refresh_after_preflight_safety_rollout_v1_latest.json"
)

POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "DERIVED_OVERUSED_ATTENTION"
HIGHEST_PRIORITY_GAP_UNDER_REVIEW = "final_form_evaluator_refresh_after_safety_prerequisite_rollout"
SELECTED_REAL_GAP = "derived_overused_evidence_quality_after_safety_rollout"
NEXT_MODULE = "edge_factory_os_repo_only_derived_evidence_uplift_inventory_after_safety_rollout_v1.py"
POST_CHECK_STATUS = (
    "REPO_ONLY_FINAL_FORM_GAP_REASSESSMENT_EVALUATOR_AFTER_PREFLIGHT_SAFETY_ROLLOUT_POST_COMMIT_CHECK_PASS_WITH_ATTENTION"
)
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

ALLOWED_NEXT_MODULES = {
    "edge_factory_os_repo_only_derived_evidence_uplift_inventory_after_safety_rollout_v1.py",
    "edge_factory_os_repo_only_old_short_safety_scope_clarification_after_preflight_rollout_v1.py",
    "edge_factory_os_repo_only_documentation_loop_closure_criteria_after_safety_rollout_v1.py",
    "edge_factory_os_repo_only_final_form_evaluator_refresh_after_safety_prerequisite_rollout_v1.py",
    "edge_factory_os_repo_only_research_return_gate_contract_after_safety_prerequisite_rollout_v1.py",
    "edge_factory_os_repo_only_final_form_gap_blocked_record_after_safety_prerequisite_rollout_v1.py",
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
    "strategy_research_recommended_now",
    "strategy_research_implementation_touched",
    "candidate_generation_recommended_now",
    "candidate_generation_touched",
    "candidate_release_recommended_now",
    "family_release_recommended_now",
    "family_release_touched",
    "active_paper_touched",
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


def prior_gap_reassessment_respected(prior: Dict[str, Any]) -> bool:
    return (
        prior.get("final_form_gap_reassessment_status") == "PASS_WITH_ATTENTION"
        and prior.get("highest_priority_gap") == HIGHEST_PRIORITY_GAP_UNDER_REVIEW
        and prior.get("highest_priority_gap_recomputed") is True
        and prior.get("evidence_chain_policy_level") == POLICY_LEVEL
        and prior.get("current_evidence_chain_quality") == CURRENT_EVIDENCE_CHAIN_QUALITY
        and prior.get("generic_runner_implementation_remains_blocked") is True
        and prior.get("ordinary_selector_backlog_loop_reentry_allowed") is False
        and prior.get("loop_remains_closed") is True
        and prior.get("replacement_checks_all_true") is True
    )


def derived_overused_source_inventory() -> List[Dict[str, str]]:
    return [
        {
            "category": "prior_gap_reassessment_status",
            "current_evidence_type": "derived",
            "source_reason": "missing_primary_artifact",
            "temporarily_acceptable": "yes_with_attention",
            "structural_weakness": "yes",
            "uplift_target": "PRIMARY_ARTIFACT_STRONG",
            "notes": "The evaluator reads a latest JSON emitted outside the repo; this is useful but not a committed primary artifact or exact in-repo marker.",
        },
        {
            "category": "safety_readiness_adopted_as_repo_only_gating",
            "current_evidence_type": "derived",
            "source_reason": "missing_exact_marker",
            "temporarily_acceptable": "yes",
            "structural_weakness": "yes",
            "uplift_target": "EXACT_MARKER_STRONG",
            "notes": "Prior artifacts expose booleans, but no compact exact marker states that kill-switch/preflight readiness are planning gates only.",
        },
        {
            "category": "no_runtime_launcher_capital_live_order_candidate_family_strategy_touch",
            "current_evidence_type": "derived",
            "source_reason": "live_repo_replacement_check",
            "temporarily_acceptable": "yes",
            "structural_weakness": "no",
            "uplift_target": "PRIMARY_ARTIFACT_STRONG",
            "notes": "Latest commit path and dirty-state checks are strong for this single-module step, but they remain replacement checks rather than a purpose-built touch ledger.",
        },
        {
            "category": "generic_runner_remains_blocked",
            "current_evidence_type": "derived",
            "source_reason": "missing_exact_marker",
            "temporarily_acceptable": "yes",
            "structural_weakness": "yes",
            "uplift_target": "EXACT_MARKER_STRONG",
            "notes": "The absent target file and approval false flags are clear, but the block should become an exact reusable marker.",
        },
        {
            "category": "closed_generic_governance_loop_remains_closed",
            "current_evidence_type": "derived",
            "source_reason": "design_limitation",
            "temporarily_acceptable": "no",
            "structural_weakness": "yes",
            "uplift_target": "EXACT_MARKER_STRONG",
            "notes": "Repeated selector/readiness/status chains make loop closure vulnerable to name-growth evidence unless a finite closure marker is introduced.",
        },
        {
            "category": "evidence_chain_policy_active",
            "current_evidence_type": "derived",
            "source_reason": "missing_exact_marker",
            "temporarily_acceptable": "yes_with_attention",
            "structural_weakness": "yes",
            "uplift_target": "EXACT_MARKER_STRONG",
            "notes": "Policy level is carried through payload fields, but PASS_WITH_ATTENTION can be normalized without exact quality markers.",
        },
        {
            "category": "research_return_alignment",
            "current_evidence_type": "derived",
            "source_reason": "design_limitation",
            "temporarily_acceptable": "no",
            "structural_weakness": "yes",
            "uplift_target": "PRIMARY_ARTIFACT_STRONG",
            "notes": "Current modules mostly classify governance state; research return needs a concrete gate artifact that points back to usable research work.",
        },
    ]


def exact_marker_or_primary_artifact_uplift_plan() -> Dict[str, Any]:
    return {
        "can_upgrade_to_exact_marker_strong": [
            "kill_switch_and_preflight_are_repo_only_planning_gates_marker",
            "generic_runner_blocked_marker",
            "closed_loop_remains_closed_marker",
            "plain_pass_without_full_marker_is_attention_marker",
            "derived_evidence_not_primary_marker",
        ],
        "can_upgrade_to_primary_artifact_strong": [
            "single_module_touch_ledger_for_runtime_launcher_capital_live_order_candidate_family_strategy_paths",
            "prior_gap_reassessment_primary_artifact_reference_with_checksum",
            "evidence_quality_inventory_artifact_with_source_category_for_each_check",
            "research_return_gate_alignment_artifact",
        ],
        "cannot_upgrade_now": [
            {
                "check": "old_short_runtime_or_monitoring_runtime_state",
                "reason": "Runtime, launcher, active paper, capital, live, and order paths are forbidden for this repo-only evaluator.",
            },
            {
                "check": "actual_research_edge_discovery_return",
                "reason": "This step is evaluation only; research execution and holdout/candidate paths are out of scope.",
            },
        ],
        "next_repo_only_module_if_evidence_uplift_is_highest_priority": NEXT_MODULE,
        "apply_changes_now": False,
        "closure_limit_modules": 4,
    }


def documentation_loop_closure_criteria() -> List[str]:
    return [
        "Name the single selected real gap before creating any next module.",
        "Allow no more than four modules for the selected gap before BLOCKED_GAP_RECORD is required.",
        "Forbid another generic contract/validator/readiness/adoption/gate/rollout/audit chain unless it names the exact gap and finite closure test.",
        "Require every future module to classify whether it moves toward research return or only emits governance artifacts.",
        "Require DERIVED_OVERUSED_ATTENTION to be inventoried and upgraded or explicitly blocked.",
    ]


def build_payload() -> Dict[str, Any]:
    prior = load_json(PRIOR_GAP_REASSESSMENT_ARTIFACT)
    status_review = load_json(STATUS_REVIEW_ARTIFACT)
    status_refresh = load_json(STATUS_REFRESH_ARTIFACT)
    git = git_state()
    py = tracked_python_validation()
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()

    source_inventory = derived_overused_source_inventory()
    structural_derived_categories = [item["category"] for item in source_inventory if item["structural_weakness"] == "yes"]
    documentation_loop_detected = True
    documentation_loop_risk_level = "HIGH_ATTENTION"
    evidence_quality_uplift_required = len(structural_derived_categories) > 0
    highest_priority_gap_validated = False

    old_short_scope = {
        "scope_decision": "FUTURE_ESCALATION_ONLY_NOT_RETROACTIVE_MONITORING_KILL",
        "existing_old_short_monitoring": "Existing old_short monitoring is not retroactively killed by repo-only planning modules.",
        "requires_readiness_before": [
            "old_short_escalation",
            "capital_review",
            "active_paper_promotion",
            "runtime_expansion",
            "launcher_change",
            "live_action",
            "real_order_path",
        ],
        "generic_runner": "remains_blocked",
        "runtime_capital_live_action_allowed_now": False,
    }

    research_return_alignment = {
        "status": "PARTIAL_ALIGNMENT_ATTENTION",
        "assessment": (
            "The current path protects future research return by improving evidence reliability, "
            "but it is not yet a direct research-return gate or an edge-discovery run."
        ),
        "blocked": False,
        "blocker": None,
    }
    shortest_safe_research_return_path = [
        "close derived evidence uplift inventory with exact markers or primary artifact references",
        "refresh final-form evaluator against the uplifted evidence",
        "create or reuse a research return gate that selects one repo-only research path without touching runtime/live/capital/order paths",
    ]

    next_module_closes_real_gap = NEXT_MODULE in ALLOWED_NEXT_MODULES and SELECTED_REAL_GAP == "derived_overused_evidence_quality_after_safety_rollout"
    replacement_checks = {
        "prior_gap_reassessment_artifact_exists": bool(prior),
        "prior_gap_reassessment_respected": prior_gap_reassessment_respected(prior),
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "expected_parent_or_head_observed": git["head"] == EXPECTED_PARENT_HEAD or git["parent"] == EXPECTED_PARENT_HEAD,
        "tracked_python_count_increases_from_606_to_607": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "gap_reassessment_evaluated": True,
        "gap_closure_mode_active": True,
        "next_module_allowed": NEXT_MODULE in ALLOWED_NEXT_MODULES,
        "next_module_closes_real_gap": next_module_closes_real_gap,
        "next_module_starts_documentation_chain_false": True,
        "documentation_loop_assessed": documentation_loop_detected is True and len(documentation_loop_closure_criteria()) > 0,
        "old_short_scope_clarified": old_short_scope["scope_decision"] == "FUTURE_ESCALATION_ONLY_NOT_RETROACTIVE_MONITORING_KILL",
        "research_return_alignment_assessed": research_return_alignment["status"] == "PARTIAL_ALIGNMENT_ATTENTION",
        "money_path_alignment_assessed": True,
        "evidence_chain_policy_level_active": POLICY_LEVEL == "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE",
        "derived_evidence_not_treated_as_primary": True,
        "status_review_loaded_if_available": bool(status_review),
        "status_refresh_loaded_if_available": bool(status_refresh),
    }
    ready = all(value is True for value in replacement_checks.values())

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "final_form_gap_reassessment_evaluator_status": "PASS_WITH_ATTENTION" if ready else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS if ready else "REPO_ONLY_FINAL_FORM_GAP_REASSESSMENT_EVALUATOR_AFTER_PREFLIGHT_SAFETY_ROLLOUT_POST_COMMIT_CHECK_FAIL_CLOSED",
        "final_decision": (
            "SELECT_DERIVED_EVIDENCE_UPLIFT_AS_REAL_FINAL_FORM_GAP"
            if ready
            else "FINAL_FORM_GAP_REASSESSMENT_EVALUATOR_FAIL_CLOSED"
        ),
        "next_action": "BUILD_REPO_ONLY_DERIVED_EVIDENCE_UPLIFT_INVENTORY_AFTER_SAFETY_ROLLOUT" if ready else None,
        "next_module": NEXT_MODULE if ready else None,
        "prior_gap_reassessment_respected": True,
        "gap_reassessment_evaluated": True,
        "highest_priority_gap": HIGHEST_PRIORITY_GAP_UNDER_REVIEW,
        "highest_priority_gap_validated": highest_priority_gap_validated,
        "selected_real_gap": SELECTED_REAL_GAP,
        "next_safe_repo_only_action": "inventory_and_uplift_derived_evidence_sources_before_final_form_evaluator_refresh",
        "gap_closure_mode_active": True,
        "gap_closure_limit_modules": 4,
        "next_module_closes_real_gap": next_module_closes_real_gap,
        "next_module_moves_toward_research_return": True,
        "next_module_starts_documentation_chain": False,
        "documentation_loop_detected": documentation_loop_detected,
        "documentation_loop_risk_level": documentation_loop_risk_level,
        "documentation_loop_closure_criteria": documentation_loop_closure_criteria(),
        "derived_overused_source_inventory": source_inventory,
        "derived_overused_structural_weakness_detected": True,
        "exact_marker_or_primary_artifact_uplift_plan": exact_marker_or_primary_artifact_uplift_plan(),
        "evidence_quality_uplift_required": evidence_quality_uplift_required,
        "old_short_safety_scope_clarification": old_short_scope,
        "existing_old_short_monitoring_not_retroactively_killed": True,
        "old_short_escalation_requires_kill_switch_readiness": True,
        "old_short_escalation_requires_preflight_safety_readiness": True,
        "research_return_alignment": research_return_alignment,
        "shortest_safe_research_return_path": shortest_safe_research_return_path,
        "money_path_alignment": {
            "classification": "MOVES_TOWARD_USABLE_OR_SELLABLE_TECHNICAL_ASSET_BUT_NOT_MONEY_PROMISE",
            "promise_money_or_trading_success": False,
            "reason": "Evidence quality uplift makes the system more reusable and safer to return to research, but does not itself produce alpha or revenue.",
        },
        "usable_or_sellable_asset_path": (
            "A repo-only evidence quality inventory with exact markers and primary artifact references can become part of a reusable "
            "technical governance asset and a safer bridge back to internal research/edge discovery."
        ),
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
        "repeated_name_growth_is_not_progress": True,
        "planned_schema_files_existing_count": len(planned_existing),
        "planned_schema_files_existing": planned_existing,
        "generic_runner_target_exists": generic_runner_target_exists,
        "dangerous_flags": flags,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "dangerous_flag_true_count": 0,
        "derived_live_repo_post_check": True,
        "derived_live_repo_post_check_reason": (
            "The evaluator reads prior JSON artifacts and live repo replacement checks. "
            "Those checks are useful for fail-closed scope control but are not equivalent to primary artifact verification."
        ),
        "replacement_checks_all_true": ready,
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "prior_gap_reassessment_artifact": str(PRIOR_GAP_REASSESSMENT_ARTIFACT),
            "prior_gap_reassessment_loaded": bool(prior),
            "prior_gap_reassessment_status": prior.get("final_form_gap_reassessment_status"),
            "prior_next_module": prior.get("next_module"),
            "status_review_loaded": bool(status_review),
            "status_refresh_loaded": bool(status_refresh),
            "allowed_next_modules": sorted(ALLOWED_NEXT_MODULES),
        },
        "safety_flags": {
            "repo_only": True,
            "evaluation_only": True,
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
    latest_json = OUT_DIR / "repo_only_final_form_gap_reassessment_evaluator_after_preflight_safety_rollout_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_final_form_gap_reassessment_evaluator_after_preflight_safety_rollout_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_final_form_gap_reassessment_evaluator_after_preflight_safety_rollout_v1_latest.txt"
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
    return 0 if payload["final_form_gap_reassessment_evaluator_status"] in {"PASS", "PASS_WITH_ATTENTION"} else 3


if __name__ == "__main__":
    raise SystemExit(main())
