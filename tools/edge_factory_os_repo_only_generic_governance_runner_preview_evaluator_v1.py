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

MODULE_NAME = "edge_factory_os_repo_only_generic_governance_runner_preview_evaluator_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_generic_governance_runner_preview_evaluator_v1.py"
EXPECTED_HEAD = "7d52c40"
OUT_DIR = LAB_ROOT / MODULE_NAME

PREVIEW_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_generic_governance_runner_preview_v1"
    / "repo_only_generic_governance_runner_preview_v1_latest.json"
)
PREVIEW_POST_CHECK_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_generic_governance_runner_preview_v1_post_commit_check"
    / "repo_only_generic_governance_runner_preview_post_commit_check_latest.json"
)
REQUIRED_PREVIEW_STATUS = "REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_PREVIEW_V1_READY"
REQUIRED_PREVIEW_POST_CHECK_STATUS = "REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_PREVIEW_POST_COMMIT_CHECK_PASS"
REQUIRED_PREVIEW_NEXT_MODULE = "edge_factory_os_repo_only_generic_governance_runner_preview_evaluator_v1.py"

NEXT_ACTION = "BUILD_REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION_CONTRACT_V1"
NEXT_MODULE = "edge_factory_os_repo_only_generic_governance_runner_implementation_contract_v1.py"

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
    "repo_only_generic_governance_runner_preview_evaluator_only": True,
    "repo_only_generic_runner_implementation_contract_recommended_next": True,
    "read_only_preview_evaluation_allowed": True,
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
    if isinstance(obj.get("generic_governance_runner_preview_evaluator_status"), str):
        return obj["generic_governance_runner_preview_evaluator_status"]
    if isinstance(obj.get("generic_governance_runner_preview_status"), str):
        return obj["generic_governance_runner_preview_status"]
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


def preview_object(payload: Dict[str, Any]) -> Dict[str, Any]:
    preview = payload.get("generic_governance_runner_preview", {}) if isinstance(payload, dict) else {}
    return preview if isinstance(preview, dict) else {}


def evaluate_preview_safety(preview: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    required_sections = [
        "generic_governance_runner_preview_status",
        "contract_inputs_verified",
        "simulated_runner_design",
        "config_state_table_preview",
        "transition_engine_preview",
        "input_validation_preview",
        "output_contract_preview",
        "physical_guard_preview",
        "safety_flag_preview",
        "blocked_actions",
        "non_goals",
        "acceptance_test_preview",
    ]
    for section in required_sections:
        if section not in preview:
            errors.append(f"preview missing required section: {section}")

    design = preview.get("simulated_runner_design", {})
    if not isinstance(design, dict):
        errors.append("simulated_runner_design missing")
    else:
        if design.get("generic_runner_is_implemented") is not False:
            errors.append("generic runner appears implemented")
        if design.get("generic_runner_implementation_allowed_now") is not False:
            errors.append("generic runner implementation allowed")
        if design.get("config_files_created") is not False:
            errors.append("config files appear created")
        if design.get("config_file_creation_allowed_now") is not False:
            errors.append("config file creation allowed")

    states = preview.get("config_state_table_preview", [])
    if not isinstance(states, list) or len(states) < 4:
        errors.append("config_state_table_preview has fewer than 4 states")
    else:
        for state in states:
            if not isinstance(state, dict):
                errors.append("config_state_table_preview contains non-object state")
            elif state.get("apply_allowed") is not False:
                errors.append(f"state permits apply: {state.get('state_id')}")

    engine = preview.get("transition_engine_preview", {})
    if not isinstance(engine, dict):
        errors.append("transition_engine_preview missing")
    else:
        if engine.get("engine_is_implemented") is not False:
            errors.append("transition engine appears implemented")
        if engine.get("engine_mode") != "simulation_only":
            errors.append(f"transition engine mode not simulation_only: {engine.get('engine_mode')}")
        if engine.get("all_states_apply_allowed_false") is not True:
            errors.append("transition engine does not prove all states apply false")

    output_contract = preview.get("output_contract_preview", {})
    if not isinstance(output_contract, dict):
        errors.append("output_contract_preview missing")
    else:
        if output_contract.get("next_module") != REQUIRED_PREVIEW_NEXT_MODULE:
            errors.append(f"output contract next_module mismatch: {output_contract.get('next_module')}")
        if output_contract.get("critical_issue_count_required") != 0:
            errors.append("output contract critical_issue_count_required not zero")

    physical = preview.get("physical_guard_preview", {})
    if not isinstance(physical, dict):
        errors.append("physical_guard_preview missing")
    else:
        if physical.get("planned_schema_file_existing_count") != 0:
            errors.append(f"physical preview planned schema count not zero: {physical.get('planned_schema_file_existing_count')}")
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
                errors.append(f"physical guard {key} not false: {physical.get(key)}")

    flags = preview.get("safety_flag_preview", {})
    if not isinstance(flags, dict):
        errors.append("safety_flag_preview missing")
    else:
        for flag in DANGEROUS_FLAGS + EXTRA_FALSE_FLAGS:
            if flags.get(flag) is not False:
                errors.append(f"safety flag preview not false: {flag}={flags.get(flag)}")

    combined_text = " ".join(
        str(item).lower()
        for item in (preview.get("blocked_actions", []) or []) + (preview.get("non_goals", []) or [])
    )
    for term in [
        "implement generic runner",
        "create config files",
        "apply consolidation",
        "create schema",
        "edit",
        "apply schema",
        "touch runtime",
        "launcher",
        "holdout",
        "generate candidates",
        "capital",
        "live",
        "real orders",
    ]:
        if term not in combined_text:
            errors.append(f"preview does not block/non-goal required term: {term}")

    return errors


def validate_preview_inputs(errors: List[str]) -> Dict[str, Any]:
    loaded: Dict[str, Any] = {}
    for key, path in {
        "generic_governance_runner_preview": PREVIEW_JSON,
        "generic_governance_runner_preview_post_check": PREVIEW_POST_CHECK_JSON,
    }.items():
        if not path.exists():
            errors.append(f"missing required preview evidence: {path}")
            continue
        try:
            loaded[key] = load_json(path)
        except Exception as exc:
            errors.append(f"unreadable preview evidence {path}: {exc!r}")

    preview_payload = loaded.get("generic_governance_runner_preview", {})
    post = loaded.get("generic_governance_runner_preview_post_check", {})
    if preview_payload:
        if preview_payload.get("generic_governance_runner_preview_status") != REQUIRED_PREVIEW_STATUS:
            errors.append(f"preview status mismatch: {preview_payload.get('generic_governance_runner_preview_status')}")
        if preview_payload.get("next_module") != REQUIRED_PREVIEW_NEXT_MODULE:
            errors.append(f"preview next_module mismatch: {preview_payload.get('next_module')}")
        if preview_payload.get("critical_issue_count") != 0:
            errors.append(f"preview critical_issue_count not zero: {preview_payload.get('critical_issue_count')}")
        preview = preview_object(preview_payload)
        if not preview:
            errors.append("preview payload missing generic_governance_runner_preview object")
        else:
            errors.extend(evaluate_preview_safety(preview))
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
    if tracked_python["tracked_python_file_count"] != 527:
        errors.append(f"tracked Python count mismatch before new file is tracked: expected=527 actual={tracked_python['tracked_python_file_count']}")

    preview_inputs = validate_preview_inputs(errors)

    physical_after = physical_guard_snapshot()
    if physical_after["planned_schema_file_existing_count"] != 0:
        errors.append(f"planned schema files existed after run: {physical_after['existing_planned_schema_files']}")

    return {
        "errors": errors,
        "git_state": git_state,
        "expected_untracked_during_run": expected_untracked,
        "tracked_python_validation": tracked_python,
        "preview_inputs": preview_inputs,
        "physical_before": physical_before,
        "physical_after": physical_after,
    }


def source_preview(validation: Dict[str, Any]) -> Dict[str, Any]:
    payload = validation["preview_inputs"].get("generic_governance_runner_preview", {})
    return preview_object(payload)


def build_evaluation(validation: Dict[str, Any]) -> Dict[str, Any]:
    preview = source_preview(validation)
    errors = evaluate_preview_safety(preview) if preview else ["preview object missing"]
    ready = not errors
    design = preview.get("simulated_runner_design", {}) if isinstance(preview, dict) else {}
    engine = preview.get("transition_engine_preview", {}) if isinstance(preview, dict) else {}
    states = preview.get("config_state_table_preview", []) if isinstance(preview, dict) else []
    return {
        "generic_governance_runner_preview_status": preview.get("generic_governance_runner_preview_status"),
        "contract_inputs_verified": preview.get("contract_inputs_verified"),
        "simulated_runner_design": {
            "generic_runner_is_implemented": design.get("generic_runner_is_implemented"),
            "generic_runner_implementation_allowed_now": design.get("generic_runner_implementation_allowed_now"),
            "config_files_created": design.get("config_files_created"),
            "config_file_creation_allowed_now": design.get("config_file_creation_allowed_now"),
            "target_name": design.get("target_name"),
        },
        "config_state_table_preview": {
            "state_count": len(states) if isinstance(states, list) else 0,
            "all_states_apply_allowed_false": all(
                isinstance(state, dict) and state.get("apply_allowed") is False
                for state in states
            )
            if isinstance(states, list)
            else False,
        },
        "transition_engine_preview": engine,
        "input_validation_preview": preview.get("input_validation_preview"),
        "output_contract_preview": preview.get("output_contract_preview"),
        "physical_guard_preview": preview.get("physical_guard_preview"),
        "safety_flag_preview": preview.get("safety_flag_preview"),
        "blocked_actions": preview.get("blocked_actions"),
        "non_goals": preview.get("non_goals"),
        "acceptance_test_preview": preview.get("acceptance_test_preview"),
        "evaluation_errors": errors,
        "ready_for_implementation_contract": ready,
        "decision_basis": [
            "preview proves generic runner is not implemented",
            "preview proves config files are not created",
            "preview proves apply is not allowed across config states",
            "preview blocks schema creation, editing, and apply",
            "preview blocks runtime, launcher, holdout, candidate, capital, live, and order actions",
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
    for flag in DANGEROUS_FLAGS + EXTRA_FALSE_FLAGS:
        if SAFETY_FLAGS.get(flag) is not False:
            errors.append(f"safety flag is not explicitly false: {flag}={SAFETY_FLAGS.get(flag)}")

    evaluation = build_evaluation(validation)
    passed = not errors and evaluation["ready_for_implementation_contract"]
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "generic_governance_runner_preview_evaluator_status": "REPO_ONLY_GENERIC_GOVERNANCE_RUNNER_PREVIEW_EVALUATOR_V1_READY" if passed else "BLOCKED",
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": "GENERIC_GOVERNANCE_RUNNER_PREVIEW_EVALUATED_READY_FOR_IMPLEMENTATION_CONTRACT" if passed else "BLOCKED_REVIEW_GENERIC_GOVERNANCE_RUNNER_PREVIEW_EVALUATION",
        "next_action": NEXT_ACTION if passed else "REVIEW_GENERIC_GOVERNANCE_RUNNER_PREVIEW_EVALUATOR_ERRORS",
        "next_module": NEXT_MODULE if passed else None,
        "reason": "Generic governance runner preview evaluator confirms the design is ready for a future repo-only implementation contract; implementation and apply remain blocked." if passed else "Generic governance runner preview evaluator failed closed because evidence or safety constraints were missing.",
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "lab_root": str(LAB_ROOT),
        "critical_issue_count": len(errors) + (0 if evaluation["ready_for_implementation_contract"] else 1),
        "warning_count": 0,
        "errors": errors + ([] if evaluation["ready_for_implementation_contract"] else ["preview evaluation did not pass"]),
        "warnings": [],
        "generic_governance_runner_preview_evaluation": evaluation,
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
    latest_json = OUT_DIR / "repo_only_generic_governance_runner_preview_evaluator_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_generic_governance_runner_preview_evaluator_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_generic_governance_runner_preview_evaluator_v1_latest.txt"
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
