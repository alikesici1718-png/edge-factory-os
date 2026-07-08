from __future__ import annotations

import ast
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_risky_surface_review_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_repo_only_risky_surface_review_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "9403d8c"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_risky_surface_review_v1.py"

DEPENDENCY_JSON = LAB_ROOT / "edge_factory_os_repo_only_dependency_surface_refresh_v1" / "repo_only_dependency_surface_refresh_v1_latest.json"
DEPENDENCY_POST_CHECK_JSON = LAB_ROOT / "edge_factory_os_repo_only_dependency_surface_refresh_post_commit_check" / "repo_only_dependency_surface_refresh_post_commit_check_latest.json"
MODULE_INDEX_JSON = LAB_ROOT / "edge_factory_os_repo_only_module_index_refresh_v1" / "repo_only_module_index_refresh_v1_latest.json"
CAPABILITY_JSON = LAB_ROOT / "edge_factory_os_repo_only_capability_map_refresh_v1" / "repo_only_capability_map_refresh_v1_latest.json"
GOVERNOR_JSON = LAB_ROOT / "edge_factory_os_post_resume_zero_error_governor_panel_v1" / "post_resume_zero_error_governor_panel_v1_latest.json"

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_risky_surface_review": True,
    "read_only_risk_review_only": True,
    "dependency_surface_required": True,
    "module_index_required": True,
    "capability_map_required": True,
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

RISK_TERMS: Dict[str, List[str]] = {
    "runtime": ["runtime", "subprocess", "runpy", "py_compile"],
    "launcher": ["launcher", "autopilot", "scheduler"],
    "capital": ["capital", "allocator", "sizing", "risk_manager"],
    "live_or_orders": ["live", "order", "orders", "execution", "broker"],
    "paper": ["paper"],
    "holdout": ["holdout"],
    "strategy_or_research": ["strategy", "research", "candidate", "scanner", "evaluator", "runner", "contract"],
    "mutation": ["apply", "patch", "repair", "write", "delete", "move", "copy", "shutil"],
}

HIGH_RISK_IMPORT_ROOTS = {
    "subprocess",
    "runpy",
    "py_compile",
    "requests",
    "shutil",
    "os",
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
        "dependency_surface_status",
        "audit_status",
        "module_index_status",
        "capability_map_status",
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
    loaded: Dict[str, Dict[str, Any]] = {}
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
    if head_subject != "Add repo-only dependency surface refresh":
        errors.append(f"unexpected HEAD commit subject: {head_subject}")

    inputs = {
        "dependency_surface": (DEPENDENCY_JSON, "REPO_ONLY_OS_DEPENDENCY_SURFACE_REFRESH_V1_READY", "edge_factory_os_repo_only_risky_surface_review_v1.py"),
        "dependency_surface_post_check": (DEPENDENCY_POST_CHECK_JSON, "REPO_ONLY_DEPENDENCY_SURFACE_REFRESH_POST_COMMIT_CHECK_PASS", "edge_factory_os_repo_only_risky_surface_review_v1.py"),
        "module_index": (MODULE_INDEX_JSON, "REPO_ONLY_OS_MODULE_INDEX_REFRESH_V1_READY", None),
        "capability_map": (CAPABILITY_JSON, "REPO_ONLY_OS_CAPABILITY_MAP_REFRESH_V1_READY", None),
        "governor": (GOVERNOR_JSON, "POST_RESUME_ZERO_ERROR_GOVERNOR_PANEL_V1_READY", None),
    }

    for key, spec in inputs.items():
        path, expected_status, expected_next_module = spec
        obj: Optional[Dict[str, Any]] = None
        record: Optional[Dict[str, Any]] = None

        try:
            obj = load_json(path)
            record = source_record(path, obj)
            loaded[key] = obj
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
        "loaded": loaded,
        "current_step_untracked_ok": current_step_untracked_ok,
        "expected_untracked_during_run": sorted(expected_untracked),
        "actual_untracked_during_run": sorted(actual_untracked),
        "clean_baseline": not errors,
    }


def risk_categories_for_path(path: str) -> List[str]:
    stem = Path(path).stem.lower()
    found = []
    for category, terms in RISK_TERMS.items():
        if any(term in stem for term in terms):
            found.append(category)
    return found


def import_roots_for_dependency_record(record: Dict[str, Any]) -> List[str]:
    imports = record.get("imports", [])
    if not isinstance(imports, list):
        return []
    roots = []
    for item in imports:
        if isinstance(item, dict):
            root = item.get("root")
            if root:
                roots.append(str(root))
    return sorted(set(roots))


def build_risky_surface_review(
    clean_baseline: bool,
    source_statuses: Dict[str, Dict[str, Any]],
    loaded: Dict[str, Dict[str, Any]],
    git_state: Dict[str, Any],
    py: Dict[str, Any],
) -> Dict[str, Any]:
    dependency_payload = loaded.get("dependency_surface", {})
    dependency_surface = dependency_payload.get("dependency_surface", {})
    dependency_records = dependency_surface.get("module_dependency_records", [])

    if not isinstance(dependency_records, list):
        dependency_records = []

    risky_records: List[Dict[str, Any]] = []
    category_counts: Counter[str] = Counter()
    high_risk_import_counts: Counter[str] = Counter()

    for record in dependency_records:
        if not isinstance(record, dict):
            continue

        path = str(record.get("path", ""))
        categories = risk_categories_for_path(path)
        import_roots = import_roots_for_dependency_record(record)
        high_risk_imports = sorted(root for root in import_roots if root in HIGH_RISK_IMPORT_ROOTS)

        if categories or high_risk_imports:
            for category in categories:
                category_counts[category] += 1
            for root in high_risk_imports:
                high_risk_import_counts[root] += 1

            risk_score = len(categories) * 10 + len(high_risk_imports) * 3
            if "runtime" in categories or "launcher" in categories or "capital" in categories or "live_or_orders" in categories:
                risk_score += 10

            risky_records.append(
                {
                    "path": path,
                    "risk_categories": categories,
                    "high_risk_import_roots": high_risk_imports,
                    "import_count": record.get("import_count", 0),
                    "risk_score": risk_score,
                    "review_decision": "REVIEW_ONLY_DO_NOT_TOUCH",
                }
            )

    risky_records = sorted(risky_records, key=lambda x: (-int(x["risk_score"]), x["path"]))

    risk_tiers = {
        "high": [x for x in risky_records if int(x["risk_score"]) >= 25],
        "medium": [x for x in risky_records if 10 <= int(x["risk_score"]) < 25],
        "low": [x for x in risky_records if int(x["risk_score"]) < 10],
    }

    return {
        "risky_surface_status": "REPO_ONLY_OS_RISKY_SURFACE_REVIEW_ACTIVE" if clean_baseline else "REPO_ONLY_OS_RISKY_SURFACE_REVIEW_BLOCKED",
        "risky_surface_scope": "REPO_ONLY_GOVERNANCE_DISCOVERY_REVIEW_ONLY",
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
        "review_summary": {
            "dependency_record_count": len(dependency_records),
            "risky_record_count": len(risky_records),
            "risk_category_counts": dict(sorted(category_counts.items())),
            "high_risk_import_counts": dict(sorted(high_risk_import_counts.items())),
            "high_risk_count": len(risk_tiers["high"]),
            "medium_risk_count": len(risk_tiers["medium"]),
            "low_risk_count": len(risk_tiers["low"]),
            "top_risky_records": risky_records[:50],
        },
        "risk_tiers_sample": {
            "high": risk_tiers["high"][:30],
            "medium": risk_tiers["medium"][:30],
            "low": risk_tiers["low"][:30],
        },
        "review_policy": {
            "direct_fix_allowed": False,
            "runtime_touch_allowed": False,
            "launcher_allowed": False,
            "capital_change_allowed": False,
            "candidate_or_family_release_allowed": False,
            "action": "MAP_ONLY_NEXT_STEP_SHOULD_CREATE_APPROVAL_GATED_REVIEW_PLAN",
        },
        "invariants": {
            "dependency_record_count_matches_surface": len(dependency_records) == dependency_surface.get("surface_summary", {}).get("module_dependency_record_count"),
            "risky_records_are_review_only": all(x.get("review_decision") == "REVIEW_ONLY_DO_NOT_TOUCH" for x in risky_records),
            "no_direct_action_recommended": True,
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
            "direct_fix",
        ],
        "recommended_next_step": {
            "step": "BUILD_REPO_ONLY_APPROVAL_GATED_RISK_REVIEW_PLAN",
            "module": "edge_factory_os_repo_only_approval_gated_risk_review_plan_v1.py",
            "scope": "REPO_ONLY_GOVERNANCE_PLANNING",
            "reason": "Risky surfaces are mapped; next safe step is an approval-gated plan, not fixes.",
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

    risky_surface = build_risky_surface_review(
        bool(validation["clean_baseline"]) and not safety_errors,
        validation["source_statuses"],
        validation["loaded"],
        validation["git_state"],
        validation["tracked_python_validation"],
    )

    if validation["pass"] and risky_surface["risky_surface_status"] != "REPO_ONLY_OS_RISKY_SURFACE_REVIEW_ACTIVE":
        errors.append(f"risky surface review did not become active: {risky_surface['risky_surface_status']}")

    invariants = risky_surface["invariants"]
    if not invariants["dependency_record_count_matches_surface"]:
        errors.append("dependency_record_count does not match source dependency surface")
    if not invariants["risky_records_are_review_only"]:
        errors.append("risky records are not all review-only")
    if not invariants["no_direct_action_recommended"]:
        errors.append("direct action recommended unexpectedly")

    passed = not errors

    payload = {
        "module": MODULE_NAME,
        "risky_surface_status": (
            "REPO_ONLY_OS_RISKY_SURFACE_REVIEW_V1_READY"
            if passed
            else "REPO_ONLY_OS_RISKY_SURFACE_REVIEW_V1_BLOCKED"
        ),
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_GOVERNANCE_DISCOVERY_REVIEW_ONLY",
        "final_decision": (
            "RISKY_SURFACE_REVIEW_READY_FOR_APPROVAL_GATED_PLAN"
            if passed
            else "KEEP_FREEZE_REVIEW_RISKY_SURFACE_ERRORS"
        ),
        "next_action": (
            "BUILD_REPO_ONLY_APPROVAL_GATED_RISK_REVIEW_PLAN_V1"
            if passed
            else "REVIEW_RISKY_SURFACE_ERRORS"
        ),
        "next_module": (
            "edge_factory_os_repo_only_approval_gated_risk_review_plan_v1.py"
            if passed
            else None
        ),
        "reason": (
            "Reviewed risky repo surfaces from dependency map without recommending direct changes."
            if passed
            else "Repo-only risky surface review validation failed."
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
        "risky_surface_review": risky_surface,
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

    latest_json = OUT_DIR / "repo_only_risky_surface_review_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_risky_surface_review_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "repo_only_risky_surface_review_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY RISKY SURFACE REVIEW v1",
        "=" * 100,
        f"risky_surface_status: {payload['risky_surface_status']}",
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
        "RISKY SURFACE SUMMARY",
        "-" * 100,
        json.dumps(risky_surface["review_summary"], indent=2, sort_keys=True),
        "",
        "INVARIANTS",
        "-" * 100,
        json.dumps(risky_surface["invariants"], indent=2, sort_keys=True),
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