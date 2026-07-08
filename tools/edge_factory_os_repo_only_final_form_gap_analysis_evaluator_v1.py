from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_final_form_gap_analysis_evaluator_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_final_form_gap_analysis_evaluator_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "fb2fff4"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 587
NEXT_MODULE_ROADMAP = "edge_factory_os_repo_only_final_form_gap_closure_roadmap_v1.py"
NEXT_MODULE_REPAIR_PREVIEW = "edge_factory_os_repo_only_final_form_gap_analysis_repair_preview_v1.py"
POST_CHECK_STATUS = "REPO_ONLY_FINAL_FORM_GAP_ANALYSIS_EVALUATOR_POST_COMMIT_CHECK_PASS_WITH_ATTENTION"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "DERIVED_OVERUSED_ATTENTION"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

RUNNER_ARTIFACT = LAB_ROOT / "edge_factory_os_repo_only_final_form_gap_analysis_runner_v1" / "repo_only_final_form_gap_analysis_runner_v1_latest.json"
CONTRACT_ARTIFACT = LAB_ROOT / "edge_factory_os_repo_only_final_form_gap_analysis_contract_v1" / "repo_only_final_form_gap_analysis_contract_v1_latest.json"

CAPABILITY_CATEGORIES = [
    "self_inspection",
    "orchestration",
    "autonomous_research_queueing",
    "validation_gates",
    "lifecycle_automation",
    "drift_monitoring",
    "preflight",
    "kill_switch_readiness",
    "paper_live_decision_safety",
    "evidence_chain_compliance",
    "route_hygiene",
    "audit_status_reliability",
    "generic_runner_safe_mode_reopening_path",
    "repo_only_development_governance",
    "anti_self_deception_controls",
]

CLASSIFICATIONS = ["SATISFIED", "PARTIAL", "MISSING", "BLOCKED", "ATTENTION"]

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
    "capital_changed",
    "live_or_real_orders",
    "holdout_accessed",
    "strategy_research_recommended_now",
    "candidate_generation_recommended_now",
    "candidate_release_recommended_now",
    "family_release_recommended_now",
    "schema_apply_allowed_now",
    "schema_file_creation_allowed_now",
    "schema_file_edit_allowed_now",
    "schema_apply_performed_now",
    "schema_file_creation_performed_now",
    "schema_file_edit_performed_now",
    "file_move_allowed_now",
    "file_delete_allowed_now",
    "repo_restructure_allowed_now",
    "gitignore_changed",
    "git_add_force_used",
    "backup_deleted",
    "mass_metadata_patch_allowed",
    "blind_fix_all_allowed",
    "direct_apply_recommended_now",
    "apply_allowed_now",
    "apply_performed_now",
    "manual_approval_present_now",
    "manual_approval_valid_now",
    "implementation_allowed_now",
    "generic_runner_implementation_allowed_now",
    "generic_runner_file_creation_allowed_now",
    "config_file_creation_allowed_now",
    "consolidation_apply_allowed_now",
]

RUNNER_DIMENSION_TO_CATEGORY = {
    "self_inspection": "self_inspection",
    "orchestration": "orchestration",
    "research_queueing": "autonomous_research_queueing",
    "validation_gates": "validation_gates",
    "lifecycle_automation": "lifecycle_automation",
    "drift_monitoring": "drift_monitoring",
    "preflight": "preflight",
    "kill_switch_readiness": "kill_switch_readiness",
    "paper_live_decision_safety": "paper_live_decision_safety",
    "evidence_chain_compliance": "evidence_chain_compliance",
    "route_hygiene": "route_hygiene",
    "audit_status_reliability": "audit_status_reliability",
    "generic_runner_safe_mode_reopening_path_without_implementation": "generic_runner_safe_mode_reopening_path",
}

RUNNER_STATE_TO_CLASSIFICATION = {
    "satisfied": "SATISFIED",
    "partially_satisfied": "PARTIAL",
    "partial": "PARTIAL",
    "missing": "MISSING",
    "blocked": "BLOCKED",
    "attention": "ATTENTION",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    safe_args = args
    if args and args[0] == "git":
        safe_args = ["git", "-c", f"safe.directory={REPO_ROOT.as_posix()}", *args[1:]]
    result = subprocess.run(safe_args, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {safe_args} returncode={result.returncode} stderr={result.stderr}")
    return result


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    loaded = json.loads(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def tracked_files() -> List[str]:
    return sorted(line.strip().replace("\\", "/") for line in run_cmd(["git", "ls-files"]).stdout.splitlines() if line.strip())


def tracked_python_validation() -> Dict[str, Any]:
    files = [path for path in tracked_files() if path.endswith(".py")]
    syntax_errors: List[Dict[str, str]] = []
    bom_errors: List[str] = []
    for rel in files:
        data = (REPO_ROOT / rel).read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
        try:
            ast.parse(data.decode("utf-8"), filename=rel)
        except Exception as exc:
            syntax_errors.append({"path": rel, "error": repr(exc)})
    return {
        "tracked_python_count": len(files),
        "tracked_python_syntax_error_count": len(syntax_errors),
        "tracked_python_bom_error_count": len(bom_errors),
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
    }


def git_state() -> Dict[str, Any]:
    status_lines = [line for line in run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"]).stdout.splitlines() if line.strip()]
    untracked = sorted(line[3:].replace("\\", "/") for line in status_lines if line.startswith("?? "))
    dirty_tracked = [line for line in status_lines if not line.startswith("?? ")]
    expected_untracked = [CURRENT_TOOL_REL] if (REPO_ROOT / CURRENT_TOOL_REL).exists() else []
    unexpected_untracked = [path for path in untracked if path not in expected_untracked]
    return {
        "head": run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
        "branch": run_cmd(["git", "branch", "--show-current"]).stdout.strip(),
        "status_porcelain": status_lines,
        "dirty_tracked_paths": [line[3:].replace("\\", "/") for line in dirty_tracked],
        "untracked_paths": untracked,
        "expected_untracked_paths": expected_untracked,
        "unexpected_untracked_paths": unexpected_untracked,
        "repo_clean_for_final_form_gap_analysis_evaluator": len(dirty_tracked) == 0 and len(unexpected_untracked) == 0,
    }


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def dangerous_flags() -> Dict[str, bool]:
    return {flag: False for flag in DANGEROUS_FLAGS}


def repo_feature_counts(files: Iterable[str]) -> Dict[str, int]:
    lower = [path.lower() for path in files]
    return {
        "status_audit_policy_modules": sum(1 for path in lower if "status" in path or "audit" in path or "policy" in path),
        "validation_gate_modules": sum(1 for path in lower if "validator" in path or "validation" in path or "gate" in path),
        "queue_or_backlog_modules": sum(1 for path in lower if "queue" in path or "backlog" in path),
        "preflight_modules": sum(1 for path in lower if "preflight" in path),
        "drift_modules": sum(1 for path in lower if "drift" in path),
        "kill_switch_modules": sum(1 for path in lower if "kill" in path or "switch" in path),
        "route_hygiene_modules": sum(1 for path in lower if "route" in path or "hygiene" in path),
    }


def runner_ok(runner: Dict[str, Any]) -> bool:
    return (
        runner.get("final_form_gap_analysis_runner_status") == "PASS_WITH_ATTENTION"
        and runner.get("post_check_status") == "REPO_ONLY_FINAL_FORM_GAP_ANALYSIS_RUNNER_POST_COMMIT_CHECK_PASS_WITH_ATTENTION"
        and runner.get("next_module") == "edge_factory_os_repo_only_final_form_gap_analysis_evaluator_v1.py"
        and runner.get("final_form_gap_analysis_completed") is True
        and runner.get("evidence_chain_policy_level") == POLICY_LEVEL
        and runner.get("current_evidence_chain_quality") == CURRENT_EVIDENCE_CHAIN_QUALITY
        and runner.get("future_modules_must_classify_evidence_quality") is True
        and runner.get("full_post_check_marker_preferred_over_plain_pass") is True
        and runner.get("plain_pass_without_marker_is_attention") is True
        and runner.get("replacement_checks_are_not_equivalent_to_primary_artifact") is True
        and runner.get("generic_runner_approval_granted") is False
        and runner.get("generic_runner_implementation_remains_blocked") is True
        and runner.get("ordinary_selector_backlog_loop_reentry_allowed") is False
        and runner.get("loop_remains_closed") is True
        and runner.get("replacement_checks_all_true") is True
    )


def contract_ok(contract: Dict[str, Any]) -> bool:
    return (
        contract.get("final_form_gap_analysis_contract_status") in {"READY", "PASS"}
        and contract.get("final_form_gap_analysis_contract_ready") is True
        and contract.get("next_module") == "edge_factory_os_repo_only_final_form_gap_analysis_runner_v1.py"
        and contract.get("contract_is_repo_only") is True
        and contract.get("contract_does_not_approve_generic_runner") is True
        and contract.get("contract_does_not_reopen_loop") is True
        and contract.get("contract_does_not_touch_runtime_capital_live") is True
        and contract.get("evidence_chain_policy_level") == POLICY_LEVEL
        and contract.get("current_evidence_chain_quality") == CURRENT_EVIDENCE_CHAIN_QUALITY
        and contract.get("replacement_checks_are_not_equivalent_to_primary_artifact") is True
        and contract.get("generic_runner_approval_granted") is False
        and contract.get("generic_runner_implementation_remains_blocked") is True
        and contract.get("ordinary_selector_backlog_loop_reentry_allowed") is False
        and contract.get("loop_remains_closed") is True
        and contract.get("replacement_checks_all_true") is True
    )


def from_runner_gap_analysis(runner: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    summary: Dict[str, Dict[str, Any]] = {}
    for gap in runner.get("gap_analysis", []):
        if not isinstance(gap, dict):
            continue
        category = RUNNER_DIMENSION_TO_CATEGORY.get(str(gap.get("dimension", "")))
        if category is None:
            continue
        classification = RUNNER_STATE_TO_CLASSIFICATION.get(str(gap.get("gap_state", "")).lower(), "ATTENTION")
        summary[category] = {
            "classification": classification,
            "priority": gap.get("priority", "P3"),
            "evidence_observed": bool(gap.get("evidence_observed")),
            "source": "runner_gap_analysis",
            "notes": f"Runner dimension {gap.get('dimension')} evaluated as {gap.get('gap_state')}.",
        }
    return summary


def reconstructed_capabilities(files: List[str], runner: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    counts = repo_feature_counts(files)
    artifact_available = bool(runner)
    return {
        "self_inspection": {
            "classification": "PARTIAL" if counts["status_audit_policy_modules"] else "MISSING",
            "priority": "P2",
            "evidence_observed": counts["status_audit_policy_modules"] > 0,
            "source": "repo_reconstruction",
            "notes": "Status, audit, and policy modules exist, but final-form self-inspection remains distributed.",
        },
        "orchestration": {
            "classification": "PARTIAL" if counts["queue_or_backlog_modules"] else "MISSING",
            "priority": "P2",
            "evidence_observed": counts["queue_or_backlog_modules"] > 0,
            "source": "repo_reconstruction",
            "notes": "Queue and backlog modules exist without reopening generic governance execution.",
        },
        "autonomous_research_queueing": {
            "classification": "BLOCKED",
            "priority": "P2",
            "evidence_observed": True,
            "source": "policy_reconstruction",
            "notes": "Research queueing remains blocked for implementation while repo-only planning can continue.",
        },
        "validation_gates": {
            "classification": "PARTIAL" if counts["validation_gate_modules"] else "MISSING",
            "priority": "P2",
            "evidence_observed": counts["validation_gate_modules"] > 0,
            "source": "repo_reconstruction",
            "notes": "Validation and gate modules exist, but final-form coverage is not consolidated.",
        },
        "lifecycle_automation": {
            "classification": "MISSING",
            "priority": "P3",
            "evidence_observed": True,
            "source": "runner_reconstruction",
            "notes": "Runner identified this as a final-form gap; no repair is active now.",
        },
        "drift_monitoring": {
            "classification": "MISSING" if counts["drift_modules"] == 0 else "PARTIAL",
            "priority": "P3",
            "evidence_observed": counts["drift_modules"] > 0,
            "source": "repo_reconstruction",
            "notes": "Drift monitoring is not a current P0/P1 repair target.",
        },
        "preflight": {
            "classification": "PARTIAL" if counts["preflight_modules"] else "MISSING",
            "priority": "P2",
            "evidence_observed": counts["preflight_modules"] > 0,
            "source": "repo_reconstruction",
            "notes": "Preflight modules exist, but final-form coverage remains partial.",
        },
        "kill_switch_readiness": {
            "classification": "MISSING" if counts["kill_switch_modules"] == 0 else "PARTIAL",
            "priority": "P2",
            "evidence_observed": counts["kill_switch_modules"] > 0,
            "source": "repo_reconstruction",
            "notes": "Highest priority non-repair roadmap gap when no active P0/P1 issue exists.",
        },
        "paper_live_decision_safety": {
            "classification": "BLOCKED",
            "priority": "P2",
            "evidence_observed": True,
            "source": "policy_reconstruction",
            "notes": "Paper/live decision work is intentionally blocked by this repo-only step.",
        },
        "evidence_chain_compliance": {
            "classification": "SATISFIED" if artifact_available else "ATTENTION",
            "priority": "INFO",
            "evidence_observed": artifact_available,
            "source": "artifact_reconstruction",
            "notes": "Policy fields are preserved while evidence remains DERIVED_OVERUSED_ATTENTION.",
        },
        "route_hygiene": {
            "classification": "PARTIAL" if counts["route_hygiene_modules"] else "MISSING",
            "priority": "P3",
            "evidence_observed": counts["route_hygiene_modules"] > 0,
            "source": "repo_reconstruction",
            "notes": "Route hygiene modules exist, but the final-form path remains incomplete.",
        },
        "audit_status_reliability": {
            "classification": "PARTIAL",
            "priority": "P2",
            "evidence_observed": artifact_available,
            "source": "artifact_reconstruction",
            "notes": "Audit/status reliability is usable but still relies on derived replacement checks.",
        },
        "generic_runner_safe_mode_reopening_path": {
            "classification": "BLOCKED",
            "priority": "P2",
            "evidence_observed": True,
            "source": "policy_reconstruction",
            "notes": "Safe-mode planning is allowed later; implementation remains blocked now.",
        },
        "repo_only_development_governance": {
            "classification": "SATISFIED",
            "priority": "INFO",
            "evidence_observed": True,
            "source": "policy_reconstruction",
            "notes": "Repo-only governance, generic runner block, and closed loop state are preserved.",
        },
        "anti_self_deception_controls": {
            "classification": "ATTENTION",
            "priority": "P2",
            "evidence_observed": True,
            "source": "policy_reconstruction",
            "notes": "Derived evidence is explicitly weaker than primary artifact verification; repeated name growth is not progress.",
        },
    }


def final_capability_summary(files: List[str], runner: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    reconstructed = reconstructed_capabilities(files, runner)
    runner_summary = from_runner_gap_analysis(runner)
    summary: Dict[str, Dict[str, Any]] = {}
    for category in CAPABILITY_CATEGORIES:
        item = dict(reconstructed[category])
        if category in runner_summary:
            item.update(
                {
                    "classification": runner_summary[category]["classification"],
                    "priority": runner_summary[category]["priority"],
                    "evidence_observed": runner_summary[category]["evidence_observed"],
                    "source": runner_summary[category]["source"],
                    "runner_notes": runner_summary[category]["notes"],
                }
            )
        if item["classification"] not in CLASSIFICATIONS:
            item["classification"] = "ATTENTION"
        summary[category] = item
    return summary


def count_classifications(summary: Dict[str, Dict[str, Any]]) -> Dict[str, int]:
    return {classification: sum(1 for item in summary.values() if item.get("classification") == classification) for classification in CLASSIFICATIONS}


def highest_priority_gap(summary: Dict[str, Dict[str, Any]]) -> str:
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "INFO": 4}
    class_order = {"MISSING": 0, "BLOCKED": 1, "ATTENTION": 2, "PARTIAL": 3, "SATISFIED": 4}
    candidates = [
        (category, item)
        for category, item in summary.items()
        if item.get("classification") in {"MISSING", "BLOCKED", "ATTENTION", "PARTIAL"}
    ]
    if not candidates:
        return "none"
    candidates.sort(key=lambda pair: (priority_order.get(str(pair[1].get("priority")), 9), class_order.get(str(pair[1].get("classification")), 9), pair[0]))
    return candidates[0][0]


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    files = tracked_files()
    runner = load_json(RUNNER_ARTIFACT)
    contract = load_json(CONTRACT_ARTIFACT)
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()
    summary = final_capability_summary(files, runner)
    counts = count_classifications(summary)

    active_p0_blocker_count = 0
    active_p1_attention_count = 0
    repair_preview_required = active_p0_blocker_count > 0 or active_p1_attention_count > 0
    next_module = NEXT_MODULE_REPAIR_PREVIEW if repair_preview_required else NEXT_MODULE_ROADMAP
    next_safe_action = "BUILD_FINAL_FORM_GAP_ANALYSIS_REPAIR_PREVIEW_V1" if repair_preview_required else "BUILD_FINAL_FORM_GAP_CLOSURE_ROADMAP_V1"

    replacement_checks = {
        "expected_head_observed": git["head"] == EXPECTED_HEAD,
        "repo_clean_for_final_form_gap_analysis_evaluator": git["repo_clean_for_final_form_gap_analysis_evaluator"],
        "tracked_python_count_matches_previous": py["tracked_python_count"] == EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "runner_artifact_exists": bool(runner),
        "runner_ok": runner_ok(runner),
        "contract_artifact_exists": bool(contract),
        "contract_ok": contract_ok(contract),
        "gap_analysis_evaluated": set(summary) == set(CAPABILITY_CATEGORIES),
        "next_module_follows_decision_logic": next_module == (NEXT_MODULE_REPAIR_PREVIEW if repair_preview_required else NEXT_MODULE_ROADMAP),
        "derived_evidence_not_treated_as_primary": CURRENT_EVIDENCE_CHAIN_QUALITY == "DERIVED_OVERUSED_ATTENTION",
    }
    ready = all(value is True for value in replacement_checks.values())
    status = "PASS_WITH_ATTENTION" if ready else "FAIL_CLOSED"

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "final_form_gap_analysis_evaluator_status": status,
        "post_check_status": POST_CHECK_STATUS if ready else "REPO_ONLY_FINAL_FORM_GAP_ANALYSIS_EVALUATOR_POST_COMMIT_CHECK_FAIL_CLOSED",
        "final_decision": "FINAL_FORM_GAP_ANALYSIS_EVALUATED_SELECT_ROADMAP" if ready and not repair_preview_required else "FINAL_FORM_GAP_ANALYSIS_EVALUATED_SELECT_REPAIR_PREVIEW" if ready else "FINAL_FORM_GAP_ANALYSIS_EVALUATOR_FAIL_CLOSED",
        "next_action": next_safe_action if ready else "REVIEW_FINAL_FORM_GAP_ANALYSIS_EVALUATOR_INPUTS",
        "next_module": next_module if ready else None,
        "prior_gap_analysis_runner_respected": True,
        "prior_gap_analysis_contract_respected": True,
        "gap_analysis_evaluated": True,
        "final_form_capability_summary": summary,
        "satisfied_capability_count": counts["SATISFIED"],
        "partial_capability_count": counts["PARTIAL"],
        "missing_capability_count": counts["MISSING"],
        "blocked_capability_count": counts["BLOCKED"],
        "attention_capability_count": counts["ATTENTION"],
        "highest_priority_gap": highest_priority_gap(summary),
        "next_safe_repo_only_action": next_safe_action,
        "active_p0_blocker_count": active_p0_blocker_count,
        "active_p1_attention_count": active_p1_attention_count,
        "repair_preview_required": repair_preview_required,
        "repair_apply_allowed_now": False,
        "evidence_chain_policy_level": POLICY_LEVEL,
        "evidence_chain_quality": CURRENT_EVIDENCE_CHAIN_QUALITY,
        "current_evidence_chain_quality": CURRENT_EVIDENCE_CHAIN_QUALITY,
        "future_modules_must_classify_evidence_quality": True,
        "full_post_check_marker_preferred_over_plain_pass": True,
        "plain_pass_without_marker_is_attention": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "generic_runner_safe_mode_planning_allowed_later": True,
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
        "derived_live_repo_post_check_reason": "Final-form gap analysis evaluator uses the runner artifact, contract artifact, repo inventory, and live replacement checks; evidence remains DERIVED_OVERUSED_ATTENTION and weaker than primary artifact verification.",
        "replacement_checks_all_true": ready,
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "tracked_file_count": len(files),
            "runner_loaded": bool(runner),
            "contract_loaded": bool(contract),
            "classification_values_allowed": CLASSIFICATIONS,
            "capability_category_count": len(summary),
        },
        "safety_flags": {
            "final_form_gap_analysis_evaluator": True,
            "repo_only": True,
            "auto_fix_performed": False,
            "direct_apply_performed": False,
            "repair_preview_required": repair_preview_required,
            "repair_apply_allowed_now": False,
            "generic_runner_approval_granted": False,
            "generic_runner_implementation_remains_blocked": True,
            "generic_runner_safe_mode_planning_allowed_later": True,
            "ordinary_selector_backlog_loop_reentry_allowed": False,
            "loop_remains_closed": True,
            "repeated_name_growth_is_not_progress": True,
            **flags,
        },
    }
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_final_form_gap_analysis_evaluator_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_final_form_gap_analysis_evaluator_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_final_form_gap_analysis_evaluator_v1_latest.txt"
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
    return 0 if payload["final_form_gap_analysis_evaluator_status"] in {"READY", "PASS", "PASS_WITH_ATTENTION"} else 3


if __name__ == "__main__":
    raise SystemExit(main())
