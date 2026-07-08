from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_and_"
    "multi_symbol_expansion_preview_after_single_symbol_3_year_summary_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "e021262"
PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_POLICY_CLEAN_"
    "PIPELINE_SUMMARY_CLOSED_MULTI_SYMBOL_EXPANSION_PREVIEW_READY"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SYMBOL_UNIVERSE_AND_MULTI_SYMBOL_"
    "EXPANSION_PREVIEW_APPROVED_10_SYMBOL_PILOT_DOWNLOAD_EXECUTION_READY"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_SYMBOL_UNIVERSE_AND_MULTI_SYMBOL_"
    "EXPANSION_PREVIEW"
)
AFTER_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_DOWNLOAD_PREVIEW_APPROVED_"
    "EXECUTION_READY"
)

TARGET_SYMBOL = "BTC-USDT-SWAP"
PILOT_SYMBOLS = [
    "BTC-USDT-SWAP",
    "ETH-USDT-SWAP",
    "SOL-USDT-SWAP",
    "XRP-USDT-SWAP",
    "DOGE-USDT-SWAP",
    "ADA-USDT-SWAP",
    "AVAX-USDT-SWAP",
    "LINK-USDT-SWAP",
    "LTC-USDT-SWAP",
    "DOT-USDT-SWAP",
]
PILOT_PURPOSE = "MULTI_SYMBOL_DOWNLOAD_AND_PIPELINE_SCALING_VALIDATION_ONLY_NOT_RESEARCH_NOT_EDGE"
DATE_RANGE_START = "2023-07-01"
DATE_RANGE_END = "2026-05-18"
EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 1_053
EXPECTED_REUSE_SYMBOL_COUNT = 1
EXPECTED_NEW_SYMBOL_COUNT = 9
EXPECTED_TOTAL_PILOT_FILE_COUNT = 10_530
EXPECTED_REUSED_FILE_COUNT = 1_053
EXPECTED_NEW_DOWNLOAD_FILE_COUNT = 9_477
EXPECTED_DORMANT_REPO_ATTENTION_COUNT = 716
RECOMMENDED_ROUTE = "OKX_USDT_SWAP_SYMBOL_UNIVERSE_AND_MULTI_SYMBOL_EXPANSION_PREVIEW"
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "download_execution_after_expansion_preview_approval_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_and_"
    "multi_symbol_expansion_preview_blocked_record_v1.py"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
PREVIOUS_SUMMARY_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_policy_clean_pipeline_summary_after_rebuild_validator_v1"
)
PREVIOUS_BUNDLE_SUMMARY = (
    PREVIOUS_SUMMARY_DIR
    / "historical_okx_single_symbol_3_year_policy_clean_pipeline_summary_bundle_summary.json"
)
PREVIOUS_PIPELINE_SUMMARY = (
    PREVIOUS_SUMMARY_DIR
    / "historical_okx_single_symbol_3_year_policy_clean_pipeline_summary.json"
)
PREVIOUS_ROUTE_DECISION = (
    PREVIOUS_SUMMARY_DIR / "historical_okx_single_symbol_3_year_next_expansion_route_decision.json"
)

DANGEROUS_FLAGS = {
    "data_download_performed": False,
    "data_build_performed": False,
    "aggregation_performed_now": False,
    "okx_api_call_performed": False,
    "okx_browse_performed": False,
    "url_fetch_performed": False,
    "csv_read_performed": False,
    "zip_read_performed": False,
    "parquet_read_performed": False,
    "strategy_research_performed": False,
    "backtest_performed": False,
    "edge_profit_claim_made": False,
    "full_universe_acquisition_performed": False,
    "broad_acquisition_ready": False,
    "runtime_touched": False,
    "capital_changed": False,
    "live_or_real_orders": False,
    "schema_or_config_created": False,
    "generic_runner_approval_granted": False,
}

P1_ATTENTION_ITEMS = [
    "bounded_10_symbol_pilot_only",
    "pilot_symbols_not_independently_verified_here",
    "not_survivorship_safe_full_universe",
    "btc_usdt_swap_reuse_expected",
    "nine_new_symbols_require_future_download_execution",
    "future_execution_download_only",
    "no_build_or_aggregation_in_future_download_execution",
    "header_and_sample_rows_only_in_future_download_execution",
    "full_universe_acquisition_blocked",
    "strategy_backtest_edge_blocked",
    "broad_acquisition_not_ready",
    "runtime_capital_live_untouched",
]


class PreviewBlocked(RuntimeError):
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
        raise PreviewBlocked(message)


def load_json(path: Path, label: str) -> dict[str, Any]:
    require(path.exists(), f"missing JSON artifact {label}: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PreviewBlocked(f"invalid JSON artifact {label}: {exc}") from exc
    require(isinstance(data, dict), f"JSON artifact {label} is not an object")
    return data


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_preconditions() -> dict[str, Any]:
    head = run_git(["rev-parse", "HEAD"])
    require(head.startswith(EXPECTED_HEAD), f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved module")
    require(Path(__file__).resolve() == APPROVED_TOOL.resolve(), "running unexpected module path")
    return {
        "head": head,
        "expected_head": EXPECTED_HEAD,
        "repo_clean_or_only_this_tool": True,
        "tracked_python_count": tracked_python_count(),
    }


def validate_previous_summary() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    bundle = load_json(PREVIOUS_BUNDLE_SUMMARY, "previous_bundle_summary")
    pipeline = load_json(PREVIOUS_PIPELINE_SUMMARY, "previous_pipeline_summary")
    route = load_json(PREVIOUS_ROUTE_DECISION, "previous_route_decision")

    require(
        bundle.get("historical_data_acquisition_okx_single_symbol_3_year_policy_clean_pipeline_summary_status")
        == PREVIOUS_STATUS,
        "previous status mismatch",
    )
    require(bundle.get("next_module") == REQUESTED_MODULE, "current next_module mismatch")
    require(bundle.get("single_symbol_3_year_policy_clean_pipeline_closed_successfully") is True, "single-symbol pipeline not closed")
    require(bundle.get("target_symbol") == TARGET_SYMBOL, "target symbol mismatch")
    require(bundle.get("output_1h_row_count") == 25_272, "output row count mismatch")
    require(bundle.get("complete_1h_row_count") == 25_271, "complete hour count mismatch")
    require(bundle.get("incomplete_1h_row_count") == 1, "incomplete hour count mismatch")
    require(bundle.get("strict_3y_completeness_claimed") is False, "strict 3y completeness claim detected")
    require(bundle.get("output_valid_for_pipeline_validation") is True, "pipeline validation flag missing")
    require(bundle.get("output_valid_for_research_backtest") is False, "research/backtest claim detected")
    require(bundle.get("output_valid_for_edge_claim") is False, "edge claim detected")
    require(bundle.get("broad_acquisition_ready") is False, "broad acquisition ready claim detected")
    require(bundle.get("source_manifest_acquisition_ready") is False, "source manifest ready claim detected")
    require(bundle.get("recommended_next_route") == RECOMMENDED_ROUTE, "recommended route mismatch")
    require(bundle.get("active_p0_blocker_count") == 0, "previous active P0 blocker count nonzero")
    require(int(bundle.get("active_p1_attention_count", 0)) >= 12, "previous active P1 attention count too low")
    require(bundle.get("replacement_checks_all_true") is True, "previous replacement checks not true")

    require(pipeline.get("multi_symbol_universe_resolved") is False, "pipeline claims multi-symbol universe resolved")
    require(pipeline.get("multi_symbol_acquisition_ready") is False, "pipeline claims multi-symbol acquisition ready")
    require(route.get("recommended_next_route") == RECOMMENDED_ROUTE, "route artifact recommendation mismatch")
    require(route.get("do_not_route_to_strategy_backtest_yet") is True, "route allows strategy/backtest")
    require(
        route.get("do_not_route_directly_to_full_285_symbol_acquisition_execution") is True,
        "route allows direct full 285-symbol execution",
    )
    require(
        route.get("next_safe_route_is_symbol_universe_multi_symbol_expansion_preview") is True,
        "route does not require symbol-universe preview",
    )
    return bundle, pipeline, route


def build_outputs(
    preconditions: dict[str, Any],
    previous_bundle: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    expected_total = len(PILOT_SYMBOLS) * EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL
    expected_new_download = EXPECTED_NEW_SYMBOL_COUNT * EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL
    require(len(PILOT_SYMBOLS) == 10, "pilot_symbol_count is not 10")
    require(len(set(PILOT_SYMBOLS)) == 10, "pilot symbols are not unique")
    require(PILOT_SYMBOLS[0] == TARGET_SYMBOL, "existing validated symbol is not first pilot symbol")
    require(expected_total == EXPECTED_TOTAL_PILOT_FILE_COUNT, "expected total pilot file count mismatch")
    require(expected_new_download == EXPECTED_NEW_DOWNLOAD_FILE_COUNT, "expected new download file count mismatch")
    require(EXPECTED_REUSED_FILE_COUNT == EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL, "expected reused file count mismatch")

    preview = {
        "symbol_universe_expansion_preview_created": True,
        "multi_symbol_pilot_preview_created": True,
        "preview_scope": "BOUNDED_10_SYMBOL_OKX_USDT_SWAP_PILOT_PREVIEW_ONLY",
        "pilot_symbol_count": len(PILOT_SYMBOLS),
        "pilot_symbols": PILOT_SYMBOLS,
        "pilot_scope": "OKX_USDT_PERPETUAL_SWAP_CANDIDATES",
        "pilot_purpose": PILOT_PURPOSE,
        "pilot_includes_existing_validated_symbol": TARGET_SYMBOL in PILOT_SYMBOLS,
        "existing_validated_symbol": TARGET_SYMBOL,
        "expected_reuse_symbol_count": EXPECTED_REUSE_SYMBOL_COUNT,
        "expected_new_symbol_count": EXPECTED_NEW_SYMBOL_COUNT,
        "date_range_start": DATE_RANGE_START,
        "date_range_end": DATE_RANGE_END,
        "expected_daily_file_count_per_symbol": EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "expected_total_pilot_file_count": EXPECTED_TOTAL_PILOT_FILE_COUNT,
        "expected_reused_file_count": EXPECTED_REUSED_FILE_COUNT,
        "expected_new_download_file_count": EXPECTED_NEW_DOWNLOAD_FILE_COUNT,
        "full_universe_acquisition_allowed_now": False,
        "strategy_backtest_edge_allowed_now": False,
        "survivorship_safe_full_universe_claimed": False,
        "all_symbols_independently_verified_in_this_module": False,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
    }

    manifest = {
        "multi_symbol_pilot_preview_created": True,
        "pilot_symbol_count": len(PILOT_SYMBOLS),
        "pilot_symbols": PILOT_SYMBOLS,
        "existing_validated_symbol": TARGET_SYMBOL,
        "symbols_reusing_existing_validated_files": [TARGET_SYMBOL],
        "symbols_requiring_future_download_execution": [symbol for symbol in PILOT_SYMBOLS if symbol != TARGET_SYMBOL],
        "expected_reuse_symbol_count": EXPECTED_REUSE_SYMBOL_COUNT,
        "expected_new_symbol_count": EXPECTED_NEW_SYMBOL_COUNT,
        "date_range_start": DATE_RANGE_START,
        "date_range_end": DATE_RANGE_END,
        "expected_daily_file_count_per_symbol": EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "expected_total_pilot_file_set_count": EXPECTED_TOTAL_PILOT_FILE_COUNT,
        "expected_reused_file_count": EXPECTED_REUSED_FILE_COUNT,
        "expected_new_download_file_count": EXPECTED_NEW_DOWNLOAD_FILE_COUNT,
        "future_execution_may_reuse_validated_btc_file_set": True,
        "future_execution_must_download_only_approved_daily_zips_for_new_symbols": True,
        "urls_materialized_in_this_preview": False,
        "full_universe_claimed": False,
    }

    resource_policy = {
        "resource_limits_policy_created": True,
        "max_symbols": 10,
        "max_new_symbols": 9,
        "max_total_file_set": EXPECTED_TOTAL_PILOT_FILE_COUNT,
        "max_new_download_files": EXPECTED_NEW_DOWNLOAD_FILE_COUNT,
        "max_zip_size_per_file_mb": 100,
        "max_csv_sample_rows_per_file": 5,
        "no_full_csv_read_during_download_execution": True,
        "no_build_aggregation_during_download_execution": True,
        "fail_closed_if_non_approved_symbol_appears": True,
        "fail_closed_if_non_approved_url_appears": True,
        "future_execution_allowed_actions": [
            "reuse_validated_btc_usdt_swap_1053_file_set",
            "download_approved_daily_zips_for_9_new_symbols",
            "compute_sha256_after_each_download",
            "inspect_zip_inventory_safely",
            "read_header_and_at_most_5_sample_rows_per_file",
            "record_per_symbol_coverage_schema_hash_and_provenance_reports",
        ],
        "future_execution_forbidden_actions": [
            "data_build",
            "aggregation",
            "strategy_backtest",
            "edge_profit_claim",
            "full_universe_ready_claim",
            "broad_acquisition_ready_claim",
            "runtime_capital_live_touch",
        ],
    }

    approval = {
        "pilot_download_approval_record_created": True,
        "approval_scope": "NEXT_10_SYMBOL_PILOT_DOWNLOAD_EXECUTION_ONLY",
        "approval_grants_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_url_fetch_now": False,
        "approval_grants_future_10_symbol_pilot_download_next": True,
        "approval_grants_build_now": False,
        "approval_grants_aggregation_now": False,
        "approval_grants_strategy_backtest_edge_now": False,
        "approval_grants_full_universe_acquisition_now": False,
        "approval_grants_runtime_capital_live_now": False,
        "approved_pilot_symbols": PILOT_SYMBOLS,
        "approved_reuse_symbol": TARGET_SYMBOL,
        "approved_new_symbol_count": EXPECTED_NEW_SYMBOL_COUNT,
        "approved_new_download_file_count": EXPECTED_NEW_DOWNLOAD_FILE_COUNT,
        "next_module": NEXT_MODULE_PASS,
    }

    limitations = {
        "limitations_report_created": True,
        "not_survivorship_safe_full_universe": True,
        "all_symbols_independently_verified_in_this_module": False,
        "full_universe_acquisition_allowed_now": False,
        "strategy_backtest_edge_allowed_now": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "source_manifest_acquisition_ready": False,
        "pilot_is_scaling_validation_only": True,
        "future_download_execution_remains_download_only": True,
        "future_build_and_aggregation_remain_blocked": True,
        "single_symbol_prior_summary_status": previous_bundle.get(
            "historical_data_acquisition_okx_single_symbol_3_year_policy_clean_pipeline_summary_status"
        ),
    }

    replacement_checks = {
        "expected_head": preconditions["head"].startswith(EXPECTED_HEAD),
        "repo_clean_or_only_this_tool": preconditions["repo_clean_or_only_this_tool"],
        "previous_summary_pass": previous_bundle.get(
            "historical_data_acquisition_okx_single_symbol_3_year_policy_clean_pipeline_summary_status"
        )
        == PREVIOUS_STATUS,
        "current_next_module_matches": previous_bundle.get("next_module") == REQUESTED_MODULE,
        "pilot_symbol_count_10": preview["pilot_symbol_count"] == 10,
        "pilot_symbols_exact": preview["pilot_symbols"] == PILOT_SYMBOLS,
        "includes_existing_validated_symbol": preview["pilot_includes_existing_validated_symbol"] is True,
        "expected_reuse_symbol_count_1": preview["expected_reuse_symbol_count"] == 1,
        "expected_new_symbol_count_9": preview["expected_new_symbol_count"] == 9,
        "date_range_expected": preview["date_range_start"] == DATE_RANGE_START
        and preview["date_range_end"] == DATE_RANGE_END,
        "daily_file_count_expected": preview["expected_daily_file_count_per_symbol"]
        == EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "total_pilot_file_count_expected": preview["expected_total_pilot_file_count"]
        == EXPECTED_TOTAL_PILOT_FILE_COUNT,
        "reused_file_count_expected": preview["expected_reused_file_count"] == EXPECTED_REUSED_FILE_COUNT,
        "new_download_file_count_expected": preview["expected_new_download_file_count"]
        == EXPECTED_NEW_DOWNLOAD_FILE_COUNT,
        "approval_record_created": approval["pilot_download_approval_record_created"] is True,
        "future_download_next_approved": approval["approval_grants_future_10_symbol_pilot_download_next"] is True,
        "download_not_performed_now": approval["approval_grants_download_now"] is False
        and preview["data_download_performed"] is False,
        "full_universe_not_selected": preview["full_universe_acquisition_allowed_now"] is False,
        "strategy_backtest_edge_not_allowed": preview["strategy_backtest_edge_allowed_now"] is False,
        "no_research_backtest_edge_claim": preview["output_valid_for_research_backtest"] is False
        and preview["output_valid_for_edge_claim"] is False,
        "broad_acquisition_not_ready": preview["broad_acquisition_ready"] is False,
        "resource_limits_expected": resource_policy["max_symbols"] == 10
        and resource_policy["max_new_symbols"] == 9
        and resource_policy["max_total_file_set"] == EXPECTED_TOTAL_PILOT_FILE_COUNT
        and resource_policy["max_new_download_files"] == EXPECTED_NEW_DOWNLOAD_FILE_COUNT,
        "no_full_csv_read_future_policy": resource_policy["no_full_csv_read_during_download_execution"] is True,
        "no_build_aggregation_future_policy": resource_policy["no_build_aggregation_during_download_execution"] is True,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        "next_module_expected": approval["next_module"] == NEXT_MODULE_PASS,
    }
    replacement_checks_all_true = all(replacement_checks.values())
    require(replacement_checks_all_true, "replacement checks did not all pass")

    self_validator = {
        "self_validator_created": True,
        "symbol_universe_expansion_preview_created": True,
        "multi_symbol_pilot_preview_created": True,
        "pilot_download_approval_record_created": True,
        "no_download_api_browse_url_fetch": True,
        "no_csv_zip_parquet_read": True,
        "no_data_build": True,
        "no_aggregation": True,
        "no_research_backtest_edge_claim": True,
        "no_full_universe_or_broad_acquisition_ready_claim": True,
        "generic_runner_implementation_remains_blocked": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
    }

    bundle = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "head": preconditions["head"],
        "tracked_python_count_at_preview_run": preconditions["tracked_python_count"],
        "historical_data_acquisition_okx_symbol_universe_and_multi_symbol_expansion_preview_status": PASS_STATUS,
        **preview,
        "pilot_download_approval_record_created": True,
        "approval_grants_download_now": False,
        "approval_grants_future_10_symbol_pilot_download_next": True,
        **DANGEROUS_FLAGS,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": len(P1_ATTENTION_ITEMS),
        "dormant_repo_attention_count": EXPECTED_DORMANT_REPO_ATTENTION_COUNT,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "p1_attention_items": P1_ATTENTION_ITEMS,
        "current_evidence_chain_quality_after_preview": AFTER_QUALITY,
        "next_module": NEXT_MODULE_PASS,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
    }

    return preview, manifest, resource_policy, approval, limitations, self_validator, bundle


def write_outputs(
    preview: dict[str, Any],
    manifest: dict[str, Any],
    resource_policy: dict[str, Any],
    approval: dict[str, Any],
    limitations: dict[str, Any],
    self_validator: dict[str, Any],
    bundle: dict[str, Any],
) -> None:
    write_json(OUTPUT_DIR / "historical_okx_symbol_universe_and_multi_symbol_expansion_preview.json", preview)
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_manifest_preview.json", manifest)
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_resource_limits_policy.json", resource_policy)
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_download_approval_record.json", approval)
    write_json(OUTPUT_DIR / "historical_okx_symbol_universe_expansion_limitations_report.json", limitations)
    write_json(OUTPUT_DIR / "historical_okx_symbol_universe_and_multi_symbol_expansion_preview_self_validator.json", self_validator)
    write_json(OUTPUT_DIR / "historical_okx_symbol_universe_and_multi_symbol_expansion_preview_bundle_summary.json", bundle)


def blocked_payload(message: str) -> dict[str, Any]:
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_symbol_universe_and_multi_symbol_expansion_preview_status": BLOCKED_STATUS,
        "symbol_universe_expansion_preview_created": False,
        "multi_symbol_pilot_preview_created": False,
        "pilot_symbol_count": 0,
        "blocker": message,
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": len(P1_ATTENTION_ITEMS),
        "dormant_repo_attention_count": EXPECTED_DORMANT_REPO_ATTENTION_COUNT,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "current_evidence_chain_quality_after_preview": "HISTORICAL_DATA_ACQUISITION_OKX_SYMBOL_UNIVERSE_AND_MULTI_SYMBOL_EXPANSION_PREVIEW_BLOCKED",
        "next_module": NEXT_MODULE_BLOCKED,
        "replacement_checks_all_true": False,
        **DANGEROUS_FLAGS,
    }


def main() -> None:
    try:
        preconditions = validate_preconditions()
        previous_bundle, _previous_pipeline, _previous_route = validate_previous_summary()
        outputs = build_outputs(preconditions, previous_bundle)
        write_outputs(*outputs)
        print(json.dumps(outputs[-1], indent=2, sort_keys=True))
    except PreviewBlocked as exc:
        blocked = blocked_payload(str(exc))
        write_json(OUTPUT_DIR / "historical_okx_symbol_universe_and_multi_symbol_expansion_preview_bundle_summary.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
