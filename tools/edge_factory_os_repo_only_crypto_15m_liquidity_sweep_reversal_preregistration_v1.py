from __future__ import annotations

import csv
import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PANEL_DIR = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_binance_okx_overlap_81_symbol_15m_panel_build_v1\panel_15m_by_symbol"
)
PANEL_REVIEW = REPO_ROOT / "artifacts" / "panel_build_reviews" / "binance_okx_overlap_81_symbol_15m_panel_review_after_build_v1.json"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "research_preregistrations" / "crypto_15m_liquidity_sweep_reversal_preregistration_v1.json"

STATUS = "PASS_REPO_ONLY_CRYPTO_15M_LIQUIDITY_SWEEP_REVERSAL_PREREGISTRATION_CREATED"
ARTIFACT_KIND = "CRYPTO_15M_LIQUIDITY_SWEEP_REVERSAL_PREREGISTRATION"
STRATEGY = "CRYPTO_15M_LIQUIDITY_SWEEP_FAILED_BREAKOUT_REVERSAL_V1"
ROUTE_FAMILY = "CRYPTO_15M_LIQUIDITY_SWEEP_REVERSAL_BASELINE"
CONFIG_ID = "crypto_15m_liquidity_sweep_48h_reversal_r2_timestop8h_v1"
EXPECTED_COLUMNS = {
    "symbol",
    "timestamp_utc",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "quote_volume",
    "complete_15m",
}


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def payload_hash(data: dict[str, Any]) -> str:
    clone = dict(data)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def git(args: list[str]) -> str:
    completed = subprocess.run(["git", "-C", str(REPO_ROOT), *args], check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def tracked_python_count() -> int:
    return len([line for line in git(["ls-files", "*.py"]).splitlines() if line.strip()])


def inspect_panel() -> dict[str, Any]:
    files = sorted(PANEL_DIR.glob("*_15m.csv.gz"))
    btc_path = PANEL_DIR / "BTCUSDT_15m.csv.gz"
    header: list[str] = []
    first_row = None
    if btc_path.exists():
        with gzip.open(btc_path, "rt", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            header = reader.fieldnames or []
            first_row = next(reader, None)
    return {
        "panel_dir": str(PANEL_DIR),
        "panel_dir_exists": PANEL_DIR.exists(),
        "symbol_file_count": len(files),
        "btc_disaster_filter_available": btc_path.exists(),
        "btc_header": header,
        "btc_header_has_required_columns": EXPECTED_COLUMNS.issubset(set(header)),
        "btc_first_row": first_row,
        "sample_files": [path.name for path in files[:10]],
    }


def main() -> int:
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status = {
        "?? tools/edge_factory_os_repo_only_crypto_15m_liquidity_sweep_reversal_preregistration_v1.py",
        "?? artifacts/research_preregistrations/crypto_15m_liquidity_sweep_reversal_preregistration_v1.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]
    panel_review = load_json(PANEL_REVIEW)
    panel = inspect_panel()
    if not panel["panel_dir_exists"] or panel["symbol_file_count"] != 81:
        raise RuntimeError("reviewed 81-symbol 15m panel missing")
    if not panel["btc_disaster_filter_available"]:
        raise RuntimeError("BTCUSDT disaster-filter anchor missing")

    preregistered_config = {
        "strategy": STRATEGY,
        "route_family": ROUTE_FAMILY,
        "config_id": CONFIG_ID,
        "single_config_only": True,
        "parameter_grid_allowed": False,
        "optimization_allowed": False,
        "dataset": {
            "name": "reviewed Binance/OKX overlap 81-symbol 15m panel",
            "panel_directory": str(PANEL_DIR),
            "panel_review_artifact": str(PANEL_REVIEW),
            "expected_symbol_count": 81,
            "expected_timeframe": "15m",
            "expected_start_utc": "2023-01-01T00:00:00Z",
            "expected_end_utc": "2025-10-31T23:45:00Z",
            "expected_rows": 7808472,
            "btc_disaster_filter_anchor": "BTCUSDT",
        },
        "fixed_parameters": {
            "prior_range_window_bars": 192,
            "atr_length": 14,
            "volume_sma_length": 20,
            "volume_mult": 1.5,
            "cross_sectional_momentum_window_bars": 16,
            "top_bottom_quantile": 0.20,
            "risk_per_trade_usdt": 5.0,
            "base_equity_usdt": 1000.0,
            "max_notional_usdt": 100.0,
            "max_concurrent_positions": 5,
            "time_stop_bars": 32,
            "reward_risk_take_profit": 2.0,
            "round_trip_cost_bps": 20.0,
        },
        "signal_rules": {
            "long": [
                "low < prior_low_48h",
                "close > prior_low_48h",
                "close > open",
                "close >= low + 0.6 * (high - low)",
                "volume > volume_sma20 * 1.5",
                "return_4h is bottom 20% of eligible universe",
                "BTC 24h return >= -5%",
            ],
            "short": [
                "high > prior_high_48h",
                "close < prior_high_48h",
                "close < open",
                "close <= low + 0.4 * (high - low)",
                "volume > volume_sma20 * 1.5",
                "return_4h is top 20% of eligible universe",
                "BTC 24h return <= +5%",
            ],
        },
        "entry_exit": {
            "entry": "signal at 15m close, enter next 15m open",
            "capacity_ranking": "sweep_depth descending, then abs(return_4h) descending",
            "long_stop": "sweep_low - 0.5 * ATR14",
            "short_stop": "sweep_high + 0.5 * ATR14",
            "take_profit": "2R",
            "time_stop_bars": 32,
            "both_hit_same_bar_policy": "assume stop first",
            "trailing_stop": "none",
        },
        "portfolio_accounting": {
            "portfolio_net_bps": "total_net_pnl_usdt / 1000 * 10000",
            "monthly_net_bps": "monthly_net_pnl_usdt / 1000 * 10000",
            "do_not_sum_trade_bps_as_portfolio_return": True,
            "no_leverage": True,
            "no_compounding": True,
            "no_reinvestment": True,
        },
        "splits": {
            "train": ["2023-01-01T00:00:00Z", "2024-07-01T00:00:00Z"],
            "validation": ["2024-07-01T00:00:00Z", "2025-04-01T00:00:00Z"],
            "holdout": ["2025-04-01T00:00:00Z", "2025-11-01T00:00:00Z"],
        },
        "evaluator_policy": {
            "diagnostic_promising_requires": [
                "validation portfolio net bps > 0",
                "holdout portfolio net bps > 0",
                "validation monthly positive rate >= 0.60",
                "holdout monthly positive rate >= 0.50",
                "validation closed trades >= 50",
                "null baseline passes",
                "top symbol trade share <= 0.25",
                "worst month > -1000 bps",
                "metric integrity passes",
                "no candidate/edge/live/capital",
            ],
            "allowed_result_classes": [
                "CRYPTO_15M_LIQUIDITY_SWEEP_REVERSAL_DIAGNOSTIC_PROMISING_NO_EDGE_NO_LIVE",
                "CRYPTO_15M_LIQUIDITY_SWEEP_REVERSAL_REJECTED_NO_FOLLOWUP",
                "CRYPTO_15M_LIQUIDITY_SWEEP_REVERSAL_INCONCLUSIVE_NEEDS_MORE_DATA",
                "CRYPTO_15M_LIQUIDITY_SWEEP_REVERSAL_INVALIDATED_BY_DATA_OR_INTEGRITY_FAILURE",
            ],
        },
    }
    safety_permissions = {
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "live_permission_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "monitor_allowed_now": False,
        "capital_permission_allowed_now": False,
        "real_orders_allowed_now": False,
        "family_release_allowed_now": False,
    }
    validation_checks = {
        "repo_clean_before_run": not unexpected_status,
        "panel_review_artifact_loaded": True,
        "panel_directory_exists": panel["panel_dir_exists"],
        "symbol_file_count_verified_81": panel["symbol_file_count"] == 81,
        "btc_disaster_filter_anchor_available": panel["btc_disaster_filter_available"],
        "btc_header_has_required_columns": panel["btc_header_has_required_columns"],
        "no_network_used": True,
        "no_api_used": True,
        "no_parameter_grid": True,
        "no_optimization": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
    }
    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": "edge_factory_os_repo_only_crypto_15m_liquidity_sweep_reversal_preregistration_v1",
        "strategy": STRATEGY,
        "route_family": ROUTE_FAMILY,
        "config_id": CONFIG_ID,
        "source_checkpoint": {
            "actual_head": git(["rev-parse", "HEAD"]),
            "tracked_python_count": tracked_python_count(),
            "repo_clean_before_run": not unexpected_status,
            "git_status_at_preregistration": status_lines,
            "allowed_new_paths_at_preregistration": sorted(allowed_status),
            "unexpected_dirty_paths_at_preregistration": unexpected_status,
        },
        "source_artifacts": {"panel_review": str(PANEL_REVIEW)},
        "panel_review_status": panel_review.get("status"),
        "panel_inspection": panel,
        "preregistered_config": preregistered_config,
        "metric_integrity_preregistration": {
            "no_lookahead_required": True,
            "prior_high_low_exclude_current_bar": True,
            "rank_uses_current_or_past_completed_returns": True,
            "entry_next_bar_open": True,
            "stop_take_uses_conservative_ohlc": True,
            "portfolio_bps_uses_base_equity_denominator": True,
            "notional_cap_required": True,
            "max_concurrent_positions_lte_5": True,
        },
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": all(validation_checks.values()) and all(value is False for value in safety_permissions.values()),
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")
    print(f"status: {STATUS}")
    print(f"strategy: {STRATEGY}")
    print(f"route_family: {ROUTE_FAMILY}")
    print(f"config_id: {CONFIG_ID}")
    print(f"symbol_file_count: {panel['symbol_file_count']}")
    print(f"btc_disaster_filter_anchor_available: {str(panel['btc_disaster_filter_available']).lower()}")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
