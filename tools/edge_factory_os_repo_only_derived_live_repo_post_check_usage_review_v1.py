from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_derived_live_repo_post_check_usage_review_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_derived_live_repo_post_check_usage_review_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "a232429"
EXPECTED_TRACKED_PYTHON_COUNT = 563
EXPECTED_PRIOR_POST_CHECK_MARKER = "REPO_ONLY_POST_LOOP_HEALTH_BACKLOG_ITEM_SELECTOR_POST_COMMIT_CHECK_PASS"
EXPECTED_PRIOR_COMMIT_PATH = "tools/edge_factory_os_repo_only_post_loop_health_backlog_item_selector_v1.py"
EXPECTED_PRIOR_NEXT_MODULE = "edge_factory_os_repo_only_derived_live_repo_post_check_usage_review_v1.py"
EXPECTED_SELECTED_BACKLOG_ITEM = "DERIVED_LIVE_REPO_POST_CHECK_USAGE_REVIEW"
EXPECTED_SELECTED_ITEM_REASON = "repeated_derived_live_repo_post_check_requires_evidence_chain_review"

NEXT_ACTION = "BUILD_REPO_ONLY_POST_CHECK_ARTIFACT_RELIABILITY_POLICY_V1"
NEXT_MODULE = "edge_factory_os_repo_only_post_check_artifact_reliability_policy_v1.py"
SELECTED_NEXT_POLICY_CATEGORY = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY"

ITEM_SELECTOR_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_post_loop_health_backlog_item_selector_v1"
    / "repo_only_post_loop_health_backlog_item_selector_v1_latest.json"
)
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

REVIEW_ARTIFACT_DIRS = [
    "edge_factory_os_repo_only_generic_governance_blocked_status_loop_closure_v1",
    "edge_factory_os_repo_only_generic_governance_blocked_status_human_decision_record_v1",
    "edge_factory_os_repo_only_os_intelligence_route_selector_after_generic_governance_loop_closure_v1",
    "edge_factory_os_repo_only_system_integrity_snapshot_after_generic_governance_loop_closure_v1",
    "edge_factory_os_repo_only_system_integrity_status_review_after_generic_governance_loop_closure_v1",
    "edge_factory_os_repo_only_post_loop_system_health_backlog_v1",
    "edge_factory_os_repo_only_post_loop_health_backlog_item_selector_v1",
]
REVIEW_TOOL_RELS = [
    "tools/edge_factory_os_repo_only_generic_governance_blocked_status_loop_closure_v1.py",
    "tools/edge_factory_os_repo_only_generic_governance_blocked_status_human_decision_record_v1.py",
    "tools/edge_factory_os_repo_only_os_intelligence_route_selector_after_generic_governance_loop_closure_v1.py",
    "tools/edge_factory_os_repo_only_system_integrity_snapshot_after_generic_governance_loop_closure_v1.py",
    "tools/edge_factory_os_repo_only_system_integrity_status_review_after_generic_governance_loop_closure_v1.py",
    "tools/edge_factory_os_repo_only_post_loop_system_health_backlog_v1.py",
    "tools/edge_factory_os_repo_only_post_loop_health_backlog_item_selector_v1.py",
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

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_derived_live_repo_post_check_usage_review": True,
    "prior_item_selector_respected": True,
    "prior_health_backlog_respected": True,
    "prior_loop_closure_respected": True,
    "human_decision_respected": True,
    "derived_live_repo_post_check_usage_reviewed": True,
    "primary_artifact_preferred": True,
    "missing_primary_artifact_must_not_silently_pass": True,
    "replacement_checks_must_be_explicit": True,
    "replacement_checks_are_not_equivalent_to_primary_artifact": True,
    "ordinary_selector_backlog_loop_reentry_allowed": False,
    "generic_governance_loop_reopen_allowed": False,
    "generic_runner_implementation_remains_blocked": True,
    **{flag: False for flag in DANGEROUS_FLAGS},
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
        / "edge_factory_os_repo_only_post_loop_health_backlog_item_selector_v1_post_commit_check"
        / "repo_only_post_loop_health_backlog_item_selector_post_commit_check_latest.json",
        LAB_ROOT
        / "edge_factory_os_repo_only_post_loop_health_backlog_item_selector_post_commit_check"
        / "repo_only_post_loop_health_backlog_item_selector_post_commit_check_latest.json",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def latest_json_for_dir(dirname: str) -> Optional[Path]:
    directory = LAB_ROOT / dirname
    if not directory.exists():
        return None
    latest = sorted(directory.glob("*_latest.json"))
    if latest:
        return latest[0]
    timestamped = sorted(directory.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    return timestamped[0] if timestamped else None


def review_artifact_payloads() -> List[Dict[str, Any]]:
    payloads: List[Dict[str, Any]] = []
    for dirname in REVIEW_ARTIFACT_DIRS:
        path = latest_json_for_dir(dirname)
        if path is None:
            payloads.append({"artifact_dir": dirname, "path": None, "payload": None, "error": "missing_latest_json"})
            continue
        try:
            payloads.append({"artifact_dir": dirname, "path": str(path), "payload": load_json(path), "error": None})
        except Exception as exc:
            payloads.append({"artifact_dir": dirname, "path": str(path), "payload": None, "error": repr(exc)})
    return payloads


def review_tool_samples() -> List[Dict[str, Any]]:
    samples: List[Dict[str, Any]] = []
    for rel in REVIEW_TOOL_RELS:
        path = REPO_ROOT / rel
        if not path.exists():
            samples.append({"path": rel, "exists": False, "derived_token_present": False})
            continue
        text = path.read_text(encoding="utf-8")
        samples.append(
            {
                "path": rel,
                "exists": True,
                "derived_token_present": "derived_live_repo_post_check" in text,
                "post_check_marker_token_present": "POST_COMMIT_CHECK_PASS" in text,
            }
        )
    return samples


def exact_marker_payloads_for_scope() -> List[Dict[str, Any]]:
    markers: List[Dict[str, Any]] = []
    marker_dirs = [
        directory
        for directory in LAB_ROOT.glob("*post_commit_check*")
        if any(scope.replace("_v1", "") in directory.name for scope in REVIEW_ARTIFACT_DIRS)
    ]
    for directory in sorted(marker_dirs):
        for path in sorted(directory.glob("*.json")):
            try:
                payload = load_json(path)
            except Exception as exc:
                markers.append({"path": str(path), "marker": None, "verified": False, "error": repr(exc)})
                continue
            marker = str(payload.get("post_check_status") or payload.get("audit_status") or "")
            markers.append(
                {
                    "path": str(path),
                    "marker": marker or None,
                    "verified": bool(marker.endswith("_POST_COMMIT_CHECK_PASS")),
                    "error": None,
                }
            )
    return markers


def usage_evidence() -> Dict[str, Any]:
    artifact_payloads = review_artifact_payloads()
    derived_samples: List[Dict[str, Any]] = []
    missing_artifacts: List[Dict[str, Any]] = []
    replacement_checks_explicit_count = 0
    for record in artifact_payloads:
        payload = record.get("payload")
        if not isinstance(payload, dict):
            missing_artifacts.append({"artifact_dir": record["artifact_dir"], "path": record["path"], "error": record["error"]})
            continue
        replacement_checks = payload.get("derived_live_repo_post_check_replacement_checks")
        if payload.get("derived_live_repo_post_check") is True:
            if isinstance(replacement_checks, dict) and replacement_checks and all(value is True for value in replacement_checks.values()):
                replacement_checks_explicit_count += 1
            derived_samples.append(
                {
                    "artifact_dir": record["artifact_dir"],
                    "path": record["path"],
                    "reason": payload.get("derived_live_repo_post_check_reason"),
                    "replacement_check_count": len(replacement_checks) if isinstance(replacement_checks, dict) else 0,
                    "replacement_checks_all_true": isinstance(replacement_checks, dict)
                    and bool(replacement_checks)
                    and all(value is True for value in replacement_checks.values()),
                    "previous_post_check_marker_verified": payload.get("previous_post_check_marker_verified"),
                    "previous_confirmed_post_check": payload.get("previous_confirmed_post_check"),
                }
            )
    exact_markers = exact_marker_payloads_for_scope()
    exact_verified = [marker for marker in exact_markers if marker.get("verified") is True]
    return {
        "review_artifact_dirs": REVIEW_ARTIFACT_DIRS,
        "review_artifact_count": len(artifact_payloads),
        "review_tool_samples": review_tool_samples(),
        "missing_artifacts": missing_artifacts,
        "missing_artifact_count": len(missing_artifacts),
        "derived_live_repo_post_check_recent_count": len(derived_samples),
        "derived_live_repo_post_check_samples": derived_samples,
        "replacement_checks_explicit_count": replacement_checks_explicit_count,
        "exact_post_check_marker_recent_count": len(exact_verified),
        "exact_post_check_marker_samples": exact_verified[:10],
        "all_marker_samples_seen": exact_markers[:20],
    }


def replacement_post_check(
    git: Dict[str, Any],
    py: Dict[str, Any],
    physical: Dict[str, Any],
    prior: Dict[str, Any],
    evidence: Dict[str, Any],
) -> Dict[str, bool]:
    return {
        "head_is_expected_item_selector_commit": git["head"] == EXPECTED_HEAD,
        "repo_clean_before_writing_except_current_tool": git["dirty_tracked_count"] == 0
        and sorted(git["untracked_paths"]) in ([], [CURRENT_TOOL_REL]),
        "latest_commit_touched_only_item_selector_module": latest_commit_paths() == [EXPECTED_PRIOR_COMMIT_PATH],
        "tracked_python_count_matches_previous": py["tracked_python_file_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "tracked_python_syntax_bom_clean": py["pass"] is True,
        "planned_schema_files_existing_count_zero": physical["planned_schema_files_existing_count"] == 0,
        "generic_runner_target_absent": physical["generic_runner_target_exists"] is False,
        "prior_item_selector_artifact_ready": prior.get("item_selector_status") == "READY",
        "prior_next_module_matches_current": prior.get("next_module") == EXPECTED_PRIOR_NEXT_MODULE,
        "prior_selected_backlog_item_matches": prior.get("selected_backlog_item") == EXPECTED_SELECTED_BACKLOG_ITEM,
        "prior_selected_item_reason_matches": prior.get("selected_item_reason") == EXPECTED_SELECTED_ITEM_REASON,
        "prior_health_backlog_respected": prior.get("prior_health_backlog_respected") is True,
        "prior_loop_closure_respected": prior.get("prior_loop_closure_respected") is True,
        "prior_human_decision_respected": prior.get("human_decision_respected") is True,
        "prior_generic_runner_approval_false": prior.get("generic_runner_approval_granted") is False,
        "prior_generic_runner_implementation_blocked": prior.get("generic_runner_implementation_remains_blocked") is True,
        "prior_ordinary_selector_backlog_loop_reentry_false": prior.get("ordinary_selector_backlog_loop_reentry_allowed") is False,
        "prior_loop_remains_closed": prior.get("loop_remains_closed") is True,
        "prior_derived_live_repo_post_check_present_true": prior.get("derived_live_repo_post_check") is True,
        "recent_derived_usage_seen": evidence["derived_live_repo_post_check_recent_count"] > 0,
        "replacement_checks_recorded_for_derived_samples": evidence["replacement_checks_explicit_count"] > 0,
        "prior_dangerous_flags_all_false": dangerous_flags_are_false(prior),
    }


def validate_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    git = git_state()
    py = validate_tracked_python()
    physical = physical_guard_snapshot()
    prior = load_json(ITEM_SELECTOR_JSON) if ITEM_SELECTOR_JSON.exists() else {}
    evidence = usage_evidence()
    marker_path = previous_post_check_marker_artifact()
    marker_payload: Optional[Dict[str, Any]] = load_json(marker_path) if marker_path is not None else None

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
        errors.append(f"missing prior item selector artifact: {ITEM_SELECTOR_JSON}")
    if evidence["derived_live_repo_post_check_recent_count"] <= 0:
        errors.append("no recent derived_live_repo_post_check=true usage found")

    exact_marker_verified = False
    exact_marker_value: Optional[str] = None
    if marker_payload is not None:
        exact_marker_value = str(marker_payload.get("post_check_status") or marker_payload.get("audit_status") or "")
        exact_marker_verified = exact_marker_value == EXPECTED_PRIOR_POST_CHECK_MARKER

    derived_checks = replacement_post_check(git, py, physical, prior, evidence)
    derived_live_repo_post_check = not exact_marker_verified
    derived_reason = None
    if derived_live_repo_post_check:
        derived_reason = (
            "exact persistent previous item-selector post-check marker was not found or could not be verified; "
            "using item-selector artifact plus live repo and recent usage replacement checks"
        )
        if not all(derived_checks.values()):
            errors.append(f"derived live repo replacement checks not all true: {derived_checks}")

    return {
        "errors": errors,
        "git_state": git,
        "tracked_python_validation": py,
        "physical": physical,
        "prior_item_selector": prior,
        "usage_evidence": evidence,
        "previous_post_check_marker_path": str(marker_path) if marker_path is not None else None,
        "previous_post_check_marker_value": exact_marker_value,
        "previous_post_check_marker_verified": exact_marker_verified,
        "derived_live_repo_post_check": derived_live_repo_post_check,
        "derived_live_repo_post_check_reason": derived_reason,
        "derived_live_repo_post_check_replacement_checks": derived_checks,
    }


def build_payload(validation: Dict[str, Any]) -> Dict[str, Any]:
    errors = list(validation["errors"])
    prior = validation["prior_item_selector"]
    physical = validation["physical"]
    py = validation["tracked_python_validation"]
    evidence = validation["usage_evidence"]
    dangerous_flags = {flag: False for flag in DANGEROUS_FLAGS}

    prior_item_selector_respected = (
        prior.get("item_selector_status") == "READY"
        and prior.get("selected_backlog_item") == EXPECTED_SELECTED_BACKLOG_ITEM
        and prior.get("selected_item_reason") == EXPECTED_SELECTED_ITEM_REASON
        and prior.get("next_module") == EXPECTED_PRIOR_NEXT_MODULE
    )
    prior_health_backlog_respected = prior.get("prior_health_backlog_respected") is True
    prior_loop_closure_respected = prior.get("prior_loop_closure_respected") is True
    human_decision_respected = prior.get("human_decision_respected") is True
    loop_remains_closed = (
        prior.get("loop_remains_closed") is True
        and prior.get("ordinary_selector_backlog_loop_reentry_allowed") is False
        and prior.get("generic_governance_loop_reopen_allowed") is False
    )
    derived_recent_count = int(evidence["derived_live_repo_post_check_recent_count"])
    exact_marker_recent_count = int(evidence["exact_post_check_marker_recent_count"])
    derived_seen_recently = derived_recent_count > 0
    derived_overuse_attention = derived_recent_count >= 3 and derived_recent_count > exact_marker_recent_count

    primary_artifact_preferred = True
    missing_primary_artifact_must_not_silently_pass = True
    replacement_checks_must_be_explicit = True
    replacement_checks_are_not_equivalent_to_primary_artifact = True
    next_module_safe = (
        NEXT_MODULE == "edge_factory_os_repo_only_post_check_artifact_reliability_policy_v1.py"
        and "runtime" not in NEXT_MODULE
        and "launcher" not in NEXT_MODULE
        and "capital" not in NEXT_MODULE
        and "holdout" not in NEXT_MODULE
        and "candidate" not in NEXT_MODULE
        and "family" not in NEXT_MODULE
        and "live_order" not in NEXT_MODULE
        and "real_order" not in NEXT_MODULE
        and "strategy_research" not in NEXT_MODULE
    )

    invariants = {
        "prior_item_selector_respected": prior_item_selector_respected,
        "prior_health_backlog_respected": prior_health_backlog_respected,
        "prior_loop_closure_respected": prior_loop_closure_respected,
        "human_decision_respected": human_decision_respected,
        "generic_runner_approval_granted_false": False is False,
        "generic_runner_implementation_remains_blocked": True,
        "ordinary_selector_backlog_loop_reentry_allowed_false": False is False,
        "loop_remains_closed": loop_remains_closed,
        "repeated_name_growth_is_not_progress": True,
        "derived_live_repo_post_check_usage_reviewed": True,
        "derived_live_repo_post_check_seen_recently": derived_seen_recently,
        "primary_artifact_preferred": primary_artifact_preferred,
        "missing_primary_artifact_must_not_silently_pass": missing_primary_artifact_must_not_silently_pass,
        "replacement_checks_must_be_explicit": replacement_checks_must_be_explicit,
        "replacement_checks_are_not_equivalent_to_primary_artifact": replacement_checks_are_not_equivalent_to_primary_artifact,
        "selected_next_policy_category_exact": SELECTED_NEXT_POLICY_CATEGORY == "POST_CHECK_ARTIFACT_RELIABILITY_POLICY",
        "next_module_exact_and_safe": next_module_safe,
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
        "status": "REPO_ONLY_DERIVED_LIVE_REPO_POST_CHECK_USAGE_REVIEW_V1_READY" if passed else "REPO_ONLY_DERIVED_LIVE_REPO_POST_CHECK_USAGE_REVIEW_V1_BLOCKED",
        "usage_review_status": "READY" if passed else "BLOCKED",
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_SELECTED" if passed else "REVIEW_DERIVED_LIVE_REPO_POST_CHECK_USAGE_ERRORS",
        "next_action": NEXT_ACTION if passed else "REVIEW_DERIVED_LIVE_REPO_POST_CHECK_USAGE_ERRORS",
        "next_module": NEXT_MODULE if passed else None,
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "critical_issue_count": len(errors),
        "warning_count": 0,
        "errors": errors,
        "warnings": [],
        "prior_item_selector_respected": prior_item_selector_respected,
        "prior_health_backlog_respected": prior_health_backlog_respected,
        "prior_loop_closure_respected": prior_loop_closure_respected,
        "human_decision_respected": human_decision_respected,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "generic_governance_loop_reopen_allowed": False,
        "loop_remains_closed": loop_remains_closed,
        "repeated_name_growth_is_not_progress": True,
        "derived_live_repo_post_check_usage_reviewed": True,
        "derived_live_repo_post_check_seen_recently": derived_seen_recently,
        "derived_live_repo_post_check_recent_count": derived_recent_count,
        "exact_post_check_marker_recent_count": exact_marker_recent_count,
        "derived_live_repo_post_check_overuse_attention": derived_overuse_attention,
        "primary_artifact_preferred": primary_artifact_preferred,
        "missing_primary_artifact_must_not_silently_pass": missing_primary_artifact_must_not_silently_pass,
        "replacement_checks_must_be_explicit": replacement_checks_must_be_explicit,
        "replacement_checks_are_not_equivalent_to_primary_artifact": replacement_checks_are_not_equivalent_to_primary_artifact,
        "selected_next_policy_category": SELECTED_NEXT_POLICY_CATEGORY,
        "planned_schema_files_existing_count": physical["planned_schema_files_existing_count"],
        "planned_schema_files_existing": physical["planned_schema_files_existing"],
        "generic_runner_target_exists": physical["generic_runner_target_exists"],
        "dangerous_flags": dangerous_flags,
        "derived_live_repo_post_check": validation["derived_live_repo_post_check"],
        "derived_live_repo_post_check_reason": validation["derived_live_repo_post_check_reason"],
        "derived_live_repo_post_check_replacement_checks": validation["derived_live_repo_post_check_replacement_checks"],
        "previous_expected_post_check_marker": EXPECTED_PRIOR_POST_CHECK_MARKER,
        "previous_post_check_marker_path": validation["previous_post_check_marker_path"],
        "previous_post_check_marker_value": validation["previous_post_check_marker_value"],
        "previous_post_check_marker_verified": validation["previous_post_check_marker_verified"],
        "evidence_chain_strength": {
            "primary_artifact_verification": "preferred",
            "derived_live_repo_post_check": "acceptable_with_explicit_replacement_checks_but_weaker_than_primary",
            "missing_primary_without_replacement_checks": "fail_closed",
        },
        "usage_review": evidence,
        "prior_item_selector_summary": {
            "status": prior.get("status"),
            "item_selector_status": prior.get("item_selector_status"),
            "final_decision": prior.get("final_decision"),
            "next_module": prior.get("next_module"),
            "selected_backlog_item": prior.get("selected_backlog_item"),
            "selected_item_reason": prior.get("selected_item_reason"),
            "prior_health_backlog_respected": prior.get("prior_health_backlog_respected"),
            "prior_loop_closure_respected": prior.get("prior_loop_closure_respected"),
            "human_decision_respected": prior.get("human_decision_respected"),
            "generic_runner_approval_granted": prior.get("generic_runner_approval_granted"),
            "generic_runner_implementation_remains_blocked": prior.get("generic_runner_implementation_remains_blocked"),
            "ordinary_selector_backlog_loop_reentry_allowed": prior.get("ordinary_selector_backlog_loop_reentry_allowed"),
            "loop_remains_closed": prior.get("loop_remains_closed"),
            "derived_live_repo_post_check": prior.get("derived_live_repo_post_check"),
        },
        "validation": {
            "git_state": validation["git_state"],
            "tracked_python_validation": py,
            "physical": physical,
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
    latest_json = OUT_DIR / "repo_only_derived_live_repo_post_check_usage_review_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_derived_live_repo_post_check_usage_review_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_derived_live_repo_post_check_usage_review_v1_latest.txt"
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
