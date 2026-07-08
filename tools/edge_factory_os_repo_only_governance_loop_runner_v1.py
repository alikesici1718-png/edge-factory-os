from __future__ import annotations

import ast
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_governance_loop_runner_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_governance_loop_runner_v1.py"
EXPECTED_HEAD = "4553ca0"
OUT_DIR = LAB_ROOT / MODULE_NAME

NEXT_ACTION = "BUILD_REPO_ONLY_FRAMEWORK_CONSOLIDATION_PLAN_V1"
NEXT_MODULE = "edge_factory_os_repo_only_framework_consolidation_plan_v1.py"

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
    "repo_only_governance_loop_detection_allowed": True,
    "repo_only_framework_consolidation_plan_recommended": True,
    "one_off_module_generation_stopped": True,
    "read_only_recent_artifact_scan_allowed": True,
    "read_only_validation_allowed": True,
}
SAFETY_FLAGS.update({name: False for name in DANGEROUS_FLAGS})

LOOP_KINDS = [
    "next_action_selector",
    "development_queue_selector",
    "development_backlog_refresh",
]
POST_CHECK_STATUS_MARKERS = [
    "POST_COMMIT_CHECK_PASS",
    "post_commit_check",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {args} returncode={result.returncode} stderr={result.stderr}")
    return result


def classify_kind(text: str) -> Optional[str]:
    lowered = text.lower()
    if "next_action_selector" in lowered:
        return "next_action_selector"
    if "development_queue_selector" in lowered:
        return "development_queue_selector"
    if "development_backlog_refresh" in lowered:
        return "development_backlog_refresh"
    return None


def first_status(obj: Dict[str, Any]) -> Optional[str]:
    if isinstance(obj.get("status"), str):
        return obj["status"]
    if isinstance(obj.get("audit_status"), str):
        return obj["audit_status"]
    if isinstance(obj.get("governance_loop_status"), str):
        return obj["governance_loop_status"]
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
    staged = [line for line in dirty_tracked if line[:2] != "  " and line[0] != " "]
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


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def json_text_for_detection(path: Path, obj: Dict[str, Any]) -> str:
    fields: List[str] = [str(path)]
    for key in ("module", "next_module", "next_action", "final_decision", "latest_commit"):
        value = obj.get(key)
        if isinstance(value, str):
            fields.append(value)
    commit_paths = obj.get("commit_paths")
    if isinstance(commit_paths, list):
        fields.extend(str(item) for item in commit_paths)
    status = first_status(obj)
    if status:
        fields.append(status)
    return " ".join(fields)


def recent_json_records(limit: int = 160) -> List[Dict[str, Any]]:
    paths: List[Path] = []
    for path in LAB_ROOT.rglob("*.json"):
        path_text = str(path).lower()
        if "holdout" in path_text:
            continue
        if MODULE_NAME in path_text:
            continue
        if any(kind in path_text for kind in LOOP_KINDS):
            paths.append(path)
    paths = sorted(paths, key=lambda item: item.stat().st_mtime, reverse=True)[:limit]

    records: List[Dict[str, Any]] = []
    for path in paths:
        obj = load_json(path)
        if obj is None:
            continue
        status = first_status(obj)
        own_record_text = " ".join(part for part in [str(path), status] if isinstance(part, str))
        detection_text = json_text_for_detection(path, obj)
        kind = classify_kind(own_record_text) or classify_kind(detection_text)
        if kind is None:
            continue
        records.append(
            {
                "path": str(path),
                "parent": str(path.parent),
                "mtime": path.stat().st_mtime,
                "kind": kind,
                "status": status,
                "critical_issue_count": obj.get("critical_issue_count"),
                "next_module": obj.get("next_module"),
                "final_decision": obj.get("final_decision"),
                "is_post_check": "post_commit_check" in str(path).lower() or (
                    isinstance(status, str) and "POST_COMMIT_CHECK" in status
                ),
            }
        )
    return records


def dedupe_records_by_parent(records: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    newest_by_parent: Dict[str, Dict[str, Any]] = {}
    for record in records:
        parent = record["parent"]
        if parent not in newest_by_parent or record["mtime"] > newest_by_parent[parent]["mtime"]:
            newest_by_parent[parent] = record
    return sorted(newest_by_parent.values(), key=lambda item: item["mtime"])


def count_adjacent_cycles(kinds: List[str]) -> int:
    cycle = LOOP_KINDS
    best = 0
    for start in range(len(kinds)):
        count = 0
        index = start
        while kinds[index : index + len(cycle)] == cycle:
            count += 1
            index += len(cycle)
        best = max(best, count)
    return best


def git_module_name_evidence() -> Dict[str, Any]:
    tracked = [
        line.strip().replace("\\", "/")
        for line in run_cmd(["git", "ls-files", "tools/*.py"]).stdout.splitlines()
        if line.strip()
    ]
    relevant = [path for path in tracked if classify_kind(path)]
    counts = Counter(classify_kind(path) for path in relevant)
    long_name_paths = [
        path
        for path in relevant
        if path.count("backlog") >= 4 or path.count("standard_os_status") >= 1 and len(Path(path).name) > 110
    ]
    return {
        "tracked_relevant_module_count": len(relevant),
        "kind_counts": {kind: counts.get(kind, 0) for kind in LOOP_KINDS},
        "long_repetitive_name_count": len(long_name_paths),
        "sample_long_repetitive_names": sorted(long_name_paths)[-12:],
        "previous_approved_next_module_present": (
            "tools/edge_factory_os_repo_only_next_action_selector_after_standard_os_status_backlog_status_backlog_backlog_backlog_backlog_refresh_v1.py"
            in tracked
        ),
        "requested_long_next_module_absent": (
            "tools/edge_factory_os_repo_only_next_action_selector_after_standard_os_status_backlog_status_backlog_backlog_backlog_backlog_backlog_refresh_v1.py"
            not in tracked
        ),
    }


def detect_governance_loop() -> Dict[str, Any]:
    module_evidence = git_module_name_evidence()
    json_records = recent_json_records()
    post_records = [record for record in json_records if record["is_post_check"]]
    post_deduped = dedupe_records_by_parent(post_records)
    post_kinds = [record["kind"] for record in post_deduped]
    recent_post_kinds = post_kinds[-18:]
    cycle_count = count_adjacent_cycles(recent_post_kinds)
    json_kind_counts = Counter(record["kind"] for record in json_records)
    clean_post_checks = [
        record
        for record in post_records
        if record.get("critical_issue_count") == 0
        and isinstance(record.get("status"), str)
        and any(marker in record["status"] or marker in record["path"] for marker in POST_CHECK_STATUS_MARKERS)
    ]
    clean_post_kind_counts = Counter(record["kind"] for record in clean_post_checks)

    missing_evidence: List[str] = []
    for kind in LOOP_KINDS:
        if module_evidence["kind_counts"].get(kind, 0) < 3:
            missing_evidence.append(f"tracked module names include fewer than 3 {kind} files")
        if json_kind_counts.get(kind, 0) < 2:
            missing_evidence.append(f"recent JSON artifacts include fewer than 2 {kind} records")
        if clean_post_kind_counts.get(kind, 0) < 2:
            missing_evidence.append(f"recent clean post-check JSON artifacts include fewer than 2 {kind} records")
    if module_evidence["long_repetitive_name_count"] < 6:
        missing_evidence.append("tracked module names do not show at least 6 long repetitive backlog/selector names")
    if cycle_count < 2:
        missing_evidence.append("recent clean post-check order does not contain two adjacent next_action_selector -> development_queue_selector -> development_backlog_refresh cycles")

    detected = not missing_evidence
    return {
        "loop_detected": detected,
        "missing_evidence": missing_evidence,
        "module_name_evidence": module_evidence,
        "recent_json_evidence": {
            "recent_json_record_count": len(json_records),
            "recent_post_check_record_count": len(post_records),
            "clean_post_check_record_count": len(clean_post_checks),
            "json_kind_counts": {kind: json_kind_counts.get(kind, 0) for kind in LOOP_KINDS},
            "clean_post_check_kind_counts": {kind: clean_post_kind_counts.get(kind, 0) for kind in LOOP_KINDS},
            "deduped_post_check_kind_sequence_tail": recent_post_kinds,
            "adjacent_cycle_count": cycle_count,
            "sample_recent_records": list(reversed(json_records[:18])),
        },
    }


def validate_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    physical_before = physical_guard_snapshot()
    git_state = get_git_state()
    target_path = REPO_ROOT / CURRENT_TOOL_REL
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
    if tracked_python["tracked_python_file_count"] != 520:
        errors.append(f"tracked Python count mismatch before new file is tracked: expected=520 actual={tracked_python['tracked_python_file_count']}")

    loop_detection = detect_governance_loop()
    if not loop_detection["loop_detected"]:
        errors.extend(f"loop evidence missing: {item}" for item in loop_detection["missing_evidence"])

    physical_after = physical_guard_snapshot()
    if physical_after["planned_schema_file_existing_count"] != 0:
        errors.append(f"planned schema files existed after run: {physical_after['existing_planned_schema_files']}")

    return {
        "errors": errors,
        "git_state": git_state,
        "expected_untracked_during_run": expected_untracked,
        "physical_before": physical_before,
        "physical_after": physical_after,
        "tracked_python_validation": tracked_python,
        "loop_detection": loop_detection,
    }


def build_payload(validation: Dict[str, Any]) -> Dict[str, Any]:
    errors = list(validation["errors"])
    safety_type_errors = [key for key, value in SAFETY_FLAGS.items() if not isinstance(value, bool)]
    if safety_type_errors:
        errors.append(f"safety flags are not boolean: {safety_type_errors}")
    dangerous_true = [key for key in DANGEROUS_FLAGS if SAFETY_FLAGS.get(key) is not False]
    if dangerous_true:
        errors.append(f"dangerous flags are not explicitly false: {dangerous_true}")

    detected = not errors and validation["loop_detection"]["loop_detected"]
    governance_loop_status = "REPO_ONLY_GOVERNANCE_LOOP_DETECTED" if detected else "BLOCKED"
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "governance_loop_status": governance_loop_status,
        "severity": "ATTENTION" if detected else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": "STOP_ONE_OFF_MODULE_EXPLOSION_BUILD_CONSOLIDATION_PLAN" if detected else "BLOCKED_REVIEW_MISSING_LOOP_EVIDENCE",
        "next_action": NEXT_ACTION if detected else "REVIEW_GOVERNANCE_LOOP_DETECTION_EVIDENCE",
        "next_module": NEXT_MODULE if detected else None,
        "reason": (
            "Repeated repo-only next_action_selector -> development_queue_selector -> development_backlog_refresh cycle detected from tracked module names and recent post-check JSON outputs."
            if detected
            else "Governance loop detector failed closed because required evidence or guard checks were missing."
        ),
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
            "physical_before": validation["physical_before"],
            "physical_after": validation["physical_after"],
            "loop_detection": validation["loop_detection"],
        },
        "governance_consolidation_route": {
            "one_off_module_generation_stopped": detected,
            "detected_sequence": LOOP_KINDS,
            "blocked_repetitive_next_module": (
                "edge_factory_os_repo_only_next_action_selector_after_standard_os_status_backlog_status_backlog_backlog_backlog_backlog_backlog_refresh_v1.py"
            ),
            "replacement_next_module": NEXT_MODULE if detected else None,
            "replacement_next_action": NEXT_ACTION if detected else None,
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
    latest_json = OUT_DIR / "repo_only_governance_loop_runner_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_governance_loop_runner_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_governance_loop_runner_v1_latest.txt"
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
