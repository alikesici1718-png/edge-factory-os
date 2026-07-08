from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_autopilot_until_research_gate_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_autopilot_until_research_gate_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD = "3174c9d"
EXPECTED_NEXT_MODULE = "edge_factory_os_repo_only_development_queue_selector_after_standard_os_status_backlog_status_backlog_refresh_v1.py"

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

INPUTS: Dict[str, Tuple[Path, str, Optional[str]]] = {
    "standard_os_status": (
        LAB_ROOT
        / "edge_factory_os_repo_only_standard_os_status_refresh_after_standard_os_status_backlog_refresh_v1"
        / "repo_only_standard_os_status_refresh_after_standard_os_status_backlog_refresh_v1_latest.json",
        "REPO_ONLY_STANDARD_OS_STATUS_REFRESH_AFTER_STANDARD_OS_STATUS_BACKLOG_REFRESH_V1_READY",
        "edge_factory_os_repo_only_next_action_selector_after_standard_os_status_backlog_status_refresh_v1.py",
    ),
    "standard_os_status_post_check": (
        LAB_ROOT
        / "edge_factory_os_repo_only_standard_os_status_refresh_after_standard_os_status_backlog_refresh_post_commit_check"
        / "repo_only_standard_os_status_refresh_after_standard_os_status_backlog_refresh_post_commit_check_latest.json",
        "REPO_ONLY_STANDARD_OS_STATUS_REFRESH_AFTER_STANDARD_OS_STATUS_BACKLOG_REFRESH_POST_COMMIT_CHECK_PASS",
        "edge_factory_os_repo_only_next_action_selector_after_standard_os_status_backlog_status_refresh_v1.py",
    ),
    "development_queue_selector": (
        LAB_ROOT
        / "edge_factory_os_repo_only_development_queue_selector_after_standard_os_status_backlog_status_refresh_v1"
        / "repo_only_development_queue_selector_after_standard_os_status_backlog_status_refresh_v1_latest.json",
        "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_REFRESH_V1_READY",
        "edge_factory_os_repo_only_development_backlog_refresh_after_standard_os_status_backlog_status_refresh_v1.py",
    ),
    "development_queue_selector_post_check": (
        LAB_ROOT
        / "edge_factory_os_repo_only_development_queue_selector_after_standard_os_status_backlog_status_refresh_post_commit_check"
        / "repo_only_development_queue_selector_after_standard_os_status_backlog_status_refresh_post_commit_check_latest.json",
        "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_REFRESH_POST_COMMIT_CHECK_PASS",
        "edge_factory_os_repo_only_development_backlog_refresh_after_standard_os_status_backlog_status_refresh_v1.py",
    ),
    "development_backlog": (
        LAB_ROOT
        / "edge_factory_os_repo_only_development_backlog_refresh_after_standard_os_status_backlog_status_refresh_v1"
        / "repo_only_development_backlog_refresh_after_standard_os_status_backlog_status_refresh_v1_latest.json",
        "REPO_ONLY_DEVELOPMENT_BACKLOG_REFRESH_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_REFRESH_V1_READY",
        "edge_factory_os_repo_only_next_action_selector_after_standard_os_status_backlog_status_backlog_refresh_v1.py",
    ),
    "development_backlog_post_check": (
        LAB_ROOT
        / "edge_factory_os_repo_only_development_backlog_refresh_after_standard_os_status_backlog_status_refresh_post_commit_check"
        / "repo_only_development_backlog_refresh_after_standard_os_status_backlog_status_refresh_post_commit_check_latest.json",
        "REPO_ONLY_DEVELOPMENT_BACKLOG_REFRESH_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_REFRESH_POST_COMMIT_CHECK_PASS",
        "edge_factory_os_repo_only_next_action_selector_after_standard_os_status_backlog_status_backlog_refresh_v1.py",
    ),
    "next_action_selector": (
        LAB_ROOT
        / "edge_factory_os_repo_only_next_action_selector_after_standard_os_status_backlog_status_backlog_refresh_v1"
        / "repo_only_next_action_selector_after_standard_os_status_backlog_status_backlog_refresh_v1_latest.json",
        "REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_V1_READY",
        EXPECTED_NEXT_MODULE,
    ),
    "next_action_selector_post_check": (
        LAB_ROOT
        / "edge_factory_os_repo_only_next_action_selector_after_standard_os_status_backlog_status_backlog_refresh_post_commit_check"
        / "repo_only_next_action_selector_after_standard_os_status_backlog_status_backlog_refresh_post_commit_check_latest.json",
        "REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_POST_COMMIT_CHECK_PASS",
        EXPECTED_NEXT_MODULE,
    ),
}

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

SAFETY_FLAGS: Dict[str, bool] = {name: False for name in DANGEROUS_FLAGS}
SAFETY_FLAGS.update(
    {
        "repo_only_governance_audit": True,
        "read_only_input_inspection_only": True,
        "autopilot_plan_output_only": True,
        "next_module_execution_allowed": False,
        "next_module_executed": False,
        "next_module_generation_allowed": False,
        "next_module_generated": False,
    }
)

BLOCKED_SCOPE_TERMS = [
    "research",
    "strategy",
    "candidate",
    "runtime",
    "capital",
    "live",
    "holdout",
    "schema_apply",
    "schema_create",
    "schema_creation",
    "schema_edit",
    "schema_registry_apply",
    "family_release",
    "candidate_release",
]

REPO_ONLY_ROUTE_TERMS = [
    "governance",
    "status",
    "backlog",
    "queue",
    "selector",
]


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
    for key, value in obj.items():
        if key.endswith("_status") and isinstance(value, str):
            return value
    audit_status = obj.get("audit_status")
    if isinstance(audit_status, str):
        return audit_status
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
        "runtime_touched": False,
        "launcher_executed": False,
        "capital_changed": False,
        "live_or_real_orders": False,
        "holdout_accessed": False,
        "schema_apply_performed_now": False,
        "schema_file_creation_performed_now": False,
        "schema_file_edit_performed_now": False,
        "file_move_performed_now": False,
        "file_delete_performed_now": False,
        "repo_restructure_performed_now": False,
    }


def get_git_state() -> Dict[str, Any]:
    status_lines = [
        line
        for line in run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"]).stdout.splitlines()
        if line.strip()
    ]
    untracked = [line[3:].replace("\\", "/") for line in status_lines if line.startswith("?? ")]
    dirty_tracked = [line for line in status_lines if not line.startswith("?? ")]
    return {
        "head": run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
        "branch": run_cmd(["git", "branch", "--show-current"]).stdout.strip(),
        "status_porcelain": status_lines,
        "dirty_tracked_count": len(dirty_tracked),
        "dirty_tracked_paths": [line[3:].replace("\\", "/") for line in dirty_tracked],
        "untracked_count": len(untracked),
        "untracked_paths": sorted(untracked),
        "git_dirty": bool(status_lines),
        "remote_status_short": run_cmd(["git", "status", "-sb", "--untracked-files=all"]).stdout.splitlines(),
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


def source_record(path: Path, obj: Dict[str, Any]) -> Dict[str, Any]:
    counts = obj.get("counts", {})
    return {
        "path": str(path),
        "exists": path.exists(),
        "status": first_status(obj),
        "severity": obj.get("severity"),
        "critical_issue_count": obj.get("critical_issue_count"),
        "warning_count": obj.get("warning_count"),
        "next_module": obj.get("next_module"),
        "next_action": obj.get("next_action"),
        "final_decision": obj.get("final_decision"),
        "latest_commit": obj.get("latest_commit"),
        "git_head": obj.get("git_state", {}).get("head") if isinstance(obj.get("git_state"), dict) else None,
        "counts": counts if isinstance(counts, dict) else {},
    }


def validate_count_zero(errors: List[str], key: str, record: Dict[str, Any], field: str) -> None:
    value = record.get(field)
    if value is None:
        errors.append(f"{key} {field} field missing")
    elif value != 0:
        errors.append(f"{key} {field} not zero: {value}")


def validate_input_record(
    errors: List[str],
    key: str,
    record: Dict[str, Any],
    expected_status: str,
    expected_next_module: Optional[str],
) -> None:
    status = record.get("status")
    if status != expected_status:
        errors.append(f"{key} status mismatch: expected={expected_status} actual={status}")

    validate_count_zero(errors, key, record, "critical_issue_count")
    validate_count_zero(errors, key, record, "warning_count")

    if expected_next_module is not None and record.get("next_module") != expected_next_module:
        errors.append(
            f"{key} next_module mismatch: expected={expected_next_module} actual={record.get('next_module')}"
        )


def dangerous_flags_are_false(obj: Dict[str, Any]) -> Tuple[bool, List[str]]:
    violations: List[str] = []
    nested = obj.get("safety_flags", {})
    for flag in DANGEROUS_FLAGS:
        top_value = obj.get(flag, False)
        nested_value = nested.get(flag, False) if isinstance(nested, dict) else False
        if top_value is not False:
            violations.append(f"top-level {flag}={top_value!r}")
        if nested_value is not False:
            violations.append(f"safety_flags {flag}={nested_value!r}")
    return not violations, violations


def classify_next_module(next_module: Optional[str]) -> Dict[str, Any]:
    module = next_module or ""
    lowered = module.lower()
    blocked_terms = [term for term in BLOCKED_SCOPE_TERMS if term in lowered]
    repo_only_family = lowered.startswith("edge_factory_os_repo_only_")
    route_family_terms = [term for term in REPO_ONLY_ROUTE_TERMS if term in lowered]
    allowed = bool(module) and repo_only_family and bool(route_family_terms) and not blocked_terms
    unknown_scope = bool(module) and not allowed and not blocked_terms
    return {
        "next_module": next_module,
        "repo_only_family": repo_only_family,
        "route_family_terms": route_family_terms,
        "blocked_terms": blocked_terms,
        "unknown_scope": unknown_scope,
        "autopilot_route_allowed_for_next_repo_only_step": allowed,
        "research_or_manual_gate_required": not allowed,
        "decision_reason": (
            "Next module is repo-only governance/status/backlog/queue/selector scope."
            if allowed
            else "Next module is blocked, research-adjacent, schema-adjacent, runtime-adjacent, or unknown scope."
        ),
    }


def collect_validation() -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []
    loaded: Dict[str, Dict[str, Any]] = {}
    source_statuses: Dict[str, Dict[str, Any]] = {}

    git_state = get_git_state()
    physical_before = physical_guard_snapshot()

    if git_state["head"] != EXPECTED_HEAD:
        errors.append(f"unexpected HEAD: expected={EXPECTED_HEAD} actual={git_state['head']}")

    if git_state["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked files present: {git_state['dirty_tracked_paths']}")

    expected_untracked = [CURRENT_TOOL_REL]
    if git_state["untracked_paths"] != expected_untracked:
        errors.append(
            f"unexpected untracked files: expected={expected_untracked} actual={git_state['untracked_paths']}"
        )

    if physical_before["planned_schema_file_existing_count"] != 0:
        errors.append(f"planned schema files existed before execution: {physical_before['existing_planned_schema_files']}")

    for key, spec in INPUTS.items():
        path, expected_status, expected_next_module = spec
        try:
            obj = load_json(path)
        except Exception as exc:
            errors.append(f"required input missing or unreadable: {key} path={path} error={exc!r}")
            continue

        loaded[key] = obj
        record = source_record(path, obj)
        source_statuses[key] = record
        validate_input_record(errors, key, record, expected_status, expected_next_module)

        safe, violations = dangerous_flags_are_false(obj)
        if not safe:
            errors.append(f"{key} dangerous safety flags not false: {violations}")

    latest_selector = loaded.get("next_action_selector", {})
    latest_selector_post = loaded.get("next_action_selector_post_check", {})
    latest_next_modules = [
        value
        for value in [
            latest_selector.get("next_module"),
            latest_selector_post.get("next_module"),
            latest_selector.get("next_action_selector_after_standard_os_status_backlog_status_backlog_refresh", {})
            .get("selected_action", {})
            .get("module")
            if isinstance(latest_selector.get("next_action_selector_after_standard_os_status_backlog_status_backlog_refresh"), dict)
            else None,
        ]
        if value
    ]

    unique_latest_next_modules = sorted(set(str(value) for value in latest_next_modules))
    if unique_latest_next_modules != [EXPECTED_NEXT_MODULE]:
        errors.append(
            f"ambiguous or unexpected latest next_module: expected={[EXPECTED_NEXT_MODULE]} actual={unique_latest_next_modules}"
        )

    post_record = source_statuses.get("next_action_selector_post_check", {})
    if post_record.get("latest_commit") != EXPECTED_HEAD:
        errors.append(
            f"latest selector post-check commit mismatch: expected={EXPECTED_HEAD} actual={post_record.get('latest_commit')}"
        )
    if post_record.get("git_head") != EXPECTED_HEAD:
        errors.append(
            f"latest selector post-check git head mismatch: expected={EXPECTED_HEAD} actual={post_record.get('git_head')}"
        )

    post_counts = post_record.get("counts", {})
    required_zero_counts = [
        "dirty_tracked_count",
        "untracked_count",
        "tracked_python_syntax_error_count",
        "tracked_python_bom_error_count",
        "planned_schema_file_existing_count",
        "runtime_action_recommended_now_count",
        "capital_action_recommended_now_count",
        "direct_apply_recommended_now_count",
        "schema_apply_performed_count",
        "schema_file_creation_performed_count",
        "schema_file_edit_performed_count",
    ]
    for field in required_zero_counts:
        if post_counts.get(field) != 0:
            errors.append(f"latest selector post-check count {field} not zero: {post_counts.get(field)}")

    py_validation = validate_tracked_python()
    if not py_validation["pass"]:
        errors.append(
            "tracked Python syntax/BOM validation failed: "
            f"syntax={py_validation['syntax_errors'][:20]} bom={py_validation['bom_errors']}"
        )
    if py_validation["tracked_python_file_count"] != 508:
        errors.append(
            f"tracked Python count mismatch: expected=508 actual={py_validation['tracked_python_file_count']}"
        )

    physical_after = physical_guard_snapshot()
    if physical_after["planned_schema_file_existing_count"] != 0:
        errors.append(f"planned schema files existed after execution: {physical_after['existing_planned_schema_files']}")

    route = classify_next_module(EXPECTED_NEXT_MODULE if unique_latest_next_modules == [EXPECTED_NEXT_MODULE] else None)

    if not route["autopilot_route_allowed_for_next_repo_only_step"]:
        warnings.append(route["decision_reason"])

    local_flag_violations = [name for name in DANGEROUS_FLAGS if SAFETY_FLAGS.get(name) is not False]
    if local_flag_violations:
        errors.append(f"local dangerous flags are not false: {local_flag_violations}")

    return {
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
        "git_state": git_state,
        "physical_before": physical_before,
        "physical_after": physical_after,
        "source_statuses": source_statuses,
        "tracked_python_validation": py_validation,
        "latest_next_modules": unique_latest_next_modules,
        "route": route,
    }


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_autopilot_until_research_gate_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_autopilot_until_research_gate_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_autopilot_until_research_gate_v1_latest.txt"

    rendered = json.dumps(payload, indent=2, sort_keys=True)
    latest_json.write_text(rendered, encoding="utf-8")
    timestamped_json.write_text(rendered, encoding="utf-8")

    txt_lines = [
        "EDGE FACTORY OS REPO-ONLY AUTOPILOT UNTIL RESEARCH GATE v1",
        "=" * 100,
        f"status: {payload['status']}",
        f"autopilot_route_allowed_for_next_repo_only_step: {payload['autopilot_route_allowed_for_next_repo_only_step']}",
        f"research_or_manual_gate_required: {payload['research_or_manual_gate_required']}",
        f"next_module: {payload['next_module']}",
        f"critical_issue_count: {payload['critical_issue_count']}",
        f"warning_count: {payload['warning_count']}",
        "",
        "ROUTE PLAN",
        "-" * 100,
        json.dumps(payload["autopilot_route_plan"], indent=2, sort_keys=True),
        "",
        "VALIDATION",
        "-" * 100,
        json.dumps(payload["validation"], indent=2, sort_keys=True),
        "",
        "ERRORS",
        "-" * 100,
        json.dumps(payload["errors"], indent=2, sort_keys=True),
        "",
        "SAFETY FLAGS",
        "-" * 100,
        json.dumps(payload["safety_flags"], indent=2, sort_keys=True),
        "",
        "OUTPUTS",
        "-" * 100,
        f"latest_json: {latest_json}",
        f"timestamped_json: {timestamped_json}",
        f"latest_txt: {latest_txt}",
    ]
    latest_txt.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")
    return {
        "latest_json": str(latest_json),
        "timestamped_json": str(timestamped_json),
        "latest_txt": str(latest_txt),
    }


def main() -> int:
    validation = collect_validation()
    passed = bool(validation["passed"])
    route = validation["route"]

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "status": "PASS" if passed else "FAIL",
        "autopilot_until_research_gate_status": "PASS" if passed else "FAIL",
        "severity": "OK" if passed else "BLOCKED",
        "final_decision": "AUTOPILOT_ROUTE_PLAN_READY" if passed else "AUTOPILOT_ROUTE_PLAN_BLOCKED_FAIL_CLOSED",
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "expected_head": EXPECTED_HEAD,
        "next_module": EXPECTED_NEXT_MODULE if passed else None,
        "expected_next_module": EXPECTED_NEXT_MODULE,
        "latest_next_modules": validation["latest_next_modules"],
        "autopilot_route_allowed_for_next_repo_only_step": bool(
            passed and route["autopilot_route_allowed_for_next_repo_only_step"]
        ),
        "research_or_manual_gate_required": bool(
            (not passed) or route["research_or_manual_gate_required"]
        ),
        "critical_issue_count": len(validation["errors"]),
        "warning_count": len(validation["warnings"]),
        "errors": validation["errors"],
        "warnings": validation["warnings"],
        "autopilot_route_plan": {
            "may_future_wrapper_generate_next_module": bool(
                passed and route["autopilot_route_allowed_for_next_repo_only_step"]
            ),
            "must_not_execute_next_module": True,
            "must_not_generate_next_module_in_this_module": True,
            "next_module_execution_performed": False,
            "next_module_generation_performed": False,
            "decision": route,
            "allowed_family_definition": {
                "repo_only_prefix_required": "edge_factory_os_repo_only_",
                "allowed_terms": REPO_ONLY_ROUTE_TERMS,
                "blocked_terms": BLOCKED_SCOPE_TERMS,
            },
        },
        "validation": {
            "git_state": validation["git_state"],
            "physical_before": validation["physical_before"],
            "physical_after": validation["physical_after"],
            "source_statuses": validation["source_statuses"],
            "tracked_python_validation": validation["tracked_python_validation"],
            "expected_untracked_during_execution": [CURRENT_TOOL_REL],
            "planned_schema_rel_paths": PLANNED_SCHEMA_REL_PATHS,
        },
        "safety_flags": SAFETY_FLAGS,
    }

    for flag in DANGEROUS_FLAGS:
        payload[flag] = False

    payload["outputs"] = write_outputs(payload)
    # Re-write latest JSON with the output paths included.
    latest_json = Path(payload["outputs"]["latest_json"])
    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
