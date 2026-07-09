from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_status_refresh_after_framework_skeleton_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_repo_only_status_refresh_after_framework_skeleton_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "8836d7f"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_status_refresh_after_framework_skeleton_v1.py"

FINAL_JSON = LAB_ROOT / "edge_factory_os_repo_only_generic_framework_skeleton_final_check_v1" / "repo_only_generic_framework_skeleton_final_check_v1_latest.json"
FINAL_POST_CHECK_JSON = LAB_ROOT / "edge_factory_os_repo_only_generic_framework_skeleton_final_check_post_commit_check" / "repo_only_generic_framework_skeleton_final_check_post_commit_check_latest.json"
AUDIT_JSON = LAB_ROOT / "edge_factory_os_repo_only_generic_framework_skeleton_audit_refresh_v1" / "repo_only_generic_framework_skeleton_audit_refresh_v1_latest.json"
APPLY_JSON = LAB_ROOT / "edge_factory_os_repo_only_generic_framework_skeleton_apply_v1" / "repo_only_generic_framework_skeleton_apply_v1_latest.json"
ACTIVE_CORE_JSON = LAB_ROOT / "edge_factory_os_repo_only_active_core_manifest_refresh_v1" / "repo_only_active_core_manifest_refresh_v1_latest.json"
MODULE_INDEX_JSON = LAB_ROOT / "edge_factory_os_repo_only_module_index_refresh_v1" / "repo_only_module_index_refresh_v1_latest.json"

EXPECTED_FRAMEWORK_PATHS = [
    "edge_factory_os_framework/README.md",
    "edge_factory_os_framework/contracts/README.md",
    "edge_factory_os_framework/core/README.md",
    "edge_factory_os_framework/manifests/README.md",
    "edge_factory_os_framework/plugins/README.md",
    "edge_factory_os_framework/policies/README.md",
    "edge_factory_os_framework/reports/README.md",
    "edge_factory_os_framework/schemas/README.md",
]

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_status_refresh_after_framework_skeleton": True,
    "read_only_status_refresh_only": True,
    "framework_skeleton_final_check_required": True,
    "framework_skeleton_complete": True,

    "repo_only_governance_allowed": True,
    "repo_only_audit_allowed": True,
    "read_only_validation_allowed": True,

    "framework_file_creation_allowed_now": False,
    "framework_directory_creation_allowed_now": False,
    "framework_file_creation_performed_now": False,
    "framework_directory_creation_performed_now": False,

    "file_move_allowed_now": False,
    "file_delete_allowed_now": False,
    "repo_restructure_allowed_now": False,
    "overwrite_existing_files_allowed": False,
    "modify_existing_files_allowed": False,

    "manual_review_allowed_now": False,
    "risk_file_edit_allowed_now": False,
    "risk_file_execution_allowed_now": False,
    "patch_allowed_now": False,

    "apply_performed_now": False,
    "commit_performed_now": False,
    "stage_performed_now": False,
    "direct_apply_allowed": False,

    "runtime_touch_allowed": False,
    "launcher_allowed": False,
    "capital_change_allowed": False,
    "active_paper_allowed": False,
    "live_allowed": False,
    "real_orders_allowed": False,
    "candidate_generation_allowed": False,
    "candidate_release_allowed": False,
    "family_release_allowed": False,
    "strategy_research_allowed": False,
    "holdout_access_allowed": False,
    "gitignore_change_allowed": False,
    "backup_delete_allowed": False,
    "backup_move_allowed": False,
    "git_add_force_allowed": False,
    "mass_metadata_patch_allowed": False,
    "blind_fix_all_allowed": False,
}

FORBIDDEN_ACTIONS: List[str] = [
    "runtime_touch",
    "launcher_execution",
    "capital_change",
    "active_paper_change",
    "live_trading",
    "real_order_execution",
    "strategy_research",
    "candidate_generation",
    "candidate_release",
    "family_release",
    "holdout_access",
    "gitignore_change",
    "backup_delete",
    "backup_move",
    "git_add_force",
    "blind_fix_all",
    "mass_metadata_patch",
    "direct_apply",
    "manual_risk_file_review_without_valid_approval",
    "risk_file_edit_without_approval",
    "risk_file_execution_without_approval",
    "overwrite_existing_files",
    "modify_existing_files",
    "move_files",
    "delete_files",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {args} returncode={result.returncode} stderr={result.stderr}")
    return result


def get_git_state() -> Dict[str, Any]:
    status_lines = [
        x
        for x in run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"]).stdout.splitlines()
        if x.strip()
    ]
    untracked = [x[3:] for x in status_lines if x.startswith("?? ")]
    dirty_tracked = [x for x in status_lines if not x.startswith("?? ")]

    return {
        "head": run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
        "branch": run_cmd(["git", "branch", "--show-current"]).stdout.strip(),
        "status_porcelain": status_lines,
        "dirty_tracked_count": len(dirty_tracked),
        "dirty_tracked_paths": [x[3:] for x in dirty_tracked],
        "untracked_count": len(untracked),
        "untracked_paths": untracked,
        "git_dirty": bool(status_lines),
        "remote_status_short": run_cmd(["git", "status", "-sb", "--untracked-files=all"]).stdout.splitlines(),
    }


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def tracked_files() -> List[str]:
    return sorted(x.strip().replace("\\", "/") for x in run_cmd(["git", "ls-files"]).stdout.splitlines() if x.strip())


def tracked_python_files() -> List[str]:
    return sorted(x.strip() for x in run_cmd(["git", "ls-files", "*.py"]).stdout.splitlines() if x.strip())


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


def commit_subject(ref: str) -> str:
    return run_cmd(["git", "log", "-1", "--pretty=%s", ref]).stdout.strip()


def commit_paths(ref: str) -> List[str]:
    lines = run_cmd(["git", "show", "--name-only", "--format=", ref]).stdout.splitlines()
    return sorted(x.strip().replace("\\", "/") for x in lines if x.strip())


def first_status(obj: Dict[str, Any]) -> Optional[str]:
    for key in [
        "framework_skeleton_final_check_status",
        "audit_status",
        "framework_skeleton_audit_refresh_status",
        "framework_skeleton_apply_status",
        "active_core_manifest_status",
        "module_index_status",
    ]:
        value = obj.get(key)
        if value:
            return str(value)
    return None


def source_record(path: Path, obj: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "path": str(path),
        "status": first_status(obj),
        "critical_issue_count": obj.get("critical_issue_count"),
        "warning_count": obj.get("warning_count"),
        "next_module": obj.get("next_module"),
        "final_decision": obj.get("final_decision"),
    }


def validate_count_zero(errors: List[str], key: str, record: Dict[str, Any], field: str) -> None:
    value = record.get(field)
    if value is None:
        errors.append(f"{key} {field} field missing")
        return
    if value != 0:
        errors.append(f"{key} {field} not 0: {value}")


def validate_status_record(
    errors: List[str],
    key: str,
    record: Dict[str, Any],
    expected_status: str,
    expected_next_module: Optional[str] = None,
) -> None:
    status = record.get("status")
    if status is None:
        errors.append(f"{key} status field missing")
    elif status != expected_status:
        errors.append(f"{key} status mismatch: expected={expected_status} actual={status}")

    validate_count_zero(errors, key, record, "critical_issue_count")
    validate_count_zero(errors, key, record, "warning_count")

    if expected_next_module is not None and record.get("next_module") != expected_next_module:
        errors.append(f"{key} next_module mismatch: expected={expected_next_module} actual={record.get('next_module')}")


def expected_hashes_from_apply(apply_obj: Dict[str, Any]) -> Dict[str, str]:
    apply_body = apply_obj.get("generic_framework_skeleton_apply", {})
    result = apply_body.get("apply_result", {})
    rows = result.get("applied_paths", [])
    mapping: Dict[str, str] = {}

    if isinstance(rows, list):
        for row in rows:
            if isinstance(row, dict) and isinstance(row.get("path"), str) and isinstance(row.get("content_sha256"), str):
                mapping[row["path"]] = row["content_sha256"]

    return mapping


def validate_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    checks: Dict[str, Any] = {}
    loaded: Dict[str, Dict[str, Any]] = {}
    source_statuses: Dict[str, Dict[str, Any]] = {}

    git_state = get_git_state()

    if not git_state["head"].startswith(EXPECTED_HEAD_PREFIX):
        errors.append(f"unexpected HEAD: {git_state['head']} expected {EXPECTED_HEAD_PREFIX}")

    expected_untracked = {CURRENT_TOOL_REL}
    actual_untracked = set(git_state["untracked_paths"])

    if git_state["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked paths present before status refresh: {git_state['dirty_tracked_paths']}")

    if actual_untracked != expected_untracked:
        errors.append(f"unexpected untracked set before status refresh: expected={sorted(expected_untracked)} actual={sorted(actual_untracked)}")

    head_subject = commit_subject("HEAD")
    checks["head_commit_subject"] = head_subject
    if head_subject != "Add repo-only generic framework skeleton final check":
        errors.append(f"unexpected HEAD commit subject: {head_subject}")

    head_paths = commit_paths("HEAD")
    checks["head_commit_paths"] = head_paths
    if head_paths != ["tools/edge_factory_os_repo_only_generic_framework_skeleton_final_check_v1.py"]:
        errors.append(f"unexpected HEAD commit paths: {head_paths}")

    inputs = {
        "generic_framework_skeleton_final_check": (
            FINAL_JSON,
            "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_FINAL_CHECK_V1_READY",
            "edge_factory_os_repo_only_status_refresh_after_framework_skeleton_v1.py",
        ),
        "generic_framework_skeleton_final_check_post_check": (
            FINAL_POST_CHECK_JSON,
            "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_FINAL_CHECK_POST_COMMIT_CHECK_PASS",
            "edge_factory_os_repo_only_status_refresh_after_framework_skeleton_v1.py",
        ),
        "generic_framework_skeleton_audit_refresh": (
            AUDIT_JSON,
            "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_AUDIT_REFRESH_V1_READY",
            None,
        ),
        "generic_framework_skeleton_apply": (
            APPLY_JSON,
            "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_APPLY_V1_READY",
            None,
        ),
        "active_core_manifest": (
            ACTIVE_CORE_JSON,
            "REPO_ONLY_ACTIVE_CORE_MANIFEST_REFRESH_V1_READY",
            None,
        ),
        "module_index": (
            MODULE_INDEX_JSON,
            "REPO_ONLY_OS_MODULE_INDEX_REFRESH_V1_READY",
            None,
        ),
    }

    for key, spec in inputs.items():
        path, expected_status, expected_next_module = spec
        obj: Optional[Dict[str, Any]] = None
        record: Optional[Dict[str, Any]] = None

        try:
            obj = load_json(path)
            loaded[key] = obj
            record = source_record(path, obj)
        except Exception as exc:
            errors.append(f"cannot load {key}: {path} error={repr(exc)}")

        if record is not None:
            source_statuses[key] = record
            checks[key] = record
            validate_status_record(errors, key, record, expected_status, expected_next_module)

    py = validate_tracked_python()
    checks["tracked_python"] = {
        "tracked_python_file_count": py["tracked_python_file_count"],
        "syntax_error_count": py["syntax_error_count"],
        "bom_error_count": py["bom_error_count"],
    }

    if not py["pass"]:
        errors.append(f"tracked Python validation failed: syntax={py['syntax_errors'][:20]} bom={py['bom_errors']}")

    return {
        "pass": not errors,
        "errors": errors,
        "checks": checks,
        "git_state": git_state,
        "tracked_python_validation": py,
        "source_statuses": source_statuses,
        "loaded": loaded,
        "expected_untracked_during_run": sorted(expected_untracked),
        "actual_untracked_during_run": sorted(actual_untracked),
        "clean_baseline": not errors,
    }


def framework_status(apply_obj: Dict[str, Any]) -> Dict[str, Any]:
    tracked = set(tracked_files())
    expected_hashes = expected_hashes_from_apply(apply_obj)

    records: List[Dict[str, Any]] = []
    errors: List[str] = []

    for rel in EXPECTED_FRAMEWORK_PATHS:
        path = REPO_ROOT / rel
        exists = path.exists()
        tracked_now = rel in tracked
        actual_hash = sha256_file(path) if exists else None
        expected_hash = expected_hashes.get(rel)
        bom = path.read_bytes().startswith(b"\xef\xbb\xbf") if exists else False

        if not exists:
            errors.append(f"framework README missing: {rel}")
        if not tracked_now:
            errors.append(f"framework README not tracked: {rel}")
        if actual_hash != expected_hash:
            errors.append(f"framework README hash mismatch: {rel} actual={actual_hash} expected={expected_hash}")
        if bom:
            errors.append(f"framework README BOM detected: {rel}")

        records.append(
            {
                "path": rel,
                "exists": exists,
                "tracked": tracked_now,
                "hash_match": actual_hash == expected_hash,
                "bom_detected": bom,
                "content_sha256_actual": actual_hash,
                "content_sha256_expected": expected_hash,
            }
        )

    return {
        "records": records,
        "errors": errors,
        "summary": {
            "framework_readme_count": len(records),
            "all_exist": all(row["exists"] is True for row in records),
            "all_tracked": all(row["tracked"] is True for row in records),
            "all_hash_match": all(row["hash_match"] is True for row in records),
            "bom_detected_count": sum(1 for row in records if row["bom_detected"] is True),
        },
    }


def classify_tracked_paths() -> Dict[str, Any]:
    paths = tracked_files()
    categories = Counter()

    for rel in paths:
        if rel.startswith("edge_factory_os_framework/"):
            categories["framework"] += 1
        elif rel.startswith("tools/"):
            categories["tools"] += 1
        elif rel.endswith(".py"):
            categories["python_other"] += 1
        else:
            categories["other"] += 1

    return {
        "tracked_file_count": len(paths),
        "category_counts": dict(sorted(categories.items())),
        "framework_paths": [rel for rel in paths if rel.startswith("edge_factory_os_framework/")],
    }


def build_status_refresh(validation: Dict[str, Any]) -> Dict[str, Any]:
    loaded = validation["loaded"]
    framework = framework_status(loaded["generic_framework_skeleton_apply"])
    repo_map = classify_tracked_paths()

    errors: List[str] = []
    errors.extend(framework["errors"])

    git_state = validation["git_state"]
    py = validation["tracked_python_validation"]

    final_check = loaded["generic_framework_skeleton_final_check"].get("generic_framework_skeleton_final_check", {})
    final_invariants = final_check.get("invariants", {})

    status = {
        "refresh_status": "STATUS_REFRESH_AFTER_FRAMEWORK_SKELETON_ACTIVE",
        "refresh_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "framework_skeleton_state": {
            "complete": True,
            "final_check_passed": loaded["generic_framework_skeleton_final_check"].get("framework_skeleton_final_check_status") == "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_FINAL_CHECK_V1_READY",
            "final_post_check_passed": loaded["generic_framework_skeleton_final_check_post_check"].get("audit_status") == "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_FINAL_CHECK_POST_COMMIT_CHECK_PASS",
            "readme_count": framework["summary"]["framework_readme_count"],
            "all_exist": framework["summary"]["all_exist"],
            "all_tracked": framework["summary"]["all_tracked"],
            "all_hash_match": framework["summary"]["all_hash_match"],
            "bom_detected_count": framework["summary"]["bom_detected_count"],
            "records": framework["records"],
        },
        "repo_state": {
            "head": git_state["head"],
            "branch": git_state["branch"],
            "dirty_tracked_count": git_state["dirty_tracked_count"],
            "untracked_count": git_state["untracked_count"],
            "tracked_python_file_count": py["tracked_python_file_count"],
            "tracked_python_syntax_error_count": py["syntax_error_count"],
            "tracked_python_bom_error_count": py["bom_error_count"],
            "tracked_file_map": repo_map,
        },
        "development_state": {
            "normal_repo_only_development_allowed_next": True,
            "next_safe_module": "edge_factory_os_repo_only_module_index_refresh_after_framework_skeleton_v1.py",
            "runtime_block_remains": True,
            "strategy_research_block_remains": True,
            "candidate_release_block_remains": True,
            "capital_live_real_order_block_remains": True,
        },
        "source_invariants": final_invariants,
    }

    invariants = {
        "framework_skeleton_complete": status["framework_skeleton_state"]["complete"] is True,
        "framework_final_check_passed": status["framework_skeleton_state"]["final_check_passed"] is True,
        "framework_final_post_check_passed": status["framework_skeleton_state"]["final_post_check_passed"] is True,
        "framework_readme_count_is_8": status["framework_skeleton_state"]["readme_count"] == 8,
        "framework_all_exist_tracked_hash_match": (
            status["framework_skeleton_state"]["all_exist"] is True
            and status["framework_skeleton_state"]["all_tracked"] is True
            and status["framework_skeleton_state"]["all_hash_match"] is True
        ),
        "framework_bom_count_zero": status["framework_skeleton_state"]["bom_detected_count"] == 0,
        "repo_clean_except_current_tool_untracked": (
            git_state["dirty_tracked_count"] == 0
            and set(git_state["untracked_paths"]) == {CURRENT_TOOL_REL}
        ),
        "tracked_python_clean": py["pass"] is True,
        "normal_repo_only_development_allowed_next": True,
        "runtime_strategy_capital_live_blocks_remain": True,
        "no_file_creation_or_modification_performed_by_status_refresh": True,
    }

    for key, value in invariants.items():
        if value is not True:
            errors.append(f"invariant {key} not true: {value}")

    return {
        "status_refresh": status,
        "invariants": invariants,
        "errors": errors,
        "recommended_next_step": {
            "step": "BUILD_REPO_ONLY_MODULE_INDEX_REFRESH_AFTER_FRAMEWORK_SKELETON",
            "module": "edge_factory_os_repo_only_module_index_refresh_after_framework_skeleton_v1.py",
            "scope": "REPO_ONLY_OS_INTELLIGENCE",
            "reason": "Framework skeleton is complete; refresh module index so the new framework paths become visible in repo intelligence.",
        },
    }


def main() -> int:
    safety_errors = [key for key, value in SAFETY_FLAGS.items() if not isinstance(value, bool)]

    validation = validate_inputs()
    errors = list(validation["errors"])

    if safety_errors:
        errors.append(f"safety flags are not boolean: {safety_errors}")

    refresh = build_status_refresh(validation)
    errors.extend(refresh["errors"])

    passed = not errors

    payload = {
        "module": MODULE_NAME,
        "status_refresh_after_framework_skeleton_status": "REPO_ONLY_STATUS_REFRESH_AFTER_FRAMEWORK_SKELETON_V1_READY" if passed else "REPO_ONLY_STATUS_REFRESH_AFTER_FRAMEWORK_SKELETON_V1_BLOCKED",
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": "FRAMEWORK_SKELETON_COMPLETE_RESUME_REPO_ONLY_OS_INTELLIGENCE" if passed else "KEEP_FREEZE_REVIEW_STATUS_REFRESH_AFTER_FRAMEWORK_SKELETON_ERRORS",
        "next_action": "BUILD_REPO_ONLY_MODULE_INDEX_REFRESH_AFTER_FRAMEWORK_SKELETON_V1" if passed else "REVIEW_STATUS_REFRESH_AFTER_FRAMEWORK_SKELETON_ERRORS",
        "next_module": "edge_factory_os_repo_only_module_index_refresh_after_framework_skeleton_v1.py" if passed else None,
        "reason": "Framework skeleton is complete and repo-only OS intelligence can resume." if passed else "Status refresh after framework skeleton validation failed.",
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "critical_issue_count": len(errors),
        "warning_count": 0,
        "errors": errors,
        "warnings": [],
        "validation": {
            "checks": validation["checks"],
            "git_state": validation["git_state"],
            "tracked_python_validation": validation["tracked_python_validation"],
            "source_statuses": validation["source_statuses"],
            "expected_untracked_during_run": validation["expected_untracked_during_run"],
            "actual_untracked_during_run": validation["actual_untracked_during_run"],
            "clean_baseline": validation["clean_baseline"],
        },
        "status_refresh_after_framework_skeleton": refresh,
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "apply_performed_now": False,
        "stage_recommended_now": False,
        "commit_recommended_now": False,
        "runtime_action_recommended_now": False,
        "capital_action_recommended_now": False,
        "holdout_action_recommended_now": False,
        "strategy_research_recommended_now": False,
        "candidate_generation_recommended_now": False,
        "candidate_release_recommended_now": False,
        "family_release_recommended_now": False,
        "framework_file_creation_performed_now": False,
        "framework_directory_creation_performed_now": False,
        "manual_review_allowed_now": False,
        "risk_file_edit_allowed_now": False,
        "risk_file_execution_allowed_now": False,
        "runtime_touched": False,
        "launcher_executed": False,
        "capital_changed": False,
        "live_or_real_orders": False,
        "holdout_accessed": False,
        "backup_deleted": False,
        "gitignore_changed": False,
        "git_add_force_used": False,
    }

    latest_json = OUT_DIR / "repo_only_status_refresh_after_framework_skeleton_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_status_refresh_after_framework_skeleton_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "repo_only_status_refresh_after_framework_skeleton_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY STATUS REFRESH AFTER FRAMEWORK SKELETON v1",
        "=" * 100,
        f"status_refresh_after_framework_skeleton_status: {payload['status_refresh_after_framework_skeleton_status']}",
        f"severity: {payload['severity']}",
        f"final_decision: {payload['final_decision']}",
        f"next_action: {payload['next_action']}",
        f"next_module: {payload['next_module']}",
        f"reason: {payload['reason']}",
        f"critical_issue_count: {payload['critical_issue_count']}",
        f"warning_count: {payload['warning_count']}",
        "",
        "ERRORS",
        "-" * 100,
        json.dumps(errors, indent=2, sort_keys=True),
        "",
        "STATUS SUMMARY",
        "-" * 100,
        json.dumps(
            {
                "framework_skeleton_state": refresh["status_refresh"]["framework_skeleton_state"],
                "repo_state": refresh["status_refresh"]["repo_state"],
                "development_state": refresh["status_refresh"]["development_state"],
                "invariants": refresh["invariants"],
            },
            indent=2,
            sort_keys=True,
        ),
        "",
        "SAFETY",
        "-" * 100,
        json.dumps(SAFETY_FLAGS, indent=2, sort_keys=True),
        "",
        "OUTPUTS",
        "-" * 100,
        f"latest_json: {latest_json}",
        f"timestamped_json: {timestamped_json}",
        f"latest_txt: {latest_txt}",
    ]

    latest_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))

    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())