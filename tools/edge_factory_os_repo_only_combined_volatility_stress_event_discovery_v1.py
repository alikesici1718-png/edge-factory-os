#!/usr/bin/env python3
"""Outcome-blind combined volatility stress event discovery.

Combines two already validated volatility diagnostic event families by symbol
and timestamp overlap only. This module does not compute forward returns,
absolute returns, p-values, nulls, options metrics, PnL, strategies, signals,
or candidates.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE = "COMBINED_VOLATILITY_STRESS_EVENT_DISCOVERY_V1"
EXPECTED_HEAD = "9d1dc80a601546b00e5e5acfcdea23afe7ce4c92"
REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_combined_volatility_stress_event_discovery_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/research/combined_volatility_stress_event_discovery_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

COMBINED_THEORY_ID = "COMBINED_VOLATILITY_STRESS_EVENT"
COMPONENT_A_THEORY_ID = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT"
COMPONENT_B_THEORY_ID = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT"
OVERLAP_WINDOW_MS = 60 * 60 * 1000

RESULT_READY = "COMBINED_VOLATILITY_STRESS_EVENT_DISCOVERY_READY"
RESULT_TOO_SPARSE = "COMBINED_VOLATILITY_STRESS_EVENT_DISCOVERY_TOO_SPARSE"
RESULT_TOO_BROAD = "COMBINED_VOLATILITY_STRESS_EVENT_DISCOVERY_TOO_BROAD"
RESULT_DATA_QUALITY = "COMBINED_VOLATILITY_STRESS_EVENT_DISCOVERY_DATA_QUALITY_ATTENTION"
RESULT_FAILED = "COMBINED_VOLATILITY_STRESS_EVENT_DISCOVERY_FAILED_STOP"

NEXT_VALIDATOR = "COMBINED_VOLATILITY_STRESS_EVENT_VALIDATOR_V1"
NEXT_REVIEW = "COMBINED_VOLATILITY_STRESS_EVENT_ACCUMULATION_OR_REFINEMENT_REVIEW_V1"
NEXT_RECOVERY = "COMBINED_VOLATILITY_STRESS_EVENT_DISCOVERY_RECOVERY_REVIEW_V1"

COMPONENT_A_SLOTS = {
    "best_oi_expansion_volatility_expansion_definition": "expansion + volatility expansion",
    "best_oi_expansion_volatility_compression_break_definition": "expansion + volatility compression break",
}
COMPONENT_B_SLOT = "optional_account_position_divergence_resolution_candidate"
COMPONENT_B_LABEL = "account/position divergence resolution"

INPUT_RELATIVE_PATHS = [
    "artifacts/research/oi_shock_with_realized_volatility_regime_shift_event_discovery_v1.json",
    "artifacts/research/oi_shock_with_realized_volatility_regime_shift_event_validator_v1.json",
    "artifacts/research/oi_shock_with_realized_volatility_regime_shift_robustness_evaluator_v1.json",
    "artifacts/contracts/oi_shock_with_realized_volatility_regime_shift_pre_registered_independent_validation_contract_v1.json",
    "artifacts/research/oi_shock_with_realized_volatility_regime_shift_pre_registered_independent_validation_runner_v1.json",
    "artifacts/research/long_short_ratio_extreme_normalization_event_discovery_v1.json",
    "artifacts/research/long_short_ratio_extreme_normalization_event_validator_v1.json",
    "artifacts/research/long_short_ratio_extreme_normalization_volatility_robustness_evaluator_v1.json",
    "artifacts/contracts/long_short_ratio_extreme_normalization_pre_registered_independent_validation_contract_v1.json",
    "artifacts/research/long_short_ratio_extreme_normalization_pre_registered_independent_validation_runner_v1.json",
    "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json",
    "artifacts/research/binance_public_kline_forward_return_diagnostic_v1.json",
]

OI_SHOCK_DISCOVERY_TOOL = (
    REPO_ROOT
    / "tools/edge_factory_os_repo_only_oi_shock_with_realized_volatility_regime_shift_event_discovery_v1.py"
)
OI_SHOCK_DIAGNOSTIC_TOOL = (
    REPO_ROOT
    / "tools/edge_factory_os_repo_only_oi_shock_with_realized_volatility_regime_shift_forward_return_diagnostic_v1.py"
)
LSR_DISCOVERY_TOOL = (
    REPO_ROOT
    / "tools/edge_factory_os_repo_only_long_short_ratio_extreme_normalization_event_discovery_v1.py"
)
LSR_DIAGNOSTIC_TOOL = (
    REPO_ROOT
    / "tools/edge_factory_os_repo_only_long_short_ratio_extreme_normalization_forward_return_diagnostic_v1.py"
)

FORBIDDEN_ACTIONS_CONFIRMED_FALSE = {
    "forward_returns": False,
    "absolute_returns": False,
    "p_values": False,
    "null_validation": False,
    "backtest": False,
    "pnl": False,
    "options_chain_lookup": False,
    "implied_volatility_lookup": False,
    "implied_move_calculation": False,
    "strategy": False,
    "signal": False,
    "candidate_generation": False,
    "release": False,
    "runtime_live_capital_order_private_account_api_key": False,
    "overlap_window_tuning": False,
    "component_event_definition_change": False,
    "outcome_use_2023_2025": False,
    "outcome_use_2026": False,
}


class DiscoveryBlocked(RuntimeError):
    """Raised when the frozen discovery cannot safely complete."""


def run_git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True, stderr=subprocess.STDOUT).strip()


def git_lines(args: list[str]) -> list[str]:
    output = run_git(args)
    return [line for line in output.splitlines() if line.strip()]


def recovery_audit() -> dict[str, Any]:
    current_head = run_git(["rev-parse", "HEAD"])
    branch = run_git(["branch", "--show-current"])
    try:
        core_longpaths = run_git(["config", "--local", "--get", "core.longpaths"])
    except subprocess.CalledProcessError:
        core_longpaths = "<unset>"
    porcelain = git_lines(["status", "--porcelain"])
    staged = git_lines(["diff", "--name-only", "--cached"])
    modified = git_lines(["diff", "--name-only"])
    untracked = git_lines(["ls-files", "--others", "--exclude-standard"])
    deleted = git_lines(["ls-files", "--deleted"])
    allowed_in_progress = {
        MODULE_RELATIVE_PATH,
        MODULE_RELATIVE_PATH.replace("/", "\\"),
        ARTIFACT_RELATIVE_PATH,
        ARTIFACT_RELATIVE_PATH.replace("/", "\\"),
    }
    dirty_paths: set[str] = set(modified + untracked + deleted)
    for line in porcelain:
        if len(line) >= 4:
            dirty_paths.add(line[3:])
    head_matches = current_head == EXPECTED_HEAD
    clean_or_output_only = (
        head_matches
        and not staged
        and all(path in allowed_in_progress for path in dirty_paths)
        and all((line.startswith("?? ") and line[3:] in allowed_in_progress) for line in porcelain)
    )
    recovery_decision = "RECOVERY_AUDIT_CLEAN_CONTINUE" if clean_or_output_only else "RECOVERY_AUDIT_STOP"
    return {
        "current_head": current_head,
        "expected_head": EXPECTED_HEAD,
        "branch": branch,
        "core_longpaths_value": core_longpaths,
        "git_status_porcelain": porcelain,
        "staged_files": staged,
        "modified_tracked_files": modified,
        "untracked_files": untracked,
        "deleted_files": deleted,
        "head_matches_expected": head_matches,
        "recovery_decision": recovery_decision,
        "recovery_audit_status": "PASS" if recovery_decision.endswith("CONTINUE") else "STOP",
    }


def print_recovery_audit(audit: dict[str, Any]) -> None:
    print(f"current HEAD: {audit['current_head']}")
    print(f"expected HEAD: {audit['expected_head']}")
    print(f"branch: {audit['branch']}")
    print(f"core.longpaths value: {audit['core_longpaths_value']}")
    print(f"git status porcelain: {audit['git_status_porcelain']}")
    print(f"staged files: {audit['staged_files']}")
    print(f"modified tracked files: {audit['modified_tracked_files']}")
    print(f"untracked files: {audit['untracked_files']}")
    print(f"deleted files: {audit['deleted_files']}")
    print(f"recovery decision: {audit['recovery_decision']}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for rel_path in INPUT_RELATIVE_PATHS:
        path = REPO_ROOT / rel_path
        if not path.exists():
            raise DiscoveryBlocked(f"missing required input artifact: {rel_path}")
        hashes[rel_path] = sha256_file(path)
    return hashes


def load_json(rel_path: str) -> dict[str, Any]:
    with (REPO_ROOT / rel_path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise DiscoveryBlocked(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def iso_from_ms(ms_value: int) -> str:
    return datetime.fromtimestamp(ms_value / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def month_from_ms(ms_value: int) -> str:
    return datetime.fromtimestamp(ms_value / 1000, timezone.utc).strftime("%Y-%m")


def assert_input_chain(inputs: dict[str, dict[str, Any]]) -> list[str]:
    blockers: list[str] = []
    oi_discovery = inputs["oi_discovery"]
    oi_validator = inputs["oi_validator"]
    oi_evaluator = inputs["oi_evaluator"]
    oi_contract = inputs["oi_contract"]
    oi_independent = inputs["oi_independent"]
    lsr_discovery = inputs["lsr_discovery"]
    lsr_validator = inputs["lsr_validator"]
    lsr_evaluator = inputs["lsr_evaluator"]
    lsr_contract = inputs["lsr_contract"]
    lsr_independent = inputs["lsr_independent"]
    if oi_discovery.get("result_classification") != "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_EVENT_DISCOVERY_READY":
        blockers.append("OI_SHOCK_DISCOVERY_NOT_READY")
    if oi_validator.get("result_classification") not in {
        "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_EVENT_VALIDATOR_PASS",
        "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_EVENT_VALIDATOR_PASS_WITH_ATTENTION",
    }:
        blockers.append("OI_SHOCK_VALIDATOR_NOT_PASSING")
    if oi_evaluator.get("result_classification") != (
        "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_ROBUSTNESS_EVALUATOR_PROMISING_VOLATILITY_DIAGNOSTIC_ONLY"
    ):
        blockers.append("OI_SHOCK_ROBUSTNESS_EVALUATOR_NOT_PROMISING_DIAGNOSTIC_ONLY")
    if oi_contract.get("result_classification") != (
        "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_READY"
    ):
        blockers.append("OI_SHOCK_CONTRACT_NOT_READY")
    if oi_independent.get("result_classification") not in {
        "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_INDEPENDENT_VALIDATION_INCONCLUSIVE_INSUFFICIENT_SAMPLE",
        "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_INDEPENDENT_VALIDATION_PASS_DIAGNOSTIC_ONLY",
    }:
        blockers.append("OI_SHOCK_INDEPENDENT_VALIDATION_UNEXPECTED_STATE")
    if lsr_discovery.get("result_classification") != "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_DISCOVERY_READY":
        blockers.append("LSR_DISCOVERY_NOT_READY")
    if lsr_validator.get("result_classification") not in {
        "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_VALIDATOR_PASS",
        "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_VALIDATOR_PASS_WITH_ATTENTION",
    }:
        blockers.append("LSR_VALIDATOR_NOT_PASSING")
    if lsr_evaluator.get("result_classification") != (
        "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_EVALUATOR_PROMISING_DIAGNOSTIC_ONLY"
    ):
        blockers.append("LSR_ROBUSTNESS_EVALUATOR_NOT_PROMISING_DIAGNOSTIC_ONLY")
    if lsr_contract.get("result_classification") != (
        "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_READY"
    ):
        blockers.append("LSR_CONTRACT_NOT_READY")
    if lsr_independent.get("result_classification") not in {
        "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_INDEPENDENT_VALIDATION_INCONCLUSIVE_INSUFFICIENT_SAMPLE",
        "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_INDEPENDENT_VALIDATION_PASS_DIAGNOSTIC_ONLY",
    }:
        blockers.append("LSR_INDEPENDENT_VALIDATION_UNEXPECTED_STATE")
    for name, artifact in inputs.items():
        for flag in ("strategy_allowed", "signal_allowed", "candidate_generation_allowed", "release_allowed"):
            if flag in artifact and artifact.get(flag) is not False:
                blockers.append(f"{name.upper()}_{flag.upper()}_NOT_FALSE")
    return blockers


def compact_source_reconstruction(reconstruction: dict[str, Any]) -> dict[str, Any]:
    archive_summary = reconstruction.get("archive_summary", {})
    archive_records = archive_summary.get("archive_records", []) if isinstance(archive_summary, dict) else []
    missing_records = [
        {
            "symbol": record.get("symbol"),
            "year": record.get("year"),
            "month": record.get("month"),
            "available": record.get("available"),
            "reason": record.get("reason"),
        }
        for record in archive_records
        if isinstance(record, dict) and record.get("available") is False
    ]
    compact = {
        "status": reconstruction.get("status"),
        "expected_counts": reconstruction.get("expected_counts"),
        "actual_counts": reconstruction.get("actual_counts"),
        "reconstruction_counters": reconstruction.get("reconstruction_counters"),
    }
    if isinstance(archive_summary, dict):
        compact["archive_summary"] = {
            "archive_record_count": len(archive_records),
            "missing_archive_records": missing_records,
            "raw_archive_paths_embedded": False,
        }
    if "selected_secondary_definitions_not_used_as_primary" in reconstruction:
        compact["selected_secondary_definitions_not_used_as_primary"] = reconstruction[
            "selected_secondary_definitions_not_used_as_primary"
        ]
    return compact


def load_inputs() -> dict[str, dict[str, Any]]:
    inputs = {
        "oi_discovery": load_json(INPUT_RELATIVE_PATHS[0]),
        "oi_validator": load_json(INPUT_RELATIVE_PATHS[1]),
        "oi_evaluator": load_json(INPUT_RELATIVE_PATHS[2]),
        "oi_contract": load_json(INPUT_RELATIVE_PATHS[3]),
        "oi_independent": load_json(INPUT_RELATIVE_PATHS[4]),
        "lsr_discovery": load_json(INPUT_RELATIVE_PATHS[5]),
        "lsr_validator": load_json(INPUT_RELATIVE_PATHS[6]),
        "lsr_evaluator": load_json(INPUT_RELATIVE_PATHS[7]),
        "lsr_contract": load_json(INPUT_RELATIVE_PATHS[8]),
        "lsr_independent": load_json(INPUT_RELATIVE_PATHS[9]),
        "dataset": load_json(INPUT_RELATIVE_PATHS[10]),
        "kline": load_json(INPUT_RELATIVE_PATHS[11]),
    }
    blockers = assert_input_chain(inputs)
    if blockers:
        raise DiscoveryBlocked("INPUT_CHAIN_BLOCKED:" + ",".join(blockers))
    return inputs


def reconstruct_components(inputs: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    oi_shock = load_module(OI_SHOCK_DISCOVERY_TOOL, "combined_oi_shock_event_discovery")
    oi_diag = load_module(OI_SHOCK_DIAGNOSTIC_TOOL, "combined_oi_shock_reconstruction")
    lsr = load_module(LSR_DISCOVERY_TOOL, "combined_lsr_event_discovery")
    lsr_diag = load_module(LSR_DIAGNOSTIC_TOOL, "combined_lsr_reconstruction")
    oi_events_by_slot, _, oi_reconstruction = oi_diag.reconstruct_events(
        inputs["dataset"], inputs["kline"], inputs["oi_discovery"], oi_shock
    )
    lsr_events_by_slot, _, lsr_reconstruction = lsr_diag.reconstruct_events(
        inputs["dataset"], inputs["kline"], inputs["lsr_discovery"], lsr
    )
    component_a_events: list[dict[str, Any]] = []
    for slot, subtype in COMPONENT_A_SLOTS.items():
        for index, event in enumerate(oi_events_by_slot.get(slot, [])):
            component_a_events.append(
                {
                    **event,
                    "component_event_id": f"A::{slot}::{event['symbol']}::{event['ts_ms']}::{index}",
                    "component_slot": slot,
                    "component_subtype": subtype,
                    "component_theory_id": COMPONENT_A_THEORY_ID,
                }
            )
    component_b_events = [
        {
            **event,
            "component_event_id": f"B::{COMPONENT_B_SLOT}::{event['symbol']}::{event['ts_ms']}::{index}",
            "component_slot": COMPONENT_B_SLOT,
            "component_subtype": COMPONENT_B_LABEL,
            "component_theory_id": COMPONENT_B_THEORY_ID,
        }
        for index, event in enumerate(lsr_events_by_slot.get(COMPONENT_B_SLOT, []))
    ]
    reconstruction = {
        "component_a": {
            "status": oi_reconstruction.get("status"),
            "selected_slots": list(COMPONENT_A_SLOTS),
            "all_reconstructed_counts": oi_reconstruction.get("actual_counts"),
            "used_count": len(component_a_events),
            "source_reconstruction": compact_source_reconstruction(oi_reconstruction),
        },
        "component_b": {
            "status": lsr_reconstruction.get("status"),
            "selected_slots": [COMPONENT_B_SLOT],
            "all_reconstructed_counts": lsr_reconstruction.get("actual_counts"),
            "used_count": len(component_b_events),
            "source_reconstruction": compact_source_reconstruction(lsr_reconstruction),
        },
        "current_prior_data_only": True,
        "forward_return_fields_used": False,
        "options_fields_used": False,
    }
    return reconstruction, component_a_events, component_b_events


def build_raw_pairs(component_a: list[dict[str, Any]], component_b: list[dict[str, Any]]) -> list[dict[str, Any]]:
    b_by_symbol: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in component_b:
        b_by_symbol[event["symbol"]].append(event)
    for symbol_events in b_by_symbol.values():
        symbol_events.sort(key=lambda item: (int(item["ts_ms"]), item["component_event_id"]))
    raw_pairs: list[dict[str, Any]] = []
    for a_event in sorted(component_a, key=lambda item: (item["symbol"], int(item["ts_ms"]), item["component_event_id"])):
        a_ts = int(a_event["ts_ms"])
        for b_event in b_by_symbol.get(a_event["symbol"], []):
            b_ts = int(b_event["ts_ms"])
            distance_ms = abs(a_ts - b_ts)
            if distance_ms > OVERLAP_WINDOW_MS:
                continue
            combined_ms = max(a_ts, b_ts)
            if a_ts == b_ts:
                order = "same_timestamp"
            elif a_ts < b_ts:
                order = "component_a_before_component_b"
            else:
                order = "component_b_before_component_a"
            raw_pairs.append(
                {
                    "symbol": a_event["symbol"],
                    "component_a_event_id": a_event["component_event_id"],
                    "component_b_event_id": b_event["component_event_id"],
                    "component_a_time_ms": a_ts,
                    "component_b_time_ms": b_ts,
                    "component_a_time": a_event["timestamp"],
                    "component_b_time": b_event["timestamp"],
                    "combined_event_time_ms": combined_ms,
                    "combined_event_time": iso_from_ms(combined_ms),
                    "month": month_from_ms(combined_ms),
                    "time_distance_minutes": distance_ms / 60_000.0,
                    "component_order": order,
                    "component_a_subtype": a_event["component_subtype"],
                    "component_b_subtype": b_event["component_subtype"],
                    "component_a_slot": a_event["component_slot"],
                    "component_b_slot": b_event["component_slot"],
                }
            )
    raw_pairs.sort(
        key=lambda item: (
            item["time_distance_minutes"],
            item["combined_event_time_ms"],
            item["component_a_time_ms"],
            item["component_b_time_ms"],
            item["symbol"],
            item["component_a_event_id"],
            item["component_b_event_id"],
        )
    )
    return raw_pairs


def deduplicate_pairs(raw_pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    used_a: set[str] = set()
    used_b: set[str] = set()
    selected: list[dict[str, Any]] = []
    for pair in raw_pairs:
        if pair["component_a_event_id"] in used_a or pair["component_b_event_id"] in used_b:
            continue
        used_a.add(pair["component_a_event_id"])
        used_b.add(pair["component_b_event_id"])
        selected.append(pair)
    selected.sort(
        key=lambda item: (
            item["combined_event_time_ms"],
            item["symbol"],
            item["time_distance_minutes"],
            item["component_a_time_ms"],
            item["component_b_time_ms"],
        )
    )
    return selected


def cooldown_count(events: list[dict[str, Any]], cooldown_hours: int) -> int:
    cooldown_ms = cooldown_hours * 60 * 60 * 1000
    last_by_symbol: dict[str, int] = {}
    kept = 0
    for event in sorted(events, key=lambda item: (item["combined_event_time_ms"], item["symbol"])):
        symbol = event["symbol"]
        ts_ms = int(event["combined_event_time_ms"])
        previous = last_by_symbol.get(symbol)
        if previous is not None and ts_ms - previous < cooldown_ms:
            continue
        last_by_symbol[symbol] = ts_ms
        kept += 1
    return kept


def concentration_summary(events: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    symbol_counts = Counter(event["symbol"] for event in events)
    month_counts = Counter(event["month"] for event in events)
    total = len(events)
    top_symbol, top_symbol_count = symbol_counts.most_common(1)[0] if symbol_counts else (None, 0)
    top_month, top_month_count = month_counts.most_common(1)[0] if month_counts else (None, 0)
    symbol_summary = {
        "unique_symbol_count": len(symbol_counts),
        "event_count_by_symbol": dict(sorted(symbol_counts.items())),
        "top_symbol": top_symbol,
        "top_symbol_count": top_symbol_count,
        "top_symbol_concentration": (top_symbol_count / total if total else None),
    }
    month_summary = {
        "unique_month_count": len(month_counts),
        "event_count_by_month": dict(sorted(month_counts.items())),
        "top_month": top_month,
        "top_month_count": top_month_count,
        "top_month_concentration": (top_month_count / total if total else None),
    }
    concentration = {
        "top_symbol": top_symbol,
        "top_symbol_concentration": symbol_summary["top_symbol_concentration"],
        "top_month": top_month,
        "top_month_concentration": month_summary["top_month_concentration"],
        "symbol_concentration_preferred_max": 0.25,
        "month_concentration_preferred_max": 0.15,
        "concentration_acceptable": (
            total > 0
            and (symbol_summary["top_symbol_concentration"] or 0.0) <= 0.25
            and (month_summary["top_month_concentration"] or 0.0) <= 0.15
        ),
    }
    return symbol_summary, month_summary, concentration


def overlap_distribution(events: list[dict[str, Any]]) -> dict[str, int]:
    buckets = Counter()
    for event in events:
        distance = float(event["time_distance_minutes"])
        if distance == 0:
            buckets["exact_same_timestamp"] += 1
        elif distance <= 15:
            buckets["within_15m"] += 1
        elif distance <= 30:
            buckets["within_30m"] += 1
        else:
            buckets["within_60m"] += 1
    return dict(sorted(buckets.items()))


def time_distance_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    values = [float(event["time_distance_minutes"]) for event in events]
    if not values:
        return {"count": 0, "mean_minutes": None, "median_minutes": None, "min_minutes": None, "max_minutes": None}
    return {
        "count": len(values),
        "mean_minutes": float(sum(values) / len(values)),
        "median_minutes": float(statistics.median(values)),
        "min_minutes": float(min(values)),
        "max_minutes": float(max(values)),
    }


def threshold_interpretation(unique_count: int) -> dict[str, Any]:
    if unique_count > 1500:
        band = "possibly_too_broad"
        interpretation = "over 1500 unique combined events; needs refinement"
    elif unique_count >= 100:
        band = "eligible"
        interpretation = ">=100 unique combined events; eligible for combined event validator if coverage/concentration are acceptable"
    elif unique_count >= 50:
        band = "attention_inconclusive"
        interpretation = "50-99 unique combined events; attention/inconclusive, likely monitor or pre-registered non-outcome refinement"
    else:
        band = "too_sparse"
        interpretation = "<50 unique combined events; too sparse for immediate diagnostic"
    return {
        "unique_combined_event_count": unique_count,
        "band": band,
        "interpretation": interpretation,
        "exceeds_100": unique_count >= 100,
        "uses_returns_or_outcomes": False,
    }


def classify(unique_count: int, concentration: dict[str, Any], symbol_summary: dict[str, Any], month_summary: dict[str, Any]) -> tuple[str, str, bool]:
    coverage_ok = symbol_summary["unique_symbol_count"] >= 8 and month_summary["unique_month_count"] >= 24
    concentration_ok = concentration["concentration_acceptable"] is True
    if unique_count > 1500:
        return RESULT_TOO_BROAD, NEXT_REVIEW, False
    if unique_count < 100:
        return RESULT_TOO_SPARSE, NEXT_REVIEW, False
    if coverage_ok and concentration_ok:
        return RESULT_READY, NEXT_VALIDATOR, True
    return RESULT_DATA_QUALITY, NEXT_REVIEW, False


def build_artifact() -> dict[str, Any]:
    audit = recovery_audit()
    print_recovery_audit(audit)
    if audit["recovery_decision"] != "RECOVERY_AUDIT_CLEAN_CONTINUE":
        raise DiscoveryBlocked(audit["recovery_decision"])
    hashes_before = input_hashes()
    inputs = load_inputs()
    reconstruction, component_a_events, component_b_events = reconstruct_components(inputs)
    raw_pairs = build_raw_pairs(component_a_events, component_b_events)
    unique_events = deduplicate_pairs(raw_pairs)
    raw_pair_count = len(raw_pairs)
    unique_count = len(unique_events)
    cooldown_counts = {
        "6h": cooldown_count(unique_events, 6),
        "12h": cooldown_count(unique_events, 12),
        "24h": cooldown_count(unique_events, 24),
    }
    symbol_summary, month_summary, concentration = concentration_summary(unique_events)
    threshold = threshold_interpretation(unique_count)
    result_classification, allowed_next_step, options_allowed_after_validator = classify(
        unique_count, concentration, symbol_summary, month_summary
    )
    component_order = Counter(event["component_order"] for event in unique_events)
    component_a_subtypes = Counter(event["component_a_subtype"] for event in unique_events)
    component_b_subtypes = Counter(event["component_b_subtype"] for event in unique_events)
    missing_summary = {
        "component_a_used_event_count": len(component_a_events),
        "component_b_used_event_count": len(component_b_events),
        "component_a_reconstruction_missing": reconstruction["component_a"]["source_reconstruction"].get("reconstruction_counters", {}).get("aggregate", {}),
        "component_b_reconstruction_missing": reconstruction["component_b"]["source_reconstruction"].get("reconstruction_counters", {}).get("aggregate", {}),
        "component_a_without_component_b_within_1h": max(0, len(component_a_events) - len({event["component_a_event_id"] for event in raw_pairs})),
        "component_b_without_component_a_within_1h": max(0, len(component_b_events) - len({event["component_b_event_id"] for event in raw_pairs})),
    }
    data_quality_warnings: list[str] = []
    if unique_count >= 100 and not concentration["concentration_acceptable"]:
        data_quality_warnings.append("combined event concentration outside preferred limits")
    if unique_count >= 100 and symbol_summary["unique_symbol_count"] < 8:
        data_quality_warnings.append("combined event symbol coverage below preferred minimum")
    if unique_count >= 100 and month_summary["unique_month_count"] < 24:
        data_quality_warnings.append("combined event month coverage below preferred minimum")
    hashes_after = input_hashes()
    if hashes_before != hashes_after:
        raise DiscoveryBlocked("INPUT_ARTIFACT_HASH_CHANGED")
    artifact = {
        "discovery_status": "PASS" if result_classification != RESULT_FAILED else "FAILED_STOP",
        "result_classification": result_classification,
        "recovery_audit_status": audit["recovery_audit_status"],
        "current_head": audit["current_head"],
        "expected_head": audit["expected_head"],
        "head_matches_expected": audit["head_matches_expected"],
        "core_longpaths_value": audit["core_longpaths_value"],
        "input_artifact_hashes_before": hashes_before,
        "input_artifact_hashes_after": hashes_after,
        "input_artifact_hashes_unchanged": hashes_before == hashes_after,
        "combined_theory_id": COMBINED_THEORY_ID,
        "component_a_theory_id": COMPONENT_A_THEORY_ID,
        "component_b_theory_id": COMPONENT_B_THEORY_ID,
        "component_event_reconstruction_status": reconstruction,
        "combined_event_definition": {
            "name": COMBINED_THEORY_ID,
            "component_a_allowed_types": list(COMPONENT_A_SLOTS.values()),
            "component_b_allowed_type": COMPONENT_B_LABEL,
            "same_symbol_required": True,
            "overlap_window": "+/-1h fixed",
            "current_prior_component_data_only": True,
            "future_return_or_volatility_outcome_used": False,
            "options_data_used": False,
        },
        "overlap_window_policy": {
            "primary_window": "+/-1h",
            "window_ms": OVERLAP_WINDOW_MS,
            "optimized_or_tuned": False,
            "informational_buckets_only": ["exact_same_timestamp", "within_15m", "within_30m", "within_60m"],
        },
        "deduplication_policy": {
            "policy": "deterministic nearest-timestamp-pair greedy matching",
            "sort_order": [
                "absolute time distance",
                "combined event time",
                "component A time",
                "component B time",
                "symbol",
                "component event ids",
            ],
            "tie_breaker": "earliest pair deterministically",
            "component_events_reused": False,
            "uses_returns_or_outcomes": False,
        },
        "combined_event_timestamp_policy": {
            "combined_event_time": "max(component_a_time, component_b_time)",
            "rationale": "time both component confirmations are known",
            "examples_first_25": [
                {
                    "symbol": event["symbol"],
                    "component_a_time": event["component_a_time"],
                    "component_b_time": event["component_b_time"],
                    "combined_event_time": event["combined_event_time"],
                    "distance_minutes": event["time_distance_minutes"],
                    "component_a_subtype": event["component_a_subtype"],
                    "component_b_subtype": event["component_b_subtype"],
                }
                for event in unique_events[:25]
            ],
        },
        "raw_pair_count": raw_pair_count,
        "unique_combined_event_count": unique_count,
        "cooldown_filtered_counts": cooldown_counts,
        "event_count_threshold_interpretation": threshold,
        "symbol_coverage_summary": symbol_summary,
        "month_coverage_summary": month_summary,
        "concentration_summary": concentration,
        "arbusdt_summary": {
            "arbusdt_count": sum(1 for event in unique_events if event["symbol"] == "ARBUSDT"),
            "arbusdt_concentration": (
                sum(1 for event in unique_events if event["symbol"] == "ARBUSDT") / unique_count if unique_count else None
            ),
        },
        "overlap_window_distribution": overlap_distribution(unique_events),
        "component_order_distribution": dict(sorted(component_order.items())),
        "component_time_distance_summary": time_distance_summary(unique_events),
        "component_a_subtype_distribution": dict(sorted(component_a_subtypes.items())),
        "component_b_subtype_distribution": dict(sorted(component_b_subtypes.items())),
        "missing_component_summary": missing_summary,
        "data_quality_warnings": data_quality_warnings,
        "options_availability_diagnostic_allowed_after_validator": options_allowed_after_validator,
        "forward_return_diagnostic_allowed": False,
        "strategy_allowed": False,
        "signal_allowed": False,
        "candidate_generation_allowed": False,
        "release_allowed": False,
        "forbidden_actions_confirmed_false": FORBIDDEN_ACTIONS_CONFIRMED_FALSE,
        "allowed_next_step": allowed_next_step,
        "blocker": None,
    }
    return artifact


def blocked_artifact(reason: str) -> dict[str, Any]:
    audit = recovery_audit()
    try:
        before = input_hashes()
        after = input_hashes()
    except Exception:
        before = {}
        after = {}
    return {
        "discovery_status": "FAILED_STOP",
        "result_classification": RESULT_FAILED,
        "recovery_audit_status": audit.get("recovery_audit_status"),
        "current_head": audit.get("current_head"),
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": audit.get("head_matches_expected"),
        "core_longpaths_value": audit.get("core_longpaths_value"),
        "input_artifact_hashes_before": before,
        "input_artifact_hashes_after": after,
        "input_artifact_hashes_unchanged": before == after and bool(before),
        "combined_theory_id": COMBINED_THEORY_ID,
        "component_a_theory_id": COMPONENT_A_THEORY_ID,
        "component_b_theory_id": COMPONENT_B_THEORY_ID,
        "component_event_reconstruction_status": None,
        "combined_event_definition": None,
        "overlap_window_policy": None,
        "deduplication_policy": None,
        "combined_event_timestamp_policy": None,
        "raw_pair_count": 0,
        "unique_combined_event_count": 0,
        "cooldown_filtered_counts": {},
        "event_count_threshold_interpretation": None,
        "symbol_coverage_summary": None,
        "month_coverage_summary": None,
        "concentration_summary": None,
        "arbusdt_summary": None,
        "overlap_window_distribution": None,
        "component_order_distribution": None,
        "component_time_distance_summary": None,
        "component_a_subtype_distribution": None,
        "component_b_subtype_distribution": None,
        "missing_component_summary": None,
        "data_quality_warnings": [],
        "options_availability_diagnostic_allowed_after_validator": False,
        "forward_return_diagnostic_allowed": False,
        "strategy_allowed": False,
        "signal_allowed": False,
        "candidate_generation_allowed": False,
        "release_allowed": False,
        "forbidden_actions_confirmed_false": FORBIDDEN_ACTIONS_CONFIRMED_FALSE,
        "allowed_next_step": NEXT_RECOVERY,
        "blocker": reason,
    }


def write_artifact(artifact: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(artifact, handle, indent=2, sort_keys=True)
        handle.write("\n")


def report_lines(artifact: dict[str, Any]) -> list[str]:
    return [
        f"status: {artifact.get('discovery_status')}",
        f"result_classification: {artifact.get('result_classification')}",
        f"recovery_audit_status: {artifact.get('recovery_audit_status')}",
        f"input_artifact_hashes_unchanged: {artifact.get('input_artifact_hashes_unchanged')}",
        f"combined_theory_id: {artifact.get('combined_theory_id')}",
        "component_event_reconstruction_status: "
        + json.dumps(artifact.get("component_event_reconstruction_status"), sort_keys=True)[:3000],
        "combined_event_definition: " + json.dumps(artifact.get("combined_event_definition"), sort_keys=True),
        "overlap_window_policy: " + json.dumps(artifact.get("overlap_window_policy"), sort_keys=True),
        "deduplication_policy: " + json.dumps(artifact.get("deduplication_policy"), sort_keys=True),
        "combined_event_timestamp_policy: "
        + json.dumps(artifact.get("combined_event_timestamp_policy"), sort_keys=True)[:3000],
        f"raw_pair_count: {artifact.get('raw_pair_count')}",
        f"unique_combined_event_count: {artifact.get('unique_combined_event_count')}",
        "cooldown_filtered_counts: " + json.dumps(artifact.get("cooldown_filtered_counts"), sort_keys=True),
        "event_count_threshold_interpretation: "
        + json.dumps(artifact.get("event_count_threshold_interpretation"), sort_keys=True),
        "symbol_coverage_summary: " + json.dumps(artifact.get("symbol_coverage_summary"), sort_keys=True),
        "month_coverage_summary: " + json.dumps(artifact.get("month_coverage_summary"), sort_keys=True),
        "concentration_summary: " + json.dumps(artifact.get("concentration_summary"), sort_keys=True),
        "arbusdt_summary: " + json.dumps(artifact.get("arbusdt_summary"), sort_keys=True),
        "overlap_window_distribution: "
        + json.dumps(artifact.get("overlap_window_distribution"), sort_keys=True),
        "component_order_distribution: "
        + json.dumps(artifact.get("component_order_distribution"), sort_keys=True),
        "component_time_distance_summary: "
        + json.dumps(artifact.get("component_time_distance_summary"), sort_keys=True),
        "component_a_subtype_distribution: "
        + json.dumps(artifact.get("component_a_subtype_distribution"), sort_keys=True),
        "component_b_subtype_distribution: "
        + json.dumps(artifact.get("component_b_subtype_distribution"), sort_keys=True),
        "missing_component_summary: " + json.dumps(artifact.get("missing_component_summary"), sort_keys=True)[:3000],
        "data_quality_warnings: " + json.dumps(artifact.get("data_quality_warnings"), sort_keys=True),
        f"options_availability_diagnostic_allowed_after_validator: {artifact.get('options_availability_diagnostic_allowed_after_validator')}",
        f"forward_return_diagnostic_allowed: {artifact.get('forward_return_diagnostic_allowed')}",
        f"strategy_allowed: {artifact.get('strategy_allowed')}",
        f"signal_allowed: {artifact.get('signal_allowed')}",
        f"candidate_generation_allowed: {artifact.get('candidate_generation_allowed')}",
        f"release_allowed: {artifact.get('release_allowed')}",
        f"allowed_next_step: {artifact.get('allowed_next_step')}",
        "commit hash: PENDING_COMMIT",
        "final git status: PENDING_COMMIT",
        "repo clean: PENDING_COMMIT",
        "tracked Python count: PENDING_COMMIT",
        "raw data committed: false",
        "cache files staged: false",
        "forbidden actions confirmed false: "
        + json.dumps(artifact.get("forbidden_actions_confirmed_false"), sort_keys=True),
        f"blocker: {artifact.get('blocker')}",
    ]


def main() -> int:
    try:
        artifact = build_artifact()
        write_artifact(artifact)
        for line in report_lines(artifact):
            print(line)
        return 0
    except Exception as exc:  # noqa: BLE001
        artifact = blocked_artifact(str(exc))
        write_artifact(artifact)
        for line in report_lines(artifact):
            print(line)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
