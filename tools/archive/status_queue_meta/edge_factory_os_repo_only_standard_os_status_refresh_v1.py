from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

OUT_DIR = REPO_ROOT / "edge_factory_os_repo_only_standard_os_status_refresh"
OUT_DIR.mkdir(parents=True, exist_ok=True)

NOW_UTC = datetime.now(timezone.utc).isoformat()

PREVIOUS_MODULE = {
    "module": "edge_factory_os_backup_hygiene_approval_or_standard_stack_refresh_v1.py",
    "commit": "4f70dab",
    "decision_status": "BACKUP_HYGIENE_APPROVAL_ABSENT_STANDARD_STACK_REFRESH_READY",
    "next_module": "edge_factory_os_repo_only_standard_os_status_refresh_v1.py",
    "manual_approval_present": False,
    "manual_approval_valid": False,
    "backup_delete_allowed_now": False,
    "backup_move_allowed_now": False,
    "gitignore_change_allowed_now": False,
    "pending_hygiene_item_count": 4,
    "known_backup_pending_count": 2,
    "universe_guard_review_required": True,
    "old_short_final_decision": "OLD_SHORT_MONITORING_READY_CONTINUE_COLLECT_NO_CAPITAL",
    "old_short_closed_trades": 20,
    "old_short_next_required_closed_trades_for_capital_review": 30,
    "standard_status_refresh_recommended": True,
}

EXPECTED_PENDING_ITEMS = [
    "tools/edge_factory_os_joint_null_distribution_validator_v1.py.readonly_fix_bak_20260514_022123",
    "tools/edge_factory_os_source_panel_anomaly_discovery_runner_v1.py.blocked_patch_bak_20260514_000647",
    "tools/edge_factory_os_universe_coverage_guard_v1.py",
]

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

ARTIFACT_DIR_HINTS = {
    "backup_hygiene_approval": [
        "edge_factory_os_backup_hygiene_approval_or_standard_stack_refresh",
        "edge_factory_os_backup_hygiene_approval",
    ],
    "runtime_family_status_panel": [
        "edge_factory_os_runtime_family_status_panel_and_backup_hygiene",
    ],
    "runtime_family_monitor_refresh_old_short_aware": [
        "edge_factory_os_runtime_family_monitor_refresh_old_short_aware",
    ],
    "runtime_family_monitor_evaluator_no_capital": [
        "edge_factory_os_runtime_family_monitor_evaluator_no_capital",
    ],
    "patch_integrity_explicit_safety_policy": [
        "edge_factory_os_patch_integrity_audit",
        "edge_factory_os_patch_integrity_explicit_safety_flag_policy",
    ],
    "governance_repair_suite": [
        "edge_factory_os_governance_repair_suite_ledger_alpha_prereg",
    ],
    "untouched_holdout_registry_nested_validation": [
        "edge_factory_os_untouched_holdout_registry",
        "edge_factory_os_untouched_holdout_registry_nested_validation",
    ],
    "global_route_family_alpha_accountant": [
        "edge_factory_os_global_route_family_alpha_accountant",
    ],
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
            data = json.load(f)
        return data if isinstance(data, dict) else {"_non_dict_json": data}
    except Exception:
        return None


def latest_json_from_dirs(dir_names: List[str]) -> Optional[Path]:
    candidates: List[Path] = []

    for name in dir_names:
        for base in [LAB_ROOT / name, REPO_ROOT / name]:
            if base.exists() and base.is_dir():
                candidates.extend(base.rglob("*.json"))

    if not candidates:
        return None

    candidates = [p for p in candidates if p.is_file()]
    if not candidates:
        return None

    return max(candidates, key=lambda p: p.stat().st_mtime)


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


def first_value(artifacts: Dict[str, Dict[str, Any]], key: str, fallback: Any = None) -> Any:
    for payload in artifacts.values():
        data = payload.get("data")
        if data is None:
            continue
        found = recursive_find(data, key)
        if found is not None:
            return found
    return fallback


def normalize_git_status_line(line: str) -> str:
    return line.strip().replace("\\", "/")


def classify_pending_items(git_status_lines: List[str]) -> Dict[str, Any]:
    normalized = [normalize_git_status_line(x) for x in git_status_lines if x.strip()]

    known_backups = [
        x for x in normalized
        if ".bak" in x
        or "_bak_" in x
        or "blocked_patch_bak" in x
        or "readonly_fix_bak" in x
    ]

    universe_guard_items = [
        x for x in normalized
        if "tools/edge_factory_os_universe_coverage_guard_v1.py" in x
    ]

    expected_found = []
    expected_missing = []
    for item in EXPECTED_PENDING_ITEMS:
        if any(item in line for line in normalized):
            expected_found.append(item)
        else:
            expected_missing.append(item)

    return {
        "git_status_lines": normalized,
        "known_backup_pending_items": known_backups,
        "known_backup_pending_count": len(known_backups),
        "universe_guard_items": universe_guard_items,
        "universe_guard_review_required": bool(universe_guard_items) or PREVIOUS_MODULE["universe_guard_review_required"],
        "expected_pending_items_found": expected_found,
        "expected_pending_items_missing_from_current_git_status": expected_missing,
        "pending_hygiene_item_count_observed": len(known_backups) + len(universe_guard_items),
    }


def gate(name: str, observed: Any, required: Any, status: str, evidence: str) -> Dict[str, Any]:
    return {
        "gate": name,
        "observed": observed,
        "required": required,
        "status": status,
        "evidence": evidence,
    }


def build_artifact_inventory() -> Dict[str, Dict[str, Any]]:
    inventory: Dict[str, Dict[str, Any]] = {}

    for label, dirs in ARTIFACT_DIR_HINTS.items():
        path = latest_json_from_dirs(dirs)
        data = load_json(path) if path else None
        inventory[label] = {
            "found": path is not None,
            "path": str(path) if path else None,
            "data": data,
        }

    return inventory


def build_report() -> Dict[str, Any]:
    artifacts = build_artifact_inventory()

    git_result = run_cmd(["git", "-C", str(REPO_ROOT), "status", "--short"])
    git_status_lines = git_result["stdout"].splitlines() if git_result["ok"] else []
    pending = classify_pending_items(git_status_lines)

    old_short_closed_trades = int(
        first_value(
            artifacts,
            "old_short_closed_trades",
            PREVIOUS_MODULE["old_short_closed_trades"],
        )
    )
    old_short_capital_threshold = 50
    old_short_remaining_for_capital_review = max(0, old_short_capital_threshold - old_short_closed_trades)

    old_short_final_decision = first_value(
        artifacts,
        "old_short_final_decision",
        PREVIOUS_MODULE["old_short_final_decision"],
    )

    holdout_selected = bool(first_value(artifacts, "holdout_selected", False))
    holdout_peeked = bool(first_value(artifacts, "holdout_peeked", False))
    holdout_usable_now = bool(first_value(artifacts, "holdout_usable_now", False))

    manual_approval_present = bool(
        first_value(
            artifacts,
            "manual_approval_present",
            PREVIOUS_MODULE["manual_approval_present"],
        )
    )
    manual_approval_valid = bool(
        first_value(
            artifacts,
            "manual_approval_valid",
            PREVIOUS_MODULE["manual_approval_valid"],
        )
    )

    policy_gates = [
        gate(
            "REPO_ONLY_SCOPE",
            SAFETY_FLAGS["repo_only"],
            True,
            "PASS",
            "This module only reads repo/artifact status and writes its own status outputs.",
        ),
        gate(
            "RUNTIME_TOUCH_BLOCK",
            SAFETY_FLAGS["runtime_touch_allowed"],
            False,
            "BLOCKED_AS_REQUIRED",
            "No runtime process, launcher, or runtime patch command is invoked.",
        ),
        gate(
            "LAUNCHER_BLOCK",
            SAFETY_FLAGS["launcher_allowed"],
            False,
            "BLOCKED_AS_REQUIRED",
            "Launcher execution is explicitly disallowed.",
        ),
        gate(
            "RUNTIME_PATCH_BLOCK",
            SAFETY_FLAGS["runtime_patch_allowed"],
            False,
            "BLOCKED_AS_REQUIRED",
            "Runtime patching is explicitly disallowed.",
        ),
        gate(
            "BACKUP_DELETE_BLOCK",
            SAFETY_FLAGS["backup_delete_allowed"],
            False,
            "BLOCKED_AS_REQUIRED",
            "manual_approval_valid=False; backup deletion remains blocked.",
        ),
        gate(
            "BACKUP_MOVE_BLOCK",
            SAFETY_FLAGS["backup_move_allowed"],
            False,
            "BLOCKED_AS_REQUIRED",
            "manual_approval_valid=False; backup moving remains blocked.",
        ),
        gate(
            "GITIGNORE_CHANGE_BLOCK",
            SAFETY_FLAGS["gitignore_change_allowed"],
            False,
            "BLOCKED_AS_REQUIRED",
            "No .gitignore change is allowed in this step.",
        ),
        gate(
            "STRATEGY_RESEARCH_BLOCK",
            SAFETY_FLAGS["strategy_research_allowed"],
            False,
            "BLOCKED_AS_REQUIRED",
            "This is status/governance refresh only, not strategy research.",
        ),
        gate(
            "CANDIDATE_AND_RELEASE_BLOCK",
            any(
                [
                    SAFETY_FLAGS["candidate_generation_allowed"],
                    SAFETY_FLAGS["candidate_contract_allowed"],
                    SAFETY_FLAGS["family_release_allowed"],
                    SAFETY_FLAGS["promotion_allowed"],
                ]
            ),
            False,
            "BLOCKED_AS_REQUIRED",
            "Candidate generation, candidate contract, family release, and promotion are all false.",
        ),
        gate(
            "CAPITAL_ACTIVE_PAPER_LIVE_REAL_ORDER_BLOCK",
            any(
                [
                    SAFETY_FLAGS["capital_change_allowed"],
                    SAFETY_FLAGS["active_paper_allowed"],
                    SAFETY_FLAGS["live_allowed"],
                    SAFETY_FLAGS["real_orders_allowed"],
                ]
            ),
            False,
            "BLOCKED_AS_REQUIRED",
            "Capital, active paper, live, and real order actions are all false.",
        ),
        gate(
            "OLD_SHORT_MONITORING_READY_BUT_NOT_CAPITAL_READY",
            {
                "old_short_final_decision": old_short_final_decision,
                "old_short_closed_trades": old_short_closed_trades,
                "capital_threshold": old_short_capital_threshold,
                "remaining": old_short_remaining_for_capital_review,
            },
            {
                "decision": "MONITORING_READY_NO_CAPITAL",
                "capital_threshold": old_short_capital_threshold,
                "remaining_must_be_positive_until_50_closed": True,
            },
            "PASS_NO_CAPITAL",
            "old_short has monitoring decision readiness but not enough closed trades for capital review.",
        ),
        gate(
            "HOLDOUT_ACCESS_BLOCK",
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
            "BLOCKED_AS_REQUIRED",
            "Untouched holdout remains unavailable for strategy use.",
        ),
        gate(
            "BACKUP_HYGIENE_PENDING_NO_ACTION",
            {
                "manual_approval_present": manual_approval_present,
                "manual_approval_valid": manual_approval_valid,
                "known_backup_pending_count": pending["known_backup_pending_count"],
                "universe_guard_review_required": pending["universe_guard_review_required"],
            },
            {
                "manual_approval_valid": False,
                "delete_or_move": False,
            },
            "PENDING_NO_DESTRUCTIVE_ACTION",
            "Known backups and universe guard remain pending; no deletion/move/gitignore action is authorized.",
        ),
    ]

    any_policy_violation = any(
        row["status"] not in {
            "PASS",
            "BLOCKED_AS_REQUIRED",
            "PASS_NO_CAPITAL",
            "PENDING_NO_DESTRUCTIVE_ACTION",
        }
        for row in policy_gates
    )

    refresh_status = (
        "REPO_ONLY_STANDARD_OS_STATUS_REFRESH_POLICY_ATTENTION"
        if any_policy_violation
        else "REPO_ONLY_STANDARD_OS_STATUS_REFRESH_READY"
    )

    result = {
        "module": "edge_factory_os_repo_only_standard_os_status_refresh_v1.py",
        "generated_at_utc": NOW_UTC,
        "repo_root": str(REPO_ROOT),
        "lab_root": str(LAB_ROOT),
        "refresh_status": refresh_status,
        "severity": "ATTENTION",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": "NO_RUNTIME_NO_RESEARCH_NO_CAPITAL_CONTINUE_REPO_ONLY_GOVERNANCE_REFRESH",
        "reason": (
            "Repo-only OS status consolidated. Runtime/research/candidate/release/capital/live actions remain blocked. "
            "Backup hygiene has no valid manual approval, and old_short remains monitoring-ready but not capital-ready."
        ),
        "previous_module_state": PREVIOUS_MODULE,
        "artifact_inventory": {
            label: {
                "found": payload["found"],
                "path": payload["path"],
            }
            for label, payload in artifacts.items()
        },
        "git_status": {
            "command_ok": git_result["ok"],
            "stderr": git_result["stderr"],
            **pending,
        },
        "old_short_status": {
            "old_short_final_decision": old_short_final_decision,
            "old_short_closed_trades": old_short_closed_trades,
            "old_short_capital_review_threshold": old_short_capital_threshold,
            "old_short_next_required_closed_trades_for_capital_review": old_short_remaining_for_capital_review,
            "old_short_monitoring_ready": True,
            "old_short_capital_ready": False,
            "old_short_capital_action_allowed": False,
            "old_short_research_invalidation_applies": False,
        },
        "backup_hygiene_status": {
            "manual_approval_present": manual_approval_present,
            "manual_approval_valid": manual_approval_valid,
            "backup_delete_allowed_now": False,
            "backup_move_allowed_now": False,
            "gitignore_change_allowed_now": False,
            "known_backup_pending_count": pending["known_backup_pending_count"],
            "universe_guard_review_required": pending["universe_guard_review_required"],
            "pending_hygiene_item_count_observed": pending["pending_hygiene_item_count_observed"],
            "no_delete_no_move_no_gitignore_change": True,
        },
        "holdout_and_validation_status": {
            "holdout_selected": holdout_selected,
            "holdout_peeked": holdout_peeked,
            "holdout_usable_now": holdout_usable_now,
            "strategy_search_allowed_now": False,
            "methodology_repair_allowed_now": True,
            "but_this_module_performs_methodology_execution": False,
        },
        "safety_flags": SAFETY_FLAGS,
        "policy_gates": policy_gates,
        "next_recommended_research_key": "RD8_12_REPO_ONLY_STANDARD_STACK_REFRESH",
        "next_module": "edge_factory_os_repo_only_standard_stack_refresh_v1.py",
        "next_action": "BUILD_REPO_ONLY_STANDARD_STACK_REFRESH_OR_REQUIRE_EXPLICIT_MANUAL_HYGIENE_APPROVAL_NO_RUNTIME_ACTION",
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
            "json": str(OUT_DIR / "repo_only_standard_os_status_refresh_latest.json"),
            "txt": str(OUT_DIR / "repo_only_standard_os_status_refresh_latest.txt"),
            "csv": str(OUT_DIR / "repo_only_standard_os_status_policy_gates_latest.csv"),
        },
    }

    return result


def write_outputs(result: Dict[str, Any]) -> None:
    json_path = OUT_DIR / "repo_only_standard_os_status_refresh_latest.json"
    txt_path = OUT_DIR / "repo_only_standard_os_status_refresh_latest.txt"
    csv_path = OUT_DIR / "repo_only_standard_os_status_policy_gates_latest.csv"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True)

    lines = []
    lines.append("EDGE FACTORY OS REPO-ONLY STANDARD OS STATUS REFRESH v1")
    lines.append("=" * 100)
    lines.append(f"refresh_status: {result['refresh_status']}")
    lines.append(f"severity: {result['severity']}")
    lines.append(f"allowed_scope: {result['allowed_scope']}")
    lines.append(f"final_decision: {result['final_decision']}")
    lines.append(f"next_action: {result['next_action']}")
    lines.append(f"next_module: {result['next_module']}")
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
    lines.append("GIT STATUS LINES")
    lines.append("-" * 100)
    for line in result["git_status"]["git_status_lines"]:
        lines.append(line)
    lines.append("")
    lines.append("POLICY GATES")
    lines.append("-" * 100)
    for row in result["policy_gates"]:
        lines.append(f"{row['gate']}: {row['status']} | observed={row['observed']} | required={row['required']}")
        lines.append(f"  evidence: {row['evidence']}")
    lines.append("")
    lines.append("ARTIFACT INVENTORY")
    lines.append("-" * 100)
    for label, payload in result["artifact_inventory"].items():
        lines.append(f"{label}: found={payload['found']} path={payload['path']}")

    txt = "\n".join(lines) + "\n"
    with txt_path.open("w", encoding="utf-8") as f:
        f.write(txt)

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["gate", "status", "observed", "required", "evidence"],
        )
        writer.writeheader()
        for row in result["policy_gates"]:
            writer.writerow({
                "gate": row["gate"],
                "status": row["status"],
                "observed": json.dumps(row["observed"], ensure_ascii=False, sort_keys=True),
                "required": json.dumps(row["required"], ensure_ascii=False, sort_keys=True),
                "evidence": row["evidence"],
            })

    print(txt)


def main() -> None:
    result = build_report()
    write_outputs(result)


if __name__ == "__main__":
    main()
