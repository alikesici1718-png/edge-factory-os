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

MODULE_NAME = "edge_factory_os_repo_only_generic_governance_runner_manual_approval_evaluator_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_generic_governance_runner_manual_approval_evaluator_v1.py"
EXPECTED_HEAD = "0e1c37e"
OUT_DIR = LAB_ROOT / MODULE_NAME

MANUAL_APPROVAL_RECORD_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_generic_governance_runner_manual_approval_record_v1"
    / "repo_only_generic_governance_runner_manual_approval_record_v1_latest.json"
)
MANUAL_APPROVAL_RECORD_POST_CHECK_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_generic_governance_runner_manual_approval_record_v1_post_commit_check"
    / "repo_only_generic_governance_runner_manual_approval_record_post_commit_check_latest.json"
)
REQUIRED_RECORD_STATUS = "REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_MANUAL_APPROVAL_RECORD_V1_READY"
REQUIRED_RECORD_POST_CHECK_STATUS = "REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_MANUAL_APPROVAL_RECORD_POST_COMMIT_CHECK_PASS"
REQUIRED_RECORD_NEXT_MODULE = "edge_factory_os_repo_only_generic_governance_runner_manual_approval_evaluator_v1.py"

NEXT_ACTION = "BUILD_REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_BLOCKED_STATUS_RECORD_V1"
NEXT_MODULE = "edge_factory_os_repo_only_generic_governance_runner_blocked_status_record_v1.py"
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
]

EXTRA_FALSE_FLAGS = [
    "manual_approval_present_now",
    "manual_approval_valid_now",
    "implementation_allowed_now",
    "generic_runner_implementation_allowed_now",
    "generic_runner_file_creation_allowed_now",
    "config_file_creation_allowed_now",
    "consolidation_apply_allowed_now",
]

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_generic_governance_runner_manual_approval_evaluator_only": True,
    "repo_only_blocked_status_record_recommended_next": True,
    "manual_approval_absence_evaluation_only": True,
    "read_only_manual_approval_record_validation_allowed": True,
    "implementation_blocked_status_recommended_next": True,
}
SAFETY_FLAGS.update({name: False for name in DANGEROUS_FLAGS + EXTRA_FALSE_FLAGS})


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {args} returncode={result.returncode} stderr={result.stderr}")
    return result


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def first_status(obj: Dict[str, Any]) -> Optional[str]:
    if isinstance(obj.get("manual_approval_evaluator_status"), str):
        return obj["manual_approval_evaluator_status"]
    if isinstance(obj.get("manual_approval_record_status"), str):
        return obj["manual_approval_record_status"]
    if isinstance(obj.get("audit_status"), str):
        return obj["audit_status"]
    if isinstance(obj.get("status"), str):
        return obj["status"]
    for key, value in obj.items():
        if key.endswith("_status") and isinstance(value, str):
            return value
    return None


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def generic_runner_target_exists() -> bool:
    return (REPO_ROOT / IMPLEMENTATION_TARGET_FILE).exists()


def physical_guard_snapshot() -> Dict[str, Any]:
    existing = planned_schema_existing_files()
    return {
        "planned_schema_rel_paths": PLANNED_SCHEMA_REL_PATHS,
        "planned_schema_path_count": len(PLANNED_SCHEMA_REL_PATHS),
        "existing_planned_schema_files": existing,
        "planned_schema_file_existing_count": len(existing),
        "generic_runner_target_file": IMPLEMENTATION_TARGET_FILE,
        "generic_runner_target_file_exists_now": generic_runner_target_exists(),
        "generic_runner_file_creation_performed": False,
        "config_file_creation_performed": False,
        "schema_apply_performed_count": 0,
        "schema_file_creation_performed_count": 0,
        "schema_file_edit_performed_count": 0,
        "runtime_touch_performed": False,
        "launcher_executed": False,
        "capital_change_performed": False,
        "live_or_real_order_performed": False,
        "holdout_access_performed": False,
        "file_move_performed": False,
        "file_delete_performed": False,
        "repo_restructure_performed": False,
    }


def get_git_state() -> Dict[str, Any]:
    status_lines = [
        line
        for line in run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"]).stdout.splitlines()
        if line.strip()
    ]
    untracked = [line[3:].replace("\\", "/") for line in status_lines if line.startswith("?? ")]
    dirty_tracked = [line for line in status_lines if not line.startswith("?? ")]
    staged = [line for line in dirty_tracked if line[0] != " "]
    return {
        "head": run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
        "branch": run_cmd(["git", "branch", "--show-current"]).stdout.strip(),
        "status_porcelain": status_lines,
        "dirty_tracked_count": len(dirty_tracked),
        "dirty_tracked_paths": [line[3:].replace("\\", "/") for line in dirty_tracked],
        "staged_count": len(staged),
        "staged_paths": [line[3:].replace("\\", "/") for line in staged],
        "untracked_count": len(untracked),
        "untracked_paths": sorted(untracked),
        "git_dirty": bool(status_lines),
    }


def tracked_python_files() -> List[str]:
    return sorted(
        line.strip().replace("\\", "/")
        for line in run_cmd(["git", "ls-files", "*.py"]).stdout.splitlines()
        if line.strip()
    )


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


def record_object(payload: Dict[str, Any]) -> Dict[str, Any]:
    record = payload.get("generic_governance_runner_manual_approval_record", {})
    return record if isinstance(record, dict) else {}


def validate_record(record: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if record.get("manual_approval_record_status") != REQUIRED_RECORD_STATUS:
        errors.append(f"manual approval record status mismatch: {record.get('manual_approval_record_status')}")
    if record.get("implementation_target_file") != IMPLEMENTATION_TARGET_FILE:
        errors.append(f"implementation target mismatch: {record.get('implementation_target_file')}")
    for field in [
        "manual_approval_present",
        "manual_approval_valid",
        "manual_approval_present_now",
        "manual_approval_valid_now",
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
        if record.get(field) is not False:
            errors.append(f"record field not false: {field}={record.get(field)}")

    absence_basis = " ".join(str(item).lower() for item in record.get("approval_absence_basis", []))
    for phrase in [
        "no explicit manual approval evidence",
        "cannot be inferred",
        "cannot be guessed",
        "implementation remains blocked",
    ]:
        if phrase not in absence_basis:
            errors.append(f"approval absence basis missing phrase: {phrase}")

    blocked_text = " ".join(str(item).lower() for item in record.get("blocked_actions", []))
    for phrase in ["infer manual approval", "guess manual approval validity", "treat this absence record as approval"]:
        if phrase not in blocked_text:
            errors.append(f"record does not block approval inference phrase: {phrase}")

    physical = record.get("physical_guards", {})
    if not isinstance(physical, dict):
        errors.append("record physical guards missing")
    else:
        for key, expected in {
            "planned_schema_file_existing_count": 0,
            "generic_runner_target_file_exists_now": False,
            "generic_runner_file_creation_performed": False,
            "config_file_creation_performed": False,
            "runtime_touch_performed": False,
            "launcher_executed": False,
            "capital_change_performed": False,
            "live_or_real_order_performed": False,
            "holdout_access_performed": False,
            "file_move_performed": False,
            "file_delete_performed": False,
            "repo_restructure_performed": False,
        }.items():
            if physical.get(key) != expected:
                errors.append(f"record physical guard mismatch: {key}={physical.get(key)}")

    required_flags = record.get("safety_flags_required_false", {})
    if not isinstance(required_flags, dict):
        errors.append("record required safety flags missing")
    else:
        for flag in DANGEROUS_FLAGS + EXTRA_FALSE_FLAGS:
            if required_flags.get(flag) is not False:
                errors.append(f"record required flag not false: {flag}={required_flags.get(flag)}")
    return errors


def validate_source_inputs(errors: List[str]) -> Dict[str, Any]:
    loaded: Dict[str, Any] = {}
    for key, path in {
        "generic_governance_runner_manual_approval_record": MANUAL_APPROVAL_RECORD_JSON,
        "generic_governance_runner_manual_approval_record_post_check": MANUAL_APPROVAL_RECORD_POST_CHECK_JSON,
    }.items():
        if not path.exists():
            errors.append(f"missing required manual approval record evidence: {path}")
            continue
        try:
            loaded[key] = load_json(path)
        except Exception as exc:
            errors.append(f"unreadable manual approval record evidence {path}: {exc!r}")

    record_payload = loaded.get("generic_governance_runner_manual_approval_record", {})
    post = loaded.get("generic_governance_runner_manual_approval_record_post_check", {})
    if record_payload:
        if record_payload.get("manual_approval_record_status") != REQUIRED_RECORD_STATUS:
            errors.append(f"manual approval record payload status mismatch: {record_payload.get('manual_approval_record_status')}")
        if record_payload.get("next_module") != REQUIRED_RECORD_NEXT_MODULE:
            errors.append(f"manual approval record next_module mismatch: {record_payload.get('next_module')}")
        if record_payload.get("critical_issue_count") != 0:
            errors.append(f"manual approval record critical_issue_count not zero: {record_payload.get('critical_issue_count')}")
        for field in [
            "manual_approval_present",
            "manual_approval_valid",
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
            if record_payload.get(field) is not False:
                errors.append(f"manual approval record top-level field not false: {field}={record_payload.get(field)}")
        record = record_object(record_payload)
        if not record:
            errors.append("manual approval record payload missing record object")
        else:
            errors.extend(validate_record(record))
    if post:
        if post.get("audit_status") != REQUIRED_RECORD_POST_CHECK_STATUS:
            errors.append(f"manual approval record post-check status mismatch: {post.get('audit_status')}")
        if post.get("latest_commit") != EXPECTED_HEAD:
            errors.append(f"manual approval record post-check latest_commit mismatch: expected={EXPECTED_HEAD} actual={post.get('latest_commit')}")
        if post.get("next_module") != REQUIRED_RECORD_NEXT_MODULE:
            errors.append(f"manual approval record post-check next_module mismatch: {post.get('next_module')}")
        if post.get("critical_issue_count") != 0:
            errors.append(f"manual approval record post-check critical_issue_count not zero: {post.get('critical_issue_count')}")
    return loaded


def validate_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    target_path = REPO_ROOT / CURRENT_TOOL_REL
    git_state = get_git_state()
    physical_before = physical_guard_snapshot()
    expected_untracked = [CURRENT_TOOL_REL] if target_path.exists() else []

    if git_state["head"] != EXPECTED_HEAD:
        errors.append(f"HEAD mismatch: expected={EXPECTED_HEAD} actual={git_state['head']}")
    if git_state["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked files present: {git_state['dirty_tracked_paths']}")
    if git_state["untracked_paths"] != expected_untracked:
        errors.append(f"unexpected untracked files: expected={expected_untracked} actual={git_state['untracked_paths']}")
    if physical_before["planned_schema_file_existing_count"] != 0:
        errors.append(f"planned schema files existed before run: {physical_before['existing_planned_schema_files']}")
    if physical_before["generic_runner_target_file_exists_now"] is not False:
        errors.append(f"generic runner target file already exists: {IMPLEMENTATION_TARGET_FILE}")

    tracked_python = validate_tracked_python()
    if not tracked_python["pass"]:
        errors.append(f"tracked Python validation failed: syntax={tracked_python['syntax_errors'][:20]} bom={tracked_python['bom_errors']}")
    if tracked_python["tracked_python_file_count"] != 533:
        errors.append(f"tracked Python count mismatch before new file is tracked: expected=533 actual={tracked_python['tracked_python_file_count']}")

    source_inputs = validate_source_inputs(errors)

    physical_after = physical_guard_snapshot()
    if physical_after["planned_schema_file_existing_count"] != 0:
        errors.append(f"planned schema files existed after run: {physical_after['existing_planned_schema_files']}")
    if physical_after["generic_runner_target_file_exists_now"] is not False:
        errors.append(f"generic runner target file exists after run: {IMPLEMENTATION_TARGET_FILE}")

    return {
        "errors": errors,
        "git_state": git_state,
        "expected_untracked_during_run": expected_untracked,
        "tracked_python_validation": tracked_python,
        "source_inputs": source_inputs,
        "physical_before": physical_before,
        "physical_after": physical_after,
    }


def source_record(validation: Dict[str, Any]) -> Dict[str, Any]:
    payload = validation["source_inputs"].get("generic_governance_runner_manual_approval_record", {})
    return record_object(payload)


def source_record_commit(validation: Dict[str, Any]) -> Optional[str]:
    post = validation["source_inputs"].get("generic_governance_runner_manual_approval_record_post_check", {})
    latest_commit = post.get("latest_commit")
    return latest_commit if isinstance(latest_commit, str) else None


def build_evaluation(validation: Dict[str, Any]) -> Dict[str, Any]:
    record = source_record(validation)
    record_errors = validate_record(record) if record else ["manual approval record object missing"]
    proofs = {
        "approval_is_absent": record.get("manual_approval_present") is False and record.get("manual_approval_present_now") is False,
        "approval_is_invalid": record.get("manual_approval_valid") is False and record.get("manual_approval_valid_now") is False,
        "approval_was_not_inferred": all(
            phrase in " ".join(str(item).lower() for item in record.get("approval_absence_basis", []))
            for phrase in ["cannot be inferred", "cannot be guessed"]
        ),
        "implementation_remains_blocked": record.get("implementation_allowed_now") is False
        and record.get("generic_runner_implementation_allowed_now") is False,
        "generic_runner_file_remains_absent": not generic_runner_target_exists()
        and record.get("generic_runner_file_creation_allowed_now") is False,
        "config_schema_apply_runtime_paths_remain_blocked": record.get("config_file_creation_allowed_now") is False
        and record.get("schema_creation_allowed_now") is False
        and record.get("schema_edit_allowed_now") is False
        and record.get("schema_apply_allowed_now") is False
        and record.get("consolidation_apply_allowed_now") is False
        and record.get("runtime_touch_allowed_now") is False,
    }
    return {
        "manual_approval_record_status": record.get("manual_approval_record_status"),
        "manual_approval_present": record.get("manual_approval_present"),
        "manual_approval_valid": record.get("manual_approval_valid"),
        "implementation_allowed_now": record.get("implementation_allowed_now"),
        "generic_runner_implementation_allowed_now": record.get("generic_runner_implementation_allowed_now"),
        "generic_runner_file_creation_allowed_now": record.get("generic_runner_file_creation_allowed_now"),
        "config_file_creation_allowed_now": record.get("config_file_creation_allowed_now"),
        "schema_creation_allowed_now": record.get("schema_creation_allowed_now"),
        "schema_edit_allowed_now": record.get("schema_edit_allowed_now"),
        "schema_apply_allowed_now": record.get("schema_apply_allowed_now"),
        "consolidation_apply_allowed_now": record.get("consolidation_apply_allowed_now"),
        "runtime_touch_allowed_now": record.get("runtime_touch_allowed_now"),
        "source_record_commit": source_record_commit(validation),
        "confirmed_proofs": proofs,
        "approval_absence_basis": record.get("approval_absence_basis"),
        "blocked_actions": record.get("blocked_actions"),
        "non_goals": record.get("non_goals"),
        "physical_guards": record.get("physical_guards"),
        "evaluation_errors": record_errors + ([] if all(proofs.values()) else [f"proof failed: {proofs}"]),
        "ready_for_blocked_status_record": not record_errors and all(proofs.values()),
        "recommended_next_action": NEXT_ACTION,
        "recommended_next_module": NEXT_MODULE,
        "decision_basis": [
            "manual approval is absent",
            "manual approval is invalid",
            "manual approval was not inferred or guessed",
            "implementation remains blocked",
            "generic runner target file remains absent",
            "config, schema, apply, consolidation, and runtime paths remain blocked",
        ],
    }


def build_payload(validation: Dict[str, Any]) -> Dict[str, Any]:
    errors = list(validation["errors"])
    safety_type_errors = [key for key, value in SAFETY_FLAGS.items() if not isinstance(value, bool)]
    if safety_type_errors:
        errors.append(f"safety flags are not boolean: {safety_type_errors}")
    for flag in DANGEROUS_FLAGS + EXTRA_FALSE_FLAGS:
        if SAFETY_FLAGS.get(flag) is not False:
            errors.append(f"safety flag is not explicitly false: {flag}={SAFETY_FLAGS.get(flag)}")

    evaluation = build_evaluation(validation)
    if not evaluation["ready_for_blocked_status_record"]:
        errors.append(f"manual approval evaluation did not pass: {evaluation['evaluation_errors']}")

    passed = not errors
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "manual_approval_evaluator_status": (
            "REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_MANUAL_APPROVAL_EVALUATOR_V1_READY"
            if passed
            else "BLOCKED"
        ),
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": (
            "MANUAL_APPROVAL_EVALUATED_ABSENT_KEEP_IMPLEMENTATION_BLOCKED"
            if passed
            else "BLOCKED_REVIEW_GENERIC_GOVERNANCE_RUNNER_MANUAL_APPROVAL_EVALUATOR_EVIDENCE"
        ),
        "next_action": NEXT_ACTION if passed else "REVIEW_GENERIC_GOVERNANCE_RUNNER_MANUAL_APPROVAL_EVALUATOR_ERRORS",
        "next_module": NEXT_MODULE if passed else None,
        "reason": (
            "Manual approval absence record is evaluated: approval remains absent and invalid, so implementation remains blocked."
            if passed
            else "Manual approval evaluator failed closed because required evidence or safety constraints were missing."
        ),
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "lab_root": str(LAB_ROOT),
        "critical_issue_count": len(errors),
        "warning_count": 0,
        "errors": errors,
        "warnings": [],
        "generic_governance_runner_manual_approval_evaluation": evaluation,
        "validation": {
            "git_state": validation["git_state"],
            "expected_untracked_during_run": validation["expected_untracked_during_run"],
            "tracked_python_validation": validation["tracked_python_validation"],
            "source_inputs": {
                key: {
                    "status": first_status(value),
                    "critical_issue_count": value.get("critical_issue_count"),
                    "next_module": value.get("next_module"),
                    "latest_commit": value.get("latest_commit"),
                    "final_decision": value.get("final_decision"),
                }
                for key, value in validation["source_inputs"].items()
            },
            "physical_before": validation["physical_before"],
            "physical_after": validation["physical_after"],
        },
        "physical_guards": {
            "before": validation["physical_before"],
            "after": validation["physical_after"],
        },
        "safety_flags": SAFETY_FLAGS,
        "stage_recommended_now": False,
        "commit_recommended_now": False,
    }
    for flag in DANGEROUS_FLAGS + EXTRA_FALSE_FLAGS:
        payload[flag] = False
    payload.update(
        {
            "manual_approval_present": False,
            "manual_approval_valid": False,
            "implementation_allowed_now": False,
            "generic_runner_implementation_allowed_now": False,
            "generic_runner_file_creation_allowed_now": False,
            "config_file_creation_allowed_now": False,
            "schema_creation_allowed_now": False,
            "schema_edit_allowed_now": False,
            "schema_apply_allowed_now": False,
            "consolidation_apply_allowed_now": False,
            "runtime_touch_allowed_now": False,
        }
    )
    return payload


def write_outputs(payload: Dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_generic_governance_runner_manual_approval_evaluator_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_generic_governance_runner_manual_approval_evaluator_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_generic_governance_runner_manual_approval_evaluator_v1_latest.txt"
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    latest_json.write_text(rendered, encoding="utf-8")
    timestamped_json.write_text(rendered, encoding="utf-8")
    latest_txt.write_text(rendered + "\n", encoding="utf-8")


def main() -> int:
    validation = validate_inputs()
    payload = build_payload(validation)
    write_outputs(payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["critical_issue_count"] == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
