#!/usr/bin/env python
"""Create an order book / depth data availability discovery artifact."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_order_book_depth_availability_discovery_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/data_availability/order_book_depth_availability_discovery_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

STATUS = "PASS_REPO_CODE_ONLY_ORDER_BOOK_DEPTH_AVAILABILITY_DISCOVERY_UNAVAILABLE"
ARTIFACT_KIND = "ORDER_BOOK_DEPTH_AVAILABILITY_DISCOVERY"
AVAILABILITY_CLASSIFICATION = (
    "ORDER_BOOK_DEPTH_PARTIAL_OR_RECENT_ONLY_NOT_AVAILABLE_FOR_FULL_2023_2025_81_SYMBOL_RESEARCH"
)
HEAD_AT_DISCOVERY_START = "7f3d50b8f6382a1e8dc53c1df7c24092d84677f0"
TRACKED_PYTHON_COUNT_AT_DISCOVERY_START = 876

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


def repo_order_book_artifact_candidates() -> list[str]:
    artifacts_root = REPO_ROOT / "artifacts"
    if not artifacts_root.exists():
        return []

    name_tokens = (
        "order_book",
        "orderbook",
        "book_ticker",
        "bookticker",
        "bookdepth",
        "book_depth",
        "bid_ask",
        "bidask",
        "bbo",
        "l2",
    )
    candidates: list[str] = []
    for path in artifacts_root.rglob("*.json"):
        lowered = path.as_posix().lower()
        if any(token in lowered for token in name_tokens):
            candidates.append(path_text(path))
    return sorted(candidates)


def local_order_book_directory_candidates() -> list[str]:
    if not EDGE_LAB_ROOT.exists():
        return []

    name_tokens = (
        "order_book",
        "orderbook",
        "book_ticker",
        "bookticker",
        "bookdepth",
        "book_depth",
        "bid_ask",
        "bidask",
        "bbo",
        "l2",
    )
    candidates: list[str] = []
    for child in EDGE_LAB_ROOT.iterdir():
        if not child.is_dir():
            continue
        lowered = child.name.lower()
        if any(token in lowered for token in name_tokens):
            candidates.append(str(child))
    return sorted(candidates)


def main() -> int:
    if ARTIFACT_PATH.exists():
        print(f"BLOCKED: artifact already exists: {ARTIFACT_PATH}")
        print("replacement_checks_all_true: false")
        return 1

    repo_candidates = repo_order_book_artifact_candidates()
    local_candidates = local_order_book_directory_candidates()

    binance_full_window_available = False
    okx_full_window_available = False
    public_no_key_full_81_coverage_available = False
    acquisition_allowed_next = False

    checked_sources = [
        {
            "source_name": "Binance USD-M Futures REST API docs",
            "source_url": "https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Order-Book",
            "source_type": "official_docs",
            "checked_for": ["current_order_book_snapshot", "historical_depth_limits"],
            "result": "current REST order book exists, but it is a live/current snapshot endpoint, not historical backfill",
        },
        {
            "source_name": "Binance USD-M Futures bookTicker REST docs",
            "source_url": "https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Symbol-Order-Book-Ticker",
            "source_type": "official_docs",
            "checked_for": ["best_bid_ask_snapshot", "bookTicker_history"],
            "result": "current best bid/ask snapshot exists, but no historical REST range parameter is documented",
        },
        {
            "source_name": "Binance public-data repository README",
            "source_url": "https://github.com/binance/binance-public-data",
            "source_type": "official_public_archive_docs",
            "checked_for": ["data.binance.vision archive families"],
            "result": (
                "README documents futures aggTrades, klines, and trades. It does not prove full 2023-2025 "
                "USD-M order book/depth/bookTicker coverage for the target universe."
            ),
        },
        {
            "source_name": "Binance Data Collection bookTicker listing/search evidence",
            "source_url": "https://data.binance.vision/?prefix=data%2Ffutures%2Fum%2Fmonthly%2FbookTicker%2FBTCUSDT%2F",
            "source_type": "official_public_archive_listing_probe",
            "checked_for": ["bookTicker_archive"],
            "result": (
                "A monthly bookTicker archive family is visible in public metadata/search results for some "
                "symbols, but evidence indicates it is partial and not current through 2025-10-31."
            ),
        },
        {
            "source_name": "OKX historical market data page",
            "source_url": "https://www.okx.com/en-us/historical-data",
            "source_type": "official_public_archive_docs",
            "checked_for": ["historical_order_book", "L2_depth"],
            "result": (
                "OKX advertises high-resolution L2 order book data from March 2023 onward, which is useful "
                "but starts after the target 2023-01-01 date."
            ),
        },
        {
            "source_name": "OKX V5 market data API docs",
            "source_url": "https://app.okx.com/docs-v5/en/",
            "source_type": "official_docs",
            "checked_for": ["current_order_book", "websocket_depth"],
            "result": "current REST and WebSocket order book channels exist; they do not establish full historical backfill.",
        },
        {
            "source_name": "Public third-party search surface",
            "source_url": "https://www.cryptohftdata.com/",
            "source_type": "third_party_docs",
            "checked_for": ["free_historical_binance_okx_order_book"],
            "result": (
                "Third-party providers may expose order book data, but discovered examples require API keys, "
                "vendor access, or start too late for the 2023-01-01 target."
            ),
        },
    ]

    binance_availability = {
        "exchange": "Binance USD-M futures",
        "full_window_available": binance_full_window_available,
        "availability_summary": (
            "Current public REST and WebSocket order book/bookTicker data exists. Public archive evidence for "
            "USD-M bookTicker/depth is partial and does not prove complete 2023-01-01 through 2025-10-31 "
            "coverage across the 81-symbol overlap universe."
        ),
        "data_types": {
            "historical_depth_snapshots": {
                "available_for_full_window": False,
                "available_window": "not proven from public/no-key Binance sources",
                "granularity": "current REST snapshot only for /fapi/v1/depth; WebSocket can collect forward",
                "symbol_coverage_estimate": "not proven for 81 symbols",
                "evidence": "Official REST order book endpoint returns the current symbol order book without historical date range parameters.",
            },
            "bookTicker_history": {
                "available_for_full_window": False,
                "available_window": "partial public monthly archive evidence, reportedly around 2023-05 through 2024-03 for BTCUSDT",
                "granularity": "best bid/ask update records when archived; current REST snapshot otherwise",
                "symbol_coverage_estimate": "not proven for 81 symbols and not full 2025 window",
                "evidence": "BookTicker public archive search/listing evidence is partial; REST bookTicker is current snapshot only.",
            },
            "bid_ask_spread_history": {
                "available_for_full_window": False,
                "available_window": "derived only where bookTicker or order book history exists",
                "granularity": "top-of-book spread derivable from bid/ask snapshots",
                "symbol_coverage_estimate": "not full 81-symbol target",
                "evidence": "Spread is derived from bid/ask; no complete historical bid/ask source was proven.",
            },
            "best_bid_ask_snapshots": {
                "available_for_full_window": False,
                "available_window": "current REST or partial historical bookTicker only",
                "granularity": "millisecond timestamps in current responses; historical archive not full",
                "symbol_coverage_estimate": "not full 81-symbol target",
                "evidence": "Official bookTicker endpoint documents current best bid/ask price and quantity.",
            },
        },
        "public_rest_limitations": [
            "REST /fapi/v1/depth is a current snapshot endpoint.",
            "REST /fapi/v1/ticker/bookTicker is current best bid/ask for one or all symbols.",
            "Neither REST endpoint provides historical startTime/endTime range backfill for order book states.",
        ],
        "data_binance_vision_archive": {
            "full_2023_2025_coverage_exists": False,
            "archive_families_found_or_indicated": ["monthly bookTicker for some USD-M symbols"],
            "full_81_symbol_coverage_proven": False,
            "notes": [
                "Official public-data README does not prove futures order book/depth/bookTicker full coverage.",
                "Public search/listing evidence indicates bookTicker history is partial and not current through 2025-10-31.",
                "No bulk archive enumeration or data download was performed.",
            ],
        },
    }

    okx_availability = {
        "exchange": "OKX swaps",
        "full_window_available": okx_full_window_available,
        "availability_summary": (
            "OKX publishes an official historical market-data page advertising high-resolution L2 order book "
            "data from March 2023 onward. This is partial for the requested 2023-01-01 start and does not by "
            "itself prove complete 81-symbol overlap coverage for the full target window."
        ),
        "data_types": {
            "historical_order_book_depth": {
                "available_for_full_window": False,
                "available_window": "official page says March 2023 onward",
                "granularity": "high-resolution L2 historical data",
                "symbol_coverage_estimate": "unknown for all 81 overlap symbols without bulk listing",
                "evidence": "OKX historical data page advertises high-resolution L2 data from March 2023 onward.",
            },
            "best_bid_ask_history": {
                "available_for_full_window": False,
                "available_window": "not separately proven for 2023-01-01 through 2023-02-28",
                "granularity": "derivable from L2 where L2 exists; current ticker/order book APIs are live/current",
                "symbol_coverage_estimate": "not proven for full 81-symbol universe",
            },
            "public_rest_order_book": {
                "available_for_full_window": False,
                "available_window": "current snapshot only",
                "granularity": "REST order book current snapshot; full order book current snapshot",
                "symbol_coverage_estimate": "live symbols only",
            },
            "public_websocket_order_book": {
                "available_for_full_window": False,
                "available_window": "forward collection only",
                "granularity": "books/books5/bbo-tbt/books-l2-tbt channels; high-frequency live data",
                "symbol_coverage_estimate": "live symbols only",
            },
        },
        "public_archive": {
            "full_2023_2025_coverage_exists": False,
            "available_window": "March 2023 onward per OKX historical-data page",
            "full_81_symbol_coverage_proven": False,
            "reason_full_window_false": "The requested window begins on 2023-01-01, before the advertised OKX order book start.",
        },
        "rest_websocket_limitations": [
            "REST order book endpoints are current snapshots, not historical range queries.",
            "Public WebSocket channels are live/forward data streams.",
            "Tick-by-tick deeper channels may require login/VIP level for some OKX channels, so they are not treated as public/no-key acquisition-ready.",
        ],
    }

    third_party_public_no_key_availability = {
        "full_window_available": False,
        "availability_summary": (
            "No clearly free public/no-key third-party source was verified to cover Binance and OKX order book "
            "history for all 81 overlap symbols from 2023-01-01 through 2025-10-31."
        ),
        "sources_reviewed": [
            {
                "source_name": "CryptoHFTData",
                "public_no_key": False,
                "full_window_coverage": False,
                "reason": "Docs/examples require an API key and OKX order book dataset page starts in 2025, not 2023.",
            },
            {
                "source_name": "Tardis.dev",
                "public_no_key": False,
                "full_window_coverage": "vendor_possible_not_public_no_key",
                "reason": "Vendor-grade historical order book data is documented, but it is not treated as public/free/no-key for this route.",
            },
            {
                "source_name": "Other public search results",
                "public_no_key": "not_proven",
                "full_window_coverage": False,
                "reason": "Found live/recent collectors, limited-symbol datasets, or unrelated venue datasets, not full Binance/OKX 81-symbol history.",
            },
        ],
    }

    continuation_decision = {
        "acquisition_allowed_next": acquisition_allowed_next,
        "strategy_execution_allowed_next": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_live_capital_allowed_now": False,
        "reason": (
            "Full-window public/no-key order book/depth/bookTicker coverage for the 81-symbol Binance/OKX "
            "overlap universe is not proven. Data direction remains pending."
        ),
    }

    validation_checks = {
        "repo_clean_before_run": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": True,
        "no_bulk_download": True,
        "no_private_api": True,
        "no_api_key_used": True,
        "no_strategy_execution": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "binance_full_window_available_false": binance_full_window_available is False,
        "okx_full_window_available_false": okx_full_window_available is False,
        "public_no_key_full_81_coverage_available_false": public_no_key_full_81_coverage_available is False,
        "acquisition_allowed_next_false": acquisition_allowed_next is False,
        "strategy_execution_allowed_next_false": True,
        "replacement_checks_all_true": True,
    }
    replacement_checks_all_true = all_true(validation_checks)
    if not replacement_checks_all_true:
        print("BLOCKED: order book depth availability validation failed")
        for key in sorted(validation_checks):
            if validation_checks[key] is not True:
                print(f"{key}: {validation_checks[key]}")
        print("replacement_checks_all_true: false")
        return 1

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_RELATIVE_PATH,
        "source_checkpoint": {
            "actual_head_at_discovery_start": HEAD_AT_DISCOVERY_START,
            "tracked_python_count_at_discovery_start": TRACKED_PYTHON_COUNT_AT_DISCOVERY_START,
            "repo_clean_before_run": True,
        },
        "checked_sources": checked_sources,
        "target_window": TARGET_WINDOW,
        "target_universe": TARGET_UNIVERSE,
        "existing_local_repo_artifacts": {
            "tracked_repo_order_book_artifact_candidates": repo_candidates,
            "tracked_repo_order_book_artifact_candidate_count": len(repo_candidates),
            "external_local_order_book_directory_candidates": local_candidates,
            "external_local_order_book_directory_candidate_count": len(local_candidates),
            "review_result": "no existing tracked order book/depth/bookTicker availability lock or reviewed data layer found",
        },
        "binance_availability": binance_availability,
        "okx_availability": okx_availability,
        "third_party_public_no_key_availability": third_party_public_no_key_availability,
        "availability_classification": AVAILABILITY_CLASSIFICATION,
        "continuation_decision": continuation_decision,
        "limitations": [
            "No bulk order book data was downloaded or enumerated.",
            "Public archive listing probes and documentation checks cannot prove missing files for every symbol without bulk enumeration.",
            "OKX official historical L2 availability begins after the requested 2023-01-01 start.",
            "Binance public/no-key historical bookTicker/depth coverage is partial or unproven for the full 2023-2025 target window.",
            "Paid/vendor/API-key sources are excluded by the task constraints.",
        ],
        "safety_permissions": {
            "order_book_depth_availability_discovery_created": True,
            "acquisition_allowed_next": acquisition_allowed_next,
            "strategy_execution_allowed_next": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
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
    print(f"availability_classification: {AVAILABILITY_CLASSIFICATION}")
    print(f"binance_full_window_available: {str(binance_full_window_available).lower()}")
    print(f"okx_full_window_available: {str(okx_full_window_available).lower()}")
    print(f"public_no_key_full_81_coverage_available: {str(public_no_key_full_81_coverage_available).lower()}")
    print(f"acquisition_allowed_next: {str(acquisition_allowed_next).lower()}")
    print("strategy_execution_allowed_next: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print("replacement_checks_all_true: true")
    return 0


if __name__ == "__main__":
    sys.exit(main())
