from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_generic_framework_skeleton_audit_refresh_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_repo_only_generic_framework_skeleton_audit_refresh_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "6dc893a"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_generic_framework_skeleton_audit_refresh_v1.py"

APPLY_JSON = LAB_ROOT / "edge_factory_os_repo_only_generic_framework_skeleton_apply_v1" / "repo_only_generic_framework_skeleton_apply_v1_latest.json"
APPLY_POST_CHECK_JSON = LAB_ROOT / "edge_factory_os_repo_only_generic_framework_skeleton_apply_post_commit_check" / "repo_only_generic_framework_skeleton_apply_post_commit_check_latest.json"
APPROVAL_JSON = LAB_ROOT / "edge_factory_os_repo_only_generic_framework_skeleton_approval_v1" / "repo_only_generic_framework_skeleton_approval_v1_latest.json"
PREVIEW_JSON = LAB_ROOT / "edge_factory_os_repo_only_generic_framework_skeleton_preview_v1" / "repo_only_generic_framework_skeleton_preview_v1_latest.json"
CONTRACT_JSON = LAB_ROOT / "edge_factory_os_repo_only_generic_framework_skeleton_contract_v1" / "repo_only_generic_framework_skeleton_contract_v1_latest.json"

EXPECTED_PATHS = [
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
    "repo_only_generic_framework_skeleton_audit_refresh": True,
    "read_only_audit_refresh_only": True,
    "generic_framework_skeleton_apply_required": True,
    "generic_framework_skeleton_apply_post_check_required": True,
    "generic_framework_skeleton_approval_required": True,
    "generic_framework_skeleton_preview_required": True,
    "generic_framework_skeleton_contract_required": True,

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


def tracked_python_files() -> List[str]:
    return sorted(x.strip() for x in run_cmd(["git", "ls-files", "*.py"]).stdout.splitlines() if x.strip())


def tracked_files() -> List[str]:
    return sorted(x.strip().replace("\\", "/") for x in run_cmd(["git", "ls-files"]).stdout.splitlines() if x.strip())


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
        "framework_skeleton_apply_status",
        "audit_status",
        "framework_skeleton_approval_status",
        "framework_skeleton_preview_status",
        "framework_skeleton_contract_status",
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


def validate_status_record(errors: List[str], key: str, record: Dict[str, Any], expected_status: str, expected_next_module: Optional[str] = None) -> None:
    status = record.get("status")
    if status is None:
        errors.append(f"{key} status field missing")
    elif status != expected_status:
        errors.append(f"{key} status mismatch: expected={expected_status} actual={status}")

    validate_count_zero(errors, key, record, "critical_issue_count")
    validate_count_zero(errors, key, record, "warning_count")

    if expected_next_module is not None and record.get("next_module") != expected_next_module:
        errors.append(f"{key} next_module mismatch: expected={expected_next_module} actual={record.get('next_module')}")


def validate_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    checks: Dict[str, Any] = {}
    source_statuses: Dict[str, Dict[str, Any]] = {}
    loaded: Dict[str, Dict[str, Any]] = {}
    git_state = get_git_state()

    if not git_state["head"].startswith(EXPECTED_HEAD_PREFIX):
        errors.append(f"unexpected HEAD: {git_state['head']} expected {EXPECTED_HEAD_PREFIX}")

    expected_untracked = {CURRENT_TOOL_REL}
    actual_untracked = set(git_state["untracked_paths"])
    current_step_untracked_ok = actual_untracked == expected_untracked

    if git_state["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked paths present before audit refresh: {git_state['dirty_tracked_paths']}")

    if not current_step_untracked_ok:
        errors.append(f"unexpected untracked set before audit refresh: expected={sorted(expected_untracked)} actual={sorted(actual_untracked)}")

    head_subject = commit_subject("HEAD")
    checks["head_commit_subject"] = head_subject
    if head_subject != "Apply repo-only generic framework skeleton":
        errors.append(f"unexpected HEAD commit subject: {head_subject}")

    expected_head_paths = sorted(["tools/edge_factory_os_repo_only_generic_framework_skeleton_apply_v1.py"] + EXPECTED_PATHS)
    actual_head_paths = commit_paths("HEAD")
    checks["head_commit_paths"] = actual_head_paths
    if actual_head_paths != expected_head_paths:
        errors.append(f"unexpected HEAD commit paths: actual={actual_head_paths} expected={expected_head_paths}")

    inputs = {
        "generic_framework_skeleton_apply": (
            APPLY_JSON,
            "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_APPLY_V1_READY",
            "edge_factory_os_repo_only_generic_framework_skeleton_audit_refresh_v1.py",
        ),
        "generic_framework_skeleton_apply_post_check": (
            APPLY_POST_CHECK_JSON,
            "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_APPLY_POST_COMMIT_CHECK_PASS",
            "edge_factory_os_repo_only_generic_framework_skeleton_audit_refresh_v1.py",
        ),
        "generic_framework_skeleton_approval": (
            APPROVAL_JSON,
            "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_APPROVAL_V1_READY",
            None,
        ),
        "generic_framework_skeleton_preview": (
            PREVIEW_JSON,
            "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_PREVIEW_V1_READY",
            None,
        ),
        "generic_framework_skeleton_contract": (
            CONTRACT_JSON,
            "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_CONTRACT_V1_READY",
            None,
        ),
    }

    for key, spec in inputs.items():
        path, expected_status, expected_next_module = spec
        obj: Optional[Dict[str, Any]] = None
        record: Optional[Dict[str, Any]] = None

        try:
            obj = load_json(path)
            record = source_record(path, obj)
            loaded[key] = obj
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
        "current_step_untracked_ok": current_step_untracked_ok,
        "expected_untracked_during_run": sorted(expected_untracked),
        "actual_untracked_during_run": sorted(actual_untracked),
        "clean_baseline": not errors,
    }


def expected_hashes_from_apply(loaded: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    apply_payload = loaded.get("generic_framework_skeleton_apply", {})
    apply_body = apply_payload.get("generic_framework_skeleton_apply", {})
    result = apply_body.get("apply_result", {})
    paths = result.get("applied_paths", [])

    mapping: Dict[str, str] = {}
    if isinstance(paths, list):
        for row in paths:
            if isinstance(row, dict) and isinstance(row.get("path"), str) and isinstance(row.get("content_sha256"), str):
                mapping[row["path"]] = row["content_sha256"]
    return mapping


def build_audit_refresh(loaded: Dict[str, Dict[str, Any]], clean_baseline: bool) -> Dict[str, Any]:
    expected_hashes = expected_hashes_from_apply(loaded)
    tracked = set(tracked_files())

    records: List[Dict[str, Any]] = []
    errors: List[str] = []

    if sorted(expected_hashes.keys()) != EXPECTED_PATHS:
        errors.append(f"expected hashes keys mismatch: {sorted(expected_hashes.keys())}")

    for rel in EXPECTED_PATHS:
        path = REPO_ROOT / rel
        exists = path.exists()
        tracked_now = rel in tracked
        bom = False
        actual_hash: Optional[str] = None
        size_bytes: Optional[int] = None

        if exists:
            data = path.read_bytes()
            bom = data.startswith(b"\xef\xbb\xbf")
            actual_hash = sha256_file(path)
            size_bytes = len(data)

        expected_hash = expected_hashes.get(rel)
        hash_match = bool(actual_hash is not None and expected_hash == actual_hash)

        if not exists:
            errors.append(f"framework skeleton file missing: {rel}")
        if not tracked_now:
            errors.append(f"framework skeleton file not tracked: {rel}")
        if bom:
            errors.append(f"framework skeleton file has BOM: {rel}")
        if not hash_match:
            errors.append(f"framework skeleton hash mismatch: {rel} expected={expected_hash} actual={actual_hash}")

        records.append(
            {
                "path": rel,
                "exists": exists,
                "tracked": tracked_now,
                "bom_detected": bom,
                "content_sha256_expected": expected_hash,
                "content_sha256_actual": actual_hash,
                "hash_match": hash_match,
                "size_bytes": size_bytes,
                "audit_decision": "FRAMEWORK_SKELETON_README_OK" if exists and tracked_now and (not bom) and hash_match else "FRAMEWORK_SKELETON_README_ATTENTION",
            }
        )

    return {
        "audit_refresh_status": "GENERIC_FRAMEWORK_SKELETON_AUDIT_REFRESH_ACTIVE" if clean_baseline and not errors else "GENERIC_FRAMEWORK_SKELETON_AUDIT_REFRESH_BLOCKED",
        "audit_scope": "REPO_ONLY_FRAMEWORK_SKELETON_AUDIT_REFRESH",
        "records": records,
        "record_count": len(records),
        "expected_path_count": len(EXPECTED_PATHS),
        "errors": errors,
        "summary": {
            "framework_readme_file_count": len(records),
            "all_files_exist": all(row["exists"] is True for row in records),
            "all_files_tracked": all(row["tracked"] is True for row in records),
            "all_hashes_match": all(row["hash_match"] is True for row in records),
            "bom_detected_count": sum(1 for row in records if row["bom_detected"] is True),
        },
        "invariants": {
            "record_count_is_8": len(records) == 8,
            "all_expected_files_exist": all(row["exists"] is True for row in records),
            "all_expected_files_are_tracked": all(row["tracked"] is True for row in records),
            "all_expected_hashes_match_apply": all(row["hash_match"] is True for row in records),
            "no_bom_in_framework_readmes": all(row["bom_detected"] is False for row in records),
            "no_runtime_strategy_or_capital_authorized": True,
            "no_file_creation_or_modification_performed_by_audit": True,
        },
        "recommended_next_step": {
            "step": "BUILD_REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_FINAL_CHECK",
            "module": "edge_factory_os_repo_only_generic_framework_skeleton_final_check_v1.py",
            "scope": "REPO_ONLY_FRAMEWORK_SKELETON_FINAL_AUDIT",
            "reason": "Audit refresh confirms skeleton files are tracked and hash-matched; next safe step is a final check before resuming normal repo-only development.",
        },
    }


def main() -> int:
    safety_errors = [key for key, value in SAFETY_FLAGS.items() if not isinstance(value, bool)]

    validation = validate_inputs()
    errors = list(validation["errors"])

    if safety_errors:
        errors.append(f"safety flags are not boolean: {safety_errors}")

    audit = build_audit_refresh(validation["loaded"], bool(validation["clean_baseline"]) and not safety_errors)
    errors.extend(audit["errors"])

    if validation["pass"] and audit["audit_refresh_status"] != "GENERIC_FRAMEWORK_SKELETON_AUDIT_REFRESH_ACTIVE":
        errors.append(f"audit refresh did not become active: {audit['audit_refresh_status']}")

    invariants = audit["invariants"]
    for key in [
        "record_count_is_8",
        "all_expected_files_exist",
        "all_expected_files_are_tracked",
        "all_expected_hashes_match_apply",
        "no_bom_in_framework_readmes",
        "no_runtime_strategy_or_capital_authorized",
        "no_file_creation_or_modification_performed_by_audit",
    ]:
        if invariants.get(key) is not True:
            errors.append(f"invariant {key} not true: {invariants.get(key)}")

    passed = not errors

    payload = {
        "module": MODULE_NAME,
        "framework_skeleton_audit_refresh_status": "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_AUDIT_REFRESH_V1_READY" if passed else "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_AUDIT_REFRESH_V1_BLOCKED",
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_FRAMEWORK_SKELETON_AUDIT_REFRESH",
        "final_decision": "GENERIC_FRAMEWORK_SKELETON_AUDIT_REFRESH_READY_FOR_FINAL_CHECK" if passed else "KEEP_FREEZE_REVIEW_GENERIC_FRAMEWORK_SKELETON_AUDIT_REFRESH_ERRORS",
        "next_action": "BUILD_REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_FINAL_CHECK_V1" if passed else "REVIEW_GENERIC_FRAMEWORK_SKELETON_AUDIT_REFRESH_ERRORS",
        "next_module": "edge_factory_os_repo_only_generic_framework_skeleton_final_check_v1.py" if passed else None,
        "reason": "Verified exact framework README skeleton files are tracked, BOM-free, and hash-matched to apply output." if passed else "Generic framework skeleton audit refresh validation failed.",
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
            "current_step_untracked_ok": validation["current_step_untracked_ok"],
            "expected_untracked_during_run": validation["expected_untracked_during_run"],
            "actual_untracked_during_run": validation["actual_untracked_during_run"],
            "clean_baseline": validation["clean_baseline"],
        },
        "generic_framework_skeleton_audit_refresh": audit,
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

    latest_json = OUT_DIR / "repo_only_generic_framework_skeleton_audit_refresh_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_generic_framework_skeleton_audit_refresh_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "repo_only_generic_framework_skeleton_audit_refresh_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY GENERIC FRAMEWORK SKELETON AUDIT REFRESH v1",
        "=" * 100,
        f"framework_skeleton_audit_refresh_status: {payload['framework_skeleton_audit_refresh_status']}",
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
        "AUDIT SUMMARY",
        "-" * 100,
        json.dumps(
            {
                "summary": audit["summary"],
                "invariants": audit["invariants"],
            },
            indent=2,
            sort_keys=True,
        ),
        "",
        "SAFETY",
        "-" * 100,
        json.dumps(SAFETY_FLAGS, indent=2, sort_keys=True),
        "",
        "GIT STATE",
        "-" * 100,
        json.dumps(validation["git_state"], indent=2, sort_keys=True),
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