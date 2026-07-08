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
MARKET_PUMP_VETO_EXECUTION = REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_idiosyncratic_sweep_short_market_pump_veto_execution_v1.json"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "research_preregistrations" / "crypto_15m_idiosyncratic_sweep_short_trap_quality_preregistration_v1.json"

STATUS = "PASS_REPO_ONLY_CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_PREREGISTRATION_CREATED"
ARTIFACT_KIND = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_PREREGISTRATION"
STRATEGY = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_V1"
ROUTE_FAMILY = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_BASELINE"
CONFIG_ID = "crypto_15m_idiosyncratic_sweep_short_trap_quality_v1"
EXPECTED_COLUMNS = {"symbol", "timestamp_utc", "open", "high", "low", "close", "volume", "quote_volume", "complete_15m"}


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def payload_hash(data: dict[str, Any]) -> str:
    clone = dict(data)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git(args: list[str]) -> str:
    completed = subprocess.run(["git", "-C", str(REPO_ROOT), *args], check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def tracked_python_count() -> int:
    return len([line for line in git(["ls-files", "*.py"]).splitlines() if line.strip()])


def inspect_anchor(symbol: str) -> dict[str, Any]:
    path = PANEL_DIR / f"{symbol}_15m.csv.gz"
    if not path.exists():
        return {"symbol": symbol, "exists": False, "has_required_columns": False, "header": []}
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames or []
        first_row = next(reader, None)
    return {
        "symbol": symbol,
        "path": str(path),
        "exists": True,
        "header": header,
        "has_required_columns": EXPECTED_COLUMNS.issubset(set(header)),
        "first_row": first_row,
    }


def main() -> int:
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status = {
        "?? tools/edge_factory_os_repo_only_crypto_15m_idiosyncratic_sweep_short_trap_quality_preregistration_v1.py",
        "?? artifacts/research_preregistrations/crypto_15m_idiosyncratic_sweep_short_trap_quality_preregistration_v1.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]
    panel_review = load_json(PANEL_REVIEW)
    prior_execution = load_json(MARKET_PUMP_VETO_EXECUTION)
    files = sorted(PANEL_DIR.glob("*_15m.csv.gz"))
    symbols = [path.name.removesuffix("_15m.csv.gz") for path in files]
    btc = inspect_anchor("BTCUSDT")
    eth = inspect_anchor("ETHUSDT")
    if len(symbols) != 81 or not btc["exists"] or not eth["exists"]:
        raise RuntimeError("BLOCKED_REQUIRED_ANCHOR_SYMBOL_MISSING")
    if not btc["has_required_columns"] or not eth["has_required_columns"]:
        raise RuntimeError("BLOCKED_REQUIRED_ANCHOR_SYMBOL_MISSING")

    inherited_parameters = {
        "timeframe": "15m",
        "rolling_beta_window_bars": 2880,
        "minimum_beta_observations": 1000,
        "residual_impulse_bars": 16,
        "residual_z_history_bars": 2880,
        "short_z_threshold": 3.5,
        "prior_range_window_bars": 192,
        "atr_length": 14,
        "volume_sma_length": 20,
        "volume_filter": "volume > volume_sma20",
        "confirmation_required": True,
        "cost_gate_expected_abs_move_min": 0.008,
        "stop_risk_quality_ratio_min": 1.0,
        "market_pump_veto_enabled": True,
        "round_trip_cost_fraction": 0.002,
        "base_equity_usdt": 1000.0,
        "risk_per_trade_usdt": 5.0,
        "max_notional_per_trade_usdt": 100.0,
        "max_concurrent_positions": 3,
        "max_new_positions_per_timestamp": 1,
        "one_open_position_per_symbol": True,
        "symbol_cooldown_bars_after_exit": 96,
        "time_stop_bars": 32,
        "reward_risk_take_profit": 2.0,
        "long_entries_enabled": False,
    }
    trap_quality_filter = {
        "computed_on": "sweep bar known at close",
        "components": {
            "upper_wick_share_gte_0_40": "upper_wick / candle_range >= 0.40",
            "close_location_lte_0_40": "(close - low) / candle_range <= 0.40",
            "sweep_depth_atr_gte_0_15": "(high - prior_high_48h) / ATR14 >= 0.15",
            "rejection_depth_atr_gte_0_05": "(prior_high_48h - close) / ATR14 >= 0.05",
        },
        "trap_quality_score": "number of passed components",
        "minimum_score": 3,
        "invalid_when": ["candle_range <= 0", "ATR14 <= 0"],
        "thresholds_are_structural_round_numbers_not_optimized": True,
    }
    confirmation_quality = {
        "confirmation_strength_atr": "(sweep_close - confirmation_close) / ATR14",
        "minimum_confirmation_strength_atr": 0.05,
        "threshold_is_structural_round_number_not_optimized": True,
    }
    market_pump_veto = {
        "veto_true_if_any": [
            "btc_ret_4h > 0.015 and eth_ret_4h > 0.015",
            "btc_ret_24h > 0.04 and eth_ret_24h > 0.04",
            "pump_breadth > 0.35",
            "median_universe_ret_4h > 0.01",
        ],
        "inherited_unchanged": True,
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
        "panel_review_loaded": True,
        "prior_market_pump_veto_execution_loaded": True,
        "panel_file_count_verified_81": len(symbols) == 81,
        "btc_anchor_available": btc["exists"],
        "eth_anchor_available": eth["exists"],
        "no_parameter_grid": True,
        "no_optimization": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_network_used": True,
        "no_api_used": True,
    }
    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": "edge_factory_os_repo_only_crypto_15m_idiosyncratic_sweep_short_trap_quality_preregistration_v1",
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
        "source_artifacts": {
            "panel_review": str(PANEL_REVIEW),
            "prior_market_pump_veto_execution": str(MARKET_PUMP_VETO_EXECUTION),
        },
        "prior_failure_evidence": {
            "prior_validation_net_bps": prior_execution.get("split_metrics", {}).get("validation", {}).get("portfolio_net_bps"),
            "prior_holdout_net_bps": prior_execution.get("split_metrics", {}).get("holdout", {}).get("portfolio_net_bps"),
            "prior_null_percentile": prior_execution.get("null_baseline", {}).get("validation_percentile"),
            "prior_null_pass": prior_execution.get("null_baseline", {}).get("null_pass"),
            "interpretation": "Market pump veto improved risk but did not improve event specificity enough to pass null.",
        },
        "panel_inspection": {
            "panel_review_status": panel_review.get("status"),
            "panel_dir": str(PANEL_DIR),
            "symbol_file_count": len(symbols),
            "btc_anchor": btc,
            "eth_anchor": eth,
        },
        "preregistered_config": {
            "single_config_only": True,
            "parameter_grid_allowed": False,
            "optimization_allowed": False,
            "hypothesis": "Short sweeps should only be traded when the sweep bar behaves like a true trap with a meaningful upper wick, weak close, real sweep depth, rejection depth, and downside confirmation.",
            "inherited_parameters": inherited_parameters,
            "market_pump_veto": market_pump_veto,
            "new_structural_trap_quality_filter": trap_quality_filter,
            "additional_confirmation_quality": confirmation_quality,
            "candidate_ranking": [
                "trap_quality_score descending",
                "confirmation_strength_atr descending",
                "abs(z_residual) descending",
                "sweep_depth_atr descending",
            ],
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
                    "validation closed trades >= 30",
                    "null baseline passes",
                    "top symbol trade share <= 0.25",
                    "worst month > -1000 bps",
                    "metric integrity passes",
                    "no candidate/edge/live/capital",
                ],
                "allowed_result_classes": [
                    "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_DIAGNOSTIC_PROMISING_NO_EDGE_NO_LIVE",
                    "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_REJECTED_NO_FOLLOWUP",
                    "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_INCONCLUSIVE_NEEDS_MORE_DATA",
                    "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_INVALIDATED_BY_DATA_OR_INTEGRITY_FAILURE",
                ],
            },
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
    print(f"symbol_file_count: {len(symbols)}")
    print("trap_quality_preregistered: true")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
