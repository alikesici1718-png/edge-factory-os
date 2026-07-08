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

MODULE_NAME = "edge_factory_os_repo_only_framework_consolidation_preview_evaluator_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_framework_consolidation_preview_evaluator_v1.py"
EXPECTED_HEAD = "f5a8537"
OUT_DIR = LAB_ROOT / MODULE_NAME

PREVIEW_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_framework_consolidation_preview_v1"
    / "repo_only_framework_consolidation_preview_v1_latest.json"
)
PREVIEW_POST_CHECK_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_framework_consolidation_preview_v1_post_commit_check"
    / "repo_only_framework_consolidation_preview_post_commit_check_latest.json"
)
REQUIRED_PREVIEW_STATUS = "REPO_ONLY_FRAMEWORK_CONSOLIDATION_PREVIEW_V1_READY"
REQUIRED_PREVIEW_POST_CHECK_STATUS = "REPO_ONLY_FRAMEWORK_CONSOLIDATION_PREVIEW_POST_COMMIT_CHECK_PASS"
REQUIRED_PREVIEW_NEXT_MODULE = "edge_factory_os_repo_only_framework_consolidation_preview_evaluator_v1.py"

NEXT_ACTION = "BUILD_REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_CONTRACT_V1"
NEXT_MODULE = "edge_factory_os_repo_only_generic_governance_runner_contract_v1.py"

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

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_framework_consolidation_preview_evaluator_only": True,
    "repo_only_generic_runner_contract_recommended_next": True,
    "generic_runner_implementation_allowed_now": False,
    "consolidation_apply_allowed_now": False,
    "read_only_preview_evaluation_allowed": True,
    "read_only_validation_allowed": True,
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


def first_status(obj: Dict[str, Any]) -> Optional[str]:
    if isinstance(obj.get("framework_consolidation_preview_evaluator_status"), str):
        return obj["framework_consolidation_preview_evaluator_status"]
    if isinstance(obj.get("framework_consolidation_preview_status"), str):
        return obj["framework_consolidation_preview_status"]
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


def validate_preview_inputs(errors: List[str]) -> Dict[str, Any]:
    loaded: Dict[str, Any] = {}
    for key, path in {
        "framework_consolidation_preview": PREVIEW_JSON,
        "framework_consolidation_preview_post_check": PREVIEW_POST_CHECK_JSON,
    }.items():
        if not path.exists():
            errors.append(f"missing required preview evidence: {path}")
            continue
        try:
            loaded[key] = load_json(path)
        except Exception as exc:
            errors.append(f"unreadable preview evidence {path}: {exc!r}")

    preview = loaded.get("framework_consolidation_preview", {})
    post = loaded.get("framework_consolidation_preview_post_check", {})
    if preview:
        if preview.get("framework_consolidation_preview_status") != REQUIRED_PREVIEW_STATUS:
            errors.append(f"preview status mismatch: {preview.get('framework_consolidation_preview_status')}")
        if preview.get("next_module") != REQUIRED_PREVIEW_NEXT_MODULE:
            errors.append(f"preview next_module mismatch: {preview.get('next_module')}")
        if preview.get("critical_issue_count") != 0:
            errors.append(f"preview critical_issue_count not zero: {preview.get('critical_issue_count')}")
        if not isinstance(preview.get("framework_consolidation_preview"), dict):
            errors.append("preview payload missing framework_consolidation_preview object")
    if post:
        if post.get("audit_status") != REQUIRED_PREVIEW_POST_CHECK_STATUS:
            errors.append(f"preview post-check status mismatch: {post.get('audit_status')}")
        if post.get("latest_commit") != EXPECTED_HEAD:
            errors.append(f"preview post-check latest_commit mismatch: expected={EXPECTED_HEAD} actual={post.get('latest_commit')}")
        if post.get("next_module") != REQUIRED_PREVIEW_NEXT_MODULE:
            errors.append(f"preview post-check next_module mismatch: {post.get('next_module')}")
        if post.get("critical_issue_count") != 0:
            errors.append(f"preview post-check critical_issue_count not zero: {post.get('critical_issue_count')}")
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
    if tracked_python["tracked_python_file_count"] != 524:
        errors.append(f"tracked Python count mismatch before new file is tracked: expected=524 actual={tracked_python['tracked_python_file_count']}")

    preview_inputs = validate_preview_inputs(errors)
    preview_eval_errors = evaluate_preview_contract(preview_inputs.get("framework_consolidation_preview", {}))
    errors.extend(preview_eval_errors)

    physical_after = physical_guard_snapshot()
    if physical_after["planned_schema_file_existing_count"] != 0:
        errors.append(f"planned schema files existed after run: {physical_after['existing_planned_schema_files']}")

    return {
        "errors": errors,
        "git_state": git_state,
        "expected_untracked_during_run": expected_untracked,
        "tracked_python_validation": tracked_python,
        "preview_inputs": preview_inputs,
        "preview_evaluation_errors": preview_eval_errors,
        "physical_before": physical_before,
        "physical_after": physical_after,
    }


def source_preview(preview_payload: Dict[str, Any]) -> Dict[str, Any]:
    preview = preview_payload.get("framework_consolidation_preview", {}) if isinstance(preview_payload, dict) else {}
    return preview if isinstance(preview, dict) else {}


def bool_false(value: Any) -> bool:
    return value is False


def evaluate_preview_contract(preview_payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    preview = source_preview(preview_payload)
    if not preview:
        return ["preview object missing for evaluation"]

    required_sections = [
        "preview_status",
        "contract_inputs_verified",
        "proposed_generic_runner_preview",
        "config_state_table_preview",
        "transition_policy_preview",
        "expected_output_schema_preview",
        "physical_guard_preview",
        "safety_flag_preview",
        "acceptance_test_preview",
        "non_goals",
        "blocked_actions",
    ]
    for section in required_sections:
        if section not in preview:
            errors.append(f"preview missing required section: {section}")

    if preview.get("preview_status") != "PREVIEW_ONLY_GENERIC_RUNNER_DESIGN_SIMULATED_NO_IMPLEMENTATION":
        errors.append(f"preview_status not simulation-only: {preview.get('preview_status')}")

    runner = preview.get("proposed_generic_runner_preview", {})
    if not isinstance(runner, dict) or runner.get("runner_not_implemented") is not True:
        errors.append("proposed_generic_runner_preview does not prove runner_not_implemented true")
    if isinstance(runner, dict) and runner.get("mode") != "preview_simulation_only":
        errors.append(f"generic runner preview mode is not preview_simulation_only: {runner.get('mode')}")

    states = preview.get("config_state_table_preview", [])
    if not isinstance(states, list) or len(states) < 4:
        errors.append("config_state_table_preview has fewer than 4 states")
    for state in states if isinstance(states, list) else []:
        if not isinstance(state, dict):
            errors.append("config_state_table_preview contains a non-object state")
            continue
        if state.get("apply_allowed") is not False:
            errors.append(f"state permits apply: {state.get('state_id')}")

    expected_schema = preview.get("expected_output_schema_preview", {})
    if not isinstance(expected_schema, dict):
        errors.append("expected_output_schema_preview is not an object")
    else:
        if expected_schema.get("next_module") != REQUIRED_PREVIEW_NEXT_MODULE:
            errors.append(f"expected_output_schema_preview next_module mismatch: {expected_schema.get('next_module')}")
        if expected_schema.get("schema_file_created") is not False:
            errors.append("expected_output_schema_preview permits schema file creation")

    guard = preview.get("physical_guard_preview", {})
    required_guard_false = [
        "runtime_touch_performed",
        "launcher_executed",
        "capital_change_performed",
        "live_or_real_order_performed",
        "holdout_access_performed",
        "file_move_performed",
        "file_delete_performed",
        "repo_restructure_performed",
    ]
    if not isinstance(guard, dict):
        errors.append("physical_guard_preview is not an object")
    else:
        if guard.get("planned_schema_file_existing_count") != 0:
            errors.append(f"physical_guard_preview planned schema count not zero: {guard.get('planned_schema_file_existing_count')}")
        for key in required_guard_false:
            if guard.get(key) is not False:
                errors.append(f"physical_guard_preview {key} is not false: {guard.get(key)}")

    flag_preview = preview.get("safety_flag_preview", {})
    if not isinstance(flag_preview, dict):
        errors.append("safety_flag_preview is not an object")
    else:
        for flag in DANGEROUS_FLAGS:
            if flag_preview.get(flag) is not False:
                errors.append(f"safety_flag_preview dangerous flag is not false: {flag}={flag_preview.get(flag)}")

    blocked_text = " ".join(str(item).lower() for item in preview.get("blocked_actions", []))
    non_goal_text = " ".join(str(item).lower() for item in preview.get("non_goals", []))
    must_block_terms = [
        "implement generic runner",
        "apply consolidation",
        "create schema",
        "edit schemas",
        "touch runtime",
        "execute launcher",
        "access holdout",
        "generate candidates",
    ]
    for term in must_block_terms:
        if term not in blocked_text and term not in non_goal_text:
            errors.append(f"preview does not block/non-goal required term: {term}")

    return errors


def build_evaluation(preview_payload: Dict[str, Any], validation: Dict[str, Any]) -> Dict[str, Any]:
    preview = source_preview(preview_payload)
    errors = evaluate_preview_contract(preview_payload)
    ready = not errors
    return {
        "preview_status": preview.get("preview_status"),
        "contract_inputs_verified": preview.get("contract_inputs_verified"),
        "proposed_generic_runner_preview": {
            "target_name": preview.get("proposed_generic_runner_preview", {}).get("target_name")
            if isinstance(preview.get("proposed_generic_runner_preview"), dict)
            else None,
            "runner_not_implemented": preview.get("proposed_generic_runner_preview", {}).get("runner_not_implemented")
            if isinstance(preview.get("proposed_generic_runner_preview"), dict)
            else None,
            "mode": preview.get("proposed_generic_runner_preview", {}).get("mode")
            if isinstance(preview.get("proposed_generic_runner_preview"), dict)
            else None,
        },
        "config_state_table_preview": {
            "state_count": len(preview.get("config_state_table_preview", []))
            if isinstance(preview.get("config_state_table_preview"), list)
            else 0,
            "all_states_apply_allowed_false": all(
                isinstance(state, dict) and state.get("apply_allowed") is False
                for state in preview.get("config_state_table_preview", [])
            )
            if isinstance(preview.get("config_state_table_preview"), list)
            else False,
        },
        "transition_policy_preview": preview.get("transition_policy_preview"),
        "expected_output_schema_preview": preview.get("expected_output_schema_preview"),
        "physical_guard_preview": preview.get("physical_guard_preview"),
        "safety_flag_preview": preview.get("safety_flag_preview"),
        "acceptance_test_preview": preview.get("acceptance_test_preview"),
        "non_goals": preview.get("non_goals"),
        "blocked_actions": preview.get("blocked_actions"),
        "evaluation_errors": errors,
        "ready_for_future_generic_runner_contract": ready,
        "decision_basis": [
            "preview is simulation-only and does not implement generic runner",
            "config state table keeps apply disallowed",
            "dangerous safety flags are false",
            "physical guards remain no-touch/no-apply",
            "blocked actions and non-goals explicitly prevent implementation/apply/schema/runtime work",
        ]
        if ready
        else [],
        "recommended_next_module": NEXT_MODULE if ready else None,
    }


def build_payload(validation: Dict[str, Any]) -> Dict[str, Any]:
    errors = list(validation["errors"])
    safety_type_errors = [key for key, value in SAFETY_FLAGS.items() if not isinstance(value, bool)]
    if safety_type_errors:
        errors.append(f"safety flags are not boolean: {safety_type_errors}")
    dangerous_true = [key for key in DANGEROUS_FLAGS if SAFETY_FLAGS.get(key) is not False]
    if dangerous_true:
        errors.append(f"dangerous flags are not explicitly false: {dangerous_true}")

    preview_payload = validation["preview_inputs"].get("framework_consolidation_preview", {})
    evaluation = build_evaluation(preview_payload, validation)
    passed = not errors and evaluation["ready_for_future_generic_runner_contract"]

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "framework_consolidation_preview_evaluator_status": "REPO_ONLY_FRAMEWORK_CONSOLIDATION_PREVIEW_EVALUATOR_V1_READY" if passed else "BLOCKED",
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": "PREVIEW_EVALUATED_READY_FOR_GENERIC_RUNNER_CONTRACT" if passed else "BLOCKED_REVIEW_FRAMEWORK_CONSOLIDATION_PREVIEW_EVALUATION",
        "next_action": NEXT_ACTION if passed else "REVIEW_FRAMEWORK_CONSOLIDATION_PREVIEW_EVALUATOR_ERRORS",
        "next_module": NEXT_MODULE if passed else None,
        "reason": "Preview evaluator confirms the repo-only preview is ready for a future generic governance runner contract/design module." if passed else "Preview evaluator failed closed because required evidence or safety constraints were missing.",
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "lab_root": str(LAB_ROOT),
        "critical_issue_count": len(errors) + (0 if evaluation["ready_for_future_generic_runner_contract"] else 1),
        "warning_count": 0,
        "errors": errors + ([] if evaluation["ready_for_future_generic_runner_contract"] else ["preview evaluation did not pass"]),
        "warnings": [],
        "framework_consolidation_preview_evaluation": evaluation,
        "validation": {
            "git_state": validation["git_state"],
            "expected_untracked_during_run": validation["expected_untracked_during_run"],
            "tracked_python_validation": validation["tracked_python_validation"],
            "preview_inputs": {
                key: {
                    "status": first_status(value),
                    "critical_issue_count": value.get("critical_issue_count"),
                    "next_module": value.get("next_module"),
                    "latest_commit": value.get("latest_commit"),
                    "final_decision": value.get("final_decision"),
                }
                for key, value in validation["preview_inputs"].items()
            },
            "preview_evaluation_errors": validation["preview_evaluation_errors"],
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
    for flag in DANGEROUS_FLAGS:
        payload[flag] = False
    return payload


def write_outputs(payload: Dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_framework_consolidation_preview_evaluator_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_framework_consolidation_preview_evaluator_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_framework_consolidation_preview_evaluator_v1_latest.txt"
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
