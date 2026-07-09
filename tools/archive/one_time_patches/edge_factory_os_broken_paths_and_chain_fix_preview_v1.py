from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]

TRIAGE_JSON = (
    REPO_ROOT
    / "edge_factory_os_attention_audit_triage"
    / "attention_audit_triage_latest.json"
)

OUT_DIR = REPO_ROOT / "edge_factory_os_broken_paths_and_chain_fix_preview"
OUT_JSON = OUT_DIR / "broken_paths_and_chain_fix_preview_latest.json"
OUT_TXT = OUT_DIR / "broken_paths_and_chain_fix_preview_latest.txt"

SAFETY_FLAGS = {
    "repo_only": True,
    "preview_only": True,
    "runtime_touch_allowed": False,
    "launcher_allowed": False,
    "runtime_patch_allowed": False,
    "backup_delete_allowed": False,
    "backup_move_allowed": False,
    "gitignore_change_allowed": False,
    "strategy_research_allowed": False,
    "candidate_generation_allowed": False,
    "family_release_allowed": False,
    "capital_change_allowed": False,
    "active_paper_allowed": False,
    "live_allowed": False,
    "real_orders_allowed": False,
    "file_delete_allowed": False,
    "file_move_allowed": False,
    "execution_allowed": False,
}

FORBIDDEN_ACTIONS = [
    "Do not modify target files.",
    "Do not apply fixes.",
    "Do not delete or move backup files.",
    "Do not change .gitignore.",
    "Do not use git add -f.",
    "Do not run launcher.",
    "Do not touch runtime.",
    "Do not start processes.",
    "Do not run strategy research.",
    "Do not generate candidates.",
    "Do not change capital.",
    "Do not enable active paper.",
    "Do not enable live trading.",
    "Do not enable or send real orders.",
    "Do not touch holdout.",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel_repo(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def run_cmd(args: List[str], timeout: int = 30) -> Dict[str, Any]:
    try:
        p = subprocess.run(
            args,
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": p.returncode == 0,
            "returncode": p.returncode,
            "stdout": p.stdout,
            "stderr": p.stderr,
        }
    except Exception as exc:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": repr(exc),
        }


def git_state() -> Dict[str, Any]:
    st = run_cmd(["git", "-C", str(REPO_ROOT), "status", "--short"])
    head = run_cmd(["git", "-C", str(REPO_ROOT), "rev-parse", "--short", "HEAD"])
    last = run_cmd(["git", "-C", str(REPO_ROOT), "log", "-1", "--pretty=%h %s"])
    lines = [x.strip().replace("\\", "/") for x in st["stdout"].splitlines() if x.strip()] if st["ok"] else []

    return {
        "status_ok": st["ok"],
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


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root is not object: {path}")
    return data


def issue_obj(row: Any) -> Dict[str, Any]:
    if not isinstance(row, dict):
        return {}
    return {
        "issue_id": row.get("issue_id"),
        "path": row.get("path"),
        "evidence": row.get("evidence"),
        "recommendation": row.get("recommendation"),
        "category": row.get("category"),
        "severity": row.get("severity"),
    }


def classify_broken_path(row: Dict[str, Any]) -> Dict[str, Any]:
    issue_id = str(row.get("issue_id") or "")
    path = str(row.get("path") or "")
    evidence = str(row.get("evidence") or "")
    recommendation = str(row.get("recommendation") or "")

    classification = "manual_review"
    proposed_action = "Review manually before any mutation."
    apply_recommended_now = False
    safe_preview_fix_possible = False
    reason = "Default conservative classification."

    if "manual_approval_json" in issue_id or "manual_backup_hygiene_approval" in evidence:
        classification = "expected_absent_manual_approval_artifact"
        proposed_action = (
            "Do not create or fake approval. Leave absent until user explicitly approves backup hygiene."
        )
        reason = "Manual approval artifact is intentionally absent; creating it would bypass governance."

    elif "old_short_guarded_runtime_reenable_plan" in path or "old_short_reactivation_gate" in path:
        classification = "false_positive_embedded_text_scan_or_stale_report"
        proposed_action = (
            "Do not patch historical report JSON. Regenerate relevant report only if needed."
        )
        reason = (
            "Broken path is inside scanned hit text from old_short reference/control-surface reports, "
            "not necessarily a live machine path used by runtime."
        )

    elif "BROKEN_LAB_PATH" in issue_id:
        classification = "possible_stale_report_artifact"
        proposed_action = (
            "Prefer regenerating source report artifact rather than patching JSON text."
        )
        reason = "Lab path warning comes from report text; should not be blindly edited."

    elif "BROKEN_PATH" in issue_id:
        classification = "real_missing_path_candidate"
        proposed_action = (
            "Build a narrow preview that converts absolute machine path to repo-relative metadata only if producer owns the field."
        )
        safe_preview_fix_possible = True
        reason = "This may be a real missing absolute path, but still requires producer-aware preview."

    return {
        "issue": issue_obj(row),
        "classification": classification,
        "safe_preview_fix_possible": safe_preview_fix_possible,
        "apply_recommended_now": apply_recommended_now,
        "proposed_action": proposed_action,
        "reason": reason,
        "recommendation_from_audit": recommendation,
    }


def classify_next_module(row: Dict[str, Any]) -> Dict[str, Any]:
    issue_id = str(row.get("issue_id") or "")
    path = str(row.get("path") or "")
    evidence = str(row.get("evidence") or "")

    missing_module = ""
    if "next_module='" in evidence:
        try:
            missing_module = evidence.split("next_module='", 1)[1].split("'", 1)[0]
        except Exception:
            missing_module = ""

    classification = "planned_future_module_or_missing_tool"
    proposed_action = "Review whether module should be built or next_module should point elsewhere."
    safe_preview_fix_possible = False
    apply_recommended_now = False
    reason = "Missing next_module can be intentional queue state."

    if "external_audit_response_integrator_or_source_panel_info_review" in missing_module:
        classification = "missing_future_external_audit_review_module"
        proposed_action = (
            "Do not patch away. Either build the named repo-only module later or update queue via explicit governance decision."
        )
        reason = "This appears to be a planned future module; not a broken runtime path."

    elif "repo_only_status_dashboard_or_manual_hygiene_approval_gate" in missing_module:
        classification = "missing_future_status_dashboard_or_hygiene_gate_module"
        proposed_action = (
            "Do not patch old report. Build the module later or supersede via new status-dashboard gate."
        )
        reason = "This is a planned next module from repo-only standard stack refresh."

    existing_tool_path = REPO_ROOT / "tools" / missing_module if missing_module else None
    existing_tool_found = bool(existing_tool_path and existing_tool_path.exists())

    return {
        "issue": issue_obj(row),
        "missing_module": missing_module,
        "existing_tool_found": existing_tool_found,
        "classification": classification,
        "safe_preview_fix_possible": safe_preview_fix_possible,
        "apply_recommended_now": apply_recommended_now,
        "proposed_action": proposed_action,
        "reason": reason,
    }


def classify_old_short(row: Dict[str, Any]) -> Dict[str, Any]:
    path = str(row.get("path") or "")
    evidence = str(row.get("evidence") or "")

    return {
        "issue": issue_obj(row),
        "classification": "expected_absent_apply_artifact_until_guarded_apply_runs",
        "safe_preview_fix_possible": False,
        "apply_recommended_now": False,
        "proposed_action": (
            "Do not fabricate apply artifact. It should appear only if old_short guarded apply module is actually run "
            "and safely produces output."
        ),
        "reason": (
            "old_short apply artifact absence is expected because guarded apply has not been executed. "
            "This is governance state, not a path repair."
        ),
        "artifact_path": path,
        "evidence": evidence,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    triage = load_json(TRIAGE_JSON)

    broken_paths = triage.get("broken_paths", [])
    next_module_chain = triage.get("next_module_chain_issues", [])
    old_short_chain = triage.get("old_short_governance_chain_issues", [])

    if not isinstance(broken_paths, list):
        broken_paths = []
    if not isinstance(next_module_chain, list):
        next_module_chain = []
    if not isinstance(old_short_chain, list):
        old_short_chain = []

    broken_classified = [
        classify_broken_path(x) for x in broken_paths if isinstance(x, dict)
    ]
    next_module_classified = [
        classify_next_module(x) for x in next_module_chain if isinstance(x, dict)
    ]
    old_short_classified = [
        classify_old_short(x) for x in old_short_chain if isinstance(x, dict)
    ]

    real_missing_required_artifacts = [
        x for x in broken_classified
        if x["classification"] == "real_missing_path_candidate"
    ]
    false_positive_or_stale_reports = [
        x for x in broken_classified
        if x["classification"] in {
            "false_positive_embedded_text_scan_or_stale_report",
            "possible_stale_report_artifact",
        }
    ]
    expected_absent_governance_artifacts = [
        x for x in broken_classified
        if x["classification"] == "expected_absent_manual_approval_artifact"
    ] + old_short_classified

    safe_preview_fix_candidates = [
        x for x in broken_classified + next_module_classified + old_short_classified
        if x.get("safe_preview_fix_possible") is True
    ]

    apply_recommended_now = [
        x for x in broken_classified + next_module_classified + old_short_classified
        if x.get("apply_recommended_now") is True
    ]

    preview_status = "BROKEN_PATHS_AND_CHAIN_FIX_PREVIEW_READY_NO_APPLY"

    if apply_recommended_now:
        final_decision = "REVIEW_PREVIEW_BEFORE_APPLY"
        next_action = "REVIEW_SAFE_FIX_CANDIDATES_BEFORE_APPLY"
        next_module = "edge_factory_os_broken_paths_and_chain_fix_apply_v1.py"
    else:
        final_decision = "NO_APPLY_RECOMMENDED_CLASSIFY_AS_EXPECTED_STALE_OR_FUTURE_MODULES"
        next_action = "REVIEW_TRIAGE_THEN_DECIDE_WHETHER_TO_BUILD_MISSING_FUTURE_MODULES"
        next_module = "edge_factory_os_attention_issue_policy_classifier_v1.py"

    result = {
        "module": "edge_factory_os_broken_paths_and_chain_fix_preview_v1.py",
        "generated_at_utc": now_iso(),
        "repo_root": str(REPO_ROOT),
        "triage_input": {
            "path": rel_repo(TRIAGE_JSON),
            "triage_status": triage.get("triage_status"),
            "selected_issue_count": triage.get("selected_issue_count"),
            "deferred_issue_count": triage.get("deferred_issue_count"),
        },
        "preview_status": preview_status,
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "counts": {
            "broken_paths": len(broken_classified),
            "next_module_chain": len(next_module_classified),
            "old_short_governance_chain": len(old_short_classified),
            "real_missing_required_artifacts": len(real_missing_required_artifacts),
            "false_positive_or_stale_reports": len(false_positive_or_stale_reports),
            "expected_absent_governance_artifacts": len(expected_absent_governance_artifacts),
            "safe_preview_fix_candidates": len(safe_preview_fix_candidates),
            "apply_recommended_now": len(apply_recommended_now),
        },
        "broken_paths_classified": broken_classified,
        "next_module_chain_classified": next_module_classified,
        "old_short_governance_chain_classified": old_short_classified,
        "safe_preview_fix_candidates": safe_preview_fix_candidates,
        "apply_recommended_now": apply_recommended_now,
        "recommended_policy": [
            {
                "category": "manual_backup_hygiene_approval_missing",
                "decision": "EXPECTED_ABSENT_DO_NOT_CREATE",
                "reason": "Approval artifacts must only appear after explicit user approval.",
            },
            {
                "category": "old_short_apply_artifact_absent",
                "decision": "EXPECTED_ABSENT_UNTIL_GUARDED_APPLY_RUNS",
                "reason": "Do not fabricate apply output. old_short apply remains unrun.",
            },
            {
                "category": "old_short_report_embedded_path_hits",
                "decision": "STALE_REPORT_OR_FALSE_POSITIVE_DO_NOT_PATCH",
                "reason": "These are scanned text hits inside report JSON; patching reports is not the correct repair.",
            },
            {
                "category": "missing_next_modules",
                "decision": "BUILD_OR_SUPERSEDE_VIA_EXPLICIT_NEXT_MODULE_DECISION",
                "reason": "Do not silently rewrite next_module fields in historical artifacts.",
            },
        ],
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "git_state": git_state(),
        "outputs": {
            "json": str(OUT_JSON),
            "txt": str(OUT_TXT),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines: List[str] = []
    lines.append("EDGE FACTORY OS BROKEN PATHS AND CHAIN FIX PREVIEW v1")
    lines.append("=" * 100)
    lines.append(f"preview_status: {preview_status}")
    lines.append(f"allowed_scope: {result['allowed_scope']}")
    lines.append(f"final_decision: {final_decision}")
    lines.append(f"next_action: {next_action}")
    lines.append(f"next_module: {next_module}")
    lines.append("")
    lines.append("COUNTS")
    lines.append("-" * 100)
    lines.append(json.dumps(result["counts"], indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("BROKEN PATHS CLASSIFIED")
    lines.append("-" * 100)
    lines.append(json.dumps(broken_classified, indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("NEXT MODULE CHAIN CLASSIFIED")
    lines.append("-" * 100)
    lines.append(json.dumps(next_module_classified, indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("OLD_SHORT GOVERNANCE CHAIN CLASSIFIED")
    lines.append("-" * 100)
    lines.append(json.dumps(old_short_classified, indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("RECOMMENDED POLICY")
    lines.append("-" * 100)
    lines.append(json.dumps(result["recommended_policy"], indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("FORBIDDEN ACTIONS")
    lines.append("-" * 100)
    for item in FORBIDDEN_ACTIONS:
        lines.append(f"- {item}")

    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"preview_status: {preview_status}")
    print(f"final_decision: {final_decision}")
    print(f"next_action: {next_action}")
    print(f"next_module: {next_module}")
    print("counts:")
    print(json.dumps(result["counts"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()