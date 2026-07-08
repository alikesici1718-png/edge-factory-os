from __future__ import annotations

import ast
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_attention_triage_classifier_gate_review_refresh_after_metadata_v4"
OUT_DIR = LAB_ROOT / "edge_factory_os_attention_triage_classifier_gate_review_refresh_after_metadata_v4"
OUT_DIR.mkdir(parents=True, exist_ok=True)

POST_COMMIT_STATUS_JSON = (
    LAB_ROOT
    / "edge_factory_os_post_commit_read_only_status_after_gate_metadata_v4"
    / "post_commit_read_only_status_after_gate_metadata_v4_latest.json"
)

EXPECTED_HEAD_PREFIX = "578879b"

EXPECTED_FIXED_METADATA_TARGETS: Set[str] = {
    "src/edge_factory_claude_critical_patch_v1.py",
    "src/edge_factory_master_gate_compatibility_repair_v1.py",
    "src/edge_factory_master_gate_compatibility_repair_v2.py",
    "src/edge_factory_master_launcher_gate_repair_v3.py",
    "src/edge_factory_master_upper_system_boot_repair_v1.py",
    "src/edge_factory_patch_launcher_remove_blocking_risk_line_v1.py",
    "src/edge_factory_patch_master_launcher_risk_args_v1.py",
    "src/edge_factory_risk_manager_v4_wrapper_patch_v2.py",
    "src/edge_factory_signal_id_fallback_line_patch_v2.py",
    "tools/edge_factory_os_month_stability_repair_diagnostic_v1.py",
    "tools/edge_factory_os_repo_cleanup_plan_v1.py",
}

KNOWN_ALLOWED_UNTRACKED: Set[str] = {
    "tools/edge_factory_os_gate_metadata_patch_preview_v2.py",
    "tools/edge_factory_os_gate_metadata_patch_preview_v3.py",
    "tools/edge_factory_os_joint_null_distribution_validator_v1.py.readonly_fix_bak_20260514_022123",
    "tools/edge_factory_os_old_short_guarded_runtime_reenable_apply_v1.py",
    "tools/edge_factory_os_post_commit_read_only_status_after_gate_metadata_v4.py",
    "tools/edge_factory_os_source_panel_anomaly_discovery_runner_v1.py.blocked_patch_bak_20260514_000647",
    "tools/edge_factory_os_universe_coverage_guard_v1.py",
    "tools/edge_factory_os_attention_triage_classifier_gate_review_refresh_after_metadata_v4.py",
}

SAFETY_FLAGS: Dict[str, bool] = {
    "read_only_refresh": True,
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


def tracked_python_files() -> List[str]:
    result = run_cmd(["git", "ls-files", "*.py"])
    return sorted([line.strip() for line in result.stdout.splitlines() if line.strip()])


def file_text(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def has_real_comment_gate_metadata_block(text: str) -> bool:
    """Return True only for actual top-level/comment-line metadata blocks.

    This intentionally ignores marker strings inside Python literals/templates.
    A real block requires exact comment marker lines:
      # EDGE_FACTORY_GATE_METADATA_START
      # EDGE_FACTORY_GATE_METADATA_END
    """
    lines = text.splitlines()
    start_indices = [
        idx for idx, line in enumerate(lines)
        if line.strip() == "# EDGE_FACTORY_GATE_METADATA_START"
    ]

    for start in start_indices:
        for end in range(start + 1, len(lines)):
            if lines[end].strip() == "# EDGE_FACTORY_GATE_METADATA_END":
                block = lines[start:end + 1]
                if all((not item.strip()) or item.lstrip().startswith("#") for item in block):
                    return True
                return False

    return False



def metadata_block_errors(rel_path: str, text: str) -> List[str]:
    errors: List[str] = []

    if text.startswith("\ufeff"):
        errors.append("BOM detected")

    if text.count("EDGE_FACTORY_GATE_METADATA_START") != 1:
        errors.append("metadata start marker count is not 1")

    if text.count("EDGE_FACTORY_GATE_METADATA_END") != 1:
        errors.append("metadata end marker count is not 1")

    required = [
        "# gate_metadata_version: 1",
        "# gate_metadata_kind: non_behavioral_comment_block",
        f"# gate_review_target_path: {rel_path}",
        "# allowed_scope: REPO_ONLY_OS_INTELLIGENCE",
        "# non_behavioral_comment_only: true",
        "# runtime_touch_allowed: false",
        "# launcher_allowed: false",
        "# capital_change_allowed: false",
        "# active_paper_allowed: false",
        "# live_allowed: false",
        "# real_orders_allowed: false",
        "# candidate_generation_allowed: false",
        "# family_release_allowed: false",
        "# strategy_research_allowed: false",
        "# holdout_access_allowed: false",
        "# backup_delete_allowed: false",
        "# backup_move_allowed: false",
        "# direct_apply_allowed: false",
    ]

    for line in required:
        if line not in text:
            errors.append(f"missing metadata line: {line}")

    try:
        ast.parse(text, filename=rel_path)
    except Exception as exc:
        errors.append(f"syntax error: {repr(exc)}")

    return errors


def detect_risk_signals(rel_path: str, text: str) -> Dict[str, Any]:
    low_path = rel_path.lower()
    low_text = text.lower()

    filename_tokens = [
        "patch",
        "repair",
        "apply",
        "cleanup",
        "delete",
        "remove",
        "move",
        "launcher",
        "risk",
        "gate",
        "guard",
        "reenable",
        "re_enable",
        "runtime",
        "capital",
        "live",
        "order",
    ]

    mutation_patterns = {
        "path_write_text": r"\.write_text\s*\(",
        "path_write_bytes": r"\.write_bytes\s*\(",
        "open_write_mode": r"open\s*\([^)]*['\"][wax]\+?['\"]",
        "unlink": r"\.unlink\s*\(",
        "rmdir": r"\.rmdir\s*\(",
        "shutil_rmtree": r"shutil\.rmtree\s*\(",
        "shutil_move": r"shutil\.move\s*\(",
        "os_remove": r"os\.remove\s*\(",
        "os_unlink": r"os\.unlink\s*\(",
        "git_commit": r"git['\"],\s*['\"]commit",
        "git_add": r"git['\"],\s*['\"]add",
        "git_reset": r"git['\"],\s*['\"]reset",
        "subprocess": r"subprocess\.",
    }

    trading_sensitive_patterns = {
        "capital_change": r"capital|allocation|size|sizing",
        "live_or_order": r"live|real_order|send_order|place_order|order_execution",
        "launcher": r"launcher|autopilot|supervisor",
        "holdout": r"holdout",
        "strategy_research": r"strategy|candidate|family_release|promotion",
    }

    filename_hits = [token for token in filename_tokens if token in low_path]
    mutation_hits = [
        name for name, pattern in mutation_patterns.items()
        if re.search(pattern, text)
    ]
    sensitive_hits = [
        name for name, pattern in trading_sensitive_patterns.items()
        if re.search(pattern, low_text)
    ]

    read_only_markers = [
        "read_only",
        "read-only",
        "preview_only",
        "no_apply",
        "apply_allowed\": false",
        "apply_allowed = false",
        "runtime_touch_allowed\": false",
        "runtime_touch_allowed = false",
    ]

    read_only_hits = [marker for marker in read_only_markers if marker in low_text]

    risk_score = len(filename_hits) + (2 * len(mutation_hits)) + len(sensitive_hits)

    return {
        "filename_hits": filename_hits,
        "mutation_hits": mutation_hits,
        "sensitive_hits": sensitive_hits,
        "read_only_hits": read_only_hits,
        "risk_score": risk_score,
    }


def classify_tracked_file(rel_path: str) -> Dict[str, Any]:
    text = file_text(rel_path)

    syntax_error: Optional[str] = None
    try:
        ast.parse(text, filename=rel_path)
    except Exception as exc:
        syntax_error = repr(exc)

    metadata_present = has_real_comment_gate_metadata_block(text)
    risk = detect_risk_signals(rel_path, text)

    if syntax_error:
        classification = "GATE_REVIEW_FAIL_SYNTAX_ERROR"
        risk_level = "CRITICAL"
        candidate = True
    elif rel_path in EXPECTED_FIXED_METADATA_TARGETS:
        errors = metadata_block_errors(rel_path, text)
        if errors:
            classification = "GATE_REVIEW_FAIL_EXPECTED_METADATA_INVALID"
            risk_level = "CRITICAL"
            candidate = True
        else:
            classification = "GATE_REVIEW_PASS_METADATA_PRESENT_AFTER_V4"
            risk_level = "INFO"
            candidate = False
    elif metadata_present:
        errors = metadata_block_errors(rel_path, text)
        if errors:
            classification = "GATE_REVIEW_ATTENTION_METADATA_PRESENT_BUT_INVALID"
            risk_level = "ATTENTION"
            candidate = True
        else:
            classification = "GATE_REVIEW_PASS_EXISTING_METADATA_PRESENT"
            risk_level = "INFO"
            candidate = False
    elif risk["mutation_hits"] and not risk["read_only_hits"]:
        classification = "GATE_REVIEW_MANUAL_REQUIRED_MUTATION_SURFACE_NO_READ_ONLY_GATE"
        risk_level = "ATTENTION"
        candidate = True
    elif risk["mutation_hits"]:
        classification = "GATE_REVIEW_ATTENTION_MUTATION_SURFACE_READ_ONLY_MARKERS_NO_METADATA"
        risk_level = "ATTENTION"
        candidate = True
    elif risk["risk_score"] >= 4:
        classification = "GATE_REVIEW_ATTENTION_RISKY_FILENAME_OR_SENSITIVE_TERMS_NO_METADATA"
        risk_level = "ATTENTION"
        candidate = True
    else:
        classification = "GATE_REVIEW_PASS_NO_FIX"
        risk_level = "INFO"
        candidate = False

    return {
        "path": rel_path,
        "classification": classification,
        "risk": risk_level,
        "candidate": candidate,
        "apply_recommended_now": False,
        "preview_fix_candidate": False,
        "direct_apply_recommended_now": False,
        "metadata_present": metadata_present,
        "risk_signals": risk,
        "syntax_error": syntax_error,
    }


def classify_untracked(path: str) -> Dict[str, Any]:
    if path == "tools/edge_factory_os_old_short_guarded_runtime_reenable_apply_v1.py":
        classification = "UNTRACKED_MANUAL_REQUIRED_OLD_SHORT_GUARDED_APPLY_DO_NOT_RUN"
        risk = "ATTENTION"
    elif "readonly_fix_bak" in path or "blocked_patch_bak" in path:
        classification = "UNTRACKED_KNOWN_BACKUP_HYGIENE_NO_DELETE_MOVE"
        risk = "ATTENTION"
    elif path in {
        "tools/edge_factory_os_gate_metadata_patch_preview_v2.py",
        "tools/edge_factory_os_gate_metadata_patch_preview_v3.py",
    }:
        classification = "UNTRACKED_SUPERSEDED_PREVIEW_TOOL_NO_ACTION"
        risk = "INFO"
    elif path == "tools/edge_factory_os_universe_coverage_guard_v1.py":
        classification = "UNTRACKED_REVIEW_REQUIRED_UNIVERSE_GUARD_NO_ACTION"
        risk = "ATTENTION"
    elif path == "tools/edge_factory_os_post_commit_read_only_status_after_gate_metadata_v4.py":
        classification = "UNTRACKED_POST_COMMIT_STATUS_TOOL_NO_ACTION"
        risk = "INFO"
    elif path == "tools/edge_factory_os_attention_triage_classifier_gate_review_refresh_after_metadata_v4.py":
        classification = "UNTRACKED_CURRENT_REFRESH_TOOL_NO_ACTION"
        risk = "INFO"
    else:
        classification = "UNTRACKED_UNKNOWN_REVIEW_REQUIRED"
        risk = "ATTENTION"

    return {
        "path": path,
        "classification": classification,
        "risk": risk,
        "candidate": classification.endswith("REVIEW_REQUIRED") or risk == "ATTENTION",
        "apply_recommended_now": False,
        "preview_fix_candidate": False,
        "direct_apply_recommended_now": False,
    }


def count_by_key(rows: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for row in rows:
        value = str(row.get(key, "UNKNOWN"))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def main() -> int:
    for key, value in SAFETY_FLAGS.items():
        if not isinstance(value, bool):
            raise SystemExit(f"safety flag is not boolean: {key}")

    errors: List[str] = []
    warnings: List[str] = []

    git_state = get_git_state()

    if not git_state["head"].startswith(EXPECTED_HEAD_PREFIX):
        errors.append(f"unexpected HEAD: {git_state['head']} expected prefix {EXPECTED_HEAD_PREFIX}")

    if git_state["dirty_tracked_count"] != 0:
        errors.append(f"tracked files dirty before classifier refresh: {git_state['dirty_tracked_paths']}")

    try:
        post_commit = load_json(POST_COMMIT_STATUS_JSON)
    except Exception as exc:
        post_commit = {}
        errors.append(f"post-commit status json missing/unreadable: {repr(exc)}")

    if post_commit:
        if post_commit.get("status") != "POST_COMMIT_READ_ONLY_STATUS_AFTER_GATE_METADATA_V4_PASS":
            errors.append(f"post-commit status is not PASS: {post_commit.get('status')}")
        if post_commit.get("critical_issue_count") != 0:
            errors.append(f"post-commit critical_issue_count not 0: {post_commit.get('critical_issue_count')}")
        if post_commit.get("warning_count") != 0:
            warnings.append(f"post-commit warning_count not 0: {post_commit.get('warning_count')}")

    untracked = set(git_state["untracked_paths"])
    unknown_untracked = sorted(untracked - KNOWN_ALLOWED_UNTRACKED)
    if unknown_untracked:
        warnings.append(f"unknown untracked paths present: {unknown_untracked}")

    tracked_files = tracked_python_files()
    tracked_rows = [classify_tracked_file(path) for path in tracked_files]

    fixed_rows = [row for row in tracked_rows if row["path"] in EXPECTED_FIXED_METADATA_TARGETS]
    fixed_failures = [
        row for row in fixed_rows
        if row["classification"] != "GATE_REVIEW_PASS_METADATA_PRESENT_AFTER_V4"
    ]

    if fixed_failures:
        errors.append(f"fixed metadata targets failed refresh validation: {fixed_failures}")

    untracked_rows = [classify_untracked(path) for path in sorted(untracked)]

    tracked_candidates = [row for row in tracked_rows if row["candidate"]]
    untracked_attention = [row for row in untracked_rows if row["risk"] == "ATTENTION"]

    critical_rows = [row for row in tracked_rows + untracked_rows if row.get("risk") == "CRITICAL"]
    attention_rows = [row for row in tracked_rows + untracked_rows if row.get("risk") == "ATTENTION"]

    classification_counts = count_by_key(tracked_rows + untracked_rows, "classification")
    risk_counts = count_by_key(tracked_rows + untracked_rows, "risk")

    if errors:
        refresh_status = "ATTENTION_TRIAGE_CLASSIFIER_GATE_REVIEW_REFRESH_AFTER_METADATA_V4_FAIL_CLOSED"
        severity = "BLOCKED"
        final_decision = "STOP_REVIEW_CLASSIFIER_REFRESH_ERRORS_NO_APPLY"
        next_action = "FIX_REFRESH_INPUT_OR_POST_COMMIT_STATUS_BEFORE_CONTINUING"
        next_module = None
        reason = "refresh errors detected; no apply allowed"
    else:
        refresh_status = "ATTENTION_TRIAGE_CLASSIFIER_GATE_REVIEW_REFRESH_AFTER_METADATA_V4_READY_NO_APPLY"
        severity = "ATTENTION"
        final_decision = "REVIEW_REFRESHED_CANDIDATES_NO_APPLY"
        next_action = "REVIEW_REMAINING_ATTENTION_THEN_DECIDE_BACKUP_HYGIENE_OR_NEXT_NON_BEHAVIORAL_PREVIEW"
        next_module = "edge_factory_os_attention_issue_policy_classifier_after_gate_metadata_v4.py"
        reason = (
            f"fixed_metadata_targets_pass={len(fixed_rows) - len(fixed_failures)}/{len(EXPECTED_FIXED_METADATA_TARGETS)}; "
            f"tracked_candidates={len(tracked_candidates)}; "
            f"untracked_attention={len(untracked_attention)}; "
            "direct_apply_recommended_now=False"
        )

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "refresh_status": refresh_status,
        "severity": severity,
        "allowed_scope": "READ_ONLY_REPO_TRIAGE_CLASSIFIER_REFRESH",
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "reason": reason,
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "source_post_commit_status_json": str(POST_COMMIT_STATUS_JSON),
        "latest_commit": git_state["head"],
        "errors": errors,
        "warnings": warnings,
        "critical_issue_count": len(errors),
        "warning_count": len(warnings),
        "counts": {
            "tracked_python_file_count": len(tracked_files),
            "fixed_metadata_target_count": len(EXPECTED_FIXED_METADATA_TARGETS),
            "fixed_metadata_pass_count": len(fixed_rows) - len(fixed_failures),
            "fixed_metadata_failure_count": len(fixed_failures),
            "tracked_candidate_count": len(tracked_candidates),
            "untracked_attention_count": len(untracked_attention),
            "critical_row_count": len(critical_rows),
            "attention_row_count": len(attention_rows),
            "direct_apply_recommended_now_count": 0,
            "preview_fix_candidate_count": 0,
            "apply_recommended_now_count": 0,
        },
        "classification_counts": classification_counts,
        "risk_counts": risk_counts,
        "fixed_metadata_target_validation": fixed_rows,
        "tracked_candidates": tracked_candidates,
        "untracked_classifications": untracked_rows,
        "critical_rows": critical_rows,
        "attention_rows": attention_rows,
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
        "preview_fix_candidate_count": 0,
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

    latest_json = OUT_DIR / "attention_triage_classifier_gate_review_refresh_after_metadata_v4_latest.json"
    timestamped_json = OUT_DIR / f"attention_triage_classifier_gate_review_refresh_after_metadata_v4_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "attention_triage_classifier_gate_review_refresh_after_metadata_v4_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    txt_lines = [
        "EDGE FACTORY OS ATTENTION TRIAGE CLASSIFIER + GATE REVIEW REFRESH AFTER METADATA v4",
        "=" * 100,
        f"refresh_status: {payload['refresh_status']}",
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
        "CLASSIFICATION COUNTS",
        "-" * 100,
        json.dumps(classification_counts, indent=2, sort_keys=True),
        "",
        "RISK COUNTS",
        "-" * 100,
        json.dumps(risk_counts, indent=2, sort_keys=True),
        "",
        "ERRORS",
        "-" * 100,
        json.dumps(errors, indent=2, sort_keys=True),
        "",
        "WARNINGS",
        "-" * 100,
        json.dumps(warnings, indent=2, sort_keys=True),
        "",
        "TRACKED CANDIDATES",
        "-" * 100,
        json.dumps(tracked_candidates, indent=2, sort_keys=True),
        "",
        "UNTRACKED CLASSIFICATIONS",
        "-" * 100,
        json.dumps(untracked_rows, indent=2, sort_keys=True),
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

    return 0 if not errors else 3


if __name__ == "__main__":
    raise SystemExit(main())