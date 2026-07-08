from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_standard_os_status_review_after_evidence_chain_rollout_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_standard_os_status_review_after_evidence_chain_rollout_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "1acdfc6"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 582
NEXT_MODULE_NO_ACTIVE_P0_P1 = "edge_factory_os_repo_only_development_queue_selector_after_evidence_chain_rollout_status_review_v1.py"
NEXT_MODULE_ACTIVE_P0_P1 = "edge_factory_os_repo_only_standard_os_status_repair_preview_after_evidence_chain_rollout_v1.py"
POST_CHECK_STATUS = "REPO_ONLY_STANDARD_OS_STATUS_REVIEW_AFTER_EVIDENCE_CHAIN_ROLLOUT_POST_COMMIT_CHECK_PASS_CONTEXTUAL"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "DERIVED_OVERUSED_ATTENTION"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"
STATUS_REFRESH_ARTIFACT = LAB_ROOT / "edge_factory_os_repo_only_standard_os_status_refresh_after_evidence_chain_rollout_v1" / "repo_only_standard_os_status_refresh_after_evidence_chain_rollout_v1_latest.json"

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


def tracked_python_validation() -> Dict[str, Any]:
    files = sorted(line.strip().replace("\\", "/") for line in run_cmd(["git", "ls-files", "*.py"]).stdout.splitlines() if line.strip())
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
        "repo_clean_for_standard_os_status_review": len(dirty_tracked) == 0 and len(unexpected_untracked) == 0,
    }


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def review_checks(status_refresh: Dict[str, Any]) -> Dict[str, bool]:
    summary = status_refresh.get("standard_os_state_summary", {})
    return {
        "status_refresh_artifact_exists": bool(status_refresh),
        "status_refresh_passed": status_refresh.get("standard_os_status_refresh_status") in {"READY", "PASS"},
        "status_refresh_next_module_points_here": status_refresh.get("next_module") == "edge_factory_os_repo_only_standard_os_status_review_after_evidence_chain_rollout_v1.py",
        "os_status_internally_consistent": summary.get("generic_governance_loop_closure") == "closed"
        and summary.get("future_module_evidence_chain_contract") == "adopted"
        and summary.get("enforcement_gate") == "validated"
        and summary.get("post_adoption_audit") == "completed"
        and summary.get("rollout_status_record") == "passed",
        "evidence_chain_rollout_respected": status_refresh.get("evidence_chain_rollout_respected") is True,
        "evidence_policy_preserved": status_refresh.get("evidence_chain_policy_level") == POLICY_LEVEL
        and status_refresh.get("current_evidence_chain_quality") == CURRENT_EVIDENCE_CHAIN_QUALITY
        and status_refresh.get("future_modules_must_classify_evidence_quality") is True
        and status_refresh.get("full_post_check_marker_preferred_over_plain_pass") is True
        and status_refresh.get("plain_pass_without_marker_is_attention") is True
        and status_refresh.get("replacement_checks_are_not_equivalent_to_primary_artifact") is True,
        "generic_runner_remains_blocked": status_refresh.get("generic_runner_approval_granted") is False
        and status_refresh.get("generic_runner_implementation_remains_blocked") is True,
        "closed_loop_remains_closed": status_refresh.get("ordinary_selector_backlog_loop_reentry_allowed") is False
        and status_refresh.get("loop_remains_closed") is True,
        "no_active_p0_p1_in_refresh": status_refresh.get("active_p0_blocker_count") == 0
        and status_refresh.get("active_p1_attention_count") == 0
        and status_refresh.get("repair_preview_required") is False,
        "replacement_checks_complete": status_refresh.get("replacement_checks_all_true") is True,
    }


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    status_refresh = load_json(STATUS_REFRESH_ARTIFACT)
    checks = review_checks(status_refresh)
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    dangerous_flags = {flag: False for flag in DANGEROUS_FLAGS}

    active_p0_blocker_count = 0 if all(checks.values()) else sum(1 for key, value in checks.items() if value is False and key in {"status_refresh_artifact_exists", "evidence_chain_rollout_respected", "generic_runner_remains_blocked", "closed_loop_remains_closed"})
    active_p1_attention_count = 0 if all(checks.values()) else sum(1 for key, value in checks.items() if value is False and key not in {"status_refresh_artifact_exists", "evidence_chain_rollout_respected", "generic_runner_remains_blocked", "closed_loop_remains_closed"})
    repair_preview_required = active_p0_blocker_count + active_p1_attention_count > 0
    next_module = NEXT_MODULE_ACTIVE_P0_P1 if repair_preview_required else NEXT_MODULE_NO_ACTIVE_P0_P1

    replacement_checks = {
        "expected_head_observed": git["head"] == EXPECTED_HEAD,
        "repo_clean_for_standard_os_status_review": git["repo_clean_for_standard_os_status_review"],
        "tracked_python_count_matches_previous": py["tracked_python_count"] == EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in dangerous_flags.values()),
        "status_review_checks_complete": all(checks.values()),
        "next_module_expected": next_module in {NEXT_MODULE_NO_ACTIVE_P0_P1, NEXT_MODULE_ACTIVE_P0_P1},
        "repair_apply_disallowed": True,
    }
    ready = all(value is True for value in replacement_checks.values())

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "standard_os_status_review_status": "PASS_CONTEXTUAL" if ready else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS if ready else "REPO_ONLY_STANDARD_OS_STATUS_REVIEW_AFTER_EVIDENCE_CHAIN_ROLLOUT_POST_COMMIT_CHECK_FAIL_CLOSED",
        "final_decision": "STANDARD_OS_STATUS_REVIEW_MOVE_TO_SAFE_QUEUE_SELECTOR" if ready and not repair_preview_required else "STANDARD_OS_STATUS_REVIEW_REPAIR_PREVIEW_REQUIRED" if ready else "STANDARD_OS_STATUS_REVIEW_FAIL_CLOSED",
        "next_action": "BUILD_DEVELOPMENT_QUEUE_SELECTOR_AFTER_EVIDENCE_CHAIN_ROLLOUT_STATUS_REVIEW_V1" if ready and not repair_preview_required else "BUILD_STANDARD_OS_STATUS_REPAIR_PREVIEW_AFTER_EVIDENCE_CHAIN_ROLLOUT_V1" if ready else "REVIEW_STANDARD_OS_STATUS_REVIEW_INPUTS",
        "next_module": next_module if ready else None,
        "evidence_chain_rollout_respected": checks["evidence_chain_rollout_respected"],
        "os_status_internally_consistent": checks["os_status_internally_consistent"],
        "safe_repo_only_development_queue_selector_selected": ready and not repair_preview_required,
        "active_p0_blocker_count": active_p0_blocker_count,
        "active_p1_attention_count": active_p1_attention_count,
        "repair_preview_required": repair_preview_required,
        "repair_apply_allowed_now": False,
        "review_checks": checks,
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
        "derived_live_repo_post_check_reason": "Standard OS status review uses the status refresh artifact plus live repo replacement checks; evidence remains DERIVED_OVERUSED_ATTENTION and weaker than primary artifact verification.",
        "replacement_checks_all_true": ready,
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {"git_state": git, "tracked_python_validation": py, "status_refresh_loaded": bool(status_refresh), "status_refresh_status": status_refresh.get("standard_os_status_refresh_status")},
        "safety_flags": {
            "standard_os_status_review_after_evidence_chain_rollout": True,
            "repo_only": True,
            "auto_fix_performed": False,
            "direct_apply_performed": False,
            "repair_preview_required": repair_preview_required,
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
    latest_json = OUT_DIR / "repo_only_standard_os_status_review_after_evidence_chain_rollout_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_standard_os_status_review_after_evidence_chain_rollout_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_standard_os_status_review_after_evidence_chain_rollout_v1_latest.txt"
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
    return 0 if payload["standard_os_status_review_status"] in {"READY", "PASS", "PASS_CONTEXTUAL", "PASS_WITH_ATTENTION"} else 3


if __name__ == "__main__":
    raise SystemExit(main())
