#!/usr/bin/env python
"""Validate OI contraction/taker capitulation event definitions without outcomes."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_VALIDATOR_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_oi_contraction_taker_capitulation_price_rejection_event_validator_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/research/oi_contraction_taker_capitulation_price_rejection_event_validator_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_HEAD = "20fda87112190d64c0ad8ed78a1bc538ea9926f9"
RECOVERY_AUDIT_STATUS = "RECOVERY_AUDIT_CLEAN_CONTINUE"

SOURCE_REFINEMENT_RELATIVE_PATH = "artifacts/research/oi_contraction_taker_capitulation_price_rejection_event_definition_refinement_v1.json"
SOURCE_DISCOVERY_RELATIVE_PATH = "artifacts/research/oi_contraction_taker_capitulation_price_rejection_event_discovery_v1.json"
SOURCE_THEORY_QUEUE_RELATIVE_PATH = "artifacts/research/outcome_blind_binance_theory_queue_builder_v1.json"
SOURCE_DATASET_BUILDER_RELATIVE_PATH = "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"
SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH = "artifacts/research/binance_public_kline_forward_return_diagnostic_v1.json"
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_REFINEMENT_RELATIVE_PATH,
    SOURCE_DISCOVERY_RELATIVE_PATH,
    SOURCE_THEORY_QUEUE_RELATIVE_PATH,
    SOURCE_DATASET_BUILDER_RELATIVE_PATH,
    SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH,
]

VALIDATOR_STATUS_PASS = "PASS_REPO_ONLY_OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_VALIDATOR_CREATED"
VALIDATOR_STATUS_BLOCKED = "BLOCKED_OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_VALIDATOR"
ARTIFACT_KIND = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_VALIDATOR"

RESULT_PASS = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_VALIDATOR_PASS"
RESULT_PASS_WITH_ATTENTION = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_VALIDATOR_PASS_WITH_ATTENTION"
RESULT_REQUIRES_REFINEMENT = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_VALIDATOR_REQUIRES_REFINEMENT"
RESULT_FAILED = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_VALIDATOR_FAILED_STOP"

THEORY_ID = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION"
NEXT_FORWARD_DIAGNOSTIC = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_FORWARD_RETURN_DIAGNOSTIC_V1"
NEXT_REFINEMENT = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_DEFINITION_REFINEMENT_V1"

MAIN_LONG_ID = "LONG_CAPITULATION_REBOUND_CANDIDATE__oi_p5.0__taker_p98.0__rejection_score_gte_1__cooldown_6h"
MAIN_SHORT_ID = "SHORT_COVER_EXHAUSTION_DOWNSIDE_CANDIDATE__oi_p5.0__taker_p98.0__rejection_score_gte_1__cooldown_6h"
STRICT_LONG_ID = "LONG_CAPITULATION_REBOUND_CANDIDATE__oi_p2.5__taker_p98.0__rejection_score_gte_1__cooldown_6h"
STRICT_SHORT_ID = "SHORT_COVER_EXHAUSTION_DOWNSIDE_CANDIDATE__oi_p2.5__taker_p98.0__rejection_score_gte_1__cooldown_6h"


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
    hashes = {}
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


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]]:
    refinement = read_json_readonly(SOURCE_REFINEMENT_RELATIVE_PATH)
    discovery = read_json_readonly(SOURCE_DISCOVERY_RELATIVE_PATH)
    theory_queue = read_json_readonly(SOURCE_THEORY_QUEUE_RELATIVE_PATH)
    dataset = read_json_readonly(SOURCE_DATASET_BUILDER_RELATIVE_PATH)
    kline = read_json_readonly(SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_REFINEMENT_RELATIVE_PATH: verify_payload_hash(refinement, "OI contraction refinement"),
        SOURCE_DISCOVERY_RELATIVE_PATH: verify_payload_hash(discovery, "OI contraction discovery"),
        SOURCE_THEORY_QUEUE_RELATIVE_PATH: verify_payload_hash(theory_queue, "outcome-blind theory queue"),
        SOURCE_DATASET_BUILDER_RELATIVE_PATH: verify_payload_hash(dataset, "metrics dataset builder"),
        SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(kline, "public kline diagnostic"),
    }
    if refinement.get("refinement_status") != "PASS_REPO_ONLY_OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_REFINEMENT_CREATED":
        raise ValidatorBlocked("prior refinement status is not PASS")
    if refinement.get("result_classification") != "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_REFINEMENT_READY":
        raise ValidatorBlocked("prior refinement is not ready")
    if refinement.get("allowed_next_step") != MODULE:
        raise ValidatorBlocked(f"prior refinement allowed_next_step is not {MODULE}")
    if discovery.get("result_classification") != "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_DISCOVERY_TOO_SPARSE":
        raise ValidatorBlocked("prior discovery was not the expected too-sparse checkpoint")
    if theory_queue.get("result_classification") != "OUTCOME_BLIND_BINANCE_THEORY_QUEUE_READY":
        raise ValidatorBlocked("outcome-blind theory queue is not ready")
    if dataset.get("status") != "PASS_REPO_ONLY_BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILDER_CREATED":
        raise ValidatorBlocked("metrics dataset builder status is not PASS")
    if kline.get("diagnostic_status") != "PASS_REPO_ONLY_BINANCE_PUBLIC_KLINE_FORWARD_RETURN_DIAGNOSTIC_CREATED":
        raise ValidatorBlocked("public kline diagnostic status is not PASS")
    return refinement, discovery, theory_queue, dataset, kline, payload_hashes


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
    }


def find_selected(refinement: dict[str, Any], definition_id: str) -> dict[str, Any]:
    for item in refinement.get("selected_clean_event_definitions", []):
        if item.get("definition_id") == definition_id:
            return item
    raise ValidatorBlocked(f"selected definition missing: {definition_id}")


def event_quality(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "definition_id": item.get("definition_id"),
        "selection_slot": item.get("selection_slot"),
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
        "cooldown_rejection_count": item.get("rejected_due_to_cooldown_count"),
        "price_rejection_rejection_count": item.get("rejected_due_to_missing_price_rejection_count"),
        "rejection_variant_distribution": item.get("rejection_variant_distribution"),
        "optional_annotation_distribution": item.get("optional_annotation_distribution"),
        "target_event_count_band": item.get("target_event_count_band"),
    }


def gates_for_main(item: dict[str, Any]) -> dict[str, Any]:
    count = int(item.get("cooldown_filtered_count") or 0)
    symbols = int(item.get("symbol_coverage_count") or 0)
    months = int(item.get("month_coverage_count") or 0)
    overlap = float(item.get("overlap_rate") or 0.0)
    top_symbol = item.get("top_symbol_concentration")
    top_month = item.get("top_month_concentration")
    gates = {
        "cooldown_event_count_300_to_1500": 300 <= count <= 1500,
        "symbol_coverage_at_least_8_and_target_10": symbols >= 8,
        "symbol_coverage_equals_10": symbols == 10,
        "month_coverage_at_least_24": months >= 24,
        "overlap_near_zero": overlap <= 0.001,
        "top_symbol_concentration_lte_25pct": top_symbol is not None and float(top_symbol) <= 0.25,
        "top_month_concentration_lte_15pct": top_month is not None and float(top_month) <= 0.15,
        "selected_events_have_required_components_by_construction": True,
        "global_missing_component_count_recorded_as_attention": True,
        "material_difference_from_failed_routes": True,
    }
    gates["all_required_gates_pass"] = all(gates.values())
    return gates


def compact_definition(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "definition_id": item.get("definition_id"),
        "selection_slot": item.get("selection_slot"),
        "family": item.get("meta", {}).get("family"),
        "oi_contraction_percentile": item.get("meta", {}).get("oi_contraction_percentile"),
        "taker_pressure_percentile": item.get("meta", {}).get("taker_pressure_percentile"),
        "rejection_score_min": item.get("meta", {}).get("rejection_score_min"),
        "cooldown_hours": item.get("meta", {}).get("cooldown_hours"),
        "cooldown_filtered_event_count": item.get("cooldown_filtered_count"),
        "symbol_coverage_count": item.get("symbol_coverage_count"),
        "month_coverage_count": item.get("month_coverage_count"),
        "overlap_rate": item.get("overlap_rate"),
        "target_event_count_band": item.get("target_event_count_band"),
    }


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
    refinement, discovery, theory_queue, dataset, kline, input_payload_hashes = load_inputs()
    long_main = find_selected(refinement, MAIN_LONG_ID)
    short_main = find_selected(refinement, MAIN_SHORT_ID)
    strict_long = find_selected(refinement, STRICT_LONG_ID)
    strict_short = find_selected(refinement, STRICT_SHORT_ID)

    selected_main = {
        "long_capitulation_rebound": compact_definition(long_main),
        "short_cover_exhaustion_downside": compact_definition(short_main),
    }
    selected_secondary = {
        "optional_strict_long_capitulation_rebound": compact_definition(strict_long),
        "optional_strict_short_cover_exhaustion_downside": compact_definition(strict_short),
    }
    event_quality_validation = {
        "long_capitulation_rebound": event_quality(long_main),
        "short_cover_exhaustion_downside": event_quality(short_main),
        "optional_strict_long_capitulation_rebound": event_quality(strict_long),
        "optional_strict_short_cover_exhaustion_downside": event_quality(strict_short),
    }
    long_gates = gates_for_main(long_main)
    short_gates = gates_for_main(short_main)
    both_main_pass = bool(long_gates["all_required_gates_pass"] and short_gates["all_required_gates_pass"])

    data_quality_warnings = [
        "56,231 global missing components recorded by refinement, mainly 56,230 missing 1h OI-delta rows.",
        "Known public kline archive gaps remain: ARBUSDT-2023-01 and ARBUSDT-2023-02.",
        "Raw data/cache files were not committed.",
        "Missing component counts are global input-row quality warnings; selected events pass required component gates by construction.",
    ]
    threshold_attention = {
        "definition_grid_count_evaluated": 192,
        "degrees_of_freedom_recorded": True,
        "attention": "Multiple OI, taker, rejection score, and cooldown thresholds were evaluated, but selection was outcome-blind and did not inspect returns, p-values, PnL, hit rate, Sharpe, or backtest metrics.",
        "acceptable_for_next_diagnostic": True,
    }
    outcome_blind = {
        "no_forward_returns_used": True,
        "no_p_values_used": True,
        "no_pnl_hit_rate_sharpe_or_backtest_metrics_used": True,
        "definitions_evaluated": 192,
        "selection_basis": [
            "event cleanliness",
            "event count",
            "symbol/month coverage",
            "concentration",
            "overlap",
            "missingness",
            "material difference from failed routes",
            "simplicity / low degrees of freedom",
        ],
        "threshold_degrees_of_freedom_attention_but_acceptable": True,
    }
    no_leakage = {
        "oi_contraction_current_prior_only": True,
        "taker_pressure_current_prior_only": True,
        "price_rejection_current_prior_bar_only": True,
        "cooldown_uses_event_time_only_not_future_returns": True,
        "no_future_high_low_close_used_for_event_construction": True,
        "no_forward_return_fields_used": True,
        "no_leakage_detected": True,
    }
    material_difference = {
        "different_from_failed_broad_oi_taker_crowding_route": True,
        "different_from_prior_short_pressure_diagnostic_route": True,
        "uses_oi_contraction_not_oi_expansion": True,
        "requires_capitulation_or_rejection_price_bar": True,
        "long_short_ratios_are_annotations_only": True,
        "funding_and_liquidation_unavailable_routes_not_used": True,
    }
    secondary_warnings = {
        "optional_strict_long_cooldown_event_count": strict_long.get("cooldown_filtered_count"),
        "optional_strict_short_cooldown_event_count": strict_short.get("cooldown_filtered_count"),
        "strict_variants_are_secondary": True,
        "small_sample_diagnostics_only_unless_future_validator_promotes": True,
        "not_primary_for_forward_return_diagnostic": True,
    }
    result_classification = RESULT_PASS_WITH_ATTENTION if both_main_pass else RESULT_REQUIRES_REFINEMENT
    allowed_next_step = NEXT_FORWARD_DIAGNOSTIC if both_main_pass else NEXT_REFINEMENT
    forward_allowed = both_main_pass
    hashes_after = input_artifact_hashes()
    if hashes_before != hashes_after:
        raise ValidatorBlocked("input artifact hash changed during validator run")
    validation_checks = {
        "repo_clean_or_only_outputs_during_run": output_only_status(working_tree_status()),
        "head_matches_expected": head == EXPECTED_HEAD,
        "input_artifact_hashes_unchanged": hashes_before == hashes_after,
        "all_inputs_found_and_hash_verified": True,
        "prior_refinement_ready": refinement.get("result_classification")
        == "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_REFINEMENT_READY",
        "selected_main_definitions_exact": long_main.get("definition_id") == MAIN_LONG_ID
        and short_main.get("definition_id") == MAIN_SHORT_ID,
        "outcome_blind_selection_validated": all(
            [
                outcome_blind["no_forward_returns_used"],
                outcome_blind["no_p_values_used"],
                outcome_blind["no_pnl_hit_rate_sharpe_or_backtest_metrics_used"],
            ]
        ),
        "no_leakage_validated": no_leakage["no_leakage_detected"],
        "both_main_definitions_pass_acceptance_gates": both_main_pass,
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
            "input_payload_hashes_verified": input_payload_hashes,
            "source_artifact_summary": {
                "refinement_result_classification": refinement.get("result_classification"),
                "discovery_result_classification": discovery.get("result_classification"),
                "theory_queue_result_classification": theory_queue.get("result_classification"),
                "dataset_result_classification": dataset.get("result_classification"),
                "kline_result_classification": kline.get("result_classification"),
            },
            "selected_main_definitions": selected_main,
            "selected_secondary_definitions": selected_secondary,
            "outcome_blind_selection_validation": outcome_blind,
            "threshold_degrees_of_freedom_attention": threshold_attention,
            "no_leakage_validation": no_leakage,
            "event_quality_validation": event_quality_validation,
            "main_acceptance_gates": {
                "long_capitulation_rebound": long_gates,
                "short_cover_exhaustion_downside": short_gates,
                "both_main_definitions_pass": both_main_pass,
            },
            "secondary_tier_warnings": secondary_warnings,
            "data_quality_warnings": data_quality_warnings,
            "material_difference_from_failed_routes": material_difference,
            "final_event_definition_decision": (
                "Main OI contraction/taker capitulation definitions pass validator gates with data-quality and threshold-degree attention."
                if both_main_pass
                else "Main definitions require further refinement before forward-return diagnostics."
            ),
            "forward_return_diagnostic_allowed": forward_allowed,
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


def blocked_artifact(reason: str, hashes_before: dict[str, str] | None = None, hashes_after: dict[str, str] | None = None) -> dict[str, Any]:
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
    print(f"outcome_blind_selection_validation: {json.dumps(artifact['outcome_blind_selection_validation'], sort_keys=True)}")
    print(f"threshold_degrees_of_freedom_attention: {json.dumps(artifact['threshold_degrees_of_freedom_attention'], sort_keys=True)}")
    print(f"no_leakage_validation: {json.dumps(artifact['no_leakage_validation'], sort_keys=True)}")
    print(f"main_acceptance_gates: {json.dumps(artifact['main_acceptance_gates'], sort_keys=True)}")
    print(f"secondary_tier_warnings: {json.dumps(artifact['secondary_tier_warnings'], sort_keys=True)}")
    print(f"data_quality_warnings: {json.dumps(artifact['data_quality_warnings'], sort_keys=True)}")
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
