from __future__ import annotations

import ast
import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_dependency_surface_refresh_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_repo_only_dependency_surface_refresh_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "9ef805a"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_dependency_surface_refresh_v1.py"

MODULE_INDEX_JSON = LAB_ROOT / "edge_factory_os_repo_only_module_index_refresh_v1" / "repo_only_module_index_refresh_v1_latest.json"
MODULE_INDEX_POST_CHECK_JSON = LAB_ROOT / "edge_factory_os_repo_only_module_index_refresh_post_commit_check" / "repo_only_module_index_refresh_post_commit_check_latest.json"
CAPABILITY_JSON = LAB_ROOT / "edge_factory_os_repo_only_capability_map_refresh_v1" / "repo_only_capability_map_refresh_v1_latest.json"
PANEL_JSON = LAB_ROOT / "edge_factory_os_post_resume_full_governance_panel_refresh_v1" / "post_resume_full_governance_panel_refresh_v1_latest.json"
GOVERNOR_JSON = LAB_ROOT / "edge_factory_os_post_resume_zero_error_governor_panel_v1" / "post_resume_zero_error_governor_panel_v1_latest.json"

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_dependency_surface_refresh": True,
    "read_only_dependency_surface_only": True,
    "module_index_required": True,
    "capability_map_required": True,
    "full_governance_panel_required": True,
    "governor_panel_required": True,

    "repo_only_governance_allowed": True,
    "repo_only_audit_allowed": True,
    "repo_only_status_refresh_allowed": True,
    "repo_only_contract_preview_allowed": True,
    "read_only_validation_allowed": True,

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

FORBIDDEN_ACTIONS: List[str] = [
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
    "old_short_guarded_apply_execution",
]

STDLIB_MODULES: Set[str] = set(getattr(sys, "stdlib_module_names", set()))
KNOWN_REPO_ROOTS = {
    "edge_factory",
    "edge_factory_os",
    "global_paper_risk_manager",
    "impulse_event_long_live_paper_logger",
    "impulse_long_gate_aware_live_paper_logger",
    "market_relative_live_paper_logger",
    "okx_event_impulse_live_paper_logger",
    "old_short_gate_aware_live_paper_logger",
    "session_ret60_reversal_live_paper_logger",
    "session_short_gate_aware_live_paper_logger",
    "sizing_contract_runtime",
    "weak_market_breakdown_short_live_paper_logger",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def get_git_state() -> Dict[str, Any]:
    status_lines = [x for x in run_cmd(["git", "status", "--porcelain=v1"]).stdout.splitlines() if x.strip()]
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
        "remote_status_short": run_cmd(["git", "status", "-sb"]).stdout.splitlines(),
    }


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def tracked_python_files() -> List[str]:
    return sorted(x.strip() for x in run_cmd(["git", "ls-files", "*.py"]).stdout.splitlines() if x.strip())


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


def first_status(obj: Dict[str, Any]) -> Optional[str]:
    for key in [
        "module_index_status",
        "audit_status",
        "capability_map_status",
        "refresh_status",
        "governor_status",
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


def validate_status_record(
    errors: List[str],
    key: str,
    record: Dict[str, Any],
    expected_status: str,
    expected_next_module: Optional[str] = None,
) -> None:
    status = record.get("status")
    if status is None:
        errors.append(f"{key} status field missing")
    elif status != expected_status:
        errors.append(f"{key} status mismatch: expected={expected_status} actual={status}")

    validate_count_zero(errors, key, record, "critical_issue_count")
    validate_count_zero(errors, key, record, "warning_count")

    if expected_next_module is not None and record.get("next_module") != expected_next_module:
        errors.append(
            f"{key} next_module mismatch: expected={expected_next_module} actual={record.get('next_module')}"
        )


def validate_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    checks: Dict[str, Any] = {}
    source_statuses: Dict[str, Dict[str, Any]] = {}
    git_state = get_git_state()

    if not git_state["head"].startswith(EXPECTED_HEAD_PREFIX):
        errors.append(f"unexpected HEAD: {git_state['head']} expected {EXPECTED_HEAD_PREFIX}")

    expected_untracked = {CURRENT_TOOL_REL}
    actual_untracked = set(git_state["untracked_paths"])
    current_step_untracked_ok = actual_untracked == expected_untracked

    if git_state["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked paths present: {git_state['dirty_tracked_paths']}")

    if not current_step_untracked_ok:
        errors.append(
            "unexpected untracked set: "
            f"expected={sorted(expected_untracked)} actual={sorted(actual_untracked)}"
        )

    head_subject = commit_subject("HEAD")
    checks["head_commit_subject"] = head_subject
    if head_subject != "Add repo-only module index refresh":
        errors.append(f"unexpected HEAD commit subject: {head_subject}")

    inputs = {
        "module_index": (MODULE_INDEX_JSON, "REPO_ONLY_OS_MODULE_INDEX_REFRESH_V1_READY", "edge_factory_os_repo_only_dependency_surface_refresh_v1.py"),
        "module_index_post_check": (MODULE_INDEX_POST_CHECK_JSON, "REPO_ONLY_MODULE_INDEX_REFRESH_POST_COMMIT_CHECK_PASS", "edge_factory_os_repo_only_dependency_surface_refresh_v1.py"),
        "capability_map": (CAPABILITY_JSON, "REPO_ONLY_OS_CAPABILITY_MAP_REFRESH_V1_READY", None),
        "full_governance_panel": (PANEL_JSON, "POST_RESUME_FULL_GOVERNANCE_PANEL_REFRESH_V1_READY", None),
        "governor": (GOVERNOR_JSON, "POST_RESUME_ZERO_ERROR_GOVERNOR_PANEL_V1_READY", None),
    }

    for key, spec in inputs.items():
        path, expected_status, expected_next_module = spec
        obj: Optional[Dict[str, Any]] = None
        record: Optional[Dict[str, Any]] = None

        try:
            obj = load_json(path)
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
        "checks": checks,
        "git_state": git_state,
        "tracked_python_validation": py,
        "source_statuses": source_statuses,
        "current_step_untracked_ok": current_step_untracked_ok,
        "expected_untracked_during_run": sorted(expected_untracked),
        "actual_untracked_during_run": sorted(actual_untracked),
        "clean_baseline": not errors,
    }


def import_root(name: str) -> str:
    return name.split(".", 1)[0] if name else ""


def classify_import(root: str, repo_stems: Set[str]) -> str:
    if not root:
        return "unknown"
    if root in repo_stems or root in KNOWN_REPO_ROOTS or root.startswith("edge_factory"):
        return "repo_local"
    if root in STDLIB_MODULES:
        return "stdlib"
    return "external_or_unresolved"


def extract_imports(rel: str, repo_stems: Set[str]) -> Dict[str, Any]:
    path = REPO_ROOT / rel
    data = path.read_bytes()
    text = data.decode("utf-8")
    tree = ast.parse(text, filename=rel)

    imports: List[Dict[str, Any]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = import_root(alias.name)
                imports.append(
                    {
                        "kind": "import",
                        "module": alias.name,
                        "root": root,
                        "classification": classify_import(root, repo_stems),
                        "lineno": getattr(node, "lineno", None),
                    }
                )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            root = import_root(module)
            if node.level and node.level > 0:
                classification = "relative_repo_local"
            else:
                classification = classify_import(root, repo_stems)
            imports.append(
                {
                    "kind": "from_import",
                    "module": module,
                    "root": root,
                    "level": node.level,
                    "classification": classification,
                    "lineno": getattr(node, "lineno", None),
                }
            )

    class_counts = Counter(item["classification"] for item in imports)
    root_counts = Counter(item["root"] for item in imports if item["root"])

    return {
        "path": rel,
        "import_count": len(imports),
        "classification_counts": dict(sorted(class_counts.items())),
        "top_import_roots": dict(root_counts.most_common(20)),
        "imports": imports[:200],
        "imports_truncated": len(imports) > 200,
    }


def build_dependency_surface(
    clean_baseline: bool,
    source_statuses: Dict[str, Dict[str, Any]],
    git_state: Dict[str, Any],
    py: Dict[str, Any],
) -> Dict[str, Any]:
    rel_paths = tracked_python_files()
    repo_stems = {Path(rel).stem for rel in rel_paths}

    records = [extract_imports(rel, repo_stems) for rel in rel_paths]

    total_classification_counts: Counter[str] = Counter()
    total_root_counts: Counter[str] = Counter()
    high_import_records: List[Dict[str, Any]] = []
    external_samples: List[Dict[str, Any]] = []
    repo_local_samples: List[Dict[str, Any]] = []

    for record in records:
        total_classification_counts.update(record["classification_counts"])
        total_root_counts.update(record["top_import_roots"])

        if record["import_count"] >= 25 and len(high_import_records) < 25:
            high_import_records.append(
                {
                    "path": record["path"],
                    "import_count": record["import_count"],
                    "classification_counts": record["classification_counts"],
                }
            )

        for item in record["imports"]:
            if item["classification"] == "external_or_unresolved" and len(external_samples) < 50:
                external_samples.append({"path": record["path"], "root": item["root"], "module": item["module"]})
            if item["classification"] in {"repo_local", "relative_repo_local"} and len(repo_local_samples) < 50:
                repo_local_samples.append({"path": record["path"], "root": item["root"], "module": item["module"]})

    return {
        "dependency_surface_status": "REPO_ONLY_OS_DEPENDENCY_SURFACE_ACTIVE" if clean_baseline else "REPO_ONLY_OS_DEPENDENCY_SURFACE_BLOCKED",
        "dependency_surface_scope": "REPO_ONLY_GOVERNANCE_DISCOVERY",
        "source_statuses": source_statuses,
        "repo_state": {
            "head": git_state["head"],
            "branch": git_state["branch"],
            "dirty_tracked_count": git_state["dirty_tracked_count"],
            "untracked_count": git_state["untracked_count"],
            "tracked_python_file_count": py["tracked_python_file_count"],
            "tracked_python_syntax_error_count": py["syntax_error_count"],
            "tracked_python_bom_error_count": py["bom_error_count"],
        },
        "surface_summary": {
            "module_dependency_record_count": len(records),
            "total_import_count": sum(record["import_count"] for record in records),
            "classification_counts": dict(sorted(total_classification_counts.items())),
            "top_import_roots": dict(total_root_counts.most_common(50)),
            "high_import_record_sample_count": len(high_import_records),
            "high_import_record_sample": high_import_records,
            "external_or_unresolved_sample_count": len(external_samples),
            "external_or_unresolved_sample": external_samples,
            "repo_local_sample_count": len(repo_local_samples),
            "repo_local_sample": repo_local_samples,
        },
        "module_dependency_records": records,
        "invariants": {
            "module_dependency_record_count_equals_tracked_python_file_count": len(records) == py["tracked_python_file_count"],
            "dependency_classification_counts_are_multilabel_per_import_not_per_file": True,
            "do_not_compare_sum_dependency_classifications_to_tracked_python_file_count": True,
        },
        "blocked_domains": [
            "runtime_touch",
            "launcher_execution",
            "capital_change",
            "active_paper_change",
            "live_trading",
            "real_orders",
            "holdout_access",
            "strategy_research",
            "candidate_generation",
            "candidate_release",
            "family_release",
        ],
        "recommended_next_step": {
            "step": "BUILD_REPO_ONLY_OS_RISKY_SURFACE_REVIEW",
            "module": "edge_factory_os_repo_only_risky_surface_review_v1.py",
            "scope": "REPO_ONLY_GOVERNANCE_DISCOVERY",
            "reason": "Dependency surface is mapped; next safe step is a read-only risky surface review before any broader development.",
        },
    }


def main() -> int:
    safety_errors = [
        key for key, value in SAFETY_FLAGS.items()
        if not isinstance(value, bool)
    ]

    validation = validate_inputs()
    errors = list(validation["errors"])

    if safety_errors:
        errors.append(f"safety flags are not boolean: {safety_errors}")

    dependency_surface = build_dependency_surface(
        bool(validation["clean_baseline"]) and not safety_errors,
        validation["source_statuses"],
        validation["git_state"],
        validation["tracked_python_validation"],
    )

    if validation["pass"] and dependency_surface["dependency_surface_status"] != "REPO_ONLY_OS_DEPENDENCY_SURFACE_ACTIVE":
        errors.append(f"dependency surface did not become active: {dependency_surface['dependency_surface_status']}")

    if not dependency_surface["invariants"]["module_dependency_record_count_equals_tracked_python_file_count"]:
        errors.append("module_dependency_record_count does not equal tracked_python_file_count")

    passed = not errors

    payload = {
        "module": MODULE_NAME,
        "dependency_surface_status": (
            "REPO_ONLY_OS_DEPENDENCY_SURFACE_REFRESH_V1_READY"
            if passed
            else "REPO_ONLY_OS_DEPENDENCY_SURFACE_REFRESH_V1_BLOCKED"
        ),
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_GOVERNANCE_DISCOVERY",
        "final_decision": (
            "DEPENDENCY_SURFACE_READY_FOR_RISKY_SURFACE_REVIEW"
            if passed
            else "KEEP_FREEZE_REVIEW_DEPENDENCY_SURFACE_ERRORS"
        ),
        "next_action": (
            "BUILD_REPO_ONLY_OS_RISKY_SURFACE_REVIEW_V1"
            if passed
            else "REVIEW_DEPENDENCY_SURFACE_ERRORS"
        ),
        "next_module": (
            "edge_factory_os_repo_only_risky_surface_review_v1.py"
            if passed
            else None
        ),
        "reason": (
            "Refreshed repo-only OS dependency surface from tracked Python imports."
            if passed
            else "Repo-only dependency surface refresh validation failed."
        ),
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
            "current_step_untracked_ok": validation["current_step_untracked_ok"],
            "expected_untracked_during_run": validation["expected_untracked_during_run"],
            "actual_untracked_during_run": validation["actual_untracked_during_run"],
            "source_statuses": validation["source_statuses"],
            "clean_baseline": validation["clean_baseline"],
        },
        "dependency_surface": dependency_surface,
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
        "stage_recommended_now": False,
        "commit_recommended_now": False,
        "runtime_action_recommended_now": False,
        "capital_action_recommended_now": False,
        "holdout_action_recommended_now": False,
        "strategy_research_recommended_now": False,
        "candidate_generation_recommended_now": False,
        "candidate_release_recommended_now": False,
        "family_release_recommended_now": False,
        "runtime_touched": False,
        "launcher_executed": False,
        "capital_changed": False,
        "live_or_real_orders": False,
        "holdout_accessed": False,
        "backup_deleted": False,
        "gitignore_changed": False,
        "git_add_force_used": False,
    }

    latest_json = OUT_DIR / "repo_only_dependency_surface_refresh_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_dependency_surface_refresh_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "repo_only_dependency_surface_refresh_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY DEPENDENCY SURFACE REFRESH v1",
        "=" * 100,
        f"dependency_surface_status: {payload['dependency_surface_status']}",
        f"severity: {payload['severity']}",
        f"final_decision: {payload['final_decision']}",
        f"next_action: {payload['next_action']}",
        f"next_module: {payload['next_module']}",
        f"reason: {payload['reason']}",
        f"critical_issue_count: {payload['critical_issue_count']}",
        f"warning_count: {payload['warning_count']}",
        "",
        "VALIDATION CHECKS",
        "-" * 100,
        json.dumps(validation["checks"], indent=2, sort_keys=True),
        "",
        "ERRORS",
        "-" * 100,
        json.dumps(errors, indent=2, sort_keys=True),
        "",
        "DEPENDENCY SURFACE SUMMARY",
        "-" * 100,
        json.dumps(dependency_surface["surface_summary"], indent=2, sort_keys=True),
        "",
        "INVARIANTS",
        "-" * 100,
        json.dumps(dependency_surface["invariants"], indent=2, sort_keys=True),
        "",
        "SAFETY",
        "-" * 100,
        json.dumps(SAFETY_FLAGS, indent=2, sort_keys=True),
        "",
        "GIT STATE",
        "-" * 100,
        json.dumps(validation["git_state"], indent=2, sort_keys=True),
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