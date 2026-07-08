from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_final_stabilization_audit_v2"
OUT_DIR = LAB_ROOT / "edge_factory_os_final_stabilization_audit_v2"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "c60ad88"
EXPECTED_HEAD_MESSAGE = "Add final stabilization audit"

EXPECTED_PREVIOUS_STABILIZATION_COMMIT_PREFIX = "9f43101"
EXPECTED_PREVIOUS_STABILIZATION_MESSAGE = "Record stabilization freeze and recurrence guard tooling"

EXPECTED_ALLOWED_UNTRACKED: Set[str] = {
    "tools/edge_factory_os_gate_metadata_patch_preview_v2.py",
    "tools/edge_factory_os_gate_metadata_patch_preview_v3.py",
    "tools/edge_factory_os_joint_null_distribution_validator_v1.py.readonly_fix_bak_20260514_022123",
    "tools/edge_factory_os_old_short_guarded_runtime_reenable_apply_v1.py",
    "tools/edge_factory_os_source_panel_anomaly_discovery_runner_v1.py.blocked_patch_bak_20260514_000647",
    "tools/edge_factory_os_universe_coverage_guard_v1.py",
}

REQUIRED_TRACKED_TOOLS: Set[str] = {
    "tools/edge_factory_os_final_stabilization_audit_v1.py",
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
    "tools/edge_factory_os_full_system_read_only_audit_refresh_after_gate_metadata_v4.py",
    "tools/edge_factory_os_gate_metadata_patch_apply_v4.py",
    "tools/edge_factory_os_gate_metadata_patch_approval_v4.py",
    "tools/edge_factory_os_gate_metadata_patch_preview_v4.py",
}

POLICY_JSON = LAB_ROOT / "edge_factory_os_attention_issue_policy_classifier_after_gate_metadata_v4" / "attention_issue_policy_classifier_after_metadata_v4_latest.json"
INVALID_METADATA_JSON = LAB_ROOT / "edge_factory_os_invalid_existing_metadata_block_inspector_v1" / "invalid_existing_metadata_block_inspector_v1_latest.json"
OLD_SHORT_LOCK_JSON = LAB_ROOT / "edge_factory_os_old_short_guarded_apply_lock_registry_v1" / "old_short_guarded_apply_lock_registry_v1_latest.json"
UNTRACKED_HYGIENE_JSON = LAB_ROOT / "edge_factory_os_untracked_hygiene_and_universe_guard_review_plan_v1" / "untracked_hygiene_and_universe_guard_review_plan_v1_latest.json"

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


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def get_git_state() -> Dict[str, Any]:
    status = run_cmd(["git", "status", "--porcelain=v1"]).stdout.splitlines()
    status_lines = [x for x in status if x.strip()]
    untracked = [x[3:] for x in status_lines if x.startswith("?? ")]
    dirty_tracked = [x for x in status_lines if not x.startswith("?? ")]
    return {
        "head": run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
        "branch": run_cmd(["git", "branch", "--show-current"]).stdout.strip(),
        "git_dirty": bool(status_lines),
        "dirty_tracked_count": len(dirty_tracked),
        "dirty_tracked_paths": [x[3:] if len(x) > 3 else x for x in dirty_tracked],
        "untracked_count": len(untracked),
        "untracked_paths": untracked,
        "status_porcelain": status_lines,
        "remote_status_short": run_cmd(["git", "status", "-sb"]).stdout.splitlines(),
    }


def commit_subject(ref: str) -> str:
    return run_cmd(["git", "log", "-1", "--pretty=%s", ref]).stdout.strip()


def commit_paths(ref: str) -> List[str]:
    out = run_cmd(["git", "show", "--name-only", "--format=", ref]).stdout.splitlines()
    return sorted([x.strip().replace("\\", "/") for x in out if x.strip()])


def tracked_python_files() -> List[str]:
    out = run_cmd(["git", "ls-files", "*.py"]).stdout.splitlines()
    return sorted([x.strip() for x in out if x.strip()])


def is_tracked(rel: str) -> bool:
    return run_cmd(["git", "ls-files", "--error-unmatch", rel]).returncode == 0


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_python(rel: str) -> Dict[str, Any]:
    path = REPO_ROOT / rel
    data = path.read_bytes()
    result = {
        "path": rel,
        "exists": path.exists(),
        "tracked": is_tracked(rel),
        "bom_detected": data.startswith(b"\xef\xbb\xbf"),
        "syntax_ok": True,
        "syntax_error": None,
    }
    try:
        ast.parse(data.decode("utf-8"), filename=rel)
    except Exception as exc:
        result["syntax_ok"] = False
        result["syntax_error"] = repr(exc)
    return result


def main() -> int:
    errors: List[str] = []
    warnings: List[str] = []

    for k, v in SAFETY_FLAGS.items():
        if not isinstance(v, bool):
            errors.append(f"safety_flags[{k}] is not boolean")

    git_state = get_git_state()

    if not git_state["head"].startswith(EXPECTED_HEAD_PREFIX):
        errors.append(f"unexpected HEAD: {git_state['head']} expected {EXPECTED_HEAD_PREFIX}")

    if commit_subject("HEAD") != EXPECTED_HEAD_MESSAGE:
        errors.append(f"unexpected HEAD commit message: {commit_subject('HEAD')}")

    prev_ref = "HEAD~1"
    prev_short = run_cmd(["git", "rev-parse", "--short", prev_ref]).stdout.strip()
    if not prev_short.startswith(EXPECTED_PREVIOUS_STABILIZATION_COMMIT_PREFIX):
        errors.append(f"unexpected previous commit: {prev_short} expected {EXPECTED_PREVIOUS_STABILIZATION_COMMIT_PREFIX}")

    if commit_subject(prev_ref) != EXPECTED_PREVIOUS_STABILIZATION_MESSAGE:
        errors.append(f"unexpected previous commit message: {commit_subject(prev_ref)}")

    head_paths = set(commit_paths("HEAD"))
    if head_paths != {"tools/edge_factory_os_final_stabilization_audit_v1.py"}:
        errors.append(f"HEAD should contain only final audit v1 path, got {sorted(head_paths)}")

    if git_state["dirty_tracked_count"] != 0:
        errors.append(f"tracked dirty paths present: {git_state['dirty_tracked_paths']}")

    untracked = set(git_state["untracked_paths"])
    if untracked != EXPECTED_ALLOWED_UNTRACKED:
        errors.append(
            "untracked set mismatch: "
            f"missing={sorted(EXPECTED_ALLOWED_UNTRACKED - untracked)} "
            f"extra={sorted(untracked - EXPECTED_ALLOWED_UNTRACKED)}"
        )

    tracked_validation = [validate_python(rel) for rel in tracked_python_files()]
    syntax_errors = [r for r in tracked_validation if not r["syntax_ok"]]
    bom_errors = [r for r in tracked_validation if r["bom_detected"]]

    if syntax_errors:
        errors.append(f"tracked Python syntax errors found: {syntax_errors[:20]}")
    if bom_errors:
        errors.append(f"tracked Python BOM errors found: {[r['path'] for r in bom_errors]}")

    required_tool_records = [validate_python(rel) for rel in sorted(REQUIRED_TRACKED_TOOLS)]
    missing_required = [r["path"] for r in required_tool_records if not r["exists"] or not r["tracked"]]
    bad_required = [r for r in required_tool_records if r["bom_detected"] or not r["syntax_ok"]]

    if missing_required:
        errors.append(f"required tracked guard tools missing/not tracked: {missing_required}")
    if bad_required:
        errors.append(f"required tracked guard tools invalid: {bad_required}")

    json_checks: Dict[str, Any] = {}
    try:
        policy = load_json(POLICY_JSON)
        policy_counts = policy.get("counts") if isinstance(policy.get("counts"), dict) else {}
        json_checks["policy_counts"] = policy_counts
        if policy_counts.get("p0_invalid_metadata_count") != 0:
            errors.append(f"policy p0_invalid_metadata_count not 0: {policy_counts.get('p0_invalid_metadata_count')}")
        if policy_counts.get("p0_old_short_locked_count") != 1:
            errors.append(f"policy p0_old_short_locked_count not 1: {policy_counts.get('p0_old_short_locked_count')}")
        if policy.get("direct_apply_recommended_now") is not False:
            errors.append("policy direct_apply_recommended_now must be false")
    except Exception as exc:
        errors.append(f"policy json check failed: {repr(exc)}")

    try:
        invalid = load_json(INVALID_METADATA_JSON)
        json_checks["invalid_metadata_status"] = invalid.get("inspector_status")
        if invalid.get("inspector_status") != "INVALID_EXISTING_METADATA_BLOCK_INSPECTOR_V1_FALSE_POSITIVE_CONFIRMED":
            errors.append(f"invalid metadata inspector status unexpected: {invalid.get('inspector_status')}")
        if invalid.get("critical_issue_count") != 0:
            errors.append("invalid metadata critical_issue_count not 0")
    except Exception as exc:
        errors.append(f"invalid metadata json check failed: {repr(exc)}")

    try:
        old_short = load_json(OLD_SHORT_LOCK_JSON)
        json_checks["old_short_lock_status"] = old_short.get("lock_status")
        if old_short.get("lock_status") != "OLD_SHORT_GUARDED_APPLY_LOCK_REGISTRY_V1_LOCKED_DO_NOT_RUN_CONFIRMED":
            errors.append(f"old_short lock status unexpected: {old_short.get('lock_status')}")
    except Exception as exc:
        errors.append(f"old_short lock json check failed: {repr(exc)}")

    try:
        hygiene = load_json(UNTRACKED_HYGIENE_JSON)
        json_checks["untracked_hygiene_status"] = hygiene.get("plan_status")
        if hygiene.get("plan_status") != "UNTRACKED_HYGIENE_AND_UNIVERSE_GUARD_REVIEW_PLAN_V1_RECORDED_NO_ACTION":
            errors.append(f"untracked hygiene status unexpected: {hygiene.get('plan_status')}")
        counts = hygiene.get("counts") if isinstance(hygiene.get("counts"), dict) else {}
        if counts.get("p1_closed_for_stabilization_count") != 2:
            errors.append(f"p1_closed_for_stabilization_count not 2: {counts.get('p1_closed_for_stabilization_count')}")
    except Exception as exc:
        errors.append(f"untracked hygiene json check failed: {repr(exc)}")

    audit_pass = not errors

    payload = {
        "module": MODULE_NAME,
        "audit_status": "FINAL_STABILIZATION_AUDIT_V2_PASS" if audit_pass else "FINAL_STABILIZATION_AUDIT_V2_FAIL",
        "severity": "ATTENTION" if audit_pass else "BLOCKED",
        "allowed_scope": "READ_ONLY_FINAL_STABILIZATION_AUDIT",
        "final_decision": (
            "STABILIZATION_CLOSED_FREEZE_CAN_BE_LIFTED_ONLY_AFTER_USER_APPROVAL"
            if audit_pass
            else "KEEP_FREEZE_AND_FIX_AUDIT_FAILURES"
        ),
        "next_action": (
            "ASK_USER_TO_APPROVE_RESUMING_OS_DEVELOPMENT_OR_HANDLE_SIX_LEFT_UNTRACKED"
            if audit_pass
            else "REVIEW_FINAL_STABILIZATION_AUDIT_V2_FAILURES"
        ),
        "next_module": None,
        "reason": (
            "HEAD c60ad88 verified, tracked repo clean, syntax/BOM clean, p0 invalid metadata 0, old_short locked, p1 recorded, exactly 6 allowed untracked remain"
            if audit_pass
            else "final stabilization audit v2 errors detected"
        ),
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "latest_commit": git_state["head"],
        "critical_issue_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "tracked_dirty_count": git_state["dirty_tracked_count"],
            "allowed_untracked_count": git_state["untracked_count"],
            "tracked_python_file_count": len(tracked_validation),
            "tracked_python_syntax_error_count": len(syntax_errors),
            "tracked_python_bom_error_count": len(bom_errors),
            "required_tracked_guard_tool_count": len(REQUIRED_TRACKED_TOOLS),
            "missing_required_tracked_guard_tool_count": len(missing_required),
            "bad_required_tracked_guard_tool_count": len(bad_required),
            "direct_apply_recommended_now_count": 0,
            "apply_recommended_now_count": 0,
            "os_development_recommended_now_count": 0,
        },
        "json_checks": json_checks,
        "expected_allowed_untracked": sorted(EXPECTED_ALLOWED_UNTRACKED),
        "actual_untracked": sorted(untracked),
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
        "stage_recommended_now": False,
        "commit_recommended_now": False,
        "os_development_recommended_now": False,
        "runtime_action_recommended_now": False,
        "capital_action_recommended_now": False,
        "holdout_action_recommended_now": False,
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

    latest_json = OUT_DIR / "final_stabilization_audit_v2_latest.json"
    timestamped_json = OUT_DIR / f"final_stabilization_audit_v2_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "final_stabilization_audit_v2_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    txt = [
        "EDGE FACTORY OS FINAL STABILIZATION AUDIT v2",
        "=" * 100,
        f"audit_status: {payload['audit_status']}",
        f"severity: {payload['severity']}",
        f"allowed_scope: {payload['allowed_scope']}",
        f"final_decision: {payload['final_decision']}",
        f"next_action: {payload['next_action']}",
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
        "JSON CHECKS",
        "-" * 100,
        json.dumps(json_checks, indent=2, sort_keys=True),
        "",
        "EXPECTED ALLOWED UNTRACKED",
        "-" * 100,
        json.dumps(sorted(EXPECTED_ALLOWED_UNTRACKED), indent=2, sort_keys=True),
        "",
        "ACTUAL UNTRACKED",
        "-" * 100,
        json.dumps(sorted(untracked), indent=2, sort_keys=True),
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

    latest_txt.write_text("\n".join(txt) + "\n", encoding="utf-8")
    print("\n".join(txt))

    return 0 if audit_pass else 3


if __name__ == "__main__":
    raise SystemExit(main())