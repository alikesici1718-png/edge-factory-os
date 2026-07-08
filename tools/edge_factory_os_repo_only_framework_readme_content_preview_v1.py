from __future__ import annotations

import ast
import difflib
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_framework_readme_content_preview_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_repo_only_framework_readme_content_preview_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "1656d19"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_framework_readme_content_preview_v1.py"

CONTRACT_JSON = LAB_ROOT / "edge_factory_os_repo_only_framework_readme_content_contract_v1" / "repo_only_framework_readme_content_contract_v1_latest.json"
CONTRACT_POST_JSON = LAB_ROOT / "edge_factory_os_repo_only_framework_readme_content_contract_post_commit_check" / "repo_only_framework_readme_content_contract_post_commit_check_latest.json"
QUEUE_JSON = LAB_ROOT / "edge_factory_os_repo_only_development_queue_selector_after_framework_skeleton_v1" / "repo_only_development_queue_selector_after_framework_skeleton_v1_latest.json"
PANEL_JSON = LAB_ROOT / "edge_factory_os_repo_only_governance_status_panel_after_framework_skeleton_v1" / "repo_only_governance_status_panel_after_framework_skeleton_v1_latest.json"

EXPECTED_README_PATHS = [
    "edge_factory_os_framework/README.md",
    "edge_factory_os_framework/contracts/README.md",
    "edge_factory_os_framework/core/README.md",
    "edge_factory_os_framework/manifests/README.md",
    "edge_factory_os_framework/plugins/README.md",
    "edge_factory_os_framework/policies/README.md",
    "edge_factory_os_framework/reports/README.md",
    "edge_factory_os_framework/schemas/README.md",
]

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_framework_readme_content_preview": True,
    "read_only_preview_only": True,
    "framework_readme_content_contract_required": True,
    "approval_required_before_apply": True,

    "repo_only_governance_allowed": True,
    "repo_only_audit_allowed": True,
    "read_only_validation_allowed": True,

    "preview_generation_allowed_now": True,
    "preview_generated_now": True,
    "apply_allowed_now": False,
    "approval_granted_now": False,

    "framework_readme_edit_allowed_now": False,
    "framework_readme_edit_performed_now": False,
    "framework_file_creation_allowed_now": False,
    "framework_directory_creation_allowed_now": False,
    "framework_file_creation_performed_now": False,
    "framework_directory_creation_performed_now": False,
    "file_move_allowed_now": False,
    "file_delete_allowed_now": False,
    "repo_restructure_allowed_now": False,
    "overwrite_existing_files_allowed": False,
    "modify_existing_files_allowed": False,
    "manual_review_allowed_now": False,
    "risk_file_edit_allowed_now": False,
    "risk_file_execution_allowed_now": False,
    "patch_allowed_now": False,
    "apply_performed_now": False,
    "commit_performed_now": False,
    "stage_performed_now": False,
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
    "mass_metadata_patch_allowed": False,
    "blind_fix_all_allowed": False,
}

FORBIDDEN_ACTIONS = [
    "edit_framework_readmes_now",
    "apply_content_now",
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
    "manual_risk_file_review_without_valid_approval",
    "risk_file_edit_without_approval",
    "risk_file_execution_without_approval",
    "overwrite_existing_files",
    "modify_existing_files",
    "move_files",
    "delete_files",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {args} returncode={result.returncode} stderr={result.stderr}")
    return result


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def get_git_state() -> Dict[str, Any]:
    status_lines = [
        x
        for x in run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"]).stdout.splitlines()
        if x.strip()
    ]
    untracked = [x[3:] for x in status_lines if x.startswith("?? ")]
    dirty_tracked = [x for x in status_lines if not x.startswith("?? ")]

    return {
        "head": run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
        "branch": run_cmd(["git", "branch", "--show-current"]).stdout.strip(),
        "status_porcelain": status_lines,
        "dirty_tracked_count": len(dirty_tracked),
        "dirty_tracked_paths": [x[3:] for x in dirty_tracked],
        "untracked_count": len(untracked),
        "untracked_paths": untracked,
        "git_dirty": bool(status_lines),
        "remote_status_short": run_cmd(["git", "status", "-sb", "--untracked-files=all"]).stdout.splitlines(),
    }


def tracked_python_files() -> List[str]:
    return sorted(x.strip().replace("\\", "/") for x in run_cmd(["git", "ls-files", "*.py"]).stdout.splitlines() if x.strip())


def validate_tracked_python() -> Dict[str, Any]:
    syntax_errors: List[Dict[str, str]] = []
    bom_errors: List[str] = []
    files = tracked_python_files()

    for rel in files:
        path = REPO_ROOT / rel
        try:
            data = path.read_bytes()
            if data.startswith(b"\xef\xbb\xbf"):
                bom_errors.append(rel)
            ast.parse(data.decode("utf-8"), filename=rel)
        except Exception as exc:
            syntax_errors.append({"path": rel, "error": repr(exc)})

    return {
        "tracked_python_file_count": len(files),
        "syntax_error_count": len(syntax_errors),
        "bom_error_count": len(bom_errors),
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
        "pass": not syntax_errors and not bom_errors,
    }


def commit_subject(ref: str) -> str:
    return run_cmd(["git", "log", "-1", "--pretty=%s", ref]).stdout.strip()


def commit_paths(ref: str) -> List[str]:
    lines = run_cmd(["git", "show", "--name-only", "--format=", ref]).stdout.splitlines()
    return sorted(x.strip().replace("\\", "/") for x in lines if x.strip())


def first_status(obj: Dict[str, Any]) -> Optional[str]:
    for key in [
        "framework_readme_content_contract_status",
        "audit_status",
        "development_queue_selector_after_framework_skeleton_status",
        "governance_status_panel_after_framework_skeleton_status",
    ]:
        value = obj.get(key)
        if value:
            return str(value)
    return None


def source_record(path: Path, obj: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "path": str(path),
        "status": first_status(obj),
        "critical_issue_count": obj.get("critical_issue_count"),
        "warning_count": obj.get("warning_count"),
        "next_module": obj.get("next_module"),
        "final_decision": obj.get("final_decision"),
    }


def validate_count_zero(errors: List[str], key: str, record: Dict[str, Any], field: str) -> None:
    value = record.get(field)
    if value is None:
        errors.append(f"{key} {field} field missing")
        return
    if value != 0:
        errors.append(f"{key} {field} not 0: {value}")


def validate_status_record(errors: List[str], key: str, record: Dict[str, Any], expected_status: str, expected_next_module: Optional[str] = None) -> None:
    status = record.get("status")
    if status is None:
        errors.append(f"{key} status field missing")
    elif status != expected_status:
        errors.append(f"{key} status mismatch: expected={expected_status} actual={status}")

    validate_count_zero(errors, key, record, "critical_issue_count")
    validate_count_zero(errors, key, record, "warning_count")

    if expected_next_module is not None and record.get("next_module") != expected_next_module:
        errors.append(f"{key} next_module mismatch: expected={expected_next_module} actual={record.get('next_module')}")


def validate_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    loaded: Dict[str, Dict[str, Any]] = {}
    source_statuses: Dict[str, Dict[str, Any]] = {}
    checks: Dict[str, Any] = {}

    git_state = get_git_state()

    if not git_state["head"].startswith(EXPECTED_HEAD_PREFIX):
        errors.append(f"unexpected HEAD: {git_state['head']} expected {EXPECTED_HEAD_PREFIX}")

    expected_untracked = {CURRENT_TOOL_REL}
    actual_untracked = set(git_state["untracked_paths"])

    if git_state["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked paths present before README content preview: {git_state['dirty_tracked_paths']}")

    if actual_untracked != expected_untracked:
        errors.append(f"unexpected untracked set before README content preview: expected={sorted(expected_untracked)} actual={sorted(actual_untracked)}")

    subject = commit_subject("HEAD")
    checks["head_commit_subject"] = subject
    if subject != "Add repo-only framework README content contract":
        errors.append(f"unexpected HEAD commit subject: {subject}")

    paths = commit_paths("HEAD")
    checks["head_commit_paths"] = paths
    if paths != ["tools/edge_factory_os_repo_only_framework_readme_content_contract_v1.py"]:
        errors.append(f"unexpected HEAD commit paths: {paths}")

    inputs = {
        "framework_readme_content_contract": (
            CONTRACT_JSON,
            "REPO_ONLY_FRAMEWORK_README_CONTENT_CONTRACT_V1_READY",
            "edge_factory_os_repo_only_framework_readme_content_preview_v1.py",
        ),
        "framework_readme_content_contract_post_check": (
            CONTRACT_POST_JSON,
            "REPO_ONLY_FRAMEWORK_README_CONTENT_CONTRACT_POST_COMMIT_CHECK_PASS",
            "edge_factory_os_repo_only_framework_readme_content_preview_v1.py",
        ),
        "development_queue_selector_after_framework_skeleton": (
            QUEUE_JSON,
            "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_FRAMEWORK_SKELETON_V1_READY",
            None,
        ),
        "governance_status_panel_after_framework_skeleton": (
            PANEL_JSON,
            "REPO_ONLY_GOVERNANCE_STATUS_PANEL_AFTER_FRAMEWORK_SKELETON_V1_READY",
            None,
        ),
    }

    for key, spec in inputs.items():
        path, expected_status, expected_next_module = spec
        obj: Optional[Dict[str, Any]] = None
        record: Optional[Dict[str, Any]] = None

        try:
            obj = load_json(path)
            loaded[key] = obj
            record = source_record(path, obj)
        except Exception as exc:
            errors.append(f"cannot load {key}: {path} error={repr(exc)}")

        if record is not None:
            source_statuses[key] = record
            checks[key] = record
            validate_status_record(errors, key, record, expected_status, expected_next_module)

    py = validate_tracked_python()
    checks["tracked_python"] = {
        "tracked_python_file_count": py["tracked_python_file_count"],
        "syntax_error_count": py["syntax_error_count"],
        "bom_error_count": py["bom_error_count"],
    }

    if not py["pass"]:
        errors.append(f"tracked Python validation failed: syntax={py['syntax_errors'][:20]} bom={py['bom_errors']}")

    return {
        "pass": not errors,
        "errors": errors,
        "loaded": loaded,
        "source_statuses": source_statuses,
        "checks": checks,
        "git_state": git_state,
        "tracked_python_validation": py,
        "expected_untracked_during_run": sorted(expected_untracked),
        "actual_untracked_during_run": sorted(actual_untracked),
        "clean_baseline": not errors,
    }


def proposed_content_for(plan: Dict[str, Any]) -> str:
    title = str(plan["planned_title"])
    purpose = str(plan["planned_purpose"])
    sections = [str(x) for x in plan["planned_required_sections"]]

    lines = [
        f"# {title}",
        "",
        purpose,
        "",
        "## Scope",
        "",
        "This README is part of the Edge Factory OS repo-only framework documentation layer.",
        "It is documentation/governance material only and does not authorize runtime execution, strategy research, candidate release, family release, capital changes, live trading, or real orders.",
        "",
    ]

    for section in sections:
        lines.extend(
            [
                f"## {section}",
                "",
                f"Planned content for `{section}` will describe the repo-only governance boundary, required inputs, allowed outputs, and fail-closed safety behavior for this framework area.",
                "",
            ]
        )

    lines.extend(
        [
            "## Safety Boundary",
            "",
            "- No runtime touch.",
            "- No launcher execution.",
            "- No capital change.",
            "- No active-paper/live/real-order action.",
            "- No strategy research, candidate generation, candidate release, or family release.",
            "- No holdout access.",
            "- No file move/delete/restructure/gitignore/backup cleanup action without a separate approved chain.",
            "",
        ]
    )

    return "\n".join(lines)


def build_preview(validation: Dict[str, Any]) -> Dict[str, Any]:
    contract_obj = validation["loaded"]["framework_readme_content_contract"]
    contract = contract_obj.get("framework_readme_content_contract", {})
    policy = contract.get("contract_policy", {})
    readme_plan = contract.get("readme_content_plan", [])

    panel_obj = validation["loaded"]["governance_status_panel_after_framework_skeleton"]
    panel = panel_obj.get("governance_status_panel_after_framework_skeleton", {})
    hard_blocks = panel.get("hard_blocks", {})

    errors: List[str] = []
    rows: List[Dict[str, Any]] = []

    if not isinstance(readme_plan, list):
        errors.append("contract readme_content_plan is not a list")
        readme_plan = []

    hard_blocks_ok = bool(hard_blocks) and all(value is False for value in hard_blocks.values())

    for item in readme_plan:
        if not isinstance(item, dict):
            errors.append(f"invalid readme plan item: {item!r}")
            continue

        rel = item.get("path")
        if rel not in EXPECTED_README_PATHS:
            errors.append(f"unexpected readme path in contract plan: {rel}")
            continue

        path = REPO_ROOT / str(rel)
        if not path.exists():
            errors.append(f"README missing: {rel}")
            continue

        current_text = path.read_text(encoding="utf-8")
        proposed_text = proposed_content_for(item)

        diff_lines = list(
            difflib.unified_diff(
                current_text.splitlines(),
                proposed_text.splitlines(),
                fromfile=f"a/{rel}",
                tofile=f"b/{rel}",
                lineterm="",
            )
        )

        preview_file = OUT_DIR / (str(rel).replace("/", "__") + ".proposed.md")
        diff_file = OUT_DIR / (str(rel).replace("/", "__") + ".diff.txt")
        preview_file.write_text(proposed_text, encoding="utf-8")
        diff_file.write_text("\n".join(diff_lines) + "\n", encoding="utf-8")

        rows.append(
            {
                "path": rel,
                "current_sha256": sha256_file(path),
                "proposed_sha256": sha256_bytes(proposed_text.encode("utf-8")),
                "current_line_count": len(current_text.splitlines()),
                "proposed_line_count": len(proposed_text.splitlines()),
                "diff_line_count": len(diff_lines),
                "preview_file": str(preview_file),
                "diff_file": str(diff_file),
                "edit_allowed_now": False,
                "apply_allowed_now": False,
                "preview_only": True,
            }
        )

    planned_paths = sorted(row["path"] for row in rows)
    expected_paths = sorted(EXPECTED_README_PATHS)

    prerequisites = {
        "contract_ready": contract_obj.get("framework_readme_content_contract_status") == "REPO_ONLY_FRAMEWORK_README_CONTENT_CONTRACT_V1_READY",
        "contract_only_policy": policy.get("contract_only") is True,
        "contract_apply_disallowed": policy.get("apply_allowed_now") is False,
        "contract_readme_edit_disallowed": policy.get("readme_edit_allowed_now") is False,
        "hard_blocks_all_false": hard_blocks_ok,
        "preview_path_set_is_expected_8": planned_paths == expected_paths,
    }

    return {
        "preview_status": "FRAMEWORK_README_CONTENT_PREVIEW_ACTIVE" if all(prerequisites.values()) and not errors else "FRAMEWORK_README_CONTENT_PREVIEW_BLOCKED",
        "preview_scope": "REPO_ONLY_DOCUMENTATION_PREVIEW",
        "preview_policy": {
            "preview_only": True,
            "apply_allowed_now": False,
            "readme_edit_allowed_now": False,
            "approval_required_before_apply": True,
            "no_repo_file_modification_now": True,
            "preview_outputs_outside_repo": True,
            "no_runtime_strategy_or_capital_work": True,
        },
        "preview_rows": rows,
        "previewed_readme_count": len(rows),
        "prerequisites": prerequisites,
        "errors": errors,
        "recommended_next_step": {
            "step": "BUILD_REPO_ONLY_FRAMEWORK_README_CONTENT_APPROVAL_GATE_V1",
            "module": "edge_factory_os_repo_only_framework_readme_content_approval_gate_v1.py",
            "scope": "REPO_ONLY_DOCUMENTATION_APPROVAL_GATE",
            "reason": "Preview is ready; next step is an approval gate, not apply.",
        },
        "invariants": {
            "previewed_readme_count_is_8": len(rows) == 8,
            "preview_paths_match_expected": planned_paths == expected_paths,
            "all_rows_preview_only": all(row["preview_only"] is True for row in rows),
            "all_rows_apply_disallowed": all(row["apply_allowed_now"] is False for row in rows),
            "all_rows_edit_disallowed": all(row["edit_allowed_now"] is False for row in rows),
            "prerequisites_all_true": all(prerequisites.values()),
            "hard_blocks_remain_false": hard_blocks_ok is True,
            "approval_required_before_apply": True,
            "no_framework_readme_edit_authorized_now": True,
            "no_runtime_strategy_or_capital_authorized": True,
            "no_repo_file_creation_or_modification_performed_by_preview": True,
        },
    }


def main() -> int:
    safety_errors = [key for key, value in SAFETY_FLAGS.items() if not isinstance(value, bool)]

    validation = validate_inputs()
    errors = list(validation["errors"])

    if safety_errors:
        errors.append(f"safety flags are not boolean: {safety_errors}")

    preview = build_preview(validation)
    errors.extend(preview["errors"])

    for key, value in preview["invariants"].items():
        if value is not True:
            errors.append(f"invariant {key} not true: {value}")

    passed = not errors

    payload = {
        "module": MODULE_NAME,
        "framework_readme_content_preview_status": "REPO_ONLY_FRAMEWORK_README_CONTENT_PREVIEW_V1_READY" if passed else "REPO_ONLY_FRAMEWORK_README_CONTENT_PREVIEW_V1_BLOCKED",
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_DOCUMENTATION_PREVIEW",
        "final_decision": "FRAMEWORK_README_CONTENT_PREVIEW_READY_FOR_APPROVAL_GATE" if passed else "KEEP_FREEZE_REVIEW_FRAMEWORK_README_CONTENT_PREVIEW_ERRORS",
        "next_action": "BUILD_REPO_ONLY_FRAMEWORK_README_CONTENT_APPROVAL_GATE_V1" if passed else "REVIEW_FRAMEWORK_README_CONTENT_PREVIEW_ERRORS",
        "next_module": "edge_factory_os_repo_only_framework_readme_content_approval_gate_v1.py" if passed else None,
        "reason": "Built preview-only framework README content outputs outside repo; no README edits performed." if passed else "Framework README content preview validation failed.",
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "critical_issue_count": len(errors),
        "warning_count": 0,
        "errors": errors,
        "warnings": [],
        "validation": {
            "checks": validation["checks"],
            "git_state": validation["git_state"],
            "tracked_python_validation": validation["tracked_python_validation"],
            "source_statuses": validation["source_statuses"],
            "expected_untracked_during_run": validation["expected_untracked_during_run"],
            "actual_untracked_during_run": validation["actual_untracked_during_run"],
            "clean_baseline": validation["clean_baseline"],
        },
        "framework_readme_content_preview": preview,
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "apply_performed_now": False,
        "stage_recommended_now": False,
        "commit_recommended_now": False,
        "runtime_action_recommended_now": False,
        "capital_action_recommended_now": False,
        "holdout_action_recommended_now": False,
        "strategy_research_recommended_now": False,
        "candidate_generation_recommended_now": False,
        "candidate_release_recommended_now": False,
        "family_release_recommended_now": False,
        "framework_file_creation_performed_now": False,
        "framework_directory_creation_performed_now": False,
        "framework_readme_edit_performed_now": False,
        "manual_review_allowed_now": False,
        "risk_file_edit_allowed_now": False,
        "risk_file_execution_allowed_now": False,
        "runtime_touched": False,
        "launcher_executed": False,
        "capital_changed": False,
        "live_or_real_orders": False,
        "holdout_accessed": False,
        "backup_deleted": False,
        "gitignore_changed": False,
        "git_add_force_used": False,
    }

    latest_json = OUT_DIR / "repo_only_framework_readme_content_preview_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_framework_readme_content_preview_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "repo_only_framework_readme_content_preview_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY FRAMEWORK README CONTENT PREVIEW v1",
        "=" * 100,
        f"framework_readme_content_preview_status: {payload['framework_readme_content_preview_status']}",
        f"severity: {payload['severity']}",
        f"final_decision: {payload['final_decision']}",
        f"next_action: {payload['next_action']}",
        f"next_module: {payload['next_module']}",
        f"reason: {payload['reason']}",
        f"critical_issue_count: {payload['critical_issue_count']}",
        f"warning_count: {payload['warning_count']}",
        "",
        "ERRORS",
        "-" * 100,
        json.dumps(errors, indent=2, sort_keys=True),
        "",
        "PREVIEW SUMMARY",
        "-" * 100,
        json.dumps(
            {
                "previewed_readme_count": preview["previewed_readme_count"],
                "preview_policy": preview["preview_policy"],
                "prerequisites": preview["prerequisites"],
                "invariants": preview["invariants"],
                "recommended_next_step": preview["recommended_next_step"],
                "preview_rows": preview["preview_rows"],
            },
            indent=2,
            sort_keys=True,
        ),
        "",
        "SAFETY",
        "-" * 100,
        json.dumps(SAFETY_FLAGS, indent=2, sort_keys=True),
        "",
        "OUTPUTS",
        "-" * 100,
        f"latest_json: {latest_json}",
        f"timestamped_json: {timestamped_json}",
        f"latest_txt: {latest_txt}",
    ]

    latest_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())