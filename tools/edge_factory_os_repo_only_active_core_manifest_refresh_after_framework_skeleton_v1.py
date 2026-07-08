from __future__ import annotations

import ast
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_active_core_manifest_refresh_after_framework_skeleton_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_repo_only_active_core_manifest_refresh_after_framework_skeleton_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "4dda4fa"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_active_core_manifest_refresh_after_framework_skeleton_v1.py"
EXPECTED_HEAD_ADDED_CAPABILITY_MAP_TOOL = "tools/edge_factory_os_repo_only_capability_map_refresh_after_framework_skeleton_v1.py"

CAPABILITY_JSON = LAB_ROOT / "edge_factory_os_repo_only_capability_map_refresh_after_framework_skeleton_v1" / "repo_only_capability_map_refresh_after_framework_skeleton_v1_latest.json"
CAPABILITY_POST_JSON = LAB_ROOT / "edge_factory_os_repo_only_capability_map_refresh_after_framework_skeleton_post_commit_check" / "repo_only_capability_map_refresh_after_framework_skeleton_post_commit_check_latest.json"
MODULE_INDEX_JSON = LAB_ROOT / "edge_factory_os_repo_only_module_index_refresh_after_framework_skeleton_v1" / "repo_only_module_index_refresh_after_framework_skeleton_v1_latest.json"
STATUS_REFRESH_JSON = LAB_ROOT / "edge_factory_os_repo_only_status_refresh_after_framework_skeleton_v1" / "repo_only_status_refresh_after_framework_skeleton_v1_latest.json"
FINAL_JSON = LAB_ROOT / "edge_factory_os_repo_only_generic_framework_skeleton_final_check_v1" / "repo_only_generic_framework_skeleton_final_check_v1_latest.json"

EXPECTED_FRAMEWORK_READMES = [
    "edge_factory_os_framework/README.md",
    "edge_factory_os_framework/contracts/README.md",
    "edge_factory_os_framework/core/README.md",
    "edge_factory_os_framework/manifests/README.md",
    "edge_factory_os_framework/plugins/README.md",
    "edge_factory_os_framework/policies/README.md",
    "edge_factory_os_framework/reports/README.md",
    "edge_factory_os_framework/schemas/README.md",
]

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_active_core_manifest_refresh_after_framework_skeleton": True,
    "read_only_active_core_manifest_refresh_only": True,
    "capability_map_after_framework_skeleton_required": True,
    "module_index_after_framework_skeleton_required": True,
    "framework_skeleton_complete_required": True,
    "capability_map_precommit_scan_gap_allowed_for_head_added_tool_only": True,

    "repo_only_governance_allowed": True,
    "repo_only_audit_allowed": True,
    "read_only_validation_allowed": True,

    "framework_file_creation_allowed_now": False,
    "framework_directory_creation_allowed_now": False,
    "framework_file_creation_performed_now": False,
    "framework_directory_creation_performed_now": False,
    "file_move_allowed_now": False,
    "file_delete_allowed_now": False,
    "repo_restructure_allowed_now": False,
    "overwrite_existing_files_allowed": False,
    "modify_existing_files_allowed": False,
    "manual_review_allowed_now": False,
    "risk_file_edit_allowed_now": False,
    "risk_file_execution_allowed_now": False,
    "patch_allowed_now": False,
    "apply_performed_now": False,
    "commit_performed_now": False,
    "stage_performed_now": False,
    "direct_apply_allowed": False,
    "runtime_touch_allowed": False,
    "launcher_allowed": False,
    "capital_change_allowed": False,
    "active_paper_allowed": False,
    "live_allowed": False,
    "real_orders_allowed": False,
    "candidate_generation_allowed": False,
    "candidate_release_allowed": False,
    "family_release_allowed": False,
    "strategy_research_allowed": False,
    "holdout_access_allowed": False,
    "gitignore_change_allowed": False,
    "backup_delete_allowed": False,
    "backup_move_allowed": False,
    "git_add_force_allowed": False,
    "mass_metadata_patch_allowed": False,
    "blind_fix_all_allowed": False,
}

FORBIDDEN_ACTIONS = [
    "runtime_touch",
    "launcher_execution",
    "capital_change",
    "active_paper_change",
    "live_trading",
    "real_order_execution",
    "strategy_research",
    "candidate_generation",
    "candidate_release",
    "family_release",
    "holdout_access",
    "gitignore_change",
    "backup_delete",
    "backup_move",
    "git_add_force",
    "blind_fix_all",
    "mass_metadata_patch",
    "direct_apply",
    "manual_risk_file_review_without_valid_approval",
    "risk_file_edit_without_approval",
    "risk_file_execution_without_approval",
    "overwrite_existing_files",
    "modify_existing_files",
    "move_files",
    "delete_files",
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


def get_git_state() -> Dict[str, Any]:
    status_lines = [
        x
        for x in run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"]).stdout.splitlines()
        if x.strip()
    ]
    untracked = [x[3:] for x in status_lines if x.startswith("?? ")]
    dirty_tracked = [x for x in status_lines if not x.startswith("?? ")]

    return {
        "head": run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
        "branch": run_cmd(["git", "branch", "--show-current"]).stdout.strip(),
        "status_porcelain": status_lines,
        "dirty_tracked_count": len(dirty_tracked),
        "dirty_tracked_paths": [x[3:] for x in dirty_tracked],
        "untracked_count": len(untracked),
        "untracked_paths": untracked,
        "git_dirty": bool(status_lines),
        "remote_status_short": run_cmd(["git", "status", "-sb", "--untracked-files=all"]).stdout.splitlines(),
    }


def tracked_files() -> List[str]:
    return sorted(x.strip().replace("\\", "/") for x in run_cmd(["git", "ls-files"]).stdout.splitlines() if x.strip())


def tracked_python_files() -> List[str]:
    return sorted(x.strip().replace("\\", "/") for x in run_cmd(["git", "ls-files", "*.py"]).stdout.splitlines() if x.strip())


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
    return sorted(x.strip().replace("\\", "/") for x in lines if x.strip())


def first_status(obj: Dict[str, Any]) -> Optional[str]:
    for key in [
        "capability_map_after_framework_skeleton_status",
        "audit_status",
        "module_index_after_framework_skeleton_status",
        "status_refresh_after_framework_skeleton_status",
        "framework_skeleton_final_check_status",
    ]:
        value = obj.get(key)
        if value:
            return str(value)
    return None


def source_record(path: Path, obj: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "path": str(path),
        "status": first_status(obj),
        "critical_issue_count": obj.get("critical_issue_count"),
        "warning_count": obj.get("warning_count"),
        "next_module": obj.get("next_module"),
        "final_decision": obj.get("final_decision"),
    }


def validate_count_zero(errors: List[str], key: str, record: Dict[str, Any], field: str) -> None:
    value = record.get(field)
    if value is None:
        errors.append(f"{key} {field} field missing")
        return
    if value != 0:
        errors.append(f"{key} {field} not 0: {value}")


def validate_status_record(errors: List[str], key: str, record: Dict[str, Any], expected_status: str, expected_next_module: Optional[str] = None) -> None:
    status = record.get("status")
    if status is None:
        errors.append(f"{key} status field missing")
    elif status != expected_status:
        errors.append(f"{key} status mismatch: expected={expected_status} actual={status}")

    validate_count_zero(errors, key, record, "critical_issue_count")
    validate_count_zero(errors, key, record, "warning_count")

    if expected_next_module is not None and record.get("next_module") != expected_next_module:
        errors.append(f"{key} next_module mismatch: expected={expected_next_module} actual={record.get('next_module')}")


def fallback_capabilities(path: str) -> List[str]:
    lower = path.lower()
    stem = Path(path).stem.lower()
    caps: Set[str] = set()

    if path.startswith("edge_factory_os_framework/"):
        caps.add("framework")
    if path.startswith("tools/"):
        caps.add("tooling")
    if path.endswith(".py"):
        caps.add("python")
    if path.endswith(".json"):
        caps.add("json_artifact")
    if path.endswith(".txt") or path.endswith(".md"):
        caps.add("documentation")

    keyword_caps = {
        "contract": "contract_governance",
        "preview": "preview_governance",
        "approval": "approval_governance",
        "apply": "apply_governance",
        "audit": "audit_validation",
        "final_check": "final_validation",
        "post_commit": "post_commit_validation",
        "status_refresh": "status_refresh",
        "module_index": "module_index",
        "capability_map": "capability_map",
        "manifest": "manifest",
        "policy": "policy",
        "runner": "runner",
        "router": "router",
        "scheduler": "scheduler",
        "operator": "operator",
        "error": "error_governance",
        "backup": "backup_hygiene",
        "quarantine": "quarantine_hygiene",
        "risk": "risk_governance",
        "holdout": "holdout_governance",
        "capital": "capital_sensitive",
        "live": "live_sensitive",
        "order": "order_sensitive",
        "runtime": "runtime_sensitive",
        "launcher": "launcher_sensitive",
        "candidate": "candidate_governance",
        "family": "family_governance",
        "strategy": "strategy_research",
        "research": "research_governance",
        "schema": "schema",
        "plugin": "plugin",
        "report": "reporting",
    }

    haystack = f"{lower} {stem}"
    for key, cap in keyword_caps.items():
        if key in haystack:
            caps.add(cap)

    if not caps:
        caps.add("unclassified")

    return sorted(caps)


def validate_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    loaded: Dict[str, Dict[str, Any]] = {}
    source_statuses: Dict[str, Dict[str, Any]] = {}
    checks: Dict[str, Any] = {}
    git_state = get_git_state()

    if not git_state["head"].startswith(EXPECTED_HEAD_PREFIX):
        errors.append(f"unexpected HEAD: {git_state['head']} expected {EXPECTED_HEAD_PREFIX}")

    expected_untracked = {CURRENT_TOOL_REL}
    actual_untracked = set(git_state["untracked_paths"])

    if git_state["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked paths present before active-core manifest refresh: {git_state['dirty_tracked_paths']}")

    if actual_untracked != expected_untracked:
        errors.append(f"unexpected untracked set before active-core manifest refresh: expected={sorted(expected_untracked)} actual={sorted(actual_untracked)}")

    subject = commit_subject("HEAD")
    checks["head_commit_subject"] = subject
    if subject != "Add repo-only capability map refresh after framework skeleton":
        errors.append(f"unexpected HEAD commit subject: {subject}")

    paths = commit_paths("HEAD")
    checks["head_commit_paths"] = paths
    if paths != [EXPECTED_HEAD_ADDED_CAPABILITY_MAP_TOOL]:
        errors.append(f"unexpected HEAD commit paths: {paths}")

    inputs = {
        "capability_map_after_framework_skeleton": (
            CAPABILITY_JSON,
            "REPO_ONLY_CAPABILITY_MAP_REFRESH_AFTER_FRAMEWORK_SKELETON_V1_READY",
            "edge_factory_os_repo_only_active_core_manifest_refresh_after_framework_skeleton_v1.py",
        ),
        "capability_map_after_framework_skeleton_post_check": (
            CAPABILITY_POST_JSON,
            "REPO_ONLY_CAPABILITY_MAP_REFRESH_AFTER_FRAMEWORK_SKELETON_POST_COMMIT_CHECK_PASS",
            "edge_factory_os_repo_only_active_core_manifest_refresh_after_framework_skeleton_v1.py",
        ),
        "module_index_after_framework_skeleton": (
            MODULE_INDEX_JSON,
            "REPO_ONLY_MODULE_INDEX_REFRESH_AFTER_FRAMEWORK_SKELETON_V1_READY",
            None,
        ),
        "status_refresh_after_framework_skeleton": (
            STATUS_REFRESH_JSON,
            "REPO_ONLY_STATUS_REFRESH_AFTER_FRAMEWORK_SKELETON_V1_READY",
            None,
        ),
        "generic_framework_skeleton_final_check": (
            FINAL_JSON,
            "REPO_ONLY_GENERIC_FRAMEWORK_SKELETON_FINAL_CHECK_V1_READY",
            None,
        ),
    }

    for key, spec in inputs.items():
        path, expected_status, expected_next_module = spec
        obj: Optional[Dict[str, Any]] = None
        record: Optional[Dict[str, Any]] = None

        try:
            obj = load_json(path)
            loaded[key] = obj
            record = source_record(path, obj)
        except Exception as exc:
            errors.append(f"cannot load {key}: {path} error={repr(exc)}")

        if record is not None:
            source_statuses[key] = record
            checks[key] = record
            validate_status_record(errors, key, record, expected_status, expected_next_module)

    py = validate_tracked_python()
    checks["tracked_python"] = {
        "tracked_python_file_count": py["tracked_python_file_count"],
        "syntax_error_count": py["syntax_error_count"],
        "bom_error_count": py["bom_error_count"],
    }

    if not py["pass"]:
        errors.append(f"tracked Python validation failed: syntax={py['syntax_errors'][:20]} bom={py['bom_errors']}")

    return {
        "pass": not errors,
        "errors": errors,
        "loaded": loaded,
        "source_statuses": source_statuses,
        "checks": checks,
        "git_state": git_state,
        "tracked_python_validation": py,
        "expected_untracked_during_run": sorted(expected_untracked),
        "actual_untracked_during_run": sorted(actual_untracked),
        "clean_baseline": not errors,
    }


def capability_records(capability_obj: Dict[str, Any]) -> List[Dict[str, Any]]:
    cap = capability_obj.get("capability_map_after_framework_skeleton", {})
    rows = cap.get("records", [])
    if isinstance(rows, list):
        return [row for row in rows if isinstance(row, dict)]
    return []


def build_active_core_manifest(validation: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []
    files = tracked_files()
    py_files = tracked_python_files()
    capability_obj = validation["loaded"]["capability_map_after_framework_skeleton"]
    cap_records = capability_records(capability_obj)

    cap_by_path: Dict[str, Dict[str, Any]] = {}
    for row in cap_records:
        path = row.get("path")
        if isinstance(path, str):
            cap_by_path[path] = row

    missing_capability_paths = sorted(set(files) - set(cap_by_path.keys()))
    extra_capability_paths = sorted(set(cap_by_path.keys()) - set(files))
    accepted_missing_capability_paths = [EXPECTED_HEAD_ADDED_CAPABILITY_MAP_TOOL]
    capability_coverage_accepted = (
        not extra_capability_paths
        and missing_capability_paths in ([], accepted_missing_capability_paths)
    )

    if not capability_coverage_accepted:
        errors.append(
            "capability coverage mismatch outside accepted HEAD-added tool gap: "
            f"missing={missing_capability_paths} extra={extra_capability_paths}"
        )

    active_core_prefixes = ["tools/", "edge_factory_os_framework/"]

    active_records: List[Dict[str, Any]] = []
    active_core_counts: Counter[str] = Counter()
    sensitive_records: List[Dict[str, Any]] = []

    sensitive_caps = {
        "runtime_sensitive",
        "launcher_sensitive",
        "capital_sensitive",
        "live_sensitive",
        "order_sensitive",
        "holdout_governance",
    }

    for rel in files:
        if not any(rel.startswith(prefix) for prefix in active_core_prefixes):
            continue

        cap_row = cap_by_path.get(rel)
        if cap_row is None:
            caps = fallback_capabilities(rel)
            capability_source = "FALLBACK_FOR_ACCEPTED_HEAD_ADDED_TOOL_GAP"
        else:
            raw_caps = cap_row.get("capabilities", [])
            caps = [str(x) for x in raw_caps] if isinstance(raw_caps, list) else fallback_capabilities(rel)
            capability_source = "CAPABILITY_MAP"

        caps_set = set(caps)
        role = "framework" if rel.startswith("edge_factory_os_framework/") else "tooling"
        active_core_counts[role] += 1

        risky = sorted(caps_set & sensitive_caps)
        record = {
            "path": rel,
            "active_core_role": role,
            "capabilities": sorted(caps_set),
            "capability_source": capability_source,
            "is_framework_readme": rel in EXPECTED_FRAMEWORK_READMES,
            "is_python_tool": rel.startswith("tools/") and rel.endswith(".py"),
            "sensitive_capabilities": risky,
            "sensitive_capability_count": len(risky),
            "allowed_as_active_core_manifest_entry": True,
            "runtime_execution_allowed": False,
            "capital_or_live_action_allowed": False,
        }
        active_records.append(record)
        if risky:
            sensitive_records.append(record)

    framework_manifest_records = [row for row in active_records if row["is_framework_readme"] is True]
    python_tool_records = [row for row in active_records if row["is_python_tool"] is True]

    if len(framework_manifest_records) != 8:
        errors.append(f"framework active manifest readme count not 8: {len(framework_manifest_records)}")
    if not python_tool_records:
        errors.append("no python tool records found for active-core manifest")

    return {
        "active_core_manifest_status": "ACTIVE_CORE_MANIFEST_AFTER_FRAMEWORK_SKELETON_ACTIVE" if not errors else "ACTIVE_CORE_MANIFEST_AFTER_FRAMEWORK_SKELETON_BLOCKED",
        "manifest_scope": "REPO_ONLY_OS_INTELLIGENCE_ACTIVE_CORE",
        "manifest_at_head": get_git_state()["head"],
        "active_core_prefixes": active_core_prefixes,
        "records": sorted(active_records, key=lambda row: row["path"]),
        "record_count": len(active_records),
        "active_core_counts": dict(sorted(active_core_counts.items())),
        "framework_readme_count": len(framework_manifest_records),
        "python_tool_count": len(python_tool_records),
        "sensitive_record_count": len(sensitive_records),
        "sensitive_records_preview": sensitive_records[:50],
        "tracked_file_count": len(files),
        "tracked_python_count": len(py_files),
        "capability_record_count": len(cap_records),
        "missing_capability_paths": missing_capability_paths,
        "extra_capability_paths": extra_capability_paths,
        "accepted_missing_capability_paths": accepted_missing_capability_paths,
        "capability_coverage_accepted": capability_coverage_accepted,
        "errors": errors,
        "invariants": {
            "record_count_positive": len(active_records) > 0,
            "framework_readme_count_is_8": len(framework_manifest_records) == 8,
            "python_tool_count_positive": len(python_tool_records) > 0,
            "capability_coverage_accepted_with_head_added_tool_gap_only": capability_coverage_accepted is True,
            "missing_capability_paths_are_only_head_added_capability_map_tool": missing_capability_paths in ([], accepted_missing_capability_paths),
            "all_records_are_repo_only_manifest_entries": all(row["allowed_as_active_core_manifest_entry"] is True for row in active_records),
            "all_runtime_execution_blocked": all(row["runtime_execution_allowed"] is False for row in active_records),
            "all_capital_or_live_action_blocked": all(row["capital_or_live_action_allowed"] is False for row in active_records),
            "no_runtime_strategy_or_capital_authorized": True,
            "no_file_creation_or_modification_performed_by_active_core_manifest_refresh": True,
        },
        "recommended_next_step": {
            "step": "BUILD_REPO_ONLY_GOVERNANCE_STATUS_PANEL_AFTER_FRAMEWORK_SKELETON",
            "module": "edge_factory_os_repo_only_governance_status_panel_after_framework_skeleton_v1.py",
            "scope": "REPO_ONLY_OS_INTELLIGENCE",
            "reason": "Active-core manifest is refreshed after accepting the known HEAD-added capability-map tool gap; build compact governance status panel next.",
        },
    }


def main() -> int:
    safety_errors = [key for key, value in SAFETY_FLAGS.items() if not isinstance(value, bool)]

    validation = validate_inputs()
    errors = list(validation["errors"])

    if safety_errors:
        errors.append(f"safety flags are not boolean: {safety_errors}")

    manifest = build_active_core_manifest(validation)
    errors.extend(manifest["errors"])

    for key, value in manifest["invariants"].items():
        if value is not True:
            errors.append(f"invariant {key} not true: {value}")

    passed = not errors

    payload = {
        "module": MODULE_NAME,
        "active_core_manifest_after_framework_skeleton_status": "REPO_ONLY_ACTIVE_CORE_MANIFEST_REFRESH_AFTER_FRAMEWORK_SKELETON_V1_READY" if passed else "REPO_ONLY_ACTIVE_CORE_MANIFEST_REFRESH_AFTER_FRAMEWORK_SKELETON_V1_BLOCKED",
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": "ACTIVE_CORE_MANIFEST_AFTER_FRAMEWORK_SKELETON_READY_FOR_GOVERNANCE_STATUS_PANEL" if passed else "KEEP_FREEZE_REVIEW_ACTIVE_CORE_MANIFEST_AFTER_FRAMEWORK_SKELETON_ERRORS",
        "next_action": "BUILD_REPO_ONLY_GOVERNANCE_STATUS_PANEL_AFTER_FRAMEWORK_SKELETON_V1" if passed else "REVIEW_ACTIVE_CORE_MANIFEST_AFTER_FRAMEWORK_SKELETON_ERRORS",
        "next_module": "edge_factory_os_repo_only_governance_status_panel_after_framework_skeleton_v1.py" if passed else None,
        "reason": "Refreshed active-core manifest after framework skeleton completion with accepted HEAD-added capability-map tool gap." if passed else "Active-core manifest refresh after framework skeleton validation failed.",
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "critical_issue_count": len(errors),
        "warning_count": 0,
        "errors": errors,
        "warnings": [],
        "validation": {
            "checks": validation["checks"],
            "git_state": validation["git_state"],
            "tracked_python_validation": validation["tracked_python_validation"],
            "source_statuses": validation["source_statuses"],
            "expected_untracked_during_run": validation["expected_untracked_during_run"],
            "actual_untracked_during_run": validation["actual_untracked_during_run"],
            "clean_baseline": validation["clean_baseline"],
        },
        "active_core_manifest_after_framework_skeleton": manifest,
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "apply_performed_now": False,
        "stage_recommended_now": False,
        "commit_recommended_now": False,
        "runtime_action_recommended_now": False,
        "capital_action_recommended_now": False,
        "holdout_action_recommended_now": False,
        "strategy_research_recommended_now": False,
        "candidate_generation_recommended_now": False,
        "candidate_release_recommended_now": False,
        "family_release_recommended_now": False,
        "framework_file_creation_performed_now": False,
        "framework_directory_creation_performed_now": False,
        "manual_review_allowed_now": False,
        "risk_file_edit_allowed_now": False,
        "risk_file_execution_allowed_now": False,
        "runtime_touched": False,
        "launcher_executed": False,
        "capital_changed": False,
        "live_or_real_orders": False,
        "holdout_accessed": False,
        "backup_deleted": False,
        "gitignore_changed": False,
        "git_add_force_used": False,
    }

    latest_json = OUT_DIR / "repo_only_active_core_manifest_refresh_after_framework_skeleton_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_active_core_manifest_refresh_after_framework_skeleton_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "repo_only_active_core_manifest_refresh_after_framework_skeleton_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY ACTIVE CORE MANIFEST REFRESH AFTER FRAMEWORK SKELETON v1",
        "=" * 100,
        f"active_core_manifest_after_framework_skeleton_status: {payload['active_core_manifest_after_framework_skeleton_status']}",
        f"severity: {payload['severity']}",
        f"final_decision: {payload['final_decision']}",
        f"next_action: {payload['next_action']}",
        f"next_module: {payload['next_module']}",
        f"reason: {payload['reason']}",
        f"critical_issue_count: {payload['critical_issue_count']}",
        f"warning_count: {payload['warning_count']}",
        "",
        "ERRORS",
        "-" * 100,
        json.dumps(errors, indent=2, sort_keys=True),
        "",
        "MANIFEST SUMMARY",
        "-" * 100,
        json.dumps(
            {
                "record_count": manifest["record_count"],
                "active_core_counts": manifest["active_core_counts"],
                "framework_readme_count": manifest["framework_readme_count"],
                "python_tool_count": manifest["python_tool_count"],
                "sensitive_record_count": manifest["sensitive_record_count"],
                "tracked_file_count": manifest["tracked_file_count"],
                "tracked_python_count": manifest["tracked_python_count"],
                "capability_record_count": manifest["capability_record_count"],
                "missing_capability_paths": manifest["missing_capability_paths"],
                "accepted_missing_capability_paths": manifest["accepted_missing_capability_paths"],
                "capability_coverage_accepted": manifest["capability_coverage_accepted"],
                "invariants": manifest["invariants"],
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
    print("\n".join(lines))
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())