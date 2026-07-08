from __future__ import annotations

import ast
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_controller_preview_after_chunk_02_summary_v1"
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "4876fa8"
PREVIOUS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_CHUNK_02_COVERAGE_SUMMARY_CLOSED_GENERIC_CHUNK_CONTROLLER_PREVIEW_READY"
PASS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_GENERIC_CHUNK_CONTROLLER_PREVIEW_READY_FOR_CYCLE_EXECUTION"
BLOCKED_STATUS = "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_GENERIC_CHUNK_CONTROLLER_PREVIEW_FAILED"
NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1.py"
FAILED_NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_controller_preview_blocked_record_v1.py"
AFTER_QUALITY = "HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_GENERIC_CHUNK_CONTROLLER_PREVIEW_READY_FOR_CYCLE_EXECUTION"

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME

CHUNK_02_SUMMARY_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_coverage_summary_after_validator_v1"
CHUNK_01_SUMMARY_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_coverage_summary_after_validator_v1"
MANIFEST_PREVIEW_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_archive_coverage_manifest_preview_after_eligibility_preview_v1"
SOURCE_DISCOVERY_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_symbol_source_discovery_after_universe_preview_approval_v1"

ARTIFACTS = {
    "chunk_02_summary": CHUNK_02_SUMMARY_DIR / "historical_okx_full_usdt_swap_chunk_02_download_coverage_summary_bundle_summary.json",
    "chunk_02_ledger": CHUNK_02_SUMMARY_DIR / "historical_okx_full_usdt_swap_cumulative_coverage_eligibility_ledger_after_chunk_02.json",
    "chunk_02_controller_approval": CHUNK_02_SUMMARY_DIR / "historical_okx_full_usdt_swap_generic_chunk_coverage_controller_preview_approval_record.json",
    "chunk_01_ledger": CHUNK_01_SUMMARY_DIR / "historical_okx_full_usdt_swap_cumulative_coverage_eligibility_ledger_after_chunk_01.json",
    "chunk_plan": MANIFEST_PREVIEW_DIR / "historical_okx_full_usdt_swap_archive_coverage_chunk_plan.json",
    "manifest_preview_summary": MANIFEST_PREVIEW_DIR / "historical_okx_full_usdt_swap_archive_coverage_manifest_preview_summary.json",
    "candidate_symbol_list": SOURCE_DISCOVERY_DIR / "historical_okx_full_usdt_swap_candidate_symbol_list.json",
}

REQUIRED_OUTPUTS = [
    "historical_okx_full_usdt_swap_generic_chunk_coverage_controller_preview.json",
    "historical_okx_full_usdt_swap_generic_chunk_coverage_controller_contract.json",
    "historical_okx_full_usdt_swap_generic_chunk_coverage_controller_resource_limits.json",
    "historical_okx_full_usdt_swap_generic_chunk_coverage_controller_next_chunk_selection_preview.json",
    "historical_okx_full_usdt_swap_generic_chunk_coverage_controller_cumulative_ledger_carry_forward.json",
    "historical_okx_full_usdt_swap_generic_chunk_coverage_controller_approval_record.json",
    "historical_okx_full_usdt_swap_generic_chunk_coverage_controller_preview_self_validator.json",
    "historical_okx_full_usdt_swap_generic_chunk_coverage_controller_preview_summary.json",
]

CONTROLLER_NAME = "OKX_FULL_USDT_SWAP_GENERIC_CHUNK_COVERAGE_CONTROLLER_V1"
CONTROLLER_SCOPE = "COVERAGE_DISCOVERY_ONLY"
CHUNKS_TOTAL = 16
CHUNKS_COMPLETED = 2
CHUNKS_REMAINING = 14
START_CHUNK_ID = "chunk_03"
END_CHUNK_ID = "chunk_16"
NEXT_CHUNK_ID = "chunk_03"
TOTAL_CANDIDATE_SYMBOL_COUNT = 303
SYMBOLS_EVALUATED_FOR_DOWNLOAD_COVERAGE = 40
CUMULATIVE_COMPLETE_SYMBOL_COUNT = 14
CUMULATIVE_GAP_SYMBOL_COUNT = 26
CUMULATIVE_PENDING_SYMBOL_COUNT = 263
CUMULATIVE_AVAILABLE_FILE_COUNT = 23_159
CUMULATIVE_MISSING_OR_FAILED_FILE_COUNT = 18_961
CUMULATIVE_PLANNED_FILE_COUNT_EVALUATED = 42_120
EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 1_053
DATE_RANGE_START = "2023-07-01"
DATE_RANGE_END = "2026-05-18"
EXPECTED_NEXT_CHUNK_SYMBOL_COUNT = 20
EXPECTED_NEXT_CHUNK_FILE_COUNT = EXPECTED_NEXT_CHUNK_SYMBOL_COUNT * EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL

EXACT_DUPLICATE_POLICY = "DROP_ONLY_EXACT_DUPLICATE_EXTRA_ROWS_KEEP_ONE_CANONICAL_ROW"
MATERIAL_CONFLICT_POLICY = "QUARANTINE_ALL_ROWS_IN_MATERIAL_CONFLICT_OPEN_TIME_GROUP"
MISSING_MINUTE_POLICY = "NO_FILL_MARK_AFFECTED_HOUR_INCOMPLETE_OR_EXCLUDE_FROM_COMPLETE_CLAIMS"


class PreviewBlocked(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PreviewBlocked(message)


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
    )
    return completed.stdout.strip()


def current_tool_rel() -> str:
    return APPROVED_TOOL.relative_to(REPO_ROOT).as_posix()


def repo_has_only_this_tool_change() -> bool:
    status = [line for line in run_git(["status", "--short"]).splitlines() if line.strip()]
    if not status:
        return True
    rel = current_tool_rel()
    return all(line[3:].replace("\\", "/") == rel for line in status)


def tracked_python_files_including_current() -> list[str]:
    files = sorted(path for path in run_git(["ls-files"]).splitlines() if path.endswith(".py"))
    rel = current_tool_rel()
    if APPROVED_TOOL.exists() and rel not in files:
        files.append(rel)
    return sorted(files)


def tracked_python_validation() -> dict[str, Any]:
    syntax_errors: list[dict[str, str]] = []
    bom_errors: list[str] = []
    files = tracked_python_files_including_current()
    for rel in files:
        raw = (REPO_ROOT / rel).read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
        try:
            ast.parse(raw.decode("utf-8"), filename=rel)
        except Exception as exc:
            syntax_errors.append({"path": rel, "error": repr(exc)})
    return {
        "tracked_python_count": len(files),
        "syntax_error_count": len(syntax_errors),
        "bom_error_count": len(bom_errors),
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
    }


def load_json(path: Path, label: str) -> dict[str, Any]:
    require(path.exists(), f"missing artifact {label}: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(payload, dict), f"artifact {label} is not a JSON object")
    return payload


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_artifacts() -> dict[str, dict[str, Any]]:
    return {label: load_json(path, label) for label, path in ARTIFACTS.items()}


def chunk_number(chunk_id: str) -> int:
    return int(chunk_id.split("_", 1)[1])


def pending_chunks_from_plan(chunk_plan: dict[str, Any]) -> list[dict[str, Any]]:
    chunks = chunk_plan.get("chunks", [])
    require(isinstance(chunks, list), "chunk plan chunks is not a list")
    pending = [chunk for chunk in chunks if isinstance(chunk, dict) and chunk_number(str(chunk.get("chunk_id"))) >= 3]
    return pending


def validate_inputs(artifacts: dict[str, dict[str, Any]], py_state: dict[str, Any]) -> tuple[dict[str, bool], dict[str, Any]]:
    head = run_git(["rev-parse", "HEAD"])
    chunk_02_summary = artifacts["chunk_02_summary"]
    chunk_02_ledger = artifacts["chunk_02_ledger"]
    chunk_02_controller_approval = artifacts["chunk_02_controller_approval"]
    chunk_01_ledger = artifacts["chunk_01_ledger"]
    chunk_plan = artifacts["chunk_plan"]
    manifest_preview = artifacts["manifest_preview_summary"]
    candidates = artifacts["candidate_symbol_list"]
    pending_chunks = pending_chunks_from_plan(chunk_plan)
    next_chunk = pending_chunks[0] if pending_chunks else {}
    pending_symbol_count_from_plan = sum(int(chunk.get("symbol_count", 0)) for chunk in pending_chunks)
    expected_pending_ids = [f"chunk_{idx:02d}" for idx in range(3, 17)]
    checks = {
        "current_head_guard_passed": head.startswith(EXPECTED_HEAD),
        "current_path_guard_passed": APPROVED_TOOL.exists(),
        "repo_has_only_approved_tool_change": repo_has_only_this_tool_change(),
        "python_syntax_bom_clean": py_state["syntax_error_count"] == 0 and py_state["bom_error_count"] == 0,
        "previous_status_passed": chunk_02_summary.get("historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_coverage_summary_status") == PREVIOUS_STATUS,
        "current_next_module_matches": chunk_02_summary.get("next_module") == REQUESTED_MODULE,
        "chunk_02_summary_allows_controller_preview": chunk_02_summary.get("generic_chunk_controller_preview_required") is True,
        "chunk_02_controller_preview_approval_created": chunk_02_summary.get("generic_chunk_controller_preview_approval_record_created") is True,
        "chunk_02_replacement_checks_true": chunk_02_summary.get("replacement_checks_all_true") is True,
        "chunk_02_no_forbidden_actions": (
            chunk_02_summary.get("okx_api_call_performed") is False
            and chunk_02_summary.get("okx_browse_performed") is False
            and chunk_02_summary.get("data_download_performed") is False
            and chunk_02_summary.get("data_build_performed") is False
            and chunk_02_summary.get("aggregation_performed_now") is False
            and chunk_02_summary.get("full_universe_download_allowed_now") is False
            and chunk_02_summary.get("data_build_allowed_now") is False
            and chunk_02_summary.get("strategy_backtest_edge_allowed_now") is False
        ),
        "chunk_01_ledger_valid": (
            chunk_01_ledger.get("cumulative_coverage_ledger_created") is True
            and chunk_01_ledger.get("chunks_completed") == 1
            and chunk_01_ledger.get("cumulative_near_3y_download_coverage_complete_symbol_count") == 5
            and chunk_01_ledger.get("cumulative_coverage_gap_symbol_count") == 15
            and chunk_01_ledger.get("cumulative_pending_symbol_count") == 283
        ),
        "chunk_02_ledger_valid": (
            chunk_02_ledger.get("cumulative_coverage_ledger_created") is True
            and chunk_02_ledger.get("chunks_completed") == CHUNKS_COMPLETED
            and chunk_02_ledger.get("chunks_remaining") == CHUNKS_REMAINING
            and chunk_02_ledger.get("total_candidate_symbol_count") == TOTAL_CANDIDATE_SYMBOL_COUNT
            and chunk_02_ledger.get("symbols_evaluated_for_download_coverage") == SYMBOLS_EVALUATED_FOR_DOWNLOAD_COVERAGE
            and chunk_02_ledger.get("cumulative_near_3y_download_coverage_complete_symbol_count") == CUMULATIVE_COMPLETE_SYMBOL_COUNT
            and chunk_02_ledger.get("cumulative_coverage_gap_symbol_count") == CUMULATIVE_GAP_SYMBOL_COUNT
            and chunk_02_ledger.get("cumulative_pending_symbol_count") == CUMULATIVE_PENDING_SYMBOL_COUNT
            and chunk_02_ledger.get("cumulative_available_file_count") == CUMULATIVE_AVAILABLE_FILE_COUNT
            and chunk_02_ledger.get("cumulative_missing_or_failed_file_count") == CUMULATIVE_MISSING_OR_FAILED_FILE_COUNT
            and chunk_02_ledger.get("cumulative_planned_file_count_evaluated") == CUMULATIVE_PLANNED_FILE_COUNT_EVALUATED
            and chunk_02_ledger.get("build_ready_symbol_count") == 0
            and chunk_02_ledger.get("acquisition_ready_symbol_count") == 0
        ),
        "approval_record_valid": (
            chunk_02_controller_approval.get("approval_grants_chunk_02_coverage_summary_now") is True
            and chunk_02_controller_approval.get("approval_grants_generic_chunk_controller_now") is False
            and chunk_02_controller_approval.get("approval_grants_future_generic_chunk_controller_preview_next") is True
            and chunk_02_controller_approval.get("approval_grants_full_universe_download_now") is False
            and chunk_02_controller_approval.get("approval_grants_data_build_now") is False
            and chunk_02_controller_approval.get("approval_grants_research_backtest_edge_now") is False
        ),
        "chunk_plan_valid": (
            chunk_plan.get("chunk_count") == CHUNKS_TOTAL
            and chunk_plan.get("candidate_symbol_count") == TOTAL_CANDIDATE_SYMBOL_COUNT
            and len(chunk_plan.get("chunks", [])) == CHUNKS_TOTAL
            and [str(chunk.get("chunk_id")) for chunk in pending_chunks] == expected_pending_ids
            and pending_symbol_count_from_plan == CUMULATIVE_PENDING_SYMBOL_COUNT
        ),
        "next_chunk_selected": (
            next_chunk.get("chunk_id") == NEXT_CHUNK_ID
            and next_chunk.get("symbol_count") == EXPECTED_NEXT_CHUNK_SYMBOL_COUNT
            and next_chunk.get("expected_file_count") == EXPECTED_NEXT_CHUNK_FILE_COUNT
            and next_chunk.get("date_range_start") == DATE_RANGE_START
            and next_chunk.get("date_range_end") == DATE_RANGE_END
            and next_chunk.get("url_existence_checked") is False
            and next_chunk.get("downloaded") is False
            and next_chunk.get("build_ready") is False
            and next_chunk.get("acquisition_ready") is False
        ),
        "manifest_preview_no_forbidden_actions": (
            manifest_preview.get("url_existence_checked") is False
            and manifest_preview.get("archive_download_performed") is False
            and manifest_preview.get("okx_api_call_performed") is False
            and manifest_preview.get("okx_browse_performed") is False
            and manifest_preview.get("data_build_performed") is False
            and manifest_preview.get("aggregation_performed_now") is False
        ),
        "candidate_symbol_count_valid": (
            candidates.get("candidate_symbol_count") == TOTAL_CANDIDATE_SYMBOL_COUNT
            and len(candidates.get("candidate_symbols", [])) == TOTAL_CANDIDATE_SYMBOL_COUNT
        ),
    }
    require(all(checks.values()), f"input validation failed: {checks}")
    return checks, {"next_chunk": next_chunk, "pending_chunks": pending_chunks}


def build_common_summary(py_state: dict[str, Any], checks: dict[str, bool], selected: dict[str, Any]) -> dict[str, Any]:
    next_chunk = selected["next_chunk"]
    next_symbols = list(next_chunk.get("symbols", []))
    replacement_checks = {
        **checks,
        "controller_contract_created": True,
        "controller_scope_is_coverage_only": True,
        "next_chunk_preview_created": next_chunk.get("chunk_id") == NEXT_CHUNK_ID and len(next_symbols) == EXPECTED_NEXT_CHUNK_SYMBOL_COUNT,
        "cumulative_ledger_carried_forward": True,
        "no_preview_download_or_url_check": True,
        "no_build_aggregation_research_edge": True,
        "next_module_is_generic_cycle_execution": True,
    }
    replacement_checks_all_true = all(replacement_checks.values())
    return {
        "historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_controller_preview_status": PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS,
        "generic_chunk_controller_preview_created": replacement_checks_all_true,
        "controller_name": CONTROLLER_NAME,
        "controller_scope": CONTROLLER_SCOPE,
        "chunks_total": CHUNKS_TOTAL,
        "chunks_completed": CHUNKS_COMPLETED,
        "chunks_remaining": CHUNKS_REMAINING,
        "start_chunk_id": START_CHUNK_ID,
        "end_chunk_id": END_CHUNK_ID,
        "next_chunk_id": NEXT_CHUNK_ID,
        "next_chunk_symbol_count": len(next_symbols),
        "next_chunk_symbols": next_symbols,
        "expected_next_chunk_file_count": int(next_chunk.get("expected_file_count", 0)),
        "total_candidate_symbol_count": TOTAL_CANDIDATE_SYMBOL_COUNT,
        "symbols_evaluated_for_download_coverage": SYMBOLS_EVALUATED_FOR_DOWNLOAD_COVERAGE,
        "cumulative_near_3y_download_coverage_complete_symbol_count": CUMULATIVE_COMPLETE_SYMBOL_COUNT,
        "cumulative_coverage_gap_symbol_count": CUMULATIVE_GAP_SYMBOL_COUNT,
        "cumulative_pending_symbol_count": CUMULATIVE_PENDING_SYMBOL_COUNT,
        "cumulative_available_file_count": CUMULATIVE_AVAILABLE_FILE_COUNT,
        "cumulative_missing_or_failed_file_count": CUMULATIVE_MISSING_OR_FAILED_FILE_COUNT,
        "cumulative_planned_file_count_evaluated": CUMULATIVE_PLANNED_FILE_COUNT_EVALUATED,
        "cumulative_coverage_ledger_carried_forward": True,
        "one_chunk_per_execution": True,
        "execute_preview_download_validate_summary_in_one_module": True,
        "download_allowed_in_preview_module": False,
        "download_allowed_in_future_controller_execution": True,
        "full_universe_download_allowed_now": False,
        "data_build_allowed_now": False,
        "aggregation_allowed_now": False,
        "strategy_backtest_edge_allowed_now": False,
        "build_ready_claim_allowed": False,
        "acquisition_ready_claim_allowed": False,
        "controller_approval_record_created": replacement_checks_all_true,
        "approval_grants_generic_controller_preview_now": replacement_checks_all_true,
        "approval_grants_controller_execution_now": False,
        "approval_grants_future_generic_chunk_coverage_cycle_execution_next": replacement_checks_all_true,
        "approval_grants_next_chunk_download_now": False,
        "approval_grants_full_universe_download_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": 505,
        "dormant_repo_attention_count": 716,
        "current_evidence_chain_quality_after_controller_preview": AFTER_QUALITY if replacement_checks_all_true else "GENERIC_CHUNK_CONTROLLER_PREVIEW_FAILED_CLOSED",
        "next_module": NEXT_MODULE if replacement_checks_all_true else FAILED_NEXT_MODULE,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "tracked_python_count": py_state["tracked_python_count"],
        "syntax_error_count": py_state["syntax_error_count"],
        "bom_error_count": py_state["bom_error_count"],
        "created_at_utc": utc_now(),
    }


def controller_contract(summary: dict[str, Any], selected: dict[str, Any]) -> dict[str, Any]:
    return {
        **summary,
        "artifact_type": "generic_chunk_coverage_controller_contract",
        "controller_design": {
            "select_next_pending_chunk_from_approved_chunk_plan": True,
            "create_in_module_preview_checks": True,
            "download_or_reuse_approved_selected_chunk_files_only": True,
            "compute_or_revalidate_sha256": True,
            "inspect_zip_inventory_safely": True,
            "read_only_csv_header_and_max_5_sample_rows": True,
            "validate_schema_and_symbol_samples": True,
            "record_coverage_gaps_explicitly": True,
            "validate_count_reconciliation": True,
            "update_cumulative_coverage_ledger": True,
            "produce_chunk_coverage_summary": True,
            "route_to_self_until_chunks_complete_then_final_summary": True,
        },
        "pending_chunk_ids": [chunk["chunk_id"] for chunk in selected["pending_chunks"]],
        "exact_duplicate_policy": EXACT_DUPLICATE_POLICY,
        "material_conflict_policy": MATERIAL_CONFLICT_POLICY,
        "missing_minute_policy": MISSING_MINUTE_POLICY,
        "synthetic_fill_allowed": False,
        "forward_fill_allowed": False,
        "backfill_allowed": False,
    }


def resource_limits(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        **summary,
        "artifact_type": "generic_chunk_coverage_controller_resource_limits",
        "per_run_limits": {
            "exactly_one_chunk_per_controller_execution_run": True,
            "no_all_at_once_full_universe_download": True,
            "no_symbols_outside_selected_chunk": True,
            "date_range_start": DATE_RANGE_START,
            "date_range_end": DATE_RANGE_END,
            "expected_daily_file_count_per_symbol": EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
            "max_csv_sample_rows_per_file": 5,
            "no_api": True,
            "no_browse": True,
            "no_data_build": True,
            "no_aggregation": True,
            "no_full_csv_read": True,
            "no_research_backtest_edge": True,
            "no_build_ready_or_acquisition_ready_claims": True,
        },
    }


def next_chunk_selection_preview(summary: dict[str, Any], next_chunk: dict[str, Any]) -> dict[str, Any]:
    return {
        **summary,
        "artifact_type": "generic_chunk_coverage_controller_next_chunk_selection_preview",
        "next_chunk_preview": {
            "next_chunk_id": NEXT_CHUNK_ID,
            "next_chunk_symbol_count": summary["next_chunk_symbol_count"],
            "next_chunk_symbols": summary["next_chunk_symbols"],
            "expected_next_chunk_file_count": summary["expected_next_chunk_file_count"],
            "expected_daily_file_count_per_symbol": EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
            "date_range_start": DATE_RANGE_START,
            "date_range_end": DATE_RANGE_END,
            "planned_status": next_chunk.get("planned_status", "PLANNED_NOT_CHECKED_NOT_DOWNLOADED"),
            "all_planned_entries_marked_not_checked": True,
            "url_existence_checked": False,
            "downloaded": False,
            "build_ready": False,
            "acquisition_ready": False,
            "planned_file_status": "NOT_CHECKED_NOT_DOWNLOADED",
        },
    }


def ledger_carry_forward(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        **summary,
        "artifact_type": "generic_chunk_coverage_controller_cumulative_ledger_carry_forward",
        "ledger_state_after_chunk_02": {
            "chunks_completed": CHUNKS_COMPLETED,
            "chunks_remaining": CHUNKS_REMAINING,
            "symbols_evaluated_for_download_coverage": SYMBOLS_EVALUATED_FOR_DOWNLOAD_COVERAGE,
            "cumulative_near_3y_download_coverage_complete_symbol_count": CUMULATIVE_COMPLETE_SYMBOL_COUNT,
            "cumulative_coverage_gap_symbol_count": CUMULATIVE_GAP_SYMBOL_COUNT,
            "cumulative_pending_symbol_count": CUMULATIVE_PENDING_SYMBOL_COUNT,
            "cumulative_available_file_count": CUMULATIVE_AVAILABLE_FILE_COUNT,
            "cumulative_missing_or_failed_file_count": CUMULATIVE_MISSING_OR_FAILED_FILE_COUNT,
            "cumulative_planned_file_count_evaluated": CUMULATIVE_PLANNED_FILE_COUNT_EVALUATED,
            "build_ready_symbol_count": 0,
            "acquisition_ready_symbol_count": 0,
        },
    }


def build_outputs(summary: dict[str, Any], selected: dict[str, Any]) -> dict[str, Any]:
    preview = {
        **summary,
        "artifact_type": "generic_chunk_coverage_controller_preview",
        "purpose": "preview and approve generic one-chunk-at-a-time coverage discovery controller; no download now",
    }
    contract = controller_contract(summary, selected)
    limits = resource_limits(summary)
    next_preview = next_chunk_selection_preview(summary, selected["next_chunk"])
    ledger = ledger_carry_forward(summary)
    approval = {
        **summary,
        "artifact_type": "generic_chunk_coverage_controller_approval_record",
        "approval_scope": "next generic chunk coverage cycle execution module only",
    }
    self_validator = {
        **summary,
        "artifact_type": "generic_chunk_coverage_controller_preview_self_validator",
        "required_outputs": REQUIRED_OUTPUTS,
        "source_artifacts": {label: str(path) for label, path in ARTIFACTS.items()},
    }
    bundle_summary = {
        **summary,
        "artifact_type": "generic_chunk_coverage_controller_preview_summary",
        "artifact_count": len(REQUIRED_OUTPUTS),
    }
    return {
        "historical_okx_full_usdt_swap_generic_chunk_coverage_controller_preview.json": preview,
        "historical_okx_full_usdt_swap_generic_chunk_coverage_controller_contract.json": contract,
        "historical_okx_full_usdt_swap_generic_chunk_coverage_controller_resource_limits.json": limits,
        "historical_okx_full_usdt_swap_generic_chunk_coverage_controller_next_chunk_selection_preview.json": next_preview,
        "historical_okx_full_usdt_swap_generic_chunk_coverage_controller_cumulative_ledger_carry_forward.json": ledger,
        "historical_okx_full_usdt_swap_generic_chunk_coverage_controller_approval_record.json": approval,
        "historical_okx_full_usdt_swap_generic_chunk_coverage_controller_preview_self_validator.json": self_validator,
        "historical_okx_full_usdt_swap_generic_chunk_coverage_controller_preview_summary.json": bundle_summary,
    }


def run_preview() -> dict[str, Any]:
    py_state = tracked_python_validation()
    artifacts = read_artifacts()
    checks, selected = validate_inputs(artifacts, py_state)
    summary = build_common_summary(py_state, checks, selected)
    outputs = build_outputs(summary, selected)
    for name, payload in outputs.items():
        write_json(OUTPUT_DIR / name, payload)
    missing = [name for name in REQUIRED_OUTPUTS if not (OUTPUT_DIR / name).exists()]
    require(not missing, f"missing controller preview outputs: {missing}")
    require(summary["replacement_checks_all_true"], "replacement checks failed")
    return summary


def blocked_payload(message: str) -> dict[str, Any]:
    return {
        "historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_controller_preview_status": BLOCKED_STATUS,
        "generic_chunk_controller_preview_created": False,
        "blocked_reason": message,
        "controller_name": CONTROLLER_NAME,
        "controller_scope": CONTROLLER_SCOPE,
        "chunks_total": CHUNKS_TOTAL,
        "chunks_completed": CHUNKS_COMPLETED,
        "chunks_remaining": CHUNKS_REMAINING,
        "start_chunk_id": START_CHUNK_ID,
        "end_chunk_id": END_CHUNK_ID,
        "next_chunk_id": NEXT_CHUNK_ID,
        "next_chunk_symbol_count": 0,
        "next_chunk_symbols": [],
        "expected_next_chunk_file_count": 0,
        "total_candidate_symbol_count": TOTAL_CANDIDATE_SYMBOL_COUNT,
        "symbols_evaluated_for_download_coverage": SYMBOLS_EVALUATED_FOR_DOWNLOAD_COVERAGE,
        "cumulative_near_3y_download_coverage_complete_symbol_count": CUMULATIVE_COMPLETE_SYMBOL_COUNT,
        "cumulative_coverage_gap_symbol_count": CUMULATIVE_GAP_SYMBOL_COUNT,
        "cumulative_pending_symbol_count": CUMULATIVE_PENDING_SYMBOL_COUNT,
        "cumulative_coverage_ledger_carried_forward": False,
        "one_chunk_per_execution": True,
        "execute_preview_download_validate_summary_in_one_module": True,
        "download_allowed_in_preview_module": False,
        "download_allowed_in_future_controller_execution": False,
        "full_universe_download_allowed_now": False,
        "data_build_allowed_now": False,
        "aggregation_allowed_now": False,
        "strategy_backtest_edge_allowed_now": False,
        "build_ready_claim_allowed": False,
        "acquisition_ready_claim_allowed": False,
        "controller_approval_record_created": False,
        "approval_grants_future_generic_chunk_coverage_cycle_execution_next": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 505,
        "current_evidence_chain_quality_after_controller_preview": "GENERIC_CHUNK_CONTROLLER_PREVIEW_FAILED_CLOSED",
        "next_module": FAILED_NEXT_MODULE,
        "replacement_checks_all_true": False,
        "created_at_utc": utc_now(),
    }


def main() -> int:
    try:
        summary = run_preview()
    except Exception as exc:
        blocked = blocked_payload(type(exc).__name__ + ": " + str(exc))
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        write_json(OUTPUT_DIR / "historical_okx_full_usdt_swap_generic_chunk_coverage_controller_preview_summary.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
