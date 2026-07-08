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

MODULE_NAME = "edge_factory_os_repo_only_generic_framework_skeleton_apply_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_repo_only_generic_framework_skeleton_apply_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "3fe80e8"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_generic_framework_skeleton_apply_v1.py"

APPROVAL_JSON = LAB_ROOT / "edge_factory_os_repo_only_generic_framework_skeleton_approval_v1" / "repo_only_generic_framework_skeleton_approval_v1_latest.json"
APPROVAL_POST_CHECK_JSON = LAB_ROOT / "edge_factory_os_repo_only_generic_framework_skeleton_approval_post_commit_check" / "repo_only_generic_framework_skeleton_approval_post_commit_check_latest.json"
PREVIEW_JSON = LAB_ROOT / "edge_factory_os_repo_only_generic_framework_skeleton_preview_v1" / "repo_only_generic_framework_skeleton_preview_v1_latest.json"
CONTRACT_JSON = LAB_ROOT / "edge_factory_os_repo_only_generic_framework_skeleton_contract_v1" / "repo_only_generic_framework_skeleton_contract_v1_latest.json"

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_generic_framework_skeleton_apply": True,
    "exact_apply_only": True,
    "generic_framework_skeleton_approval_required": True,
    "generic_framework_skeleton_preview_required": True,
    "generic_framework_skeleton_contract_required": True,

    "repo_only_governance_allowed": True,
    "repo_only_audit_allowed": True,
    "read_only_validation_allowed": True,

    "framework_skeleton_approval_present": True,
    "framework_skeleton_approval_valid": True,
    "exact_framework_readme_creation_allowed_by_approval": True,

    "framework_file_creation_allowed_now": True,
    "framework_directory_creation_allowed_now": True,
    "framework_file_creation_performed_now": True,
    "framework_directory_creation_performed_now": True,

    "file_move_allowed_now": False,
    "file_delete_allowed_now": False,
    "repo_restructure_allowed_now": False,
    "overwrite_existing_files_allowed": False,
    "modify_existing_files_allowed": False,

    "manual_review_allowed_now": False,
    "risk_file_edit_allowed_now": False,
    "risk_file_execution_allowed_now": False,
    "patch_allowed_now": False,

    "apply_performed_now": True,
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


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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


def first_status(obj: Dict[str, Any]) -> Optional[str]:
    for key in [
        "framework_skeleton_approval_status",
        "audit_status",
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
        errors.append(f"dirty tracked paths present before apply: {git_state['dirty_tracked_paths']}")

    if not current_step_untracked_ok:
        errors.append(f"unexpected untracked set before apply: expected={sorted(expected_untracked)} actual={sorted(actual_untracked)}")

    head_subject = commit_subject("HEAD")
    checks["head_commit_subject"] = head_subject
    if head_subject != "Add repo-only generic framework skeleton approval":
        errors.append(f"unexpected HEAD commit subject: {head_subject}")

    inputs = {
        "generic_framework_skeleton_approval": (
            APPROVAL_JSON,
            "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_APPROVAL_V1_READY",
            "edge_factory_os_repo_only_generic_framework_skeleton_apply_v1.py",
        ),
        "generic_framework_skeleton_approval_post_check": (
            APPROVAL_POST_CHECK_JSON,
            "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_APPROVAL_POST_COMMIT_CHECK_PASS",
            "edge_factory_os_repo_only_generic_framework_skeleton_apply_v1.py",
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


def approval_paths(loaded: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    approval_payload = loaded["generic_framework_skeleton_approval"]
    approval = approval_payload.get("generic_framework_skeleton_approval", {})
    paths = approval.get("approved_paths", [])
    if not isinstance(paths, list):
        return []
    return [item for item in paths if isinstance(item, dict)]


def contract_content_map(loaded: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    contract_payload = loaded["generic_framework_skeleton_contract"]
    contract = contract_payload.get("generic_framework_skeleton_contract", {})
    path_contracts = contract.get("path_contracts", [])
    mapping: Dict[str, str] = {}
    if isinstance(path_contracts, list):
        for item in path_contracts:
            if isinstance(item, dict) and isinstance(item.get("path"), str) and isinstance(item.get("content_utf8_no_bom"), str):
                mapping[item["path"]] = item["content_utf8_no_bom"]
    return mapping


def build_apply_plan(loaded: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    approved = approval_paths(loaded)
    content_by_path = contract_content_map(loaded)

    planned: List[Dict[str, Any]] = []
    errors: List[str] = []

    approved_names = sorted([str(item.get("path")) for item in approved])
    contract_names = sorted(content_by_path.keys())

    if approved_names != EXPECTED_PATHS:
        errors.append(f"approved paths mismatch expected: approved={approved_names} expected={EXPECTED_PATHS}")

    if contract_names != EXPECTED_PATHS:
        errors.append(f"contract paths mismatch expected: contract={contract_names} expected={EXPECTED_PATHS}")

    for item in approved:
        rel = item.get("path")
        approved_hash = item.get("content_sha256")

        if not isinstance(rel, str):
            errors.append(f"invalid approved path item: {item}")
            continue

        content = content_by_path.get(rel)
        if not isinstance(content, str):
            errors.append(f"missing contract content for approved path: {rel}")
            continue

        content_hash = sha256_text(content)
        if content_hash != approved_hash:
            errors.append(f"approved hash mismatch for {rel}: approval={approved_hash} contract={content_hash}")

        target = REPO_ROOT / rel
        planned.append(
            {
                "path": rel,
                "target": str(target),
                "parent_directory": str(target.parent),
                "target_exists_before_apply": target.exists(),
                "parent_exists_before_apply": target.parent.exists(),
                "content_sha256": content_hash,
                "content_bytes_utf8": len(content.encode("utf-8")),
                "approved_action": item.get("approved_action"),
            }
        )

    return {
        "errors": errors,
        "planned": sorted(planned, key=lambda row: row["path"]),
    }


def apply_exact_files(planned: List[Dict[str, Any]], content_by_path: Dict[str, str]) -> Dict[str, Any]:
    errors: List[str] = []
    applied: List[Dict[str, Any]] = []
    created_parent_dirs: List[str] = []

    for row in planned:
        rel = row["path"]
        target = REPO_ROOT / rel

        if target.exists():
            errors.append(f"target already exists before write: {rel}")
            continue

        parent = target.parent
        if not parent.exists():
            parent.mkdir(parents=True, exist_ok=True)
            created_parent_dirs.append(str(parent.relative_to(REPO_ROOT)).replace("\\", "/"))

        content = content_by_path[rel]
        target.write_bytes(content.encode("utf-8"))

        if target.read_bytes().startswith(b"\xef\xbb\xbf"):
            errors.append(f"BOM detected after write: {rel}")

        actual_hash = sha256_file(target)
        expected_hash = row["content_sha256"]
        if actual_hash != expected_hash:
            errors.append(f"hash mismatch after write for {rel}: actual={actual_hash} expected={expected_hash}")

        applied.append(
            {
                "path": rel,
                "content_sha256": actual_hash,
                "content_bytes_utf8": target.stat().st_size,
                "created_parent_directory": not row["parent_exists_before_apply"],
                "applied_action": "CREATE_EXACT_README_ONLY",
            }
        )

    return {
        "errors": errors,
        "applied_paths": sorted(applied, key=lambda row: row["path"]),
        "applied_path_count": len(applied),
        "created_parent_directories": sorted(set(created_parent_dirs)),
        "created_parent_directory_count": len(set(created_parent_dirs)),
    }


def main() -> int:
    safety_errors = [key for key, value in SAFETY_FLAGS.items() if not isinstance(value, bool)]

    validation = validate_inputs()
    errors = list(validation["errors"])

    if safety_errors:
        errors.append(f"safety flags are not boolean: {safety_errors}")

    content_by_path = {}
    apply_plan = {"errors": ["apply plan not built"], "planned": []}
    apply_result = {"errors": ["apply not executed"], "applied_paths": [], "applied_path_count": 0, "created_parent_directories": [], "created_parent_directory_count": 0}

    if not errors:
        content_by_path = contract_content_map(validation["loaded"])
        apply_plan = build_apply_plan(validation["loaded"])
        errors.extend(apply_plan["errors"])

    if not errors:
        if len(apply_plan["planned"]) != 8:
            errors.append(f"planned apply count not 8: {len(apply_plan['planned'])}")
        if any(row["target_exists_before_apply"] is True for row in apply_plan["planned"]):
            errors.append("one or more target files already exists before apply")
        if any(row.get("approved_action") != "CREATE_EXACT_README_ONLY" for row in apply_plan["planned"]):
            errors.append("one or more planned paths is not approved for CREATE_EXACT_README_ONLY")

    if not errors:
        apply_result = apply_exact_files(apply_plan["planned"], content_by_path)
        errors.extend(apply_result["errors"])

    git_state_after_apply = get_git_state()

    expected_untracked_after_apply = sorted([CURRENT_TOOL_REL] + EXPECTED_PATHS)
    actual_untracked_after_apply = sorted(git_state_after_apply["untracked_paths"])

    if not errors and actual_untracked_after_apply != expected_untracked_after_apply:
        errors.append(
            "unexpected untracked paths after apply: "
            f"actual={actual_untracked_after_apply} expected={expected_untracked_after_apply}"
        )

    if git_state_after_apply["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked paths after apply: {git_state_after_apply['dirty_tracked_paths']}")

    passed = not errors

    invariants = {
        "approval_valid_and_consumed": validation["pass"] is True,
        "planned_apply_count_is_8": len(apply_plan.get("planned", [])) == 8,
        "applied_path_count_is_8": apply_result.get("applied_path_count") == 8,
        "only_expected_untracked_paths_after_apply": actual_untracked_after_apply == expected_untracked_after_apply,
        "no_dirty_tracked_after_apply": git_state_after_apply["dirty_tracked_count"] == 0,
        "all_applied_paths_are_expected": sorted([row["path"] for row in apply_result.get("applied_paths", [])]) == EXPECTED_PATHS,
        "no_runtime_strategy_or_capital_authorized": True,
        "no_overwrite_modify_delete_move_performed": True,
    }

    for key, value in invariants.items():
        if value is not True:
            errors.append(f"invariant {key} not true: {value}")

    passed = not errors

    payload = {
        "module": MODULE_NAME,
        "framework_skeleton_apply_status": "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_APPLY_V1_READY" if passed else "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_APPLY_V1_BLOCKED",
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_EXACT_FRAMEWORK_SKELETON_APPLY",
        "final_decision": "GENERIC_FRAMEWORK_SKELETON_EXACT_APPLY_READY_FOR_AUDIT_REFRESH" if passed else "KEEP_FREEZE_REVIEW_GENERIC_FRAMEWORK_SKELETON_APPLY_ERRORS",
        "next_action": "BUILD_REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_AUDIT_REFRESH_V1" if passed else "REVIEW_GENERIC_FRAMEWORK_SKELETON_APPLY_ERRORS",
        "next_module": "edge_factory_os_repo_only_generic_framework_skeleton_audit_refresh_v1.py" if passed else None,
        "reason": "Created exact approved framework README skeleton files only." if passed else "Generic framework skeleton apply validation failed.",
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "critical_issue_count": len(errors),
        "warning_count": 0,
        "errors": errors,
        "warnings": [],
        "validation": {
            "checks": validation["checks"],
            "git_state_before_apply": validation["git_state"],
            "git_state_after_apply": git_state_after_apply,
            "tracked_python_validation": validation["tracked_python_validation"],
            "source_statuses": validation["source_statuses"],
            "clean_baseline": validation["clean_baseline"],
        },
        "generic_framework_skeleton_apply": {
            "apply_plan": apply_plan,
            "apply_result": apply_result,
            "expected_applied_paths": EXPECTED_PATHS,
            "expected_untracked_after_apply": expected_untracked_after_apply,
            "actual_untracked_after_apply": actual_untracked_after_apply,
            "invariants": invariants,
        },
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "apply_performed_now": True if passed else False,
        "stage_recommended_now": True if passed else False,
        "commit_recommended_now": True if passed else False,
        "runtime_action_recommended_now": False,
        "capital_action_recommended_now": False,
        "holdout_action_recommended_now": False,
        "strategy_research_recommended_now": False,
        "candidate_generation_recommended_now": False,
        "candidate_release_recommended_now": False,
        "family_release_recommended_now": False,
        "framework_file_creation_performed_now": True if passed else False,
        "framework_directory_creation_performed_now": True if passed else False,
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

    latest_json = OUT_DIR / "repo_only_generic_framework_skeleton_apply_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_generic_framework_skeleton_apply_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "repo_only_generic_framework_skeleton_apply_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY GENERIC FRAMEWORK SKELETON APPLY v1",
        "=" * 100,
        f"framework_skeleton_apply_status: {payload['framework_skeleton_apply_status']}",
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
        "APPLY SUMMARY",
        "-" * 100,
        json.dumps(
            {
                "applied_path_count": apply_result.get("applied_path_count"),
                "created_parent_directory_count": apply_result.get("created_parent_directory_count"),
                "applied_paths": apply_result.get("applied_paths"),
                "invariants": invariants,
            },
            indent=2,
            sort_keys=True,
        ),
        "",
        "SAFETY",
        "-" * 100,
        json.dumps(SAFETY_FLAGS, indent=2, sort_keys=True),
        "",
        "GIT STATE AFTER APPLY",
        "-" * 100,
        json.dumps(git_state_after_apply, indent=2, sort_keys=True),
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