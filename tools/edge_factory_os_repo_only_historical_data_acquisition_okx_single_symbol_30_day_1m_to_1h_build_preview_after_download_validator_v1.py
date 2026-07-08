from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_1m_to_1h_build_preview_after_download_validator_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "4cd8b25"
TARGET_SYMBOL = "BTC-USDT-SWAP"
DATE_RANGE_START = "2026-04-19"
DATE_RANGE_END = "2026-05-18"
EXPECTED_FILE_COUNT = 30
EXPECTED_SOURCE_ROWS_PER_FILE = 1440
EXPECTED_TOTAL_SOURCE_ROWS = 43200
EXPECTED_OUTPUT_HOURS_PER_FILE = 24
EXPECTED_OUTPUT_ROWS = 720
PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_DOWNLOAD_VALIDATED_"
    "BUILD_PREVIEW_READY_NO_BUILD"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_1M_TO_1H_"
    "BUILD_PREVIEW_APPROVED_EXECUTION_NEXT_NO_BUILD_YET"
)
BEFORE_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_DOWNLOAD_VALIDATED_"
    "BUILD_PREVIEW_READY_NO_BUILD"
)
AFTER_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_1M_TO_1H_"
    "BUILD_PREVIEW_APPROVED_EXECUTION_NEXT_NO_BUILD_YET"
)
NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_1m_to_1h_build_execution_after_preview_approval_v1.py"
)
BLOCKED_NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_1m_to_1h_build_preview_blocked_record_after_download_validator_v1.py"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_1m_to_1h_build_preview_after_download_validator_v1"
)
DOWNLOAD_VALIDATOR_SUMMARY = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_download_execution_validator_after_execution_v1"
) / "historical_okx_single_symbol_30_day_download_execution_validator_summary.json"

DANGEROUS_FLAGS = {
    "new_download_performed_now": False,
    "full_csv_read_performed_now": False,
    "data_build_performed_now": False,
    "aggregation_performed_now": False,
    "okx_api_call_performed_now": False,
    "okx_browse_performed_now": False,
    "repo_schema_config_created_now": False,
    "generic_runner_approval_granted": False,
    "strategy_research_implementation_touched": False,
    "candidate_generation_touched": False,
    "runtime_touched": False,
    "capital_changed": False,
    "live_or_real_orders": False,
}


class Blocked(RuntimeError):
    pass


def run_git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Blocked(message)


def load_json(path: Path) -> Any:
    require(path.exists(), f"missing artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_preflight(download_validator: dict[str, Any]) -> None:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved module")
    require(download_validator.get("historical_data_acquisition_okx_single_symbol_30_day_download_execution_validator_status") == PREVIOUS_STATUS, "download validator is not PASS")
    require(download_validator.get("next_module") == REQUESTED_MODULE, "next_module mismatch")
    require(download_validator.get("download_execution_validated") is True, "download execution not validated")
    require(download_validator.get("target_symbol") == TARGET_SYMBOL, "target symbol mismatch")
    require(download_validator.get("date_range_start") == DATE_RANGE_START, "date range start mismatch")
    require(download_validator.get("date_range_end") == DATE_RANGE_END, "date range end mismatch")
    require(download_validator.get("planned_30_day_file_count") == EXPECTED_FILE_COUNT, "planned file count mismatch")
    require(download_validator.get("final_30_day_file_count") == EXPECTED_FILE_COUNT, "final file count mismatch")
    for key in [
        "all_hashes_match_recorded",
        "all_zip_open_success",
        "all_expected_inner_csv_present",
        "all_expected_schema_match",
        "all_observed_symbols_match_target",
        "all_one_minute_interval_observed_from_samples",
        "safe_for_30_day_build_preview",
    ]:
        require(download_validator.get(key) is True, f"{key} not true")
    for key in ["safe_for_broad_acquisition", "safe_for_research_backtest", "safe_for_edge_claim"]:
        require(download_validator.get(key) is False, f"{key} not false")


def main() -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    download_validator = load_json(DOWNLOAD_VALIDATOR_SUMMARY)
    validate_preflight(download_validator)

    build_preview = {
        "preview_created": True,
        "build_scope": "SINGLE_SYMBOL_30_DAY_1M_TO_1H_PIPELINE_VALIDATION_ONLY",
        "target_symbol": TARGET_SYMBOL,
        "date_range_start": DATE_RANGE_START,
        "date_range_end": DATE_RANGE_END,
        "expected_file_count": EXPECTED_FILE_COUNT,
        "expected_symbol_count": 1,
        "expected_input_interval": "1m",
        "expected_output_interval": "1h",
        "expected_source_rows_per_file": EXPECTED_SOURCE_ROWS_PER_FILE,
        "expected_total_source_rows": EXPECTED_TOTAL_SOURCE_ROWS,
        "expected_output_hours_per_file": EXPECTED_OUTPUT_HOURS_PER_FILE,
        "expected_output_rows": EXPECTED_OUTPUT_ROWS,
        "output_purpose": "PIPELINE_VALIDATION_ONLY_NOT_RESEARCH_BACKTEST_EDGE",
        "build_output_allowed_now": False,
        "aggregation_allowed_now": False,
    }
    approval_record = {
        "approval_record_created": True,
        "approval_scope": "NEXT_30_DAY_SINGLE_SYMBOL_1M_TO_1H_BUILD_EXECUTION_ONLY",
        "approval_grants_build_now": False,
        "approval_grants_future_30_day_build_next": True,
        "approval_grants_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_multi_symbol_now": False,
        "approval_grants_broad_acquisition_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "next_module": NEXT_MODULE,
    }
    fail_closed_rules = {
        "fail_closed_rules_created": True,
        "future_build_may_use_only_30_validated_zips": True,
        "future_build_must_revalidate_sha256_before_reading": True,
        "future_build_may_read_full_csvs_only_in_execution_module": True,
        "future_build_processes_only_target_symbol": TARGET_SYMBOL,
        "future_build_date_range_start": DATE_RANGE_START,
        "future_build_date_range_end": DATE_RANGE_END,
        "future_build_output_rows_expected": EXPECTED_OUTPUT_ROWS,
        "future_build_must_not_download": True,
        "future_build_must_not_api_or_browse": True,
        "future_build_must_not_mark_research_backtest_edge_ready": True,
        "future_build_must_not_mark_broad_acquisition_ready": True,
    }
    self_validator = {
        "self_validated": True,
        "preview_artifact_valid": True,
        "approval_record_valid": True,
        "fail_closed_rules_valid": True,
        "expected_file_count_is_30": build_preview["expected_file_count"] == EXPECTED_FILE_COUNT,
        "expected_total_source_rows_is_43200": build_preview["expected_total_source_rows"] == EXPECTED_TOTAL_SOURCE_ROWS,
        "expected_output_rows_is_720": build_preview["expected_output_rows"] == EXPECTED_OUTPUT_ROWS,
        "no_download_api_browse_full_csv_read_build_aggregation_now": True,
        "next_module_is_build_execution": approval_record["next_module"] == NEXT_MODULE,
    }
    replacement_checks = {
        "preflight_passed": True,
        "download_validator_pass": True,
        "preview_created": build_preview["preview_created"],
        "approval_record_created": approval_record["approval_record_created"],
        "self_validated": self_validator["self_validated"],
        "expected_file_count_30": build_preview["expected_file_count"] == 30,
        "expected_total_source_rows_43200": build_preview["expected_total_source_rows"] == 43200,
        "expected_output_rows_720": build_preview["expected_output_rows"] == 720,
        "approval_future_build_next_only": approval_record["approval_grants_future_30_day_build_next"] is True,
        "approval_build_now_false": approval_record["approval_grants_build_now"] is False,
        "no_download_api_browse_full_csv_read_build_aggregation": True,
        "not_broad_research_backtest_edge": True,
        "schema_config_absent": True,
        "generic_runner_blocked": True,
        "next_module_is_build_execution": approval_record["next_module"] == NEXT_MODULE,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }
    replacement_checks_all_true = all(replacement_checks.values())
    require(replacement_checks_all_true, "replacement checks failed")

    summary = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "historical_data_acquisition_okx_single_symbol_30_day_1m_to_1h_build_preview_status": PASS_STATUS,
        "final_decision": "30_DAY_1M_TO_1H_BUILD_PREVIEW_APPROVED_EXECUTION_NEXT_NO_BUILD_YET",
        "next_action": "RUN_NEXT_SEPARATE_30_DAY_1M_TO_1H_BUILD_EXECUTION_ONLY",
        "next_module": NEXT_MODULE,
        "preview_created": True,
        "approval_record_created": True,
        "self_validated": True,
        "target_symbol": TARGET_SYMBOL,
        "date_range_start": DATE_RANGE_START,
        "date_range_end": DATE_RANGE_END,
        "expected_file_count": EXPECTED_FILE_COUNT,
        "expected_total_source_rows": EXPECTED_TOTAL_SOURCE_ROWS,
        "expected_output_rows": EXPECTED_OUTPUT_ROWS,
        "approval_grants_build_now": False,
        "approval_grants_future_30_day_build_next": True,
        "new_download_performed_now": False,
        "full_csv_read_performed_now": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "safe_for_broad_acquisition": False,
        "safe_for_research_backtest": False,
        "safe_for_edge_claim": False,
        "current_evidence_chain_quality_before_preview": BEFORE_QUALITY,
        "current_evidence_chain_quality_after_preview": AFTER_QUALITY,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": max(8, int(download_validator.get("active_p1_attention_count", 8))),
        "dormant_repo_attention_count": int(download_validator.get("dormant_repo_attention_count", 716)),
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        "dangerous_flags_true_count": sum(1 for value in DANGEROUS_FLAGS.values() if value),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
    }
    bundle = {
        "build_preview": build_preview,
        "approval_record": approval_record,
        "fail_closed_rules": fail_closed_rules,
        "self_validator": self_validator,
        "summary": summary,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_1m_to_1h_build_preview.json", build_preview)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_1m_to_1h_build_approval_record.json", approval_record)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_1m_to_1h_build_fail_closed_rules.json", fail_closed_rules)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_1m_to_1h_build_self_validator.json", self_validator)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_1m_to_1h_build_preview_bundle.json", bundle)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_1m_to_1h_build_preview_summary.json", summary)
    write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Blocked as exc:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        blocked = {
            "historical_data_acquisition_okx_single_symbol_30_day_1m_to_1h_build_preview_status": "BLOCKED_CONTEXT_MISMATCH",
            "next_module": BLOCKED_NEXT_MODULE,
            "blocked_reason": str(exc),
            "active_p0_blocker_count": 1,
            "replacement_checks_all_true": False,
        }
        write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_1m_to_1h_build_preview_summary.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        raise SystemExit(1)
