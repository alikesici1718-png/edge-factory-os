from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]

REVIEW_JSON = (
    REPO_ROOT
    / "edge_factory_os_runtime_risk_and_mutation_policy_review"
    / "runtime_risk_and_mutation_policy_review_latest.json"
)

OUT_DIR = REPO_ROOT / "edge_factory_os_gate_review_candidate_preview"
OUT_JSON = OUT_DIR / "gate_review_candidate_preview_latest.json"
OUT_TXT = OUT_DIR / "gate_review_candidate_preview_latest.txt"

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
    "old_short_guarded_apply_allowed": False,
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

REQUIRED_GUARD_TERMS = [
    "safety_flags",
    "forbidden_actions",
    "allowed_scope",
]

BLOCK_FLAG_TERMS = [
    "runtime_touch_allowed",
    "launcher_allowed",
    "capital_change_allowed",
    "live_allowed",
    "real_orders_allowed",
]

APPROVAL_TERMS = [
    "approval",
    "manual_approval",
    "preview",
    "no_apply",
    "apply_status",
    "preview_status",
]

DANGER_TERMS = [
    "os.remove",
    ".unlink",
    "unlink(",
    "shutil.rmtree",
    "shutil.move",
    "os.rename",
    ".rename",
    "subprocess.run",
    "Popen",
    "startfile",
    "git add -f",
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


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root is not object: {path}")
    return data


def read_text(path_str: str) -> str:
    p = REPO_ROOT / path_str.replace("/", "\\")
    try:
        if p.is_file():
            return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    return ""


def has_false_assignment(text_l: str, term: str) -> bool:
    patterns = [
        rf'"{re.escape(term)}"\s*:\s*false',
        rf"'{re.escape(term)}'\s*:\s*False",
        rf"{re.escape(term)}\s*=\s*False",
    ]
    return any(re.search(pat, text_l, flags=re.IGNORECASE) for pat in patterns)


def classify_candidate(row: Dict[str, Any]) -> Dict[str, Any]:
    # Support both shapes:
    # 1) nested classifier row: {"issue": {"path": ...}, "classification": ...}
    # 2) compact review row: {"path": ..., "issue_id": ..., "classification": ...}
    issue = row.get("issue", {})
    if not isinstance(issue, dict):
        issue = {}

    path = str(issue.get("path") or row.get("path") or "").replace("\\", "/")
    issue_id = str(issue.get("issue_id") or row.get("issue_id") or "")
    evidence = str(issue.get("evidence") or row.get("evidence") or "")
    classification_from_prior = str(row.get("classification") or "")
    prior_reason = str(row.get("reason") or "")

    text = read_text(path)
    text_l = text.lower()

    guard_terms_present = [term for term in REQUIRED_GUARD_TERMS if term.lower() in text_l]
    block_flags_present = [term for term in BLOCK_FLAG_TERMS if term.lower() in text_l]
    block_flags_false = [term for term in BLOCK_FLAG_TERMS if has_false_assignment(text_l, term)]
    approval_terms_present = [term for term in APPROVAL_TERMS if term.lower() in text_l]
    danger_terms_present = [term for term in DANGER_TERMS if term.lower() in text_l]

    file_exists = bool(text)
    has_required_guard_terms = len(guard_terms_present) >= 2
    has_core_block_flags = len(block_flags_present) >= 3
    has_core_false_flags = len(block_flags_false) >= 3
    has_approval_or_preview_language = len(approval_terms_present) >= 1
    has_danger_terms = len(danger_terms_present) > 0

    classification = "GATE_REVIEW_MANUAL_REQUIRED"
    risk_level = "ATTENTION"
    apply_recommended_now = False
    preview_fix_candidate = False
    proposed_next_action = "Manual review before any change."
    reason = "Default conservative gate review."

    if not file_exists:
        classification = "GATE_REVIEW_TARGET_FILE_MISSING"
        risk_level = "ATTENTION"
        proposed_next_action = "Do not patch. Confirm whether the candidate is stale or moved."
        reason = "Candidate target file could not be read."

    elif has_required_guard_terms and has_core_block_flags and has_core_false_flags and has_approval_or_preview_language and not has_danger_terms:
        classification = "GATE_REVIEW_PASS_NO_FIX"
        risk_level = "INFO"
        proposed_next_action = "No fix. Candidate already appears guarded."
        reason = "Required guard terms, false safety flags, and approval/preview language are present."

    elif has_required_guard_terms and has_core_block_flags and has_approval_or_preview_language:
        classification = "GATE_REVIEW_PASS_WITH_ATTENTION"
        risk_level = "ATTENTION"
        proposed_next_action = "No direct apply. Later audit policy may mark this as guarded after review."
        reason = "Guard structure exists but not all core block flags were detected as explicit false assignments."

    elif has_required_guard_terms and has_core_block_flags and has_danger_terms:
        classification = "GATE_REVIEW_DANGEROUS_PATTERN_BUT_GUARDED_MANUAL_REVIEW"
        risk_level = "ATTENTION"
        proposed_next_action = "Manual review only. Do not alter behavior."
        reason = "Dangerous mutation/start-like terms exist, but guard terms are also present."

    elif has_danger_terms and not has_required_guard_terms:
        classification = "GATE_REVIEW_FAIL_DANGEROUS_PATTERN_NO_CLEAR_GATE"
        risk_level = "ATTENTION"
        preview_fix_candidate = True
        proposed_next_action = "Build a future preview-only metadata/guard patch only after manual review."
        reason = "Dangerous terms found without sufficient explicit guard metadata."

    elif not has_required_guard_terms:
        classification = "GATE_REVIEW_FAIL_MISSING_EXPLICIT_GATE_METADATA"
        risk_level = "ATTENTION"
        preview_fix_candidate = True
        proposed_next_action = "Future preview may add explicit non-behavioral guard metadata/comments; no apply now."
        reason = "Candidate lacks enough explicit safety/gate metadata for the audit policy."

    return {
        "issue": {
            "issue_id": issue_id,
            "path": path,
            "category": issue.get("category"),
            "severity": issue.get("severity"),
            "evidence": evidence,
            "recommendation": issue.get("recommendation"),
        },
        "prior_classification": classification_from_prior,
        "prior_reason": prior_reason,
        "classification": classification,
        "risk_level": risk_level,
        "apply_recommended_now": apply_recommended_now,
        "preview_fix_candidate": preview_fix_candidate,
        "proposed_next_action": proposed_next_action,
        "reason": reason,
        "signals": {
            "file_exists": file_exists,
            "guard_terms_present": guard_terms_present,
            "block_flags_present": block_flags_present,
            "block_flags_false": block_flags_false,
            "approval_terms_present": approval_terms_present,
            "danger_terms_present": danger_terms_present,
            "has_required_guard_terms": has_required_guard_terms,
            "has_core_block_flags": has_core_block_flags,
            "has_core_false_flags": has_core_false_flags,
            "has_approval_or_preview_language": has_approval_or_preview_language,
            "has_danger_terms": has_danger_terms,
        },
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    review = load_json(REVIEW_JSON)

    gate_candidates = review.get("gate_review_candidates", [])
    if not isinstance(gate_candidates, list):
        gate_candidates = []

    classified = [
        classify_candidate(row)
        for row in gate_candidates
        if isinstance(row, dict)
    ]

    class_counts = Counter(row["classification"] for row in classified)
    risk_counts = Counter(row["risk_level"] for row in classified)

    apply_recommended = [row for row in classified if row["apply_recommended_now"]]
    preview_fix_candidates = [row for row in classified if row["preview_fix_candidate"]]

    preview_status = "GATE_REVIEW_CANDIDATE_PREVIEW_READY_NO_APPLY"
    direct_apply_recommended_now = False

    if preview_fix_candidates:
        final_decision = "REVIEW_GATE_CANDIDATES_BEFORE_METADATA_PATCH_PREVIEW"
        next_action = "REVIEW_CANDIDATES_THEN_BUILD_NON_BEHAVIORAL_GATE_METADATA_PREVIEW_IF_APPROVED"
        next_module = "edge_factory_os_gate_metadata_patch_preview_v1.py"
    else:
        final_decision = "NO_GATE_METADATA_PATCH_PREVIEW_NEEDED_NOW"
        next_action = "CONTINUE_RUNTIME_SURFACE_MANUAL_REVIEW_PACKET"
        next_module = "edge_factory_os_runtime_surface_manual_review_packet_v1.py"

    result = {
        "module": "edge_factory_os_gate_review_candidate_preview_v1.py",
        "generated_at_utc": now_iso(),
        "repo_root": str(REPO_ROOT),
        "preview_status": preview_status,
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "direct_apply_recommended_now": direct_apply_recommended_now,
        "review_input": {
            "path": rel_repo(REVIEW_JSON),
            "review_status": review.get("review_status"),
            "bucket_counts": review.get("bucket_counts"),
            "next_module": review.get("next_module"),
        },
        "counts": {
            "gate_review_candidate_count": len(classified),
            "apply_recommended_now": len(apply_recommended),
            "preview_fix_candidate_count": len(preview_fix_candidates),
        },
        "classification_counts": dict(class_counts),
        "risk_counts": dict(risk_counts),
        "classified_gate_candidates": classified,
        "preview_fix_candidates": preview_fix_candidates,
        "apply_recommended_now_rows": apply_recommended,
        "recommended_policy": [
            {
                "policy": "No behavioral change from gate review.",
                "reason": "This preview only detects whether explicit guard metadata exists.",
            },
            {
                "policy": "Missing metadata does not prove unsafe behavior.",
                "reason": "If needed, only non-behavioral metadata/comment patch previews should be considered.",
            },
            {
                "policy": "Dangerous patterns require manual review.",
                "reason": "Do not auto-patch apply/repair/patch/hygiene modules.",
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
    lines.append("EDGE FACTORY OS GATE REVIEW CANDIDATE PREVIEW v1")
    lines.append("=" * 100)
    lines.append(f"preview_status: {preview_status}")
    lines.append(f"allowed_scope: {result['allowed_scope']}")
    lines.append(f"final_decision: {final_decision}")
    lines.append(f"next_action: {next_action}")
    lines.append(f"next_module: {next_module}")
    lines.append(f"direct_apply_recommended_now: {direct_apply_recommended_now}")
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
    lines.append(json.dumps(preview_fix_candidates, indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("CLASSIFIED GATE CANDIDATES")
    lines.append("-" * 100)
    lines.append(json.dumps(classified, indent=2, ensure_ascii=False))
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
    print(f"direct_apply_recommended_now: {direct_apply_recommended_now}")
    print("counts:")
    print(json.dumps(result["counts"], indent=2, ensure_ascii=False))
    print("classification_counts:")
    print(json.dumps(result["classification_counts"], indent=2, sort_keys=True, ensure_ascii=False))
    print("risk_counts:")
    print(json.dumps(result["risk_counts"], indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()