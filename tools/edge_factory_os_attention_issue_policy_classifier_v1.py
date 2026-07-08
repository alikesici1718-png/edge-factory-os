from __future__ import annotations

import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]

AUDIT_JSON = (
    REPO_ROOT
    / "edge_factory_os_full_system_read_only_audit"
    / "full_system_read_only_audit_latest.json"
)

TRIAGE_JSON = (
    REPO_ROOT
    / "edge_factory_os_attention_audit_triage"
    / "attention_audit_triage_latest.json"
)

BROKEN_CHAIN_PREVIEW_JSON = (
    REPO_ROOT
    / "edge_factory_os_broken_paths_and_chain_fix_preview"
    / "broken_paths_and_chain_fix_preview_latest.json"
)

OUT_DIR = REPO_ROOT / "edge_factory_os_attention_issue_policy_classifier"
OUT_JSON = OUT_DIR / "attention_issue_policy_classifier_latest.json"
OUT_TXT = OUT_DIR / "attention_issue_policy_classifier_latest.txt"

CLASSIFY_CATEGORIES = {
    "mutation_without_explicit_gate",
    "launcher_runtime_risk_heuristic",
    "duplicate_superseded_modules",
}

SAFETY_FLAGS = {
    "repo_only": True,
    "classification_only": True,
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
    "Do not run old_short guarded apply.",
]


RUNTIME_SURFACE_HINTS = [
    "launcher",
    "autopilot",
    "supervisor",
    "command_center",
    "process_watchdog",
    "paper_logger",
    "live_paper",
    "live",
    "real_order",
    "risk_manager",
    "runtime",
]

DANGEROUS_MUTATION_HINTS = [
    "shutil.rmtree",
    "os.remove",
    "unlink(",
    ".unlink",
    "rmdir(",
    ".rmdir",
    "shutil.move",
    "replace(",
    "rename(",
    "git add -f",
    "subprocess.run",
    "Popen",
    "startfile",
]

SAFE_GOVERNANCE_HINTS = [
    "read_only",
    "repo_only",
    "preview_only",
    "classification_only",
    "allowed_scope",
    "safety_flags",
    "forbidden_actions",
    "runtime_touch_allowed",
    "launcher_allowed",
    "live_allowed",
    "real_orders_allowed",
    "capital_change_allowed",
]

WRITE_HINTS = [
    "write_text",
    "write_bytes",
    "json.dump",
    "open(",
    "Set-Content",
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
        "old_short_guarded_apply_untracked": any(
            "tools/edge_factory_os_old_short_guarded_runtime_reenable_apply_v1.py" in x
            for x in lines
        ),
        "universe_guard_review_required": any(
            "tools/edge_factory_os_universe_coverage_guard_v1.py" in x
            for x in lines
        ),
    }


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def read_text_for_path(path_str: str) -> str:
    if not path_str:
        return ""
    p = REPO_ROOT / path_str.replace("/", "\\")
    try:
        if p.is_file():
            return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    return ""


def compact_issue(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "issue_id": row.get("issue_id"),
        "category": row.get("category"),
        "severity": row.get("severity"),
        "path": row.get("path"),
        "evidence": row.get("evidence"),
        "recommendation": row.get("recommendation"),
    }


def classify_mutation_issue(row: Dict[str, Any]) -> Dict[str, Any]:
    path = str(row.get("path") or "").replace("\\", "/")
    issue_id = str(row.get("issue_id") or "")
    evidence = str(row.get("evidence") or "")
    recommendation = str(row.get("recommendation") or "")
    path_l = path.lower()
    text = read_text_for_path(path)
    text_l = text.lower()
    evidence_l = evidence.lower() + " " + recommendation.lower() + " " + issue_id.lower()

    classification = "mutation_policy_review_required"
    risk_level = "ATTENTION"
    apply_recommended_now = False
    preview_fix_candidate = False
    reason = "Mutation heuristic requires manual policy classification."

    has_safe_governance = any(h in text_l or h in evidence_l for h in SAFE_GOVERNANCE_HINTS)
    has_dangerous_hint = any(h.lower() in text_l or h.lower() in evidence_l for h in DANGEROUS_MUTATION_HINTS)
    has_write_hint = any(h.lower() in text_l or h.lower() in evidence_l for h in WRITE_HINTS)
    is_tool = path_l.startswith("tools/")
    is_src = path_l.startswith("src/")
    is_known_output_writer = "edge_factory_os_" in path_l and is_tool and has_write_hint

    if any(x in path_l for x in ["_preview_", "read_only_audit", "triage", "classifier"]):
        classification = "expected_repo_output_writer_preview_or_audit"
        risk_level = "INFO"
        reason = "Preview/audit/classifier modules legitimately write their own report artifacts; no target mutation implied."
        apply_recommended_now = False
        preview_fix_candidate = False

    elif is_known_output_writer and has_safe_governance and not has_dangerous_hint:
        classification = "guarded_governance_output_writer_likely_false_positive"
        risk_level = "INFO"
        reason = "Tool appears to write governance/report artifacts and carries safety/read-only/repo-only guards."
        apply_recommended_now = False
        preview_fix_candidate = False

    elif any(x in path_l for x in ["_apply_", "_repair_", "_patch_", "hygiene", "cleanup"]):
        classification = "mutating_tool_requires_gate_or_manual_approval"
        risk_level = "ATTENTION"
        reason = "Apply/repair/patch/hygiene modules may be legitimate but must remain behind explicit preview/approval gates."
        apply_recommended_now = False
        preview_fix_candidate = True

    elif is_src and any(x in path_l for x in RUNTIME_SURFACE_HINTS):
        classification = "runtime_surface_mutation_risk_requires_manual_review"
        risk_level = "ATTENTION"
        reason = "src runtime/launcher/paper/live/risk surface should not be patched automatically."
        apply_recommended_now = False
        preview_fix_candidate = False

    elif has_dangerous_hint:
        classification = "dangerous_mutation_pattern_requires_manual_review"
        risk_level = "ATTENTION"
        reason = "Potential delete/move/process/subprocess mutation pattern detected; requires manual review."
        apply_recommended_now = False
        preview_fix_candidate = False

    return {
        "issue": compact_issue(row),
        "classification": classification,
        "risk_level": risk_level,
        "apply_recommended_now": apply_recommended_now,
        "preview_fix_candidate": preview_fix_candidate,
        "reason": reason,
        "signals": {
            "has_safe_governance": has_safe_governance,
            "has_dangerous_hint": has_dangerous_hint,
            "has_write_hint": has_write_hint,
            "is_tool": is_tool,
            "is_src": is_src,
            "text_read": bool(text),
        },
    }


def classify_launcher_issue(row: Dict[str, Any]) -> Dict[str, Any]:
    path = str(row.get("path") or "").replace("\\", "/")
    issue_id = str(row.get("issue_id") or "")
    evidence = str(row.get("evidence") or "")
    recommendation = str(row.get("recommendation") or "")
    path_l = path.lower()
    text = read_text_for_path(path)
    text_l = text.lower()
    evidence_l = evidence.lower() + " " + recommendation.lower() + " " + issue_id.lower()

    classification = "launcher_runtime_policy_review_required"
    risk_level = "ATTENTION"
    apply_recommended_now = False
    preview_fix_candidate = False
    reason = "Launcher/runtime heuristic requires manual classification."

    has_safe_block_flags = all(x in text_l for x in ["launcher_allowed", "runtime_touch_allowed"]) or (
        "launcher_allowed" in evidence_l and "false" in evidence_l
    )
    has_launcher_start_hint = any(x in text_l or x in evidence_l for x in [
        "subprocess.run",
        "popen",
        "startfile",
        "launcher",
        "autopilot",
        "supervisor",
        "command_center",
    ])
    is_runtime_src = path_l.startswith("src/") and any(x in path_l for x in RUNTIME_SURFACE_HINTS)
    is_governance_tool = path_l.startswith("tools/edge_factory_os_")

    if is_governance_tool and has_safe_block_flags:
        classification = "guarded_launcher_reference_likely_false_positive"
        risk_level = "INFO"
        reason = "Governance tool appears to reference launcher/runtime while explicitly blocking it."
        apply_recommended_now = False
        preview_fix_candidate = False

    elif is_runtime_src:
        classification = "real_runtime_surface_requires_strict_manual_gate"
        risk_level = "ATTENTION"
        reason = "Runtime/launcher source surface should be reviewed manually; no automatic patch."
        apply_recommended_now = False
        preview_fix_candidate = False

    elif has_launcher_start_hint and not has_safe_block_flags:
        classification = "launcher_start_pattern_requires_manual_review"
        risk_level = "ATTENTION"
        reason = "Launcher/runtime start-like pattern detected without clear local block flags."
        apply_recommended_now = False
        preview_fix_candidate = False

    else:
        classification = "launcher_heuristic_unclassified_review_later"
        risk_level = "INFO"
        reason = "Heuristic match lacks enough evidence for immediate fix."
        apply_recommended_now = False
        preview_fix_candidate = False

    return {
        "issue": compact_issue(row),
        "classification": classification,
        "risk_level": risk_level,
        "apply_recommended_now": apply_recommended_now,
        "preview_fix_candidate": preview_fix_candidate,
        "reason": reason,
        "signals": {
            "has_safe_block_flags": has_safe_block_flags,
            "has_launcher_start_hint": has_launcher_start_hint,
            "is_runtime_src": is_runtime_src,
            "is_governance_tool": is_governance_tool,
            "text_read": bool(text),
        },
    }


def classify_duplicate_issue(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "issue": compact_issue(row),
        "classification": "duplicate_superseded_module_requires_manual_hygiene_gate",
        "risk_level": "INFO",
        "apply_recommended_now": False,
        "preview_fix_candidate": False,
        "reason": "Do not delete/move/archive duplicate modules without explicit hygiene approval.",
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    audit = load_json(AUDIT_JSON)
    triage = load_json(TRIAGE_JSON)
    broken_preview = load_json(BROKEN_CHAIN_PREVIEW_JSON)

    if audit is None:
        raise RuntimeError(f"Missing/unreadable audit JSON: {AUDIT_JSON}")

    issue_inventory = audit.get("issue_inventory")
    if not isinstance(issue_inventory, list):
        raise RuntimeError("audit issue_inventory missing or not list")

    mutation_rows = [
        row for row in issue_inventory
        if isinstance(row, dict) and row.get("category") == "mutation_without_explicit_gate"
    ]
    launcher_rows = [
        row for row in issue_inventory
        if isinstance(row, dict) and row.get("category") == "launcher_runtime_risk_heuristic"
    ]
    duplicate_rows = [
        row for row in issue_inventory
        if isinstance(row, dict) and row.get("category") == "duplicate_superseded_modules"
    ]

    mutation_classified = [classify_mutation_issue(row) for row in mutation_rows]
    launcher_classified = [classify_launcher_issue(row) for row in launcher_rows]
    duplicate_classified = [classify_duplicate_issue(row) for row in duplicate_rows]

    all_classified = mutation_classified + launcher_classified + duplicate_classified

    class_counts = Counter(x["classification"] for x in all_classified)
    risk_counts = Counter(x["risk_level"] for x in all_classified)

    apply_recommended_now = [x for x in all_classified if x.get("apply_recommended_now") is True]
    preview_fix_candidates = [x for x in all_classified if x.get("preview_fix_candidate") is True]

    real_manual_review_count = sum(
        1 for x in all_classified
        if "requires_manual" in x["classification"]
        or "requires_strict_manual_gate" in x["classification"]
        or "requires_gate" in x["classification"]
    )

    likely_false_positive_count = sum(
        1 for x in all_classified
        if "false_positive" in x["classification"]
        or x["classification"] in {
            "expected_repo_output_writer_preview_or_audit",
            "guarded_governance_output_writer_likely_false_positive",
            "guarded_launcher_reference_likely_false_positive",
        }
    )

    classifier_status = "ATTENTION_ISSUE_POLICY_CLASSIFIER_READY_NO_FIXES_APPLIED"

    if apply_recommended_now:
        final_decision = "REVIEW_POLICY_CLASSIFIER_BEFORE_ANY_FIX_PREVIEW"
        next_action = "REVIEW_APPLY_RECOMMENDED_ROWS_MANUALLY"
        next_module = "edge_factory_os_attention_policy_fix_preview_v1.py"
    else:
        final_decision = "NO_DIRECT_APPLY_RECOMMENDED_BUILD_RUNTIME_RISK_REVIEW_OR_HYGIENE_GATE_NEXT"
        next_action = "REVIEW_MANUAL_RISK_BUCKETS_THEN_BUILD_POLICY_GUARDS_OR_HYGIENE_APPROVAL"
        next_module = "edge_factory_os_runtime_risk_and_mutation_policy_review_v1.py"

    result = {
        "module": "edge_factory_os_attention_issue_policy_classifier_v1.py",
        "generated_at_utc": now_iso(),
        "repo_root": str(REPO_ROOT),
        "classifier_status": classifier_status,
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "audit_input": {
            "path": rel_repo(AUDIT_JSON),
            "audit_status": audit.get("audit_status"),
            "issue_count": audit.get("issue_count"),
            "critical_issue_count": audit.get("critical_issue_count"),
            "attention_issue_count": audit.get("attention_issue_count"),
            "info_issue_count": audit.get("info_issue_count"),
        },
        "previous_triage": {
            "path": rel_repo(TRIAGE_JSON),
            "loaded": triage is not None,
            "triage_status": triage.get("triage_status") if triage else None,
        },
        "broken_paths_chain_preview": {
            "path": rel_repo(BROKEN_CHAIN_PREVIEW_JSON),
            "loaded": broken_preview is not None,
            "preview_status": broken_preview.get("preview_status") if broken_preview else None,
            "apply_recommended_now": broken_preview.get("counts", {}).get("apply_recommended_now") if broken_preview else None,
        },
        "counts": {
            "mutation_without_explicit_gate": len(mutation_rows),
            "launcher_runtime_risk_heuristic": len(launcher_rows),
            "duplicate_superseded_modules": len(duplicate_rows),
            "classified_total": len(all_classified),
            "apply_recommended_now": len(apply_recommended_now),
            "preview_fix_candidates": len(preview_fix_candidates),
            "real_manual_review_count": real_manual_review_count,
            "likely_false_positive_count": likely_false_positive_count,
        },
        "classification_counts": dict(class_counts),
        "risk_counts": dict(risk_counts),
        "mutation_classified": mutation_classified,
        "launcher_classified": launcher_classified,
        "duplicate_classified": duplicate_classified,
        "apply_recommended_now_rows": apply_recommended_now,
        "preview_fix_candidates": preview_fix_candidates,
        "recommended_policy_order": [
            {
                "order": 1,
                "action": "Do not auto-fix mutation/launcher heuristic issues.",
                "reason": "These are code-surface policy issues, not syntax errors.",
            },
            {
                "order": 2,
                "action": "Build runtime/mutation policy review module.",
                "reason": "Separate true runtime surfaces from governance false positives.",
            },
            {
                "order": 3,
                "action": "Only after review, add explicit guard comments or policy metadata where useful.",
                "reason": "Avoid changing behavior of runtime/source modules.",
            },
            {
                "order": 4,
                "action": "Run audit again after policy metadata/gate improvements.",
                "reason": "Confirm attention count reduction without runtime mutation.",
            },
            {
                "order": 5,
                "action": "Handle duplicate/superseded modules only via manual hygiene approval.",
                "reason": "Deletion/move/archive is explicitly blocked without approval.",
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
    lines.append("EDGE FACTORY OS ATTENTION ISSUE POLICY CLASSIFIER v1")
    lines.append("=" * 100)
    lines.append(f"classifier_status: {classifier_status}")
    lines.append(f"allowed_scope: {result['allowed_scope']}")
    lines.append(f"final_decision: {final_decision}")
    lines.append(f"next_action: {next_action}")
    lines.append(f"next_module: {next_module}")
    lines.append("")
    lines.append("COUNTS")
    lines.append("-" * 100)
    lines.append(json.dumps(result["counts"], indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("CLASSIFICATION COUNTS")
    lines.append("-" * 100)
    lines.append(json.dumps(result["classification_counts"], indent=2, sort_keys=True, ensure_ascii=False))
    lines.append("")
    lines.append("RISK COUNTS")
    lines.append("-" * 100)
    lines.append(json.dumps(result["risk_counts"], indent=2, sort_keys=True, ensure_ascii=False))
    lines.append("")
    lines.append("PREVIEW FIX CANDIDATES")
    lines.append("-" * 100)
    lines.append(json.dumps(preview_fix_candidates[:80], indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("APPLY RECOMMENDED NOW ROWS")
    lines.append("-" * 100)
    lines.append(json.dumps(apply_recommended_now, indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("RECOMMENDED POLICY ORDER")
    lines.append("-" * 100)
    lines.append(json.dumps(result["recommended_policy_order"], indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("FORBIDDEN ACTIONS")
    lines.append("-" * 100)
    for item in FORBIDDEN_ACTIONS:
        lines.append(f"- {item}")

    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"classifier_status: {classifier_status}")
    print(f"final_decision: {final_decision}")
    print(f"next_action: {next_action}")
    print(f"next_module: {next_module}")
    print("counts:")
    print(json.dumps(result["counts"], indent=2, ensure_ascii=False))
    print("classification_counts:")
    print(json.dumps(result["classification_counts"], indent=2, sort_keys=True, ensure_ascii=False))
    print("risk_counts:")
    print(json.dumps(result["risk_counts"], indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()