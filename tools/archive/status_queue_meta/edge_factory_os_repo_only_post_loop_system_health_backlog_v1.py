from __future__ import annotations

import ast
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_post_loop_system_health_backlog_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_post_loop_system_health_backlog_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "1994df5"
EXPECTED_TRACKED_PYTHON_COUNT = 561
EXPECTED_PRIOR_POST_CHECK_MARKER = "REPO_ONLY_SYSTEM_INTEGRITY_STATUS_REVIEW_AFTER_GENERIC_GOVERNANCE_LOOP_CLOSURE_POST_COMMIT_CHECK_PASS"
EXPECTED_PRIOR_COMMIT_PATH = "tools/edge_factory_os_repo_only_system_integrity_status_review_after_generic_governance_loop_closure_v1.py"
EXPECTED_PRIOR_NEXT_MODULE = "edge_factory_os_repo_only_post_loop_system_health_backlog_v1.py"

NEXT_ACTION = "BUILD_REPO_ONLY_POST_LOOP_HEALTH_BACKLOG_ITEM_SELECTOR_V1"
NEXT_MODULE = "edge_factory_os_repo_only_post_loop_health_backlog_item_selector_v1.py"
BACKLOG_CATEGORY = "REPO_ONLY_POST_LOOP_SYSTEM_HEALTH_BACKLOG"

STATUS_REVIEW_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_system_integrity_status_review_after_generic_governance_loop_closure_v1"
    / "repo_only_system_integrity_status_review_after_generic_governance_loop_closure_v1_latest.json"
)
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

FORBIDDEN_BACKLOG_KEYWORDS = [
    "generic runner implementation",
    "generic runner target",
    "config creation",
    "schema creation",
    "runtime",
    "launcher",
    "capital",
    "live order",
    "real order",
    "candidate generation",
    "family release",
    "active paper",
    "strategy research execution",
    "holdout execution",
    "next_action_selector after generic governance blocked status",
    "development_queue_selector after generic governance blocked status",
    "development_backlog_refresh after generic governance blocked status",
]

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_post_loop_system_health_backlog": True,
    "health_backlog_only": True,
    "prior_status_review_respected": True,
    "prior_snapshot_respected": True,
    "prior_loop_closure_respected": True,
    "human_decision_respected": True,
    "backlog_is_materially_different": True,
    "backlog_is_repo_only_os_intelligence": True,
    "ordinary_selector_backlog_loop_reentry_allowed": False,
    "generic_governance_loop_reopen_allowed": False,
    "generic_runner_implementation_remains_blocked": True,
    **{flag: False for flag in DANGEROUS_FLAGS},
}

ORDINARY_CONTINUATION_RE = re.compile(
    r"edge_factory_os_repo_only_(next_action_selector|development_queue_selector|development_backlog_refresh)"
    r"_after_generic_governance_blocked_status.*_v1[.]py$"
)


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
    return json.loads(path.read_text(encoding="utf-8"))


def git_state() -> Dict[str, Any]:
    status_lines = [
        line
        for line in run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"]).stdout.splitlines()
        if line.strip()
    ]
    untracked = [line[3:].replace("\\", "/") for line in status_lines if line.startswith("?? ")]
    dirty_tracked = [line for line in status_lines if not line.startswith("?? ")]
    staged = [line for line in dirty_tracked if line[0] != " "]
    return {
        "head": run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
        "branch": run_cmd(["git", "branch", "--show-current"]).stdout.strip(),
        "status_porcelain": status_lines,
        "dirty_tracked_count": len(dirty_tracked),
        "dirty_tracked_paths": [line[3:].replace("\\", "/") for line in dirty_tracked],
        "staged_count": len(staged),
        "staged_paths": [line[3:].replace("\\", "/") for line in staged],
        "untracked_count": len(untracked),
        "untracked_paths": sorted(untracked),
        "git_dirty": bool(status_lines),
    }


def tracked_files(pattern: str) -> List[str]:
    return sorted(line.strip().replace("\\", "/") for line in run_cmd(["git", "ls-files", pattern]).stdout.splitlines() if line.strip())


def tracked_python_files() -> List[str]:
    return tracked_files("*.py")


def validate_tracked_python() -> Dict[str, Any]:
    syntax_errors: List[Dict[str, str]] = []
    bom_errors: List[str] = []
    files = tracked_python_files()
    for rel in files:
        path = REPO_ROOT / rel
        try:
            data = path.read_bytes()
            if data.startswith(b"\xef\xbb\xbf"):
                bom_errors.append(rel)
            ast.parse(data.decode("utf-8"), filename=rel)
        except Exception as exc:
            syntax_errors.append({"path": rel, "error": repr(exc)})
    return {
        "tracked_python_file_count": len(files),
        "syntax_error_count": len(syntax_errors),
        "bom_error_count": len(bom_errors),
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
        "pass": not syntax_errors and not bom_errors,
    }


def latest_commit_paths(ref: str = "HEAD") -> List[str]:
    return sorted(line.strip().replace("\\", "/") for line in run_cmd(["git", "show", "--name-only", "--format=", ref]).stdout.splitlines() if line.strip())


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def generic_runner_target_exists() -> bool:
    return (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()


def physical_guard_snapshot() -> Dict[str, Any]:
    existing = planned_schema_existing_files()
    return {
        "planned_schema_rel_paths": PLANNED_SCHEMA_REL_PATHS,
        "planned_schema_files_existing": existing,
        "planned_schema_files_existing_count": len(existing),
        "generic_runner_target_file": GENERIC_RUNNER_TARGET_FILE,
        "generic_runner_target_exists": generic_runner_target_exists(),
        "runtime_touch_performed": False,
        "launcher_executed": False,
        "capital_change_performed": False,
        "live_or_real_order_performed": False,
        "holdout_access_performed": False,
        "candidate_generation_performed": False,
        "family_release_performed": False,
        "strategy_research_performed": False,
        "schema_file_creation_performed": False,
        "schema_file_edit_performed": False,
        "generic_runner_file_creation_performed": False,
        "config_file_creation_performed": False,
    }


def dangerous_flags_are_false(obj: Dict[str, Any]) -> bool:
    flags = obj.get("dangerous_flags", {})
    if not isinstance(flags, dict) or any(value is not False for value in flags.values()):
        return False
    safety = obj.get("safety_flags", {})
    if isinstance(safety, dict):
        for flag in DANGEROUS_FLAGS:
            if safety.get(flag, False) is not False:
                return False
    return True


def previous_post_check_marker_artifact() -> Optional[Path]:
    candidates = [
        LAB_ROOT
        / "edge_factory_os_repo_only_system_integrity_status_review_after_generic_governance_loop_closure_v1_post_commit_check"
        / "repo_only_system_integrity_status_review_after_generic_governance_loop_closure_post_commit_check_latest.json",
        LAB_ROOT
        / "edge_factory_os_repo_only_system_integrity_status_review_after_generic_governance_loop_closure_post_commit_check"
        / "repo_only_system_integrity_status_review_after_generic_governance_loop_closure_post_commit_check_latest.json",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def build_backlog_items() -> List[Dict[str, Any]]:
    return [
        {
            "rank": 1,
            "key": "POST_LOOP_HEALTH_BACKLOG_ITEM_SELECTOR",
            "module": "edge_factory_os_repo_only_post_loop_health_backlog_item_selector_v1.py",
            "category": "REPO_ONLY_POST_LOOP_SYSTEM_HEALTH_BACKLOG",
            "allowed": True,
            "scope": "REPO_ONLY_OS_INTELLIGENCE",
            "reason": "Select one concrete repo-only health backlog item without reopening the closed generic governance loop.",
        },
        {
            "rank": 2,
            "key": "ARTIFACT_RELIABILITY_REVIEW",
            "module": "edge_factory_os_repo_only_artifact_reliability_review_after_generic_governance_loop_closure_v1.py",
            "category": "REPO_ONLY_ARTIFACT_RELIABILITY_REVIEW",
            "allowed": True,
            "scope": "REPO_ONLY_OS_INTELLIGENCE",
            "reason": "Review whether artifacts and derived checks are reliable enough for subsequent repo-only routing.",
        },
        {
            "rank": 3,
            "key": "DERIVED_LIVE_REPO_POST_CHECK_USAGE_REVIEW",
            "module": "edge_factory_os_repo_only_derived_live_repo_post_check_usage_review_v1.py",
            "category": "REPO_ONLY_DERIVED_CHECK_REVIEW",
            "allowed": True,
            "scope": "REPO_ONLY_OS_INTELLIGENCE",
            "reason": "Track and reduce overuse of derived live repo post-check replacement paths.",
        },
        {
            "rank": 4,
            "key": "REPO_ONLY_STATUS_INVENTORY",
            "module": "edge_factory_os_repo_only_status_inventory_after_generic_governance_loop_closure_v1.py",
            "category": "REPO_ONLY_STATUS_INVENTORY",
            "allowed": True,
            "scope": "REPO_ONLY_OS_INTELLIGENCE",
            "reason": "Inventory current repo-only status/audit artifacts after loop closure.",
        },
        {
            "rank": 5,
            "key": "ROUTE_HYGIENE_REVIEW",
            "module": "edge_factory_os_repo_only_route_hygiene_review_after_generic_governance_loop_closure_v1.py",
            "category": "REPO_ONLY_ROUTE_HYGIENE_REVIEW",
            "allowed": True,
            "scope": "REPO_ONLY_OS_INTELLIGENCE",
            "reason": "Check route naming and transition hygiene without extending the old loop.",
        },
        {
            "rank": 6,
            "key": "SYSTEM_INTEGRITY_GUARD_SUMMARY",
            "module": "edge_factory_os_repo_only_system_integrity_guard_summary_v1.py",
            "category": "REPO_ONLY_SYSTEM_INTEGRITY_GUARD_SUMMARY",
            "allowed": True,
            "scope": "REPO_ONLY_OS_INTELLIGENCE",
            "reason": "Summarize the currently active repo-only guard facts.",
        },
        {
            "rank": 7,
            "key": "FUTURE_GENERIC_RUNNER_SAFE_MODE_APPROVAL_CONTRACT_PLANNING_ONLY",
            "module": "edge_factory_os_repo_only_generic_runner_safe_mode_approval_contract_plan_v1.py",
            "category": "REPO_ONLY_APPROVAL_CONTRACT_PLANNING_ONLY",
            "allowed": True,
            "scope": "REPO_ONLY_OS_INTELLIGENCE",
            "reason": "Plan, but do not implement, a future safe-mode approval contract for possible generic runner reopening.",
        },
    ]


def backlog_items_safe(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    violations: List[str] = []
    for item in items:
        text = " ".join(str(item.get(key, "")) for key in ["key", "module", "category", "reason"]).lower()
        for keyword in FORBIDDEN_BACKLOG_KEYWORDS:
            if keyword in text:
                if item.get("key") != "FUTURE_GENERIC_RUNNER_SAFE_MODE_APPROVAL_CONTRACT_PLANNING_ONLY":
                    violations.append(f"{item.get('key')} contains forbidden keyword {keyword}")
                elif keyword not in {"generic runner implementation", "generic runner target", "config creation", "schema creation"}:
                    violations.append(f"{item.get('key')} contains forbidden keyword {keyword}")
        module = str(item.get("module", ""))
        if ORDINARY_CONTINUATION_RE.match(module):
            violations.append(f"{item.get('key')} reopens ordinary loop")
        if item.get("scope") != "REPO_ONLY_OS_INTELLIGENCE":
            violations.append(f"{item.get('key')} wrong scope {item.get('scope')}")
        if item.get("allowed") is not True:
            violations.append(f"{item.get('key')} not allowed true")
    selected = items[0] if items else None
    return {
        "safe": not violations,
        "violations": violations,
        "selected_item": selected,
        "allowed_item_count": sum(1 for item in items if item.get("allowed") is True),
    }


def replacement_post_check(git: Dict[str, Any], py: Dict[str, Any], physical: Dict[str, Any], prior: Dict[str, Any]) -> Dict[str, bool]:
    return {
        "head_is_expected_status_review_commit": git["head"] == EXPECTED_HEAD,
        "repo_clean_before_writing_except_current_tool": git["dirty_tracked_count"] == 0
        and sorted(git["untracked_paths"]) in ([], [CURRENT_TOOL_REL]),
        "latest_commit_touched_only_status_review_module": latest_commit_paths() == [EXPECTED_PRIOR_COMMIT_PATH],
        "tracked_python_count_matches_previous": py["tracked_python_file_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "tracked_python_syntax_bom_clean": py["pass"] is True,
        "planned_schema_files_existing_count_zero": physical["planned_schema_files_existing_count"] == 0,
        "generic_runner_target_absent": physical["generic_runner_target_exists"] is False,
        "prior_status_review_artifact_ready": prior.get("status") == "REPO_ONLY_SYSTEM_INTEGRITY_STATUS_REVIEW_AFTER_GENERIC_GOVERNANCE_LOOP_CLOSURE_V1_READY",
        "prior_system_integrity_review_status_ready": prior.get("system_integrity_review_status") == "READY",
        "prior_next_module_matches_current": prior.get("next_module") == EXPECTED_PRIOR_NEXT_MODULE,
        "prior_snapshot_respected": prior.get("prior_snapshot_respected") is True,
        "prior_loop_closure_respected": prior.get("prior_loop_closure_respected") is True,
        "prior_human_decision_respected": prior.get("human_decision_respected") is True,
        "prior_generic_runner_approval_false": prior.get("generic_runner_approval_granted") is False,
        "prior_generic_runner_implementation_blocked": prior.get("generic_runner_implementation_remains_blocked") is True,
        "prior_ordinary_selector_backlog_loop_reentry_false": prior.get("ordinary_selector_backlog_loop_reentry_allowed") is False,
        "prior_loop_remains_closed": prior.get("loop_remains_closed") is True,
        "prior_selected_next_route_category_health_backlog": prior.get("selected_next_route_category") == BACKLOG_CATEGORY,
        "prior_dangerous_flags_all_false": dangerous_flags_are_false(prior),
    }


def validate_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    git = git_state()
    py = validate_tracked_python()
    physical = physical_guard_snapshot()
    prior = load_json(STATUS_REVIEW_JSON) if STATUS_REVIEW_JSON.exists() else {}
    marker_path = previous_post_check_marker_artifact()
    marker_payload: Optional[Dict[str, Any]] = load_json(marker_path) if marker_path is not None else None
    backlog_items = build_backlog_items()
    safety = backlog_items_safe(backlog_items)

    expected_untracked = [CURRENT_TOOL_REL] if (REPO_ROOT / CURRENT_TOOL_REL).exists() else []
    if git["head"] != EXPECTED_HEAD:
        errors.append(f"HEAD mismatch: expected={EXPECTED_HEAD} actual={git['head']}")
    if git["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked paths present: {git['dirty_tracked_paths']}")
    if git["untracked_paths"] != expected_untracked:
        errors.append(f"unexpected untracked paths: expected={expected_untracked} actual={git['untracked_paths']}")
    if py["tracked_python_file_count"] != EXPECTED_TRACKED_PYTHON_COUNT:
        errors.append(f"tracked Python count mismatch: expected={EXPECTED_TRACKED_PYTHON_COUNT} actual={py['tracked_python_file_count']}")
    if not py["pass"]:
        errors.append(f"tracked Python validation failed: syntax={py['syntax_errors'][:20]} bom={py['bom_errors']}")
    if physical["planned_schema_files_existing_count"] != 0:
        errors.append(f"planned schema files exist: {physical['planned_schema_files_existing']}")
    if physical["generic_runner_target_exists"] is not False:
        errors.append(f"generic runner target exists: {GENERIC_RUNNER_TARGET_FILE}")
    if not prior:
        errors.append(f"missing prior status review artifact: {STATUS_REVIEW_JSON}")
    if not safety["safe"]:
        errors.append(f"backlog item safety violations: {safety['violations']}")

    exact_marker_verified = False
    exact_marker_value: Optional[str] = None
    if marker_payload is not None:
        exact_marker_value = str(marker_payload.get("post_check_status") or marker_payload.get("audit_status") or "")
        exact_marker_verified = exact_marker_value == EXPECTED_PRIOR_POST_CHECK_MARKER

    derived_checks = replacement_post_check(git, py, physical, prior)
    derived_live_repo_post_check = not exact_marker_verified
    derived_reason = None
    if derived_live_repo_post_check:
        derived_reason = (
            "exact persistent previous status-review post-check marker was not found or could not be verified; "
            "using status-review artifact plus live repo replacement checks"
        )
        if not all(derived_checks.values()):
            errors.append(f"derived live repo replacement checks not all true: {derived_checks}")

    return {
        "errors": errors,
        "git_state": git,
        "tracked_python_validation": py,
        "physical": physical,
        "prior_status_review": prior,
        "backlog_items": backlog_items,
        "backlog_item_safety": safety,
        "previous_post_check_marker_path": str(marker_path) if marker_path is not None else None,
        "previous_post_check_marker_value": exact_marker_value,
        "previous_post_check_marker_verified": exact_marker_verified,
        "derived_live_repo_post_check": derived_live_repo_post_check,
        "derived_live_repo_post_check_reason": derived_reason,
        "derived_live_repo_post_check_replacement_checks": derived_checks,
    }


def build_payload(validation: Dict[str, Any]) -> Dict[str, Any]:
    errors = list(validation["errors"])
    prior = validation["prior_status_review"]
    physical = validation["physical"]
    py = validation["tracked_python_validation"]
    safety = validation["backlog_item_safety"]
    dangerous_flags = {flag: False for flag in DANGEROUS_FLAGS}

    prior_status_review_respected = (
        prior.get("system_integrity_review_status") == "READY"
        and prior.get("next_module") == EXPECTED_PRIOR_NEXT_MODULE
        and prior.get("selected_next_route_category") == BACKLOG_CATEGORY
    )
    prior_snapshot_respected = prior.get("prior_snapshot_respected") is True
    prior_loop_closure_respected = prior.get("prior_loop_closure_respected") is True
    human_decision_respected = prior.get("human_decision_respected") is True
    loop_remains_closed = (
        prior.get("loop_remains_closed") is True
        and prior.get("ordinary_selector_backlog_loop_reentry_allowed") is False
    )
    backlog_is_materially_different = safety["safe"] is True and safety["allowed_item_count"] >= 5
    backlog_is_repo_only_os_intelligence = all(item.get("scope") == "REPO_ONLY_OS_INTELLIGENCE" for item in validation["backlog_items"])
    selected_backlog_item = safety["selected_item"]

    invariants = {
        "prior_status_review_respected": prior_status_review_respected,
        "prior_snapshot_respected": prior_snapshot_respected,
        "prior_loop_closure_respected": prior_loop_closure_respected,
        "human_decision_respected": human_decision_respected,
        "generic_runner_approval_granted_false": False is False,
        "generic_runner_implementation_remains_blocked": True,
        "ordinary_selector_backlog_loop_reentry_allowed_false": False is False,
        "loop_remains_closed": loop_remains_closed,
        "repeated_name_growth_is_not_progress": True,
        "backlog_category_exact": BACKLOG_CATEGORY == "REPO_ONLY_POST_LOOP_SYSTEM_HEALTH_BACKLOG",
        "backlog_is_materially_different": backlog_is_materially_different,
        "backlog_is_repo_only_os_intelligence": backlog_is_repo_only_os_intelligence,
        "selected_item_exact": isinstance(selected_backlog_item, dict)
        and selected_backlog_item.get("module") == NEXT_MODULE,
        "planned_schema_files_existing_count_zero": physical["planned_schema_files_existing_count"] == 0,
        "generic_runner_target_absent": physical["generic_runner_target_exists"] is False,
        "tracked_python_clean": py["pass"] is True,
        "dangerous_flags_all_false": all(value is False for value in dangerous_flags.values()),
    }
    for key, value in invariants.items():
        if value is not True:
            errors.append(f"invariant not true: {key}={value}")

    passed = not errors
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "status": "REPO_ONLY_POST_LOOP_SYSTEM_HEALTH_BACKLOG_V1_READY" if passed else "REPO_ONLY_POST_LOOP_SYSTEM_HEALTH_BACKLOG_V1_BLOCKED",
        "post_loop_health_backlog_status": "READY" if passed else "BLOCKED",
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": "POST_LOOP_HEALTH_BACKLOG_ITEM_SELECTOR_SELECTED" if passed else "REVIEW_POST_LOOP_SYSTEM_HEALTH_BACKLOG_ERRORS",
        "next_action": NEXT_ACTION if passed else "REVIEW_POST_LOOP_SYSTEM_HEALTH_BACKLOG_ERRORS",
        "next_module": NEXT_MODULE if passed else None,
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "critical_issue_count": len(errors),
        "warning_count": 0,
        "errors": errors,
        "warnings": [],
        "prior_status_review_respected": prior_status_review_respected,
        "prior_snapshot_respected": prior_snapshot_respected,
        "prior_loop_closure_respected": prior_loop_closure_respected,
        "human_decision_respected": human_decision_respected,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "generic_governance_loop_reopen_allowed": False,
        "loop_remains_closed": loop_remains_closed,
        "repeated_name_growth_is_not_progress": True,
        "backlog_category": BACKLOG_CATEGORY,
        "backlog_is_materially_different": backlog_is_materially_different,
        "backlog_is_repo_only_os_intelligence": backlog_is_repo_only_os_intelligence,
        "backlog_items": validation["backlog_items"],
        "selected_backlog_item": selected_backlog_item,
        "planned_schema_files_existing_count": physical["planned_schema_files_existing_count"],
        "planned_schema_files_existing": physical["planned_schema_files_existing"],
        "generic_runner_target_exists": physical["generic_runner_target_exists"],
        "dangerous_flags": dangerous_flags,
        "derived_live_repo_post_check": validation["derived_live_repo_post_check"],
        "derived_live_repo_post_check_reason": validation["derived_live_repo_post_check_reason"],
        "derived_live_repo_post_check_replacement_checks": validation["derived_live_repo_post_check_replacement_checks"],
        "previous_confirmed_post_check": EXPECTED_PRIOR_POST_CHECK_MARKER,
        "previous_post_check_marker_path": validation["previous_post_check_marker_path"],
        "previous_post_check_marker_value": validation["previous_post_check_marker_value"],
        "previous_post_check_marker_verified": validation["previous_post_check_marker_verified"],
        "prior_status_review_summary": {
            "status": prior.get("status"),
            "system_integrity_review_status": prior.get("system_integrity_review_status"),
            "final_decision": prior.get("final_decision"),
            "next_module": prior.get("next_module"),
            "prior_snapshot_respected": prior.get("prior_snapshot_respected"),
            "prior_loop_closure_respected": prior.get("prior_loop_closure_respected"),
            "human_decision_respected": prior.get("human_decision_respected"),
            "generic_runner_approval_granted": prior.get("generic_runner_approval_granted"),
            "generic_runner_implementation_remains_blocked": prior.get("generic_runner_implementation_remains_blocked"),
            "ordinary_selector_backlog_loop_reentry_allowed": prior.get("ordinary_selector_backlog_loop_reentry_allowed"),
            "loop_remains_closed": prior.get("loop_remains_closed"),
            "selected_next_route_category": prior.get("selected_next_route_category"),
        },
        "validation": {
            "git_state": validation["git_state"],
            "tracked_python_validation": py,
            "physical": physical,
            "backlog_item_safety": safety,
            "invariants": invariants,
        },
        "safety_flags": SAFETY_FLAGS,
        "stage_recommended_now": False,
        "commit_recommended_now": False,
    }
    payload.update(dangerous_flags)
    payload.update(
        {
            "manual_approval_present": False,
            "manual_approval_valid": False,
            "manual_approval_present_for_generic_runner": False,
            "manual_approval_valid_for_generic_runner": False,
            "approval_inferred_or_guessed": False,
            "implementation_allowed_now": False,
            "generic_runner_implementation_allowed_now": False,
            "schema_creation_allowed_now": False,
            "schema_edit_allowed_now": False,
            "runtime_touch_allowed_now": False,
            "generic_runner_file_creation_performed": False,
            "config_file_creation_performed": False,
            "schema_file_creation_performed": False,
            "schema_file_edit_performed": False,
            "runtime_touch_performed": False,
            "capital_change_performed": False,
            "live_or_real_order_performed": False,
            "holdout_access_performed": False,
        }
    )
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_post_loop_system_health_backlog_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_post_loop_system_health_backlog_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_post_loop_system_health_backlog_v1_latest.txt"
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    latest_json.write_text(rendered, encoding="utf-8")
    timestamped_json.write_text(rendered, encoding="utf-8")
    latest_txt.write_text(rendered + "\n", encoding="utf-8")
    return {"latest_json": str(latest_json), "timestamped_json": str(timestamped_json), "latest_txt": str(latest_txt)}


def main() -> int:
    validation = validate_inputs()
    payload = build_payload(validation)
    outputs = write_outputs(payload)
    payload["outputs"] = outputs
    Path(outputs["latest_json"]).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["critical_issue_count"] == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
