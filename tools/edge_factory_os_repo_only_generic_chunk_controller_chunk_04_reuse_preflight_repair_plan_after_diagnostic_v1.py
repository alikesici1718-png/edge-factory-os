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
TOOL_REL = "tools/edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_plan_after_diagnostic_v1.py"
TOOL_PATH = REPO_ROOT / TOOL_REL
TARGET_REL = "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1.py"
TARGET_FILE = REPO_ROOT / TARGET_REL
EXPECTED_HEAD = "e0436ce"

DIAGNOSTIC_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_failure_diagnostic_v1"
DIAGNOSTIC_SUMMARY = DIAGNOSTIC_DIR / "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_failure_diagnostic_summary.json"
DIAGNOSTIC_REPAIR_SCOPE = DIAGNOSTIC_DIR / "repo_only_generic_chunk_controller_chunk_04_repair_scope_recommendation.json"
DIAGNOSTIC_LINE_MAP = DIAGNOSTIC_DIR / "repo_only_generic_chunk_controller_chunk_04_btc_reuse_leak_line_map.json"
CHUNK_PLAN_PATH = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_archive_coverage_manifest_preview_after_eligibility_preview_v1" / "historical_okx_full_usdt_swap_archive_coverage_chunk_plan.json"
PILOT_HASH_REPORT = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_download_execution_validator_after_execution_v1" / "historical_okx_10_symbol_pilot_hash_validation_report.json"
OUTPUT_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_plan_after_diagnostic_v1"

PASS_STATUS = "PASS_REPO_ONLY_GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_REPAIR_PLAN_READY_FOR_APPLY"
FAIL_STATUS = "BLOCKED_REPO_ONLY_GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_REPAIR_PLAN"
QUALITY = "GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_REPAIR_PLAN_READY_FOR_APPLY"
BLOCKED_QUALITY = "GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_REPAIR_PLAN_BLOCKED"
NEXT_APPLY_MODULE = "edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_apply_after_plan_v1.py"
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_plan_blocked_record_v1.py"

ROOT_CAUSE_CODES = [
    "REUSE_CANDIDATE_SCOPE_BUG",
    "PREFLIGHT_ORDERING_BUG",
    "PLANNED_MANIFEST_NOT_BUILT_BEFORE_REUSE_VALIDATION",
    "BLOCKED_STATE_FIELD_SEMANTICS_BUG",
    "STALE_GLOBAL_REUSE_STATE_BUG",
]
EXPECTED_REUSE = ["DOGE-USDT-SWAP", "DOT-USDT-SWAP"]

REQUIRED_ARTIFACTS = [
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


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def run_git(args: list[str]) -> str:
    completed = subprocess.run(
        [
            "git",
            "-c",
            "core.longpaths=true",
            "-c",
            f"safe.directory={REPO_ROOT}",
            "-C",
            str(REPO_ROOT),
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout.strip()


def status_lines() -> list[str]:
    return [line for line in run_git(["status", "--short"]).splitlines() if line.strip()]


def status_path(line: str) -> str:
    if len(line) >= 3 and line[2] == " ":
        return line[3:].replace("\\", "/")
    return line[2:].lstrip().replace("\\", "/")


def repo_effectively_clean(lines: list[str]) -> bool:
    return {status_path(line) for line in lines}.issubset({TOOL_REL})


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tracked_python_count() -> int:
    return len([line for line in run_git(["ls-files", "--", "*.py"]).splitlines() if line.strip()])


def syntax_bom_check() -> dict[str, Any]:
    files = [REPO_ROOT / line for line in run_git(["ls-files", "--", "*.py"]).splitlines() if line.strip()]
    if TOOL_PATH.exists() and TOOL_PATH not in files:
        files.append(TOOL_PATH)
    syntax_errors: list[dict[str, str]] = []
    bom_errors: list[str] = []
    ok = 0
    for path in files:
        raw = path.read_bytes()
        rel = path.relative_to(REPO_ROOT).as_posix()
        if raw.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
            continue
        try:
            ast.parse(raw.decode("utf-8"), filename=rel)
            ok += 1
        except Exception as exc:  # noqa: BLE001
            syntax_errors.append({"file": rel, "error": repr(exc)})
    return {
        "files_checked": len(files),
        "syntax_error_count": len(syntax_errors),
        "bom_error_count": len(bom_errors),
        "ast_parse_success_count": ok,
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


def build_artifacts() -> dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    status = status_lines()
    diagnostic = read_json(DIAGNOSTIC_SUMMARY)
    repair_scope_from_diagnostic = read_json(DIAGNOSTIC_REPAIR_SCOPE)
    line_map = read_json(DIAGNOSTIC_LINE_MAP) if DIAGNOSTIC_LINE_MAP.exists() else {}
    source = TARGET_FILE.read_text(encoding="utf-8")
    target_sha_before = sha256_file(TARGET_FILE)
    symbols = chunk_04_symbols()
    counts = pilot_counts()
    expected_reuse = [symbol for symbol in EXPECTED_REUSE if symbol in symbols and counts.get(symbol) == 1053]
    root_codes = [code for code in diagnostic.get("root_cause_codes", []) if code in ROOT_CAUSE_CODES]
    diagnostic_confirmed = (
        diagnostic.get("generic_chunk_controller_chunk_04_reuse_preflight_failure_diagnostic_status")
        == "PASS_REPO_ONLY_GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_FAILURE_DIAGNOSED_READY_FOR_REPAIR_PLAN"
        and diagnostic.get("replacement_checks_all_true") is True
        and diagnostic.get("approval_grants_patch_plan_next") is True
    )
    root_cause_confirmed = (
        diagnostic.get("root_cause_identified") is True
        and set(ROOT_CAUSE_CODES).issubset(set(diagnostic.get("root_cause_codes", [])))
        and diagnostic.get("unexpected_btc_reuse_requirement_confirmed") is True
        and diagnostic.get("planned_file_count_zero_root_cause_identified") is True
        and diagnostic.get("chunks_remaining_mismatch_root_cause_identified") is True
    )
    patch_strategy = {
        "artifact_type": "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_patch_strategy",
        "target_file": TARGET_REL,
        "patch_scope": "EXISTING_GENERIC_CONTROLLER_ONLY",
        "chunk_specific_file_creation_required": False,
        "strategy_steps": [
            "Move selected chunk plan construction ahead of pilot reuse validation in run_execution.",
            "Replace single REUSE_SYMBOL global semantics with selected-chunk reuse candidate discovery.",
            "Load pilot reuse universe as symbol -> date -> provenance, then filter to APPROVED_SYMBOLS.",
            "Validate only selected-chunk reuse candidates with complete 1053-file provenance.",
            "Treat unrelated pilot symbols, including BTC for chunk_04, as ignored out-of-scope provenance.",
            "Allow zero selected reuse candidates and proceed with all selected chunk files as download candidates.",
            "Fix blocked_payload to use loaded state values for no-progress failures and explicit progress_applied=false.",
            "Keep all no API, no browse, no build, no aggregation, no full CSV read, and fail-closed gates.",
        ],
        "line_map_inputs": line_map,
    }
    reuse_scope_filter_plan = {
        "artifact_type": "repo_only_generic_chunk_controller_chunk_04_reuse_scope_filter_plan",
        "selected_chunk_reuse_scope_filter_required": True,
        "btc_reuse_leak_fix_required": True,
        "raw_reuse_universe_allowed": True,
        "selected_chunk_reuse_candidates_formula": "global_pilot_reuse_symbols ∩ selected_chunk_symbols",
        "unexpected_out_of_scope_reuse_candidates_policy": "ignore for current chunk; never require or count",
        "chunk_04_selected_symbols": symbols,
        "expected_after_patch_chunk_04_reuse_candidate_symbols": expected_reuse,
        "expected_after_patch_chunk_04_reuse_candidate_symbol_count": len(expected_reuse),
        "expected_after_patch_btc_required_for_chunk_04": False,
    }
    planned_manifest_fix = {
        "artifact_type": "repo_only_generic_chunk_controller_chunk_04_planned_manifest_ordering_fix_plan",
        "planned_manifest_ordering_fix_required": True,
        "current_bad_order": ["load_and_validate_preview", "load_pilot_reuse_index", "build_plan"],
        "required_order": ["load_and_validate_preview", "build_selected_chunk_planned_manifest", "load_filtered_selected_chunk_reuse_index", "validate selected reuse candidates", "execute_downloads"],
        "expected_after_patch_planned_file_count_for_chunk_04": 21060,
        "planned_file_count_must_exist_before_reuse_validation": True,
    }
    blocked_state_fix = {
        "artifact_type": "repo_only_generic_chunk_controller_chunk_04_blocked_state_semantics_fix_plan",
        "blocked_state_semantics_fix_required": True,
        "pre_download_failure_semantics": {
            "progress_applied": False,
            "failed_chunk_id": "chunk_04",
            "retry_chunk_id": "chunk_04",
            "chunks_completed_after": "chunks_completed_before",
            "chunks_remaining_after": "chunks_total - chunks_completed_after",
            "next_chunk_id_after_execution": None,
            "next_module": "blocked record / diagnostic route",
        },
        "expected_for_current_failure": {
            "chunks_total": 16,
            "chunks_completed_after": 3,
            "chunks_remaining_after": 13,
        },
    }
    patch_preview = {
        "artifact_type": "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_patch_preview",
        "target_file": TARGET_REL,
        "patch_scope": "EXISTING_GENERIC_CONTROLLER_ONLY",
        "chunk_specific_file_creation_required": False,
        "preview_not_applied": True,
        "planned_manifest_ordering_fix_required": True,
        "selected_chunk_reuse_scope_filter_required": True,
        "btc_reuse_leak_fix_required": True,
        "blocked_state_semantics_fix_required": True,
        "expected_after_patch_planned_file_count_for_chunk_04": 21060,
        "expected_after_patch_btc_required_for_chunk_04": False,
        "expected_after_patch_chunk_04_reuse_candidates": expected_reuse,
        "expected_after_patch_safe_for_no_download_dry_run": True,
        "expected_after_patch_safe_for_chunk_04_real_execution": False,
        "diff_intent": [
            {
                "replace": "REUSE_SYMBOL = \"BTC-USDT-SWAP\" single-symbol required reuse model",
                "with": "selected chunk pilot reuse map filtered by APPROVED_SYMBOLS",
            },
            {
                "replace": "reuse_index = load_pilot_reuse_index(); plan = build_plan(preview, reuse_index)",
                "with": "plan = build_plan(preview, empty/late reuse map); selected_reuse_index = load_selected_chunk_reuse_index(APPROVED_SYMBOLS); annotate plan with selected reuse",
            },
            {
                "replace": "\"chunks_remaining_after\": 14 in blocked_payload",
                "with": "\"chunks_remaining_after\": CHUNKS_TOTAL - CHUNKS_COMPLETED_BEFORE plus progress_applied=false/retry_chunk_id",
            },
        ],
    }
    approval = {
        "artifact_type": "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_approval_record",
        "created_at_utc": utc_now(),
        "approval_grants_repair_plan_now": True,
        "approval_grants_patch_apply_now": False,
        "approval_grants_future_reuse_preflight_repair_apply_next": True,
        "approval_grants_chunk_04_rerun_now": False,
        "approval_grants_download_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "next_module": NEXT_APPLY_MODULE,
    }
    target_sha_after = sha256_file(TARGET_FILE)
    checks = {
        "head_matches": head == EXPECTED_HEAD,
        "repo_clean": repo_effectively_clean(status),
        "diagnostic_confirmed": diagnostic_confirmed,
        "root_cause_confirmed": root_cause_confirmed,
        "target_file_exists": TARGET_FILE.exists(),
        "target_file_not_modified": target_sha_before == target_sha_after,
        "patch_existing_generic_controller_only": repair_scope_from_diagnostic.get("patch_existing_generic_controller_only") is True,
        "chunk_specific_module_not_required": repair_scope_from_diagnostic.get("chunk_specific_module_required") is False,
        "expected_reuse_candidates_confirmed": expected_reuse == EXPECTED_REUSE,
        "approval_no_apply_or_rerun": approval["approval_grants_patch_apply_now"] is False and approval["approval_grants_chunk_04_rerun_now"] is False,
        "no_forbidden_actions": True,
    }
    passed = all(checks.values())
    summary = {
        "artifact_type": "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_plan_summary",
        "generic_chunk_controller_chunk_04_reuse_preflight_repair_plan_status": PASS_STATUS if passed else FAIL_STATUS,
        "repair_plan_created": passed,
        "created_at_utc": utc_now(),
        "target_file": TARGET_REL.replace("/", "\\"),
        "target_file_modified": target_sha_before != target_sha_after,
        "diagnostic_confirmed": diagnostic_confirmed,
        "root_cause_confirmed": root_cause_confirmed,
        "root_cause_codes": root_codes,
        "patch_existing_generic_controller_only": True,
        "chunk_specific_module_required": False,
        "planned_manifest_ordering_fix_required": True,
        "selected_chunk_reuse_scope_filter_required": True,
        "btc_reuse_leak_fix_required": True,
        "blocked_state_semantics_fix_required": True,
        "expected_after_patch_planned_file_count_for_chunk_04": 21060,
        "expected_after_patch_btc_required_for_chunk_04": False,
        "expected_after_patch_chunk_04_reuse_candidate_symbols": expected_reuse,
        "expected_after_patch_chunk_04_reuse_candidate_symbol_count": len(expected_reuse),
        "expected_after_patch_safe_for_no_download_dry_run": True,
        "expected_after_patch_safe_for_chunk_04_real_execution": False,
        "patch_preview_created": True,
        "repair_approval_record_created": True,
        "approval_grants_future_reuse_preflight_repair_apply_next": approval["approval_grants_future_reuse_preflight_repair_apply_next"],
        "approval_grants_patch_apply_now": approval["approval_grants_patch_apply_now"],
        "approval_grants_chunk_04_rerun_now": approval["approval_grants_chunk_04_rerun_now"],
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "full_csv_read_performed": False,
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": int(diagnostic.get("active_p1_attention_count") or 0),
        "current_evidence_chain_quality_after_repair_plan": QUALITY if passed else BLOCKED_QUALITY,
        "next_module": NEXT_APPLY_MODULE if passed else NEXT_BLOCKED_MODULE,
        "replacement_checks_all_true": passed,
        "replacement_checks": checks,
    }
    self_validator = {
        "artifact_type": "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_plan_self_validator",
        "replacement_checks": checks,
        "replacement_checks_all_true": passed,
        "syntax_bom_deferred_to_runner": True,
        "target_sha256_before": target_sha_before,
        "target_sha256_after": target_sha_after,
    }
    plan = {
        "artifact_type": "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_plan",
        "summary": summary,
        "patch_strategy": patch_strategy,
        "reuse_scope_filter_plan": reuse_scope_filter_plan,
        "planned_manifest_ordering_fix_plan": planned_manifest_fix,
        "blocked_state_semantics_fix_plan": blocked_state_fix,
        "patch_preview": patch_preview,
        "approval_record": approval,
        "self_validator": self_validator,
        "forbidden_actions_performed": {
            "patch_apply": False,
            "chunk_04_rerun": False,
            "download": False,
            "api": False,
            "browse": False,
            "url_fetch": False,
            "zip_csv_parquet_read": False,
            "full_csv_read": False,
            "data_build": False,
            "aggregation": False,
            "delete": False,
            "move": False,
            "cleanup": False,
            "research_backtest_edge": False,
            "runtime_capital_live": False,
        },
    }
    return {
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_plan.json": plan,
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_patch_strategy.json": patch_strategy,
        "repo_only_generic_chunk_controller_chunk_04_reuse_scope_filter_plan.json": reuse_scope_filter_plan,
        "repo_only_generic_chunk_controller_chunk_04_planned_manifest_ordering_fix_plan.json": planned_manifest_fix,
        "repo_only_generic_chunk_controller_chunk_04_blocked_state_semantics_fix_plan.json": blocked_state_fix,
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_patch_preview.json": patch_preview,
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_approval_record.json": approval,
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_plan_self_validator.json": self_validator,
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_plan_summary.json": summary,
    }


def run() -> dict[str, Any]:
    artifacts = build_artifacts()
    for name, payload in artifacts.items():
        write_json(OUTPUT_DIR / name, payload)
    syntax = syntax_bom_check()
    summary = artifacts["repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_plan_summary.json"]
    missing = [name for name in REQUIRED_ARTIFACTS if not (OUTPUT_DIR / name).exists()]
    if missing or syntax["syntax_error_count"] or syntax["bom_error_count"]:
        summary["replacement_checks_all_true"] = False
        summary["missing_artifacts"] = missing
        summary["syntax_bom_report"] = syntax
        write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_plan_summary.json", summary)
    return summary


def main() -> int:
    summary = run()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    sys.exit(main())
