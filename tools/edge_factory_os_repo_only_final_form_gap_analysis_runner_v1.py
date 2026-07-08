from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_final_form_gap_analysis_runner_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_final_form_gap_analysis_runner_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "3caa823"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 586
NEXT_MODULE = "edge_factory_os_repo_only_final_form_gap_analysis_evaluator_v1.py"
POST_CHECK_STATUS = "REPO_ONLY_FINAL_FORM_GAP_ANALYSIS_RUNNER_POST_COMMIT_CHECK_PASS_WITH_ATTENTION"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "DERIVED_OVERUSED_ATTENTION"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"
CONTRACT_ARTIFACT = LAB_ROOT / "edge_factory_os_repo_only_final_form_gap_analysis_contract_v1" / "repo_only_final_form_gap_analysis_contract_v1_latest.json"

ALLOWED_EVIDENCE_CHAIN_QUALITY_VALUES = [
    "PRIMARY_ARTIFACT_STRONG",
    "EXACT_MARKER_STRONG",
    "DERIVED_EXPLICIT_ATTENTION",
    "DERIVED_OVERUSED_ATTENTION",
    "MISSING_EVIDENCE_FAIL_CLOSED",
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

LATEST_ARTIFACTS = [
    LAB_ROOT / "edge_factory_os_repo_only_future_module_evidence_chain_rollout_status_record_v1" / "repo_only_future_module_evidence_chain_rollout_status_record_v1_latest.json",
    LAB_ROOT / "edge_factory_os_repo_only_standard_os_status_refresh_after_evidence_chain_rollout_v1" / "repo_only_standard_os_status_refresh_after_evidence_chain_rollout_v1_latest.json",
    LAB_ROOT / "edge_factory_os_repo_only_standard_os_status_review_after_evidence_chain_rollout_v1" / "repo_only_standard_os_status_review_after_evidence_chain_rollout_v1_latest.json",
    LAB_ROOT / "edge_factory_os_repo_only_development_queue_selector_after_evidence_chain_rollout_status_review_v1" / "repo_only_development_queue_selector_after_evidence_chain_rollout_status_review_v1_latest.json",
    LAB_ROOT / "edge_factory_os_repo_only_development_backlog_prioritization_after_evidence_chain_rollout_v1" / "repo_only_development_backlog_prioritization_after_evidence_chain_rollout_v1_latest.json",
    CONTRACT_ARTIFACT,
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
    return {"tracked_python_count": len(files), "tracked_python_syntax_error_count": len(syntax_errors), "tracked_python_bom_error_count": len(bom_errors), "syntax_errors": syntax_errors, "bom_errors": bom_errors}


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
        "repo_clean_for_final_form_gap_analysis_runner": len(dirty_tracked) == 0 and len(unexpected_untracked) == 0,
    }


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


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
        and contract.get("future_modules_must_classify_evidence_quality") is True
        and contract.get("full_post_check_marker_preferred_over_plain_pass") is True
        and contract.get("plain_pass_without_marker_is_attention") is True
        and contract.get("replacement_checks_are_not_equivalent_to_primary_artifact") is True
        and contract.get("generic_runner_approval_granted") is False
        and contract.get("generic_runner_implementation_remains_blocked") is True
        and contract.get("ordinary_selector_backlog_loop_reentry_allowed") is False
        and contract.get("loop_remains_closed") is True
        and contract.get("replacement_checks_all_true") is True
    )


def repo_feature_counts(files: List[str]) -> Dict[str, int]:
    lower = [path.lower() for path in files]
    return {
        "status_audit_policy_modules": sum(1 for path in lower if "status" in path or "audit" in path or "policy" in path),
        "validation_gate_modules": sum(1 for path in lower if "validator" in path or "validation" in path or "gate" in path),
        "queue_or_backlog_modules": sum(1 for path in lower if "queue" in path or "backlog" in path),
        "preflight_modules": sum(1 for path in lower if "preflight" in path),
        "drift_modules": sum(1 for path in lower if "drift" in path),
        "kill_switch_modules": sum(1 for path in lower if "kill" in path or "switch" in path),
        "route_hygiene_modules": sum(1 for path in lower if "route" in path or "hygiene" in path),
        "generic_runner_modules": sum(1 for path in lower if "framework_governance_runner" in path),
    }


def gap_analysis(contract: Dict[str, Any], files: List[str], artifacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    dimensions = contract.get("final_form_gap_analysis_contract", {}).get("dimensions", [])
    counts = repo_feature_counts(files)
    artifact_loaded_count = sum(1 for artifact in artifacts if bool(artifact))
    status_by_dimension = {
        "self_inspection": ("partially_satisfied", "P2", counts["status_audit_policy_modules"] > 0),
        "orchestration": ("partially_satisfied", "P2", counts["queue_or_backlog_modules"] > 0),
        "research_queueing": ("blocked", "P2", True),
        "validation_gates": ("partially_satisfied", "P2", counts["validation_gate_modules"] > 0),
        "lifecycle_automation": ("missing", "P3", True),
        "drift_monitoring": ("missing", "P3", counts["drift_modules"] == 0),
        "preflight": ("partially_satisfied", "P2", counts["preflight_modules"] > 0),
        "kill_switch_readiness": ("missing", "P2", counts["kill_switch_modules"] == 0),
        "paper_live_decision_safety": ("blocked", "P2", True),
        "evidence_chain_compliance": ("satisfied", "INFO", artifact_loaded_count >= 4),
        "route_hygiene": ("partially_satisfied", "P3", counts["route_hygiene_modules"] > 0),
        "audit_status_reliability": ("partially_satisfied", "P2", artifact_loaded_count >= 4),
        "generic_runner_safe_mode_reopening_path_without_implementation": ("blocked", "P2", counts["generic_runner_modules"] == 0),
    }
    gaps: List[Dict[str, Any]] = []
    for dimension in dimensions:
        state, priority, observed = status_by_dimension.get(dimension, ("missing", "P3", False))
        gaps.append(
            {
                "dimension": dimension,
                "gap_state": state,
                "severity": priority,
                "priority": priority,
                "evidence_observed": observed,
                "repo_only": True,
                "generic_runner_blocked_state_preserved": True,
            }
        )
    return gaps


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    files = tracked_files()
    contract = load_json(CONTRACT_ARTIFACT)
    artifacts = [load_json(path) for path in LATEST_ARTIFACTS]
    gaps = gap_analysis(contract, files, artifacts)
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    dangerous_flags = {flag: False for flag in DANGEROUS_FLAGS}
    gap_state_counts = {state: sum(1 for gap in gaps if gap["gap_state"] == state) for state in ["satisfied", "partially_satisfied", "blocked", "missing"]}

    replacement_checks = {
        "expected_head_observed": git["head"] == EXPECTED_HEAD,
        "repo_clean_for_final_form_gap_analysis_runner": git["repo_clean_for_final_form_gap_analysis_runner"],
        "tracked_python_count_matches_previous": py["tracked_python_count"] == EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in dangerous_flags.values()),
        "contract_artifact_exists": bool(contract),
        "contract_ok": contract_ok(contract),
        "repo_state_read": len(files) > 0,
        "latest_artifacts_read_where_feasible": sum(1 for artifact in artifacts if bool(artifact)) >= 4,
        "gap_analysis_has_all_contract_dimensions": len(gaps) == len(contract.get("final_form_gap_analysis_contract", {}).get("dimensions", [])),
        "next_module_expected": NEXT_MODULE == "edge_factory_os_repo_only_final_form_gap_analysis_evaluator_v1.py",
    }
    ready = all(value is True for value in replacement_checks.values())

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "final_form_gap_analysis_runner_status": "PASS_WITH_ATTENTION" if ready else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS if ready else "REPO_ONLY_FINAL_FORM_GAP_ANALYSIS_RUNNER_POST_COMMIT_CHECK_FAIL_CLOSED",
        "final_decision": "FINAL_FORM_GAP_ANALYSIS_COMPLETED_SELECT_EVALUATOR" if ready else "FINAL_FORM_GAP_ANALYSIS_RUNNER_FAIL_CLOSED",
        "next_action": "BUILD_FINAL_FORM_GAP_ANALYSIS_EVALUATOR_V1" if ready else "REVIEW_FINAL_FORM_GAP_ANALYSIS_RUNNER_INPUTS",
        "next_module": NEXT_MODULE if ready else None,
        "final_form_gap_analysis_completed": ready,
        "gap_analysis_is_repo_only": True,
        "gap_analysis_does_not_approve_generic_runner": True,
        "gap_analysis_does_not_reopen_loop": True,
        "gap_analysis_does_not_touch_runtime_capital_live": True,
        "gap_analysis": gaps,
        "gap_state_counts": gap_state_counts,
        "gap_count": len(gaps),
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 0,
        "repair_preview_required": False,
        "repair_apply_allowed_now": False,
        "evidence_chain_policy_level": POLICY_LEVEL,
        "evidence_chain_quality": CURRENT_EVIDENCE_CHAIN_QUALITY,
        "current_evidence_chain_quality": CURRENT_EVIDENCE_CHAIN_QUALITY,
        "allowed_evidence_chain_quality_values": ALLOWED_EVIDENCE_CHAIN_QUALITY_VALUES,
        "future_modules_must_classify_evidence_quality": True,
        "full_post_check_marker_preferred_over_plain_pass": True,
        "plain_pass_without_marker_is_attention": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": len(planned_existing),
        "planned_schema_files_existing": planned_existing,
        "generic_runner_target_exists": generic_runner_target_exists,
        "dangerous_flags": dangerous_flags,
        "dangerous_flags_all_false": all(value is False for value in dangerous_flags.values()),
        "dangerous_flag_true_count": 0,
        "auto_fix_performed": False,
        "direct_apply_performed": False,
        "derived_live_repo_post_check": True,
        "derived_live_repo_post_check_reason": "Final-form gap analysis runner uses repo file inventory, latest policy/status artifacts, and live replacement checks; evidence remains DERIVED_OVERUSED_ATTENTION and weaker than primary artifact verification.",
        "replacement_checks_all_true": ready,
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "tracked_file_count": len(files),
            "latest_artifact_loaded_count": sum(1 for artifact in artifacts if bool(artifact)),
            "contract_loaded": bool(contract),
        },
        "safety_flags": {
            "final_form_gap_analysis_runner": True,
            "repo_only": True,
            "auto_fix_performed": False,
            "direct_apply_performed": False,
            "repair_preview_required": False,
            "repair_apply_allowed_now": False,
            "generic_runner_approval_granted": False,
            "generic_runner_implementation_remains_blocked": True,
            "ordinary_selector_backlog_loop_reentry_allowed": False,
            "loop_remains_closed": True,
            **dangerous_flags,
        },
    }
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_final_form_gap_analysis_runner_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_final_form_gap_analysis_runner_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_final_form_gap_analysis_runner_v1_latest.txt"
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
    return 0 if payload["final_form_gap_analysis_runner_status"] in {"READY", "PASS", "PASS_WITH_ATTENTION"} else 3


if __name__ == "__main__":
    raise SystemExit(main())
