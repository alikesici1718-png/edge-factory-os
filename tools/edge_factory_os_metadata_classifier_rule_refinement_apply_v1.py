from __future__ import annotations

import ast
import difflib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_metadata_classifier_rule_refinement_apply_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_metadata_classifier_rule_refinement_apply_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "578879b"

PREVIEW_JSON = (
    LAB_ROOT
    / "edge_factory_os_metadata_classifier_rule_refinement_preview_v1"
    / "metadata_classifier_rule_refinement_preview_v1_latest.json"
)

APPROVAL_JSON = (
    LAB_ROOT
    / "edge_factory_os_metadata_classifier_rule_refinement_approval_v1"
    / "metadata_classifier_rule_refinement_approval_v1_latest.json"
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
    "tools/edge_factory_os_metadata_classifier_rule_refinement_apply_v1.py",
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
    "apply_performed_now": True,
    "classifier_rule_apply_only": True,
    "target_is_untracked_stabilization_tool": True,
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


def normalize_diff(text: str) -> str:
    return "\n".join(text.strip().splitlines()).strip()


def fail_closed(reason: str, extra: Optional[Dict[str, Any]] = None) -> int:
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "apply_status": "METADATA_CLASSIFIER_RULE_REFINEMENT_APPLY_V1_FAIL_CLOSED",
        "severity": "BLOCKED",
        "allowed_scope": "CLASSIFIER_RULE_APPLY_TO_UNTRACKED_STABILIZATION_TOOL",
        "final_decision": "STOP_NO_PARTIAL_APPLY",
        "next_action": "REVIEW_APPLY_FAILURE",
        "next_module": None,
        "reason": reason,
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "preview_json": str(PREVIEW_JSON),
        "approval_json": str(APPROVAL_JSON),
        "target_tool": str(TARGET_TOOL),
        "safety_flags": {**SAFETY_FLAGS, "apply_performed_now": False},
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
        "target_files_modified": [],
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

    out = OUT_DIR / "metadata_classifier_rule_refinement_apply_v1_fail_closed_latest.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS METADATA CLASSIFIER RULE REFINEMENT APPLY v1")
    print("=" * 100)
    print("apply_status: METADATA_CLASSIFIER_RULE_REFINEMENT_APPLY_V1_FAIL_CLOSED")
    print(f"reason: {reason}")
    print(f"output: {out}")
    return 2


def is_untracked(rel_path: str, git_state: Dict[str, Any]) -> bool:
    return rel_path in set(git_state.get("untracked_paths", []))


def compute_diff(original: str, proposed: str) -> str:
    diff_lines = list(difflib.unified_diff(
        original.splitlines(keepends=True),
        proposed.splitlines(keepends=True),
        fromfile=f"a/{TARGET_TOOL_REL}",
        tofile=f"b/{TARGET_TOOL_REL}",
        lineterm="",
    ))
    return "".join(diff_lines)


def validate_source(source: str) -> Dict[str, Any]:
    errors: List[str] = []

    if source.startswith("\ufeff"):
        errors.append("source has BOM")

    try:
        ast.parse(source, filename=TARGET_TOOL_REL)
    except Exception as exc:
        errors.append(f"syntax error: {repr(exc)}")

    required_snippets = [
        "def has_real_comment_gate_metadata_block(text: str) -> bool:",
        'line.strip() == "# EDGE_FACTORY_GATE_METADATA_START"',
        'lines[end].strip() == "# EDGE_FACTORY_GATE_METADATA_END"',
        "metadata_present = has_real_comment_gate_metadata_block(text)",
        '"direct_apply_recommended_now": False',
        '"apply_recommended_now": False',
    ]

    forbidden_snippets = [
        "def has_gate_metadata(text: str) -> bool:",
        "metadata_present = has_gate_metadata(text)",
    ]

    for snippet in required_snippets:
        if snippet not in source:
            errors.append(f"missing required snippet: {snippet}")

    for snippet in forbidden_snippets:
        if snippet in source:
            errors.append(f"forbidden old snippet still present: {snippet}")

    return {
        "source_validation_pass": not errors,
        "errors": errors,
    }


def run_embedded_regression() -> Dict[str, Any]:
    errors: List[str] = []

    def has_real_comment_gate_metadata_block(text: str) -> bool:
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

    tests = {
        "real_valid_comment_block": has_real_comment_gate_metadata_block(
            "# EDGE_FACTORY_GATE_METADATA_START\n# gate_metadata_version: 1\n# EDGE_FACTORY_GATE_METADATA_END"
        ) is True,
        "string_literal_markers_ignored": has_real_comment_gate_metadata_block(
            'x = "# EDGE_FACTORY_GATE_METADATA_START"\ny = "# EDGE_FACTORY_GATE_METADATA_END"'
        ) is False,
        "diff_template_markers_ignored": has_real_comment_gate_metadata_block(
            'if line.startswith("+# EDGE_FACTORY_GATE_METADATA_START"):\n    pass\nif line.startswith("+# EDGE_FACTORY_GATE_METADATA_END"):\n    pass'
        ) is False,
        "broken_non_comment_block_rejected": has_real_comment_gate_metadata_block(
            "# EDGE_FACTORY_GATE_METADATA_START\nnot_a_comment = True\n# EDGE_FACTORY_GATE_METADATA_END"
        ) is False,
    }

    for name, ok in tests.items():
        if not ok:
            errors.append(f"regression failed: {name}")

    return {
        "regression_pass": not errors,
        "errors": errors,
        "tests": tests,
    }


def main() -> int:
    for key, value in SAFETY_FLAGS.items():
        if not isinstance(value, bool):
            raise SystemExit(f"safety flag is not boolean: {key}")

    git_state_before = get_git_state()

    if not git_state_before["head"].startswith(EXPECTED_HEAD_PREFIX):
        return fail_closed(
            "unexpected HEAD",
            {
                "expected_head_prefix": EXPECTED_HEAD_PREFIX,
                "git_state_before": git_state_before,
            },
        )

    if git_state_before["dirty_tracked_count"] != 0:
        return fail_closed(
            "tracked files dirty; refusing apply",
            {
                "git_state_before": git_state_before,
            },
        )

    unknown_untracked = sorted(set(git_state_before["untracked_paths"]) - KNOWN_ALLOWED_UNTRACKED)
    if unknown_untracked:
        return fail_closed(
            "unknown untracked paths present",
            {
                "unknown_untracked": unknown_untracked,
                "git_state_before": git_state_before,
            },
        )

    try:
        preview = load_json(PREVIEW_JSON)
        approval = load_json(APPROVAL_JSON)
    except Exception as exc:
        return fail_closed(
            "could not load preview/approval json",
            {
                "error": repr(exc),
                "git_state_before": git_state_before,
            },
        )

    if preview.get("preview_status") != "METADATA_CLASSIFIER_RULE_REFINEMENT_PREVIEW_V1_READY_NO_APPLY":
        return fail_closed("preview not ready", {"preview_status": preview.get("preview_status"), "git_state_before": git_state_before})

    if approval.get("approval_status") != "METADATA_CLASSIFIER_RULE_REFINEMENT_APPROVAL_V1_READY_FOR_APPLY":
        return fail_closed("approval not ready", {"approval_status": approval.get("approval_status"), "git_state_before": git_state_before})

    approved_targets = approval.get("approved_targets")
    if approved_targets != [TARGET_TOOL_REL]:
        return fail_closed(
            "approved targets mismatch",
            {
                "approved_targets": approved_targets,
                "expected": [TARGET_TOOL_REL],
                "git_state_before": git_state_before,
            },
        )

    if approval.get("comment_only_or_classifier_rule_apply_next_step_allowed") is not True:
        return fail_closed(
            "approval does not allow classifier rule apply next step",
            {
                "value": approval.get("comment_only_or_classifier_rule_apply_next_step_allowed"),
                "git_state_before": git_state_before,
            },
        )

    if not TARGET_TOOL.exists():
        return fail_closed("target tool missing", {"target_tool": str(TARGET_TOOL), "git_state_before": git_state_before})

    if not is_untracked(TARGET_TOOL_REL, git_state_before):
        return fail_closed(
            "target tool must be untracked before apply",
            {
                "target_tool_rel": TARGET_TOOL_REL,
                "git_state_before": git_state_before,
            },
        )

    if not PREVIEW_DIFF.exists():
        return fail_closed("preview diff missing", {"preview_diff": str(PREVIEW_DIFF), "git_state_before": git_state_before})

    if not PROPOSED_SOURCE.exists():
        return fail_closed("proposed source missing", {"proposed_source": str(PROPOSED_SOURCE), "git_state_before": git_state_before})

    original = TARGET_TOOL.read_text(encoding="utf-8")
    proposed = PROPOSED_SOURCE.read_text(encoding="utf-8")
    preview_diff = PREVIEW_DIFF.read_text(encoding="utf-8")

    source_validation = validate_source(proposed)
    if not source_validation["source_validation_pass"]:
        return fail_closed(
            "proposed source validation failed",
            {
                "source_validation": source_validation,
                "git_state_before": git_state_before,
            },
        )

    generated_diff = compute_diff(original, proposed)

    if normalize_diff(generated_diff) != normalize_diff(preview_diff):
        return fail_closed(
            "generated diff does not match approved preview diff",
            {
                "generated_diff_preview": generated_diff[:4000],
                "approved_diff_preview": preview_diff[:4000],
                "git_state_before": git_state_before,
            },
        )

    regression = run_embedded_regression()
    if not regression["regression_pass"]:
        return fail_closed(
            "embedded regression failed",
            {
                "regression": regression,
                "git_state_before": git_state_before,
            },
        )

    TARGET_TOOL.write_text(proposed, encoding="utf-8")

    post_text = TARGET_TOOL.read_text(encoding="utf-8")
    post_validation = validate_source(post_text)

    if not post_validation["source_validation_pass"]:
        return fail_closed(
            "post-apply validation failed; manual review required",
            {
                "post_validation": post_validation,
                "git_state_before": git_state_before,
                "git_state_after_failure": get_git_state(),
            },
        )

    git_state_after = get_git_state()

    if git_state_after["dirty_tracked_count"] != 0:
        return fail_closed(
            "tracked files became dirty after applying to untracked tool",
            {
                "git_state_before": git_state_before,
                "git_state_after": git_state_after,
            },
        )

    if TARGET_TOOL_REL not in set(git_state_after["untracked_paths"]):
        return fail_closed(
            "target tool no longer appears as untracked after apply",
            {
                "target_tool_rel": TARGET_TOOL_REL,
                "git_state_before": git_state_before,
                "git_state_after": git_state_after,
            },
        )

    applied_diff_path = OUT_DIR / "metadata_classifier_rule_refinement_apply_v1_applied_diff_latest.diff"
    applied_diff_path.write_text(generated_diff, encoding="utf-8")

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "apply_status": "METADATA_CLASSIFIER_RULE_REFINEMENT_APPLY_V1_APPLIED_TO_UNTRACKED_TOOL",
        "severity": "ATTENTION",
        "allowed_scope": "CLASSIFIER_RULE_APPLY_TO_UNTRACKED_STABILIZATION_TOOL",
        "final_decision": "RERUN_TRIAGE_CLASSIFIER_REFRESH_AND_POLICY_CLASSIFIER_WITH_REFINED_RULE",
        "next_action": "RERUN_REFINED_TRIAGE_CLASSIFIER_REFRESH_NO_RUNTIME_ACTION",
        "next_module": TARGET_TOOL_REL,
        "reason": "refined classifier rule applied to the untracked stabilization tool only; tracked repo files remain clean",
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "preview_json": str(PREVIEW_JSON),
        "approval_json": str(APPROVAL_JSON),
        "target_tool": str(TARGET_TOOL),
        "target_tool_rel": TARGET_TOOL_REL,
        "applied_diff_path": str(applied_diff_path),
        "modified_target_count": 1,
        "modified_targets": [TARGET_TOOL_REL],
        "target_files_modified": [TARGET_TOOL_REL],
        "source_validation": source_validation,
        "post_validation": post_validation,
        "regression": regression,
        "tracked_files_modified_count": 0,
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
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
        "git_state_before": git_state_before,
        "git_state_after": git_state_after,
    }

    latest_json = OUT_DIR / "metadata_classifier_rule_refinement_apply_v1_latest.json"
    timestamped_json = OUT_DIR / f"metadata_classifier_rule_refinement_apply_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "metadata_classifier_rule_refinement_apply_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    txt_lines = [
        "EDGE FACTORY OS METADATA CLASSIFIER RULE REFINEMENT APPLY v1",
        "=" * 100,
        f"apply_status: {payload['apply_status']}",
        f"severity: {payload['severity']}",
        f"allowed_scope: {payload['allowed_scope']}",
        f"final_decision: {payload['final_decision']}",
        f"next_action: {payload['next_action']}",
        f"next_module: {payload['next_module']}",
        f"reason: {payload['reason']}",
        f"modified_target_count: {payload['modified_target_count']}",
        "",
        "MODIFIED TARGETS",
        "-" * 100,
        json.dumps(payload["modified_targets"], indent=2, sort_keys=True),
        "",
        "SOURCE VALIDATION",
        "-" * 100,
        json.dumps(source_validation, indent=2, sort_keys=True),
        "",
        "POST VALIDATION",
        "-" * 100,
        json.dumps(post_validation, indent=2, sort_keys=True),
        "",
        "REGRESSION",
        "-" * 100,
        json.dumps(regression, indent=2, sort_keys=True),
        "",
        "SAFETY",
        "-" * 100,
        json.dumps(SAFETY_FLAGS, indent=2, sort_keys=True),
        "",
        "GIT STATE BEFORE",
        "-" * 100,
        json.dumps(git_state_before, indent=2, sort_keys=True),
        "",
        "GIT STATE AFTER",
        "-" * 100,
        json.dumps(git_state_after, indent=2, sort_keys=True),
        "",
        "OUTPUTS",
        "-" * 100,
        f"latest_json: {latest_json}",
        f"timestamped_json: {timestamped_json}",
        f"latest_txt: {latest_txt}",
        f"applied_diff_path: {applied_diff_path}",
    ]

    latest_txt.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")

    print("\n".join(txt_lines))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())