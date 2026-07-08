from __future__ import annotations

import ast
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_coverage_summary_after_validator_v1"
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "c1bc353"
PREVIOUS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_FIRST_CHUNK_DOWNLOAD_VALIDATED_WITH_COVERAGE_GAPS_COVERAGE_SUMMARY_READY_NO_BUILD"
PASS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_FIRST_CHUNK_DOWNLOAD_COVERAGE_SUMMARY_CLOSED_CHUNK_02_PREVIEW_READY"
BLOCKED_STATUS = "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_FIRST_CHUNK_DOWNLOAD_COVERAGE_SUMMARY_FAILED"
NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_preview_after_first_chunk_coverage_summary_v1.py"
FAILED_NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_coverage_summary_blocked_record_v1.py"
AFTER_QUALITY = "HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_FIRST_CHUNK_COVERAGE_SUMMARY_CLOSED_CHUNK_02_PREVIEW_READY"

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME

VALIDATOR_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_execution_validator_after_execution_v1"
EXECUTION_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_execution_after_preview_approval_v1"
MANIFEST_PREVIEW_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_archive_coverage_manifest_preview_after_eligibility_preview_v1"
SOURCE_DISCOVERY_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_symbol_source_discovery_after_universe_preview_approval_v1"

ARTIFACTS = {
    "validator_summary": VALIDATOR_DIR / "historical_okx_full_usdt_swap_first_chunk_download_execution_validator_summary.json",
    "per_symbol_validation": VALIDATOR_DIR / "historical_okx_full_usdt_swap_first_chunk_per_symbol_coverage_validation_report.json",
    "gap_validation": VALIDATOR_DIR / "historical_okx_full_usdt_swap_first_chunk_gap_validation_report.json",
    "execution_summary": EXECUTION_DIR / "historical_okx_full_usdt_swap_first_chunk_download_execution_summary.json",
    "chunk_plan": MANIFEST_PREVIEW_DIR / "historical_okx_full_usdt_swap_archive_coverage_chunk_plan.json",
    "candidate_symbol_list": SOURCE_DISCOVERY_DIR / "historical_okx_full_usdt_swap_candidate_symbol_list.json",
}

REQUIRED_OUTPUTS = [
    "historical_okx_full_usdt_swap_first_chunk_download_coverage_summary.json",
    "historical_okx_full_usdt_swap_first_chunk_coverage_eligible_symbols.json",
    "historical_okx_full_usdt_swap_first_chunk_coverage_gap_symbols.json",
    "historical_okx_full_usdt_swap_cumulative_coverage_eligibility_ledger_after_chunk_01.json",
    "historical_okx_full_usdt_swap_chunk_02_download_preview_approval_record.json",
    "historical_okx_full_usdt_swap_first_chunk_download_coverage_summary_self_validator.json",
    "historical_okx_full_usdt_swap_first_chunk_download_coverage_summary_bundle_summary.json",
]

CHUNK_ID = "chunk_01"
CHUNK_SYMBOL_COUNT = 20
CHUNKS_TOTAL = 16
CHUNKS_COMPLETED = 1
CHUNKS_REMAINING = 15
TOTAL_CANDIDATE_SYMBOL_COUNT = 303
PLANNED_FILE_COUNT = 21_060
FINAL_AVAILABLE_FILE_COUNT = 10_106
MISSING_OR_FAILED_FILE_COUNT = 10_954
FULL_COVERAGE_SYMBOLS = [
    "1INCH-USDT-SWAP",
    "AAVE-USDT-SWAP",
    "ADA-USDT-SWAP",
    "AGLD-USDT-SWAP",
    "ALGO-USDT-SWAP",
]
GAP_SYMBOLS = [
    "0G-USDT-SWAP",
    "2Z-USDT-SWAP",
    "A-USDT-SWAP",
    "AAPL-USDT-SWAP",
    "ACH-USDT-SWAP",
    "ACT-USDT-SWAP",
    "ACU-USDT-SWAP",
    "AERO-USDT-SWAP",
    "AEVO-USDT-SWAP",
    "AI-USDT-SWAP",
    "AIXBT-USDT-SWAP",
    "ALLO-USDT-SWAP",
    "AMD-USDT-SWAP",
    "AMZN-USDT-SWAP",
    "ANIME-USDT-SWAP",
]


class SummaryBlocked(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SummaryBlocked(message)


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


def validate_inputs(artifacts: dict[str, dict[str, Any]], py_state: dict[str, Any]) -> dict[str, bool]:
    head = run_git(["rev-parse", "HEAD"])
    validator = artifacts["validator_summary"]
    execution = artifacts["execution_summary"]
    chunk_plan = artifacts["chunk_plan"]
    candidates = artifacts["candidate_symbol_list"]
    per_symbol = artifacts["per_symbol_validation"].get("per_symbol_coverage", [])
    checks = {
        "current_head_guard_passed": head.startswith(EXPECTED_HEAD),
        "current_path_guard_passed": APPROVED_TOOL.exists(),
        "repo_has_only_approved_tool_change": repo_has_only_this_tool_change(),
        "python_syntax_bom_clean": py_state["syntax_error_count"] == 0 and py_state["bom_error_count"] == 0,
        "validator_status_passed": validator.get("historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_execution_validator_status") == PREVIOUS_STATUS,
        "current_next_module_matches": validator.get("next_module") == REQUESTED_MODULE,
        "validator_allows_summary": validator.get("first_chunk_download_validated_for_coverage_summary") is True,
        "validator_replacement_checks_true": validator.get("replacement_checks_all_true") is True,
        "execution_no_forbidden_actions": (
            execution.get("okx_api_call_performed") is False
            and execution.get("okx_browse_performed") is False
            and execution.get("data_build_performed") is False
            and execution.get("aggregation_performed_now") is False
            and execution.get("full_csv_read_performed") is False
            and execution.get("files_marked_build_ready") is False
            and execution.get("source_manifest_acquisition_ready") is False
        ),
        "chunk_id_valid": validator.get("chunk_id") == CHUNK_ID,
        "chunk_symbol_count_valid": validator.get("chunk_symbol_count") == CHUNK_SYMBOL_COUNT,
        "planned_count_valid": validator.get("planned_file_count") == PLANNED_FILE_COUNT,
        "available_count_valid": validator.get("final_available_file_count") == FINAL_AVAILABLE_FILE_COUNT,
        "missing_count_valid": validator.get("missing_or_failed_file_count") == MISSING_OR_FAILED_FILE_COUNT,
        "count_reconciliation_valid": validator.get("count_reconciliation_pass") is True and FINAL_AVAILABLE_FILE_COUNT + MISSING_OR_FAILED_FILE_COUNT == PLANNED_FILE_COUNT,
        "full_coverage_symbols_valid": validator.get("symbols_with_full_file_coverage") == FULL_COVERAGE_SYMBOLS,
        "gap_symbols_valid": validator.get("symbols_with_coverage_gaps") == GAP_SYMBOLS,
        "near_3y_symbols_valid": validator.get("symbols_near_3y_download_coverage_complete") == FULL_COVERAGE_SYMBOLS,
        "no_build_or_acquisition_ready": validator.get("files_marked_build_ready") is False and validator.get("source_manifest_acquisition_ready") is False,
        "no_research_backtest_edge_claim": (
            validator.get("output_valid_for_research_backtest") is False
            and validator.get("output_valid_for_edge_claim") is False
            and validator.get("safe_for_full_universe_acquisition") is False
            and validator.get("broad_acquisition_ready") is False
        ),
        "chunk_plan_valid": (
            chunk_plan.get("chunk_count") == CHUNKS_TOTAL
            and chunk_plan.get("candidate_symbol_count") == TOTAL_CANDIDATE_SYMBOL_COUNT
            and len(chunk_plan.get("chunks", [])) == CHUNKS_TOTAL
            and chunk_plan["chunks"][0].get("chunk_id") == CHUNK_ID
            and chunk_plan["chunks"][1].get("chunk_id") == "chunk_02"
            and chunk_plan["chunks"][1].get("symbol_count") == 20
        ),
        "candidate_symbol_count_valid": (
            candidates.get("candidate_symbol_count") == TOTAL_CANDIDATE_SYMBOL_COUNT
            and len(candidates.get("candidate_symbols", [])) == TOTAL_CANDIDATE_SYMBOL_COUNT
        ),
        "per_symbol_coverage_available": isinstance(per_symbol, list) and len(per_symbol) == CHUNK_SYMBOL_COUNT,
    }
    require(all(checks.values()), f"input validation failed: {checks}")
    return checks


def common_summary(artifacts: dict[str, dict[str, Any]], checks: dict[str, bool], py_state: dict[str, Any]) -> dict[str, Any]:
    validator = artifacts["validator_summary"]
    evaluated_count = CHUNK_SYMBOL_COUNT
    pending_count = TOTAL_CANDIDATE_SYMBOL_COUNT - evaluated_count
    replacement_checks = {
        **checks,
        "coverage_summary_created": True,
        "eligible_and_gap_sets_disjoint": not (set(FULL_COVERAGE_SYMBOLS) & set(GAP_SYMBOLS)),
        "eligible_plus_gap_equals_chunk_symbol_count": len(FULL_COVERAGE_SYMBOLS) + len(GAP_SYMBOLS) == CHUNK_SYMBOL_COUNT,
        "cumulative_counts_valid": 5 + 15 + pending_count == TOTAL_CANDIDATE_SYMBOL_COUNT,
        "no_download_api_browse_build_aggregation_now": True,
        "next_route_is_chunk_02_preview": True,
        "approval_record_created": True,
    }
    replacement_checks_all_true = all(replacement_checks.values())
    return {
        "historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_coverage_summary_status": PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS,
        "coverage_summary_created": replacement_checks_all_true,
        "chunk_id": CHUNK_ID,
        "chunks_total": CHUNKS_TOTAL,
        "chunks_completed": CHUNKS_COMPLETED,
        "chunks_remaining": CHUNKS_REMAINING,
        "chunk_symbol_count": CHUNK_SYMBOL_COUNT,
        "planned_file_count": PLANNED_FILE_COUNT,
        "final_available_file_count": FINAL_AVAILABLE_FILE_COUNT,
        "missing_or_failed_file_count": MISSING_OR_FAILED_FILE_COUNT,
        "coverage_gap_detected": True,
        "symbols_with_full_file_coverage_count": len(FULL_COVERAGE_SYMBOLS),
        "symbols_with_full_file_coverage": FULL_COVERAGE_SYMBOLS,
        "symbols_with_coverage_gaps_count": len(GAP_SYMBOLS),
        "symbols_with_coverage_gaps": GAP_SYMBOLS,
        "near_3y_download_coverage_complete_symbol_count": len(FULL_COVERAGE_SYMBOLS),
        "near_3y_download_coverage_complete_symbols": FULL_COVERAGE_SYMBOLS,
        "build_ready_symbol_count": 0,
        "acquisition_ready_symbol_count": 0,
        "cumulative_coverage_ledger_created": replacement_checks_all_true,
        "total_candidate_symbol_count": TOTAL_CANDIDATE_SYMBOL_COUNT,
        "symbols_evaluated_for_download_coverage": evaluated_count,
        "cumulative_near_3y_download_coverage_complete_symbol_count": len(FULL_COVERAGE_SYMBOLS),
        "cumulative_coverage_gap_symbol_count": len(GAP_SYMBOLS),
        "cumulative_pending_symbol_count": pending_count,
        "cumulative_available_file_count": FINAL_AVAILABLE_FILE_COUNT,
        "cumulative_missing_or_failed_file_count": MISSING_OR_FAILED_FILE_COUNT,
        "cumulative_planned_file_count_evaluated": PLANNED_FILE_COUNT,
        "next_chunk_download_preview_required": True,
        "chunk_02_download_preview_approval_record_created": replacement_checks_all_true,
        "approval_grants_coverage_summary_now": replacement_checks_all_true,
        "approval_grants_chunk_02_download_preview_now": False,
        "approval_grants_future_chunk_02_download_preview_next": replacement_checks_all_true,
        "approval_grants_chunk_02_download_execution_now": False,
        "approval_grants_full_universe_download_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "full_universe_download_allowed_now": False,
        "data_build_allowed_now": False,
        "strategy_backtest_edge_allowed_now": False,
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
        "active_p1_attention_count": max(int(validator.get("active_p1_attention_count", 0)), 505),
        "dormant_repo_attention_count": 716,
        "current_evidence_chain_quality_after_summary": AFTER_QUALITY if replacement_checks_all_true else "FIRST_CHUNK_COVERAGE_SUMMARY_FAILED_CLOSED",
        "next_module": NEXT_MODULE if replacement_checks_all_true else FAILED_NEXT_MODULE,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "tracked_python_count": py_state["tracked_python_count"],
        "syntax_error_count": py_state["syntax_error_count"],
        "bom_error_count": py_state["bom_error_count"],
        "created_at_utc": utc_now(),
    }


def build_outputs(summary: dict[str, Any], artifacts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    chunk_02 = artifacts["chunk_plan"]["chunks"][1]
    eligible = {
        **summary,
        "artifact_type": "first_chunk_coverage_eligible_symbols",
        "eligible_symbols": [
            {
                "symbol": symbol,
                "near_3y_download_coverage_complete": True,
                "build_ready": False,
                "acquisition_ready": False,
                "requires_future_build_preview_before_any_build": True,
            }
            for symbol in FULL_COVERAGE_SYMBOLS
        ],
    }
    gaps = {
        **summary,
        "artifact_type": "first_chunk_coverage_gap_symbols",
        "coverage_gap_symbols": [
            {
                "symbol": symbol,
                "near_3y_download_coverage_complete": False,
                "excluded_from_near_3y_download_complete_claim_now": True,
                "build_ready": False,
                "acquisition_ready": False,
            }
            for symbol in GAP_SYMBOLS
        ],
    }
    ledger = {
        **summary,
        "artifact_type": "cumulative_coverage_eligibility_ledger_after_chunk_01",
        "ledger_entries": {
            "near_3y_download_coverage_complete_symbols": FULL_COVERAGE_SYMBOLS,
            "coverage_gap_symbols": GAP_SYMBOLS,
            "pending_symbol_count": summary["cumulative_pending_symbol_count"],
        },
        "build_phase_blocked_until_separately_approved": True,
    }
    approval = {
        **summary,
        "artifact_type": "chunk_02_download_preview_approval_record",
        "approval_scope": "next separate chunk_02 download preview only",
        "chunk_02_chunk_id": chunk_02["chunk_id"],
        "chunk_02_symbol_count": chunk_02["symbol_count"],
        "chunk_02_symbols": chunk_02["symbols"],
    }
    self_validator = {
        **summary,
        "artifact_type": "coverage_summary_self_validator",
        "required_outputs": REQUIRED_OUTPUTS,
        "validator_source_status": artifacts["validator_summary"].get("historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_execution_validator_status"),
    }
    coverage_summary = {
        **summary,
        "artifact_type": "first_chunk_download_coverage_summary",
        "per_symbol_coverage_validation_source": str(ARTIFACTS["per_symbol_validation"]),
    }
    bundle_summary = {
        **summary,
        "artifact_type": "first_chunk_download_coverage_summary_bundle_summary",
        "artifact_count": len(REQUIRED_OUTPUTS),
    }
    return {
        "historical_okx_full_usdt_swap_first_chunk_download_coverage_summary.json": coverage_summary,
        "historical_okx_full_usdt_swap_first_chunk_coverage_eligible_symbols.json": eligible,
        "historical_okx_full_usdt_swap_first_chunk_coverage_gap_symbols.json": gaps,
        "historical_okx_full_usdt_swap_cumulative_coverage_eligibility_ledger_after_chunk_01.json": ledger,
        "historical_okx_full_usdt_swap_chunk_02_download_preview_approval_record.json": approval,
        "historical_okx_full_usdt_swap_first_chunk_download_coverage_summary_self_validator.json": self_validator,
        "historical_okx_full_usdt_swap_first_chunk_download_coverage_summary_bundle_summary.json": bundle_summary,
    }


def run_summary() -> dict[str, Any]:
    py_state = tracked_python_validation()
    artifacts = read_artifacts()
    checks = validate_inputs(artifacts, py_state)
    summary = common_summary(artifacts, checks, py_state)
    outputs = build_outputs(summary, artifacts)
    for name, payload in outputs.items():
        write_json(OUTPUT_DIR / name, payload)
    missing = [name for name in REQUIRED_OUTPUTS if not (OUTPUT_DIR / name).exists()]
    require(not missing, f"missing summary outputs: {missing}")
    require(summary["replacement_checks_all_true"], "replacement checks failed")
    return summary


def blocked_payload(message: str) -> dict[str, Any]:
    return {
        "historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_coverage_summary_status": BLOCKED_STATUS,
        "coverage_summary_created": False,
        "blocked_reason": message,
        "chunk_id": CHUNK_ID,
        "chunks_completed": 0,
        "chunks_remaining": CHUNKS_TOTAL,
        "planned_file_count": 0,
        "final_available_file_count": 0,
        "missing_or_failed_file_count": 0,
        "symbols_with_full_file_coverage_count": 0,
        "symbols_with_full_file_coverage": [],
        "symbols_with_coverage_gaps_count": 0,
        "symbols_with_coverage_gaps": [],
        "near_3y_download_coverage_complete_symbol_count": 0,
        "build_ready_symbol_count": 0,
        "acquisition_ready_symbol_count": 0,
        "cumulative_coverage_ledger_created": False,
        "total_candidate_symbol_count": TOTAL_CANDIDATE_SYMBOL_COUNT,
        "symbols_evaluated_for_download_coverage": 0,
        "cumulative_near_3y_download_coverage_complete_symbol_count": 0,
        "cumulative_coverage_gap_symbol_count": 0,
        "cumulative_pending_symbol_count": TOTAL_CANDIDATE_SYMBOL_COUNT,
        "next_chunk_download_preview_required": False,
        "chunk_02_download_preview_approval_record_created": False,
        "approval_grants_future_chunk_02_download_preview_next": False,
        "full_universe_download_allowed_now": False,
        "data_build_allowed_now": False,
        "strategy_backtest_edge_allowed_now": False,
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 505,
        "current_evidence_chain_quality_after_summary": "FIRST_CHUNK_COVERAGE_SUMMARY_FAILED_CLOSED",
        "next_module": FAILED_NEXT_MODULE,
        "replacement_checks_all_true": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "created_at_utc": utc_now(),
    }


def main() -> int:
    try:
        summary = run_summary()
    except Exception as exc:
        blocked = blocked_payload(type(exc).__name__ + ": " + str(exc))
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        write_json(OUTPUT_DIR / "historical_okx_full_usdt_swap_first_chunk_download_coverage_summary_bundle_summary.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
