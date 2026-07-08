from __future__ import annotations

import ast
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_framework_consolidation_plan_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_framework_consolidation_plan_v1.py"
EXPECTED_HEAD = "d897f2e"
OUT_DIR = LAB_ROOT / MODULE_NAME

GOVERNANCE_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_governance_loop_runner_v1"
    / "repo_only_governance_loop_runner_v1_latest.json"
)
GOVERNANCE_POST_CHECK_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_governance_loop_runner_v1_post_commit_check"
    / "repo_only_governance_loop_runner_post_commit_check_latest.json"
)
REQUIRED_GOVERNANCE_STATUS = "REPO_ONLY_GOVERNANCE_LOOP_DETECTED"
REQUIRED_GOVERNANCE_POST_CHECK_STATUS = "REPO_ONLY_GOVERNANCE_LOOP_RUNNER_POST_COMMIT_CHECK_PASS"

NEXT_ACTION = "BUILD_REPO_ONLY_FRAMEWORK_CONSOLIDATION_CONTRACT_V1"
NEXT_MODULE = "edge_factory_os_repo_only_framework_consolidation_contract_v1.py"

LOOP_KINDS = [
    "next_action_selector",
    "development_queue_selector",
    "development_backlog_refresh",
]

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
    "repo_only_framework_consolidation_plan_only": True,
    "repo_only_contract_module_recommended_next": True,
    "no_apply_in_this_module": True,
    "read_only_recent_artifact_scan_allowed": True,
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
    if isinstance(obj.get("framework_consolidation_plan_status"), str):
        return obj["framework_consolidation_plan_status"]
    if isinstance(obj.get("governance_loop_status"), str):
        return obj["governance_loop_status"]
    if isinstance(obj.get("audit_status"), str):
        return obj["audit_status"]
    if isinstance(obj.get("status"), str):
        return obj["status"]
    for key, value in obj.items():
        if key.endswith("_status") and isinstance(value, str):
            return value
    return None


def classify_kind(text: str) -> Optional[str]:
    lowered = text.lower()
    if "next_action_selector" in lowered:
        return "next_action_selector"
    if "development_queue_selector" in lowered:
        return "development_queue_selector"
    if "development_backlog_refresh" in lowered:
        return "development_backlog_refresh"
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


def safe_load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return load_json(path)
    except Exception:
        return None


def recent_repo_only_json_records(limit: int = 180) -> List[Dict[str, Any]]:
    paths: List[Path] = []
    for path in LAB_ROOT.rglob("*.json"):
        text = str(path).lower()
        if "holdout" in text or MODULE_NAME in text:
            continue
        if not any(kind in text for kind in LOOP_KINDS):
            continue
        paths.append(path)
    paths = sorted(paths, key=lambda item: item.stat().st_mtime, reverse=True)[:limit]

    records: List[Dict[str, Any]] = []
    for path in paths:
        obj = safe_load_json(path)
        if obj is None:
            continue
        status = first_status(obj)
        own_text = " ".join(part for part in [str(path), status] if isinstance(part, str))
        kind = classify_kind(own_text)
        if kind is None:
            continue
        records.append(
            {
                "path": str(path),
                "parent": str(path.parent),
                "kind": kind,
                "status": status,
                "critical_issue_count": obj.get("critical_issue_count"),
                "next_module": obj.get("next_module"),
                "final_decision": obj.get("final_decision"),
                "is_post_check": "post_commit_check" in str(path).lower()
                or (isinstance(status, str) and "POST_COMMIT_CHECK" in status),
                "mtime": path.stat().st_mtime,
            }
        )
    return records


def dedupe_by_parent(records: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    newest_by_parent: Dict[str, Dict[str, Any]] = {}
    for record in records:
        parent = record["parent"]
        if parent not in newest_by_parent or record["mtime"] > newest_by_parent[parent]["mtime"]:
            newest_by_parent[parent] = record
    return sorted(newest_by_parent.values(), key=lambda item: item["mtime"])


def count_adjacent_cycles(kinds: List[str]) -> int:
    best = 0
    for start in range(len(kinds)):
        count = 0
        index = start
        while kinds[index : index + len(LOOP_KINDS)] == LOOP_KINDS:
            count += 1
            index += len(LOOP_KINDS)
        best = max(best, count)
    return best


def module_name_evidence() -> Dict[str, Any]:
    tracked_tools = [
        line.strip().replace("\\", "/")
        for line in run_cmd(["git", "ls-files", "tools/*.py"]).stdout.splitlines()
        if line.strip()
    ]
    relevant = [path for path in tracked_tools if classify_kind(path)]
    counts = Counter(classify_kind(path) for path in relevant)
    long_names = [
        path
        for path in relevant
        if path.count("backlog") >= 4 or ("standard_os_status" in path and len(Path(path).name) > 110)
    ]
    return {
        "tracked_repetitive_module_count": len(relevant),
        "kind_counts": {kind: counts.get(kind, 0) for kind in LOOP_KINDS},
        "long_repetitive_name_count": len(long_names),
        "sample_long_repetitive_names": sorted(long_names)[-12:],
    }


def explosion_evidence() -> Dict[str, Any]:
    records = recent_repo_only_json_records()
    post_records = [record for record in records if record["is_post_check"]]
    clean_post_records = [
        record
        for record in post_records
        if record.get("critical_issue_count") == 0
        and isinstance(record.get("status"), str)
        and "POST_COMMIT_CHECK_PASS" in record["status"]
    ]
    deduped_post = dedupe_by_parent(clean_post_records)
    post_kinds = [record["kind"] for record in deduped_post]
    post_tail = post_kinds[-18:]
    json_counts = Counter(record["kind"] for record in records)
    clean_post_counts = Counter(record["kind"] for record in clean_post_records)
    modules = module_name_evidence()
    adjacent_cycle_count = count_adjacent_cycles(post_tail)
    missing: List[str] = []
    for kind in LOOP_KINDS:
        if modules["kind_counts"].get(kind, 0) < 3:
            missing.append(f"tracked module names include fewer than 3 {kind} files")
        if json_counts.get(kind, 0) < 2:
            missing.append(f"recent repo-only JSON outputs include fewer than 2 {kind} records")
        if clean_post_counts.get(kind, 0) < 2:
            missing.append(f"recent clean post-check outputs include fewer than 2 {kind} records")
    if modules["long_repetitive_name_count"] < 6:
        missing.append("tracked module names do not include at least 6 long repetitive selector/queue/backlog names")
    if adjacent_cycle_count < 2:
        missing.append("recent clean post-check outputs do not show at least two adjacent selector -> queue -> backlog cycles")

    return {
        "evidence_complete": not missing,
        "missing_evidence": missing,
        "module_name_evidence": modules,
        "recent_json_evidence": {
            "recent_json_record_count": len(records),
            "recent_post_check_record_count": len(post_records),
            "clean_post_check_record_count": len(clean_post_records),
            "json_kind_counts": {kind: json_counts.get(kind, 0) for kind in LOOP_KINDS},
            "clean_post_check_kind_counts": {kind: clean_post_counts.get(kind, 0) for kind in LOOP_KINDS},
            "deduped_post_check_kind_sequence_tail": post_tail,
            "adjacent_cycle_count": adjacent_cycle_count,
            "sample_recent_records": list(reversed(records[:18])),
        },
    }


def validate_governance_inputs(errors: List[str]) -> Dict[str, Any]:
    loaded: Dict[str, Any] = {}
    for key, path in {
        "governance_loop_runner": GOVERNANCE_JSON,
        "governance_loop_runner_post_check": GOVERNANCE_POST_CHECK_JSON,
    }.items():
        if not path.exists():
            errors.append(f"missing required governance evidence: {path}")
            continue
        try:
            loaded[key] = load_json(path)
        except Exception as exc:
            errors.append(f"unreadable governance evidence {path}: {exc!r}")

    runner = loaded.get("governance_loop_runner", {})
    post = loaded.get("governance_loop_runner_post_check", {})
    if runner:
        if runner.get("governance_loop_status") != REQUIRED_GOVERNANCE_STATUS:
            errors.append(f"governance loop status mismatch: {runner.get('governance_loop_status')}")
        if runner.get("next_module") != "edge_factory_os_repo_only_framework_consolidation_plan_v1.py":
            errors.append(f"governance loop next_module mismatch: {runner.get('next_module')}")
        if runner.get("critical_issue_count") != 0:
            errors.append(f"governance loop critical_issue_count not zero: {runner.get('critical_issue_count')}")
    if post:
        if post.get("audit_status") != REQUIRED_GOVERNANCE_POST_CHECK_STATUS:
            errors.append(f"governance post-check status mismatch: {post.get('audit_status')}")
        if post.get("latest_commit") != EXPECTED_HEAD:
            errors.append(f"governance post-check latest_commit mismatch: expected={EXPECTED_HEAD} actual={post.get('latest_commit')}")
        if post.get("next_module") != "edge_factory_os_repo_only_framework_consolidation_plan_v1.py":
            errors.append(f"governance post-check next_module mismatch: {post.get('next_module')}")
        if post.get("critical_issue_count") != 0:
            errors.append(f"governance post-check critical_issue_count not zero: {post.get('critical_issue_count')}")

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
    if tracked_python["tracked_python_file_count"] != 521:
        errors.append(f"tracked Python count mismatch before new file is tracked: expected=521 actual={tracked_python['tracked_python_file_count']}")

    governance = validate_governance_inputs(errors)
    evidence = explosion_evidence()
    if not evidence["evidence_complete"]:
        errors.extend(f"module explosion evidence missing: {item}" for item in evidence["missing_evidence"])

    physical_after = physical_guard_snapshot()
    if physical_after["planned_schema_file_existing_count"] != 0:
        errors.append(f"planned schema files existed after run: {physical_after['existing_planned_schema_files']}")

    return {
        "errors": errors,
        "git_state": git_state,
        "expected_untracked_during_run": expected_untracked,
        "tracked_python_validation": tracked_python,
        "governance_inputs": governance,
        "module_explosion_evidence": evidence,
        "physical_before": physical_before,
        "physical_after": physical_after,
    }


def build_plan(validation: Dict[str, Any]) -> Dict[str, Any]:
    evidence = validation["module_explosion_evidence"]
    return {
        "problem_summary": {
            "summary": "Repo-only governance has been producing a new Python module for each selector, queue, and backlog step, with each name carrying accumulated context. The result is repetitive tooling growth instead of a stable framework path.",
            "tracked_repetitive_module_count": evidence["module_name_evidence"]["tracked_repetitive_module_count"],
            "long_repetitive_name_count": evidence["module_name_evidence"]["long_repetitive_name_count"],
            "clean_post_check_record_count": evidence["recent_json_evidence"]["clean_post_check_record_count"],
        },
        "repeated_pattern_detected": {
            "sequence": LOOP_KINDS,
            "adjacent_cycle_count": evidence["recent_json_evidence"]["adjacent_cycle_count"],
            "recent_post_check_kind_sequence_tail": evidence["recent_json_evidence"]["deduped_post_check_kind_sequence_tail"],
            "kind_counts": evidence["recent_json_evidence"]["clean_post_check_kind_counts"],
        },
        "modules_to_stop_generating": [
            "edge_factory_os_repo_only_next_action_selector_after_*_v1.py",
            "edge_factory_os_repo_only_development_queue_selector_after_*_v1.py",
            "edge_factory_os_repo_only_development_backlog_refresh_after_*_v1.py",
        ],
        "proposed_generic_runner_design": {
            "runner_module_family": "edge_factory_os_repo_only_framework_governance_runner_v1.py",
            "responsibility": "Use one stable runner to evaluate repo-only governance state, select next repo-only plan/contract steps, and produce standard JSON/TXT outputs without creating a fresh module per transition.",
            "core_components": [
                "static safety flag registry with all dangerous flags explicitly false by default",
                "physical guard snapshot helper reused for planned schema absence and no runtime/launcher/capital/holdout/file-move/file-delete actions",
                "input evidence loader for latest approved JSON and post-check outputs",
                "config-driven transition table for selector, queue, backlog, plan, and contract states",
                "fail-closed validator that reports exact missing evidence instead of selecting a new one-off module",
            ],
            "output_contract": [
                "status",
                "final_decision",
                "next_action",
                "next_module",
                "critical_issue_count",
                "validation",
                "physical_guards",
                "safety_flags",
            ],
        },
        "proposed_config_driven_flow": {
            "configuration_shape": {
                "states": "named repo-only governance states",
                "required_inputs": "latest JSON/post-check files and expected statuses",
                "guards": "HEAD, clean git, tracked Python syntax/BOM, planned schema absence, dangerous flags false",
                "allowed_next": "plan or contract modules only until explicit future approval",
                "blocked_actions": "runtime, launcher, schema apply/create/edit, strategy research, holdout, candidates, capital/live/real orders, file move/delete/restructure",
            },
            "transition_policy": [
                "selector/queue/backlog loop is represented as data, not as new Python file names",
                "new modules are reserved for governance milestones such as plan and contract records",
                "apply modules are not selected until a future explicit approval gate exists and passes",
            ],
        },
        "migration_plan_read_only": [
            "Inventory existing selector, queue, and backlog modules and outputs without modifying them.",
            "Define the consolidation contract that fixes required inputs, statuses, guards, and output fields.",
            "Build a future generic runner preview module that reads the contract and emits a no-apply dry-run decision.",
            "Compare generic runner output with recent one-off outputs to confirm behavioral parity.",
            "Only after separate explicit approval, plan a deprecation/indexing step for old one-off modules; do not delete or move them in this plan.",
        ],
        "required_future_approval_gates": [
            "explicit approval to create the consolidation contract module",
            "explicit approval before creating any generic runner implementation",
            "explicit approval before modifying framework files",
            "explicit approval before adding or editing schema files",
            "explicit approval before any apply, migration, deletion, move, or restructure step",
        ],
        "risks": [
            "A generic runner could hide state-specific assumptions if the contract is too loose.",
            "Old one-off outputs may contain naming-specific expectations that need read-only compatibility checks.",
            "A premature apply step could change governance behavior without enough audit evidence.",
            "Leaving all old modules in place may keep repo size high until a separately approved cleanup plan exists.",
        ],
        "blocked_actions": [
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
        ],
        "next_recommended_module": NEXT_MODULE,
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
    plan = build_plan(validation)
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "framework_consolidation_plan_status": "REPO_ONLY_FRAMEWORK_CONSOLIDATION_PLAN_V1_READY" if passed else "BLOCKED",
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": "FRAMEWORK_CONSOLIDATION_PLAN_READY_FOR_CONTRACT" if passed else "BLOCKED_REVIEW_FRAMEWORK_CONSOLIDATION_PLAN_EVIDENCE",
        "next_action": NEXT_ACTION if passed else "REVIEW_FRAMEWORK_CONSOLIDATION_PLAN_ERRORS",
        "next_module": NEXT_MODULE if passed else None,
        "reason": "Plan-only consolidation route is ready for a repo-only contract module." if passed else "Framework consolidation plan failed closed because required evidence or guard checks were missing.",
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
            "governance_inputs": {
                key: {
                    "status": first_status(value),
                    "critical_issue_count": value.get("critical_issue_count"),
                    "next_module": value.get("next_module"),
                    "latest_commit": value.get("latest_commit"),
                    "final_decision": value.get("final_decision"),
                }
                for key, value in validation["governance_inputs"].items()
            },
            "module_explosion_evidence": validation["module_explosion_evidence"],
            "physical_before": validation["physical_before"],
            "physical_after": validation["physical_after"],
        },
        "framework_consolidation_plan": plan,
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
    latest_json = OUT_DIR / "repo_only_framework_consolidation_plan_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_framework_consolidation_plan_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_framework_consolidation_plan_v1_latest.txt"
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
