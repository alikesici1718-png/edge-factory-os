from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

OUT_DIR = REPO_ROOT / "edge_factory_os_old_short_reactivation_gate"
OUT_DIR.mkdir(parents=True, exist_ok=True)

NOW_UTC = datetime.now(timezone.utc).isoformat()

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
    "old_short_reactivation_allowed_now": False,
    "old_short_runtime_enable_allowed_now": False,
}

KNOWN_STATUS_ARTIFACTS = [
    LAB_ROOT / "edge_factory_os_runtime_family_status_panel_and_backup_hygiene" / "runtime_family_status_panel_and_backup_hygiene_latest.json",
    LAB_ROOT / "edge_factory_os_runtime_family_monitor_refresh_old_short_aware" / "runtime_family_monitor_refresh_old_short_aware_latest.json",
    LAB_ROOT / "edge_factory_os_runtime_family_monitor_evaluator_no_capital" / "runtime_family_monitor_evaluator_no_capital_latest.json",
    REPO_ROOT / "edge_factory_os_repo_only_standard_os_status_refresh" / "repo_only_standard_os_status_refresh_latest.json",
    REPO_ROOT / "edge_factory_os_repo_only_standard_stack_refresh" / "repo_only_standard_stack_refresh_latest.json",
]

SCAN_DIRS = [
    REPO_ROOT / "tools",
    REPO_ROOT / "edge_factory_os_framework",
    REPO_ROOT,
]

SCAN_SUFFIXES = {".py", ".json", ".txt", ".md", ".yaml", ".yml"}


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


def inspect_status_artifacts() -> Dict[str, Dict[str, Any]]:
    result: Dict[str, Dict[str, Any]] = {}

    for path in KNOWN_STATUS_ARTIFACTS:
        label = path.stem
        result[label] = {
            "path": str(path),
            "found": path.exists(),
            "data": load_json(path) if path.exists() and path.suffix.lower() == ".json" else None,
        }

    return result


def normalize_git_line(line: str) -> str:
    return line.strip().replace("\\", "/")


def inspect_git() -> Dict[str, Any]:
    status = run_cmd(["git", "-C", str(REPO_ROOT), "status", "--short"])
    head = run_cmd(["git", "-C", str(REPO_ROOT), "rev-parse", "--short", "HEAD"])
    last = run_cmd(["git", "-C", str(REPO_ROOT), "log", "-1", "--pretty=%h %s"])

    lines = [
        normalize_git_line(x)
        for x in status["stdout"].splitlines()
        if x.strip()
    ] if status["ok"] else []

    return {
        "status_ok": status["ok"],
        "head_short": head["stdout"].strip() if head["ok"] else None,
        "last_commit": last["stdout"].strip() if last["ok"] else None,
        "git_status_lines": lines,
        "untracked_or_dirty_count": len(lines),
        "known_backup_pending_count": len([
            x for x in lines
            if ".bak" in x
            or "_bak_" in x
            or "blocked_patch_bak" in x
            or "readonly_fix_bak" in x
        ]),
        "universe_guard_review_required": any(
            "tools/edge_factory_os_universe_coverage_guard_v1.py" in x
            for x in lines
        ),
    }


def scan_old_short_references() -> Dict[str, Any]:
    matches: List[Dict[str, Any]] = []

    for base in SCAN_DIRS:
        if not base.exists():
            continue

        for path in base.rglob("*"):
            if not path.is_file():
                continue

            if path.suffix.lower() not in SCAN_SUFFIXES:
                continue

            rel = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path

            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            low = text.lower()
            if "old_short" not in low:
                continue

            line_hits = []
            for i, line in enumerate(text.splitlines(), start=1):
                line_low = line.lower()
                if "old_short" in line_low:
                    interesting = any(
                        token in line_low
                        for token in [
                            "enabled",
                            "disabled",
                            "active",
                            "allow",
                            "block",
                            "family",
                            "monitor",
                            "capital",
                            "runtime",
                            "closed",
                            "threshold",
                            "old_short",
                        ]
                    )
                    if interesting:
                        line_hits.append({
                            "line": i,
                            "text": line.strip()[:260],
                        })

            matches.append({
                "path": str(rel),
                "hit_count": len(line_hits),
                "hits": line_hits[:20],
            })

    matches = sorted(matches, key=lambda x: (-x["hit_count"], x["path"]))

    return {
        "old_short_reference_file_count": len(matches),
        "matches": matches[:50],
    }


def gate(name: str, status: str, observed: Any, required: Any, evidence: str) -> Dict[str, Any]:
    return {
        "gate": name,
        "status": status,
        "observed": observed,
        "required": required,
        "evidence": evidence,
    }


def build_report() -> Dict[str, Any]:
    artifacts = inspect_status_artifacts()
    git = inspect_git()
    scan = scan_old_short_references()

    old_short_final_decision = first_found(
        artifacts,
        "old_short_final_decision",
        "UNKNOWN_FROM_CURRENT_ARTIFACTS",
    )
    old_short_closed_trades = int(first_found(artifacts, "old_short_closed_trades", 20))
    old_short_capital_threshold = int(first_found(artifacts, "old_short_capital_review_threshold", 50))
    old_short_remaining = max(0, old_short_capital_threshold - old_short_closed_trades)

    old_short_monitoring_ready = bool(first_found(artifacts, "old_short_monitoring_ready", True))
    old_short_capital_ready = bool(first_found(artifacts, "old_short_capital_ready", False))
    old_short_capital_action_allowed = bool(first_found(artifacts, "old_short_capital_action_allowed", False))

    manual_approval_present = bool(first_found(artifacts, "manual_approval_present", False))
    manual_approval_valid = bool(first_found(artifacts, "manual_approval_valid", False))

    active_paper_allowed_from_artifacts = bool(first_found(artifacts, "active_paper_allowed", False))
    runtime_touch_allowed_from_artifacts = bool(first_found(artifacts, "runtime_touch_allowed", False))
    launcher_allowed_from_artifacts = bool(first_found(artifacts, "launcher_allowed", False))
    live_allowed_from_artifacts = bool(first_found(artifacts, "live_allowed", False))
    real_orders_allowed_from_artifacts = bool(first_found(artifacts, "real_orders_allowed", False))

    reactivation_blockers = []

    if not manual_approval_valid:
        reactivation_blockers.append("NO_EXPLICIT_MANUAL_REACTIVATION_APPROVAL")

    if runtime_touch_allowed_from_artifacts is False:
        reactivation_blockers.append("RUNTIME_TOUCH_CURRENTLY_BLOCKED")

    if launcher_allowed_from_artifacts is False:
        reactivation_blockers.append("LAUNCHER_CURRENTLY_BLOCKED")

    if active_paper_allowed_from_artifacts is False:
        reactivation_blockers.append("ACTIVE_PAPER_CURRENTLY_BLOCKED")

    if old_short_capital_ready is False:
        reactivation_blockers.append("OLD_SHORT_NOT_CAPITAL_READY")

    if old_short_capital_action_allowed is False:
        reactivation_blockers.append("OLD_SHORT_CAPITAL_ACTION_BLOCKED")

    if live_allowed_from_artifacts is False:
        reactivation_blockers.append("LIVE_BLOCKED")

    if real_orders_allowed_from_artifacts is False:
        reactivation_blockers.append("REAL_ORDERS_BLOCKED")

    old_short_can_be_reopened_now = False

    policy_gates = [
        gate(
            "REPO_ONLY_REACTIVATION_GATE",
            "PASS",
            SAFETY_FLAGS["repo_only"],
            True,
            "This module only checks old_short reactivation prerequisites; it does not enable runtime.",
        ),
        gate(
            "NO_RUNTIME_TOUCH_THIS_STEP",
            "BLOCKED_AS_REQUIRED",
            {
                "runtime_touch_allowed": SAFETY_FLAGS["runtime_touch_allowed"],
                "launcher_allowed": SAFETY_FLAGS["launcher_allowed"],
                "runtime_patch_allowed": SAFETY_FLAGS["runtime_patch_allowed"],
                "execution_allowed": SAFETY_FLAGS["execution_allowed"],
            },
            {
                "runtime_touch_allowed": False,
                "launcher_allowed": False,
                "runtime_patch_allowed": False,
                "execution_allowed": False,
            },
            "No runtime process, launcher, runtime patch, or execution action is performed.",
        ),
        gate(
            "OLD_SHORT_REACTIVATION_NOT_ALLOWED_WITHOUT_MANUAL_APPROVAL",
            "BLOCKED_AS_REQUIRED",
            {
                "manual_approval_present": manual_approval_present,
                "manual_approval_valid": manual_approval_valid,
            },
            {
                "manual_approval_valid": True,
                "required_before_runtime_enable": True,
            },
            "User stated old_short was closed, but current step has no explicit machine-readable reactivation approval.",
        ),
        gate(
            "OLD_SHORT_MONITORING_READY_BUT_NOT_CAPITAL_READY",
            "PASS_NO_CAPITAL",
            {
                "old_short_final_decision": old_short_final_decision,
                "old_short_closed_trades": old_short_closed_trades,
                "old_short_capital_threshold": old_short_capital_threshold,
                "old_short_remaining": old_short_remaining,
                "old_short_monitoring_ready": old_short_monitoring_ready,
                "old_short_capital_ready": old_short_capital_ready,
                "old_short_capital_action_allowed": old_short_capital_action_allowed,
            },
            {
                "capital_threshold": 50,
                "capital_ready": False,
                "capital_action_allowed": False,
            },
            "old_short may be monitoring-ready, but capital review/action remains blocked until 50 closed trades.",
        ),
        gate(
            "LIVE_REAL_ORDER_BLOCK",
            "BLOCKED_AS_REQUIRED",
            {
                "live_allowed": live_allowed_from_artifacts,
                "real_orders_allowed": real_orders_allowed_from_artifacts,
            },
            {
                "live_allowed": False,
                "real_orders_allowed": False,
            },
            "Reactivation cannot imply live trading or real orders.",
        ),
    ]

    result = {
        "module": "edge_factory_os_old_short_reactivation_gate_v1.py",
        "generated_at_utc": NOW_UTC,
        "repo_root": str(REPO_ROOT),
        "lab_root": str(LAB_ROOT),
        "gate_status": "OLD_SHORT_REACTIVATION_GATE_BLOCKED_MANUAL_APPROVAL_REQUIRED",
        "severity": "ATTENTION",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": "DO_NOT_REOPEN_OLD_SHORT_YET_CREATE_EXPLICIT_MANUAL_REACTIVATION_APPROVAL_FIRST",
        "reason": (
            "The user says old_short was manually closed. Current artifacts say old_short is monitoring-ready "
            "but not capital-ready. Runtime touch, launcher, active paper, live, and real order paths remain blocked. "
            "This module records that reopening requires a separate explicit manual reactivation approval and a guarded runtime action."
        ),
        "old_short_can_be_reopened_now": old_short_can_be_reopened_now,
        "reactivation_blockers": reactivation_blockers,
        "old_short_status": {
            "old_short_final_decision": old_short_final_decision,
            "old_short_closed_trades": old_short_closed_trades,
            "old_short_capital_review_threshold": old_short_capital_threshold,
            "old_short_next_required_closed_trades_for_capital_review": old_short_remaining,
            "old_short_monitoring_ready": old_short_monitoring_ready,
            "old_short_capital_ready": old_short_capital_ready,
            "old_short_capital_action_allowed": old_short_capital_action_allowed,
        },
        "manual_approval_status": {
            "manual_approval_present": manual_approval_present,
            "manual_approval_valid": manual_approval_valid,
            "required_approval_text": (
                "I explicitly approve repo-only preparation for old_short reactivation gate. "
                "Do not enable live trading, real orders, or capital changes. "
                "Only prepare a separate guarded runtime re-enable plan for old_short monitoring/active-paper restoration."
            ),
        },
        "safety_flags": SAFETY_FLAGS,
        "artifact_status": {
            key: {
                "path": value["path"],
                "found": value["found"],
            }
            for key, value in artifacts.items()
        },
        "git_state": git,
        "old_short_reference_scan": scan,
        "policy_gates": policy_gates,
        "next_module": "edge_factory_os_old_short_manual_reactivation_approval_v1.py",
        "next_action": "STOP_OR_CREATE_EXPLICIT_MANUAL_REACTIVATION_APPROVAL_NO_RUNTIME_ACTION",
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
            "json": str(OUT_DIR / "old_short_reactivation_gate_latest.json"),
            "txt": str(OUT_DIR / "old_short_reactivation_gate_latest.txt"),
        },
    }

    return result


def write_outputs(result: Dict[str, Any]) -> None:
    json_path = OUT_DIR / "old_short_reactivation_gate_latest.json"
    txt_path = OUT_DIR / "old_short_reactivation_gate_latest.txt"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True)

    lines = []
    lines.append("EDGE FACTORY OS OLD_SHORT REACTIVATION GATE v1")
    lines.append("=" * 100)
    lines.append(f"gate_status: {result['gate_status']}")
    lines.append(f"severity: {result['severity']}")
    lines.append(f"allowed_scope: {result['allowed_scope']}")
    lines.append(f"final_decision: {result['final_decision']}")
    lines.append(f"old_short_can_be_reopened_now: {result['old_short_can_be_reopened_now']}")
    lines.append(f"next_action: {result['next_action']}")
    lines.append(f"next_module: {result['next_module']}")
    lines.append("")
    lines.append("REACTIVATION BLOCKERS")
    lines.append("-" * 100)
    for item in result["reactivation_blockers"]:
        lines.append(str(item))
    lines.append("")
    lines.append("OLD_SHORT STATUS")
    lines.append("-" * 100)
    for key, value in result["old_short_status"].items():
        lines.append(f"{key}: {value}")
    lines.append("")
    lines.append("MANUAL APPROVAL STATUS")
    lines.append("-" * 100)
    for key, value in result["manual_approval_status"].items():
        lines.append(f"{key}: {value}")
    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for key, value in result["safety_flags"].items():
        lines.append(f"{key}: {value}")
    lines.append("")
    lines.append("OLD_SHORT REFERENCE SCAN")
    lines.append("-" * 100)
    lines.append(f"old_short_reference_file_count: {result['old_short_reference_scan']['old_short_reference_file_count']}")
    for match in result["old_short_reference_scan"]["matches"][:20]:
        lines.append(f"path: {match['path']} hit_count={match['hit_count']}")
        for hit in match["hits"][:8]:
            lines.append(f"  L{hit['line']}: {hit['text']}")
    lines.append("")
    lines.append("POLICY GATES")
    lines.append("-" * 100)
    for row in result["policy_gates"]:
        lines.append(f"{row['gate']}: {row['status']}")
        lines.append(f"  observed: {row['observed']}")
        lines.append(f"  required: {row['required']}")
        lines.append(f"  evidence: {row['evidence']}")

    text = "\n".join(lines) + "\n"

    with txt_path.open("w", encoding="utf-8") as f:
        f.write(text)

    print(text)


def main() -> None:
    result = build_report()
    write_outputs(result)


if __name__ == "__main__":
    main()
