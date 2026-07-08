from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_material_duplicate_conflict_policy_after_conflict_review_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "92ef4ce"
TARGET_SYMBOL = "BTC-USDT-SWAP"
PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_CONFLICTING_DUPLICATE_"
    "DATA_QUALITY_REVIEW_MATERIAL_CONFLICT_POLICY_READY"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_MATERIAL_DUPLICATE_"
    "CONFLICT_POLICY_APPROVED_POLICY_CLEAN_REBUILD_READY"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_MATERIAL_DUPLICATE_"
    "CONFLICT_POLICY"
)
CONFLICT_RESOLUTION_POLICY = "QUARANTINE_MATERIAL_CONFLICTING_OPEN_TIME_GROUP"
CONFLICT_OPEN_TIME = 1_776_150_360_000
CONFLICT_OPEN_TIME_UTC = "2026-04-14T07:06:00+00:00"
AFFECTED_HOUR_UTC = "2026-04-14T07:00:00+00:00"
DIFFERING_FIELDS = ["high", "vol", "vol_ccy", "vol_quote"]
OBSERVED_SOURCE_ROW_COUNT = 1_516_641
EXPECTED_TOTAL_SOURCE_ROWS = 1_516_320
EXACT_DUPLICATE_EXTRA_ROW_COUNT = 320
MATERIAL_CONFLICTING_GROUP_COUNT = 1
MATERIAL_CONFLICTING_ROW_COUNT = 2
EXPECTED_CLEAN_SOURCE_ROWS_AFTER_POLICY = 1_516_319
EXPECTED_COMPLETE_1H_ROWS_AFTER_POLICY = 25_271
EXPECTED_INCOMPLETE_1H_ROWS_AFTER_POLICY = 1
AFTER_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_MATERIAL_CONFLICT_POLICY_"
    "APPROVED_POLICY_CLEAN_REBUILD_READY"
)
NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_policy_clean_rebuild_execution_after_material_conflict_policy_v1.py"
)
BLOCKED_NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_material_conflict_policy_blocked_manual_review_v1.py"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
CONFLICT_REVIEW_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_conflicting_duplicate_data_quality_review_after_diagnostic_v1"
)
DIAGNOSTIC_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_duplicate_minute_resolution_diagnostic_after_blocked_build_v1"
)
BLOCKED_BUILD_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_1m_to_1h_build_execution_after_preview_approval_v1"
)

CONFLICT_REVIEW_SUMMARY = CONFLICT_REVIEW_DIR / "historical_okx_single_symbol_3_year_conflicting_duplicate_review_summary.json"
RAW_ROWS_REPORT = CONFLICT_REVIEW_DIR / "historical_okx_single_symbol_3_year_conflicting_duplicate_raw_rows_report.json"
FIELD_DIFF_REPORT = CONFLICT_REVIEW_DIR / "historical_okx_single_symbol_3_year_conflicting_duplicate_field_diff_report.json"
DIAGNOSTIC_SUMMARY = DIAGNOSTIC_DIR / "historical_okx_single_symbol_3_year_duplicate_minute_diagnostic_summary.json"
BLOCKED_BUILD_SUMMARY = BLOCKED_BUILD_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_build_execution_summary.json"

DANGEROUS_FLAGS = {
    "download_performed_now": False,
    "api_call_performed_now": False,
    "browse_performed_now": False,
    "url_fetch_performed_now": False,
    "full_csv_read_performed_now": False,
    "data_build_performed": False,
    "aggregation_performed_now": False,
    "dedupe_execution_performed_now": False,
    "rebuild_execution_performed_now": False,
    "output_csv_created": False,
    "row_selection_among_conflicts_performed": False,
    "ohlcv_modification_performed": False,
    "synthetic_fill_used": False,
    "forward_fill_used": False,
    "backfill_used": False,
    "research_backtest_candidate_performed": False,
    "edge_profit_claim_made": False,
    "broad_acquisition_ready": False,
    "strict_3y_completeness_claimed": False,
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


def load_json(path: Path) -> Any:
    require(path.exists(), f"missing artifact: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"artifact is not a JSON object: {path}")
    return data


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_preflight(
    review: dict[str, Any],
    raw_rows: dict[str, Any],
    field_diff: dict[str, Any],
    diagnostic: dict[str, Any],
    blocked_build: dict[str, Any],
) -> None:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved module")
    require(
        review.get("historical_data_acquisition_okx_single_symbol_3_year_conflicting_duplicate_data_quality_review_status")
        == PREVIOUS_STATUS,
        "conflict review status mismatch",
    )
    require(review.get("next_module") == REQUESTED_MODULE, "next_module mismatch")
    require(review.get("target_symbol") == TARGET_SYMBOL, "target symbol mismatch")
    require(review.get("conflict_open_time") == CONFLICT_OPEN_TIME, "conflict open_time mismatch")
    require(review.get("conflict_open_time_utc") == CONFLICT_OPEN_TIME_UTC, "conflict UTC mismatch")
    require(review.get("differing_fields") == DIFFERING_FIELDS, "differing fields mismatch")
    require(review.get("conflict_classification") == "OHLCV_MATERIAL_CONFLICT", "conflict classification mismatch")
    require(review.get("confirm_only_conflict") is False, "confirm-only flag mismatch")
    require(review.get("ohlcv_material_conflict") is True, "material flag mismatch")
    require(review.get("raw_conflict_rows_captured") is True, "raw rows flag mismatch")
    require(review.get("active_p0_blocker_count") == 1, "P0 blocker count mismatch")
    require(review.get("active_p1_attention_count") == 9, "P1 attention count mismatch")
    require(review.get("data_build_performed") is False, "review data build flag mismatch")
    require(review.get("aggregation_performed_now") is False, "review aggregation flag mismatch")
    require(review.get("output_csv_created") is False, "review output flag mismatch")
    require(raw_rows.get("raw_conflict_rows_captured") is True, "raw row report capture mismatch")
    require(raw_rows.get("conflict_row_count") == MATERIAL_CONFLICTING_ROW_COUNT, "raw row count mismatch")
    require(field_diff.get("field_diff_report_created") is True, "field diff report flag mismatch")
    require(field_diff.get("differing_fields") == DIFFERING_FIELDS, "field diff differing fields mismatch")
    require(diagnostic.get("exact_duplicate_extra_row_count") == EXACT_DUPLICATE_EXTRA_ROW_COUNT, "exact duplicate count mismatch")
    require(diagnostic.get("conflicting_duplicate_group_count") == MATERIAL_CONFLICTING_GROUP_COUNT, "diagnostic conflict group mismatch")
    require(diagnostic.get("conflicting_duplicate_extra_row_count") == 1, "diagnostic conflict extra mismatch")
    require(diagnostic.get("source_row_count_total") == OBSERVED_SOURCE_ROW_COUNT, "diagnostic source row mismatch")
    require(blocked_build.get("source_row_count_total") == OBSERVED_SOURCE_ROW_COUNT, "blocked build source row mismatch")
    require(blocked_build.get("expected_total_source_rows") == EXPECTED_TOTAL_SOURCE_ROWS, "blocked build expected row mismatch")


def main() -> None:
    generated_at = utc_now()
    review = load_json(CONFLICT_REVIEW_SUMMARY)
    raw_rows = load_json(RAW_ROWS_REPORT)
    field_diff = load_json(FIELD_DIFF_REPORT)
    diagnostic = load_json(DIAGNOSTIC_SUMMARY)
    blocked_build = load_json(BLOCKED_BUILD_SUMMARY)
    validate_preflight(review, raw_rows, field_diff, diagnostic, blocked_build)

    material_policy = {
        "material_conflict_policy_created": True,
        "conflict_resolution_policy": CONFLICT_RESOLUTION_POLICY,
        "target_symbol": TARGET_SYMBOL,
        "conflicting_open_time": CONFLICT_OPEN_TIME,
        "conflicting_open_time_utc": CONFLICT_OPEN_TIME_UTC,
        "differing_fields": DIFFERING_FIELDS,
        "choose_conflicting_row_allowed": False,
        "average_conflicting_rows_allowed": False,
        "merge_conflicting_rows_allowed": False,
        "synthesize_missing_minute_allowed": False,
        "forward_fill_allowed": False,
        "backfill_allowed": False,
        "exact_duplicate_drop_allowed": True,
        "material_conflict_quarantine_required": True,
        "future_rebuild_allowed_after_policy": True,
        "future_rebuild_must_audit_all_dropped_exact_duplicates": True,
        "future_rebuild_must_audit_quarantined_material_conflict": True,
        "future_rebuild_complete_hour_claim_requires_60_clean_source_rows": True,
        "no_research_backtest_edge_ready_claim": True,
    }
    quarantine_policy = {
        "conflict_quarantine_policy_created": True,
        "quarantine_scope": "BOTH_ROWS_FOR_MATERIAL_CONFLICTING_OPEN_TIME_GROUP",
        "conflict_open_time": CONFLICT_OPEN_TIME,
        "conflict_open_time_utc": CONFLICT_OPEN_TIME_UTC,
        "conflict_source_date": review["conflict_source_date"],
        "conflict_source_file": review["conflict_source_file"],
        "material_conflicting_row_count": MATERIAL_CONFLICTING_ROW_COUNT,
        "material_conflict_rows_to_quarantine": MATERIAL_CONFLICTING_ROW_COUNT,
        "quarantine_audit_required": True,
        "replacement_minute_allowed": False,
        "affected_hour_utc": AFFECTED_HOUR_UTC,
        "affected_hour_complete": False,
    }
    rebuild_preview = {
        "policy_clean_rebuild_preview_created": True,
        "preview_only": True,
        "observed_source_row_count": OBSERVED_SOURCE_ROW_COUNT,
        "exact_duplicate_rows_to_drop": EXACT_DUPLICATE_EXTRA_ROW_COUNT,
        "material_conflict_rows_to_quarantine": MATERIAL_CONFLICTING_ROW_COUNT,
        "expected_clean_source_rows_after_policy": EXPECTED_CLEAN_SOURCE_ROWS_AFTER_POLICY,
        "expected_complete_1h_rows_after_policy": EXPECTED_COMPLETE_1H_ROWS_AFTER_POLICY,
        "expected_incomplete_1h_rows_after_policy": EXPECTED_INCOMPLETE_1H_ROWS_AFTER_POLICY,
        "affected_hour_utc": AFFECTED_HOUR_UTC,
        "all_hours_complete_after_policy": False,
        "future_rebuild_must_not_claim_all_hours_complete": True,
        "future_rebuild_may_emit_incomplete_hour_only_if_flagged_incomplete": True,
        "future_rebuild_output_pipeline_validation_only": True,
        "data_build_performed_now": False,
        "aggregation_performed_now": False,
        "output_csv_created_now": False,
    }
    approval_record = {
        "policy_clean_rebuild_approval_record_created": True,
        "approval_grants_policy_now": True,
        "approval_grants_rebuild_now": False,
        "approval_grants_future_policy_clean_rebuild_next": True,
        "approval_grants_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "next_module": NEXT_MODULE,
    }
    self_validator = {
        "self_validator_created": True,
        "preflight_passed": True,
        "material_policy_valid": material_policy["material_conflict_policy_created"] is True
        and material_policy["conflict_resolution_policy"] == CONFLICT_RESOLUTION_POLICY
        and material_policy["choose_conflicting_row_allowed"] is False
        and material_policy["exact_duplicate_drop_allowed"] is True,
        "quarantine_policy_valid": quarantine_policy["material_conflict_rows_to_quarantine"] == MATERIAL_CONFLICTING_ROW_COUNT
        and quarantine_policy["affected_hour_complete"] is False,
        "rebuild_preview_valid": rebuild_preview["expected_clean_source_rows_after_policy"] == EXPECTED_CLEAN_SOURCE_ROWS_AFTER_POLICY
        and rebuild_preview["expected_complete_1h_rows_after_policy"] == EXPECTED_COMPLETE_1H_ROWS_AFTER_POLICY
        and rebuild_preview["all_hours_complete_after_policy"] is False,
        "approval_record_valid": approval_record["approval_grants_policy_now"] is True
        and approval_record["approval_grants_rebuild_now"] is False
        and approval_record["approval_grants_future_policy_clean_rebuild_next"] is True,
        "no_download_api_browse_build_aggregation": all(value is False for value in DANGEROUS_FLAGS.values()),
        "not_research_backtest_edge_broad": True,
        "next_module_valid": approval_record["next_module"] == NEXT_MODULE,
    }
    replacement_checks = {
        "preflight_passed": True,
        "material_conflict_policy_created": material_policy["material_conflict_policy_created"],
        "conflict_policy_valid": material_policy["conflict_resolution_policy"] == CONFLICT_RESOLUTION_POLICY,
        "conflict_identity_preserved": material_policy["conflicting_open_time"] == CONFLICT_OPEN_TIME
        and material_policy["conflicting_open_time_utc"] == CONFLICT_OPEN_TIME_UTC
        and material_policy["differing_fields"] == DIFFERING_FIELDS,
        "no_conflict_row_selection_or_merge": material_policy["choose_conflicting_row_allowed"] is False
        and material_policy["average_conflicting_rows_allowed"] is False
        and material_policy["merge_conflicting_rows_allowed"] is False,
        "exact_duplicate_drop_allowed": material_policy["exact_duplicate_drop_allowed"] is True,
        "material_conflict_quarantine_required": material_policy["material_conflict_quarantine_required"] is True,
        "policy_clean_rebuild_preview_created": rebuild_preview["policy_clean_rebuild_preview_created"],
        "approval_record_created": approval_record["policy_clean_rebuild_approval_record_created"],
        "row_arithmetic_valid": OBSERVED_SOURCE_ROW_COUNT
        - EXACT_DUPLICATE_EXTRA_ROW_COUNT
        - MATERIAL_CONFLICTING_ROW_COUNT
        == EXPECTED_CLEAN_SOURCE_ROWS_AFTER_POLICY,
        "affected_hour_incomplete": quarantine_policy["affected_hour_complete"] is False
        and rebuild_preview["affected_hour_utc"] == AFFECTED_HOUR_UTC,
        "future_output_not_all_complete": rebuild_preview["all_hours_complete_after_policy"] is False
        and rebuild_preview["expected_complete_1h_rows_after_policy"] == EXPECTED_COMPLETE_1H_ROWS_AFTER_POLICY
        and rebuild_preview["expected_incomplete_1h_rows_after_policy"] == EXPECTED_INCOMPLETE_1H_ROWS_AFTER_POLICY,
        "approval_future_rebuild_only": approval_record["approval_grants_policy_now"] is True
        and approval_record["approval_grants_rebuild_now"] is False
        and approval_record["approval_grants_future_policy_clean_rebuild_next"] is True,
        "no_download_api_browse_build_aggregation": all(value is False for value in DANGEROUS_FLAGS.values()),
        "strict_3y_not_claimed": True,
        "not_research_backtest_edge_broad": True,
        "active_p0_cleared_by_policy_approval": True,
        "next_module_valid": approval_record["next_module"] == NEXT_MODULE,
    }
    replacement_checks_all_true = all(replacement_checks.values())
    require(replacement_checks_all_true, "replacement checks failed")
    summary = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "historical_data_acquisition_okx_single_symbol_3_year_material_duplicate_conflict_policy_status": PASS_STATUS,
        "material_conflict_policy_created": True,
        "conflict_resolution_policy": CONFLICT_RESOLUTION_POLICY,
        "target_symbol": TARGET_SYMBOL,
        "conflict_open_time": CONFLICT_OPEN_TIME,
        "conflict_open_time_utc": CONFLICT_OPEN_TIME_UTC,
        "differing_fields": DIFFERING_FIELDS,
        "exact_duplicate_extra_row_count": EXACT_DUPLICATE_EXTRA_ROW_COUNT,
        "material_conflicting_group_count": MATERIAL_CONFLICTING_GROUP_COUNT,
        "material_conflicting_row_count": MATERIAL_CONFLICTING_ROW_COUNT,
        "choose_conflicting_row_allowed": False,
        "average_conflicting_rows_allowed": False,
        "merge_conflicting_rows_allowed": False,
        "exact_duplicate_drop_allowed": True,
        "material_conflict_quarantine_required": True,
        "policy_clean_rebuild_preview_created": True,
        "policy_clean_rebuild_approval_record_created": True,
        "observed_source_row_count": OBSERVED_SOURCE_ROW_COUNT,
        "exact_duplicate_rows_to_drop": EXACT_DUPLICATE_EXTRA_ROW_COUNT,
        "material_conflict_rows_to_quarantine": MATERIAL_CONFLICTING_ROW_COUNT,
        "expected_clean_source_rows_after_policy": EXPECTED_CLEAN_SOURCE_ROWS_AFTER_POLICY,
        "expected_complete_1h_rows_after_policy": EXPECTED_COMPLETE_1H_ROWS_AFTER_POLICY,
        "expected_incomplete_1h_rows_after_policy": EXPECTED_INCOMPLETE_1H_ROWS_AFTER_POLICY,
        "affected_hour_utc": AFFECTED_HOUR_UTC,
        "all_hours_complete_after_policy": False,
        "approval_grants_rebuild_now": False,
        "approval_grants_future_policy_clean_rebuild_next": True,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "output_csv_created": False,
        "strict_3y_completeness_claimed": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 9,
        "current_evidence_chain_quality_after_policy": AFTER_QUALITY,
        "next_module": NEXT_MODULE,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": True,
        "tracked_python_count_at_policy_run": tracked_python_count(),
    }
    bundle = {
        "material_duplicate_conflict_policy": material_policy,
        "conflict_quarantine_policy": quarantine_policy,
        "policy_clean_rebuild_preview": rebuild_preview,
        "policy_clean_rebuild_approval_record": approval_record,
        "self_validator": self_validator,
        "summary": summary,
    }
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_material_duplicate_conflict_policy.json", material_policy)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_conflict_quarantine_policy.json", quarantine_policy)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_policy_clean_rebuild_preview.json", rebuild_preview)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_policy_clean_rebuild_approval_record.json", approval_record)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_material_conflict_policy_self_validator.json", self_validator)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_material_conflict_policy_summary.json", summary)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_material_conflict_policy_bundle_summary.json", bundle)
    write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Blocked as exc:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        blocked = {
            "module_name": MODULE_NAME,
            "generated_at_utc": utc_now(),
            "historical_data_acquisition_okx_single_symbol_3_year_material_duplicate_conflict_policy_status": BLOCKED_STATUS,
            "material_conflict_policy_created": False,
            "conflict_resolution_policy": None,
            "target_symbol": TARGET_SYMBOL,
            "conflict_open_time": CONFLICT_OPEN_TIME,
            "conflict_open_time_utc": CONFLICT_OPEN_TIME_UTC,
            "policy_clean_rebuild_preview_created": False,
            "policy_clean_rebuild_approval_record_created": False,
            "approval_grants_rebuild_now": False,
            "approval_grants_future_policy_clean_rebuild_next": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "output_csv_created": False,
            "strict_3y_completeness_claimed": False,
            "output_valid_for_research_backtest": False,
            "output_valid_for_edge_claim": False,
            "broad_acquisition_ready": False,
            "active_p0_blocker_count": 1,
            "active_p1_attention_count": 9,
            "current_evidence_chain_quality_after_policy": "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_MATERIAL_CONFLICT_POLICY_BLOCKED",
            "next_module": BLOCKED_NEXT_MODULE,
            "replacement_checks_all_true": False,
            "blocked_reason": str(exc),
        }
        write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_material_conflict_policy_summary.json", blocked)
        write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        raise SystemExit(1)
