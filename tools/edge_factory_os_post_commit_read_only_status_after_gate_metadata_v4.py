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

MODULE_NAME = "edge_factory_os_post_commit_read_only_status_after_gate_metadata_v4"
OUT_DIR = LAB_ROOT / "edge_factory_os_post_commit_read_only_status_after_gate_metadata_v4"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "578879b"
EXPECTED_COMMIT_MESSAGE = "Add gate metadata comments after v4 approval"

EXPECTED_COMMITTED_PATHS: Set[str] = {
    "src/edge_factory_claude_critical_patch_v1.py",
    "src/edge_factory_master_gate_compatibility_repair_v1.py",
    "src/edge_factory_master_gate_compatibility_repair_v2.py",
    "src/edge_factory_master_launcher_gate_repair_v3.py",
    "src/edge_factory_master_upper_system_boot_repair_v1.py",
    "src/edge_factory_patch_launcher_remove_blocking_risk_line_v1.py",
    "src/edge_factory_patch_master_launcher_risk_args_v1.py",
    "src/edge_factory_risk_manager_v4_wrapper_patch_v2.py",
    "src/edge_factory_signal_id_fallback_line_patch_v2.py",
    "tools/edge_factory_os_full_system_read_only_audit_refresh_after_gate_metadata_v4.py",
    "tools/edge_factory_os_gate_metadata_patch_apply_v4.py",
    "tools/edge_factory_os_gate_metadata_patch_approval_v4.py",
    "tools/edge_factory_os_gate_metadata_patch_preview_v4.py",
    "tools/edge_factory_os_month_stability_repair_diagnostic_v1.py",
    "tools/edge_factory_os_repo_cleanup_plan_v1.py",
}

EXPECTED_METADATA_TARGETS: Set[str] = {
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

KNOWN_ALLOWED_UNTRACKED: Set[str] = {
    "tools/edge_factory_os_gate_metadata_patch_preview_v2.py",
    "tools/edge_factory_os_gate_metadata_patch_preview_v3.py",
    "tools/edge_factory_os_joint_null_distribution_validator_v1.py.readonly_fix_bak_20260514_022123",
    "tools/edge_factory_os_old_short_guarded_runtime_reenable_apply_v1.py",
    "tools/edge_factory_os_source_panel_anomaly_discovery_runner_v1.py.blocked_patch_bak_20260514_000647",
    "tools/edge_factory_os_universe_coverage_guard_v1.py",
    "tools/edge_factory_os_post_commit_read_only_status_after_gate_metadata_v4.py",
}

SAFETY_FLAGS: Dict[str, bool] = {
    "read_only_status_refresh": True,
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
    "old_short_guarded_apply_allowed": False,
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


def tracked_python_files() -> List[str]:
    result = run_cmd(["git", "ls-files", "*.py"])
    return sorted([line.strip() for line in result.stdout.splitlines() if line.strip()])


def latest_commit_paths() -> Dict[str, Any]:
    msg = run_cmd(["git", "log", "-1", "--pretty=%s"]).stdout.strip()
    name_status = run_cmd(["git", "show", "--name-status", "--format=", "HEAD"]).stdout.splitlines()

    paths: List[str] = []
    statuses: List[Dict[str, str]] = []

    for line in name_status:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) >= 2:
            status = parts[0]
            path = parts[-1].replace("\\", "/")
            paths.append(path)
            statuses.append({"status": status, "path": path})

    return {
        "commit_message": msg,
        "paths": sorted(paths),
        "name_status": statuses,
    }


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
    errors: List[str] = []

    if text.startswith("\ufeff"):
        errors.append("BOM detected")

    block = extract_metadata_block(text)
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

    try:
        ast.parse(text, filename=rel_path)
    except Exception as exc:
        errors.append(f"syntax error after metadata block: {repr(exc)}")

    return {
        "target_path": rel_path,
        "metadata_pass": not errors,
        "errors": errors,
        "metadata_line_count": len(lines),
    }


def main() -> int:
    for key, value in SAFETY_FLAGS.items():
        if not isinstance(value, bool):
            raise SystemExit(f"safety flag is not boolean: {key}")

    errors: List[str] = []
    warnings: List[str] = []

    git_state = get_git_state()
    commit_info = latest_commit_paths()

    if not git_state["head"].startswith(EXPECTED_HEAD_PREFIX):
        errors.append(f"unexpected HEAD: {git_state['head']} expected prefix {EXPECTED_HEAD_PREFIX}")

    if commit_info["commit_message"] != EXPECTED_COMMIT_MESSAGE:
        errors.append(f"unexpected latest commit message: {commit_info['commit_message']}")

    latest_paths = set(commit_info["paths"])
    if latest_paths != EXPECTED_COMMITTED_PATHS:
        errors.append(
            "latest commit path set mismatch: "
            f"missing={sorted(EXPECTED_COMMITTED_PATHS - latest_paths)} "
            f"extra={sorted(latest_paths - EXPECTED_COMMITTED_PATHS)}"
        )

    if git_state["dirty_tracked_count"] != 0:
        errors.append(f"tracked files dirty after commit: {git_state['dirty_tracked_paths']}")

    untracked = set(git_state["untracked_paths"])
    unknown_untracked = sorted(untracked - KNOWN_ALLOWED_UNTRACKED)
    missing_known_untracked = sorted(KNOWN_ALLOWED_UNTRACKED - untracked)

    if unknown_untracked:
        errors.append(f"unknown untracked paths after commit: {unknown_untracked}")

    if missing_known_untracked:
        warnings.append(f"some known untracked paths are not present: {missing_known_untracked}")

    metadata_validations: List[Dict[str, Any]] = []
    for rel in sorted(EXPECTED_METADATA_TARGETS):
        validation = validate_metadata_block(rel)
        metadata_validations.append(validation)
        if not validation["metadata_pass"]:
            errors.extend([f"{rel}: {err}" for err in validation["errors"]])

    all_py = tracked_python_files()
    syntax_errors: List[Dict[str, str]] = []
    bom_errors: List[str] = []

    for rel in all_py:
        path = REPO_ROOT / rel
        try:
            text = path.read_text(encoding="utf-8")
            if text.startswith("\ufeff"):
                bom_errors.append(rel)
            ast.parse(text, filename=rel)
        except Exception as exc:
            syntax_errors.append({"path": rel, "error": repr(exc)})

    if bom_errors:
        errors.append(f"tracked Python BOM errors found: {bom_errors}")

    if syntax_errors:
        errors.append(f"tracked Python syntax errors found: {syntax_errors[:20]}")

    status_pass = not errors

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "status": (
            "POST_COMMIT_READ_ONLY_STATUS_AFTER_GATE_METADATA_V4_PASS"
            if status_pass
            else "POST_COMMIT_READ_ONLY_STATUS_AFTER_GATE_METADATA_V4_FAIL"
        ),
        "severity": "ATTENTION" if status_pass else "BLOCKED",
        "allowed_scope": "READ_ONLY_REPO_STATUS_REFRESH",
        "final_decision": (
            "REFRESH_TRIAGE_CLASSIFIER_GATE_REVIEW_FROM_NEW_HEAD"
            if status_pass
            else "STOP_REVIEW_POST_COMMIT_STATUS_FAILURE"
        ),
        "next_action": (
            "BUILD_OR_RUN_TRIAGE_CLASSIFIER_GATE_REVIEW_REFRESH_NO_RUNTIME_ACTION"
            if status_pass
            else "FIX_POST_COMMIT_STATUS_FAILURE_BEFORE_CONTINUING"
        ),
        "next_module": (
            "edge_factory_os_attention_triage_classifier_gate_review_refresh_after_metadata_v4"
            if status_pass
            else None
        ),
        "reason": (
            "commit 578879b verified; metadata blocks/syntax/BOM clean; only known untracked paths remain"
            if status_pass
            else "post-commit status errors detected"
        ),
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "latest_commit": git_state["head"],
        "latest_commit_info": commit_info,
        "errors": errors,
        "warnings": warnings,
        "critical_issue_count": len(errors),
        "warning_count": len(warnings),
        "status_pass": status_pass,
        "metadata_validations": metadata_validations,
        "tracked_python_file_count": len(all_py),
        "repo_python_syntax_error_count": len(syntax_errors),
        "repo_python_syntax_errors": syntax_errors,
        "repo_bom_error_count": len(bom_errors),
        "repo_bom_errors": bom_errors,
        "expected_committed_paths": sorted(EXPECTED_COMMITTED_PATHS),
        "expected_metadata_targets": sorted(EXPECTED_METADATA_TARGETS),
        "known_allowed_untracked": sorted(KNOWN_ALLOWED_UNTRACKED),
        "unknown_untracked": unknown_untracked,
        "missing_known_untracked": missing_known_untracked,
        "commit_performed_now": False,
        "apply_performed_now": False,
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

    latest_json = OUT_DIR / "post_commit_read_only_status_after_gate_metadata_v4_latest.json"
    timestamped_json = OUT_DIR / f"post_commit_read_only_status_after_gate_metadata_v4_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "post_commit_read_only_status_after_gate_metadata_v4_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    txt_lines = [
        "EDGE FACTORY OS POST-COMMIT READ-ONLY STATUS AFTER GATE METADATA v4",
        "=" * 100,
        f"status: {payload['status']}",
        f"severity: {payload['severity']}",
        f"allowed_scope: {payload['allowed_scope']}",
        f"final_decision: {payload['final_decision']}",
        f"next_action: {payload['next_action']}",
        f"next_module: {payload['next_module']}",
        f"reason: {payload['reason']}",
        f"latest_commit: {payload['latest_commit']}",
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
        "LATEST COMMIT PATHS",
        "-" * 100,
        json.dumps(commit_info["paths"], indent=2, sort_keys=True),
        "",
        "KNOWN ALLOWED UNTRACKED",
        "-" * 100,
        json.dumps(sorted(KNOWN_ALLOWED_UNTRACKED), indent=2, sort_keys=True),
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

    return 0 if status_pass else 3


if __name__ == "__main__":
    raise SystemExit(main())