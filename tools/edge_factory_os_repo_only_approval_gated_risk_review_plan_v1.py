from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_approval_gated_risk_review_plan_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_repo_only_approval_gated_risk_review_plan_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "f6f99bb"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_approval_gated_risk_review_plan_v1.py"

RISKY_JSON = LAB_ROOT / "edge_factory_os_repo_only_risky_surface_review_v1" / "repo_only_risky_surface_review_v1_latest.json"
RISKY_POST_CHECK_JSON = LAB_ROOT / "edge_factory_os_repo_only_risky_surface_review_post_commit_check" / "repo_only_risky_surface_review_post_commit_check_latest.json"
DEPENDENCY_JSON = LAB_ROOT / "edge_factory_os_repo_only_dependency_surface_refresh_v1" / "repo_only_dependency_surface_refresh_v1_latest.json"
MODULE_INDEX_JSON = LAB_ROOT / "edge_factory_os_repo_only_module_index_refresh_v1" / "repo_only_module_index_refresh_v1_latest.json"
GOVERNOR_JSON = LAB_ROOT / "edge_factory_os_post_resume_zero_error_governor_panel_v1" / "post_resume_zero_error_governor_panel_v1_latest.json"

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_approval_gated_risk_review_plan": True,
    "read_only_plan_only": True,
    "approval_required_before_any_review_action": True,
    "risky_surface_review_required": True,
    "dependency_surface_required": True,
    "module_index_required": True,
    "governor_panel_required": True,

    "repo_only_governance_allowed": True,
    "repo_only_audit_allowed": True,
    "repo_only_status_refresh_allowed": True,
    "repo_only_contract_preview_allowed": True,
    "read_only_validation_allowed": True,

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
    "risk_file_edit_allowed_now": False,
    "risk_file_execution_allowed_now": False,
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
    "old_short_guarded_apply_execution",
    "risk_file_edit_without_approval",
    "risk_file_execution_without_approval",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def get_git_state() -> Dict[str, Any]:
    status_lines = [x for x in run_cmd(["git", "status", "--porcelain=v1"]).stdout.splitlines() if x.strip()]
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
        "remote_status_short": run_cmd(["git", "status", "-sb"]).stdout.splitlines(),
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
        "risky_surface_status",
        "audit_status",
        "dependency_surface_status",
        "module_index_status",
        "governor_status",
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
        errors.append(
            f"{key} next_module mismatch: expected={expected_next_module} actual={record.get('next_module')}"
        )


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
        errors.append(f"dirty tracked paths present: {git_state['dirty_tracked_paths']}")

    if not current_step_untracked_ok:
        errors.append(
            "unexpected untracked set: "
            f"expected={sorted(expected_untracked)} actual={sorted(actual_untracked)}"
        )

    head_subject = commit_subject("HEAD")
    checks["head_commit_subject"] = head_subject
    if head_subject != "Add repo-only risky surface review":
        errors.append(f"unexpected HEAD commit subject: {head_subject}")

    inputs = {
        "risky_surface": (RISKY_JSON, "REPO_ONLY_OS_RISKY_SURFACE_REVIEW_V1_READY", "edge_factory_os_repo_only_approval_gated_risk_review_plan_v1.py"),
        "risky_surface_post_check": (RISKY_POST_CHECK_JSON, "REPO_ONLY_RISKY_SURFACE_REVIEW_POST_COMMIT_CHECK_PASS", "edge_factory_os_repo_only_approval_gated_risk_review_plan_v1.py"),
        "dependency_surface": (DEPENDENCY_JSON, "REPO_ONLY_OS_DEPENDENCY_SURFACE_REFRESH_V1_READY", None),
        "module_index": (MODULE_INDEX_JSON, "REPO_ONLY_OS_MODULE_INDEX_REFRESH_V1_READY", None),
        "governor": (GOVERNOR_JSON, "POST_RESUME_ZERO_ERROR_GOVERNOR_PANEL_V1_READY", None),
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


def build_plan(loaded: Dict[str, Dict[str, Any]], clean_baseline: bool) -> Dict[str, Any]:
    risky_payload = loaded.get("risky_surface", {})
    risky_review = risky_payload.get("risky_surface_review", {})
    summary = risky_review.get("review_summary", {})

    top_records = summary.get("top_risky_records", [])
    if not isinstance(top_records, list):
        top_records = []

    plan_items = []
    for idx, record in enumerate(top_records[:30], start=1):
        if not isinstance(record, dict):
            continue
        plan_items.append(
            {
                "rank": idx,
                "path": record.get("path"),
                "risk_score": record.get("risk_score"),
                "risk_categories": record.get("risk_categories", []),
                "review_action": "MANUAL_REVIEW_ONLY_AFTER_EXPLICIT_APPROVAL",
                "edit_allowed": False,
                "execute_allowed": False,
                "direct_fix_allowed": False,
                "required_approval_scope": "REPO_ONLY_RISK_REVIEW_APPROVAL_NO_PATCH_NO_EXECUTION",
            }
        )

    return {
        "approval_gated_plan_status": "APPROVAL_GATED_RISK_REVIEW_PLAN_ACTIVE" if clean_baseline else "APPROVAL_GATED_RISK_REVIEW_PLAN_BLOCKED",
        "plan_scope": "REPO_ONLY_GOVERNANCE_PLANNING",
        "source_risky_summary": {
            "risky_record_count": summary.get("risky_record_count"),
            "high_risk_count": summary.get("high_risk_count"),
            "medium_risk_count": summary.get("medium_risk_count"),
            "low_risk_count": summary.get("low_risk_count"),
            "risk_category_counts": summary.get("risk_category_counts"),
            "high_risk_import_counts": summary.get("high_risk_import_counts"),
        },
        "approval_model": {
            "approval_required_before_manual_file_review": True,
            "approval_required_before_any_patch": True,
            "approval_required_before_any_execution": True,
            "current_approval_present": False,
            "current_approval_valid": False,
            "manual_review_allowed_now": False,
            "patch_allowed_now": False,
            "execution_allowed_now": False,
            "runtime_touch_allowed_now": False,
        },
        "plan_items": plan_items,
        "plan_item_count": len(plan_items),
        "global_rules": [
            "No file edits from this plan.",
            "No runtime execution from this plan.",
            "No launcher execution from this plan.",
            "No capital/live/real-order action.",
            "No candidate/family/strategy research action.",
            "Only build an approval record module next.",
        ],
        "required_next_approval_module": {
            "module": "edge_factory_os_repo_only_risk_review_manual_approval_record_v1.py",
            "approval_scope": "REPO_ONLY_RISK_REVIEW_APPROVAL_NO_PATCH_NO_EXECUTION",
            "approval_must_not_authorize": [
                "runtime_touch",
                "launcher_execution",
                "capital_change",
                "live_trading",
                "real_orders",
                "holdout_access",
                "strategy_research",
                "candidate_generation",
                "candidate_release",
                "family_release",
                "patch_apply",
                "direct_fix",
            ],
        },
        "invariants": {
            "plan_items_are_review_only": all(
                item["review_action"] == "MANUAL_REVIEW_ONLY_AFTER_EXPLICIT_APPROVAL"
                and item["edit_allowed"] is False
                and item["execute_allowed"] is False
                and item["direct_fix_allowed"] is False
                for item in plan_items
            ),
            "current_approval_absent": True,
            "no_patch_or_execution_authorized": True,
        },
        "recommended_next_step": {
            "step": "BUILD_REPO_ONLY_RISK_REVIEW_MANUAL_APPROVAL_RECORD",
            "module": "edge_factory_os_repo_only_risk_review_manual_approval_record_v1.py",
            "scope": "REPO_ONLY_GOVERNANCE_APPROVAL_RECORD",
            "reason": "Approval-gated plan exists; next safe step is to record/deny explicit approval, not review or patch files.",
        },
    }


def main() -> int:
    safety_errors = [
        key for key, value in SAFETY_FLAGS.items()
        if not isinstance(value, bool)
    ]

    validation = validate_inputs()
    errors = list(validation["errors"])

    if safety_errors:
        errors.append(f"safety flags are not boolean: {safety_errors}")

    plan = build_plan(validation["loaded"], bool(validation["clean_baseline"]) and not safety_errors)

    if validation["pass"] and plan["approval_gated_plan_status"] != "APPROVAL_GATED_RISK_REVIEW_PLAN_ACTIVE":
        errors.append(f"approval-gated plan did not become active: {plan['approval_gated_plan_status']}")

    invariants = plan["invariants"]
    if not invariants["plan_items_are_review_only"]:
        errors.append("plan items are not all review-only")
    if not invariants["current_approval_absent"]:
        errors.append("current approval is not absent")
    if not invariants["no_patch_or_execution_authorized"]:
        errors.append("patch/execution authorized unexpectedly")

    passed = not errors

    payload = {
        "module": MODULE_NAME,
        "approval_plan_status": (
            "REPO_ONLY_APPROVAL_GATED_RISK_REVIEW_PLAN_V1_READY"
            if passed
            else "REPO_ONLY_APPROVAL_GATED_RISK_REVIEW_PLAN_V1_BLOCKED"
        ),
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_GOVERNANCE_PLANNING",
        "final_decision": (
            "APPROVAL_GATED_RISK_REVIEW_PLAN_READY_FOR_MANUAL_APPROVAL_RECORD"
            if passed
            else "KEEP_FREEZE_REVIEW_APPROVAL_GATED_PLAN_ERRORS"
        ),
        "next_action": (
            "BUILD_REPO_ONLY_RISK_REVIEW_MANUAL_APPROVAL_RECORD_V1"
            if passed
            else "REVIEW_APPROVAL_GATED_PLAN_ERRORS"
        ),
        "next_module": (
            "edge_factory_os_repo_only_risk_review_manual_approval_record_v1.py"
            if passed
            else None
        ),
        "reason": (
            "Built an approval-gated repo-only risk review plan with no direct review, patch, or execution authorization."
            if passed
            else "Approval-gated risk review plan validation failed."
        ),
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
            "current_step_untracked_ok": validation["current_step_untracked_ok"],
            "expected_untracked_during_run": validation["expected_untracked_during_run"],
            "actual_untracked_during_run": validation["actual_untracked_during_run"],
            "source_statuses": validation["source_statuses"],
            "clean_baseline": validation["clean_baseline"],
        },
        "approval_gated_risk_review_plan": plan,
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
        "stage_recommended_now": False,
        "commit_recommended_now": False,
        "runtime_action_recommended_now": False,
        "capital_action_recommended_now": False,
        "holdout_action_recommended_now": False,
        "strategy_research_recommended_now": False,
        "candidate_generation_recommended_now": False,
        "candidate_release_recommended_now": False,
        "family_release_recommended_now": False,
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

    latest_json = OUT_DIR / "repo_only_approval_gated_risk_review_plan_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_approval_gated_risk_review_plan_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "repo_only_approval_gated_risk_review_plan_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY APPROVAL-GATED RISK REVIEW PLAN v1",
        "=" * 100,
        f"approval_plan_status: {payload['approval_plan_status']}",
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
        "APPROVAL MODEL",
        "-" * 100,
        json.dumps(plan["approval_model"], indent=2, sort_keys=True),
        "",
        "PLAN SUMMARY",
        "-" * 100,
        json.dumps(
            {
                "plan_item_count": plan["plan_item_count"],
                "source_risky_summary": plan["source_risky_summary"],
                "required_next_approval_module": plan["required_next_approval_module"],
                "invariants": plan["invariants"],
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