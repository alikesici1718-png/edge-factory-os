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

MODULE_NAME = "edge_factory_os_invalid_existing_metadata_block_inspector_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_invalid_existing_metadata_block_inspector_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

POLICY_CLASSIFIER_JSON = (
    LAB_ROOT
    / "edge_factory_os_attention_issue_policy_classifier_after_gate_metadata_v4"
    / "attention_issue_policy_classifier_after_metadata_v4_latest.json"
)

EXPECTED_HEAD_PREFIX = "578879b"

EXPECTED_P0_INVALID_PATHS: Set[str] = {
    "tools/edge_factory_os_full_system_read_only_audit_refresh_after_gate_metadata_v4.py",
    "tools/edge_factory_os_gate_metadata_patch_apply_v4.py",
    "tools/edge_factory_os_gate_metadata_patch_approval_v4.py",
    "tools/edge_factory_os_gate_metadata_patch_preview_v4.py",
}

KNOWN_ALLOWED_UNTRACKED: Set[str] = {
    "tools/edge_factory_os_attention_issue_policy_classifier_after_gate_metadata_v4.py",
    "tools/edge_factory_os_attention_triage_classifier_gate_review_refresh_after_metadata_v4.py",
    "tools/edge_factory_os_gate_metadata_patch_preview_v2.py",
    "tools/edge_factory_os_gate_metadata_patch_preview_v3.py",
    "tools/edge_factory_os_invalid_existing_metadata_block_inspector_v1.py",
    "tools/edge_factory_os_joint_null_distribution_validator_v1.py.readonly_fix_bak_20260514_022123",
    "tools/edge_factory_os_old_short_guarded_runtime_reenable_apply_v1.py",
    "tools/edge_factory_os_post_commit_read_only_status_after_gate_metadata_v4.py",
    "tools/edge_factory_os_source_panel_anomaly_discovery_runner_v1.py.blocked_patch_bak_20260514_000647",
    "tools/edge_factory_os_universe_coverage_guard_v1.py",
}

SAFETY_FLAGS: Dict[str, bool] = {
    "read_only_inspector": True,
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


def is_tracked_file(rel_path: str) -> bool:
    result = run_cmd(["git", "ls-files", "--error-unmatch", rel_path])
    return result.returncode == 0


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def fail_closed(reason: str, extra: Optional[Dict[str, Any]] = None) -> int:
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "inspector_status": "INVALID_EXISTING_METADATA_BLOCK_INSPECTOR_V1_FAIL_CLOSED",
        "severity": "BLOCKED",
        "allowed_scope": "READ_ONLY_INSPECTION",
        "final_decision": "STOP_NO_APPLY",
        "next_action": "REVIEW_INSPECTOR_INPUT_FAILURE",
        "next_module": None,
        "reason": reason,
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "policy_classifier_json": str(POLICY_CLASSIFIER_JSON),
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

    out = OUT_DIR / "invalid_existing_metadata_block_inspector_v1_fail_closed_latest.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS INVALID EXISTING METADATA BLOCK INSPECTOR v1")
    print("=" * 100)
    print("inspector_status: INVALID_EXISTING_METADATA_BLOCK_INSPECTOR_V1_FAIL_CLOSED")
    print(f"reason: {reason}")
    print(f"output: {out}")
    return 2


def find_real_comment_metadata_blocks(lines: List[str]) -> List[Dict[str, Any]]:
    blocks: List[Dict[str, Any]] = []

    start_indices = [
        idx for idx, line in enumerate(lines)
        if line.strip() == "# EDGE_FACTORY_GATE_METADATA_START"
    ]

    for start in start_indices:
        end: Optional[int] = None
        for idx in range(start + 1, len(lines)):
            if lines[idx].strip() == "# EDGE_FACTORY_GATE_METADATA_END":
                end = idx
                break

        if end is None:
            blocks.append({
                "start_line_1based": start + 1,
                "end_line_1based": None,
                "valid_comment_block_shape": False,
                "errors": ["missing end marker"],
                "lines": lines[start:start + 30],
            })
            continue

        block_lines = lines[start:end + 1]
        errors: List[str] = []

        for local_idx, raw in enumerate(block_lines):
            if raw.strip() == "":
                continue
            if not raw.lstrip().startswith("#"):
                errors.append(f"line {start + local_idx + 1} is not a comment line: {raw}")

        blocks.append({
            "start_line_1based": start + 1,
            "end_line_1based": end + 1,
            "valid_comment_block_shape": not errors,
            "errors": errors,
            "lines": block_lines,
        })

    return blocks


class MarkerStringVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.string_marker_locations: List[Dict[str, Any]] = []

    def visit_Constant(self, node: ast.Constant) -> Any:
        if isinstance(node.value, str) and (
            "EDGE_FACTORY_GATE_METADATA_START" in node.value
            or "EDGE_FACTORY_GATE_METADATA_END" in node.value
        ):
            self.string_marker_locations.append({
                "lineno": getattr(node, "lineno", None),
                "col_offset": getattr(node, "col_offset", None),
                "preview": node.value[:220],
            })
        self.generic_visit(node)


def find_line_marker_occurrences(lines: List[str]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for idx, line in enumerate(lines, start=1):
        if "EDGE_FACTORY_GATE_METADATA_START" in line or "EDGE_FACTORY_GATE_METADATA_END" in line:
            out.append({
                "line_1based": idx,
                "is_comment_marker_line": line.strip() in {
                    "# EDGE_FACTORY_GATE_METADATA_START",
                    "# EDGE_FACTORY_GATE_METADATA_END",
                },
                "line": line[:260],
            })
    return out


def inspect_path(rel_path: str) -> Dict[str, Any]:
    path = REPO_ROOT / rel_path
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    syntax_error: Optional[str] = None
    tree: Optional[ast.AST] = None

    try:
        tree = ast.parse(text, filename=rel_path)
    except Exception as exc:
        syntax_error = repr(exc)

    real_comment_blocks = find_real_comment_metadata_blocks(lines)
    line_marker_occurrences = find_line_marker_occurrences(lines)

    string_marker_locations: List[Dict[str, Any]] = []
    if tree is not None:
        visitor = MarkerStringVisitor()
        visitor.visit(tree)
        string_marker_locations = visitor.string_marker_locations

    has_real_comment_block = bool(real_comment_blocks)
    has_string_markers = bool(string_marker_locations)
    has_line_markers = bool(line_marker_occurrences)

    if text.startswith("\ufeff"):
        disposition = "REAL_FILE_BOM_ERROR_REQUIRES_REVIEW"
        conclusion = "REAL_ERROR"
    elif syntax_error:
        disposition = "REAL_SYNTAX_ERROR_REQUIRES_REVIEW"
        conclusion = "REAL_ERROR"
    elif has_real_comment_block:
        invalid_blocks = [
            block for block in real_comment_blocks
            if not block.get("valid_comment_block_shape")
        ]
        if invalid_blocks:
            disposition = "REAL_METADATA_COMMENT_BLOCK_INVALID_REQUIRES_TARGETED_PREVIEW"
            conclusion = "REAL_METADATA_ERROR"
        else:
            disposition = "REAL_METADATA_COMMENT_BLOCK_PRESENT_AND_VALID_SHAPE"
            conclusion = "VALID_METADATA_PRESENT"
    elif has_string_markers:
        disposition = "FALSE_POSITIVE_METADATA_TEMPLATE_STRING_MARKERS_NO_PATCH_REQUIRED"
        conclusion = "FALSE_POSITIVE"
    elif has_line_markers:
        disposition = "MARKERS_PRESENT_BUT_NOT_COMMENT_BLOCK_REVIEW_ONLY"
        conclusion = "REVIEW_ONLY"
    else:
        disposition = "NO_METADATA_MARKERS_FOUND_REVIEW_CLASSIFIER_RULE"
        conclusion = "CLASSIFIER_RULE_FALSE_POSITIVE"

    return {
        "path": rel_path,
        "tracked": is_tracked_file(rel_path),
        "file_exists": path.exists(),
        "syntax_error": syntax_error,
        "bom_detected": text.startswith("\ufeff"),
        "has_real_comment_metadata_block": has_real_comment_block,
        "real_comment_metadata_blocks": real_comment_blocks,
        "has_string_literal_metadata_markers": has_string_markers,
        "string_literal_metadata_marker_locations": string_marker_locations,
        "has_any_line_marker_occurrence": has_line_markers,
        "line_marker_occurrences": line_marker_occurrences,
        "conclusion": conclusion,
        "disposition": disposition,
        "apply_recommended_now": False,
        "preview_fix_candidate_now": False,
        "direct_apply_recommended_now": False,
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
            "tracked files dirty; refusing inspection continuation",
            {
                "git_state": git_state,
            },
        )

    untracked = set(git_state["untracked_paths"])
    unknown_untracked = sorted(untracked - KNOWN_ALLOWED_UNTRACKED)

    try:
        policy = load_json(POLICY_CLASSIFIER_JSON)
    except Exception as exc:
        return fail_closed(
            "could not load policy classifier json",
            {
                "error": repr(exc),
                "git_state": git_state,
            },
        )

    if policy.get("classifier_status") != "ATTENTION_ISSUE_POLICY_CLASSIFIER_AFTER_METADATA_V4_READY":
        return fail_closed(
            "policy classifier status is not ready",
            {
                "classifier_status": policy.get("classifier_status"),
                "git_state": git_state,
            },
        )

    p0_invalid = policy.get("p0_invalid_metadata")
    if not isinstance(p0_invalid, list):
        return fail_closed(
            "p0_invalid_metadata missing or not list",
            {
                "git_state": git_state,
            },
        )

    p0_paths = {str(row.get("path", "")) for row in p0_invalid}

    if p0_paths != EXPECTED_P0_INVALID_PATHS:
        return fail_closed(
            "P0 invalid metadata path set mismatch",
            {
                "expected_p0_paths": sorted(EXPECTED_P0_INVALID_PATHS),
                "actual_p0_paths": sorted(p0_paths),
                "missing": sorted(EXPECTED_P0_INVALID_PATHS - p0_paths),
                "extra": sorted(p0_paths - EXPECTED_P0_INVALID_PATHS),
                "git_state": git_state,
            },
        )

    inspections = [inspect_path(path) for path in sorted(EXPECTED_P0_INVALID_PATHS)]

    conclusion_counts: Dict[str, int] = {}
    disposition_counts: Dict[str, int] = {}

    for row in inspections:
        conclusion_counts[row["conclusion"]] = conclusion_counts.get(row["conclusion"], 0) + 1
        disposition_counts[row["disposition"]] = disposition_counts.get(row["disposition"], 0) + 1

    false_positive_count = conclusion_counts.get("FALSE_POSITIVE", 0)
    real_error_count = sum(
        count for conclusion, count in conclusion_counts.items()
        if conclusion in {"REAL_ERROR", "REAL_METADATA_ERROR"}
    )

    warnings: List[str] = []
    if unknown_untracked:
        warnings.append(f"unknown untracked paths present: {unknown_untracked}")

    if real_error_count == 0 and false_positive_count == len(EXPECTED_P0_INVALID_PATHS):
        inspector_status = "INVALID_EXISTING_METADATA_BLOCK_INSPECTOR_V1_FALSE_POSITIVE_CONFIRMED"
        final_decision = "CLOSE_P0_INVALID_METADATA_AS_CLASSIFIER_FALSE_POSITIVE"
        next_action = "BUILD_CLASSIFIER_RULE_REFINEMENT_OR_P1_UNTRACKED_REVIEW_PLAN_NO_APPLY"
        next_module = "edge_factory_os_metadata_classifier_rule_refinement_preview_v1.py"
        reason = "4/4 P0 invalid metadata findings are template string marker false positives; no target patch required"
        severity = "ATTENTION"
    elif real_error_count == 0:
        inspector_status = "INVALID_EXISTING_METADATA_BLOCK_INSPECTOR_V1_NO_REAL_METADATA_ERROR_REVIEW_CLASSIFIER"
        final_decision = "CLOSE_REAL_METADATA_ERROR_AND_REVIEW_CLASSIFIER_RULE"
        next_action = "BUILD_CLASSIFIER_RULE_REFINEMENT_OR_P1_UNTRACKED_REVIEW_PLAN_NO_APPLY"
        next_module = "edge_factory_os_metadata_classifier_rule_refinement_preview_v1.py"
        reason = "P0 invalid metadata findings are not real metadata block errors"
        severity = "ATTENTION"
    else:
        inspector_status = "INVALID_EXISTING_METADATA_BLOCK_INSPECTOR_V1_REAL_METADATA_ERROR_FOUND"
        final_decision = "BUILD_TARGETED_METADATA_REPAIR_PREVIEW_FOR_REAL_ERRORS_ONLY"
        next_action = "BUILD_TARGETED_REAL_METADATA_REPAIR_PREVIEW_NO_APPLY"
        next_module = "edge_factory_os_real_metadata_block_repair_preview_v1.py"
        reason = f"real metadata errors found: {real_error_count}"
        severity = "BLOCKED"

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "inspector_status": inspector_status,
        "severity": severity,
        "allowed_scope": "READ_ONLY_INSPECTION",
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "reason": reason,
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "source_policy_classifier_json": str(POLICY_CLASSIFIER_JSON),
        "latest_commit": git_state["head"],
        "counts": {
            "p0_invalid_input_count": len(p0_invalid),
            "inspected_path_count": len(inspections),
            "false_positive_count": false_positive_count,
            "real_error_count": real_error_count,
            "unknown_untracked_count": len(unknown_untracked),
            "direct_apply_recommended_now_count": 0,
            "apply_recommended_now_count": 0,
            "preview_fix_candidate_now_count": 0,
        },
        "conclusion_counts": dict(sorted(conclusion_counts.items())),
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "inspections": inspections,
        "warnings": warnings,
        "critical_issue_count": real_error_count,
        "warning_count": len(warnings),
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
        "preview_fix_candidate_now": False,
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

    latest_json = OUT_DIR / "invalid_existing_metadata_block_inspector_v1_latest.json"
    timestamped_json = OUT_DIR / f"invalid_existing_metadata_block_inspector_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "invalid_existing_metadata_block_inspector_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    txt_lines = [
        "EDGE FACTORY OS INVALID EXISTING METADATA BLOCK INSPECTOR v1",
        "=" * 100,
        f"inspector_status: {payload['inspector_status']}",
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
        "CONCLUSION COUNTS",
        "-" * 100,
        json.dumps(payload["conclusion_counts"], indent=2, sort_keys=True),
        "",
        "DISPOSITION COUNTS",
        "-" * 100,
        json.dumps(payload["disposition_counts"], indent=2, sort_keys=True),
        "",
        "INSPECTIONS",
        "-" * 100,
        json.dumps(inspections, indent=2, sort_keys=True),
        "",
        "WARNINGS",
        "-" * 100,
        json.dumps(warnings, indent=2, sort_keys=True),
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

    return 0 if real_error_count == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())