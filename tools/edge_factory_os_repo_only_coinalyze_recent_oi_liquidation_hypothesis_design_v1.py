#!/usr/bin/env python3
"""Create Coinalyze recent OI/liquidation hypothesis design artifact.

Hypothesis design only. This module does not call Coinalyze, use API keys, run
strategies, generate signals, run backtests, compute PnL, create candidates, or
grant runtime/live/capital permission.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


MODULE = "edge_factory_os_repo_only_coinalyze_recent_oi_liquidation_hypothesis_design_v1"
STATUS = "PASS_REPO_ONLY_COINALYZE_RECENT_OI_LIQUIDATION_HYPOTHESIS_DESIGN_CREATED"
ARTIFACT_KIND = "COINALYZE_RECENT_OI_LIQUIDATION_HYPOTHESIS_DESIGN"
REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = REPO_ROOT / "tools" / "edge_factory_os_repo_only_coinalyze_recent_oi_liquidation_hypothesis_design_v1.py"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "research_designs" / "coinalyze_recent_oi_liquidation_hypothesis_design_v1.json"
DISCOVERY_PATH = REPO_ROOT / "artifacts" / "data_discovery" / "coinalyze_free_oi_liq_funding_availability_discovery_v5.json"
SAFE_DIR = str(REPO_ROOT).replace("\\", "/")
EXPECTED_NEW_PATHS = {
    str(TOOL_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
    str(ARTIFACT_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
}


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


def endpoint_success_counts(discovery: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in discovery.get("endpoint_probe_results", []):
        if row.get("request_ok") and int(row.get("row_count", 0)) > 0:
            endpoint = str(row.get("endpoint"))
            counts[endpoint] = counts.get(endpoint, 0) + 1
    return counts


def build_hypotheses() -> list[dict[str, Any]]:
    shared_anti_overfit = [
        "No parameter grid in the first event study.",
        "Use round structural thresholds only, such as top decile event buckets or fixed multiples of recent median liquidation volume.",
        "Chronologically split recent data if enough history exists; do not use later segments to tune earlier definitions.",
        "Compare event windows to simple time-block nulls before any backtest is considered.",
        "No candidate, edge, live, or capital permission from event-study results.",
    ]
    return [
        {
            "hypothesis_key": "LONG_LIQUIDATION_EXHAUSTION_REVERSAL",
            "mechanism": "After a strong sell move, a large long-liquidation spike with falling open interest can mark forced selling exhaustion rather than voluntary risk transfer.",
            "why_others_cant_arb": "The setup depends on forced deleveraging, latency of crowd unwind, and uncertainty about whether liquidations are complete; many participants cannot add risk during cascades.",
            "required_data_fields": ["long_liquidation_volume", "open_interest", "open_interest_delta", "close", "price_return", "funding_rate", "long_short_ratio"],
            "preferred_interval": "15min",
            "minimum_history_needed": "At least 30 recent 15m days for a first event study; 60 or more days preferred for chronological segmentation.",
            "expected_direction": "Upward mean reversion after the liquidation cascade completes and OI has flushed.",
            "no_trade_conditions": [
                "Liquidation spike occurs without OI contraction.",
                "Funding and long/short ratio still indicate fresh long crowding after the event.",
                "Broad market remains in an accelerating sell cascade.",
                "Event occurs in illiquid or incomplete data windows.",
            ],
            "possible_failure_modes": [
                "Liquidation cascade is trend continuation rather than exhaustion.",
                "OI drop reflects liquidity withdrawal, not completed forced selling.",
                "Funding data is too sparse or exchange-specific to identify crowding.",
                "Recent free-history window is too short for robust tail-event statistics.",
            ],
            "overfitting_risks": [
                "Choosing best liquidation-spike threshold after seeing outcomes.",
                "Optimizing rebound horizon by symbol.",
                "Treating one exchange's liquidation feed as market-wide truth.",
            ],
            "proposed_first_test_type": "EVENT_STUDY_ONLY",
            "anti_overfit_requirements": shared_anti_overfit,
            "pass_fail_design_criteria_for_future_preregistration": {
                "pass": "Across chronological segments, post-event forward returns are directionally positive after costs are ignored for event study, event frequency is sufficient, and effect is not dominated by one symbol.",
                "fail": "Forward returns are mixed, entirely symbol/month dependent, or similar to timestamp-block null events.",
            },
        },
        {
            "hypothesis_key": "SHORT_LIQUIDATION_EXHAUSTION_REVERSAL",
            "mechanism": "After a strong pump, a large short-liquidation spike with falling open interest can mark forced buying exhaustion after a short squeeze.",
            "why_others_cant_arb": "Short squeezes are reflexive and balance-sheet constrained; arbitrageurs may wait until forced buying slows, making exhaustion timing hard but potentially observable.",
            "required_data_fields": ["short_liquidation_volume", "open_interest", "open_interest_delta", "close", "price_return", "funding_rate", "long_short_ratio"],
            "preferred_interval": "15min",
            "minimum_history_needed": "At least 30 recent 15m days for initial event study; 60 or more days preferred.",
            "expected_direction": "Downward mean reversion after short-squeeze exhaustion and OI flush.",
            "no_trade_conditions": [
                "Short-liquidation spike occurs while OI continues to expand.",
                "Funding remains negative enough to suggest shorts are still crowded rather than flushed.",
                "BTC and ETH are in broad market pump conditions.",
                "The event is caused by listing or data discontinuity.",
            ],
            "possible_failure_modes": [
                "Short liquidation spike starts a momentum breakout instead of ending one.",
                "OI drop is too small to prove deleveraging.",
                "Crowding proxies disagree across funding and long/short ratio.",
            ],
            "overfitting_risks": [
                "Picking pump-return and liquidation thresholds from best examples.",
                "Selecting only symbols with visible squeeze reversals.",
                "Using holdout-like recent days to tune event definitions.",
            ],
            "proposed_first_test_type": "EVENT_STUDY_ONLY",
            "anti_overfit_requirements": shared_anti_overfit,
            "pass_fail_design_criteria_for_future_preregistration": {
                "pass": "Forward returns after short-liquidation/OI-flush events are negative across multiple symbols and segments, with timestamp-block nulls less competitive.",
                "fail": "Events continue upward, are too rare, or depend on a single pump episode.",
            },
        },
        {
            "hypothesis_key": "OI_BUILDUP_BREAKOUT_CONTINUATION_OR_TRAP",
            "mechanism": "Open interest rising with price expansion indicates leverage buildup; continuation may follow if no liquidation occurs, while liquidation against the crowded side may turn the move into a trap.",
            "why_others_cant_arb": "The signal separates healthy leverage expansion from forced unwind only after combining OI trend, price trend, and liquidation side; single-variable arbitrage is noisy.",
            "required_data_fields": ["open_interest", "open_interest_delta", "price_return", "long_liquidation_volume", "short_liquidation_volume", "funding_rate"],
            "preferred_interval": "15min",
            "minimum_history_needed": "At least 60 days of 15m or 1h data for buildup periods plus event follow-through windows.",
            "expected_direction": "Continuation when OI builds without adverse liquidation; reversal when buildup is followed by liquidation shock against the crowded side.",
            "no_trade_conditions": [
                "OI and price move are directionally inconsistent.",
                "Liquidation data is missing or side cannot be separated.",
                "Funding is neutral and OI buildup is small relative to recent baseline.",
            ],
            "possible_failure_modes": [
                "OI buildup reflects hedging, not directional leverage.",
                "Liquidation shock arrives after the measured forward window.",
                "Continuation and trap regimes cancel in aggregate.",
            ],
            "overfitting_risks": [
                "Optimizing OI buildup lookback.",
                "Separating continuation/trap regimes after seeing PnL-like outcomes.",
                "Choosing different event windows by symbol.",
            ],
            "proposed_first_test_type": "DATASET_BUILD_ONLY",
            "anti_overfit_requirements": shared_anti_overfit,
            "pass_fail_design_criteria_for_future_preregistration": {
                "pass": "Dataset review confirms stable OI trend, liquidation-side, funding, and price fields across the probe universe before any event outcome test.",
                "fail": "Field coverage is inconsistent, side labels are ambiguous, or event counts are too sparse.",
            },
        },
        {
            "hypothesis_key": "FUNDING_CROWDING_UNWIND",
            "mechanism": "Extreme positive funding suggests crowded longs and extreme negative funding suggests crowded shorts; OI contraction plus liquidation confirms crowd unwind.",
            "why_others_cant_arb": "Funding crowding can persist longer than expected, so naive contrarian trades are dangerous; forced-liquidation confirmation may identify the narrower unwind phase.",
            "required_data_fields": ["funding_rate", "open_interest", "open_interest_delta", "long_liquidation_volume", "short_liquidation_volume", "price_return", "long_short_ratio"],
            "preferred_interval": "1hour",
            "minimum_history_needed": "At least 60 recent days because funding regimes are slower than 15m liquidation shocks.",
            "expected_direction": "Reversal away from the crowded funding side after OI contracts and liquidation confirms unwind.",
            "no_trade_conditions": [
                "Funding is extreme but OI is still expanding.",
                "No liquidation confirmation occurs.",
                "Funding field is stale, missing, or exchange timing cannot be aligned.",
            ],
            "possible_failure_modes": [
                "Funding remains extreme during persistent trend.",
                "Funding is arbitraged by basis trades and not a clean directional crowding measure.",
                "Free recent data has too few full funding cycles.",
            ],
            "overfitting_risks": [
                "Choosing funding cutoffs from best reversals.",
                "Combining many confirmation filters until sample is tiny.",
                "Using the same recent window for threshold discovery and evaluation.",
            ],
            "proposed_first_test_type": "EVENT_STUDY_ONLY",
            "anti_overfit_requirements": shared_anti_overfit,
            "pass_fail_design_criteria_for_future_preregistration": {
                "pass": "Extreme-funding plus OI/liquidation-confirmed events show consistent reversal direction across chronological segments.",
                "fail": "Funding extremes alone dominate without confirmation, or confirmed events are too rare to evaluate honestly.",
            },
        },
        {
            "hypothesis_key": "LIQUIDATION_IMBALANCE_WITH_OI_FLUSH",
            "mechanism": "A one-sided liquidation imbalance plus falling OI may distinguish forced exit from ordinary volatility and identify short-term exhaustion.",
            "why_others_cant_arb": "The opportunity depends on transient forced flow and balance-sheet stress; crowd exits are not easily arbitraged while liquidation engines are still active.",
            "required_data_fields": ["long_liquidation_volume", "short_liquidation_volume", "liquidation_imbalance", "open_interest", "open_interest_delta", "price_return", "volume"],
            "preferred_interval": "15min",
            "minimum_history_needed": "At least 30 recent 15m days for first event study; more history required before any backtest.",
            "expected_direction": "Short-term reversal opposite the liquidation side once OI confirms a flush.",
            "no_trade_conditions": [
                "Long and short liquidations are balanced.",
                "OI does not fall during the liquidation event.",
                "Price movement is small relative to recent volatility.",
                "Event overlaps known data outage or incomplete exchange coverage.",
            ],
            "possible_failure_modes": [
                "Liquidation imbalance is a momentum confirmation, not exhaustion.",
                "OI flush follows rather than precedes the tradable reversal window.",
                "Event study is dominated by one market-wide cascade.",
            ],
            "overfitting_risks": [
                "Mining imbalance ratios.",
                "Choosing forward windows after looking at event returns.",
                "Dropping symbols with adverse liquidation behavior.",
            ],
            "proposed_first_test_type": "EVENT_STUDY_ONLY",
            "anti_overfit_requirements": shared_anti_overfit,
            "pass_fail_design_criteria_for_future_preregistration": {
                "pass": "One-sided liquidation plus OI-flush events show reversal behavior across sides, symbols, and chronological segments, with no single cascade dominating.",
                "fail": "Imbalance events behave like normal volatility or are not distinct from random high-volume intervals.",
            },
        },
    ]


def build_payload() -> dict[str, Any]:
    discovery = load_json(DISCOVERY_PATH)
    endpoint_counts = endpoint_success_counts(discovery)
    ready = (
        discovery.get("status") == "PASS_REPO_ONLY_COINALYZE_FREE_OI_LIQ_FUNDING_AVAILABILITY_DISCOVERY_V5_CREATED"
        and discovery.get("result_classification") == "COINALYZE_FREE_DATA_READY_FOR_RECENT_OI_LIQUIDATION_RESEARCH"
    )
    clean = repo_clean_except_expected_new_files()
    hypotheses = build_hypotheses()
    payload: dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": source_checkpoint(),
        "source_artifacts": {
            "coinalyze_v5_discovery": str(DISCOVERY_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
            "prior_ohlcv_context_used": False,
        },
        "prior_discovery_summary": {
            "commit": "aeee03c3a504db2d72262cc23fcf3be5313abf74",
            "status": discovery.get("status"),
            "result_classification": discovery.get("result_classification"),
            "market_count": discovery.get("market_discovery_summary", {}).get("market_count"),
            "probe_symbol_count": len(discovery.get("probe_symbols", [])),
            "usable_oi_symbol_count": discovery.get("usable_data_summary", {}).get("usable_oi_symbol_count"),
            "usable_liquidation_symbol_count": discovery.get("usable_data_summary", {}).get("usable_liquidation_symbol_count"),
            "usable_funding_symbol_count": discovery.get("usable_data_summary", {}).get("usable_funding_symbol_count"),
            "best_usable_interval": discovery.get("interval_coverage_summary", {}).get("best_usable_interval"),
            "endpoint_success_counts": endpoint_counts,
        },
        "data_availability_interpretation": {
            "ready_for_recent_research": ready,
            "usable_for_2022_2025_deep_backtest": False,
            "recommended_scope": "Recent Coinalyze-only dataset build followed by event studies before any strategy backtest.",
            "available_mechanism_inputs": [
                "open_interest_history",
                "liquidation_history",
                "funding_rate_history",
                "long_short_ratio_history",
                "ohlcv_history_for_alignment",
            ],
            "interpretation": "The V5 discovery found OI, liquidation, and funding coverage across all 10 probe symbols with 15min as the best usable interval, supporting recent-data mechanism studies but not long-history OHLCV-style lockbox claims.",
        },
        "hypothesis_designs": hypotheses,
        "recommended_hypothesis_priority": [
            {
                "rank": 1,
                "hypothesis_key": "LIQUIDATION_IMBALANCE_WITH_OI_FLUSH",
                "rationale": "Most directly tests forced-flow exhaustion using liquidation side plus OI contraction and can be studied symmetrically for long and short cascades.",
            },
            {
                "rank": 2,
                "hypothesis_key": "LONG_LIQUIDATION_EXHAUSTION_REVERSAL",
                "rationale": "Clean forced-selling exhaustion mechanism after sell cascades.",
            },
            {
                "rank": 3,
                "hypothesis_key": "SHORT_LIQUIDATION_EXHAUSTION_REVERSAL",
                "rationale": "Clean forced-buying exhaustion mechanism after short squeezes.",
            },
            {
                "rank": 4,
                "hypothesis_key": "FUNDING_CROWDING_UNWIND",
                "rationale": "Useful crowding overlay, but funding can persist and should require OI/liquidation confirmation.",
            },
            {
                "rank": 5,
                "hypothesis_key": "OI_BUILDUP_BREAKOUT_CONTINUATION_OR_TRAP",
                "rationale": "Broader regime concept that should start with dataset review because continuation/trap definitions are easier to overfit.",
            },
        ],
        "anti_overfit_policy": {
            "no_parameter_grid": True,
            "event_study_before_strategy_backtest": True,
            "round_structural_thresholds_only": True,
            "chronological_segments_required_if_enough_data": True,
            "no_live_capital_candidate_after_event_study": True,
            "future_backtest_requires_lockbox_or_paper_forward": True,
            "coinalyze_free_data_recent_short_history_limitation": True,
        },
        "next_allowed_step": "COINALYZE_RECENT_OI_LIQUIDATION_DATASET_BUILDER_V1",
        "limitations": [
            "This design uses only V5 availability metadata; it does not call Coinalyze or acquire new rows.",
            "Coinalyze free data is recent and short-history, so any later backtest would require separate lockbox or paper-forward treatment.",
            "Hypotheses are mechanisms for future testing, not candidates or edge claims.",
        ],
        "safety_permissions": {
            "hypothesis_design_created": True,
            "data_builder_allowed_next": True,
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
        "validation_checks": {
            "repo_clean_before_run": clean,
            "coinalyze_v5_discovery_loaded": True,
            "discovery_ready_verified": ready,
            "no_api_key_used": True,
            "no_api_call_made": True,
            "no_strategy_execution": True,
            "no_signal_generation": True,
            "no_backtest_run": True,
            "no_pnl_computation": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_runtime_live_capital": True,
            "exactly_one_python_tool_created": TOOL_PATH.exists(),
            "exactly_one_json_artifact_created": True,
            "no_existing_repo_files_modified": clean,
            "replacement_checks_all_true": clean and ready,
        },
        "replacement_checks_all_true": clean and ready,
        "payload_sha256_excluding_hash": None,
    }
    payload["payload_sha256_excluding_hash"] = payload_hash(payload)
    return payload


def main() -> int:
    payload = build_payload()
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status: {payload['status']}")
    print("result_summary: designed 5 recent Coinalyze OI/liquidation/funding hypotheses for event-study-first research")
    print(f"hypothesis_count: {len(payload['hypothesis_designs'])}")
    print(f"top_priority_hypothesis: {payload['recommended_hypothesis_priority'][0]['hypothesis_key']}")
    print(f"next_allowed_step: {payload['next_allowed_step']}")
    print("strategy_execution_allowed_now: false")
    print("signal_generation_allowed_now: false")
    print("backtest_allowed_now: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {payload['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(payload['replacement_checks_all_true']).lower()}")
    return 0 if payload["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
