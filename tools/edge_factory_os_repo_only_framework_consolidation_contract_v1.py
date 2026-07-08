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

MODULE_NAME = "edge_factory_os_repo_only_framework_consolidation_contract_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_framework_consolidation_contract_v1.py"
EXPECTED_HEAD = "274952b"
OUT_DIR = LAB_ROOT / MODULE_NAME

PLAN_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_framework_consolidation_plan_v1"
    / "repo_only_framework_consolidation_plan_v1_latest.json"
)
PLAN_POST_CHECK_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_framework_consolidation_plan_v1_post_commit_check"
    / "repo_only_framework_consolidation_plan_post_commit_check_latest.json"
)
REQUIRED_PLAN_STATUS = "REPO_ONLY_FRAMEWORK_CONSOLIDATION_PLAN_V1_READY"
REQUIRED_PLAN_POST_CHECK_STATUS = "REPO_ONLY_FRAMEWORK_CONSOLIDATION_PLAN_POST_COMMIT_CHECK_PASS"
REQUIRED_PLAN_NEXT_MODULE = "edge_factory_os_repo_only_framework_consolidation_contract_v1.py"

NEXT_ACTION = "BUILD_REPO_ONLY_FRAMEWORK_CONSOLIDATION_PREVIEW_V1"
NEXT_MODULE = "edge_factory_os_repo_only_framework_consolidation_preview_v1.py"
GENERIC_RUNNER_TARGET_NAME = "edge_factory_os_repo_only_framework_governance_runner_v1.py"

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
    "repo_only_framework_consolidation_contract_only": True,
    "repo_only_preview_module_recommended_next": True,
    "generic_runner_implementation_allowed_now": False,
    "consolidation_apply_allowed_now": False,
    "read_only_plan_conversion_allowed": True,
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
    if isinstance(obj.get("framework_consolidation_contract_status"), str):
        return obj["framework_consolidation_contract_status"]
    if isinstance(obj.get("framework_consolidation_plan_status"), str):
        return obj["framework_consolidation_plan_status"]
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


def validate_plan_inputs(errors: List[str]) -> Dict[str, Any]:
    loaded: Dict[str, Any] = {}
    for key, path in {
        "framework_consolidation_plan": PLAN_JSON,
        "framework_consolidation_plan_post_check": PLAN_POST_CHECK_JSON,
    }.items():
        if not path.exists():
            errors.append(f"missing required plan evidence: {path}")
            continue
        try:
            loaded[key] = load_json(path)
        except Exception as exc:
            errors.append(f"unreadable plan evidence {path}: {exc!r}")

    plan = loaded.get("framework_consolidation_plan", {})
    post = loaded.get("framework_consolidation_plan_post_check", {})
    if plan:
        if plan.get("framework_consolidation_plan_status") != REQUIRED_PLAN_STATUS:
            errors.append(f"plan status mismatch: {plan.get('framework_consolidation_plan_status')}")
        if plan.get("next_module") != REQUIRED_PLAN_NEXT_MODULE:
            errors.append(f"plan next_module mismatch: {plan.get('next_module')}")
        if plan.get("critical_issue_count") != 0:
            errors.append(f"plan critical_issue_count not zero: {plan.get('critical_issue_count')}")
        if not isinstance(plan.get("framework_consolidation_plan"), dict):
            errors.append("plan payload missing framework_consolidation_plan object")
    if post:
        if post.get("audit_status") != REQUIRED_PLAN_POST_CHECK_STATUS:
            errors.append(f"plan post-check status mismatch: {post.get('audit_status')}")
        if post.get("latest_commit") != EXPECTED_HEAD:
            errors.append(f"plan post-check latest_commit mismatch: expected={EXPECTED_HEAD} actual={post.get('latest_commit')}")
        if post.get("next_module") != REQUIRED_PLAN_NEXT_MODULE:
            errors.append(f"plan post-check next_module mismatch: {post.get('next_module')}")
        if post.get("critical_issue_count") != 0:
            errors.append(f"plan post-check critical_issue_count not zero: {post.get('critical_issue_count')}")
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
    if tracked_python["tracked_python_file_count"] != 522:
        errors.append(f"tracked Python count mismatch before new file is tracked: expected=522 actual={tracked_python['tracked_python_file_count']}")

    plan_inputs = validate_plan_inputs(errors)

    physical_after = physical_guard_snapshot()
    if physical_after["planned_schema_file_existing_count"] != 0:
        errors.append(f"planned schema files existed after run: {physical_after['existing_planned_schema_files']}")

    return {
        "errors": errors,
        "git_state": git_state,
        "expected_untracked_during_run": expected_untracked,
        "tracked_python_validation": tracked_python,
        "plan_inputs": plan_inputs,
        "physical_before": physical_before,
        "physical_after": physical_after,
    }


def source_plan(validation: Dict[str, Any]) -> Dict[str, Any]:
    return validation["plan_inputs"].get("framework_consolidation_plan", {})


def source_plan_commit(validation: Dict[str, Any]) -> Optional[str]:
    return validation["plan_inputs"].get("framework_consolidation_plan_post_check", {}).get("latest_commit")


def build_contract(validation: Dict[str, Any]) -> Dict[str, Any]:
    plan_payload = source_plan(validation)
    plan = plan_payload.get("framework_consolidation_plan", {}) if isinstance(plan_payload, dict) else {}
    proposed_flow = plan.get("proposed_config_driven_flow", {}) if isinstance(plan, dict) else {}
    proposed_design = plan.get("proposed_generic_runner_design", {}) if isinstance(plan, dict) else {}
    blocked_actions = plan.get("blocked_actions", []) if isinstance(plan, dict) else []
    future_gates = plan.get("required_future_approval_gates", []) if isinstance(plan, dict) else []

    return {
        "contract_id": "REPO_ONLY_FRAMEWORK_CONSOLIDATION_CONTRACT_V1",
        "contract_status": "CONTRACT_READY_PLAN_ONLY_NO_APPLY",
        "source_plan_module": "edge_factory_os_repo_only_framework_consolidation_plan_v1.py",
        "source_plan_commit": source_plan_commit(validation),
        "generic_runner_target_name": GENERIC_RUNNER_TARGET_NAME,
        "config_driven_flow_requirements": {
            "configuration_shape": proposed_flow.get("configuration_shape", {}),
            "transition_policy": proposed_flow.get("transition_policy", []),
            "required_state_model": [
                "represent selector, queue, backlog, plan, contract, and preview steps as config states",
                "keep transition decisions in data rather than encoding accumulated context in file names",
                "require every state to declare expected inputs, guard checks, allowed next action, and blocked actions",
            ],
            "generic_runner_requirements": proposed_design.get("core_components", []),
            "generic_runner_output_contract": proposed_design.get("output_contract", []),
        },
        "required_inputs": [
            {
                "name": "latest_approved_plan_json",
                "path": str(PLAN_JSON),
                "required_status": REQUIRED_PLAN_STATUS,
                "required_next_module": REQUIRED_PLAN_NEXT_MODULE,
                "required_critical_issue_count": 0,
            },
            {
                "name": "latest_plan_post_commit_check_json",
                "path": str(PLAN_POST_CHECK_JSON),
                "required_status": REQUIRED_PLAN_POST_CHECK_STATUS,
                "required_latest_commit": EXPECTED_HEAD,
                "required_next_module": REQUIRED_PLAN_NEXT_MODULE,
                "required_critical_issue_count": 0,
            },
            {
                "name": "repo_git_state",
                "required_head": EXPECTED_HEAD,
                "required_dirty_tracked_count": 0,
                "allowed_untracked_during_run": [CURRENT_TOOL_REL],
            },
            {
                "name": "tracked_python_validation",
                "required_tracked_python_file_count_before_contract_commit": 522,
                "required_syntax_error_count": 0,
                "required_bom_error_count": 0,
            },
        ],
        "required_outputs": [
            "framework_consolidation_contract_status",
            "final_decision",
            "next_action",
            "next_module",
            "critical_issue_count",
            "framework_consolidation_contract",
            "validation",
            "physical_guards",
            "safety_flags",
        ],
        "required_physical_guards": {
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
        "required_safety_flags": {flag: False for flag in DANGEROUS_FLAGS},
        "allowed_actions": [
            "read approved framework consolidation plan JSON",
            "read approved framework consolidation plan post-check JSON",
            "read recent repo-only governance evidence if needed by future preview",
            "write contract JSON/TXT outputs",
            "recommend repo-only preview/design module next",
        ],
        "blocked_actions": blocked_actions
        + [
            "implement generic runner now",
            "apply consolidation now",
            "modify existing framework files now",
            "create or edit schemas now",
            "delete or move old modules now",
        ],
        "future_approval_gates": future_gates
        + [
            "explicit approval before preview can become implementation",
            "explicit approval before the generic runner is created",
            "explicit approval before any one-off module cleanup, deletion, move, or restructure",
        ],
        "acceptance_tests": [
            "contract module exits zero only when plan JSON and plan post-check JSON both pass",
            "contract output status is REPO_ONLY_FRAMEWORK_CONSOLIDATION_CONTRACT_V1_READY",
            "contract output next_module is edge_factory_os_repo_only_framework_consolidation_preview_v1.py",
            "all dangerous flags are present and false at top level and under safety_flags",
            "physical guards show planned schema files absent before and after",
            "tracked Python syntax and BOM validation is clean",
            "repo status during run contains no tracked changes and only this contract file as untracked",
        ],
        "fail_closed_conditions": [
            "HEAD is not 274952b",
            "repo has dirty tracked files",
            "repo has unexpected untracked files",
            "contract target file was not the only untracked file during execution",
            "plan JSON is missing, unreadable, non-ready, or has critical issues",
            "plan post-check JSON is missing, unreadable, non-pass, wrong commit, or has critical issues",
            "plan next_module is not edge_factory_os_repo_only_framework_consolidation_contract_v1.py",
            "tracked Python syntax or BOM validation fails",
            "planned schema files exist before or after",
            "any dangerous safety flag is not explicitly false",
        ],
        "migration_non_goals": [
            "do not implement the generic runner in this contract",
            "do not apply consolidation",
            "do not modify existing framework files",
            "do not delete, move, or rewrite old selector, queue, or backlog modules",
            "do not create, edit, or apply schema files",
            "do not run strategy research, access holdout, generate candidates, or touch runtime",
        ],
    }


def build_payload(validation: Dict[str, Any]) -> Dict[str, Any]:
    errors = list(validation["errors"])
    safety_type_errors = [key for key, value in SAFETY_FLAGS.items() if not isinstance(value, bool)]
    if safety_type_errors:
        errors.append(f"safety flags are not boolean: {safety_type_errors}")
    dangerous_true = [key for key in DANGEROUS_FLAGS if SAFETY_FLAGS.get(key) is not False]
    if dangerous_true:
        errors.append(f"dangerous flags are not explicitly false: {dangerous_true}")

    passed = not errors
    contract = build_contract(validation)
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "framework_consolidation_contract_status": "REPO_ONLY_FRAMEWORK_CONSOLIDATION_CONTRACT_V1_READY" if passed else "BLOCKED",
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": "FRAMEWORK_CONSOLIDATION_CONTRACT_READY_FOR_PREVIEW" if passed else "BLOCKED_REVIEW_FRAMEWORK_CONSOLIDATION_CONTRACT_EVIDENCE",
        "next_action": NEXT_ACTION if passed else "REVIEW_FRAMEWORK_CONSOLIDATION_CONTRACT_ERRORS",
        "next_module": NEXT_MODULE if passed else None,
        "reason": "Contract-only consolidation route is ready for a repo-only preview/design module." if passed else "Framework consolidation contract failed closed because required evidence or guard checks were missing.",
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "lab_root": str(LAB_ROOT),
        "critical_issue_count": len(errors),
        "warning_count": 0,
        "errors": errors,
        "warnings": [],
        "validation": {
            "git_state": validation["git_state"],
            "expected_untracked_during_run": validation["expected_untracked_during_run"],
            "tracked_python_validation": validation["tracked_python_validation"],
            "plan_inputs": {
                key: {
                    "status": first_status(value),
                    "critical_issue_count": value.get("critical_issue_count"),
                    "next_module": value.get("next_module"),
                    "latest_commit": value.get("latest_commit"),
                    "final_decision": value.get("final_decision"),
                }
                for key, value in validation["plan_inputs"].items()
            },
            "physical_before": validation["physical_before"],
            "physical_after": validation["physical_after"],
        },
        "framework_consolidation_contract": contract,
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
    latest_json = OUT_DIR / "repo_only_framework_consolidation_contract_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_framework_consolidation_contract_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_framework_consolidation_contract_v1_latest.txt"
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
