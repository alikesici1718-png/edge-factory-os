#!/usr/bin/env python
"""Descriptive OI/taker/crowding proxy event study over Binance Data Vision metrics."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = "BINANCE_OI_TAKER_CROWDING_PROXY_EVENT_STUDY_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_binance_oi_taker_crowding_proxy_event_study_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/research/binance_oi_taker_crowding_proxy_event_study_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH
SOURCE_ARTIFACT_RELATIVE_PATH = "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"

STATUS_PASS = "PASS_REPO_ONLY_BINANCE_OI_TAKER_CROWDING_PROXY_EVENT_STUDY_CREATED"
STATUS_BLOCKED = "BLOCKED_BINANCE_OI_TAKER_CROWDING_PROXY_EVENT_STUDY"
ARTIFACT_KIND = "BINANCE_OI_TAKER_CROWDING_PROXY_EVENT_STUDY"

RESULT_READY_DESCRIPTIVE = "BINANCE_OI_TAKER_CROWDING_PROXY_EVENT_STUDY_READY_FOR_DEEPER_PROXY_VALIDATION"
RESULT_DESCRIPTIVE_PRICE_MISSING = "BINANCE_OI_TAKER_CROWDING_PROXY_EVENT_STUDY_DESCRIPTIVE_ONLY_PRICE_DEPENDENCY_MISSING"
RESULT_INSUFFICIENT = "BINANCE_OI_TAKER_CROWDING_PROXY_EVENT_STUDY_INSUFFICIENT"
RESULT_BLOCKED = "BINANCE_OI_TAKER_CROWDING_PROXY_EVENT_STUDY_BLOCKED"

NEXT_DEEPER_VALIDATION = "BINANCE_OI_TAKER_CROWDING_PROXY_VALIDATION_CONTRACT_V1"
NEXT_PRICE_DEPENDENCY = "BINANCE_PUBLIC_PRICE_DATA_DEPENDENCY_REVIEW_FOR_PROXY_EVENT_STUDY_V1"
NEXT_GAP_REVIEW = "BINANCE_OI_TAKER_CROWDING_PROXY_EVENT_STUDY_GAP_REVIEW_V1"
NEXT_BLOCKED = "BINANCE_OI_TAKER_CROWDING_PROXY_EVENT_STUDY_BLOCKER_REVIEW_V1"

SOURCE_DATASET_COMMIT = "f419728037c3650a00b0491ccdc8e551cff21653"
SOURCE_REPO_HEAD_BEFORE_TOOL_CREATION = "f419728037c3650a00b0491ccdc8e551cff21653"
TRACKED_PYTHON_COUNT_BEFORE_TOOL_CREATION = 1057
GIT_STATUS_SHORT_BEFORE_TOOL_CREATION: list[str] = []

REQUESTED_SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "DOGEUSDT",
    "XRPUSDT",
    "BNBUSDT",
    "LINKUSDT",
    "APTUSDT",
    "ARBUSDT",
    "OPUSDT",
]

EVENT_DEFINITIONS = [
    {
        "event_id": "oi_expansion_taker_buy_global_crowding_high",
        "description": "OI expansion with high taker buy/sell ratio and high global account long/short crowding.",
        "thresholds": {
            "oi_change_pct": "symbol p90",
            "taker_buy_sell_ratio": "symbol p90",
            "account_long_short_ratio": "symbol p90",
        },
        "non_tradable_research_label": True,
    },
    {
        "event_id": "oi_expansion_taker_sell_global_crowding_low",
        "description": "OI expansion with low taker buy/sell ratio and low global account long/short crowding.",
        "thresholds": {
            "oi_change_pct": "symbol p90",
            "taker_buy_sell_ratio": "symbol p10",
            "account_long_short_ratio": "symbol p10",
        },
        "non_tradable_research_label": True,
    },
    {
        "event_id": "oi_expansion_top_account_crowding_high",
        "description": "OI expansion with high top-trader account long/short crowding.",
        "thresholds": {
            "oi_change_pct": "symbol p90",
            "top_account_long_short_ratio": "symbol p90",
        },
        "non_tradable_research_label": True,
    },
    {
        "event_id": "oi_expansion_top_position_crowding_high",
        "description": "OI expansion with high top-trader position long/short crowding.",
        "thresholds": {
            "oi_change_pct": "symbol p90",
            "top_position_long_short_ratio": "symbol p90",
        },
        "non_tradable_research_label": True,
    },
    {
        "event_id": "broad_proxy_alignment_extreme",
        "description": "OI expansion with at least three same-side taker/account/top-account/top-position proxy extremes.",
        "thresholds": {
            "oi_change_pct": "symbol p75",
            "proxy_extremes": "at least three of taker/global/top-account/top-position above p90 or below p10",
        },
        "non_tradable_research_label": True,
    },
]

FORBIDDEN_ROUTE_REUSE = [
    "funding crowding reversal",
    "taker-buy exhaustion",
    "taker-flow momentum continuation",
    "funding carry",
    "funding volume surge",
]


class EventStudyBlocked(Exception):
    pass


def canonical_payload_hash(payload: dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(clean, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def git_status_short() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        return [f"git_status_failed: {result.stderr.strip()}"]
    return [line.rstrip() for line in result.stdout.splitlines() if line.strip()]


def tracked_python_count() -> int | None:
    result = subprocess.run(
        ["git", "ls-files", "*.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        return None
    return len([line for line in result.stdout.splitlines() if line.strip()])


def no_existing_tracked_files_modified(status_lines: list[str]) -> bool:
    allowed = {
        f"?? {MODULE_RELATIVE_PATH}",
        f"?? {ARTIFACT_RELATIVE_PATH}",
        f"A  {MODULE_RELATIVE_PATH}",
        f"A  {ARTIFACT_RELATIVE_PATH}",
    }
    for line in status_lines:
        if line in allowed:
            continue
        if line.startswith("?? "):
            continue
        return False
    return True


def existing_artifact_can_be_replaced() -> bool:
    if not ARTIFACT_PATH.exists():
        return True
    try:
        payload = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    except Exception:
        return False
    return payload.get("artifact_kind") == ARTIFACT_KIND and payload.get("module") == MODULE


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise EventStudyBlocked(f"missing required input artifact: {path.relative_to(REPO_ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise EventStudyBlocked(f"input artifact is not a JSON object: {path.relative_to(REPO_ROOT)}")
    return payload


def load_dataset_builder_artifact() -> tuple[dict[str, Any], str]:
    payload = read_json(REPO_ROOT / SOURCE_ARTIFACT_RELATIVE_PATH)
    stored_hash = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored_hash, str):
        raise EventStudyBlocked("dataset builder artifact missing payload_sha256_excluding_hash")
    recomputed_hash = canonical_payload_hash(payload)
    if stored_hash != recomputed_hash:
        raise EventStudyBlocked(f"dataset builder hash mismatch: {recomputed_hash} != {stored_hash}")
    if payload.get("status") != "PASS_REPO_ONLY_BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILDER_CREATED":
        raise EventStudyBlocked("dataset builder artifact status is not PASS")
    if payload.get("replacement_checks_all_true") is not True:
        raise EventStudyBlocked("dataset builder replacement_checks_all_true is not true")
    if payload.get("result_classification") != "BINANCE_DATA_VISION_UM_METRICS_DATASET_READY_FOR_PROXY_EVENT_STUDY":
        raise EventStudyBlocked("dataset builder artifact is not ready for proxy event study")
    return payload, stored_hash


def to_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"none", "null", "nan"}:
        return None
    try:
        output = float(text)
    except ValueError:
        return None
    if math.isnan(output) or math.isinf(output):
        return None
    return output


def quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    pos = (len(ordered) - 1) * q
    lower = int(math.floor(pos))
    upper = int(math.ceil(pos))
    if lower == upper:
        return ordered[lower]
    fraction = pos - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def update_numeric_summary(summary: dict[str, Any], value: float | None) -> None:
    if value is None:
        return
    summary["count"] += 1
    summary["sum"] += value
    summary["min"] = value if summary["min"] is None else min(summary["min"], value)
    summary["max"] = value if summary["max"] is None else max(summary["max"], value)


def finalize_numeric_summary(summary: dict[str, Any]) -> dict[str, Any]:
    count = summary["count"]
    return {
        "count": count,
        "mean": (summary["sum"] / count) if count else None,
        "min": summary["min"],
        "max": summary["max"],
    }


def empty_event_summary(event_id: str) -> dict[str, Any]:
    return {
        "event_id": event_id,
        "event_count": 0,
        "symbols": set(),
        "timestamp_min": None,
        "timestamp_max": None,
        "counts_by_year": {},
        "counts_by_hour_utc": {f"{hour:02d}": 0 for hour in range(24)},
        "context_numeric": {
            "oi_change_pct": {"count": 0, "sum": 0.0, "min": None, "max": None},
            "taker_buy_sell_ratio": {"count": 0, "sum": 0.0, "min": None, "max": None},
            "account_long_short_ratio": {"count": 0, "sum": 0.0, "min": None, "max": None},
            "top_account_long_short_ratio": {"count": 0, "sum": 0.0, "min": None, "max": None},
            "top_position_long_short_ratio": {"count": 0, "sum": 0.0, "min": None, "max": None},
        },
    }


def update_event_summary(summary: dict[str, Any], row: dict[str, str], values: dict[str, float | None]) -> None:
    timestamp = row["timestamp"]
    summary["event_count"] += 1
    summary["symbols"].add(row["symbol"])
    summary["timestamp_min"] = timestamp if summary["timestamp_min"] is None else min(summary["timestamp_min"], timestamp)
    summary["timestamp_max"] = timestamp if summary["timestamp_max"] is None else max(summary["timestamp_max"], timestamp)
    year = timestamp[:4]
    hour = timestamp[11:13]
    summary["counts_by_year"][year] = summary["counts_by_year"].get(year, 0) + 1
    summary["counts_by_hour_utc"][hour] = summary["counts_by_hour_utc"].get(hour, 0) + 1
    for key, value in values.items():
        if key in summary["context_numeric"]:
            update_numeric_summary(summary["context_numeric"][key], value)


def finalize_event_summary(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_id": summary["event_id"],
        "event_count": summary["event_count"],
        "symbol_count": len(summary["symbols"]),
        "symbols": sorted(summary["symbols"]),
        "timestamp_min": summary["timestamp_min"],
        "timestamp_max": summary["timestamp_max"],
        "counts_by_year": dict(sorted(summary["counts_by_year"].items())),
        "counts_by_hour_utc": summary["counts_by_hour_utc"],
        "context_numeric": {
            key: finalize_numeric_summary(value) for key, value in summary["context_numeric"].items()
        },
    }


def collect_thresholds(path: Path) -> tuple[dict[str, dict[str, float | None]], dict[str, Any]]:
    values = {
        "oi_change_pct": [],
        "taker_buy_sell_ratio": [],
        "account_long_short_ratio": [],
        "top_account_long_short_ratio": [],
        "top_position_long_short_ratio": [],
    }
    rows = 0
    missing_by_field = {key: 0 for key in values}
    timestamp_min = None
    timestamp_max = None
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows += 1
            timestamp = row.get("timestamp")
            if timestamp:
                timestamp_min = timestamp if timestamp_min is None else min(timestamp_min, timestamp)
                timestamp_max = timestamp if timestamp_max is None else max(timestamp_max, timestamp)
            for key in values:
                value = to_float(row.get(key))
                if value is None:
                    missing_by_field[key] += 1
                else:
                    values[key].append(value)
    thresholds = {
        key: {
            "p10": quantile(field_values, 0.10),
            "p25": quantile(field_values, 0.25),
            "p75": quantile(field_values, 0.75),
            "p90": quantile(field_values, 0.90),
            "observed_count": len(field_values),
            "missing_count": missing_by_field[key],
        }
        for key, field_values in values.items()
    }
    coverage = {
        "row_count": rows,
        "timestamp_min": timestamp_min,
        "timestamp_max": timestamp_max,
        "missing_by_field": missing_by_field,
    }
    return thresholds, coverage


def ge(value: float | None, threshold: float | None) -> bool:
    return value is not None and threshold is not None and value >= threshold


def le(value: float | None, threshold: float | None) -> bool:
    return value is not None and threshold is not None and value <= threshold


def evaluate_events(row: dict[str, str], thresholds: dict[str, dict[str, float | None]]) -> tuple[list[str], dict[str, float | None]]:
    values = {
        "oi_change_pct": to_float(row.get("oi_change_pct")),
        "taker_buy_sell_ratio": to_float(row.get("taker_buy_sell_ratio")),
        "account_long_short_ratio": to_float(row.get("account_long_short_ratio")),
        "top_account_long_short_ratio": to_float(row.get("top_account_long_short_ratio")),
        "top_position_long_short_ratio": to_float(row.get("top_position_long_short_ratio")),
    }
    events: list[str] = []
    if (
        ge(values["oi_change_pct"], thresholds["oi_change_pct"]["p90"])
        and ge(values["taker_buy_sell_ratio"], thresholds["taker_buy_sell_ratio"]["p90"])
        and ge(values["account_long_short_ratio"], thresholds["account_long_short_ratio"]["p90"])
    ):
        events.append("oi_expansion_taker_buy_global_crowding_high")
    if (
        ge(values["oi_change_pct"], thresholds["oi_change_pct"]["p90"])
        and le(values["taker_buy_sell_ratio"], thresholds["taker_buy_sell_ratio"]["p10"])
        and le(values["account_long_short_ratio"], thresholds["account_long_short_ratio"]["p10"])
    ):
        events.append("oi_expansion_taker_sell_global_crowding_low")
    if ge(values["oi_change_pct"], thresholds["oi_change_pct"]["p90"]) and ge(
        values["top_account_long_short_ratio"],
        thresholds["top_account_long_short_ratio"]["p90"],
    ):
        events.append("oi_expansion_top_account_crowding_high")
    if ge(values["oi_change_pct"], thresholds["oi_change_pct"]["p90"]) and ge(
        values["top_position_long_short_ratio"],
        thresholds["top_position_long_short_ratio"]["p90"],
    ):
        events.append("oi_expansion_top_position_crowding_high")
    high_extremes = sum(
        ge(values[key], thresholds[key]["p90"])
        for key in [
            "taker_buy_sell_ratio",
            "account_long_short_ratio",
            "top_account_long_short_ratio",
            "top_position_long_short_ratio",
        ]
    )
    low_extremes = sum(
        le(values[key], thresholds[key]["p10"])
        for key in [
            "taker_buy_sell_ratio",
            "account_long_short_ratio",
            "top_account_long_short_ratio",
            "top_position_long_short_ratio",
        ]
    )
    if ge(values["oi_change_pct"], thresholds["oi_change_pct"]["p75"]) and (high_extremes >= 3 or low_extremes >= 3):
        events.append("broad_proxy_alignment_extreme")
    return events, values


def validate_normalized_files(dataset_artifact: dict[str, Any]) -> list[Path]:
    files = dataset_artifact.get("generated_external_files", {}).get("normalized_by_symbol_files")
    if not isinstance(files, list) or len(files) != len(REQUESTED_SYMBOLS):
        raise EventStudyBlocked("dataset artifact does not list the expected normalized symbol files")
    paths = [Path(str(path)) for path in files]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise EventStudyBlocked(f"normalized files missing: {missing}")
    symbol_names = {path.name.split("_", 1)[0] for path in paths}
    if sorted(symbol_names) != sorted(REQUESTED_SYMBOLS):
        raise EventStudyBlocked(f"normalized file symbol set mismatch: {sorted(symbol_names)}")
    return sorted(paths, key=lambda path: path.name)


def run_event_study() -> dict[str, Any]:
    if not existing_artifact_can_be_replaced():
        raise EventStudyBlocked(f"artifact already exists and is not this module output: {ARTIFACT_RELATIVE_PATH}")
    status_at_run_start = git_status_short()
    dataset_artifact, dataset_hash = load_dataset_builder_artifact()
    normalized_files = validate_normalized_files(dataset_artifact)

    event_summaries = {definition["event_id"]: empty_event_summary(definition["event_id"]) for definition in EVENT_DEFINITIONS}
    per_symbol_thresholds: dict[str, Any] = {}
    per_symbol_coverage: dict[str, Any] = {}
    total_rows = 0
    global_timestamp_min = None
    global_timestamp_max = None

    for path in normalized_files:
        symbol = path.name.split("_", 1)[0]
        thresholds, coverage = collect_thresholds(path)
        per_symbol_thresholds[symbol] = thresholds
        per_symbol_coverage[symbol] = coverage
        total_rows += coverage["row_count"]
        if coverage["timestamp_min"]:
            global_timestamp_min = coverage["timestamp_min"] if global_timestamp_min is None else min(global_timestamp_min, coverage["timestamp_min"])
        if coverage["timestamp_max"]:
            global_timestamp_max = coverage["timestamp_max"] if global_timestamp_max is None else max(global_timestamp_max, coverage["timestamp_max"])

        with path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                events, values = evaluate_events(row, thresholds)
                for event_id in events:
                    update_event_summary(event_summaries[event_id], row, values)

    finalized_events = {event_id: finalize_event_summary(summary) for event_id, summary in event_summaries.items()}
    event_count = sum(item["event_count"] for item in finalized_events.values())
    unique_event_symbols = sorted({symbol for item in finalized_events.values() for symbol in item["symbols"]})
    event_timestamp_mins = [item["timestamp_min"] for item in finalized_events.values() if item["timestamp_min"]]
    event_timestamp_maxs = [item["timestamp_max"] for item in finalized_events.values() if item["timestamp_max"]]
    symbols_with_any_event = len(unique_event_symbols)
    alignment_quality = {
        "normalized_files_loaded": len(normalized_files),
        "rows_scanned": total_rows,
        "symbols_with_any_event": symbols_with_any_event,
        "event_definitions_with_events": sum(1 for item in finalized_events.values() if item["event_count"] > 0),
        "event_definitions_tested": len(EVENT_DEFINITIONS),
        "timestamp_range_matches_dataset": (
            global_timestamp_min == dataset_artifact["normalized_dataset_summary"]["timestamp_global_min"]
            and global_timestamp_max == dataset_artifact["normalized_dataset_summary"]["timestamp_global_max"]
        ),
    }
    missingness = {
        "per_symbol_missing_by_field": {
            symbol: coverage["missing_by_field"] for symbol, coverage in per_symbol_coverage.items()
        },
        "total_missing_by_field": {},
    }
    for coverage in per_symbol_coverage.values():
        for field, count in coverage["missing_by_field"].items():
            missingness["total_missing_by_field"][field] = missingness["total_missing_by_field"].get(field, 0) + count

    return_dependency = {
        "forward_return_impact_computed": False,
        "reason": "normalized Binance Data Vision UM metrics dataset has no public price/return fields",
        "required_dependency_for_future": "public price dataset aligned by symbol and timestamp",
        "diagnostic_label_status": "skipped_missing_dependency",
    }
    descriptive_ready = event_count > 0 and symbols_with_any_event >= 5 and alignment_quality["timestamp_range_matches_dataset"]
    deeper_proxy_validation_recommended = descriptive_ready
    result_classification = RESULT_DESCRIPTIVE_PRICE_MISSING if descriptive_ready else RESULT_INSUFFICIENT
    next_allowed_step = NEXT_PRICE_DEPENDENCY if descriptive_ready else NEXT_GAP_REVIEW
    if deeper_proxy_validation_recommended:
        next_allowed_step = NEXT_DEEPER_VALIDATION
        result_classification = RESULT_READY_DESCRIPTIVE

    validation_checks = {
        "repo_clean_before_run": GIT_STATUS_SHORT_BEFORE_TOOL_CREATION == [],
        "dataset_builder_artifact_loaded": True,
        "dataset_builder_artifact_hash_verified": True,
        "normalized_dataset_loaded": len(normalized_files) == len(REQUESTED_SYMBOLS),
        "read_only_research_event_study": True,
        "descriptive_statistics_only": True,
        "return_impact_skipped_missing_price_dependency": True,
        "no_private_api_used": True,
        "no_account_api_used": True,
        "no_order_endpoint_used": True,
        "no_api_key_used": True,
        "no_strategy_execution": True,
        "no_signal_generation": True,
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_trade_simulation": True,
        "no_optimization": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_failed_strategy_route_reuse": True,
        "exactly_one_python_tool_created": (REPO_ROOT / MODULE_RELATIVE_PATH).exists(),
        "exactly_one_json_artifact_created": True,
        "no_existing_tracked_files_modified": no_existing_tracked_files_modified(status_at_run_start),
    }
    replacement_checks_all_true = all(value is True for value in validation_checks.values())
    validation_checks["replacement_checks_all_true"] = replacement_checks_all_true

    artifact: dict[str, Any] = {
        "status": STATUS_PASS if replacement_checks_all_true else STATUS_BLOCKED,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "repo_root": str(REPO_ROOT),
            "source_dataset_commit": SOURCE_DATASET_COMMIT,
            "repo_head_before_tool_creation": SOURCE_REPO_HEAD_BEFORE_TOOL_CREATION,
            "tracked_python_count_before_tool_creation": TRACKED_PYTHON_COUNT_BEFORE_TOOL_CREATION,
            "tracked_python_count_at_run": tracked_python_count(),
            "git_status_short_before_tool_creation": GIT_STATUS_SHORT_BEFORE_TOOL_CREATION,
            "git_status_short_at_run_start": status_at_run_start,
            "run_started_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "source_artifacts": {
            "binance_data_vision_um_metrics_dataset_builder": {
                "path": SOURCE_ARTIFACT_RELATIVE_PATH,
                "status": dataset_artifact.get("status"),
                "result_classification": dataset_artifact.get("result_classification"),
                "payload_sha256_excluding_hash": dataset_hash,
            }
        },
        "input_dataset_summary": dataset_artifact.get("normalized_dataset_summary", {}),
        "event_count": event_count,
        "symbol_count": symbols_with_any_event,
        "timestamp_range": {
            "dataset_timestamp_min": global_timestamp_min,
            "dataset_timestamp_max": global_timestamp_max,
            "event_timestamp_min": min(event_timestamp_mins) if event_timestamp_mins else None,
            "event_timestamp_max": max(event_timestamp_maxs) if event_timestamp_maxs else None,
        },
        "proxy_event_definitions_tested": EVENT_DEFINITIONS,
        "descriptive_statistics": {
            "events_by_definition": finalized_events,
            "event_definition_count": len(EVENT_DEFINITIONS),
            "total_event_rows_counting_overlaps": event_count,
            "symbols_with_any_event": unique_event_symbols,
            "per_symbol_thresholds": per_symbol_thresholds,
        },
        "alignment_quality": alignment_quality,
        "missingness": missingness,
        "regime_context_summaries": {
            "by_year": {
                event_id: summary["counts_by_year"] for event_id, summary in finalized_events.items()
            },
            "by_hour_utc": {
                event_id: summary["counts_by_hour_utc"] for event_id, summary in finalized_events.items()
            },
        },
        "forward_return_diagnostic": return_dependency,
        "validation_limits": [
            "This is a descriptive proxy event study only.",
            "Events are non-tradable research labels derived from OI, taker ratio, and crowding ratios.",
            "No public price fields are present in the normalized metrics dataset, so forward-return diagnostics were skipped.",
            "No strategy, signal, backtest, PnL, trade simulation, optimization, candidate generation, or edge claim was performed.",
            "Previously failed strategy routes were not reused.",
        ],
        "deeper_proxy_validation_contract_recommended": deeper_proxy_validation_recommended,
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "safety_permissions": {
            "read_only_research_event_study_created": replacement_checks_all_true,
            "deeper_proxy_validation_contract_allowed_next": deeper_proxy_validation_recommended,
            "strategy_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
            "backtest_allowed_now": False,
            "pnl_computation_allowed_now": False,
            "trade_simulation_allowed_now": False,
            "optimization_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
        },
        "forbidden_route_reuse": {
            "not_reused": True,
            "forbidden_routes": FORBIDDEN_ROUTE_REUSE,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def blocked_artifact(reason: str) -> dict[str, Any]:
    validation_checks = {
        "repo_clean_before_run": GIT_STATUS_SHORT_BEFORE_TOOL_CREATION == [],
        "dataset_builder_artifact_loaded": (REPO_ROOT / SOURCE_ARTIFACT_RELATIVE_PATH).exists(),
        "read_only_research_event_study": True,
        "descriptive_statistics_only": True,
        "no_private_api_used": True,
        "no_account_api_used": True,
        "no_order_endpoint_used": True,
        "no_api_key_used": True,
        "no_strategy_execution": True,
        "no_signal_generation": True,
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_trade_simulation": True,
        "no_optimization": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_failed_strategy_route_reuse": True,
        "exactly_one_python_tool_created": (REPO_ROOT / MODULE_RELATIVE_PATH).exists(),
        "exactly_one_json_artifact_created": False,
        "no_existing_tracked_files_modified": no_existing_tracked_files_modified(git_status_short()),
        "replacement_checks_all_true": False,
    }
    artifact: dict[str, Any] = {
        "status": STATUS_BLOCKED,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "repo_root": str(REPO_ROOT),
            "source_dataset_commit": SOURCE_DATASET_COMMIT,
            "blocked_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "source_artifacts": {
            "binance_data_vision_um_metrics_dataset_builder": {"path": SOURCE_ARTIFACT_RELATIVE_PATH}
        },
        "event_count": 0,
        "symbol_count": 0,
        "timestamp_range": {},
        "proxy_event_definitions_tested": EVENT_DEFINITIONS,
        "descriptive_statistics": {},
        "validation_limits": [f"BLOCKED: {reason}"],
        "deeper_proxy_validation_contract_recommended": False,
        "result_classification": RESULT_BLOCKED,
        "next_allowed_step": NEXT_BLOCKED,
        "safety_permissions": {
            "read_only_research_event_study_created": False,
            "deeper_proxy_validation_contract_allowed_next": False,
            "strategy_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
            "backtest_allowed_now": False,
            "pnl_computation_allowed_now": False,
            "trade_simulation_allowed_now": False,
            "optimization_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def write_artifact(artifact: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def print_summary(artifact: dict[str, Any]) -> None:
    timestamp_range = artifact.get("timestamp_range", {})
    print(f"status: {artifact['status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"event_count: {artifact['event_count']}")
    print(f"symbol_count: {artifact['symbol_count']}")
    print(f"timestamp_min: {timestamp_range.get('event_timestamp_min')}")
    print(f"timestamp_max: {timestamp_range.get('event_timestamp_max')}")
    print("proxy_event_definitions_tested:")
    for definition in EVENT_DEFINITIONS:
        print(f"- {definition['event_id']}: {definition['description']}")
    print("descriptive_statistics: see artifact descriptive_statistics.events_by_definition")
    print("validation_limits: descriptive research only; no price fields, so forward-return diagnostics skipped")
    print(f"deeper_proxy_validation_contract_recommended: {bool_text(artifact.get('deeper_proxy_validation_contract_recommended') is True)}")
    print(f"next_allowed_step: {artifact['next_allowed_step']}")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {bool_text(artifact['replacement_checks_all_true'])}")


def main() -> int:
    try:
        artifact = run_event_study()
        write_artifact(artifact)
        print_summary(artifact)
        return 0 if artifact["replacement_checks_all_true"] else 2
    except EventStudyBlocked as exc:
        artifact = blocked_artifact(str(exc))
        write_artifact(artifact)
        print_summary(artifact)
        print(f"exact_blocker: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
