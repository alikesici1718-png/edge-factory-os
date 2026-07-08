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

MODULE_NAME = "edge_factory_os_repo_only_generic_governance_runner_implementation_contract_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_generic_governance_runner_implementation_contract_v1.py"
EXPECTED_HEAD = "9e5df14"
OUT_DIR = LAB_ROOT / MODULE_NAME

SOURCE_PREVIEW_EVALUATOR_MODULE = "edge_factory_os_repo_only_generic_governance_runner_preview_evaluator_v1.py"
SOURCE_PREVIEW_EVALUATOR_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_generic_governance_runner_preview_evaluator_v1"
    / "repo_only_generic_governance_runner_preview_evaluator_v1_latest.json"
)
SOURCE_PREVIEW_EVALUATOR_POST_CHECK_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_generic_governance_runner_preview_evaluator_v1_post_commit_check"
    / "repo_only_generic_governance_runner_preview_evaluator_post_commit_check_latest.json"
)
REQUIRED_SOURCE_PREVIEW_EVALUATOR_STATUS = "REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_PREVIEW_EVALUATOR_V1_READY"
REQUIRED_SOURCE_PREVIEW_EVALUATOR_POST_CHECK_STATUS = "REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_PREVIEW_EVALUATOR_POST_COMMIT_CHECK_PASS"
REQUIRED_SOURCE_PREVIEW_EVALUATOR_NEXT_MODULE = (
    "edge_factory_os_repo_only_generic_governance_runner_implementation_contract_v1.py"
)

NEXT_ACTION = "BUILD_REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_PREVIEW_V1"
NEXT_MODULE = "edge_factory_os_repo_only_generic_governance_runner_implementation_preview_v1.py"
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
]

EXTRA_FALSE_FLAGS = [
    "generic_runner_implementation_allowed_now",
    "config_file_creation_allowed_now",
    "consolidation_apply_allowed_now",
]

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_generic_governance_runner_implementation_contract_only": True,
    "repo_only_generic_runner_implementation_preview_recommended_next": True,
    "read_only_preview_evaluator_conversion_allowed": True,
    "read_only_validation_allowed": True,
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
    if isinstance(obj.get("generic_governance_runner_implementation_contract_status"), str):
        return obj["generic_governance_runner_implementation_contract_status"]
    if isinstance(obj.get("generic_governance_runner_preview_evaluator_status"), str):
        return obj["generic_governance_runner_preview_evaluator_status"]
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


def physical_guard_snapshot() -> Dict[str, Any]:
    existing = planned_schema_existing_files()
    return {
        "planned_schema_rel_paths": PLANNED_SCHEMA_REL_PATHS,
        "planned_schema_path_count": len(PLANNED_SCHEMA_REL_PATHS),
        "existing_planned_schema_files": existing,
        "planned_schema_file_existing_count": len(existing),
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


def source_evaluation(payload: Dict[str, Any]) -> Dict[str, Any]:
    evaluation = payload.get("generic_governance_runner_preview_evaluation", {})
    return evaluation if isinstance(evaluation, dict) else {}


def validate_source_preview_evaluator_safety(evaluation: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if evaluation.get("ready_for_implementation_contract") is not True:
        errors.append("source evaluator did not mark preview ready for implementation contract")
    if evaluation.get("recommended_next_module") != REQUIRED_SOURCE_PREVIEW_EVALUATOR_NEXT_MODULE:
        errors.append(f"source evaluator recommended_next_module mismatch: {evaluation.get('recommended_next_module')}")

    design = evaluation.get("simulated_runner_design", {})
    if not isinstance(design, dict):
        errors.append("source evaluator simulated_runner_design missing")
    else:
        if design.get("generic_runner_is_implemented") is not False:
            errors.append("source evaluator permits or reports generic runner implementation")
        if design.get("generic_runner_implementation_allowed_now") is not False:
            errors.append("source evaluator permits generic runner implementation now")
        if design.get("config_files_created") is not False:
            errors.append("source evaluator reports config files created")
        if design.get("config_file_creation_allowed_now") is not False:
            errors.append("source evaluator permits config file creation now")

    state_table = evaluation.get("config_state_table_preview", {})
    if not isinstance(state_table, dict) or state_table.get("all_states_apply_allowed_false") is not True:
        errors.append("source evaluator does not prove apply is false for all config states")

    physical = evaluation.get("physical_guard_preview", {})
    if not isinstance(physical, dict):
        errors.append("source evaluator physical_guard_preview missing")
    else:
        if physical.get("planned_schema_file_existing_count") != 0:
            errors.append(f"source evaluator planned schema count not zero: {physical.get('planned_schema_file_existing_count')}")
        for key in [
            "runtime_touch_performed",
            "launcher_executed",
            "capital_change_performed",
            "live_or_real_order_performed",
            "holdout_access_performed",
            "file_move_performed",
            "file_delete_performed",
            "repo_restructure_performed",
        ]:
            if physical.get(key) is not False:
                errors.append(f"source evaluator physical guard {key} not false: {physical.get(key)}")

    flags = evaluation.get("safety_flag_preview", {})
    if not isinstance(flags, dict):
        errors.append("source evaluator safety_flag_preview missing")
    else:
        for flag in DANGEROUS_FLAGS + EXTRA_FALSE_FLAGS:
            if flags.get(flag) is not False:
                errors.append(f"source evaluator safety flag not false: {flag}={flags.get(flag)}")

    combined_text = " ".join(
        str(item).lower()
        for item in (evaluation.get("blocked_actions", []) or []) + (evaluation.get("non_goals", []) or [])
    )
    for term in [
        "implement generic runner",
        "create config files",
        "apply consolidation",
        "modify existing framework files",
        "delete old modules",
        "move old modules",
        "edit schemas",
        "create schema files",
        "apply schemas",
        "run strategy research",
        "touch runtime",
        "execute launcher",
        "access holdout",
        "generate candidates",
        "change capital",
        "live",
        "real orders",
    ]:
        if term not in combined_text:
            errors.append(f"source evaluator does not block/non-goal required term: {term}")
    return errors


def validate_source_inputs(errors: List[str]) -> Dict[str, Any]:
    loaded: Dict[str, Any] = {}
    for key, path in {
        "generic_governance_runner_preview_evaluator": SOURCE_PREVIEW_EVALUATOR_JSON,
        "generic_governance_runner_preview_evaluator_post_check": SOURCE_PREVIEW_EVALUATOR_POST_CHECK_JSON,
    }.items():
        if not path.exists():
            errors.append(f"missing required source evaluator evidence: {path}")
            continue
        try:
            loaded[key] = load_json(path)
        except Exception as exc:
            errors.append(f"unreadable source evaluator evidence {path}: {exc!r}")

    evaluator = loaded.get("generic_governance_runner_preview_evaluator", {})
    post = loaded.get("generic_governance_runner_preview_evaluator_post_check", {})
    if evaluator:
        if evaluator.get("generic_governance_runner_preview_evaluator_status") != REQUIRED_SOURCE_PREVIEW_EVALUATOR_STATUS:
            errors.append(
                "source evaluator status mismatch: "
                f"{evaluator.get('generic_governance_runner_preview_evaluator_status')}"
            )
        if evaluator.get("next_module") != REQUIRED_SOURCE_PREVIEW_EVALUATOR_NEXT_MODULE:
            errors.append(f"source evaluator next_module mismatch: {evaluator.get('next_module')}")
        if evaluator.get("critical_issue_count") != 0:
            errors.append(f"source evaluator critical_issue_count not zero: {evaluator.get('critical_issue_count')}")
        evaluation = source_evaluation(evaluator)
        if not evaluation:
            errors.append("source evaluator payload missing generic_governance_runner_preview_evaluation object")
        else:
            errors.extend(validate_source_preview_evaluator_safety(evaluation))
    if post:
        if post.get("audit_status") != REQUIRED_SOURCE_PREVIEW_EVALUATOR_POST_CHECK_STATUS:
            errors.append(f"source evaluator post-check status mismatch: {post.get('audit_status')}")
        if post.get("latest_commit") != EXPECTED_HEAD:
            errors.append(
                "source evaluator post-check latest_commit mismatch: "
                f"expected={EXPECTED_HEAD} actual={post.get('latest_commit')}"
            )
        if post.get("next_module") != REQUIRED_SOURCE_PREVIEW_EVALUATOR_NEXT_MODULE:
            errors.append(f"source evaluator post-check next_module mismatch: {post.get('next_module')}")
        if post.get("critical_issue_count") != 0:
            errors.append(f"source evaluator post-check critical_issue_count not zero: {post.get('critical_issue_count')}")
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

    tracked_python = validate_tracked_python()
    if not tracked_python["pass"]:
        errors.append(f"tracked Python validation failed: syntax={tracked_python['syntax_errors'][:20]} bom={tracked_python['bom_errors']}")
    if tracked_python["tracked_python_file_count"] != 528:
        errors.append(f"tracked Python count mismatch before new file is tracked: expected=528 actual={tracked_python['tracked_python_file_count']}")

    source_inputs = validate_source_inputs(errors)

    physical_after = physical_guard_snapshot()
    if physical_after["planned_schema_file_existing_count"] != 0:
        errors.append(f"planned schema files existed after run: {physical_after['existing_planned_schema_files']}")

    return {
        "errors": errors,
        "git_state": git_state,
        "expected_untracked_during_run": expected_untracked,
        "tracked_python_validation": tracked_python,
        "source_inputs": source_inputs,
        "physical_before": physical_before,
        "physical_after": physical_after,
    }


def source_preview_evaluator_commit(validation: Dict[str, Any]) -> Optional[str]:
    post = validation["source_inputs"].get("generic_governance_runner_preview_evaluator_post_check", {})
    latest_commit = post.get("latest_commit")
    return latest_commit if isinstance(latest_commit, str) else None


def source_preview_evaluation(validation: Dict[str, Any]) -> Dict[str, Any]:
    payload = validation["source_inputs"].get("generic_governance_runner_preview_evaluator", {})
    return source_evaluation(payload)


def build_contract(validation: Dict[str, Any]) -> Dict[str, Any]:
    evaluation = source_preview_evaluation(validation)
    design = evaluation.get("simulated_runner_design", {}) if isinstance(evaluation, dict) else {}
    source_target_name = design.get("target_name") if isinstance(design, dict) else None
    physical_before = validation["physical_before"]
    physical_after = validation["physical_after"]
    required_false_flags = {flag: False for flag in DANGEROUS_FLAGS + EXTRA_FALSE_FLAGS}
    return {
        "implementation_contract_id": "REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_CONTRACT_V1",
        "implementation_contract_status": "STRICT_CONTRACT_READY_NO_IMPLEMENTATION_NO_CONFIG_NO_APPLY_NO_SCHEMA_NO_RUNTIME",
        "source_preview_evaluator_module": SOURCE_PREVIEW_EVALUATOR_MODULE,
        "source_preview_evaluator_commit": source_preview_evaluator_commit(validation),
        "source_preview_evaluator_json": str(SOURCE_PREVIEW_EVALUATOR_JSON),
        "source_preview_evaluator_post_check_json": str(SOURCE_PREVIEW_EVALUATOR_POST_CHECK_JSON),
        "source_preview_evaluator_status": first_status(
            validation["source_inputs"].get("generic_governance_runner_preview_evaluator", {})
        ),
        "source_preview_evaluator_post_check_status": first_status(
            validation["source_inputs"].get("generic_governance_runner_preview_evaluator_post_check", {})
        ),
        "source_preview_target_name": source_target_name,
        "generic_runner_target_file": GENERIC_RUNNER_TARGET_FILE,
        "implementation_allowed_later_only_if_contract_passes": True,
        "implementation_allowed_later_constraints": [
            "a future module may only preview implementation after this contract exits ready with critical_issue_count 0",
            "a future implementation preview must remain repo-only and non-apply",
            "direct implementation remains blocked in this module",
            "config file creation remains blocked in this module",
            "schema creation, editing, and apply remain blocked in this module",
            "runtime, launcher, holdout, candidates, capital, live, and real orders remain blocked",
        ],
        "config_file_creation_allowed_now": False,
        "schema_creation_allowed_now": False,
        "apply_allowed_now": False,
        "required_runner_behaviors": [
            "load a future repo-only governance config only after a separate approved preview gate exists",
            "validate each configured module state before selecting any next action",
            "fail closed when required input evidence is missing, stale, unreadable, or internally inconsistent",
            "emit deterministic JSON with status, final_decision, next_action, next_module, validation, physical_guards, and safety_flags",
            "keep apply disabled unless a future explicit approval gate changes that state",
            "preserve old selector, queue, backlog, and framework modules unless a later explicit migration gate approves changes",
            "treat schema, runtime, launcher, holdout, candidate generation, capital, and live or real order actions as blocked by default",
        ],
        "required_inputs": [
            {
                "name": "latest_generic_governance_runner_preview_evaluator_json",
                "path": str(SOURCE_PREVIEW_EVALUATOR_JSON),
                "required_status": REQUIRED_SOURCE_PREVIEW_EVALUATOR_STATUS,
                "required_critical_issue_count": 0,
                "required_next_module": REQUIRED_SOURCE_PREVIEW_EVALUATOR_NEXT_MODULE,
                "required_ready_for_implementation_contract": True,
            },
            {
                "name": "latest_generic_governance_runner_preview_evaluator_post_check_json",
                "path": str(SOURCE_PREVIEW_EVALUATOR_POST_CHECK_JSON),
                "required_status": REQUIRED_SOURCE_PREVIEW_EVALUATOR_POST_CHECK_STATUS,
                "required_latest_commit": EXPECTED_HEAD,
                "required_critical_issue_count": 0,
                "required_next_module": REQUIRED_SOURCE_PREVIEW_EVALUATOR_NEXT_MODULE,
            },
            {
                "name": "repo_git_state",
                "required_head": EXPECTED_HEAD,
                "required_dirty_tracked_count": 0,
                "allowed_untracked_during_run": [CURRENT_TOOL_REL],
            },
            {
                "name": "tracked_python_validation",
                "required_tracked_python_file_count_before_contract_commit": 528,
                "required_syntax_error_count": 0,
                "required_bom_error_count": 0,
            },
            {
                "name": "planned_schema_physical_absence",
                "required_planned_schema_file_existing_count_before": 0,
                "required_planned_schema_file_existing_count_after": 0,
                "planned_schema_rel_paths": PLANNED_SCHEMA_REL_PATHS,
            },
        ],
        "required_outputs": [
            "generic_governance_runner_implementation_contract_status",
            "final_decision",
            "next_action",
            "next_module",
            "critical_issue_count",
            "generic_governance_runner_implementation_contract",
            "validation",
            "physical_guards",
            "safety_flags",
        ],
        "required_physical_guards": {
            "before": physical_before,
            "after": physical_after,
            "planned_schema_file_existing_count": 0,
            "runtime_touch_performed": False,
            "launcher_executed": False,
            "capital_change_performed": False,
            "live_or_real_order_performed": False,
            "holdout_access_performed": False,
            "file_move_performed": False,
            "file_delete_performed": False,
            "repo_restructure_performed": False,
        },
        "required_safety_flags": required_false_flags,
        "blocked_actions": [
            "implement generic runner",
            "create config files",
            "apply consolidation",
            "modify existing framework files",
            "delete old modules",
            "move old modules",
            "edit schemas",
            "create schema files",
            "apply schemas",
            "run strategy research",
            "touch runtime",
            "execute launcher",
            "access holdout",
            "generate candidates",
            "change capital",
            "place live or real orders",
            "use git add -f",
            "change .gitignore",
            "delete backups",
            "perform mass metadata patches",
            "perform blind fix-all changes",
            "proceed to implementation preview in this run",
        ],
        "non_goals": [
            "do not implement the generic runner in this contract",
            "do not create a runner implementation file in this contract",
            "do not create configuration files in this contract",
            "do not apply consolidation in this contract",
            "do not modify existing framework files",
            "do not delete, move, or rewrite old modules",
            "do not create, edit, or apply schema files",
            "do not touch runtime or launchers",
            "do not access holdout, generate candidates, change capital, or place live or real orders",
            "do not proceed to the implementation preview module in this run",
        ],
        "acceptance_tests": [
            "module exits zero only when source preview evaluator JSON and post-check JSON both pass",
            "module output status is REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_CONTRACT_V1_READY",
            "module output critical_issue_count is 0",
            "module output final_decision is GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_CONTRACT_READY_FOR_PREVIEW",
            "module output next_action is BUILD_REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_PREVIEW_V1",
            "module output next_module is edge_factory_os_repo_only_generic_governance_runner_implementation_preview_v1.py",
            "module proves generic_runner_implementation_allowed_now is false",
            "module proves config_file_creation_allowed_now is false",
            "module proves consolidation_apply_allowed_now is false",
            "module proves schema creation, schema editing, schema apply, direct apply, and runtime actions are false",
            "module proves planned schema files are absent before and after",
            "module fails closed if direct implementation, apply, config, schema, runtime, launcher, holdout, candidate, capital, live, or real order actions are permitted",
        ],
        "fail_closed_conditions": [
            "HEAD is not 9e5df14",
            "repo has dirty tracked files",
            "repo has unexpected untracked files other than this intended module during execution",
            "target file is absent before writing requirement was not satisfied by the wrapper",
            "source preview evaluator JSON is missing, unreadable, non-ready, wrong next_module, or has critical issues",
            "source preview evaluator post-check JSON is missing, unreadable, non-pass, wrong commit, wrong next_module, or has critical issues",
            "source preview evaluator does not mark ready_for_implementation_contract true",
            "source preview evaluator permits generic runner implementation, config file creation, apply, schema, runtime, launcher, holdout, candidate, capital, live, or real-order work",
            "tracked Python syntax or BOM validation fails",
            "planned schema files exist before or after",
            "any dangerous safety flag is missing, non-boolean, or not explicitly false",
            "generic_runner_implementation_allowed_now is not false",
            "config_file_creation_allowed_now is not false",
            "consolidation_apply_allowed_now is not false",
        ],
        "future_approval_gates": [
            "explicit approval before building the repo-only generic governance runner implementation preview module",
            "explicit approval before implementing any generic runner file",
            "explicit approval before creating any config file",
            "explicit approval before applying consolidation",
            "explicit approval before modifying framework files",
            "explicit approval before creating, editing, or applying schema files",
            "explicit approval before any cleanup, deletion, move, or repo restructure",
            "explicit approval before touching runtime, launchers, holdout, candidates, capital, live, or real orders",
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

    contract = build_contract(validation)
    if contract["config_file_creation_allowed_now"] is not False:
        errors.append("contract permits config file creation now")
    if contract["schema_creation_allowed_now"] is not False:
        errors.append("contract permits schema creation now")
    if contract["apply_allowed_now"] is not False:
        errors.append("contract permits apply now")

    passed = not errors
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "generic_governance_runner_implementation_contract_status": (
            "REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_CONTRACT_V1_READY"
            if passed
            else "BLOCKED"
        ),
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": (
            "GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_CONTRACT_READY_FOR_PREVIEW"
            if passed
            else "BLOCKED_REVIEW_GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_CONTRACT_EVIDENCE"
        ),
        "next_action": NEXT_ACTION if passed else "REVIEW_GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_CONTRACT_ERRORS",
        "next_module": NEXT_MODULE if passed else None,
        "reason": (
            "Generic governance runner implementation contract is ready for a repo-only non-apply implementation preview; direct implementation, config, schema, apply, and runtime work remain blocked."
            if passed
            else "Generic governance runner implementation contract failed closed because required evidence or safety constraints were missing."
        ),
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "lab_root": str(LAB_ROOT),
        "critical_issue_count": len(errors),
        "warning_count": 0,
        "errors": errors,
        "warnings": [],
        "generic_governance_runner_implementation_contract": contract,
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
    return payload


def write_outputs(payload: Dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_generic_governance_runner_implementation_contract_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_generic_governance_runner_implementation_contract_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_generic_governance_runner_implementation_contract_v1_latest.txt"
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
