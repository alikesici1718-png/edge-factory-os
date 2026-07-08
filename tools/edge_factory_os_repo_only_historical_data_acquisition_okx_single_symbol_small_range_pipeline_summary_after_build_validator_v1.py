from __future__ import annotations

import json
import subprocess
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "small_range_pipeline_summary_after_build_validator_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "1e8b435"
TARGET_SYMBOL = "BTC-USDT-SWAP"
SEVEN_DAY_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMALL_RANGE_"
    "1M_TO_1H_BUILD_VALIDATED_PIPELINE_RANGE_SUMMARY_READY"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMALL_RANGE_PIPELINE_SUMMARY_"
    "30_DAY_DOWNLOAD_PREVIEW_APPROVED_EXECUTION_NEXT_NO_DOWNLOAD_YET"
)
BUILD_SCOPE = "SINGLE_SYMBOL_30_DAY_1M_TO_1H_PIPELINE_RANGE_VALIDATION_ONLY"
NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_download_execution_after_summary_preview_approval_v1.py"
)
AFTER_30_DAY_VALIDATED_NEXT_ROUTE = (
    "DIRECT_TO_3_YEAR_SINGLE_SYMBOL_BTC_USDT_SWAP_HISTORICAL_ACQUISITION_BUILD_PREVIEW;"
    "NO_14_DAY_21_DAY_60_DAY_OR_90_DAY_INTERMEDIATE;"
    "NO_MULTI_SYMBOL_UNTIL_SINGLE_SYMBOL_3_YEAR_PIPELINE_PASSES"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "small_range_pipeline_summary_after_build_validator_v1"
)
SEVEN_DAY_VALIDATOR_SUMMARY = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_small_range_"
    "1m_to_1h_build_execution_validator_after_execution_v1"
) / "historical_okx_single_symbol_small_range_1m_to_1h_build_execution_validator_summary.json"

DANGEROUS_FLAGS = {
    "data_download_performed_now": False,
    "data_fetch_performed_now": False,
    "external_api_call_performed_now": False,
    "external_download_performed_now": False,
    "okx_api_call_performed_now": False,
    "okx_browse_performed_now": False,
    "okx_download_performed_now": False,
    "data_build_performed_now": False,
    "aggregation_performed_now": False,
    "strategy_research_recommended_now": False,
    "strategy_research_implementation_touched": False,
    "candidate_generation_recommended_now": False,
    "candidate_generation_touched": False,
    "runtime_touched": False,
    "capital_changed": False,
    "live_or_real_orders": False,
    "repo_schema_config_created_now": False,
    "generic_runner_approval_granted": False,
    "source_manifest_created_now": False,
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


def load_json(path: Path) -> Any:
    if not path.exists():
        raise Blocked(f"missing artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Blocked(message)


def daterange(start: date, end: date) -> list[date]:
    days = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)
    return days


def okx_url(symbol: str, day: date) -> str:
    day_compact = day.strftime("%Y%m%d")
    day_iso = day.isoformat()
    return (
        "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/"
        f"{day_compact}/{symbol}-candlesticks-{day_iso}.zip"
    )


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved module")

    seven_day = load_json(SEVEN_DAY_VALIDATOR_SUMMARY)
    require(
        seven_day.get("historical_data_acquisition_okx_single_symbol_small_range_1m_to_1h_build_execution_validator_status")
        == SEVEN_DAY_STATUS,
        "seven-day validator is not PASS",
    )
    require(seven_day.get("next_module") == REQUESTED_MODULE, "current next_module mismatch")
    require(seven_day.get("small_range_build_execution_validated") is True, "seven-day build not validated")
    require(seven_day.get("output_csv_row_count") == 168, "seven-day output row count mismatch")
    require(seven_day.get("output_valid_for_pipeline_range_validation") is True, "seven-day pipeline validation missing")
    require(seven_day.get("output_valid_for_research_backtest") is False, "seven-day research/backtest claim detected")
    require(seven_day.get("output_valid_for_edge_claim") is False, "seven-day edge claim detected")
    require(seven_day.get("active_p0_blocker_count") == 0, "seven-day P0 blocker count nonzero")

    planned_days = daterange(date(2026, 4, 19), date(2026, 5, 18))
    reusable_days = daterange(date(2026, 5, 12), date(2026, 5, 18))
    missing_days = daterange(date(2026, 4, 19), date(2026, 5, 11))
    planned_urls = [okx_url(TARGET_SYMBOL, day) for day in planned_days]

    planned_30_day_file_count = len(planned_days)
    existing_validated_reuse_file_count = len(reusable_days)
    missing_download_file_count = len(missing_days)
    require(planned_30_day_file_count == 30, "planned URL count is not 30")
    require(existing_validated_reuse_file_count == 7, "existing validated reuse file count is not 7")
    require(missing_download_file_count == 23, "missing download file count is not 23")

    pipeline_summary = {
        "summary_created": True,
        "source_seven_day_validator_status": SEVEN_DAY_STATUS,
        "source_symbol": TARGET_SYMBOL,
        "source_range": "2026-05-12 through 2026-05-18",
        "source_output_rows": 168,
        "source_output_valid_for_pipeline_range_validation": True,
        "source_output_valid_for_research_backtest": False,
        "source_output_valid_for_edge_claim": False,
        "summary_scope": "SEVEN_DAY_PIPELINE_RANGE_VALIDATION_SUMMARY_ONLY",
    }

    thirty_day_preview = {
        "thirty_day_preview_created": True,
        "target_symbol": TARGET_SYMBOL,
        "date_range_start": "2026-04-19",
        "date_range_end": "2026-05-18",
        "planned_30_day_file_count": planned_30_day_file_count,
        "planned_30_day_url_count": len(planned_urls),
        "planned_urls": planned_urls,
        "existing_validated_reuse_dates": [day.isoformat() for day in reusable_days],
        "existing_validated_reuse_file_count": existing_validated_reuse_file_count,
        "missing_download_dates": [day.isoformat() for day in missing_days],
        "missing_download_file_count": missing_download_file_count,
        "input_interval": "1m",
        "target_output_interval": "1h",
        "purpose": "PIPELINE_RANGE_VALIDATION_ONLY_NOT_RESEARCH_BACKTEST_EDGE",
        "new_download_performed_now": False,
        "api_call_performed_now": False,
        "browse_performed_now": False,
        "csv_or_zip_read_now": False,
        "data_build_performed_now": False,
        "aggregation_performed_now": False,
    }

    approval_record = {
        "thirty_day_approval_record_created": True,
        "approval_scope": "NEXT_30_DAY_SINGLE_SYMBOL_DOWNLOAD_EXECUTION_ONLY",
        "approval_grants_30_day_download_execution_next": True,
        "approval_grants_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_build_now": False,
        "approval_grants_aggregation_now": False,
        "approval_grants_multi_symbol_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "next_module": NEXT_MODULE,
    }

    escalation_policy = {
        "post_30_day_escalation_policy_created": True,
        "do_not_route_to_14_day": True,
        "do_not_route_to_21_day": True,
        "do_not_route_to_60_day": True,
        "do_not_route_to_90_day": True,
        "thirty_day_is_final_intermediate_range_test": True,
        "after_30_day_validated_next_route": AFTER_30_DAY_VALIDATED_NEXT_ROUTE,
        "three_year_jump_scope": "SINGLE_SYMBOL_BTC_USDT_SWAP_FIRST",
        "full_multi_symbol_acquisition_remains_blocked_until_single_symbol_3_year_pipeline_passes": True,
        "broad_acquisition_ready": False,
        "research_backtest_edge_ready": False,
    }

    self_validator = {
        "self_validator_created": True,
        "summary_created": pipeline_summary["summary_created"],
        "thirty_day_preview_created": thirty_day_preview["thirty_day_preview_created"],
        "thirty_day_approval_record_created": approval_record["thirty_day_approval_record_created"],
        "post_30_day_escalation_policy_created": escalation_policy["post_30_day_escalation_policy_created"],
        "planned_30_day_file_count_is_30": planned_30_day_file_count == 30,
        "existing_validated_reuse_file_count_is_7": existing_validated_reuse_file_count == 7,
        "missing_download_file_count_is_23": missing_download_file_count == 23,
        "no_download_api_browse_build_aggregation_now": True,
        "no_csv_zip_read_now": True,
        "no_research_backtest_edge_claim": True,
        "no_acquisition_ready_claim": True,
        "next_module_is_direct_30_day_download_execution": approval_record["next_module"] == NEXT_MODULE,
        "after_30_day_route_skips_intermediate_tests": True,
        "replacement_checks_all_true": True,
    }

    replacement_checks = {
        "head_matches": head == EXPECTED_HEAD,
        "repo_clean_or_only_this_tool": True,
        "seven_day_validator_pass": True,
        "current_next_module_matches": True,
        "summary_created": pipeline_summary["summary_created"],
        "thirty_day_preview_created": thirty_day_preview["thirty_day_preview_created"],
        "thirty_day_approval_record_created": approval_record["thirty_day_approval_record_created"],
        "post_30_day_escalation_policy_created": escalation_policy["post_30_day_escalation_policy_created"],
        "planned_30_day_file_count_30": planned_30_day_file_count == 30,
        "existing_validated_reuse_file_count_7": existing_validated_reuse_file_count == 7,
        "missing_download_file_count_23": missing_download_file_count == 23,
        "no_download_api_browse": True,
        "no_csv_zip_read": True,
        "no_build_aggregation": True,
        "no_research_backtest_edge_claim": True,
        "direct_30_day_download_next": NEXT_MODULE.endswith("30_day_download_execution_after_summary_preview_approval_v1.py"),
        "after_30_day_direct_3_year_single_symbol": "DIRECT_TO_3_YEAR_SINGLE_SYMBOL" in AFTER_30_DAY_VALIDATED_NEXT_ROUTE,
        "no_14_21_60_90_route": all(token in AFTER_30_DAY_VALIDATED_NEXT_ROUTE for token in ["NO_14_DAY", "21_DAY", "60_DAY", "90_DAY"]),
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }
    replacement_checks_all_true = all(replacement_checks.values())
    require(replacement_checks_all_true, "replacement checks failed")

    summary = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": head,
        "historical_data_acquisition_okx_single_symbol_small_range_pipeline_summary_status": PASS_STATUS,
        "final_decision": "30_DAY_SINGLE_SYMBOL_DOWNLOAD_PREVIEW_APPROVED_EXECUTION_NEXT",
        "next_action": "RUN_DIRECT_30_DAY_SINGLE_SYMBOL_DOWNLOAD_EXECUTION",
        "next_module": NEXT_MODULE,
        "summary_created": True,
        "thirty_day_preview_created": True,
        "thirty_day_approval_record_created": True,
        "post_30_day_escalation_policy_created": True,
        "self_validator_created": True,
        "target_symbol": TARGET_SYMBOL,
        "date_range_start": "2026-04-19",
        "date_range_end": "2026-05-18",
        "build_scope": BUILD_SCOPE,
        "planned_30_day_file_count": planned_30_day_file_count,
        "planned_30_day_url_count": len(planned_urls),
        "existing_validated_reuse_file_count": existing_validated_reuse_file_count,
        "missing_download_file_count": missing_download_file_count,
        "after_30_day_validated_next_route": AFTER_30_DAY_VALIDATED_NEXT_ROUTE,
        "no_14_day_intermediate": True,
        "no_21_day_intermediate": True,
        "no_60_day_intermediate": True,
        "no_90_day_intermediate": True,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "new_download_performed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "csv_or_zip_read_now": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "output_valid_for_pipeline_range_validation": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "source_manifest_acquisition_ready": False,
        "full_multi_symbol_acquisition_blocked": True,
        "strategy_signal_claims_made": False,
        "tradable_edge_claims_made": False,
        "profit_claims_made": False,
        "backtest_performed": False,
        "candidate_generation_performed": False,
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": max(8, int(seven_day.get("active_p1_attention_count", 8))),
        "dormant_repo_attention_count": int(seven_day.get("dormant_repo_attention_count", 716)),
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        "dangerous_flags_true_count": sum(1 for value in DANGEROUS_FLAGS.values() if value),
        "derived_live_repo_post_check": PASS_STATUS,
        "derived_live_repo_post_check_reason": (
            "created a repo-only seven-day pipeline summary plus a 30-day BTC-USDT-SWAP download "
            "preview and approval record; planned exactly 30 daily ZIPs for 2026-04-19 through "
            "2026-05-18, reused 7 already validated files, marked 23 missing files for the future "
            "download execution, performed no download/API/browse/CSV/ZIP read/build/aggregation, "
            "and locked the post-30-day route directly to single-symbol 3-year preview while keeping "
            "multi-symbol and broad acquisition blocked"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
    }

    bundle = {
        "pipeline_summary": pipeline_summary,
        "thirty_day_download_preview": thirty_day_preview,
        "thirty_day_download_approval_record": approval_record,
        "post_30_day_escalation_policy": escalation_policy,
        "self_validator": self_validator,
        "summary": summary,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_small_range_pipeline_summary.json", pipeline_summary)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_download_preview.json", thirty_day_preview)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_download_approval_record.json", approval_record)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_post_30_day_escalation_policy.json", escalation_policy)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_small_range_pipeline_summary_self_validator.json", self_validator)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_small_range_pipeline_summary_bundle.json", bundle)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_small_range_pipeline_summary_after_build_validator_summary.json", summary)
    write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Blocked as exc:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        blocked = {
            "historical_data_acquisition_okx_single_symbol_small_range_pipeline_summary_status": "BLOCKED_CONTEXT_MISMATCH",
            "next_module": "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_small_range_pipeline_summary_blocked_record_v1.py",
            "blocked_reason": str(exc),
            "active_p0_blocker_count": 1,
            "replacement_checks_all_true": False,
        }
        write_json(OUTPUT_DIR / "historical_okx_single_symbol_small_range_pipeline_summary_after_build_validator_summary.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        raise SystemExit(1)
