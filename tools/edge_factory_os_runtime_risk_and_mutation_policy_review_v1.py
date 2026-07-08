from __future__ import annotations

import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]

CLASSIFIER_JSON = (
    REPO_ROOT
    / "edge_factory_os_attention_issue_policy_classifier"
    / "attention_issue_policy_classifier_latest.json"
)

OUT_DIR = REPO_ROOT / "edge_factory_os_runtime_risk_and_mutation_policy_review"
OUT_JSON = OUT_DIR / "runtime_risk_and_mutation_policy_review_latest.json"
OUT_TXT = OUT_DIR / "runtime_risk_and_mutation_policy_review_latest.txt"

SAFETY_FLAGS = {
    "repo_only": True,
    "review_only": True,
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


def compact_row(row: Dict[str, Any]) -> Dict[str, Any]:
    issue = row.get("issue", {})
    if not isinstance(issue, dict):
        issue = {}

    return {
        "issue_id": issue.get("issue_id"),
        "category": issue.get("category"),
        "severity": issue.get("severity"),
        "path": issue.get("path"),
        "evidence": issue.get("evidence"),
        "classification": row.get("classification"),
        "risk_level": row.get("risk_level"),
        "reason": row.get("reason"),
        "signals": row.get("signals"),
    }


def bucket_for_classification(classification: str) -> str:
    if classification in {
        "expected_repo_output_writer_preview_or_audit",
        "guarded_governance_output_writer_likely_false_positive",
        "guarded_launcher_reference_likely_false_positive",
    }:
        return "LIKELY_FALSE_POSITIVE_NO_FIX"

    if classification in {
        "mutating_tool_requires_gate_or_manual_approval",
    }:
        return "GATE_REVIEW_CANDIDATE"

    if classification in {
        "runtime_surface_mutation_risk_requires_manual_review",
        "real_runtime_surface_requires_strict_manual_gate",
    }:
        return "RUNTIME_SURFACE_MANUAL_REVIEW"

    if classification in {
        "dangerous_mutation_pattern_requires_manual_review",
        "launcher_start_pattern_requires_manual_review",
    }:
        return "DANGEROUS_PATTERN_MANUAL_REVIEW"

    if classification in {
        "mutation_policy_review_required",
        "launcher_heuristic_unclassified_review_later",
    }:
        return "UNCLASSIFIED_POLICY_REVIEW"

    if classification == "duplicate_superseded_module_requires_manual_hygiene_gate":
        return "HYGIENE_APPROVAL_REQUIRED"

    return "OTHER_REVIEW"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    classifier = load_json(CLASSIFIER_JSON)

    mutation_rows = classifier.get("mutation_classified", [])
    launcher_rows = classifier.get("launcher_classified", [])
    duplicate_rows = classifier.get("duplicate_classified", [])

    if not isinstance(mutation_rows, list):
        mutation_rows = []
    if not isinstance(launcher_rows, list):
        launcher_rows = []
    if not isinstance(duplicate_rows, list):
        duplicate_rows = []

    all_rows = []
    for row in mutation_rows + launcher_rows + duplicate_rows:
        if isinstance(row, dict):
            all_rows.append(row)

    bucketed: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in all_rows:
        classification = str(row.get("classification") or "")
        bucket = bucket_for_classification(classification)
        bucketed[bucket].append(compact_row(row))

    bucket_counts = {key: len(value) for key, value in sorted(bucketed.items())}

    runtime_surface_manual_review = bucketed.get("RUNTIME_SURFACE_MANUAL_REVIEW", [])
    dangerous_pattern_manual_review = bucketed.get("DANGEROUS_PATTERN_MANUAL_REVIEW", [])
    gate_review_candidates = bucketed.get("GATE_REVIEW_CANDIDATE", [])
    likely_false_positive = bucketed.get("LIKELY_FALSE_POSITIVE_NO_FIX", [])
    hygiene_required = bucketed.get("HYGIENE_APPROVAL_REQUIRED", [])
    unclassified_policy_review = bucketed.get("UNCLASSIFIED_POLICY_REVIEW", [])

    review_status = "RUNTIME_RISK_AND_MUTATION_POLICY_REVIEW_READY_NO_FIXES_APPLIED"

    # No direct apply should be recommended from this module.
    direct_apply_recommended_now = False

    next_recommended_modules = [
        {
            "priority": 1,
            "module": "edge_factory_os_gate_review_candidate_preview_v1.py",
            "scope": "repo-only preview",
            "reason": "Review 23 apply/repair/patch/hygiene tools for explicit gate metadata before changing anything.",
            "input_bucket": "GATE_REVIEW_CANDIDATE",
            "row_count": len(gate_review_candidates),
        },
        {
            "priority": 2,
            "module": "edge_factory_os_runtime_surface_manual_review_packet_v1.py",
            "scope": "read-only review packet",
            "reason": "Runtime/src surfaces require manual review, not patching.",
            "input_bucket": "RUNTIME_SURFACE_MANUAL_REVIEW",
            "row_count": len(runtime_surface_manual_review),
        },
        {
            "priority": 3,
            "module": "edge_factory_os_dangerous_pattern_manual_review_packet_v1.py",
            "scope": "read-only review packet",
            "reason": "Dangerous mutation/start patterns require review before any policy metadata or code changes.",
            "input_bucket": "DANGEROUS_PATTERN_MANUAL_REVIEW",
            "row_count": len(dangerous_pattern_manual_review),
        },
        {
            "priority": 4,
            "module": "edge_factory_os_backup_hygiene_manual_approval_gate_v1.py",
            "scope": "manual approval only",
            "reason": "Duplicate/superseded modules and backup files require explicit hygiene approval before delete/move/archive.",
            "input_bucket": "HYGIENE_APPROVAL_REQUIRED",
            "row_count": len(hygiene_required),
        },
        {
            "priority": 5,
            "module": "edge_factory_os_audit_false_positive_suppression_preview_v1.py",
            "scope": "preview only",
            "reason": "Likely false positives may be suppressed later via audit-policy metadata, not by editing historical reports.",
            "input_bucket": "LIKELY_FALSE_POSITIVE_NO_FIX",
            "row_count": len(likely_false_positive),
        },
    ]

    final_decision = "NO_DIRECT_APPLY_BUILD_GATE_REVIEW_CANDIDATE_PREVIEW_NEXT"
    next_action = "BUILD_GATE_REVIEW_CANDIDATE_PREVIEW_NO_RUNTIME_ACTION"
    next_module = "edge_factory_os_gate_review_candidate_preview_v1.py"

    result = {
        "module": "edge_factory_os_runtime_risk_and_mutation_policy_review_v1.py",
        "generated_at_utc": now_iso(),
        "repo_root": str(REPO_ROOT),
        "review_status": review_status,
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "direct_apply_recommended_now": direct_apply_recommended_now,
        "classifier_input": {
            "path": rel_repo(CLASSIFIER_JSON),
            "classifier_status": classifier.get("classifier_status"),
            "counts": classifier.get("counts"),
            "classification_counts": classifier.get("classification_counts"),
            "risk_counts": classifier.get("risk_counts"),
        },
        "bucket_counts": bucket_counts,
        "runtime_surface_manual_review": runtime_surface_manual_review,
        "dangerous_pattern_manual_review": dangerous_pattern_manual_review,
        "gate_review_candidates": gate_review_candidates,
        "likely_false_positive_no_fix": likely_false_positive,
        "hygiene_approval_required": hygiene_required,
        "unclassified_policy_review": unclassified_policy_review,
        "next_recommended_modules": next_recommended_modules,
        "recommended_policy": [
            {
                "policy": "No direct code apply from heuristic audit categories.",
                "reason": "Mutation and launcher heuristics require review packets and explicit gates.",
            },
            {
                "policy": "Preview/approval before any mutating repair module changes.",
                "reason": "Apply/repair/patch/hygiene tools can be legitimate but must show explicit gate metadata.",
            },
            {
                "policy": "Runtime/src surfaces are manual-review only.",
                "reason": "Runtime, launcher, supervisor, paper, live, and risk surfaces must not be changed by heuristic cleanup.",
            },
            {
                "policy": "Duplicate/superseded cleanup requires manual hygiene approval.",
                "reason": "Delete/move/archive remains blocked without explicit approval.",
            },
            {
                "policy": "False positives should be suppressed in audit policy, not by editing historical reports.",
                "reason": "Preserve evidence and lesson memory.",
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
    lines.append("EDGE FACTORY OS RUNTIME RISK AND MUTATION POLICY REVIEW v1")
    lines.append("=" * 100)
    lines.append(f"review_status: {review_status}")
    lines.append(f"allowed_scope: {result['allowed_scope']}")
    lines.append(f"final_decision: {final_decision}")
    lines.append(f"next_action: {next_action}")
    lines.append(f"next_module: {next_module}")
    lines.append(f"direct_apply_recommended_now: {direct_apply_recommended_now}")
    lines.append("")
    lines.append("BUCKET COUNTS")
    lines.append("-" * 100)
    lines.append(json.dumps(bucket_counts, indent=2, sort_keys=True, ensure_ascii=False))
    lines.append("")
    lines.append("NEXT RECOMMENDED MODULES")
    lines.append("-" * 100)
    lines.append(json.dumps(next_recommended_modules, indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("GATE REVIEW CANDIDATES")
    lines.append("-" * 100)
    lines.append(json.dumps(gate_review_candidates, indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("RUNTIME SURFACE MANUAL REVIEW SAMPLE")
    lines.append("-" * 100)
    lines.append(json.dumps(runtime_surface_manual_review[:80], indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("DANGEROUS PATTERN MANUAL REVIEW SAMPLE")
    lines.append("-" * 100)
    lines.append(json.dumps(dangerous_pattern_manual_review[:80], indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("LIKELY FALSE POSITIVE SAMPLE")
    lines.append("-" * 100)
    lines.append(json.dumps(likely_false_positive[:80], indent=2, ensure_ascii=False))
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

    print(f"review_status: {review_status}")
    print(f"final_decision: {final_decision}")
    print(f"next_action: {next_action}")
    print(f"next_module: {next_module}")
    print(f"direct_apply_recommended_now: {direct_apply_recommended_now}")
    print("bucket_counts:")
    print(json.dumps(bucket_counts, indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()