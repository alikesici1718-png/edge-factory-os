from __future__ import annotations

import ast
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_full_system_read_only_audit_refresh_after_gate_metadata_v4"
OUT_DIR = LAB_ROOT / "edge_factory_os_full_system_read_only_audit_refresh_after_gate_metadata_v4"
OUT_DIR.mkdir(parents=True, exist_ok=True)

APPLY_JSON = LAB_ROOT / "edge_factory_os_gate_metadata_patch_apply_v4" / "gate_metadata_patch_apply_v4_latest.json"
PREVIEW_JSON = LAB_ROOT / "edge_factory_os_gate_metadata_patch_preview_v4" / "gate_metadata_patch_preview_v4_latest.json"
APPROVAL_JSON = LAB_ROOT / "edge_factory_os_gate_metadata_patch_approval_v4" / "gate_metadata_patch_approval_v4_latest.json"

EXPECTED_HEAD_PREFIX = "f62e5bd"

EXPECTED_MODIFIED_TARGETS: Set[str] = {
    "src/edge_factory_claude_critical_patch_v1.py",
    "src/edge_factory_master_gate_compatibility_repair_v1.py",
    "src/edge_factory_master_gate_compatibility_repair_v2.py",
    "src/edge_factory_master_launcher_gate_repair_v3.py",
    "src/edge_factory_master_upper_system_boot_repair_v1.py",
    "src/edge_factory_patch_launcher_remove_blocking_risk_line_v1.py",
    "src/edge_factory_patch_master_launcher_risk_args_v1.py",
    "src/edge_factory_risk_manager_v4_wrapper_patch_v2.py",
    "src/edge_factory_signal_id_fallback_line_patch_v2.py",
    "tools/edge_factory_os_month_stability_repair_diagnostic_v1.py",
    "tools/edge_factory_os_repo_cleanup_plan_v1.py",
}

EXPECTED_COMMIT_INCLUDE_UNTRACKED: Set[str] = {
    "tools/edge_factory_os_gate_metadata_patch_preview_v4.py",
    "tools/edge_factory_os_gate_metadata_patch_approval_v4.py",
    "tools/edge_factory_os_gate_metadata_patch_apply_v4.py",
    "tools/edge_factory_os_full_system_read_only_audit_refresh_after_gate_metadata_v4.py",
}

KNOWN_LEAVE_UNTRACKED: Set[str] = {
    "tools/edge_factory_os_gate_metadata_patch_preview_v2.py",
    "tools/edge_factory_os_gate_metadata_patch_preview_v3.py",
    "tools/edge_factory_os_joint_null_distribution_validator_v1.py.readonly_fix_bak_20260514_022123",
    "tools/edge_factory_os_old_short_guarded_runtime_reenable_apply_v1.py",
    "tools/edge_factory_os_source_panel_anomaly_discovery_runner_v1.py.blocked_patch_bak_20260514_000647",
    "tools/edge_factory_os_universe_coverage_guard_v1.py",
}

SAFETY_FLAGS: Dict[str, bool] = {
    "read_only_audit": True,
    "apply_performed_now": False,
    "commit_performed_now": False,
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
    "direct_apply",
    "old_short_guarded_apply_execution",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: List[str], cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def get_git_state() -> Dict[str, Any]:
    head = run_cmd(["git", "rev-parse", "--short", "HEAD"])
    branch = run_cmd(["git", "branch", "--show-current"])
    status = run_cmd(["git", "status", "--porcelain=v1"])
    remote = run_cmd(["git", "status", "-sb"])

    status_lines = [line for line in status.stdout.splitlines() if line.strip()]
    untracked = [line[3:] for line in status_lines if line.startswith("?? ")]
    dirty_tracked_lines = [line for line in status_lines if not line.startswith("?? ")]

    dirty_tracked_paths: List[str] = []
    for line in dirty_tracked_lines:
        path = line[3:] if len(line) > 3 else line
        dirty_tracked_paths.append(path)

    return {
        "head": head.stdout.strip(),
        "branch": branch.stdout.strip(),
        "status_porcelain": status_lines,
        "remote_status_short": remote.stdout.splitlines(),
        "git_dirty": bool(status_lines),
        "dirty_tracked_count": len(dirty_tracked_lines),
        "dirty_tracked_paths": dirty_tracked_paths,
        "untracked_count": len(untracked),
        "untracked_paths": untracked,
    }


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def is_tracked_file(rel_path: str) -> bool:
    result = run_cmd(["git", "ls-files", "--error-unmatch", rel_path])
    return result.returncode == 0


def tracked_python_files() -> List[str]:
    result = run_cmd(["git", "ls-files", "*.py"])
    return sorted([line.strip() for line in result.stdout.splitlines() if line.strip()])


def parse_python_file(rel_path: str) -> Optional[str]:
    path = REPO_ROOT / rel_path
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("\ufeff"):
            return "BOM detected"
        ast.parse(text, filename=rel_path)
        return None
    except Exception as exc:
        return repr(exc)


def get_git_diff_for_path(rel_path: str) -> str:
    result = run_cmd(["git", "diff", "--", rel_path])
    return result.stdout


def validate_comment_only_diff(rel_path: str, diff_text: str) -> Dict[str, Any]:
    added_non_comment_lines: List[str] = []
    removed_lines: List[str] = []
    marker_start_count = 0
    marker_end_count = 0

    for line in diff_text.splitlines():
        if line.startswith("+# EDGE_FACTORY_GATE_METADATA_START"):
            marker_start_count += 1
        if line.startswith("+# EDGE_FACTORY_GATE_METADATA_END"):
            marker_end_count += 1

        if line.startswith("+") and not line.startswith("+++"):
            added = line[1:]
            if added != "" and not added.startswith("#"):
                added_non_comment_lines.append(line)

        if line.startswith("-") and not line.startswith("---"):
            removed_lines.append(line)

    return {
        "target_path": rel_path,
        "added_non_comment_lines": added_non_comment_lines,
        "removed_lines": removed_lines,
        "added_metadata_start_marker_count": marker_start_count,
        "added_metadata_end_marker_count": marker_end_count,
        "diff_line_count": len(diff_text.splitlines()),
        "comment_only_diff_pass": (
            not added_non_comment_lines
            and not removed_lines
            and marker_start_count == 1
            and marker_end_count == 1
        ),
    }


def extract_metadata_block(text: str) -> Optional[str]:
    pattern = re.compile(
        r"# EDGE_FACTORY_GATE_METADATA_START\n(.*?)# EDGE_FACTORY_GATE_METADATA_END",
        flags=re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        return None
    return "# EDGE_FACTORY_GATE_METADATA_START\n" + match.group(1) + "# EDGE_FACTORY_GATE_METADATA_END"


def validate_metadata_block(rel_path: str) -> Dict[str, Any]:
    path = REPO_ROOT / rel_path
    text = path.read_text(encoding="utf-8")

    block = extract_metadata_block(text)
    errors: List[str] = []

    if block is None:
        errors.append("metadata block missing")
        return {
            "target_path": rel_path,
            "metadata_pass": False,
            "errors": errors,
        }

    lines = block.splitlines()
    for line in lines:
        if not line.startswith("#"):
            errors.append(f"non-comment metadata line: {line}")

    required_exact_lines = [
        "# gate_metadata_version: 1",
        "# gate_metadata_kind: non_behavioral_comment_block",
        f"# gate_review_target_path: {rel_path}",
        "# allowed_scope: REPO_ONLY_OS_INTELLIGENCE",
        "# preview_only: true",
        "# non_behavioral_comment_only: true",
        "# runtime_touch_allowed: false",
        "# launcher_allowed: false",
        "# capital_change_allowed: false",
        "# active_paper_allowed: false",
        "# live_allowed: false",
        "# real_orders_allowed: false",
        "# candidate_generation_allowed: false",
        "# family_release_allowed: false",
        "# strategy_research_allowed: false",
        "# holdout_access_allowed: false",
        "# backup_delete_allowed: false",
        "# backup_move_allowed: false",
        "# direct_apply_allowed: false",
    ]

    for required in required_exact_lines:
        if required not in lines:
            errors.append(f"missing required metadata line: {required}")

    if text.count("EDGE_FACTORY_GATE_METADATA_START") != 1:
        errors.append("metadata start marker count is not 1")
    if text.count("EDGE_FACTORY_GATE_METADATA_END") != 1:
        errors.append("metadata end marker count is not 1")

    return {
        "target_path": rel_path,
        "metadata_pass": not errors,
        "errors": errors,
        "metadata_line_count": len(lines),
    }


def validate_json_contracts() -> Dict[str, Any]:
    errors: List[str] = []

    try:
        preview = load_json(PREVIEW_JSON)
        approval = load_json(APPROVAL_JSON)
        apply = load_json(APPLY_JSON)
    except Exception as exc:
        return {
            "json_contract_pass": False,
            "errors": [f"json load failed: {repr(exc)}"],
        }

    if preview.get("preview_status") != "GATE_METADATA_PATCH_PREVIEW_V4_READY_NO_APPLY":
        errors.append(f"bad preview_status: {preview.get('preview_status')}")

    if approval.get("approval_status") != "GATE_METADATA_PATCH_APPROVAL_V4_READY_COMMENT_ONLY_APPLY_ALLOWED":
        errors.append(f"bad approval_status: {approval.get('approval_status')}")

    if apply.get("apply_status") != "GATE_METADATA_PATCH_APPLY_V4_COMMENT_ONLY_APPLIED":
        errors.append(f"bad apply_status: {apply.get('apply_status')}")

    modified_targets = set(apply.get("modified_targets") or [])
    if modified_targets != EXPECTED_MODIFIED_TARGETS:
        errors.append(
            "apply modified_targets mismatch: "
            f"missing={sorted(EXPECTED_MODIFIED_TARGETS - modified_targets)} "
            f"extra={sorted(modified_targets - EXPECTED_MODIFIED_TARGETS)}"
        )

    apply_flags = apply.get("safety_flags") if isinstance(apply.get("safety_flags"), dict) else {}
    required_false_flags = [
        "runtime_touch_allowed",
        "launcher_allowed",
        "capital_change_allowed",
        "active_paper_allowed",
        "live_allowed",
        "real_orders_allowed",
        "candidate_generation_allowed",
        "candidate_release_allowed",
        "family_release_allowed",
        "strategy_research_allowed",
        "holdout_access_allowed",
        "gitignore_change_allowed",
        "backup_delete_allowed",
        "backup_move_allowed",
        "git_add_force_allowed",
    ]

    for key in required_false_flags:
        if apply_flags.get(key) is not False:
            errors.append(f"apply safety flag not false: {key}={apply_flags.get(key)}")

    if apply_flags.get("comment_only_apply") is not True:
        errors.append("apply safety flag comment_only_apply is not true")

    if apply_flags.get("non_behavioral_metadata_only") is not True:
        errors.append("apply safety flag non_behavioral_metadata_only is not true")

    return {
        "json_contract_pass": not errors,
        "errors": errors,
        "preview_json": str(PREVIEW_JSON),
        "approval_json": str(APPROVAL_JSON),
        "apply_json": str(APPLY_JSON),
    }


def main() -> int:
    for key, value in SAFETY_FLAGS.items():
        if not isinstance(value, bool):
            raise SystemExit(f"safety flag is not boolean: {key}")

    git_state = get_git_state()

    errors: List[str] = []
    warnings: List[str] = []

    if not git_state["head"].startswith(EXPECTED_HEAD_PREFIX):
        errors.append(f"unexpected git HEAD: {git_state['head']} expected prefix {EXPECTED_HEAD_PREFIX}")

    dirty_tracked = set(git_state["dirty_tracked_paths"])
    if dirty_tracked != EXPECTED_MODIFIED_TARGETS:
        errors.append(
            "dirty tracked paths mismatch: "
            f"missing={sorted(EXPECTED_MODIFIED_TARGETS - dirty_tracked)} "
            f"extra={sorted(dirty_tracked - EXPECTED_MODIFIED_TARGETS)}"
        )

    untracked = set(git_state["untracked_paths"])
    expected_known_untracked = KNOWN_LEAVE_UNTRACKED | EXPECTED_COMMIT_INCLUDE_UNTRACKED
    unknown_untracked = sorted(untracked - expected_known_untracked)
    missing_expected_commit_untracked = sorted(EXPECTED_COMMIT_INCLUDE_UNTRACKED - untracked)

    if unknown_untracked:
        warnings.append(f"unknown untracked paths present: {unknown_untracked}")

    if missing_expected_commit_untracked:
        warnings.append(f"expected audit/metadata tool files not all untracked yet: {missing_expected_commit_untracked}")

    json_contract_validation = validate_json_contracts()
    if not json_contract_validation["json_contract_pass"]:
        errors.extend([f"json_contract: {e}" for e in json_contract_validation["errors"]])

    target_validations: List[Dict[str, Any]] = []
    diff_validations: List[Dict[str, Any]] = []
    syntax_errors_changed: List[Dict[str, Any]] = []

    for rel in sorted(EXPECTED_MODIFIED_TARGETS):
        if not is_tracked_file(rel):
            errors.append(f"target not tracked by git: {rel}")
            continue

        target = REPO_ROOT / rel
        if not target.exists():
            errors.append(f"target missing: {rel}")
            continue

        syntax_error = parse_python_file(rel)
        if syntax_error:
            syntax_errors_changed.append({"target_path": rel, "error": syntax_error})

        metadata_validation = validate_metadata_block(rel)
        target_validations.append(metadata_validation)
        if not metadata_validation["metadata_pass"]:
            errors.extend([f"{rel}: {e}" for e in metadata_validation["errors"]])

        diff_text = get_git_diff_for_path(rel)
        diff_validation = validate_comment_only_diff(rel, diff_text)
        diff_validations.append(diff_validation)
        if not diff_validation["comment_only_diff_pass"]:
            errors.append(f"{rel}: diff is not clean comment-only metadata insertion")

    if syntax_errors_changed:
        errors.extend([f"{row['target_path']}: syntax error after metadata apply: {row['error']}" for row in syntax_errors_changed])

    all_tracked_py = tracked_python_files()
    repo_python_syntax_errors: List[Dict[str, Any]] = []
    repo_bom_errors: List[str] = []

    for rel in all_tracked_py:
        path = REPO_ROOT / rel
        try:
            text = path.read_text(encoding="utf-8")
            if text.startswith("\ufeff"):
                repo_bom_errors.append(rel)
            ast.parse(text, filename=rel)
        except Exception as exc:
            repo_python_syntax_errors.append({"path": rel, "error": repr(exc)})

    if repo_bom_errors:
        errors.append(f"tracked python BOM errors found: {repo_bom_errors}")

    if repo_python_syntax_errors:
        errors.append(f"tracked python syntax errors found: {repo_python_syntax_errors[:20]}")

    audit_pass = not errors

    recommended_stage_paths = sorted(EXPECTED_MODIFIED_TARGETS | EXPECTED_COMMIT_INCLUDE_UNTRACKED)

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "audit_status": (
            "FULL_SYSTEM_READ_ONLY_AUDIT_REFRESH_AFTER_GATE_METADATA_V4_PASS"
            if audit_pass
            else "FULL_SYSTEM_READ_ONLY_AUDIT_REFRESH_AFTER_GATE_METADATA_V4_FAIL"
        ),
        "severity": "ATTENTION" if audit_pass else "BLOCKED",
        "allowed_scope": "READ_ONLY_REPO_AUDIT",
        "final_decision": (
            "COMMIT_GATE_METADATA_PATCH_V4_IF_USER_ACCEPTS_STAGE_LIST"
            if audit_pass
            else "STOP_REVIEW_AUDIT_FAILURES_NO_COMMIT"
        ),
        "next_action": (
            "COMMIT_ONLY_APPROVED_METADATA_TARGETS_AND_V4_AUDIT_TOOLING_NO_FORCE_ADD"
            if audit_pass
            else "FIX_AUDIT_FAILURES_BEFORE_COMMIT"
        ),
        "next_module": "git_commit_gate_metadata_patch_v4" if audit_pass else None,
        "reason": (
            "11 tracked targets contain exactly one non-behavioral metadata comment block and repo tracked Python syntax/BOM audit passed"
            if audit_pass
            else "audit errors detected; commit blocked"
        ),
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "errors": errors,
        "warnings": warnings,
        "critical_issue_count": len(errors),
        "warning_count": len(warnings),
        "audit_pass": audit_pass,
        "json_contract_validation": json_contract_validation,
        "target_metadata_validations": target_validations,
        "diff_validations": diff_validations,
        "syntax_errors_changed": syntax_errors_changed,
        "tracked_python_file_count": len(all_tracked_py),
        "repo_python_syntax_error_count": len(repo_python_syntax_errors),
        "repo_python_syntax_errors": repo_python_syntax_errors,
        "repo_bom_error_count": len(repo_bom_errors),
        "repo_bom_errors": repo_bom_errors,
        "expected_modified_targets": sorted(EXPECTED_MODIFIED_TARGETS),
        "actual_dirty_tracked_paths": sorted(dirty_tracked),
        "known_leave_untracked": sorted(KNOWN_LEAVE_UNTRACKED),
        "expected_commit_include_untracked": sorted(EXPECTED_COMMIT_INCLUDE_UNTRACKED),
        "unknown_untracked": unknown_untracked,
        "recommended_stage_paths": recommended_stage_paths,
        "commit_performed_now": False,
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "runtime_touched": False,
        "launcher_executed": False,
        "capital_changed": False,
        "live_or_real_orders": False,
        "holdout_accessed": False,
        "backup_deleted_or_moved": False,
        "gitignore_changed": False,
        "git_add_force_used": False,
        "git_state": git_state,
    }

    latest_json = OUT_DIR / "full_system_read_only_audit_refresh_after_gate_metadata_v4_latest.json"
    timestamped_json = OUT_DIR / f"full_system_read_only_audit_refresh_after_gate_metadata_v4_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "full_system_read_only_audit_refresh_after_gate_metadata_v4_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    txt_lines = [
        "EDGE FACTORY OS FULL SYSTEM READ-ONLY AUDIT REFRESH AFTER GATE METADATA v4",
        "=" * 100,
        f"audit_status: {payload['audit_status']}",
        f"severity: {payload['severity']}",
        f"allowed_scope: {payload['allowed_scope']}",
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
        "WARNINGS",
        "-" * 100,
        json.dumps(warnings, indent=2, sort_keys=True),
        "",
        "RECOMMENDED STAGE PATHS",
        "-" * 100,
        json.dumps(recommended_stage_paths, indent=2, sort_keys=True),
        "",
        "KNOWN LEAVE UNTRACKED",
        "-" * 100,
        json.dumps(sorted(KNOWN_LEAVE_UNTRACKED), indent=2, sort_keys=True),
        "",
        "GIT STATE",
        "-" * 100,
        json.dumps(git_state, indent=2, sort_keys=True),
        "",
        "OUTPUTS",
        "-" * 100,
        f"latest_json: {latest_json}",
        f"timestamped_json: {timestamped_json}",
        f"latest_txt: {latest_txt}",
    ]

    latest_txt.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")

    print("\n".join(txt_lines))

    return 0 if audit_pass else 3


if __name__ == "__main__":
    raise SystemExit(main())