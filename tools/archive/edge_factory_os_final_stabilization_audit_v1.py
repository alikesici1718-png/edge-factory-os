from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_final_stabilization_audit_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_final_stabilization_audit_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "9f43101"
EXPECTED_COMMIT_MESSAGE = "Record stabilization freeze and recurrence guard tooling"

POST_COMMIT_STATUS_JSON = (
    LAB_ROOT
    / "edge_factory_os_post_commit_read_only_status_after_gate_metadata_v4"
    / "post_commit_read_only_status_after_gate_metadata_v4_latest.json"
)

POLICY_JSON = (
    LAB_ROOT
    / "edge_factory_os_attention_issue_policy_classifier_after_gate_metadata_v4"
    / "attention_issue_policy_classifier_after_metadata_v4_latest.json"
)

INVALID_METADATA_INSPECTOR_JSON = (
    LAB_ROOT
    / "edge_factory_os_invalid_existing_metadata_block_inspector_v1"
    / "invalid_existing_metadata_block_inspector_v1_latest.json"
)

FREEZE_CONTROLLER_JSON = (
    LAB_ROOT
    / "edge_factory_os_stabilization_freeze_error_closure_controller_v1"
    / "stabilization_freeze_error_closure_controller_v1_latest.json"
)

OLD_SHORT_LOCK_JSON = (
    LAB_ROOT
    / "edge_factory_os_old_short_guarded_apply_lock_registry_v1"
    / "old_short_guarded_apply_lock_registry_v1_latest.json"
)

UNTRACKED_HYGIENE_JSON = (
    LAB_ROOT
    / "edge_factory_os_untracked_hygiene_and_universe_guard_review_plan_v1"
    / "untracked_hygiene_and_universe_guard_review_plan_v1_latest.json"
)

COMMIT_PLAN_JSON = (
    LAB_ROOT
    / "edge_factory_os_untracked_stabilization_tooling_commit_plan_v1"
    / "untracked_stabilization_tooling_commit_plan_v1_latest.json"
)

COMMIT_APPROVAL_JSON = (
    LAB_ROOT
    / "edge_factory_os_stabilization_tooling_commit_approval_v1"
    / "stabilization_tooling_commit_approval_v1_latest.json"
)

EXPECTED_LATEST_COMMIT_PATHS: Set[str] = {
    "tools/edge_factory_os_attention_issue_policy_classifier_after_gate_metadata_v4.py",
    "tools/edge_factory_os_attention_triage_classifier_gate_review_refresh_after_metadata_v4.py",
    "tools/edge_factory_os_invalid_existing_metadata_block_inspector_v1.py",
    "tools/edge_factory_os_metadata_classifier_rule_refinement_apply_v1.py",
    "tools/edge_factory_os_metadata_classifier_rule_refinement_approval_v1.py",
    "tools/edge_factory_os_metadata_classifier_rule_refinement_preview_v1.py",
    "tools/edge_factory_os_old_short_guarded_apply_lock_registry_v1.py",
    "tools/edge_factory_os_post_commit_read_only_status_after_gate_metadata_v4.py",
    "tools/edge_factory_os_stabilization_freeze_error_closure_controller_v1.py",
    "tools/edge_factory_os_stabilization_tooling_commit_approval_v1.py",
    "tools/edge_factory_os_untracked_hygiene_and_universe_guard_review_plan_v1.py",
    "tools/edge_factory_os_untracked_stabilization_tooling_commit_plan_v1.py",
}

EXPECTED_ALLOWED_UNTRACKED: Set[str] = {
    "tools/edge_factory_os_gate_metadata_patch_preview_v2.py",
    "tools/edge_factory_os_gate_metadata_patch_preview_v3.py",
    "tools/edge_factory_os_joint_null_distribution_validator_v1.py.readonly_fix_bak_20260514_022123",
    "tools/edge_factory_os_old_short_guarded_runtime_reenable_apply_v1.py",
    "tools/edge_factory_os_source_panel_anomaly_discovery_runner_v1.py.blocked_patch_bak_20260514_000647",
    "tools/edge_factory_os_universe_coverage_guard_v1.py",
}

REQUIRED_TRACKED_GUARD_TOOLS: Set[str] = EXPECTED_LATEST_COMMIT_PATHS | {
    "tools/edge_factory_os_full_system_read_only_audit_refresh_after_gate_metadata_v4.py",
    "tools/edge_factory_os_gate_metadata_patch_apply_v4.py",
    "tools/edge_factory_os_gate_metadata_patch_approval_v4.py",
    "tools/edge_factory_os_gate_metadata_patch_preview_v4.py",
}

SAFETY_FLAGS: Dict[str, bool] = {
    "stabilization_freeze_active": True,
    "final_stabilization_audit": True,
    "stage_performed_now": False,
    "commit_performed_now": False,
    "apply_performed_now": False,
    "direct_apply_allowed": False,
    "os_development_allowed": False,
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
    "mass_metadata_patch_allowed": False,
}

FORBIDDEN_ACTIONS: List[str] = [
    "os_feature_development",
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
    "old_short_guarded_apply_execution",
    "universe_guard_stage_without_approval",
    "universe_guard_delete",
    "universe_guard_move",
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


def latest_commit_info() -> Dict[str, Any]:
    msg = run_cmd(["git", "log", "-1", "--pretty=%s"]).stdout.strip()
    name_status_lines = run_cmd(["git", "show", "--name-status", "--format=", "HEAD"]).stdout.splitlines()

    paths: List[str] = []
    name_status: List[Dict[str, str]] = []

    for line in name_status_lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            status = parts[0]
            path = parts[-1].replace("\\", "/")
            paths.append(path)
            name_status.append({"status": status, "path": path})

    return {
        "message": msg,
        "paths": sorted(paths),
        "name_status": name_status,
    }


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def tracked_python_files() -> List[str]:
    result = run_cmd(["git", "ls-files", "*.py"])
    return sorted([line.strip() for line in result.stdout.splitlines() if line.strip()])


def is_tracked(path: str) -> bool:
    return run_cmd(["git", "ls-files", "--error-unmatch", path]).returncode == 0


def sha256_file(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_record(rel_path: str) -> Dict[str, Any]:
    path = REPO_ROOT / rel_path
    exists = path.exists()
    record: Dict[str, Any] = {
        "path": rel_path,
        "exists": exists,
        "tracked": is_tracked(rel_path),
        "size_bytes": None,
        "sha256": None,
        "bom_detected": None,
        "syntax_ok": None,
        "syntax_error": None,
        "line_count": None,
    }

    if not exists:
        return record

    data = path.read_bytes()
    record["size_bytes"] = len(data)
    record["sha256"] = hashlib.sha256(data).hexdigest()
    record["bom_detected"] = data.startswith(b"\xef\xbb\xbf")
    text = data.decode("utf-8", errors="replace")
    record["line_count"] = len(text.splitlines())

    if rel_path.endswith(".py"):
        try:
            ast.parse(text, filename=rel_path)
            record["syntax_ok"] = True
        except Exception as exc:
            record["syntax_ok"] = False
            record["syntax_error"] = repr(exc)

    return record


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
            text = data.decode("utf-8")
            ast.parse(text, filename=rel)
        except Exception as exc:
            syntax_errors.append({"path": rel, "error": repr(exc)})

    return {
        "tracked_python_file_count": len(files),
        "syntax_error_count": len(syntax_errors),
        "syntax_errors": syntax_errors,
        "bom_error_count": len(bom_errors),
        "bom_errors": bom_errors,
        "pass": not syntax_errors and not bom_errors,
    }


def validate_json_states() -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []
    loaded: Dict[str, Dict[str, Any]] = {}

    paths = {
        "post_commit_status": POST_COMMIT_STATUS_JSON,
        "policy": POLICY_JSON,
        "invalid_metadata_inspector": INVALID_METADATA_INSPECTOR_JSON,
        "freeze_controller": FREEZE_CONTROLLER_JSON,
        "old_short_lock": OLD_SHORT_LOCK_JSON,
        "untracked_hygiene": UNTRACKED_HYGIENE_JSON,
        "commit_plan": COMMIT_PLAN_JSON,
        "commit_approval": COMMIT_APPROVAL_JSON,
    }

    for key, path in paths.items():
        try:
            loaded[key] = load_json(path)
        except Exception as exc:
            errors.append(f"{key} load failed: {path} error={repr(exc)}")

    if "policy" in loaded:
        counts = loaded["policy"].get("counts") if isinstance(loaded["policy"].get("counts"), dict) else {}
        if counts.get("p0_invalid_metadata_count") != 0:
            errors.append(f"policy p0_invalid_metadata_count not zero: {counts.get('p0_invalid_metadata_count')}")
        if counts.get("p0_old_short_locked_count") != 1:
            errors.append(f"policy p0_old_short_locked_count not one: {counts.get('p0_old_short_locked_count')}")
        if loaded["policy"].get("direct_apply_recommended_now") is not False:
            errors.append("policy direct_apply_recommended_now must be false")

    if "invalid_metadata_inspector" in loaded:
        if loaded["invalid_metadata_inspector"].get("inspector_status") != "INVALID_EXISTING_METADATA_BLOCK_INSPECTOR_V1_FALSE_POSITIVE_CONFIRMED":
            errors.append(f"invalid metadata inspector status unexpected: {loaded['invalid_metadata_inspector'].get('inspector_status')}")
        if loaded["invalid_metadata_inspector"].get("critical_issue_count") != 0:
            errors.append("invalid metadata inspector critical_issue_count not zero")

    if "freeze_controller" in loaded:
        if loaded["freeze_controller"].get("controller_status") != "STABILIZATION_FREEZE_ERROR_CLOSURE_CONTROLLER_V1_OPEN_ITEMS_REMAIN":
            errors.append(f"freeze controller status unexpected: {loaded['freeze_controller'].get('controller_status')}")
        safety = loaded["freeze_controller"].get("safety_flags") if isinstance(loaded["freeze_controller"].get("safety_flags"), dict) else {}
        if safety.get("os_development_allowed") is not False:
            errors.append("freeze controller os_development_allowed must be false")

    if "old_short_lock" in loaded:
        if loaded["old_short_lock"].get("lock_status") != "OLD_SHORT_GUARDED_APPLY_LOCK_REGISTRY_V1_LOCKED_DO_NOT_RUN_CONFIRMED":
            errors.append(f"old_short lock status unexpected: {loaded['old_short_lock'].get('lock_status')}")
        rec = loaded["old_short_lock"].get("old_short_lock_record") if isinstance(loaded["old_short_lock"].get("old_short_lock_record"), dict) else {}
        for key in [
            "execution_allowed",
            "stage_allowed_without_explicit_approval",
            "delete_allowed_without_explicit_approval",
            "move_allowed_without_explicit_approval",
            "gitignore_allowed_without_explicit_approval",
            "runtime_allowed",
            "launcher_allowed",
            "capital_allowed",
            "live_allowed",
            "real_orders_allowed",
        ]:
            if rec.get(key) is not False:
                errors.append(f"old_short lock record {key} must be false")

    if "untracked_hygiene" in loaded:
        if loaded["untracked_hygiene"].get("plan_status") != "UNTRACKED_HYGIENE_AND_UNIVERSE_GUARD_REVIEW_PLAN_V1_RECORDED_NO_ACTION":
            errors.append(f"untracked hygiene status unexpected: {loaded['untracked_hygiene'].get('plan_status')}")
        counts = loaded["untracked_hygiene"].get("counts") if isinstance(loaded["untracked_hygiene"].get("counts"), dict) else {}
        if counts.get("p1_closed_for_stabilization_count") != 2:
            errors.append(f"p1_closed_for_stabilization_count not 2: {counts.get('p1_closed_for_stabilization_count')}")

    if "commit_plan" in loaded:
        if loaded["commit_plan"].get("plan_status") != "UNTRACKED_STABILIZATION_TOOLING_COMMIT_PLAN_V1_READY_NO_STAGE":
            errors.append(f"commit plan status unexpected: {loaded['commit_plan'].get('plan_status')}")

    if "commit_approval" in loaded:
        if loaded["commit_approval"].get("approval_status") != "STABILIZATION_TOOLING_COMMIT_APPROVAL_V1_READY_FOR_EXACT_PATH_COMMIT":
            errors.append(f"commit approval status unexpected: {loaded['commit_approval'].get('approval_status')}")
        paths = set(loaded["commit_approval"].get("approved_commit_paths") or [])
        if paths != EXPECTED_LATEST_COMMIT_PATHS:
            errors.append(
                "commit approval approved paths mismatch: "
                f"missing={sorted(EXPECTED_LATEST_COMMIT_PATHS - paths)} "
                f"extra={sorted(paths - EXPECTED_LATEST_COMMIT_PATHS)}"
            )

    return {
        "json_state_pass": not errors,
        "errors": errors,
        "warnings": warnings,
        "loaded_keys": sorted(loaded.keys()),
    }


def validate_guard_tool_sources() -> Dict[str, Any]:
    errors: List[str] = []
    records: List[Dict[str, Any]] = []

    for rel in sorted(REQUIRED_TRACKED_GUARD_TOOLS):
        rec = file_record(rel)
        records.append(rec)
        if not rec["exists"]:
            errors.append(f"required guard tool missing: {rel}")
        if not rec["tracked"]:
            errors.append(f"required guard tool not tracked: {rel}")
        if rec["bom_detected"] is True:
            errors.append(f"required guard tool has BOM: {rel}")
        if rec["syntax_ok"] is not True:
            errors.append(f"required guard tool syntax failed: {rel} error={rec['syntax_error']}")

    triage_tool = REPO_ROOT / "tools/edge_factory_os_attention_triage_classifier_gate_review_refresh_after_metadata_v4.py"
    if triage_tool.exists():
        text = triage_tool.read_text(encoding="utf-8")
        required_snippets = [
            "def has_real_comment_gate_metadata_block(text: str) -> bool:",
            "metadata_present = has_real_comment_gate_metadata_block(text)",
        ]
        forbidden_snippets = [
            "def has_gate_metadata(text: str) -> bool:",
            "metadata_present = has_gate_metadata(text)",
        ]
        for snippet in required_snippets:
            if snippet not in text:
                errors.append(f"refined triage tool missing snippet: {snippet}")
        for snippet in forbidden_snippets:
            if snippet in text:
                errors.append(f"refined triage tool still contains old snippet: {snippet}")

    return {
        "guard_tool_source_pass": not errors,
        "errors": errors,
        "records": records,
    }


def validate_allowed_untracked(git_state: Dict[str, Any]) -> Dict[str, Any]:
    untracked = set(git_state["untracked_paths"])
    missing = sorted(EXPECTED_ALLOWED_UNTRACKED - untracked)
    extra = sorted(untracked - EXPECTED_ALLOWED_UNTRACKED)

    records = [file_record(path) for path in sorted(EXPECTED_ALLOWED_UNTRACKED)]

    decision_records: List[Dict[str, Any]] = []
    for rec in records:
        path = rec["path"]
        if path in {
            "tools/edge_factory_os_gate_metadata_patch_preview_v2.py",
            "tools/edge_factory_os_gate_metadata_patch_preview_v3.py",
        }:
            decision = "LEAVE_UNTRACKED_SUPERSEDED_PREVIEW_TOOL_NO_ACTION"
        elif path == "tools/edge_factory_os_old_short_guarded_runtime_reenable_apply_v1.py":
            decision = "LEAVE_UNTRACKED_LOCKED_DO_NOT_RUN"
        elif path == "tools/edge_factory_os_universe_coverage_guard_v1.py":
            decision = "LEAVE_UNTRACKED_UNIVERSE_GUARD_PENDING_EXPLICIT_STAGE_OR_DISCARD_APPROVAL"
        else:
            decision = "LEAVE_UNTRACKED_BACKUP_PENDING_EXPLICIT_CLEANUP_APPROVAL"

        decision_records.append({
            "path": path,
            "decision": decision,
            "stage_allowed_now": False,
            "delete_allowed_now": False,
            "move_allowed_now": False,
            "gitignore_allowed_now": False,
            "record": rec,
        })

    return {
        "allowed_untracked_pass": not missing and not extra,
        "expected_count": len(EXPECTED_ALLOWED_UNTRACKED),
        "actual_count": len(untracked),
        "missing_allowed_untracked": missing,
        "extra_untracked": extra,
        "decision_records": decision_records,
    }


def main() -> int:
    for key, value in SAFETY_FLAGS.items():
        if not isinstance(value, bool):
            raise SystemExit(f"safety flag is not boolean: {key}")

    git_state = get_git_state()
    commit_info = latest_commit_info()

    errors: List[str] = []
    warnings: List[str] = []

    if not git_state["head"].startswith(EXPECTED_HEAD_PREFIX):
        errors.append(f"unexpected HEAD: {git_state['head']} expected prefix {EXPECTED_HEAD_PREFIX}")

    if commit_info["message"] != EXPECTED_COMMIT_MESSAGE:
        errors.append(f"unexpected latest commit message: {commit_info['message']}")

    latest_paths = set(commit_info["paths"])
    if latest_paths != EXPECTED_LATEST_COMMIT_PATHS:
        errors.append(
            "latest commit path set mismatch: "
            f"missing={sorted(EXPECTED_LATEST_COMMIT_PATHS - latest_paths)} "
            f"extra={sorted(latest_paths - EXPECTED_LATEST_COMMIT_PATHS)}"
        )

    if git_state["dirty_tracked_count"] != 0:
        errors.append(f"tracked dirty files present: {git_state['dirty_tracked_paths']}")

    tracked_python_validation = validate_tracked_python()
    if not tracked_python_validation["pass"]:
        errors.append(
            "tracked python syntax/BOM validation failed: "
            f"syntax_errors={tracked_python_validation['syntax_errors'][:20]} "
            f"bom_errors={tracked_python_validation['bom_errors']}"
        )

    json_validation = validate_json_states()
    if not json_validation["json_state_pass"]:
        errors.extend([f"json_state: {err}" for err in json_validation["errors"]])
    warnings.extend([f"json_state: {warn}" for warn in json_validation["warnings"]])

    guard_tool_validation = validate_guard_tool_sources()
    if not guard_tool_validation["guard_tool_source_pass"]:
        errors.extend([f"guard_tool: {err}" for err in guard_tool_validation["errors"]])

    untracked_validation = validate_allowed_untracked(git_state)
    if not untracked_validation["allowed_untracked_pass"]:
        errors.append(
            "allowed untracked validation failed: "
            f"missing={untracked_validation['missing_allowed_untracked']} "
            f"extra={untracked_validation['extra_untracked']}"
        )

    audit_pass = not errors

    if audit_pass:
        audit_status = "FINAL_STABILIZATION_AUDIT_V1_PASS_FREEZE_STILL_ACTIVE"
        severity = "ATTENTION"
        final_decision = "STABILIZATION_FOUNDATION_CLEAN_BUT_OS_DEVELOPMENT_STILL_FROZEN_UNTIL_USER_APPROVES_RESUME"
        next_action = "ASK_USER_WHETHER_TO_HANDLE_SIX_LEFT_UNTRACKED_OR_RESUME_GOVERNANCE_ONLY_NEXT"
        next_module = None
        reason = "HEAD 9f43101 verified; tracked repo clean; p0 invalid metadata zero; old_short locked; p1 recorded; exactly 6 allowed untracked remain"
    else:
        audit_status = "FINAL_STABILIZATION_AUDIT_V1_FAIL"
        severity = "BLOCKED"
        final_decision = "KEEP_FREEZE_AND_FIX_AUDIT_FAILURES"
        next_action = "REVIEW_FINAL_STABILIZATION_AUDIT_FAILURES"
        next_module = None
        reason = "final stabilization audit errors detected"

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "audit_status": audit_status,
        "severity": severity,
        "allowed_scope": "READ_ONLY_FINAL_STABILIZATION_AUDIT",
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "reason": reason,
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "latest_commit": git_state["head"],
        "latest_commit_info": commit_info,
        "critical_issue_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "expected_latest_commit_path_count": len(EXPECTED_LATEST_COMMIT_PATHS),
            "actual_latest_commit_path_count": len(latest_paths),
            "tracked_dirty_count": git_state["dirty_tracked_count"],
            "tracked_python_file_count": tracked_python_validation["tracked_python_file_count"],
            "tracked_python_syntax_error_count": tracked_python_validation["syntax_error_count"],
            "tracked_python_bom_error_count": tracked_python_validation["bom_error_count"],
            "required_guard_tool_count": len(REQUIRED_TRACKED_GUARD_TOOLS),
            "allowed_untracked_expected_count": untracked_validation["expected_count"],
            "allowed_untracked_actual_count": untracked_validation["actual_count"],
            "extra_untracked_count": len(untracked_validation["extra_untracked"]),
            "missing_allowed_untracked_count": len(untracked_validation["missing_allowed_untracked"]),
            "direct_apply_recommended_now_count": 0,
            "apply_recommended_now_count": 0,
            "stage_recommended_now_count": 0,
            "commit_recommended_now_count": 0,
            "os_development_recommended_now_count": 0,
        },
        "tracked_python_validation": tracked_python_validation,
        "json_state_validation": json_validation,
        "guard_tool_validation": guard_tool_validation,
        "allowed_untracked_validation": untracked_validation,
        "expected_allowed_untracked": sorted(EXPECTED_ALLOWED_UNTRACKED),
        "expected_latest_commit_paths": sorted(EXPECTED_LATEST_COMMIT_PATHS),
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
        "stage_recommended_now": False,
        "commit_recommended_now": False,
        "os_development_recommended_now": False,
        "candidate_generation_recommended_now": False,
        "family_release_recommended_now": False,
        "runtime_action_recommended_now": False,
        "capital_action_recommended_now": False,
        "holdout_action_recommended_now": False,
        "target_files_modified": [],
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

    latest_json = OUT_DIR / "final_stabilization_audit_v1_latest.json"
    timestamped_json = OUT_DIR / f"final_stabilization_audit_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "final_stabilization_audit_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    txt_lines = [
        "EDGE FACTORY OS FINAL STABILIZATION AUDIT v1",
        "=" * 100,
        f"audit_status: {payload['audit_status']}",
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
        "COUNTS",
        "-" * 100,
        json.dumps(payload["counts"], indent=2, sort_keys=True),
        "",
        "ERRORS",
        "-" * 100,
        json.dumps(errors, indent=2, sort_keys=True),
        "",
        "WARNINGS",
        "-" * 100,
        json.dumps(warnings, indent=2, sort_keys=True),
        "",
        "ALLOWED UNTRACKED VALIDATION",
        "-" * 100,
        json.dumps(untracked_validation, indent=2, sort_keys=True),
        "",
        "TRACKED PYTHON VALIDATION",
        "-" * 100,
        json.dumps(tracked_python_validation, indent=2, sort_keys=True),
        "",
        "JSON STATE VALIDATION",
        "-" * 100,
        json.dumps(json_validation, indent=2, sort_keys=True),
        "",
        "GUARD TOOL VALIDATION",
        "-" * 100,
        json.dumps({
            "guard_tool_source_pass": guard_tool_validation["guard_tool_source_pass"],
            "errors": guard_tool_validation["errors"],
            "record_count": len(guard_tool_validation["records"]),
        }, indent=2, sort_keys=True),
        "",
        "SAFETY",
        "-" * 100,
        json.dumps(SAFETY_FLAGS, indent=2, sort_keys=True),
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