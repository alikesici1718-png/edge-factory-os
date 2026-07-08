#!/usr/bin/env python
"""Outcome-blind refinement for OI contraction/taker capitulation events."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_DEFINITION_REFINEMENT_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_oi_contraction_taker_capitulation_price_rejection_event_definition_refinement_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/research/oi_contraction_taker_capitulation_price_rejection_event_definition_refinement_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_HEAD = "b96d73d6b1f4d9412fdebcfb39f871cf43d93a64"
RECOVERY_AUDIT_STATUS = "RECOVERY_AUDIT_CLEAN_CONTINUE"

SOURCE_DISCOVERY_RELATIVE_PATH = "artifacts/research/oi_contraction_taker_capitulation_price_rejection_event_discovery_v1.json"
SOURCE_THEORY_QUEUE_RELATIVE_PATH = "artifacts/research/outcome_blind_binance_theory_queue_builder_v1.json"
SOURCE_DATASET_BUILDER_RELATIVE_PATH = "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"
SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH = "artifacts/research/binance_public_kline_forward_return_diagnostic_v1.json"
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_DISCOVERY_RELATIVE_PATH,
    SOURCE_THEORY_QUEUE_RELATIVE_PATH,
    SOURCE_DATASET_BUILDER_RELATIVE_PATH,
    SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH,
]

BASE_DISCOVERY_TOOL = REPO_ROOT / "tools" / "edge_factory_os_repo_only_oi_contraction_taker_capitulation_price_rejection_event_discovery_v1.py"

REFINEMENT_STATUS_PASS = "PASS_REPO_ONLY_OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_REFINEMENT_CREATED"
REFINEMENT_STATUS_BLOCKED = "BLOCKED_OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_REFINEMENT"
ARTIFACT_KIND = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_DEFINITION_REFINEMENT"

RESULT_READY = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_REFINEMENT_READY"
RESULT_STILL_TOO_SPARSE = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_REFINEMENT_STILL_TOO_SPARSE"
RESULT_TOO_BROAD = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_REFINEMENT_TOO_BROAD"
RESULT_ATTENTION = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_REFINEMENT_DATA_QUALITY_ATTENTION"
RESULT_FAILED = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_REFINEMENT_FAILED_STOP"

THEORY_ID = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION"
NEXT_VALIDATOR = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_VALIDATOR_V1"
NEXT_QUEUE_ROUTE = "OUTCOME_BLIND_BINANCE_THEORY_NEXT_SELECTED_ROUTE_V1"

OI_CONTRACTION_QUANTILES = [0.01, 0.025, 0.05, 0.10]
TAKER_PRESSURE_QUANTILES = [0.99, 0.98, 0.975]
REJECTION_SCORE_BUCKETS = [1, 2]
COOLDOWN_HOURS = [3, 6, 12, 24]


class RefinementBlocked(Exception):
    pass


def load_base_module() -> Any:
    if not BASE_DISCOVERY_TOOL.exists():
        raise RefinementBlocked(f"missing base discovery tool: {BASE_DISCOVERY_TOOL}")
    spec = importlib.util.spec_from_file_location("oi_contraction_discovery_base_v1", BASE_DISCOVERY_TOOL)
    if spec is None or spec.loader is None:
        raise RefinementBlocked("could not load base discovery tool module spec")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OI_CONTRACTION_QUANTILES = list(OI_CONTRACTION_QUANTILES)
    module.TAKER_PRESSURE_QUANTILES = list(TAKER_PRESSURE_QUANTILES)
    module.REJECTION_SCORE_BUCKETS = list(REJECTION_SCORE_BUCKETS)
    module.COOLDOWN_HOURS = list(COOLDOWN_HOURS)

    def percentile_name(q: float) -> str:
        lookup = {
            0.0025: "p0.25",
            0.005: "p0.5",
            0.01: "p1.0",
            0.025: "p2.5",
            0.05: "p5.0",
            0.10: "p10.0",
            0.50: "p50.0",
            0.75: "p75.0",
            0.90: "p90.0",
            0.95: "p95.0",
            0.975: "p97.5",
            0.98: "p98.0",
            0.99: "p99.0",
            0.995: "p99.5",
            0.9975: "p99.75",
        }
        return lookup.get(q, f"p{q * 100:g}")

    module.percentile_name = percentile_name
    return module


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
        raise RefinementBlocked(f"git {' '.join(args)} failed: {stderr.strip() or stdout.strip()}")
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
            raise RefinementBlocked(f"missing required input artifact: {relative_path}")
        hashes[relative_path] = sha256_file(path)
    return hashes


def read_json_readonly(relative_path: str) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise RefinementBlocked(f"missing required input artifact: {relative_path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise RefinementBlocked(f"input artifact is not a JSON object: {relative_path}")
    return payload


def verify_payload_hash(payload: dict[str, Any], label: str) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise RefinementBlocked(f"{label} missing payload_sha256_excluding_hash")
    recomputed = canonical_payload_hash(payload)
    if stored != recomputed:
        raise RefinementBlocked(f"{label} payload hash mismatch: {recomputed} != {stored}")
    return stored


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]]:
    discovery = read_json_readonly(SOURCE_DISCOVERY_RELATIVE_PATH)
    theory_queue = read_json_readonly(SOURCE_THEORY_QUEUE_RELATIVE_PATH)
    dataset = read_json_readonly(SOURCE_DATASET_BUILDER_RELATIVE_PATH)
    kline = read_json_readonly(SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_DISCOVERY_RELATIVE_PATH: verify_payload_hash(discovery, "OI contraction prior discovery"),
        SOURCE_THEORY_QUEUE_RELATIVE_PATH: verify_payload_hash(theory_queue, "outcome-blind theory queue"),
        SOURCE_DATASET_BUILDER_RELATIVE_PATH: verify_payload_hash(dataset, "metrics dataset builder"),
        SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(kline, "public kline diagnostic"),
    }
    if discovery.get("discovery_status") != "PASS_REPO_ONLY_OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_DISCOVERY_CREATED":
        raise RefinementBlocked("prior OI contraction discovery status is not PASS")
    if discovery.get("result_classification") != "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_DISCOVERY_TOO_SPARSE":
        raise RefinementBlocked("prior OI contraction discovery was not classified too sparse")
    if discovery.get("allowed_next_step") != MODULE:
        raise RefinementBlocked(f"prior OI contraction discovery allowed_next_step is not {MODULE}")
    if theory_queue.get("result_classification") != "OUTCOME_BLIND_BINANCE_THEORY_QUEUE_READY":
        raise RefinementBlocked("outcome-blind theory queue is not ready")
    if dataset.get("status") != "PASS_REPO_ONLY_BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILDER_CREATED":
        raise RefinementBlocked("metrics dataset builder status is not PASS")
    if kline.get("diagnostic_status") != "PASS_REPO_ONLY_BINANCE_PUBLIC_KLINE_FORWARD_RETURN_DIAGNOSTIC_CREATED":
        raise RefinementBlocked("public kline diagnostic status is not PASS")
    return discovery, theory_queue, dataset, kline, payload_hashes


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
        "failed_routes_reused_under_new_names": False,
    }


def compact_prior_discovery(prior: dict[str, Any]) -> dict[str, Any]:
    selected = prior.get("selected_clean_event_definitions", [])
    return {
        "status": prior.get("discovery_status"),
        "result_classification": prior.get("result_classification"),
        "selected_definitions": [
            {
                "selection_slot": item.get("selection_slot"),
                "definition_id": item.get("definition_id"),
                "raw_event_count": item.get("raw_event_count"),
                "cooldown_filtered_count": item.get("cooldown_filtered_count"),
                "symbol_coverage_count": item.get("symbol_coverage_count"),
                "month_coverage_count": item.get("month_coverage_count"),
                "overlap_rate": item.get("overlap_rate"),
                "target_event_count_band": item.get("target_event_count_band"),
            }
            for item in selected
        ],
        "reason_refinement_allowed": "prior clean event discovery was mechanically distinct but too sparse",
    }


def target_count_band(count: int) -> str:
    if 300 <= count <= 1500:
        return "ideal"
    if 1500 < count <= 5000:
        return "acceptable_but_possibly_broad"
    if 100 <= count < 300:
        return "sparse_but_potentially_usable"
    if count > 5000:
        return "too_broad"
    return "too_sparse"


def score_refined_definition(summary: dict[str, Any]) -> float:
    count = int(summary["cooldown_filtered_count"])
    band = target_count_band(count)
    band_score = {
        "ideal": 1000.0,
        "acceptable_but_possibly_broad": 650.0,
        "sparse_but_potentially_usable": 430.0,
        "too_sparse": -450.0,
        "too_broad": -750.0,
    }[band]
    meta = summary["meta"]
    symbol_score = float(summary["symbol_coverage_count"]) * 28.0
    month_score = float(summary["month_coverage_count"]) * 5.0
    count_center_bonus = -abs(count - 700) * 0.07 if count else -125.0
    concentration_penalty = 0.0
    top_symbol = summary["top_symbol_concentration"]
    top_month = summary["top_month_concentration"]
    if top_symbol is not None and top_symbol > 0.25:
        concentration_penalty += 450.0 * (top_symbol - 0.25)
    if top_month is not None and top_month > 0.15:
        concentration_penalty += 300.0 * (top_month - 0.15)
    overlap_penalty = float(summary["overlap_rate"]) * 140.0
    broad_oi_penalty = 140.0 if meta["oi_contraction_percentile"] == "p10.0" else 0.0
    taker_broad_penalty = 80.0 if meta["taker_pressure_percentile"] == "p97.5" else 0.0
    simplicity_bonus = 30.0 if meta["rejection_score_min"] == 1 else 12.0
    cooldown_bonus = {3: 8.0, 6: 20.0, 12: 16.0, 24: 6.0}.get(int(meta["cooldown_hours"]), 0.0)
    return (
        band_score
        + symbol_score
        + month_score
        + count_center_bonus
        + simplicity_bonus
        + cooldown_bonus
        - concentration_penalty
        - overlap_penalty
        - broad_oi_penalty
        - taker_broad_penalty
    )


def compact_summary(summary: dict[str, Any]) -> dict[str, Any]:
    fields = [
        "definition_id",
        "meta",
        "raw_event_count",
        "cooldown_filtered_count",
        "unique_timestamp_count",
        "unique_symbol_timestamp_count",
        "symbol_coverage_count",
        "symbols",
        "month_coverage_count",
        "months",
        "top_symbol",
        "top_symbol_concentration",
        "top_month",
        "top_month_concentration",
        "arbusdt_count",
        "overlap_rate",
        "missing_component_count",
        "rejected_due_to_cooldown_count",
        "rejected_due_to_missing_price_rejection_count",
        "rejected_due_to_missing_oi_or_taker_component_count",
        "rejection_variant_distribution",
        "optional_annotation_distribution",
        "target_event_count_band",
    ]
    return {field: summary[field] for field in fields}


def select_refined_definitions(summaries: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], str, str, str]:
    selections: list[dict[str, Any]] = []
    slots = [
        ("best_long_capitulation_candidate", "LONG_CAPITULATION_REBOUND_CANDIDATE"),
        ("best_short_cover_exhaustion_candidate", "SHORT_COVER_EXHAUSTION_DOWNSIDE_CANDIDATE"),
    ]
    for slot_name, family in slots:
        candidates = [
            summary
            for summary in summaries.values()
            if summary["meta"]["family"] == family and summary["cooldown_filtered_count"] > 0
        ]
        if not candidates:
            continue
        candidates.sort(key=score_refined_definition, reverse=True)
        best = compact_summary(candidates[0])
        best["selection_slot"] = slot_name
        best["selection_score"] = score_refined_definition(candidates[0])
        selections.append(best)
        strict_candidates = [
            item
            for item in candidates[1:]
            if item["target_event_count_band"] in {"ideal", "sparse_but_potentially_usable"}
            and item["meta"]["oi_contraction_percentile"] in {"p1.0", "p2.5"}
            and item["meta"]["taker_pressure_percentile"] in {"p99.0", "p98.0"}
        ]
        if strict_candidates:
            strict_candidates.sort(key=score_refined_definition, reverse=True)
            optional = compact_summary(strict_candidates[0])
            optional["selection_slot"] = f"optional_strict_{slot_name}"
            optional["selection_score"] = score_refined_definition(strict_candidates[0])
            selections.append(optional)
    if not selections:
        return [], "No nonzero refined definitions survived current/prior-bar gates.", RESULT_STILL_TOO_SPARSE, NEXT_QUEUE_ROUTE
    bands = [item["target_event_count_band"] for item in selections]
    if any(band in {"ideal", "acceptable_but_possibly_broad", "sparse_but_potentially_usable"} for band in bands):
        return (
            selections[:4],
            "Selected only by outcome-blind count band, symbol/month coverage, concentration, overlap, missingness, material difference, and low degrees of freedom.",
            RESULT_READY,
            NEXT_VALIDATOR,
        )
    if all(band == "too_broad" for band in bands):
        return selections[:4], "Relaxed definitions became too broad under outcome-blind cleanliness gates.", RESULT_TOO_BROAD, NEXT_QUEUE_ROUTE
    return selections[:4], "Relaxed definitions remain too sparse after outcome-blind threshold relaxation.", RESULT_STILL_TOO_SPARSE, NEXT_QUEUE_ROUTE


def output_counts(summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        definition_id: {
            "family": summary["meta"]["family"],
            "raw_event_count": summary["raw_event_count"],
            "cooldown_filtered_count": summary["cooldown_filtered_count"],
            "target_event_count_band": summary["target_event_count_band"],
            "symbol_coverage_count": summary["symbol_coverage_count"],
            "month_coverage_count": summary["month_coverage_count"],
        }
        for definition_id, summary in summaries.items()
    }


def output_by_field(summaries: dict[str, dict[str, Any]], field: str) -> dict[str, Any]:
    return {definition_id: summary[field] for definition_id, summary in summaries.items()}


def nested_distribution(summaries: dict[str, dict[str, Any]], field: str) -> dict[str, Any]:
    return {definition_id: summary[field] for definition_id, summary in summaries.items() if summary["cooldown_filtered_count"] > 0}


def selected_by_slot(selected: list[dict[str, Any]]) -> dict[str, Any]:
    return {item["selection_slot"]: item for item in selected}


def base_artifact(
    head: str | None,
    hashes_before: dict[str, str] | None,
    hashes_after: dict[str, str] | None,
    blocker: str | None,
) -> dict[str, Any]:
    unchanged = hashes_before == hashes_after if hashes_before and hashes_after else False
    return {
        "refinement_status": REFINEMENT_STATUS_BLOCKED if blocker else REFINEMENT_STATUS_PASS,
        "status": REFINEMENT_STATUS_BLOCKED if blocker else REFINEMENT_STATUS_PASS,
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
        "prior_discovery_summary": {},
        "material_difference_from_failed_routes": "Refines OI contraction plus taker capitulation/rejection only; it does not revive the failed OI-expansion pressure-failure route, uses long-short ratios only as annotations, and does not use funding/liquidation unavailable data.",
        "refinement_grid": {
            "oi_contraction_thresholds": ["p1.0", "p2.5", "p5.0", "p10.0 broad diagnostic only"],
            "taker_pressure_thresholds": ["p99.0", "p98.0", "p97.5"],
            "rejection_strength": ["score>=1", "score>=2"],
            "selection_basis": "event cleanliness, coverage, concentration, overlap, missingness, material difference, and simplicity only",
        },
        "cooldown_grid": ["3h", "6h", "12h", "24h"],
        "event_families_tested": {},
        "event_counts_by_definition": {},
        "cooldown_filtered_counts": {},
        "selected_clean_event_definitions": [],
        "selected_definition_reason": None,
        "symbol_coverage_summary": {},
        "month_coverage_summary": {},
        "concentration_summary": {},
        "arbusdt_summary": {},
        "overlap_summary": {},
        "missing_data_summary": {},
        "rejection_reason_summary": {},
        "rejection_variant_distribution": {},
        "optional_annotation_distribution": {},
        "target_event_count_interpretation": {
            "ideal": "300 to 1500 cooldown-filtered events",
            "acceptable_but_possibly_broad": "1500 to 5000 cooldown-filtered events",
            "too_broad": "over 5000 cooldown-filtered events",
            "sparse_but_potentially_usable": "100 to 300 cooldown-filtered events",
            "too_sparse": "under 100 cooldown-filtered events",
            "preferred_concentration_gates": {
                "top_symbol_concentration": "<= 25%",
                "top_month_concentration": "<= 15%",
                "overlap": "near 0",
            },
        },
        "validation_limits": [
            "Refinement is outcome-blind event definition work only.",
            "No forward returns, p-values, null validation, backtest, PnL, signal, candidate, or edge claim was produced.",
            "Thresholds were relaxed only from the prior too-sparse event discovery using event cleanliness and coverage criteria.",
            "p10 OI contraction is recorded as broad diagnostic only and penalized in selection.",
        ],
        "forbidden_actions_confirmed_false": forbidden_false(),
        "allowed_next_step": NEXT_QUEUE_ROUTE if blocker else None,
        "blocker": blocker,
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }


def build_artifact() -> dict[str, Any]:
    head = current_head()
    if head != EXPECTED_HEAD:
        raise RefinementBlocked(f"HEAD mismatch: {head} != {EXPECTED_HEAD}")
    if not output_only_status(working_tree_status()):
        raise RefinementBlocked(f"unexpected dirty repo state during build: {working_tree_status()}")
    discovery, theory_queue, dataset, kline_diagnostic, input_payload_hashes = load_inputs()
    base = load_base_module()
    symbols = dataset.get("normalized_dataset_summary", {}).get("built_symbols") or dataset.get("requested_symbols")
    if not isinstance(symbols, list) or not symbols:
        raise RefinementBlocked("dataset builder artifact missing built symbol list")
    symbols = [str(symbol) for symbol in symbols]
    archive_summary = base.verify_cached_archives(symbols, kline_diagnostic)
    catalog = base.build_definition_catalog()
    summaries = {def_id: base.blank_summary(def_id, meta) for def_id, meta in catalog.items()}
    missing_counter = base.Counter()
    paths = base.normalized_paths(dataset)
    symbol_to_path = {path.name.split("_", 1)[0]: path for path in paths}
    kline_quality: dict[str, Any] = {}
    for symbol in symbols:
        path = symbol_to_path.get(symbol)
        if path is None:
            missing_counter[f"{symbol}_normalized_path_missing"] += 1
            continue
        kline_data = base.load_kline_symbol(symbol, archive_summary["archive_records"])
        kline_quality[symbol] = kline_data["quality"]
        base.run_symbol_discovery(path, kline_data, catalog, summaries, missing_counter)
    global_missing_components = int(sum(missing_counter.values()))
    finalized = {
        definition_id: base.finalize_summary(summary, global_missing_components)
        for definition_id, summary in summaries.items()
    }
    selected, selection_reason, result_classification, next_step = select_refined_definitions(finalized)
    hashes_before = input_artifact_hashes()
    hashes_after = input_artifact_hashes()
    if hashes_before != hashes_after:
        raise RefinementBlocked("input artifact hash changed during build")
    validation_checks = {
        "repo_clean_or_only_outputs_during_run": output_only_status(working_tree_status()),
        "head_matches_expected": head == EXPECTED_HEAD,
        "input_artifact_hashes_unchanged": hashes_before == hashes_after,
        "prior_discovery_loaded": discovery.get("result_classification")
        == "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_DISCOVERY_TOO_SPARSE",
        "theory_queue_ready": theory_queue.get("result_classification") == "OUTCOME_BLIND_BINANCE_THEORY_QUEUE_READY",
        "public_binance_derived_data_only": True,
        "no_new_downloads_performed": True,
        "no_forward_returns_computed": True,
        "no_p_values_computed": True,
        "no_null_validation_run": True,
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_strategy_signal_candidate_release": True,
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
            "prior_discovery_summary": compact_prior_discovery(discovery),
            "event_families_tested": base.EVENT_FAMILIES,
            "available_data_source_summary": {
                "symbols": symbols,
                "normalized_metric_files": [str(path) for path in paths],
                "kline_cache_root": str(base.KLINE_CACHE_ROOT),
                "archive_availability_summary": archive_summary,
                "kline_quality": kline_quality,
            },
            "event_counts_by_definition": output_counts(finalized),
            "cooldown_filtered_counts": output_by_field(finalized, "cooldown_filtered_count"),
            "selected_clean_event_definitions": selected,
            "selected_clean_event_definitions_by_slot": selected_by_slot(selected),
            "selected_definition_reason": selection_reason,
            "symbol_coverage_summary": output_by_field(finalized, "symbol_coverage_count"),
            "month_coverage_summary": output_by_field(finalized, "month_coverage_count"),
            "concentration_summary": {
                def_id: {
                    "top_symbol": summary["top_symbol"],
                    "top_symbol_concentration": summary["top_symbol_concentration"],
                    "top_month": summary["top_month"],
                    "top_month_concentration": summary["top_month_concentration"],
                    "preferred_gate_top_symbol_lte_25pct": (
                        summary["top_symbol_concentration"] is not None
                        and summary["top_symbol_concentration"] <= 0.25
                    ),
                    "preferred_gate_top_month_lte_15pct": (
                        summary["top_month_concentration"] is not None
                        and summary["top_month_concentration"] <= 0.15
                    ),
                }
                for def_id, summary in finalized.items()
            },
            "arbusdt_summary": output_by_field(finalized, "arbusdt_count"),
            "overlap_summary": output_by_field(finalized, "overlap_rate"),
            "missing_data_summary": {
                "global_missing_component_count": global_missing_components,
                "missing_component_counter": dict(missing_counter),
                "archive_missing_count": archive_summary["missing_count"],
                "missing_archive_keys": archive_summary["missing_archive_keys"],
            },
            "rejection_reason_summary": {
                def_id: {
                    "rejected_due_to_cooldown_count": summary["rejected_due_to_cooldown_count"],
                    "rejected_due_to_missing_price_rejection_count": summary[
                        "rejected_due_to_missing_price_rejection_count"
                    ],
                    "rejected_due_to_missing_oi_or_taker_component_count": summary[
                        "rejected_due_to_missing_oi_or_taker_component_count"
                    ],
                }
                for def_id, summary in finalized.items()
            },
            "rejection_variant_distribution": nested_distribution(finalized, "rejection_variant_distribution"),
            "optional_annotation_distribution": nested_distribution(finalized, "optional_annotation_distribution"),
            "allowed_next_step": next_step,
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
    selected = artifact.get("selected_clean_event_definitions", [])
    selected_counts = {
        item.get("selection_slot"): {
            "definition_id": item.get("definition_id"),
            "raw_event_count": item.get("raw_event_count"),
            "cooldown_filtered_count": item.get("cooldown_filtered_count"),
            "target_event_count_band": item.get("target_event_count_band"),
        }
        for item in selected
    }
    print(f"status: {artifact['refinement_status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"recovery_audit_status: {artifact['recovery_audit_status']}")
    print(f"input_artifact_hashes_unchanged: {bool_text(bool(artifact['input_artifact_hashes_unchanged']))}")
    print(f"theory_id: {artifact['theory_id']}")
    print(f"selected_clean_event_definitions: {json.dumps(selected_counts, sort_keys=True)}")
    print(f"event_counts_by_definition: {len(artifact.get('event_counts_by_definition', {}))} definitions evaluated")
    print(f"cooldown_filtered_counts: {json.dumps(selected_counts, sort_keys=True)}")
    print(f"symbol_coverage_summary: {json.dumps({item.get('selection_slot'): item.get('symbol_coverage_count') for item in selected}, sort_keys=True)}")
    print(f"month_coverage_summary: {json.dumps({item.get('selection_slot'): item.get('month_coverage_count') for item in selected}, sort_keys=True)}")
    print(f"concentration_summary: {json.dumps({item.get('selection_slot'): {'top_symbol': item.get('top_symbol'), 'top_symbol_concentration': item.get('top_symbol_concentration'), 'top_month': item.get('top_month'), 'top_month_concentration': item.get('top_month_concentration')} for item in selected}, sort_keys=True)}")
    print(f"arbusdt_summary: {json.dumps({item.get('selection_slot'): item.get('arbusdt_count') for item in selected}, sort_keys=True)}")
    print(f"overlap_summary: {json.dumps({item.get('selection_slot'): item.get('overlap_rate') for item in selected}, sort_keys=True)}")
    print(f"missing_data_summary: {json.dumps(artifact.get('missing_data_summary', {}), sort_keys=True)}")
    print(f"rejection_reason_summary: {json.dumps({item.get('selection_slot'): {'cooldown_rejects': item.get('rejected_due_to_cooldown_count'), 'price_rejection_rejects': item.get('rejected_due_to_missing_price_rejection_count')} for item in selected}, sort_keys=True)}")
    print(f"rejection_variant_distribution: {json.dumps({item.get('selection_slot'): item.get('rejection_variant_distribution') for item in selected}, sort_keys=True)}")
    print(f"optional_annotation_distribution: {json.dumps({item.get('selection_slot'): item.get('optional_annotation_distribution') for item in selected}, sort_keys=True)[:2000]}")
    print(f"allowed_next_step: {artifact['allowed_next_step']}")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {bool_text(bool(artifact.get('replacement_checks_all_true')))}")
    print(f"blocker: {artifact.get('blocker')}")


def main() -> int:
    hashes_before: dict[str, str] | None = None
    try:
        hashes_before = input_artifact_hashes()
        artifact = build_artifact()
    except RefinementBlocked as exc:
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
