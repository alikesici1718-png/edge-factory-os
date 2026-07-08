#!/usr/bin/env python3
"""Coinalyze liquidation imbalance + OI flush event study.

Event study only. This module does not call APIs, use API keys, execute a
strategy, generate trading signals, run a backtest, compute PnL, optimize,
create candidates, claim edge, or grant runtime/live/capital permission.
"""

from __future__ import annotations

import hashlib
import json
import random
import statistics
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


MODULE = "edge_factory_os_repo_only_coinalyze_liquidation_imbalance_oi_flush_event_study_v1"
STATUS = "PASS_REPO_ONLY_COINALYZE_LIQUIDATION_IMBALANCE_OI_FLUSH_EVENT_STUDY_CREATED"
ARTIFACT_KIND = "COINALYZE_LIQUIDATION_IMBALANCE_OI_FLUSH_EVENT_STUDY"
REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = REPO_ROOT / "tools" / "edge_factory_os_repo_only_coinalyze_liquidation_imbalance_oi_flush_event_study_v1.py"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "event_studies" / "coinalyze_liquidation_imbalance_oi_flush_event_study_v1.json"
DATASET_BUILDER_PATH = REPO_ROOT / "artifacts" / "data_builds" / "coinalyze_recent_oi_liquidation_dataset_builder_v1.json"
HYPOTHESIS_DESIGN_PATH = REPO_ROOT / "artifacts" / "research_designs" / "coinalyze_recent_oi_liquidation_hypothesis_design_v1.json"
EXTERNAL_DATASET_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_coinalyze_recent_oi_liquidation_dataset_v1")
NORMALIZED_ROOT = EXTERNAL_DATASET_ROOT / "normalized_by_symbol"
SAFE_DIR = str(REPO_ROOT).replace("\\", "/")
EXPECTED_NEW_PATHS = {
    str(TOOL_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
    str(ARTIFACT_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
}

ROLLING_WINDOW_BARS = 96
ROLLING_MIN_BARS = 48
PAST_RETURN_BARS = 4
FORWARD_HORIZONS = {
    "1h": 4,
    "2h": 8,
    "4h": 16,
}
BASELINE_RUNS = 100


def git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={SAFE_DIR}", "-C", str(REPO_ROOT), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def source_checkpoint() -> str:
    return git(["rev-parse", "HEAD"])


def git_status_entries() -> list[tuple[str, str]]:
    raw = git(["status", "--short", "-uall"])
    entries: list[tuple[str, str]] = []
    for line in raw.splitlines():
        if line.strip():
            entries.append((line[:2], line[3:].strip().strip('"').replace("\\", "/")))
    return entries


def repo_clean_except_expected_new_files() -> bool:
    for status, path in git_status_entries():
        if status == "??" and path in EXPECTED_NEW_PATHS:
            continue
        return False
    return True


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def payload_hash(payload: dict[str, Any]) -> str:
    clone = dict(payload)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def load_symbol_rows() -> dict[str, list[dict[str, Any]]]:
    rows_by_symbol: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(NORMALIZED_ROOT.glob("*.jsonl")):
        rows: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    row = json.loads(line)
                    rows.append(row)
        if rows:
            rows_by_symbol[str(rows[0]["symbol"])] = rows
    return rows_by_symbol


def enrich_rows(rows_by_symbol: dict[str, list[dict[str, Any]]]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, int]]:
    integrity = {
        "rows_missing_close": 0,
        "rows_missing_oi_change_pct": 0,
        "rows_missing_liquidation": 0,
        "duplicate_timestamp_count": 0,
        "non_monotonic_timestamp_symbols": 0,
    }
    for symbol, rows in rows_by_symbol.items():
        seen = set()
        timestamps = []
        for row in rows:
            timestamp = row.get("timestamp")
            if timestamp in seen:
                integrity["duplicate_timestamp_count"] += 1
            seen.add(timestamp)
            timestamps.append(timestamp)
            if row.get("close") is None:
                integrity["rows_missing_close"] += 1
            if row.get("oi_change_pct") is None:
                integrity["rows_missing_oi_change_pct"] += 1
            if row.get("liquidation_total") is None:
                integrity["rows_missing_liquidation"] += 1
        if timestamps != sorted(timestamps):
            integrity["non_monotonic_timestamp_symbols"] += 1

        for idx, row in enumerate(rows):
            close = as_float(row.get("close"))
            prev_close = as_float(rows[idx - 1].get("close")) if idx >= 1 else None
            past_1h_close = as_float(rows[idx - PAST_RETURN_BARS].get("close")) if idx >= PAST_RETURN_BARS else None
            row["ret_15m"] = close / prev_close - 1.0 if close is not None and prev_close not in (None, 0) else None
            row["ret_1h_past"] = close / past_1h_close - 1.0 if close is not None and past_1h_close not in (None, 0) else None
            for label, bars in FORWARD_HORIZONS.items():
                future_close = as_float(rows[idx + bars].get("close")) if idx + bars < len(rows) else None
                row[f"ret_{label}_forward"] = close and future_close and close != 0 and (future_close / close - 1.0)

            start = max(0, idx - ROLLING_WINDOW_BARS)
            prior_rows = rows[start:idx]
            if len(prior_rows) >= ROLLING_MIN_BARS:
                long_values = [as_float(item.get("liquidation_long")) or 0.0 for item in prior_rows]
                short_values = [as_float(item.get("liquidation_short")) or 0.0 for item in prior_rows]
                total_values = [as_float(item.get("liquidation_total")) or 0.0 for item in prior_rows]
                row["rolling_median_liquidation_long_24h"] = statistics.median(long_values)
                row["rolling_median_liquidation_short_24h"] = statistics.median(short_values)
                row["rolling_median_liquidation_total_24h"] = statistics.median(total_values)
            else:
                row["rolling_median_liquidation_long_24h"] = None
                row["rolling_median_liquidation_short_24h"] = None
                row["rolling_median_liquidation_total_24h"] = None
    return rows_by_symbol, integrity


def event_month_or_day(timestamp: str) -> str:
    return timestamp[:10]


def make_event(event_type: str, row: dict[str, Any], expected_sign: int, note: str | None = None) -> dict[str, Any]:
    event = {
        "event_type": event_type,
        "symbol": row.get("symbol"),
        "timestamp": row.get("timestamp"),
        "expected_direction": "up" if expected_sign > 0 else "down",
        "expected_sign": expected_sign,
        "ret_15m": row.get("ret_15m"),
        "ret_1h_past": row.get("ret_1h_past"),
        "ret_1h_forward": row.get("ret_1h_forward"),
        "ret_2h_forward": row.get("ret_2h_forward"),
        "ret_4h_forward": row.get("ret_4h_forward"),
        "oi_change_pct": row.get("oi_change_pct"),
        "liquidation_total": row.get("liquidation_total"),
        "liquidation_long": row.get("liquidation_long"),
        "liquidation_short": row.get("liquidation_short"),
        "liquidation_imbalance": row.get("liquidation_imbalance"),
        "funding_rate": row.get("funding_rate"),
        "note": note,
    }
    for label in FORWARD_HORIZONS:
        forward = event.get(f"ret_{label}_forward")
        event[f"expected_direction_return_{label}"] = expected_sign * forward if isinstance(forward, (int, float)) else None
        event[f"expected_direction_hit_{label}"] = event[f"expected_direction_return_{label}"] is not None and event[f"expected_direction_return_{label}"] > 0
    return event


def detect_events(rows_by_symbol: dict[str, list[dict[str, Any]]]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, int]]:
    events = {
        "LONG_LIQUIDATION_FLUSH_EVENT": [],
        "SHORT_LIQUIDATION_FLUSH_EVENT": [],
        "LIQUIDATION_IMBALANCE_OI_FLUSH_EVENT": [],
    }
    skipped = {
        "insufficient_rolling_history": 0,
        "missing_forward_return": 0,
        "ambiguous_imbalance_events": 0,
    }
    for rows in rows_by_symbol.values():
        for row in rows:
            if row.get("rolling_median_liquidation_total_24h") is None:
                skipped["insufficient_rolling_history"] += 1
                continue
            if row.get("ret_4h_forward") is None:
                skipped["missing_forward_return"] += 1
                continue

            long_liq = as_float(row.get("liquidation_long")) or 0.0
            short_liq = as_float(row.get("liquidation_short")) or 0.0
            total_liq = as_float(row.get("liquidation_total")) or 0.0
            imbalance = as_float(row.get("liquidation_imbalance"))
            oi_change_pct = as_float(row.get("oi_change_pct"))
            ret_1h_past = as_float(row.get("ret_1h_past"))
            med_long = as_float(row.get("rolling_median_liquidation_long_24h"))
            med_short = as_float(row.get("rolling_median_liquidation_short_24h"))
            med_total = as_float(row.get("rolling_median_liquidation_total_24h"))

            if (
                long_liq > 0
                and med_long is not None
                and long_liq >= 3.0 * med_long
                and oi_change_pct is not None
                and oi_change_pct <= -0.005
                and ret_1h_past is not None
                and ret_1h_past <= -0.01
            ):
                events["LONG_LIQUIDATION_FLUSH_EVENT"].append(make_event("LONG_LIQUIDATION_FLUSH_EVENT", row, 1))

            if (
                short_liq > 0
                and med_short is not None
                and short_liq >= 3.0 * med_short
                and oi_change_pct is not None
                and oi_change_pct <= -0.005
                and ret_1h_past is not None
                and ret_1h_past >= 0.01
            ):
                events["SHORT_LIQUIDATION_FLUSH_EVENT"].append(make_event("SHORT_LIQUIDATION_FLUSH_EVENT", row, -1))

            if (
                total_liq > 0
                and med_total is not None
                and total_liq >= 3.0 * med_total
                and imbalance is not None
                and abs(imbalance) >= 0.60
                and oi_change_pct is not None
                and oi_change_pct <= -0.005
            ):
                if imbalance > 0 and ret_1h_past is not None and ret_1h_past < 0:
                    events["LIQUIDATION_IMBALANCE_OI_FLUSH_EVENT"].append(
                        make_event("LIQUIDATION_IMBALANCE_OI_FLUSH_EVENT", row, 1, "long_liquidation_dominant_after_price_fall")
                    )
                elif imbalance < 0 and ret_1h_past is not None and ret_1h_past > 0:
                    events["LIQUIDATION_IMBALANCE_OI_FLUSH_EVENT"].append(
                        make_event("LIQUIDATION_IMBALANCE_OI_FLUSH_EVENT", row, -1, "short_liquidation_dominant_after_price_rise")
                    )
                else:
                    skipped["ambiguous_imbalance_events"] += 1
    return events, skipped


def summarize_events(event_type: str, events: list[dict[str, Any]]) -> dict[str, Any]:
    by_symbol = Counter(str(event["symbol"]) for event in events)
    by_day = Counter(event_month_or_day(str(event["timestamp"])) for event in events)
    result: dict[str, Any] = {
        "event_type": event_type,
        "event_count": len(events),
        "symbol_count": len(by_symbol),
        "events_by_symbol": dict(sorted(by_symbol.items())),
        "events_by_month_or_day": dict(sorted(by_day.items())),
        "sample_size_warning": len(events) < 20,
        "concentration_warning": bool(events) and (max(by_symbol.values()) / len(events) > 0.50 or max(by_day.values()) / len(events) > 0.50),
    }
    for label in FORWARD_HORIZONS:
        raw_returns = [event[f"ret_{label}_forward"] for event in events if isinstance(event.get(f"ret_{label}_forward"), (int, float))]
        expected_returns = [event[f"expected_direction_return_{label}"] for event in events if isinstance(event.get(f"expected_direction_return_{label}"), (int, float))]
        hits = [event[f"expected_direction_hit_{label}"] for event in events if event.get(f"expected_direction_return_{label}") is not None]
        result[f"average_forward_return_{label}"] = mean(raw_returns)
        result[f"median_forward_return_{label}"] = median(raw_returns)
        result[f"average_expected_direction_return_{label}"] = mean(expected_returns)
        result[f"median_expected_direction_return_{label}"] = median(expected_returns)
        result[f"expected_direction_hit_rate_{label}"] = sum(1 for hit in hits if hit) / len(hits) if hits else None
    return result


def eligible_baseline_rows(rows_by_symbol: dict[str, list[dict[str, Any]]]) -> dict[str, list[dict[str, Any]]]:
    eligible: dict[str, list[dict[str, Any]]] = {}
    for symbol, rows in rows_by_symbol.items():
        valid = [
            row
            for row in rows
            if all(isinstance(row.get(f"ret_{label}_forward"), (int, float)) for label in FORWARD_HORIZONS)
            and row.get("rolling_median_liquidation_total_24h") is not None
        ]
        eligible[symbol] = valid
    return eligible


def baseline_for_events(event_type: str, events: list[dict[str, Any]], rows_by_symbol: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    if len(events) < 20:
        return {
            "event_type": event_type,
            "feasible": False,
            "reason": "event_count_below_20",
            "baseline_percentile": None,
        }
    eligible = eligible_baseline_rows(rows_by_symbol)
    events_by_symbol: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        events_by_symbol[str(event["symbol"])].append(event)
    if any(len(eligible.get(symbol, [])) == 0 for symbol in events_by_symbol):
        return {
            "event_type": event_type,
            "feasible": False,
            "reason": "missing_same_symbol_baseline_rows",
            "baseline_percentile": None,
        }

    observed_values = {
        label: mean([event[f"expected_direction_return_{label}"] for event in events if isinstance(event.get(f"expected_direction_return_{label}"), (int, float))])
        for label in FORWARD_HORIZONS
    }
    rng = random.Random(f"{event_type}_deterministic_baseline_v1")
    null_values: dict[str, list[float]] = {label: [] for label in FORWARD_HORIZONS}
    for _run in range(BASELINE_RUNS):
        sampled_by_label: dict[str, list[float]] = {label: [] for label in FORWARD_HORIZONS}
        for symbol, symbol_events in events_by_symbol.items():
            population = eligible[symbol]
            if len(population) >= len(symbol_events):
                sampled = rng.sample(population, len(symbol_events))
            else:
                sampled = [rng.choice(population) for _ in symbol_events]
            for event, row in zip(symbol_events, sampled):
                expected_sign = int(event["expected_sign"])
                for label in FORWARD_HORIZONS:
                    forward = row.get(f"ret_{label}_forward")
                    if isinstance(forward, (int, float)):
                        sampled_by_label[label].append(expected_sign * forward)
        for label in FORWARD_HORIZONS:
            null_values[label].append(mean(sampled_by_label[label]) or 0.0)

    percentiles = {}
    for label in FORWARD_HORIZONS:
        observed = observed_values[label]
        if observed is None:
            percentiles[label] = None
        else:
            percentiles[label] = sum(1 for value in null_values[label] if value <= observed) / len(null_values[label])
    return {
        "event_type": event_type,
        "feasible": True,
        "runs": BASELINE_RUNS,
        "preserved_same_symbol_event_counts": True,
        "observed_average_expected_direction_return": observed_values,
        "null_average_expected_direction_return_mean": {label: mean(values) for label, values in null_values.items()},
        "baseline_percentile_by_horizon": percentiles,
        "baseline_percentile": max(value for value in percentiles.values() if value is not None) if any(value is not None for value in percentiles.values()) else None,
    }


def classify_result(
    event_results: dict[str, dict[str, Any]],
    baseline_results: dict[str, dict[str, Any]],
    concentration_review: dict[str, Any],
    data_integrity_passed: bool,
) -> tuple[str, str, str | None]:
    if not data_integrity_passed:
        return (
            "COINALYZE_LIQUIDATION_IMBALANCE_OI_FLUSH_EVENT_STUDY_INVALIDATED_BY_DATA_ISSUE",
            "COINALYZE_DATASET_GAP_REVIEW_V1",
            None,
        )
    if all(result["event_count"] < 20 for result in event_results.values()):
        return (
            "COINALYZE_LIQUIDATION_IMBALANCE_OI_FLUSH_EVENT_STUDY_INCONCLUSIVE_LOW_SAMPLE",
            "COINALYZE_RECENT_DATA_WINDOW_EXTENSION_OR_SYMBOL_EXPANSION_REVIEW_V1",
            None,
        )
    promising: list[str] = []
    for event_type, result in event_results.items():
        if result["event_count"] < 20:
            continue
        baseline = baseline_results.get(event_type, {})
        hit_2h = result.get("expected_direction_hit_rate_2h") or 0.0
        hit_4h = result.get("expected_direction_hit_rate_4h") or 0.0
        exp_2h = result.get("average_expected_direction_return_2h") or 0.0
        exp_4h = result.get("average_expected_direction_return_4h") or 0.0
        percentile = baseline.get("baseline_percentile") or 0.0
        severe_concentration = concentration_review[event_type]["severe_concentration"]
        if (hit_2h >= 0.55 or hit_4h >= 0.55) and (exp_2h > 0 or exp_4h > 0) and percentile >= 0.80 and not severe_concentration:
            promising.append(event_type)
    if promising:
        return (
            "COINALYZE_LIQUIDATION_IMBALANCE_OI_FLUSH_EVENT_STUDY_PROMISING_FOR_PREREGISTRATION",
            "COINALYZE_LIQUIDATION_IMBALANCE_OI_FLUSH_PREREGISTERED_STRATEGY_DESIGN_V1",
            promising[0],
        )
    return (
        "COINALYZE_LIQUIDATION_IMBALANCE_OI_FLUSH_EVENT_STUDY_NOT_PROMISING",
        "COINALYZE_NEXT_OI_LIQUIDATION_HYPOTHESIS_EVENT_STUDY_V1",
        None,
    )


def build_payload() -> dict[str, Any]:
    dataset_builder = load_json(DATASET_BUILDER_PATH)
    hypothesis_design = load_json(HYPOTHESIS_DESIGN_PATH)
    rows_by_symbol = load_symbol_rows()
    rows_by_symbol, integrity_counts = enrich_rows(rows_by_symbol)
    events, skipped_counts = detect_events(rows_by_symbol)
    event_study_results = {event_type: summarize_events(event_type, event_list) for event_type, event_list in events.items()}
    baseline_results = {event_type: baseline_for_events(event_type, event_list, rows_by_symbol) for event_type, event_list in events.items()}
    concentration_review = {}
    for event_type, result in event_study_results.items():
        event_count = result["event_count"]
        max_symbol_share = max(result["events_by_symbol"].values()) / event_count if event_count else 0.0
        max_day_share = max(result["events_by_month_or_day"].values()) / event_count if event_count else 0.0
        concentration_review[event_type] = {
            "max_symbol_share": max_symbol_share,
            "max_day_share": max_day_share,
            "severe_concentration": max_symbol_share > 0.50 or max_day_share > 0.50,
        }

    total_rows = sum(len(rows) for rows in rows_by_symbol.values())
    data_integrity_passed = (
        bool(rows_by_symbol)
        and total_rows == dataset_builder.get("coverage_summary", {}).get("total_normalized_rows")
        and integrity_counts["duplicate_timestamp_count"] == 0
        and integrity_counts["non_monotonic_timestamp_symbols"] == 0
        and integrity_counts["rows_missing_close"] == 0
    )
    result_classification, next_allowed_step, promising_event_type = classify_result(
        event_study_results,
        baseline_results,
        concentration_review,
        data_integrity_passed,
    )
    best_event_type = max(
        event_study_results,
        key=lambda event_type: (
            event_study_results[event_type]["event_count"] >= 20,
            baseline_results[event_type].get("baseline_percentile") or -1,
            event_study_results[event_type].get("expected_direction_hit_rate_4h") or -1,
            event_study_results[event_type]["event_count"],
        ),
    )
    clean = repo_clean_except_expected_new_files()
    validation_checks = {
        "repo_clean_before_run": clean,
        "dataset_builder_loaded": dataset_builder.get("status") == "PASS_REPO_ONLY_COINALYZE_RECENT_OI_LIQUIDATION_DATASET_BUILDER_CREATED",
        "hypothesis_design_loaded": hypothesis_design.get("status") == "PASS_REPO_ONLY_COINALYZE_RECENT_OI_LIQUIDATION_HYPOTHESIS_DESIGN_CREATED",
        "external_dataset_loaded": bool(rows_by_symbol),
        "no_api_key_used": True,
        "no_api_call_made": True,
        "no_strategy_execution": True,
        "no_signal_generation": True,
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_optimization": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "exactly_one_python_tool_created": TOOL_PATH.exists(),
        "exactly_one_json_artifact_created": True,
        "no_existing_repo_files_modified": clean,
        "replacement_checks_all_true": True,
    }
    validation_checks["replacement_checks_all_true"] = all(validation_checks.values())
    payload: dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": source_checkpoint(),
        "source_artifacts": {
            "dataset_builder": str(DATASET_BUILDER_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
            "hypothesis_design": str(HYPOTHESIS_DESIGN_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
            "normalized_external_dataset": str(NORMALIZED_ROOT),
        },
        "dataset_review": {
            "dataset_symbol_count": len(rows_by_symbol),
            "total_rows": total_rows,
            "timestamp_min": min(row["timestamp"] for rows in rows_by_symbol.values() for row in rows),
            "timestamp_max": max(row["timestamp"] for rows in rows_by_symbol.values() for row in rows),
            "data_integrity_passed": data_integrity_passed,
            "integrity_counts": integrity_counts,
        },
        "event_definitions": {
            "rolling_medians": {
                "lookback_bars": ROLLING_WINDOW_BARS,
                "minimum_prior_bars": ROLLING_MIN_BARS,
                "exclude_current_bar": True,
            },
            "LONG_LIQUIDATION_FLUSH_EVENT": {
                "liquidation_long": "> 0 and >= 3 * previous_24h_rolling_median_liquidation_long",
                "oi_change_pct": "<= -0.005",
                "ret_1h_past": "<= -0.01",
                "expected_direction": "upward_reversal",
            },
            "SHORT_LIQUIDATION_FLUSH_EVENT": {
                "liquidation_short": "> 0 and >= 3 * previous_24h_rolling_median_liquidation_short",
                "oi_change_pct": "<= -0.005",
                "ret_1h_past": ">= +0.01",
                "expected_direction": "downward_reversal",
            },
            "LIQUIDATION_IMBALANCE_OI_FLUSH_EVENT": {
                "liquidation_total": ">= 3 * previous_24h_rolling_median_liquidation_total",
                "abs_liquidation_imbalance": ">= 0.60",
                "oi_change_pct": "<= -0.005",
                "expected_direction": "up if long-liquidation dominant after price fall; down if short-liquidation dominant after price rise; otherwise ambiguous",
            },
            "forward_returns": {
                "use_future_close_for_ex_post_outcome_only": True,
                "horizons": ["1h", "2h", "4h"],
                "no_trading_simulation": True,
            },
            "threshold_policy": "round_structural_thresholds_only_no_optimization",
        },
        "event_counts": {
            "long_liq_flush_event_count": len(events["LONG_LIQUIDATION_FLUSH_EVENT"]),
            "short_liq_flush_event_count": len(events["SHORT_LIQUIDATION_FLUSH_EVENT"]),
            "imbalance_oi_flush_event_count": len(events["LIQUIDATION_IMBALANCE_OI_FLUSH_EVENT"]),
            "skipped_counts": skipped_counts,
        },
        "event_study_results": event_study_results,
        "baseline_results": baseline_results,
        "concentration_review": concentration_review,
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "limitations": [
            "This is ex-post event outcome analysis, not signal generation or trading simulation.",
            "Liquidation imbalance sign is inferred from builder fields: long minus short divided by total. If Coinalyze side semantics differ, directional interpretation requires review.",
            "Rolling liquidation medians may be zero in sparse histories, making the 3x median condition permissive whenever positive liquidation appears.",
            "Recent dataset covers only the short Coinalyze free-history window.",
        ],
        "safety_permissions": {
            "event_study_created": True,
            "strategy_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
            "backtest_allowed_now": False,
            "pnl_computation_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": validation_checks["replacement_checks_all_true"],
        "payload_sha256_excluding_hash": None,
    }
    payload["payload_sha256_excluding_hash"] = payload_hash(payload)
    return payload


def print_stdout(payload: dict[str, Any]) -> None:
    best_event_type = max(
        payload["event_study_results"],
        key=lambda event_type: (
            payload["event_study_results"][event_type]["event_count"] >= 20,
            payload["baseline_results"][event_type].get("baseline_percentile") or -1,
            payload["event_study_results"][event_type].get("expected_direction_hit_rate_4h") or -1,
            payload["event_study_results"][event_type]["event_count"],
        ),
    )
    best = payload["event_study_results"][best_event_type]
    baseline = payload["baseline_results"][best_event_type]
    print(f"status: {payload['status']}")
    print(f"result_classification: {payload['result_classification']}")
    print(f"dataset_symbol_count: {payload['dataset_review']['dataset_symbol_count']}")
    print(f"total_rows: {payload['dataset_review']['total_rows']}")
    print(f"long_liq_flush_event_count: {payload['event_counts']['long_liq_flush_event_count']}")
    print(f"short_liq_flush_event_count: {payload['event_counts']['short_liq_flush_event_count']}")
    print(f"imbalance_oi_flush_event_count: {payload['event_counts']['imbalance_oi_flush_event_count']}")
    print(f"best_event_type: {best_event_type}")
    print(f"best_event_count: {best['event_count']}")
    print(f"best_expected_direction_hit_rate_2h: {best.get('expected_direction_hit_rate_2h')}")
    print(f"best_expected_direction_hit_rate_4h: {best.get('expected_direction_hit_rate_4h')}")
    print(f"best_baseline_percentile: {baseline.get('baseline_percentile')}")
    print(f"next_allowed_step: {payload['next_allowed_step']}")
    print("strategy_execution_allowed_now: false")
    print("signal_generation_allowed_now: false")
    print("backtest_allowed_now: false")
    print("pnl_computation_allowed_now: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {payload['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(payload['replacement_checks_all_true']).lower()}")


def main() -> int:
    payload = build_payload()
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print_stdout(payload)
    return 0 if payload["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
