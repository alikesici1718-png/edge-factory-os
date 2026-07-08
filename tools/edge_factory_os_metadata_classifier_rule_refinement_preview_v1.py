from __future__ import annotations

import ast
import difflib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_metadata_classifier_rule_refinement_preview_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_metadata_classifier_rule_refinement_preview_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "578879b"

FREEZE_CONTROLLER_JSON = (
    LAB_ROOT
    / "edge_factory_os_stabilization_freeze_error_closure_controller_v1"
    / "stabilization_freeze_error_closure_controller_v1_latest.json"
)

INVALID_METADATA_INSPECTOR_JSON = (
    LAB_ROOT
    / "edge_factory_os_invalid_existing_metadata_block_inspector_v1"
    / "invalid_existing_metadata_block_inspector_v1_latest.json"
)

TRIAGE_CLASSIFIER_TOOL = REPO_ROOT / "tools" / "edge_factory_os_attention_triage_classifier_gate_review_refresh_after_metadata_v4.py"

KNOWN_ALLOWED_UNTRACKED: Set[str] = {
    "tools/edge_factory_os_attention_issue_policy_classifier_after_gate_metadata_v4.py",
    "tools/edge_factory_os_attention_triage_classifier_gate_review_refresh_after_metadata_v4.py",
    "tools/edge_factory_os_gate_metadata_patch_preview_v2.py",
    "tools/edge_factory_os_gate_metadata_patch_preview_v3.py",
    "tools/edge_factory_os_invalid_existing_metadata_block_inspector_v1.py",
    "tools/edge_factory_os_joint_null_distribution_validator_v1.py.readonly_fix_bak_20260514_022123",
    "tools/edge_factory_os_metadata_classifier_rule_refinement_preview_v1.py",
    "tools/edge_factory_os_old_short_guarded_runtime_reenable_apply_v1.py",
    "tools/edge_factory_os_post_commit_read_only_status_after_gate_metadata_v4.py",
    "tools/edge_factory_os_source_panel_anomaly_discovery_runner_v1.py.blocked_patch_bak_20260514_000647",
    "tools/edge_factory_os_stabilization_freeze_error_closure_controller_v1.py",
    "tools/edge_factory_os_universe_coverage_guard_v1.py",
}

SAFETY_FLAGS: Dict[str, bool] = {
    "stabilization_freeze_active": True,
    "read_only_preview": True,
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
        "preview_status": "METADATA_CLASSIFIER_RULE_REFINEMENT_PREVIEW_V1_FAIL_CLOSED",
        "severity": "BLOCKED",
        "allowed_scope": "READ_ONLY_CLASSIFIER_RULE_PREVIEW",
        "final_decision": "STOP_NO_APPLY",
        "next_action": "REVIEW_PREVIEW_INPUT_FAILURE",
        "next_module": None,
        "reason": reason,
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "freeze_controller_json": str(FREEZE_CONTROLLER_JSON),
        "invalid_metadata_inspector_json": str(INVALID_METADATA_INSPECTOR_JSON),
        "target_classifier_tool": str(TRIAGE_CLASSIFIER_TOOL),
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

    out = OUT_DIR / "metadata_classifier_rule_refinement_preview_v1_fail_closed_latest.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS METADATA CLASSIFIER RULE REFINEMENT PREVIEW v1")
    print("=" * 100)
    print("preview_status: METADATA_CLASSIFIER_RULE_REFINEMENT_PREVIEW_V1_FAIL_CLOSED")
    print(f"reason: {reason}")
    print(f"output: {out}")
    return 2


def is_untracked(path: Path, git_state: Dict[str, Any]) -> bool:
    rel = path.relative_to(REPO_ROOT).as_posix()
    return rel in set(git_state.get("untracked_paths", []))


def build_refined_helper_code() -> str:
    return '''
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
'''.strip("\n")


def make_preview_diff(original: str) -> Dict[str, Any]:
    old_func_pattern = re.compile(
        r"def has_gate_metadata\(text: str\) -> bool:\n"
        r"    return \(\n"
        r"        \"EDGE_FACTORY_GATE_METADATA_START\" in text\n"
        r"        and \"EDGE_FACTORY_GATE_METADATA_END\" in text\n"
        r"    \)\n",
        flags=re.MULTILINE,
    )

    new_helper = build_refined_helper_code() + "\n\n"

    replacement_count = 0
    updated = old_func_pattern.sub(new_helper, original)
    if updated != original:
        replacement_count += 1

    if replacement_count != 1:
        return {
            "preview_ok": False,
            "reason": f"expected exactly one has_gate_metadata function replacement; replacement_count={replacement_count}",
            "updated_text": original,
            "diff_text": "",
        }

    updated2 = updated.replace(
        "metadata_present = has_gate_metadata(text)",
        "metadata_present = has_real_comment_gate_metadata_block(text)",
    )

    call_replacement_count = updated.count("metadata_present = has_gate_metadata(text)") - updated2.count("metadata_present = has_gate_metadata(text)")
    if call_replacement_count != 1:
        return {
            "preview_ok": False,
            "reason": f"expected exactly one call replacement; call_replacement_count={call_replacement_count}",
            "updated_text": original,
            "diff_text": "",
        }

    diff_lines = list(difflib.unified_diff(
        original.splitlines(keepends=True),
        updated2.splitlines(keepends=True),
        fromfile="a/tools/edge_factory_os_attention_triage_classifier_gate_review_refresh_after_metadata_v4.py",
        tofile="b/tools/edge_factory_os_attention_triage_classifier_gate_review_refresh_after_metadata_v4.py",
        lineterm="",
    ))
    diff_text = "".join(diff_lines)

    return {
        "preview_ok": True,
        "reason": "refined classifier preview built successfully",
        "updated_text": updated2,
        "diff_text": diff_text,
        "replacement_count": replacement_count,
        "call_replacement_count": call_replacement_count,
    }


def run_static_regression_on_updated_source(updated_source: str) -> Dict[str, Any]:
    errors: List[str] = []

    try:
        ast.parse(updated_source, filename="edge_factory_os_attention_triage_classifier_gate_review_refresh_after_metadata_v4.py")
    except Exception as exc:
        errors.append(f"updated source syntax error: {repr(exc)}")

    namespace: Dict[str, Any] = {}
    try:
        helper_code = build_refined_helper_code()
        exec(helper_code, namespace)
        fn = namespace["has_real_comment_gate_metadata_block"]

        case_real_valid = "\n".join([
            "# EDGE_FACTORY_GATE_METADATA_START",
            "# gate_metadata_version: 1",
            "# EDGE_FACTORY_GATE_METADATA_END",
            "print('ok')",
        ])

        case_string_template = "\n".join([
            'x = "# EDGE_FACTORY_GATE_METADATA_START"',
            'y = "# EDGE_FACTORY_GATE_METADATA_END"',
        ])

        case_diff_string = "\n".join([
            'if line.startswith("+# EDGE_FACTORY_GATE_METADATA_START"):',
            '    pass',
            'if line.startswith("+# EDGE_FACTORY_GATE_METADATA_END"):',
            '    pass',
        ])

        case_broken = "\n".join([
            "# EDGE_FACTORY_GATE_METADATA_START",
            "not_a_comment_line = True",
            "# EDGE_FACTORY_GATE_METADATA_END",
        ])

        tests = {
            "real_valid_comment_block": fn(case_real_valid) is True,
            "string_literal_markers_ignored": fn(case_string_template) is False,
            "diff_template_markers_ignored": fn(case_diff_string) is False,
            "broken_non_comment_block_rejected": fn(case_broken) is False,
        }

        for name, passed in tests.items():
            if not passed:
                errors.append(f"regression test failed: {name}")

        return {
            "regression_pass": not errors,
            "errors": errors,
            "tests": tests,
        }

    except Exception as exc:
        errors.append(f"regression execution failed: {repr(exc)}")
        return {
            "regression_pass": False,
            "errors": errors,
            "tests": {},
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
            "tracked files dirty; refusing classifier refinement preview",
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
        freeze = load_json(FREEZE_CONTROLLER_JSON)
        invalid = load_json(INVALID_METADATA_INSPECTOR_JSON)
    except Exception as exc:
        return fail_closed(
            "could not load required stabilization inputs",
            {
                "error": repr(exc),
                "git_state": git_state,
            },
        )

    if freeze.get("controller_status") != "STABILIZATION_FREEZE_ERROR_CLOSURE_CONTROLLER_V1_OPEN_ITEMS_REMAIN":
        return fail_closed(
            "freeze controller status unexpected",
            {
                "controller_status": freeze.get("controller_status"),
                "git_state": git_state,
            },
        )

    if invalid.get("inspector_status") != "INVALID_EXISTING_METADATA_BLOCK_INSPECTOR_V1_FALSE_POSITIVE_CONFIRMED":
        return fail_closed(
            "invalid metadata inspector did not confirm false positive",
            {
                "inspector_status": invalid.get("inspector_status"),
                "git_state": git_state,
            },
        )

    if not TRIAGE_CLASSIFIER_TOOL.exists():
        return fail_closed(
            "target triage classifier tool missing",
            {
                "target": str(TRIAGE_CLASSIFIER_TOOL),
                "git_state": git_state,
            },
        )

    if not is_untracked(TRIAGE_CLASSIFIER_TOOL, git_state):
        return fail_closed(
            "target triage classifier tool is not untracked as expected; refusing preview",
            {
                "target": str(TRIAGE_CLASSIFIER_TOOL),
                "git_state": git_state,
            },
        )

    original = TRIAGE_CLASSIFIER_TOOL.read_text(encoding="utf-8")
    if original.startswith("\ufeff"):
        return fail_closed("target classifier tool has BOM", {"git_state": git_state})

    preview = make_preview_diff(original)
    if not preview["preview_ok"]:
        return fail_closed(
            "could not build refined classifier preview",
            {
                "preview_reason": preview["reason"],
                "git_state": git_state,
            },
        )

    regression = run_static_regression_on_updated_source(preview["updated_text"])

    if not regression["regression_pass"]:
        return fail_closed(
            "refined classifier regression failed",
            {
                "regression": regression,
                "git_state": git_state,
            },
        )

    diff_path = OUT_DIR / "metadata_classifier_rule_refinement_preview_v1_latest.diff"
    proposed_source_path = OUT_DIR / "edge_factory_os_attention_triage_classifier_gate_review_refresh_after_metadata_v4_refined_preview.py"

    diff_path.write_text(preview["diff_text"], encoding="utf-8")
    proposed_source_path.write_text(preview["updated_text"], encoding="utf-8")

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "preview_status": "METADATA_CLASSIFIER_RULE_REFINEMENT_PREVIEW_V1_READY_NO_APPLY",
        "severity": "ATTENTION",
        "allowed_scope": "READ_ONLY_CLASSIFIER_RULE_PREVIEW",
        "final_decision": "REVIEW_CLASSIFIER_RULE_REFINEMENT_THEN_APPROVAL_IF_ACCEPTED",
        "next_action": "BUILD_METADATA_CLASSIFIER_RULE_REFINEMENT_APPROVAL_V1_NO_RUNTIME_ACTION",
        "next_module": "edge_factory_os_metadata_classifier_rule_refinement_approval_v1.py",
        "reason": "preview refines classifier to ignore metadata marker strings and only accept real comment marker blocks",
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "freeze_controller_json": str(FREEZE_CONTROLLER_JSON),
        "invalid_metadata_inspector_json": str(INVALID_METADATA_INSPECTOR_JSON),
        "target_classifier_tool": str(TRIAGE_CLASSIFIER_TOOL),
        "diff_path": str(diff_path),
        "proposed_source_path": str(proposed_source_path),
        "counts": {
            "false_positive_count_confirmed": (invalid.get("counts") or {}).get("false_positive_count"),
            "real_error_count_confirmed": (invalid.get("counts") or {}).get("real_error_count"),
            "replacement_count": preview.get("replacement_count"),
            "call_replacement_count": preview.get("call_replacement_count"),
            "direct_apply_recommended_now_count": 0,
            "apply_recommended_now_count": 0,
        },
        "regression": regression,
        "patch_target_is_untracked": True,
        "target_file_modified_now": False,
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
        "preview_fix_candidate_now": True,
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

    latest_json = OUT_DIR / "metadata_classifier_rule_refinement_preview_v1_latest.json"
    timestamped_json = OUT_DIR / f"metadata_classifier_rule_refinement_preview_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "metadata_classifier_rule_refinement_preview_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    txt_lines = [
        "EDGE FACTORY OS METADATA CLASSIFIER RULE REFINEMENT PREVIEW v1",
        "=" * 100,
        f"preview_status: {payload['preview_status']}",
        f"severity: {payload['severity']}",
        f"allowed_scope: {payload['allowed_scope']}",
        f"final_decision: {payload['final_decision']}",
        f"next_action: {payload['next_action']}",
        f"next_module: {payload['next_module']}",
        f"reason: {payload['reason']}",
        "",
        "COUNTS",
        "-" * 100,
        json.dumps(payload["counts"], indent=2, sort_keys=True),
        "",
        "REGRESSION",
        "-" * 100,
        json.dumps(regression, indent=2, sort_keys=True),
        "",
        "OUTPUTS",
        "-" * 100,
        f"latest_json: {latest_json}",
        f"timestamped_json: {timestamped_json}",
        f"latest_txt: {latest_txt}",
        f"diff_path: {diff_path}",
        f"proposed_source_path: {proposed_source_path}",
        "",
        "SAFETY",
        "-" * 100,
        json.dumps(SAFETY_FLAGS, indent=2, sort_keys=True),
        "",
        "GIT STATE",
        "-" * 100,
        json.dumps(git_state, indent=2, sort_keys=True),
    ]

    latest_txt.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")

    print("\n".join(txt_lines))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())