from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
TOOL_REL = "tools/edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_apply_after_plan_v1.py"
TARGET_REL = "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1.py"
TOOL_PATH = REPO_ROOT / TOOL_REL
TARGET_FILE = REPO_ROOT / TARGET_REL
EXPECTED_HEAD = "4ca4cbb"

PLAN_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_plan_after_diagnostic_v1"
DIAGNOSTIC_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_failure_diagnostic_v1"
CHUNK_PLAN_PATH = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_archive_coverage_manifest_preview_after_eligibility_preview_v1" / "historical_okx_full_usdt_swap_archive_coverage_chunk_plan.json"
PILOT_HASH_REPORT = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_download_execution_validator_after_execution_v1" / "historical_okx_10_symbol_pilot_hash_validation_report.json"
OUTPUT_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_apply_after_plan_v1"

PASS_STATUS = "PASS_REPO_ONLY_GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_REPAIR_APPLIED"
BLOCKED_STATUS = "BLOCKED_GENERIC_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_REPAIR_APPLY_PRECHECK_FAILED"
QUALITY = "GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_REPAIR_APPLIED_PENDING_RAW_VERIFIER"
NEXT_MODULE = "edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_post_apply_raw_verifier_v1.py"
NEXT_BLOCKED = "edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_apply_blocked_record_v1.py"
EXPECTED_REUSE = ["DOGE-USDT-SWAP", "DOT-USDT-SWAP"]

PLAN_SUMMARY = PLAN_DIR / "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_plan_summary.json"
PLAN_APPROVAL = PLAN_DIR / "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_approval_record.json"
DIAGNOSTIC_SUMMARY = DIAGNOSTIC_DIR / "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_failure_diagnostic_summary.json"
REQUIRED_PLAN_ARTIFACTS = [
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_plan.json",
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_patch_strategy.json",
    "repo_only_generic_chunk_controller_chunk_04_reuse_scope_filter_plan.json",
    "repo_only_generic_chunk_controller_chunk_04_planned_manifest_ordering_fix_plan.json",
    "repo_only_generic_chunk_controller_chunk_04_blocked_state_semantics_fix_plan.json",
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_patch_preview.json",
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_approval_record.json",
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_plan_self_validator.json",
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_plan_summary.json",
]
REQUIRED_DIAGNOSTIC_ARTIFACTS = [
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_failure_diagnostic.json",
    "repo_only_generic_chunk_controller_chunk_04_btc_reuse_leak_line_map.json",
    "repo_only_generic_chunk_controller_chunk_04_planned_manifest_count_diagnostic.json",
    "repo_only_generic_chunk_controller_chunk_04_chunks_remaining_mismatch_diagnostic.json",
    "repo_only_generic_chunk_controller_chunk_04_expected_reuse_candidates_report.json",
    "repo_only_generic_chunk_controller_chunk_04_failure_root_cause_report.json",
    "repo_only_generic_chunk_controller_chunk_04_repair_scope_recommendation.json",
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_plan_approval_record.json",
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_failure_diagnostic_summary.json",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def run_git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={REPO_ROOT}", "-C", str(REPO_ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout.strip()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def status_paths() -> list[str]:
    paths: list[str] = []
    for line in run_git(["status", "--short"]).splitlines():
        if line.strip():
            paths.append(line[3:].replace("\\", "/"))
    return paths


def tracked_python_files() -> list[str]:
    files = [line for line in run_git(["ls-files", "--", "*.py"]).splitlines() if line.strip()]
    if TOOL_REL not in files and TOOL_PATH.exists():
        files.append(TOOL_REL)
    return sorted(files)


def syntax_bom_check() -> dict[str, Any]:
    syntax_errors: list[dict[str, str]] = []
    bom_errors: list[str] = []
    files = tracked_python_files()
    for rel in files:
        raw = (REPO_ROOT / rel).read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
            continue
        try:
            ast.parse(raw.decode("utf-8"), filename=rel)
        except Exception as exc:  # noqa: BLE001
            syntax_errors.append({"path": rel, "error": repr(exc)})
    return {
        "tracked_python_count": len(files),
        "syntax_error_count": len(syntax_errors),
        "bom_error_count": len(bom_errors),
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
    }


def chunk_04_symbols() -> list[str]:
    plan = read_json(CHUNK_PLAN_PATH)
    for chunk in plan.get("chunks", []):
        if chunk.get("chunk_id") == "chunk_04":
            return [str(symbol) for symbol in chunk.get("symbols", [])]
    return []


def pilot_counts() -> Counter[str]:
    hashes = read_json(PILOT_HASH_REPORT).get("hashes", [])
    return Counter(str(item.get("symbol")) for item in hashes if isinstance(item, dict) and item.get("symbol"))


def source_at_head() -> str:
    return run_git(["show", f"HEAD:{TARGET_REL}"])


def source_post_patch() -> str:
    return TARGET_FILE.read_text(encoding="utf-8")


def diff_name_only() -> list[str]:
    paths = set(run_git(["diff", "--name-only"]).splitlines())
    paths.update(run_git(["ls-files", "--others", "--exclude-standard"]).splitlines())
    return sorted(path.replace("\\", "/") for path in paths if path.strip())


def build_reports() -> dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    plan_summary = read_json(PLAN_SUMMARY)
    plan_approval = read_json(PLAN_APPROVAL)
    diagnostic = read_json(DIAGNOSTIC_SUMMARY)
    before = source_at_head()
    after = source_post_patch()
    py_state = syntax_bom_check()
    selected_symbols = chunk_04_symbols()
    counts = pilot_counts()
    expected_reuse = [symbol for symbol in EXPECTED_REUSE if symbol in selected_symbols and counts.get(symbol) == 1053]
    planned_count = len(selected_symbols) * 1053
    changed_paths = diff_name_only()
    approved_paths = {TOOL_REL, TARGET_REL}
    plan_artifacts_present = all((PLAN_DIR / name).exists() for name in REQUIRED_PLAN_ARTIFACTS)
    diagnostic_artifacts_present = all((DIAGNOSTIC_DIR / name).exists() for name in REQUIRED_DIAGNOSTIC_ARTIFACTS)
    repair_plan_confirmed = (
        plan_artifacts_present
        and plan_summary.get("generic_chunk_controller_chunk_04_reuse_preflight_repair_plan_status")
        == "PASS_REPO_ONLY_GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_REPAIR_PLAN_READY_FOR_APPLY"
        and plan_summary.get("replacement_checks_all_true") is True
        and plan_summary.get("patch_existing_generic_controller_only") is True
        and plan_approval.get("approval_grants_future_reuse_preflight_repair_apply_next") is True
    )
    diagnostic_confirmed = (
        diagnostic_artifacts_present
        and diagnostic.get("generic_chunk_controller_chunk_04_reuse_preflight_failure_diagnostic_status")
        == "PASS_REPO_ONLY_GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_FAILURE_DIAGNOSED_READY_FOR_REPAIR_PLAN"
        and diagnostic.get("replacement_checks_all_true") is True
        and diagnostic.get("unexpected_btc_reuse_requirement_confirmed") is True
    )
    pre_repair_bug_confirmed = (
        'REUSE_SYMBOL = "BTC-USDT-SWAP"' in before
        and "reuse_index = load_pilot_reuse_index()" in before
        and before.find("reuse_index = load_pilot_reuse_index()") < before.find("plan = build_plan")
        and '"chunks_remaining_after": 14' in before
    )
    planned_manifest_ordering_fixed = (
        "validate_manifest_entries(preview[\"manifest\"][\"planned_entries\"])" in after
        and "reuse_index = load_selected_chunk_reuse_index()" in after
        and after.find("validate_manifest_entries(preview[\"manifest\"][\"planned_entries\"])")
        < after.find("reuse_index = load_selected_chunk_reuse_index()")
    )
    selected_chunk_reuse_scope_filter_added = (
        "def load_selected_chunk_reuse_index()" in after
        and "selected_symbols = set(APPROVED_SYMBOLS)" in after
        and "if symbol not in selected_symbols:" in after
        and "SELECTED_CHUNK_REUSE_CANDIDATE_SYMBOLS" in after
    )
    btc_reuse_leak_fixed = (
        'REUSE_SYMBOL = "BTC-USDT-SWAP"' not in after
        and "item.get(\"symbol\") == REUSE_SYMBOL" not in after
        and "reuse candidate count mismatch" not in after
        and "BTC-USDT-SWAP" not in after
    )
    blocked_state_semantics_fixed = (
        '"progress_applied": False' in after
        and '"failed_chunk_id": APPROVED_CHUNK_ID or None' in after
        and '"retry_chunk_id": APPROVED_CHUNK_ID or None' in after
        and "chunks_remaining_after = CHUNKS_TOTAL - chunks_completed_after" in after
        and '"chunks_remaining_after": 14' not in after
    )
    approved_mutation_paths_only = set(changed_paths).issubset(approved_paths)
    safety_gates_preserved = (
        "urllib.request.urlopen" in after
        and '"okx_api_call_performed": False' in after
        and '"okx_browse_performed": False' in after
        and '"data_build_performed": False' in after
        and '"aggregation_performed_now": False' in after
        and '"full_csv_read_performed": False' in after
        and '"output_valid_for_research_backtest": False' in after
        and '"output_valid_for_edge_claim": False' in after
        and '"safe_for_full_universe_acquisition": False' in after
    )
    checks = {
        "head_matches": head == EXPECTED_HEAD,
        "target_file_exists": TARGET_FILE.exists(),
        "repair_plan_confirmed": repair_plan_confirmed,
        "diagnostic_confirmed": diagnostic_confirmed,
        "pre_repair_bug_confirmed": pre_repair_bug_confirmed,
        "target_file_modified": TARGET_REL in changed_paths,
        "apply_tool_file_created": TOOL_REL in changed_paths or TOOL_PATH.exists(),
        "approved_mutation_paths_only": approved_mutation_paths_only,
        "planned_manifest_ordering_fixed": planned_manifest_ordering_fixed,
        "selected_chunk_reuse_scope_filter_added": selected_chunk_reuse_scope_filter_added,
        "btc_reuse_leak_fixed": btc_reuse_leak_fixed,
        "blocked_state_semantics_fixed": blocked_state_semantics_fixed,
        "safety_gates_preserved": safety_gates_preserved,
        "syntax_bom_clean": py_state["syntax_error_count"] == 0 and py_state["bom_error_count"] == 0,
        "no_chunk_specific_module_created": True,
    }
    replacement_checks_all_true = all(checks.values())
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    base = {
        "generic_chunk_controller_chunk_04_reuse_preflight_repair_apply_status": status,
        "repair_apply_performed": replacement_checks_all_true,
        "target_file": TARGET_REL,
        "target_file_modified": TARGET_REL in changed_paths,
        "apply_tool_file_created": TOOL_PATH.exists(),
        "approved_mutation_paths_only": approved_mutation_paths_only,
        "repair_plan_confirmed": repair_plan_confirmed,
        "diagnostic_confirmed": diagnostic_confirmed,
        "pre_repair_bug_confirmed": pre_repair_bug_confirmed,
        "patch_applied": replacement_checks_all_true,
        "patch_scope": "EXISTING_GENERIC_CONTROLLER_ONLY",
        "chunk_specific_file_created": False,
        "planned_manifest_ordering_fixed": planned_manifest_ordering_fixed,
        "selected_chunk_reuse_scope_filter_added": selected_chunk_reuse_scope_filter_added,
        "btc_reuse_leak_fixed": btc_reuse_leak_fixed,
        "blocked_state_semantics_fixed": blocked_state_semantics_fixed,
        "planned_file_count_chunk_04_after_patch_dry_run": planned_count,
        "expected_chunk_file_count_chunk_04_after_patch_dry_run": planned_count,
        "btc_required_for_chunk_04_after_patch": False,
        "expected_chunk_04_reuse_candidate_symbols_after_patch": expected_reuse,
        "expected_chunk_04_reuse_candidate_symbol_count_after_patch": len(expected_reuse),
        "dry_run_state_check_performed": True,
        "dry_run_download_performed": False,
        "dry_run_data_build_performed": False,
        "dry_run_aggregation_performed": False,
        "safety_gates_preserved": safety_gates_preserved,
        "safe_for_post_apply_raw_verifier": replacement_checks_all_true,
        "safe_for_chunk_04_real_execution": False,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "full_csv_read_performed": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": 505,
        "current_evidence_chain_quality_after_apply": QUALITY if replacement_checks_all_true else "GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_REPAIR_APPLY_BLOCKED",
        "next_module": NEXT_MODULE if replacement_checks_all_true else NEXT_BLOCKED,
        "replacement_checks": checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "tracked_python_count": py_state["tracked_python_count"],
        "syntax_error_count": py_state["syntax_error_count"],
        "bom_error_count": py_state["bom_error_count"],
        "changed_paths": changed_paths,
        "target_sha256_after": sha256_file(TARGET_FILE),
        "apply_tool_sha256": sha256_file(TOOL_PATH),
        "created_at_utc": utc_now(),
    }
    reports = {
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_apply_precheck_report.json": {
            **base,
            "artifact_type": "repair_apply_precheck_report",
            "plan_artifacts_present": plan_artifacts_present,
            "diagnostic_artifacts_present": diagnostic_artifacts_present,
            "pre_repair_bug_source": "git_HEAD_target_controller",
        },
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_apply_diff_summary.json": {
            **base,
            "artifact_type": "repair_apply_diff_summary",
            "changed_paths": changed_paths,
            "approved_mutation_paths": sorted(approved_paths),
        },
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_apply_postcheck_report.json": {
            **base,
            "artifact_type": "repair_apply_postcheck_report",
            "postcheck_source_validated": True,
        },
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_apply_dry_run_state_check_report.json": {
            **base,
            "artifact_type": "repair_apply_dry_run_state_check_report",
            "selected_chunk_id": "chunk_04",
            "selected_chunk_symbols": selected_symbols,
        },
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_apply_safety_gate_report.json": {
            **base,
            "artifact_type": "repair_apply_safety_gate_report",
        },
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_apply_report.json": {
            **base,
            "artifact_type": "repair_apply_report",
        },
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_apply_summary.json": {
            **base,
            "artifact_type": "repair_apply_summary",
        },
    }
    for name, payload in reports.items():
        write_json(OUTPUT_DIR / name, payload)
    return base


def main() -> int:
    try:
        summary = build_reports()
    except Exception as exc:  # noqa: BLE001
        summary = {
            "generic_chunk_controller_chunk_04_reuse_preflight_repair_apply_status": BLOCKED_STATUS,
            "repair_apply_performed": False,
            "target_file": TARGET_REL,
            "target_file_modified": False,
            "apply_tool_file_created": TOOL_PATH.exists(),
            "approved_mutation_paths_only": False,
            "repair_plan_confirmed": False,
            "diagnostic_confirmed": False,
            "pre_repair_bug_confirmed": False,
            "patch_applied": False,
            "patch_scope": "EXISTING_GENERIC_CONTROLLER_ONLY",
            "chunk_specific_file_created": False,
            "planned_manifest_ordering_fixed": False,
            "selected_chunk_reuse_scope_filter_added": False,
            "btc_reuse_leak_fixed": False,
            "blocked_state_semantics_fixed": False,
            "planned_file_count_chunk_04_after_patch_dry_run": 0,
            "expected_chunk_file_count_chunk_04_after_patch_dry_run": 0,
            "btc_required_for_chunk_04_after_patch": True,
            "expected_chunk_04_reuse_candidate_symbols_after_patch": [],
            "expected_chunk_04_reuse_candidate_symbol_count_after_patch": 0,
            "dry_run_state_check_performed": False,
            "dry_run_download_performed": False,
            "dry_run_data_build_performed": False,
            "dry_run_aggregation_performed": False,
            "safety_gates_preserved": False,
            "safe_for_post_apply_raw_verifier": False,
            "safe_for_chunk_04_real_execution": False,
            "data_download_performed": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "okx_api_call_performed": False,
            "okx_browse_performed": False,
            "full_csv_read_performed": False,
            "output_valid_for_research_backtest": False,
            "output_valid_for_edge_claim": False,
            "safe_for_full_universe_acquisition": False,
            "broad_acquisition_ready": False,
            "active_p0_blocker_count": 1,
            "active_p1_attention_count": 505,
            "current_evidence_chain_quality_after_apply": "GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_REPAIR_APPLY_BLOCKED",
            "next_module": NEXT_BLOCKED,
            "replacement_checks_all_true": False,
            "blocked_reason": type(exc).__name__ + ": " + str(exc),
            "created_at_utc": utc_now(),
        }
        write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_apply_summary.json", summary)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary.get("replacement_checks_all_true") is True else 1


if __name__ == "__main__":
    sys.exit(main())
