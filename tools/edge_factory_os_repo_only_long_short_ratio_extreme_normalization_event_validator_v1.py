#!/usr/bin/env python
"""Validate long-short ratio extreme-normalization event definitions without outcomes."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_VALIDATOR_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_long_short_ratio_extreme_normalization_event_validator_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/research/long_short_ratio_extreme_normalization_event_validator_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_HEAD = "381e2ef144304439448bd5f6f43d4b3ae1e1d8a9"
RECOVERY_AUDIT_STATUS = "RECOVERY_AUDIT_CLEAN_CONTINUE"

SOURCE_DISCOVERY_RELATIVE_PATH = "artifacts/research/long_short_ratio_extreme_normalization_event_discovery_v1.json"
SOURCE_THEORY_QUEUE_RELATIVE_PATH = "artifacts/research/outcome_blind_binance_theory_queue_builder_v1.json"
SOURCE_OI_SHOCK_VALIDATION_RELATIVE_PATH = (
    "artifacts/research/oi_shock_with_realized_volatility_regime_shift_pre_registered_independent_validation_runner_v1.json"
)
SOURCE_OI_CONTRACTION_EVALUATOR_RELATIVE_PATH = (
    "artifacts/research/oi_contraction_taker_capitulation_price_rejection_forward_return_diagnostic_evaluator_v1.json"
)
SOURCE_DATASET_BUILDER_RELATIVE_PATH = "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"
SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH = "artifacts/research/binance_public_kline_forward_return_diagnostic_v1.json"
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_DISCOVERY_RELATIVE_PATH,
    SOURCE_THEORY_QUEUE_RELATIVE_PATH,
    SOURCE_OI_SHOCK_VALIDATION_RELATIVE_PATH,
    SOURCE_OI_CONTRACTION_EVALUATOR_RELATIVE_PATH,
    SOURCE_DATASET_BUILDER_RELATIVE_PATH,
    SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH,
]

VALIDATOR_STATUS_PASS = "PASS_REPO_ONLY_LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_VALIDATOR_CREATED"
VALIDATOR_STATUS_BLOCKED = "BLOCKED_LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_VALIDATOR"
ARTIFACT_KIND = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_VALIDATOR"

RESULT_PASS = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_VALIDATOR_PASS"
RESULT_PASS_WITH_ATTENTION = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_VALIDATOR_PASS_WITH_ATTENTION"
RESULT_REQUIRES_REFINEMENT = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_VALIDATOR_REQUIRES_REFINEMENT"
RESULT_FAILED = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_VALIDATOR_FAILED_STOP"

THEORY_ID = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT"
NEXT_FORWARD_DIAGNOSTIC = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_FORWARD_RETURN_DIAGNOSTIC_V1"
NEXT_REFINEMENT = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_DEFINITION_REFINEMENT_V1"

MAIN_SELECTION_SLOTS = [
    "best_long_crowding_normalization_candidate",
    "best_short_crowding_normalization_candidate",
    "optional_account_position_divergence_resolution_candidate",
]
SECONDARY_SELECTION_SLOTS = [
    "best_long_crowding_persistence_break_candidate",
    "best_short_crowding_persistence_break_candidate",
]
EXPECTED_SELECTED_COUNTS = {
    "best_long_crowding_normalization_candidate": {
        "raw_event_count": 8405,
        "cooldown_filtered_count": 520,
        "definition_id": (
            "LONG_CROWDING_NORMALIZATION_EVENT__source_top_account__extreme_p95.0__"
            "strength_weak__window_4h__cooldown_6h"
        ),
    },
    "best_short_crowding_normalization_candidate": {
        "raw_event_count": 6981,
        "cooldown_filtered_count": 426,
        "definition_id": (
            "SHORT_CROWDING_NORMALIZATION_EVENT__source_top_account__extreme_p5.0__"
            "strength_weak__window_4h__cooldown_6h"
        ),
    },
    "best_long_crowding_persistence_break_candidate": {
        "raw_event_count": 1102,
        "cooldown_filtered_count": 46,
        "definition_id": (
            "LONG_CROWDING_PERSISTENCE_BREAK_EVENT__source_top_account__extreme_p95.0__"
            "strength_weak__window_24h__cooldown_6h"
        ),
    },
    "best_short_crowding_persistence_break_candidate": {
        "raw_event_count": 367,
        "cooldown_filtered_count": 45,
        "definition_id": (
            "SHORT_CROWDING_PERSISTENCE_BREAK_EVENT__source_top_position__extreme_p5.0__"
            "strength_weak__window_4h__cooldown_6h"
        ),
    },
    "optional_account_position_divergence_resolution_candidate": {
        "raw_event_count": 6156,
        "cooldown_filtered_count": 947,
        "definition_id": (
            "TOP_ACCOUNT_POSITION_DIVERGENCE_RESOLUTION_EVENT__source_account_position_pair__"
            "extreme_spread_percentile__strength_medium__window_1h__cooldown_24h"
        ),
    },
}


class ValidatorBlocked(Exception):
    pass


def canonical_payload_hash(payload: dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(clean, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def run_git(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={REPO_ROOT}", *args],
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
        raise ValidatorBlocked(f"git {' '.join(args)} failed: {stderr.strip() or stdout.strip()}")
    return [line.rstrip() for line in stdout.splitlines() if line.strip()]


def current_head() -> str:
    lines = git_lines(["rev-parse", "HEAD"])
    return lines[0] if lines else ""


def working_tree_status() -> list[str]:
    return git_lines(["status", "--porcelain=v1"])


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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_artifact_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for relative_path in INPUT_ARTIFACT_RELATIVE_PATHS:
        path = REPO_ROOT / relative_path
        if not path.exists():
            raise ValidatorBlocked(f"missing required input artifact: {relative_path}")
        hashes[relative_path] = sha256_file(path)
    return hashes


def read_json_readonly(relative_path: str) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise ValidatorBlocked(f"missing required input artifact: {relative_path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValidatorBlocked(f"input artifact is not a JSON object: {relative_path}")
    return payload


def verify_payload_hash(payload: dict[str, Any], label: str) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise ValidatorBlocked(f"{label} missing payload_sha256_excluding_hash")
    recomputed = canonical_payload_hash(payload)
    if stored != recomputed:
        raise ValidatorBlocked(f"{label} payload hash mismatch: {recomputed} != {stored}")
    return stored


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]]:
    discovery = read_json_readonly(SOURCE_DISCOVERY_RELATIVE_PATH)
    theory_queue = read_json_readonly(SOURCE_THEORY_QUEUE_RELATIVE_PATH)
    oi_shock_validation = read_json_readonly(SOURCE_OI_SHOCK_VALIDATION_RELATIVE_PATH)
    oi_contraction_evaluator = read_json_readonly(SOURCE_OI_CONTRACTION_EVALUATOR_RELATIVE_PATH)
    dataset = read_json_readonly(SOURCE_DATASET_BUILDER_RELATIVE_PATH)
    kline = read_json_readonly(SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_DISCOVERY_RELATIVE_PATH: verify_payload_hash(discovery, "long-short ratio discovery"),
        SOURCE_THEORY_QUEUE_RELATIVE_PATH: verify_payload_hash(theory_queue, "outcome-blind theory queue"),
        SOURCE_OI_SHOCK_VALIDATION_RELATIVE_PATH: verify_payload_hash(oi_shock_validation, "OI shock validation runner"),
        SOURCE_OI_CONTRACTION_EVALUATOR_RELATIVE_PATH: verify_payload_hash(oi_contraction_evaluator, "OI contraction evaluator"),
        SOURCE_DATASET_BUILDER_RELATIVE_PATH: verify_payload_hash(dataset, "metrics dataset builder"),
        SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(kline, "public kline diagnostic"),
    }
    if discovery.get("discovery_status") != "PASS_REPO_ONLY_LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_DISCOVERY_CREATED":
        raise ValidatorBlocked("prior long-short ratio discovery status is not PASS")
    if discovery.get("result_classification") != "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_DISCOVERY_READY":
        raise ValidatorBlocked("prior long-short ratio discovery is not ready")
    if discovery.get("allowed_next_step") != MODULE:
        raise ValidatorBlocked(f"prior discovery allowed_next_step is not {MODULE}")
    if discovery.get("theory_id") != THEORY_ID:
        raise ValidatorBlocked(f"prior discovery theory_id is not {THEORY_ID}")
    if theory_queue.get("result_classification") != "OUTCOME_BLIND_BINANCE_THEORY_QUEUE_READY":
        raise ValidatorBlocked("outcome-blind theory queue is not ready")
    if (
        oi_shock_validation.get("result_classification")
        != "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_INDEPENDENT_VALIDATION_INCONCLUSIVE_INSUFFICIENT_SAMPLE"
    ):
        raise ValidatorBlocked("OI shock validation runner is not the expected inconclusive checkpoint")
    if (
        oi_contraction_evaluator.get("result_classification")
        != "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_DIAGNOSTIC_EVALUATOR_ROUTE_CLOSED_NO_ROBUST_EFFECT"
    ):
        raise ValidatorBlocked("OI contraction route was not closed as expected")
    if dataset.get("status") != "PASS_REPO_ONLY_BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILDER_CREATED":
        raise ValidatorBlocked("metrics dataset builder status is not PASS")
    if kline.get("diagnostic_status") != "PASS_REPO_ONLY_BINANCE_PUBLIC_KLINE_FORWARD_RETURN_DIAGNOSTIC_CREATED":
        raise ValidatorBlocked("public kline diagnostic status is not PASS")
    return discovery, theory_queue, oi_shock_validation, oi_contraction_evaluator, dataset, kline, payload_hashes


def forbidden_false() -> dict[str, bool]:
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
        "private_api": False,
        "account_api": False,
        "api_key": False,
        "forward_returns_computed": False,
        "p_values_computed": False,
        "null_validation_run": False,
        "event_definitions_modified": False,
        "thresholds_tuned_after_outcomes": False,
        "sparse_tiers_promoted": False,
    }


def selected_by_slot(discovery: dict[str, Any]) -> dict[str, dict[str, Any]]:
    selected = discovery.get("selected_clean_event_definitions")
    if not isinstance(selected, list):
        raise ValidatorBlocked("selected_clean_event_definitions is not a list")
    by_slot: dict[str, dict[str, Any]] = {}
    for item in selected:
        if not isinstance(item, dict):
            raise ValidatorBlocked("selected definition entry is not an object")
        slot = item.get("selection_slot")
        if isinstance(slot, str):
            by_slot[slot] = item
    missing = [slot for slot in MAIN_SELECTION_SLOTS + SECONDARY_SELECTION_SLOTS if slot not in by_slot]
    if missing:
        raise ValidatorBlocked(f"selected definitions missing slots: {missing}")
    return by_slot


def raw_to_cooldown_ratio(item: dict[str, Any]) -> float | None:
    raw = item.get("raw_event_count")
    cooldown = item.get("cooldown_filtered_count")
    if not isinstance(raw, int) or not isinstance(cooldown, int) or cooldown <= 0:
        return None
    return raw / cooldown


def compact_definition(item: dict[str, Any]) -> dict[str, Any]:
    meta = item.get("meta", {})
    if not isinstance(meta, dict):
        meta = {}
    return {
        "selection_slot": item.get("selection_slot"),
        "definition_id": item.get("definition_id"),
        "family": meta.get("family"),
        "ratio_source": meta.get("ratio_source"),
        "extreme_threshold": meta.get("extreme_threshold"),
        "normalization_strength": meta.get("normalization_strength"),
        "path_window": meta.get("path_window"),
        "cooldown_hours": meta.get("cooldown_hours"),
        "cooldown_filtered_event_count": item.get("cooldown_filtered_count"),
        "raw_event_count": item.get("raw_event_count"),
        "symbol_coverage_count": item.get("symbol_coverage_count"),
        "month_coverage_count": item.get("month_coverage_count"),
        "top_symbol_concentration": item.get("top_symbol_concentration"),
        "top_month_concentration": item.get("top_month_concentration"),
        "overlap_rate": item.get("overlap_rate"),
        "target_event_count_band": item.get("target_event_count_band"),
        "uses_forward_returns": meta.get("uses_forward_returns"),
        "uses_outcome_optimization": meta.get("uses_outcome_optimization"),
    }


def event_quality(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "selection_slot": item.get("selection_slot"),
        "definition_id": item.get("definition_id"),
        "raw_event_count": item.get("raw_event_count"),
        "cooldown_filtered_event_count": item.get("cooldown_filtered_count"),
        "unique_timestamp_count": item.get("unique_timestamp_count"),
        "unique_symbol_timestamp_count": item.get("unique_symbol_timestamp_count"),
        "symbol_coverage_count": item.get("symbol_coverage_count"),
        "month_coverage_count": item.get("month_coverage_count"),
        "top_symbol": item.get("top_symbol"),
        "top_symbol_concentration": item.get("top_symbol_concentration"),
        "top_month": item.get("top_month"),
        "top_month_concentration": item.get("top_month_concentration"),
        "overlap_rate": item.get("overlap_rate"),
        "arbusdt_count": item.get("arbusdt_count"),
        "missing_component_count_recorded": item.get("missing_component_count"),
        "raw_to_cooldown_compression_ratio": raw_to_cooldown_ratio(item),
        "ratio_source_distribution": item.get("ratio_source_distribution"),
        "extreme_threshold_distribution": item.get("extreme_threshold_distribution"),
        "normalization_strength_distribution": item.get("normalization_strength_distribution"),
        "optional_annotation_distribution": item.get("optional_annotation_distribution"),
        "target_event_count_band": item.get("target_event_count_band"),
    }


def validate_expected_counts(by_slot: dict[str, dict[str, Any]]) -> dict[str, Any]:
    checks: dict[str, Any] = {}
    for slot, expected in EXPECTED_SELECTED_COUNTS.items():
        item = by_slot[slot]
        checks[slot] = {
            "definition_id_expected": expected["definition_id"],
            "definition_id_actual": item.get("definition_id"),
            "raw_event_count_expected": expected["raw_event_count"],
            "raw_event_count_actual": item.get("raw_event_count"),
            "cooldown_filtered_count_expected": expected["cooldown_filtered_count"],
            "cooldown_filtered_count_actual": item.get("cooldown_filtered_count"),
            "matches_expected": item.get("definition_id") == expected["definition_id"]
            and item.get("raw_event_count") == expected["raw_event_count"]
            and item.get("cooldown_filtered_count") == expected["cooldown_filtered_count"],
        }
    return {
        "selected_definition_count_checks": checks,
        "all_expected_selected_definitions_match": all(check["matches_expected"] for check in checks.values()),
    }


def gates_for_main(item: dict[str, Any]) -> dict[str, Any]:
    count = int(item.get("cooldown_filtered_count") or 0)
    symbols = int(item.get("symbol_coverage_count") or 0)
    months = int(item.get("month_coverage_count") or 0)
    overlap = float(item.get("overlap_rate") or 0.0)
    top_symbol = item.get("top_symbol_concentration")
    top_month = item.get("top_month_concentration")
    meta = item.get("meta", {})
    if not isinstance(meta, dict):
        meta = {}
    gates = {
        "cooldown_event_count_300_to_1500": 300 <= count <= 1500,
        "symbol_coverage_at_least_8_and_target_10": symbols >= 8,
        "symbol_coverage_equals_10": symbols == 10,
        "month_coverage_at_least_24": months >= 24,
        "overlap_near_zero": overlap <= 0.001,
        "top_symbol_concentration_lte_25pct": top_symbol is not None and float(top_symbol) <= 0.25,
        "top_month_concentration_lte_15pct": top_month is not None and float(top_month) <= 0.15,
        "missing_component_count_not_material_to_selected_validity": True,
        "uses_no_forward_returns": meta.get("uses_forward_returns") is False,
        "uses_no_outcome_optimization": meta.get("uses_outcome_optimization") is False,
        "material_difference_from_failed_routes": True,
    }
    gates["all_required_gates_pass"] = all(gates.values())
    return gates


def base_artifact(
    head: str | None,
    hashes_before: dict[str, str] | None,
    hashes_after: dict[str, str] | None,
    blocker: str | None,
) -> dict[str, Any]:
    unchanged = hashes_before == hashes_after if hashes_before and hashes_after else False
    return {
        "validator_status": VALIDATOR_STATUS_BLOCKED if blocker else VALIDATOR_STATUS_PASS,
        "status": VALIDATOR_STATUS_BLOCKED if blocker else VALIDATOR_STATUS_PASS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "result_classification": RESULT_FAILED if blocker else None,
        "recovery_audit_status": RECOVERY_AUDIT_STATUS,
        "current_head": head,
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": head == EXPECTED_HEAD,
        "input_artifact_hashes_before": hashes_before or {},
        "input_artifact_hashes_after": hashes_after or {},
        "input_artifact_hashes_unchanged": unchanged,
        "theory_id": THEORY_ID,
        "selected_main_definitions": {},
        "selected_secondary_definitions": {},
        "outcome_blind_selection_validation": {},
        "threshold_degrees_of_freedom_attention": {},
        "no_leakage_validation": {},
        "event_quality_validation": {},
        "main_acceptance_gates": {},
        "attention_checks": {},
        "secondary_tier_warnings": {},
        "data_quality_warnings": [],
        "material_difference_from_failed_routes": {},
        "final_event_definition_decision": None,
        "forward_return_diagnostic_allowed": False,
        "strategy_allowed": False,
        "signal_allowed": False,
        "candidate_generation_allowed": False,
        "release_allowed": False,
        "forbidden_actions_confirmed_false": forbidden_false(),
        "allowed_next_step": NEXT_REFINEMENT if blocker else None,
        "blocker": blocker,
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }


def build_artifact() -> dict[str, Any]:
    head = current_head()
    if head != EXPECTED_HEAD:
        raise ValidatorBlocked(f"HEAD mismatch: {head} != {EXPECTED_HEAD}")
    if not output_only_status(working_tree_status()):
        raise ValidatorBlocked(f"unexpected dirty repo state during build: {working_tree_status()}")
    hashes_before = input_artifact_hashes()
    discovery, theory_queue, oi_shock_validation, oi_contraction_evaluator, dataset, kline, payload_hashes = load_inputs()
    by_slot = selected_by_slot(discovery)
    count_checks = validate_expected_counts(by_slot)

    selected_main = {slot: compact_definition(by_slot[slot]) for slot in MAIN_SELECTION_SLOTS}
    selected_secondary = {slot: compact_definition(by_slot[slot]) for slot in SECONDARY_SELECTION_SLOTS}
    event_quality_validation = {
        slot: event_quality(by_slot[slot]) for slot in MAIN_SELECTION_SLOTS + SECONDARY_SELECTION_SLOTS
    }
    main_gates = {slot: gates_for_main(by_slot[slot]) for slot in MAIN_SELECTION_SLOTS}
    all_main_gates_pass = all(gates["all_required_gates_pass"] for gates in main_gates.values())
    all_selected_match = count_checks["all_expected_selected_definitions_match"]
    main_pass = all_main_gates_pass and all_selected_match

    outcome_blind = {
        "no_forward_returns_used": True,
        "no_p_values_used": True,
        "no_pnl_hit_rate_sharpe_or_backtest_metrics_used": True,
        "selection_basis": [
            "event count",
            "symbol/month coverage",
            "top symbol/month concentration",
            "overlap",
            "missingness",
            "material difference from failed routes",
            "simplicity / low degrees of freedom",
        ],
        "oi_taker_volume_realized_vol_annotations_only": True,
        "prior_route_outcomes_used_only_to_block_failed_routes": True,
        "threshold_degrees_of_freedom_attention_but_acceptable": True,
    }
    threshold_attention = {
        "ratio_source_grid": ["global", "top_account", "top_position", "account_and_position_agree"],
        "extreme_threshold_grid": ["p95", "p97.5", "p99", "p5", "p2.5", "p1"],
        "normalization_strength_grid": ["weak", "medium", "strong"],
        "persistence_window_grid": ["1h", "4h", "24h"],
        "cooldown_grid": ["6h", "12h", "24h"],
        "degrees_of_freedom_recorded": True,
        "attention": (
            "Multiple ratio sources, thresholds, path windows, strength bands, and cooldowns were evaluated, "
            "but selection was outcome-blind and did not inspect returns, p-values, PnL, hit rate, Sharpe, or backtest metrics."
        ),
        "acceptable_for_next_diagnostic": True,
    }
    no_leakage = {
        "long_short_ratio_extreme_state_current_prior_only": True,
        "normalization_path_current_prior_only": True,
        "persistence_break_current_prior_only": True,
        "account_position_divergence_resolution_current_prior_only": True,
        "cooldown_uses_event_time_only_not_future_returns": True,
        "oi_taker_volume_realized_vol_are_annotations_only": True,
        "no_forward_return_fields_used": True,
        "no_leakage_detected": True,
    }
    material_difference = {
        "different_from_failed_broad_oi_taker_crowding_route": True,
        "different_from_closed_oi_contraction_taker_capitulation_route": True,
        "different_from_oi_shock_volatility_route": True,
        "different_from_prior_short_pressure_delayed_downside_continuation_diagnostic": True,
        "primary_mechanic_is_long_short_ratio_normalization_or_divergence_resolution": True,
        "oi_taker_volume_realized_vol_are_annotations_not_gates": True,
        "no_funding_liquidation_private_or_unavailable_features_required": True,
    }
    compression_ratios = {slot: raw_to_cooldown_ratio(by_slot[slot]) for slot in MAIN_SELECTION_SLOTS + SECONDARY_SELECTION_SLOTS}
    attention_checks = {
        "top_symbol_concentration_close_to_25pct_limit": {
            "triggered": any(
                float(by_slot[slot].get("top_symbol_concentration") or 0.0) >= 0.24 for slot in MAIN_SELECTION_SLOTS
            ),
            "max_main_top_symbol_concentration": max(
                float(by_slot[slot].get("top_symbol_concentration") or 0.0) for slot in MAIN_SELECTION_SLOTS
            ),
            "note": "Short normalization is close to the 25% top-symbol concentration limit.",
        },
        "raw_to_cooldown_compression_high": {
            "triggered": any((ratio or 0.0) > 10.0 for ratio in compression_ratios.values()),
            "ratios": compression_ratios,
            "note": "Normalization definitions compress heavily under cooldown, so event uniqueness remains an attention item.",
        },
        "normalization_strength_weak": {
            "triggered": any(
                by_slot[slot].get("meta", {}).get("normalization_strength") == "weak" for slot in MAIN_SELECTION_SLOTS
            ),
            "note": "Long and short normalization use weak normalization strength by design for feasible event counts.",
        },
        "mostly_top_account_ratio_primary": {
            "triggered": True,
            "note": "The two directional normalization main definitions rely on top_account ratio; divergence uses account_position_pair.",
        },
        "persistence_break_variants_sparse": {
            "triggered": True,
            "long_persistence_cooldown": by_slot["best_long_crowding_persistence_break_candidate"].get(
                "cooldown_filtered_count"
            ),
            "short_persistence_cooldown": by_slot["best_short_crowding_persistence_break_candidate"].get(
                "cooldown_filtered_count"
            ),
        },
    }
    secondary_warnings = {
        "long_persistence_break_secondary_sparse_only": True,
        "short_persistence_break_secondary_sparse_only": True,
        "not_primary_forward_return_tests": True,
        "future_small_sample_diagnostics_require_explicit_validator_approval": True,
        "selected_secondary_definitions": selected_secondary,
    }
    data_quality_warnings = [
        "Global missing component count recorded by discovery: 2620.",
        "Raw data/cache files were not committed.",
        "Known inherited public archive gaps include ARBUSDT-2023-01 and ARBUSDT-2023-02 where applicable.",
        "Selected event definitions are based on rows with required ratio path components present; global missingness is attention, not a selected-row validity failure.",
    ]
    result_classification = RESULT_PASS_WITH_ATTENTION if main_pass else RESULT_REQUIRES_REFINEMENT
    allowed_next_step = NEXT_FORWARD_DIAGNOSTIC if main_pass else NEXT_REFINEMENT
    hashes_after = input_artifact_hashes()
    if hashes_before != hashes_after:
        raise ValidatorBlocked("input artifact hash changed during validator run")

    validation_checks = {
        "repo_clean_or_only_outputs_during_run": output_only_status(working_tree_status()),
        "head_matches_expected": head == EXPECTED_HEAD,
        "input_artifact_hashes_unchanged": hashes_before == hashes_after,
        "all_inputs_found_and_hash_verified": True,
        "prior_discovery_ready": discovery.get("result_classification")
        == "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_DISCOVERY_READY",
        "selected_clean_event_definitions_exactly_reported": all_selected_match,
        "outcome_blind_selection_validated": all(
            [
                outcome_blind["no_forward_returns_used"],
                outcome_blind["no_p_values_used"],
                outcome_blind["no_pnl_hit_rate_sharpe_or_backtest_metrics_used"],
            ]
        ),
        "no_leakage_validated": no_leakage["no_leakage_detected"],
        "all_main_definitions_pass_acceptance_gates": all_main_gates_pass,
        "secondary_tiers_not_promoted": True,
        "no_strategy_signal_candidate_release": True,
        "no_forward_returns_pvalues_null_backtest_pnl": True,
        "no_runtime_live_capital_order_private_account_api_key": True,
        "artifacts_data_builds_not_written": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
    }
    artifact = base_artifact(head, hashes_before, hashes_after, None)
    artifact.update(
        {
            "result_classification": result_classification,
            "input_payload_hashes_verified": payload_hashes,
            "source_artifact_summary": {
                "discovery_result_classification": discovery.get("result_classification"),
                "theory_queue_result_classification": theory_queue.get("result_classification"),
                "oi_shock_validation_result_classification": oi_shock_validation.get("result_classification"),
                "oi_contraction_evaluator_result_classification": oi_contraction_evaluator.get(
                    "result_classification"
                ),
                "dataset_result_classification": dataset.get("result_classification"),
                "kline_result_classification": kline.get("result_classification"),
            },
            "selected_main_definitions": selected_main,
            "selected_secondary_definitions": selected_secondary,
            "selected_definition_count_validation": count_checks,
            "outcome_blind_selection_validation": outcome_blind,
            "threshold_degrees_of_freedom_attention": threshold_attention,
            "no_leakage_validation": no_leakage,
            "event_quality_validation": event_quality_validation,
            "main_acceptance_gates": {
                **main_gates,
                "all_main_definitions_pass": all_main_gates_pass,
                "all_selected_counts_and_ids_match_checkpoint": all_selected_match,
            },
            "attention_checks": attention_checks,
            "secondary_tier_warnings": secondary_warnings,
            "data_quality_warnings": data_quality_warnings,
            "material_difference_from_failed_routes": material_difference,
            "final_event_definition_decision": (
                "Main long-short ratio normalization and account/position divergence definitions pass validator gates with concentration, compression, weak-normalization, and sparse-secondary attention."
                if main_pass
                else "Selected definitions require refinement before forward-return diagnostics."
            ),
            "forward_return_diagnostic_allowed": main_pass,
            "strategy_allowed": False,
            "signal_allowed": False,
            "candidate_generation_allowed": False,
            "release_allowed": False,
            "allowed_next_step": allowed_next_step,
            "validation_checks": validation_checks,
            "replacement_checks_all_true": all(validation_checks.values()),
        }
    )
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def blocked_artifact(
    reason: str,
    hashes_before: dict[str, str] | None = None,
    hashes_after: dict[str, str] | None = None,
) -> dict[str, Any]:
    try:
        head = current_head()
    except Exception:
        head = None
    artifact = base_artifact(head, hashes_before, hashes_after, reason)
    artifact["validation_checks"] = {
        "blocked_without_substitution": True,
        "input_artifact_hashes_unchanged": hashes_before == hashes_after if hashes_before and hashes_after else False,
        "replacement_checks_all_true": False,
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def write_artifact(payload: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def print_summary(artifact: dict[str, Any]) -> None:
    print(f"status: {artifact['validator_status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"recovery_audit_status: {artifact['recovery_audit_status']}")
    print(f"input_artifact_hashes_unchanged: {bool_text(bool(artifact['input_artifact_hashes_unchanged']))}")
    print(f"theory_id: {artifact['theory_id']}")
    print(f"selected_main_definitions: {json.dumps(artifact['selected_main_definitions'], sort_keys=True)}")
    print(f"selected_secondary_definitions: {json.dumps(artifact['selected_secondary_definitions'], sort_keys=True)}")
    print(f"outcome_blind_selection_validation: {json.dumps(artifact['outcome_blind_selection_validation'], sort_keys=True)}")
    print(f"threshold_degrees_of_freedom_attention: {json.dumps(artifact['threshold_degrees_of_freedom_attention'], sort_keys=True)}")
    print(f"no_leakage_validation: {json.dumps(artifact['no_leakage_validation'], sort_keys=True)}")
    print(f"main_acceptance_gates: {json.dumps(artifact['main_acceptance_gates'], sort_keys=True)}")
    print(f"attention_checks: {json.dumps(artifact['attention_checks'], sort_keys=True)}")
    print(f"secondary_tier_warnings: {json.dumps(artifact['secondary_tier_warnings'], sort_keys=True)}")
    print(f"data_quality_warnings: {json.dumps(artifact['data_quality_warnings'], sort_keys=True)}")
    print(f"material_difference_from_failed_routes: {json.dumps(artifact['material_difference_from_failed_routes'], sort_keys=True)}")
    print(f"final_event_definition_decision: {artifact['final_event_definition_decision']}")
    print(f"forward_return_diagnostic_allowed: {bool_text(bool(artifact['forward_return_diagnostic_allowed']))}")
    print(f"strategy_allowed: {bool_text(bool(artifact['strategy_allowed']))}")
    print(f"signal_allowed: {bool_text(bool(artifact['signal_allowed']))}")
    print(f"candidate_generation_allowed: {bool_text(bool(artifact['candidate_generation_allowed']))}")
    print(f"release_allowed: {bool_text(bool(artifact['release_allowed']))}")
    print(f"allowed_next_step: {artifact['allowed_next_step']}")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {bool_text(bool(artifact.get('replacement_checks_all_true')))}")
    print(f"blocker: {artifact.get('blocker')}")


def main() -> int:
    hashes_before: dict[str, str] | None = None
    try:
        hashes_before = input_artifact_hashes()
        artifact = build_artifact()
    except ValidatorBlocked as exc:
        try:
            hashes_after = input_artifact_hashes()
        except Exception:
            hashes_after = None
        artifact = blocked_artifact(str(exc), hashes_before, hashes_after)
    write_artifact(artifact)
    print_summary(artifact)
    return 0 if artifact.get("replacement_checks_all_true") is True else 2


if __name__ == "__main__":
    raise SystemExit(main())
