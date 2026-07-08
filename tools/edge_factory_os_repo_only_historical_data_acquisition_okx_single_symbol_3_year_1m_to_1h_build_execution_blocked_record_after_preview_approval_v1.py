from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_1m_to_1h_build_execution_blocked_record_after_preview_approval_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "7494a27"
TARGET_SYMBOL = "BTC-USDT-SWAP"
EXPECTED_FILE_COUNT = 1053
EXPECTED_TOTAL_SOURCE_ROWS = 1_516_320
OBSERVED_SOURCE_ROWS = 1_516_641
DUPLICATE_OPEN_TIME_COUNT = 321
MISSING_MINUTE_COUNT = 0
PREVIOUS_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_1M_TO_1H_BUILD_EXECUTION"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_BUILD_BLOCKED_RECORD_"
    "DUPLICATE_MINUTE_RESOLUTION_DIAGNOSTIC_READY"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_BUILD_BLOCKED_RECORD"
)
BLOCK_REASON = "DUPLICATE_OPEN_TIME_ROWS"
BEFORE_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_1M_TO_1H_BUILD_EXECUTION_"
    "BLOCKED_DUPLICATE_OPEN_TIME_ROWS"
)
AFTER_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_BUILD_BLOCKED_DUPLICATE_"
    "MINUTE_RESOLUTION_DIAGNOSTIC_READY"
)
NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_duplicate_minute_resolution_diagnostic_after_blocked_build_v1.py"
)
FAILED_NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_build_blocked_record_failed_review_v1.py"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
BUILD_EXECUTION_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_1m_to_1h_build_execution_after_preview_approval_v1"
)

ARTIFACTS = {
    "latest": BUILD_EXECUTION_DIR / (
        "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
        "3_year_1m_to_1h_build_execution_after_preview_approval_v1_latest.json"
    ),
    "summary": BUILD_EXECUTION_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_build_execution_summary.json",
    "execution_report": BUILD_EXECUTION_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_build_execution_report.json",
    "gap_duplicate_report": BUILD_EXECUTION_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_gap_duplicate_report.json",
    "schema_report": BUILD_EXECUTION_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_schema_validation_report.json",
    "provenance_report": BUILD_EXECUTION_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_output_provenance_report.json",
    "compliance_report": BUILD_EXECUTION_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_build_execution_compliance_report.json",
}

DANGEROUS_FLAGS = {
    "download_performed_now": False,
    "api_call_performed_now": False,
    "browse_performed_now": False,
    "url_fetch_performed_now": False,
    "full_csv_read_performed_now": False,
    "new_data_build_performed_now": False,
    "aggregation_performed_now": False,
    "output_1h_csv_created_now": False,
    "synthetic_fill_used": False,
    "forward_fill_used": False,
    "backfill_used": False,
    "research_backtest_edge_claim_made": False,
    "broad_acquisition_ready_claim_made": False,
    "runtime_touched": False,
    "capital_changed": False,
    "live_or_real_orders": False,
    "schema_or_config_created": False,
    "generic_runner_approval_granted": False,
}


class Blocked(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def repo_has_only_this_tool_change() -> bool:
    status = run_git(["status", "--short"]).splitlines()
    if not status:
        return True
    approved_rel = APPROVED_TOOL.relative_to(REPO_ROOT).as_posix()
    return all(line[3:].replace("\\", "/") == approved_rel for line in status)


def tracked_python_count() -> int:
    return sum(1 for path in run_git(["ls-files"]).splitlines() if path.endswith(".py"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Blocked(message)


def load_json(path: Path, label: str, exists: dict[str, bool], valid: dict[str, bool]) -> Any:
    exists[label] = path.exists()
    require(path.exists(), f"missing artifact {label}: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        valid[label] = False
        raise Blocked(f"invalid JSON artifact {label}: {exc}") from exc
    valid[label] = True
    require(isinstance(data, dict), f"artifact {label} is not a JSON object")
    return data


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_preflight(summary: dict[str, Any], gap: dict[str, Any], schema: dict[str, Any], provenance: dict[str, Any], compliance: dict[str, Any]) -> None:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved module")
    require(
        summary.get("historical_data_acquisition_okx_single_symbol_3_year_1m_to_1h_build_execution_status")
        == PREVIOUS_STATUS,
        "previous build status mismatch",
    )
    require(summary.get("next_module") == REQUESTED_MODULE, "next_module mismatch")
    require(summary.get("build_execution_performed") is False, "blocked build unexpectedly marked performed")
    require(summary.get("target_symbol") == TARGET_SYMBOL, "target symbol mismatch")
    require(summary.get("expected_file_count") == EXPECTED_FILE_COUNT, "expected file count mismatch")
    require(summary.get("file_count_processed") == EXPECTED_FILE_COUNT, "file count processed mismatch")
    require(summary.get("all_source_zips_exist") is True, "source ZIP existence flag mismatch")
    require(summary.get("all_source_zip_sha256_match") is True, "source ZIP hash flag mismatch")
    require(summary.get("all_expected_inner_csv_present") is True, "inner CSV flag mismatch")
    require(summary.get("schema_match") is True, "schema flag mismatch")
    require(summary.get("full_csv_read_performed") is True, "prior full CSV read evidence missing")
    require(summary.get("source_row_count_total") == OBSERVED_SOURCE_ROWS, "source row count mismatch")
    require(summary.get("expected_total_source_rows") == EXPECTED_TOTAL_SOURCE_ROWS, "expected source row count mismatch")
    require(summary.get("source_row_count_by_file_valid") is False, "source row by file flag mismatch")
    require(summary.get("unique_symbol_count") == 1, "unique symbol count mismatch")
    require(summary.get("observed_symbol") == TARGET_SYMBOL, "observed symbol mismatch")
    require(summary.get("open_time_monotonic_by_file") is False, "open time monotonic flag mismatch")
    require(summary.get("duplicate_open_time_count_total") == DUPLICATE_OPEN_TIME_COUNT, "duplicate count mismatch")
    require(summary.get("missing_minute_count_total") == MISSING_MINUTE_COUNT, "missing minute count mismatch")
    require(summary.get("aggregation_performed_now") is False, "aggregation unexpectedly performed")
    require(summary.get("data_build_performed") is False, "data build unexpectedly performed")
    require(summary.get("output_csv_created") is False, "output CSV unexpectedly created")
    require(summary.get("active_p0_blocker_count") == 1, "P0 blocker count mismatch")
    require(summary.get("replacement_checks_all_true") is False, "blocked execution unexpectedly passed replacement checks")
    require(gap.get("duplicate_open_time_count_total") == DUPLICATE_OPEN_TIME_COUNT, "gap report duplicate count mismatch")
    require(gap.get("missing_minute_count_total") == MISSING_MINUTE_COUNT, "gap report missing minute count mismatch")
    require(schema.get("schema_match") is True, "schema report mismatch")
    require(provenance.get("output_row_count") == 0, "provenance output row count mismatch")
    require(provenance.get("url_iteration_performed") is False, "provenance URL iteration flag mismatch")
    for key in ["no_new_download", "no_api", "no_browse", "no_url_fetch", "no_url_iteration"]:
        require(compliance.get(key) is True, f"compliance {key} mismatch")
    for key in ["output_valid_for_research_backtest", "output_valid_for_edge_claim", "broad_acquisition_ready", "source_manifest_acquisition_ready"]:
        require(compliance.get(key) is False, f"compliance {key} mismatch")


def main() -> None:
    generated_at = utc_now()
    exists: dict[str, bool] = {}
    valid: dict[str, bool] = {}
    artifacts = {
        label: load_json(path, label, exists, valid)
        for label, path in ARTIFACTS.items()
    }
    summary = artifacts["summary"]
    validate_preflight(
        summary,
        artifacts["gap_duplicate_report"],
        artifacts["schema_report"],
        artifacts["provenance_report"],
        artifacts["compliance_report"],
    )

    blocked_record = {
        "blocked_record_created": True,
        "build_execution_blocked": True,
        "block_reason": BLOCK_REASON,
        "source_status": summary.get("historical_data_acquisition_okx_single_symbol_3_year_1m_to_1h_build_execution_status"),
        "target_symbol": TARGET_SYMBOL,
        "expected_file_count": EXPECTED_FILE_COUNT,
        "file_count_processed": EXPECTED_FILE_COUNT,
        "source_row_count_total": OBSERVED_SOURCE_ROWS,
        "expected_total_source_rows": EXPECTED_TOTAL_SOURCE_ROWS,
        "duplicate_open_time_count_total": DUPLICATE_OPEN_TIME_COUNT,
        "missing_minute_count_total": MISSING_MINUTE_COUNT,
        "active_p0_blocker_count": 1,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "output_csv_created": False,
        "strict_3y_completeness_claimed": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "source_manifest_acquisition_ready": False,
        "p0_remains_active_until_duplicate_diagnosis_resolves_it": True,
    }
    duplicate_resolution_preview = {
        "duplicate_resolution_preview_created": True,
        "preview_only": True,
        "execution_performed_now": False,
        "target_symbol": TARGET_SYMBOL,
        "duplicate_open_time_count_total": DUPLICATE_OPEN_TIME_COUNT,
        "future_duplicate_resolution_module_may_read_1053_csvs_again_for_duplicate_diagnosis_only": True,
        "future_duplicate_resolution_must_identify_duplicate_open_time_rows": True,
        "duplicate_classification_policy": {
            "exact_duplicate_rows": (
                "same open_time, same OHLCV, same vol, same vol_ccy, same vol_quote, and same confirm"
            ),
            "conflicting_duplicate_rows": (
                "same open_time but different OHLCV, volume field, or confirm value"
            ),
        },
        "if_all_duplicates_exact": {
            "future_exact_deduped_rebuild_may_be_approved_by_next_diagnostic": True,
            "keep_one_row_per_open_time": True,
            "discard_identical_duplicate_rows": True,
            "record_all_removals_in_audit_artifact": True,
        },
        "if_any_conflicting_duplicate_exists": {
            "fail_closed": True,
            "route_to_data_quality_anomaly_review": True,
            "do_not_choose_between_conflicting_rows_without_separate_policy": True,
        },
        "never_synthesize_missing_minutes": True,
        "never_fill": True,
        "never_alter_ohlcv_values": True,
        "never_mark_research_backtest_edge_ready": True,
        "download_allowed": False,
        "api_allowed": False,
        "browse_allowed": False,
        "build_or_aggregation_performed_now": False,
    }
    approval_record = {
        "duplicate_resolution_approval_record_created": True,
        "approval_scope": "NEXT_DUPLICATE_MINUTE_DIAGNOSIS_ONLY_AFTER_BLOCKED_3_YEAR_BUILD",
        "approval_grants_duplicate_resolution_now": False,
        "approval_grants_future_duplicate_diagnosis_next": True,
        "approval_grants_dedupe_execution_now": False,
        "approval_grants_rebuild_now": False,
        "approval_grants_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "next_module": NEXT_MODULE,
    }
    limitations_report = {
        "build_blocked_limitations_report_created": True,
        "strict_3y_completeness_claimed": False,
        "completed_1h_output_exists": False,
        "pipeline_output_valid_for_research_backtest": False,
        "pipeline_output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "known_p0_blocker": BLOCK_REASON,
        "duplicate_open_time_count_total": DUPLICATE_OPEN_TIME_COUNT,
        "required_next_step": "DUPLICATE_MINUTE_RESOLUTION_DIAGNOSTIC_ONLY",
        "download_api_browse_forbidden": True,
        "new_build_aggregation_forbidden_in_this_module": True,
    }
    self_validator = {
        "self_validator_created": True,
        "preflight_passed": True,
        "required_source_artifacts_exist": all(exists.values()),
        "required_source_artifacts_valid_json": all(valid.values()),
        "blocked_record_valid": blocked_record["build_execution_blocked"] is True
        and blocked_record["block_reason"] == BLOCK_REASON
        and blocked_record["duplicate_open_time_count_total"] == DUPLICATE_OPEN_TIME_COUNT,
        "duplicate_resolution_preview_valid": duplicate_resolution_preview["duplicate_resolution_preview_created"] is True
        and duplicate_resolution_preview["execution_performed_now"] is False,
        "approval_record_valid": approval_record["approval_grants_future_duplicate_diagnosis_next"] is True
        and approval_record["approval_grants_rebuild_now"] is False
        and approval_record["approval_grants_download_now"] is False
        and approval_record["approval_grants_research_backtest_edge_now"] is False,
        "no_download_api_browse_build_aggregation_now": all(value is False for value in DANGEROUS_FLAGS.values()),
        "p0_remains_active": blocked_record["active_p0_blocker_count"] == 1,
        "next_module_valid": approval_record["next_module"] == NEXT_MODULE,
    }
    replacement_checks = {
        "preflight_passed": True,
        "blocked_record_created": blocked_record["blocked_record_created"],
        "duplicate_resolution_preview_created": duplicate_resolution_preview["duplicate_resolution_preview_created"],
        "duplicate_resolution_approval_record_created": approval_record["duplicate_resolution_approval_record_created"],
        "build_execution_blocked": blocked_record["build_execution_blocked"],
        "block_reason_duplicate_open_time_rows": blocked_record["block_reason"] == BLOCK_REASON,
        "target_symbol_valid": blocked_record["target_symbol"] == TARGET_SYMBOL,
        "file_count_valid": blocked_record["file_count_processed"] == EXPECTED_FILE_COUNT,
        "source_rows_preserved": blocked_record["source_row_count_total"] == OBSERVED_SOURCE_ROWS,
        "expected_rows_preserved": blocked_record["expected_total_source_rows"] == EXPECTED_TOTAL_SOURCE_ROWS,
        "duplicate_count_preserved": blocked_record["duplicate_open_time_count_total"] == DUPLICATE_OPEN_TIME_COUNT,
        "missing_minutes_zero": blocked_record["missing_minute_count_total"] == MISSING_MINUTE_COUNT,
        "p0_active": blocked_record["active_p0_blocker_count"] == 1,
        "approval_future_duplicate_diagnosis_next": approval_record["approval_grants_future_duplicate_diagnosis_next"] is True,
        "approval_rebuild_now_false": approval_record["approval_grants_rebuild_now"] is False,
        "approval_download_now_false": approval_record["approval_grants_download_now"] is False,
        "approval_research_edge_now_false": approval_record["approval_grants_research_backtest_edge_now"] is False,
        "no_build_aggregation_output": blocked_record["data_build_performed"] is False
        and blocked_record["aggregation_performed_now"] is False
        and blocked_record["output_csv_created"] is False,
        "strict_3y_not_claimed": blocked_record["strict_3y_completeness_claimed"] is False,
        "not_research_backtest_edge_broad": blocked_record["output_valid_for_research_backtest"] is False
        and blocked_record["output_valid_for_edge_claim"] is False
        and blocked_record["broad_acquisition_ready"] is False,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        "next_module_valid": approval_record["next_module"] == NEXT_MODULE,
    }
    replacement_checks_all_true = all(replacement_checks.values())
    require(replacement_checks_all_true, "replacement checks failed")

    summary_payload = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "historical_data_acquisition_okx_single_symbol_3_year_build_blocked_record_status": PASS_STATUS,
        "blocked_record_created": True,
        "duplicate_resolution_preview_created": True,
        "duplicate_resolution_approval_record_created": True,
        "build_execution_blocked": True,
        "block_reason": BLOCK_REASON,
        "target_symbol": TARGET_SYMBOL,
        "expected_file_count": EXPECTED_FILE_COUNT,
        "file_count_processed": EXPECTED_FILE_COUNT,
        "source_row_count_total": OBSERVED_SOURCE_ROWS,
        "expected_total_source_rows": EXPECTED_TOTAL_SOURCE_ROWS,
        "duplicate_open_time_count_total": DUPLICATE_OPEN_TIME_COUNT,
        "missing_minute_count_total": MISSING_MINUTE_COUNT,
        "active_p0_blocker_count": 1,
        "approval_grants_future_duplicate_diagnosis_next": True,
        "approval_grants_rebuild_now": False,
        "approval_grants_download_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "output_csv_created": False,
        "strict_3y_completeness_claimed": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "current_evidence_chain_quality_before_blocked_record": BEFORE_QUALITY,
        "current_evidence_chain_quality_after_blocked_record": AFTER_QUALITY,
        "next_module": NEXT_MODULE,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": True,
        "tracked_python_count_at_blocked_record_run": tracked_python_count(),
    }
    bundle = {
        "blocked_record": blocked_record,
        "duplicate_resolution_preview": duplicate_resolution_preview,
        "duplicate_resolution_approval_record": approval_record,
        "limitations_report": limitations_report,
        "self_validator": self_validator,
        "summary": summary_payload,
    }
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_build_blocked_record.json", blocked_record)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_duplicate_minute_resolution_preview.json", duplicate_resolution_preview)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_duplicate_minute_resolution_approval_record.json", approval_record)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_build_blocked_limitations_report.json", limitations_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_build_blocked_self_validator.json", self_validator)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_build_blocked_bundle_summary.json", bundle)
    write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", summary_payload)
    print(json.dumps(summary_payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Blocked as exc:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        blocked = {
            "module_name": MODULE_NAME,
            "generated_at_utc": utc_now(),
            "historical_data_acquisition_okx_single_symbol_3_year_build_blocked_record_status": BLOCKED_STATUS,
            "blocked_record_created": False,
            "duplicate_resolution_preview_created": False,
            "duplicate_resolution_approval_record_created": False,
            "build_execution_blocked": True,
            "block_reason": BLOCK_REASON,
            "target_symbol": TARGET_SYMBOL,
            "source_row_count_total": OBSERVED_SOURCE_ROWS,
            "expected_total_source_rows": EXPECTED_TOTAL_SOURCE_ROWS,
            "duplicate_open_time_count_total": DUPLICATE_OPEN_TIME_COUNT,
            "missing_minute_count_total": MISSING_MINUTE_COUNT,
            "active_p0_blocker_count": 1,
            "approval_grants_future_duplicate_diagnosis_next": False,
            "approval_grants_rebuild_now": False,
            "approval_grants_download_now": False,
            "approval_grants_research_backtest_edge_now": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "output_csv_created": False,
            "strict_3y_completeness_claimed": False,
            "output_valid_for_research_backtest": False,
            "output_valid_for_edge_claim": False,
            "broad_acquisition_ready": False,
            "current_evidence_chain_quality_before_blocked_record": BEFORE_QUALITY,
            "current_evidence_chain_quality_after_blocked_record": BEFORE_QUALITY,
            "next_module": FAILED_NEXT_MODULE,
            "replacement_checks_all_true": False,
            "blocked_reason": str(exc),
        }
        write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        raise SystemExit(1)
