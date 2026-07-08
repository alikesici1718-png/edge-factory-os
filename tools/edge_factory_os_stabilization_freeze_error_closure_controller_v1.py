from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_stabilization_freeze_error_closure_controller_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_stabilization_freeze_error_closure_controller_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "578879b"

POST_COMMIT_JSON = (
    LAB_ROOT
    / "edge_factory_os_post_commit_read_only_status_after_gate_metadata_v4"
    / "post_commit_read_only_status_after_gate_metadata_v4_latest.json"
)

TRIAGE_REFRESH_JSON = (
    LAB_ROOT
    / "edge_factory_os_attention_triage_classifier_gate_review_refresh_after_metadata_v4"
    / "attention_triage_classifier_gate_review_refresh_after_metadata_v4_latest.json"
)

POLICY_CLASSIFIER_JSON = (
    LAB_ROOT
    / "edge_factory_os_attention_issue_policy_classifier_after_gate_metadata_v4"
    / "attention_issue_policy_classifier_after_metadata_v4_latest.json"
)

INVALID_METADATA_INSPECTOR_JSON = (
    LAB_ROOT
    / "edge_factory_os_invalid_existing_metadata_block_inspector_v1"
    / "invalid_existing_metadata_block_inspector_v1_latest.json"
)

KNOWN_ALLOWED_UNTRACKED: Set[str] = {
    "tools/edge_factory_os_attention_issue_policy_classifier_after_gate_metadata_v4.py",
    "tools/edge_factory_os_attention_triage_classifier_gate_review_refresh_after_metadata_v4.py",
    "tools/edge_factory_os_gate_metadata_patch_preview_v2.py",
    "tools/edge_factory_os_gate_metadata_patch_preview_v3.py",
    "tools/edge_factory_os_invalid_existing_metadata_block_inspector_v1.py",
    "tools/edge_factory_os_joint_null_distribution_validator_v1.py.readonly_fix_bak_20260514_022123",
    "tools/edge_factory_os_old_short_guarded_runtime_reenable_apply_v1.py",
    "tools/edge_factory_os_post_commit_read_only_status_after_gate_metadata_v4.py",
    "tools/edge_factory_os_source_panel_anomaly_discovery_runner_v1.py.blocked_patch_bak_20260514_000647",
    "tools/edge_factory_os_universe_coverage_guard_v1.py",
    "tools/edge_factory_os_stabilization_freeze_error_closure_controller_v1.py",
}

SAFETY_FLAGS: Dict[str, bool] = {
    "stabilization_freeze_active": True,
    "os_development_allowed": False,
    "read_only_controller": True,
    "apply_performed_now": False,
    "commit_performed_now": False,
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
    "old_short_guarded_apply_allowed": False,
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


def fail_closed(reason: str, extra: Optional[Dict[str, Any]] = None) -> int:
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "controller_status": "STABILIZATION_FREEZE_ERROR_CLOSURE_CONTROLLER_V1_FAIL_CLOSED",
        "severity": "BLOCKED",
        "allowed_scope": "READ_ONLY_STABILIZATION_CONTROLLER",
        "final_decision": "STOP_NO_OS_DEVELOPMENT_NO_APPLY",
        "next_action": "REVIEW_CONTROLLER_INPUT_FAILURE",
        "next_module": None,
        "reason": reason,
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
        "os_development_recommended_now": False,
        "runtime_touched": False,
        "launcher_executed": False,
        "capital_changed": False,
        "live_or_real_orders": False,
        "holdout_accessed": False,
        "backup_deleted_or_moved": False,
        "gitignore_changed": False,
        "git_add_force_used": False,
    }
    if extra:
        payload.update(extra)

    out = OUT_DIR / "stabilization_freeze_error_closure_controller_v1_fail_closed_latest.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS STABILIZATION FREEZE + ERROR CLOSURE CONTROLLER v1")
    print("=" * 100)
    print("controller_status: STABILIZATION_FREEZE_ERROR_CLOSURE_CONTROLLER_V1_FAIL_CLOSED")
    print(f"reason: {reason}")
    print(f"output: {out}")
    return 2


def validate_inputs(git_state: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    if not git_state["head"].startswith(EXPECTED_HEAD_PREFIX):
        errors.append(f"unexpected HEAD: {git_state['head']} expected prefix {EXPECTED_HEAD_PREFIX}")

    if git_state["dirty_tracked_count"] != 0:
        errors.append(f"tracked files dirty: {git_state['dirty_tracked_paths']}")

    untracked = set(git_state["untracked_paths"])
    unknown_untracked = sorted(untracked - KNOWN_ALLOWED_UNTRACKED)
    if unknown_untracked:
        errors.append(f"unknown untracked paths present: {unknown_untracked}")

    missing_known = sorted(KNOWN_ALLOWED_UNTRACKED - untracked)
    if missing_known:
        warnings.append(f"known untracked paths absent; okay if cleaned later: {missing_known}")

    loaded: Dict[str, Dict[str, Any]] = {}
    input_paths = {
        "post_commit": POST_COMMIT_JSON,
        "triage_refresh": TRIAGE_REFRESH_JSON,
        "policy_classifier": POLICY_CLASSIFIER_JSON,
        "invalid_metadata_inspector": INVALID_METADATA_INSPECTOR_JSON,
    }

    for key, path in input_paths.items():
        try:
            loaded[key] = load_json(path)
        except Exception as exc:
            errors.append(f"cannot load {key}: {path} error={repr(exc)}")

    if "post_commit" in loaded:
        if loaded["post_commit"].get("status") != "POST_COMMIT_READ_ONLY_STATUS_AFTER_GATE_METADATA_V4_PASS":
            errors.append(f"post_commit status not pass: {loaded['post_commit'].get('status')}")
        if loaded["post_commit"].get("critical_issue_count") != 0:
            errors.append("post_commit critical_issue_count is not 0")

    if "triage_refresh" in loaded:
        if loaded["triage_refresh"].get("refresh_status") != "ATTENTION_TRIAGE_CLASSIFIER_GATE_REVIEW_REFRESH_AFTER_METADATA_V4_READY_NO_APPLY":
            errors.append(f"triage refresh status unexpected: {loaded['triage_refresh'].get('refresh_status')}")
        if loaded["triage_refresh"].get("critical_issue_count") != 0:
            errors.append("triage refresh critical_issue_count is not 0")
        if loaded["triage_refresh"].get("direct_apply_recommended_now") is not False:
            errors.append("triage refresh direct_apply_recommended_now must be false")

    if "policy_classifier" in loaded:
        if loaded["policy_classifier"].get("classifier_status") != "ATTENTION_ISSUE_POLICY_CLASSIFIER_AFTER_METADATA_V4_READY":
            errors.append(f"policy classifier status unexpected: {loaded['policy_classifier'].get('classifier_status')}")
        if loaded["policy_classifier"].get("direct_apply_recommended_now") is not False:
            errors.append("policy classifier direct_apply_recommended_now must be false")

    if "invalid_metadata_inspector" in loaded:
        if loaded["invalid_metadata_inspector"].get("inspector_status") != "INVALID_EXISTING_METADATA_BLOCK_INSPECTOR_V1_FALSE_POSITIVE_CONFIRMED":
            errors.append(f"invalid metadata inspector status unexpected: {loaded['invalid_metadata_inspector'].get('inspector_status')}")
        if loaded["invalid_metadata_inspector"].get("critical_issue_count") != 0:
            errors.append("invalid metadata inspector critical_issue_count is not 0")

    return {
        "errors": errors,
        "warnings": warnings,
        "loaded": loaded,
    }


def make_closure_ledger(loaded: Dict[str, Dict[str, Any]], git_state: Dict[str, Any]) -> List[Dict[str, Any]]:
    policy = loaded.get("policy_classifier", {})
    invalid = loaded.get("invalid_metadata_inspector", {})
    triage = loaded.get("triage_refresh", {})

    counts = policy.get("counts") if isinstance(policy.get("counts"), dict) else {}
    triage_counts = triage.get("counts") if isinstance(triage.get("counts"), dict) else {}

    return [
        {
            "id": "P0_INVALID_METADATA_FALSE_POSITIVE",
            "status": "CLOSED_FALSE_POSITIVE",
            "severity": "INFO",
            "evidence": {
                "inspector_status": invalid.get("inspector_status"),
                "false_positive_count": (invalid.get("counts") or {}).get("false_positive_count"),
                "real_error_count": (invalid.get("counts") or {}).get("real_error_count"),
                "critical_issue_count": invalid.get("critical_issue_count"),
            },
            "remaining_action": "Refine classifier rule so metadata marker strings inside Python string literals are not treated as real metadata blocks.",
            "apply_required": False,
            "runtime_required": False,
        },
        {
            "id": "P0_OLD_SHORT_GUARDED_APPLY_LOCKED",
            "status": "OPEN_LOCKED_DO_NOT_RUN",
            "severity": "ATTENTION",
            "evidence": {
                "p0_old_short_locked_count": counts.get("p0_old_short_locked_count"),
                "path": "tools/edge_factory_os_old_short_guarded_runtime_reenable_apply_v1.py",
            },
            "remaining_action": "Keep locked. Do not run. Later decide whether to archive/commit/delete only through explicit approval chain.",
            "apply_required": False,
            "runtime_required": False,
        },
        {
            "id": "P1_BACKUP_HYGIENE",
            "status": "OPEN_PLAN_ONLY_NO_DELETE_MOVE",
            "severity": "ATTENTION",
            "evidence": {
                "p1_backup_hygiene_count": counts.get("p1_backup_hygiene_count"),
                "paths": [
                    "tools/edge_factory_os_joint_null_distribution_validator_v1.py.readonly_fix_bak_20260514_022123",
                    "tools/edge_factory_os_source_panel_anomaly_discovery_runner_v1.py.blocked_patch_bak_20260514_000647",
                ],
            },
            "remaining_action": "Create no-delete/no-move hygiene review plan. No cleanup action until explicit approval.",
            "apply_required": False,
            "runtime_required": False,
        },
        {
            "id": "P1_UNIVERSE_GUARD_REVIEW",
            "status": "OPEN_REVIEW_REQUIRED_NO_ACTION",
            "severity": "ATTENTION",
            "evidence": {
                "p1_universe_guard_count": counts.get("p1_universe_guard_count"),
                "path": "tools/edge_factory_os_universe_coverage_guard_v1.py",
            },
            "remaining_action": "Review whether this untracked guard is useful before any stage/delete decision.",
            "apply_required": False,
            "runtime_required": False,
        },
        {
            "id": "BROAD_MUTATION_SURFACE_GOVERNANCE_DEBT",
            "status": "OPEN_LONG_TERM_NO_FIX_ALL",
            "severity": "ATTENTION",
            "evidence": {
                "broad_mutation_review_count": counts.get("broad_mutation_review_count"),
                "tracked_candidate_count": counts.get("tracked_candidate_count"),
                "triage_tracked_candidate_count": triage_counts.get("tracked_candidate_count"),
            },
            "remaining_action": "Do not mass patch. Add recurrence-prevention classifier refinement and later sample/contract-based policy reviews only.",
            "apply_required": False,
            "runtime_required": False,
        },
        {
            "id": "UNTRACKED_STABILIZATION_TOOLING",
            "status": "OPEN_COMMIT_OR_DISCARD_PLAN_NEEDED",
            "severity": "ATTENTION",
            "evidence": {
                "untracked_paths": git_state.get("untracked_paths", []),
            },
            "remaining_action": "Decide which stabilization tools to commit and which superseded tools to leave/remove later. No git add -f, no delete/move now.",
            "apply_required": False,
            "runtime_required": False,
        },
    ]


def main() -> int:
    for key, value in SAFETY_FLAGS.items():
        if not isinstance(value, bool):
            raise SystemExit(f"safety flag is not boolean: {key}")

    git_state = get_git_state()
    validation = validate_inputs(git_state)

    if validation["errors"]:
        return fail_closed(
            "input validation failed",
            {
                "validation_errors": validation["errors"],
                "validation_warnings": validation["warnings"],
                "git_state": git_state,
            },
        )

    loaded = validation["loaded"]
    closure_ledger = make_closure_ledger(loaded, git_state)

    open_items = [item for item in closure_ledger if not str(item["status"]).startswith("CLOSED")]
    closed_items = [item for item in closure_ledger if str(item["status"]).startswith("CLOSED")]

    recurrence_prevention_protocol = {
        "freeze_rule": "No OS feature/research development until stabilization closure reaches ZERO P0 and P1 open items or user explicitly overrides.",
        "mandatory_chain": [
            "read-only inspect",
            "preview",
            "approval",
            "comment-only/apply if needed",
            "read-only audit refresh",
            "post-commit status refresh",
        ],
        "classifier_rules_to_fix_before_future_metadata_sweeps": [
            "Do not classify metadata marker strings inside Python string literals as real metadata blocks.",
            "Do not produce mass metadata patch candidates from broad mutation-surface scans.",
            "Only target files with exact path evidence, tracked-file confirmation, and clean diff preview.",
            "Keep direct_apply_recommended_now false unless a dedicated approval module has passed.",
        ],
        "forbidden_until_closure": FORBIDDEN_ACTIONS,
    }

    if open_items:
        controller_status = "STABILIZATION_FREEZE_ERROR_CLOSURE_CONTROLLER_V1_OPEN_ITEMS_REMAIN"
        final_decision = "KEEP_OS_DEVELOPMENT_FROZEN_CLOSE_P0_P1_AND_PREVENT_RECURRENCE"
        next_action = "BUILD_METADATA_CLASSIFIER_RULE_REFINEMENT_PREVIEW_V1_THEN_UNTRACKED_HYGIENE_PLAN"
        next_module = "edge_factory_os_metadata_classifier_rule_refinement_preview_v1.py"
        severity = "ATTENTION"
        reason = f"closed_items={len(closed_items)}; open_items={len(open_items)}; OS development remains frozen"
    else:
        controller_status = "STABILIZATION_FREEZE_ERROR_CLOSURE_CONTROLLER_V1_ALL_CLOSED"
        final_decision = "RUN_FINAL_STABILIZATION_AUDIT_BEFORE_RESUMING_OS_DEVELOPMENT"
        next_action = "BUILD_FINAL_STABILIZATION_AUDIT_AND_RECURRENCE_GUARD"
        next_module = "edge_factory_os_final_stabilization_audit_and_recurrence_guard_v1.py"
        severity = "ATTENTION"
        reason = "all closure ledger items closed; final guard still required before OS development resumes"

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "controller_status": controller_status,
        "severity": severity,
        "allowed_scope": "READ_ONLY_STABILIZATION_CONTROLLER",
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "reason": reason,
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "latest_commit": git_state["head"],
        "counts": {
            "closure_ledger_item_count": len(closure_ledger),
            "closed_item_count": len(closed_items),
            "open_item_count": len(open_items),
            "p0_false_positive_closed_count": 1,
            "p0_locked_open_count": 1,
            "p1_open_count": 2,
            "broad_governance_debt_open_count": 1,
            "untracked_tooling_open_count": 1,
            "direct_apply_recommended_now_count": 0,
            "apply_recommended_now_count": 0,
            "os_development_recommended_now_count": 0,
        },
        "closure_ledger": closure_ledger,
        "open_items": open_items,
        "closed_items": closed_items,
        "recurrence_prevention_protocol": recurrence_prevention_protocol,
        "input_validation_warnings": validation["warnings"],
        "critical_issue_count": 0,
        "warning_count": len(validation["warnings"]),
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
        "os_development_recommended_now": False,
        "candidate_generation_recommended_now": False,
        "family_release_recommended_now": False,
        "runtime_action_recommended_now": False,
        "capital_action_recommended_now": False,
        "holdout_action_recommended_now": False,
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

    latest_json = OUT_DIR / "stabilization_freeze_error_closure_controller_v1_latest.json"
    timestamped_json = OUT_DIR / f"stabilization_freeze_error_closure_controller_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "stabilization_freeze_error_closure_controller_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    txt_lines = [
        "EDGE FACTORY OS STABILIZATION FREEZE + ERROR CLOSURE CONTROLLER v1",
        "=" * 100,
        f"controller_status: {payload['controller_status']}",
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
        "CLOSURE LEDGER",
        "-" * 100,
        json.dumps(closure_ledger, indent=2, sort_keys=True),
        "",
        "OPEN ITEMS",
        "-" * 100,
        json.dumps(open_items, indent=2, sort_keys=True),
        "",
        "RECURRENCE PREVENTION PROTOCOL",
        "-" * 100,
        json.dumps(recurrence_prevention_protocol, indent=2, sort_keys=True),
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

    return 0


if __name__ == "__main__":
    raise SystemExit(main())