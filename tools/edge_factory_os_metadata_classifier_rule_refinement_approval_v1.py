from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_metadata_classifier_rule_refinement_approval_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_metadata_classifier_rule_refinement_approval_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "578879b"

PREVIEW_JSON = (
    LAB_ROOT
    / "edge_factory_os_metadata_classifier_rule_refinement_preview_v1"
    / "metadata_classifier_rule_refinement_preview_v1_latest.json"
)

PREVIEW_DIFF = (
    LAB_ROOT
    / "edge_factory_os_metadata_classifier_rule_refinement_preview_v1"
    / "metadata_classifier_rule_refinement_preview_v1_latest.diff"
)

PROPOSED_SOURCE = (
    LAB_ROOT
    / "edge_factory_os_metadata_classifier_rule_refinement_preview_v1"
    / "edge_factory_os_attention_triage_classifier_gate_review_refresh_after_metadata_v4_refined_preview.py"
)

TARGET_TOOL_REL = "tools/edge_factory_os_attention_triage_classifier_gate_review_refresh_after_metadata_v4.py"
TARGET_TOOL = REPO_ROOT / TARGET_TOOL_REL

KNOWN_ALLOWED_UNTRACKED: Set[str] = {
    "tools/edge_factory_os_attention_issue_policy_classifier_after_gate_metadata_v4.py",
    "tools/edge_factory_os_attention_triage_classifier_gate_review_refresh_after_metadata_v4.py",
    "tools/edge_factory_os_gate_metadata_patch_preview_v2.py",
    "tools/edge_factory_os_gate_metadata_patch_preview_v3.py",
    "tools/edge_factory_os_invalid_existing_metadata_block_inspector_v1.py",
    "tools/edge_factory_os_joint_null_distribution_validator_v1.py.readonly_fix_bak_20260514_022123",
    "tools/edge_factory_os_metadata_classifier_rule_refinement_approval_v1.py",
    "tools/edge_factory_os_metadata_classifier_rule_refinement_preview_v1.py",
    "tools/edge_factory_os_old_short_guarded_runtime_reenable_apply_v1.py",
    "tools/edge_factory_os_post_commit_read_only_status_after_gate_metadata_v4.py",
    "tools/edge_factory_os_source_panel_anomaly_discovery_runner_v1.py.blocked_patch_bak_20260514_000647",
    "tools/edge_factory_os_stabilization_freeze_error_closure_controller_v1.py",
    "tools/edge_factory_os_universe_coverage_guard_v1.py",
}

SAFETY_FLAGS: Dict[str, bool] = {
    "stabilization_freeze_active": True,
    "approval_only": True,
    "apply_performed_now": False,
    "commit_performed_now": False,
    "direct_apply_allowed": False,
    "os_development_allowed": False,
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
    "mass_metadata_patch_allowed": False,
}

FORBIDDEN_ACTIONS: List[str] = [
    "os_feature_development",
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
    "mass_metadata_patch",
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


def fail_closed(reason: str, extra: Optional[Dict[str, Any]] = None) -> int:
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "approval_status": "METADATA_CLASSIFIER_RULE_REFINEMENT_APPROVAL_V1_FAIL_CLOSED",
        "severity": "BLOCKED",
        "allowed_scope": "READ_ONLY_CLASSIFIER_RULE_APPROVAL",
        "final_decision": "STOP_NO_APPLY",
        "next_action": "REVIEW_APPROVAL_FAILURE",
        "next_module": None,
        "reason": reason,
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "preview_json": str(PREVIEW_JSON),
        "preview_diff": str(PREVIEW_DIFF),
        "proposed_source": str(PROPOSED_SOURCE),
        "target_tool": str(TARGET_TOOL),
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
        "runtime_touched": False,
        "launcher_executed": False,
        "capital_changed": False,
        "live_or_real_orders": False,
        "holdout_accessed": False,
        "backup_deleted_or_moved": False,
        "gitignore_changed": False,
        "git_add_force_used": False,
    }
    if extra:
        payload.update(extra)

    out = OUT_DIR / "metadata_classifier_rule_refinement_approval_v1_fail_closed_latest.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS METADATA CLASSIFIER RULE REFINEMENT APPROVAL v1")
    print("=" * 100)
    print("approval_status: METADATA_CLASSIFIER_RULE_REFINEMENT_APPROVAL_V1_FAIL_CLOSED")
    print(f"reason: {reason}")
    print(f"output: {out}")
    return 2


def is_untracked(rel_path: str, git_state: Dict[str, Any]) -> bool:
    return rel_path in set(git_state.get("untracked_paths", []))


def validate_proposed_source(source: str) -> Dict[str, Any]:
    errors: List[str] = []

    if source.startswith("\ufeff"):
        errors.append("proposed source has BOM")

    try:
        ast.parse(source, filename=TARGET_TOOL_REL)
    except Exception as exc:
        errors.append(f"syntax error: {repr(exc)}")

    required_snippets = [
        "def has_real_comment_gate_metadata_block(text: str) -> bool:",
        'line.strip() == "# EDGE_FACTORY_GATE_METADATA_START"',
        'lines[end].strip() == "# EDGE_FACTORY_GATE_METADATA_END"',
        "metadata_present = has_real_comment_gate_metadata_block(text)",
        "direct_apply_recommended_now",
        '"direct_apply_recommended_now": False',
        '"apply_recommended_now": False',
    ]

    for snippet in required_snippets:
        if snippet not in source:
            errors.append(f"missing required snippet: {snippet}")

    forbidden_snippets = [
        "metadata_present = has_gate_metadata(text)",
        "def has_gate_metadata(text: str) -> bool:",
    ]

    for snippet in forbidden_snippets:
        if snippet in source:
            errors.append(f"forbidden old classifier snippet still present: {snippet}")

    return {
        "source_validation_pass": not errors,
        "errors": errors,
    }


def validate_diff(diff_text: str) -> Dict[str, Any]:
    errors: List[str] = []

    if not diff_text.strip():
        errors.append("preview diff is empty")

    if f"--- a/{TARGET_TOOL_REL}" not in diff_text:
        errors.append("diff missing expected old target header")

    if f"+++ b/{TARGET_TOOL_REL}" not in diff_text:
        errors.append("diff missing expected new target header")

    if "def has_real_comment_gate_metadata_block(text: str) -> bool:" not in diff_text:
        errors.append("diff does not add refined helper")

    if "metadata_present = has_real_comment_gate_metadata_block(text)" not in diff_text:
        errors.append("diff does not replace metadata_present call")

    if "metadata_present = has_gate_metadata(text)" not in diff_text:
        errors.append("diff does not show old call removal/context")

    suspicious_added_lines: List[str] = []

    for line in diff_text.splitlines():
        if not line.startswith("+") or line.startswith("+++"):
            continue

        low = line.lower()
        if any(token in low for token in [
            "subprocess.run",
            "os.system",
            "shutil.",
            ".unlink(",
            ".rmdir(",
            "git add",
            "git commit",
            "send_order",
            "place_order",
            "live_trading",
        ]):
            suspicious_added_lines.append(line)

    if suspicious_added_lines:
        errors.append(f"suspicious added lines found: {suspicious_added_lines[:20]}")

    return {
        "diff_validation_pass": not errors,
        "errors": errors,
        "suspicious_added_lines": suspicious_added_lines,
    }


def main() -> int:
    for key, value in SAFETY_FLAGS.items():
        if not isinstance(value, bool):
            raise SystemExit(f"safety flag is not boolean: {key}")

    git_state = get_git_state()

    if not git_state["head"].startswith(EXPECTED_HEAD_PREFIX):
        return fail_closed(
            "unexpected HEAD",
            {
                "expected_head_prefix": EXPECTED_HEAD_PREFIX,
                "git_state": git_state,
            },
        )

    if git_state["dirty_tracked_count"] != 0:
        return fail_closed(
            "tracked files dirty; refusing approval",
            {
                "git_state": git_state,
            },
        )

    unknown_untracked = sorted(set(git_state["untracked_paths"]) - KNOWN_ALLOWED_UNTRACKED)
    if unknown_untracked:
        return fail_closed(
            "unknown untracked paths present",
            {
                "unknown_untracked": unknown_untracked,
                "git_state": git_state,
            },
        )

    try:
        preview = load_json(PREVIEW_JSON)
    except Exception as exc:
        return fail_closed(
            "could not load preview json",
            {
                "error": repr(exc),
                "git_state": git_state,
            },
        )

    if preview.get("preview_status") != "METADATA_CLASSIFIER_RULE_REFINEMENT_PREVIEW_V1_READY_NO_APPLY":
        return fail_closed(
            "preview status is not READY_NO_APPLY",
            {
                "preview_status": preview.get("preview_status"),
                "git_state": git_state,
            },
        )

    if preview.get("direct_apply_recommended_now") is not False:
        return fail_closed(
            "preview direct_apply_recommended_now must be false",
            {
                "direct_apply_recommended_now": preview.get("direct_apply_recommended_now"),
                "git_state": git_state,
            },
        )

    if preview.get("apply_recommended_now") is not False:
        return fail_closed(
            "preview apply_recommended_now must be false",
            {
                "apply_recommended_now": preview.get("apply_recommended_now"),
                "git_state": git_state,
            },
        )

    counts = preview.get("counts") if isinstance(preview.get("counts"), dict) else {}
    if counts.get("false_positive_count_confirmed") != 4:
        return fail_closed("false_positive_count_confirmed must be 4", {"counts": counts, "git_state": git_state})

    if counts.get("real_error_count_confirmed") != 0:
        return fail_closed("real_error_count_confirmed must be 0", {"counts": counts, "git_state": git_state})

    if counts.get("replacement_count") != 1 or counts.get("call_replacement_count") != 1:
        return fail_closed("replacement counts must both be 1", {"counts": counts, "git_state": git_state})

    regression = preview.get("regression") if isinstance(preview.get("regression"), dict) else {}
    tests = regression.get("tests") if isinstance(regression.get("tests"), dict) else {}

    required_tests = {
        "real_valid_comment_block",
        "string_literal_markers_ignored",
        "diff_template_markers_ignored",
        "broken_non_comment_block_rejected",
    }

    if regression.get("regression_pass") is not True:
        return fail_closed("preview regression_pass is not true", {"regression": regression, "git_state": git_state})

    missing_tests = sorted(required_tests - set(tests.keys()))
    failed_tests = sorted([name for name in required_tests if tests.get(name) is not True])

    if missing_tests or failed_tests:
        return fail_closed(
            "preview regression tests missing or failed",
            {
                "missing_tests": missing_tests,
                "failed_tests": failed_tests,
                "regression": regression,
                "git_state": git_state,
            },
        )

    if not PREVIEW_DIFF.exists():
        return fail_closed("preview diff missing", {"preview_diff": str(PREVIEW_DIFF), "git_state": git_state})

    if not PROPOSED_SOURCE.exists():
        return fail_closed("proposed source missing", {"proposed_source": str(PROPOSED_SOURCE), "git_state": git_state})

    if not TARGET_TOOL.exists():
        return fail_closed("target tool missing", {"target_tool": str(TARGET_TOOL), "git_state": git_state})

    if not is_untracked(TARGET_TOOL_REL, git_state):
        return fail_closed(
            "target tool should be untracked before refinement apply",
            {
                "target_tool_rel": TARGET_TOOL_REL,
                "git_state": git_state,
            },
        )

    diff_text = PREVIEW_DIFF.read_text(encoding="utf-8")
    proposed_source = PROPOSED_SOURCE.read_text(encoding="utf-8")

    diff_validation = validate_diff(diff_text)
    source_validation = validate_proposed_source(proposed_source)

    if not diff_validation["diff_validation_pass"]:
        return fail_closed(
            "diff validation failed",
            {
                "diff_validation": diff_validation,
                "git_state": git_state,
            },
        )

    if not source_validation["source_validation_pass"]:
        return fail_closed(
            "proposed source validation failed",
            {
                "source_validation": source_validation,
                "git_state": git_state,
            },
        )

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "approval_status": "METADATA_CLASSIFIER_RULE_REFINEMENT_APPROVAL_V1_READY_FOR_APPLY",
        "severity": "ATTENTION",
        "allowed_scope": "READ_ONLY_CLASSIFIER_RULE_APPROVAL",
        "final_decision": "BUILD_AND_RUN_METADATA_CLASSIFIER_RULE_REFINEMENT_APPLY_V1",
        "next_action": "APPLY_REFINED_CLASSIFIER_RULE_TO_UNTRACKED_STABILIZATION_TOOL_THEN_RERUN_REFRESH",
        "next_module": "edge_factory_os_metadata_classifier_rule_refinement_apply_v1.py",
        "reason": "preview and regression approved; refined classifier rule can be applied to the untracked stabilization tool only",
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "preview_json": str(PREVIEW_JSON),
        "preview_diff": str(PREVIEW_DIFF),
        "proposed_source": str(PROPOSED_SOURCE),
        "target_tool": str(TARGET_TOOL),
        "target_tool_rel": TARGET_TOOL_REL,
        "counts": counts,
        "regression": regression,
        "diff_validation": diff_validation,
        "source_validation": source_validation,
        "approved_target_count": 1,
        "approved_targets": [TARGET_TOOL_REL],
        "target_file_modified_now": False,
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
        "comment_only_or_classifier_rule_apply_next_step_allowed": True,
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

    latest_json = OUT_DIR / "metadata_classifier_rule_refinement_approval_v1_latest.json"
    timestamped_json = OUT_DIR / f"metadata_classifier_rule_refinement_approval_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "metadata_classifier_rule_refinement_approval_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    txt_lines = [
        "EDGE FACTORY OS METADATA CLASSIFIER RULE REFINEMENT APPROVAL v1",
        "=" * 100,
        f"approval_status: {payload['approval_status']}",
        f"severity: {payload['severity']}",
        f"allowed_scope: {payload['allowed_scope']}",
        f"final_decision: {payload['final_decision']}",
        f"next_action: {payload['next_action']}",
        f"next_module: {payload['next_module']}",
        f"reason: {payload['reason']}",
        "",
        "COUNTS",
        "-" * 100,
        json.dumps(counts, indent=2, sort_keys=True),
        "",
        "REGRESSION",
        "-" * 100,
        json.dumps(regression, indent=2, sort_keys=True),
        "",
        "DIFF VALIDATION",
        "-" * 100,
        json.dumps(diff_validation, indent=2, sort_keys=True),
        "",
        "SOURCE VALIDATION",
        "-" * 100,
        json.dumps(source_validation, indent=2, sort_keys=True),
        "",
        "APPROVED TARGETS",
        "-" * 100,
        json.dumps(payload["approved_targets"], indent=2, sort_keys=True),
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

    return 0


if __name__ == "__main__":
    raise SystemExit(main())