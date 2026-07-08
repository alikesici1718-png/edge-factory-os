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

MODULE_NAME = "edge_factory_os_repo_only_generic_governance_runner_implementation_preview_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_generic_governance_runner_implementation_preview_v1.py"
EXPECTED_HEAD = "4dc621f"
OUT_DIR = LAB_ROOT / MODULE_NAME

CONTRACT_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_generic_governance_runner_implementation_contract_v1"
    / "repo_only_generic_governance_runner_implementation_contract_v1_latest.json"
)
CONTRACT_POST_CHECK_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_generic_governance_runner_implementation_contract_v1_post_commit_check"
    / "repo_only_generic_governance_runner_implementation_contract_post_commit_check_latest.json"
)
REQUIRED_CONTRACT_STATUS = "REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_CONTRACT_V1_READY"
REQUIRED_CONTRACT_POST_CHECK_STATUS = "REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_CONTRACT_POST_COMMIT_CHECK_PASS"
REQUIRED_CONTRACT_NEXT_MODULE = "edge_factory_os_repo_only_generic_governance_runner_implementation_preview_v1.py"

NEXT_ACTION = "BUILD_REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_PREVIEW_EVALUATOR_V1"
NEXT_MODULE = "edge_factory_os_repo_only_generic_governance_runner_implementation_preview_evaluator_v1.py"
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
    "generic_runner_file_creation_allowed_now",
    "config_file_creation_allowed_now",
    "consolidation_apply_allowed_now",
]

CONTRACT_EXTRA_FALSE_FLAGS = [
    "generic_runner_implementation_allowed_now",
    "config_file_creation_allowed_now",
    "consolidation_apply_allowed_now",
]

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_generic_governance_runner_implementation_preview_only": True,
    "repo_only_generic_runner_implementation_preview_evaluator_recommended_next": True,
    "read_only_implementation_preview_allowed": True,
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
    if isinstance(obj.get("generic_governance_runner_implementation_preview_status"), str):
        return obj["generic_governance_runner_implementation_preview_status"]
    if isinstance(obj.get("generic_governance_runner_implementation_contract_status"), str):
        return obj["generic_governance_runner_implementation_contract_status"]
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


def contract_object(payload: Dict[str, Any]) -> Dict[str, Any]:
    contract = payload.get("generic_governance_runner_implementation_contract", {})
    return contract if isinstance(contract, dict) else {}


def validate_contract_safety(contract: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if contract.get("implementation_contract_id") != "REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_CONTRACT_V1":
        errors.append(f"contract id mismatch: {contract.get('implementation_contract_id')}")
    if contract.get("generic_runner_target_file") != GENERIC_RUNNER_TARGET_FILE:
        errors.append(f"generic runner target mismatch: {contract.get('generic_runner_target_file')}")
    if contract.get("implementation_allowed_later_only_if_contract_passes") is not True:
        errors.append("contract does not require a passing contract before later implementation preview")
    if contract.get("config_file_creation_allowed_now") is not False:
        errors.append("contract permits config file creation now")
    if contract.get("schema_creation_allowed_now") is not False:
        errors.append("contract permits schema creation now")
    if contract.get("apply_allowed_now") is not False:
        errors.append("contract permits apply now")

    required_flags = contract.get("required_safety_flags", {})
    if not isinstance(required_flags, dict):
        errors.append("contract required_safety_flags missing")
    else:
        for flag in DANGEROUS_FLAGS + CONTRACT_EXTRA_FALSE_FLAGS:
            if required_flags.get(flag) is not False:
                errors.append(f"contract required safety flag not false: {flag}={required_flags.get(flag)}")

    physical = contract.get("required_physical_guards", {})
    if not isinstance(physical, dict):
        errors.append("contract required_physical_guards missing")
    else:
        if physical.get("planned_schema_file_existing_count") != 0:
            errors.append(f"contract planned schema count not zero: {physical.get('planned_schema_file_existing_count')}")
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
                errors.append(f"contract physical guard {key} not false: {physical.get(key)}")

    combined_text = " ".join(
        str(item).lower()
        for item in (contract.get("blocked_actions", []) or []) + (contract.get("non_goals", []) or [])
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
            errors.append(f"contract does not block/non-goal required term: {term}")
    return errors


def validate_contract_inputs(errors: List[str]) -> Dict[str, Any]:
    loaded: Dict[str, Any] = {}
    for key, path in {
        "generic_governance_runner_implementation_contract": CONTRACT_JSON,
        "generic_governance_runner_implementation_contract_post_check": CONTRACT_POST_CHECK_JSON,
    }.items():
        if not path.exists():
            errors.append(f"missing required implementation contract evidence: {path}")
            continue
        try:
            loaded[key] = load_json(path)
        except Exception as exc:
            errors.append(f"unreadable implementation contract evidence {path}: {exc!r}")

    contract_payload = loaded.get("generic_governance_runner_implementation_contract", {})
    post = loaded.get("generic_governance_runner_implementation_contract_post_check", {})
    if contract_payload:
        if contract_payload.get("generic_governance_runner_implementation_contract_status") != REQUIRED_CONTRACT_STATUS:
            errors.append(
                "implementation contract status mismatch: "
                f"{contract_payload.get('generic_governance_runner_implementation_contract_status')}"
            )
        if contract_payload.get("next_module") != REQUIRED_CONTRACT_NEXT_MODULE:
            errors.append(f"implementation contract next_module mismatch: {contract_payload.get('next_module')}")
        if contract_payload.get("critical_issue_count") != 0:
            errors.append(f"implementation contract critical_issue_count not zero: {contract_payload.get('critical_issue_count')}")
        contract = contract_object(contract_payload)
        if not contract:
            errors.append("implementation contract payload missing contract object")
        else:
            errors.extend(validate_contract_safety(contract))
    if post:
        if post.get("audit_status") != REQUIRED_CONTRACT_POST_CHECK_STATUS:
            errors.append(f"implementation contract post-check status mismatch: {post.get('audit_status')}")
        if post.get("latest_commit") != EXPECTED_HEAD:
            errors.append(
                "implementation contract post-check latest_commit mismatch: "
                f"expected={EXPECTED_HEAD} actual={post.get('latest_commit')}"
            )
        if post.get("next_module") != REQUIRED_CONTRACT_NEXT_MODULE:
            errors.append(f"implementation contract post-check next_module mismatch: {post.get('next_module')}")
        if post.get("critical_issue_count") != 0:
            errors.append(f"implementation contract post-check critical_issue_count not zero: {post.get('critical_issue_count')}")
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
    if tracked_python["tracked_python_file_count"] != 529:
        errors.append(f"tracked Python count mismatch before new file is tracked: expected=529 actual={tracked_python['tracked_python_file_count']}")

    contract_inputs = validate_contract_inputs(errors)

    physical_after = physical_guard_snapshot()
    if physical_after["planned_schema_file_existing_count"] != 0:
        errors.append(f"planned schema files existed after run: {physical_after['existing_planned_schema_files']}")

    return {
        "errors": errors,
        "git_state": git_state,
        "expected_untracked_during_run": expected_untracked,
        "tracked_python_validation": tracked_python,
        "contract_inputs": contract_inputs,
        "physical_before": physical_before,
        "physical_after": physical_after,
    }


def source_contract(validation: Dict[str, Any]) -> Dict[str, Any]:
    payload = validation["contract_inputs"].get("generic_governance_runner_implementation_contract", {})
    return contract_object(payload)


def source_contract_commit(validation: Dict[str, Any]) -> Optional[str]:
    post = validation["contract_inputs"].get("generic_governance_runner_implementation_contract_post_check", {})
    latest_commit = post.get("latest_commit")
    return latest_commit if isinstance(latest_commit, str) else None


def build_preview(validation: Dict[str, Any]) -> Dict[str, Any]:
    contract = source_contract(validation)
    physical_before = validation["physical_before"]
    physical_after = validation["physical_after"]
    return {
        "generic_governance_runner_implementation_preview_status": (
            "PREVIEW_ONLY_NO_GENERIC_RUNNER_FILE_NO_CONFIG_NO_SCHEMA_NO_APPLY_NO_RUNTIME"
        ),
        "contract_inputs_verified": {
            "contract_status": first_status(
                validation["contract_inputs"].get("generic_governance_runner_implementation_contract", {})
            ),
            "contract_post_check_status": first_status(
                validation["contract_inputs"].get("generic_governance_runner_implementation_contract_post_check", {})
            ),
            "contract_next_module": validation["contract_inputs"]
            .get("generic_governance_runner_implementation_contract", {})
            .get("next_module"),
            "contract_post_check_next_module": validation["contract_inputs"]
            .get("generic_governance_runner_implementation_contract_post_check", {})
            .get("next_module"),
            "source_contract_commit": source_contract_commit(validation),
            "implementation_contract_id": contract.get("implementation_contract_id"),
            "implementation_contract_status": contract.get("implementation_contract_status"),
        },
        "proposed_runner_file_preview": {
            "target_file": GENERIC_RUNNER_TARGET_FILE,
            "target_file_exists_now": (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists(),
            "generic_runner_file_created_now": False,
            "generic_runner_file_creation_allowed_now": False,
            "generic_runner_implementation_allowed_now": False,
            "preview_mode": "design_only_no_file_write",
            "implementation_scope_preview": [
                "future runner file would be generated only after evaluator and explicit approval gates",
                "future runner file would be repo-only and would not touch runtime",
                "this preview writes no runner file and modifies no existing framework file",
            ],
        },
        "proposed_runner_behavior_preview": {
            "runner_implemented_now": False,
            "config_files_created_now": False,
            "config_file_creation_allowed_now": False,
            "apply_allowed_now": False,
            "schema_creation_allowed_now": False,
            "schema_edit_allowed_now": False,
            "schema_apply_allowed_now": False,
            "runtime_touch_allowed_now": False,
            "expected_later_behaviors_from_contract": contract.get("required_runner_behaviors", []),
            "fail_closed_default": True,
            "non_apply_output_only": True,
        },
        "state_transition_preview": {
            "transition_engine_implemented_now": False,
            "transition_engine_mode": "preview_only",
            "states": [
                {
                    "state_id": "CONTRACT_EVIDENCE_READY",
                    "description": "contract and post-check evidence are present and ready",
                    "apply_allowed": False,
                    "next_if_pass": "IMPLEMENTATION_PREVIEW_READY",
                    "next_if_fail": "BLOCKED_REVIEW_CONTRACT_EVIDENCE",
                },
                {
                    "state_id": "IMPLEMENTATION_PREVIEW_READY",
                    "description": "repo-only preview may be evaluated by a future evaluator module",
                    "apply_allowed": False,
                    "next_if_pass": NEXT_MODULE,
                    "next_if_fail": "BLOCKED_REVIEW_IMPLEMENTATION_PREVIEW",
                },
                {
                    "state_id": "IMPLEMENTATION_FILE_REQUESTED",
                    "description": "direct generic runner implementation is requested too early",
                    "apply_allowed": False,
                    "next_if_pass": None,
                    "next_if_fail": "BLOCKED_DIRECT_IMPLEMENTATION_NOT_APPROVED",
                },
                {
                    "state_id": "CONFIG_SCHEMA_RUNTIME_REQUESTED",
                    "description": "config, schema, runtime, launcher, holdout, candidate, capital, or order work is requested too early",
                    "apply_allowed": False,
                    "next_if_pass": None,
                    "next_if_fail": "BLOCKED_DANGEROUS_ACTION_NOT_APPROVED",
                },
            ],
            "all_states_apply_allowed_false": True,
        },
        "input_validation_preview": {
            "required_inputs": [
                {
                    "name": "implementation_contract_json",
                    "path": str(CONTRACT_JSON),
                    "required_status": REQUIRED_CONTRACT_STATUS,
                    "required_critical_issue_count": 0,
                    "required_next_module": REQUIRED_CONTRACT_NEXT_MODULE,
                },
                {
                    "name": "implementation_contract_post_check_json",
                    "path": str(CONTRACT_POST_CHECK_JSON),
                    "required_status": REQUIRED_CONTRACT_POST_CHECK_STATUS,
                    "required_latest_commit": EXPECTED_HEAD,
                    "required_critical_issue_count": 0,
                    "required_next_module": REQUIRED_CONTRACT_NEXT_MODULE,
                },
                {
                    "name": "repo_git_state",
                    "required_head": EXPECTED_HEAD,
                    "required_dirty_tracked_count": 0,
                    "allowed_untracked_during_run": [CURRENT_TOOL_REL],
                },
                {
                    "name": "tracked_python_validation",
                    "required_tracked_python_file_count_before_preview_commit": 529,
                    "required_syntax_error_count": 0,
                    "required_bom_error_count": 0,
                },
                {
                    "name": "planned_schema_physical_absence",
                    "required_planned_schema_file_existing_count_before": 0,
                    "required_planned_schema_file_existing_count_after": 0,
                },
            ],
            "missing_evidence_behavior": "BLOCKED with explicit missing evidence list",
            "fail_closed_conditions": [
                "HEAD is not 4dc621f",
                "repo has dirty tracked files",
                "repo has unexpected untracked files other than this intended preview module",
                "implementation contract JSON is missing, unreadable, non-ready, wrong next_module, or has critical issues",
                "implementation contract post-check JSON is missing, unreadable, non-pass, wrong commit, wrong next_module, or has critical issues",
                "implementation contract permits implementation, file creation, config, apply, schema, runtime, launcher, holdout, candidate, capital, live, or real-order work",
                "tracked Python syntax or BOM validation fails",
                "planned schema files exist before or after",
                "any dangerous safety flag is missing, non-boolean, or not explicitly false",
            ],
        },
        "output_payload_preview": {
            "status_field": "generic_governance_runner_implementation_preview_status",
            "ready_status": "REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_PREVIEW_V1_READY",
            "final_decision": "GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_PREVIEW_READY_FOR_EVALUATOR",
            "next_action": NEXT_ACTION,
            "next_module": NEXT_MODULE,
            "critical_issue_count_required": 0,
            "required_outputs": [
                "generic_governance_runner_implementation_preview_status",
                "final_decision",
                "next_action",
                "next_module",
                "critical_issue_count",
                "generic_governance_runner_implementation_preview",
                "validation",
                "physical_guards",
                "safety_flags",
            ],
        },
        "physical_guard_preview": {
            "planned_schema_file_existing_count": 0,
            "runtime_touch_performed": False,
            "launcher_executed": False,
            "capital_change_performed": False,
            "live_or_real_order_performed": False,
            "holdout_access_performed": False,
            "file_move_performed": False,
            "file_delete_performed": False,
            "repo_restructure_performed": False,
            "before": physical_before,
            "after": physical_after,
        },
        "safety_flag_preview": SAFETY_FLAGS,
        "blocked_actions": [
            "implement generic runner",
            "create generic runner file",
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
            "proceed to implementation preview evaluator in this run",
        ],
        "non_goals": [
            "do not implement the generic runner in this preview",
            "do not create the generic runner file in this preview",
            "do not create configuration files in this preview",
            "do not apply consolidation in this preview",
            "do not modify existing framework files",
            "do not delete, move, or rewrite old modules",
            "do not create, edit, or apply schema files",
            "do not touch runtime or launchers",
            "do not access holdout, generate candidates, change capital, or place live or real orders",
            "do not proceed to the implementation preview evaluator module in this run",
        ],
        "acceptance_test_preview": [
            "preview exits zero only when implementation contract JSON and post-check JSON both pass",
            "preview output status is REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_PREVIEW_V1_READY",
            "preview output critical_issue_count is 0",
            "preview output final_decision is GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_PREVIEW_READY_FOR_EVALUATOR",
            "preview output next_action is BUILD_REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_PREVIEW_EVALUATOR_V1",
            "preview output next_module is edge_factory_os_repo_only_generic_governance_runner_implementation_preview_evaluator_v1.py",
            "preview proves generic runner file is not created",
            "preview proves config files are not created",
            "preview proves apply is not allowed",
            "preview proves schema files are not created, edited, or applied",
            "preview proves runtime, launcher, holdout, candidate, capital, live, and order actions are blocked",
            "preview fails closed if implementation, apply, config, schema, or runtime actions are permitted",
        ],
    }


def evaluate_preview_safety(preview: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    required_sections = [
        "generic_governance_runner_implementation_preview_status",
        "contract_inputs_verified",
        "proposed_runner_file_preview",
        "proposed_runner_behavior_preview",
        "state_transition_preview",
        "input_validation_preview",
        "output_payload_preview",
        "physical_guard_preview",
        "safety_flag_preview",
        "blocked_actions",
        "non_goals",
        "acceptance_test_preview",
    ]
    for section in required_sections:
        if section not in preview:
            errors.append(f"preview missing required section: {section}")

    runner_file = preview.get("proposed_runner_file_preview", {})
    if not isinstance(runner_file, dict):
        errors.append("proposed_runner_file_preview missing")
    else:
        if runner_file.get("generic_runner_file_created_now") is not False:
            errors.append("preview permits or performs generic runner file creation")
        if runner_file.get("generic_runner_file_creation_allowed_now") is not False:
            errors.append("preview permits generic runner file creation now")
        if runner_file.get("generic_runner_implementation_allowed_now") is not False:
            errors.append("preview permits generic runner implementation now")

    behavior = preview.get("proposed_runner_behavior_preview", {})
    if not isinstance(behavior, dict):
        errors.append("proposed_runner_behavior_preview missing")
    else:
        for key in [
            "runner_implemented_now",
            "config_files_created_now",
            "config_file_creation_allowed_now",
            "apply_allowed_now",
            "schema_creation_allowed_now",
            "schema_edit_allowed_now",
            "schema_apply_allowed_now",
            "runtime_touch_allowed_now",
        ]:
            if behavior.get(key) is not False:
                errors.append(f"preview behavior {key} not false: {behavior.get(key)}")

    transitions = preview.get("state_transition_preview", {})
    if not isinstance(transitions, dict):
        errors.append("state_transition_preview missing")
    else:
        if transitions.get("transition_engine_implemented_now") is not False:
            errors.append("preview implements transition engine now")
        if transitions.get("all_states_apply_allowed_false") is not True:
            errors.append("preview does not prove all state transitions keep apply false")
        states = transitions.get("states", [])
        if not isinstance(states, list) or len(states) < 4:
            errors.append("state_transition_preview has fewer than 4 states")
        elif not all(isinstance(state, dict) and state.get("apply_allowed") is False for state in states):
            errors.append("one or more preview states allow apply")

    physical = preview.get("physical_guard_preview", {})
    if not isinstance(physical, dict):
        errors.append("physical_guard_preview missing")
    else:
        if physical.get("planned_schema_file_existing_count") != 0:
            errors.append(f"preview planned schema count not zero: {physical.get('planned_schema_file_existing_count')}")
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
                errors.append(f"preview physical guard {key} not false: {physical.get(key)}")

    flags = preview.get("safety_flag_preview", {})
    if not isinstance(flags, dict):
        errors.append("safety_flag_preview missing")
    else:
        for flag in DANGEROUS_FLAGS + EXTRA_FALSE_FLAGS:
            if flags.get(flag) is not False:
                errors.append(f"preview safety flag not false: {flag}={flags.get(flag)}")

    combined_text = " ".join(
        str(item).lower()
        for item in (preview.get("blocked_actions", []) or []) + (preview.get("non_goals", []) or [])
    )
    for term in [
        "implement generic runner",
        "create generic runner file",
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
            errors.append(f"preview does not block/non-goal required term: {term}")
    return errors


def build_payload(validation: Dict[str, Any]) -> Dict[str, Any]:
    errors = list(validation["errors"])
    safety_type_errors = [key for key, value in SAFETY_FLAGS.items() if not isinstance(value, bool)]
    if safety_type_errors:
        errors.append(f"safety flags are not boolean: {safety_type_errors}")
    for flag in DANGEROUS_FLAGS + EXTRA_FALSE_FLAGS:
        if SAFETY_FLAGS.get(flag) is not False:
            errors.append(f"safety flag is not explicitly false: {flag}={SAFETY_FLAGS.get(flag)}")

    preview = build_preview(validation)
    preview_errors = evaluate_preview_safety(preview)
    errors.extend(preview_errors)
    passed = not errors
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "generic_governance_runner_implementation_preview_status": (
            "REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_PREVIEW_V1_READY"
            if passed
            else "BLOCKED"
        ),
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": (
            "GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_PREVIEW_READY_FOR_EVALUATOR"
            if passed
            else "BLOCKED_REVIEW_GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_PREVIEW_EVIDENCE"
        ),
        "next_action": NEXT_ACTION if passed else "REVIEW_GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_PREVIEW_ERRORS",
        "next_module": NEXT_MODULE if passed else None,
        "reason": (
            "Generic governance runner implementation preview is ready for a repo-only non-apply evaluator; direct implementation, config, schema, apply, and runtime work remain blocked."
            if passed
            else "Generic governance runner implementation preview failed closed because required evidence or safety constraints were missing."
        ),
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "lab_root": str(LAB_ROOT),
        "critical_issue_count": len(errors),
        "warning_count": 0,
        "errors": errors,
        "warnings": [],
        "generic_governance_runner_implementation_preview": preview,
        "validation": {
            "git_state": validation["git_state"],
            "expected_untracked_during_run": validation["expected_untracked_during_run"],
            "tracked_python_validation": validation["tracked_python_validation"],
            "contract_inputs": {
                key: {
                    "status": first_status(value),
                    "critical_issue_count": value.get("critical_issue_count"),
                    "next_module": value.get("next_module"),
                    "latest_commit": value.get("latest_commit"),
                    "final_decision": value.get("final_decision"),
                }
                for key, value in validation["contract_inputs"].items()
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
    latest_json = OUT_DIR / "repo_only_generic_governance_runner_implementation_preview_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_generic_governance_runner_implementation_preview_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_generic_governance_runner_implementation_preview_v1_latest.txt"
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
