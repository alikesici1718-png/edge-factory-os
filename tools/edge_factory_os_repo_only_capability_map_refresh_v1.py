from __future__ import annotations

import ast
import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_capability_map_refresh_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_repo_only_capability_map_refresh_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "6558b39"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_capability_map_refresh_v1.py"

PANEL_JSON = LAB_ROOT / "edge_factory_os_post_resume_full_governance_panel_refresh_v1" / "post_resume_full_governance_panel_refresh_v1_latest.json"
PANEL_POST_CHECK_JSON = LAB_ROOT / "edge_factory_os_post_resume_full_governance_panel_refresh_post_commit_check" / "post_resume_full_governance_panel_refresh_post_commit_check_latest.json"
INSTANTIATOR_JSON = LAB_ROOT / "edge_factory_os_zero_error_work_order_instantiator_v1" / "zero_error_work_order_instantiator_v1_latest.json"
GOVERNOR_JSON = LAB_ROOT / "edge_factory_os_post_resume_zero_error_governor_panel_v1" / "post_resume_zero_error_governor_panel_v1_latest.json"

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_capability_map_refresh": True,
    "read_only_capability_mapping_only": True,
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


CAPABILITY_KEYWORDS: Dict[str, List[str]] = {
    "audit": ["audit", "inspector", "checker", "check"],
    "governance": ["governance", "governor", "policy", "gate"],
    "work_order": ["work_order", "backlog", "queue", "instantiator"],
    "recovery": ["recovery", "resume", "manifest", "journal"],
    "safety": ["safety", "guard", "lock", "freeze", "quarantine"],
    "error_handling": ["error", "ack", "inventory"],
    "feature_panel": ["feature", "panel"],
    "research": ["research", "scanner", "evaluator", "runner", "contract"],
    "runtime_related": ["runtime", "launcher", "paper", "live", "capital", "order"],
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
        "refresh_status",
        "audit_status",
        "instantiator_status",
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
    if head_subject != "Add post-resume full governance panel refresh":
        errors.append(f"unexpected HEAD commit subject: {head_subject}")

    inputs = {
        "full_governance_panel": (PANEL_JSON, "POST_RESUME_FULL_GOVERNANCE_PANEL_REFRESH_V1_READY", "edge_factory_os_repo_only_capability_map_refresh_v1.py"),
        "full_governance_panel_post_check": (PANEL_POST_CHECK_JSON, "POST_RESUME_FULL_GOVERNANCE_PANEL_REFRESH_POST_COMMIT_CHECK_PASS", "edge_factory_os_repo_only_capability_map_refresh_v1.py"),
        "instantiator": (INSTANTIATOR_JSON, "ZERO_ERROR_WORK_ORDER_INSTANTIATOR_V1_READY", None),
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


def classify_capabilities(rel_paths: List[str]) -> Dict[str, Any]:
    directory_counts: Counter[str] = Counter()
    capability_counts: Counter[str] = Counter()
    capability_examples: Dict[str, List[str]] = defaultdict(list)
    prefix_counts: Counter[str] = Counter()

    for rel in rel_paths:
        p = Path(rel)
        top = p.parts[0] if p.parts else "."
        directory_counts[top] += 1

        stem = p.stem.lower()
        parts = stem.split("_")
        prefix = "_".join(parts[:4]) if len(parts) >= 4 else stem
        prefix_counts[prefix] += 1

        matched = False
        for capability, needles in CAPABILITY_KEYWORDS.items():
            if any(needle in stem for needle in needles):
                capability_counts[capability] += 1
                matched = True
                if len(capability_examples[capability]) < 10:
                    capability_examples[capability].append(rel)

        if not matched:
            capability_counts["uncategorized"] += 1
            if len(capability_examples["uncategorized"]) < 10:
                capability_examples["uncategorized"].append(rel)

    return {
        "tracked_python_file_count": len(rel_paths),
        "directory_counts": dict(sorted(directory_counts.items())),
        "capability_counts": dict(sorted(capability_counts.items())),
        "capability_examples": {k: v for k, v in sorted(capability_examples.items())},
        "top_prefix_counts": dict(prefix_counts.most_common(30)),
    }


def build_capability_map(
    clean_baseline: bool,
    source_statuses: Dict[str, Dict[str, Any]],
    git_state: Dict[str, Any],
    py: Dict[str, Any],
) -> Dict[str, Any]:
    rel_paths = tracked_python_files()
    capability_scan = classify_capabilities(rel_paths)

    return {
        "capability_map_status": "REPO_ONLY_OS_CAPABILITY_MAP_ACTIVE" if clean_baseline else "REPO_ONLY_OS_CAPABILITY_MAP_BLOCKED",
        "capability_map_scope": "REPO_ONLY_GOVERNANCE_DISCOVERY",
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
        "capability_scan": capability_scan,
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
            "step": "BUILD_REPO_ONLY_OS_MODULE_INDEX_REFRESH",
            "module": "edge_factory_os_repo_only_module_index_refresh_v1.py",
            "scope": "REPO_ONLY_GOVERNANCE_DISCOVERY",
            "reason": "Capability categories are mapped; next safe step is a module index refresh with exact module records.",
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

    capability_map = build_capability_map(
        bool(validation["clean_baseline"]) and not safety_errors,
        validation["source_statuses"],
        validation["git_state"],
        validation["tracked_python_validation"],
    )

    if validation["pass"] and capability_map["capability_map_status"] != "REPO_ONLY_OS_CAPABILITY_MAP_ACTIVE":
        errors.append(f"capability map did not become active: {capability_map['capability_map_status']}")

    passed = not errors

    payload = {
        "module": MODULE_NAME,
        "capability_map_status": (
            "REPO_ONLY_OS_CAPABILITY_MAP_REFRESH_V1_READY"
            if passed
            else "REPO_ONLY_OS_CAPABILITY_MAP_REFRESH_V1_BLOCKED"
        ),
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_GOVERNANCE_DISCOVERY",
        "final_decision": (
            "CAPABILITY_MAP_READY_FOR_MODULE_INDEX_REFRESH"
            if passed
            else "KEEP_FREEZE_REVIEW_CAPABILITY_MAP_ERRORS"
        ),
        "next_action": (
            "BUILD_REPO_ONLY_OS_MODULE_INDEX_REFRESH_V1"
            if passed
            else "REVIEW_CAPABILITY_MAP_ERRORS"
        ),
        "next_module": (
            "edge_factory_os_repo_only_module_index_refresh_v1.py"
            if passed
            else None
        ),
        "reason": (
            "Refreshed repo-only OS capability map from tracked Python modules."
            if passed
            else "Repo-only capability map refresh validation failed."
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
        "capability_map": capability_map,
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

    latest_json = OUT_DIR / "repo_only_capability_map_refresh_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_capability_map_refresh_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "repo_only_capability_map_refresh_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY CAPABILITY MAP REFRESH v1",
        "=" * 100,
        f"capability_map_status: {payload['capability_map_status']}",
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
        "CAPABILITY MAP",
        "-" * 100,
        json.dumps(capability_map, indent=2, sort_keys=True),
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