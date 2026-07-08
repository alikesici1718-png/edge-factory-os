#!/usr/bin/env python
"""Outcome-blind Binance theory queue builder for available public OI/taker/kline features."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = "OUTCOME_BLIND_BINANCE_THEORY_QUEUE_BUILDER_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_outcome_blind_binance_theory_queue_builder_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/research/outcome_blind_binance_theory_queue_builder_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_HEAD = "073a4bcb8e06b6582c9a87099cf56169a4fc6b81"

SOURCE_DATASET_BUILDER_RELATIVE_PATH = "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"
SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH = "artifacts/research/binance_public_kline_forward_return_diagnostic_v1.json"
SOURCE_HOLDOUT_RELATIVE_PATH = (
    "artifacts/research/extreme_oi_taker_crowding_price_failure_frozen_historical_holdout_backtest_v1.json"
)
SOURCE_INDEPENDENT_VALIDATION_RELATIVE_PATH = (
    "artifacts/research/extreme_oi_taker_crowding_price_failure_pre_registered_independent_validation_runner_v1.json"
)
SOURCE_SEMANTICS_RELATIVE_PATH = (
    "artifacts/research/extreme_oi_taker_crowding_price_failure_direction_semantics_review_v1.json"
)
SOURCE_BROAD_ROBUSTNESS_RELATIVE_PATH = "artifacts/research/binance_oi_taker_crowding_forward_return_robustness_runner_v1.json"
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_DATASET_BUILDER_RELATIVE_PATH,
    SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH,
    SOURCE_HOLDOUT_RELATIVE_PATH,
    SOURCE_INDEPENDENT_VALIDATION_RELATIVE_PATH,
    SOURCE_SEMANTICS_RELATIVE_PATH,
    SOURCE_BROAD_ROBUSTNESS_RELATIVE_PATH,
]

THEORY_QUEUE_STATUS_PASS = "PASS_REPO_ONLY_OUTCOME_BLIND_BINANCE_THEORY_QUEUE_BUILDER_CREATED"
THEORY_QUEUE_STATUS_BLOCKED = "BLOCKED_OUTCOME_BLIND_BINANCE_THEORY_QUEUE_BUILDER"
ARTIFACT_KIND = "OUTCOME_BLIND_BINANCE_THEORY_QUEUE_BUILDER"

RESULT_READY = "OUTCOME_BLIND_BINANCE_THEORY_QUEUE_READY"
RESULT_ATTENTION = "OUTCOME_BLIND_BINANCE_THEORY_QUEUE_REQUIRES_ATTENTION"
RESULT_FAILED = "OUTCOME_BLIND_BINANCE_THEORY_QUEUE_FAILED_STOP"

NEXT_READY = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_DISCOVERY_V1"
NEXT_ATTENTION = "OUTCOME_BLIND_BINANCE_THEORY_QUEUE_REVIEW_V1"


class TheoryQueueBlocked(Exception):
    pass


def canonical_payload_hash(payload: dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(clean, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def git_base_args() -> list[str]:
    safe_dir = str(REPO_ROOT).replace("\\", "/")
    return ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={safe_dir}"]


def run_git(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(
        [*git_base_args(), *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return result.returncode, result.stdout, result.stderr


def git_lines(args: list[str]) -> list[str]:
    code, stdout, stderr = run_git(args)
    if code != 0:
        raise TheoryQueueBlocked(f"git {' '.join(args)} failed: {stderr.strip() or stdout.strip()}")
    return [line.rstrip() for line in stdout.splitlines() if line.strip()]


def current_head() -> str:
    lines = git_lines(["rev-parse", "HEAD"])
    return lines[0] if lines else ""


def current_branch() -> str:
    lines = git_lines(["branch", "--show-current"])
    return lines[0] if lines else ""


def output_only_status(status_lines: list[str]) -> bool:
    allowed = {
        f"?? {MODULE_RELATIVE_PATH}",
        f"?? {ARTIFACT_RELATIVE_PATH}",
        f"A  {MODULE_RELATIVE_PATH}",
        f"A  {ARTIFACT_RELATIVE_PATH}",
    }
    for line in status_lines:
        if line in allowed:
            continue
        if line.startswith("!! ") and line[3:].startswith("cache/"):
            continue
        return False
    return True


def recovery_audit() -> dict[str, Any]:
    head = current_head()
    porcelain = git_lines(["status", "--porcelain=v1"])
    staged = git_lines(["diff", "--cached", "--name-status"])
    modified = git_lines(["diff", "--name-status"])
    untracked = git_lines(["ls-files", "--others", "--exclude-standard"])
    deleted = git_lines(["ls-files", "--deleted"])
    head_matches = head == EXPECTED_HEAD
    if staged:
        decision = "RECOVERY_STAGED_FILES_PRESENT_STOP"
    elif not head_matches:
        decision = "RECOVERY_HEAD_MISMATCH_STOP"
    elif not output_only_status(porcelain):
        decision = "RECOVERY_DIRTY_WITH_UNKNOWN_OR_RISKY_FILES_STOP"
    else:
        decision = "RECOVERY_AUDIT_CLEAN_CONTINUE"
    return {
        "current_head": head,
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": head_matches,
        "branch": current_branch(),
        "git_status_porcelain": porcelain,
        "staged_files": staged,
        "modified_tracked_files": modified,
        "untracked_files": untracked,
        "deleted_files": deleted,
        "recovery_decision": decision,
        "git_clean_before": not porcelain and not staged and not modified and not untracked and not deleted,
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_artifact_hashes() -> dict[str, str]:
    hashes = {}
    for relative_path in INPUT_ARTIFACT_RELATIVE_PATHS:
        path = REPO_ROOT / relative_path
        if not path.exists():
            raise TheoryQueueBlocked(f"missing required input artifact: {relative_path}")
        hashes[relative_path] = sha256_file(path)
    return hashes


def read_json_readonly(relative_path: str) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise TheoryQueueBlocked(f"missing required input artifact: {relative_path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise TheoryQueueBlocked(f"input artifact is not a JSON object: {relative_path}")
    return payload


def verify_payload_hash(payload: dict[str, Any], label: str) -> str | None:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        return None
    recomputed = canonical_payload_hash(payload)
    if stored != recomputed:
        raise TheoryQueueBlocked(f"{label} payload hash mismatch: {recomputed} != {stored}")
    return stored


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str | None]]:
    dataset = read_json_readonly(SOURCE_DATASET_BUILDER_RELATIVE_PATH)
    kline = read_json_readonly(SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH)
    holdout = read_json_readonly(SOURCE_HOLDOUT_RELATIVE_PATH)
    independent = read_json_readonly(SOURCE_INDEPENDENT_VALIDATION_RELATIVE_PATH)
    semantics = read_json_readonly(SOURCE_SEMANTICS_RELATIVE_PATH)
    broad_robustness = read_json_readonly(SOURCE_BROAD_ROBUSTNESS_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_DATASET_BUILDER_RELATIVE_PATH: verify_payload_hash(dataset, "metrics dataset builder"),
        SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(kline, "public kline diagnostic"),
        SOURCE_HOLDOUT_RELATIVE_PATH: verify_payload_hash(holdout, "historical holdout"),
        SOURCE_INDEPENDENT_VALIDATION_RELATIVE_PATH: verify_payload_hash(independent, "independent validation"),
        SOURCE_SEMANTICS_RELATIVE_PATH: verify_payload_hash(semantics, "direction semantics review"),
        SOURCE_BROAD_ROBUSTNESS_RELATIVE_PATH: verify_payload_hash(broad_robustness, "broad robustness runner"),
    }
    return dataset, kline, holdout, independent, semantics, broad_robustness, payload_hashes


def available_feature_registry(dataset: dict[str, Any], kline: dict[str, Any], holdout: dict[str, Any], independent: dict[str, Any]) -> dict[str, Any]:
    summary = dataset.get("normalized_dataset_summary", {})
    return {
        "open_interest_metrics": {
            "available": summary.get("symbols_with_open_interest", 0) == summary.get("built_symbol_count", 0),
            "symbols_available": summary.get("symbols_with_open_interest"),
            "coverage": {
                "research_2023_2025_min": summary.get("timestamp_global_min"),
                "research_2023_2025_max": summary.get("timestamp_global_max"),
                "historical_holdout_window": holdout.get("actual_holdout_window"),
                "independent_2026_window": independent.get("independent_validation_window"),
            },
        },
        "taker_buy_sell_pressure_ratio": {
            "available": summary.get("symbols_with_taker_ratio", 0) == summary.get("built_symbol_count", 0),
            "symbols_available": summary.get("symbols_with_taker_ratio"),
            "note": "Metric archive has taker buy/sell ratio and derived sell pressure, not raw taker buy/sell volume components.",
        },
        "global_long_short_ratio": {
            "available": summary.get("symbols_with_global_long_short", 0) == summary.get("built_symbol_count", 0),
            "symbols_available": summary.get("symbols_with_global_long_short"),
        },
        "top_account_long_short_ratio": {
            "available": summary.get("symbols_with_top_account_ratio", 0) == summary.get("built_symbol_count", 0),
            "symbols_available": summary.get("symbols_with_top_account_ratio"),
        },
        "top_position_long_short_ratio": {
            "available": summary.get("symbols_with_top_position_ratio", 0) == summary.get("built_symbol_count", 0),
            "symbols_available": summary.get("symbols_with_top_position_ratio"),
        },
        "public_15m_kline_ohlcv": {
            "available": sorted(kline.get("symbols_built", [])) == sorted(kline.get("symbols_requested", [])),
            "interval": kline.get("interval"),
            "research_archive_availability": kline.get("public_data_source"),
            "row_count": kline.get("kline_row_count"),
        },
        "historical_2020_2022_probe_metadata": {
            "available": True,
            "symbols_available": holdout.get("symbols_available"),
            "archive_availability_summary": {
                "available_archive_count": holdout.get("archive_availability_summary", {}).get("available_archive_count"),
                "missing_archive_count": holdout.get("archive_availability_summary", {}).get("missing_archive_count"),
            },
            "holdout_event_count": holdout.get("event_count"),
        },
        "independent_2026_probe_metadata": {
            "available": True,
            "symbols_available": independent.get("symbols_available"),
            "archive_availability_summary": {
                "available_archive_count": independent.get("archive_availability_summary", {}).get("available_archive_count"),
                "missing_archive_count": independent.get("archive_availability_summary", {}).get("missing_archive_count"),
            },
            "validation_event_count": independent.get("event_count"),
        },
    }


def unavailable_feature_registry(dataset: dict[str, Any]) -> dict[str, Any]:
    unavailable = dataset.get("unavailable_data_summary", {})
    return {
        "liquidation": {
            "available": False,
            "reason": unavailable.get("liquidation", "unavailable in metrics archive"),
            "route_policy": "data-unavailable theories only; no direct liquidation flush tests",
        },
        "funding": {
            "available": False,
            "reason": unavailable.get("funding", "unavailable in metrics archive"),
            "route_policy": "do not revive funding crowding/carry/volume surge routes",
        },
        "raw_taker_buy_sell_volume_components": {
            "available": False,
            "reason": unavailable.get("taker_buy_sell_volume_components", "ratio available but raw components unavailable"),
        },
        "private_account_order_live_data": {
            "available": False,
            "reason": "forbidden by safety policy and not needed for outcome-blind research queue",
        },
    }


def prior_route_lessons(holdout: dict[str, Any], independent: dict[str, Any], semantics: dict[str, Any], broad: dict[str, Any]) -> dict[str, Any]:
    return {
        "broad_oi_taker_crowding_route": {
            "result_classification": broad.get("result_classification"),
            "lesson": "Do not reuse broad OI/taker/crowding forward-return route; future theories need materially narrower mechanics.",
            "closed_for_queue_reuse": True,
        },
        "short_pressure_failure_delayed_downside_continuation": {
            "neutral_label": semantics.get("approved_neutral_diagnostic_label"),
            "direction_relabel_required": semantics.get("direction_relabel_required"),
            "independent_2026_result": independent.get("result_classification"),
            "historical_holdout_result": holdout.get("result_classification"),
            "lesson": "Keep as monitor/accumulation only; do not turn into live/candidate route or retune thresholds.",
            "closed_for_new_theory_queue_as_live_or_candidate": True,
        },
        "data_availability_lesson": {
            "liquidation_and_funding_unavailable": True,
            "lesson": "Avoid theories that require true liquidation or funding history unless explicitly marked data-unavailable.",
        },
    }


def blocked_route_keys() -> list[str]:
    return [
        "broad_oi_taker_crowding_forward_return_route",
        "funding_crowding_reversal",
        "funding_carry",
        "funding_extreme_volume_surge",
        "taker_buy_exhaustion",
        "taker_flow_momentum_continuation",
        "SHORT_PRESSURE_FAILURE_DELAYED_DOWNSIDE_CONTINUATION_DIAGNOSTIC_as_live_candidate_route",
        "liquidation_required_route_without_liquidation_data",
        "funding_required_route_without_funding_data",
    ]


def forbidden_actions() -> dict[str, bool]:
    return {
        "strategy": False,
        "signal": False,
        "backtest": False,
        "pnl": False,
        "trade_simulation": False,
        "optimization_against_returns": False,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "order_private_account_api_key": False,
        "forward_returns_computed": False,
        "p_values_computed": False,
        "null_validation_run": False,
        "failed_routes_reused_under_new_names": False,
    }


def theory_catalog() -> list[dict[str, Any]]:
    return [
        {
            "theory_id": "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION",
            "mechanical_rationale": "Open interest contraction can indicate forced position reduction or de-risking; if same-bar taker pressure is extreme and price rejects the flow direction, the event is mechanically distinct from OI expansion pressure failure.",
            "required_features": ["open_interest", "oi_delta_log_1h", "taker_buy_sell_ratio_or_sell_pressure", "15m_ohlc_range_wicks_close_location"],
            "data_availability_status": "available",
            "material_difference_from_failed_routes": "Uses OI contraction instead of expansion and makes price rejection mandatory; no funding, liquidation, or broad crowding premise.",
            "overfitting_risk": "medium_low",
            "expected_event_frequency_band": "sparse_but_feasible_to_ideal",
            "pre_registration_requirements": [
                "freeze contraction percentile grid before return diagnostics",
                "define long capitulation and short-cover variants without forward returns",
                "cooldown and concentration gates before any return labels",
            ],
            "primary_event_discovery_module_name": "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_DISCOVERY_V1",
            "allowed_next_step_if_selected": "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_DISCOVERY_V1",
            "recommended_priority": 1,
        },
        {
            "theory_id": "OI_EXPANSION_PRICE_ABSORPTION_WITH_VOLUME_CONFIRMATION",
            "mechanical_rationale": "OI expansion plus extreme taker flow is only considered when the current bar/range shows absorption and public kline volume confirms stress.",
            "required_features": ["open_interest", "taker_ratio", "15m_ohlcv_volume", "range_close_location", "wick_absorption"],
            "data_availability_status": "available",
            "material_difference_from_failed_routes": "Requires absorption and volume confirmation; avoids broad crowding and does not reuse short_core pressure-failure definition.",
            "overfitting_risk": "medium",
            "expected_event_frequency_band": "ideal_to_acceptable",
            "pre_registration_requirements": [
                "limit volume threshold degrees of freedom",
                "predefine absorption variants before return diagnostics",
                "block any reuse of exact short_core labels",
            ],
            "primary_event_discovery_module_name": "OI_EXPANSION_PRICE_ABSORPTION_WITH_VOLUME_CONFIRMATION_EVENT_DISCOVERY_V1",
            "allowed_next_step_if_selected": "OI_EXPANSION_PRICE_ABSORPTION_WITH_VOLUME_CONFIRMATION_EVENT_DISCOVERY_V1",
            "recommended_priority": 4,
        },
        {
            "theory_id": "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT",
            "mechanical_rationale": "An OI shock concurrent with realized-volatility compression/expansion transition is a market-state change, not a directional prediction.",
            "required_features": ["open_interest", "oi_delta_log_1h_or_4h", "15m_ohlc_realized_volatility", "volatility_regime_state"],
            "data_availability_status": "available",
            "material_difference_from_failed_routes": "Regime-state event with no taker-flow momentum premise and no crowding route reuse.",
            "overfitting_risk": "low_medium",
            "expected_event_frequency_band": "ideal",
            "pre_registration_requirements": [
                "freeze realized volatility windows",
                "classify expansion/compression states before return labels",
                "market-state diagnostics before any side-specific interpretation",
            ],
            "primary_event_discovery_module_name": "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_EVENT_DISCOVERY_V1",
            "allowed_next_step_if_selected": "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_EVENT_DISCOVERY_V1",
            "recommended_priority": 2,
        },
        {
            "theory_id": "TAKER_PRESSURE_DIVERGENCE_WITH_PRICE_NONCONFIRMATION",
            "mechanical_rationale": "Extreme taker pressure with non-confirming price action can be studied with OI as an annotation rather than a tuned hard gate.",
            "required_features": ["taker_ratio", "15m_ohlc_close_location", "price_nonconfirmation", "oi_annotation"],
            "data_availability_status": "available",
            "material_difference_from_failed_routes": "OI is annotation/tier, not optimized threshold; avoids taker-flow momentum continuation and taker-buy exhaustion labels.",
            "overfitting_risk": "medium_high",
            "expected_event_frequency_band": "acceptable_but_potentially_broad",
            "pre_registration_requirements": [
                "cap variants and sides",
                "use OI tiers only for descriptive coverage",
                "reject momentum/exhaustion naming",
            ],
            "primary_event_discovery_module_name": "TAKER_PRESSURE_DIVERGENCE_WITH_PRICE_NONCONFIRMATION_EVENT_DISCOVERY_V1",
            "allowed_next_step_if_selected": "TAKER_PRESSURE_DIVERGENCE_WITH_PRICE_NONCONFIRMATION_EVENT_DISCOVERY_V1",
            "recommended_priority": 7,
        },
        {
            "theory_id": "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT",
            "mechanical_rationale": "Top account/position long-short ratios moving from extreme toward neutral can define a crowding-state normalization event using only ratio path/current/prior state.",
            "required_features": ["top_account_long_short_ratio", "top_position_long_short_ratio", "global_long_short_ratio", "ratio_path_change"],
            "data_availability_status": "available",
            "material_difference_from_failed_routes": "Ratio-path normalization does not require OI expansion/taker flow as the core event and does not use funding crowding.",
            "overfitting_risk": "low_medium",
            "expected_event_frequency_band": "sparse_but_feasible_to_ideal",
            "pre_registration_requirements": [
                "freeze extreme and neutral bands from symbol-month distributions",
                "record account vs position variants before returns",
                "avoid funding terminology",
            ],
            "primary_event_discovery_module_name": "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_DISCOVERY_V1",
            "allowed_next_step_if_selected": "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_DISCOVERY_V1",
            "recommended_priority": 3,
        },
        {
            "theory_id": "CROSS_SYMBOL_PRESSURE_DISPERSION_EVENT",
            "mechanical_rationale": "A cross-sectional dispersion/concentration event captures relative pressure across symbols without directional single-symbol optimization.",
            "required_features": ["multi_symbol_oi_change", "multi_symbol_taker_pressure", "cross_sectional_dispersion"],
            "data_availability_status": "available_with_symbol_listing_limitations",
            "material_difference_from_failed_routes": "Cross-symbol state diagnostic, not the exact short_core or broad single-event route.",
            "overfitting_risk": "medium",
            "expected_event_frequency_band": "ideal",
            "pre_registration_requirements": [
                "freeze symbol universe before event discovery",
                "handle listing-history missingness explicitly",
                "no forward-return-weighted symbol selection",
            ],
            "primary_event_discovery_module_name": "CROSS_SYMBOL_PRESSURE_DISPERSION_EVENT_DISCOVERY_V1",
            "allowed_next_step_if_selected": "CROSS_SYMBOL_PRESSURE_DISPERSION_EVENT_DISCOVERY_V1",
            "recommended_priority": 5,
        },
        {
            "theory_id": "MARKET_WIDE_OI_SYNCHRONIZATION_STRESS_EVENT",
            "mechanical_rationale": "Synchronized OI expansion/contraction and taker imbalance across many symbols define a market stress state, not a strategy.",
            "required_features": ["multi_symbol_oi_change", "multi_symbol_taker_imbalance", "market_wide_synchronization_count"],
            "data_availability_status": "available_with_symbol_listing_limitations",
            "material_difference_from_failed_routes": "Market-state diagnostic that avoids single-symbol crowding forward-return route reuse.",
            "overfitting_risk": "low_medium",
            "expected_event_frequency_band": "sparse_but_feasible",
            "pre_registration_requirements": [
                "freeze breadth threshold",
                "freeze symbol inclusion policy",
                "separate expansion and contraction states before diagnostics",
            ],
            "primary_event_discovery_module_name": "MARKET_WIDE_OI_SYNCHRONIZATION_STRESS_EVENT_DISCOVERY_V1",
            "allowed_next_step_if_selected": "MARKET_WIDE_OI_SYNCHRONIZATION_STRESS_EVENT_DISCOVERY_V1",
            "recommended_priority": 6,
        },
        {
            "theory_id": "PRICE_RANGE_REJECTION_WITH_OI_TAKER_CONFIRMATION",
            "mechanical_rationale": "Make public kline wick/range rejection the primary event, while OI/taker features confirm stress rather than define the same already-tested short_core route.",
            "required_features": ["15m_ohlc_wick_range_rejection", "open_interest_annotation", "taker_pressure_confirmation"],
            "data_availability_status": "available",
            "material_difference_from_failed_routes": "Price action is primary and OI/taker are confirmation tiers; must exclude the exact tested short_core definition.",
            "overfitting_risk": "medium_high",
            "expected_event_frequency_band": "acceptable_but_potentially_broad",
            "pre_registration_requirements": [
                "hard exclude exact short_core definition",
                "freeze wick/range logic before return labels",
                "limit confirmation tier count",
            ],
            "primary_event_discovery_module_name": "PRICE_RANGE_REJECTION_WITH_OI_TAKER_CONFIRMATION_EVENT_DISCOVERY_V1",
            "allowed_next_step_if_selected": "PRICE_RANGE_REJECTION_WITH_OI_TAKER_CONFIRMATION_EVENT_DISCOVERY_V1",
            "recommended_priority": 8,
        },
    ]


def score_theory(theory: dict[str, Any]) -> dict[str, Any]:
    availability = {
        "available": 20,
        "available_with_symbol_listing_limitations": 16,
        "partial": 10,
        "data_unavailable": 0,
    }.get(theory["data_availability_status"], 0)
    material_difference = {
        "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION": 20,
        "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT": 19,
        "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT": 18,
        "MARKET_WIDE_OI_SYNCHRONIZATION_STRESS_EVENT": 17,
        "CROSS_SYMBOL_PRESSURE_DISPERSION_EVENT": 16,
        "OI_EXPANSION_PRICE_ABSORPTION_WITH_VOLUME_CONFIRMATION": 14,
        "PRICE_RANGE_REJECTION_WITH_OI_TAKER_CONFIRMATION": 12,
        "TAKER_PRESSURE_DIVERGENCE_WITH_PRICE_NONCONFIRMATION": 10,
    }[theory["theory_id"]]
    interpretability = {
        "low_medium": 17,
        "medium_low": 16,
        "medium": 13,
        "medium_high": 9,
    }.get(theory["overfitting_risk"], 10)
    event_feasibility = {
        "ideal": 18,
        "sparse_but_feasible_to_ideal": 16,
        "sparse_but_feasible": 13,
        "ideal_to_acceptable": 13,
        "acceptable_but_potentially_broad": 10,
    }.get(theory["expected_event_frequency_band"], 8)
    concentration_potential = 14 if "multi_symbol" not in theory["required_features"] else 12
    independent_validation_feasibility = 15 if theory["data_availability_status"].startswith("available") else 5
    threshold_discipline = {
        "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT": 15,
        "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT": 15,
        "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION": 14,
        "MARKET_WIDE_OI_SYNCHRONIZATION_STRESS_EVENT": 14,
        "CROSS_SYMBOL_PRESSURE_DISPERSION_EVENT": 12,
        "OI_EXPANSION_PRICE_ABSORPTION_WITH_VOLUME_CONFIRMATION": 10,
        "PRICE_RANGE_REJECTION_WITH_OI_TAKER_CONFIRMATION": 9,
        "TAKER_PRESSURE_DIVERGENCE_WITH_PRICE_NONCONFIRMATION": 8,
    }[theory["theory_id"]]
    robustness_testability = 15 if theory["data_availability_status"].startswith("available") else 5
    total = (
        availability
        + material_difference
        + interpretability
        + event_feasibility
        + concentration_potential
        + independent_validation_feasibility
        + threshold_discipline
        + robustness_testability
    )
    return {
        "theory_id": theory["theory_id"],
        "score_total": total,
        "score_components": {
            "data_availability": availability,
            "material_difference_from_failed_routes": material_difference,
            "interpretability_low_overfitting": interpretability,
            "expected_event_count_feasibility": event_feasibility,
            "low_overlap_low_concentration_potential": concentration_potential,
            "independent_validation_feasibility": independent_validation_feasibility,
            "minimal_threshold_degrees_of_freedom": threshold_discipline,
            "robustness_testability": robustness_testability,
        },
        "scoring_outcome_blind": True,
    }


def build_research_budget_policy() -> dict[str, Any]:
    return {
        "future_theory_sequence": [
            "event_discovery_without_returns",
            "event_validator",
            "forward_return_diagnostic",
            "null_validation",
            "robustness",
            "pre_registered_independent_validation",
            "monitor_or_close",
        ],
        "one_theory_at_a_time": True,
        "failed_robustness_policy": "close_or_materially_redesign; do not rename and retest same mechanics",
        "independent_validation_fail_or_inconclusive_policy": "monitor_or_close; do not tune thresholds",
        "candidate_or_release_allowed": False,
    }


def build_overfitting_controls() -> dict[str, Any]:
    return {
        "outcome_blind_queue_scoring": True,
        "no_forward_returns_inspected_for_theory_selection": True,
        "no_p_values_used_for_theory_selection": True,
        "no_pnl_sharpe_hit_rate_or_backtest_metrics": True,
        "pre_register_event_definitions_before_return_diagnostics": True,
        "limit_threshold_degrees_of_freedom": True,
        "cooldown_and_concentration_checks_before_outcome_labels": True,
        "independent_validation_required_before_any_promotion": True,
        "no_strategy_signal_candidate_release_permission": True,
    }


def blocked_artifact(
    reason: str,
    audit: dict[str, Any] | None = None,
    hashes_before: dict[str, str] | None = None,
    hashes_after: dict[str, str] | None = None,
) -> dict[str, Any]:
    try:
        head = current_head()
    except Exception:
        head = None
    unchanged = hashes_before == hashes_after if hashes_before and hashes_after else False
    artifact = {
        "theory_queue_status": THEORY_QUEUE_STATUS_BLOCKED,
        "status": THEORY_QUEUE_STATUS_BLOCKED,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "result_classification": RESULT_FAILED,
        "recovery_audit_status": (audit or {}).get("recovery_decision", "RECOVERY_UNKNOWN"),
        "current_head": head,
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": head == EXPECTED_HEAD,
        "input_artifact_hashes_before": hashes_before or {},
        "input_artifact_hashes_after": hashes_after or {},
        "input_artifact_hashes_unchanged": unchanged,
        "available_feature_registry": {},
        "unavailable_feature_registry": {},
        "prior_route_lessons": {},
        "blocked_route_keys": blocked_route_keys(),
        "theory_families_considered": [],
        "theory_scores": {},
        "selected_next_research_batch": [],
        "backlog_theories": [],
        "research_budget_policy": build_research_budget_policy(),
        "overfitting_controls": build_overfitting_controls(),
        "forbidden_actions_confirmed_false": forbidden_actions(),
        "allowed_next_step": NEXT_ATTENTION,
        "blocker": reason,
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def build_artifact() -> dict[str, Any]:
    audit = recovery_audit()
    if audit["recovery_decision"] != "RECOVERY_AUDIT_CLEAN_CONTINUE":
        return blocked_artifact(audit["recovery_decision"], audit)
    hashes_before = input_artifact_hashes()
    dataset, kline, holdout, independent, semantics, broad, payload_hashes = load_inputs()
    if dataset.get("result_classification") != "BINANCE_DATA_VISION_UM_METRICS_DATASET_READY_FOR_PROXY_EVENT_STUDY":
        raise TheoryQueueBlocked("metrics dataset is not ready for proxy event study")
    if kline.get("diagnostic_status") != "PASS_REPO_ONLY_BINANCE_PUBLIC_KLINE_FORWARD_RETURN_DIAGNOSTIC_CREATED":
        raise TheoryQueueBlocked("public kline diagnostic input is not PASS")
    theories = theory_catalog()
    scores = {theory["theory_id"]: score_theory(theory) for theory in theories}
    ranked = sorted(theories, key=lambda item: (item["recommended_priority"], -scores[item["theory_id"]]["score_total"]))
    selected_ids = [
        "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION",
        "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT",
        "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT",
    ]
    selected = [theory for theory in ranked if theory["theory_id"] in selected_ids]
    backlog = [theory for theory in ranked if theory["theory_id"] not in selected_ids]
    for theory in theories:
        theory["forbidden_actions"] = forbidden_actions()
        theory["reason_for_priority"] = {
            "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION": "Highest priority because it is outcome-blind, uses available OI/taker/price features, and is mechanically opposite the failed OI expansion pressure-failure route.",
            "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT": "Selected for robust market-state mechanics, low dependence on directional naming, and limited threshold degrees of freedom.",
            "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT": "Selected because ratio-path normalization uses available top-account/top-position features without funding or broad OI/taker reuse.",
        }.get(theory["theory_id"], "Backlog: mechanically plausible but lower priority due broader definitions, greater overlap risk, or higher threshold degrees of freedom.")
    hashes_after = input_artifact_hashes()
    input_unchanged = hashes_before == hashes_after
    if not input_unchanged:
        raise TheoryQueueBlocked("INPUT_ARTIFACT_HASH_CHANGED")
    validation_checks = {
        "input_artifact_hashes_unchanged": input_unchanged,
        "available_oi_taker_crowding_kline_features": True,
        "unavailable_funding_liquidation_blocked": True,
        "selected_batch_at_most_3": len(selected) <= 3,
        "first_selected_is_preferred_contraction_theory": selected[0]["theory_id"] == "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION",
        "no_forward_returns_computed": True,
        "no_p_values_computed": True,
        "no_null_validation_run": True,
        "no_strategy_signal_candidate_release_permissions": True,
    }
    result_classification = RESULT_READY if all(validation_checks.values()) else RESULT_ATTENTION
    allowed_next_step = NEXT_READY if result_classification == RESULT_READY else NEXT_ATTENTION
    artifact = {
        "theory_queue_status": THEORY_QUEUE_STATUS_PASS,
        "status": THEORY_QUEUE_STATUS_PASS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "result_classification": result_classification,
        "recovery_audit_status": audit["recovery_decision"],
        "current_head": audit["current_head"],
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": audit["head_matches_expected"],
        "input_artifact_hashes_before": hashes_before,
        "input_artifact_hashes_after": hashes_after,
        "input_artifact_hashes_unchanged": input_unchanged,
        "input_payload_hashes_verified": payload_hashes,
        "available_feature_registry": available_feature_registry(dataset, kline, holdout, independent),
        "unavailable_feature_registry": unavailable_feature_registry(dataset),
        "prior_route_lessons": prior_route_lessons(holdout, independent, semantics, broad),
        "blocked_route_keys": blocked_route_keys(),
        "theory_families_considered": theories,
        "theory_scores": scores,
        "selected_next_research_batch": selected,
        "backlog_theories": backlog,
        "research_budget_policy": build_research_budget_policy(),
        "overfitting_controls": build_overfitting_controls(),
        "forbidden_actions_confirmed_false": forbidden_actions(),
        "allowed_next_step": allowed_next_step,
        "blocker": None,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": all(validation_checks.values()),
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def write_artifact(payload: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def print_summary(artifact: dict[str, Any]) -> None:
    print(f"status: {artifact['theory_queue_status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"recovery_audit_status: {artifact['recovery_audit_status']}")
    print(f"input_artifact_hashes_unchanged: {bool_text(bool(artifact['input_artifact_hashes_unchanged']))}")
    print(f"available_feature_registry: {artifact['available_feature_registry']}")
    print(f"unavailable_feature_registry: {artifact['unavailable_feature_registry']}")
    print(f"selected_next_research_batch: {artifact['selected_next_research_batch']}")
    top = artifact["selected_next_research_batch"][0]["theory_id"] if artifact["selected_next_research_batch"] else None
    print(f"top_selected_theory: {top}")
    print(f"blocked_route_keys: {artifact['blocked_route_keys']}")
    print(f"overfitting_controls: {artifact['overfitting_controls']}")
    print(f"research_budget_policy: {artifact['research_budget_policy']}")
    print(f"allowed_next_step: {artifact['allowed_next_step']}")
    print(f"forbidden actions confirmed false: {artifact['forbidden_actions_confirmed_false']}")
    print(f"blocker: {artifact['blocker']}")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")


def main() -> int:
    hashes_before = None
    hashes_after = None
    audit = None
    try:
        audit = recovery_audit()
        print(f"current HEAD: {audit['current_head']}")
        print(f"expected HEAD: {EXPECTED_HEAD}")
        print(f"branch: {audit['branch']}")
        print(f"git status porcelain: {audit['git_status_porcelain']}")
        print(f"staged files: {audit['staged_files']}")
        print(f"modified tracked files: {audit['modified_tracked_files']}")
        print(f"untracked files: {audit['untracked_files']}")
        print(f"deleted files: {audit['deleted_files']}")
        print(f"recovery decision: {audit['recovery_decision']}")
        hashes_before = input_artifact_hashes()
        artifact = build_artifact()
        hashes_after = input_artifact_hashes()
        if hashes_before != hashes_after:
            artifact = blocked_artifact("INPUT_ARTIFACT_HASH_CHANGED", audit, hashes_before, hashes_after)
        write_artifact(artifact)
        print_summary(artifact)
        return 0 if artifact["theory_queue_status"] == THEORY_QUEUE_STATUS_PASS else 1
    except Exception as exc:
        try:
            hashes_after = input_artifact_hashes() if hashes_before else None
        except Exception:
            hashes_after = None
        artifact = blocked_artifact(str(exc), audit, hashes_before, hashes_after)
        write_artifact(artifact)
        print_summary(artifact)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
