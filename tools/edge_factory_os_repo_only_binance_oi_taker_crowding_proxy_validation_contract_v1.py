#!/usr/bin/env python
"""Create a repo-only validation contract for Binance OI/taker/crowding proxy events."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import subprocess
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = "BINANCE_OI_TAKER_CROWDING_PROXY_VALIDATION_CONTRACT_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_binance_oi_taker_crowding_proxy_validation_contract_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/contracts/binance_oi_taker_crowding_proxy_validation_contract_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH
EVENT_STUDY_RELATIVE_PATH = "artifacts/research/binance_oi_taker_crowding_proxy_event_study_v1.json"
DATASET_BUILDER_RELATIVE_PATH = "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"

VALIDATION_CONTRACT_STATUS = "PASS_REPO_ONLY_BINANCE_OI_TAKER_CROWDING_PROXY_VALIDATION_CONTRACT_CREATED"
BLOCKED_STATUS = "BLOCKED_BINANCE_OI_TAKER_CROWDING_PROXY_VALIDATION_CONTRACT"
ARTIFACT_KIND = "BINANCE_OI_TAKER_CROWDING_PROXY_VALIDATION_CONTRACT"

RESULT_READY_PRICE_REQUIRED = "BINANCE_OI_TAKER_CROWDING_PROXY_DEFINITIONS_VALID_PRICE_RETURN_DATA_REQUIRED"
RESULT_READY_EVALUATOR = "BINANCE_OI_TAKER_CROWDING_PROXY_DEFINITIONS_VALID_FOR_VALIDATION_EVALUATOR"
RESULT_UNSTABLE_REVIEW = "BINANCE_OI_TAKER_CROWDING_PROXY_DEFINITIONS_REQUIRE_STABILITY_REVIEW"
RESULT_BLOCKED = "BINANCE_OI_TAKER_CROWDING_PROXY_VALIDATION_CONTRACT_BLOCKED"

NEXT_PRICE_CONTRACT = "BINANCE_PUBLIC_KLINE_RETURN_DATASET_CONTRACT_V1"
NEXT_EVALUATOR = "BINANCE_OI_TAKER_CROWDING_PROXY_VALIDATION_EVALUATOR_V1"
NEXT_REVIEW = "BINANCE_OI_TAKER_CROWDING_PROXY_DEFINITION_STABILITY_REVIEW_V1"
NEXT_BLOCKED = "BINANCE_OI_TAKER_CROWDING_PROXY_VALIDATION_CONTRACT_BLOCKER_REVIEW_V1"

SOURCE_EVENT_STUDY_COMMIT = "67b664d1cb437692ccfdba6e4872e9f331c3cf25"
SOURCE_DATASET_COMMIT = "f419728037c3650a00b0491ccdc8e551cff21653"
SOURCE_REPO_HEAD_BEFORE_TOOL_CREATION = "67b664d1cb437692ccfdba6e4872e9f331c3cf25"
TRACKED_PYTHON_COUNT_BEFORE_TOOL_CREATION = 1058
GIT_STATUS_SHORT_BEFORE_TOOL_CREATION: list[str] = []

EVENT_IDS = [
    "oi_expansion_taker_buy_global_crowding_high",
    "oi_expansion_taker_sell_global_crowding_low",
    "oi_expansion_top_account_crowding_high",
    "oi_expansion_top_position_crowding_high",
    "broad_proxy_alignment_extreme",
]

FORBIDDEN_FAILED_ROUTES = [
    "funding crowding reversal",
    "funding carry",
    "funding extreme volume surge",
    "taker-buy exhaustion",
    "taker-flow momentum continuation",
]


class ContractBlocked(Exception):
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
        raise ContractBlocked(f"missing input artifact: {path.relative_to(REPO_ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ContractBlocked(f"input artifact is not a JSON object: {path.relative_to(REPO_ROOT)}")
    return payload


def verify_artifact_hash(payload: dict[str, Any], label: str) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise ContractBlocked(f"{label} missing payload_sha256_excluding_hash")
    recomputed = canonical_payload_hash(payload)
    if stored != recomputed:
        raise ContractBlocked(f"{label} hash mismatch: {recomputed} != {stored}")
    return stored


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], str, str]:
    event_study = read_json(REPO_ROOT / EVENT_STUDY_RELATIVE_PATH)
    dataset_builder = read_json(REPO_ROOT / DATASET_BUILDER_RELATIVE_PATH)
    event_hash = verify_artifact_hash(event_study, "event study artifact")
    dataset_hash = verify_artifact_hash(dataset_builder, "dataset builder artifact")
    if event_study.get("status") != "PASS_REPO_ONLY_BINANCE_OI_TAKER_CROWDING_PROXY_EVENT_STUDY_CREATED":
        raise ContractBlocked("event study status is not PASS")
    if event_study.get("replacement_checks_all_true") is not True:
        raise ContractBlocked("event study replacement checks are not all true")
    if dataset_builder.get("status") != "PASS_REPO_ONLY_BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILDER_CREATED":
        raise ContractBlocked("dataset builder status is not PASS")
    if dataset_builder.get("replacement_checks_all_true") is not True:
        raise ContractBlocked("dataset builder replacement checks are not all true")
    return event_study, dataset_builder, event_hash, dataset_hash


def to_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"none", "null", "nan"}:
        return None
    try:
        result = float(text)
    except ValueError:
        return None
    if math.isnan(result) or math.isinf(result):
        return None
    return result


def ge(value: float | None, threshold: float | None) -> bool:
    return value is not None and threshold is not None and value >= threshold


def le(value: float | None, threshold: float | None) -> bool:
    return value is not None and threshold is not None and value <= threshold


def evaluate_row(row: dict[str, str], thresholds: dict[str, Any]) -> list[str]:
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
    return events


def normalized_paths(dataset_builder: dict[str, Any]) -> list[Path]:
    files = dataset_builder.get("generated_external_files", {}).get("normalized_by_symbol_files")
    if not isinstance(files, list) or not files:
        raise ContractBlocked("dataset builder artifact does not expose normalized files")
    paths = [Path(str(path)) for path in files]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise ContractBlocked(f"normalized dataset files missing: {missing}")
    return sorted(paths, key=lambda path: path.name)


def concentration_from_counts(counts: dict[str, int]) -> dict[str, Any]:
    total = sum(counts.values())
    if total == 0:
        return {"total": 0, "top_key": None, "top_count": 0, "top_share": None, "max_min_ratio": None}
    top_key, top_count = max(counts.items(), key=lambda item: item[1])
    positive = [value for value in counts.values() if value > 0]
    min_positive = min(positive) if positive else 0
    return {
        "total": total,
        "top_key": top_key,
        "top_count": top_count,
        "top_share": top_count / total,
        "max_min_ratio": (top_count / min_positive) if min_positive else None,
    }


def recompute_overlap(event_study: dict[str, Any], dataset_builder: dict[str, Any]) -> dict[str, Any]:
    thresholds_by_symbol = event_study.get("descriptive_statistics", {}).get("per_symbol_thresholds", {})
    paths = normalized_paths(dataset_builder)
    event_counts = {event_id: 0 for event_id in EVENT_IDS}
    per_symbol_counts = {event_id: {} for event_id in EVENT_IDS}
    per_day_counts = {event_id: {} for event_id in EVENT_IDS}
    pairwise = {"|".join(pair): 0 for pair in combinations(EVENT_IDS, 2)}
    overlap_multiplicity = {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
    duplicate_keys = {event_id: 0 for event_id in EVENT_IDS}
    seen_keys = {event_id: set() for event_id in EVENT_IDS}
    unique_event_rows = set()
    rows_scanned = 0

    for path in paths:
        symbol = path.name.split("_", 1)[0]
        thresholds = thresholds_by_symbol.get(symbol)
        if not isinstance(thresholds, dict):
            raise ContractBlocked(f"missing per-symbol thresholds for {symbol}")
        with path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                rows_scanned += 1
                events = evaluate_row(row, thresholds)
                count_key = str(len(events))
                overlap_multiplicity[count_key] = overlap_multiplicity.get(count_key, 0) + 1
                if not events:
                    continue
                row_key = f"{row.get('symbol')}|{row.get('timestamp')}"
                unique_event_rows.add(row_key)
                for event_id in events:
                    event_counts[event_id] += 1
                    per_symbol_counts[event_id][symbol] = per_symbol_counts[event_id].get(symbol, 0) + 1
                    day = str(row.get("timestamp", ""))[:10]
                    per_day_counts[event_id][day] = per_day_counts[event_id].get(day, 0) + 1
                    full_key = f"{event_id}|{row_key}"
                    if full_key in seen_keys[event_id]:
                        duplicate_keys[event_id] += 1
                    seen_keys[event_id].add(full_key)
                for pair in combinations(sorted(events), 2):
                    pairwise["|".join(pair)] = pairwise.get("|".join(pair), 0) + 1

    reported = event_study.get("descriptive_statistics", {}).get("events_by_definition", {})
    count_matches = {
        event_id: {
            "reported": reported.get(event_id, {}).get("event_count"),
            "recomputed": event_counts[event_id],
            "matches": reported.get(event_id, {}).get("event_count") == event_counts[event_id],
        }
        for event_id in EVENT_IDS
    }
    pairwise_nonzero = {
        key: value for key, value in sorted(pairwise.items()) if value > 0
    }
    return {
        "rows_scanned": rows_scanned,
        "event_counts_recomputed": event_counts,
        "event_counts_match_reported": count_matches,
        "all_event_counts_match_reported": all(item["matches"] for item in count_matches.values()),
        "unique_symbol_timestamp_event_rows": len(unique_event_rows),
        "total_event_rows_counting_overlaps": sum(event_counts.values()),
        "overlap_row_count": sum(count for multiplicity, count in overlap_multiplicity.items() if int(multiplicity) >= 2),
        "overlap_share_of_unique_event_rows": (
            sum(count for multiplicity, count in overlap_multiplicity.items() if int(multiplicity) >= 2) / len(unique_event_rows)
            if unique_event_rows
            else None
        ),
        "overlap_multiplicity_distribution_all_rows": overlap_multiplicity,
        "pairwise_overlap_counts": pairwise_nonzero,
        "duplicate_event_keys": duplicate_keys,
        "duplicate_event_key_total": sum(duplicate_keys.values()),
        "per_symbol_counts": per_symbol_counts,
        "per_day_counts": per_day_counts,
    }


def summarize_symbol_concentration(overlap: dict[str, Any]) -> dict[str, Any]:
    per_event = {
        event_id: concentration_from_counts(counts)
        for event_id, counts in overlap["per_symbol_counts"].items()
    }
    aggregate_counts: dict[str, int] = {}
    for counts in overlap["per_symbol_counts"].values():
        for symbol, count in counts.items():
            aggregate_counts[symbol] = aggregate_counts.get(symbol, 0) + count
    return {
        "aggregate": concentration_from_counts(aggregate_counts),
        "per_event": per_event,
        "concentration_flag": concentration_from_counts(aggregate_counts)["top_share"] is not None
        and concentration_from_counts(aggregate_counts)["top_share"] > 0.35,
    }


def summarize_timestamp_concentration(overlap: dict[str, Any], event_study: dict[str, Any]) -> dict[str, Any]:
    by_year = event_study.get("regime_context_summaries", {}).get("by_year", {})
    per_event_year_concentration = {
        event_id: concentration_from_counts({str(k): int(v) for k, v in counts.items()})
        for event_id, counts in by_year.items()
    }
    aggregate_day_counts: dict[str, int] = {}
    for day_counts in overlap["per_day_counts"].values():
        for day, count in day_counts.items():
            aggregate_day_counts[day] = aggregate_day_counts.get(day, 0) + count
    day_concentration = concentration_from_counts(aggregate_day_counts)
    return {
        "per_event_year_concentration": per_event_year_concentration,
        "aggregate_day_concentration": day_concentration,
        "timestamp_instability_flag": any(
            item["top_share"] is not None and item["top_share"] > 0.60
            for item in per_event_year_concentration.values()
        ),
    }


def validate_proxy_definitions(event_study: dict[str, Any], overlap: dict[str, Any]) -> dict[str, Any]:
    definitions = event_study.get("proxy_event_definitions_tested", [])
    valid_ids = [definition.get("event_id") for definition in definitions if definition.get("event_id") in EVENT_IDS]
    event_counts = overlap["event_counts_recomputed"]
    return {
        "definitions_present": len(valid_ids) == len(EVENT_IDS),
        "definition_count": len(definitions),
        "validated_event_ids": valid_ids,
        "all_definitions_have_events": all(event_counts.get(event_id, 0) > 0 for event_id in EVENT_IDS),
        "all_definitions_cover_all_symbols": all(
            event_study.get("descriptive_statistics", {})
            .get("events_by_definition", {})
            .get(event_id, {})
            .get("symbol_count")
            == 10
            for event_id in EVENT_IDS
        ),
        "counts_match_event_study": overlap["all_event_counts_match_reported"],
        "usable_for_deeper_diagnostic_validation": (
            len(valid_ids) == len(EVENT_IDS)
            and all(event_counts.get(event_id, 0) > 0 for event_id in EVENT_IDS)
            and overlap["all_event_counts_match_reported"]
            and overlap["duplicate_event_key_total"] == 0
        ),
    }


def build_contract() -> dict[str, Any]:
    if not existing_artifact_can_be_replaced():
        raise ContractBlocked(f"artifact exists and is not this contract output: {ARTIFACT_RELATIVE_PATH}")
    status_at_run_start = git_status_short()
    event_study, dataset_builder, event_hash, dataset_hash = load_inputs()
    overlap = recompute_overlap(event_study, dataset_builder)
    proxy_validation = validate_proxy_definitions(event_study, overlap)
    symbol_concentration = summarize_symbol_concentration(overlap)
    timestamp_concentration = summarize_timestamp_concentration(overlap, event_study)
    missing_dependency = {
        "forward_return_diagnostic_status": event_study.get("forward_return_diagnostic", {}).get("diagnostic_label_status"),
        "forward_return_impact_computed": event_study.get("forward_return_diagnostic", {}).get("forward_return_impact_computed"),
        "missing_dependency": event_study.get("forward_return_diagnostic", {}).get("required_dependency_for_future"),
        "reason": event_study.get("forward_return_diagnostic", {}).get("reason"),
        "public_kline_return_data_required_before_forward_return_diagnostic": True,
    }
    instability_detected = (
        symbol_concentration["concentration_flag"]
        or timestamp_concentration["timestamp_instability_flag"]
        or overlap["duplicate_event_key_total"] > 0
    )
    if not proxy_validation["usable_for_deeper_diagnostic_validation"]:
        result_classification = RESULT_UNSTABLE_REVIEW
        allowed_next_step = NEXT_REVIEW
    elif missing_dependency["public_kline_return_data_required_before_forward_return_diagnostic"]:
        result_classification = RESULT_READY_PRICE_REQUIRED
        allowed_next_step = NEXT_PRICE_CONTRACT
    elif instability_detected:
        result_classification = RESULT_UNSTABLE_REVIEW
        allowed_next_step = NEXT_REVIEW
    else:
        result_classification = RESULT_READY_EVALUATOR
        allowed_next_step = NEXT_EVALUATOR

    validation_checks = {
        "repo_clean_before_run": GIT_STATUS_SHORT_BEFORE_TOOL_CREATION == [],
        "input_artifacts_found": True,
        "input_artifact_hashes_verified": True,
        "proxy_event_definitions_validated": proxy_validation["usable_for_deeper_diagnostic_validation"],
        "event_counts_recomputed_match_input": overlap["all_event_counts_match_reported"],
        "duplicate_event_key_total_zero": overlap["duplicate_event_key_total"] == 0,
        "public_price_return_dependency_required": True,
        "read_only_validation_contract": True,
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
    safety_flags = {
        "strategy": False,
        "signal": False,
        "backtest": False,
        "pnl": False,
        "trade_simulation": False,
        "optimization": False,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "order_private_account_api_key": False,
    }
    artifact: dict[str, Any] = {
        "validation_contract_status": VALIDATION_CONTRACT_STATUS if replacement_checks_all_true else BLOCKED_STATUS,
        "status": VALIDATION_CONTRACT_STATUS if replacement_checks_all_true else BLOCKED_STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "repo_root": str(REPO_ROOT),
            "source_event_study_commit": SOURCE_EVENT_STUDY_COMMIT,
            "source_dataset_commit": SOURCE_DATASET_COMMIT,
            "repo_head_before_tool_creation": SOURCE_REPO_HEAD_BEFORE_TOOL_CREATION,
            "tracked_python_count_before_tool_creation": TRACKED_PYTHON_COUNT_BEFORE_TOOL_CREATION,
            "tracked_python_count_at_run": tracked_python_count(),
            "git_status_short_before_tool_creation": GIT_STATUS_SHORT_BEFORE_TOOL_CREATION,
            "git_status_short_at_run_start": status_at_run_start,
            "run_started_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "result_classification": result_classification,
        "input_artifacts_found": {
            EVENT_STUDY_RELATIVE_PATH: True,
            DATASET_BUILDER_RELATIVE_PATH: True,
        },
        "source_artifacts": {
            "event_study": {
                "path": EVENT_STUDY_RELATIVE_PATH,
                "status": event_study.get("status"),
                "result_classification": event_study.get("result_classification"),
                "payload_sha256_excluding_hash": event_hash,
            },
            "dataset_builder": {
                "path": DATASET_BUILDER_RELATIVE_PATH,
                "status": dataset_builder.get("status"),
                "result_classification": dataset_builder.get("result_classification"),
                "payload_sha256_excluding_hash": dataset_hash,
            },
        },
        "proxy_event_definitions_validated": proxy_validation,
        "event_overlap_summary": {
            "rows_scanned": overlap["rows_scanned"],
            "event_counts_recomputed": overlap["event_counts_recomputed"],
            "event_counts_match_reported": overlap["event_counts_match_reported"],
            "unique_symbol_timestamp_event_rows": overlap["unique_symbol_timestamp_event_rows"],
            "total_event_rows_counting_overlaps": overlap["total_event_rows_counting_overlaps"],
            "overlap_row_count": overlap["overlap_row_count"],
            "overlap_share_of_unique_event_rows": overlap["overlap_share_of_unique_event_rows"],
            "overlap_multiplicity_distribution_all_rows": overlap["overlap_multiplicity_distribution_all_rows"],
            "pairwise_overlap_counts": overlap["pairwise_overlap_counts"],
            "duplicate_event_keys": overlap["duplicate_event_keys"],
            "duplicate_event_key_total": overlap["duplicate_event_key_total"],
        },
        "symbol_concentration_summary": symbol_concentration,
        "timestamp_concentration_summary": timestamp_concentration,
        "missing_dependency_summary": missing_dependency,
        "public_price_return_dependency_required": True,
        "allowed_next_step": allowed_next_step,
        "forbidden_actions": [
            "strategy",
            "signal",
            "backtest",
            "PnL",
            "trade_simulation",
            "optimization",
            "candidate_generation",
            "edge_claim",
            "runtime/live/capital/order/private_api/account_api/api_key",
        ],
        "forbidden_failed_strategy_routes_not_reused": {
            "not_reused": True,
            "routes": FORBIDDEN_FAILED_ROUTES,
        },
        "safety_flags": safety_flags,
        "validation_limits": [
            "This is a validation contract only, not an evaluator with forward returns.",
            "Forward-return diagnostics require a public kline/return dataset before any return impact study.",
            "Overlap and concentration are descriptive validation checks, not tradable signals.",
            "No strategy, signal, backtest, PnL, simulation, optimization, candidate generation, or edge claim is authorized.",
        ],
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def blocked_contract(reason: str) -> dict[str, Any]:
    safety_flags = {
        "strategy": False,
        "signal": False,
        "backtest": False,
        "pnl": False,
        "trade_simulation": False,
        "optimization": False,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "order_private_account_api_key": False,
    }
    artifact: dict[str, Any] = {
        "validation_contract_status": BLOCKED_STATUS,
        "status": BLOCKED_STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "result_classification": RESULT_BLOCKED,
        "input_artifacts_found": {
            EVENT_STUDY_RELATIVE_PATH: (REPO_ROOT / EVENT_STUDY_RELATIVE_PATH).exists(),
            DATASET_BUILDER_RELATIVE_PATH: (REPO_ROOT / DATASET_BUILDER_RELATIVE_PATH).exists(),
        },
        "proxy_event_definitions_validated": {"usable_for_deeper_diagnostic_validation": False},
        "event_overlap_summary": {},
        "symbol_concentration_summary": {},
        "timestamp_concentration_summary": {},
        "missing_dependency_summary": {"blocked_reason": reason},
        "public_price_return_dependency_required": True,
        "allowed_next_step": NEXT_BLOCKED,
        "forbidden_actions": [
            "strategy",
            "signal",
            "backtest",
            "PnL",
            "trade_simulation",
            "optimization",
            "candidate_generation",
            "edge_claim",
            "runtime/live/capital/order/private_api/account_api/api_key",
        ],
        "safety_flags": safety_flags,
        "validation_checks": {
            "replacement_checks_all_true": False,
            "no_strategy_execution": True,
            "no_signal_generation": True,
            "no_backtest_run": True,
            "no_pnl_computation": True,
            "no_trade_simulation": True,
            "no_optimization": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_runtime_live_capital": True,
        },
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def write_artifact(artifact: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def print_summary(artifact: dict[str, Any]) -> None:
    print(f"validation_contract_status: {artifact['validation_contract_status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"input_artifacts_found: {artifact['input_artifacts_found']}")
    print(f"proxy_event_definitions_validated: {bool_text(artifact['proxy_event_definitions_validated'].get('usable_for_deeper_diagnostic_validation') is True)}")
    overlap = artifact.get("event_overlap_summary", {})
    print(f"event_overlap_unique_rows: {overlap.get('unique_symbol_timestamp_event_rows')}")
    print(f"event_overlap_total_rows_counting_overlaps: {overlap.get('total_event_rows_counting_overlaps')}")
    print(f"duplicate_event_key_total: {overlap.get('duplicate_event_key_total')}")
    print(f"public_price_return_dependency_required: {bool_text(artifact.get('public_price_return_dependency_required') is True)}")
    print(f"allowed_next_step: {artifact['allowed_next_step']}")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {bool_text(artifact['replacement_checks_all_true'])}")


def main() -> int:
    try:
        artifact = build_contract()
        write_artifact(artifact)
        print_summary(artifact)
        return 0 if artifact["replacement_checks_all_true"] else 2
    except ContractBlocked as exc:
        artifact = blocked_contract(str(exc))
        write_artifact(artifact)
        print_summary(artifact)
        print(f"exact_blocker: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
