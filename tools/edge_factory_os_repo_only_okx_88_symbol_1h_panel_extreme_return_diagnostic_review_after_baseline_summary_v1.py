#!/usr/bin/env python3
"""Targeted repo-only diagnostic review for OKX 88-symbol 1h extreme returns.

This module reads the validated 1h panel output and existing diagnostic
artifacts only. It does not read original 1m ZIP/CSV sources, build or
aggregate data, execute strategy search, generate candidates, optimize, claim
edge, or touch runtime/live/capital.
"""

from __future__ import annotations

import csv
import json
import math
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path(
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_extreme_return_diagnostic_review_after_baseline_summary_v1.py"
)
OUTPUT_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_extreme_return_diagnostic_review_after_baseline_summary_v1"

SUMMARY_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_summary_after_execution_v1"
BASELINE_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_execution_after_preview_v1"
BUILD_EXECUTION_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_execution_after_preview_approval_v1"
)
VALIDATOR_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_after_execution_v1"
)

BASELINE_SUMMARY = SUMMARY_DIR / "repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_summary.json"
RETURN_SANITY = BASELINE_DIR / "repo_only_okx_88_symbol_1h_panel_return_distribution_sanity.json"
INCOMPLETE_HOURS = BASELINE_DIR / "repo_only_okx_88_symbol_1h_panel_incomplete_hour_diagnostics.json"
VOLUME_SANITY = BASELINE_DIR / "repo_only_okx_88_symbol_1h_panel_volume_liquidity_sanity.json"
OUTPUT_MANIFEST = BUILD_EXECUTION_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_manifest.json"
OUTPUT_SCHEMA = BUILD_EXECUTION_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_output_schema_report.json"
PROVENANCE = BUILD_EXECUTION_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_provenance_manifest.json"
VALIDATOR_SUMMARY = VALIDATOR_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_summary.json"

EXPECTED_HEADS = {"53d107b", "9181332"}
EXPECTED_EXTREME_RETURN_COUNT = 80
EXPECTED_OUTPUT_ROWS = 2223936
EXPECTED_SYMBOL_COUNT = 88
SUMMARY_PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_BASELINE_RESEARCH_SANITY_SUMMARY_READY"
PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_EXTREME_RETURN_DIAGNOSTIC_REVIEW_READY"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_EXTREME_RETURN_DIAGNOSTIC_REVIEW_REQUIRED"
NEXT_HOLDOUT_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_registry_builder_before_strategy_search_v1.py"
NEXT_UNRESOLVED_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_unresolved_extreme_return_review_after_diagnostic_v1.py"
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_extreme_return_diagnostic_review_blocked_record_v1.py"
QUALITY_PASS = "OKX_88_SYMBOL_1H_PANEL_EXTREME_RETURN_REVIEW_PASS_HOLDOUT_REGISTRY_BUILDER_NEXT"
QUALITY_UNRESOLVED = "OKX_88_SYMBOL_1H_PANEL_EXTREME_RETURN_REVIEW_UNRESOLVED_ATTENTION_REVIEW_NEXT"
QUALITY_BLOCKED = "OKX_88_SYMBOL_1H_PANEL_EXTREME_RETURN_REVIEW_BLOCKED_REVIEW_REQUIRED"


class RunningStats:
    def __init__(self) -> None:
        self.count = 0
        self.mean = 0.0
        self.m2 = 0.0

    def add(self, value: float) -> None:
        self.count += 1
        delta = value - self.mean
        self.mean += delta / self.count
        self.m2 += delta * (value - self.mean)

    def std(self) -> float:
        if self.count <= 1:
            return 0.0
        return math.sqrt(self.m2 / (self.count - 1))


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} did not contain a JSON object")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fieldnames})


def git(args: list[str]) -> str:
    proc = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={REPO.as_posix()}", "-C", str(REPO), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def tracked_python_count() -> int:
    output = git(["ls-files", "*.py"])
    return len([line for line in output.splitlines() if line.strip()])


def clean_status_allowing_tool() -> tuple[bool, list[str]]:
    lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    unexpected = [line for line in lines if not line.replace("\\", "/").endswith(TOOL_REL.as_posix())]
    return not unexpected, unexpected


def parse_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y"}


def safe_float(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def parse_hour(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def hour_delta(current: str, first: str) -> float:
    return (parse_hour(current) - parse_hour(first)).total_seconds() / 3600.0


def load_inputs() -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    loaded: dict[str, dict[str, Any]] = {}
    errors: dict[str, str] = {}
    for label, path in {
        "baseline_summary": BASELINE_SUMMARY,
        "return_sanity": RETURN_SANITY,
        "incomplete_hours": INCOMPLETE_HOURS,
        "volume_sanity": VOLUME_SANITY,
        "output_manifest": OUTPUT_MANIFEST,
        "output_schema": OUTPUT_SCHEMA,
        "provenance": PROVENANCE,
        "validator_summary": VALIDATOR_SUMMARY,
    }.items():
        try:
            loaded[label] = read_json(path)
        except (OSError, json.JSONDecodeError, RuntimeError) as exc:
            errors[label] = f"{path}: {exc}"
    return loaded, errors


def discover_extreme_rule(return_sanity: dict[str, Any]) -> tuple[bool, str | None, float | None, str]:
    threshold = return_sanity.get("extreme_return_abs_threshold")
    if isinstance(threshold, (int, float)) and math.isfinite(float(threshold)):
        return True, str(RETURN_SANITY), float(threshold), f"abs(close_to_close_return) >= {float(threshold)}"
    return False, None, None, "EXTREME_RETURN_RULE_NOT_DISCOVERABLE"


def first_pass_panel(output_file: Path, volume_field: str | None) -> dict[str, Any]:
    first_hour_by_symbol: dict[str, str] = {}
    volume_stats_by_symbol: dict[str, RunningStats] = {}
    row_count = 0
    fieldnames: list[str] = []
    with output_file.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        required = {"symbol", "hour_open_time_utc", "open", "high", "low", "close", "source_row_count", "complete_1h"}
        missing = sorted(required - set(fieldnames))
        if missing:
            raise RuntimeError(f"validated panel output missing required fields: {missing}")
        for row in reader:
            row_count += 1
            symbol = row["symbol"]
            hour = row["hour_open_time_utc"]
            if symbol not in first_hour_by_symbol or hour < first_hour_by_symbol[symbol]:
                first_hour_by_symbol[symbol] = hour
            if volume_field:
                volume = safe_float(row.get(volume_field))
                if volume is not None:
                    volume_stats_by_symbol.setdefault(symbol, RunningStats()).add(volume)
    return {
        "fieldnames": fieldnames,
        "first_hour_by_symbol": first_hour_by_symbol,
        "row_count": row_count,
        "volume_stats_by_symbol": volume_stats_by_symbol,
    }


def classify_extreme(row: dict[str, Any]) -> str:
    if row["ohlc_data_issue_flag"]:
        return "DATA_ISSUE_SUSPECT"
    if row["current_incomplete_hour_overlap"] or row["previous_incomplete_hour_overlap"]:
        return "INCOMPLETE_OR_QUARANTINE_RELATED"
    if row["is_first_available_7d_window"]:
        return "LISTING_OR_START_WINDOW_EVENT"
    if row["volume_spike_flag"]:
        return "REAL_MARKET_EVENT_LIKE"
    return "UNRESOLVED_REQUIRES_REVIEW"


def extract_extremes(
    output_file: Path,
    threshold: float,
    first_hour_by_symbol: dict[str, str],
    volume_stats_by_symbol: dict[str, RunningStats],
    volume_fields: list[str],
) -> list[dict[str, Any]]:
    previous_by_symbol: dict[str, dict[str, Any]] = {}
    extremes: list[dict[str, Any]] = []
    primary_volume_field = volume_fields[0] if volume_fields else None

    with output_file.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            symbol = row["symbol"]
            hour = row["hour_open_time_utc"]
            close = safe_float(row.get("close"))
            previous = previous_by_symbol.get(symbol)
            if previous is not None:
                previous_close = safe_float(previous.get("close"))
                if close is not None and previous_close is not None and previous_close > 0:
                    close_to_close_return = close / previous_close - 1.0
                    if math.isfinite(close_to_close_return) and abs(close_to_close_return) >= threshold:
                        open_value = safe_float(row.get("open"))
                        high_value = safe_float(row.get("high"))
                        low_value = safe_float(row.get("low"))
                        source_row_count = safe_float(row.get("source_row_count"))
                        previous_source_row_count = safe_float(previous.get("source_row_count"))
                        current_complete = parse_bool(row.get("complete_1h"))
                        previous_complete = parse_bool(previous.get("complete_1h"))
                        first_hour = first_hour_by_symbol[symbol]
                        first_delta_hours = hour_delta(hour, first_hour)
                        current_incomplete = not current_complete
                        previous_incomplete = not previous_complete

                        volume_spike_flag = False
                        volume_z_score: float | None = None
                        if primary_volume_field:
                            volume_value = safe_float(row.get(primary_volume_field))
                            stats = volume_stats_by_symbol.get(symbol)
                            std = stats.std() if stats else 0.0
                            if volume_value is not None and stats and std > 0:
                                volume_z_score = (volume_value - stats.mean) / std
                                volume_spike_flag = volume_z_score >= 5.0 and volume_value > stats.mean

                        ohlc_issue = False
                        if None in {open_value, high_value, low_value, close}:
                            ohlc_issue = True
                        elif high_value < low_value or high_value < max(open_value, close) or low_value > min(open_value, close):
                            ohlc_issue = True
                        elif source_row_count is not None and source_row_count <= 0:
                            ohlc_issue = True

                        extreme = {
                            "symbol": symbol,
                            "hour_timestamp": hour,
                            "previous_close_timestamp": previous.get("hour_open_time_utc"),
                            "previous_close": previous_close,
                            "current_close": close,
                            "return": close_to_close_return,
                            "abs_return": abs(close_to_close_return),
                            "open": open_value,
                            "high": high_value,
                            "low": low_value,
                            "close": close,
                            "source_row_count": row.get("source_row_count"),
                            "previous_source_row_count": previous.get("source_row_count"),
                            "complete_1h": current_complete,
                            "previous_complete_1h": previous_complete,
                            "month": hour[:7],
                            "date": hour[:10],
                            "first_available_hour": first_hour,
                            "hours_since_first_available": first_delta_hours,
                            "is_first_available_day_or_window": first_delta_hours <= 168,
                            "is_first_available_24h_window": first_delta_hours <= 24,
                            "is_first_available_72h_window": first_delta_hours <= 72,
                            "is_first_available_7d_window": first_delta_hours <= 168,
                            "current_incomplete_hour_overlap": current_incomplete,
                            "previous_incomplete_hour_overlap": previous_incomplete,
                            "incomplete_hour_overlap": current_incomplete or previous_incomplete,
                            "conflict_or_quarantine_overlap_available": False,
                            "conflict_or_quarantine_overlap": False,
                            "volume_spike_flag": volume_spike_flag,
                            "volume_z_score": volume_z_score,
                            "ohlc_data_issue_flag": ohlc_issue,
                        }
                        for field in volume_fields:
                            extreme[field] = row.get(field)
                        extreme["classification"] = classify_extreme(extreme)
                        extremes.append(extreme)
            previous_by_symbol[symbol] = row
    return extremes


def distribution_rows(counter: Counter[str], key_name: str) -> list[dict[str, Any]]:
    return [{key_name: key, "count": count} for key, count in counter.most_common()]


def build_outputs() -> dict[str, Any]:
    head = git(["rev-parse", "--short", "HEAD"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    loaded, load_errors = load_inputs()
    baseline_summary = loaded.get("baseline_summary", {})
    return_sanity = loaded.get("return_sanity", {})
    volume_sanity = loaded.get("volume_sanity", {})
    output_manifest = loaded.get("output_manifest", {})
    output_schema = loaded.get("output_schema", {})
    validator = loaded.get("validator_summary", {})

    rule_discovered, rule_source, threshold, rule_text = discover_extreme_rule(return_sanity)
    output_file = Path(str(output_manifest.get("output_file", "")))
    volume_fields = [field for field in volume_sanity.get("volume_fields", []) if isinstance(field, str)]
    expected_count = int(baseline_summary.get("extreme_return_diagnostic_count", EXPECTED_EXTREME_RETURN_COUNT) or 0)

    baseline_summary_confirmed = (
        baseline_summary.get("okx_88_symbol_1h_panel_baseline_research_sanity_summary_status") == SUMMARY_PASS_STATUS
        and baseline_summary.get("baseline_summary_created") is True
        and baseline_summary.get("replacement_checks_all_true") is True
        and baseline_summary.get("next_review_must_extract_full_row_level_extremes") is True
        and baseline_summary.get("strategy_search_allowed_now") is False
        and baseline_summary.get("candidate_generation_allowed_now") is False
        and baseline_summary.get("edge_claim_allowed_now") is False
    )
    validated_panel_confirmed = (
        output_file.exists()
        and output_manifest.get("output_file_created") is True
        and output_manifest.get("output_is_pipeline_validation_only") is True
        and output_manifest.get("output_1h_row_count") == EXPECTED_OUTPUT_ROWS
        and output_manifest.get("selected_symbol_count") == EXPECTED_SYMBOL_COUNT
        and validator.get("okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_EXECUTION_VALIDATED"
        and validator.get("original_source_full_csv_read_by_validator") is False
        and output_schema.get("pipeline_validation_only") is True
    )

    extraction_error: str | None = None
    extremes: list[dict[str, Any]] = []
    first_pass: dict[str, Any] = {}
    if repo_clean and baseline_summary_confirmed and validated_panel_confirmed and rule_discovered and threshold is not None:
        try:
            first_pass = first_pass_panel(output_file, volume_fields[0] if volume_fields else None)
            extremes = extract_extremes(
                output_file=output_file,
                threshold=threshold,
                first_hour_by_symbol=first_pass["first_hour_by_symbol"],
                volume_stats_by_symbol=first_pass["volume_stats_by_symbol"],
                volume_fields=volume_fields,
            )
        except (OSError, RuntimeError, ValueError) as exc:
            extraction_error = str(exc)
    else:
        missing_reasons = []
        if not repo_clean:
            missing_reasons.append("repo dirty")
        if not baseline_summary_confirmed:
            missing_reasons.append("baseline summary missing/invalid")
        if not validated_panel_confirmed:
            missing_reasons.append("validated 1h panel output or manifest missing/invalid")
        if not rule_discovered:
            missing_reasons.append("EXTREME_RETURN_RULE_NOT_DISCOVERABLE")
        extraction_error = "; ".join(missing_reasons) or None

    extracted_count = len(extremes)
    extracted_count_matches = extracted_count == expected_count == EXPECTED_EXTREME_RETURN_COUNT
    row_level_extracted = extracted_count_matches

    by_symbol = Counter(row["symbol"] for row in extremes)
    by_month = Counter(row["month"] for row in extremes)
    by_date = Counter(row["date"] for row in extremes)
    by_timestamp = Counter(row["hour_timestamp"] for row in extremes)
    top_3 = by_symbol.most_common(3)
    top_3_symbols = [symbol for symbol, _count in top_3]
    top_3_count = sum(count for _symbol, count in top_3)
    top_3_ratio = top_3_count / extracted_count if extracted_count else None
    top_months = by_month.most_common(3)
    top_month_count = top_months[0][1] if top_months else None
    top_3_month_count = sum(count for _month, count in top_months)

    current_incomplete_count = sum(1 for row in extremes if row["current_incomplete_hour_overlap"])
    previous_incomplete_count = sum(1 for row in extremes if row["previous_incomplete_hour_overlap"])
    incomplete_union_count = sum(1 for row in extremes if row["incomplete_hour_overlap"])
    incomplete_ratio = incomplete_union_count / extracted_count if extracted_count else None
    first_24h_count = sum(1 for row in extremes if row["is_first_available_24h_window"])
    first_72h_count = sum(1 for row in extremes if row["is_first_available_72h_window"])
    first_7d_count = sum(1 for row in extremes if row["is_first_available_7d_window"])
    volume_spike_count = sum(1 for row in extremes if row["volume_spike_flag"])

    classification_counts = Counter(row["classification"] for row in extremes)
    data_issue_count = classification_counts.get("DATA_ISSUE_SUSPECT", 0)
    listing_count = classification_counts.get("LISTING_OR_START_WINDOW_EVENT", 0)
    incomplete_class_count = classification_counts.get("INCOMPLETE_OR_QUARANTINE_RELATED", 0)
    real_market_count = classification_counts.get("REAL_MARKET_EVENT_LIKE", 0)
    unresolved_count = classification_counts.get("UNRESOLVED_REQUIRES_REVIEW", 0)

    review_passed = extracted_count_matches and unresolved_count == 0
    passed_with_attention = extracted_count_matches and unresolved_count > 0
    blocked = not extracted_count_matches or extraction_error is not None
    if blocked:
        status = BLOCKED_STATUS
        quality = QUALITY_BLOCKED
        next_module = NEXT_BLOCKED_MODULE
    elif review_passed:
        status = PASS_STATUS
        quality = QUALITY_PASS
        next_module = NEXT_HOLDOUT_MODULE
    else:
        status = PASS_STATUS
        quality = QUALITY_UNRESOLVED
        next_module = NEXT_UNRESOLVED_MODULE

    replacement_checks = {
        "baseline_summary_confirmed": baseline_summary_confirmed,
        "current_head_matches_expected": head in EXPECTED_HEADS,
        "extracted_count_matches_baseline": extracted_count_matches,
        "extreme_return_rule_discovered": rule_discovered,
        "no_forbidden_strategy_candidate_edge_runtime_actions": True,
        "no_original_1m_source_read": True,
        "repo_clean_except_current_tool": repo_clean,
        "row_level_extremes_extracted": row_level_extracted,
        "strategy_search_remains_blocked": True,
        "validated_1h_panel_output_confirmed": validated_panel_confirmed,
    }
    replacement_checks_all_true = all(replacement_checks.values())
    if not replacement_checks_all_true:
        status = BLOCKED_STATUS
        quality = QUALITY_BLOCKED
        next_module = NEXT_BLOCKED_MODULE
        review_passed = False
        passed_with_attention = False

    top_rows = sorted(extremes, key=lambda item: item["abs_return"], reverse=True)[:10]
    concentrated_top3 = bool(extracted_count and (top_3_count >= 70 or (top_3_ratio is not None and top_3_ratio >= 0.75)))
    clustered_month = bool(extracted_count and (top_month_count is not None and (top_month_count >= 40 or top_3_month_count >= 60)))
    listing_suspected = bool(extracted_count and first_7d_count > extracted_count / 2)

    review = {
        "active_p0_blocker_count": 0 if replacement_checks_all_true else sum(1 for value in replacement_checks.values() if not value),
        "active_p1_attention_count": unresolved_count if replacement_checks_all_true else expected_count,
        "aggregation_performed_now": False,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_holdout_registry_builder_next": bool(review_passed),
        "approval_grants_strategy_search_now": False,
        "approval_grants_unresolved_extreme_return_review_next": bool(passed_with_attention),
        "baseline_summary_confirmed": baseline_summary_confirmed,
        "candidate_generation_allowed_now": False,
        "candidate_generation_performed": False,
        "conflict_or_quarantine_overlap_available": False,
        "conflict_or_quarantine_overlap_count": 0,
        "created_at_utc": now_utc(),
        "current_evidence_chain_quality_after_review": quality,
        "data_build_performed": False,
        "data_download_performed": False,
        "data_issue_suspect_count": data_issue_count,
        "edge_claim_allowed_now": False,
        "edge_claim_performed": False,
        "expected_extreme_return_count": expected_count,
        "extracted_count_matches_baseline": extracted_count_matches,
        "extracted_extreme_return_count": extracted_count,
        "extreme_return_clustered_by_month": clustered_month,
        "extreme_return_concentrated_in_top_3_symbols": concentrated_top3,
        "extreme_return_current_incomplete_hour_overlap_count": current_incomplete_count,
        "extreme_return_previous_incomplete_hour_overlap_count": previous_incomplete_count,
        "extreme_return_first_24h_overlap_count": first_24h_count,
        "extreme_return_first_72h_overlap_count": first_72h_count,
        "extreme_return_first_7d_overlap_count": first_7d_count,
        "extreme_return_review_blocks_strategy_search": True,
        "extreme_return_review_passed": bool(review_passed),
        "extreme_return_review_passed_with_attention": bool(passed_with_attention),
        "extreme_return_review_performed": replacement_checks_all_true,
        "extreme_return_rows_artifact_created": replacement_checks_all_true,
        "extreme_return_rule_discovered": rule_discovered,
        "extreme_return_rule_source_artifact": rule_source,
        "extreme_return_threshold_or_rule": rule_text,
        "extreme_return_top_3_concentration_ratio": top_3_ratio,
        "extreme_return_top_3_symbol_count": top_3_count,
        "extreme_return_top_3_symbols": top_3_symbols,
        "extreme_return_top_month": top_months[0][0] if top_months else None,
        "extreme_return_top_month_count": top_month_count,
        "extreme_return_top_symbol": by_symbol.most_common(1)[0][0] if by_symbol else None,
        "extreme_return_top_symbol_count": by_symbol.most_common(1)[0][1] if by_symbol else None,
        "extreme_return_unique_month_count": len(by_month),
        "extreme_return_unique_symbol_count": len(by_symbol),
        "family_release_allowed_now": False,
        "first_available_window_overlap_available": bool(first_pass.get("first_hour_by_symbol")),
        "holdout_registry_creation_required_before_strategy_search": True,
        "holdout_registry_valid_for_this_panel": False,
        "incomplete_hour_overlap_available": bool("complete_1h" in first_pass.get("fieldnames", [])),
        "incomplete_hour_overlap_ratio": incomplete_ratio,
        "incomplete_or_quarantine_related_count": incomplete_class_count,
        "listing_or_start_window_event_count": listing_count,
        "listing_or_start_window_event_suspected": listing_suspected,
        "next_module": next_module,
        "next_route_approval_record_created": replacement_checks_all_true,
        "okx_88_symbol_1h_panel_extreme_return_diagnostic_review_status": status,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "original_source_full_csv_read_performed": False,
        "output_valid_for_edge_claim": False,
        "output_valid_for_research_backtest": True,
        "real_market_event_like_count": real_market_count,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "row_level_extremes_extracted": row_level_extracted,
        "runtime_live_capital_allowed_now": False,
        "strategy_search_allowed_now": False,
        "strategy_search_executed": False,
        "symbol_distribution_created": replacement_checks_all_true,
        "timestamp_distribution_created": replacement_checks_all_true,
        "top_rows_created": replacement_checks_all_true,
        "tracked_python_count_at_review_run": tracked_python_count(),
        "unresolved_extreme_return_count": unresolved_count,
        "validated_1h_panel_output_confirmed": validated_panel_confirmed,
        "volume_spike_overlap_available": bool(volume_fields),
        "volume_spike_overlap_count": volume_spike_count,
    }
    if extraction_error:
        review["extraction_error"] = extraction_error

    symbol_rows = distribution_rows(by_symbol, "symbol")
    time_rows: list[dict[str, Any]] = []
    for row in distribution_rows(by_month, "value"):
        time_rows.append({"distribution": "month", **row})
    for row in distribution_rows(by_date, "value"):
        time_rows.append({"distribution": "date", **row})
    for row in distribution_rows(by_timestamp, "value"):
        time_rows.append({"distribution": "hour_timestamp", **row})

    incomplete_overlap = {
        "extreme_return_current_incomplete_hour_overlap_count": current_incomplete_count,
        "extreme_return_previous_incomplete_hour_overlap_count": previous_incomplete_count,
        "incomplete_hour_overlap_available": review["incomplete_hour_overlap_available"],
        "incomplete_hour_overlap_count": incomplete_union_count,
        "incomplete_hour_overlap_ratio": incomplete_ratio,
    }
    listing_overlap = {
        "extreme_return_first_24h_overlap_count": first_24h_count,
        "extreme_return_first_72h_overlap_count": first_72h_count,
        "extreme_return_first_7d_overlap_count": first_7d_count,
        "first_available_window_overlap_available": review["first_available_window_overlap_available"],
        "listing_or_start_window_event_suspected": listing_suspected,
    }
    volume_overlap = {
        "volume_fields": volume_fields,
        "volume_spike_definition": "per-symbol primary volume z-score >= 5.0 using validated 1h panel rows",
        "volume_spike_overlap_available": bool(volume_fields),
        "volume_spike_overlap_count": volume_spike_count,
    }
    classification_summary = {
        "classification_is_not_edge_or_candidate_ranking": True,
        "data_issue_suspect_count": data_issue_count,
        "incomplete_or_quarantine_related_count": incomplete_class_count,
        "listing_or_start_window_event_count": listing_count,
        "real_market_event_like_count": real_market_count,
        "unresolved_extreme_return_count": unresolved_count,
    }
    route_approval = {
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_holdout_registry_builder_next": bool(review_passed),
        "approval_grants_strategy_search_now": False,
        "approval_grants_unresolved_extreme_return_review_next": bool(passed_with_attention),
        "next_module": next_module,
        "strategy_search_allowed_now": False,
    }
    self_validator = {
        "created_at_utc": review["created_at_utc"],
        "current_head": head,
        "expected_heads": sorted(EXPECTED_HEADS),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "required_output_artifacts": [],
        "unexpected_git_status_entries": unexpected_status,
    }

    return {
        "classification_summary": classification_summary,
        "extreme_rows": extremes,
        "incomplete_overlap": incomplete_overlap,
        "listing_overlap": listing_overlap,
        "review": review,
        "route_approval": route_approval,
        "self_validator": self_validator,
        "symbol_rows": symbol_rows,
        "time_rows": time_rows,
        "top_rows": top_rows,
        "volume_overlap": volume_overlap,
    }


def write_outputs(outputs: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    review_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_extreme_return_diagnostic_review.json"
    rows_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_extreme_return_rows.csv"
    symbol_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_extreme_return_symbol_distribution.csv"
    time_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_extreme_return_time_distribution.csv"
    top_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_extreme_return_top_rows.csv"
    incomplete_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_extreme_return_incomplete_overlap.json"
    listing_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_extreme_return_listing_window_overlap.json"
    volume_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_extreme_return_volume_overlap.json"
    classification_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_extreme_return_classification_summary.json"
    route_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_extreme_return_next_route_approval_record.json"
    validator_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_extreme_return_diagnostic_review_self_validator.json"

    row_fields = [
        "symbol",
        "hour_timestamp",
        "previous_close_timestamp",
        "previous_close",
        "current_close",
        "return",
        "abs_return",
        "open",
        "high",
        "low",
        "close",
        "source_row_count",
        "previous_source_row_count",
        "complete_1h",
        "previous_complete_1h",
        "vol",
        "vol_ccy",
        "vol_quote",
        "month",
        "date",
        "first_available_hour",
        "hours_since_first_available",
        "is_first_available_day_or_window",
        "is_first_available_24h_window",
        "is_first_available_72h_window",
        "is_first_available_7d_window",
        "current_incomplete_hour_overlap",
        "previous_incomplete_hour_overlap",
        "incomplete_hour_overlap",
        "conflict_or_quarantine_overlap_available",
        "conflict_or_quarantine_overlap",
        "volume_spike_flag",
        "volume_z_score",
        "ohlc_data_issue_flag",
        "classification",
    ]

    write_json(review_path, outputs["review"])
    write_csv(rows_path, outputs["extreme_rows"], row_fields)
    write_csv(symbol_path, outputs["symbol_rows"], ["symbol", "count"])
    write_csv(time_path, outputs["time_rows"], ["distribution", "value", "count"])
    write_csv(top_path, outputs["top_rows"], row_fields)
    write_json(incomplete_path, outputs["incomplete_overlap"])
    write_json(listing_path, outputs["listing_overlap"])
    write_json(volume_path, outputs["volume_overlap"])
    write_json(classification_path, outputs["classification_summary"])
    write_json(route_path, outputs["route_approval"])
    artifact_paths = [
        review_path,
        rows_path,
        symbol_path,
        time_path,
        top_path,
        incomplete_path,
        listing_path,
        volume_path,
        classification_path,
        route_path,
        validator_path,
    ]
    outputs["self_validator"]["required_output_artifacts"] = [str(path) for path in artifact_paths]
    outputs["self_validator"]["required_output_artifacts_exist"] = {str(path): path.exists() for path in artifact_paths[:-1]}
    write_json(validator_path, outputs["self_validator"])


def main() -> int:
    outputs = build_outputs()
    write_outputs(outputs)
    print(json.dumps(outputs["review"], indent=2, sort_keys=True))
    return 0 if outputs["review"]["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
