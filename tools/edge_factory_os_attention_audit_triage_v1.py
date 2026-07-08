from __future__ import annotations

import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]

AUDIT_JSON = (
    REPO_ROOT
    / "edge_factory_os_full_system_read_only_audit"
    / "full_system_read_only_audit_latest.json"
)

OUT_DIR = REPO_ROOT / "edge_factory_os_attention_audit_triage"
OUT_JSON = OUT_DIR / "attention_audit_triage_latest.json"
OUT_TXT = OUT_DIR / "attention_audit_triage_latest.txt"

TRIAGE_CATEGORIES = {
    "broken_paths",
    "next_module_chain",
    "old_short_governance_chain",
    "duplicate_superseded_modules",
}

DEFERRED_CATEGORIES = {
    "mutation_without_explicit_gate",
    "launcher_runtime_risk_heuristic",
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
    "Do not fix anything from this triage module.",
    "Do not modify target files.",
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


def load_audit() -> Dict[str, Any]:
    with AUDIT_JSON.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise RuntimeError("Audit JSON root is not object")
    return data


def compact_issue(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "issue_id": row.get("issue_id"),
        "category": row.get("category"),
        "severity": row.get("severity"),
        "path": row.get("path"),
        "evidence": row.get("evidence"),
        "recommendation": row.get("recommendation"),
    }


def classify_selected_issue(row: Dict[str, Any]) -> Dict[str, Any]:
    category = row.get("category")
    path = str(row.get("path") or "")
    evidence = str(row.get("evidence") or "")

    can_preview_fix = False
    fix_class = "manual_review"
    reason = "Needs manual review before any mutation."

    if category == "broken_paths":
        can_preview_fix = True
        fix_class = "path_reference_fix_preview"
        reason = "Broken path issues can usually be fixed by validating path existence and producing a narrow patch preview."

    elif category == "next_module_chain":
        can_preview_fix = True
        fix_class = "next_module_chain_preview"
        reason = "next_module chain issues are narrow metadata/linkage fixes, suitable for preview-first repair."

    elif category == "old_short_governance_chain":
        can_preview_fix = True
        fix_class = "old_short_governance_chain_preview"
        reason = "old_short chain should be fixed through preview-only governance repair, not runtime action."

    elif category == "duplicate_superseded_modules":
        can_preview_fix = False
        fix_class = "cleanup_requires_manual_hygiene_approval"
        reason = "Duplicate/superseded modules may require archive/delete decisions; do not clean without explicit hygiene approval."

    return {
        "issue": compact_issue(row),
        "fix_class": fix_class,
        "can_build_preview_fix": can_preview_fix,
        "reason": reason,
        "target_path": path,
        "evidence": evidence,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    audit = load_audit()
    issues = audit.get("issue_inventory", [])
    if not isinstance(issues, list):
        raise RuntimeError("issue_inventory missing or not list")

    counts_by_category = Counter(str(row.get("category")) for row in issues if isinstance(row, dict))
    counts_by_severity = Counter(str(row.get("severity")) for row in issues if isinstance(row, dict))

    selected = [
        row for row in issues
        if isinstance(row, dict) and row.get("category") in TRIAGE_CATEGORIES
    ]

    deferred = [
        row for row in issues
        if isinstance(row, dict) and row.get("category") in DEFERRED_CATEGORIES
    ]

    grouped_selected: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in selected:
        grouped_selected[str(row.get("category"))].append(compact_issue(row))

    classified = [classify_selected_issue(row) for row in selected]

    safe_fix_candidates = [
        row for row in classified
        if row["can_build_preview_fix"] is True
    ]

    requires_manual_review = [
        row for row in classified
        if row["can_build_preview_fix"] is False
    ]

    recommended_fix_order = [
        {
            "order": 1,
            "category": "broken_paths",
            "action": "Build preview-only repair module for broken path references. No file mutation until preview reviewed.",
        },
        {
            "order": 2,
            "category": "next_module_chain",
            "action": "Build preview-only repair module for broken next_module references.",
        },
        {
            "order": 3,
            "category": "old_short_governance_chain",
            "action": "Review old_short apply/approval chain. Do not run old_short runtime apply blindly.",
        },
        {
            "order": 4,
            "category": "duplicate_superseded_modules",
            "action": "Manual hygiene gate only. Do not delete/move/archive in this phase.",
        },
        {
            "order": 5,
            "category": "mutation_without_explicit_gate",
            "action": "Deferred. Triage false positives versus real mutators after concrete chain/path issues are clear.",
        },
        {
            "order": 6,
            "category": "launcher_runtime_risk_heuristic",
            "action": "Deferred. Triage only after mutation category is classified. Runtime/launcher remains blocked.",
        },
    ]

    triage_status = "ATTENTION_AUDIT_TRIAGE_READY_NO_FIXES_APPLIED"

    result = {
        "module": "edge_factory_os_attention_audit_triage_v1.py",
        "generated_at_utc": now_iso(),
        "repo_root": str(REPO_ROOT),
        "audit_input": {
            "path": rel_repo(AUDIT_JSON),
            "audit_status": audit.get("audit_status"),
            "issue_count": audit.get("issue_count"),
            "critical_issue_count": audit.get("critical_issue_count"),
            "attention_issue_count": audit.get("attention_issue_count"),
            "info_issue_count": audit.get("info_issue_count"),
        },
        "triage_status": triage_status,
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": "REVIEW_TRIAGE_BEFORE_BUILDING_FIX_MODULES",
        "selected_issue_count": len(selected),
        "deferred_issue_count": len(deferred),
        "issue_count_by_category": dict(counts_by_category),
        "issue_count_by_severity": dict(counts_by_severity),
        "broken_paths": grouped_selected.get("broken_paths", []),
        "next_module_chain_issues": grouped_selected.get("next_module_chain", []),
        "old_short_governance_chain_issues": grouped_selected.get("old_short_governance_chain", []),
        "duplicate_superseded_modules": grouped_selected.get("duplicate_superseded_modules", []),
        "safe_fix_candidates": safe_fix_candidates,
        "requires_manual_review": requires_manual_review,
        "deferred_categories": {
            "mutation_without_explicit_gate": counts_by_category.get("mutation_without_explicit_gate", 0),
            "launcher_runtime_risk_heuristic": counts_by_category.get("launcher_runtime_risk_heuristic", 0),
        },
        "recommended_fix_order": recommended_fix_order,
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "git_state": git_state(),
        "next_action": "REVIEW_BROKEN_PATHS_AND_CHAIN_ISSUES_FIRST",
        "next_module": "edge_factory_os_broken_paths_and_chain_fix_preview_v1.py",
        "outputs": {
            "json": str(OUT_JSON),
            "txt": str(OUT_TXT),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines: List[str] = []
    lines.append("EDGE FACTORY OS ATTENTION AUDIT TRIAGE v1")
    lines.append("=" * 100)
    lines.append(f"triage_status: {triage_status}")
    lines.append(f"allowed_scope: {result['allowed_scope']}")
    lines.append(f"final_decision: {result['final_decision']}")
    lines.append(f"selected_issue_count: {result['selected_issue_count']}")
    lines.append(f"deferred_issue_count: {result['deferred_issue_count']}")
    lines.append(f"next_action: {result['next_action']}")
    lines.append(f"next_module: {result['next_module']}")
    lines.append("")
    lines.append("AUDIT INPUT")
    lines.append("-" * 100)
    lines.append(json.dumps(result["audit_input"], indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("ISSUE COUNT BY CATEGORY")
    lines.append("-" * 100)
    lines.append(json.dumps(result["issue_count_by_category"], indent=2, sort_keys=True, ensure_ascii=False))
    lines.append("")
    lines.append("SELECTED TRIAGE CATEGORIES")
    lines.append("-" * 100)
    lines.append(f"broken_paths: {len(result['broken_paths'])}")
    lines.append(f"next_module_chain: {len(result['next_module_chain_issues'])}")
    lines.append(f"old_short_governance_chain: {len(result['old_short_governance_chain_issues'])}")
    lines.append(f"duplicate_superseded_modules: {len(result['duplicate_superseded_modules'])}")
    lines.append("")
    lines.append("BROKEN PATHS")
    lines.append("-" * 100)
    lines.append(json.dumps(result["broken_paths"], indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("NEXT MODULE CHAIN ISSUES")
    lines.append("-" * 100)
    lines.append(json.dumps(result["next_module_chain_issues"], indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("OLD_SHORT GOVERNANCE CHAIN ISSUES")
    lines.append("-" * 100)
    lines.append(json.dumps(result["old_short_governance_chain_issues"], indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("DUPLICATE / SUPERSEDED MODULES")
    lines.append("-" * 100)
    lines.append(json.dumps(result["duplicate_superseded_modules"], indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("RECOMMENDED FIX ORDER")
    lines.append("-" * 100)
    lines.append(json.dumps(recommended_fix_order, indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("DEFERRED CATEGORIES")
    lines.append("-" * 100)
    lines.append(json.dumps(result["deferred_categories"], indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("FORBIDDEN ACTIONS")
    lines.append("-" * 100)
    for item in FORBIDDEN_ACTIONS:
        lines.append(f"- {item}")

    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"triage_status: {triage_status}")
    print(f"selected_issue_count: {len(selected)}")
    print(f"deferred_issue_count: {len(deferred)}")
    print(f"broken_paths: {len(result['broken_paths'])}")
    print(f"next_module_chain: {len(result['next_module_chain_issues'])}")
    print(f"old_short_governance_chain: {len(result['old_short_governance_chain_issues'])}")
    print(f"duplicate_superseded_modules: {len(result['duplicate_superseded_modules'])}")
    print(f"next_module: {result['next_module']}")


if __name__ == "__main__":
    main()