from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]

PLAN_JSON = (
    REPO_ROOT
    / "edge_factory_os_old_short_guarded_runtime_reenable_plan"
    / "old_short_guarded_runtime_reenable_plan_latest.json"
)

OUT_DIR = REPO_ROOT / "edge_factory_os_old_short_guarded_runtime_reenable_patch_preview"
OUT_JSON = OUT_DIR / "old_short_guarded_runtime_reenable_patch_preview_latest.json"
OUT_TXT = OUT_DIR / "old_short_guarded_runtime_reenable_patch_preview_latest.txt"

REQUIRED_PLAN_STATUS = "OLD_SHORT_GUARDED_RUNTIME_REENABLE_PLAN_READY_NO_EXECUTION"

INSPECT_REL_PATHS: List[str] = [
    "tools/edge_factory_os_runtime_family_monitor_refresh_old_short_aware_v1.py",
    "tools/edge_factory_os_runtime_family_monitor_evaluator_no_capital_v1.py",
    "tools/edge_factory_os_family_registry_and_lesson_enforcer_repair_v1.py",
    "tools/edge_factory_os_runtime_family_status_panel_and_backup_hygiene_v1.py",
    "edge_factory_os_framework/status/runtime_family_monitor_refresh_old_short_aware_summary_v1.json",
    "edge_factory_os_framework/policies/runtime_family_monitor_refresh_old_short_aware_state_v1.json",
    "edge_factory_os_framework/registries/runtime_family_registry_v1.json",
    "edge_factory_os_framework/status/runtime_family_status_panel_and_backup_hygiene_v1.json",
    "src/edge_factory_master_launcher_gate_repair_v3.py",
    "src/edge_factory_patch_master_launcher_risk_args_v1.py",
    "src/old_short_gate_aware_live_paper_logger.py",
    "tools/edge_factory_runtime_regression_guard_v1.py",
    "src/global_paper_risk_manager.py",
    "src/edge_factory_paper_boot_plan.py",
    "src/global_paper_risk_manager_v3_priority.py",
    "src/edge_factory_paper_sample_watcher_v1.py",
]

KEYWORD_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("old_short", re.compile(r"old_short", re.IGNORECASE)),
    ("family_monitor", re.compile(r"family|monitor|registry|runtime_family", re.IGNORECASE)),
    ("gate_or_guard", re.compile(r"gate|guard|blocked|approval|policy", re.IGNORECASE)),
    ("paper_not_live", re.compile(r"paper|simulat|dry|sandbox", re.IGNORECASE)),
]

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only": True,
    "runtime_touch_allowed": False,
    "launcher_allowed": False,
    "runtime_patch_allowed": False,
    "patch_apply_allowed_now": False,
    "backup_delete_allowed": False,
    "backup_move_allowed": False,
    "gitignore_change_allowed": False,
    "strategy_research_allowed": False,
    "candidate_generation_allowed": False,
    "candidate_contract_allowed": False,
    "family_release_allowed": False,
    "promotion_allowed": False,
    "capital_change_allowed": False,
    "active_paper_execution_allowed_now": False,
    "live_allowed": False,
    "real_orders_allowed": False,
    "file_delete_allowed": False,
    "file_move_allowed": False,
    "archive_allowed": False,
    "execution_allowed": False,
    "old_short_runtime_enable_allowed_now": False,
}

FORBIDDEN_ACTIONS: List[str] = [
    "Do not touch runtime.",
    "Do not run launcher.",
    "Do not start any process.",
    "Do not apply runtime patch.",
    "Do not enable old_short runtime now.",
    "Do not enable active paper execution now.",
    "Do not change capital.",
    "Do not enable live trading.",
    "Do not send or enable real orders.",
    "Do not delete, move, or archive backup files.",
    "Do not change .gitignore.",
    "Do not use git add -f.",
    "Do not run strategy research or generate trading candidates.",
    "Do not release or promote any family.",
    "Do not touch holdout.",
    "Do not bypass governance because something looks safe.",
]

NOW_UTC = datetime.now(timezone.utc).isoformat()


def run_cmd(args: List[str], timeout: int = 30) -> Dict[str, Any]:
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


def inspect_git() -> Dict[str, Any]:
    status = run_cmd(["git", "-C", str(REPO_ROOT), "status", "--short"])
    head = run_cmd(["git", "-C", str(REPO_ROOT), "rev-parse", "--short", "HEAD"])
    last = run_cmd(["git", "-C", str(REPO_ROOT), "log", "-1", "--pretty=%h %s"])

    lines = status["stdout"].splitlines() if status["ok"] else []
    lines = [x.strip().replace("\\", "/") for x in lines if x.strip()]

    return {
        "status_ok": status["ok"],
        "head_short": head["stdout"].strip() if head["ok"] else None,
        "last_commit": last["stdout"].strip() if last["ok"] else None,
        "git_status_lines": lines,
        "untracked_or_dirty_count": len(lines),
        "known_backup_pending_count": len(
            [
                x
                for x in lines
                if ".bak" in x
                or "_bak_" in x
                or "blocked_patch_bak" in x
                or "readonly_fix_bak" in x
            ]
        ),
        "universe_guard_review_required": any(
            "tools/edge_factory_os_universe_coverage_guard_v1.py" in x for x in lines
        ),
    }


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(REPO_ROOT)).replace("\\", "/")
    except Exception:
        return str(p).replace("\\", "/")


def inspect_file(rel_path: str) -> Dict[str, Any]:
    path = (REPO_ROOT / rel_path.replace("/", "\\")).resolve()
    rec: Dict[str, Any] = {
        "relative_path": rel_path.replace("\\", "/"),
        "exists": path.is_file(),
        "bytes": None,
        "line_count": None,
        "keyword_hits": {},
        "note": None,
    }
    if not rec["exists"]:
        rec["note"] = "missing_on_disk"
        return rec
    try:
        st = path.stat()
        rec["bytes"] = int(st.st_size)
        text = path.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()
        rec["line_count"] = len(lines)
        for name, pat in KEYWORD_PATTERNS:
            rec["keyword_hits"][name] = sum(1 for ln in lines if pat.search(ln))
    except Exception as exc:
        rec["note"] = f"read_error:{exc!r}"
    return rec


def get_nested(d: Optional[Dict[str, Any]], *keys: str) -> Any:
    cur: Any = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def validate_restore_scope(rs: Any) -> Tuple[bool, List[str], Dict[str, Any]]:
    errs: List[str] = []
    detail: Dict[str, Any] = {"restore_scope_object": rs}
    if not isinstance(rs, dict):
        errs.append("restore_scope_missing_or_not_object")
        return False, errs, detail

    expected = {
        "restore_family": "old_short",
        "restore_mode": "MONITORING_OR_ACTIVE_PAPER_ONLY",
        "capital_change_allowed": False,
        "live_trading_allowed": False,
        "real_orders_allowed": False,
        "runtime_enable_allowed_now": False,
        "patch_apply_allowed_now": False,
    }
    for k, v in expected.items():
        if rs.get(k) != v:
            errs.append(f"restore_scope_field_mismatch:{k}:observed={rs.get(k)!r}:expected={v!r}")
    ok = len(errs) == 0
    detail["expected_fields"] = expected
    return ok, errs, detail


def build_policy_gates(
    prior_ok: bool,
    scope_ok: bool,
    status_ok: bool,
) -> List[Dict[str, Any]]:
    return [
        {
            "gate": "REPO_ONLY_PATCH_PREVIEW",
            "required": True,
            "observed": True,
            "status": "PASS",
            "evidence": "Module only reads prior plan, inspects paths, writes patch-preview artifacts under its output directory.",
        },
        {
            "gate": "PRIOR_PLAN_STATUS_MATCH",
            "required": True,
            "observed": prior_ok,
            "status": "PASS" if prior_ok else "FAIL",
            "evidence": f"plan_status must equal {REQUIRED_PLAN_STATUS}.",
        },
        {
            "gate": "RESTORE_SCOPE_UNCHANGED",
            "required": True,
            "observed": scope_ok,
            "status": "PASS" if scope_ok else "FAIL",
            "evidence": "guarded_reenable_plan.restore_scope must remain old_short monitoring/active-paper only with all execution/capital/live/real-order flags false.",
        },
        {
            "gate": "NO_TARGET_FILE_MUTATION",
            "required": True,
            "observed": True,
            "status": "PASS",
            "evidence": "This module does not open target paths for write or apply patches.",
        },
        {
            "gate": "NO_RUNTIME_LAUNCHER_OR_PROCESS_START",
            "required": True,
            "observed": True,
            "status": "PASS",
            "evidence": "No launcher invocation; git/status only via read-only subprocess for reporting.",
        },
        {
            "gate": "GIT_STATUS_READABLE",
            "required": False,
            "observed": status_ok,
            "status": "PASS" if status_ok else "WARN",
            "evidence": "git status used for governance snapshot only.",
        },
    ]


def build_proposed_patch_preview(
    inspected: List[Dict[str, Any]],
    old_short_status: Any,
) -> Dict[str, Any]:
    """Governance-only description of likely future edit surfaces. No trading logic."""
    family_tool = []
    framework_json = []
    runtime_boundary = []
    for row in inspected:
        rp = row["relative_path"]
        if rp.startswith("tools/") and "runtime_family" in rp or "family_registry" in rp:
            family_tool.append(rp)
        elif rp.startswith("edge_factory_os_framework/"):
            framework_json.append(rp)
        elif rp.startswith("src/"):
            runtime_boundary.append(rp)

    return {
        "intent": (
            "Future approved patches would align repo-side monitoring/registry/gate surfaces "
            "with the prior guarded plan scope (old_short, monitoring or active paper only, "
            "no capital, no live, no real orders). This preview does not prescribe parameter "
            "or strategy changes."
        ),
        "likely_future_patch_surfaces": {
            "family_monitor_registry_tools_py": sorted(set(family_tool)),
            "framework_status_policy_registry_json": sorted(set(framework_json)),
            "launcher_paper_logger_regression_src_py": sorted(set(runtime_boundary)),
        },
        "per_file_roles": [
            {
                "relative_path": row["relative_path"],
                "exists": row["exists"],
                "role_hint": (
                    "framework_status_or_policy_record"
                    if row["relative_path"].startswith("edge_factory_os_framework/")
                    else (
                        "repo_tool_family_or_panel"
                        if row["relative_path"].startswith("tools/")
                        else "runtime_adjacent_gate_or_paper_module"
                    )
                ),
            }
            for row in inspected
        ],
        "old_short_status_snapshot_for_context": old_short_status,
        "explicit_exclusions_from_this_module": [
            "No edits applied.",
            "No diff applied to working tree.",
            "No runtime configuration mutation.",
        ],
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    git_state = inspect_git()
    plan = load_json(PLAN_JSON)

    prior_validation: Dict[str, Any] = {
        "plan_path": rel(PLAN_JSON),
        "plan_loaded": plan is not None,
        "plan_status_observed": None,
        "plan_status_required": REQUIRED_PLAN_STATUS,
        "plan_status_match": False,
        "restore_scope_validation": {},
    }

    failed_gates: List[str] = []
    plan_status_match = False
    scope_ok = False
    old_short_status: Any = None

    if plan is None:
        failed_gates.append("PRIOR_PLAN_MISSING_OR_UNREADABLE")
    else:
        ps = plan.get("plan_status")
        prior_validation["plan_status_observed"] = ps
        plan_status_match = ps == REQUIRED_PLAN_STATUS
        prior_validation["plan_status_match"] = plan_status_match
        if not plan_status_match:
            failed_gates.append("PRIOR_PLAN_STATUS_MISMATCH")

        rs = get_nested(plan, "guarded_reenable_plan", "restore_scope")
        scope_ok, scope_errs, scope_detail = validate_restore_scope(rs)
        prior_validation["restore_scope_validation"] = {
            "ok": scope_ok,
            "errors": scope_errs,
            "detail": scope_detail,
        }
        if not scope_ok:
            failed_gates.append("RESTORE_SCOPE_MISMATCH")

        old_short_status = get_nested(plan, "guarded_reenable_plan", "old_short_status")

    inspected = [inspect_file(p) for p in INSPECT_REL_PATHS]
    missing_inspect = [x["relative_path"] for x in inspected if not x["exists"]]
    if missing_inspect:
        failed_gates.append("INSPECT_TARGET_MISSING:" + ",".join(missing_inspect))

    prior_ok = (
        plan is not None
        and prior_validation.get("plan_status_match")
        and prior_validation.get("restore_scope_validation", {}).get("ok")
        and not missing_inspect
    )

    policy_gates = build_policy_gates(
        prior_ok=bool(prior_validation.get("plan_status_match")),
        scope_ok=bool(prior_validation.get("restore_scope_validation", {}).get("ok")),
        status_ok=bool(git_state.get("status_ok")),
    )

    if prior_ok:
        patch_preview_status = "OLD_SHORT_GUARDED_RUNTIME_REENABLE_PATCH_PREVIEW_READY_NO_APPLY"
        severity = "INFO"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        final_decision = "PATCH_PREVIEW_READY_REQUIRE_FINAL_EXECUTION_APPROVAL_BEFORE_APPLY"
        next_action = "STOP_OR_BUILD_FINAL_EXECUTION_APPROVAL_NO_RUNTIME_ACTION"
        next_module = "edge_factory_os_old_short_final_runtime_reenable_execution_approval_v1.py"
    else:
        patch_preview_status = "OLD_SHORT_GUARDED_RUNTIME_REENABLE_PATCH_PREVIEW_BLOCKED"
        severity = "HIGH"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        final_decision = "STOP_FIX_PRIOR_PLAN_OR_SCOPE_DO_NOT_APPLY_PATCH"
        next_action = "STOP_NO_RUNTIME_ACTION_REVIEW_PRIOR_PLAN_AND_DISK_PATHS"
        next_module = "edge_factory_os_old_short_guarded_runtime_reenable_plan_v1.py"

    payload: Dict[str, Any] = {
        "module": "edge_factory_os_old_short_guarded_runtime_reenable_patch_preview_v1.py",
        "generated_at_utc": NOW_UTC,
        "patch_preview_status": patch_preview_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "old_short_status": old_short_status,
        "restore_scope": get_nested(plan, "guarded_reenable_plan", "restore_scope")
        if plan
        else None,
        "prior_plan_validation": prior_validation,
        "inspected_files": inspected,
        "proposed_patch_preview": build_proposed_patch_preview(inspected, old_short_status),
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "safety_flags": SAFETY_FLAGS,
        "policy_gates": policy_gates,
        "failed_gates": sorted(set(failed_gates)),
        "git_state": git_state,
        "outputs": {
            "json": str(OUT_JSON),
            "txt": str(OUT_TXT),
        },
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines_txt: List[str] = [
        "Edge Factory OS — old_short guarded runtime re-enable PATCH PREVIEW (repo-only, no apply)",
        f"generated_at_utc: {NOW_UTC}",
        f"patch_preview_status: {patch_preview_status}",
        f"severity: {severity}",
        f"allowed_scope: {allowed_scope}",
        f"final_decision: {final_decision}",
        f"next_action: {next_action}",
        f"next_module: {next_module}",
        "",
        "prior_plan_validation (summary):",
        json.dumps(prior_validation, indent=2, ensure_ascii=False),
        "",
        "failed_gates:",
        json.dumps(payload["failed_gates"], indent=2, ensure_ascii=False),
        "",
        "old_short_status:",
        json.dumps(old_short_status, indent=2, ensure_ascii=False),
        "",
        "restore_scope:",
        json.dumps(payload["restore_scope"], indent=2, ensure_ascii=False),
        "",
        "inspected_files (summary paths):",
        ", ".join(x["relative_path"] for x in inspected),
        "",
        "proposed_patch_preview (JSON):",
        json.dumps(payload["proposed_patch_preview"], indent=2, ensure_ascii=False),
        "",
        "forbidden_actions:",
        "\n".join(f"- {x}" for x in FORBIDDEN_ACTIONS),
        "",
        "safety_flags:",
        json.dumps(SAFETY_FLAGS, indent=2, sort_keys=True, ensure_ascii=False),
        "",
        "git_state:",
        json.dumps(git_state, indent=2, ensure_ascii=False),
    ]
    OUT_TXT.write_text("\n".join(lines_txt) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_TXT}")
    print(f"patch_preview_status={patch_preview_status}")


if __name__ == "__main__":
    main()
