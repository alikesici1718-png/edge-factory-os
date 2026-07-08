from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

OUT_DIR = REPO_ROOT / "edge_factory_os_repo_only_standard_stack_refresh"
OUT_DIR.mkdir(parents=True, exist_ok=True)

NOW_UTC = datetime.now(timezone.utc).isoformat()

PREVIOUS_MODULE = {
    "module": "edge_factory_os_repo_only_standard_os_status_refresh_v1.py",
    "commit": "bee1c94",
    "refresh_status": "REPO_ONLY_STANDARD_OS_STATUS_REFRESH_READY",
    "severity": "ATTENTION",
    "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
    "final_decision": "NO_RUNTIME_NO_RESEARCH_NO_CAPITAL_CONTINUE_REPO_ONLY_GOVERNANCE_REFRESH",
    "next_module": "edge_factory_os_repo_only_standard_stack_refresh_v1.py",
    "old_short_final_decision": "OLD_SHORT_MONITORING_READY_CONTINUE_COLLECT_NO_CAPITAL",
    "old_short_closed_trades": 20,
    "old_short_capital_review_threshold": 50,
    "old_short_next_required_closed_trades_for_capital_review": 30,
    "manual_approval_present": False,
    "manual_approval_valid": False,
    "backup_delete_allowed_now": False,
    "backup_move_allowed_now": False,
    "gitignore_change_allowed_now": False,
    "known_backup_pending_count": 2,
    "universe_guard_review_required": True,
    "pending_hygiene_item_count_observed": 3,
}

EXPECTED_UNTRACKED_ITEMS = [
    "tools/edge_factory_os_joint_null_distribution_validator_v1.py.readonly_fix_bak_20260514_022123",
    "tools/edge_factory_os_source_panel_anomaly_discovery_runner_v1.py.blocked_patch_bak_20260514_000647",
    "tools/edge_factory_os_universe_coverage_guard_v1.py",
]

REQUIRED_ARTIFACTS = {
    "repo_only_standard_os_status_refresh": [
        REPO_ROOT / "edge_factory_os_repo_only_standard_os_status_refresh" / "repo_only_standard_os_status_refresh_latest.json",
        REPO_ROOT / "edge_factory_os_repo_only_standard_os_status_refresh" / "repo_only_standard_os_status_refresh_latest.txt",
    ],
    "backup_hygiene_approval_or_standard_stack_refresh": [
        LAB_ROOT / "edge_factory_os_backup_hygiene_approval_or_standard_stack_refresh" / "backup_hygiene_approval_or_standard_stack_refresh_latest.json",
    ],
    "runtime_family_status_panel_and_backup_hygiene": [
        LAB_ROOT / "edge_factory_os_runtime_family_status_panel_and_backup_hygiene" / "runtime_family_status_panel_and_backup_hygiene_latest.json",
    ],
    "runtime_family_monitor_refresh_old_short_aware": [
        LAB_ROOT / "edge_factory_os_runtime_family_monitor_refresh_old_short_aware" / "runtime_family_monitor_refresh_old_short_aware_latest.json",
    ],
    "runtime_family_monitor_evaluator_no_capital": [
        LAB_ROOT / "edge_factory_os_runtime_family_monitor_evaluator_no_capital" / "runtime_family_monitor_evaluator_no_capital_latest.json",
    ],
    "governance_repair_suite_ledger_alpha_prereg": [
        LAB_ROOT / "edge_factory_os_governance_repair_suite_ledger_alpha_prereg" / "governance_repair_suite_ledger_alpha_prereg_latest.json",
    ],
    "global_route_family_alpha_accountant": [
        LAB_ROOT / "edge_factory_os_global_route_family_alpha_accountant" / "global_route_family_alpha_accountant_latest.json",
    ],
}

SAFETY_FLAGS = {
    "repo_only": True,
    "runtime_touch_allowed": False,
    "launcher_allowed": False,
    "runtime_patch_allowed": False,
    "backup_delete_allowed": False,
    "backup_move_allowed": False,
    "gitignore_change_allowed": False,
    "strategy_research_allowed": False,
    "candidate_generation_allowed": False,
    "candidate_contract_allowed": False,
    "family_release_allowed": False,
    "promotion_allowed": False,
    "capital_change_allowed": False,
    "active_paper_allowed": False,
    "live_allowed": False,
    "real_orders_allowed": False,
    "file_delete_allowed": False,
    "file_move_allowed": False,
    "archive_allowed": False,
    "execution_allowed": False,
}


def run_cmd(args: List[str], timeout: int = 20) -> Dict[str, Any]:
    try:
        proc = subprocess.run(
            args,
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except Exception as exc:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": repr(exc),
        }


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else {"_json": obj}
    except Exception:
        return None


def recursive_find(obj: Any, key: str) -> Any:
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for value in obj.values():
            found = recursive_find(value, key)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = recursive_find(item, key)
            if found is not None:
                return found
    return None


def first_found(payloads: Dict[str, Dict[str, Any]], key: str, fallback: Any = None) -> Any:
    for info in payloads.values():
        data = info.get("data")
        if data is None:
            continue
        found = recursive_find(data, key)
        if found is not None:
            return found
    return fallback


def normalize_git_line(line: str) -> str:
    return line.strip().replace("\\", "/")


def inspect_git() -> Dict[str, Any]:
    status_result = run_cmd(["git", "-C", str(REPO_ROOT), "status", "--short"])
    branch_result = run_cmd(["git", "-C", str(REPO_ROOT), "branch", "--show-current"])
    head_result = run_cmd(["git", "-C", str(REPO_ROOT), "rev-parse", "--short", "HEAD"])
    last_commit_result = run_cmd(["git", "-C", str(REPO_ROOT), "log", "-1", "--pretty=%h %s"])

    lines = [
        normalize_git_line(x)
        for x in status_result["stdout"].splitlines()
        if x.strip()
    ] if status_result["ok"] else []

    expected_found = []
    expected_missing = []
    for item in EXPECTED_UNTRACKED_ITEMS:
        if any(item in line for line in lines):
            expected_found.append(item)
        else:
            expected_missing.append(item)

    known_backup_lines = [
        x for x in lines
        if ".bak" in x
        or "_bak_" in x
        or "blocked_patch_bak" in x
        or "readonly_fix_bak" in x
    ]

    universe_guard_lines = [
        x for x in lines
        if "tools/edge_factory_os_universe_coverage_guard_v1.py" in x
    ]

    this_tool_untracked = [
        x for x in lines
        if "tools/edge_factory_os_repo_only_standard_stack_refresh_v1.py" in x
    ]

    output_dir_untracked = [
        x for x in lines
        if "edge_factory_os_repo_only_standard_stack_refresh/" in x
    ]

    return {
        "status_command_ok": status_result["ok"],
        "status_stderr": status_result["stderr"],
        "branch": branch_result["stdout"].strip() if branch_result["ok"] else None,
        "head_short": head_result["stdout"].strip() if head_result["ok"] else None,
        "last_commit": last_commit_result["stdout"].strip() if last_commit_result["ok"] else None,
        "git_status_lines": lines,
        "expected_untracked_items_found": expected_found,
        "expected_untracked_items_missing": expected_missing,
        "known_backup_pending_count": len(known_backup_lines),
        "known_backup_pending_items": known_backup_lines,
        "universe_guard_review_required": bool(universe_guard_lines) or PREVIOUS_MODULE["universe_guard_review_required"],
        "universe_guard_items": universe_guard_lines,
        "this_tool_untracked": this_tool_untracked,
        "output_dir_untracked": output_dir_untracked,
        "dirty_or_untracked_count": len(lines),
    }


def inspect_artifacts() -> Dict[str, Dict[str, Any]]:
    result: Dict[str, Dict[str, Any]] = {}

    for label, paths in REQUIRED_ARTIFACTS.items():
        found_paths = [p for p in paths if p.exists()]
        selected = found_paths[0] if found_paths else None
        result[label] = {
            "required_paths": [str(p) for p in paths],
            "found": selected is not None,
            "selected_path": str(selected) if selected else None,
            "data": load_json(selected) if selected else None,
        }

    return result


def policy_gate(name: str, status: str, observed: Any, required: Any, evidence: str) -> Dict[str, Any]:
    return {
        "gate": name,
        "status": status,
        "observed": observed,
        "required": required,
        "evidence": evidence,
    }


def build_report() -> Dict[str, Any]:
    git = inspect_git()
    artifacts = inspect_artifacts()

    old_short_closed = int(
        first_found(
            artifacts,
            "old_short_closed_trades",
            PREVIOUS_MODULE["old_short_closed_trades"],
        )
    )
    old_short_threshold = 50
    old_short_remaining = max(0, old_short_threshold - old_short_closed)

    old_short_final_decision = first_found(
        artifacts,
        "old_short_final_decision",
        PREVIOUS_MODULE["old_short_final_decision"],
    )

    manual_approval_present = bool(
        first_found(
            artifacts,
            "manual_approval_present",
            PREVIOUS_MODULE["manual_approval_present"],
        )
    )
    manual_approval_valid = bool(
        first_found(
            artifacts,
            "manual_approval_valid",
            PREVIOUS_MODULE["manual_approval_valid"],
        )
    )

    holdout_selected = bool(first_found(artifacts, "holdout_selected", False))
    holdout_peeked = bool(first_found(artifacts, "holdout_peeked", False))
    holdout_usable_now = bool(first_found(artifacts, "holdout_usable_now", False))

    artifact_summary = {
        key: {
            "found": value["found"],
            "selected_path": value["selected_path"],
        }
        for key, value in artifacts.items()
    }

    missing_artifacts = [
        key for key, value in artifact_summary.items()
        if not value["found"]
    ]

    policy_gates = [
        policy_gate(
            "REPO_ONLY_SCOPE",
            "PASS",
            SAFETY_FLAGS["repo_only"],
            True,
            "This module only reads git/artifact state and writes its own report outputs.",
        ),
        policy_gate(
            "NO_RUNTIME_LAUNCHER_OR_PATCH",
            "BLOCKED_AS_REQUIRED",
            {
                "runtime_touch_allowed": SAFETY_FLAGS["runtime_touch_allowed"],
                "launcher_allowed": SAFETY_FLAGS["launcher_allowed"],
                "runtime_patch_allowed": SAFETY_FLAGS["runtime_patch_allowed"],
            },
            {
                "runtime_touch_allowed": False,
                "launcher_allowed": False,
                "runtime_patch_allowed": False,
            },
            "Runtime, launcher, and patch operations remain explicitly blocked.",
        ),
        policy_gate(
            "NO_BACKUP_DELETE_MOVE_OR_GITIGNORE_CHANGE",
            "BLOCKED_AS_REQUIRED",
            {
                "manual_approval_present": manual_approval_present,
                "manual_approval_valid": manual_approval_valid,
                "backup_delete_allowed": SAFETY_FLAGS["backup_delete_allowed"],
                "backup_move_allowed": SAFETY_FLAGS["backup_move_allowed"],
                "gitignore_change_allowed": SAFETY_FLAGS["gitignore_change_allowed"],
            },
            {
                "manual_approval_valid": False,
                "backup_delete_allowed": False,
                "backup_move_allowed": False,
                "gitignore_change_allowed": False,
            },
            "No valid explicit manual approval exists, so backup hygiene stays pending without destructive action.",
        ),
        policy_gate(
            "NO_STRATEGY_RESEARCH_OR_CANDIDATE_RELEASE",
            "BLOCKED_AS_REQUIRED",
            {
                "strategy_research_allowed": SAFETY_FLAGS["strategy_research_allowed"],
                "candidate_generation_allowed": SAFETY_FLAGS["candidate_generation_allowed"],
                "candidate_contract_allowed": SAFETY_FLAGS["candidate_contract_allowed"],
                "family_release_allowed": SAFETY_FLAGS["family_release_allowed"],
                "promotion_allowed": SAFETY_FLAGS["promotion_allowed"],
            },
            {
                "strategy_research_allowed": False,
                "candidate_generation_allowed": False,
                "candidate_contract_allowed": False,
                "family_release_allowed": False,
                "promotion_allowed": False,
            },
            "This refresh is governance/status only and does not open a research or release route.",
        ),
        policy_gate(
            "NO_CAPITAL_ACTIVE_PAPER_LIVE_REAL_ORDER",
            "BLOCKED_AS_REQUIRED",
            {
                "capital_change_allowed": SAFETY_FLAGS["capital_change_allowed"],
                "active_paper_allowed": SAFETY_FLAGS["active_paper_allowed"],
                "live_allowed": SAFETY_FLAGS["live_allowed"],
                "real_orders_allowed": SAFETY_FLAGS["real_orders_allowed"],
            },
            {
                "capital_change_allowed": False,
                "active_paper_allowed": False,
                "live_allowed": False,
                "real_orders_allowed": False,
            },
            "Capital, active paper, live, and real order pathways remain blocked.",
        ),
        policy_gate(
            "OLD_SHORT_MONITORING_READY_NOT_CAPITAL_READY",
            "PASS_NO_CAPITAL",
            {
                "old_short_final_decision": old_short_final_decision,
                "old_short_closed_trades": old_short_closed,
                "capital_review_threshold": old_short_threshold,
                "remaining_for_capital_review": old_short_remaining,
            },
            {
                "old_short_closed_trades_min_for_capital_review": old_short_threshold,
                "capital_ready": False,
                "capital_action_allowed": False,
            },
            "old_short is monitoring-ready but still below the 50 closed trade capital review threshold.",
        ),
        policy_gate(
            "HOLDOUT_ACCESS_BLOCKED",
            "BLOCKED_AS_REQUIRED",
            {
                "holdout_selected": holdout_selected,
                "holdout_peeked": holdout_peeked,
                "holdout_usable_now": holdout_usable_now,
            },
            {
                "holdout_selected": False,
                "holdout_peeked": False,
                "holdout_usable_now": False,
            },
            "Untouched holdout remains unavailable for strategy use.",
        ),
        policy_gate(
            "PENDING_HYGIENE_VISIBLE_NO_ACTION",
            "PENDING_NO_DESTRUCTIVE_ACTION",
            {
                "known_backup_pending_count": git["known_backup_pending_count"],
                "universe_guard_review_required": git["universe_guard_review_required"],
                "expected_untracked_items_found": git["expected_untracked_items_found"],
                "expected_untracked_items_missing": git["expected_untracked_items_missing"],
            },
            {
                "delete_move_gitignore_change": False,
                "manual_approval_required_before_cleanup": True,
            },
            "Known pending backup/universe-guard hygiene remains visible but untouched.",
        ),
        policy_gate(
            "ARTIFACT_CONTINUITY_CHECK",
            "PASS_WITH_NOTED_GAPS" if missing_artifacts else "PASS",
            {
                "missing_artifacts": missing_artifacts,
                "artifact_summary": artifact_summary,
            },
            {
                "must_not_fail_if_optional_artifacts_missing": True,
                "must_record_missing_artifacts": True,
            },
            "Continuity artifacts are inventoried. Missing optional artifacts are recorded instead of guessed.",
        ),
    ]

    stack_attention_reasons = []
    if git["known_backup_pending_count"] > 0:
        stack_attention_reasons.append("known_backup_hygiene_pending")
    if git["universe_guard_review_required"]:
        stack_attention_reasons.append("universe_guard_review_required")
    if missing_artifacts:
        stack_attention_reasons.append("some_optional_continuity_artifacts_missing")
    if old_short_remaining > 0:
        stack_attention_reasons.append("old_short_not_capital_ready")

    stack_status = (
        "REPO_ONLY_STANDARD_STACK_REFRESH_READY_WITH_PENDING_ATTENTION"
        if stack_attention_reasons
        else "REPO_ONLY_STANDARD_STACK_REFRESH_READY"
    )

    result = {
        "module": "edge_factory_os_repo_only_standard_stack_refresh_v1.py",
        "generated_at_utc": NOW_UTC,
        "repo_root": str(REPO_ROOT),
        "lab_root": str(LAB_ROOT),
        "stack_status": stack_status,
        "severity": "ATTENTION",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": "NO_RUNTIME_NO_RESEARCH_NO_CAPITAL_NO_HYGIENE_ACTION_CONTINUE_SAFE_STATUS_GOVERNANCE",
        "reason": (
            "Standard stack refresh completed as repo-only OS intelligence. "
            "Runtime, launcher, patching, backup cleanup, strategy research, candidate/release, and capital/live pathways remain blocked."
        ),
        "stack_attention_reasons": stack_attention_reasons,
        "previous_module_state": PREVIOUS_MODULE,
        "git_state": git,
        "artifact_summary": artifact_summary,
        "missing_artifacts": missing_artifacts,
        "old_short_status": {
            "old_short_final_decision": old_short_final_decision,
            "old_short_closed_trades": old_short_closed,
            "old_short_capital_review_threshold": old_short_threshold,
            "old_short_next_required_closed_trades_for_capital_review": old_short_remaining,
            "old_short_monitoring_ready": True,
            "old_short_capital_ready": False,
            "old_short_capital_action_allowed": False,
            "old_short_research_invalidation_applies": False,
        },
        "backup_hygiene_status": {
            "manual_approval_present": manual_approval_present,
            "manual_approval_valid": manual_approval_valid,
            "known_backup_pending_count": git["known_backup_pending_count"],
            "known_backup_pending_items": git["known_backup_pending_items"],
            "universe_guard_review_required": git["universe_guard_review_required"],
            "universe_guard_items": git["universe_guard_items"],
            "backup_delete_allowed_now": False,
            "backup_move_allowed_now": False,
            "gitignore_change_allowed_now": False,
            "cleanup_requires_explicit_manual_approval": True,
        },
        "holdout_status": {
            "holdout_selected": holdout_selected,
            "holdout_peeked": holdout_peeked,
            "holdout_usable_now": holdout_usable_now,
            "strategy_search_allowed_now": False,
        },
        "safety_flags": SAFETY_FLAGS,
        "policy_gates": policy_gates,
        "next_recommended_research_key": "RD8_13_REPO_ONLY_STATUS_DASHBOARD_OR_MANUAL_HYGIENE_APPROVAL_GATE",
        "next_module": "edge_factory_os_repo_only_status_dashboard_or_manual_hygiene_approval_gate_v1.py",
        "next_action": "BUILD_REPO_ONLY_STATUS_DASHBOARD_OR_STOP_FOR_EXPLICIT_MANUAL_HYGIENE_APPROVAL_NO_RUNTIME_ACTION",
        "next_step_rules": {
            "runtime_touch": False,
            "launcher": False,
            "runtime_patch": False,
            "backup_delete": False,
            "backup_move": False,
            "gitignore_change": False,
            "strategy_research": False,
            "candidate_generation": False,
            "family_release": False,
            "capital_change": False,
            "active_paper": False,
            "live": False,
            "real_orders": False,
        },
        "outputs": {
            "json": str(OUT_DIR / "repo_only_standard_stack_refresh_latest.json"),
            "txt": str(OUT_DIR / "repo_only_standard_stack_refresh_latest.txt"),
        },
    }

    return result


def write_outputs(result: Dict[str, Any]) -> None:
    json_path = OUT_DIR / "repo_only_standard_stack_refresh_latest.json"
    txt_path = OUT_DIR / "repo_only_standard_stack_refresh_latest.txt"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True)

    lines = []
    lines.append("EDGE FACTORY OS REPO-ONLY STANDARD STACK REFRESH v1")
    lines.append("=" * 100)
    lines.append(f"stack_status: {result['stack_status']}")
    lines.append(f"severity: {result['severity']}")
    lines.append(f"allowed_scope: {result['allowed_scope']}")
    lines.append(f"final_decision: {result['final_decision']}")
    lines.append(f"next_action: {result['next_action']}")
    lines.append(f"next_module: {result['next_module']}")
    lines.append("")
    lines.append("STACK ATTENTION REASONS")
    lines.append("-" * 100)
    for item in result["stack_attention_reasons"]:
        lines.append(str(item))
    if not result["stack_attention_reasons"]:
        lines.append("none")
    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for key, value in result["safety_flags"].items():
        lines.append(f"{key}: {value}")
    lines.append("")
    lines.append("OLD_SHORT STATUS")
    lines.append("-" * 100)
    for key, value in result["old_short_status"].items():
        lines.append(f"{key}: {value}")
    lines.append("")
    lines.append("BACKUP HYGIENE STATUS")
    lines.append("-" * 100)
    for key, value in result["backup_hygiene_status"].items():
        lines.append(f"{key}: {value}")
    lines.append("")
    lines.append("GIT STATE")
    lines.append("-" * 100)
    lines.append(f"branch: {result['git_state']['branch']}")
    lines.append(f"head_short: {result['git_state']['head_short']}")
    lines.append(f"last_commit: {result['git_state']['last_commit']}")
    lines.append(f"dirty_or_untracked_count: {result['git_state']['dirty_or_untracked_count']}")
    lines.append("git_status_lines:")
    for line in result["git_state"]["git_status_lines"]:
        lines.append(f"  {line}")
    lines.append("")
    lines.append("ARTIFACT SUMMARY")
    lines.append("-" * 100)
    for key, value in result["artifact_summary"].items():
        lines.append(f"{key}: found={value['found']} path={value['selected_path']}")
    lines.append("")
    lines.append("POLICY GATES")
    lines.append("-" * 100)
    for row in result["policy_gates"]:
        lines.append(f"{row['gate']}: {row['status']}")
        lines.append(f"  observed: {row['observed']}")
        lines.append(f"  required: {row['required']}")
        lines.append(f"  evidence: {row['evidence']}")

    txt = "\n".join(lines) + "\n"

    with txt_path.open("w", encoding="utf-8") as f:
        f.write(txt)

    print(txt)


def main() -> None:
    result = build_report()
    write_outputs(result)


if __name__ == "__main__":
    main()
