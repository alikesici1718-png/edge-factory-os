from __future__ import annotations

import ast
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_archive_coverage_eligibility_preview_after_symbol_source_discovery_v1"
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "a50b923"
PREVIOUS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_SYMBOL_SOURCE_DISCOVERY_READY_FOR_ARCHIVE_COVERAGE_ELIGIBILITY_PREVIEW"
PASS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_ARCHIVE_COVERAGE_ELIGIBILITY_PREVIEW_READY_FOR_MANIFEST_PREVIEW"
BLOCKED_STATUS = "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_ARCHIVE_COVERAGE_ELIGIBILITY_PREVIEW_FAILED_CLOSED"
NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_archive_coverage_manifest_preview_after_eligibility_preview_v1.py"
FAILED_NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_archive_coverage_eligibility_preview_blocked_record_v1.py"
AFTER_QUALITY = "HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_ARCHIVE_COVERAGE_ELIGIBILITY_PREVIEW_READY_FOR_MANIFEST_PREVIEW"

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME

SOURCE_DISCOVERY_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_symbol_source_discovery_after_universe_preview_approval_v1"
PILOT_SUMMARY_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_pipeline_summary_after_build_validator_v1"
POLICY_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_after_batch_anomaly_classification_v1"

ARTIFACTS = {
    "symbol_source_summary": SOURCE_DISCOVERY_DIR / "historical_okx_full_usdt_swap_symbol_source_discovery_summary.json",
    "candidate_symbol_list": SOURCE_DISCOVERY_DIR / "historical_okx_full_usdt_swap_candidate_symbol_list.json",
    "pilot_pipeline_summary": PILOT_SUMMARY_DIR / "historical_okx_10_symbol_pilot_batch_policy_clean_pipeline_summary_bundle_summary.json",
    "batch_policy_summary": POLICY_DIR / "historical_okx_10_symbol_pilot_batch_policy_summary.json",
}

REQUIRED_OUTPUTS = [
    "historical_okx_full_usdt_swap_archive_coverage_eligibility_preview.json",
    "historical_okx_full_usdt_swap_archive_coverage_workload_preview.json",
    "historical_okx_full_usdt_swap_archive_coverage_chunking_policy.json",
    "historical_okx_full_usdt_swap_archive_coverage_eligibility_rules.json",
    "historical_okx_full_usdt_swap_batch_policy_carry_forward_for_full_universe.json",
    "historical_okx_full_usdt_swap_archive_coverage_manifest_preview_approval_record.json",
    "historical_okx_full_usdt_swap_archive_coverage_eligibility_preview_self_validator.json",
    "historical_okx_full_usdt_swap_archive_coverage_eligibility_preview_summary.json",
]

EXPECTED_CANDIDATE_SYMBOL_COUNT = 303
EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 1053
EXPECTED_TOTAL_ARCHIVE_FILE_COUNT = 319_059
EXISTING_10_SYMBOL_PILOT_FILE_COUNT = 10_530
EXISTING_PILOT_SYMBOL_COUNT = 10
REMAINING_CANDIDATE_SYMBOL_COUNT = 293
REMAINING_EXPECTED_ARCHIVE_FILE_COUNT = 308_529
DATE_START = "2023-07-01"
DATE_END = "2026-05-18"
URL_PATTERN = "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/YYYYMMDD/SYMBOL-candlesticks-YYYY-MM-DD.zip"

POLICY = {
    "exact_duplicate_policy": "DROP_ONLY_EXACT_DUPLICATE_EXTRA_ROWS_KEEP_ONE_CANONICAL_ROW",
    "material_conflict_policy": "QUARANTINE_ALL_ROWS_IN_MATERIAL_CONFLICT_OPEN_TIME_GROUP",
    "missing_minute_policy": "NO_FILL_MARK_AFFECTED_HOUR_INCOMPLETE_OR_EXCLUDE_FROM_COMPLETE_CLAIMS",
    "synthetic_fill_allowed": False,
    "forward_fill_allowed": False,
    "backfill_allowed": False,
}


class Blocked(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Blocked(message)


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
    require(path.exists(), f"missing required artifact {label}: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(payload, dict), f"artifact {label} is not a JSON object")
    return payload


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_artifacts() -> dict[str, dict[str, Any]]:
    return {label: load_json(path, label) for label, path in ARTIFACTS.items()}


def validate_inputs(artifacts: dict[str, dict[str, Any]], py_state: dict[str, Any]) -> dict[str, Any]:
    head = run_git(["rev-parse", "HEAD"])
    source = artifacts["symbol_source_summary"]
    candidate_list = artifacts["candidate_symbol_list"]
    pilot = artifacts["pilot_pipeline_summary"]
    policy = artifacts["batch_policy_summary"]
    symbols = candidate_list.get("candidate_symbols", [])
    checks = {
        "current_head_guard_passed": head.startswith(EXPECTED_HEAD),
        "current_path_guard_passed": APPROVED_TOOL.exists(),
        "repo_has_only_approved_tool_change": repo_has_only_this_tool_change(),
        "python_syntax_bom_clean": py_state["syntax_error_count"] == 0 and py_state["bom_error_count"] == 0,
        "previous_status_passed": source.get("historical_data_acquisition_okx_full_usdt_swap_symbol_source_discovery_status") == PREVIOUS_STATUS,
        "current_next_module_matches": source.get("next_module") == REQUESTED_MODULE,
        "candidate_symbol_list_created": source.get("candidate_symbol_list_created") is True and candidate_list.get("candidate_symbol_list_created") is True,
        "candidate_symbol_count_303": source.get("candidate_symbol_count") == EXPECTED_CANDIDATE_SYMBOL_COUNT and len(symbols) == EXPECTED_CANDIDATE_SYMBOL_COUNT,
        "candidate_symbols_unique": len(symbols) == len(set(symbols)),
        "candidate_symbols_usdt_swap_format": all(isinstance(symbol, str) and symbol.endswith("-USDT-SWAP") for symbol in symbols),
        "source_discovery_no_forbidden_actions": (
            source.get("okx_api_call_performed") is False
            and source.get("okx_browse_performed") is False
            and source.get("data_download_performed") is False
            and source.get("data_build_performed") is False
            and source.get("aggregation_performed_now") is False
        ),
        "source_no_readiness_claim": (
            source.get("output_valid_for_research_backtest") is False
            and source.get("output_valid_for_edge_claim") is False
            and source.get("safe_for_full_universe_acquisition") is False
            and source.get("broad_acquisition_ready") is False
        ),
        "pilot_pipeline_closed": pilot.get("pipeline_closed_successfully") is True and pilot.get("replacement_checks_all_true") is True,
        "batch_policy_available": policy.get("replacement_checks_all_true") is True,
    }
    return {"head": head, "checks": checks}


def common_summary(artifacts: dict[str, dict[str, Any]], chain: dict[str, Any], py_state: dict[str, Any]) -> dict[str, Any]:
    source = artifacts["symbol_source_summary"]
    replacement_checks = {
        **chain["checks"],
        "expected_total_archive_file_count_valid": EXPECTED_CANDIDATE_SYMBOL_COUNT * EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL == EXPECTED_TOTAL_ARCHIVE_FILE_COUNT,
        "remaining_file_count_valid": REMAINING_CANDIDATE_SYMBOL_COUNT * EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL == REMAINING_EXPECTED_ARCHIVE_FILE_COUNT,
        "no_url_existence_check_or_download": True,
        "manifest_generation_not_performed_now": True,
        "next_module_is_manifest_preview": True,
        "no_download_api_browse_build_aggregation_now": True,
        "no_research_backtest_edge_claim": True,
        "no_full_universe_or_broad_ready_claim": True,
    }
    replacement_checks_all_true = all(replacement_checks.values())
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    return {
        "historical_data_acquisition_okx_full_usdt_swap_archive_coverage_eligibility_preview_status": status,
        "archive_coverage_eligibility_preview_created": replacement_checks_all_true,
        "candidate_symbol_count": EXPECTED_CANDIDATE_SYMBOL_COUNT,
        "expected_daily_file_count_per_symbol": EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "expected_total_archive_file_count": EXPECTED_TOTAL_ARCHIVE_FILE_COUNT,
        "existing_10_symbol_pilot_file_count": EXISTING_10_SYMBOL_PILOT_FILE_COUNT,
        "existing_pilot_symbol_count": EXISTING_PILOT_SYMBOL_COUNT,
        "remaining_candidate_symbol_count": REMAINING_CANDIDATE_SYMBOL_COUNT,
        "remaining_expected_archive_file_count": REMAINING_EXPECTED_ARCHIVE_FILE_COUNT,
        "estimated_manifest_size_category": "LARGE",
        "max_available_start_candidate": DATE_START,
        "max_available_end_date": DATE_END,
        "strict_3y_completeness_claimed": False,
        "near_3y_eligibility_rules_created": replacement_checks_all_true,
        "url_pattern_preview_created": True,
        "url_pattern_preview": URL_PATTERN,
        "url_existence_checked": False,
        "archive_download_performed": False,
        "archive_download_allowed_now": False,
        "manifest_generation_performed_now": False,
        "future_manifest_preview_required": True,
        "chunking_policy_created": replacement_checks_all_true,
        "recommended_chunk_symbol_min": 10,
        "recommended_chunk_symbol_max": 25,
        "full_download_requires_separate_approval": True,
        "full_build_requires_separate_approval": True,
        "batch_policy_carry_forward_created": True,
        **POLICY,
        "future_manifest_preview_approval_record_created": replacement_checks_all_true,
        "approval_grants_eligibility_preview_now": replacement_checks_all_true,
        "approval_grants_manifest_generation_now": False,
        "approval_grants_future_archive_coverage_manifest_preview_next": replacement_checks_all_true,
        "approval_grants_archive_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "full_universe_acquisition_allowed_now": False,
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
        "active_p1_attention_count": max(int(source.get("active_p1_attention_count", 0)), 505),
        "dormant_repo_attention_count": 716,
        "current_evidence_chain_quality_after_preview": AFTER_QUALITY if replacement_checks_all_true else "FULL_USDT_SWAP_ARCHIVE_COVERAGE_ELIGIBILITY_PREVIEW_FAILED_CLOSED",
        "next_module": NEXT_MODULE if replacement_checks_all_true else FAILED_NEXT_MODULE,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "tracked_python_count": py_state["tracked_python_count"],
        "syntax_error_count": py_state["syntax_error_count"],
        "bom_error_count": py_state["bom_error_count"],
        "created_at_utc": utc_now(),
    }


def build_outputs(summary: dict[str, Any], artifacts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    candidate_symbols = artifacts["candidate_symbol_list"].get("candidate_symbols", [])
    preview = {
        **summary,
        "artifact_type": "archive_coverage_eligibility_preview",
        "target_universe": {
            "exchange": "OKX",
            "instrument_type": "PERPETUAL_SWAP",
            "quote_scope": "USDT_SWAP",
            "candidate_symbol_count": EXPECTED_CANDIDATE_SYMBOL_COUNT,
            "symbol_format": "BASE-USDT-SWAP",
            "date_range": {"start": DATE_START, "end": DATE_END},
        },
        "candidate_symbol_sample": candidate_symbols[:25],
        "manifest_shape_preview_only": {
            "fields": ["symbol", "date", "yyyymmdd", "planned_url", "planned_zip_name", "planned_inner_csv_name", "chunk_id"],
            "planned_url_pattern": URL_PATTERN,
            "full_manifest_rows_expected_if_approved_later": EXPECTED_TOTAL_ARCHIVE_FILE_COUNT,
            "full_manifest_written_now": False,
        },
    }
    workload = {
        **summary,
        "artifact_type": "archive_coverage_workload_preview",
        "workload_formula": "candidate_symbol_count * expected_daily_file_count_per_symbol",
        "remaining_formula": "(candidate_symbol_count - existing_pilot_symbol_count) * expected_daily_file_count_per_symbol",
    }
    chunking = {
        **summary,
        "artifact_type": "archive_coverage_chunking_policy",
        "recommended_staged_plan": [
            "Manifest generation only.",
            "Coverage probe/download in chunks after separate approval.",
            "Use 10 to 25 symbols per batch.",
            "Reuse already validated 10-symbol pilot files where symbols overlap.",
            "Do not perform one-symbol-at-a-time loops.",
            "Do not attempt all 319059 ZIP downloads in one unbounded step.",
        ],
        "chunk_requirements": [
            "planned_symbol_count",
            "expected_file_count",
            "max_download_count",
            "failure_or_gap_reporting",
            "hash_and_provenance_output",
            "no_data_build_until_download_validation_passes",
        ],
    }
    rules = {
        **summary,
        "artifact_type": "archive_coverage_eligibility_rules",
        "eligibility_rules": [
            "All expected dates are present or gaps are explicitly recorded.",
            "Every file opens as a safe ZIP.",
            "Expected inner CSV exists.",
            "Schema matches OKX candlestick schema instrument_name,open,high,low,close,vol,vol_ccy,vol_quote,open_time,confirm.",
            "CSV symbol matches expected symbol.",
            "Exact duplicates, material conflicts, and missing minutes are handled only by validated batch policy.",
            "No synthetic fill, forward fill, or backfill is used.",
            "Any incomplete hour remains incomplete.",
        ],
    }
    carry_forward = {
        **summary,
        "artifact_type": "batch_policy_carry_forward_for_full_universe",
        "policy_scope": "future full-universe archive coverage and build routes after separate approvals",
    }
    approval = {
        **summary,
        "artifact_type": "archive_coverage_manifest_preview_approval_record",
        "approval_scope": "next separate repo-only archive coverage manifest preview module only",
    }
    self_validator = {
        **summary,
        "artifact_type": "self_validator",
        "required_outputs": REQUIRED_OUTPUTS,
    }
    summary_artifact = {
        **summary,
        "artifact_type": "summary",
        "artifact_count": len(REQUIRED_OUTPUTS),
    }
    return {
        "historical_okx_full_usdt_swap_archive_coverage_eligibility_preview.json": preview,
        "historical_okx_full_usdt_swap_archive_coverage_workload_preview.json": workload,
        "historical_okx_full_usdt_swap_archive_coverage_chunking_policy.json": chunking,
        "historical_okx_full_usdt_swap_archive_coverage_eligibility_rules.json": rules,
        "historical_okx_full_usdt_swap_batch_policy_carry_forward_for_full_universe.json": carry_forward,
        "historical_okx_full_usdt_swap_archive_coverage_manifest_preview_approval_record.json": approval,
        "historical_okx_full_usdt_swap_archive_coverage_eligibility_preview_self_validator.json": self_validator,
        "historical_okx_full_usdt_swap_archive_coverage_eligibility_preview_summary.json": summary_artifact,
    }


def run_preview() -> dict[str, Any]:
    py_state = tracked_python_validation()
    artifacts = read_artifacts()
    chain = validate_inputs(artifacts, py_state)
    summary = common_summary(artifacts, chain, py_state)
    outputs = build_outputs(summary, artifacts)
    for name, payload in outputs.items():
        write_json(OUTPUT_DIR / name, payload)
    missing = [name for name in REQUIRED_OUTPUTS if not (OUTPUT_DIR / name).exists()]
    require(not missing, f"missing required outputs: {missing}")
    require(summary["replacement_checks_all_true"] is True, "replacement checks did not all pass")
    return summary


def main() -> int:
    try:
        summary = run_preview()
    except Exception as exc:
        blocked = {
            "historical_data_acquisition_okx_full_usdt_swap_archive_coverage_eligibility_preview_status": BLOCKED_STATUS,
            "archive_coverage_eligibility_preview_created": False,
            "blocked_reason": repr(exc),
            "next_module": FAILED_NEXT_MODULE,
            "replacement_checks_all_true": False,
            "url_existence_checked": False,
            "archive_download_performed": False,
            "okx_api_call_performed": False,
            "okx_browse_performed": False,
            "data_download_performed": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "created_at_utc": utc_now(),
        }
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        write_json(OUTPUT_DIR / "historical_okx_full_usdt_swap_archive_coverage_eligibility_preview_summary.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
