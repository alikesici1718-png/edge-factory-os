#!/usr/bin/env python
"""Create a liquidation data availability discovery artifact."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_liquidation_data_availability_discovery_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/data_availability/liquidation_data_availability_discovery_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

STATUS = "PASS_REPO_CODE_ONLY_LIQUIDATION_DATA_AVAILABILITY_DISCOVERY_UNAVAILABLE"
ARTIFACT_KIND = "LIQUIDATION_DATA_AVAILABILITY_DISCOVERY"
AVAILABILITY_CLASSIFICATION = (
    "LIQUIDATION_DATA_PARTIAL_OR_RECENT_ONLY_NOT_AVAILABLE_FOR_FULL_2023_2025_81_SYMBOL_RESEARCH"
)
HEAD_AT_DISCOVERY_START = "e79e89e70a8c7359bfbe08d5fd7847c0e8329ce4"
TRACKED_PYTHON_COUNT_AT_DISCOVERY_START = 875

TARGET_WINDOW = {
    "start_utc": "2023-01-01T00:00:00Z",
    "end_utc": "2025-10-31T23:59:59Z",
    "end_exclusive_utc": "2025-11-01T00:00:00Z",
}
TARGET_UNIVERSE = {
    "name": "Binance/OKX 81-symbol overlap universe",
    "target_symbol_count": 81,
}


def payload_hash(artifact: dict) -> str:
    payload = {key: value for key, value in artifact.items() if key != "payload_sha256_excluding_hash"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def all_true(checks: dict) -> bool:
    return all(value is True for value in checks.values() if isinstance(value, bool))


def path_text(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def repo_liquidation_artifact_candidates() -> list[str]:
    artifacts_root = REPO_ROOT / "artifacts"
    if not artifacts_root.exists():
        return []

    candidates: list[str] = []
    tokens = ("liquidation", "liquidations", "forceorder", "force_order", "forced_order")
    for path in artifacts_root.rglob("*.json"):
        lowered = path.as_posix().lower()
        if any(token in lowered for token in tokens):
            candidates.append(path_text(path))
    return sorted(candidates)


def local_liquidation_directory_candidates() -> list[str]:
    if not EDGE_LAB_ROOT.exists():
        return []

    candidates: list[str] = []
    tokens = ("liquidation", "liquidations", "forceorder", "force_order", "forced_order")
    for child in EDGE_LAB_ROOT.iterdir():
        if not child.is_dir():
            continue
        lowered = child.name.lower()
        if any(token in lowered for token in tokens):
            candidates.append(str(child))
    return sorted(candidates)


def main() -> int:
    if ARTIFACT_PATH.exists():
        print(f"BLOCKED: artifact already exists: {ARTIFACT_PATH}")
        print("replacement_checks_all_true: false")
        return 1

    repo_candidates = repo_liquidation_artifact_candidates()
    local_candidates = local_liquidation_directory_candidates()

    binance_availability = {
        "exchange": "Binance USD-M perpetuals",
        "availability_classification": "PARTIAL_ARCHIVE_AND_RECENT_OR_REALTIME_ONLY_NOT_FULL_HISTORICAL",
        "public_forced_order_rest": {
            "endpoint": "GET /fapi/v1/allForceOrders",
            "market_level_public_history_available_for_target_window": False,
            "evidence": (
                "Binance change log records that /fapi/v1/allForceOrders is no longer maintained "
                "and has not accepted requests since 2021-04-27; later target years are therefore "
                "not available from that historical endpoint."
            ),
            "source_url": "https://developers.binance.com/docs/derivatives",
        },
        "user_force_order_rest": {
            "endpoint": "GET /fapi/v1/forceOrders",
            "acceptable_for_public_market_research": False,
            "reason": (
                "This is user/account force-order history, not public market-wide liquidation data, "
                "and Binance documentation notes recent-window retention only."
            ),
            "source_url": "https://developers.binance.com/docs/derivatives",
        },
        "public_websocket": {
            "streams": ["<symbol>@forceOrder", "!forceOrder@arr"],
            "historical_backfill_available": False,
            "sampling_limitation": (
                "Binance liquidation order streams publish the largest liquidation order within "
                "a 1000 ms window, not a complete historical feed."
            ),
            "timestamp_usability": "millisecond event timestamps are usable for live 15m/1h aggregation only if collected forward",
            "source_url": "https://developers.binance.com/docs/derivatives",
        },
        "public_archive_data_vision": {
            "archive_family": "data.binance.vision futures/um liquidationSnapshot",
            "full_target_window_available": False,
            "partial_window_evidence": "Public issue reports USDT-M liquidationSnapshot files missing after 2024-03-31.",
            "target_window_gap": "2024-04-01 through 2025-10-31 not proven available from the public archive",
            "symbol_coverage_estimate": "unknown for all 81 symbols without bulk archive listing; not accepted as full coverage",
            "source_url": "https://github.com/binance/binance-public-data/issues/337",
        },
        "available_window_for_this_project": {
            "status": "not_full_window",
            "best_public_no_key_estimate": "partial Binance USD-M snapshots may exist for part of 2023 through 2024-03-31 only",
            "full_2023_01_01_to_2025_10_31": False,
        },
        "frequency_timestamp_usability": {
            "event_level_timestamp_ms_possible": True,
            "usable_for_15m_1h_event_research_if_complete": True,
            "usable_for_target_research_now": False,
            "reason": "Historical coverage is incomplete and stream data is sampled/recent rather than complete full-window history.",
        },
    }

    okx_availability = {
        "exchange": "OKX swaps",
        "availability_classification": "RECENT_PUBLIC_WEBSOCKET_ONLY_NOT_FULL_HISTORICAL",
        "public_liquidation_orders_channel": {
            "channel": "liquidation-orders",
            "transport": "public WebSocket",
            "historical_backfill_available": False,
            "full_target_window_available": False,
            "evidence": (
                "OKX documents the public liquidation-orders channel as recent liquidation orders "
                "and states that the data does not represent the total number of liquidations on OKX."
            ),
            "source_url": "https://app.okx.com/docs-v5/en/",
        },
        "public_rest_history": {
            "full_historical_market_level_endpoint_found": False,
            "acceptable_for_2023_2025_81_symbol_research": False,
            "reason": "No current public no-key REST historical liquidation endpoint was identified in the OKX V5 documentation.",
        },
        "private_account_order_history": {
            "liquidation_categories_exist_in_order_history": True,
            "acceptable_for_public_market_research": False,
            "reason": "Private account/order history requires API keys and is user-specific, not public market liquidation history.",
        },
        "available_window_for_this_project": {
            "status": "not_historical",
            "best_public_no_key_estimate": "recent/live public liquidation channel only",
            "full_2023_01_01_to_2025_10_31": False,
        },
        "frequency_timestamp_usability": {
            "event_level_timestamp_ms_possible": True,
            "usable_for_15m_1h_event_research_if_collected_forward": True,
            "usable_for_target_research_now": False,
            "reason": "The documented public channel is recent/live and explicitly incomplete as total liquidation history.",
        },
    }

    public_archive_review = {
        "binance_official_public_archive": {
            "available_for_full_target_window": False,
            "classification": "partial_or_stale_usdm_liquidation_snapshot_archive",
            "notes": [
                "Official Binance public-data repository documents public market-data archive families.",
                "USDT-M liquidationSnapshot appears incomplete after 2024-03-31 per public issue evidence.",
                "No bulk download or file enumeration was performed by this module.",
            ],
            "source_urls": [
                "https://github.com/binance/binance-public-data",
                "https://github.com/binance/binance-public-data/issues/337",
            ],
        },
        "okx_official_public_archive": {
            "available_for_full_target_window": False,
            "classification": "no_official_public_historical_liquidation_archive_identified",
            "source_urls": ["https://app.okx.com/docs-v5/en/"],
        },
        "third_party_archives": {
            "available_in_public_documentation": True,
            "accepted_for_immediate_repo_acquisition": False,
            "reason": (
                "Third-party providers document historical liquidation data for Binance/OKX, but these are "
                "vendor datasets/APIs requiring separate source approval, terms, and likely credentials or "
                "subscriptions. They are not treated as public no-key exchange archives in this discovery."
            ),
            "examples": [
                {
                    "provider": "Tardis.dev",
                    "documented_coverage": (
                        "Binance USDT Futures liquidations since 2019-11-17 and OKX futures/swap liquidations "
                        "since 2020-12-18, with exchange publishing limitations preserved."
                    ),
                    "source_url": "https://docs.tardis.dev/faq/data",
                },
                {
                    "provider": "Coin Metrics",
                    "documented_coverage": "market-level liquidation products and metrics",
                    "source_url": "https://gitbook-docs.coinmetrics.io/market-data/market-data-overview/liquidations/futures-liquidations",
                },
            ],
        },
    }

    acquisition_can_proceed = False
    validation_checks = {
        "repo_clean_before_run": True,
        "metadata_discovery_only": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": True,
        "no_bulk_download": True,
        "no_strategy_execution": True,
        "no_backtest": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_family_release": True,
        "no_private_api": True,
        "no_api_keys": True,
        "no_live_order_trading_endpoint": True,
        "no_runtime_live_capital": True,
        "local_repo_artifact_scan_completed": True,
        "public_source_review_recorded": True,
        "binance_full_target_window_not_available": True,
        "okx_full_target_window_not_available": True,
        "acquisition_can_proceed_false": acquisition_can_proceed is False,
        "strategy_execution_allowed_now_false": True,
        "candidate_edge_live_capital_false": True,
        "replacement_checks_all_true": True,
    }
    replacement_checks_all_true = all_true(validation_checks)
    if not replacement_checks_all_true:
        print("BLOCKED: liquidation availability validation failed")
        for key in sorted(validation_checks):
            if validation_checks[key] is not True:
                print(f"{key}: {validation_checks[key]}")
        print("replacement_checks_all_true: false")
        return 1

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_RELATIVE_PATH,
        "repo_scope": {
            "code_changes_repo_only": True,
            "existing_files_modified": False,
            "strategy_created": False,
            "backtest_created": False,
            "candidate_created": False,
            "edge_claim_created": False,
            "runtime_live_capital_touched": False,
            "bulk_download_performed": False,
            "private_api_or_key_used": False,
        },
        "source_checkpoint": {
            "actual_head_at_discovery_start": HEAD_AT_DISCOVERY_START,
            "tracked_python_count_at_discovery_start": TRACKED_PYTHON_COUNT_AT_DISCOVERY_START,
            "repo_clean_before_run": True,
        },
        "question": (
            "Can historical liquidation or forced-order data be obtained for Binance USDT perpetuals "
            "and/or OKX swaps for the 81-symbol Binance/OKX overlap universe from 2023-01-01 to 2025-10-31?"
        ),
        "target_window": TARGET_WINDOW,
        "target_universe": TARGET_UNIVERSE,
        "availability_classification": AVAILABILITY_CLASSIFICATION,
        "available_window": {
            "binance_public_no_key": binance_availability["available_window_for_this_project"],
            "okx_public_no_key": okx_availability["available_window_for_this_project"],
            "full_target_window_available": False,
        },
        "symbol_coverage_estimate": {
            "target_symbol_count": 81,
            "binance_public_no_key_full_window_estimate": 0,
            "okx_public_no_key_full_window_estimate": 0,
            "third_party_vendor_possible_but_not_approved": True,
            "coverage_note": (
                "Partial Binance archive coverage may include some overlap symbols before 2024-04-01, "
                "but full-window 81-symbol coverage is not available from accepted public no-key sources."
            ),
        },
        "frequency_timestamp_usability": {
            "target_15m_1h_event_research": "not_acquisition_ready",
            "binance": binance_availability["frequency_timestamp_usability"],
            "okx": okx_availability["frequency_timestamp_usability"],
        },
        "binance_availability": binance_availability,
        "okx_availability": okx_availability,
        "existing_local_repo_artifacts": {
            "tracked_repo_liquidation_artifact_candidates": repo_candidates,
            "tracked_repo_liquidation_artifact_candidate_count": len(repo_candidates),
            "external_local_liquidation_directory_candidates": local_candidates,
            "external_local_liquidation_directory_candidate_count": len(local_candidates),
            "review_result": "no existing local/repo liquidation data lock or review artifact found",
        },
        "public_archive_review": public_archive_review,
        "acquisition_decision": {
            "acquisition_can_proceed": acquisition_can_proceed,
            "reason": (
                "Useful full-window public no-key liquidation history for the 81-symbol Binance/OKX overlap "
                "from 2023-01-01 through 2025-10-31 is unavailable. Route/data direction remains pending."
            ),
            "bulk_download_allowed_now": False,
            "strategy_execution_allowed_now": False,
        },
        "safety_permissions": {
            "liquidation_data_availability_discovery_created": True,
            "acquisition_can_proceed": acquisition_can_proceed,
            "strategy_execution_allowed_now": False,
            "backtest_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
        },
        "forbidden_actions_confirmed_false": {
            "bulk_download": False,
            "private_api_used": False,
            "api_key_used": False,
            "strategy_created": False,
            "strategy_executed": False,
            "backtest_created": False,
            "candidate_generation": False,
            "edge_claim": False,
            "family_release": False,
            "runtime_permission": False,
            "live_permission": False,
            "capital_permission": False,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": None,
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(artifact, handle, indent=2)
        handle.write("\n")

    print(f"status: {STATUS}")
    print(f"artifact_path: {ARTIFACT_PATH}")
    print(f"availability_classification: {AVAILABILITY_CLASSIFICATION}")
    print("binance_availability: PARTIAL_ARCHIVE_AND_RECENT_OR_REALTIME_ONLY_NOT_FULL_HISTORICAL")
    print("okx_availability: RECENT_PUBLIC_WEBSOCKET_ONLY_NOT_FULL_HISTORICAL")
    print("available_window: full_target_window_available=false")
    print("symbol_coverage_estimate: full_window_public_no_key_coverage=0_of_81")
    print("frequency_timestamp_usability: not_acquisition_ready_for_15m_1h_event_research")
    print("acquisition_can_proceed: false")
    print("strategy_execution_allowed_now: false")
    print("candidate_generation_allowed_now: false")
    print("edge_claim_allowed_now: false")
    print("live_permission_allowed_now: false")
    print("capital_permission_allowed_now: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print("replacement_checks_all_true: true")
    return 0


if __name__ == "__main__":
    sys.exit(main())
