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

MODULE_NAME = "edge_factory_os_repo_only_next_action_selector_after_generic_governance_blocked_status_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_next_action_selector_after_generic_governance_blocked_status_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "db309da"
EXPECTED_TRACKED_PYTHON_COUNT = 536

BLOCKED_STATUS_EVALUATOR_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_generic_governance_runner_blocked_status_evaluator_v1"
    / "edge_factory_os_repo_only_generic_governance_runner_blocked_status_evaluator_v1_latest.json"
)
BLOCKED_STATUS_EVALUATOR_POST_CHECK_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_generic_governance_runner_blocked_status_evaluator_v1_post_commit_check"
    / "repo_only_generic_governance_runner_blocked_status_evaluator_post_commit_check_latest.json"
)

REQUIRED_EVALUATOR_STATUS = "REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_BLOCKED_STATUS_EVALUATOR_V1_READY"
REQUIRED_EVALUATOR_POST_CHECK_STATUS = "REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_BLOCKED_STATUS_EVALUATOR_POST_COMMIT_CHECK_PASS"
REQUIRED_EVALUATOR_NEXT_ACTION = "BUILD_REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_V1"
REQUIRED_EVALUATOR_NEXT_MODULE = "edge_factory_os_repo_only_next_action_selector_after_generic_governance_blocked_status_v1.py"

READY_STATUS = "REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_V1_READY"
FINAL_DECISION = "GENERIC_GOVERNANCE_BLOCKED_STATUS_EVALUATED_READY_FOR_REPO_ONLY_QUEUE_SELECTOR"
NEXT_ACTION = "BUILD_REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_V1"
NEXT_MODULE = "edge_factory_os_repo_only_development_queue_selector_after_generic_governance_blocked_status_v1.py"

GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

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
    "repo_only_next_action_selector_after_generic_governance_blocked_status": True,
    "next_action_selector_only": True,
    "read_only_blocked_status_evidence_validation_only": True,
    "development_queue_selector_after_generic_governance_blocked_status_allowed_next": True,
}
SAFETY_FLAGS.update({flag: False for flag in DANGEROUS_FLAGS})

SOURCE_FALSE_FIELDS = [
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
    "direct_apply_recommended_now",
    "apply_allowed_now",
    "apply_performed_now",
    "manual_approval_present_now",
    "manual_approval_valid_now",
]

PHYSICAL_FALSE_FIELDS = {
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
}


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


def commit_subject(ref: str) -> str:
    return run_cmd(["git", "log", "-1", "--pretty=%s", ref]).stdout.strip()


def commit_paths(ref: str) -> List[str]:
    lines = run_cmd(["git", "show", "--name-only", "--format=", ref]).stdout.splitlines()
    return sorted(line.strip().replace("\\", "/") for line in lines if line.strip())


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def generic_runner_target_exists() -> bool:
    return (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()


def physical_guard_snapshot() -> Dict[str, Any]:
    existing_schema_files = planned_schema_existing_files()
    snapshot: Dict[str, Any] = {
        "planned_schema_rel_paths": PLANNED_SCHEMA_REL_PATHS,
        "planned_schema_path_count": len(PLANNED_SCHEMA_REL_PATHS),
        "existing_planned_schema_files": existing_schema_files,
        "planned_schema_file_existing_count": len(existing_schema_files),
        "generic_runner_target_file": GENERIC_RUNNER_TARGET_FILE,
        "generic_runner_target_file_exists_now": generic_runner_target_exists(),
    }
    snapshot.update(PHYSICAL_FALSE_FIELDS)
    return snapshot


def first_status(obj: Dict[str, Any]) -> Optional[str]:
    for key in ["blocked_status_evaluator_status", "audit_status", "status"]:
        value = obj.get(key)
        if isinstance(value, str):
            return value
    return None


def source_record(path: Path, obj: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "path": str(path),
        "status": first_status(obj),
        "critical_issue_count": obj.get("critical_issue_count"),
        "warning_count": obj.get("warning_count"),
        "next_action": obj.get("next_action"),
        "next_module": obj.get("next_module"),
        "final_decision": obj.get("final_decision"),
        "latest_commit": obj.get("latest_commit"),
    }


def validate_source_false_fields(errors: List[str], evaluator: Dict[str, Any]) -> None:
    for field in SOURCE_FALSE_FIELDS:
        if evaluator.get(field) is not False:
            errors.append(f"blocked status evaluator field not false: {field}={evaluator.get(field)}")
    for flag in DANGEROUS_FLAGS:
        if evaluator.get(flag) is not False:
            errors.append(f"blocked status evaluator dangerous flag not false: {flag}={evaluator.get(flag)}")
        safety_flags = evaluator.get("safety_flags", {})
        if isinstance(safety_flags, dict) and safety_flags.get(flag) is not False:
            errors.append(f"blocked status evaluator safety flag not false: {flag}={safety_flags.get(flag)}")


def validate_source_physical_guards(errors: List[str], evaluator: Dict[str, Any], post_check: Dict[str, Any]) -> None:
    guards = evaluator.get("physical_guards", {})
    if not isinstance(guards, dict):
        errors.append("blocked status evaluator physical_guards missing")
        return
    if guards.get("generic_runner_target_file_exists") is not False:
        errors.append(f"blocked status evaluator generic runner guard not false: {guards.get('generic_runner_target_file_exists')}")
    if guards.get("planned_schema_files_exist") is not False:
        errors.append(f"blocked status evaluator planned schema guard not false: {guards.get('planned_schema_files_exist')}")

    counts = post_check.get("counts", {})
    if isinstance(counts, dict):
        if counts.get("planned_schema_file_existing_count") != 0:
            errors.append(f"post-check planned schema count not zero: {counts.get('planned_schema_file_existing_count')}")
        if counts.get("generic_runner_target_file_exists_count") != 0:
            errors.append(f"post-check generic runner target count not zero: {counts.get('generic_runner_target_file_exists_count')}")
    else:
        errors.append("blocked status evaluator post-check counts missing")
    if post_check.get("generic_runner_target_file_exists_now") is not False:
        errors.append(f"post-check generic runner target exists not false: {post_check.get('generic_runner_target_file_exists_now')}")
    if post_check.get("planned_schema_existing_files") != []:
        errors.append(f"post-check planned schema files not empty: {post_check.get('planned_schema_existing_files')}")


def validate_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    loaded: Dict[str, Dict[str, Any]] = {}
    source_statuses: Dict[str, Dict[str, Any]] = {}

    git_state = get_git_state()
    physical_before = physical_guard_snapshot()

    if git_state["head"] != EXPECTED_HEAD:
        errors.append(f"HEAD mismatch: expected={EXPECTED_HEAD} actual={git_state['head']}")
    if git_state["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked paths present before selector run: {git_state['dirty_tracked_paths']}")
    if git_state["untracked_paths"] != [CURRENT_TOOL_REL]:
        errors.append(f"unexpected untracked paths before selector run: expected={[CURRENT_TOOL_REL]} actual={git_state['untracked_paths']}")
    if physical_before["planned_schema_file_existing_count"] != 0:
        errors.append(f"planned schema files existed before selector run: {physical_before['existing_planned_schema_files']}")
    if physical_before["generic_runner_target_file_exists_now"] is not False:
        errors.append(f"generic runner target file existed before selector run: {GENERIC_RUNNER_TARGET_FILE}")

    tracked_python = validate_tracked_python()
    if tracked_python["tracked_python_file_count"] != EXPECTED_TRACKED_PYTHON_COUNT:
        errors.append(
            "tracked Python count mismatch before selector commit: "
            f"expected={EXPECTED_TRACKED_PYTHON_COUNT} actual={tracked_python['tracked_python_file_count']}"
        )
    if not tracked_python["pass"]:
        errors.append(f"tracked Python validation failed: syntax={tracked_python['syntax_errors'][:20]} bom={tracked_python['bom_errors']}")

    subject = commit_subject("HEAD")
    paths = commit_paths("HEAD")
    if subject != "Add repo-only generic governance runner blocked status evaluator":
        errors.append(f"unexpected HEAD commit subject: {subject}")
    if paths != ["tools/edge_factory_os_repo_only_generic_governance_runner_blocked_status_evaluator_v1.py"]:
        errors.append(f"unexpected HEAD commit paths: {paths}")

    inputs = {
        "blocked_status_evaluator": BLOCKED_STATUS_EVALUATOR_JSON,
        "blocked_status_evaluator_post_check": BLOCKED_STATUS_EVALUATOR_POST_CHECK_JSON,
    }
    for key, path in inputs.items():
        try:
            obj = load_json(path)
            loaded[key] = obj
            source_statuses[key] = source_record(path, obj)
        except Exception as exc:
            errors.append(f"cannot load {key}: {path} error={repr(exc)}")

    evaluator = loaded.get("blocked_status_evaluator", {})
    post_check = loaded.get("blocked_status_evaluator_post_check", {})
    if evaluator:
        if evaluator.get("blocked_status_evaluator_status") != REQUIRED_EVALUATOR_STATUS:
            errors.append(f"blocked status evaluator status mismatch: {evaluator.get('blocked_status_evaluator_status')}")
        if evaluator.get("critical_issue_count") != 0:
            errors.append(f"blocked status evaluator critical_issue_count not zero: {evaluator.get('critical_issue_count')}")
        if evaluator.get("next_action") != REQUIRED_EVALUATOR_NEXT_ACTION:
            errors.append(f"blocked status evaluator next_action mismatch: {evaluator.get('next_action')}")
        if evaluator.get("next_module") != REQUIRED_EVALUATOR_NEXT_MODULE:
            errors.append(f"blocked status evaluator next_module mismatch: {evaluator.get('next_module')}")
        if evaluator.get("final_decision") != "BLOCKED_STATUS_EVALUATED_IMPLEMENTATION_REMAINS_BLOCKED":
            errors.append(f"blocked status evaluator final_decision mismatch: {evaluator.get('final_decision')}")
        validate_source_false_fields(errors, evaluator)

    if post_check:
        if post_check.get("audit_status") != REQUIRED_EVALUATOR_POST_CHECK_STATUS:
            errors.append(f"blocked status evaluator post-check status mismatch: {post_check.get('audit_status')}")
        if post_check.get("critical_issue_count") != 0:
            errors.append(f"blocked status evaluator post-check critical_issue_count not zero: {post_check.get('critical_issue_count')}")
        if post_check.get("latest_commit") != EXPECTED_HEAD:
            errors.append(f"blocked status evaluator post-check latest_commit mismatch: {post_check.get('latest_commit')}")
        if post_check.get("next_module") != REQUIRED_EVALUATOR_NEXT_MODULE:
            errors.append(f"blocked status evaluator post-check next_module mismatch: {post_check.get('next_module')}")
        if post_check.get("next_action") != REQUIRED_EVALUATOR_NEXT_ACTION:
            errors.append(f"blocked status evaluator post-check next_action mismatch: {post_check.get('next_action')}")
        validate_source_physical_guards(errors, evaluator, post_check)

    physical_after = physical_guard_snapshot()
    if physical_after["planned_schema_file_existing_count"] != 0:
        errors.append(f"planned schema files existed after selector validation: {physical_after['existing_planned_schema_files']}")
    if physical_after["generic_runner_target_file_exists_now"] is not False:
        errors.append(f"generic runner target file existed after selector validation: {GENERIC_RUNNER_TARGET_FILE}")

    return {
        "pass": not errors,
        "errors": errors,
        "loaded": loaded,
        "source_statuses": source_statuses,
        "git_state": git_state,
        "tracked_python_validation": tracked_python,
        "head_commit_subject": subject,
        "head_commit_paths": paths,
        "expected_untracked_during_run": [CURRENT_TOOL_REL],
        "actual_untracked_during_run": git_state["untracked_paths"],
        "physical_before": physical_before,
        "physical_after": physical_after,
    }


def build_selector(validation: Dict[str, Any]) -> Dict[str, Any]:
    evaluator = validation["loaded"].get("blocked_status_evaluator", {})
    physical_before = validation["physical_before"]
    physical_after = validation["physical_after"]

    prerequisites = {
        "input_validation_pass": validation["pass"] is True,
        "blocked_status_evaluator_ready": evaluator.get("blocked_status_evaluator_status") == REQUIRED_EVALUATOR_STATUS,
        "blocked_status_evaluator_post_check_pass": validation["source_statuses"].get("blocked_status_evaluator_post_check", {}).get("status") == REQUIRED_EVALUATOR_POST_CHECK_STATUS,
        "blocked_status_evaluator_selected_this_module": evaluator.get("next_module") == REQUIRED_EVALUATOR_NEXT_MODULE,
        "implementation_remains_blocked": evaluator.get("implementation_allowed_now") is False and evaluator.get("generic_runner_implementation_allowed_now") is False,
        "manual_approval_remains_absent": evaluator.get("manual_approval_present") is False and evaluator.get("manual_approval_present_now") is False,
        "manual_approval_remains_invalid": evaluator.get("manual_approval_valid") is False and evaluator.get("manual_approval_valid_now") is False,
        "approval_not_inferred": evaluator.get("approval_inferred_or_guessed") is False,
        "generic_runner_target_file_absent_before": physical_before["generic_runner_target_file_exists_now"] is False,
        "generic_runner_target_file_absent_after": physical_after["generic_runner_target_file_exists_now"] is False,
        "generic_runner_file_creation_blocked": evaluator.get("generic_runner_file_creation_allowed_now") is False,
        "config_file_creation_blocked": evaluator.get("config_file_creation_allowed_now") is False,
        "schema_file_creation_blocked": evaluator.get("schema_file_creation_allowed_now") is False,
        "schema_file_edit_blocked": evaluator.get("schema_file_edit_allowed_now") is False,
        "schema_apply_blocked": evaluator.get("schema_apply_allowed_now") is False,
        "consolidation_apply_blocked": evaluator.get("consolidation_apply_allowed_now") is False,
        "runtime_touch_blocked": evaluator.get("runtime_touch_allowed_now") is False,
        "planned_schema_files_absent_before": physical_before["planned_schema_file_existing_count"] == 0,
        "planned_schema_files_absent_after": physical_after["planned_schema_file_existing_count"] == 0,
        "tracked_python_clean": validation["tracked_python_validation"]["pass"] is True,
    }

    candidate_actions = [
        {
            "rank": 1,
            "key": "DEVELOPMENT_QUEUE_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS",
            "module": NEXT_MODULE,
            "scope": "REPO_ONLY_OS_INTELLIGENCE",
            "allowed": True,
            "reason": "Blocked status is verified; select the next safe repo-only queue step without implementing the generic runner.",
            "blocked_actions": [
                "generic_runner_implementation",
                "generic_runner_file_creation",
                "config_file_creation",
                "schema_file_creation",
                "schema_file_edit",
                "schema_apply",
                "consolidation_apply",
                "runtime_touch",
                "launcher_execution",
                "capital_change",
                "live_or_real_orders",
                "strategy_research",
                "candidate_generation",
                "candidate_release",
                "family_release",
                "holdout_access",
                "file_move",
                "file_delete",
                "repo_restructure",
                "approval_inference",
            ],
        },
        {
            "rank": 2,
            "key": "GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION",
            "module": GENERIC_RUNNER_TARGET_FILE,
            "scope": "BLOCKED_MANUAL_APPROVAL_ABSENT_INVALID",
            "allowed": False,
            "reason": "Implementation remains blocked; manual approval is absent/invalid and must not be inferred.",
            "blocked_actions": ["generic_runner_implementation", "generic_runner_file_creation", "approval_inference"],
        },
        {
            "rank": 3,
            "key": "CONFIG_SCHEMA_APPLY_RUNTIME_PATH",
            "module": None,
            "scope": "BLOCKED",
            "allowed": False,
            "reason": "Config, schema, apply, consolidation, and runtime paths remain blocked.",
            "blocked_actions": ["config_file_creation", "schema_file_creation", "schema_file_edit", "schema_apply", "consolidation_apply", "runtime_touch"],
        },
    ]

    selected = candidate_actions[0] if all(prerequisites.values()) else None
    return {
        "selector_status": "NEXT_ACTION_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_ACTIVE" if selected else "NEXT_ACTION_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BLOCKED",
        "candidate_actions": candidate_actions,
        "candidate_action_count": len(candidate_actions),
        "selected_action": selected,
        "selected_next_module": selected["module"] if selected else None,
        "selected_next_action": NEXT_ACTION if selected else None,
        "selected_scope": selected["scope"] if selected else None,
        "prerequisites": prerequisites,
        "confirmed_proofs": {
            "implementation_remains_blocked": evaluator.get("implementation_allowed_now") is False and evaluator.get("generic_runner_implementation_allowed_now") is False,
            "manual_approval_remains_absent": evaluator.get("manual_approval_present") is False and evaluator.get("manual_approval_present_now") is False,
            "manual_approval_remains_invalid": evaluator.get("manual_approval_valid") is False and evaluator.get("manual_approval_valid_now") is False,
            "generic_runner_target_file_remains_absent": physical_before["generic_runner_target_file_exists_now"] is False and physical_after["generic_runner_target_file_exists_now"] is False,
            "config_schema_apply_runtime_paths_remain_blocked": all(
                evaluator.get(field) is False
                for field in [
                    "config_file_creation_allowed_now",
                    "schema_file_creation_allowed_now",
                    "schema_file_edit_allowed_now",
                    "schema_apply_allowed_now",
                    "consolidation_apply_allowed_now",
                    "runtime_touch_allowed_now",
                ]
            ),
        },
        "physical_guards": {
            "before": physical_before,
            "after": physical_after,
            "planned_schema_file_existing_count": 0,
            "generic_runner_target_file_exists_now": False,
            **PHYSICAL_FALSE_FIELDS,
        },
        "selector_policy": {
            "next_action_selector_only": True,
            "do_not_implement_generic_runner": True,
            "do_not_create_generic_runner_target_file": True,
            "do_not_create_config_files": True,
            "do_not_create_edit_or_apply_schema_files": True,
            "do_not_touch_runtime_or_launcher": True,
            "do_not_infer_or_grant_manual_approval": True,
            "do_not_proceed_to_next_module_in_this_run": True,
        },
        "invariants": {
            "selector_prerequisites_all_true": all(prerequisites.values()),
            "selected_module_is_development_queue_selector_after_generic_governance_blocked_status": selected is not None and selected["module"] == NEXT_MODULE,
            "selected_action_is_development_queue_selector": selected is not None and selected["key"] == "DEVELOPMENT_QUEUE_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS",
            "selected_scope_is_repo_only_os_intelligence": selected is not None and selected["scope"] == "REPO_ONLY_OS_INTELLIGENCE",
            "generic_runner_implementation_not_selected": selected is not None and selected["key"] != "GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION",
            "config_schema_apply_runtime_not_selected": selected is not None and selected["key"] != "CONFIG_SCHEMA_APPLY_RUNTIME_PATH",
            "all_dangerous_flags_false": all(SAFETY_FLAGS.get(flag) is False for flag in DANGEROUS_FLAGS),
            "all_physical_performed_guards_false": all(value is False for value in PHYSICAL_FALSE_FIELDS.values()),
            "planned_schema_files_absent_before": physical_before["planned_schema_file_existing_count"] == 0,
            "planned_schema_files_absent_after": physical_after["planned_schema_file_existing_count"] == 0,
            "generic_runner_target_absent_before": physical_before["generic_runner_target_file_exists_now"] is False,
            "generic_runner_target_absent_after": physical_after["generic_runner_target_file_exists_now"] is False,
        },
    }


def build_payload(validation: Dict[str, Any], selector: Dict[str, Any], errors: List[str]) -> Dict[str, Any]:
    passed = not errors
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "next_action_selector_after_generic_governance_blocked_status_status": READY_STATUS if passed else "REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_V1_BLOCKED",
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": FINAL_DECISION if passed else "KEEP_GENERIC_GOVERNANCE_BLOCKED_REVIEW_NEXT_ACTION_SELECTOR_ERRORS",
        "next_action": NEXT_ACTION if passed else "REVIEW_NEXT_ACTION_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_ERRORS",
        "next_module": NEXT_MODULE if passed else None,
        "reason": (
            "Selected the repo-only development queue selector after confirming generic governance runner implementation remains blocked."
            if passed
            else "Next action selector failed closed because required blocked-status evidence or physical guards did not hold."
        ),
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "critical_issue_count": len(errors),
        "warning_count": 0,
        "errors": errors,
        "warnings": [],
        "validation": {
            "git_state": validation["git_state"],
            "head_commit_subject": validation["head_commit_subject"],
            "head_commit_paths": validation["head_commit_paths"],
            "tracked_python_validation": validation["tracked_python_validation"],
            "source_statuses": validation["source_statuses"],
            "expected_untracked_during_run": validation["expected_untracked_during_run"],
            "actual_untracked_during_run": validation["actual_untracked_during_run"],
            "physical_before": validation["physical_before"],
            "physical_after": validation["physical_after"],
        },
        "next_action_selector_after_generic_governance_blocked_status": selector,
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": [
            "implement_generic_runner",
            "create_generic_runner_target_file",
            "create_config_files",
            "apply_consolidation",
            "modify_existing_framework_files",
            "delete_old_modules",
            "move_old_modules",
            "create_schema_files",
            "edit_schema_files",
            "apply_schema_files",
            "touch_runtime",
            "execute_launcher",
            "run_strategy_research",
            "access_holdout",
            "generate_candidates",
            "change_capital",
            "place_live_or_real_orders",
            "infer_or_grant_approval",
            "proceed_to_next_module_in_this_run",
            "use_git_add_force",
        ],
        "physical_guards": selector["physical_guards"],
        "stage_recommended_now": False,
        "commit_recommended_now": False,
    }
    for flag in DANGEROUS_FLAGS:
        payload[flag] = False
    payload.update(
        {
            "manual_approval_present": False,
            "manual_approval_valid": False,
            "approval_inferred_or_guessed": False,
            "implementation_allowed_now": False,
            "generic_runner_implementation_allowed_now": False,
            "generic_runner_file_creation_allowed_now": False,
            "config_file_creation_allowed_now": False,
            "schema_creation_allowed_now": False,
            "schema_edit_allowed_now": False,
            "runtime_touch_allowed_now": False,
            "generic_runner_file_creation_performed": False,
            "config_file_creation_performed": False,
            "runtime_touch_performed": False,
            "capital_change_performed": False,
            "live_or_real_order_performed": False,
            "holdout_access_performed": False,
            "file_move_performed": False,
            "file_delete_performed": False,
            "repo_restructure_performed": False,
            "planned_schema_file_existing_count": 0,
            "generic_runner_target_file_exists_now": False,
        }
    )
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_next_action_selector_after_generic_governance_blocked_status_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_next_action_selector_after_generic_governance_blocked_status_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_next_action_selector_after_generic_governance_blocked_status_v1_latest.txt"

    rendered_json = json.dumps(payload, indent=2, sort_keys=True)
    latest_json.write_text(rendered_json, encoding="utf-8")
    timestamped_json.write_text(rendered_json, encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY NEXT ACTION SELECTOR AFTER GENERIC GOVERNANCE BLOCKED STATUS v1",
        "=" * 100,
        f"next_action_selector_after_generic_governance_blocked_status_status: {payload['next_action_selector_after_generic_governance_blocked_status_status']}",
        f"severity: {payload['severity']}",
        f"final_decision: {payload['final_decision']}",
        f"next_action: {payload['next_action']}",
        f"next_module: {payload['next_module']}",
        f"critical_issue_count: {payload['critical_issue_count']}",
        f"warning_count: {payload['warning_count']}",
        "",
        "ERRORS",
        "-" * 100,
        json.dumps(payload["errors"], indent=2, sort_keys=True),
        "",
        "SELECTOR SUMMARY",
        "-" * 100,
        json.dumps(
            {
                "selected_action": payload["next_action_selector_after_generic_governance_blocked_status"]["selected_action"],
                "confirmed_proofs": payload["next_action_selector_after_generic_governance_blocked_status"]["confirmed_proofs"],
                "prerequisites": payload["next_action_selector_after_generic_governance_blocked_status"]["prerequisites"],
                "invariants": payload["next_action_selector_after_generic_governance_blocked_status"]["invariants"],
                "physical_guards": payload["physical_guards"],
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
    return {
        "latest_json": str(latest_json),
        "timestamped_json": str(timestamped_json),
        "latest_txt": str(latest_txt),
    }


def main() -> int:
    validation = validate_inputs()
    errors = list(validation["errors"])
    safety_type_errors = [key for key, value in SAFETY_FLAGS.items() if not isinstance(value, bool)]
    if safety_type_errors:
        errors.append(f"safety flags are not boolean: {safety_type_errors}")

    selector = build_selector(validation)
    for key, value in selector["confirmed_proofs"].items():
        if value is not True:
            errors.append(f"confirmed proof not true: {key}={value}")
    for key, value in selector["invariants"].items():
        if value is not True:
            errors.append(f"invariant not true: {key}={value}")

    payload = build_payload(validation, selector, errors)
    outputs = write_outputs(payload)
    payload["outputs"] = outputs

    # Rewrite latest outputs with the output manifest included in the JSON payload.
    write_outputs(payload)

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["critical_issue_count"] == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
