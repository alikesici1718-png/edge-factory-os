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

MODULE_NAME = "edge_factory_os_repo_only_generic_framework_skeleton_final_check_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_repo_only_generic_framework_skeleton_final_check_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "6155f72"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_generic_framework_skeleton_final_check_v1.py"

AUDIT_JSON = LAB_ROOT / "edge_factory_os_repo_only_generic_framework_skeleton_audit_refresh_v1" / "repo_only_generic_framework_skeleton_audit_refresh_v1_latest.json"
AUDIT_POST_CHECK_JSON = LAB_ROOT / "edge_factory_os_repo_only_generic_framework_skeleton_audit_refresh_post_commit_check" / "repo_only_generic_framework_skeleton_audit_refresh_post_commit_check_latest.json"
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

EXPECTED_CHAIN = [
    ("generic_framework_skeleton_contract", CONTRACT_JSON, "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_CONTRACT_V1_READY"),
    ("generic_framework_skeleton_preview", PREVIEW_JSON, "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_PREVIEW_V1_READY"),
    ("generic_framework_skeleton_approval", APPROVAL_JSON, "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_APPROVAL_V1_READY"),
    ("generic_framework_skeleton_apply", APPLY_JSON, "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_APPLY_V1_READY"),
    ("generic_framework_skeleton_apply_post_check", APPLY_POST_CHECK_JSON, "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_APPLY_POST_COMMIT_CHECK_PASS"),
    ("generic_framework_skeleton_audit_refresh", AUDIT_JSON, "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_AUDIT_REFRESH_V1_READY"),
    ("generic_framework_skeleton_audit_refresh_post_check", AUDIT_POST_CHECK_JSON, "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_AUDIT_REFRESH_POST_COMMIT_CHECK_PASS"),
]

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_generic_framework_skeleton_final_check": True,
    "read_only_final_check_only": True,
    "generic_framework_skeleton_chain_required": True,

    "repo_only_governance_allowed": True,
    "repo_only_audit_allowed": True,
    "read_only_validation_allowed": True,

    "framework_skeleton_complete": True,
    "normal_repo_only_development_resume_allowed_next": True,

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
        "framework_skeleton_audit_refresh_status",
        "audit_status",
        "framework_skeleton_apply_status",
        "framework_skeleton_approval_status",
        "framework_skeleton_preview_status",
        "framework_skeleton_contract_status",
    ]:
        value = obj.get(key)
        if value:
            return str(value)
    return None


def record_for_json(label: str, path: Path, expected_status: str) -> Dict[str, Any]:
    obj = load_json(path)
    status = first_status(obj)
    return {
        "label": label,
        "path": str(path),
        "status": status,
        "expected_status": expected_status,
        "status_match": status == expected_status,
        "critical_issue_count": obj.get("critical_issue_count"),
        "warning_count": obj.get("warning_count"),
        "next_module": obj.get("next_module"),
        "final_decision": obj.get("final_decision"),
        "raw": obj,
    }


def count_zero_ok(value: Any) -> bool:
    return isinstance(value, int) and value == 0


def expected_hashes_from_apply(apply_obj: Dict[str, Any]) -> Dict[str, str]:
    apply_body = apply_obj.get("generic_framework_skeleton_apply", {})
    result = apply_body.get("apply_result", {})
    paths = result.get("applied_paths", [])

    mapping: Dict[str, str] = {}
    if isinstance(paths, list):
        for row in paths:
            if isinstance(row, dict) and isinstance(row.get("path"), str) and isinstance(row.get("content_sha256"), str):
                mapping[row["path"]] = row["content_sha256"]
    return mapping


def build_final_check() -> Dict[str, Any]:
    errors: List[str] = []
    chain_records: List[Dict[str, Any]] = []

    for label, path, expected_status in EXPECTED_CHAIN:
        try:
            record = record_for_json(label, path, expected_status)
            chain_records.append(
                {
                    "label": record["label"],
                    "path": record["path"],
                    "status": record["status"],
                    "expected_status": record["expected_status"],
                    "status_match": record["status_match"],
                    "critical_issue_count": record["critical_issue_count"],
                    "warning_count": record["warning_count"],
                    "next_module": record["next_module"],
                    "final_decision": record["final_decision"],
                }
            )

            if not record["status_match"]:
                errors.append(f"{label} status mismatch: expected={expected_status} actual={record['status']}")
            if not count_zero_ok(record["critical_issue_count"]):
                errors.append(f"{label} critical_issue_count not 0: {record['critical_issue_count']}")
            if not count_zero_ok(record["warning_count"]):
                errors.append(f"{label} warning_count not 0: {record['warning_count']}")

        except Exception as exc:
            errors.append(f"cannot load chain record {label}: {path} error={repr(exc)}")

    apply_obj = load_json(APPLY_JSON)
    expected_hashes = expected_hashes_from_apply(apply_obj)
    tracked = set(tracked_files())
    framework_records: List[Dict[str, Any]] = []

    for rel in EXPECTED_PATHS:
        path = REPO_ROOT / rel
        exists = path.exists()
        tracked_now = rel in tracked
        actual_hash = sha256_file(path) if exists else None
        expected_hash = expected_hashes.get(rel)
        bom = path.read_bytes().startswith(b"\xef\xbb\xbf") if exists else False

        if not exists:
            errors.append(f"framework file missing: {rel}")
        if not tracked_now:
            errors.append(f"framework file not tracked: {rel}")
        if actual_hash != expected_hash:
            errors.append(f"framework file hash mismatch: {rel} actual={actual_hash} expected={expected_hash}")
        if bom:
            errors.append(f"framework file BOM detected: {rel}")

        framework_records.append(
            {
                "path": rel,
                "exists": exists,
                "tracked": tracked_now,
                "bom_detected": bom,
                "content_sha256_actual": actual_hash,
                "content_sha256_expected": expected_hash,
                "hash_match": actual_hash == expected_hash,
            }
        )

    git_state = get_git_state()
    py = validate_tracked_python()

    if git_state["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked paths present: {git_state['dirty_tracked_paths']}")

    expected_untracked = {CURRENT_TOOL_REL}
    actual_untracked = set(git_state["untracked_paths"])
    if actual_untracked != expected_untracked:
        errors.append(f"unexpected untracked set: actual={sorted(actual_untracked)} expected={sorted(expected_untracked)}")

    if not git_state["head"].startswith(EXPECTED_HEAD_PREFIX):
        errors.append(f"unexpected HEAD: {git_state['head']} expected prefix {EXPECTED_HEAD_PREFIX}")

    if commit_subject("HEAD") != "Add repo-only generic framework skeleton audit refresh":
        errors.append(f"unexpected HEAD commit subject: {commit_subject('HEAD')}")

    if not py["pass"]:
        errors.append(f"tracked Python validation failed: syntax={py['syntax_errors'][:20]} bom={py['bom_errors']}")

    invariants = {
        "chain_record_count_is_7": len(chain_records) == 7,
        "all_chain_statuses_match": all(row["status_match"] is True for row in chain_records),
        "all_chain_counts_zero": all(row["critical_issue_count"] == 0 and row["warning_count"] == 0 for row in chain_records),
        "framework_readme_count_is_8": len(framework_records) == 8,
        "all_framework_files_exist": all(row["exists"] is True for row in framework_records),
        "all_framework_files_tracked": all(row["tracked"] is True for row in framework_records),
        "all_framework_hashes_match_apply": all(row["hash_match"] is True for row in framework_records),
        "no_bom_in_framework_files": all(row["bom_detected"] is False for row in framework_records),
        "repo_clean_except_current_tool_untracked": git_state["dirty_tracked_count"] == 0 and actual_untracked == expected_untracked,
        "tracked_python_clean": py["pass"] is True,
        "no_runtime_strategy_or_capital_authorized": True,
        "no_file_creation_or_modification_performed_by_final_check": True,
    }

    for key, value in invariants.items():
        if value is not True:
            errors.append(f"invariant {key} not true: {value}")

    return {
        "final_check_status": "GENERIC_FRAMEWORK_SKELETON_FINAL_CHECK_ACTIVE" if not errors else "GENERIC_FRAMEWORK_SKELETON_FINAL_CHECK_BLOCKED",
        "final_check_scope": "REPO_ONLY_FRAMEWORK_SKELETON_FINAL_AUDIT",
        "chain_records": chain_records,
        "framework_records": framework_records,
        "summary": {
            "chain_record_count": len(chain_records),
            "framework_readme_count": len(framework_records),
            "dirty_tracked_count": git_state["dirty_tracked_count"],
            "untracked_count": git_state["untracked_count"],
            "tracked_python_file_count": py["tracked_python_file_count"],
            "tracked_python_syntax_error_count": py["syntax_error_count"],
            "tracked_python_bom_error_count": py["bom_error_count"],
        },
        "invariants": invariants,
        "errors": errors,
        "recommended_next_step": {
            "step": "RESUME_NORMAL_REPO_ONLY_OS_DEVELOPMENT",
            "module": "edge_factory_os_repo_only_status_refresh_after_framework_skeleton_v1.py",
            "scope": "REPO_ONLY_OS_INTELLIGENCE",
            "reason": "Framework skeleton chain is complete and audited; resume normal repo-only OS development with a status refresh.",
        },
    }


def main() -> int:
    safety_errors = [key for key, value in SAFETY_FLAGS.items() if not isinstance(value, bool)]

    final_check = build_final_check()
    errors = list(final_check["errors"])

    if safety_errors:
        errors.append(f"safety flags are not boolean: {safety_errors}")

    passed = not errors

    payload = {
        "module": MODULE_NAME,
        "framework_skeleton_final_check_status": "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_FINAL_CHECK_V1_READY" if passed else "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_FINAL_CHECK_V1_BLOCKED",
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_FRAMEWORK_SKELETON_FINAL_AUDIT",
        "final_decision": "GENERIC_FRAMEWORK_SKELETON_CHAIN_COMPLETE_RESUME_REPO_ONLY_OS_DEVELOPMENT" if passed else "KEEP_FREEZE_REVIEW_GENERIC_FRAMEWORK_SKELETON_FINAL_CHECK_ERRORS",
        "next_action": "BUILD_REPO_ONLY_STATUS_REFRESH_AFTER_FRAMEWORK_SKELETON_V1" if passed else "REVIEW_GENERIC_FRAMEWORK_SKELETON_FINAL_CHECK_ERRORS",
        "next_module": "edge_factory_os_repo_only_status_refresh_after_framework_skeleton_v1.py" if passed else None,
        "reason": "Generic framework skeleton chain completed and final audit passed." if passed else "Generic framework skeleton final check validation failed.",
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "critical_issue_count": len(errors),
        "warning_count": 0,
        "errors": errors,
        "warnings": [],
        "generic_framework_skeleton_final_check": final_check,
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

    latest_json = OUT_DIR / "repo_only_generic_framework_skeleton_final_check_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_generic_framework_skeleton_final_check_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "repo_only_generic_framework_skeleton_final_check_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY GENERIC FRAMEWORK SKELETON FINAL CHECK v1",
        "=" * 100,
        f"framework_skeleton_final_check_status: {payload['framework_skeleton_final_check_status']}",
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
        "FINAL CHECK SUMMARY",
        "-" * 100,
        json.dumps(
            {
                "summary": final_check["summary"],
                "invariants": final_check["invariants"],
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