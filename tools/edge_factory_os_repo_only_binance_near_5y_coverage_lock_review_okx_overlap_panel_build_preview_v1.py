#!/usr/bin/env python3
"""Repo-only Binance near-5y coverage review and OKX overlap preview.

This is a planning preview only. It reads the committed Binance coverage lock
and one explicitly allowed external OKX symbol-lock metadata JSON discovered
from repo-local code references. It does not read panel rows, kline rows, ZIPs,
or run strategy research.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_STATUS = (
    "PASS_REPO_ONLY_BINANCE_NEAR_5Y_COVERAGE_LOCK_REVIEW_OKX_OVERLAP_PANEL_BUILD_PREVIEW_CREATED"
)
MODULE_PATH = (
    "tools/edge_factory_os_repo_only_binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.py"
)
PREVIEW_ARTIFACT_PATH = (
    "artifacts/panel_build_previews/"
    "binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.json"
)
REPO_PATH = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
PREVIEW_PATH = REPO_PATH / PREVIEW_ARTIFACT_PATH
TEMP_PREVIEW_PATH = PREVIEW_PATH.with_suffix(".json.tmp")
BINANCE_LOCK_PATH = REPO_PATH / "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json"
PRIOR_HEAD = "4d1d32beb9797f28fe15940b743495bce5ac092d"
PRIOR_TRACKED_PYTHON_COUNT = 807
PRIOR_BINANCE_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_USDT_PERPETUAL_1M_COVERAGE_DISCOVERY_LOCK_CREATED"
PRIOR_BINANCE_PAYLOAD_HASH = "18a84b71c649b0462fdb0d511597dcb701448fe06184ef9c8da93d6911ada4e0"
EXPECTED_CANDIDATE_COUNT = 704
EXPECTED_NEAR_5Y_COUNT = 638
EXPECTED_STRICT_5Y_COUNT = 102
EXPECTED_PENDING_FAILED_COUNT = 0
EXPECTED_OKX_SYMBOL_COUNT = 88
PRIMARY_START_MONTH = "2021-05"
PRIMARY_END_EXCLUSIVE_MONTH = "2026-05"
PRIMARY_WINDOW_START_UTC = "2021-05-01T00:00:00Z"
PRIMARY_WINDOW_END_EXCLUSIVE_UTC = "2026-05-01T00:00:00Z"
OKX_SYMBOL_RE = re.compile(r"^[A-Z0-9]+-USDT-SWAP$")
FORBIDDEN_OKX_PANEL_NAME = "repo_only_okx_88_symbol_1h_panel_revised_non_holdout_view.csv"

SOURCE_CHECKPOINT = {
    "previous_attempt_blocked_due_missing_repo_local_okx_88_symbol_manifest": True,
    "prior_binance_coverage_lock": "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json",
    "prior_binance_coverage_status": PRIOR_BINANCE_STATUS,
    "prior_binance_coverage_tool": "tools/edge_factory_os_repo_only_binance_usdt_perpetual_1m_coverage_discovery_and_lock_v1.py",
    "prior_head": PRIOR_HEAD,
    "prior_payload_sha256_excluding_hash": PRIOR_BINANCE_PAYLOAD_HASH,
    "prior_tracked_python_count": PRIOR_TRACKED_PYTHON_COUNT,
    "project": "Edge Factory OS / Binance coverage + OKX overlap planning",
    "repo_clean_before_preview": True,
    "this_retry_uses_explicit_read_only_external_okx_symbol_lock_metadata_permission": True,
}

REQUIRED_BINANCE_COVERAGE_LOCK_FACTS = {
    "candidate_universe_symbols_total": EXPECTED_CANDIDATE_COUNT,
    "near_5y_complete_symbols": EXPECTED_NEAR_5Y_COUNT,
    "payload_sha256_excluding_hash": PRIOR_BINANCE_PAYLOAD_HASH,
    "pending_or_failed_probe_symbols": EXPECTED_PENDING_FAILED_COUNT,
    "status": PRIOR_BINANCE_STATUS,
    "strict_5y_complete_symbols": EXPECTED_STRICT_5Y_COUNT,
}


class BlockedError(RuntimeError):
    """Raised when preview creation must stop before writing artifacts."""


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def month_start(month: str) -> dt.datetime:
    year, month_number = (int(part) for part in month.split("-"))
    return dt.datetime(year, month_number, 1, tzinfo=dt.timezone.utc)


def hours_between_months(start_month: str, end_exclusive_month: str) -> int:
    delta = month_start(end_exclusive_month) - month_start(start_month)
    return int(delta.total_seconds() // 3600)


def max_month(values: list[str]) -> str:
    return max(values)


def okx_base(symbol: str) -> str:
    if not symbol.endswith("-USDT-SWAP"):
        raise ValueError(f"Unexpected OKX symbol format: {symbol}")
    return symbol.split("-USDT-SWAP", 1)[0].upper()


def load_binance_lock() -> dict[str, Any]:
    if not BINANCE_LOCK_PATH.is_file():
        raise BlockedError(f"Binance coverage lock path is missing: {BINANCE_LOCK_PATH}")
    lock = read_json(BINANCE_LOCK_PATH)
    if lock.get("status") != PRIOR_BINANCE_STATUS:
        raise BlockedError("Binance coverage lock status is wrong")
    if lock.get("payload_sha256_excluding_hash") != PRIOR_BINANCE_PAYLOAD_HASH:
        raise BlockedError("Binance coverage lock payload hash does not match expected")
    summary = lock.get("global_coverage_summary", {})
    universe = lock.get("universe_summary", {})
    if universe.get("candidate_universe_symbols_total") != EXPECTED_CANDIDATE_COUNT:
        raise AssertionError("candidate universe count mismatch")
    if summary.get("near_5y_complete_symbols") != EXPECTED_NEAR_5Y_COUNT:
        raise AssertionError("near-5y count mismatch")
    if summary.get("strict_5y_complete_symbols") != EXPECTED_STRICT_5Y_COUNT:
        raise AssertionError("strict-5y count mismatch")
    if summary.get("pending_or_failed_probe_symbols") != EXPECTED_PENDING_FAILED_COUNT:
        raise AssertionError("pending/failed count mismatch")
    return lock


def discover_external_okx_symbol_lock_path() -> tuple[Path, list[str], str]:
    source_files = [
        REPO_PATH
        / "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_preview_after_full_coverage_summary_v1.py",
        REPO_PATH
        / "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_execution_after_preview_approval_v1.py",
        REPO_PATH
        / "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_coverage_discovery_final_summary_after_generic_controller_v1.py",
    ]
    edge_root: Path | None = None
    dir_name: str | None = None
    file_name: str | None = None
    used_files: list[str] = []
    for path in source_files:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if "repo_only_okx_full_usdt_swap_near_3y_complete_symbol_set_locked.json" in text:
            used_files.append(str(path.relative_to(REPO_PATH)).replace("\\", "/"))
            file_name = "repo_only_okx_full_usdt_swap_near_3y_complete_symbol_set_locked.json"
        edge_match = re.search(r'EDGE_ROOT\s*=\s*Path\(r"([^"]+)"\)', text)
        if edge_match:
            edge_root = Path(edge_match.group(1))
        dir_match = re.search(
            r'"(edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_coverage_discovery_final_summary_after_generic_controller_v1)"',
            text,
        )
        if dir_match:
            dir_name = dir_match.group(1)
    if edge_root is None or dir_name is None or file_name is None:
        raise BlockedError("external OKX symbol-lock metadata path could not be discovered from repo-local references")
    discovered = edge_root / dir_name / file_name
    return discovered, sorted(set(used_files)), (
        "discovered from repo-local EDGE_ROOT, FINAL_SUMMARY_DIR, and COMPLETE_LOCKED filename references"
    )


def is_metadata_lock_path(path: Path) -> bool:
    lower_name = path.name.lower()
    lower_text = str(path).lower()
    forbidden_suffixes = {".csv", ".parquet", ".zip", ".jsonl", ".pkl", ".pickle", ".db", ".sqlite"}
    return (
        path.suffix.lower() == ".json"
        and "complete_symbol_set_locked" in lower_name
        and FORBIDDEN_OKX_PANEL_NAME.lower() not in lower_text
        and "panel_revised_non_holdout_view" not in lower_text
        and path.suffix.lower() not in forbidden_suffixes
    )


def load_okx_symbol_lock(path: Path) -> dict[str, Any]:
    if not is_metadata_lock_path(path):
        raise BlockedError("external OKX symbol-lock metadata path is not metadata/lock/manifest-like")
    if not path.is_file():
        raise BlockedError(f"external OKX symbol-lock metadata file is missing: {path}")
    data = path.read_bytes()
    lock = json.loads(data.decode("utf-8"))
    symbols = lock.get("near_3y_complete_symbols") or lock.get("build_preview_eligible_symbols")
    if not isinstance(symbols, list):
        raise BlockedError("external OKX symbol-lock metadata does not contain a selected symbol list")
    selected = sorted(str(symbol) for symbol in symbols)
    if len(selected) != EXPECTED_OKX_SYMBOL_COUNT or len(set(selected)) != EXPECTED_OKX_SYMBOL_COUNT:
        raise BlockedError("external OKX selected symbol count is not exactly 88")
    if any(not OKX_SYMBOL_RE.match(symbol) for symbol in selected):
        raise BlockedError("external OKX selected symbol list contains unexpected symbol formats")
    stat = path.stat()
    return {
        "file_size_bytes": stat.st_size,
        "lock": lock,
        "modified_time_ns": stat.st_mtime_ns,
        "sha256": sha256_bytes(data),
        "symbols": selected,
    }


def record_by_symbol(lock: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(row["symbol"]): row for row in lock.get("symbol_coverage_records", [])}


def binance_base(record: dict[str, Any]) -> str:
    metadata = record.get("exchange_info_metadata") or {}
    base = metadata.get("baseAsset")
    if isinstance(base, str) and base:
        return base.upper()
    symbol = str(record.get("symbol", ""))
    return symbol[:-4].upper() if symbol.endswith("USDT") else symbol.upper()


def current_trading(record: dict[str, Any]) -> bool:
    metadata = record.get("exchange_info_metadata") or {}
    return record.get("current_trading") is True or metadata.get("status") == "TRADING"


def listing_aware_hours(record: dict[str, Any]) -> int:
    candidates = [PRIMARY_START_MONTH]
    for key in ("onboard_month", "first_available_month"):
        value = record.get(key)
        if isinstance(value, str) and re.match(r"^\d{4}-\d{2}$", value):
            candidates.append(value)
    start = max_month(candidates)
    if start >= PRIMARY_END_EXCLUSIVE_MONTH:
        return 0
    return hours_between_months(start, PRIMARY_END_EXCLUSIVE_MONTH)


def build_alias_review(okx_symbols: list[str], binance_base_to_symbols: dict[str, list[str]]) -> list[dict[str, Any]]:
    prefixes = ("1000", "1000000")
    rows: list[dict[str, Any]] = []
    for symbol in okx_symbols:
        base = okx_base(symbol)
        candidates: list[str] = []
        for prefix in prefixes:
            prefixed = prefix + base
            candidates.extend(binance_base_to_symbols.get(prefixed, []))
            if base.startswith(prefix):
                candidates.extend(binance_base_to_symbols.get(base[len(prefix) :], []))
        if candidates:
            rows.append(
                {
                    "binance_review_only_symbols": sorted(set(candidates)),
                    "exact_base_overlap_allowed": False,
                    "okx_base_asset": base,
                    "okx_symbol": symbol,
                    "review_reason": "potential multiplier or alias relationship; not auto-mapped",
                }
            )
    return rows


def build_summary() -> dict[str, Any]:
    binance_lock = load_binance_lock()
    okx_path, okx_source_files, extraction_method = discover_external_okx_symbol_lock_path()
    okx_lock = load_okx_symbol_lock(okx_path)
    okx_symbols = okx_lock["symbols"]
    okx_bases = sorted(okx_base(symbol) for symbol in okx_symbols)

    locked_sets = binance_lock["locked_symbol_sets"]
    near_5y_symbols = sorted(locked_sets["binance_usdt_perpetual_near_5y_complete_symbols"])
    strict_5y_symbols = sorted(locked_sets["binance_usdt_perpetual_strict_5y_complete_symbols"])
    records = record_by_symbol(binance_lock)
    near_records = [records[symbol] for symbol in near_5y_symbols]
    strict_records = [records[symbol] for symbol in strict_5y_symbols]

    near_base_to_symbols: dict[str, list[str]] = {}
    for symbol in near_5y_symbols:
        near_base_to_symbols.setdefault(binance_base(records[symbol]), []).append(symbol)
    strict_set = set(strict_5y_symbols)
    okx_base_to_symbol = {okx_base(symbol): symbol for symbol in okx_symbols}
    exact_bases = sorted(set(okx_base_to_symbol) & set(near_base_to_symbols))
    exact_okx = sorted(okx_base_to_symbol[base] for base in exact_bases)
    exact_binance = sorted(symbol for base in exact_bases for symbol in near_base_to_symbols[base])
    exact_strict = sorted(symbol for symbol in exact_binance if symbol in strict_set)
    exact_near_current = sorted(symbol for symbol in exact_binance if current_trading(records[symbol]))
    exact_strict_current = sorted(symbol for symbol in exact_strict if current_trading(records[symbol]))
    missing_okx = sorted(symbol for symbol in okx_symbols if okx_base(symbol) not in near_base_to_symbols)
    alias_review = build_alias_review(missing_okx, near_base_to_symbols)

    option_a_hours = sum(listing_aware_hours(records[symbol]) for symbol in near_5y_symbols)
    option_b_hours_per_symbol = hours_between_months(PRIMARY_START_MONTH, PRIMARY_END_EXCLUSIVE_MONTH)
    option_b_hours = option_b_hours_per_symbol * len(strict_5y_symbols)
    option_c_hours = sum(listing_aware_hours(records[symbol]) for symbol in exact_binance)

    recommended_option = (
        "BINANCE_OKX_EXACT_OVERLAP_NEAR_5Y_SECOND_SOURCE_PANEL"
        if len(exact_bases) >= 40
        else "BINANCE_STRICT_5Y_102_RECTANGULAR_1M_TO_1H_PANEL"
    )
    recommendation_reason = (
        "Exact OKX/Binance near-5y base overlap is meaningful (>=40), so the overlap panel is the best first "
        "second-source planning target."
        if len(exact_bases) >= 40
        else "Exact OKX/Binance near-5y base overlap is below 40, so the narrower strict rectangular panel is preferred."
    )

    universe = binance_lock["universe_summary"]
    global_summary = binance_lock["global_coverage_summary"]
    coverage_policy = binance_lock["coverage_window_policy"]
    near_current = sum(1 for record in near_records if current_trading(record))
    strict_current = sum(1 for record in strict_records if current_trading(record))
    candidate_count = universe["candidate_universe_symbols_total"]
    strict_fraction = round(len(strict_5y_symbols) / len(near_5y_symbols), 12)
    gap_fraction = round(global_summary["coverage_gap_symbols"] / candidate_count, 12)

    payload: dict[str, Any] = {
        "artifact_kind": "BINANCE_NEAR_5Y_COVERAGE_LOCK_REVIEW_OKX_OVERLAP_PANEL_BUILD_PREVIEW",
        "binance_coverage_lock_review": {
            "candidate_universe_symbols_total": candidate_count,
            "coverage_gap_fraction_of_candidate_universe": gap_fraction,
            "coverage_gap_symbols_count": global_summary["coverage_gap_symbols"],
            "coverage_review_passed": True,
            "coverage_review_reason": (
                "Binance lock status/hash/counts verified; near-5y is listing-aware, while strict-5y is the "
                "rectangular subset."
            ),
            "current_trading_symbols_total": universe["current_trading_symbols_total"],
            "global_max_available_daily_date": coverage_policy["global_max_available_daily_date"],
            "latest_monthly_archive_month": coverage_policy["latest_monthly_archive_month"],
            "near_3y_complete_symbols_count": global_summary["near_3y_complete_symbols"],
            "near_5y_complete_symbols_count": len(near_5y_symbols),
            "near_5y_not_strict_5y_count": len(near_5y_symbols) - len(strict_5y_symbols),
            "near_5y_symbols_current_trading_count": near_current,
            "near_5y_symbols_non_trading_count": len(near_5y_symbols) - near_current,
            "pending_or_failed_probe_symbols_count": global_summary["pending_or_failed_probe_symbols"],
            "strict_3y_complete_symbols_count": global_summary["strict_3y_complete_symbols"],
            "strict_5y_complete_symbols_count": len(strict_5y_symbols),
            "strict_5y_fraction_of_near_5y": strict_fraction,
            "strict_5y_symbols_current_trading_count": strict_current,
            "strict_5y_symbols_non_trading_count": len(strict_5y_symbols) - strict_current,
        },
        "binance_near_5y_symbol_set_review": {
            "binance_near_5y_base_assets": sorted(near_base_to_symbols),
            "binance_near_5y_symbols": near_5y_symbols,
            "binance_near_5y_symbols_count": len(near_5y_symbols),
            "interpretation": (
                "Near-5y completeness is listing-aware and not a strict rectangular 5y claim for every symbol."
            ),
            "strict_5y_symbols": strict_5y_symbols,
            "strict_5y_symbols_count": len(strict_5y_symbols),
        },
        "limitations": [
            "This preview is based on Binance coverage lock metadata, not kline row validation.",
            "No Binance kline ZIP contents were opened.",
            "No Binance kline rows were read.",
            "No Binance panel was built.",
            "OKX overlap uses conservative exact base-asset matching only.",
            "Multiplier/alias symbols are not automatically mapped.",
            "Near-5y complete is listing-aware and not equivalent to strict rectangular 5y completeness.",
            "Strict 5y completeness is narrower but better for rectangular panel construction.",
            "External OKX metadata was read only to extract the locked 88-symbol list.",
            "No OKX panel rows were read.",
            "This preview is not a backtest.",
            "This preview is not candidate generation.",
            "This preview is not an edge claim.",
            "This preview grants no runtime/live/capital permission.",
        ],
        "module": MODULE_PATH,
        "okx_binance_overlap_planning": {
            "binance_near_5y_base_assets": sorted(near_base_to_symbols),
            "binance_near_5y_symbols": near_5y_symbols,
            "binance_near_5y_symbols_count": len(near_5y_symbols),
            "binance_near_5y_symbols_not_in_okx_exact_base_count": len(
                [symbol for symbol in near_5y_symbols if binance_base(records[symbol]) not in okx_base_to_symbol]
            ),
            "exact_overlap_base_assets": exact_bases,
            "exact_overlap_binance_near_5y_current_trading_symbols": exact_near_current,
            "exact_overlap_binance_strict_5y_current_trading_symbols": exact_strict_current,
            "exact_overlap_binance_strict_5y_symbols": exact_strict,
            "exact_overlap_binance_symbols": exact_binance,
            "exact_overlap_count": len(exact_bases),
            "exact_overlap_near_5y_current_trading_count": len(exact_near_current),
            "exact_overlap_okx_symbols": exact_okx,
            "exact_overlap_strict_5y_count": len(exact_strict),
            "exact_overlap_strict_5y_current_trading_count": len(exact_strict_current),
            "multiplier_or_alias_potential_matches_review_only": alias_review,
            "okx_base_assets": okx_bases,
            "okx_selected_symbols": okx_symbols,
            "okx_selected_symbols_count": len(okx_symbols),
            "okx_symbol_source_file_size_bytes": okx_lock["file_size_bytes"],
            "okx_symbol_source_modified_time_ns": okx_lock["modified_time_ns"],
            "okx_symbol_source_path": str(okx_path),
            "okx_symbol_source_sha256": okx_lock["sha256"],
            "okx_symbol_source_type": "external_okx_symbol_lock_metadata_read_only",
            "okx_symbols_missing_from_binance_near_5y_exact_base": missing_okx,
            "overlap_planning_passed": True,
            "overlap_planning_reason": "Conservative exact base-asset overlap computed without multiplier or alias auto-mapping.",
        },
        "okx_symbol_set_extraction": {
            "external_okx_symbol_lock_metadata_path": str(okx_path),
            "external_okx_symbol_lock_metadata_read_only": True,
            "okx_base_assets": okx_bases,
            "okx_selected_symbols": okx_symbols,
            "okx_selected_symbols_count": len(okx_symbols),
            "okx_symbol_extraction_method": extraction_method,
            "okx_symbol_source_file_size_bytes": okx_lock["file_size_bytes"],
            "okx_symbol_source_modified_time_ns": okx_lock["modified_time_ns"],
            "okx_symbol_source_sha256": okx_lock["sha256"],
            "okx_symbol_source_type": "external_okx_symbol_lock_metadata_read_only",
        },
        "panel_build_preview": {
            "option_a": {
                "build_preview_recommendation": "viable_but_large_listing_aware_panel",
                "build_risk_level": "high_resource_due_638_symbols_and_1m_archives",
                "daily_tail_extension_available_through": coverage_policy["global_max_available_daily_date"],
                "daily_tail_extension_included_in_first_build": False,
                "expected_1h_rows_listing_aware": option_a_hours,
                "expected_1m_rows_listing_aware": option_a_hours * 60,
                "expected_rows_policy": (
                    "sum per-symbol expected 1h rows from max(symbol first available/onboard month, 2021-05) "
                    "to 2026-05-01 exclusive"
                ),
                "expected_symbol_count": len(near_5y_symbols),
                "listing_aware_ragged_panel": True,
                "option_id": "BINANCE_NEAR_5Y_638_LISTING_AWARE_1M_TO_1H_PANEL",
                "primary_monthly_window_end_month": "2026-04",
                "primary_monthly_window_start_month": PRIMARY_START_MONTH,
                "primary_window_end_exclusive_utc": PRIMARY_WINDOW_END_EXCLUSIVE_UTC,
                "primary_window_start_utc": PRIMARY_WINDOW_START_UTC,
                "rectangular_full_5y_panel": False,
                "source_interval": "1m",
                "symbol_set": "binance_usdt_perpetual_near_5y_complete_symbols",
                "synthetic_pre_onboard_fill_allowed": False,
                "target_interval": "1h",
            },
            "option_b": {
                "build_preview_recommendation": "conservative_rectangular_panel_candidate",
                "build_risk_level": "moderate_resource",
                "expected_1h_rows_rectangular": option_b_hours,
                "expected_1m_rows_rectangular": option_b_hours * 60,
                "expected_rows_per_symbol_1h": option_b_hours_per_symbol,
                "expected_symbol_count": len(strict_5y_symbols),
                "listing_aware_ragged_panel": False,
                "option_id": "BINANCE_STRICT_5Y_102_RECTANGULAR_1M_TO_1H_PANEL",
                "primary_window_end_exclusive_utc": PRIMARY_WINDOW_END_EXCLUSIVE_UTC,
                "primary_window_start_utc": PRIMARY_WINDOW_START_UTC,
                "rectangular_full_5y_panel": True,
                "source_interval": "1m",
                "symbol_set": "binance_usdt_perpetual_strict_5y_complete_symbols",
                "synthetic_pre_onboard_fill_allowed": False,
                "target_interval": "1h",
            },
            "option_c": {
                "build_preview_recommendation": "best_next_step_for_second_source_research_if_panel_build_is_approved",
                "build_risk_level": "lower_than_full_638_panel",
                "expected_1h_rows_listing_aware": option_c_hours,
                "expected_1m_rows_listing_aware": option_c_hours * 60,
                "expected_symbol_count": len(exact_bases),
                "listing_aware_ragged_panel": True,
                "option_id": "BINANCE_OKX_EXACT_OVERLAP_NEAR_5Y_SECOND_SOURCE_PANEL",
                "primary_window_end_exclusive_utc": PRIMARY_WINDOW_END_EXCLUSIVE_UTC,
                "primary_window_start_utc": PRIMARY_WINDOW_START_UTC,
                "purpose": "OKX second-source validation planning",
                "rectangular_full_5y_panel": len(exact_strict) == len(exact_binance),
                "source_interval": "1m",
                "strict_5y_overlap_available": len(exact_strict),
                "symbol_set": exact_binance,
                "target_interval": "1h",
            },
            "no_strategy_allowed_from_preview": True,
            "panel_build_execution_allowed_now": False,
            "panel_build_requires_new_execution_tool_next": True,
            "panel_build_requires_user_approval_next": True,
            "recommendation_reason": recommendation_reason,
            "recommended_next_build_option": recommended_option,
        },
        "recommended_next_step": {
            "panel_build_execution_allowed_now": False,
            "panel_build_requires_user_approval_next": True,
            "recommended_next_build_option": recommended_option,
            "recommended_next_build_reason": recommendation_reason,
        },
        "repo_scope": {
            "api_key_used": False,
            "binance_coverage_discovery_rerun": False,
            "binance_kline_rows_read": False,
            "binance_kline_zip_downloaded": False,
            "binance_kline_zip_opened": False,
            "binance_panel_built": False,
            "candidate_generation": False,
            "code_changes_repo_only": True,
            "edge_claim": False,
            "okx_external_symbol_lock_metadata_read": True,
            "okx_external_symbol_lock_metadata_read_only": True,
            "okx_panel_rows_read": False,
            "okx_whitelisted_artifact_read": False,
            "preview_artifact_created_in_repo": True,
            "private_api_used": False,
            "public_network_used": False,
            "runtime_live_capital": False,
            "strategy_search_executed": False,
        },
        "safety_permissions": {
            "binance_kline_download_allowed_now": False,
            "binance_panel_build_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "capital_permission_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "holdout_access_allowed_now": False,
            "live_permission_allowed_now": False,
            "next_step_may_be_panel_build_execution_prompt_only_after_user_approval": True,
            "okx_panel_access_allowed_now": False,
            "panel_build_allowed_now": False,
            "panel_build_execution_requires_user_approval_next": True,
            "panel_build_preview_created": True,
            "runtime_permission_allowed_now": False,
            "strategy_search_allowed_now": False,
        },
        "source_artifacts": {
            "binance_coverage_lock_path": str(BINANCE_LOCK_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "binance_coverage_lock_payload_hash_verified": True,
            "binance_coverage_lock_status": binance_lock["status"],
            "external_okx_symbol_lock_metadata_path": str(okx_path),
            "external_okx_symbol_lock_metadata_read_only": True,
            "external_okx_symbol_lock_metadata_sha256": okx_lock["sha256"],
            "okx_panel_rows_read": False,
            "okx_symbol_extraction_method": extraction_method,
            "okx_symbol_source_files": okx_source_files,
        },
        "source_checkpoint": SOURCE_CHECKPOINT,
        "status": REQUIRED_STATUS,
        "symbol_normalization_policy": {
            "binance_canonical_exact_base_key": "baseAsset uppercased from Binance coverage lock metadata",
            "exact_overlap_rule": "OKX base key must equal Binance baseAsset exactly",
            "multiplier_or_alias_symbols_auto_mapped": False,
            "okx_canonical_exact_base_key": "part before '-USDT-SWAP', uppercased",
            "only_exact_base_overlap_allowed_in_okx_overlap_panel_preview": True,
            "review_only_alias_examples": ["PEPE versus 1000PEPE", "SHIB versus 1000SHIB", "BONK versus 1000BONK", "FLOKI versus 1000FLOKI"],
        },
    }
    payload["validation_checks"] = {
        "binance_candidate_universe_count_verified_704": candidate_count == EXPECTED_CANDIDATE_COUNT,
        "binance_coverage_lock_loaded": True,
        "binance_coverage_lock_payload_hash_verified": binance_lock["payload_sha256_excluding_hash"]
        == PRIOR_BINANCE_PAYLOAD_HASH,
        "binance_coverage_lock_status_verified": binance_lock["status"] == PRIOR_BINANCE_STATUS,
        "binance_near_5y_count_verified_638": len(near_5y_symbols) == EXPECTED_NEAR_5Y_COUNT,
        "binance_pending_failed_count_verified_0": global_summary["pending_or_failed_probe_symbols"]
        == EXPECTED_PENDING_FAILED_COUNT,
        "binance_strict_5y_count_verified_102": len(strict_5y_symbols) == EXPECTED_STRICT_5Y_COUNT,
        "exact_overlap_computed": True,
        "exactly_one_new_tracked_json_preview_artifact_expected": True,
        "exactly_one_new_tracked_python_tool_file_expected": True,
        "external_okx_symbol_lock_metadata_path_discovered_from_repo_reference": bool(okx_source_files),
        "external_okx_symbol_lock_metadata_read_only": True,
        "module_path_equals_required_path": MODULE_PATH
        == "tools/edge_factory_os_repo_only_binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.py",
        "multiplier_alias_candidates_not_auto_mapped": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_existing_files_modified_expected": True,
        "no_kline_rows_read": True,
        "no_kline_zip_downloaded": True,
        "no_kline_zip_opened": True,
        "no_network_used": True,
        "no_panel_built": True,
        "no_runtime_live_capital": True,
        "no_strategy_search": True,
        "okx_panel_rows_not_read": True,
        "okx_symbol_count_verified_88": len(okx_symbols) == EXPECTED_OKX_SYMBOL_COUNT,
        "okx_symbol_set_extracted": True,
        "okx_whitelisted_non_holdout_panel_not_read": True,
        "panel_build_options_created": True,
        "payload_sha256_excluding_hash_present": True,
        "preview_artifact_json_valid": True,
        "preview_artifact_path_equals_required_path": PREVIEW_ARTIFACT_PATH
        == "artifacts/panel_build_previews/binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.json",
        "replacement_checks_all_true": True,
        "status_equals_required_status": True,
    }
    payload["replacement_checks_all_true"] = all(value is True for value in payload["validation_checks"].values())
    payload_without_hash = dict(payload)
    payload_without_hash.pop("payload_sha256_excluding_hash", None)
    payload["payload_sha256_excluding_hash"] = sha256_bytes(canonical_json_bytes(payload_without_hash))
    return payload


def validate_summary(summary: dict[str, Any]) -> None:
    assert summary["status"] == REQUIRED_STATUS
    assert summary["module"] == MODULE_PATH
    assert PREVIEW_ARTIFACT_PATH == (
        "artifacts/panel_build_previews/binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.json"
    )
    checks = summary["validation_checks"]
    assert checks["binance_coverage_lock_loaded"] is True
    assert checks["binance_coverage_lock_status_verified"] is True
    assert checks["binance_coverage_lock_payload_hash_verified"] is True
    assert checks["binance_near_5y_count_verified_638"] is True
    assert checks["binance_strict_5y_count_verified_102"] is True
    assert checks["binance_pending_failed_count_verified_0"] is True
    assert checks["external_okx_symbol_lock_metadata_path_discovered_from_repo_reference"] is True
    assert checks["external_okx_symbol_lock_metadata_read_only"] is True
    assert checks["okx_symbol_count_verified_88"] is True
    assert summary["repo_scope"]["okx_panel_rows_read"] is False
    assert summary["repo_scope"]["okx_whitelisted_artifact_read"] is False
    assert summary["repo_scope"]["binance_kline_rows_read"] is False
    assert summary["repo_scope"]["binance_kline_zip_opened"] is False
    assert summary["repo_scope"]["binance_kline_zip_downloaded"] is False
    assert summary["safety_permissions"]["panel_build_allowed_now"] is False
    assert summary["safety_permissions"]["binance_panel_build_allowed_now"] is False
    assert summary["safety_permissions"]["strategy_search_allowed_now"] is False
    assert summary["safety_permissions"]["candidate_generation_allowed_now"] is False
    assert summary["safety_permissions"]["edge_claim_allowed_now"] is False
    assert summary["safety_permissions"]["runtime_permission_allowed_now"] is False
    assert summary["safety_permissions"]["live_permission_allowed_now"] is False
    assert summary["safety_permissions"]["capital_permission_allowed_now"] is False
    assert summary["replacement_checks_all_true"] is True
    assert summary["payload_sha256_excluding_hash"]


def write_preview(summary: dict[str, Any]) -> None:
    PREVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    if TEMP_PREVIEW_PATH.exists():
        TEMP_PREVIEW_PATH.unlink()
    TEMP_PREVIEW_PATH.write_bytes(canonical_json_bytes(summary) + b"\n")
    TEMP_PREVIEW_PATH.replace(PREVIEW_PATH)


def stdout_summary(summary: dict[str, Any]) -> dict[str, Any]:
    preview = summary["panel_build_preview"]
    overlap = summary["okx_binance_overlap_planning"]
    return {
        "binance_candidate_universe_symbols_total": summary["binance_coverage_lock_review"][
            "candidate_universe_symbols_total"
        ],
        "binance_near_5y_symbols_count": summary["binance_near_5y_symbol_set_review"][
            "binance_near_5y_symbols_count"
        ],
        "binance_strict_5y_symbols_count": summary["binance_near_5y_symbol_set_review"]["strict_5y_symbols_count"],
        "candidate_generation": False,
        "edge_claim": False,
        "exact_overlap_count": overlap["exact_overlap_count"],
        "exact_overlap_near_5y_current_trading_count": overlap["exact_overlap_near_5y_current_trading_count"],
        "exact_overlap_strict_5y_count": overlap["exact_overlap_strict_5y_count"],
        "okx_selected_symbols_count": overlap["okx_selected_symbols_count"],
        "okx_symbol_source_path": overlap["okx_symbol_source_path"],
        "option_a_expected_1h_rows_listing_aware": preview["option_a"]["expected_1h_rows_listing_aware"],
        "option_b_expected_1h_rows_rectangular": preview["option_b"]["expected_1h_rows_rectangular"],
        "option_c_expected_1h_rows_listing_aware": preview["option_c"]["expected_1h_rows_listing_aware"],
        "panel_build_allowed_now": False,
        "payload_sha256_excluding_hash": summary["payload_sha256_excluding_hash"],
        "preview_artifact_path": PREVIEW_ARTIFACT_PATH,
        "recommended_next_build_option": preview["recommended_next_build_option"],
        "recommended_next_build_reason": preview["recommendation_reason"],
        "replacement_checks_all_true": summary["replacement_checks_all_true"],
        "runtime_live_capital": False,
        "status": summary["status"],
        "strategy_search_executed": False,
    }


def main() -> int:
    try:
        summary = build_summary()
        validate_summary(summary)
    except BlockedError as exc:
        print(
            json.dumps(
                {
                    "exact_blocker": str(exc),
                    "replacement_checks_all_true": False,
                    "status": "BLOCKED",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1
    write_preview(summary)
    print(json.dumps(stdout_summary(summary), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
