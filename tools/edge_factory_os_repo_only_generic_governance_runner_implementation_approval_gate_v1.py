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

MODULE_NAME = "edge_factory_os_repo_only_generic_governance_runner_implementation_approval_gate_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_generic_governance_runner_implementation_approval_gate_v1.py"
EXPECTED_HEAD = "101d5c6"
OUT_DIR = LAB_ROOT / MODULE_NAME

SOURCE_PREVIEW_EVALUATOR_MODULE = "edge_factory_os_repo_only_generic_governance_runner_implementation_preview_evaluator_v1.py"
PREVIEW_EVALUATOR_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_generic_governance_runner_implementation_preview_evaluator_v1"
    / "repo_only_generic_governance_runner_implementation_preview_evaluator_v1_latest.json"
)
PREVIEW_EVALUATOR_POST_CHECK_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_generic_governance_runner_implementation_preview_evaluator_v1_post_commit_check"
    / "repo_only_generic_governance_runner_implementation_preview_evaluator_post_commit_check_latest.json"
)
REQUIRED_PREVIEW_EVALUATOR_STATUS = "REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_PREVIEW_EVALUATOR_V1_READY"
REQUIRED_PREVIEW_EVALUATOR_POST_CHECK_STATUS = (
    "REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_PREVIEW_EVALUATOR_POST_COMMIT_CHECK_PASS"
)
REQUIRED_PREVIEW_EVALUATOR_NEXT_MODULE = (
    "edge_factory_os_repo_only_generic_governance_runner_implementation_approval_gate_v1.py"
)

NEXT_ACTION = "BUILD_REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_MANUAL_APPROVAL_RECORD_V1"
NEXT_MODULE = "edge_factory_os_repo_only_generic_governance_runner_manual_approval_record_v1.py"
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
    "generic_runner_implementation_allowed_now",
    "generic_runner_file_creation_allowed_now",
    "config_file_creation_allowed_now",
    "consolidation_apply_allowed_now",
    "manual_approval_present_now",
    "manual_approval_valid_now",
]

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_generic_governance_runner_implementation_approval_gate_only": True,
    "repo_only_manual_approval_record_recommended_next": True,
    "manual_approval_required_before_implementation": True,
    "read_only_preview_evaluator_validation_allowed": True,
    "read_only_gate_creation_allowed": True,
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
    if isinstance(obj.get("generic_governance_runner_implementation_approval_gate_status"), str):
        return obj["generic_governance_runner_implementation_approval_gate_status"]
    if isinstance(obj.get("generic_governance_runner_implementation_preview_evaluator_status"), str):
        return obj["generic_governance_runner_implementation_preview_evaluator_status"]
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


def source_evaluation(payload: Dict[str, Any]) -> Dict[str, Any]:
    evaluation = payload.get("generic_governance_runner_implementation_preview_evaluation", {})
    return evaluation if isinstance(evaluation, dict) else {}


def validate_source_evaluation(evaluation: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if evaluation.get("ready_for_explicit_implementation_approval_gate") is not True:
        errors.append("source evaluator did not mark preview ready for explicit implementation approval gate")
    if evaluation.get("recommended_next_module") != REQUIRED_PREVIEW_EVALUATOR_NEXT_MODULE:
        errors.append(f"source evaluator recommended_next_module mismatch: {evaluation.get('recommended_next_module')}")

    proofs = evaluation.get("confirmed_proofs", {})
    required_true_proofs = [
        "generic_runner_file_is_not_created",
        "generic_runner_file_creation_not_allowed",
        "generic_runner_implementation_not_allowed",
        "config_files_are_not_created",
        "config_file_creation_not_allowed",
        "apply_is_not_allowed",
        "schema_files_not_created_edited_or_applied",
        "runtime_launcher_holdout_candidate_capital_live_order_actions_blocked",
    ]
    if not isinstance(proofs, dict):
        errors.append("source evaluator confirmed_proofs missing")
    else:
        for proof in required_true_proofs:
            if proofs.get(proof) is not True:
                errors.append(f"source evaluator proof not true: {proof}={proofs.get(proof)}")

    flags = evaluation.get("safety_flag_preview", {})
    if not isinstance(flags, dict):
        errors.append("source evaluator safety_flag_preview missing")
    else:
        for flag in DANGEROUS_FLAGS + [
            "generic_runner_implementation_allowed_now",
            "generic_runner_file_creation_allowed_now",
            "config_file_creation_allowed_now",
            "consolidation_apply_allowed_now",
        ]:
            if flags.get(flag) is not False:
                errors.append(f"source evaluator safety flag not false: {flag}={flags.get(flag)}")

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

    combined_text = " ".join(
        str(item).lower()
        for item in (evaluation.get("blocked_actions", []) or []) + (evaluation.get("non_goals", []) or [])
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
            errors.append(f"source evaluator does not block/non-goal required term: {term}")
    return errors


def validate_source_inputs(errors: List[str]) -> Dict[str, Any]:
    loaded: Dict[str, Any] = {}
    for key, path in {
        "generic_governance_runner_implementation_preview_evaluator": PREVIEW_EVALUATOR_JSON,
        "generic_governance_runner_implementation_preview_evaluator_post_check": PREVIEW_EVALUATOR_POST_CHECK_JSON,
    }.items():
        if not path.exists():
            errors.append(f"missing required implementation preview evaluator evidence: {path}")
            continue
        try:
            loaded[key] = load_json(path)
        except Exception as exc:
            errors.append(f"unreadable implementation preview evaluator evidence {path}: {exc!r}")

    evaluator = loaded.get("generic_governance_runner_implementation_preview_evaluator", {})
    post = loaded.get("generic_governance_runner_implementation_preview_evaluator_post_check", {})
    if evaluator:
        if evaluator.get("generic_governance_runner_implementation_preview_evaluator_status") != REQUIRED_PREVIEW_EVALUATOR_STATUS:
            errors.append(
                "implementation preview evaluator status mismatch: "
                f"{evaluator.get('generic_governance_runner_implementation_preview_evaluator_status')}"
            )
        if evaluator.get("next_module") != REQUIRED_PREVIEW_EVALUATOR_NEXT_MODULE:
            errors.append(f"implementation preview evaluator next_module mismatch: {evaluator.get('next_module')}")
        if evaluator.get("critical_issue_count") != 0:
            errors.append(f"implementation preview evaluator critical_issue_count not zero: {evaluator.get('critical_issue_count')}")
        evaluation = source_evaluation(evaluator)
        if not evaluation:
            errors.append("implementation preview evaluator payload missing evaluation object")
        else:
            errors.extend(validate_source_evaluation(evaluation))
    if post:
        if post.get("audit_status") != REQUIRED_PREVIEW_EVALUATOR_POST_CHECK_STATUS:
            errors.append(f"implementation preview evaluator post-check status mismatch: {post.get('audit_status')}")
        if post.get("latest_commit") != EXPECTED_HEAD:
            errors.append(
                "implementation preview evaluator post-check latest_commit mismatch: "
                f"expected={EXPECTED_HEAD} actual={post.get('latest_commit')}"
            )
        if post.get("next_module") != REQUIRED_PREVIEW_EVALUATOR_NEXT_MODULE:
            errors.append(f"implementation preview evaluator post-check next_module mismatch: {post.get('next_module')}")
        if post.get("critical_issue_count") != 0:
            errors.append(f"implementation preview evaluator post-check critical_issue_count not zero: {post.get('critical_issue_count')}")
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
    if tracked_python["tracked_python_file_count"] != 531:
        errors.append(f"tracked Python count mismatch before new file is tracked: expected=531 actual={tracked_python['tracked_python_file_count']}")

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


def source_preview_evaluator_commit(validation: Dict[str, Any]) -> Optional[str]:
    post = validation["source_inputs"].get("generic_governance_runner_implementation_preview_evaluator_post_check", {})
    latest_commit = post.get("latest_commit")
    return latest_commit if isinstance(latest_commit, str) else None


def build_approval_gate(validation: Dict[str, Any]) -> Dict[str, Any]:
    physical_before = validation["physical_before"]
    physical_after = validation["physical_after"]
    return {
        "approval_gate_status": "READY_MANUAL_APPROVAL_REQUIRED_NO_IMPLEMENTATION_ALLOWED",
        "source_preview_evaluator_module": SOURCE_PREVIEW_EVALUATOR_MODULE,
        "source_preview_evaluator_commit": source_preview_evaluator_commit(validation),
        "source_preview_evaluator_json": str(PREVIEW_EVALUATOR_JSON),
        "source_preview_evaluator_post_check_json": str(PREVIEW_EVALUATOR_POST_CHECK_JSON),
        "implementation_target_file": IMPLEMENTATION_TARGET_FILE,
        "manual_approval_required_before_implementation": True,
        "current_manual_approval_present": False,
        "current_manual_approval_valid": False,
        "implementation_allowed_now": False,
        "generic_runner_implementation_allowed_now": False,
        "generic_runner_file_creation_allowed_now": False,
        "config_file_creation_allowed_now": False,
        "schema_creation_allowed_now": False,
        "schema_edit_allowed_now": False,
        "schema_apply_allowed_now": False,
        "consolidation_apply_allowed_now": False,
        "runtime_touch_allowed_now": False,
        "required_future_manual_approval_fields": [
            "approval_record_id",
            "approval_status",
            "approved_by_human",
            "approved_at_utc",
            "approved_next_module",
            "approved_implementation_target_file",
            "source_approval_gate_module",
            "source_approval_gate_commit",
            "explicit_statement_no_config_schema_runtime_apply",
            "explicit_statement_manual_approval_is_for_preview_or_contract_only_unless_later_gate_allows_implementation",
            "dangerous_flags_all_false",
        ],
        "approval_validity_rules": [
            "manual approval is absent in this gate and therefore implementation is blocked",
            "a future approval record must be repo-only and non-apply",
            "a future approval record must name the exact implementation target file",
            "a future approval record must preserve config, schema, runtime, launcher, holdout, candidate, capital, live, and real-order blocks",
            "a future approval record must keep all dangerous flags false",
            "a future approval record must not create the generic runner file",
            "a future approval record must not create config files or schema files",
            "a future approval record must fail closed if source evaluator evidence is missing or stale",
        ],
        "blocked_actions": [
            "implement generic runner",
            "create generic runner target file",
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
            "proceed to manual approval record module in this run",
        ],
        "non_goals": [
            "do not implement the generic runner in this approval gate",
            "do not create the generic runner target file in this approval gate",
            "do not create configuration files in this approval gate",
            "do not apply consolidation in this approval gate",
            "do not modify existing framework files",
            "do not delete, move, or rewrite old modules",
            "do not create, edit, or apply schema files",
            "do not touch runtime or launchers",
            "do not access holdout, generate candidates, change capital, or place live or real orders",
            "do not proceed to the manual approval record module in this run",
        ],
        "fail_closed_conditions": [
            "HEAD is not 101d5c6",
            "repo has dirty tracked files",
            "repo has unexpected untracked files other than this intended approval gate module during execution",
            "source preview evaluator JSON is missing, unreadable, non-ready, wrong next_module, or has critical issues",
            "source preview evaluator post-check JSON is missing, unreadable, non-pass, wrong commit, wrong next_module, or has critical issues",
            "source preview evaluator does not prove readiness for explicit approval gate",
            "source preview evaluator permits implementation, generic runner file creation, config, apply, schema, runtime, launcher, holdout, candidate, capital, live, or real-order work",
            "tracked Python syntax or BOM validation fails",
            "planned schema files exist before or after",
            "generic runner target file exists before or after",
            "manual approval is claimed present or valid now",
            "any dangerous safety flag is missing, non-boolean, or not explicitly false",
        ],
        "future_next_steps_after_approval": [
            "build a repo-only manual approval record module",
            "validate the manual approval record in a separate repo-only evaluator",
            "build a future implementation contract only after approval record evidence passes",
            "continue to block direct implementation, config, schema, apply, and runtime work until an explicit later implementation gate passes",
        ],
        "required_physical_guards": {
            "before": physical_before,
            "after": physical_after,
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
        },
        "required_safety_flags": {flag: False for flag in DANGEROUS_FLAGS + EXTRA_FALSE_FLAGS},
    }


def validate_gate(gate: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    required_false_fields = [
        "current_manual_approval_present",
        "current_manual_approval_valid",
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
    for field in required_false_fields:
        if gate.get(field) is not False:
            errors.append(f"approval gate field not false: {field}={gate.get(field)}")
    if gate.get("manual_approval_required_before_implementation") is not True:
        errors.append("manual approval is not required before implementation")
    physical = gate.get("required_physical_guards", {})
    if not isinstance(physical, dict):
        errors.append("approval gate physical guards missing")
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
                errors.append(f"approval gate physical guard mismatch: {key}={physical.get(key)}")
    required_flags = gate.get("required_safety_flags", {})
    if not isinstance(required_flags, dict):
        errors.append("approval gate required_safety_flags missing")
    else:
        for flag in DANGEROUS_FLAGS + EXTRA_FALSE_FLAGS:
            if required_flags.get(flag) is not False:
                errors.append(f"approval gate required safety flag not false: {flag}={required_flags.get(flag)}")
    return errors


def build_payload(validation: Dict[str, Any]) -> Dict[str, Any]:
    errors = list(validation["errors"])
    safety_type_errors = [key for key, value in SAFETY_FLAGS.items() if not isinstance(value, bool)]
    if safety_type_errors:
        errors.append(f"safety flags are not boolean: {safety_type_errors}")
    for flag in DANGEROUS_FLAGS + EXTRA_FALSE_FLAGS:
        if SAFETY_FLAGS.get(flag) is not False:
            errors.append(f"safety flag is not explicitly false: {flag}={SAFETY_FLAGS.get(flag)}")

    gate = build_approval_gate(validation)
    errors.extend(validate_gate(gate))
    passed = not errors
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "generic_governance_runner_implementation_approval_gate_status": (
            "REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_APPROVAL_GATE_V1_READY"
            if passed
            else "BLOCKED"
        ),
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": (
            "IMPLEMENTATION_APPROVAL_GATE_READY_MANUAL_APPROVAL_REQUIRED"
            if passed
            else "BLOCKED_REVIEW_GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_APPROVAL_GATE_EVIDENCE"
        ),
        "next_action": NEXT_ACTION if passed else "REVIEW_GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_APPROVAL_GATE_ERRORS",
        "next_module": NEXT_MODULE if passed else None,
        "reason": (
            "Implementation approval gate is ready and requires a future manual approval record before any generic runner implementation; all implementation, config, schema, apply, and runtime actions remain blocked now."
            if passed
            else "Implementation approval gate failed closed because required evidence or safety constraints were missing."
        ),
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "lab_root": str(LAB_ROOT),
        "critical_issue_count": len(errors),
        "warning_count": 0,
        "errors": errors,
        "warnings": [],
        "generic_governance_runner_implementation_approval_gate": gate,
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
    latest_json = OUT_DIR / "repo_only_generic_governance_runner_implementation_approval_gate_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_generic_governance_runner_implementation_approval_gate_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_generic_governance_runner_implementation_approval_gate_v1_latest.txt"
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
