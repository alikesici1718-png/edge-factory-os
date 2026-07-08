#!/usr/bin/env python3
"""Repo-only review of unresolved OKX 88-symbol 1h extreme returns.

This module inspects only prior diagnostic artifacts and the validated 1h panel
output around the six unresolved extreme rows. It does not read original 1m
ZIP/CSV sources, download, browse, call APIs, build data, aggregate data, run
strategy search, generate candidates, optimize, claim edge, or touch
runtime/live/capital.
"""

from __future__ import annotations

import csv
import json
import math
import subprocess
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path("tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_unresolved_extreme_return_review_after_diagnostic_v1.py")
OUTPUT_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_unresolved_extreme_return_review_after_diagnostic_v1"

EXTREME_REVIEW_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_extreme_return_diagnostic_review_after_baseline_summary_v1"
BASELINE_SUMMARY_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_summary_after_execution_v1"
BASELINE_EXECUTION_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_execution_after_preview_v1"
BUILD_EXECUTION_DIR = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_execution_after_preview_approval_v1"
VALIDATOR_DIR = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_after_execution_v1"

EXTREME_REVIEW = EXTREME_REVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_extreme_return_diagnostic_review.json"
EXTREME_ROWS = EXTREME_REVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_extreme_return_rows.csv"
BASELINE_SUMMARY = BASELINE_SUMMARY_DIR / "repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_summary.json"
OUTPUT_MANIFEST = BUILD_EXECUTION_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_manifest.json"
OUTPUT_SCHEMA = BUILD_EXECUTION_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_output_schema_report.json"
VALIDATOR_SUMMARY = VALIDATOR_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_summary.json"
INCOMPLETE_HOURS = BASELINE_EXECUTION_DIR / "repo_only_okx_88_symbol_1h_panel_incomplete_hour_diagnostics.json"
VOLUME_SANITY = BASELINE_EXECUTION_DIR / "repo_only_okx_88_symbol_1h_panel_volume_liquidity_sanity.json"

EXPECTED_HEAD = "24902b0"
EXPECTED_INPUT_UNRESOLVED_COUNT = 6
EXPECTED_OUTPUT_ROWS = 2223936
PREVIOUS_PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_EXTREME_RETURN_DIAGNOSTIC_REVIEW_READY"
PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_UNRESOLVED_EXTREME_RETURN_REVIEW_READY"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_UNRESOLVED_EXTREME_RETURN_REVIEW_REQUIRED"
NEXT_HOLDOUT_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_registry_builder_before_strategy_search_v1.py"
NEXT_SOURCE_REVIEW_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_unresolved_extreme_return_source_review_preview_v1.py"
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_unresolved_extreme_return_review_blocked_record_v1.py"
QUALITY_RESOLVED = "OKX_88_SYMBOL_1H_PANEL_UNRESOLVED_EXTREME_RETURN_REVIEW_RESOLVED_HOLDOUT_REGISTRY_NEXT"
QUALITY_SOURCE_REVIEW = "OKX_88_SYMBOL_1H_PANEL_UNRESOLVED_EXTREME_RETURN_REVIEW_SOURCE_REVIEW_PREVIEW_NEXT"
QUALITY_BLOCKED = "OKX_88_SYMBOL_1H_PANEL_UNRESOLVED_EXTREME_RETURN_REVIEW_BLOCKED_REVIEW_REQUIRED"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_hour(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def iso_hour(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def safe_float(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def parse_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y"}


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} did not contain a JSON object")
    return payload


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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


def load_inputs() -> tuple[dict[str, Any], dict[str, str]]:
    loaded: dict[str, Any] = {}
    errors: dict[str, str] = {}
    for label, path, loader in [
        ("extreme_review", EXTREME_REVIEW, read_json),
        ("extreme_rows", EXTREME_ROWS, read_csv),
        ("baseline_summary", BASELINE_SUMMARY, read_json),
        ("output_manifest", OUTPUT_MANIFEST, read_json),
        ("output_schema", OUTPUT_SCHEMA, read_json),
        ("validator_summary", VALIDATOR_SUMMARY, read_json),
        ("incomplete_hours", INCOMPLETE_HOURS, read_json),
        ("volume_sanity", VOLUME_SANITY, read_json),
    ]:
        try:
            loaded[label] = loader(path)
        except (OSError, json.JSONDecodeError, RuntimeError) as exc:
            errors[label] = f"{path}: {exc}"
    return loaded, errors


def unresolved_rows(extreme_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in extreme_rows if row.get("classification") == "UNRESOLVED_REQUIRES_REVIEW"]


def row_key(row: dict[str, Any]) -> tuple[str, str]:
    return str(row["symbol"]), str(row["hour_timestamp"])


def ohlc_consistent(row: dict[str, Any]) -> bool:
    open_value = safe_float(row.get("open"))
    high_value = safe_float(row.get("high"))
    low_value = safe_float(row.get("low"))
    close_value = safe_float(row.get("close"))
    if None in {open_value, high_value, low_value, close_value}:
        return False
    return bool(high_value >= low_value and high_value >= max(open_value, close_value) and low_value <= min(open_value, close_value))


def ohlc_supports_close_move(previous_close: float | None, row: dict[str, Any]) -> bool:
    current_close = safe_float(row.get("close"))
    high_value = safe_float(row.get("high"))
    low_value = safe_float(row.get("low"))
    if previous_close is None or current_close is None or high_value is None or low_value is None:
        return False
    return bool(low_value <= previous_close <= high_value and low_value <= current_close <= high_value)


def median(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    midpoint = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[midpoint]
    return (ordered[midpoint - 1] + ordered[midpoint]) / 2.0


def percentile_rank(values: list[float], target: float | None) -> float | None:
    if target is None or not values:
        return None
    less_or_equal = sum(1 for value in values if value <= target)
    return less_or_equal / len(values)


def scan_panel(output_file: Path, targets: list[dict[str, str]]) -> dict[str, Any]:
    target_symbols = {row["symbol"] for row in targets}
    target_hours = {row["hour_timestamp"] for row in targets}
    target_dt_by_symbol: dict[str, list[datetime]] = {}
    for row in targets:
        target_dt_by_symbol.setdefault(row["symbol"], []).append(parse_hour(row["hour_timestamp"]))

    previous_by_symbol: dict[str, dict[str, Any]] = {}
    context_rows: list[dict[str, Any]] = []
    cross_rows: list[dict[str, Any]] = []
    target_panel_rows: dict[tuple[str, str], dict[str, Any]] = {}
    fieldnames: list[str] = []
    row_count = 0

    with output_file.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        required = {"symbol", "hour_open_time_utc", "open", "high", "low", "close", "vol", "source_row_count", "complete_1h"}
        missing = sorted(required - set(fieldnames))
        if missing:
            raise RuntimeError(f"validated panel output missing required fields: {missing}")

        for row in reader:
            row_count += 1
            symbol = row["symbol"]
            hour = row["hour_open_time_utc"]
            hour_dt = parse_hour(hour)
            close_value = safe_float(row.get("close"))
            previous = previous_by_symbol.get(symbol)
            previous_close = safe_float(previous.get("close")) if previous else None
            row_return = None
            if previous_close is not None and close_value is not None and previous_close > 0:
                row_return = close_value / previous_close - 1.0

            enriched = {
                "symbol": symbol,
                "hour_timestamp": hour,
                "open": safe_float(row.get("open")),
                "high": safe_float(row.get("high")),
                "low": safe_float(row.get("low")),
                "close": close_value,
                "previous_close": previous_close,
                "return": row_return,
                "abs_return": abs(row_return) if row_return is not None else None,
                "vol": safe_float(row.get("vol")),
                "vol_ccy": safe_float(row.get("vol_ccy")),
                "vol_quote": safe_float(row.get("vol_quote")),
                "source_row_count": row.get("source_row_count"),
                "complete_1h": parse_bool(row.get("complete_1h")),
                "ohlc_consistent": ohlc_consistent(row),
            }

            if symbol in target_symbols:
                for target_dt in target_dt_by_symbol[symbol]:
                    hour_offset = int((hour_dt - target_dt).total_seconds() // 3600)
                    if -24 <= hour_offset <= 24:
                        context_rows.append({"target_hour_timestamp": iso_hour(target_dt), "hour_offset": hour_offset, **enriched})
                        break
                if hour in target_hours:
                    target_panel_rows[(symbol, hour)] = enriched

            if hour in target_hours:
                cross_rows.append(enriched)

            previous_by_symbol[symbol] = row

    return {
        "context_rows": context_rows,
        "cross_rows": cross_rows,
        "fieldnames": fieldnames,
        "row_count": row_count,
        "target_panel_rows": target_panel_rows,
    }


def classify_row(row: dict[str, Any]) -> str:
    if row["cross_symbol_market_shock_like"]:
        return "CROSS_SYMBOL_MARKET_SHOCK_LIKE"
    if row["bad_tick_like_reversal"]:
        return "BAD_TICK_LIKE_REVERSAL_SUSPECT"
    if row["data_issue_suspect_context"]:
        return "DATA_ISSUE_SUSPECT_CONTEXT"
    if row["ohlc_supports_move"] and row["complete_1h"] and row["previous_complete_1h"] and not row["bad_tick_like_reversal"]:
        return "REAL_MARKET_EVENT_LIKE_CONTEXT_CONFIRMED"
    return "UNRESOLVED_REQUIRES_SOURCE_REVIEW"


def review_unresolved(targets: list[dict[str, str]], panel: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    context_rows = panel["context_rows"]
    cross_rows = panel["cross_rows"]
    context_by_key: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in context_rows:
        context_by_key.setdefault((row["symbol"], row["target_hour_timestamp"]), []).append(row)

    cross_by_hour: dict[str, list[dict[str, Any]]] = {}
    for row in cross_rows:
        cross_by_hour.setdefault(row["hour_timestamp"], []).append(row)

    reviewed_rows: list[dict[str, Any]] = []
    cross_summary_rows: list[dict[str, Any]] = []
    classification_counts: Counter[str] = Counter()

    for target in targets:
        symbol = target["symbol"]
        hour = target["hour_timestamp"]
        current = panel["target_panel_rows"].get((symbol, hour))
        if current is None:
            reviewed_rows.append({"symbol": symbol, "hour_timestamp": hour, "classification": "UNRESOLVED_REQUIRES_SOURCE_REVIEW", "missing_panel_target_row": True})
            classification_counts["UNRESOLVED_REQUIRES_SOURCE_REVIEW"] += 1
            continue

        local_rows = sorted(context_by_key.get((symbol, hour), []), key=lambda item: item["hour_offset"])
        local_abs_returns = [row["abs_return"] for row in local_rows if isinstance(row.get("abs_return"), float)]
        local_volumes = [row["vol"] for row in local_rows if isinstance(row.get("vol"), float)]
        next_rows = [row for row in local_rows if row["hour_offset"] == 1]
        previous_rows = [row for row in local_rows if row["hour_offset"] == -1]
        next_row = next_rows[0] if next_rows else None
        previous_row = previous_rows[0] if previous_rows else None

        current_return = safe_float(target.get("return"))
        current_abs_return = abs(current_return) if current_return is not None else None
        next_return = next_row.get("return") if next_row else None
        next_abs_return = abs(next_return) if isinstance(next_return, float) else None
        reversal = bool(
            isinstance(current_return, float)
            and isinstance(next_return, float)
            and current_return * next_return < 0
            and abs(next_return) >= min(0.15, abs(current_return) * 0.5)
        )
        continuation = bool(isinstance(current_return, float) and isinstance(next_return, float) and current_return * next_return > 0 and abs(next_return) >= 0.05)

        cross_at_hour = cross_by_hour.get(hour, [])
        cross_abs_05 = sum(1 for row in cross_at_hour if isinstance(row.get("abs_return"), float) and row["abs_return"] >= 0.05)
        cross_abs_10 = sum(1 for row in cross_at_hour if isinstance(row.get("abs_return"), float) and row["abs_return"] >= 0.10)
        cross_abs_25 = sum(1 for row in cross_at_hour if isinstance(row.get("abs_return"), float) and row["abs_return"] >= 0.25)
        cross_symbols_abs_10 = sorted(row["symbol"] for row in cross_at_hour if isinstance(row.get("abs_return"), float) and row["abs_return"] >= 0.10)
        cross_symbols_abs_25 = sorted(row["symbol"] for row in cross_at_hour if isinstance(row.get("abs_return"), float) and row["abs_return"] >= 0.25)
        cross_shock = cross_abs_25 >= 3 or cross_abs_10 >= 10
        isolated = cross_abs_10 <= 1

        volume = safe_float(target.get("vol"))
        local_volume_percentile = percentile_rank(local_volumes, volume)
        volume_context_support = bool(local_volume_percentile is not None and local_volume_percentile >= 0.80)
        supports_move = ohlc_supports_close_move(safe_float(target.get("previous_close")), target)
        ohlc_ok = ohlc_consistent(target)
        complete_current = parse_bool(target.get("complete_1h"))
        complete_previous = parse_bool(target.get("previous_complete_1h"))
        high_value = safe_float(target.get("high"))
        low_value = safe_float(target.get("low"))
        close_value = safe_float(target.get("close"))
        high_low_range_ratio = ((high_value - low_value) / close_value) if high_value is not None and low_value is not None and close_value else None

        bad_tick = bool(reversal and (not supports_move or not ohlc_ok) and not volume_context_support)
        data_issue = bool(not ohlc_ok or not supports_move or not complete_current or not complete_previous)

        reviewed = {
            "symbol": symbol,
            "hour_timestamp": hour,
            "previous_close_timestamp": target.get("previous_close_timestamp"),
            "previous_close": safe_float(target.get("previous_close")),
            "current_close": safe_float(target.get("current_close")),
            "next_close": next_row.get("close") if next_row else None,
            "return": current_return,
            "abs_return": current_abs_return,
            "next_hour_return": next_return,
            "next_hour_abs_return": next_abs_return,
            "next_hour_reversal_flag": reversal,
            "jump_continuation_flag": continuation,
            "local_median_absolute_return": median(local_abs_returns),
            "local_context_row_count": len(local_rows),
            "local_volume_percentile": local_volume_percentile,
            "volume_context_support": volume_context_support,
            "source_row_count": target.get("source_row_count"),
            "previous_source_row_count": target.get("previous_source_row_count"),
            "complete_1h": complete_current,
            "previous_complete_1h": complete_previous,
            "next_complete_1h": next_row.get("complete_1h") if next_row else None,
            "ohlc_consistent": ohlc_ok,
            "ohlc_supports_move": supports_move,
            "high_low_range_ratio": high_low_range_ratio,
            "cross_symbol_abs_return_ge_0_05_count": cross_abs_05,
            "cross_symbol_abs_return_ge_0_10_count": cross_abs_10,
            "cross_symbol_abs_return_ge_0_25_count": cross_abs_25,
            "cross_symbol_market_shock_like": cross_shock,
            "cross_symbol_ge_0_10_symbols": ";".join(cross_symbols_abs_10),
            "cross_symbol_ge_0_25_symbols": ";".join(cross_symbols_abs_25),
            "isolated_single_symbol_move": isolated,
            "bad_tick_like_reversal": bad_tick,
            "data_issue_suspect_context": data_issue,
        }
        reviewed["classification"] = classify_row(reviewed)
        reviewed_rows.append(reviewed)
        classification_counts[reviewed["classification"]] += 1

        cross_summary_rows.append(
            {
                "symbol": symbol,
                "hour_timestamp": hour,
                "same_hour_symbol_count": len(cross_at_hour),
                "cross_symbol_abs_return_ge_0_05_count": cross_abs_05,
                "cross_symbol_abs_return_ge_0_10_count": cross_abs_10,
                "cross_symbol_abs_return_ge_0_25_count": cross_abs_25,
                "cross_symbol_market_shock_like": cross_shock,
                "cross_symbol_ge_0_10_symbols": ";".join(cross_symbols_abs_10),
                "cross_symbol_ge_0_25_symbols": ";".join(cross_symbols_abs_25),
            }
        )

    summary = {
        "bad_tick_like_reversal_suspect_count": classification_counts["BAD_TICK_LIKE_REVERSAL_SUSPECT"],
        "cross_symbol_market_shock_like_count": classification_counts["CROSS_SYMBOL_MARKET_SHOCK_LIKE"],
        "data_issue_suspect_context_count": classification_counts["DATA_ISSUE_SUSPECT_CONTEXT"],
        "real_market_event_like_context_confirmed_count": classification_counts["REAL_MARKET_EVENT_LIKE_CONTEXT_CONFIRMED"],
        "unresolved_requires_source_review_count": classification_counts["UNRESOLVED_REQUIRES_SOURCE_REVIEW"],
    }
    return reviewed_rows, context_rows, cross_summary_rows, summary


def build_outputs() -> dict[str, Any]:
    head = git(["rev-parse", "--short", "HEAD"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    loaded, load_errors = load_inputs()
    extreme_review = loaded.get("extreme_review", {})
    extreme_rows = loaded.get("extreme_rows", [])
    manifest = loaded.get("output_manifest", {})
    schema = loaded.get("output_schema", {})
    validator = loaded.get("validator_summary", {})
    targets = unresolved_rows(extreme_rows) if isinstance(extreme_rows, list) else []
    output_file = Path(str(manifest.get("output_file", "")))

    previous_review_confirmed = (
        extreme_review.get("okx_88_symbol_1h_panel_extreme_return_diagnostic_review_status") == PREVIOUS_PASS_STATUS
        and extreme_review.get("replacement_checks_all_true") is True
        and extreme_review.get("unresolved_extreme_return_count") == EXPECTED_INPUT_UNRESOLVED_COUNT
        and extreme_review.get("approval_grants_unresolved_extreme_return_review_next") is True
        and extreme_review.get("strategy_search_allowed_now") is False
        and extreme_review.get("candidate_generation_allowed_now") is False
        and extreme_review.get("edge_claim_allowed_now") is False
    )
    validated_output_confirmed = (
        output_file.exists()
        and manifest.get("output_file_created") is True
        and manifest.get("output_is_pipeline_validation_only") is True
        and manifest.get("output_1h_row_count") == EXPECTED_OUTPUT_ROWS
        and schema.get("pipeline_validation_only") is True
        and validator.get("okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_EXECUTION_VALIDATED"
        and validator.get("original_source_full_csv_read_by_validator") is False
    )
    unresolved_rows_identified = len(targets) == EXPECTED_INPUT_UNRESOLVED_COUNT

    panel: dict[str, Any] = {"context_rows": [], "cross_rows": [], "fieldnames": [], "row_count": 0, "target_panel_rows": {}}
    reviewed_rows: list[dict[str, Any]] = []
    context_rows: list[dict[str, Any]] = []
    cross_rows: list[dict[str, Any]] = []
    classification_summary = {
        "bad_tick_like_reversal_suspect_count": 0,
        "cross_symbol_market_shock_like_count": 0,
        "data_issue_suspect_context_count": 0,
        "real_market_event_like_context_confirmed_count": 0,
        "unresolved_requires_source_review_count": EXPECTED_INPUT_UNRESOLVED_COUNT,
    }
    extraction_error: str | None = None
    if repo_clean and previous_review_confirmed and validated_output_confirmed and unresolved_rows_identified and not load_errors:
        try:
            panel = scan_panel(output_file, targets)
            reviewed_rows, context_rows, cross_rows, classification_summary = review_unresolved(targets, panel)
        except (OSError, RuntimeError, ValueError) as exc:
            extraction_error = str(exc)
    else:
        reasons = []
        if not repo_clean:
            reasons.append("repo dirty")
        if load_errors:
            reasons.append(f"input artifact errors: {load_errors}")
        if not previous_review_confirmed:
            reasons.append("previous extreme-return review missing/invalid")
        if not validated_output_confirmed:
            reasons.append("validated 1h panel output missing/invalid")
        if not unresolved_rows_identified:
            reasons.append(f"unresolved rows not identified: found {len(targets)}")
        extraction_error = "; ".join(reasons) or None

    unresolved_after = classification_summary["unresolved_requires_source_review_count"]
    attention_resolved = unresolved_after == 0 and len(reviewed_rows) == EXPECTED_INPUT_UNRESOLVED_COUNT
    replacement_checks = {
        "context_windows_created": len(context_rows) > 0,
        "cross_symbol_context_created": len(cross_rows) == EXPECTED_INPUT_UNRESOLVED_COUNT,
        "current_head_matches_expected": head == EXPECTED_HEAD,
        "input_unresolved_count_is_6": len(targets) == EXPECTED_INPUT_UNRESOLVED_COUNT,
        "local_context_review_performed": len(reviewed_rows) == EXPECTED_INPUT_UNRESOLVED_COUNT,
        "no_forbidden_strategy_candidate_edge_runtime_actions": True,
        "no_original_1m_source_read": True,
        "previous_extreme_return_review_confirmed": previous_review_confirmed,
        "repo_clean_except_current_tool": repo_clean,
        "strategy_search_remains_blocked": True,
        "unresolved_rows_identified": unresolved_rows_identified,
        "validated_1h_panel_output_confirmed": validated_output_confirmed,
    }
    replacement_checks_all_true = all(replacement_checks.values())

    if not replacement_checks_all_true:
        status = BLOCKED_STATUS
        quality = QUALITY_BLOCKED
        next_module = NEXT_BLOCKED_MODULE
        approval_holdout = False
        approval_source = False
        attention_resolved = False
    elif attention_resolved:
        status = PASS_STATUS
        quality = QUALITY_RESOLVED
        next_module = NEXT_HOLDOUT_MODULE
        approval_holdout = True
        approval_source = False
    else:
        status = PASS_STATUS
        quality = QUALITY_SOURCE_REVIEW
        next_module = NEXT_SOURCE_REVIEW_MODULE
        approval_holdout = False
        approval_source = True

    review = {
        "active_p0_blocker_count": 0 if replacement_checks_all_true else sum(1 for passed in replacement_checks.values() if not passed),
        "active_p1_attention_count": 0 if attention_resolved else unresolved_after,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_holdout_registry_builder_next": approval_holdout,
        "approval_grants_strategy_search_now": False,
        "approval_grants_unresolved_source_review_preview_next": approval_source,
        "bad_tick_like_reversal_suspect_count": classification_summary["bad_tick_like_reversal_suspect_count"],
        "candidate_generation_allowed_now": False,
        "candidate_generation_performed": False,
        "context_windows_created": len(context_rows) > 0 and replacement_checks_all_true,
        "created_at_utc": now_utc(),
        "cross_symbol_context_created": len(cross_rows) == EXPECTED_INPUT_UNRESOLVED_COUNT and replacement_checks_all_true,
        "cross_symbol_context_review_performed": len(cross_rows) == EXPECTED_INPUT_UNRESOLVED_COUNT and replacement_checks_all_true,
        "cross_symbol_market_shock_like_count": classification_summary["cross_symbol_market_shock_like_count"],
        "current_evidence_chain_quality_after_unresolved_review": quality,
        "data_download_performed": False,
        "data_issue_suspect_context_count": classification_summary["data_issue_suspect_context_count"],
        "edge_claim_allowed_now": False,
        "edge_claim_performed": False,
        "extreme_return_attention_resolved": attention_resolved,
        "family_release_allowed_now": False,
        "holdout_registry_creation_required_before_strategy_search": True,
        "holdout_registry_valid_for_this_panel": False,
        "input_artifact_errors": load_errors,
        "input_unresolved_extreme_return_count": len(targets),
        "local_context_review_performed": len(reviewed_rows) == EXPECTED_INPUT_UNRESOLVED_COUNT and replacement_checks_all_true,
        "next_module": next_module,
        "ohlc_sanity_review_performed": len(reviewed_rows) == EXPECTED_INPUT_UNRESOLVED_COUNT and replacement_checks_all_true,
        "okx_88_symbol_1h_panel_unresolved_extreme_return_review_status": status,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "previous_extreme_return_review_confirmed": previous_review_confirmed,
        "real_market_event_like_context_confirmed_count": classification_summary["real_market_event_like_context_confirmed_count"],
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "runtime_live_capital_allowed_now": False,
        "source_1m_read_performed": False,
        "strategy_search_allowed_now": False,
        "strategy_search_executed": False,
        "strategy_search_must_remain_blocked_until_holdout_registry_valid_for_this_panel": True,
        "tracked_python_count_at_review_run": tracked_python_count(),
        "unresolved_extreme_return_count_after_review": unresolved_after,
        "unresolved_extreme_return_review_performed": replacement_checks_all_true,
        "unresolved_requires_source_review_count": unresolved_after,
        "unresolved_rows_artifact_created": len(reviewed_rows) == EXPECTED_INPUT_UNRESOLVED_COUNT and replacement_checks_all_true,
        "unresolved_rows_identified": unresolved_rows_identified,
        "validated_1h_panel_output_confirmed": validated_output_confirmed,
        "volume_context_review_performed": len(reviewed_rows) == EXPECTED_INPUT_UNRESOLVED_COUNT and replacement_checks_all_true,
    }
    if extraction_error:
        review["extraction_error"] = extraction_error

    route = {
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_holdout_registry_builder_next": approval_holdout,
        "approval_grants_strategy_search_now": False,
        "approval_grants_unresolved_source_review_preview_next": approval_source,
        "next_module": next_module,
        "strategy_search_allowed_now": False,
    }
    self_validator = {
        "created_at_utc": review["created_at_utc"],
        "current_head": head,
        "expected_head": EXPECTED_HEAD,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "required_output_artifacts": [],
        "unexpected_git_status_entries": unexpected_status,
    }
    return {
        "classification": classification_summary,
        "context_rows": context_rows,
        "cross_rows": cross_rows,
        "review": review,
        "reviewed_rows": reviewed_rows,
        "route": route,
        "self_validator": self_validator,
    }


def write_outputs(outputs: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    review_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_unresolved_extreme_return_review.json"
    rows_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_unresolved_extreme_return_rows.csv"
    context_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_unresolved_extreme_return_context_windows.csv"
    cross_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_unresolved_extreme_return_cross_symbol_context.csv"
    classification_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_unresolved_extreme_return_classification.json"
    route_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_unresolved_extreme_return_next_route_approval_record.json"
    validator_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_unresolved_extreme_return_review_self_validator.json"

    reviewed_fields = [
        "symbol",
        "hour_timestamp",
        "previous_close_timestamp",
        "previous_close",
        "current_close",
        "next_close",
        "return",
        "abs_return",
        "next_hour_return",
        "next_hour_abs_return",
        "next_hour_reversal_flag",
        "jump_continuation_flag",
        "local_median_absolute_return",
        "local_context_row_count",
        "local_volume_percentile",
        "volume_context_support",
        "source_row_count",
        "previous_source_row_count",
        "complete_1h",
        "previous_complete_1h",
        "next_complete_1h",
        "ohlc_consistent",
        "ohlc_supports_move",
        "high_low_range_ratio",
        "cross_symbol_abs_return_ge_0_05_count",
        "cross_symbol_abs_return_ge_0_10_count",
        "cross_symbol_abs_return_ge_0_25_count",
        "cross_symbol_market_shock_like",
        "cross_symbol_ge_0_10_symbols",
        "cross_symbol_ge_0_25_symbols",
        "isolated_single_symbol_move",
        "bad_tick_like_reversal",
        "data_issue_suspect_context",
        "classification",
    ]
    context_fields = [
        "target_hour_timestamp",
        "hour_offset",
        "symbol",
        "hour_timestamp",
        "open",
        "high",
        "low",
        "close",
        "previous_close",
        "return",
        "abs_return",
        "vol",
        "vol_ccy",
        "vol_quote",
        "source_row_count",
        "complete_1h",
        "ohlc_consistent",
    ]
    cross_fields = [
        "symbol",
        "hour_timestamp",
        "same_hour_symbol_count",
        "cross_symbol_abs_return_ge_0_05_count",
        "cross_symbol_abs_return_ge_0_10_count",
        "cross_symbol_abs_return_ge_0_25_count",
        "cross_symbol_market_shock_like",
        "cross_symbol_ge_0_10_symbols",
        "cross_symbol_ge_0_25_symbols",
    ]

    write_json(review_path, outputs["review"])
    write_csv(rows_path, outputs["reviewed_rows"], reviewed_fields)
    write_csv(context_path, outputs["context_rows"], context_fields)
    write_csv(cross_path, outputs["cross_rows"], cross_fields)
    write_json(classification_path, outputs["classification"])
    write_json(route_path, outputs["route"])
    artifact_paths = [review_path, rows_path, context_path, cross_path, classification_path, route_path, validator_path]
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
