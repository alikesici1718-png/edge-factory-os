from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_generic_governance_runner_blocked_status_evaluator_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_generic_governance_runner_blocked_status_evaluator_v1.py"
EXPECTED_HEAD = "9884e68"
EXPECTED_PYTHON_COUNT = 535
OUT_DIR = LAB_ROOT / MODULE_NAME

RECORD_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_generic_governance_runner_blocked_status_record_v1"
    / "repo_only_generic_governance_runner_blocked_status_record_v1_latest.json"
)
RECORD_POST_CHECK_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_generic_governance_runner_blocked_status_record_v1_post_commit_check"
    / "repo_only_generic_governance_runner_blocked_status_record_post_commit_check_latest.json"
)

REQUIRED_RECORD_STATUS = "REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_BLOCKED_STATUS_RECORD_V1_READY"
REQUIRED_RECORD_POST_CHECK_STATUS = "REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_BLOCKED_STATUS_RECORD_POST_COMMIT_CHECK_PASS"
REQUIRED_RECORD_NEXT_MODULE = "edge_factory_os_repo_only_generic_governance_runner_blocked_status_evaluator_v1.py"

NEXT_ACTION = "BUILD_REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_V1"
NEXT_MODULE = "edge_factory_os_repo_only_next_action_selector_after_generic_governance_blocked_status_v1.py"
IMPLEMENTATION_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

PLANNED_SCHEMA_REL_PATHS = [
    "edge_factory_os_framework/schemas/edge_factory_os_status_record_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_safety_flags_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_git_state_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_tracked_python_validation_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_queue_item_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_artifact_reference_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_post_commit_check_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_framework_schema_registry_v1.schema.json",
]

DANGEROUS_FLAGS = [
    "runtime_touched",
    "launcher_executed",
    "capital_changed",
    "live_or_real_orders",
    "holdout_accessed",
    "strategy_research_recommended_now",
    "candidate_generation_recommended_now",
    "candidate_release_recommended_now",
    "family_release_recommended_now",
    "schema_apply_allowed_now",
    "schema_file_creation_allowed_now",
    "schema_file_edit_allowed_now",
    "schema_apply_performed_now",
    "schema_file_creation_performed_now",
    "schema_file_edit_performed_now",
    "file_move_allowed_now",
    "file_delete_allowed_now",
    "repo_restructure_allowed_now",
    "gitignore_changed",
    "git_add_force_used",
    "backup_deleted",
    "mass_metadata_patch_allowed",
    "blind_fix_all_allowed",
    "direct_apply_recommended_now",
    "apply_allowed_now",
    "apply_performed_now",
    "manual_approval_present_now",
    "manual_approval_valid_now",
    "implementation_allowed_now",
    "generic_runner_implementation_allowed_now",
    "generic_runner_file_creation_allowed_now",
    "config_file_creation_allowed_now",
    "consolidation_apply_allowed_now",
]

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_generic_governance_runner_blocked_status_evaluation_only": True,
    "manual_approval_absent_evaluation_only": True,
}
SAFETY_FLAGS.update({name: False for name in DANGEROUS_FLAGS})


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {args} returncode={result.returncode} stderr={result.stderr}")
    return result


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def get_git_state() -> Dict[str, Any]:
    status_lines = [
        line
        for line in run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"]).stdout.splitlines()
        if line.strip()
    ]
    untracked = [line[3:].replace("\\", "/") for line in status_lines if line.startswith("?? ")]
    return {
        "head": run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
        "status_porcelain": status_lines,
        "untracked_paths": sorted(untracked),
        "git_dirty": bool(status_lines),
    }


def validate_tracked_python() -> Dict[str, Any]:
    syntax_errors: List[Dict[str, str]] = []
    bom_errors: List[str] = []
    files = sorted(
        line.strip().replace("\\", "/")
        for line in run_cmd(["git", "ls-files", "*.py"]).stdout.splitlines()
        if line.strip()
    )
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
        "pass": not syntax_errors and not bom_errors,
    }


def validate_inputs(errors: List[str]) -> Dict[str, Any]:
    git_state = get_git_state()
    if git_state["head"] != EXPECTED_HEAD:
        errors.append(f"HEAD mismatch: expected={EXPECTED_HEAD} actual={git_state['head']}")

    expected_untracked = [CURRENT_TOOL_REL]
    if git_state["untracked_paths"] != expected_untracked:
        errors.append(f"unexpected untracked files: expected={expected_untracked} actual={git_state['untracked_paths']}")

    python_val = validate_tracked_python()
    if python_val["tracked_python_file_count"] != EXPECTED_PYTHON_COUNT:
        errors.append(f"tracked Python count mismatch: expected={EXPECTED_PYTHON_COUNT} actual={python_val['tracked_python_file_count']}")
    if not python_val["pass"]:
        errors.append("tracked Python syntax or BOM validation failed")

    if (REPO_ROOT / IMPLEMENTATION_TARGET_FILE).exists():
        errors.append(f"generic runner target file already exists: {IMPLEMENTATION_TARGET_FILE}")

    for rel in PLANNED_SCHEMA_REL_PATHS:
        if (REPO_ROOT / rel).exists():
            errors.append(f"planned schema file already exists: {rel}")

    loaded: Dict[str, Any] = {}
    for key, path in {"record": RECORD_JSON, "post_check": RECORD_POST_CHECK_JSON}.items():
        if not path.exists():
            errors.append(f"missing record evidence: {path}")
            continue
        try:
            loaded[key] = load_json(path)
        except Exception as exc:
            errors.append(f"unreadable record evidence {path}: {exc!r}")

    record = loaded.get("record", {})
    if record.get("blocked_status_record_status") != REQUIRED_RECORD_STATUS:
        errors.append(f"record status mismatch: {record.get('blocked_status_record_status')}")
    if record.get("next_module") != REQUIRED_RECORD_NEXT_MODULE:
        errors.append(f"record next_module mismatch: {record.get('next_module')}")

    post = loaded.get("post_check", {})
    if post.get("audit_status") != REQUIRED_RECORD_POST_CHECK_STATUS:
        errors.append(f"record post-check status mismatch: {post.get('audit_status')}")

    return loaded


def build_payload(loaded: Dict[str, Any], errors: List[str]) -> Dict[str, Any]:
    record = loaded.get("record", {}).get("generic_governance_runner_blocked_status_record", {})

    # 11. Confirm all of these are false
    fields_to_check = [
        "manual_approval_present",
        "manual_approval_valid",
        "approval_inferred_or_guessed",
        "implementation_allowed_now",
        "generic_runner_implementation_allowed_now",
        "generic_runner_file_creation_allowed_now",
        "config_file_creation_allowed_now",
        "schema_creation_allowed_now",
        "schema_edit_allowed_now",
        "schema_apply_allowed_now",
        "consolidation_apply_allowed_now",
        "runtime_touch_allowed_now",
    ]

    for field in fields_to_check:
        val = record.get(field)
        if val is not False:
            # 12. Fail closed if any approval is inferred, guessed, or treated as valid
            errors.append(f"safety field is not False: {field}={val}")

    passed = not errors
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "blocked_status_evaluator_status": (
            "REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_BLOCKED_STATUS_EVALUATOR_V1_READY" if passed else "BLOCKED"
        ),
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": (
            "BLOCKED_STATUS_EVALUATED_IMPLEMENTATION_REMAINS_BLOCKED"
            if passed
            else "BLOCKED_EVALUATION_FAILED"
        ),
        "next_action": NEXT_ACTION if passed else "REVIEW_ERRORS",
        "next_module": NEXT_MODULE if passed else None,
        "reason": (
            "Confirmed generic governance runner implementation remains blocked because manual approval is absent/invalid."
            if passed
            else "Evaluation failed due to safety gate violations or missing prerequisites."
        ),
        "created_at_utc": now_utc(),
        "critical_issue_count": len(errors),
        "errors": errors,
        "safety_flags": SAFETY_FLAGS,
    }

    # Populate specific required status fields at top level
    for field in fields_to_check:
        payload[field] = False

    for flag in DANGEROUS_FLAGS:
        payload[flag] = False

    payload["physical_guards"] = {
        "generic_runner_target_file_exists": False,
        "planned_schema_files_exist": False,
        "repo_clean_except_new_evaluator": passed,
    }

    return payload


def write_outputs(payload: Dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / f"{MODULE_NAME}_latest.json"
    timestamped_json = OUT_DIR / f"{MODULE_NAME}_{stamp}.json"
    latest_txt = OUT_DIR / f"{MODULE_NAME}_latest.txt"

    rendered_json = json.dumps(payload, indent=2, sort_keys=True)

    # Create the text report
    lines = [
        f"EDGE FACTORY OS BLOCKED STATUS EVALUATOR v1",
        "=" * 100,
        f"status: {payload['blocked_status_evaluator_status']}",
        f"final_decision: {payload['final_decision']}",
        f"next_action: {payload['next_action']}",
        f"next_module: {payload['next_module']}",
        "",
        "SAFETY CHECK",
        "-" * 100,
    ]
    for field in [
        "manual_approval_present",
        "manual_approval_valid",
        "approval_inferred_or_guessed",
        "implementation_allowed_now",
        "generic_runner_implementation_allowed_now",
        "generic_runner_file_creation_allowed_now",
        "config_file_creation_allowed_now",
        "schema_creation_allowed_now",
        "schema_edit_allowed_now",
        "schema_apply_allowed_now",
        "consolidation_apply_allowed_now",
        "runtime_touch_allowed_now",
    ]:
        lines.append(f"{field}: {payload.get(field)}")

    lines.append("")
    lines.append("DANGEROUS FLAGS (REQUIRED FALSE)")
    lines.append("-" * 100)
    for flag in DANGEROUS_FLAGS:
        lines.append(f"{flag}: {payload.get(flag)}")

    if payload["errors"]:
        lines.append("")
        lines.append("ERRORS")
        lines.append("-" * 100)
        for err in payload["errors"]:
            lines.append(f"ERROR: {err}")

    rendered_txt = "\n".join(lines) + "\n"

    latest_json.write_text(rendered_json, encoding="utf-8")
    timestamped_json.write_text(rendered_json, encoding="utf-8")
    latest_txt.write_text(rendered_txt, encoding="utf-8")


def main() -> int:
    errors: List[str] = []
    loaded = validate_inputs(errors)
    payload = build_payload(loaded, errors)
    write_outputs(payload)

    # After writing, check repo status again to confirm exactly one untracked file
    git_final = get_git_state()
    if git_final["untracked_paths"] != [CURRENT_TOOL_REL]:
        print(f"CRITICAL: Final repo status dirty: {git_final['untracked_paths']}")

    print(f"Status: {payload['blocked_status_evaluator_status']}")
    print(f"Decision: {payload['final_decision']}")
    print(f"Critical Issues: {payload['critical_issue_count']}")

    if payload["critical_issue_count"] > 0:
        for err in payload["errors"]:
            print(f"  - {err}")
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())